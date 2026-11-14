---
description: Discover what a feature or an existing system needs before it is specified, in topics, record every claim as a finding with its evidence, and confirm the understanding with a person.
handoffs:
  - label: Confirm the Understanding
    agent: akka.discover
    prompt: confirm
    send: true
  - label: Write the Specification
    agent: akka.specify
    prompt: Write the specification from the confirmed findings in discovery/
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

This command runs `akka specify` subcommands (`probes`, `conform`) and, for discovery, `akka bom generate`. They need the akka CLI release that includes the discovery gates and probes. If a subcommand is reported as unknown, tell the person their CLI is older than this plugin, name the missing subcommand, skip the step that needs it and say it was skipped.

## Outline

Discovery is the work that comes before a specification: learning what is already known, what
else exists, what the words mean, how an existing system behaves, and whether the person agrees
with what the AI has understood. Every claim it makes is written down as a **finding**, with the
evidence a reader can open and a status that says how far to trust it. A specification may rest
only on findings a person has confirmed.

Discovery works on one project at a time, not one feature. Everything it writes goes in a
`discovery/` folder at the project root, shared by every spec in `specs/`.

### Topics

Discovery work is organised in **topics**. A topic is one question or goal, such as how refunds
are approved or how cost is shown, with its own folder `discovery/<topic>/`. Several topics can
be active on one project at once, and two assistant sessions can work on two topics without
touching each other's files.

Each topic folder holds a header file, `topic.md`, written from the `topic` template:

```text
# Topic: <title>

**Goal**: <goal or question> | **Track**: ideation|modernization | **Code**: <CODE>
**Scope**: project|<area> | **Status**: active|settled|parked | **Owner**: <name or role> | **Started**: <YYYY-MM-DD>
```

- **Topic name**: the folder name, in lower case with words joined by `-` (`refund-approval`). It is never one of the sub-command words `research`, `landscape`, `concepts`, `system`, `confirm` or `mock`, and never begins with `-`.
- **Code**: two to four capital letters, unique among the project's topics, assigned when the topic is created and never changed (`PAY` for refund approval). Every identifier the topic writes carries it, so identifiers from two topics never collide.
- **Track**: ideation for a new idea, modernization for a rebuild of an existing system.
- **Scope**: `project` when the topic is about the whole project, otherwise the name of the area it covers. The Story draws a project-scoped topic in its overview and an area topic in its own chapter.
- **Status**: `active` while discovery is under way, `settled` once its understanding is agreed, `parked` when work stops without a conclusion. Only the person sets a topic settled or parked.

### Inputs: the idea, notes and materials

A topic can begin from a raw idea before any step has run: the most basic concept, an extension
of the project, a new project, or a rewrite of something that exists. The person, often through
the console, records two kinds of input beside `topic.md`:

- `notes.md`, from the `notes` template: the idea and the thoughts that follow it, oldest first,
  one line each, `- [N-<CODE>-<n>] <text> | by: <who> | date: <YYYY-MM-DD>`. `N-<CODE>-1` is the
  idea in the person's words when the topic began from one. Notes are the person's: never rewrite
  or delete one.
- `materials.md`, from the `materials` template: what the person brought to study, one line each,
  `- [S-<CODE>-<n>] <name> | kind: file|link|codebase|database|competitor|inspiration|person | location: <where> | feeds: research|concepts|landscape|system | status: not-read|read|unreachable | by: <who> | date: <YYYY-MM-DD> | note: <why it matters>`.
  Attached files sit in `discovery/<topic>/materials/`. A database is recorded by the **name** of
  the environment variable that holds its address, never the address.

An idea-stage project is a folder with only `.akka/project.yaml` (`stage: idea`) and
`discovery/`; the console makes one for a new project. `/akka:setup` adds the Akka SDK
scaffolding to that same folder when the project is ready for code.

The `discovery/` root keeps a **project-level set** of files: material about the whole project
that belongs to no single topic, and the project's shared concept list in
`discovery/concepts.md`. Its identifiers carry no code (`F-<n>`), which is also how identifiers
written before topics existed read.

### Input

The input is `<topic> <sub-command> [context]`:

| Input | What it does | Writes |
|-------|--------------|--------|
| *(nothing)* | Lists the topics and recommends the next step | nothing |
| `<topic>` | Reads the topic's notes and materials first, then shows where that topic stands and recommends its next step; creates the topic first if it does not exist | `discovery/<topic>/topic.md` when new; `status:` in `materials.md` |
| `<topic> research` | Gathers what is already known about the problem | `discovery/<topic>/research.md` |
| `<topic> landscape` | Compares the competitors, alternatives and substitutes | `discovery/<topic>/landscape.md` |
| `<topic> concepts` | Agrees the vocabulary and the domain concepts, promotes shared ones and finds conflicts | `discovery/<topic>/concepts.md`, `discovery/concepts.md` |
| `<topic> system` | Examines an existing system: its structure and its behaviour | `discovery/<topic>/system-map.md`, `discovery/<topic>/behaviour.md` |
| `<topic> confirm` | Explains the understanding item by item for a person to agree, amend, comment on or disagree with | `discovery/<topic>/understanding.md` |
| `<topic> mock` | Registers storyboards, mocks and animatics and records their review | `discovery/<topic>/mocks/index.md` |
| `--prework <engagement>` | Writes a pre-work prompt pack for someone to run before the first session | `discovery/prework/prompts.md` |

