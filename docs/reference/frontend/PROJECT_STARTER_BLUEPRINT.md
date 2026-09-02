# Complete End-to-End Next.js 16 + React 19 + Shadcn + MCP Architectural Blueprint

> **Universal Master Reference & Autonomous Agent Execution Guide**  
> This file contains the complete, end-to-end setup, command sequences, multi-IDE MCP configurations, agent skill installations, architectural rules, code templates, and documentation standards. 
> 
> **How to Use in Any Future Project:**
> Provide this single file to any AI coding agent (Antigravity, Cursor, Claude Code, Copilot) with the prompt in [Section 9](#9-autonomous-agent-prompt-copy--paste). The agent will configure the entire repository autonomously.

---

## Table of Contents

1. [Technology Stack & Core Specifications](#1-technology-stack--core-specifications)
2. [Automated CLI Setup Sequence](#2-automated-cli-setup-sequence)
3. [MCP Server Integration (Antigravity, Cursor, VS Code, Claude Code)](#3-mcp-server-integration-antigravity-cursor-vs-code-claude-code)
4. [Aceternity UI & Multi-Registry Configuration](#4-aceternity-ui--multi-registry-configuration)
5. [Agent Skills Installation (`shadcn` & `frontend-design`)](#5-agent-skills-installation-shadcn--frontend-design)
6. [The 10 Mandatory Architectural Rules](#6-the-10-mandatory-architectural-rules)
7. [Complete Production-Ready Code Templates](#7-complete-production-ready-code-templates)
   - [7.1 Ambient Global Types (`src/types/*.d.ts`)](#71-ambient-global-types-srctypesdts)
   - [7.2 Axios Interceptors & React Query (`src/api-actions/`)](#72-axios-interceptors--react-query-srcapi-actions)
   - [7.3 Zustand Client Store (`src/store/`)](#73-zustand-client-store-srcstore)
   - [7.4 Single Unified Provider (`src/providers/index.tsx`)](#74-single-unified-provider-srcprovidersindextsx)
   - [7.5 Root Layout (`src/app/layout.tsx`)](#75-root-layout-srcapplayouttsx)
   - [7.6 React 19 Safe Responsive Hook (`src/hooks/use-mobile.ts`)](#76-react-19-safe-responsive-hook-srchooksuse-mobilets)
   - [7.7 Next.js Configuration with Image Hostnames (`next.config.ts`)](#77-nextjs-configuration-with-image-hostnames-nextconfigts)
   - [7.8 Tailwind CSS v4 Theme Tokens (`src/app/globals.css`)](#78-tailwind-css-v4-theme-tokens-srcappglobalscss)
8. [Documentation Architecture (`docs/` Structure)](#8-documentation-architecture-docs-structure)
9. [Autonomous Agent Prompt (Copy & Paste)](#9-autonomous-agent-prompt-copy--paste)

---

## 1. Technology Stack & Core Specifications

| Layer | Technology | Version | Key Capability |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | `16.x` | Turbopack, React Server Components (RSC), Async route params |
| **Runtime / UI** | React & React DOM | `19.x` | React 19 Compiler, `useActionState`, `useSyncExternalStore` |
| **Styling** | Tailwind CSS & tw-animate | `v4.x` | CSS-first `@theme inline` design tokens, OKLCH color spaces |
| **Components** | Shadcn UI (`base-luma`) | Latest | `@base-ui/react` primitives (60+ accessible components) |
| **Registries** | Aceternity UI & Shadcn | Latest | `@aceternity` registry for high-end micro-interactions |
| **Motion** | Framer Motion & Motion | Latest | Spring transitions, layout animations, GPU-accelerated motion |
| **Icons** | Lucide React & Tabler Icons | Latest | Tree-shakeable SVG icon libraries |
| **State** | Zustand | `5.x` | Atomic selector client stores, zero boilerplate |
| **API Client** | Axios + TanStack React Query | `v5.x` | Request/response interceptors + server-state caching |
| **Type System** | TypeScript | `5.x` | Strict ambient `.d.ts` declarations without `export` |

---

## 2. Automated CLI Setup Sequence

Run these shell commands in the root of the project to initialize all libraries, components, skills, and tools:

```bash
# Step 1: Initialize Shadcn UI with Base UI preset
npx shadcn@latest init --preset b3dRdodCXC -y

# Step 2: Add full suite of Shadcn UI components
npx shadcn@latest add accordion alert alert-dialog aspect-ratio attachment avatar badge breadcrumb bubble button button-group calendar card carousel chart checkbox collapsible combobox command context-menu dialog direction drawer dropdown-menu empty field form hover-card input input-group input-otp item kbd label marker menubar message message-scroller native-select navigation-menu pagination popover progress questionnaire radio-group resizable scroll-area select separator sheet sidebar skeleton slider spinner switch table tabs textarea toast toggle toggle-group tooltip -y

# Step 3: Install State Management, HTTP, Query, Animation, and Icon Packages
npm install zustand axios @tanstack/react-query framer-motion motion @tabler/icons-react clsx tailwind-merge

# Step 4: Install official Shadcn AI agent skill
npx skills add https://github.com/shadcn-ui/ui --skill shadcn
```

---

## 3. MCP Server Integration (Antigravity, Cursor, VS Code, Claude Code)

Model Context Protocol (MCP) enables AI assistants to directly query, search, and install components from any configured registry in natural language.

### A. Antigravity IDE Configuration
Create or update `.agents/mcp_config.json`:
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

### B. Claude Code & Universal Config
Create or update `.mcp.json`:
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

### C. Cursor IDE Configuration
Create or update `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

### D. VS Code Configuration
Create or update `.vscode/mcp.json`:
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

---

## 4. Aceternity UI & Multi-Registry Configuration

To enable one-line component installation from Aceternity UI and other custom registries, configure `components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "base-luma",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {
    "@aceternity": "https://ui.aceternity.com/registry/{name}.json"
  }
}
```

Now any Aceternity component can be installed via CLI:
```bash
npx shadcn@latest add @aceternity/bento-grid
npx shadcn@latest add @aceternity/card-hover-effect
npx shadcn@latest add @aceternity/background-beams
```

---

## 5. Agent Skills Installation (`shadcn` & `frontend-design`)

Agent skills are specialized cheatsheets and rules stored in `.agents/skills/<skill_name>/SKILL.md` that AI agents automatically read and follow:

1. **Install official `shadcn` skill**:
   ```bash
   npx skills add https://github.com/shadcn-ui/ui --skill shadcn
   ```
   Stored at: `.agents/skills/shadcn/SKILL.md`

2. **Verify `frontend-design` skill**:
   Ensure `.agents/skills/frontend-design/SKILL.md` exists to enforce distinctive aesthetics, modern typography, rich micro-animations, and prevent generic "template" looks.

---

## 6. The 10 Mandatory Architectural Rules

All AI assistants and human developers working in the codebase **MUST** obey these 10 rules:

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        CBRTYCART MANDATORY ARCHITECTURE                           │
├───────────────────────────────────────────────────────────────────────────────────┤
│ 1. DRY (Don't Repeat Yourself)      │ Reuse UI, state, API helpers & queries     │
│ 2. Route _components/ Isolation     │ Local components in private _components/    │
│ 3. Ambient Types in src/types/      │ *.d.ts files WITHOUT export/import          │
│ 4. Zustand State Management         │ Atomic selector client stores in src/store/ │
│ 5. API Actions & React Query        │ Centralized Axios in src/api-actions/       │
│ 6. Single Global Provider           │ One <AppProvider> in src/app/layout.tsx     │
│ 7. Shadcn UI & Skill Standards      │ gap-* (no space-x), size-*, cn(), FieldGroup│
│ 8. Global CSS Color Scheme          │ Semantic tokens (bg-background, bg-primary) │
│ 9. Next.js 16+ Dynamic Parameters   │ Await Promise params & searchParams         │
│ 10. Universal Relative Paths        │ No local absolute machine paths             │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Rule 1: DRY (Don't Repeat Yourself)
Never duplicate UI elements, forms, queries, mutations, or utility logic. Always reuse the 60+ pre-installed components in `src/components/ui/`.

### Rule 2: Route `_components/` Isolation
Every route or collection that contains private UI components MUST place them inside a `_components/` folder:
- **Correct**: `src/app/products/_components/product-card.tsx`
- **Incorrect**: `src/app/products/product-card.tsx` or `src/components/product-card.tsx`

### Rule 3: Ambient Global `.d.ts` Types in `src/types/`
Define project data models, entities, and interfaces inside `src/types/*.d.ts` **WITHOUT using `export` or `import`**. TypeScript registers them globally.
- **Correct**:
  ```typescript
  // src/types/products.d.ts
  interface Product {
    id: string;
    name: string;
    price: number;
  }
  ```
- **Incorrect**:
  ```typescript
  export interface Product { ... } // ❌ Do not export!
  ```

### Rule 4: Client State with Zustand
Place all Zustand stores in `src/store/`. Always use atomic selector hooks:
```tsx
const items = useCartStore((state) => state.items);
const addItem = useCartStore((state) => state.addItem);
```

### Rule 5: API Actions, Axios Interceptors & React Query
- Centralized Axios client with request & response interceptors lives in `src/api-actions/client.ts`.
- Place all React Query hooks in `src/api-actions/hooks/`.
- Never call raw `fetch()` or `axios.get()` inside page components.

### Rule 6: Single Unified Global Provider
- In `src/app/layout.tsx`, use **ONLY ONE** composite `<AppProvider>` from `src/providers/index.tsx`.
- All sub-providers (`ApiQueryProvider`, `TooltipProvider`, theme, auth) **MUST** be composed inside `src/providers/index.tsx`.
- **Never add multiple individual providers into `layout.tsx`**.

### Rule 7: Shadcn UI & Skill Standards
- Follow `.agents/skills/shadcn/SKILL.md`.
- Use `gap-*` (flex/grid) instead of `space-x-*` / `space-y-*`.
- Use `size-*` for equal width and height (`size-4`, `size-10`).
- Use `cn()` from `@/lib/utils` for conditional classes.
- Forms use `FieldGroup` + `Field`.
- Proper part composition (e.g. `CardHeader` + `CardTitle` + `CardContent` + `CardFooter`).

### Rule 8: Global CSS Color Scheme & Semantic Tokens
- **ALWAYS** use semantic CSS tokens defined in `src/app/globals.css`:
  - Backgrounds: `bg-background`, `bg-card`, `bg-popover`, `bg-muted`, `bg-primary`, `bg-secondary`, `bg-accent`
  - Text: `text-foreground`, `text-muted-foreground`, `text-primary-foreground`, `text-card-foreground`
  - Borders & Rings: `border-border`, `border-input`, `ring-ring`
- **NEVER** hardcode arbitrary colors or raw hex values (`#10b981`, `bg-blue-500`).

### Rule 9: Next.js 16+ Dynamic Parameters
Page and layout `params` and `searchParams` are Promises in Next.js 16+ and **MUST** be awaited:
```tsx
// src/app/products/[id]/page.tsx
export default async function ProductPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <div>Product ID: {id}</div>;
}
```

### Rule 10: Universal Relative Paths
Never use machine-specific absolute file paths (`/Users/...` or `C:\...`) in code or documentation. Always use clean relative paths for developer portability.

---

## 7. Complete Production-Ready Code Templates

### 7.1 Ambient Global Types (`src/types/*.d.ts`)

#### `src/types/global.d.ts`
```typescript
/**
 * Global Ambient System & API Types
 * Do NOT use 'export' or 'import' in this file.
 */
interface ApiResponse<T = unknown> {
  success: boolean;
  message?: string;
  data: T;
  statusCode?: number;
}

interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMeta;
}

interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string;
  role: "admin" | "merchant" | "user";
  createdAt: string;
}
```

#### `src/types/store.d.ts`
```typescript
/**
 * Global Ambient Store Types
 * Do NOT use 'export' or 'import' in this file.
 */
interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  imageUrl?: string;
  sku?: string;
}

interface CartStoreState {
  items: CartItem[];
  isOpen: boolean;
  totalQuantity: number;
  totalAmount: number;
  addItem: (item: Omit<CartItem, "quantity"> & { quantity?: number }) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  toggleCart: () => void;
  setCartOpen: (open: boolean) => void;
}
```

---

### 7.2 Axios Interceptors & React Query (`src/api-actions/`)

#### `src/api-actions/client.ts`
```typescript
import axios, { type AxiosInstance, type AxiosRequestConfig, type InternalAxiosRequestConfig } from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request Interceptor: Attach Auth Tokens
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Normalize Errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message || "An unexpected error occurred";

    if (status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      // Optional: window.location.href = "/login";
    }

    return Promise.reject({
      status: status || 0,
      message,
      data: error.response?.data || null,
    });
  }
);

// DRY Generic Request Helpers
export const api = {
  get: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<ApiResponse<T>>(url, config).then((res) => res.data),
  post: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.post<ApiResponse<T>>(url, data, config).then((res) => res.data),
  put: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.put<ApiResponse<T>>(url, data, config).then((res) => res.data),
  patch: <T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
    apiClient.patch<ApiResponse<T>>(url, data, config).then((res) => res.data),
  delete: <T = unknown>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<ApiResponse<T>>(url, config).then((res) => res.data),
};
```

#### `src/api-actions/provider.tsx`
```tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

export function ApiQueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes fresh
            gcTime: 1000 * 60 * 30,    // 30 minutes garbage collect
            refetchOnWindowFocus: false,
            retry: (failureCount, error: any) => {
              if (error?.status === 404 || error?.status === 401 || error?.status === 403) return false;
              return failureCount < 2;
            },
          },
        },
      })
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
```

#### `src/api-actions/hooks/use-api-query.ts`
```typescript
"use client";

import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from "@tanstack/react-query";
import { api } from "../client";

export function useApiQuery<TData = unknown>(
  key: (string | number | Record<string, unknown>)[],
  url: string,
  options?: Omit<UseQueryOptions<ApiResponse<TData>, Error, TData>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: key,
    queryFn: () => api.get<TData>(url),
    select: (res) => res.data,
    ...options,
  });
}

export function useApiMutation<TData = unknown, TVariables = unknown>(
  url: string,
  method: "post" | "put" | "patch" | "delete" = "post",
  options?: UseMutationOptions<ApiResponse<TData>, Error, TVariables>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (variables: TVariables) => {
      if (method === "delete") return api.delete<TData>(url);
      return api[method]<TData>(url, variables);
    },
    ...options,
    onSuccess: (data, variables, context) => {
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });
}
```

#### `src/api-actions/hooks/index.ts`
```typescript
export * from "./use-api-query";
```

---

### 7.3 Zustand Client Store (`src/store/`)

#### `src/store/use-cart-store.ts`
```typescript
import { create } from "zustand";

const calculateTotals = (items: CartItem[]) => {
  return items.reduce(
    (acc, item) => ({
      totalQuantity: acc.totalQuantity + item.quantity,
      totalAmount: acc.totalAmount + item.price * item.quantity,
    }),
    { totalQuantity: 0, totalAmount: 0 }
  );
};

export const useCartStore = create<CartStoreState>((set, get) => ({
  items: [],
  isOpen: false,
  totalQuantity: 0,
  totalAmount: 0,

  addItem: (item) => {
    const { items } = get();
    const existingIndex = items.findIndex((i) => i.id === item.id);
    const quantityToAdd = item.quantity || 1;

    let updatedItems: CartItem[];
    if (existingIndex > -1) {
      updatedItems = items.map((i, idx) =>
        idx === existingIndex ? { ...i, quantity: i.quantity + quantityToAdd } : i
      );
    } else {
      updatedItems = [...items, { ...item, quantity: quantityToAdd }];
    }

    const { totalQuantity, totalAmount } = calculateTotals(updatedItems);
    set({ items: updatedItems, totalQuantity, totalAmount });
  },

  removeItem: (id) => {
    const { items } = get();
    const updatedItems = items.filter((i) => i.id !== id);
    const { totalQuantity, totalAmount } = calculateTotals(updatedItems);
    set({ items: updatedItems, totalQuantity, totalAmount });
  },

  updateQuantity: (id, quantity) => {
    if (quantity <= 0) {
      get().removeItem(id);
      return;
    }
    const { items } = get();
    const updatedItems = items.map((i) => (i.id === id ? { ...i, quantity } : i));
    const { totalQuantity, totalAmount } = calculateTotals(updatedItems);
    set({ items: updatedItems, totalQuantity, totalAmount });
  },

  clearCart: () => set({ items: [], totalQuantity: 0, totalAmount: 0 }),
  toggleCart: () => set((state) => ({ isOpen: !state.isOpen })),
  setCartOpen: (open) => set({ isOpen: open }),
}));
```

#### `src/store/index.ts`
```typescript
export * from "./use-cart-store";
```

---

### 7.4 Single Unified Provider (`src/providers/index.tsx`)

```tsx
"use client";

import { type ReactNode } from "react";
import { ApiQueryProvider } from "@/api-actions/provider";
import { TooltipProvider } from "@/components/ui/tooltip";

export interface AppProviderProps {
  children: ReactNode;
}

export function AppProvider({ children }: AppProviderProps) {
  return (
    <ApiQueryProvider>
      <TooltipProvider>
        {children}
      </TooltipProvider>
    </ApiQueryProvider>
  );
}

export default AppProvider;
```

---

### 7.5 Root Layout (`src/app/layout.tsx`)

```tsx
import type { Metadata } from "next";
import { AppProvider } from "@/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "CertyCart — Cryptographic Authentication Commerce",
  description: "Next-generation authenticated luxury commerce with on-chain cryptographic proof.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased font-sans">
      <body className="min-h-full flex flex-col bg-background text-foreground selection:bg-primary/20 selection:text-primary">
        {/* Single composite provider wrapping entire application */}
        <AppProvider>
          {children}
        </AppProvider>
      </body>
    </html>
  );
}
```

---

### 7.6 React 19 Safe Responsive Hook (`src/hooks/use-mobile.ts`)

```typescript
import * as React from "react";

const MOBILE_BREAKPOINT = 768;

function subscribe(callback: () => void) {
  const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
  mql.addEventListener("change", callback);
  return () => mql.removeEventListener("change", callback);
}

function getSnapshot() {
  return window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`).matches;
}

function getServerSnapshot() {
  return false;
}

export function useIsMobile(): boolean {
  return React.useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
```

---

### 7.7 Next.js Configuration with Image Hostnames (`next.config.ts`)

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "assets.aceternity.com",
      },
    ],
  },
};

