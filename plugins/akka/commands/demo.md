---
description: Generate personalized Akka sales presentations. Supports 4 modes — generic pitch, sales leave-behind, live SA demo, customer self-serve. Run `/akka:demo help` for usage.
handoffs:
  - label: Check Setup
    agent: akka.setup
    prompt: Verify that this machine has all required tools (Java, Maven, Akka CLI) for running the demo.
    send: true
  - label: Build & Run App
    agent: akka.build
    prompt: Build and run the service locally so we can embed it in the demo presentation.
    send: true
  - label: Run Resilience Tests
    agent: akka.reliability
    prompt: Start resilience testing against the running service.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

---

### Help Mode

If `$ARGUMENTS` is `help` or `--help`, print this usage guide and stop:

```
/akka:demo — Generate interactive Akka presentations

MODES:
  --mode overview       Standard Akka platform presentation (no project)
  --mode shareable      Offline-ready presentation with project showcase
  --mode live           Presentation with embedded running app (default)
  --mode hands-on       Presentation with setup guide for the recipient to run it

OPTIONS:
  --presenter NAME      Your name on the title slide
  --presenter-title T   Your title
  --for NAME            Who this presentation is for
  --logo PATH           Their logo image
  --project PATH        Path to Akka project (default: current directory)
  --repo URL            Git repo URL (for hands-on mode)
  --output PATH         Output file (default: ./demo-presentation.html)
  --port PORT           Override service port detection

EXAMPLES:
  /akka:demo                                    Interactive setup
  /akka:demo --mode overview                    Standard platform presentation
  /akka:demo --for "NTT Data"                   Live demo for NTT Data
  /akka:demo --mode shareable --for "Manulife"  Shareable with screenshots
  /akka:demo --mode hands-on --repo <url>       Hands-on package
```

---

### Interactive Mode

If `$ARGUMENTS` is empty or missing required values, prompt the user interactively.

First, briefly explain what `/akka:demo` does:

> This skill generates an interactive presentation showcasing Akka and (optionally) a specific project you've built. You can personalize it, include a live app, or package it for someone else to explore — without the live app — on their own.

Then ask:

1. **"What kind of presentation do you need?"**
   - **Overview** — "What is Akka?" presentation, no project-specific content → `--mode overview`
   - **Shareable** — A presentation with a project showcase someone can browse offline (screenshots, architecture, code) → `--mode shareable`
   - **Live** — A presentation with your running app embedded for a live walkthrough → `--mode live`
   - **Hands-on** — A presentation packaged for the recipient to clone the project and run it themselves → `--mode hands-on`

2. **"Your name?"** (skip for overview) — default: git config user.name
3. **"Your title?"** (skip for overview) — default: blank
4. **"Who are you presenting to?"** (skip for overview) — the person or team receiving the presentation
5. **"Recipient's logo?"** (optional) — path to an image file
6. **"Project directory?"** (skip for overview) — default: current directory
7. **"Repository URL?"** (hands-on mode only) — the repo the recipient will clone

After collecting all answers, show a confirmation summary before generating:

```
Ready to generate:

  Mode        Live
  Presenter   Tyler Jewell, CEO, Akka
  For         NTT Data
  Project     ./samples/social-proofing-agent
  Output      ./demo-presentation.html

Generate? [Y/n]
```

If the user confirms (or presses Enter), proceed. If they say no, cancel.

---

### Argument Parsing

If `$ARGUMENTS` contains flags, parse them:
- `--mode VALUE` — one of: overview, shareable, live, hands-on
- `--presenter VALUE` — presenter name
- `--presenter-title VALUE` — presenter title
- `--for VALUE` — who this presentation is for
- `--logo VALUE` — path to their logo image
- `--project VALUE` — path to Akka project directory
- `--repo VALUE` — git repo URL (hands-on mode)
- `--output VALUE` — output file path
- `--port VALUE` — service port override

A bare path argument (no flag) is treated as `--project`.
A bare URL argument (starts with `http`) is treated as `--repo` and implies cloning.

