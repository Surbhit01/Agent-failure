import json

from models.client import DEFAULT_MODEL, make_client
from tools.schemas import CALCULATOR


MESSAGE_OPTIONS = ["What is 17*23","Where is India located?"]

client = make_client()

for m in MESSAGE_OPTIONS:
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": m}],
        tools=[CALCULATOR],
    )
    choice = resp.choices[0]
    print("message:", m)
    print("finish_reason:", choice.finish_reason)
    print("content:", repr(choice.message.content))
    print("raw message:", json.dumps(choice.message.model_dump(exclude_none=True), indent=2))
