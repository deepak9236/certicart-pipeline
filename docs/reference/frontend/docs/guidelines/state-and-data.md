# Data Flow, Server Actions & State Management

This document details how data should be fetched, mutated, and managed in **CertyCart**.

---

## 1. Server-Side Data Fetching (Recommended Default)

Fetch data directly in React Server Components using `async/await`:

```tsx
// src/app/products/page.tsx
interface Product {
  id: string;
  name: string;
  price: number;
}

async function getProducts(): Promise<Product[]> {
  // Direct DB call, ORM query, or fetch()
  const res = await fetch("https://api.example.com/products", {
    next: { revalidate: 60 }, // ISR caching
  });
  if (!res.ok) throw new Error("Failed to fetch products");
  return res.json();
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <div className="container py-8">
      <h1 className="text-2xl font-bold tracking-tight">Products</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        {products.map((p) => (
          <div key={p.id} className="p-4 border rounded-xl">
            <h3>{p.name}</h3>
            <p>${p.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 2. Mutations with Server Actions

Define Server Actions in dedicated action files or at the top of server files with `"use server"`:

```typescript
// src/lib/actions/cart.ts
"use server";

import { revalidatePath } from "next/cache";

export async function addToCart(formData: FormData) {
  const productId = formData.get("productId") as string;
  const quantity = Number(formData.get("quantity") || 1);

  // Perform database or session mutation
  // ...

  revalidatePath("/cart");
  return { success: true };
}
```

---

## 3. Client State Management

- Keep UI state (modal open/closed, tabs, search query input state) local with standard React hooks (`useState`, `useReducer`).
- For global client state, use React Context or lightweight state stores when necessary.
- For URL-driven state (pagination, filters, search terms), use `useSearchParams` and `useRouter` / `usePathname` to keep state shareable and bookmarkable.

---

## 4. Form Handling

Leverage standard HTML forms with Server Actions or React 19 `useActionState`:

```tsx
"use client";

import { useActionState } from "react";
import { addToCart } from "@/lib/actions/cart";
import { Button } from "@/components/ui/button";

export function AddToCartButton({ productId }: { productId: string }) {
  const [state, formAction, isPending] = useActionState(addToCart, null);

  return (
    <form action={formAction}>
      <input type="hidden" name="productId" value={productId} />
      <Button type="submit" disabled={isPending}>
        {isPending ? "Adding..." : "Add to Cart"}
      </Button>
    </form>
  );
}
```