**Legacy flag aliases:**
- `--customer` → `--for`
- `--customer-logo` → `--logo`
- `generic` → `overview`
- `leave-behind` → `shareable`
- `customer` → `hands-on`

---

## Purpose

`/akka:demo` generates a **personalized, interactive sales presentation** from any Akka project. It introspects the project's components, design artifacts, and source code, then produces a single self-contained HTML file combining the Akka sales presentation with an embedded project showcase.

The output opens in any browser, presents full-screen, and requires no server. A salesperson can email it, share via Drive, or present it live.

---

## Execution Outline

1. **Locate project** — find or clone the Akka project
2. **Introspect** — scan all components, design artifacts, and source code
3. **Check environment** — verify runtime status
4. **Build & start** — compile and run (live mode only)
5. **Load templates** — read the four template files
6. **Generate presentation** — substitute project data into templates and assemble
7. **Write & report** — write output file, print next steps

---

## Step 1: Locate the Project

If the user provides a **GitHub URL**:
1. Clone the repo into a working directory
2. Note the local path

If the user provides a **local path**:
1. Verify the path exists and contains a `pom.xml` or `build.gradle`

If **no project specified** (overview mode or current directory):
1. For modes other than overview: verify `pom.xml` exists with `akka-sdk` dependency

---

## Step 2: Introspect the Project

Skip this step for **overview mode**. For all other modes, build a complete component inventory.

### 2a. Read spec and design artifacts

Call `akka_sdd_list_specs` to find features. If not available, glob for `specs/*/spec.md`.

For each feature, read these files if they exist:
- `spec.md` — extract: title (first `#` heading), description (first paragraph), requirements (bullet list items)
- `plan-diagrams.md` — extract the sequence diagram mermaid source block
- `plan.md` — extract component design notes

From `spec.md`, derive:
- `DEMO_TITLE` — project name formatted as HTML, e.g. `Social Proofing <span class="accent">Agent</span>`
- `DEMO_DESCRIPTION` — first paragraph, HTML-escaped
- `REQUIREMENTS_HTML` — each bullet point as a `<li>` element

### 2b. Scan and classify Java source files

Glob all `*.java` files under `src/main/java/`. For each file, read and classify:

| Pattern in file | Component type |
|----------------|----------------|
| `extends EventSourcedEntity` | Event Sourced Entity |
| `extends KeyValueEntity` | Key-Value Entity |
| `extends Workflow` | Workflow |
| `extends View` | View |
| `extends Consumer` | Consumer |
| `extends Agent` | Agent |
| `@HttpEndpoint` on class | HTTP Endpoint |
| `extends TimedAction` | Timed Action |
| `record`, `enum`, or `sealed interface` in a domain/model package | Domain Object |

For each classified component, extract:
- **Class name** (simple name, not fully qualified)
- **Component ID** — value of `@ComponentId("...")` or `@Component(id = "...")`
- **Short description** — one sentence from Javadoc or inferred from class name + type
- **Route metadata** — for endpoints, list each `@Get`/`@Post`/`@Put`/`@Delete` annotation with its path
- **Representative code snippet** — see §2c below

### 2c. Extract syntax-highlighted code snippets

For each component, extract 20–40 lines showing the most revealing part:

| Component type | What to show |
|---------------|-------------|
| Event Sourced Entity | The `sealed interface Events` definition + one `@CommandHandler` + one `@EventHandler` |
| Key-Value Entity | The value type + one command handler |
| Workflow | The workflow definition + first step |
| View | The `@Table` record type + `@Query` methods |
| Consumer | The `@Consume.From*` annotation + `onEvent` method |
| Agent | The system message string + `generateMessage` signature |
| HTTP Endpoint | All `@Get`/`@Post`/`@Put`/`@Delete` route methods |
| Domain Object | The full `record`/`enum`/`sealed interface` definition |

