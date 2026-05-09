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
  --output PATH         Output file (live default: {project}/src/main/resources/static-resources/demo.html; other: ./demo-presentation.html)
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
6. **Generate presentation** — write and run `~/.akka/gen_demo.py` to produce the final HTML; the script also copies assets
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
- `spec.md` — extract: title (first `#` heading); then **synthesize** a Brief description and bullet list (do not copy the raw spec — see below)
- `plan-diagrams.md` — extract all five mermaid source blocks (User Journey, Actor-Goal, Entity Map, Component Graph, Sequence)
- `plan.md` — extract component design notes

**The Brief tab is read by a non-technical buyer in 10 seconds.** Do not paste the spec's `**Input**:` paragraph (often a dense run-on) and do not enumerate every functional requirement. Instead:

- **Description** — write **one or two short sentences** in plain English. No jargon. No comma-spliced lists of features. Tell the reader *what the user gets*, not what the system does internally. Example good: *"AI-powered sales workspace. Reps ask plain-English questions and get a ranked list of doctors with reasons. Compliance is enforced live, not after the fact."* Example bad: *"A sales acceleration workspace that demonstrates an agentic stack — natural-language territory queries, explainable next-best-action recommendations, runtime Sunshine Act compliance, and a model-lifecycle drift gate — augmenting the existing recommendation engine without replacing it."*
- **Bullets** — pick **4–6 bullets total**. Each bullet is **one short layman line** (≤ 12 words). Group similar requirements together rather than listing each FR-### individually. Skip anything that is not differentiating. Drop the words *MUST*, *system*, *user*, and acronyms unless they're already brand-recognizable to the buyer.

**Detect which of the five diagram types are present** in `plan-diagrams.md`. The five types are identified by these keywords:
1. `journey` — User Journey
2. `flowchart` containing actor/goal nodes — Actor-Goal
3. `erDiagram` — Entity Map
4. `flowchart` containing component/annotation nodes — Component Graph
5. `sequenceDiagram` — Sequence

Decide what to do based on the count of types found:

- **All 5 present** — render every diagram normally and continue silently. No mention to the user.
- **At least 1 but fewer than 5 present** — render whatever is present. Record which types are missing; surface them in the final §7 report (e.g. `Diagrams: 3 of 5 rendered. Missing: Actor-Goal, Entity Map.`) and tell the user *they can run `/akka:plan` to fill in the missing diagrams*. Do **not** invoke `/akka:plan` automatically.
- **None present** (file missing, empty, or contains zero recognized diagram types) — skip the Design Views group entirely. In the final report, tell the user *no diagrams were found in `plan-diagrams.md`; run `/akka:plan` to generate all five, then re-run `/akka:demo`*. Do **not** invoke `/akka:plan` automatically.

The rule of thumb: never silently regenerate diagrams the user already authored or auto-invoke another skill on their behalf. If at least one diagram exists, the user has touched this file — respect that and only render what's there.

From `spec.md`, derive:
- `DEMO_TITLE` — project name formatted as HTML, e.g. `Social Proofing <span class="accent">Agent</span>`
- `DEMO_DESCRIPTION` — your synthesized 1–2 sentence layman description (see above), HTML-escaped
- `REQUIREMENTS_HTML` — your 4–6 curated layman bullets, each as a `<li>` element

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

Group components by type in this order. **Design Views must always come first** —
the design artifacts (User Journey, Actor-Goal, Entity Map, Component Graph,
Sequence) tell the architectural story before the implementing components, so
they belong at the top of the table:

1. **Design Views** (from spec artifacts — see §2e) — *always first when present*
2. HTTP Endpoints
3. Event Sourced Entities
4. Key-Value Entities
5. Workflows
6. Consumers
7. Agents
8. Views
9. Timed Actions
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

For each spec diagram found (User Journey, Actor-Goal, Entity Map, Component Graph, Sequence), add a row + detail panel in the Design Views group. **Pre-render the mermaid source to SVG with `mmdc` and inline the SVG** (§7 pre-rendering pipeline). Never emit `<pre class="mermaid">` or load mermaid.js — the deck must remain a single, self-contained, offline-capable HTML file.

Sequence diagrams are the one exception: they are converted to the JSON shape consumed by `demo.js` at §2g and rendered as a hand-built SVG by the custom renderer baked into the deck. Do not pre-render sequence mermaid blocks to SVG via mmdc.

