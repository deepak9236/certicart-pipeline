# Single Unified Global Provider (`AppProvider`)

This document outlines the architecture and rules for global React context providers in **CertyCart**.

---

## 1. The Single Global Provider Rule

> [!IMPORTANT]
> To prevent provider soup and scattered context nesting across different layouts, **`src/app/layout.tsx` must ONLY use one composite `<AppProvider>`** imported from `@/providers`.
>
> All client providers (TanStack React Query, Tooltip, Theme, Auth, Modal managers, etc.) **must be composed inside `src/providers/index.tsx`**.

---

## 2. Directory Structure

```text
src/
├── providers/
│   └── index.tsx            # Composite AppProvider exporting all composed contexts
└── app/
    └── layout.tsx           # Uses <AppProvider> directly around children
```

---

## 3. Composition Pattern (`src/providers/index.tsx`)

```tsx
"use client";

import { type ReactNode } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ApiQueryProvider } from "@/api-actions/provider";

interface AppProviderProps {
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
```

---

## 4. Usage in Root Layout (`src/app/layout.tsx`)

```tsx
import { AppProvider } from "@/providers";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AppProvider>
          {children}
        </AppProvider>
      </body>
    </html>
  );
}
```