Read the input this way:

1. Empty: run the topic list.
2. It starts with `--prework`: run the pre-work step.
3. The first word is a sub-command word: the topic was left out. With exactly one topic in the project, use that one. With several, list them and ask which, with your suggestion. With none, ask the topic questions below and create it first.
4. Otherwise the first word is the topic name. A second word that is a sub-command runs that step for the topic; any other text is context. Text after the sub-command is context for it (for example `refunds system ../legacy-app` or `checkout mock mocks/checkout.html`).

### Creating a topic

When the named topic has no folder, create it before running any step. There is no separate
command for this. Ask these one at a time, each with your suggested answer:

1. What is the goal, or the question this topic should answer, in one sentence?
2. Is this a new idea, or a rebuild of a system that already exists? (the track)
3. What exists today: documents, a running system, earlier work, or nothing?

Then propose a code from the topic name that no other topic uses, set the scope (`project` when
the goal is about the whole project, otherwise the area), the status `active`, the owner (the
person, by name or role) and today's date, and write `discovery/<topic>/topic.md` from the
`topic` template. Record the goal as note `N-<CODE>-1` in `notes.md`, and each thing named in
the answer to question 3 as a material in `materials.md`, with `status: not-read`. Then read the
inputs as below, and run the requested step, or recommend the first one.

A topic the console created from an idea has the goal `Shape the idea in note N-<CODE>-1.` in
its `topic.md`. Before the first step, propose a one-sentence goal drawn from the idea and ask
the person to accept or reword it; on their answer, replace that goal in `topic.md` and change
nothing else in the header.

## Setup (every step)

1. **Prerequisite check**: Call `akka_sdd_list_specs`. If this MCP tool is not available, stop and tell the user: *"The Akka MCP server is not running. Run `/akka:setup` first, or run `akka specify init .` from the terminal."* The tool also tells you which specs exist, which the status check reports.
2. **Constitution**: Call `akka_sdd_constitution` and keep its principles in mind. A principle that limits what may be examined or shared (for example, no customer data in development) applies to discovery too. An idea-stage project (`.akka/project.yaml` with `stage: idea`) has no constitution until `/akka:setup` adds one: when the tool reports none, continue without it, do not run `akka specify init` in the project, and ask the person once whether any rule limits what may be examined or shared.
3. **Folders**: PROJECT_ROOT is the directory holding `.akka/` (or `pom.xml`). DISCOVERY_DIR is `PROJECT_ROOT/discovery/`. TOPIC_DIR is `DISCOVERY_DIR/<topic>/`. Create a folder the first time a step writes into it.
4. **Read what exists**: Read the topic's `topic.md` and every `.md` file in TOPIC_DIR, the project-level files at the DISCOVERY_DIR root, and the `topic.md` of every other topic, before asking anything. Read another topic's files when this one depends on them. Never ask a question a discovery file already answers.
5. **Read the inputs first**: before any other step's work, read the topic's `notes.md` and `materials.md` as described in *Reading the inputs* below. Every run of `/akka:discover <topic>`, with or without a sub-command, does this.
6. **Track and code**: Take the track and the code from the topic's `topic.md`, and record the topic and its code in the header of every file this run writes.
7. **Template**: Before writing a file for the first time, call `akka_sdd_get_template` with the template name in the step below, and follow its sections and record formats exactly. When the file already exists, add to it and keep what is there.
8. **Stay in the topic**: A step writes only in TOPIC_DIR, except that `concepts` adds reference lines to `discovery/concepts.md` and conflict items to another topic's `understanding.md`.

## Reading the inputs

The topic's notes and materials are read before anything else, every time the topic is named.

1. **Notes**: read every line of `notes.md`. The idea (`N-<CODE>-1`) and the notes after it say what the person is after; use them to choose questions and to word the goal. A note is not evidence: a claim taken from one is recorded as `stated: <who>, <date>` only after the person confirms it.
2. **Materials**: take each material whose status is `not-read`, and those marked `unreachable` when the person says it has been fixed. Read it for the steps its `feeds:` names:
   - **file** (documents, spreadsheets, slides) and **link**: read it for `research` (users, outcomes, constraints, prior work) and `concepts` (the words used and what they mean). Open an attached file from `discovery/<topic>/materials/` only to read its text; never run it.
   - **codebase**: the source for `system`. Pass its folder as `--source <location>` to `akka specify probes list` and `akka specify probes run`, as in the `system` step; do not read it by hand to count anything.
   - **database**: the input of the `schema` probe, by the variable's **name** only. Pass the name as `--database-var <NAME>` to `akka specify probes run`, as in the `system` step; the probe reads the database's catalogue through that variable. When the variable is not set in the environment the command says so, the probe reads the code base alone, and you tell the person the database was not reached. Never read the variable's value, print it, ask for it or write it anywhere.
   - **competitor** and **inspiration**: options and ideas for `landscape`. An inspiration is not a competitor: record what the person admires in it, not how it competes.
   - **person**: someone to ask, for `research`. Add them to Requests for Other People with what to ask; never contact anyone.