The pipeline also applies to any other mermaid block the user has pointed the skill at (e.g. `reference-architecture/*.md`). Treat each one as an additional Design View row.

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

### 2h. Apply Akka Design System to the project app HTML

Skip for **overview mode**. For all other modes, locate the project's primary app HTML file and ensure it uses the Akka design system.

**Locate the app HTML**: Glob for `src/main/resources/static-resources/index.html` (or `index.htm`) in the project directory. If not found, skip this section.

**Check for Akka design system compliance** — the file must satisfy ALL of these:

| Check | Expected |
|-------|----------|
| Google Fonts link | `Instrument Sans` and `Roboto Mono` loaded via `fonts.googleapis.com` |
| `--accent` CSS variable | `#F5C518` (Akka yellow) |
| `body` font-family | starts with `'Instrument Sans'` |
| `header` background | `#000` or `var(--bg)` — not a blue-tinted value like `#0d1218` |
| Button text color | `#000` — not navy/dark-blue values like `#001824` |
| RUNNING status color | uses a blue variable (e.g. `var(--running)` or `#1E90FF`) — not the yellow accent |
| Monospace font | `'Roboto Mono'` as the first listed monospace font |
| Hardcoded old-blue rgba values | none of `rgba(78, 195, 255, ...)` remain |

**If any check fails**, apply the following changes to the file:

1. **Add font imports** (inside `<head>`, before any `<style>` tag if not already present):
   ```html
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
   ```

2. **Set or update the `:root` CSS variable block** — replace the entire `:root { ... }` block with:
   ```css
   :root {
     --bg: #000;
     --bg-elev: #0D0D0D;
     --bg-elev-2: #141414;
     --border: #1C1C1C;
     --border-light: #222;
     --text: #fff;
     --text-dim: #B8B8B8;
     --text-muted: #555;
     --accent: #F5C518;
     --accent-2: #4EC9B0;
     --warn: #F5C518;
     --danger: #ff6b6b;
     --good: #28c840;
     --running: #1E90FF;
   }
   ```

3. **Update `body` font-family** — replace whatever is there with:
   ```css
   font-family: 'Instrument Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
   ```

4. **Fix header background** — replace any hardcoded blue-tinted header background (e.g. `#0d1218`, `#0a1628`, `#11161d`) with `#000`.

5. **Fix button text color** — replace any navy/dark-blue text color on `.btn` (e.g. `#001824`, `#001f3f`) with `#000`.

6. **Fix RUNNING status pill** — update `.status-pill.RUNNING` to use blue, not yellow:
   ```css
   .status-pill.RUNNING { background: rgba(30, 144, 255, 0.15); color: var(--running); }
   ```

7. **Fix hardcoded old-accent rgba values** — replace any `rgba(78, 195, 255, ...)` with the yellow equivalent by substituting the RGB triple: `78, 195, 255` → `245, 197, 24`.

8. **Fix AWAITING_APPROVAL and policy gate rgba** — replace any `rgba(245, 176, 65, ...)` with `rgba(245, 197, 24, ...)` (exact Akka yellow).

9. **Update monospace font references** — replace `ui-monospace, SFMono-Regular, Menlo, monospace` with `'Roboto Mono', ui-monospace, SFMono-Regular, Menlo, monospace`. Replace bare `ui-monospace, monospace` with `'Roboto Mono', ui-monospace, monospace`.

10. **Fix disclaimer and divider** — if the disclaimer block uses hardcoded blue-gray backgrounds (e.g. `#15202b`, `#1f2933`), replace with `var(--bg-elev)` and `var(--border)`. If the brand divider uses a hardcoded color, replace with `var(--text-muted)`.

Apply all changes as surgical edits — do not rewrite the file structure, logic, or JavaScript. Only touch CSS color/font values.

After editing, note in the Step 7 report: `"App styled with Akka design system"`.

---

## Step 3: Check Environment

Call `akka_local_status`. Record the result.

- If `"status": "started"` — runtime is running; note any already-running services
- If not started — runtime needs to be started in Step 4

**Do NOT call `akka_local_start`** if status already shows `"started"`. The runtime is shared across all services and restarting it kills other running services.

For live mode, also record:
- `STATIC_DIR` = `{PROJECT_DIR}/src/main/resources/static-resources/`
- This is where the finished presentation and all its assets will be written so Akka can serve them.

---

