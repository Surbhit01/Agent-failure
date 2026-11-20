"""Run with: uv run python -m unittest discover -s tests -t ."""
import unittest
from types import SimpleNamespace as NS

from agent.loop import run, run_tool
from tools.calculator import calculate


class CalculatorTests(unittest.TestCase):
    def test_math(self):
        self.assertEqual(calculate("17 * 23"), "391")
        self.assertEqual(calculate("(2 + 3) * -4"), "-20")

    def test_rejects_code(self):  # the point of the AST evaluator
        self.assertTrue(calculate("__import__('os').system('ls')").startswith("error"))
        self.assertTrue(calculate("2 ** 3").startswith("error"))
        self.assertTrue(calculate("1/0").startswith("error"))


class RunToolTests(unittest.TestCase):
    def test_errors_returned_as_text(self):
        self.assertIn("unknown tool", run_tool("rm_rf", "{}"))
        self.assertIn("not valid JSON", run_tool("calculator", "{oops"))
        self.assertIn("missing", run_tool("calculator", "{}"))


def fake_client(messages_to_return):
    """A stand-in model that replays scripted replies, so loop tests need no Ollama."""
    replies = iter(messages_to_return)
    create = lambda **kw: NS(choices=[NS(message=next(replies), finish_reason="stop")])
    return NS(chat=NS(completions=NS(create=create)))


class Msg:
    def __init__(self, content=None, tool_calls=None):
        self.content, self.tool_calls = content, tool_calls

    def model_dump(self, exclude_none=True):
        return {"role": "assistant", "content": self.content or ""}


def tool_call(expr, id="c1"):
    return NS(id=id, function=NS(name="calculator", arguments='{"expression": "%s"}' % expr))


class LoopTests(unittest.TestCase):
    def test_tool_then_answer(self):
        client = fake_client([Msg(tool_calls=[tool_call("2+2")]), Msg(content="4")])
        r = run("2+2?", client=client)
        self.assertEqual((r["stop_reason"], r["steps"], r["final_answer"]), ("final_answer", 2, "4"))
        self.assertEqual(r["messages"][-2], {"role": "tool", "tool_call_id": "c1", "content": "4"})

    def test_step_limit(self):
        client = fake_client([Msg(tool_calls=[tool_call("1+1")]) for _ in range(5)])
        r = run("loop forever", client=client, max_steps=3)
        self.assertEqual((r["stop_reason"], r["steps"]), ("step_limit", 3))


if __name__ == "__main__":
    unittest.main()