3. **Mark each one**: set its `status:` to `read` once read, or `unreachable` when it could not be opened (a file that is not there, a folder that does not exist, a link that does not answer, a variable that is not set), and tell the person what went wrong in one sentence. Change only the `status:` field of the line.
4. **Ask from what you found**: at most three plain questions, one at a time, each with your suggested answer, about what the inputs leave open or contradict. Ask nothing the notes or materials already answer.
5. **Cite**: a finding drawn from a material names it in its evidence as `S-<CODE>-<n>`, with a page, sheet or section when it helps (`evidence: S-PAY-2 sheet Q3`).

## Findings

A finding is one claim, the evidence for it, and how far to trust it. It is always one list line
in this exact form, so the console and the exit conditions can read it:

```text
- [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed
```

Findings about an existing system add the rung that established them:

```text
- [F-<CODE>-<n>] <claim> | evidence: <source> | status: observed | rung: exercised: <probe>
```

Rules for every finding:

- **Identifier**: `<CODE>` is the topic's code; `<n>` is unique within the topic. Before adding findings, find the highest `F-<CODE>-<n>` in TOPIC_DIR and continue from it. Never renumber or reuse a number; a finding that turns out wrong is corrected in place, keeping its number. Findings in the project-level set at the DISCOVERY_DIR root are written `F-<n>`, numbered after the highest `F-<n>` there.
- **Claim**: one plain sentence a reader new to the subject can follow. It never contains the character `|`.
- **Evidence**: one or more sources, separated by `; `, each something a reader can open or check:
  - a file path, with `:line` when it helps;
  - `S-<n>` from the Sources list in the topic's `research.md`, with a page or section;
  - `S-<CODE>-<n>`, a material from the topic's `materials.md`, with a page, sheet or section;
  - a URL;
  - a probe result, `.akka/discovery/<probe>.json`;
  - `stated: <role or name>, <YYYY-MM-DD>` for something a person said in this conversation;
  - `reasoning: <what it was reasoned from>`, for inferred findings only;
  - `understanding.md U-<CODE>-<n>`, added when a person confirms it.
- **Status**:
  - `observed`: seen directly in a source that addresses it. At least one source is not `reasoning:`.
  - `inferred`: reasoned rather than seen. Say what it was reasoned from.
  - `confirmed`: a person agreed to it, or to an amended wording, in `confirm`. Only that step sets this status, and the evidence then includes `understanding.md U-<CODE>-<n>`.
- **Never invent**. If you do not know, write the question under the file's Unknowns section, with the role most likely to know. An unknown is not a finding.
- **Lines that mention a finding** without defining it write the identifier without square brackets (`F-PAY-12`), because a line that starts with `[F-<CODE>-<n>]` defines that finding.

Every template marks some sections *required, or none*. Such a section is never deleted. When it
has nothing to record, its only line is `none: <what was checked>`, so a reader can tell
"checked and empty" from "not looked at".

## Talking with the person

- Ask one question at a time, never a list, and no more than five in a step, most important first. The items `confirm` presents and the reviews `mock` asks for are not counted as questions. Before asking, read the discovery files and anything the person pointed you to.
- For each question, offer your suggested answer and why, so the person can reply "yes".
- Write for someone who has never configured Akka. The first time you use a technical term, say what it means in a few plain words.
- When the person answers "don't know", record it under Unknowns with who might know, and move on.
- Never ask the person to paste credentials, personal data, customer records or anything a constitution principle forbids. Ask them to describe it instead.
- Record what the person tells you as findings with evidence `stated: <their name or role>, <date>`. Ask for their name or role once per session.
- Each step ends by telling the person, in two or three sentences, what was written, how many findings were added by status, and the recommended next step. It also rewrites the two sections of `topic.md` it keeps: Where It Stands, in one or two sentences, and Files, one line per file of the topic with its findings counted by status.

## No arguments: the topic list

1. Read every `discovery/*/topic.md`. For each topic, show its name, code, goal, track, scope, status and owner, and count its findings by status, its understanding items by response (with how many open, rethink or disagreed items are high-impact), and its mocks by approval.
2. Show the project-level set at the DISCOVERY_DIR root the same way, when it has files.
3. Count findings that no spec cites, and spec requirements that cite a finding that is not confirmed or does not exist. A spec cites a finding by writing its identifier in square brackets on a functional requirement bullet, such as `[F-PAY-3]`.
4. Recommend one next step, the first that applies:
   1. No topic exists: ask what the work is about and offer to create the first topic with `/akka:discover <topic>`. When the people who know the subject are not in this conversation, recommend `/akka:discover --prework <engagement>` first.
   2. For the active topic that has gone furthest, its next step as below.
5. Show the result as a short table of topics and counts, then the one recommendation with its reason. Write nothing.

## A topic with no sub-command: where the topic stands

1. List each of the topic's files and whether it exists: `notes.md`, `materials.md` (with how many materials are not read or unreachable), `research.md`, `landscape.md`, `concepts.md`, `system-map.md`, `behaviour.md`, `understanding.md`, `mocks/index.md`.
2. Count its findings by status, its understanding items by response and how many open, rethink or disagreed items are high-impact, and its mocks by approval (approved, changes-requested, pending).
3. Recommend one next step, the first that applies:
   1. The first missing file in the track's order:
      - ideation: research, landscape, concepts;
      - modernization: research, system, concepts, then landscape if the person wants alternatives compared.
   2. A UI is part of the work and the topic's `mocks/index.md` has nothing approved: `/akka:discover <topic> mock`.
   3. There are findings that are not confirmed, or high-impact items still open, rethink or disagreed: `/akka:discover <topic> confirm`.
   4. Otherwise: ask the person whether the topic is settled, and then `/akka:specify`, which cites the confirmed findings.
