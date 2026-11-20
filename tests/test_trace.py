import json
import tempfile
import unittest
from pathlib import Path

from agent.loop import run
from tests.test_agent import Msg, fake_client, tool_call


class TraceTests(unittest.TestCase):
    def test_events_in_order_and_complete(self):
        d = Path(tempfile.mkdtemp())
        client = fake_client([Msg(tool_calls=[tool_call("2+2")]), Msg(content="4")])
        r = run("2+2?", client=client, task_id="t1", trace_dir=d)
        events = [json.loads(line) for line in Path(r["trace_path"]).read_text().splitlines()]
        self.assertEqual([e["type"] for e in events], ["start", "model", "tool", "model", "final"])
        self.assertTrue(all(e["task_id"] == "t1" and e["run_id"] == r["trace_path"].split("/")[-1][:-6] for e in events))
        tool = events[2]
        self.assertEqual((tool["tool_name"], tool["tool_result"]), ("calculator", "4"))
        self.assertEqual(events[-1]["final_answer"], "4")

    def test_step_limit_is_recorded(self):
        d = Path(tempfile.mkdtemp())
        client = fake_client([Msg(tool_calls=[tool_call("1+1")]) for _ in range(5)])
        r = run("loop", client=client, max_steps=2, trace_dir=d)
        last = json.loads(Path(r["trace_path"]).read_text().splitlines()[-1])
        self.assertEqual((last["type"], last["stop_reason"]), ("final", "step_limit"))


if __name__ == "__main__":
    unittest.main()
