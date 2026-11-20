"""The plain agent loop: call model -> run requested tools -> append results -> repeat."""
import json
import time

from agent.trace import TRACE_DIR, Tracer
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


def run(task: str, model: str = DEFAULT_MODEL, client=None, max_steps: int = MAX_STEPS,
        task_id: str = "adhoc", trace_dir=TRACE_DIR) -> dict:
    client = client or make_client()
    tracer = Tracer(task_id, model, trace_dir)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": task}]
    tracer.log("start", task=task, system_prompt=SYSTEM_PROMPT, tools=list(TOOL_FUNCTIONS), max_steps=max_steps)

    def finish(final_answer, stop_reason, steps):
        tracer.log("final", final_answer=final_answer, stop_reason=stop_reason, steps=steps)
        return {"final_answer": final_answer, "stop_reason": stop_reason, "steps": steps,
                "messages": messages, "trace_path": str(tracer.path)}

    for step in range(1, max_steps + 1):
        t0 = time.perf_counter()
        resp = client.chat.completions.create(model=model, messages=messages, tools=TOOL_SCHEMAS)
        duration = time.perf_counter() - t0
        choice = resp.choices[0]
        msg = choice.message
        messages.append(msg.model_dump(exclude_none=True))
        usage = getattr(resp, "usage", None)
        tracer.log(
            "model", step=step, duration_s=round(duration, 3), finish_reason=choice.finish_reason,
            content=msg.content,
            tool_calls=[{"id": c.id, "name": c.function.name, "arguments": c.function.arguments}
                        for c in (msg.tool_calls or [])],
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )
        if not msg.tool_calls:  # no tool requested -> this is the final answer
            return finish(msg.content, "final_answer", step)
        for call in msg.tool_calls:
            t0 = time.perf_counter()
            result = run_tool(call.function.name, call.function.arguments)
            tracer.log(
                "tool", step=step, tool_call_id=call.id, tool_name=call.function.name,
                tool_args=call.function.arguments, tool_result=result,
                duration_s=round(time.perf_counter() - t0, 3),
            )
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return finish(None, "step_limit", max_steps)
