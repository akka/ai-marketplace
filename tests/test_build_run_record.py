"""Tests for plugins/akka/hooks/build_run_record.py. Run: python -m unittest discover -s tests"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(__file__), "..", "plugins", "akka", "hooks", "build_run_record.py")
spec = importlib.util.spec_from_file_location("build_run_record", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

TASKS = "specs/001-x/tasks.md"


def line(message_id, minute, model="opus", inp=1, out=1, edit=None, kind="text"):
    block = {"type": "text", "text": "x"}
    if edit:
        block = {"type": "tool_use", "name": "Edit", "input": {
            "file_path": "/proj/" + TASKS, "old_string": "- [ ] %s a" % edit, "new_string": "- [x] %s a" % edit}}
    elif kind == "bash":
        block = {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}
    return json.dumps({"type": "assistant", "timestamp": "2026-11-14T09:%02d:00Z" % minute, "message": {
        "id": message_id, "model": model, "content": [block],
        "usage": {"input_tokens": inp, "output_tokens": out}}})


class Project(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.root, True)
        os.makedirs(os.path.join(self.root, "specs", "001-x"))
        with open(os.path.join(self.root, TASKS), "w") as handle:
            handle.write("- [x] T001 a\n- [x] T002 a\n")
        self.transcript = os.path.join(self.root, "session.jsonl")
        self.marker = os.path.join(self.root, hook.MARKER)
        self.state = os.path.join(self.root, hook.STATE)
        self.write_marker()

    def write_marker(self, **extra):
        marker = {"spec": "001-x", "command": "implement", "startedAt": "2026-11-14T09:10:00Z",
                  "tasksFile": TASKS, "tasksDone": []}
        marker.update(extra)
        hook.write_json(self.marker, marker)

    def append(self, *lines, path=None):
        with open(path or self.transcript, "a") as handle:
            handle.write("\n".join(lines) + "\n")

    def fire(self, event="Stop"):
        hook.run({"hook_event_name": event, "session_id": "s", "cwd": self.root,
                  "transcript_path": self.transcript})

    def record(self):
        folder = os.path.join(self.root, ".akka", "runs", "build", "001-x")
        names = os.listdir(folder)
        self.assertEqual(len(names), 1)
        with open(os.path.join(folder, names[0])) as handle:
            return json.load(handle)

    def usage(self, entry):
        return {row["model"]: (row["requests"], row["inputTokens"]) for row in entry["models"]}


class RunRecordTest(Project):
    def test_tick_in_a_multi_block_message_is_kept_and_usage_comes_from_the_last_line(self):
        self.append(line("a", 11, inp=5),
                    line("b", 12, inp=2, edit="T001"), line("b", 12, inp=7, kind="bash"),
                    line("c", 13, inp=3))
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(record["models"][0]["inputTokens"], 5 + 7 + 3)
        self.assertEqual([item["task"] for item in record["taskUsage"]], ["T001", None])
        self.assertEqual(self.usage(record["taskUsage"][0]), {"opus": (1, 7)})

    def test_usage_before_the_first_tick_goes_to_no_task(self):
        self.append(line("a", 11, inp=10), line("b", 12, inp=20, edit="T001"),
                    line("c", 13, inp=30, edit="T002"), line("d", 14, inp=40))
        self.fire("SessionEnd")
        by_task = {item["task"]: self.usage(item) for item in self.record()["taskUsage"]}
        self.assertEqual(by_task, {"T001": {"opus": (1, 20)}, "T002": {"opus": (1, 30)},
                                   None: {"opus": (2, 50)}})

    def test_lines_before_started_at_are_ignored(self):
        self.append(line("old", 1, inp=99), line("old2", 5, inp=99), line("a", 11, inp=4))
        self.fire("SessionEnd")
        self.assertEqual(self.record()["models"][0]["inputTokens"], 4)

    def test_incremental_reads_across_stops_match_one_read(self):
        self.append(line("a", 11, inp=1), line("b", 12, inp=2, edit="T001"), line("c", 13, inp=3))
        self.fire()
        first = os.path.getsize(self.transcript)
        self.assertEqual(hook.read_json(self.state)["files"][self.transcript], first)
        self.append(line("c", 13, inp=9), line("d", 14, inp=4, edit="T002"), line("e", 15, inp=5))
        self.fire()
        self.assertEqual(hook.read_json(self.state)["files"][self.transcript], os.path.getsize(self.transcript))
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(record["models"][0]["inputTokens"], 1 + 2 + 9 + 4 + 5)
        by_task = {item["task"]: self.usage(item) for item in record["taskUsage"]}
        self.assertEqual(by_task, {"T001": {"opus": (1, 2)}, "T002": {"opus": (2, 13)}, None: {"opus": (2, 6)}})
        self.assertFalse(os.path.exists(self.state))

    def test_a_partial_last_line_is_read_on_the_next_stop(self):
        whole = line("a", 11, inp=6)
        with open(self.transcript, "w") as handle:
            handle.write(whole[:20])
        self.fire()
        with open(self.transcript, "a") as handle:
            handle.write(whole[20:] + "\n")
        self.fire("SessionEnd")
        self.assertEqual(self.record()["models"][0]["inputTokens"], 6)

    def test_closing_marker_finalizes_on_stop_and_removes_the_marker(self):
        self.append(line("a", 11, inp=3))
        self.fire()
        self.assertTrue(os.path.exists(self.marker))
        self.write_marker(closing=True)
        self.fire()
        self.assertEqual(self.record()["models"][0]["inputTokens"], 3)
        self.assertFalse(os.path.exists(self.marker))
        self.assertFalse(os.path.exists(self.state))
        self.append(line("z", 20, inp=50))
        self.fire("SessionEnd")
        self.assertEqual(self.record()["models"][0]["inputTokens"], 3)

    def test_subagent_transcripts_are_included(self):
        sub = os.path.join(self.root, "session", "subagents")
        os.makedirs(sub)
        self.append(line("a", 11, inp=1), line("b", 13, inp=2, edit="T001"))
        self.append(line("s1", 12, model="sonnet", inp=10), path=os.path.join(sub, "agent-1.jsonl"))
        self.fire()
        self.append(line("s2", 14, model="sonnet", inp=20), path=os.path.join(sub, "agent-1.jsonl"))
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(self.usage(record), {"opus": (2, 3), "sonnet": (2, 30)})

    def test_session_end_without_usage_removes_the_marker(self):
        self.append(line("old", 1, inp=9))
        self.fire("SessionEnd")
        self.assertFalse(os.path.exists(self.marker))
        self.assertFalse(os.path.exists(os.path.join(self.root, ".akka", "runs", "build", "001-x")))

    def test_a_state_left_by_an_earlier_run_is_written_out_when_a_new_run_starts(self):
        self.append(line("a", 11, inp=3))
        self.fire()
        self.write_marker(startedAt="2026-11-14T10:00:00Z")
        self.fire()
        self.assertEqual(self.record()["models"][0]["inputTokens"], 3)

    def test_failures_never_raise(self):
        with open(self.marker, "w") as handle:
            handle.write("{broken")
        hook.run({"cwd": self.root})


if __name__ == "__main__":
    unittest.main()
