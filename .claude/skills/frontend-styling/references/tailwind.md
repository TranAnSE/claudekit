# Frontend Styling — Tailwind CSS Patterns


# Tailwind CSS

## When to Use

- Styling React/Next.js components
- Responsive design
- Rapid UI development

## When NOT to Use

- Backend-only projects with no frontend or UI layer
- Projects using CSS-in-JS solutions like styled-components or Emotion
- Non-web applications such as CLI tools, mobile native apps, or desktop utilities

---

## Core Patterns

### 1. Responsive Design

Tailwind uses a mobile-first breakpoint system. Styles without a prefix apply to all screen sizes; prefixed styles apply at that breakpoint and above.

| Breakpoint | Min Width | Typical Target |
|------------|-----------|----------------|
| `sm`       | 640px     | Large phones   |
| `md`       | 768px     | Tablets        |
| `lg`       | 1024px    | Laptops        |
| `xl`       | 1280px    | Desktops       |
| `2xl`      | 1536px    | Large screens  |

```tsx
// Mobile-first responsive text and spacing
function HeroSection() {
  return (
    <section className="px-4 py-8 sm:px-6 sm:py-12 md:px-8 md:py-16 lg:py-24">
      <h1 className="text-2xl font-bold sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl">
        Build faster with Tailwind
      </h1>
      <p className="mt-4 text-sm text-gray-600 sm:text-base md:text-lg lg:max-w-2xl">
        A utility-first CSS framework for rapid UI development.
      </p>
    </section>
  );
}
```

```tsx
// Responsive container with constrained width
function PageContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
      {children}
    </div>
  );
}
```

```tsx
// Responsive visibility - show/hide elements at breakpoints
function ResponsiveNav() {
  return (
    <nav>
      {/* Mobile hamburger - hidden on desktop */}
      <button className="block md:hidden">
        <MenuIcon />
      </button>
      {/* Desktop nav links - hidden on mobile */}
      <div className="hidden md:flex md:items-center md:gap-6">
        <a href="/about">About</a>
        <a href="/pricing">Pricing</a>
        <a href="/docs">Docs</a>
      </div>
    </nav>
  );
}
```

### 2. Dark Mode

**Class strategy** (recommended) -- toggle via a `dark` class on the `<html>` element:

```js
// tailwind.config.js
module.exports = {
  darkMode: "class",
};
```

```tsx
// Theme toggle component
function ThemeToggle() {
  const [dark, setDark] = useState(false);

  function toggle() {
    setDark(!dark);
    document.documentElement.classList.toggle("dark");
  }

  return (
    <button
      onClick={toggle}
      className="rounded-full p-2 text-gray-600 hover:bg-gray-100
                 dark:text-gray-300 dark:hover:bg-gray-800"
    >
      {dark ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
```

```tsx
// Dark mode with CSS variables for flexible theming
function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm
                    dark:border-gray-700 dark:bg-gray-900 dark:shadow-gray-900/20">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
        {title}
      </h3>
      <div className="mt-2 text-gray-600 dark:text-gray-400">
        {children}
      </div>
    </div>
  );
}
```

**Media strategy** -- follows the OS preference automatically:

```js
// tailwind.config.js
module.exports = {
  darkMode: "media",
};
```

