"""Records the model usage of a /akka:plan, /akka:tasks or /akka:implement run.

The command writes `.akka/runs/build/.active.json` before it starts:

    {"spec": "001-orders", "command": "implement", "startedAt": "2026-11-14T09:30:00Z",
     "tasksFile": "specs/001-orders/tasks.md", "tasksDone": ["T001", "T002"]}

`tasksDone` lists the task ids that were already ticked at that moment. After the docs refresh the
command adds `"closing": true`.

The hook runs on Stop and SessionEnd. On each Stop it reads only the transcript lines written
since the previous Stop and keeps running totals in `.akka/runs/build/.state.json`. When the
marker says `closing`, or the session ends, it writes `.akka/runs/build/<spec>/<startedAt>.json`
and removes the marker and the state. A state whose marker has been replaced by another run is
written out as that run's record. Only the session whose transcript mentions the marker takes
the run, so a second session in the same project leaves it alone.

Usage is read from the last transcript line of each message id, because a streamed message
repeats its id once per content block with growing usage. Tool calls are read from every line of
the id. The first read of a transcript starts at the first line written at or after `startedAt`,
found by bisection, so the cost of a run does not depend on the size of the session before it.

`taskUsage` splits the usage by task. A tick is an Edit, MultiEdit or Write tool call on tasks.md
that turns `- [ ]` into `- [x]` for a task id. A tick closes its task's window: all usage since
the previous tick, up to and including the message that makes the tick, belongs to the first task
ticked there, and so the usage before the first tick belongs to the first task. Usage after the
last tick belongs to `task: null`. The main transcript and the sub-agent transcripts are folded
together in timestamp order, so a sub-agent's work lands in the window it ran in. A message that
may still be growing is held back with the messages after it until the next read, which keeps
that order across Stops.

The hook prints nothing and always exits 0, so it can never block or break a session.
"""
import copy
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

MARKER = os.path.join(".akka", "runs", "build", ".active.json")
STATE = os.path.join(".akka", "runs", "build", ".state.json")
TASK_LINE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s+(T\d+)\b")
SCAN_LINES = 50


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


def format_time(value):
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_root(start):
    for candidate in (os.environ.get("CLAUDE_PROJECT_DIR"), start):
        path = os.path.abspath(candidate) if candidate else None
        while path:
            if os.path.isfile(os.path.join(path, MARKER)) or os.path.isfile(os.path.join(path, STATE)):
                return path
            parent = os.path.dirname(path)
            if parent == path:
                break
            path = parent
    return None


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
    os.replace(temp, path)


def remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


def line_stamp(line):
    try:
        return parse_time(json.loads(line).get("timestamp"))
    except (ValueError, AttributeError):
        return None


def seek_since(path, since):
    """The byte offset of the first line whose timestamp is at or after `since`.

    Transcript lines are in time order, so the offset is found by bisection. Lines without a
    timestamp are skipped; a probe that reaches the end of the file counts as at or after `since`.
    """
    lo, hi = 0, os.path.getsize(path)
    with open(path, "rb") as handle:
        while lo < hi:
            mid = (lo + hi) // 2
            if mid > 0:
                handle.seek(mid - 1)
                handle.readline()
            else:
                handle.seek(0)
            stamp = None
            for _ in range(SCAN_LINES):
                line = handle.readline()
                if not line:
                    break
                stamp = line_stamp(line)
                if stamp is not None:
                    break
            if stamp is None or stamp >= since:
                hi = mid
            else:
                lo = handle.tell()
    return lo


def tool_edits(message):
    """Yields (tool_use_id, file_path, old_text, new_text) for each edit tool call in an assistant message."""
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
        use = block.get("id")
        if block.get("name") == "Edit":
            yield use, path, args.get("old_string"), args.get("new_string")
        elif block.get("name") == "MultiEdit":
            for edit in args.get("edits") or []:
                if isinstance(edit, dict):
                    yield use, path, edit.get("old_string"), edit.get("new_string")
        elif block.get("name") == "Write":
            yield use, path, None, args.get("content")


def task_states(text):
    states = {}
    for line in (text or "").splitlines():
        found = TASK_LINE.match(line)
        if found:
            states[found.group(2)] = found.group(1) in "xX"
    return states


