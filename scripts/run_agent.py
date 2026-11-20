import sys

from agent.loop import run

task = " ".join(sys.argv[1:]) or "What is 17 * 23, then add 100?"
result = run(task)
for m in result["messages"][2:]:
    print(f"[{m['role']}]", m.get("content") or m.get("tool_calls"))
print(f"\nstop_reason={result['stop_reason']} steps={result['steps']}")
print("FINAL:", result["final_answer"])
print("trace:", result["trace_path"])
