# Architecture Overview

This document provides a high-level overview of the **CertyCart** architecture, directory layout, and technology stack.

---

## 1. Directory Structure

```text
certycart/
├── .next/                   # Next.js build output (gitignored)
├── docs/                    # Project documentation & AI agent rules
├── public/                  # Static assets (images, SVGs, favicon)
├── src/
│   ├── app/                 # Next.js App Router (pages, layouts, route handlers)
│   │   ├── favicon.ico
│   │   ├── globals.css      # Tailwind v4 theme & CSS variable definitions
│   │   ├── layout.tsx       # Root layout (TooltipProvider, fonts, metadata)
│   │   └── page.tsx         # Home page entrypoint
│   ├── components/          # React components
│   │   ├── ui/              # Shadcn / Base UI primitives (button, dialog, card, etc.)
│   │   └── ...              # Domain/feature components
│   ├── hooks/               # Custom React hooks (e.g., use-mobile.ts)
│   └── lib/                 # Utilities, helpers, and client/server shared logic
│       └── utils.ts         # cn() className merger (clsx + tailwind-merge)
├── components.json          # Shadcn UI configuration (base-luma, Base UI)
├── eslint.config.mjs        # Flat ESLint configuration
├── next.config.ts           # Next.js configuration
├── package.json             # Dependencies and npm scripts
├── postcss.config.mjs       # PostCSS config for Tailwind v4
└── tsconfig.json            # TypeScript path aliases & strict compiler options
```

---

## 2. Core Technology Stack

| Layer | Technology | Version | Notes |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | `16.x` | Turbopack dev, RSC by default, Async params |
| **UI Library** | React | `19.x` | React 19 + React Compiler enabled |
| **Styling** | Tailwind CSS | `v4.x` | CSS-first configuration via `@theme` |
| **Component Kit** | Shadcn UI (`base-luma`) | `@shadcn/react` | Built on `@base-ui/react` |
| **Icons** | Lucide React | `^1.34.0` | Standard SVG icon set |
| **Type Safety** | TypeScript | `^5.x` | Strict type checking, `@/*` path aliases |

---

## 3. Path Aliases

Standard path aliases configured in [`tsconfig.json`](file:///Users/deepakkumar/kalpiCapital/certycart/tsconfig.json):

```typescript
import { Button } from "@/components/ui/button"  // Points to src/components/ui/button
import { cn } from "@/lib/utils"                 // Points to src/lib/utils
import { useIsMobile } from "@/hooks/use-mobile" // Points to src/hooks/use-mobile
```

---

## 4. Key Architectural Patterns

1. **Server-First Mindset**: By default, components in `src/app/` are React Server Components (RSC). Only mark components with `"use client"` when state, effects, or browser event listeners are strictly necessary.
2. **Atomic UI Primitives**: All base UI components reside in `src/components/ui/`. Domain-specific components should compose these primitives rather than reinventing styles.
3. **Strict CSS Variables**: Colors and theme tokens are defined in [`src/app/globals.css`](file:///Users/deepakkumar/kalpiCapital/certycart/src/app/globals.css) using semantic tokens (`--background`, `--foreground`, `--primary`, `--muted`, etc.) ensuring consistent theming across light and dark modes.
