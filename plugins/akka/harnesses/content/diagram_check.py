#!/usr/bin/env python3
"""Structural checks for the diagrams in a generated docs/ page.

Ships with the Akka plugin and is copied into a project's /harnesses/content/
by /akka:docs. Feeds the CONTENT-LANGUAGE condition, which owns the falsifiable
structural conventions of the documentation surface.

    python diagram_check.py docs/index.html

Exit 0 = green, 1 = red (findings printed), 2 = could not run.

No third-party dependencies: the standard library only, so it runs wherever
Python does and never turns a missing package into a false red.

Derived from self_check.py in cathrynlavery/diagram-design (MIT, (c) 2025
Cathryn Lavery). The accessible-SVG contract and the label-mask geometry rule
are that project's; the Akka skin rules and the connector checks are not.
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# --- Akka skin, from templates/akka-style-guide.md ------------------------
# The template is the design. A generated page may only use these values.
ALLOWED_COLORS = {
    "#070707", "#0a0a0a", "#050505", "#0d0d0d", "#141414", "#1c1c1c", "#1a1600",
    "#120a1a", "#04180a", "#0f1418", "#2a2a2a", "#333",
    "#f5c518", "#f5f5f5", "#fff", "#ffffff", "#b8b8b8", "#999", "#9a9a9a",
    "#888", "#8a8a8a", "#666", "#6a6a6a", "#555", "#546e7a", "#aaa", "#ccc",
    "#28c840", "#a855f7", "#7ec8e3", "#ff6b6b", "#c792ea", "#ffcb6b",
    "#c3e88d", "#82aaff", "#f78c6c", "#b0bec5", "#5a4a00",
}
# The lookbehind keeps numeric HTML entities (&#9654; — the chevron) from
# being read as colors.
HEX_RE = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b")

# A connector between off-axis nodes must be a rounded orthogonal path.
# A <line> is only legitimate when its endpoints share an axis.
DIAGONAL_TOLERANCE = 0.5


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.svgs: list[dict] = []
        self.lines: list[dict] = []
        self.scripts = 0
        self.remote: list[str] = []
        self._svg: dict | None = None
        self._depth = 0
        self._capture: str | None = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}

        if tag == "svg":
            self._depth += 1
            if self._depth == 1:
                self._svg = {
                    "role": a.get("role", ""),
                    "labelledby": a.get("aria-labelledby", ""),
                    "hidden": a.get("aria-hidden", ""),
                    "children": [],
                    "title_id": "",
                    "desc_id": "",
                    "title_text": "",
                    "desc_text": "",
                }
                self.svgs.append(self._svg)
        elif self._svg is not None and tag in ("title", "desc"):
            self._svg["children"].append(tag)
            self._svg[f"{tag}_id"] = a.get("id", "")
            self._capture = tag
        elif self._svg is not None and tag == "defs":
            self._svg["children"].append("defs")
        elif tag == "line":
            try:
                self.lines.append({
                    "x1": float(a.get("x1", 0)), "y1": float(a.get("y1", 0)),
                    "x2": float(a.get("x2", 0)), "y2": float(a.get("y2", 0)),
                })
            except ValueError:
                pass
        elif tag == "script":
            self.scripts += 1
        # No src is ever legitimately remote in a self-contained page. Only a
        # stylesheet href gets the Google Fonts exemption.
        if a.get("src", "").startswith(("http://", "https://", "//")):
            self.remote.append(a["src"])
        href = a.get("href", "")
        if href.startswith(("http://", "//")):
            self.remote.append(href)
        elif href.startswith("https://") and "fonts.googleapis.com" not in href:
            self.remote.append(href)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "svg":
            self._depth -= 1
            if self._depth == 0:
                self._svg = None
        if tag == self._capture:
            self._capture = None

    def handle_data(self, data):
        if self._capture and self._svg is not None:
            self._svg[f"{self._capture}_text"] += data.strip()


def check(path: Path) -> list[str]:
    src = path.read_text(encoding="utf-8", errors="replace")
    p = Page()
    p.feed(src)
    out: list[str] = []

    # --- accessible-SVG contract -----------------------------------------
    for i, svg in enumerate(p.svgs, 1):
        if svg["hidden"] == "true":
            continue  # decorative, correctly opted out
        where = f"svg {i}"
        if svg["role"] != "img":
            out.append(f"{where}: needs role=\"img\"")
        if not svg["children"] or svg["children"][0] != "title":
            out.append(f"{where}: <title> must be the first child, before <defs>")
        if not svg["title_text"]:
            out.append(f"{where}: <title> is empty")
        if not svg["desc_text"]:
            out.append(f"{where}: <desc> is empty")
        for kind in ("title", "desc"):
            if kind not in svg["children"]:
                continue  # absence is already reported as an empty element
            ident = svg[f"{kind}_id"]
            if not ident:
                out.append(f"{where}: <{kind}> needs an id")
            elif ident in ("title", "desc"):
                out.append(
                    f"{where}: <{kind}> id is bare '{ident}' — must be "
                    f"diagram-prefixed, or two diagrams collide"
                )
        want = f"{svg['title_id']} {svg['desc_id']}".strip()
        if svg["labelledby"].split() != want.split() or not want:
            out.append(
                f"{where}: aria-labelledby must name title then desc "
                f"(expected \"{want}\", got \"{svg['labelledby']}\")"
            )
        if len(svg["title_text"]) > 60:
            out.append(f"{where}: <title> is {len(svg['title_text'])} chars, keep it under 60")

    # --- connector geometry ----------------------------------------------
    for ln in p.lines:
        dx, dy = abs(ln["x2"] - ln["x1"]), abs(ln["y2"] - ln["y1"])
        if dx > DIAGONAL_TOLERANCE and dy > DIAGONAL_TOLERANCE:
            out.append(
                f"diagonal <line> from ({ln['x1']:g},{ln['y1']:g}) to "
                f"({ln['x2']:g},{ln['y2']:g}) — off-axis connectors must be "
                f"rounded right-angle <path> elbows"
            )

    # --- single-file safety ----------------------------------------------
    for url in p.remote:
        out.append(f"remote asset not allowed in a self-contained page: {url}")
    if p.scripts:
        out.append(f"{p.scripts} <script> element(s) — docs/index.html is static")

    # --- Akka skin -------------------------------------------------------
    off = {c.lower() for c in HEX_RE.findall(src)} - ALLOWED_COLORS
    for c in sorted(off):
        out.append(f"color {c} is not in the Akka palette — the template is the design")

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()

    failed = False
    for path in args.paths:
        if not path.exists():
            print(f"CANNOT RUN  {path}: no such file", file=sys.stderr)
            return 2
        findings = check(path)
        if findings:
            failed = True
            print(f"RED  {path}")
            for f in findings:
                print(f"  - {f}")
        else:
            print(f"GREEN  {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
