#!/usr/bin/env python3
"""Generate per-harness plugin artifacts for the `akka` plugin from the single
source of truth: plugins/akka/commands/*.md.

Emits (repo-root, so each harness's native installer resolves this one repo):
  - Gemini CLI:  gemini-extension.json + commands/akka/<name>.toml
  - Codex CLI:   .codex-plugin/plugin.json (MCP server declared inline)
                 + skills/akka-<name>/SKILL.md + .agents/plugins/marketplace.json

Claude Code (.claude-plugin/marketplace.json + plugins/akka/commands/*.md) is the
source and is left untouched. The `akka mcp serve` MCP server is registered in each
harness so the akka toolset is available regardless of command format.

Run from the repo root:  python3 bin/generate-harnesses.py
"""
import json
import os
import re
import glob
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "plugins", "akka", "commands")
PLUGIN_JSON = json.load(open(os.path.join(ROOT, "plugins", "akka", ".claude-plugin", "plugin.json"), encoding="utf-8"))
VERSION = PLUGIN_JSON.get("version", "0.0.0")

# The harness-agnostic MCP server (Claude registers this per-project via `akka
# specify init`; for the other harnesses we bundle it in the plugin manifest).
MCP = {"command": "akka", "args": ["mcp", "serve"]}


def parse_command(path):
    """Return (name, description, body) for a command markdown file."""
    name = os.path.splitext(os.path.basename(path))[0]
    text = open(path, encoding="utf-8").read()
    description, body = "", text
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", text, re.DOTALL)
    if m:
        fm, body = m.group(1), m.group(2)
        dm = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if dm:
            description = dm.group(1).strip().strip('"').strip("'")
    return name, description, body.strip()


def commands():
    return [parse_command(p) for p in sorted(glob.glob(os.path.join(SRC, "*.md")))]


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def reset_dir(path):
    """Remove a generated output tree so renamed/deleted commands leave nothing behind."""
    if os.path.isdir(path):
        shutil.rmtree(path)


def gen_gemini(cmds):
    """Gemini CLI extension: gemini-extension.json + commands/akka/*.toml."""
    manifest = {
        "name": "akka",
        "version": VERSION,
        "description": PLUGIN_JSON.get("description", "Akka SDK development tools"),
        "mcpServers": {"akka": MCP},
    }
    write(os.path.join(ROOT, "gemini-extension.json"),
          json.dumps(manifest, indent=2) + "\n")
    reset_dir(os.path.join(ROOT, "commands", "akka"))
    for name, desc, body in cmds:
        # $ARGUMENTS (Claude) -> {{args}} (Gemini)
        prompt = body.replace("$ARGUMENTS", "{{args}}")
        # TOML triple-quoted basic string: escape backslashes first (so regexes
        # like \bT\d{3}\b and sed's \(...\1 survive), then guard against a """
        # terminating the string early.
        prompt = prompt.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        toml = ""
        if desc:
            toml += f"description = {json.dumps(desc)}\n\n"
        toml += 'prompt = """\n' + prompt + '\n"""\n'
        write(os.path.join(ROOT, "commands", "akka", f"{name}.toml"), toml)
    return len(cmds)


def codex_body(body):
    """Codex has no $ARGUMENTS substitution — a skill reads the live conversation.
    Drop the literal placeholder block and reword any remaining references so the
    skill never shows an unsubstituted `$ARGUMENTS` token."""
    body = re.sub(r"```text\r?\n\$ARGUMENTS\r?\n```\r?\n+", "", body)
    return body.replace("$ARGUMENTS", "the user's request")


def gen_codex(cmds):
    """Codex CLI plugin: .codex-plugin/plugin.json + skills/ + marketplace."""
    # Declare the MCP server inline in plugin.json (a spec-supported form) rather
    # than via a companion ./.mcp.json at the plugin root. Because the plugin root
    # is the repo root, an inline object keeps the whole Codex config under
    # .codex-plugin/ and leaves no root file to collide with Claude Code's own
    # project ./.mcp.json. Codex uses the same `mcpServers` key Claude Code does.
    write(os.path.join(ROOT, ".codex-plugin", "plugin.json"), json.dumps({
        "name": "akka",
        "version": VERSION,
        "description": PLUGIN_JSON.get("description", "Akka SDK development tools"),
        "author": PLUGIN_JSON.get("author", {"name": "Akka"}),
        "skills": "./skills/",
        "mcpServers": {"akka": MCP},
    }, indent=2) + "\n")
    reset_dir(os.path.join(ROOT, "skills"))
    for name, desc, body in cmds:
        skill = "---\n"
        skill += f"name: akka-{name}\n"
        if desc:
            skill += f"description: {json.dumps(desc)}\n"
        skill += "---\n\n" + codex_body(body) + "\n"
        write(os.path.join(ROOT, "skills", f"akka-{name}", "SKILL.md"), skill)
    write(os.path.join(ROOT, ".agents", "plugins", "marketplace.json"), json.dumps({
        "name": "ai-marketplace",
        "interface": {"displayName": "Akka AI Marketplace"},
        "plugins": [{
            "name": "akka",
            "source": {"source": "local", "path": "."},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Development",
        }],
    }, indent=2) + "\n")
    return len(cmds)


def main():
    cmds = commands()
    g = gen_gemini(cmds)
    c = gen_codex(cmds)
    print(f"source commands: {len(cmds)}")
    print(f"gemini: gemini-extension.json + {g} commands/akka/*.toml")
    print(f"codex:  .codex-plugin/plugin.json + {c} skills/ + .agents/plugins/marketplace.json")


if __name__ == "__main__":
    main()
