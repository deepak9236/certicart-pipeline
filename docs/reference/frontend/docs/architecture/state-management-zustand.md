# State Management with Zustand

This document outlines state management conventions and rules using **Zustand** in **CertyCart**.

---

## 1. Directory Structure

```text
src/
├── types/
│   └── store.d.ts           # Global ambient store types (without export)
└── store/
    ├── index.ts             # Store barrel export
    ├── use-cart-store.ts    # Shopping cart, items, checkout states
    └── use-ui-store.ts      # Modal states, drawer toggles, UI preferences
```

---

## 2. Store Creation Pattern

1. **Ambient Typing**: State and action types live in `src/types/store.d.ts` without `export`.
2. **Atomic Updaters**: Set actions mutate state immutably using `set((state) => ({ ... }))`.
3. **DRY Selectors**: Components should select only the exact slices they need to minimize re-renders.

### Example:

```typescript
// src/store/use-cart-store.ts
import { create } from "zustand";

export const useCartStore = create<CartStore>((set) => ({
  items: [],
  isOpen: false,
  totalAmount: 0,
  totalQuantity: 0,

  addItem: (product, quantity = 1) =>
    set((state) => {
      // ... immutable addition logic
    }),

  removeItem: (productId) =>
    set((state) => {
      // ... immutable removal logic
    }),

  clearCart: () => set({ items: [], totalAmount: 0, totalQuantity: 0 }),
  toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),
  setCartOpen: (open) => set({ isOpen: open }),
}));
```

---

## 3. Best Practices for Consuming Stores in Components

### ✅ Select specific slices (Prevents unnecessary re-renders):
```tsx
"use client";

import { useCartStore } from "@/store";

export function CartBadge() {
  // Only re-renders when totalQuantity changes
  const totalQuantity = useCartStore((state) => state.totalQuantity);
  const toggleCart = useCartStore((state) => state.toggleCart);

  return (
    <button onClick={toggleCart} className="relative">
      <span>Cart ({totalQuantity})</span>
    </button>
  );
}
```

### ❌ Avoid whole-store subscriptions:
```tsx
// ❌ Avoid this unless you need all properties
const store = useCartStore();
```