4. Show the result as a short table of files and counts, then the one recommendation with its reason. Write nothing, except `topic.md` when the topic was just created.

## research

**Purpose**: Gather what is already known about the problem: who it is for, what they need, what
success looks like, what constrains it, and what was tried before.

**Template**: `research`. **Writes**: `discovery/<topic>/research.md`.

1. Collect sources before asking anything: documents and links the person gave, files in the project (README, docs, prior specs), the pre-work outputs in `discovery/prework/` if they exist, and, if you have a web search tool and the person agrees to its use, public sources. List each source once under Sources as `S-<n>` with its owner, date and whether it looks current. A material from `materials.md` is not listed again: findings cite it by its own `S-<CODE>-<n>`.
2. Ask only for what the sources and the topic's goal do not answer, chosen from:
   - What are we making or replacing, in one or two sentences?
   - Who will use it, and what do they need to get done?
   - What would make this a success, with a number if there is one?
   - What must it respect: rules, approvals, dates, systems it must work with?
   - What has already been tried or decided?
3. Write findings into the sections Users and Needs, Outcomes and Measures, Constraints and Regulation, and Prior Work. A pre-work output marked `[KNOWN]` becomes an observed finding citing that file; `[INFERRED]` becomes inferred; `[UNKNOWN]` goes under Unknowns.
4. Write Unknowns and Requests for Other People: what to ask of which role, each with one sentence on why it matters.

## landscape

**Purpose**: Set out every way the job is done today or could be done, so the specification knows
what it competes with and what it must be better than.

**Template**: `landscape`. **Writes**: `discovery/<topic>/landscape.md`.

1. State the job being compared in one sentence, taken from the topic's goal and `research.md` when it exists.
2. List the options: competitors (sell the same thing), alternatives (a different product for the same job), substitutes (a spreadsheet, a manual step, an in-house tool) and the status quo (what happens if nothing is built). Always include the status quo.
3. Ask the person which dimensions matter to them. Suggest four to six that fit the job (for example cost to run, time to a result, accuracy, who can change it, how it is audited) and let them add, drop or rename. Number them `L-<n>`; `D-<n>` belongs to the plan's decisions.
4. Fill the comparison. Every cell either names the finding that supports it or reads `unknown`. Do not fill a cell from general impressions.
5. Under What This Means for the Specification, write the implications as inferred findings with `reasoning:` naming the findings they come from.

## concepts

**Purpose**: Agree what the words mean and which things have identity, state and rules. This feeds
the specification's Key Entities and the console glossary.

**Template**: `concepts`. **Writes**: `discovery/<topic>/concepts.md`; reference lines in `discovery/concepts.md`; conflict items in the `understanding.md` of each topic involved in a conflict.

1. Gather candidate terms from the topic's files, the sources, the project's shared concept list in `discovery/concepts.md` and, for a modernization, the names in `system-map.md`.
2. Ask the person for the words their people use, and for any term that means different things to different groups. Ask about states only where a concept clearly moves through some (an application is submitted, reviewed, decided).
3. Write the Glossary: one row per term, a one-sentence plain definition, words to avoid, and the finding behind it.
4. Write one block per concept, headed `### C-<CODE>-<n>: <name>`, with identity, states, relationships and rules. Each rule is a finding. Give each concept a `visual` block in the template's format: choose the one kind of the five that shows the concept best (a lifecycle is a state, a sequence of steps a flow, what it connects to a relationship) and fill only its lines. `/akka:docs` draws it in the project Story.
5. Record every disagreement about a term within the topic under Conflicting Usage, naming who uses which meaning. Do not pick a winner here; `confirm` asks the person.
6. **Single source**: a concept is defined in the topic where it arose and stays there. Never copy a concept block into another topic or into `discovery/concepts.md`. A topic that uses a concept another topic defines refers to it as `<CODE>/C-<CODE>-<n>`.
7. **Promote**: when a concept is used beyond this topic, or the person asks for it to be shared, propose promoting it. On the person's yes, add one reference line under the Shared heading of `discovery/concepts.md` (create the file from the `concepts` template, with Scope `project`, if it does not exist):

   ```text
   - see: <CODE>/C-<CODE>-<n> | shared
   ```

   and record it under Shared with the Project in the topic's `concepts.md`. The Story then draws the concept in its overview. Promotion changes nothing in the definition.
8. **Conflicts between topics**: compare every concept name in this topic with the concepts of every other topic and the shared list. When two topics define the same name differently, do not change either definition. Write a conflict item into the `understanding.md` of each topic involved, in the `confirm` structure below, with `impact: high`, `response: open`, `version: 1` and `| conflict: <CODE>/C-<CODE>-<n>, <CODE>/C-<CODE>-<n>`. Its explanation sets the two definitions side by side, says what depends on the difference and recommends one way to reconcile them: one name for both, two names, or one concept moved. Record it under Conflicts with Other Topics in the topic's `concepts.md`. The person reconciles it in `confirm`; nothing is changed before then.

