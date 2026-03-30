# Tailwind CSS UI Pattern Recipes

Copy-paste patterns for common UI components. All examples use Tailwind v3+ utility classes.

---

## Responsive Navbar

```html
<nav class="bg-white shadow">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
    <div class="flex h-16 items-center justify-between">
      <div class="flex items-center gap-8">
        <a href="/" class="text-xl font-bold text-gray-900">Logo</a>
        <div class="hidden md:flex md:gap-6">
          <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Dashboard</a>
          <a href="#" class="text-sm font-medium text-gray-500 hover:text-gray-900">Projects</a>
          <a href="#" class="text-sm font-medium text-gray-500 hover:text-gray-900">Settings</a>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button class="rounded-full bg-gray-100 p-2 text-gray-600 hover:bg-gray-200">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0a3 3 0 11-6 0m6 0H9" />
          </svg>
        </button>
        <img class="h-8 w-8 rounded-full" src="https://via.placeholder.com/32" alt="Avatar" />
      </div>
      <!-- Mobile menu button -->
      <button class="md:hidden rounded p-2 text-gray-600 hover:bg-gray-100">
        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
    </div>
  </div>
</nav>
```

---

## Card Grid

```html
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
  <!-- Card -->
  <div class="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm
              transition hover:shadow-md">
    <img class="h-48 w-full object-cover" src="https://via.placeholder.com/400x200" alt="" />
    <div class="p-5">
      <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
      <p class="mt-2 text-sm text-gray-600">
        Brief description of the card content goes here.
      </p>
      <div class="mt-4 flex items-center justify-between">
        <span class="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5
                     text-xs font-medium text-blue-700">Category</span>
        <a href="#" class="text-sm font-medium text-blue-600 hover:text-blue-500">
          View details &rarr;
        </a>
      </div>
    </div>
  </div>
  <!-- Repeat cards... -->
</div>
```

---

## Hero Section

```html
<section class="bg-white">
  <div class="mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-2xl text-center">
      <span class="inline-block rounded-full bg-blue-50 px-3 py-1 text-sm
                   font-medium text-blue-700">New Release</span>
      <h1 class="mt-4 text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
        Build faster with modern tools
      </h1>
      <p class="mt-6 text-lg leading-8 text-gray-600">
        A concise value proposition that explains what the product does
        and why users should care.
      </p>
      <div class="mt-10 flex items-center justify-center gap-4">
        <a href="#" class="rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold
                         text-white shadow-sm hover:bg-blue-500">Get started</a>
        <a href="#" class="text-sm font-semibold text-gray-900 hover:text-gray-700">
          Learn more &rarr;
        </a>
      </div>
    </div>
  </div>
</section>
```

---

## Form Layout

```html
<form class="mx-auto max-w-lg space-y-6">
  <div>
    <label for="name" class="block text-sm font-medium text-gray-700">Full Name</label>
    <input type="text" id="name" name="name"
      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2
             text-sm shadow-sm placeholder:text-gray-400
             focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
  </div>

  <div>
    <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
    <input type="email" id="email" name="email"
      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2
             text-sm shadow-sm placeholder:text-gray-400
             focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500" />
    <p class="mt-1 text-sm text-gray-500">We'll never share your email.</p>
  </div>

  <div>
    <label for="message" class="block text-sm font-medium text-gray-700">Message</label>
    <textarea id="message" name="message" rows="4"
      class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2
             text-sm shadow-sm placeholder:text-gray-400
             focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"></textarea>
  </div>

  <div class="flex items-center justify-end gap-3">
    <button type="button" class="rounded-md px-4 py-2 text-sm font-medium
                                  text-gray-700 hover:bg-gray-50">Cancel</button>
    <button type="submit" class="rounded-md bg-blue-600 px-4 py-2 text-sm
                                  font-semibold text-white shadow-sm
                                  hover:bg-blue-500">Submit</button>
  </div>
</form>
```

---

## Modal Overlay

```html
<!-- Backdrop -->
<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
  <!-- Modal -->
  <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
    <div class="flex items-start justify-between">
      <h2 class="text-lg font-semibold text-gray-900">Confirm Action</h2>
      <button class="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    <p class="mt-3 text-sm text-gray-600">
      Are you sure you want to proceed? This action cannot be undone.
    </p>
    <div class="mt-6 flex justify-end gap-3">
      <button class="rounded-md px-4 py-2 text-sm font-medium text-gray-700
                     hover:bg-gray-50">Cancel</button>
      <button class="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold
                     text-white hover:bg-red-500">Delete</button>
    </div>
  </div>
</div>
```

---

## Sidebar Layout

```html
<div class="flex h-screen">
  <!-- Sidebar -->
  <aside class="hidden w-64 flex-shrink-0 border-r border-gray-200 bg-gray-50 lg:block">
    <div class="flex h-16 items-center px-6">
      <span class="text-lg font-bold text-gray-900">App Name</span>
    </div>
    <nav class="space-y-1 px-3 py-4">
      <a href="#" class="flex items-center gap-3 rounded-md bg-blue-50 px-3 py-2
                        text-sm font-medium text-blue-700">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0h4" />
        </svg>
        Dashboard
      </a>
      <a href="#" class="flex items-center gap-3 rounded-md px-3 py-2 text-sm
                        font-medium text-gray-700 hover:bg-gray-100">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
        </svg>
        Users
      </a>
      <a href="#" class="flex items-center gap-3 rounded-md px-3 py-2 text-sm
                        font-medium text-gray-700 hover:bg-gray-100">
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Settings
      </a>
    </nav>
  </aside>

  <!-- Main content -->
  <main class="flex-1 overflow-y-auto bg-white">
    <div class="px-6 py-8 lg:px-8">
      <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
      <div class="mt-6">
        <!-- Page content here -->
      </div>
    </div>
  </main>
</div>
```

---

## Tips

- Use `transition` and `hover:` for interactive feedback
- Use `focus-visible:` instead of `focus:` for keyboard-only focus rings
- Use `dark:` variants when supporting dark mode
- Prefer `gap-*` over margin utilities for flex/grid spacing
- Use `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8` as a standard container
