# API-Actions, Axios Interceptors & React Query Architecture

This document describes the data fetching, API calling, and caching architecture in **CertyCart**.

---

## 1. Directory Structure

```text
src/api-actions/
├── client.ts              # Axios instance with request & response interceptors and helper methods
├── provider.tsx            # TanStack React Query QueryClientProvider
└── hooks/                 # Reusable custom React Query hooks
    ├── index.ts           # Barrel exports for hooks
    ├── use-api-query.ts   # Generic useApiQuery & useApiMutation hooks
    └── use-products.ts    # Domain-specific query/mutation hooks
```

---

## 2. Axios Client with Interceptors (`src/api-actions/client.ts`)

- **Base URL**: Defaults to `process.env.NEXT_PUBLIC_API_URL || "/api"`.
- **Request Interceptor**:
  - Automatically attaches `Authorization: Bearer <token>` when tokens exist in browser storage.
  - Injects default headers (`Content-Type`, `Accept`).
- **Response Interceptor**:
  - Catches HTTP error status codes (401, 403, 500) and formats them into a normalized error object `{ status, message, data }`.
- **DRY Helper Methods**:
  - `api.get<T>(url, config)`
  - `api.post<T>(url, data, config)`
  - `api.put<T>(url, data, config)`
  - `api.patch<T>(url, data, config)`
  - `api.delete<T>(url, config)`

---

## 3. React Query Hooks in `src/api-actions/hooks/`

All queries and mutations must be wrapped in custom React Query hooks inside `src/api-actions/hooks/`.

### Generic Query Hook Example:
```tsx
import { useApiQuery } from "@/api-actions/hooks";

export function useProductDetails(productId: string) {
  return useApiQuery<ProductItem>(
    ["products", productId],
    `/products/${productId}`,
    undefined,
    { enabled: Boolean(productId) }
  );
}
```

### Generic Mutation Hook Example:
```tsx
import { useApiMutation } from "@/api-actions/hooks";

export function useCreateCertificate() {
  return useApiMutation<CertificateData, { title: string; issuer: string }>(
    [["certificates"], ["user-profile"]] // Automatically invalidates these queries on success
  );
}
```

---

## 4. Usage in Route Components

```tsx
"use client";

import { useProductDetails } from "@/api-actions/hooks/use-products";
import { Skeleton } from "@/components/ui/skeleton";

export function ProductDetailsView({ productId }: { productId: string }) {
  const { data: product, isLoading, error } = useProductDetails(productId);

  if (isLoading) return <Skeleton className="h-64 w-full" />;
  if (error) return <div className="text-destructive">Failed to load product</div>;
  if (!product) return <div>No product found</div>;

  return <div>{product.title}</div>;
}
```
