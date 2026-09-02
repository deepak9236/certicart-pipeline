# Feature Development Workflow

This document provides a step-by-step playbook for implementing new features, components, and pages in **CertyCart**.

---

## Step 1: Understand Requirements & Architecture
1. Identify the route and page structure needed (`src/app/<route>/page.tsx`).
2. Identify which data is static, server-fetched, or client-interactive.
3. Review existing UI components in [`src/components/ui/`](file:///Users/deepakkumar/kalpiCapital/certycart/src/components/ui/) to reuse existing primitives.

---

## Step 2: Build or Compose Components
1. If the feature requires reusable domain components, create them in `src/components/<feature-name>/`.
2. Follow naming standards (`kebab-case.tsx` file name, `PascalCase` exported function).
3. Use `cn()` from `@/lib/utils` for dynamic class names.
4. Compose pre-existing primitives (`Button`, `Card`, `Dialog`, `Input`, etc.).

---

## Step 3: Create the Route & Page
1. Create `src/app/<feature>/page.tsx`.
2. Keep the page as a **Server Component** by default.
3. If dynamic route parameters are used, declare `params: Promise<{ ... }>` and await them.
4. Add descriptive metadata with `export const metadata: Metadata = { ... }` or `generateMetadata`.

---

## Step 4: Add Interactivity & State
1. Isolate interactive elements into client components with `"use client"`.
2. Place client components in the same feature folder or in `src/components/`.
3. Wire mutations to Server Actions in `src/lib/actions/` or appropriate API routes.

---

## Step 5: Verification & Quality Assurance
Before finalizing changes:
1. **Run Linter**: Ensure no lint errors:
   ```bash
   npm run lint
   ```
2. **Type Check / Build**: Ensure build passes without errors:
   ```bash
   npm run build
   ```
3. **Verify in Browser**: Test layout responsiveness (mobile, tablet, desktop) and interactive states (hover, active, focus, disabled).