## system

**Purpose**: Find out what an existing system is made of and how it actually behaves, by reading it
and, wherever possible, by running it. This is the heart of the modernization track: the old
system's behaviour is the answer key for the new one.

**Templates**: `system-map` and `behaviour`. **Writes**: `discovery/<topic>/system-map.md`, `discovery/<topic>/behaviour.md`. The probes record their results in `.akka/discovery/run.json` and `.akka/discovery/<probe>.json`.

### What to ask

Ask only what you cannot find out:

- Where is a readable copy of the system's source? (A folder path or a clone.)
- Is a copy of it running that we may send requests to? If so, at what address? Never send requests to a production system unless the person says it is safe.
- How deep should we go? Explain the three study levels in plain words:
  - **read**: look at the source only. Quick, but everything about behaviour stays a guess.
  - **run**: also send requests to a running copy and watch what it does. This is what turns a guess into an observation.
  - **diff**: also compare it with a running rebuild, request by request.
- Is a rebuild already running (only for diff)?

### The escalation ladder

Every claim about behaviour climbs this ladder until something authoritative settles it. Record the
rung that settled it in the finding's `rung:` field. These are the same words a specification's
requirement annotation uses.

| Rung | Action | `rung:` | Status it gives |
|------|--------|---------|-----------------|
| 1 | Read the source | `inspected` | `inferred`: reading produces a hypothesis, never a specification |
| 2 | Read documentation that addresses this exact case | `documented` | `observed` |
| 3 | Probe: run the system and observe | `exercised: <probe>` | `observed` |
| 4 | Docs are silent and running it shows no defined behaviour | `unresolvable` | `observed`, and listed under Decisions to Force |

Use the cheapest probe that answers the question. Before suggesting anything that needs new
infrastructure (a database, an account, an API key), say which cheaper rung you ruled out and why;
the old system's dependencies are not the investigation's dependencies.

Rules that apply on every rung:

- A claim with "every", "all", "none" or "only" cites something that enumerated the whole set (a probe result or a bill of materials), never a few examples.
- A name is not evidence. A claim about what something does cites its body or a run, never its identifier.
- A constant's meaning is where it is used, not where it is defined.
- A threshold, length or size rule is probed below, at and above the boundary, and recorded in Boundaries Probed.
- "Not found in what I read" is not "does not exist". Write it as an unknown with the next rung, not as a finding.
- Describe what the old system does. Never call it a bug or an accident; that is a claim about someone's intent.

### Steps

1. **See which probes can reach the system**. Run:

   ```text
   akka specify probes list --source <source path> --target <address> --study <read|run|diff>
   ```

   Leave out `--target` when nothing is running. Show the person, in plain words, which probes are available and which are not, with the reason for each (for example *"the timing probe needs a running copy"*). A probe that cannot run is reported, never silently skipped.

2. **Approval of declared probes**. A probe a project or organization declared is a command that runs with the person's privileges. If one is selected and not yet approved, show its exact command and ask the person whether to approve it. Run `akka specify probes approve <probe>` only after they say yes to that command. Built-in probes need no approval.

3. **Run the probes**. Run:

   ```text
   akka specify probes run --source <source path> --target <address> --study <level> [--probe +<name>,-<name>] [--database-var <NAME>]
   ```

   `--probe` adds or removes probes against the study level's defaults. `--database-var` takes the **name** of the environment variable that holds a database material's address, as recorded in `materials.md` (for example `CLAIMS_DB_URL`), never the address itself; the `schema` probe then reads the database's catalogue as well as the source. The database counts as available only when that variable is set in the environment the command runs in; if it is not, ask the person to set it in their own terminal, and never ask for its value. `run.json` records the name only. Report any probe that was withheld or failed, with its reason. A failed probe produced nothing, so no finding may cite it. To see one probe's raw exchange, use `akka specify probes test <probe>` with the same flags.

4. **Draft the findings the probes support**. Run `akka specify probes findings --topic <topic>`. It prints one finding line for each count a probe established (routes, tables, libraries, outside services called, tests and reachability), numbered after the highest `F-<CODE>-<n>` in the topic, and an Unknowns line for each gap a probe reported. Its numbers continue from the files as they are when it runs, so run it after this run's other findings are written, and copy each line into the right section of `system-map.md` or `behaviour.md` as written. `--write system-map` appends the lines under a `## Draft Findings` heading instead, which is not a template section: move them into place before the step ends.

5. **Bill of materials** (Akka services only). When the source is an Akka service, run `akka bom generate <source path> --out discovery/<topic>/bom`. Its AI bill of materials lists models, agents, prompts, tools, endpoints, flows and personal data, each with the file and line it was read from. Cite `discovery/<topic>/bom/<file>` as evidence.

6. **Write `system-map.md`**: the system studied, the inventory with a count for every kind (`0` where none exists; counts come from a probe or the bill of materials, never from reading by hand), structure findings, reachability (code that exists but never runs does not need rebuilding), test coverage, and the probes table.

7. **Write `behaviour.md`**: one finding per rule, grouped by capability, each with its rung. List every finding still at `inspected` under Read but Not Run with the probe that would settle it. List every `unresolvable` finding under Decisions to Force.

