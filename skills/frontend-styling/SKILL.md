---
name: frontend-styling
description: >
  Use when styling web components with Tailwind CSS or ensuring accessibility compliance — including utility classes, responsive breakpoints, dark mode, WCAG, ARIA, aria-label, aria-describedby, screen reader, keyboard navigation, focus management, color contrast, alt text, semantic HTML, or skip links.
---

# Frontend Styling

## When to Use

- Styling React/Next.js components with Tailwind CSS utility classes
- Building responsive layouts, dark mode support, or design systems
- Ensuring WCAG 2.1 AA compliance for UI components
- Adding keyboard navigation, focus management, or screen reader support
- Fixing accessibility audit findings

## When NOT to Use

- Backend API development with no UI surface
- Component logic or state management — use `frontend`
- CLI tools (different accessibility model)

---

## Quick Reference

| Topic | Reference | Key features |
|-------|-----------|-------------|
| Tailwind CSS | `references/tailwind.md` | Utility classes, responsive, dark mode, cn(), twMerge, @apply |
| Accessibility | `references/accessibility.md` | WCAG, ARIA, keyboard nav, focus trapping, semantic HTML, alt text |

---

## Best Practices

1. **Mobile-first always.** Write base styles for mobile, layer breakpoint prefixes for larger screens.
2. **Use the spacing scale consistently.** Stick to Tailwind's default scale rather than arbitrary values.
3. **Extract repeated patterns to components** when the same classes appear three or more times.
4. **Prefer `cn()` / `twMerge` for conditional classes** to avoid class conflicts.
5. **Use CSS variables for theme tokens.**
6. **Use semantic HTML elements** — `button`, `a`, `input` instead of `div` and `span` for interactive elements.
7. **Every `<img>` needs `alt`.** Decorative images use `alt=""`.
8. **Never use `tabIndex > 0`.** It breaks natural tab order.

## Common Pitfalls

1. **Dynamic class name construction** — `bg-${color}-500` will not work with Tailwind's JIT compiler.
2. **Forgetting content paths in `tailwind.config.js`.**
3. **Class conflicts without twMerge.**
4. **Ignoring dark mode from the start.**
5. **`div` and `span` for interactive elements** — use semantic HTML instead.
6. **Missing `alt` text on images.**
7. **Unlabeled form inputs.**
8. **Focus not managed in SPAs** — especially modals, drawers, and dropdown menus.
9. **`aria-hidden="true"` on focusable elements.**
10. **Color-only error indicators** — always include text or icons alongside color changes.

---

## Related Skills

- `frontend` — React and Next.js component patterns
- `owasp` — Security aspects of frontend development
