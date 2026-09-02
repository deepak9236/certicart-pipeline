# Shadcn MCP Server & Aceternity UI Integration

This document outlines how the **Shadcn MCP Server** and **Aceternity UI** registry are configured and used in **CertyCart**.

---

## 1. Shadcn MCP Server Integration

The shadcn MCP server allows AI assistants in Antigravity IDE (and other MCP clients) to browse, search, and install components, blocks, and UI items directly using natural language.

### MCP Configuration Files:
- **Antigravity IDE**: `.agents/mcp_config.json`
- **Universal / Claude Code**: `.mcp.json`
- **Cursor**: `.cursor/mcp.json`
- **VS Code**: `.vscode/mcp.json`

### Configuration Content:
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

## 2. Aceternity UI Registry in `components.json`

Aceternity UI provides a shadcn-compatible registry. It is configured in `components.json` under `registries`:

```json
{
  "registries": {
    "@aceternity": "https://ui.aceternity.com/registry/{name}.json"
  }
}
```

---

## 3. How to Install Components

### Via Natural Language (MCP):
- *"Add 3d-card from Aceternity registry"*
- *"Install hero-parallax component from @aceternity"*
- *"Add sparkler effect from aceternity"*

### Via CLI:
```bash
# Using namespace syntax configured in components.json:
npx shadcn@latest add @aceternity/3d-card

# Or direct URL:
npx shadcn@latest add https://ui.aceternity.com/registry/3d-card.json
```

---

## 4. Dependencies Installed for Aceternity UI
Aceternity UI animations and visual components rely on:
- `framer-motion` & `motion`
- `@tabler/icons-react` & `lucide-react`
- `clsx` & `tailwind-merge` (`cn` helper from `@/lib/utils`)