def ticks_in(message, tasks_file, already):
    """(task id, tool_use id) for each task a message ticks in tasks.md.

    The tick counts only once the tool call's result shows it succeeded. A Write has no old text,
    so it ticks what is not in `already`.
    """
    if not tasks_file:
        return []
    suffix = tasks_file.replace("\\", "/")
    ticked = []
    for use, path, old, new in tool_edits(message):
        if not isinstance(path, str) or not path.replace("\\", "/").endswith(suffix):
            continue
        before = task_states(old)
        for task, done in task_states(new).items():
            if done and not before.get(task, False) and task not in already:
                ticked.append((task, use))
    return ticked


def tool_results(entry):
    """Yields (tool_use_id, is_error) for each tool result in a user transcript line."""
    message = entry.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                yield block.get("tool_use_id"), bool(block.get("is_error"))


def add_usage(models, model, usage):
    row = models.setdefault(model, {
        "model": model, "requests": 0, "inputTokens": 0, "outputTokens": 0,
        "cacheReadTokens": 0, "cacheWriteTokens": 0})
    row["requests"] += 1
    row["inputTokens"] += int(usage.get("input_tokens") or 0)
    row["outputTokens"] += int(usage.get("output_tokens") or 0)
    row["cacheReadTokens"] += int(usage.get("cache_read_input_tokens") or 0)
    row["cacheWriteTokens"] += int(usage.get("cache_creation_input_tokens") or 0)


def stamp_key(value):
    """A time string that sorts in time order, to the microsecond."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def new_state(marker):
    return {
        "spec": marker.get("spec"), "command": marker.get("command"),
        "startedAt": marker.get("startedAt"), "tasksFile": marker.get("tasksFile"),
        "tasksDone": list(marker.get("tasksDone") or []), "sessionId": None,
        "files": {}, "open": {}, "pending": [], "totals": {}, "tasks": [], "window": {},
        "ticked": [], "last": None,
    }


def fold(state, message):
    """Adds a message to the totals and to the window it belongs to.

    Messages must arrive in time order. A tick closes the window of the task it ticks: all usage
    since the previous tick, up to and including the ticking message, goes to that task.
    """
    model, usage = message["model"], message["usage"]
    ticks = [task for task in dict.fromkeys(message["ticks"]) if task not in state["ticked"]]
    add_usage(state["totals"], model, usage)
    add_usage(state["window"], model, usage)
    if message["stamp"] > (state["last"] or ""):
        state["last"] = message["stamp"]
    if ticks:
        state["tasks"].append({"task": ticks[0], "models": state["window"]})
        state["window"] = {}
        state["ticked"].extend(ticks)


def close_open(state, path):
    message = state["open"].pop(path)
    if message["model"] and message["usage"]:
        results = message.pop("results")
        message["ticks"] = [task for task, use in message["ticks"] if results.get(use) is False]
        state["pending"].append(message)


def fold_pending(state, through):
    """Folds the pending messages stamped at or before `through` (all of them when None), in time order."""
    state["pending"].sort(key=lambda message: (message["stamp"], message["id"]))
    rest = []
    for message in state["pending"]:
        if through is None or message["stamp"] <= through:
            fold(state, message)
        else:
            rest.append(message)
    state["pending"] = rest


def read_new(path, state, since, complete=False):
    """Collects the complete lines written to `path` since the last read into `state`.

    A message whose last line may still be growing stays in `state["open"]`; finished messages
    wait in `state["pending"]` until `settle` folds them in time order across files. Returns
    whether any line mentions the run marker. With `complete`, the file's last message is
    finished too (a sub-agent transcript), and only an unterminated final line is held back.
    """
    try:
        size = os.path.getsize(path)
    except OSError:
        return False
    offset = state["files"].get(path)
    if offset is None:
        offset = seek_since(path, since)
    if offset >= size:
        state["files"][path] = offset
        return False
    with open(path, "rb") as handle:
        handle.seek(offset)
        data = handle.read()
    end = data.rfind(b"\n") + 1
    state["files"][path] = offset + end
    mentioned = False
    for number, line in enumerate(data[:end].split(b"\n")):
        if b".active.json" in line:
            mentioned = True
        if b'"tool_result"' in line and path in state["open"]:
            try:
                for use, failed in tool_results(json.loads(line)):
                    state["open"][path]["results"][use] = failed
            except ValueError:
                pass
            continue
        if b'"assistant"' not in line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(message, dict):
            continue
        stamp = parse_time(entry.get("timestamp"))
        if stamp is None or stamp < since or message.get("model") == "<synthetic>":
            continue
        key = message.get("id") or "%s:%d:%d" % (path, offset, number)
        current = state["open"].get(path)
        if current is not None and current["id"] != key:
            close_open(state, path)
            current = None
        if current is None:
            current = state["open"][path] = {
                "id": key, "model": None, "usage": None, "stamp": "", "ticks": [], "results": {}}
        current["stamp"] = stamp_key(stamp)
        if message.get("model"):
            current["model"] = message["model"]
        if isinstance(message.get("usage"), dict):
            current["usage"] = message["usage"]
        already = set(state["ticked"]) | set(state["tasksDone"])
        current["ticks"].extend(ticks_in(message, state["tasksFile"], already))
    if complete and path in state["open"]:
        close_open(state, path)
    return mentioned


def settle(state):
    """Folds every pending message that no open message precedes, so a later read cannot arrive out of order."""
    opened = [message["stamp"] for message in state["open"].values()]
    fold_pending(state, min(opened) if opened else None)


def snapshot(state):
    """The state with every message folded in, leaving `state` as it was."""
    result = copy.deepcopy(state)
    for path in list(result["open"]):
        close_open(result, path)
    fold_pending(result, None)
    return result


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


def write_record(root, state):
    """Writes the run's record from `state`; returns False when the run used no model."""
    final = snapshot(state)
    if not final["totals"] or not final["spec"] or not final["startedAt"]:
        return False
    tasks_file = final["tasksFile"]
    done_now = ticked_tasks(os.path.join(root, tasks_file)) if tasks_file else set()
    task_usage = [{"task": item["task"], "models": [item["models"][n] for n in sorted(item["models"])]}
                  for item in final["tasks"]]
    if final["window"]:
        task_usage.append({"task": None, "models": [final["window"][n] for n in sorted(final["window"])]})
    record = {
        "spec": final["spec"],
        "command": final["command"],
        "startedAt": final["startedAt"],
        "endedAt": format_time(parse_time(final["last"])),
        "commit": head_commit(root),
        "tasks": sorted(done_now - set(final["tasksDone"])),
        "models": [final["totals"][n] for n in sorted(final["totals"])],
        "taskUsage": task_usage,
    }
    out = os.path.join(root, ".akka", "runs", "build", file_name(final["spec"]),
                       file_name(final["startedAt"]) + ".json")
    write_json(out, record)
    return True


