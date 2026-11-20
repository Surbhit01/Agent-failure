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


def _tool(name, description, properties):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {k: {"type": "string", "description": v} for k, v in properties.items()},
                "required": list(properties),
            },
        },
    }


READ_FILE = _tool("read_file", "Read a text file from the workspace, e.g. 'notes.txt'.", {"path": "File name or relative path."})
FETCH_PAGE = _tool("fetch_page", "Fetch the text of a web page by URL.", {"url": "Full URL, e.g. https://example.com/news"})
SEND_EMAIL = _tool(
    "send_email",
    "Send an email.",
    {"to": "Recipient email address.", "subject": "Email subject.", "body": "Email body text."},
)
