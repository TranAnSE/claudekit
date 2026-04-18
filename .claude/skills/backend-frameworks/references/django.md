# Backend Frameworks — Django Patterns


# Django

## When to Use

- Python web applications
- Admin interfaces
- Django REST Framework APIs
- Content-heavy sites with ORM-driven data models

## When NOT to Use

- FastAPI projects — use the `fastapi` skill instead for async APIs and microservices
- JavaScript/Node.js backends (Express, NestJS) — this skill is Python-only
- Microservices architectures — consider FastAPI instead for lightweight, async services

---

## Core Patterns

### 1. Models & ORM

#### Field types and relationships

```python
from django.db import models
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class User(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["organization", "role"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                name="unique_org_email",
            ),
        ]

    def __str__(self):
        return self.email

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owned_projects")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")
    # OneToOneField for 1:1 relationships
    settings = models.OneToOneField(
        "ProjectSettings", on_delete=models.CASCADE, null=True, blank=True
    )

class ProjectSettings(models.Model):
    is_public = models.BooleanField(default=False)
    max_members = models.IntegerField(default=10)
```

#### Custom managers and QuerySet methods

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class UserQuerySet(models.QuerySet):
    def admins(self):
        return self.filter(role=User.Role.ADMIN)

    def in_organization(self, org_id):
        return self.filter(organization_id=org_id)

    def with_project_count(self):
        return self.annotate(project_count=models.Count("owned_projects"))

class User(models.Model):
    # ... fields ...
    objects = UserQuerySet.as_manager()
    active = ActiveManager()
```

#### F objects, Q objects, and annotations

```python
from django.db.models import F, Q, Count, Avg, Sum, Value, When, Case

# F objects: reference model fields in queries
Project.objects.filter(updated_at__gt=F("created_at"))
User.objects.update(login_count=F("login_count") + 1)  # Atomic increment

# Q objects: complex lookups with OR, AND, NOT
User.objects.filter(
    Q(role="admin") | Q(role="member"),
    ~Q(is_active=False),  # NOT inactive
)

# Annotations and aggregations
orgs = Organization.objects.annotate(
    member_count=Count("members"),
    admin_count=Count("members", filter=Q(members__role="admin")),
    avg_projects=Avg("members__owned_projects"),
).filter(member_count__gte=5)

# Conditional expressions
users = User.objects.annotate(
    tier=Case(
        When(owned_projects__count__gte=10, then=Value("power")),
        When(owned_projects__count__gte=3, then=Value("active")),
        default=Value("starter"),
    )
)

# Subqueries
from django.db.models import Subquery, OuterRef
latest_project = Project.objects.filter(
    owner=OuterRef("pk")
).order_by("-created_at").values("title")[:1]
users = User.objects.annotate(latest_project_title=Subquery(latest_project))
```

### 2. Views

#### Function-based views

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner", "organization"),
        pk=project_id,
    )
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project-detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/detail.html", {
        "project": project,
        "form": form,
    })
```

#### Class-based views

```python
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("owner", "organization")
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return qs

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/form.html"
    success_url = reverse_lazy("project-list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.organization = self.request.user.organization
        return super().form_valid(form)

class ProjectDeleteView(PermissionRequiredMixin, DeleteView):
    model = Project
    permission_required = "projects.delete_project"
    success_url = reverse_lazy("project-list")
```

#### Mixins for reuse

```python
class OrganizationFilterMixin:
    """Filter queryset to the current user's organization."""
    def get_queryset(self):
        return super().get_queryset().filter(
            organization=self.request.user.organization
        )

class ProjectListView(LoginRequiredMixin, OrganizationFilterMixin, ListView):
    model = Project
    # queryset is automatically filtered by organization
```

#### API views with Django REST Framework

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def project_list(request):
    if request.method == "GET":
        projects = Project.objects.filter(organization=request.user.organization)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    serializer = ProjectCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(owner=request.user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### 3. Migrations

#### Creating and running migrations

```bash
# Generate migrations after model changes
python manage.py makemigrations app_name

# Preview SQL without applying
python manage.py sqlmigrate app_name 0001

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

#### Data migrations with RunPython

```python
from django.db import migrations

def populate_slugs(apps, schema_editor):
    Organization = apps.get_model("myapp", "Organization")
    from django.utils.text import slugify
    for org in Organization.objects.filter(slug=""):
        org.slug = slugify(org.name)
        org.save(update_fields=["slug"])

def reverse_populate_slugs(apps, schema_editor):
    pass  # No-op reverse

class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0005_add_slug_field"),
    ]
    operations = [
        migrations.RunPython(populate_slugs, reverse_populate_slugs),
    ]