export default nextConfig;
```

---

### 7.8 Tailwind CSS v4 Theme Tokens (`src/app/globals.css`)

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) * 0.6);
  --radius-md: calc(var(--radius) * 0.8);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) * 1.4);
}

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.511 0.096 186.391);
  --primary-foreground: oklch(0.984 0.014 180.72);
  --secondary: oklch(0.967 0.001 286.375);
  --secondary-foreground: oklch(0.21 0.006 285.885);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.5rem;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.437 0.078 188.216);
  --primary-foreground: oklch(0.984 0.014 180.72);
  --secondary: oklch(0.274 0.006 286.033);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
}

@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## 8. Documentation Architecture (`docs/` Structure)

Maintain a clean, organized `docs/` hierarchy with relative links so all developers and AI agents can navigate the repository:

```text
docs/
├── README.md                                # Master documentation index
├── architecture/
│   ├── overview.md                          # High-level architecture & tech stack
│   ├── nextjs-conventions.md                # Next.js 16+ & React 19 conventions
│   ├── api-actions-and-queries.md           # Axios interceptors & TanStack React Query
│   ├── providers.md                         # Single unified AppProvider setup
│   └── state-management-zustand.md          # Zustand store architecture & selectors
├── guidelines/
│   ├── ai-rules.md                          # AI coding agent rules & guardrails
│   ├── components-and-ui.md                 # Shadcn Base UI & Tailwind CSS v4 tokens
│   ├── shadcn-mcp-and-aceternity.md         # Shadcn MCP server & Aceternity registry
│   └── state-and-data.md                    # Data mutation flows & validation
├── standards/
│   ├── dry-and-component-isolation.md       # DRY standard & route _components/
│   ├── types-and-dts.md                     # Ambient global .d.ts types (no export)
│   └── code-style-and-conventions.md        # Code formatting and import rules
└── workflows/
    └── feature-development.md               # Step-by-step feature workflow
