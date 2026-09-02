# AI Coding Agent Rules & Guardrails

This document outlines the strict protocol and requirements that AI assistants must follow when interacting with the **CertyCart** codebase.

---

## 1. Preserving `AGENTS.md` and Rules Blocks

- **Never remove `<!-- BEGIN:nextjs-agent-rules -->` blocks**: Next.js automatically maintains this block. Removing or corrupting it causes unnecessary diff noise and conflicts.
- Always keep diffs minimal, clean, and focused on the user's objective.

---

## 2. Core Architectural Mandates for AI Agents

1. **Follow the DRY Principle**:
   - Never duplicate code, logic, forms, or UI layouts.
   - Always reuse existing primitives in `src/components/ui/`.
2. **Mandatory `_components/` in Every Route / Collection**:
   - Any route or collection holding local components MUST place them in a `_components/` folder (e.g., `src/app/products/_components/`).
3. **Global Ambient Types in `src/types/`**:
   - Create type declaration files as `src/types/*.d.ts`.
   - **DO NOT** use `export` or `import` in `.d.ts` files inside `src/types/`. All types must be ambient and globally accessible.
4. **Client State Management with Zustand**:
   - Store definitions reside in `src/store/`.
   - Always use specific selector hooks to prevent unnecessary re-renders.
5. **API Actions & React Query via `src/api-actions/`**:
   - Use the centralized Axios instance with interceptors (`src/api-actions/client.ts`).
   - Place all React Query hooks in `src/api-actions/hooks/`.
6. **Single Global Provider**:
   - In `src/app/layout.tsx`, use ONLY one composite `<AppProvider>` from `src/providers/index.tsx`.
   - Never add multiple individual providers into `layout.tsx`.
7. **Shadcn UI Standards & Skill**:
   - Follow the installed **`shadcn` skill** (`.agents/skills/shadcn/SKILL.md`).
   - Use `gap-*` (flex/grid) instead of `space-x-*` / `space-y-*`.
   - Use `size-*` for equal width/height (`size-4`, `size-10`).
   - Use `cn()` for dynamic class merging.
8. **Global CSS Color Scheme**:
   - ALWAYS use semantic CSS tokens defined in `src/app/globals.css` (`bg-background`, `text-foreground`, `bg-card`, `bg-primary`, `text-primary-foreground`, `border-border`, etc.).
   - NEVER hardcode arbitrary colors.
9. **Next.js 16+ Dynamic Parameters**:
   - `params` and `searchParams` are Promises (`Promise<{ id: string }>`) and MUST be awaited.

---

## 3. Fast Decision Checklist for AI Agents

Before writing code or proposing edits, verify:

- [ ] Is this a new route with private components? If yes, did I create `_components/`?
- [ ] Are new types defined in `src/types/*.d.ts` without `export`?
- [ ] Is client state placed in a Zustand store in `src/store/`?
- [ ] Are data mutations and fetch queries using hooks from `src/api-actions/hooks/`?
- [ ] Is `src/app/layout.tsx` using only `<AppProvider>`?
- [ ] Are theme variables and colors using Tailwind v4 semantic tokens from `src/app/globals.css`?
- [ ] Does `npm run lint` and TypeScript check pass cleanly?
