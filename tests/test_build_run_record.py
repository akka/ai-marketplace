"""Tests for plugins/akka/hooks/build_run_record.py. Run: python -m unittest discover -s tests"""
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

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


MARKER_WRITE = json.dumps({"type": "user", "timestamp": "2026-11-14T09:10:00Z",
                           "message": {"content": "wrote .akka/runs/build/.active.json"}})


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
        self.append(MARKER_WRITE)

    def write_marker(self, **extra):
        marker = {"spec": "001-x", "command": "implement", "startedAt": "2026-11-14T09:10:00Z",
                  "tasksFile": TASKS, "tasksDone": []}
        marker.update(extra)
        hook.write_json(self.marker, marker)

    def append(self, *lines, path=None):
        path = path or self.transcript
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as handle:
            handle.write("\n".join(lines) + "\n")

    def fire(self, event="Stop", session="s"):
        hook.run({"hook_event_name": event, "session_id": session, "cwd": self.root,
                  "transcript_path": self.transcript})

    def records_dir(self):
        return os.path.join(self.root, ".akka", "runs", "build", "001-x")

    def record(self):
        names = os.listdir(self.records_dir())
        self.assertEqual(len(names), 1)
        with open(os.path.join(self.records_dir(), names[0])) as handle:
            return json.load(handle)

    def usage(self, entry):
        return {row["model"]: (row["requests"], row["inputTokens"]) for row in entry["models"]}

    def by_task(self, record):
        return {item["task"]: self.usage(item) for item in record["taskUsage"]}


