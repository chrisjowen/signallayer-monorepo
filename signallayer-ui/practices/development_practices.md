# SvelteKit & Svelte 5 Technical Standards

## Overview
This document defines the architectural and technical standards for SvelteKit projects in the Cofounder Hub ecosystem. We prioritize performance, type safety, and the "Runes" methodology of Svelte 5.

## Core Stack
- **Framework**: [SvelteKit](https://kit.svelte.dev/) (latest)
- **Engine**: [Svelte 5](https://svelte.dev/blog/svelte-5-is-alive) (Runes)
- **Language**: [TypeScript](https://www.typescriptlang.org/) (Strict Mode)
- **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
- **UI Components**: [Shadcn Svelte](https://shadcn-svelte.com/) (based on [Bits UI](https://bits-ui.com/))
- **Package Manager**: `bun` (preferred) or `pnpm`

## Svelte 5 Runes Methodology
We embrace Svelte 5 Runes for state management. Avoid legacy Svelte 4 syntax (`let` for state, `$:` for derived).

### State Management
- Use `$state()` for reactive variables.
- Use `$derived()` for computed values.
- Use `$effect()` sparingly for side effects (syncing with outside world).
- Use `$props()` to define component interfaces.

```typescript
// Good: Using Runes
let { initialCount = 0 } = $props<{ initialCount?: number }>();
let count = $state(initialCount);
let doubled = $derived(count * 2);
```

### Component Patterns
- **Presentation vs. Logic**: Keep components focused on UI. Move complex logic into `.svelte.ts` files (classes or functions using runes).
- **Snippet usage**: Use `{#snippet ...}` for reusable UI fragments within a component.
- **Render tags**: Use `{@render ...}` to invoke snippets.

## TypeScript Standards
- Enable `strict: true` in `tsconfig.json`.
- Avoid `any`. Use `unknown` if types are truly unknown.
- Define interfaces for all data structures.
- Use `type` for simple data containers and `interface` for extendable objects.
- Prefer SvelteKit's generated types (`PageData`, `ActionData`) for load functions and actions.

## Styling (Tailwind 4)
- **Utility First**: Use utility classes for layout and spacing.
- **Customization**: Use the `theme()` function and CSS variables for brand colors.
- **No Inline Styles**: Unless dynamically calculated and unavoidable.
- **Class Merging**: Use `cn()` utility (from shadcn) to merge classes cleanly.

## Project Structure
```
src/
├── lib/
│   ├── components/     # UI Components (Shadcn + Custom)
│   │   ├── ui/        # Shadcn primitives
│   │   └── shared/    # Reusable custom components
│   ├── assets/        # Images, fonts, icons
│   ├── server/        # Server-only utilities (db, auth)
│   ├── utils/         # Helper functions
│   └── types/         # Global TypeScript definitions
├── routes/            # SvelteKit file-based routing
└── app.html           # Main entry point
```

## State Architecture
- **Local State**: Store in components using runes.
- **Shared State**: Use classes in `.svelte.ts` files to create "Stores" that can be imported and used anywhere.
- **Server State**: Use SvelteKit's `load` functions and `page` store for server-driven data.

## Definition of Done (Frontend)
- [ ] TypeScript types are fully defined (no implicit `any`).
- [ ] Responsive design verified (Mobile/Desktop).
- [ ] Accessible (ARIA labels, keyboard navigation).
- [ ] Performance (No unnecessary `$effect` triggers).
- [ ] Unit tests for complex logic in `.svelte.ts` files.
