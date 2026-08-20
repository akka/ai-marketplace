# Akka documentation skin

The palette, type and geometry that `docs-template.html` renders in. This file is
**data, not advice**: `harnesses/content/diagram_check.py` reads the same values, so a
generated page using a color that is not listed here reds CONTENT-LANGUAGE.

Customers do not override this. The template is the design.

## Semantic roles

Akka's documentation is dark-ground, so `ink` is light and `paper` is near-black. Roles are
named by function, so a fragment can say "muted" instead of hard-coding a hex.

| Role | Purpose | Value |
|---|---|---|
| `paper` | page background | `#070707` |
| `paper-2` | panel and card background | `#0A0A0A` |
| `paper-3` | code block ground | `#050505` |
| `paper-inset` | node fill, code bar | `#141414`, `#0D0D0D` |
| `ink` | primary text, node names | `#F5F5F5` / `#fff` |
| `muted` | body text | `#B8B8B8` |
| `soft` | secondary text, sublabels | `#999`, `#888` |
| `faint` | hints, footer, chevron | `#666`, `#555` |
| `rule` | hairline borders | `#1C1C1C` |
| `rule-soft` | section divider, lifeline | `#141414`, `#2a2a2a` |
| `accent` | Akka yellow — brand mark, focal path, entity kind | `#F5C518` |
| `arrow` | default connector | `#8a8a8a` |
| `arrow-reply` | reply / projection connector | `#6a6a6a` |

## Component-kind colors

Categorical, not editorial. These identify *what a component is*, and the legend decodes
them. They apply to inventory graphics only — the component graph and the entity boxes.
The interaction diagram uses editorial color instead: one yellow primary path, everything
else `arrow` grey.

| Kind | Class | Fill | Stroke |
|---|---|---|---|
| External | `ext` / `n-ext` | `#141414` | `#666` dashed `4 3` |
| HTTP Endpoint | `ep` / `n-ep` | `#141414` | `#fff` |
| Event Sourced Entity | `ese` / `n-ese` | `#1A1600` | `#F5C518` |
| Key Value Entity | `kve` / `n-kve` | `#04180A` | `#28C840` |
| View | `view` / `n-view` | `#120A1A` | `#A855F7` |
| Workflow | `wf` / `n-wf` | `#0F1418` | `#7EC8E3` |
| Agent | `agent` / `n-agent` | `#141414` | `#FF6B6B` |

## Syntax highlighting

| Token | Class | Value |
|---|---|---|
| keyword | `kw` | `#C792EA` |
| type | `ty` | `#FFCB6B` |
| string | `st` | `#C3E88D` |
| comment | `cm` | `#546E7A` |
| annotation | `an` | `#F5C518` |
| function | `fn` | `#82AAFF` |
| number | `num` | `#F78C6C` |

## Typography

System sans (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto`) for prose and node
names; `'SF Mono', 'Cascadia Code', Consolas` for anything technical — component ids, field
types, code, connector labels, event chips. A human-readable name never goes in mono.

| Element | Size | Weight |
|---|---|---|
| h1 | 40px | 700 |
| lead | 15px | 400 |
| section label | 11px, tracked 3px, uppercase | 600 |
| stat number | 30px | 700 |
| section title | 14px | 700 |
| node name | 12px | 700 |
| body / description | 13.5px | 400 |
| connector label | 8px, tracked .06em | 400 |
| band and kind label | 9px / 7px, tracked, uppercase | 700 |

## Geometry

- **4px grid.** Every coordinate, width, height, gap and font size divisible by 4. Exempt:
  stroke widths (0.8, 1, 1.2), opacity, and corner radius. Checked on `<rect>` and
  `<line>` coordinates.
- **Radius** 4, 6, 8, or 10 on a box; 2 on a label mask, where a larger radius eats the
  plate. Never a pill on a node.
- **Component-graph bands** at y=64, 192, 320; nodes 160×48; add 128 per extra band.
- **Elbow radius** r=8 (6 in tight layouts).
- **Attach points** ≥12px apart when several connectors share a box edge.
- **Label mask** 6–10px clear of its stroke, on open canvas.
- **No shadows.** Borders only.

## Budget

| Limit | Value |
|---|---|
| Nodes per diagram | 9 |
| Connectors per diagram | 12 |
| Interaction lanes | 5 |
| Accent elements in a narrative diagram | 2 |

Over budget, split into an overview plus a detail diagram. A component omitted for budget is
recorded in the component reference with its reason.