class RunRecordTest(Project):
    def test_tick_in_a_multi_block_message_is_kept_and_usage_comes_from_the_last_line(self):
        self.append(line("a", 11, inp=5),
                    line("b", 12, inp=2, edit="T001"), line("b", 12, inp=7, kind="bash"),
                    line("c", 13, inp=3))
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(record["models"][0]["inputTokens"], 5 + 7 + 3)
        self.assertEqual(self.by_task(record), {"T001": {"opus": (2, 12)}, None: {"opus": (1, 3)}})

    def test_a_tick_closes_its_task_window_including_usage_before_the_first_tick(self):
        self.append(line("a", 11, inp=10), line("b", 12, inp=20, edit="T001"),
                    line("c", 13, inp=30, edit="T002"), line("d", 14, inp=40))
        self.fire("SessionEnd")
        self.assertEqual(self.by_task(self.record()), {
            "T001": {"opus": (2, 30)}, "T002": {"opus": (1, 30)}, None: {"opus": (1, 40)}})

    def test_one_turn_with_two_subagents_and_two_ticks(self):
        sub = os.path.join(self.root, "session", "subagents")
        self.append(line("m0", 11), line("m1", 14, edit="T001"), line("m2", 15), line("m3", 18, edit="T002"))
        self.append(line("a1", 12, model="sonnet", inp=100), line("a2", 13, model="sonnet", inp=100),
                    path=os.path.join(sub, "agent-1.jsonl"))
        self.append(line("b1", 16, model="sonnet", inp=1000), line("b2", 17, model="sonnet", inp=1000),
                    path=os.path.join(sub, "agent-2.jsonl"))
        self.fire("SessionEnd")
        self.assertEqual(self.by_task(self.record()), {
            "T001": {"opus": (2, 2), "sonnet": (2, 200)},
            "T002": {"opus": (2, 2), "sonnet": (2, 2000)}})

    def test_messages_are_ordered_across_files_and_across_stops(self):
        sub = os.path.join(self.root, "session", "subagents", "agent-1.jsonl")
        self.append(line("x", 11), line("y", 20, edit="T001"))
        self.append(line("s1", 15, model="sonnet"), path=sub)
        self.fire()
        self.append(line("z", 21), path=self.transcript)
        self.append(line("s2", 16, model="sonnet"), path=sub)
        self.fire()
        self.fire("SessionEnd")
        self.assertEqual(self.by_task(self.record()), {
            "T001": {"opus": (2, 2), "sonnet": (2, 2)}, None: {"opus": (1, 1)}})

    def test_lines_before_started_at_are_ignored(self):
        with open(self.transcript, "w") as handle:
            handle.write(line("old", 1, inp=99) + "\n" + line("old2", 5, inp=99) + "\n" + MARKER_WRITE + "\n")
        self.append(line("a", 11, inp=4))
        self.fire("SessionEnd")
        self.assertEqual(self.record()["models"][0]["inputTokens"], 4)

    def test_incremental_reads_across_stops_match_one_read(self):
        self.append(line("a", 11, inp=1), line("b", 12, inp=2, edit="T001"), line("c", 13, inp=3))
        self.fire()
        self.assertEqual(hook.read_json(self.state)["files"][self.transcript], os.path.getsize(self.transcript))
        self.append(line("c", 13, inp=9), line("d", 14, inp=4, edit="T002"), line("e", 15, inp=5))
        self.fire()
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(record["models"][0]["inputTokens"], 1 + 2 + 9 + 4 + 5)
        self.assertEqual(self.by_task(record), {
            "T001": {"opus": (2, 3)}, "T002": {"opus": (2, 13)}, None: {"opus": (1, 5)}})
        self.assertFalse(os.path.exists(self.state))

    def test_a_partial_last_line_is_read_on_the_next_stop(self):
        whole = line("a", 11, inp=6)
        with open(self.transcript, "a") as handle:
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
        self.append(line("a", 11, inp=1), line("b", 13, inp=2, edit="T001"))
        self.append(line("s1", 12, model="sonnet", inp=10), path=os.path.join(sub, "agent-1.jsonl"))
        self.fire()
        self.append(line("s2", 14, model="sonnet", inp=20), path=os.path.join(sub, "agent-1.jsonl"))
        self.fire("SessionEnd")
        record = self.record()
        self.assertEqual(self.usage(record), {"opus": (2, 3), "sonnet": (2, 30)})
        self.assertEqual(self.by_task(record), {"T001": {"opus": (2, 3), "sonnet": (1, 10)},
                                                None: {"sonnet": (1, 20)}})

    def test_session_end_without_usage_removes_the_marker(self):
        self.fire("SessionEnd")
        self.assertFalse(os.path.exists(self.marker))
        self.assertFalse(os.path.exists(self.records_dir()))

    def test_a_session_that_did_not_write_the_marker_leaves_the_run_alone(self):
        other = os.path.join(self.root, "other.jsonl")
        with open(other, "w") as handle:
            handle.write(line("o", 12, inp=77) + "\n")
        hook.run({"hook_event_name": "SessionEnd", "session_id": "other", "cwd": self.root,
                  "transcript_path": other})
        self.assertTrue(os.path.exists(self.marker))
        self.assertFalse(os.path.exists(self.records_dir()))

    def test_a_state_left_by_an_earlier_run_is_written_out_when_a_new_run_starts(self):
        self.append(line("a", 11, inp=3))
        self.fire()
        self.write_marker(startedAt="2026-11-14T10:00:00Z")
        self.fire()
        self.assertEqual(self.record()["models"][0]["inputTokens"], 3)


class NeverBreaksTest(Project):
    def test_an_unreadable_marker_is_ignored(self):
        with open(self.marker, "w") as handle:
            handle.write("{broken")
        hook.run({"cwd": self.root})

    def test_main_exits_zero_on_unreadable_input(self):
        with mock.patch.object(sys, "stdin", io.StringIO("garbage")):
            with self.assertRaises(SystemExit) as caught:
                hook.main()
        self.assertEqual(caught.exception.code, 0)

    def test_main_exits_zero_when_the_run_raises(self):
        with mock.patch.object(sys, "stdin", io.StringIO("{}")), \
                mock.patch.object(hook, "run", side_effect=RuntimeError("boom")):
            with self.assertRaises(SystemExit) as caught:
                hook.main()
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