**CSS variables approach** for more granular theme control:

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --primary: 221 83% 53%;
    --muted: 210 40% 96%;
  }

  .dark {
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --primary: 217 91% 60%;
    --muted: 217 33% 17%;
  }
}
```

```js
// tailwind.config.js -- reference the CSS variables
module.exports = {
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: "hsl(var(--primary))",
        muted: "hsl(var(--muted))",
      },
    },
  },
};
```

### 3. Layout Patterns

**Sidebar layout:**

```tsx
function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      {/* Sidebar - fixed width, scrollable */}
      <aside className="hidden w-64 flex-shrink-0 overflow-y-auto border-r
                        border-gray-200 bg-gray-50 p-4 dark:border-gray-700
                        dark:bg-gray-900 lg:block">
        <nav className="flex flex-col gap-1">
          <SidebarLink href="/dashboard" icon={<HomeIcon />} label="Home" />
          <SidebarLink href="/settings" icon={<GearIcon />} label="Settings" />
        </nav>
      </aside>
      {/* Main content - fills remaining space */}
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
```

**Card grid:**

```tsx
function CardGrid({ items }: { items: CardItem[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.id}
          className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm
                     transition-shadow hover:shadow-md dark:border-gray-700
                     dark:bg-gray-800"
        >
          <h3 className="font-medium text-gray-900 dark:text-gray-100">
            {item.title}
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {item.description}
          </p>
        </div>
      ))}
    </div>
  );
}
```

**Centered content with max-width:**

```tsx
function ArticleLayout({ children }: { children: React.ReactNode }) {
  return (
    <article className="mx-auto max-w-prose px-4 py-8">
      <div className="prose prose-gray dark:prose-invert lg:prose-lg">
        {children}
      </div>
    </article>
  );
}
```

**Sticky header with content scroll:**

```tsx
function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen flex-col">
      <header className="sticky top-0 z-40 flex h-16 items-center border-b
                         border-gray-200 bg-white/80 px-6 backdrop-blur-sm
                         dark:border-gray-800 dark:bg-gray-950/80">
        <Logo />
        <nav className="ml-auto flex items-center gap-4">
          <NavLinks />
        </nav>
      </header>
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
```

### 4. Component Styling

**Button variants using a helper:**

```tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-blue-600 text-white hover:bg-blue-700",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100",
        outline: "border border-gray-300 bg-transparent hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800",
        ghost: "hover:bg-gray-100 dark:hover:bg-gray-800",
        destructive: "bg-red-600 text-white hover:bg-red-700",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4",
        lg: "h-12 px-6 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

function Button({ className, variant, size, ...props }: ButtonProps) {
  return (
    <button className={cn(buttonVariants({ variant, size }), className)} {...props} />
  );
}
```

**Form input:**

```tsx
function FormInput({ label, error, ...props }: InputProps) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>
      <input
        className={cn(
          "block w-full rounded-md border px-3 py-2 text-sm shadow-sm",
          "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500",
          "dark:bg-gray-900 dark:text-gray-100 dark:placeholder:text-gray-500",
          error
            ? "border-red-500 focus:ring-red-500"
            : "border-gray-300 dark:border-gray-600"
        )}
        {...props}
      />
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}
```

**Navigation with active state:**

```tsx
function NavLink({ href, active, children }: NavLinkProps) {
  return (
    <a
      href={href}
      className={cn(
        "rounded-md px-3 py-2 text-sm font-medium transition-colors",
        active
          ? "bg-gray-900 text-white dark:bg-gray-100 dark:text-gray-900"
          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100"
      )}
    >
      {children}
    </a>
  );
}
```

### 5. Animations & Transitions

**Built-in animations:**

```tsx
// Spin for loading indicators
<svg className="h-5 w-5 animate-spin text-white" viewBox="0 0 24 24">...</svg>

// Pulse for skeleton loaders
function Skeleton() {
  return <div className="h-4 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />;
}

// Bounce for attention
<div className="animate-bounce">
  <ArrowDownIcon />
</div>

// Ping for notification badges
<span className="relative flex h-3 w-3">
  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75" />
  <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500" />
</span>
```

**Transitions for interactive elements:**

```tsx
// Smooth hover transitions
function HoverCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm transition-all
                    duration-200 ease-in-out hover:-translate-y-1 hover:shadow-lg
                    dark:border-gray-700 dark:bg-gray-800">
      {children}
    </div>
  );
}

// Color and opacity transitions
<button className="bg-blue-500 text-white transition-colors duration-150
                   hover:bg-blue-600 active:bg-blue-700">
  Submit
</button>

// Scale on hover
<div className="transform transition-transform duration-200 hover:scale-105">
  <img src={src} alt={alt} className="rounded-lg" />