8. **Climb**. For each high-impact finding still at `inspected`, propose the probe or document that would settle it and ask whether to run it now.

Never start, stop or change a running system without asking. Never copy customer data out of it into discovery files.

## confirm

**Purpose**: Make sure the AI and the person understand the same thing. The AI explains what it
has understood, one item at a time, in words a reader who does not know the project's jargon can
follow, and the person agrees, amends, comments or disagrees. This is the only step that makes a
finding `confirmed`.

**Template**: `understanding`. **Writes**: `discovery/<topic>/understanding.md`, and updates the finding lines it confirms.

An understanding item is one list line that starts at the beginning of the line, with its
explanation and thread as indented lines beneath it:

```text
- [U-<CODE>-<n>] <restatement> | impact: high|normal | covers: F-<CODE>-<n>[, F-<CODE>-<n>] | response: agree|amend|rethink|disagree|open | version: <n> | reason: <reason> | by: <name or role> | date: <YYYY-MM-DD>
  - v1 (AI)
    - What I think you mean: <one or two sentences>
    - Why I am asking: <one sentence, including what depends on the answer>
    - My suggestion: <one sentence, only when there is a choice>
    - An example: <one sentence>
    - What changes if I am wrong: <one or two sentences>
  - comment (<name or role>, <YYYY-MM-DD>): <the person's words>
  - answer (<name or role>, <YYYY-MM-DD>): agree|amend|disagree
  - v2 (AI)
    - What I think you mean: ...
```

The indented lines are the item's thread, oldest first, and are never items of their own.
`version` is the version the response answers. An `answer` line records a response the person
gave after a comment without a new version being written; without it, a comment after the newest
version leaves the item unsettled.

### Every item has the same structure

Each version the AI writes has up to five parts, in this order, in plain language for a reader
who does not know the project's jargon. The first three are the default view, always shown when
the item is open. The last two are shown only when the person asks for more.

Default view:

1. **What I think you mean**: the understanding, in one or two sentences. Any term the project uses is explained in the same sentence.
2. **Why I am asking**: one sentence that also says what depends on the answer: which requirement, rule, test, gate or part of the design.
3. **My suggestion**: only when there is a choice to make, one sentence naming the option you suggest. Leave this part out when there is nothing to choose.

Behind one click ("More"):

4. **An example**: one sentence with a concrete case, with real-looking values.
5. **What changes if I am wrong**: one or two sentences on what would be built differently, or what would go wrong.

Write complete, plain sentences. Never ask a question that needs earlier context: every item can
be read on its own, without the conversation so far, another item or a finding the person has not
seen. Say plainly when an item rests on reading the source alone (rung `inspected`) or on
inference, so the person knows they are judging a guess.

### Steps

1. **Build the items**. Group the topic's findings that are not yet confirmed into items. Each item is one plain sentence (the restatement) in your own words that a person can judge without opening the evidence, and lists the findings it covers. Give an item `impact: high` when a wrong answer would change the scope, the data, a rule, a gate or a test; otherwise `normal`. Add every Conflicting Usage term and every Decisions to Force finding as its own item. Number new items after the highest `U-<CODE>-<n>` in the file. Write every new item into `understanding.md`, with its `v1 (AI)` explanation, `response: open` and `version: 1`, before asking anything, so nothing is lost if the conversation stops.
2. **Ask who is answering**: their name or role, recorded on each item they answer.
3. **Present one item at a time**, high-impact first, starting with items whose response is open. Show its identifier, its restatement and the three default parts of its newest version, and say that the example and the consequence of being wrong are behind "More"; show them when the person asks. Ask one question at a time, never a list. Do not present a summary and then offer to expand it: the default view is the item. Then ask for one of four answers:
   - **Agree**: the understanding is right. A reason is welcome.
   - **Amend**: the person rewrites the restatement in their own words.
   - **Comment**: the person says what is wrong or missing, and the item comes back to you.
   - **Disagree**: the understanding is wrong. A reason is required.
4. **Record each answer** on the item line, only from the person's own answer, and never fill a response the person did not give:
   - **Agree**: `response: agree`, `version` set to the version they answered, `reason`, `by`, `date`.
   - **Amend**: the person's wording replaces the restatement on the item line, and becomes the record. The AI's wording stays in the thread as its `v<n> (AI)` lines. Set `response: amend`, `version`, `reason`, `by`, `date`.
   - **Comment**: set `response: rethink`, `by` and `date`, and add the thread line `comment (<who>, <date>): <their words>` under the newest version. Then write the next version, `v<n+1> (AI)`, with its parts revised to answer the comment, raise `version` to it and set `response: open`. Present the revised version as the next question. The item keeps its identifier; nothing in the thread is deleted.
   - **An answer after a comment, with no new version**: when the person agrees, amends or disagrees with the version they commented on, without asking for it to be rewritten, record the response on the item line as above, with `version` unchanged, and add the thread line `answer (<who>, <date>): agree|amend|disagree` after their comment. That line is what settles the item; without it the comment leaves the item unsettled.
   - **Disagree**: `response: disagree`, `reason` (ask for it if they gave none), `by`, `date`.