Apply syntax highlighting by wrapping tokens in `<span>` tags with these CSS classes:
- `.kw` — Java keywords: `public`, `private`, `class`, `record`, `enum`, `interface`, `sealed`, `return`, `var`, `if`, `new`, `void`, `static`, `final`, `sealed`, `permits`, `implements`, `extends`
- `.ty` — Type names: capitalized identifiers (e.g. `String`, `Effect`, `ProductState`, `List`)
- `.st` — String literals: anything between double quotes
- `.cm` — Comments: `//` lines and `/* */` blocks
- `.an` — Annotations: `@` followed by identifier (e.g. `@ComponentId`, `@Get`, `@CommandHandler`)
- `.fn` — Method names: identifier immediately before `(`
- `.num` — Numeric literals: digits

Preserve original indentation exactly. Use `&lt;` and `&gt;` for angle brackets. Use `&amp;` for `&`.

### 2d. Build the component table HTML

This is `{{COMPONENTS_TABLE_HTML}}` — the inner content of the `.comp-table` div.

Group components by type in this order:
1. HTTP Endpoints
2. Event Sourced Entities
3. Key-Value Entities
4. Workflows
5. Consumers
6. Agents
7. Views
8. Timed Actions
9. Design Views (from spec artifacts — see §2e)
10. Domain Objects

For each group with at least one member, emit:

```html
<div class="comp-group-header">
  <span class="dot" style="background:COLOR"></span>
  <span class="comp-group-count">(N)</span>
  <span style="color:COLOR">Group Name</span>
</div>
```

For each component in the group, emit a row + detail panel pair:

```html
<div class="comp-row" data-comp="UNIQUE-KEY">
  <span class="comp-row-dot" style="background:COLOR"></span>
  <span class="comp-row-name">ClassName</span>
  <span class="comp-row-type">Type Label</span>
  <span class="comp-row-desc">Short one-line description</span>
</div>
<div class="comp-detail" data-detail="UNIQUE-KEY">
  <div class="comp-detail-desc">Longer description sentence.</div>
  <div class="comp-detail-code">
    <div class="comp-detail-code-bar">FileName.java</div>
    <div class="comp-detail-code-body">SYNTAX-HIGHLIGHTED CODE HERE</div>
  </div>
</div>
```

**UNIQUE-KEY** must be a short, lowercase, hyphen-separated identifier, unique across all components (e.g. `ep-product`, `ese-entity`, `ag-social-proof`).

**COLOR** per component type (use consistently for dot, group header, and row dot):

| Type | Color |
|------|-------|
| Event Sourced Entity | `#F5C518` |
| Key-Value Entity | `#28C840` |
| Workflow | `#1E90FF` |
| View | `#A855F7` |
| Consumer | `#F97316` |
| Agent | `#7EC8E3` |
| Endpoint | `#fff` |
| Timed Action | `#888` |
| Design View | `#4EC9B0` |
| Domain Object | `#82AAFF` |

**Do NOT** put `{{COMPONENTS_TABLE_HTML}}` — or any content generated by substituting it — inside an HTML comment block. The component table HTML contains `-->` sequences from its own embedded HTML comments (e.g. `<!-- Design Views -->`), which would prematurely close any enclosing HTML comment and cause the entire table HTML (plus anything after it) to render as visible raw text on screen.

### 2e. Build Design Views entries in the component table

For each spec diagram found (User Journey, Actor-Goal, Entity Map, Component Graph, Sequence), add a row + detail panel in the Design Views group. Render each mermaid diagram source as static HTML using the rules in §7.

### 2f. Count totals

From the scan, calculate:
- `COMPONENT_COUNT` — total components excluding Domain Objects
- `EVENT_COUNT` — number of event types (entries in sealed interfaces annotated on entities)
- `ENDPOINT_COUNT` — total `@Get`/`@Post`/`@Put`/`@Delete` methods across all endpoint classes
- `DESIGN_VIEW_COUNT` — number of design diagrams found
- `AGENT_COUNT` — number of Agent components
- `LOC` — sum of line counts across all Java files, formatted with comma (e.g. `1,800`)