</div>
```

**Custom keyframes in config:**

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.3s ease-out",
        "slide-in-right": "slide-in-right 0.3s ease-out",
        "scale-in": "scale-in 0.2s ease-out",
      },
    },
  },
};
```

```tsx
// Using custom animations
<div className="animate-fade-in">Content that fades in</div>
<aside className="animate-slide-in-right">Sidebar panel</aside>
```

### 6. Custom Theme

**Extending tailwind.config.js:**

```js
// tailwind.config.js
const { fontFamily } = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./src/**/*.{ts,tsx}", "./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        mono: ["JetBrains Mono", ...fontFamily.mono],
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
        128: "32rem",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.75rem" }],
      },
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require("@tailwindcss/forms"),
    require("@tailwindcss/container-queries"),
  ],
};
```

### 7. Performance

**Content configuration** -- ensure only used classes ship to production:

```js
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
};
```

**Avoid dynamic class construction** -- Tailwind cannot detect dynamically built class names:

```tsx
// BAD -- Tailwind will NOT include these classes
const color = "red";
<div className={`bg-${color}-500`}>...</div>

// GOOD -- use complete class names so Tailwind can detect them
const bgColor = isError ? "bg-red-500" : "bg-green-500";
<div className={bgColor}>...</div>
```

**Safelist for truly dynamic values:**

```js
// tailwind.config.js
module.exports = {
  safelist: [
    "bg-red-500",
    "bg-green-500",
    "bg-blue-500",
    { pattern: /^text-(red|green|blue)-(400|500|600)$/ },
  ],
};
```

**Keep class strings readable with cn():**

```ts
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// Composing classes cleanly
<div className={cn(
  "rounded-lg border p-4",
  isActive && "border-blue-500 bg-blue-50",
  isDisabled && "pointer-events-none opacity-50",
  className
)}>
```

---

## Best Practices

1. **Mobile-first always** -- write base styles for mobile, then layer breakpoint prefixes for larger screens. Never design desktop-down.
2. **Use the spacing scale consistently** -- stick to Tailwind's default scale (4, 8, 12, 16...) rather than arbitrary values. Use `space-y-*` and `gap-*` instead of individual margins.
3. **Extract repeated patterns to components** -- when the same set of classes appears three or more times, create a React component rather than duplicating the class string.
4. **Use `@apply` sparingly** -- only for styles that cannot live in a component, such as global prose styles or third-party element overrides. Overusing `@apply` defeats the utility-first approach.
5. **Prefer `cn()` / `twMerge` for conditional classes** -- avoids class conflicts and keeps logic readable compared to string template concatenation.
6. **Use CSS variables for theme tokens** -- allows runtime theme switching and integrates well with dark mode, while keeping Tailwind as the styling layer.
7. **Group related utilities logically** -- order classes as: layout, sizing, spacing, typography, colors, borders, effects, transitions. Consistent ordering improves readability.
8. **Enable the typography plugin for prose content** -- `@tailwindcss/typography` provides sensible defaults for rendered markdown or CMS content without manual styling.

## Common Pitfalls

1. **Dynamic class name construction** -- `bg-${color}-500` will not work because Tailwind scans source files statically. Always use complete, literal class names.
2. **Forgetting content paths** -- if a class is not being generated, check that `content` in `tailwind.config.js` includes all files where Tailwind classes are used, including component libraries.
3. **Class conflicts without twMerge** -- `className="p-4 p-6"` applies both; the result depends on CSS source order, not the order in the string. Use `twMerge` to resolve conflicts predictably.
4. **Overusing arbitrary values** -- `w-[347px]` bypasses the design system. If you find many arbitrary values, extend the theme instead.
5. **Not testing responsive breakpoints** -- always verify layouts at each breakpoint. Use browser dev tools' responsive mode or resize the viewport during development.
6. **Ignoring dark mode from the start** -- adding dark mode later requires touching every component. Apply `dark:` variants alongside initial styling to avoid large retrofits.

## Related Skills

- `shadcn-ui` - Component library built on Radix primitives with Tailwind styling
- `react` - React component patterns and best practices
- `nextjs` - Next.js framework with built-in Tailwind support