5. **Apply each answer to the findings it covers**:
   - **Agree**: set each finding's status to `confirmed` and add `understanding.md U-<CODE>-<n>` to its evidence.
   - **Amend**: rewrite the finding's claim to the amended wording, set it to `confirmed`, and add `understanding.md U-<CODE>-<n>` to its evidence. When the item covers several findings, rewrite only the claims the amendment changes and confirm the others as they stand; a fact the amendment adds that no covered finding states becomes a new finding, with evidence `stated: <who>, <date>; understanding.md U-<CODE>-<n>` and status `confirmed`. If the amendment contradicts an observed or exercised finding, say so plainly with the evidence before recording it, and add a Decisions Raised row: the specification must choose between what the system does and what the person wants.
   - **Comment**: change no finding until the person agrees or amends.
   - **Disagree**: leave the finding's status as it was, add `understanding.md U-<CODE>-<n> (disagreed)` to its evidence, and add a Follow-ups line with the next step (probe it, ask someone, or record a decision). A disagreed high-impact item blocks the specification until it is settled.
   - **A conflict item**: apply the reconciliation the person chose to the concept blocks of both topics, and record it in both topics' `understanding.md`.
6. **Update Outcome**: counts by response, open high-impact items, and the session's date and participants.
7. **Report** which findings are now confirmed and citable, and which high-impact items remain open, rethink or disagreed. A high-impact item counts as settled only when its newest version has an agree or amend, and no comment follows that version without an `answer` line after it.

## mock

**Purpose**: Treat storyboards, mocks, animatics and prototypes as review artifacts, so that a
person's approval, or the changes they asked for, is recorded and a plan can gate on it.

**Template**: `mock-index`. **Writes**: `discovery/<topic>/mocks/index.md`.

A mock entry is one list line in this exact form:

```text
- [M-<CODE>-<n>] <title> | file: <path> | kind: storyboard|mock|animatic|prototype | version: <n> | shows: <what it illustrates> | approval: pending|approved by <who> on <YYYY-MM-DD>|changes-requested by <who> on <YYYY-MM-DD>
```

- **With a file path** in the input: register it. If the file is outside `discovery/<topic>/mocks/`, ask whether to copy it there; the index records the path relative to `discovery/<topic>/mocks/`. Ask what it is meant to show and which user stories, requirements or findings it illustrates, if that is not clear from the file. Add an entry numbered after the highest `M-<CODE>-<n>`, with `version: 1` and `approval: pending`. A revised file of an existing entry updates that entry's `file`, raises its `version` and sets `approval: pending` again.
- **Without a file path**: list the entries that are pending or have changes requested, and ask the person to review them. Tell them where each file is; do not open a browser unless they ask. For each, ask: **approve**, or **request changes**, with a reason.
- **Record each review** only from the reviewer's own answer: set the entry's `approval` to `approved by <who> on <date>` or `changes-requested by <who> on <date>`, and add a Review History line `- M-<CODE>-<n> v<n>: <approved|changes-requested> by <who> on <date>: <reason>`. Never approve on someone's behalf.
- Report which entries are approved, which wait for changes, and which plan gates they unblock.

## --prework: the pre-work prompt pack

**Purpose**: Before the first working session, the person who owns the problem (and often their
colleagues) gathers what is known, what is guessed and what nobody knows yet, using their own AI
assistant. This option writes the prompts they will run. The pack is neutral: it names no
customer, product or person; it uses placeholders the owner fills in.

**Writes**: `discovery/prework/prompts.md`. The files the prompts produce are brought back into `discovery/prework/`, where `/akka:discover <topic> research` reads them.

1. **Ask** (at most five questions, with suggested answers):
   - In a sentence, what is the engagement? (the `<engagement>` text, if given, may already answer this)
   - Is it a new idea or a rebuild of an existing system?
   - What is the role of the person who will run the prompts, and what do they know best?
   - Which AI assistant will they use, and can it search their documents and email?
   - What must never be pasted into the assistant (personal data, customer records, source code, credentials)?
2. **Write the pack** with these parts, in this order:
   1. **How to use**: run Prompt 0 at the start of every conversation; run one numbered prompt per conversation; save each output as a separate file, named exactly as shown, in one shared folder in the organization's approved storage; bring all files to the first session. Long conversations lose detail.
   2. **Request list first**: the prompts that need other people or exports, listed at the top with the role to ask and what to ask for, so those conversations start in parallel while the owner runs the rest.
   3. **Strongest model**: name the prompts that need the most careful reading and reasoning (the rules, tests and ground truth, the stakeholders, and the final brief), and say that the strongest model the assistant offers should be chosen for those. Any model is fine for the others.
   4. **Prompt 0: ground rules**, pasted first every time. It tells the assistant: who the owner is and what they know; never invent facts, write UNKNOWN and name the role who would know; label every statement [KNOWN] (the owner or a document said so), [INFERRED] (reasoned from general knowledge) or [UNKNOWN]; ask questions in one batch of at most seven, most important first; never ask for personal data, customer records, credentials or source code, and describe rather than paste; search the documents the owner can access before asking, and list every source used with title, owner, date and how current it seems; define technical terms in plain language the first time; finish each task with a Markdown document ending in Open questions; keep a running list of things the owner should find out.
   5. **Numbered prompts**, each with a "Save as `NN-name.md`" line, a request to ask up to seven questions first, and the sections the document must contain, always ending with Open questions. Start from the catalogue for the track, then drop, merge or add prompts to fit the engagement:
      - **ideation**: 01 problem and users; 02 how the job is done today (alternatives, substitutes, status quo); 03 vocabulary and concepts; 04 constraints, regulation and approvals; 05 stakeholders and what each wants; 06 pain, urgency and success measures with today's baseline; 07 kickoff brief.
      - **modernization**: 01 what the system is for; 02 the surrounding systems and the hand-offs between them; 03 the rules and calculations, with a request list for the people who maintain them; 04 tests and what "correct" means, including keeping the old system's results as the answer key; 05 constraints, regulation and approvals; 06 overlapping systems and any consolidation goal; 07 stakeholders and unstated ambitions, with an interview guide; 08 pain, urgency and success measures with today's baseline; 09 kickoff brief.
      - The **kickoff brief** is always last: run in the conversation that has seen the others, or with the other documents pasted in after confirming they hold nothing sensitive. It asks for the project in one paragraph; known, inferred and unknown as three lists; the ten open questions that could most change the plan, each with who can answer; the five biggest risks and how early each would show; contradictions between documents or stakeholders; decisions needed before design starts; three possible first-release scopes (small, medium, ambitious); a plain-language glossary; and a data and access request list with who must approve each item.
   6. **A seed for the specification**: a short paragraph with placeholders, describing what and why and not the technology, to refine after the pre-work.
