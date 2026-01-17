# Project Context: Cofounder Hub UI

## Purpose
The primary interface for Cofounder Hub, where Chris (Founder) and Paul (AI Cofounder) collaborate on strategy, operations, and technical execution. The UI provides high-leverage visualizations, strategic task management, and a unified view of the cofounder partnership.

## Tech Stack
- **Framework**: SvelteKit 2
- **Engine**: Svelte 5 (Runes)
- **Language**: TypeScript (Strict)
- **Styling**: Tailwind CSS 4
- **UI Components**: Shadcn Svelte (Bits UI)
- **Icons**: Lucide Svelte

## Project Conventions

### Code Style
- Use **Svelte 5 Runes** (`$state`, `$derived`, `$props`) exclusively. No legacy stores or reactive declarations.
- Follow **Functional/Declarative** patterns. 
- Strict TypeScript: No `any`, comprehensive interfaces for all data.
- Utility-first CSS with Tailwind 4.

### Architecture Patterns
- **Feature-based Structure**: Group related logic, components, and types.
- **Server-Side Logic**: Maximize usage of SvelteKit `load` functions and Form Actions.
- **State classes**: Use `.svelte.ts` files for shared logic/state using runes.

### Styling & Design
- Follow the **Luna Design Guide**: Premium, strategic, minimalist.
- Use HSL variables for consistent theme management.
- Dark mode by default or automatic based on system.

### Testing Strategy
- Playwright for E2E flows.
- Vitest for unit testing specialized logic in `.svelte.ts`.

### Git Workflow
- Conventional Commits.
- Feature branches.
- Atomic commits.

## Domain Context
- **The Partnership**: The UI represents a dual-seat cockpit. It's not just "user data", it's "founder context".
- **Signal vs. Noise**: Every design element should prioritize high-leverage information over clutter.

## Important Constraints
- Fast load times (Strategic speed).
- Highly responsive for both mobile oversight and desktop execution.
- Privacy-first for founder discussions.

