---
name: akka-docs
description: "Generate rendered project documentation \u2014 a component reference plus entity and interaction diagrams \u2014 into the project's docs/ folder as a self-contained docs/index.html."
---

## User Input

```text
$ARGUMENTS
```

The input is optional. If present, treat it as a short subtitle for the
documentation (a one-line description of what the service does). If empty,
derive the subtitle from the project README or constitution.

## Purpose

This command generates a self-contained documentation site for the current
Akka project into its `docs/` folder. It introspects the project's components
and source, then renders four artifacts into a single `docs/index.html`,
styled to match Akka:

- an **entity diagram** — each entity's state fields, its events, and the
  domain objects it references;
- an **interaction diagram** — a sequence view of how a request flows through
  endpoints, entities, and views;
- a **component graph** — the components grouped by layer (edge, domain, read
  model);
- a **component reference** — every component explained, with a
  syntax-highlighted code excerpt.

The output is a single self-contained HTML file — all CSS is inline, all
diagrams are inline SVG or HTML. No external assets, no build step, no
JavaScript required. When done, run `akka specify docs` (see Step 5) so the
user is told exactly where to find it.

## Introspection

Work primarily from the project source. If the service is running and the
`akka_backoffice_list_components` MCP tool is available, you may cross-check the
component inventory against runtime discovery, but do not require it.

---

## Workflow

### Step 1 — Identify the project

1. Read `pom.xml` for the `<artifactId>` — this is the project name shown in
   the header.
2. Derive a one-line subtitle from the user input, else from `README`, else
   from `.akka/constitution/`. Keep it to a single sentence.

### Step 2 — Discover and classify components

Scan `src/main/java` (or `src/main/scala`). Classify each component by its base
class / annotation:

| Signal | Component type | Node class | Accent |
| --- | --- | --- | --- |
| `@HttpEndpoint` / `@GrpcEndpoint` / `@McpEndpoint` | HTTP Endpoint | `ep` | white |
| `extends EventSourcedEntity` | Event Sourced Entity | `ese` | `#F5C518` |
| `extends KeyValueEntity` | Key Value Entity | `kve` | `#28C840` |
| `extends View` | View | `view` | `#A855F7` |
| `extends Workflow` | Workflow | `view` (purple) | `#A855F7` |
| `extends Consumer` | Consumer | `ep` | `#F97316` |
| `extends Agent` | Agent | `ese` (cyan) | `#7EC8E3` |

For each **entity**, extract: the state type's fields (name + Java type), and
its events (the `record`s of the sealed `Event`/`interface`). For each
**endpoint**, extract its route paths and HTTP methods. Collect **domain
objects** — records referenced by entity state (e.g. `LineItem` in
`List<LineItem>`).

### Step 3 — Build the artifacts

Assemble `docs/index.html` from the template in the **HTML template** section
below. Fill in:

- **Header**: brand mark, project name (`<h1>`), subtitle (`.lead`).
- **Stats grid**: five `.stat` tiles — components, events, endpoints, views,
  domain objects (use whatever five metrics fit the project).
- **Diagrams** section (`.section-label` = "Diagrams"), each a collapsed
  `<details class="sec">`:
  - **Entity diagram** — one `.ent-box` per entity (state fields as `.ent-row`,
    events as `.ent-ev`) plus a muted `.ent-box` per referenced domain object.
  - **Interaction diagram** — an inline SVG sequence diagram of the primary
    write flow: client → endpoint → entity → view → reply. Use vertical
    lifelines, an activation box on the entity, and draw `persist(...)` as a
    **self-loop to the right of the entity lifeline** with the label placed to
    the right (`text-anchor="start"`) so it never overlaps the lifeline.
    Request/command arrows solid `#8a8a8a`; event/persist arrows `#F5C518`;
    reply/projection arrows dashed `#6a6a6a`. Follow the SVG in the template.
  - **Component graph** — `.dg-layer` blocks for Edge, Domain, and Read model,
    each holding `.node` tiles of the right class from Step 2, plus a `.legend`.
- **Components** section (`.section-label` = "Components"), one collapsed
  `<details class="sec">` per component: a `.comp-desc` paragraph explaining
  what it does and why, then a `.code` block with a real excerpt from the
  source, syntax-highlighted with the span classes below.

