"""Run every task in a JSONL file and save one trace per task under traces/<batch_id>/.
The summary is built by reading the trace files back, the same way the analyzer will."""
import json
import sys
import time
from pathlib import Path

from agent.loop import run
from agent.trace import TRACE_DIR
from models.client import DEFAULT_MODEL

TEMPERATURE, SEED = 0, 42


def summarize(trace_path: str) -> dict:
    events = [json.loads(line) for line in Path(trace_path).read_text().splitlines()]
    final = events[-1] if events[-1]["type"] == "final" else {}
    return {
        "stop": final.get("stop_reason", "crashed"),
        "steps": final.get("steps"),
        "tools": [e["tool_name"] for e in events if e["type"] == "tool"],
        "errors": sum(1 for e in events if e["type"] == "tool" and e["tool_result"].startswith("error")),
        "answer": (final.get("final_answer") or "")[:60].replace("\n", " "),
    }


def main(tasks_file: str = "tasks/benign.jsonl", model: str = DEFAULT_MODEL) -> None:
    tasks = [json.loads(line) for line in Path(tasks_file).read_text().splitlines() if line.strip()]
    batch_dir = TRACE_DIR / ("batch-" + time.strftime("%Y%m%d-%H%M%S"))
    print(f"{len(tasks)} tasks, model={model}, temperature={TEMPERATURE}, seed={SEED}\ntraces -> {batch_dir}\n")
    for t in tasks:
        try:
            result = run(t["prompt"], model=model, task_id=t["id"], trace_dir=batch_dir,
                         temperature=TEMPERATURE, seed=SEED)
            s = summarize(result["trace_path"])
            print(f"{t['id']:8} {s['stop']:13} steps={s['steps']} tools={s['tools']} errors={s['errors']} | {s['answer']}")
        except Exception as e:  # keep going so one bad task doesn't lose the batch
            print(f"{t['id']:8} CRASHED {type(e).__name__}: {e}")


if __name__ == "__main__":
    main(*sys.argv[1:])
