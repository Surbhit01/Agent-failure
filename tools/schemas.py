"""Tool descriptions the model sees. The model only requests calls; our code executes them."""

CALCULATOR = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '17 * 23'.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Arithmetic expression using + - * / and parentheses."}
            },
            "required": ["expression"],
        },
    },
}
