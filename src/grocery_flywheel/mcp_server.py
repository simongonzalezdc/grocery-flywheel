from __future__ import annotations

import json
import sys
from typing import Any, cast

from . import __version__
from .core import analyze_state
from .render import render_dashboard
from .state_io import load_state, render_to_file

# The MCP protocol revision this server speaks. Deliberately NOT tied to
# the package version: it tracks the protocol spec date, not releases.
PROTOCOL_VERSION = "2024-11-05"


def _load_state(args: dict[str, Any]) -> dict[str, Any]:
    state_json = args.get("state_json")
    state_path = args.get("state_path")
    if state_json:
        return cast(dict[str, Any], json.loads(str(state_json)))
    if state_path:
        return load_state(str(state_path))
    raise ValueError("Provide state_json or state_path.")


def analyze_replenishment_state(args: dict[str, Any]) -> dict[str, Any]:
    return analyze_state(_load_state(args))


def render_replenishment_dashboard(args: dict[str, Any]) -> dict[str, Any]:
    output_path = args.get("output_path")
    if not output_path:
        raise ValueError("Provide output_path.")
    analysis = analyze_state(_load_state(args))
    target = render_to_file(render_dashboard(analysis), str(output_path))
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


ToolSpec = dict[str, Any]

TOOLS: dict[str, ToolSpec] = {
    "analyze_replenishment_state": {
        "description": "Analyze a Grocery Flywheel replenishment state document and return its structured analysis (items, gaps, sourcing research). Returns a state analysis dict. Use when the agent needs the replenishment picture before rendering or summarizing. Pass state_json (inline state) or state_path (path to a state file) from user input or a previous step.",
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
        "description": "Render the Grocery Flywheel replenishment dashboard as a self-contained HTML file on disk. Returns a dict with output_path (the written file) and items (analyzed item count). Use when the agent must produce a viewable dashboard artifact. Pass output_path (the HTML target) plus state_json or state_path from a prior analyze_replenishment_state result or user input.",
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
        "description": "Extract sourcing research questions and decision boundaries from a replenishment state document. Returns a dict with count and items (item, current_source, research_question, decision_boundary). Use when the agent must summarize open sourcing decisions without the full analysis. Pass state_json or state_path from a prior analyze_replenishment_state result or user input.",
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
    handler = TOOLS[name]["handler"]
    return cast(dict[str, Any], handler(arguments or {}))


def _tool_list() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
        }
        for name, spec in sorted(TOOLS.items())
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
                "serverInfo": {"name": "grocery-flywheel", "version": __version__},
            },
        )
    if method == "tools/list":
        return _response(
            message_id,
            {
                "tools": _tool_list(),
                "_meta": {"ttlMs": 3600000, "cacheScope": "public"},
            },
        )
    if method == "tools/call":
        try:
            result = handle_tool_call(params.get("name", ""), params.get("arguments") or {})
            return _response(
                message_id,
                {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
            )
        except ValueError as exc:
            return _error(message_id, -32602, str(exc))
        except Exception as exc:  # noqa: BLE001
            return _error(message_id, -32603, f"Internal error: {exc}")
    return _error(message_id, -32601, f"Unsupported method: {method}")


def serve(stdin: Any, stdout: Any) -> None:
    """Run the line-delimited JSON-RPC loop over the given streams.

    Split from ``main`` so tests can drive the protocol with StringIO
    instead of the real stdin/stdout.
    """
    for line in stdin:
        if not line.strip():
            continue
        try:
            reply = handle_message(json.loads(line))
        except json.JSONDecodeError as exc:
            reply = _error(None, -32700, f"Invalid JSON: {exc}")
        except Exception as exc:  # noqa: BLE001
            reply = _error(None, -32603, f"Internal error: {exc}")
        if reply is not None:
            stdout.write(json.dumps(reply) + "\n")
            stdout.flush()


def main() -> None:
    serve(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
