# TypeScript Ambient Types (`.d.ts`) Standards

This document specifies the global type declaration rules for the **CertyCart** codebase.

---

## 1. The Global `.d.ts` Rule

> [!IMPORTANT]
> All shared data models, API payloads, domain entities, and store states **MUST** be defined in `.d.ts` declaration files inside [`src/types/`](file:///Users/deepakkumar/kalpiCapital/certycart/src/types/).
> 
> **CRITICAL RULE**: Do **NOT** use `export` or `import` at the top level of `.d.ts` files in `src/types/`. When a `.d.ts` file contains no top-level `import` or `export`, TypeScript treats it as an **ambient declaration file**, automatically registering all types and interfaces globally across the entire project without needing any `import { ... }` statements!

---

## 2. Directory Layout for Types

```text
src/types/
├── global.d.ts         # Generic ApiResponse<T>, pagination, user entities, common primitives
├── store.d.ts          # Zustand store state & actions interfaces
├── products.d.ts       # Products, certificates, categories & inventory interfaces
└── order.d.ts          # Orders, checkout, shipping & payment payloads
```

---

## 3. Example Ambient Declaration Syntax

### ✅ Correct Pattern (`src/types/products.d.ts`):

```typescript
// Notice: NO "export" keyword!
interface CertificateData {
  certId: string;
  issuer: string;
  issueDate: string;
  verificationHash: string;
  status: "verified" | "pending" | "expired";
}

interface ProductItem {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  certificate?: CertificateData;
  categories: string[];
}
```

### ✅ Usage in Any Component / File:

```tsx
// src/app/products/_components/product-card.tsx
// Notice: NO "import { ProductItem } from '@/types/...' needed!

interface ProductCardProps {
  product: ProductItem; // 👈 Automatically available globally!
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <div className="p-4 border rounded-xl">
      <h3>{product.title}</h3>
      <span>{product.price} {product.currency}</span>
    </div>
  );
}
```

---

## 4. ❌ What to Avoid

```typescript
// ❌ DO NOT DO THIS in src/types/*.d.ts:
export interface ProductItem { ... } // "export" turns file into a module, breaking global scope!

// ❌ DO NOT DO THIS in components:
import { ProductItem } from "@/types/products"; // Unnecessary import!
```
