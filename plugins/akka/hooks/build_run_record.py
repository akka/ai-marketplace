#!/usr/bin/env python3
"""Records the model usage of a /akka:plan, /akka:tasks or /akka:implement run.

The command writes `.akka/runs/build/.active.json` before it starts:

    {"spec": "001-orders", "command": "implement", "startedAt": "2026-11-14T09:30:00Z",
     "tasksFile": "specs/001-orders/tasks.md", "tasksDone": ["T001", "T002"]}

`tasksDone` lists the task ids that were already ticked at that moment. This hook runs on Stop
and SessionEnd. It sums the usage of the assistant messages in the session transcript that were
written at or after `startedAt`, by model, and writes `.akka/runs/build/<spec>/<startedAt>.json`.
`taskUsage` splits the same usage by task: the usage between one tick of a task in tasks.md and the
next belongs to the task ticked at the end of that window, and usage outside the first and last
tick belongs to `task: null`. A tick is an Edit, MultiEdit or Write tool call on tasks.md that turns
`- [ ]` into `- [x]` for a task id.
Stop rewrites the same file each time with the cumulative figures, so the record is always
current; SessionEnd writes it a last time and removes the marker.

The first hook event that finds usage after `startedAt` binds the marker to its session, so a
second session in the same project does not add its usage to the record.

The hook prints nothing and always exits 0, so it can never block or break a session.
"""
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MARKER = os.path.join(".akka", "runs", "build", ".active.json")
TASK_LINE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(T\d+)\b")


def parse_time(text):
    if not isinstance(text, str):
        return None
    try:
        value = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def find_root(start):
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), start):
        path = os.path.abspath(candidate) if candidate else None
        while path:
            if os.path.isfile(os.path.join(path, MARKER)):
                return path
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
    return None


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
    os.replace(temp, path)


def transcript_files(transcript_path):
    """The session transcript and, when present, the transcripts of its sub-agents."""
    session_dir = os.path.splitext(transcript_path)[0]
    return [transcript_path] + sorted(glob.glob(os.path.join(session_dir, "subagents", "*.jsonl")))


def tool_edits(message):
    """Yields (file_path, old_text, new_text) for each edit tool call in an assistant message."""
    content = message.get("content")
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        args = block.get("input")
        if not isinstance(args, dict):
            continue
        path = args.get("file_path")
        if block.get("name") == "Edit":
            yield path, args.get("old_string"), args.get("new_string")
        elif block.get("name") == "MultiEdit":
            for edit in args.get("edits") or []:
                if isinstance(edit, dict):
                    yield path, edit.get("old_string"), edit.get("new_string")
        elif block.get("name") == "Write":
            yield path, None, args.get("content")


def task_states(text):
    states = {}
    for line in (text or "").splitlines():
        found = TASK_LINE.match(line)
        if found:
            states[found.group(2)] = found.group(1) in "xX"
    return states


def ticks_in(message, tasks_file, already):
    """Task ids a message ticks in tasks.md. A Write has no old text, so it ticks what is not yet in `already`."""
    if not tasks_file:
        return []
    suffix = tasks_file.replace("\\", "/")
    ticked = []
    for path, old, new in tool_edits(message):
        if not isinstance(path, str) or not path.replace("\\", "/").endswith(suffix):
            continue
        before = task_states(old)
        for task, done in task_states(new).items():
            if done and not before.get(task, False) and task not in already:
                ticked.append(task)
    return ticked


def sum_usage(transcript_path, since, tasks_file=None, done_before=()):
    """Returns (models, last_timestamp, task_usage). A streamed message repeats its id; the last copy wins."""
    messages = {}
    for path in transcript_files(transcript_path):
        try:
            handle = open(path, "r", encoding="utf-8")
        except OSError:
            continue
        with handle:
            for index, line in enumerate(handle):
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                message = entry.get("message")
                if entry.get("type") != "assistant" or not isinstance(message, dict):
                    continue
                usage = message.get("usage")
                model = message.get("model")
                stamp = parse_time(entry.get("timestamp"))
                if not isinstance(usage, dict) or not model or model == "<synthetic>":
                    continue
                if stamp is None or stamp < since:
                    continue
                key = message.get("id") or "%s:%d" % (path, index)
                messages[key] = (model, usage, stamp, message)

    ordered = sorted(messages.values(), key=lambda item: item[2])
    ticks = []
    seen = set(done_before)
    for _, _, stamp, message in ordered:
        for task in ticks_in(message, tasks_file, seen):
            seen.add(task)
            ticks.append((stamp, task))

    totals = {}
    by_task = {}
    last = None
    for model, usage, stamp, _ in ordered:
        owner = next((task for tick, task in ticks if stamp <= tick), None)
        for table in (totals, by_task.setdefault(owner, {})):
            row = table.setdefault(model, {
                "model": model, "requests": 0, "inputTokens": 0, "outputTokens": 0,
                "cacheReadTokens": 0, "cacheWriteTokens": 0})
            row["requests"] += 1
            row["inputTokens"] += int(usage.get("input_tokens") or 0)
            row["outputTokens"] += int(usage.get("output_tokens") or 0)
            row["cacheReadTokens"] += int(usage.get("cache_read_input_tokens") or 0)
            row["cacheWriteTokens"] += int(usage.get("cache_creation_input_tokens") or 0)
        if last is None or stamp > last:
            last = stamp
    order = [task for _, task in ticks] + [None]
    task_usage = [{"task": task, "models": [by_task[task][name] for name in sorted(by_task[task])]}
                  for task in order if task in by_task]
    return [totals[name] for name in sorted(totals)], last, task_usage


def ticked_tasks(path):
    ticked = set()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                found = TASK_LINE.match(line)
                if found and found.group(1) in "xX":
                    ticked.add(found.group(2))
    except OSError:
        pass
    return ticked


def head_commit(root):
    try:
        result = subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True,
                                text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def file_name(text):
    return re.sub(r"[^A-Za-z0-9._-]", "-", text)


def run(event):
    transcript = event.get("transcript_path")
    root = find_root(event.get("cwd") or os.getcwd())
    if not transcript or not root or not os.path.isfile(transcript):
        return
    marker_path = os.path.join(root, MARKER)
    marker = read_json(marker_path)

    session = event.get("session_id")
    if marker.get("sessionId") and session and marker["sessionId"] != session:
        return
    since = parse_time(marker.get("startedAt"))
    if since is None:
        since = datetime.fromtimestamp(os.path.getmtime(marker_path), timezone.utc)

    tasks_file = marker.get("tasksFile")
    done_before = set(marker.get("tasksDone") or [])
    models, last, task_usage = sum_usage(transcript, since, tasks_file, done_before)
    spec = marker.get("spec")
    if not models or not spec:
        return
    if session and not marker.get("sessionId"):
        marker["sessionId"] = session
        write_json(marker_path, marker)

    started = marker.get("startedAt") or since.strftime("%Y-%m-%dT%H:%M:%SZ")
    done_now = ticked_tasks(os.path.join(root, tasks_file)) if tasks_file else set()

    record = {
        "spec": spec,
        "command": marker.get("command"),
        "startedAt": started,
        "endedAt": last.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": head_commit(root),
        "tasks": sorted(done_now - done_before),
        "models": models,
        "taskUsage": task_usage,
    }
    out = os.path.join(root, ".akka", "runs", "build", file_name(spec), file_name(started) + ".json")
    write_json(out, record)

    if event.get("hook_event_name") == "SessionEnd":
        os.remove(marker_path)


def main():
    try:
        run(json.load(sys.stdin))
    except BaseException:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