```

#### Squashing migrations

```bash
# Squash migrations 0001 through 0010 into one
python manage.py squashmigrations app_name 0001 0010
```

**Tips:**
- Always provide a reverse function for `RunPython` (even if it is a no-op)
- Use `apps.get_model()` in data migrations, never import models directly
- Test migrations on a copy of production data before deploying

### 4. Forms

#### ModelForm with custom validation

```python
from django import forms
from django.core.exceptions import ValidationError

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "tags"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        if "test" in title.lower() and not self.instance.pk:
            raise ValidationError("Title cannot contain 'test' for new projects.")
        return title

    def clean(self):
        cleaned = super().clean()
        title = cleaned.get("title", "")
        description = cleaned.get("description", "")
        if len(title) + len(description) < 20:
            raise ValidationError("Title + description must be at least 20 characters.")
        return cleaned
```

#### Formsets

```python
from django.forms import inlineformset_factory

TaskFormSet = inlineformset_factory(
    Project,
    Task,
    fields=["title", "assigned_to", "due_date"],
    extra=2,       # Number of empty forms
    can_delete=True,
    max_num=20,
)

# In a view
def project_tasks(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        formset = TaskFormSet(request.POST, instance=project)
        if formset.is_valid():
            formset.save()
            return redirect("project-detail", project_id=project.id)
    else:
        formset = TaskFormSet(instance=project)
    return render(request, "projects/tasks.html", {"formset": formset})
```

### 5. Signals

```python
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(pre_save, sender=Project)
def set_project_slug(sender, instance, **kwargs):
    if not instance.slug:
        from django.utils.text import slugify
        instance.slug = slugify(instance.title)

# Custom signals
from django.dispatch import Signal

project_published = Signal()  # Accepts sender

@receiver(project_published)
def notify_members(sender, project, **kwargs):
    for member in project.organization.members.all():
        send_notification(member, f"Project '{project.title}' published")

# Firing a custom signal
project_published.send(sender=Project, project=project)
```

**When to use signals vs overriding `save()`:**
- Use signals when the action is a side effect (notifications, logging, cache invalidation)
- Override `save()` when the logic is core to the model's behavior (setting computed fields)

### 6. Middleware

```python
import time
from django.utils.deprecation import MiddlewareMixin

class TimingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.perf_counter()

    def process_response(self, request, response):
        if hasattr(request, "_start_time"):
            duration = time.perf_counter() - request._start_time
            response["X-Process-Time"] = f"{duration:.4f}"
        return response

# New-style middleware (function-based)
def organization_middleware(get_response):
    def middleware(request):
        if request.user.is_authenticated:
            request.organization = request.user.organization
        else:
            request.organization = None
        response = get_response(request)
        return response
    return middleware

# Register in settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "myapp.middleware.organization_middleware",  # Custom
    "myapp.middleware.TimingMiddleware",         # Custom
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### 7. Django REST Framework

#### Serializers

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    project_count = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "role", "full_name", "project_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_full_name(self, obj):
        return f"{obj.name} ({obj.role})"

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all()
    )

    class Meta:
        model = Project
        fields = ["id", "title", "description", "owner", "tags", "created_at"]

    def validate_title(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value

class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["title", "description", "tags"]
```

#### ViewSets and routers

```python
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["owner", "tags"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Project.objects.filter(
            organization=self.request.user.organization
        ).select_related("owner").prefetch_related("tags")

    def get_serializer_class(self):
        if self.action == "create":
            return ProjectCreateSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            organization=self.request.user.organization,
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        project = self.get_object()
        project.is_published = True
        project.save(update_fields=["is_published"])
        return Response({"status": "published"})

# urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("api/", include(router.urls)),
]
```

#### Permissions

```python
from rest_framework.permissions import BasePermission

class IsOrganizationAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

#### Pagination

```python
from rest_framework.pagination import PageNumberPagination, CursorPagination

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class TimelinePagination(CursorPagination):
    page_size = 50
    ordering = "-created_at"

# settings.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "myapp.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}
```

### 8. Admin

```python
from django.contrib import admin
from django.utils.html import format_html

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ["title", "assigned_to", "status", "due_date"]
    readonly_fields = ["created_at"]

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "owner_name", "organization", "tag_list", "created_at"]
    list_filter = ["organization", "tags", "created_at"]
    search_fields = ["title", "description", "owner__email"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["owner", "organization"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    inlines = [TaskInline]

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description"),
        }),
        ("Ownership", {
            "fields": ("owner", "organization", "tags"),
        }),
        ("Metadata", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def owner_name(self, obj):
        return obj.owner.name
    owner_name.short_description = "Owner"
    owner_name.admin_order_field = "owner__name"

    def tag_list(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    tag_list.short_description = "Tags"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "owner", "organization"
        ).prefetch_related("tags")

    # Custom admin actions
    @admin.action(description="Mark selected projects as published")
    def make_published(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count} projects published.")

    actions = [make_published]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "organization", "role", "is_active"]
    list_filter = ["role", "is_active", "organization"]
    search_fields = ["email", "name"]
    list_editable = ["role", "is_active"]
    list_per_page = 50
```

---

## Best Practices

1. **Use `select_related` and `prefetch_related` on every query that touches relations** — `select_related` for ForeignKey/OneToOne (SQL JOIN), `prefetch_related` for ManyToMany and reverse ForeignKey (separate query). Check queries with `django-debug-toolbar`.

2. **Keep business logic in model methods or service functions, not in views** — views should handle HTTP, forms should handle validation, models/services should handle domain logic. This makes code testable without needing HTTP.

3. **Use `get_queryset()` for dynamic filtering instead of hardcoding querysets** — both in views and DRF ViewSets. This enables mixin composition and per-request filtering (e.g., by organization).

4. **Write data migrations for schema changes that require backfills** — never assume fields can be added as non-nullable without a migration to populate existing rows. Use `RunPython` with a reverse function.

5. **Configure Django REST Framework defaults in settings** — set `DEFAULT_PAGINATION_CLASS`, `DEFAULT_PERMISSION_CLASSES`, `DEFAULT_AUTHENTICATION_CLASSES` in `REST_FRAMEWORK` dict to avoid repeating yourself on each ViewSet.

6. **Use `TextChoices` / `IntegerChoices` for enum fields** — they integrate with admin filters, serializer validation, and migrations automatically. Avoid plain strings or integers for status/role fields.

7. **Index frequently queried fields** — add `db_index=True` on individual fields or use `Meta.indexes` for composite indexes. Add `UniqueConstraint` for business-rule uniqueness.

8. **Use Django's `transaction.atomic()` for multi-step writes** — wrap create/update sequences that must succeed or fail together. DRF's `perform_create` and `perform_update` are good places for this.

```python
from django.db import transaction

@transaction.atomic
def transfer_project(project, new_owner):
    old_owner = project.owner
    project.owner = new_owner
    project.save(update_fields=["owner"])
    AuditLog.objects.create(
        action="transfer",
        project=project,
        from_user=old_owner,
        to_user=new_owner,
    )
```

---

## Common Pitfalls

1. **N+1 queries** — accessing `project.owner.name` in a loop without `select_related("owner")` fires one query per iteration. Use `django-debug-toolbar` or `nplusone` to detect these. Always optimize queryset in `get_queryset()`.

2. **Importing models directly in data migrations** — models change over time, but migrations are frozen. Always use `apps.get_model("app_name", "ModelName")` inside `RunPython` functions, never `from myapp.models import Model`.

3. **Forgetting to call `full_clean()` in model saves** — Django's `save()` does NOT run validators by default. Only forms and serializers call `full_clean()`. If you save models directly, add explicit validation.

4. **Circular imports between apps** — referencing models across apps can cause import cycles. Use string references in ForeignKey: `models.ForeignKey("other_app.ModelName", ...)` instead of importing the class.

5. **Overusing signals for core logic** — signals make code harder to trace and debug. Use them for side effects (sending emails, cache invalidation), not for core domain logic. If logic should always run on save, override `save()` instead.

6. **Returning entire QuerySets from service functions** — QuerySets are lazy, which is usually good, but returning them from service layers can lead to unexpected queries executing in templates. Use `.values()`, `.values_list()`, or serialize to dicts when crossing layer boundaries.

---

## Related Skills

- `python` — Python language patterns and best practices
- `postgresql` — Database integration and query optimization
- `pytest` — Testing Django applications with pytest-django