```

---

## 9. Autonomous Agent Prompt (Copy & Paste)

Copy and paste this exact prompt into your AI agent at the start of any new project:

```markdown
Please set up and architect this repository following the end-to-end blueprint in PROJECT_STARTER_BLUEPRINT.md:
1. Run all setup CLI commands (Shadcn init with Base UI preset, add all 60+ UI components, install zustand, axios, @tanstack/react-query, framer-motion, @tabler/icons-react, and add the shadcn skill).
2. Configure MCP server JSON files for Antigravity (.agents/mcp_config.json), Cursor (.cursor/mcp.json), VS Code (.vscode/mcp.json), and Claude Code (.mcp.json).
3. Add the @aceternity registry to components.json and configure next.config.ts with remotePatterns and reactCompiler.
4. Establish the 10 Mandatory Architectural Rules: DRY practice, route _components/ isolation, ambient global .d.ts types in src/types/ without export, Zustand store in src/store/, Axios interceptors with React Query in src/api-actions/, a single unified <AppProvider> in src/providers/ wrapped in src/app/layout.tsx, strict semantic tokens from src/app/globals.css, and async Next.js 16 dynamic route params.
5. Create the complete directory structure and documentation tree in docs/.
6. Run npm run lint to verify zero errors and zero warnings.
```