### 2g. Build SEQUENCE_DATA_JSON

If `plan-diagrams.md` contains a mermaid sequence diagram, convert it to the JSON format that `demo.js` expects:

```json
{
  "participants": [
    {"id": "SHORTID", "name": "Display\nName", "ext": true|false, "color": "#HEX"}
  ],
  "messages": [
    {"region": "Region Label", "color": "#HEX"},
    {"from": INDEX, "to": INDEX, "label": "message text", "dashed": true|false}
  ]
}
```

Rules:
- `ext: true` for external systems (clients, external APIs, simulators); `ext: false` for Akka components
- `color` on participants: use the component-type colors from §2d
- `region` objects create colored separator bands; use Blue `#2196F3` for ingestion, Amber `#FF9800` for processing, Green `#4CAF50` for delivery
- `dashed: true` for response arrows; `dashed: false` for request/command arrows
- `name` supports `\n` for two-line headers
- `from`/`to` are 0-based indices into the `participants` array

If no sequence diagram exists in the specs, synthesize one from the component relationships discovered in §2b.

---

## Step 3: Check Environment

Call `akka_local_status`. Record the result.

- If `"status": "started"` — runtime is running; note the service URL and port
- If not started — note that the presentation will include a "Start App" guide in the App tab

**Do NOT call `akka_local_start`** if status already shows `"started"`. The runtime is shared across all services and restarting it kills other running services.

---

## Step 4: Build & Start (live mode only)

Skip for overview, shareable, and hands-on modes.

If environment is ready and user wants the live app embedded:
1. Run `akka_maven_compile` — if it fails, continue and show error in App tab
2. If compile succeeded and runtime is not running: `akka_local_start`
3. `akka_local_run_service` to start the service
4. `akka_local_status` to get the service URL and port
5. Record `SERVICE_URL` (e.g. `http://localhost:9004`)

---

## Step 5: Load Templates

Read all four template files from the plugin installation directory:

```
~/.claude/plugins/akka/templates/base.html   — full Akka sales deck with 5 insertion markers
~/.claude/plugins/akka/templates/demo.css    — all #demo-section scoped CSS (~400 lines)
~/.claude/plugins/akka/templates/demo.html   — demo section HTML with {{PLACEHOLDER}} markers + TAB6 markers
~/.claude/plugins/akka/templates/demo.js     — tab switching, SVG diagrams, keyboard nav (~240 lines)
```

Read all four files in full before beginning assembly.

---

## Step 6: Generate the Presentation HTML

Assemble the output by substituting into the templates. **Do not write new CSS, JS, or structural HTML from scratch.** Everything is already in the templates — just fill in the placeholders.

### 6a. Build mode-specific App tab content

#### live mode — APP_CONTENT_HTML

If service is running:
```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">SERVICE_URL</div>
  </div>
  <div class="app-body" style="height:420px;padding:0;">
    <iframe src="SERVICE_URL" style="width:100%;height:100%;border:none;"
            title="PROJECT NAME"></iframe>
  </div>
</div>
```

If service is NOT running, show a boot terminal placeholder:
```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">Service not running</div>
  </div>
  <div class="app-body" style="height:420px; display:flex; align-items:center;
       justify-content:center; flex-direction:column; gap:16px;">
    <div style="color:#666; font-size:13px;">Run <code style="color:#F5C518">/akka:build</code> to start the service,
    then regenerate.</div>
  </div>
</div>
```

#### shareable mode — APP_CONTENT_HTML

Static product card gallery showing representative examples of each social proof strategy the project generates. Use a 2×2 grid with inline styles. Each card shows: strategy label (colored per type), product name, category, the social proof message as a colored banner, and signal stats. Derive card content from the project's domain objects and agent description. If unknown, use representative examples consistent with the project's domain.

```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">PROJECT NAME — Demo Screenshots</div>
  </div>
  <div class="app-body" style="height:420px; display:grid; grid-template-columns:1fr 1fr;
       gap:12px; padding:16px; background:#0A0A0A; overflow:auto;">
    <!-- 4 product cards, one per strategy variant -->
  </div>
</div>
```