## Step 4: Build & Start (live mode only)

Skip for overview, shareable, and hands-on modes.

Use the **Build & Run App** handoff — do not call `akka_maven_compile`, `akka_local_start`, or `akka_local_run_service` manually. The handoff handles compilation, runtime startup, and service registration in the correct order.

After the handoff completes:
1. Call `akka_local_status` to confirm the service is running and retrieve the port
2. Record `SERVICE_URL` (e.g. `http://localhost:9004`) and `PORT`
3. If the build failed, generate the presentation anyway — the App tab will show the error and suggest `/akka:build`

---

## Step 5: Refresh Templates From Upstream

Templates are pulled from the public competitive repo on every run so the slide content, copy, and structure are always current. The plugin only ships a minimal fallback used when the network or Python is unavailable.

**Upstream:** `https://github.com/TylerJewell/competitive`
**Cache root:** `~/.akka/competitive/`
**Staging root:** `~/.akka/sales-presentation-staged/` (mirrors the plugin layout so §6 substitution and §6h asset copy work unchanged)

### 5a. Refresh, build, and stage

Implement this phase as a single Python script at `~/.akka/refresh_demo_templates.py` and execute it. Pure-bash globbing across nested directories is fragile on Windows shells; Python is required for the build anyway.

The script must:

1. **Clone or fast-forward** `~/.akka/competitive/` from `https://github.com/TylerJewell/competitive`.
   - If the directory does not exist: `git clone --depth 1 https://github.com/TylerJewell/competitive ~/.akka/competitive`
   - If it exists: `git -C ~/.akka/competitive pull --ff-only`
   - On any git failure (no network, auth required, repo gone), **do not abort** — log a warning and skip to the fallback in §5c.

2. **Build the deck** by running `python3 ~/.akka/competitive/sales-presentation/builder/build.py --mode overview`. This produces:
   - `~/.akka/competitive/sales-presentation/generated/overview/index.html`
   - `~/.akka/competitive/sales-presentation/generated/overview/{images,logos,resilience}/`
   - On build failure: log the stderr and skip to the fallback in §5c.

3. **Stage into plugin layout** at `~/.akka/sales-presentation-staged/`:
   - `templates/base.html` ← `generated/overview/index.html`
   - `templates/demo.css`  ← `slides/12-demo/slide.css`
   - `templates/demo.html` ← `slides/12-demo/slide.html`
   - `templates/demo.js`   ← `slides/12-demo/slide.js`
   - `images/`, `logos/`, `resilience/` ← copied from `generated/overview/`
   - Use `shutil.copytree(..., dirs_exist_ok=True)` and `shutil.copy2` so re-runs are idempotent.

4. **Record `PLUGIN_DIR` = `~/.akka/sales-presentation-staged/`** when staging succeeded. The remainder of the skill (§5b, §6, §6h) reads from `PLUGIN_DIR` unchanged.

### 5b. Fallback to bundled templates

If git or Python is unavailable, or the build failed, fall back to the bundled copy. Search these candidate paths in order, stopping at the first that exists:

```
~/.claude/plugins/cache/akka-ai-marketplace/akka/*/templates/
~/.claude/plugins/marketplaces/akka-ai-marketplace/plugins/akka/templates/
```

Use a glob on the version wildcard (`*`) and take the highest version match. Record this as `PLUGIN_DIR` (the `plugins/akka/` root, one level above `templates/`). Warn the user that the deck may be stale: `"Couldn't refresh from upstream — using bundled templates. Run /akka:demo with network access to get the latest slides."`

If neither the staging dir nor a bundled path exists, stop and tell the user: `"Plugin templates not found. Re-install the Akka plugin with: akka plugin install akka"`

### 5c. Locate the four template files

Read these files in full before beginning substitution:

```
PLUGIN_DIR/templates/base.html   — assembled sales deck with insertion markers
PLUGIN_DIR/templates/demo.css    — all #demo-section scoped CSS
PLUGIN_DIR/templates/demo.html   — demo section HTML with {{PLACEHOLDER}} markers
PLUGIN_DIR/templates/demo.js     — tab switching, SVG diagrams, keyboard nav
```

Also record the asset directories for the copy step in §6h:

```
PLUGIN_DIR/images/       — presentation slide images
PLUGIN_DIR/logos/        — customer/partner logos
PLUGIN_DIR/resilience/   — resilience demo HTML
```

---

