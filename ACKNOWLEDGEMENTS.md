# Acknowledgements

This repository contains material adapted from third-party open-source projects.
This file reproduces the required copyright and license notices and describes
which parts are derived work.

## Spec Kit

The [`akka`](plugins/akka/) plugin
contains templates and command prompts adapted from Spec Kit
(<https://github.com/github/spec-kit>), an open-source specification-driven
development toolkit by GitHub, Inc. Spec Kit is distributed under the MIT
License, reproduced below.

### Files derived from Spec Kit

Templates (`plugins/akka/templates/`):

- `checklist-template.md`
- `constitution-template.md`
- `plan-template.md`
- `spec-template.md`
- `tasks-template.md`

Commands (`plugins/akka/commands/`):

- `analyze.md` (derived, extended with Akka MCP tools)
- `checklist.md` (derived)
- `clarify.md` (derived)
- `constitution.md` (derived, extended for `akka_sdd_constitution` MCP tool)
- `converge.md` (derived)
- `implement.md` (derived, substantially extended with Akka feature-branch,
  ignore-file, and merge-to-main flows)
- `issues.md` (derived from `taskstoissues.md`)
- `plan.md` (derived)
- `specify.md` (derived, adapted to `akka_sdd_create_spec` MCP tool)
- `tasks.md` (derived)

### Files original to this repository

- `plugins/akka/commands/setup.md`
- `plugins/akka/commands/build.md`
- `plugins/akka/commands/deploy.md`
- `plugins/akka/commands/inspect.md`
- `plugins/akka/commands/reliability.md`
- `plugins/akka/commands/review.md` (heavily rewritten from spec-kit's version;
  effectively new)
- `plugins/akka/templates/review-checklist-template.md`

## Diagram Design

The [`akka`](plugins/akka/) plugin's documentation graphics adapt material from
Diagram Design (<https://github.com/cathrynlavery/diagram-design>), an
open-source diagramming skill by Cathryn Lavery, distributed under the MIT
License, reproduced below.

### Files derived from Diagram Design

- `plugins/akka/harnesses/content/diagram_check.py` — the accessible-SVG
  contract and the label-mask geometry rule are derived from that project's
  `scripts/self_check.py` and `scripts/verify-geometry.py`. The Akka palette
  check and the connector checks are original to this repository.

### Concepts adapted, without copied text

`plugins/akka/commands/docs.md` and `plugins/akka/templates/docs-template.html`
adopt that project's *grammar* — mandatory rounded right-angle connectors,
fanned attach points, the masked-label gap, the 4px grid, the per-diagram
complexity budget, and the separation of a skin from the rules that draw on it.
The skin itself is Akka's own and is not derived: `akka-style-guide.md` replaces
that project's `references/style-guide.md` with Akka's dark palette, and the
editorial-versus-categorical color split resolves a conflict between the two
systems rather than adopting either wholesale.

### Diagram Design MIT License

```
MIT License

Copyright (c) 2025 Cathryn Lavery

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Spec Kit MIT License

```
MIT License

Copyright GitHub, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
