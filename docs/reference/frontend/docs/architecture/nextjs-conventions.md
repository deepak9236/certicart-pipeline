# Next.js 16+ & React 19 Conventions

> [!IMPORTANT]
> As referenced in [`AGENTS.md`](file:///Users/deepakkumar/kalpiCapital/certycart/AGENTS.md), this project runs **Next.js 16** and **React 19**.
> Several core APIs have breaking changes from Next.js 14/15 and older training data. Always follow the patterns documented below.

---

## 1. Dynamic Route Parameters are Asynchronous (`Promise`)

In Next.js 16, `params` and `searchParams` passed to pages, layouts, and route handlers are **Promises** and **MUST** be awaited or unwrapped with `React.use()`.

### ❌ Incorrect (Old Next.js pattern):
```tsx
// DO NOT DO THIS
export default function ProductPage({ params }: { params: { id: string } }) {
  return <div>Product ID: {params.id}</div>;
}
```

### ✅ Correct (Server Component):
```tsx
// In Server Components, async await the params Promise
interface PageProps {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function ProductPage({ params, searchParams }: PageProps) {
  const { id } = await params;
  const query = await searchParams;

  return <div>Product ID: {id}</div>;
}
```

### ✅ Correct (Client Component):
```tsx
"use client";

import { use } from "react";

interface ClientPageProps {
  params: Promise<{ id: string }>;
}

export default function ClientPage({ params }: ClientPageProps) {
  const { id } = use(params);
  return <div>Product ID: {id}</div>;
}
```

---

## 2. Server Components vs Client Components

- **Default to Server Components**: Keep pages and data-fetching components as Server Components.
- **Push `"use client"` to the leaves**: Only create Client Components when you need:
  - Interactive hooks: `useState`, `useReducer`, `useEffect`, `useRef`
  - Browser APIs: `window`, `localStorage`, `navigator`
  - Custom event handlers with state changes (`onClick`, `onChange`, `onSubmit`)
- **Wrap Client boundaries gracefully**: Pass Server Components as `children` to Client Component wrappers when needed.

---

## 3. Metadata Generation

`generateMetadata` also receives `params` and `searchParams` as Promises:

```tsx
import type { Metadata } from "next";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return {
    title: `Product - ${slug}`,
    description: `Details for product ${slug}`,
  };
}
```

---

## 4. React 19 & React Compiler

This project has `babel-plugin-react-compiler` enabled in dev/build.
- Manual `useMemo`, `useCallback`, and `React.memo` are rarely needed unless fine-tuning third-party libraries.
- Adhere strictly to the **Rules of React** (no mutating props/state, pure rendering, side-effects only in effects or handlers).

---

## 5. Next.js Documentation Reference

If you need deeper framework documentation on internal APIs, check local Next.js docs under:
[`node_modules/next/dist/docs/`](file:///Users/deepakkumar/kalpiCapital/certycart/node_modules/next/dist/docs/)
