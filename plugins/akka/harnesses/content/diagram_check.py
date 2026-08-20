#!/usr/bin/env python3
"""Structural checks for the diagrams in a generated docs/ page.

Ships with the Akka plugin and is copied into a project's /harnesses/content/
by /akka:docs. Feeds the CONTENT-LANGUAGE condition, which owns the falsifiable
structural conventions of the documentation surface.

    python diagram_check.py docs/index.html

Exit 0 = green, 1 = red (findings printed), 2 = could not run.

No third-party dependencies: the standard library only, so it runs wherever
Python does and never turns a missing package into a false red.

Derived from self_check.py and verify-geometry.py in cathrynlavery/diagram-design
(MIT, (c) 2025 Cathryn Lavery). The accessible-SVG contract and the label-mask
geometry rule are that project's; the Akka skin, budget and grid rules are not.

WHAT IS DELIBERATELY NOT CHECKED, and why -- a check that misfires is worse than
no check, because people learn to ignore it:

  * Elbow radius and attach-point spacing. Both need the connector's endpoints
    resolved out of a path `d`, and a wrong answer would red a correct page.
  * The 6-10px label gap. Measuring it needs to know which connector a label
    belongs to, which is not recoverable from the markup.
  * Paint order. "Connectors before nodes" holds for node graphs but is false
    for sequence diagrams, where lane headers are drawn first by construction.
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
ACCENT = "#f5c518"

# The lookbehind keeps numeric HTML entities (&#9654; -- the chevron) from
# being read as colors.
HEX_RE = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b")

# Mojibake: UTF-8 bytes that were read as Latin-1 and re-encoded. The em dash
# (E2 80 94) is the one that actually shows up in these pages.
MOJIBAKE = {
    "â€”": "em dash",
    "â€™": "apostrophe",
    "â€": "opening quote",
    "Â·": "middle dot",
}

DIAGONAL_TOLERANCE = 0.5
GRID = 4

# Per diagram, from the style guide.
MAX_NODES = 9
MAX_CONNECTORS = 12
MAX_LANES = 5
MAX_ACCENTS = 2


def num(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.svgs: list[dict] = []
        self.scripts = 0
        self.remote: list[str] = []
        self.body_classes: set[str] = set()
        self._svg: dict | None = None
        self._depth = 0
        self._defs = 0
        self._capture: str | None = None
        self._order = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        self._order += 1
        for cls in a.get("class", "").split():
            self.body_classes.add(cls)

        if tag == "svg":
            self._depth += 1
            if self._depth == 1:
                self._svg = {
                    "role": a.get("role", ""), "labelledby": a.get("aria-labelledby", ""),
                    "hidden": a.get("aria-hidden", ""), "children": [],
                    "title_id": "", "desc_id": "", "title_text": "", "desc_text": "",
                    "shapes": [],
                }
                self.svgs.append(self._svg)
        elif self._svg is not None and tag in ("title", "desc"):
            self._svg["children"].append(tag)
            self._svg[f"{tag}_id"] = a.get("id", "")
            self._capture = tag
        elif self._svg is not None and tag == "defs":
            self._svg["children"].append("defs")
            self._defs += 1
        elif self._svg is not None and tag in ("rect", "line", "path", "polygon", "text"):
            self._svg["shapes"].append(
                {"tag": tag, "attrs": a, "order": self._order, "in_defs": self._defs > 0}
            )

        if a.get("src", "").startswith(("http://", "https://", "//")):
            self.remote.append(a["src"])
        href = a.get("href", "")
        if href.startswith(("http://", "//")):
            self.remote.append(href)
        elif href.startswith("https://") and "fonts.googleapis.com" not in href:
            self.remote.append(href)
        if tag == "script":
            self.scripts += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "svg":
            self._depth -= 1
            if self._depth == 0:
                self._svg = None
        elif tag == "defs" and self._defs:
            self._defs -= 1
        if tag == self._capture:
            self._capture = None

    def handle_data(self, data):
        if self._capture and self._svg is not None:
            self._svg[f"{self._capture}_text"] += data.strip()


def box(shape: dict) -> tuple[float, float, float, float] | None:
    a = shape["attrs"]
    x, y, w, h = (num(a.get(k, "")) for k in ("x", "y", "width", "height"))
    if None in (x, y, w, h):
        return None
    return x, y, w, h


def overlaps(p, q) -> bool:
    return p[0] < q[0] + q[2] and p[0] + p[2] > q[0] and p[1] < q[1] + q[3] and p[1] + p[3] > q[1]


def check_accessibility(svg: dict, where: str, out: list[str]) -> None:
    if svg["role"] != "img":
        out.append(f'{where}: needs role="img"')
    if not svg["children"] or svg["children"][0] != "title":
        out.append(f"{where}: <title> must be the first child, before <defs>")
    if not svg["title_text"]:
        out.append(f"{where}: <title> is empty")
    if not svg["desc_text"]:
        out.append(f"{where}: <desc> is empty")
    for kind in ("title", "desc"):
        if kind not in svg["children"]:
            continue
        ident = svg[f"{kind}_id"]
        if not ident:
            out.append(f"{where}: <{kind}> needs an id")
        elif ident in ("title", "desc"):
            out.append(
                f"{where}: <{kind}> id is bare '{ident}' — must be diagram-prefixed, "
                f"or two diagrams collide"
            )
    want = f"{svg['title_id']} {svg['desc_id']}".strip()
    if svg["labelledby"].split() != want.split() or not want:
        out.append(
            f'{where}: aria-labelledby must name title then desc '
            f'(expected "{want}", got "{svg["labelledby"]}")'
        )
    if len(svg["title_text"]) > 60:
        out.append(f"{where}: <title> is {len(svg['title_text'])} chars, keep it under 60")


def check_geometry(svg: dict, where: str, out: list[str]) -> None:
    """Grid alignment, diagonal connectors, and masks clipped by later nodes."""
    for s in svg["shapes"]:
        a = s["attrs"]
        if s["tag"] == "line":
            pts = {k: num(a.get(k, "")) for k in ("x1", "y1", "x2", "y2")}
            if None not in pts.values():
                if abs(pts["x2"] - pts["x1"]) > DIAGONAL_TOLERANCE and \
                   abs(pts["y2"] - pts["y1"]) > DIAGONAL_TOLERANCE:
                    out.append(
                        f"{where}: diagonal <line> ({pts['x1']:g},{pts['y1']:g}) to "
                        f"({pts['x2']:g},{pts['y2']:g}) — off-axis connectors must be "
                        f"rounded right-angle <path> elbows"
                    )
                for k, v in pts.items():
                    if v % GRID:
                        out.append(f"{where}: <line> {k}={v:g} is off the {GRID}px grid")
        elif s["tag"] == "rect" and not s["in_defs"]:
            b = box(s)
            if b:
                for name, v in zip(("x", "y", "width", "height"), b):
                    if v % GRID:
                        out.append(f"{where}: <rect> {name}={v:g} is off the {GRID}px grid")

    # A mask painted before a node that overlaps it gets clipped by the node fill,
    # and the label renders as a fragment on the node border.
    rects = [s for s in svg["shapes"] if s["tag"] == "rect" and not s["in_defs"] and box(s)]
    masks = [s for s in rects if "emask" in s["attrs"].get("class", "")
             or (18 <= box(s)[2] <= 200 and 8 <= box(s)[3] <= 14)]
    nodes = [s for s in rects if s not in masks and box(s)[2] >= 60 and box(s)[3] >= 28]
    for m in masks:
        for n in nodes:
            if n["order"] > m["order"] and overlaps(box(m), box(n)):
                mb, nb = box(m), box(n)
                out.append(
                    f"{where}: label mask at ({mb[0]:g},{mb[1]:g}) is overlapped by a node "
                    f"at ({nb[0]:g},{nb[1]:g}) drawn after it — the node fill clips the text"
                )


def check_budget(svg: dict, where: str, out: list[str]) -> None:
    rects = [s for s in svg["shapes"] if s["tag"] == "rect" and not s["in_defs"] and box(s)]
    masks = [s for s in rects if "emask" in s["attrs"].get("class", "")
             or (18 <= box(s)[2] <= 200 and 8 <= box(s)[3] <= 14)]
    nodes = [s for s in rects if s not in masks and box(s)[2] >= 60 and box(s)[3] >= 28]
    # A lane header is a wide, short box along the top edge.
    lanes = [s for s in nodes if box(s)[1] < 64 and box(s)[3] <= 40 and box(s)[2] >= 100]

    # Two idioms: marker-end on the stroke, or a separate polygon arrowhead.
    connectors = [s for s in svg["shapes"] if not s["in_defs"] and (
        (s["tag"] in ("line", "path") and s["attrs"].get("marker-end"))
        or s["tag"] == "polygon")]
    accents = [s for s in svg["shapes"]
               if s["tag"] in ("line", "path") and not s["in_defs"]
               and (s["attrs"].get("stroke", "").lower() == ACCENT
                    or "evt" in s["attrs"].get("class", "").split())]

    for count, limit, what in (
        (len(nodes), MAX_NODES, "nodes"),
        (len(connectors), MAX_CONNECTORS, "connectors"),
        (len(lanes), MAX_LANES, "lanes"),
        (len(accents), MAX_ACCENTS, "accent strokes"),
    ):
        if count > limit:
            out.append(
                f"{where}: {count} {what}, budget is {limit} — split into an overview "
                f"plus a detail diagram rather than shrinking the type"
            )


def check_labels_masked(svg: dict, where: str, out: list[str]) -> None:
    """Every connector label needs an opaque plate, or it bleeds through its line."""
    rects = [s for s in svg["shapes"] if s["tag"] == "rect" and not s["in_defs"] and box(s)]
    for s in svg["shapes"]:
        if s["tag"] != "text" or s["in_defs"]:
            continue
        a = s["attrs"]
        is_label = "elbl" in a.get("class", "").split() or a.get("font-size") == "8"
        x, y = num(a.get("x", "")), num(a.get("y", ""))
        if not is_label or x is None or y is None:
            continue
        # The plate sits behind the glyphs: same column, spanning the cap height.
        if not any(r[0] <= x <= r[0] + r[2] and r[1] <= y - 3 <= r[1] + r[3]
                   for r in map(box, rects)):
            out.append(
                f"{where}: connector label at ({x:g},{y:g}) has no mask rect behind it — "
                f"it will bleed through its own connector"
            )


def check(path: Path) -> list[str]:
    raw = path.read_bytes()
    src = raw.decode("utf-8", errors="replace")
    out: list[str] = []

    # --- encoding ---------------------------------------------------------
    if raw[:3] == b"\xef\xbb\xbf":
        out.append("file starts with a UTF-8 BOM — write it without one")
    for seq, name in MOJIBAKE.items():
        if seq in src:
            out.append(
                f"mojibake: {src.count(seq)} occurrence(s) of a double-encoded {name} — "
                f"the file was read as Latin-1 and rewritten as UTF-8"
            )
    if "�" in src:
        out.append("file contains U+FFFD replacement characters — it is not valid UTF-8")

    p = Page()
    p.feed(src)

    for i, svg in enumerate(p.svgs, 1):
        if svg["hidden"] == "true":
            continue  # decorative, correctly opted out
        where = f"svg {i} ({svg['title_text'] or 'untitled'})"
        check_accessibility(svg, where, out)
        check_geometry(svg, where, out)
        check_budget(svg, where, out)
        check_labels_masked(svg, where, out)

    # --- every class used must have a rule ---------------------------------
    # An undefined class falls back to SVG defaults: black fill, no stroke. On
    # this dark ground that is an invisible diagram, and nothing else catches it.
    style = "".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S))
    defined = set(re.findall(r"\.([A-Za-z][\w-]*)", style))
    for cls in sorted(p.body_classes - defined):
        out.append(f"class '{cls}' is used but has no CSS rule — it renders as SVG defaults")

    # --- single-file safety -----------------------------------------------
    for url in p.remote:
        out.append(f"remote asset not allowed in a self-contained page: {url}")
    if p.scripts:
        out.append(f"{p.scripts} <script> element(s) — docs/index.html is static")

    # --- Akka skin ---------------------------------------------------------
    for c in sorted({c.lower() for c in HEX_RE.findall(src)} - ALLOWED_COLORS):
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
