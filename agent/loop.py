"""The plain agent loop: call model -> run requested tools -> append results -> repeat."""
import json

from models.client import DEFAULT_MODEL, make_client
from tools.calculator import calculate
from tools.sandbox import fetch_page, read_file, send_email
from tools.schemas import CALCULATOR, FETCH_PAGE, READ_FILE, SEND_EMAIL

MAX_STEPS = 10
TOOL_FUNCTIONS = {
    "calculator": lambda args: calculate(args["expression"]),
    "read_file": lambda args: read_file(args["path"]),
    "fetch_page": lambda args: fetch_page(args["url"]),
    "send_email": lambda args: send_email(args["to"], args["subject"], args["body"]),
}
TOOL_SCHEMAS = [CALCULATOR, READ_FILE, FETCH_PAGE, SEND_EMAIL]
SYSTEM_PROMPT = "You are a helpful assistant. Use the tools when they help. Give a short final answer."


def run_tool(name: str, raw_arguments: str) -> str:
    """Execute one requested tool call. Problems come back as text so the model can retry."""
    if name not in TOOL_FUNCTIONS:
        return f"error: unknown tool '{name}'"
    try:
        args = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return "error: arguments were not valid JSON"
    try:
        return TOOL_FUNCTIONS[name](args)
    except (KeyError, TypeError):
        return "error: missing or wrong arguments"


def run(task: str, model: str = DEFAULT_MODEL, client=None, max_steps: int = MAX_STEPS) -> dict:
    client = client or make_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": task}]
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(model=model, messages=messages, tools=TOOL_SCHEMAS)
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        print(f"step {step}: finish_reason={resp.choices[0].finish_reason}, content={repr(msg.content)}")
        if not msg.tool_calls:  # no tool requested -> this is the final answer
            return {"final_answer": msg.content, "stop_reason": "final_answer", "steps": step, "messages": messages}
        for call in msg.tool_calls:
            print(f"step {step}: tool call: {call.function.name}({call.function.arguments})")
            result = run_tool(call.function.name, call.function.arguments)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return {"final_answer": None, "stop_reason": "step_limit", "steps": max_steps, "messages": messages}