#### hands-on mode — APP_CONTENT_HTML

Step-by-step run guide with 4 numbered steps:
1. **Prerequisites** — Java 21+, Maven 3.9+, Akka CLI install command
2. **Clone and build** — `git clone REPO_URL`, `cd PROJECT_DIR`, `mvn compile -q`
3. **Set LLM key and run** — `export ANTHROPIC_API_KEY=...`, `akka local run`, `open http://localhost:PORT`
4. **Try it** — brief prose on what to do first in the app

```html
<div class="try-steps" style="max-width:640px;">
  <div class="try-step">
    <div class="try-step-num">01</div>
    <div class="try-step-content">
      <div class="try-step-title">TITLE</div>
      <div class="try-step-desc">DESC</div>
      <div class="mini-term">...</div>
    </div>
  </div>
  <!-- repeat for each step -->
</div>
```

#### overview mode — no App tab

Skip — demo section is not added at all.

### 6b. Build all placeholder values

Collect everything from Steps 2 and 4:

| Placeholder | Value source |
|-------------|-------------|
| `{{DEMO_TITLE}}` | Project name as HTML with `<span class="accent">` on a keyword |
| `{{DEMO_DESCRIPTION}}` | First paragraph from spec.md, HTML-safe |
| `{{REQUIREMENTS_HTML}}` | Each spec requirement as `<li>TEXT</li>` |
| `{{BUILD_TIME}}` | Measured or estimated spec-to-running time (e.g. `"35m"`) |
| `{{LOC}}` | Total Java LOC with comma formatting |
| `{{APP_HEADLINE}}` | live: `'A complete <span class="accent">PROJECT system</span>'`; shareable: same; hands-on: `'Run it <span class="accent">yourself</span>'` |
| `{{APP_DESCRIPTION}}` | One sentence for the App tab; mode-specific |
| `{{APP_CONTENT_HTML}}` | From §6a |
| `{{APP_STATS_HTML}}` | `.app-stat` divs: endpoints, entities, events, agents, views, LOC |
| `{{ARCH_SUMMARY_HTML}}` | Six `.arch-summary-stat` divs: components, events, endpoints, design views, agents, LOC |
| `{{COMPONENTS_TABLE_HTML}}` | From §2d + §2e |
| `{{REPO_URL}}` | Git repo URL (from `--repo` flag, git remote, or clone URL) |
| `{{SEQUENCE_DATA_JSON}}` | From §2g |

**APP_STATS_HTML structure:**
```html
<div class="app-stat"><div class="app-stat-num">N</div><div class="app-stat-label">API endpoints</div></div>
<div class="app-stat"><div class="app-stat-num">N</div><div class="app-stat-label">Entities</div></div>
<div class="app-stat"><div class="app-stat-num">N</div><div class="app-stat-label">Event types</div></div>
<div class="app-stat"><div class="app-stat-num">N</div><div class="app-stat-label">Agents</div></div>
<div class="app-stat"><div class="app-stat-num">N</div><div class="app-stat-label">Views</div></div>
<div class="app-stat"><div class="app-stat-num">N,NNN</div><div class="app-stat-label">LOC</div></div>
```

**ARCH_SUMMARY_HTML structure** (always 6 stats in this order):
```html
<div class="arch-summary-stat"><div class="arch-summary-num">N</div><div class="arch-summary-label">Components</div></div>
<div class="arch-summary-stat"><div class="arch-summary-num">N</div><div class="arch-summary-label">Event Types</div></div>
<div class="arch-summary-stat"><div class="arch-summary-num">N</div><div class="arch-summary-label">API Endpoints</div></div>
<div class="arch-summary-stat"><div class="arch-summary-num">N</div><div class="arch-summary-label">Design Views</div></div>
<div class="arch-summary-stat"><div class="arch-summary-num">N</div><div class="arch-summary-label">Agents</div></div>
<div class="arch-summary-stat"><div class="arch-summary-num">N,NNN</div><div class="arch-summary-label">LOC</div></div>
```

