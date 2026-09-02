# UI & Component Guidelines

CertyCart uses **Shadcn UI (`base-luma` style)** built on top of **Base UI (`@base-ui/react`)** and styled using **Tailwind CSS v4**.

---

## 1. Official `shadcn` Skill Installed

The official **`shadcn` skill** is installed at `.agents/skills/shadcn/SKILL.md`.

### Core Rules from the Shadcn Skill:
1. **Use semantic colors**: Always use `bg-primary`, `text-primary-foreground`, `bg-background`, `text-foreground`, `border-border`, etc. Never use raw hardcoded hex or arbitrary colors.
2. **Spacing**: Use `flex flex-col gap-*` or `grid gap-*`. **Never use `space-x-*` or `space-y-*`**.
3. **Dimensions**: Use `size-*` when width and height are equal (`size-4`, `size-10`).
4. **Conditional classes**: Use `cn(...)` from `@/lib/utils`.
5. **Form layout**: Use `FieldGroup` + `Field`.

---

## 2. Available UI Components (`src/components/ui/`)

All standard Shadcn UI components are pre-installed in `src/components/ui/`.

### Common Components & Imports:

```tsx
// Buttons & Badges
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

// Layout & Cards
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

// Forms & Inputs
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Field } from "@/components/ui/field";

// Overlays & Dialogs
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

// Feedback & Loading
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { toast } from "@/components/ui/toast";

// Data Display
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
```

---

## 3. Global CSS Color Scheme & Theme Tokens

All colors are dynamically configured in `src/app/globals.css` using OKLCH and CSS variables:

| Semantic Class | Usage |
| :--- | :--- |
| `bg-background` / `text-foreground` | App background and main text |
| `bg-card` / `text-card-foreground` | Surfaces and cards |
| `bg-primary` / `text-primary-foreground` | Primary brand buttons, active badges, highlights |
| `bg-secondary` / `text-secondary-foreground` | Secondary buttons and chips |
| `bg-muted` / `text-muted-foreground` | Subdued text, subtle backgrounds, table headers |
| `bg-accent` / `text-accent-foreground` | Hover states and interactive pills |
| `border-border` / `border-input` | Card outlines, dividers, input borders |
| `ring-ring` | Focus rings |

---

## 4. Single Global Provider Setup

Ensure all global providers are composed in `src/providers/index.tsx` and used once in `src/app/layout.tsx`.

Example in `src/app/layout.tsx`:
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
