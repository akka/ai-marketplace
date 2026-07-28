#!/usr/bin/env bash
# Set the `akka` plugin's version consistently across every descriptor that
# carries it, derived from a git tag. The deprecated `akka-specify` plugin is
# intentionally left untouched.
#
# Descriptors updated:
#   plugins/akka/.claude-plugin/plugin.json   (source of truth for generate-harnesses.py)
#   plugins/akka/.codex-plugin/plugin.json    (hand-maintained per-plugin Codex manifest)
#   .claude-plugin/marketplace.json           (akka entry only)
# Then bin/generate-harnesses.py is run to regenerate the derived files:
#   gemini-extension.json
#   .codex-plugin/plugin.json
#
# Usage:
#   bin/set-plugin-versions.sh              # use the highest semver tag in the repo
#   bin/set-plugin-versions.sh v2.5.0       # use an explicit tag
#
# macOS/BSD-compatible: uses only POSIX shell features plus python3 (already a
# prerequisite of bin/generate-harnesses.py).

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)

TAG="${1:-}"
if [ -z "$TAG" ]; then
  TAG=$(git -C "$ROOT" tag --sort=-v:refname | head -n1 || true)
  if [ -z "$TAG" ]; then
    echo "error: no git tags in this repo; pass a tag explicitly (e.g. $0 v2.5.0)" >&2
    exit 1
  fi
fi

VERSION="${TAG#v}"
if ! printf '%s' "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$'; then
  echo "error: tag '$TAG' does not look like a semver version (X.Y.Z[-pre])" >&2
  exit 1
fi

echo "Setting akka plugin version to $VERSION (from tag $TAG)"

# Update the version field of a JSON descriptor.
# $1: file path
# $2: plugin name to target within a plugins[] array; empty => update top-level "version"
set_version() {
  python3 - "$1" "$2" "$VERSION" <<'PY'
import json, sys
path, name, version = sys.argv[1], sys.argv[2], sys.argv[3]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
if name:
    hit = False
    for p in data.get("plugins", []):
        if p.get("name") == name:
            p["version"] = version
            hit = True
    if not hit:
        sys.exit(f"error: no plugin named {name!r} in {path}")
else:
    data["version"] = version
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
}

set_version "$ROOT/plugins/akka/.claude-plugin/plugin.json" ""
set_version "$ROOT/plugins/akka/.codex-plugin/plugin.json" ""
set_version "$ROOT/.claude-plugin/marketplace.json"        "akka"

python3 "$ROOT/bin/generate-harnesses.py" >/dev/null

echo "Version now set to $VERSION in:"
grep -HEn '"version"[[:space:]]*:[[:space:]]*"' \
  "$ROOT/plugins/akka/.claude-plugin/plugin.json" \
  "$ROOT/plugins/akka/.codex-plugin/plugin.json" \
  "$ROOT/.claude-plugin/marketplace.json" \
  "$ROOT/.codex-plugin/plugin.json" \
  "$ROOT/gemini-extension.json"