### 6c. Substitute demo.html template

Perform all replacements on the loaded `demo.html` content:
```python
for placeholder, value in substitutions.items():
    demo_html = demo_html.replace(placeholder, value)
```

All 13 placeholders must be replaced before proceeding. Verify no `{{...}}` tokens remain.

**For hands-on mode** — after substitution, remove Tab 6 (Try It Yourself) using the explicit markers already in `demo.html`:

```python
import re
demo_html = re.sub(r'<!-- TAB6-NAV-START -->.*?<!-- TAB6-NAV-END -->',
                   '', demo_html, flags=re.DOTALL)
demo_html = re.sub(r'<!-- TAB6-PANEL-START -->.*?<!-- TAB6-PANEL-END -->',
                   '', demo_html, flags=re.DOTALL)
```

**NEVER** attempt to remove Tab 6 by matching its opening `<div>` tag with dot-star regex. The div has nested children; the first `</div>` match will be an inner child's closing tag, leaving broken partial HTML that causes the entire content area to go blank.

### 6d. Assemble presenter info into base.html

For all modes except overview:
```python
output = base_html
output = output.replace('{{PRESENTER_NAME}}', presenter_name)
output = output.replace('{{PRESENTER_TITLE}}', presenter_title)
output = output.replace('{{PRESENTER_LINKEDIN}}', presenter_linkedin or '#')
```

For **overview mode** — strip the presenter div entirely using regex (simple string replace
would leave a broken anchor tag):
```python
import re
output = re.sub(r'\s*<div class="title-presenter">.*?</div>\s*', '\n',
                output, flags=re.DOTALL)
output = output.replace("    document.getElementById('demo-wrapper'),\n", '')
```

The second line removes the demo-wrapper reference from the views array JS, since there is no demo-wrapper in overview mode.

### 6e. Inject demo section into base.html

For all modes except overview:
```python
output = output.replace('<!-- DEMO_CSS_MARKER -->',  demo_css)
output = output.replace('<!-- DEMO_HTML_MARKER -->', demo_html)
output = output.replace('/* DEMO_JS_MARKER */',      demo_js)
```

For **overview mode** — replace all three markers with empty strings:
```python
output = output.replace('<!-- DEMO_CSS_MARKER -->',  '')
output = output.replace('<!-- DEMO_HTML_MARKER -->', '')
output = output.replace('/* DEMO_JS_MARKER */',      '')
```

### 6f. Resilience iframe path

No path substitution needed. The plugin assets (including `resilience/`) are copied to the output directory in Step 7, so `src="resilience/resilience.html"` resolves correctly from wherever the output file lives.

### 6g. Verify before writing

Before writing the output file, verify:
1. No unreplaced `{{...}}` placeholders remain
2. `id="demo-wrapper"` is present (for non-overview modes)
3. `src="resilience/resilience.html"` is still present (not accidentally removed)
4. For hands-on: `data-tab="5"` is absent (Tab 6 successfully removed)
5. For live: `src="http://localhost` is present (iframe injected)
6. For shareable: no `iframe` pointing to localhost

---

## Step 7: Write Output and Report

Write the assembled HTML with UTF-8 encoding to the output path.

Then copy the plugin's static assets into the same directory so all relative paths in the presentation resolve correctly:

```bash
PLUGIN=~/.claude/plugins/akka
OUT=$(dirname OUTPUT_PATH)
cp -r "$PLUGIN/images"     "$OUT/"
cp -r "$PLUGIN/logos"      "$OUT/"
cp -r "$PLUGIN/resilience" "$OUT/"
```

If any of those directories already exist in `OUT`, skip (do not overwrite).

Report to the user:

```
Done.

  Presentation    open FILENAME
  Live App        http://localhost:PORT    (live mode only)
  Console         http://localhost:9889   (if runtime running)
  Resilience      /akka:reliability
  Deploy          /akka:deploy
```

