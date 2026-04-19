# Frontend Styling — Accessibility Patterns


# Accessibility (a11y)

## When to Use

- Building new UI components (buttons, modals, forms, navigation)
- Reviewing existing components for WCAG 2.1 AA compliance
- Adding keyboard navigation to interactive elements
- Implementing focus management (modals, drawers, dropdown menus)
- Fixing accessibility audit findings

## When NOT to Use

- Backend API development (no UI surface)
- CLI tools (different accessibility model)
- Internal admin tools where the team explicitly opts out (document the decision)

---

## Core Principles

### Semantic HTML first

Use the right element before reaching for ARIA:

```tsx
// BAD — div pretending to be a button
<div onClick={handleClick} className="btn">Submit</div>

// GOOD — semantic button
<button onClick={handleClick} type="submit">Submit</button>
```

```tsx
// BAD — div pretending to be a nav
<div className="nav">
  <div onClick={() => navigate('/home')}>Home</div>
</div>

// GOOD — semantic nav + links
<nav aria-label="Main navigation">
  <a href="/home">Home</a>
  <a href="/about">About</a>
</nav>
```

### The first rule of ARIA

**"No ARIA is better than bad ARIA."** Only use ARIA when native HTML semantics can't express the relationship.

---

## Interactive Components

### Buttons and links

```tsx
// Button — performs an action
<button type="button" onClick={onDelete}>
  Delete Item
</button>

// Link — navigates somewhere
<a href="/settings">Settings</a>

// Icon-only button — MUST have accessible name
<button type="button" aria-label="Close dialog" onClick={onClose}>
  <XIcon aria-hidden="true" />
</button>
```

### Forms

```tsx
// Every input needs a label
<div>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-required="true"
    aria-invalid={!!errors.email}
    aria-describedby={errors.email ? 'email-error' : undefined}
  />
  {errors.email && (
    <p id="email-error" role="alert">
      {errors.email.message}
    </p>
  )}
</div>
```

```tsx
// Form with react-hook-form + shadcn/ui
<FormField
  control={form.control}
  name="email"
  render={({ field }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input {...field} type="email" />
      </FormControl>
      <FormMessage />
    </FormItem>
  )}
/>
```

### Modals / Dialogs

```tsx
// Using shadcn/ui Dialog (Radix-based — accessibility built in)
<Dialog>
  <DialogTrigger asChild>
    <Button>Open Settings</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Settings</DialogTitle>
      <DialogDescription>Update your preferences below.</DialogDescription>
    </DialogHeader>
    {/* Focus is automatically trapped inside */}
    <form>...</form>
  </DialogContent>
</Dialog>
```

For custom modals without Radix:

```tsx
// Focus trap + escape key + scroll lock
function Modal({ isOpen, onClose, title, children }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const el = ref.current;
    const previousFocus = document.activeElement as HTMLElement;

    // Focus first focusable element
    el?.querySelector<HTMLElement>('button, [href], input, select, textarea')?.focus();

    // Trap focus
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
      if (e.key !== 'Tab') return;
      // ... focus trap logic
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previousFocus?.focus(); // Restore focus on close
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div role="dialog" aria-modal="true" aria-labelledby="modal-title" ref={ref}>
      <h2 id="modal-title">{title}</h2>
      {children}
    </div>
  );
}
```

---

## Keyboard Navigation

### Required keyboard support

| Component | Keys |
|-----------|------|
| Button | `Enter`, `Space` to activate |
| Link | `Enter` to navigate |
| Modal | `Escape` to close, `Tab` to cycle focus |
| Dropdown | `Arrow Up/Down` to navigate, `Enter` to select, `Escape` to close |
| Tabs | `Arrow Left/Right` to switch, `Tab` to enter content |
| Checkbox | `Space` to toggle |

### Skip link

```tsx
// First element in <body> — lets keyboard users skip navigation
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:p-4 focus:bg-white focus:z-50">
  Skip to main content
</a>

// ... navigation ...

<main id="main-content">
  {/* Page content */}
</main>
```

### Focus visible

```css
/* Tailwind — ensure focus ring is visible */
@layer base {
  *:focus-visible {
    @apply outline-2 outline-offset-2 outline-blue-600;
  }
}
```

---

## Color and Contrast

### WCAG AA contrast ratios

| Text size | Minimum ratio |
|-----------|--------------|
| Normal text (<18px) | 4.5:1 |
| Large text (>=18px bold or >=24px) | 3:1 |
| UI components & graphics | 3:1 |

### Don't rely on color alone

```tsx
// BAD — only color indicates error
<input className={error ? 'border-red-500' : 'border-gray-300'} />

// GOOD — color + icon + text
<input
  className={error ? 'border-red-500' : 'border-gray-300'}
  aria-invalid={!!error}
  aria-describedby={error ? 'email-error' : undefined}
/>
{error && (
  <p id="email-error" role="alert" className="text-red-600 flex items-center gap-1">
    <AlertIcon aria-hidden="true" /> {error}
  </p>
)}
```

---

## Images and Media

```tsx
// Informative image — describe the content
<img src="/chart.png" alt="Revenue grew 25% from Q1 to Q2 2026" />

// Decorative image -- hide from screen readers
<img src="/decoration.svg" alt="" aria-hidden="true" />

// Complex image — link to full description
<figure>
  <img src="/architecture.png" alt="System architecture diagram" aria-describedby="arch-desc" />
  <figcaption id="arch-desc">
    Three-tier architecture: React frontend, FastAPI backend, PostgreSQL database.
  </figcaption>
</figure>
```

---

## Testing

### Automated

```bash
# axe-core via Playwright
npx playwright test --project=accessibility

# eslint-plugin-jsx-a11y (catches common issues at lint time)
npm install -D eslint-plugin-jsx-a11y
```

```typescript
// Playwright a11y test
import AxeBuilder from '@axe-core/playwright';

test('homepage has no a11y violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

### Manual checklist

- [ ] Tab through entire page — can you reach and operate every interactive element?
- [ ] Use screen reader (VoiceOver / NVDA) — does every element have an accessible name?
- [ ] Zoom to 200% — does layout remain usable?
- [ ] Disable CSS — does content order make sense?
- [ ] Check color contrast with browser DevTools

---

## Common Pitfalls

1. **`div` and `span` for interactive elements.** Use `button`, `a`, `input` instead. Divs have no keyboard support or ARIA roles by default.
2. **Missing `alt` text on images.** Every `<img>` needs `alt`. Decorative images use `alt=""`.
3. **Unlabeled form inputs.** Every input needs a `<label>` with matching `htmlFor`/`id`.
4. **Focus not managed in SPAs.** When navigating to a new page in React/Next.js, move focus to the main content area.
5. **`tabIndex > 0`.** Never use positive `tabIndex`. It breaks natural tab order. Use `0` (natural order) or `-1` (programmatic focus only).
6. **`aria-hidden="true"` on focusable elements.** Hidden elements that can receive focus confuse screen readers.
7. **Color-only error indicators.** Always pair color with text, icons, or patterns.

---

## Related Skills

- `react` — Component patterns that naturally support accessibility
- `shadcn-ui` — Radix-based components with built-in a11y
- `tailwind` — Utility classes for focus styles and screen-reader-only text
- `playwright` — E2E testing with axe-core accessibility checks
- `nextjs` — App Router patterns for accessible page transitions