3. **Report** the file path, the number of prompts, and which ones need other people first.


## Key rules

- Use absolute paths when reading and writing files.
- Findings, understanding items, concepts and mock entries use the exact forms above, with the topic's code: `[F-<CODE>-<n>]`, `[U-<CODE>-<n>]`, `### C-<CODE>-<n>:`, `[M-<CODE>-<n>]`. A line that starts with one of these identifiers in brackets and lacks a required field is an error, not an ignored line. The project-level set at the `discovery/` root writes the same forms without a code.
- A step writes in its own topic's folder. The exceptions are the reference lines and conflict items `concepts` writes, and nothing else.
- Only `confirm` sets a finding to `confirmed`, and only from a person's answer. Only `mock` records an approval, and only from the reviewer's answer. Only the person sets a topic settled or parked.
- A step adds to an existing file; it never deletes another step's findings or any line of an item's thread.
- `notes.md` and `materials.md` are the person's. Discovery adds a note or a material only from what the person said, and changes nothing in them but a material's `status:`. A database's address, and any password, key or token, is never written to a discovery file.
- Discovery refreshes the Story with `/akka:docs story` when the person settles a topic, and when a concept or a finding the Story cites changes, in the same session. A topic's chapter alone is `/akka:docs story <topic>`.
- Discovery never writes a specification. `/akka:specify` does, citing confirmed findings by identifier, such as `[F-PAY-3]`, from any topic.

## Done When

- [ ] `akka_sdd_list_specs` and `akka_sdd_constitution` were called, and the topic's files, the project-level files and every topic's `topic.md` were read before any question was asked.
- [ ] The topic's `notes.md` and `materials.md` were read first; every material read is marked `read` or `unreachable`; no more than three questions came from them; findings drawn from a material cite it as `S-<CODE>-<n>`; a database was used by its variable's name only.
- [ ] The topic and step were read from the input as described (the topic list ran when there was no input; with several topics and none named, the person was asked which); a new topic was created after at most three questions, with a code unique in the project and a name that is not a sub-command word.
- [ ] Each file written follows the template returned by `akka_sdd_get_template` for its step, records the topic and its code in its header, and every *required, or none* section has content or a `none: <what was checked>` line.
- [ ] Every finding added is one line `- [F-<CODE>-<n>] <claim> | evidence: <source> | status: observed|inferred|confirmed`, numbered after the highest number in the topic, with evidence a reader can open; behaviour and structure findings carry a `rung:`.
- [ ] Questions were asked one at a time, no more than five in the step; every "don't know" became an Unknowns line.
- [ ] `system`: probe availability was shown with reasons, declared probes ran only after the person approved their exact command, `.akka/discovery/run.json` was written by `akka specify probes run`, a database material was passed by its variable's name with `--database-var`, and no finding cites a probe that failed.
- [ ] `concepts`: every concept is defined once, in its topic; a promoted concept has one `- see: <CODE>/C-<CODE>-<n> | shared` line in `discovery/concepts.md` and was promoted on the person's yes; every concept name defined differently by two topics has a conflict item in each topic's `understanding.md`.
- [ ] `confirm`: items were presented one at a time, each showing the three default parts in plain language, readable on its own, with the example and the consequence behind "More"; every item is one `[U-<CODE>-<n>]` line with impact, covers, response and version, and its versions, comments and answer lines as indented thread lines; a response given after a comment without a new version has an `answer` line; every response, reason, comment, name and date came from the person; agreed and amended findings are `confirmed` with `understanding.md U-<CODE>-<n>` in their evidence.
- [ ] `mock`: every entry is one `[M-<CODE>-<n>]` line; every approval or change request came from the reviewer and is in Review History.
- [ ] `--prework`: the pack has how to use, the request list first, the strongest-model note, Prompt 0, numbered prompts each naming its output file, the kickoff brief last, and a specification seed, with no customer, product or person named.
- [ ] The report gave the files written, the findings added by status, and one recommended next step.