---

## Diagram Rendering Rules (§7)

When converting mermaid diagram source to static HTML:

1. **No mermaid.js** — all diagrams are rendered as static HTML/CSS/SVG
2. **Orthogonal connections only** — right angles, no curves or diagonals
3. **SVG for lines** — `shape-rendering: crispEdges`, 1px strokes, color `#444`

**User Journey diagram** — `.dg-journey-nodes` with `.dg-journey-row` elements:
```html
<div class="dg-journey-nodes">
  <div class="dg-journey-row">
    <span class="dg-journey-node dg-journey-p1">Feature name</span>
    <span class="dg-journey-arrow">→</span>
    <span class="dg-journey-node dg-journey-p1">Outcome</span>
  </div>
</div>
<div class="dg-legend" style="margin-top:12px">
  <div class="dg-legend-item"><div class="dg-legend-bar" style="background:#2196F3"></div>P1 Core</div>
  <div class="dg-legend-item"><div class="dg-legend-bar" style="background:#FF9800"></div>P2 Enhanced</div>
  <div class="dg-legend-item"><div class="dg-legend-bar" style="background:#4CAF50"></div>P3 Demo</div>
</div>
```
Phase classes: `dg-journey-p1` (blue), `dg-journey-p2` (amber), `dg-journey-p3` (green).

**Actor-Goal diagram** — `<table class="dg-ag-table">` with columns: Actor | Goal | Components | External.

**Entity Map** — `.dg-entity-map` with `.dg-node` divs colored by component type (see §2d).

**Component Graph** — Layered `.dg-layer` divs (External → API Layer → Application Layer), each with `.dg-layer-nodes` and `.dg-node` elements. Between layers, `.dg-connections` with `.dg-conn-group` elements containing `.dg-conn-tree` for SVG connectors rendered by demo.js at runtime.

**Sequence Diagram** — Rendered to `<div id="seqDiagram">` by demo.js at runtime from `window.DEMO_SEQUENCE_DATA`. Provide the JSON via `{{SEQUENCE_DATA_JSON}}` (see §2g). Do not render this one statically.

---

## Key Rules

1. **Never synthesize CSS, JS, or structural HTML** — read the templates, substitute placeholders. Every design decision is already made.
2. **The sales presentation's design always wins** — demo CSS is scoped under `#demo-section` and must never override presentation styles.
3. **Never add a top navigation bar** — it breaks every sticky section in the presentation.
4. **Never use floating/fixed nav** for the demo sidebar — it overlaps content.
5. **The demo section scroll anchor** — `demo-wrapper` is `height:200vh; position:relative`. `demo-section` is `position:sticky; top:0`. Do not change these.
6. **Tab panels use opacity, not display:none** — inactive panels have `opacity:0; pointer-events:none`. They overlay each other via `position:absolute; inset:0` inside `.content { position:relative }`.
7. **Tab 6 removal** — use the `TAB6-NAV-START/END` and `TAB6-PANEL-START/END` markers in `demo.html`. Never use dot-star regex on the raw `<div>` tags.
8. **COMPONENTS_TABLE_HTML and HTML comments** — never place substituted component table content inside an HTML comment block. The table HTML contains `-->` sequences that would break the comment.
9. **UTF-8 encoding** — use explicit `encoding='utf-8'` for all file reads and writes.
10. **Number keys 1–6** switch demo tabs only when the demo section is in the viewport.

---

## Error Handling

- **No pom.xml found** — tell the user this doesn't appear to be an Akka project. Suggest `/akka:setup`.
- **No specs found** — generate without Brief tab spec content. Use project name + component summary as fallback description.
- **No diagrams found** — skip Design Views group in Architecture tab. Component code viewer still works.
- **Build fails** — generate the presentation anyway. App tab shows the error and suggests `/akka:build`.
- **No Java files found** — error and stop; cannot generate a demo without components.
- **akka_local_status shows started but port unknown** — use port 9000 as default.