## Step 6: Generate the Presentation HTML

**Always implement Step 6 by writing a Python script** at `~/.akka/gen_demo.py` and running it. Do not attempt inline substitution in prose — the HTML is large (200KB+), context window truncation will silently corrupt it. The script handles: syntax-highlighted component table, sequence JSON, all placeholder substitutions, template injection, asset copy, and endpoint routing check. Write the complete script, then execute it with `python3 ~/.akka/gen_demo.py`.

If `~/.akka/gen_demo.py` already exists from a prior run, read it first and update only the sections that differ (presenter, port, project data) rather than rewriting from scratch. This makes reruns fast.

Assemble the output by substituting into the templates. **Do not write new CSS, JS, or structural HTML from scratch.** Everything is already in the templates — just fill in the placeholders.

### 6a. Build mode-specific App tab content

#### live mode — APP_CONTENT_HTML

The presentation is served from the same Akka service at `http://localhost:PORT/demo.html`. The app itself is served at `http://localhost:PORT/` from the same static-resources directory. Use the absolute `http://localhost:PORT/` URL in the iframe so it resolves correctly whether the presentation is opened from the server or copied elsewhere.

If service is running, do NOT set an inline `height` on `.app-body` — let the
stylesheet handle it (it sizes the iframe to fill the available viewport):
```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">http://localhost:PORT/</div>
  </div>
  <div class="app-body" style="padding:0;">
    <iframe src="http://localhost:PORT/" style="width:100%;height:100%;border:none;"
            title="PROJECT NAME"></iframe>
  </div>
</div>
```

If service is NOT running, show a boot terminal placeholder. The stylesheet's
viewport-relative height applies here too — only override layout properties:
```html
<div class="app-frame">
  <div class="app-chrome">
    <div class="app-url">Service not running</div>
  </div>
  <div class="app-body" style="display:flex; align-items:center;
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
| `{{DEMO_DESCRIPTION}}` | Curated 1–2 sentence layman description (see §2a) |
| `{{REQUIREMENTS_HTML}}` | 4–6 curated layman bullets as `<li>TEXT</li>` (see §2a) |
| `{{BUILD_TIME}}` | Measured or estimated spec-to-running time (e.g. `"35m"`) |
| `{{LOC}}` | Total Java LOC with comma formatting |
| `{{APP_HEADLINE}}` | live: `'A complete <span class="accent">PROJECT system</span>'`; shareable: same; hands-on: `'Run it <span class="accent">yourself</span>'` |
| `{{APP_CONTENT_HTML}}` | From §6a |
| `{{ARCH_SUMMARY_HTML}}` | Six `.arch-summary-stat` divs: components, events, endpoints, design views, agents, LOC |
| `{{COMPONENTS_TABLE_HTML}}` | From §2d + §2e |
| `{{REPO_URL}}` | Git repo URL (from `--repo` flag, git remote, or clone URL) |
| `{{SEQUENCE_DATA_JSON}}` | From §2g |

The App tab no longer carries a description sentence or stat pills — the iframe sits directly under the headline so it can grow tall without scrollbars. Do **not** emit `{{APP_DESCRIPTION}}` or `{{APP_STATS_HTML}}`; those placeholders have been removed from the template.

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

### 6h. Copy assets and check endpoint routing (live mode only)

**Include these steps directly in `gen_demo.py`** — do not rely on manual shell commands after the script runs.

#### Asset copy

Copy **all** asset subdirectories from the staged build into `OUT_DIR`. Use a wildcard loop so any new directory added to the sales presentation is automatically included:

```python
import shutil, os

staged = plugin_dir  # PLUGIN_DIR resolved in Step 5a
for name in os.listdir(staged):
    src = os.path.join(staged, name)
    dst = os.path.join(out_dir, name)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
```

**Never list directories by name** (`images`, `logos`, `resilience`). The wildcard loop ensures newly added asset directories (e.g. `videos/`, `fonts/`) are automatically included without requiring spec updates.

#### Endpoint routing check

After copying, scan the project for the HTTP endpoint that serves static files. It typically has `@HttpEndpoint` and `@Acl` annotations and returns `HttpResponses.staticResource(...)`.

**If it contains `@Get("/**")`**: this conflicts with any `@Get("/api/...")` routes in the same class and causes a startup failure (`Overlapping wildcard paths`). Replace it with per-directory routes — one `@Get("/DIRNAME/**")` for each directory that was just copied into `OUT_DIR`:

```java
// For each directory in OUT_DIR, add a route like this:
@Get("/images/**")
public HttpResponse image(HttpRequest request) {
  return HttpResponses.staticResource(request, "/");
}

