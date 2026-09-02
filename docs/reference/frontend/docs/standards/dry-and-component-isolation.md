# DRY Principles & Route `_components` Architecture

This document defines mandatory architectural rules regarding code reuse (DRY) and route/collection component isolation for the **CertyCart** project.

---

## 1. The DRY (Don't Repeat Yourself) Standard

AI agents and developers **MUST** follow DRY practices across all layers of the application:

1. **Do not duplicate UI elements**:
   - Always leverage the 60+ pre-built primitives in [`src/components/ui/`](file:///Users/deepakkumar/kalpiCapital/certycart/src/components/ui/).
   - Extract recurring composite layouts (e.g., product card, cert badge, filter panel) into reusable components.
2. **Do not duplicate API logic**:
   - Never write raw `axios.get` / `fetch` calls directly inside page components.
   - Use [`src/api-actions/client.ts`](file:///Users/deepakkumar/kalpiCapital/certycart/src/api-actions/client.ts) helpers and React Query hooks from [`src/api-actions/hooks/`](file:///Users/deepakkumar/kalpiCapital/certycart/src/api-actions/hooks/).
3. **Do not duplicate state logic**:
   - Centralize shared client state in Zustand stores under [`src/store/`](file:///Users/deepakkumar/kalpiCapital/certycart/src/store/).
4. **Do not duplicate types**:
   - Centralize entity types in [`src/types/*.d.ts`](file:///Users/deepakkumar/kalpiCapital/certycart/src/types/) as global ambient types.

---

## 2. Mandatory `_components` in Every Route & Collection

In Next.js App Router, prefixing a folder with an underscore (`_`) marks it as a **private folder**, preventing it and its subfolders from being routed.

### Rule:
Every route folder (and collection folder) that contains route-specific components **MUST** place them inside a `_components/` directory.

### Directory Structure Example:

```text
src/app/
├── (shop)/
│   ├── products/
│   │   ├── _components/             # 👈 Mandatory for route-specific components
│   │   │   ├── product-grid.tsx
│   │   │   ├── product-filter-bar.tsx
│   │   │   └── product-sort-select.tsx
│   │   ├── [id]/
│   │   │   ├── _components/         # 👈 Route-specific components for product details
│   │   │   │   ├── product-gallery.tsx
│   │   │   │   ├── cert-verification-badge.tsx
│   │   │   │   └── add-to-cart-section.tsx
│   │   │   └── page.tsx
│   │   └── page.tsx
│   └── cart/
│       ├── _components/             # 👈 Route-specific components for cart
│       │   ├── cart-item-row.tsx
│       │   └── cart-summary-card.tsx
│       └── page.tsx
```

---

## 3. Decision Matrix: Where Should a Component Live?

| Component Scope | Location | Example |
| :--- | :--- | :--- |
| **Atomic UI Primitives** | `src/components/ui/` | `button.tsx`, `dialog.tsx`, `card.tsx` |
| **App-Wide Shared Components** | `src/components/common/` or `src/components/layout/` | `site-header.tsx`, `site-footer.tsx` |
| **Route/Collection-Specific Component** | `src/app/<route>/_components/` | `src/app/checkout/_components/payment-form.tsx` |
