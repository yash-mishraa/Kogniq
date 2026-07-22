# Kogniq Design System

The visual language is typography-first, quiet, and intentional. It is designed for sustained knowledge work rather than marketing or dashboard administration.

## Foundation

- **Type:** Instrument Sans is the UI and editorial face. Geist Mono is limited to the Locus, metadata, identifiers, and compact system detail. Heading scales are optical, responsive, and led by whitespace rather than cards.
- **Color:** Use semantic tokens only: `canvas`, `surface`, `raised`, `ink`, `muted`, `line`, `accent`, `success`, `warning`, and `danger`. Accent is blue and signals action—not brand decoration.
- **Space:** Use Tailwind’s 4px-based scale. Prefer `8`, `12`, `16`, `20`, `24`, and `32px` increments.
- **Shape:** Corners are `3px`, `6px`, and `10px`; avoid pill-heavy UI. Borders establish structure before shadows do.
- **Elevation:** `shadow-panel` is reserved for cards; `shadow-overlay` is reserved for floating, modal layers.
- **Motion:** Motion explains state transitions only. Typography resolves into focus, an intention becomes a workspace title, and selected content unfolds in place. Respect `prefers-reduced-motion` automatically.
- **Layers:** Base `0`, sticky `10`, overlay `50`, transient UI `70`.

Light and dark values live in `src/app/globals.css`. Components must consume semantic color classes, never raw hard-coded greys, so both themes remain equivalent.

## Components

| Component | Use |
| --- | --- |
| `Button` | Primary, secondary, ghost, and destructive explicit actions. |
| `IconButton` | A compact icon action; `label` is mandatory for assistive technology. |
| `Input`, `Textarea` | Structured single- and multi-line entry. Always pair with an external label when context is not obvious. |
| `Search` | Query entry with the search affordance included. |
| `Badge` | Brief status/category labels. Use semantic tones sparingly. |
| `Card` | A bounded related region; never use as a decorative page tile. |
| `Dialog` | Blocking, focused decisions. Escape and close control dismiss it. |
| `Drawer` | Supplemental context that should retain the workspace underneath. |
| `Tooltip` | Explains icon-only controls; never hides essential information. |
| `Dropdown` | A short contextual action list. Destructive actions use the destructive tone. |
| `Tabs` | Local content grouping, not global navigation. |
| `Sidebar`, `SidebarItem` | Legacy structural primitives; not part of the visible Kogniq product experience. |
| `ApplicationLayout`, `ResizablePanels` | Legacy structural primitives; environments instead unfold contextually from the Locus. |
| `CommandPalette` | Legacy primitive; Kogniq uses the contextual Locus rather than command language. |
| `Table` | Dense structured comparisons and records. |
| `EmptyState` | Clear absence, a concise explanation, and an optional next action. |
| `Skeleton` | Utility primitive only; do not use in product flows. State should resolve through truthful typography and layout. |
| `Progress` | Utility primitive only; do not use as a generic loading metaphor. |
| `UploadZone` | A reusable file-picker surface. It accepts files through its callback but has no ingestion behavior. |

## Accessibility contract

- Every interactive primitive supports native keyboard behavior; Radix primitives provide modal, menu, tabs, and tooltip semantics.
- `:focus-visible` is a 2px accent ring. Do not remove it.
- Icon-only controls require labels. Decorative icons are `aria-hidden`.
- Modal overlays trap focus and support Escape. The Locus is a semantic form control with a contextual accessible label.
- Motion reduces to near-instant under the user’s reduced-motion preference.
- Text and borders use semantic contrast values in both themes.

## Visual reference

Run `npm run dev` inside `apps/web` and visit `/`. The experience flow is the maintained visual reference: Arrival, Access, Intention, and the contextual Workspace environments.

To capture a reference image after starting the app:

```powershell
# browser preview: http://localhost:3000/
```
