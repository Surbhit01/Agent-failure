"""Trace writer: one JSON line per event, appended as the run happens (so a crash keeps what came before).
Event types: start, model, tool, final. Analysis code reads these files and nothing else."""
import json
import time
import uuid
from pathlib import Path

TRACE_DIR = Path(__file__).resolve().parent.parent / "traces"


class Tracer:
    def __init__(self, task_id: str, model: str, trace_dir: Path = TRACE_DIR):
        self.run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.base = {"run_id": self.run_id, "task_id": task_id, "model": model}
        trace_dir.mkdir(parents=True, exist_ok=True)
        self.path = trace_dir / f"{self.run_id}.jsonl"

    def log(self, type: str, **fields) -> None:
        record = {"type": type, **self.base, "ts": time.time(), **fields}
        with self.path.open("a") as f:
            f.write(json.dumps(record) + "\n")
