from models.client import DEFAULT_MODEL, make_client

client = make_client()
resp = client.chat.completions.create(
    model=DEFAULT_MODEL,
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(resp.choices[0].message.content)
print("tokens:", resp.usage.total_tokens)
