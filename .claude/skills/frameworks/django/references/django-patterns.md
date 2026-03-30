# Django Patterns Quick Reference

## QuerySet Patterns

### select_related (FK/OneToOne - single JOIN)

```python
# BAD: N+1 queries
for order in Order.objects.all():
    print(order.customer.name)  # Hits DB each iteration

# GOOD: 1 query with JOIN
for order in Order.objects.select_related("customer"):
    print(order.customer.name)

# Chain through multiple FKs
Order.objects.select_related("customer__company")
```

### prefetch_related (M2M/reverse FK - separate query)

```python
# BAD: N+1 on reverse FK
for author in Author.objects.all():
    print(author.book_set.all())  # Query per author

# GOOD: 2 queries total
for author in Author.objects.prefetch_related("books"):
    print(author.books.all())

# Custom prefetch with filtering
from django.db.models import Prefetch

Author.objects.prefetch_related(
    Prefetch("books", queryset=Book.objects.filter(published=True), to_attr="published_books")
)
```

### F Objects (reference model fields in queries)

```python
from django.db.models import F

Product.objects.filter(stock__lt=F("reorder_level"))        # Compare fields
Product.objects.filter(id=1).update(stock=F("stock") - 1)   # Atomic update
Order.objects.filter(amount__gt=F("customer__credit_limit")) # Across relations
```

### Q Objects (complex lookups with OR/NOT)

```python
from django.db.models import Q

# OR
User.objects.filter(Q(role="admin") | Q(is_superuser=True))

# NOT
User.objects.filter(~Q(status="banned"))

# Complex combinations
User.objects.filter(
    (Q(role="admin") | Q(role="staff")) & ~Q(status="inactive")
)

# Dynamic query building
conditions = Q()
if name:    conditions &= Q(name__icontains=name)
if email:   conditions &= Q(email__icontains=email)
User.objects.filter(conditions)
```

### Subquery and OuterRef

```python
from django.db.models import Subquery, OuterRef, Exists

# Subquery: latest order date per customer
latest_order = Order.objects.filter(
    customer=OuterRef("pk")
).order_by("-created_at").values("created_at")[:1]

Customer.objects.annotate(last_order=Subquery(latest_order))

# Exists: customers with orders
Customer.objects.annotate(
    has_orders=Exists(Order.objects.filter(customer=OuterRef("pk")))
).filter(has_orders=True)
```

### Aggregation

```python
from django.db.models import Count, Sum, Avg

# Aggregate (returns dict)
Order.objects.aggregate(total=Sum("amount"), avg=Avg("amount"))

# Annotate (per-row)
Customer.objects.annotate(order_count=Count("orders"))
```

---

## Model Patterns

### Abstract Base Model

```python
class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # No DB table created

class Order(TimestampMixin):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Inherits created_at, updated_at
```

### Proxy Model (same table, different behavior)

```python
class PendingOrderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="pending")

class PendingOrder(Order):
    objects = PendingOrderManager()
    class Meta:
        proxy = True  # Same DB table as Order
```

### Custom Manager and QuerySet

```python
class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")

    def by_author(self, author):
        return self.filter(author=author)

class Article(models.Model):
    objects = PublishedQuerySet.as_manager()

# Chainable: Article.objects.published().by_author(user)
```

---

## View Patterns

### Class-Based View Mixins

| Mixin | Purpose |
|-------|---------|
| `LoginRequiredMixin` | Require authentication |
| `PermissionRequiredMixin` | Require specific permission |
| `UserPassesTestMixin` | Custom permission test |
| `FormView` | Handle form display + submission |
| `CreateView` / `UpdateView` | Model form CRUD |
| `ListView` / `DetailView` | Read operations |

```python
class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Order
    permission_required = "orders.view_order"
    paginate_by = 25

    def get_queryset(self):
        return super().get_queryset().filter(customer=self.request.user)
```

---

## Django REST Framework Patterns

### Nested Serializers

```python
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["street", "city", "zip_code"]

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = Customer
        fields = ["id", "name", "address"]

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(**address_data)
        return Customer.objects.create(address=address, **validated_data)
```

### Custom Permissions

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.is_staff

# Usage
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
```

### ViewSet Actions

```python
from rest_framework.decorators import action

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        order.cancel()
        return Response({"status": "cancelled"})

    @action(detail=False, methods=["get"])
    def summary(self, request):
        return Response(self.get_queryset().aggregate(total=Sum("amount"), count=Count("id")))
```

### Filtering (django-filter)

```python
class OrderFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["status", "customer"]
```
