# CertyCart Documentation & AI Agent Context

Welcome to the **CertyCart** architecture and developer documentation. This documentation is structured for both human engineers and AI coding assistants to quickly understand the codebase architecture, modern Next.js 16 / React 19 conventions, UI component usage, Zustand store, Axios + React Query, ambient `.d.ts` types, and standard development workflows.

---

## ⚡ Fast Navigation for Developers & AI Agents

When working on a task, inspect the relevant documentation first to adhere to repository conventions:

| What are you doing? | Read this file first |
| :--- | :--- |
| **Universal All-in-One Setup Blueprint** | [`PROJECT_STARTER_BLUEPRINT.md`](../PROJECT_STARTER_BLUEPRINT.md) |
| **System Overview & Tech Stack** | [`docs/architecture/overview.md`](architecture/overview.md) |
| **Next.js 16 & React 19 Rules** (Breaking changes, async params) | [`docs/architecture/nextjs-conventions.md`](architecture/nextjs-conventions.md) |
| **API Actions, Axios Interceptors & React Query** | [`docs/architecture/api-actions-and-queries.md`](architecture/api-actions-and-queries.md) |
| **Single Global Provider (`AppProvider`)** | [`docs/architecture/providers.md`](architecture/providers.md) |
| **Zustand State Management** | [`docs/architecture/state-management-zustand.md`](architecture/state-management-zustand.md) |
| **AI Assistant Rules & Guardrails** | [`docs/guidelines/ai-rules.md`](guidelines/ai-rules.md) |
| **DRY Principles & Route `_components/`** | [`docs/standards/dry-and-component-isolation.md`](standards/dry-and-component-isolation.md) |
| **Global Ambient Types (`.d.ts` without export)** | [`docs/standards/types-and-dts.md`](standards/types-and-dts.md) |
| **UI Components (Shadcn + Base UI + Tailwind v4)** | [`docs/guidelines/components-and-ui.md`](guidelines/components-and-ui.md) |
| **Shadcn MCP & Aceternity UI Registry** | [`docs/guidelines/shadcn-mcp-and-aceternity.md`](guidelines/shadcn-mcp-and-aceternity.md) |
| **Data Fetching, Server Actions & Forms** | [`docs/guidelines/state-and-data.md`](guidelines/state-and-data.md) |
| **Code Style, TypeScript & Naming Conventions** | [`docs/standards/code-style-and-conventions.md`](standards/code-style-and-conventions.md) |
| **Adding a New Feature / Page Step-by-Step** | [`docs/workflows/feature-development.md`](workflows/feature-development.md) |

---

## 📁 Documentation Structure

```text
docs/
├── README.md                                # This index and fast entrypoint
├── architecture/
│   ├── overview.md                          # Project overview, tech stack & directory tree
│   ├── nextjs-conventions.md                # Next.js 16+ & React 19 conventions (Async params, RSC)
│   ├── api-actions-and-queries.md           # Axios interceptors & TanStack React Query hooks
│   ├── providers.md                         # Single unified AppProvider architecture
│   └── state-management-zustand.md          # Zustand store architecture & selectors
├── guidelines/
│   ├── ai-rules.md                          # Critical guardrails & instructions for AI models
│   ├── components-and-ui.md                 # Shadcn Base UI & Tailwind CSS v4 guidelines
│   ├── shadcn-mcp-and-aceternity.md         # Shadcn MCP server & Aceternity UI registry guide
│   └── state-and-data.md                    # Data flow, Server Actions, and validation
├── standards/
│   ├── dry-and-component-isolation.md       # DRY standard & mandatory route _components/
│   ├── types-and-dts.md                     # Ambient global .d.ts types (no export keyword)
│   └── code-style-and-conventions.md        # TypeScript standards, naming rules, and imports
└── workflows/
    └── feature-development.md               # End-to-end guide for creating new features
```

---

## 🚀 Core Architecture Highlights

- **Framework**: Next.js 16 (App Router)
- **UI System**: shadcn/ui (`base-luma` style built on `@base-ui/react` + Tailwind CSS v4)
- **Aceternity UI**: Configured via `@aceternity` registry in `components.json` + `framer-motion`
- **MCP Server**: Configured for Antigravity (`.agents/mcp_config.json`), Cursor, VS Code, and Claude Code
- **Client State**: Zustand (`src/store/`)
- **Data Fetching / Queries**: Axios interceptor client + TanStack React Query (`src/api-actions/`)
- **Global Types**: TypeScript ambient declaration files in `src/types/*.d.ts` without `export`
- **Route Isolation**: Every route/collection with private UI components uses a `_components/` folder
- **Single Global Provider**: Root layout uses only `<AppProvider>` from `src/providers/`
- **DRY Standard**: Zero code duplication across UI, actions, and store