@Get("/logos/**")
public HttpResponse logo(HttpRequest request) {
  return HttpResponses.staticResource(request, "/");
}

@Get("/resilience/**")
public HttpResponse resilienceAsset(HttpRequest request) {
  return HttpResponses.staticResource(request, "/");
}

// Keep a single-segment fallback for top-level files (demo.html, favicon, etc.):
@Get("/{asset}")
public HttpResponse asset(String asset) {
  return HttpResponses.staticResource(asset);
}
```

Also ensure `import akka.http.javadsl.model.HttpRequest;` is present in the endpoint file.

**If it already uses per-directory routes**: check that a route exists for every directory in `OUT_DIR`. If a new directory was added (e.g. `resilience/`), add the corresponding `@Get("/resilience/**")` route.

After any endpoint edit, include a recompile step in gen_demo.py or note it clearly in the report — the service must be restarted to pick up both the new static files and the routing change.

---

## Step 7: Write Output and Report

### Output path by mode

**live mode** — write into the project's Akka static resources directory so the presentation is served by the running service:
```
OUT_DIR = {PROJECT_DIR}/src/main/resources/static-resources/
OUTPUT  = OUT_DIR/demo.html
```
Create `OUT_DIR` if it doesn't exist.

**All other modes** — write to `--output` path (default: `./demo-presentation.html`):
```
OUT_DIR = dirname(OUTPUT_PATH)
OUTPUT  = OUTPUT_PATH
```

### Write the HTML

Write the assembled HTML with UTF-8 encoding to `OUTPUT`.

### Copy assets

This is handled by `gen_demo.py` (see §6h). If running outside the script context, copy all asset subdirectories from the staged build:

```bash
for dir in "$PLUGIN_DIR"/*/; do
  name=$(basename "$dir")
  [ "$name" = "commands" ] || [ "$name" = "templates" ] && continue
  cp -r "$dir" "$OUT_DIR/$name"
done
```

Do not list directories by name — the loop ensures all of them (images, logos, resilience, and any future additions) are copied.

### Package as a self-contained zip

After the HTML and all assets are written, **always** package them into a single distributable zip so the deck can be emailed or dropped on a partner's machine without an unpack step on the sender's side.

Bundle everything sitting next to `OUTPUT` in `OUT_DIR` that the deck references — `demo.html` itself plus every asset subdirectory that was copied in the previous step (`images/`, `logos/`, `resilience/`, and any future additions). Use a wildcard walk over `OUT_DIR` so newly added asset directories are picked up automatically. Do not include the project's own application files (e.g. `index.html`, `app.js`, `style.css` from `static-resources/`) — those are the host service's UI, not the deck.

```python
import os, zipfile

ZIP_INCLUDES = {'demo.html', 'images', 'logos', 'resilience'}  # extend as new asset dirs appear
ZIP_PATH = os.path.join(OUT_DIR, f"{project_slug}-demo.zip")

with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for entry in os.listdir(OUT_DIR):
        if entry not in ZIP_INCLUDES:
            continue
        full = os.path.join(OUT_DIR, entry)
        if os.path.isfile(full):
            z.write(full, entry)
        else:
            for dirpath, _, files in os.walk(full):
                for f in files:
                    fp = os.path.join(dirpath, f)
                    z.write(fp, os.path.relpath(fp, OUT_DIR))
```

`project_slug` is the lowercased, hyphen-separated artifactId from `pom.xml` (e.g. `email-agent`). For overview mode (no project introspection), use `akka-presentation`.

The zip MUST be self-contained: a partner who unzips it anywhere should be able to double-click `demo.html` and see the deck render correctly with no network access. If the deck references any new asset directory in the future, add it to `ZIP_INCLUDES` so it travels with the zip.

Include the zip emission in `gen_demo.py` (after the asset copy in §6h) so it happens automatically on every run.

### Restart service (live mode only)

Akka serves static files from the **compiled classpath** (`target/classes/`), not directly from `src/main/resources/`. The files written above won't be accessible until the service is recompiled and restarted.

Call `akka_local_run_service` with the project directory. This triggers recompilation (picking up the new files from `src/main/resources/static-resources/`) and restarts the service.

After restart, the presentation is live at `http://localhost:PORT/demo.html` and the app is at `http://localhost:PORT/`.

### Report

```
Done.

  Presentation    http://localhost:PORT/demo.html       (live mode)
  Presentation    open OUTPUT_PATH                      (other modes)
  Distributable   {OUT_DIR}/{project_slug}-demo.zip     (always)
  Live App        http://localhost:PORT/                (live mode only)
  Console         http://localhost:9889                 (if runtime running)
  Resilience      /akka:reliability
  Deploy          /akka:deploy
```

If any of the five Design View diagrams were missing or absent (see §2a), append a line to the report **before** "Done.":

- All 5 present: omit the line.
- 1–4 present: `Diagrams: N of 5 rendered. Missing: <comma-separated list>. Run /akka:plan to fill them in, then re-run /akka:demo.`
- 0 present: `Diagrams: none found in plan-diagrams.md. Run /akka:plan to generate all five, then re-run /akka:demo.`

---

## Diagram Rendering Rules (§7)

When converting mermaid diagram source to static HTML:

1. **No mermaid.js at runtime, ever.** The output `demo.html` MUST be a single, self-contained file that works offline. Pre-render every mermaid block to SVG at generation time and inline the SVG directly into the HTML. Never include `<script src="…mermaid…">` tags or load mermaid from a CDN.
2. **Orthogonal connections only** — right angles, no curves or diagonals (applies to hand-authored diagrams in §7.x below).
3. **SVG for lines** — `shape-rendering: crispEdges`, 1px strokes, color `#444` (applies to hand-authored diagrams).

### Pre-rendering pipeline for mermaid sources

When a design view comes from a mermaid block (e.g. found in `plan-diagrams.md`, `reference-architecture/*.md`, or any markdown the user has pointed at):

1. Extract the mermaid source between ```` ```mermaid ```` fences and write it to a temporary `.mmd` file (e.g. `~/.akka/mermaid-tmp/<key>.mmd`).
2. Pre-render to SVG using `mmdc` from `@mermaid-js/mermaid-cli`. Prefer a globally installed `mmdc`; otherwise invoke it via npx without polluting the user's global packages:
   ```bash
   npx -y -p @mermaid-js/mermaid-cli mmdc \
     -i ~/.akka/mermaid-tmp/<key>.mmd \
     -o ~/.akka/mermaid-tmp/<key>.svg \
     -b transparent
   ```
3. Inline the produced SVG into the design-view detail panel:
   - Strip any leading `<?xml …?>` prolog and `<!DOCTYPE …>` line.
   - Strip the SVG's outer `width="…"` / `height="…"` attributes and add `style="max-width:100%; height:auto; display:block;"` so it scales with its container.
   - Wrap the inlined SVG in a light-background canvas (`background:#fafafa; border-radius:8px; padding:14px; overflow:auto;`) so the diagram is readable on the deck's dark surface.
4. **Never** emit a `<pre class="mermaid">` block, a `mermaid.initialize(…)` call, or any reference to a mermaid CDN. If `mmdc` cannot be invoked (no Node, no network, command failed), fall back to the hand-authored static HTML rules in §7.x for the five canonical diagram types.

This pipeline applies to **any** mermaid source the skill discovers — the five canonical diagrams in `plan-diagrams.md`, mermaid blocks elsewhere in `specs/`, and architecture diagrams in `reference-architecture/` — without exception.

### Required tooling

The plugin requires Node.js (≥ 18) and network access on first run so `npx -y -p @mermaid-js/mermaid-cli mmdc` can fetch the renderer. After the first run, `mmdc` is cached in npm's package cache and works offline. Surface a clear error if Node is missing: `"mermaid pre-rendering needs Node.js (≥ 18). Install Node, then re-run /akka:demo."` Do NOT degrade silently to the CDN — that breaks the offline-self-contained guarantee.

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
- **No diagrams found** — skip Design Views group in Architecture tab. Component code viewer still works. Surface the missing-diagram message in the §7 report so the user knows to run `/akka:plan`. Do **not** auto-invoke `/akka:plan`.
- **Build fails** — generate the presentation anyway. App tab shows the error and suggests `/akka:build`.
- **No Java files found** — error and stop; cannot generate a demo without components.
- **akka_local_status shows started but port unknown** — use port 9000 as default.