Syntax-highlight classes (wrap tokens in `<span class="...">`): `kw` keyword,
`ty` type, `st` string, `cm` comment, `an` annotation, `fn` method name,
`num` number. **Escape** `<`, `>`, and `&` in all code excerpts
(`&lt;`, `&gt;`, `&amp;`).

### Step 4 — Write the file

Write the assembled HTML to `docs/index.html` (create `docs/` if needed).
All sections must be **collapsed by default** — plain `<details class="sec">`
with no `open` attribute. Diagrams come before the component reference.

### Step 5 — Tell the user where it is

Run:

```bash
akka specify docs
```

This prints the path to `docs/index.html` and a `file://` URL to open it. If
the `akka` CLI is unavailable, print the relative path (`docs/index.html`) and
the absolute `file://` URL yourself.

---

## HTML template

Produce a file with exactly this shell. Keep the `<style>` block verbatim; fill
the body following the element patterns shown.

```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>PROJECT_NAME — Project Documentation</title>
<style>
:root{--yellow:#F5C518;--green:#28C840;--white:#F5F5F5;}
*{margin:0;box-sizing:border-box}
body{background:#070707;color:#B8B8B8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:48px 40px 80px;position:relative}
.bg{position:fixed;inset:0;background-image:radial-gradient(circle,rgba(245,197,24,0.035) 1px,transparent 1px);background-size:48px 48px;pointer-events:none;z-index:0}
.wrap>*{position:relative;z-index:1}
.mono{font-family:'SF Mono','Cascadia Code','Consolas',monospace}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:6px}
.brand-mark{font-weight:800;letter-spacing:1px;color:#0A0A0A;background:var(--yellow);padding:3px 9px;border-radius:5px;font-size:14px}
.brand-sub{font-size:11px;text-transform:uppercase;letter-spacing:3px;color:#666;font-weight:600}
h1{font-size:40px;font-weight:700;letter-spacing:-0.03em;color:var(--white);margin:14px 0 6px}
.lead{font-size:15px;color:#999;max-width:720px;margin-bottom:34px}
.section-label{font-size:11px;text-transform:uppercase;letter-spacing:3px;color:var(--yellow);font-weight:600;margin:52px 0 16px;display:flex;align-items:center;gap:10px}
.section-label::before{content:'';width:28px;height:2px;background:var(--yellow)}
.stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:8px}
.stat{background:#0A0A0A;border:1px solid #1C1C1C;border-radius:8px;padding:16px;text-align:center}
.stat-num{font-size:30px;font-weight:700;color:var(--yellow);line-height:1}
.stat-label{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:1.5px;margin-top:6px}
details.sec{background:#0A0A0A;border:1px solid #1C1C1C;border-radius:10px;margin-bottom:10px;overflow:hidden}
details.sec>summary{list-style:none;cursor:pointer;padding:15px 20px;display:flex;align-items:center;gap:11px;user-select:none}
details.sec>summary::-webkit-details-marker{display:none}
.chev{color:#555;font-size:10px;transition:transform .2s ease;width:12px;flex-shrink:0}
details[open]>summary .chev{transform:rotate(90deg);color:var(--yellow)}
.sec-dot{width:8px;height:8px;border-radius:4px;flex-shrink:0}
.sec-title{font-size:14px;font-weight:700;color:var(--white)}
.sec-type{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:#666;margin-left:2px}
.sec-id{font-size:11px;color:#F5C518;margin-left:2px}
.sec-hint{font-size:12px;color:#666;margin-left:auto;text-align:right}
.sec-body{padding:4px 22px 22px;border-top:1px solid #141414}
.comp-desc{font-size:13.5px;color:#9a9a9a;margin:12px 0 14px;max-width:820px}
.code{background:#050505;border:1px solid #1C1C1C;border-radius:8px;overflow:hidden}
.code-bar{background:#0D0D0D;border-bottom:1px solid #1C1C1C;padding:6px 14px;font-size:11px;color:#666}
.code-body{padding:14px 18px;font-size:12px;line-height:1.75;color:#B8B8B8;white-space:pre;overflow-x:auto}
.kw{color:#C792EA}.ty{color:#FFCB6B}.st{color:#C3E88D}.cm{color:#546E7A;font-style:italic}.an{color:#F5C518}.fn{color:#82AAFF}.num{color:#F78C6C}
.dg-layer{padding:14px 0;border-bottom:1px solid #1C1C1C}.dg-layer:last-child{border-bottom:none}
.dg-layer-label{font-size:9px;text-transform:uppercase;letter-spacing:2px;font-weight:700;color:#F5C518;margin-bottom:12px;display:flex;align-items:center;gap:6px}
.dg-layer-label::before{content:'';width:14px;height:1px;background:#F5C518}
.dg-nodes{display:flex;gap:10px;flex-wrap:wrap}
.node{border-radius:6px;padding:8px 14px;min-width:120px}
.node .nt{font-size:7px;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:3px}
.node .nn{font-size:12px;font-weight:700;color:#fff}
.node.ext{background:#141414;border:1px dashed #666}.node.ext .nt{color:#666}
.node.ep{background:#141414;border:1px solid #fff}.node.ep .nt{color:#aaa}
.node.ese{background:#1A1600;border:1px solid #F5C518}.node.ese .nt{color:#F5C518}
.node.view{background:#120A1A;border:1px solid #A855F7}.node.view .nt{color:#A855F7}
.node.kve{background:#04180A;border:1px solid #28C840}.node.kve .nt{color:#28C840}
.legend{display:flex;gap:18px;padding-top:14px;margin-top:6px;border-top:1px solid #1C1C1C;flex-wrap:wrap}
.legend-item{display:flex;align-items:center;gap:6px;font-size:10px;color:#888}
.legend-bar{width:14px;height:2px;border-radius:1px}
.entity{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:6px}
.ent-box{background:#050505;border:1px solid #1C1C1C;border-radius:8px;overflow:hidden}
.ent-title{background:#1A1600;border-bottom:1px solid #F5C518;padding:8px 14px;font-weight:700;color:#F5C518;font-size:13px}
.ent-rows{padding:8px 0}
.ent-row{display:flex;justify-content:space-between;padding:4px 14px;font-size:12px;font-family:'SF Mono','Consolas',monospace}
.ent-row .fname{color:#ccc}.ent-row .ftype{color:#FFCB6B}
.ent-events{padding:8px 14px 12px}
.ent-events .lbl{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:#888;margin-bottom:6px}
.ent-ev{display:inline-block;background:#141414;border:1px solid #333;border-radius:4px;padding:3px 9px;margin:0 5px 5px 0;font-size:11px;color:#C3E88D;font-family:'SF Mono','Consolas',monospace}
.foot{margin-top:56px;padding-top:20px;border-top:1px solid #1C1C1C;font-size:11px;color:#555;display:flex;justify-content:space-between}
.foot .cmd{color:#F5C518}
</style></head>
<body><div class="bg"></div><div class="wrap">

<div class="brand"><span class="brand-mark">AKKA</span><span class="brand-sub">Project Documentation</span></div>
<h1>PROJECT_NAME</h1>
<p class="lead">SUBTITLE</p>

<div class="stats">
  <div class="stat"><div class="stat-num">N</div><div class="stat-label">Components</div></div>
  <!-- four more .stat tiles -->
</div>

<div class="section-label">Diagrams</div>

<!-- Entity diagram (collapsed) -->
<details class="sec">
  <summary><span class="chev">&#9654;</span><span class="sec-dot" style="background:#F5C518"></span><span class="sec-title">Entity diagram</span><span class="sec-hint">State, events, and referenced domain objects</span></summary>
  <div class="sec-body"><div class="entity">
    <div class="ent-box">
      <div class="ent-title">ENTITY <span style="font-weight:400;font-size:10px;color:#888">&middot; state</span></div>
      <div class="ent-rows">
        <div class="ent-row"><span class="fname">FIELD</span><span class="ftype">TYPE</span></div>
      </div>
      <div class="ent-events"><div class="lbl">Events</div>
        <span class="ent-ev">EVENT</span>
      </div>
    </div>
    <div class="ent-box">
      <div class="ent-title" style="background:#0A0A0A;border-bottom-color:#546E7A;color:#B0BEC5">DOMAIN_OBJECT <span style="font-weight:400;font-size:10px;color:#888">&middot; domain object</span></div>
      <div class="ent-rows">
        <div class="ent-row"><span class="fname">FIELD</span><span class="ftype">TYPE</span></div>
      </div>
      <div class="ent-events"><div class="lbl">Referenced by</div>
        <span class="ent-ev" style="color:#F5C518;border-color:#5a4a00">ENTITY.field</span>
      </div>
    </div>
  </div></div>
</details>

<!-- Interaction diagram (collapsed) — sequence: client -> endpoint -> entity (activation + persist self-loop) -> view -> reply -->
<details class="sec">
  <summary><span class="chev">&#9654;</span><span class="sec-dot" style="background:#F5C518"></span><span class="sec-title">Interaction diagram</span><span class="sec-hint">Primary write flow through endpoint, entity, and view</span></summary>
  <div class="sec-body">
  <svg viewBox="0 0 980 320" width="100%" font-family="'SF Mono','Consolas',monospace">
    <g font-size="11" font-weight="700" text-anchor="middle">
      <rect x="40"  y="14" width="150" height="30" rx="4" fill="#141414" stroke="#666" stroke-dasharray="4 3"/><text x="115" y="34" fill="#999">Client</text>
      <rect x="285" y="14" width="185" height="30" rx="4" fill="#141414" stroke="#fff"/><text x="377" y="34" fill="#fff">ENDPOINT</text>
      <rect x="560" y="14" width="175" height="30" rx="4" fill="#1A1600" stroke="#F5C518"/><text x="647" y="34" fill="#F5C518">ENTITY</text>
      <rect x="800" y="14" width="150" height="30" rx="4" fill="#120A1A" stroke="#A855F7"/><text x="875" y="34" fill="#A855F7">VIEW</text>
    </g>
    <g stroke="#2a2a2a"><line x1="115" y1="44" x2="115" y2="310"/><line x1="377" y1="44" x2="377" y2="310"/><line x1="647" y1="44" x2="647" y2="310"/><line x1="875" y1="44" x2="875" y2="310"/></g>
    <rect x="642" y="96" width="10" height="130" fill="#1A1600" stroke="#F5C518"/>
    <g font-size="10" text-anchor="middle">
      <line x1="115" y1="80" x2="373" y2="80" stroke="#8a8a8a"/><polygon points="377,80 369,76 369,84" fill="#8a8a8a"/><text x="246" y="74" fill="#aaa">POST /path</text>
      <line x1="377" y1="112" x2="640" y2="112" stroke="#8a8a8a"/><polygon points="644,112 636,108 636,116" fill="#8a8a8a"/><text x="510" y="106" fill="#aaa">command(...)</text>
      <path d="M652 132 H700 V152 H656" fill="none" stroke="#F5C518"/><polygon points="652,152 660,148 660,156" fill="#F5C518"/>
      <text x="708" y="146" fill="#F5C518" text-anchor="start">persist(EVENT)</text>
      <line x1="652" y1="182" x2="871" y2="182" stroke="#F5C518" stroke-dasharray="5 3"/><polygon points="875,182 867,178 867,186" fill="#F5C518"/><text x="763" y="176" fill="#F5C518">EVENT event</text>
      <line x1="642" y1="248" x2="381" y2="248" stroke="#6a6a6a" stroke-dasharray="5 3"/><polygon points="377,248 385,244 385,252" fill="#6a6a6a"/><text x="510" y="242" fill="#888">updated state</text>
      <line x1="377" y1="284" x2="119" y2="284" stroke="#6a6a6a" stroke-dasharray="5 3"/><polygon points="115,284 123,280 123,288" fill="#6a6a6a"/><text x="246" y="278" fill="#888">200 response</text>
    </g>
  </svg>
  <div class="legend">
    <div class="legend-item"><span class="legend-bar" style="background:#8a8a8a"></span>request / command</div>
    <div class="legend-item"><span class="legend-bar" style="background:#F5C518"></span>event / persist</div>
    <div class="legend-item"><span class="legend-bar" style="background:#6a6a6a;height:0;border-top:1px dashed #6a6a6a"></span>reply / projection</div>
  </div>
  </div>
</details>

<!-- Component graph (collapsed) -->
<details class="sec">
  <summary><span class="chev">&#9654;</span><span class="sec-dot" style="background:#F5C518"></span><span class="sec-title">Component graph</span><span class="sec-hint">Edge, domain, and read-model layers</span></summary>
  <div class="sec-body">
  <div class="dg-layer"><div class="dg-layer-label">Edge</div><div class="dg-nodes">
    <div class="node ext"><div class="nt">External</div><div class="nn">Client</div></div>
    <div class="node ep"><div class="nt">HTTP Endpoint</div><div class="nn">ENDPOINT</div></div>
  </div></div>
  <div class="dg-layer"><div class="dg-layer-label">Domain</div><div class="dg-nodes">
    <div class="node ese"><div class="nt">Event Sourced Entity</div><div class="nn">ENTITY</div></div>
  </div></div>
  <div class="dg-layer"><div class="dg-layer-label">Read model</div><div class="dg-nodes">
    <div class="node view"><div class="nt">View</div><div class="nn">VIEW</div></div>
  </div></div>
  <div class="legend">
    <div class="legend-item"><span class="legend-bar" style="background:#fff"></span>Endpoint</div>
    <div class="legend-item"><span class="legend-bar" style="background:#F5C518"></span>Event Sourced Entity</div>
    <div class="legend-item"><span class="legend-bar" style="background:#A855F7"></span>View</div>
    <div class="legend-item"><span class="legend-bar" style="background:#28C840"></span>Key Value Entity</div>
    <div class="legend-item"><span class="legend-bar" style="background:#7EC8E3"></span>Agent</div>
  </div>
  </div>
</details>

<div class="section-label">Components</div>

<!-- One collapsed details.sec per component. sec-dot color = component accent. -->
<details class="sec">
  <summary><span class="chev">&#9654;</span><span class="sec-dot" style="background:#fff"></span><span class="sec-title">COMPONENT</span><span class="sec-type">TYPE</span><span class="sec-id mono">component-id</span><span class="sec-hint">one-line role</span></summary>
  <div class="sec-body">
    <p class="comp-desc">What this component does and why.</p>
    <div class="code"><div class="code-bar mono">Component.java</div><div class="code-body mono"><span class="an">@Annotation</span>
<span class="kw">public class</span> <span class="ty">Component</span> { <span class="cm">// ...</span> }</div></div>
  </div>
</details>

<div class="foot"><span>Generated by <span class="cmd mono">/akka:docs</span> &middot; docs/index.html</span><span>Akka SDK</span></div>
</div></body></html>
```

