from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .core import analyze_state
from .render import render_dashboard

PROTOCOL_VERSION = "2024-11-05"


def _load_state(args: dict[str, Any]) -> dict[str, Any]:
    state_json = args.get("state_json")
    state_path = args.get("state_path")
    if state_json:
        return json.loads(str(state_json))
    if state_path:
        return json.loads(Path(str(state_path)).read_text())
    raise ValueError("Provide state_json or state_path.")


def analyze_replenishment_state(args: dict[str, Any]) -> dict[str, Any]:
    return analyze_state(_load_state(args))


def render_replenishment_dashboard(args: dict[str, Any]) -> dict[str, Any]:
    output_path = args.get("output_path")
    if not output_path:
        raise ValueError("Provide output_path.")
    analysis = analyze_state(_load_state(args))
    target = Path(str(output_path))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_dashboard(analysis))
    return {"output_path": str(target), "items": len(analysis["items"])}


def summarize_sourcing_research(args: dict[str, Any]) -> dict[str, Any]:
    analysis = analyze_state(_load_state(args))
    rows = analysis.get("sourcing_research", [])
    return {
        "count": len(rows),
        "items": [
            {
                "item": row.get("item"),
                "current_source": row.get("current_source"),
                "research_question": row.get("research_question"),
                "decision_boundary": row.get("decision_boundary"),
            }
            for row in rows
        ],
    }


TOOLS = {
    "analyze_replenishment_state": {
        "description": "Analyze a Grocery Flywheel state JSON object or file path.",
        "handler": analyze_replenishment_state,
        "inputSchema": {
            "type": "object",
            "properties": {
                "state_path": {"type": "string"},
                "state_json": {"type": "string"},
            },
        },
    },
    "render_replenishment_dashboard": {
        "description": "Render the local Grocery Flywheel HTML dashboard from state JSON.",
        "handler": render_replenishment_dashboard,
        "inputSchema": {
            "type": "object",
            "properties": {
                "state_path": {"type": "string"},
                "state_json": {"type": "string"},
                "output_path": {"type": "string"},
            },
            "required": ["output_path"],
        },
    },
    "summarize_sourcing_research": {
        "description": "Extract sourcing research questions and decision boundaries from state JSON.",
        "handler": summarize_sourcing_research,
        "inputSchema": {
            "type": "object",
            "properties": {
                "state_path": {"type": "string"},
                "state_json": {"type": "string"},
            },
        },
    },
}


def handle_tool_call(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    return TOOLS[name]["handler"](arguments or {})


def _tool_list() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
        }
        for name, spec in TOOLS.items()
    ]


def _response(message_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def handle_message(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    message_id = message.get("id")
    params = message.get("params") or {}

    if message_id is None:
        return None
    if method == "initialize":
        return _response(
            message_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "grocery-flywheel", "version": "0.1.0"},
            },
        )
    if method == "tools/list":
        return _response(message_id, {"tools": _tool_list()})
    if method == "tools/call":
        try:
            result = handle_tool_call(params.get("name", ""), params.get("arguments") or {})
            return _response(
                message_id,
                {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            )
        except ValueError as exc:
            return _error(message_id, -32602, str(exc))
    return _error(message_id, -32601, f"Unsupported method: {method}")


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle_message(json.loads(line))
        except json.JSONDecodeError as exc:
            reply = _error(None, -32700, f"Invalid JSON: {exc}")
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
