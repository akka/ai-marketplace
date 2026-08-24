#!/usr/bin/env python3
"""Generate per-harness plugin artifacts for the `akka` plugin from the single
source of truth: plugins/akka/commands/*.md.

Emits (repo-root, so each harness's native installer resolves this one repo):
  - Gemini CLI:  gemini-extension.json + commands/<name>.toml
  - Codex CLI:   .codex-plugin/plugin.json (MCP server declared inline)
                 + skills/<name>/SKILL.md + .agents/plugins/marketplace.json
  - Antigravity / AGY: mcp_config.json (reusing root plugin.json and skills/)
  - Agent Plugins 1.0.0 (agent-plugins.org): plugin.json + mcp.json, reusing the
                 root skills/ tree the Codex target already emits at the location
                 the spec mandates. Additive — no existing harness reads these.

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

# Agent Plugins spec version pinned in the emitted $schema URLs.
SPEC_VERSION = "1.0.0"


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
    """Gemini CLI extension: gemini-extension.json + commands/*.toml."""
    manifest = {
        "name": "akka",
        "version": VERSION,
        "description": PLUGIN_JSON.get("description", "Akka SDK development tools"),
        "mcpServers": {"akka": MCP},
    }
    write(os.path.join(ROOT, "gemini-extension.json"),
          json.dumps(manifest, indent=2) + "\n")
    reset_dir(os.path.join(ROOT, "commands"))
    for name, desc, body in cmds:
        # $ARGUMENTS (Claude) -> {{args}} (Gemini)
        prompt = body.replace("$ARGUMENTS", "{{args}}")
        # TOML triple-quoted basic string: escape backslashes first (so regexes
        # like \bT\d{3}\b and sed's \(...\1 survive), then guard against a """
        # terminating the string early.
        prompt = prompt.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        toml = ""
        if desc:
            # ensure_ascii=False: the file is UTF-8 and the prompt body below is
            # written unescaped, so an escaped description would spell the same
            # character two ways in one file.
            toml += f"description = {json.dumps(desc, ensure_ascii=False)}\n\n"
        toml += 'prompt = """\n' + prompt + '\n"""\n'
        write(os.path.join(ROOT, "commands", f"{name}.toml"), toml)
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
        skill += f"name: {name}\n"
        if desc:
            skill += f"description: {json.dumps(desc, ensure_ascii=False)}\n"
        skill += "---\n\n" + codex_body(body) + "\n"
        write(os.path.join(ROOT, "skills", name, "SKILL.md"), skill)
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


def gen_antigravity():
    """Antigravity / AGY CLI: mcp_config.json at the plugin root.

    Antigravity discovers plugins using root `plugin.json` (emitted by
    gen_agent_plugins), skills under `skills/` (emitted by gen_codex),
    and MCP servers under `mcp_config.json`.
    """
    write(os.path.join(ROOT, "mcp_config.json"), json.dumps({
        "mcpServers": {"akka": MCP},
    }, indent=2) + "\n")


def gen_agent_plugins():
    """Agent Plugins 1.0.0: plugin.json + mcp.json at the plugin root.

    The spec fixes component locations rather than declaring them: skills are
    discovered at skills/<name>/SKILL.md — exactly where gen_codex already writes
    them — so this target only has to emit the two manifests. Must run after
    gen_codex, which resets skills/.

    Root `mcp.json` does not collide with Claude Code's project `./.mcp.json`;
    the spec's filename is undotted. Commands are out of scope in v1 (reserved
    for a later version), so the Gemini/Codex command fan-out still stands.
    """
    write(os.path.join(ROOT, "plugin.json"), json.dumps({
        "$schema": f"https://agent-plugins.org/schemas/{SPEC_VERSION}/plugin.schema.json",
        "name": "akka",
        "version": VERSION,
        "description": PLUGIN_JSON.get("description", "Akka SDK development tools"),
        "author": PLUGIN_JSON.get("author", {"name": "Akka"}),
        "homepage": "https://akka.io",
        "repository": "https://github.com/akka/ai-marketplace",
        "license": "Apache-2.0",
        "keywords": ["akka", "sdk", "spec-driven-development", "agentic"],
    }, indent=2) + "\n")
    write(os.path.join(ROOT, "mcp.json"), json.dumps({
        "$schema": f"https://agent-plugins.org/schemas/{SPEC_VERSION}/mcp.schema.json",
        "mcpServers": {"akka": dict(MCP, type="stdio")},
    }, indent=2) + "\n")


def main():
    cmds = commands()
    g = gen_gemini(cmds)
    c = gen_codex(cmds)
    gen_agent_plugins()
    gen_antigravity()
    print(f"source commands: {len(cmds)}")
    print(f"gemini:      gemini-extension.json + {g} commands/*.toml")
    print(f"codex:       .codex-plugin/plugin.json + {c} skills/ + .agents/plugins/marketplace.json")
    print(f"antigravity: mcp_config.json (plugin.json + skills/ shared)")
    print(f"agent-plugins {SPEC_VERSION}: plugin.json + mcp.json (skills/ shared with codex)")


if __name__ == "__main__":
    main()