---

## Key Rules

- **Self-contained** — one `docs/index.html`, all CSS inline, all diagrams
  inline SVG/HTML. No external stylesheets, scripts, fonts, or images.
- **Collapsed by default** — every section is `<details class="sec">` with no
  `open` attribute. Diagrams come before the component reference.
- **Real content** — code excerpts are trimmed from actual source, not
  invented. Entity fields and events come from the real state and event types.
- **Escape HTML** in code excerpts (`&lt;`, `&gt;`, `&amp;`).
- **persist() draws clean** — the entity self-message is a loop to the right of
  the lifeline with the label `text-anchor="start"`; it must not overlap the
  lifeline or the activation box.
- **Match Akka colors** — use the accent per component type from Step 2.
- **Print the location** — always finish by running `akka specify docs` (or
  printing the path and `file://` URL) so the user knows where the docs are.

## Done When

- [ ] Components were discovered from source and classified by type (endpoint,
      event-sourced entity, key-value entity, view, workflow, consumer, agent).
- [ ] `docs/index.html` was written, self-contained (inline CSS + inline SVG/HTML),
      with the project name and subtitle in the header and a stats grid.
- [ ] The **Diagrams** section renders, in order, an entity diagram, an
      interaction (sequence) diagram, and a component graph — each a collapsed
      `<details class="sec">`.
- [ ] The interaction diagram's `persist(...)` self-message is drawn as a clean
      loop to the right of the entity lifeline, with no overlap.
- [ ] The **Components** section has one collapsed `<details class="sec">` per
      component, each with a description and a syntax-highlighted source excerpt
      (HTML-escaped).
- [ ] All sections are collapsed by default; diagrams precede the component
      reference.
- [ ] `akka specify docs` was run (or the path + `file://` URL printed) so the
      user knows where to open the rendered documentation.