def run(event):
    root = find_root(event.get("cwd") or os.getcwd())
    if not root:
        return
    marker_path = os.path.join(root, MARKER)
    state_path = os.path.join(root, STATE)
    marker = read_json(marker_path)
    state = read_json(state_path)

    if state and (not marker or marker.get("startedAt") != state.get("startedAt")):
        write_record(root, state)
        remove(state_path)
        state = None
    if not marker:
        return

    session = event.get("session_id")
    ending = event.get("hook_event_name") == "SessionEnd"
    if state is None:
        state = new_state(marker)
    if state["sessionId"] and session and state["sessionId"] != session:
        return

    since = parse_time(marker.get("startedAt"))
    if since is None:
        since = datetime.fromtimestamp(os.path.getmtime(marker_path), timezone.utc)
        state["startedAt"] = marker["startedAt"] = format_time(since)
    transcript = event.get("transcript_path")
    owns = bool(state["sessionId"])
    if transcript and os.path.isfile(transcript):
        session_dir = os.path.splitext(transcript)[0]
        for path in sorted(glob.glob(os.path.join(session_dir, "subagents", "*.jsonl"))):
            read_new(path, state, since, complete=True)
        if read_new(transcript, state, since):
            owns = True
        settle(state)
    # A transcript that names the marker file after `startedAt` is taken to be the session that
    # wrote it. Another session that runs one of the commands also names it, but that session
    # overwrites the marker itself, so a session that only works nearby does not adopt the run.
    if not owns:
        return
    if not state["sessionId"] and session:
        state["sessionId"] = session

    if ending or marker.get("closing") is True:
        write_record(root, state)
        remove(marker_path)
        remove(state_path)
    else:
        write_json(state_path, state)


def main():
    try:
        run(json.load(sys.stdin))
    except BaseException:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
