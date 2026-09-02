# Code Style & Naming Conventions

This document defines the coding standards, TypeScript conventions, and file organization rules for **CertyCart**.

---

## 1. Naming Conventions

| Item | Convention | Example |
| :--- | :--- | :--- |
| **Component Files** | `kebab-case.tsx` | `src/components/product-card.tsx` |
| **Component Functions** | `PascalCase` | `export function ProductCard()` |
| **Hook Files** | `kebab-case.ts` with `use-` prefix | `src/hooks/use-cart-count.ts` |
| **Hook Functions** | `camelCase` with `use` prefix | `export function useCartCount()` |
| **Utility Files** | `kebab-case.ts` | `src/lib/format-currency.ts` |
| **Types & Interfaces** | `PascalCase` | `export interface CartItem { ... }` |
| **Constants** | `SCREAMING_SNAKE_CASE` | `export const MAX_CART_ITEMS = 50;` |

---

## 2. Component Organization & Export Patterns

- Prefer **named exports** for components, utilities, and hooks:
  ```tsx
  // ✅ Recommended
  export function HeroSection() { ... }
  
  // ⚠️ Only use default exports when required by Next.js conventions (page.tsx, layout.tsx, template.tsx)
  export default function Page() { ... }
  ```

---

## 3. TypeScript Rules

- **Strict Typing**: Avoid `any`. Use `unknown` with type narrowing if the type is indeterminate.
- **Explicit Props Interface**: Define props above the component:
  ```tsx
  interface MetricCardProps {
    title: string;
    value: string | number;
    trend?: "up" | "down" | "neutral";
    className?: string;
  }
  
  export function MetricCard({ title, value, trend = "neutral", className }: MetricCardProps) {
    // ...
  }
  ```
- **Async Next.js Props**: Always type App Router dynamic props as `Promise`:
  ```tsx
  interface PageProps {
    params: Promise<{ id: string }>;
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
  }
  ```

---

## 4. Import Ordering

Keep imports organized in logical groups separated by a blank line:

1. React & Next.js core modules (`react`, `next/...`)
2. Third-party packages (`lucide-react`, `date-fns`, etc.)
3. UI components (`@/components/ui/...`)
4. Custom components (`@/components/...`)
5. Hooks & Utilities (`@/hooks/...`, `@/lib/...`)
6. Types / Interfaces
