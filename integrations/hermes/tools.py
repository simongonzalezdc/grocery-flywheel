"""Native adapters: one engine, no retailer or model integration."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re

from .containment import (ARG_LIMIT, RESULT_LIMIT, BoundaryError, io_error,
                          read_state, require, size, strict_json, write_dashboard)
from .engine.grocery_flywheel import mcp_server
from .engine.grocery_flywheel.core import analyze_state
from .engine.grocery_flywheel.optimization import OBJECTIVES
from .engine.grocery_flywheel.render import render_dashboard

HANDLERS = {"grocery_analyze": mcp_server.analyze_replenishment_state,
            "grocery_dietary": mcp_server.evaluate_dietary,
            "grocery_sourcing": mcp_server.summarize_sourcing_research,
            "grocery_plan": mcp_server.plan_next_cart}
NAMES = (*HANDLERS, "grocery_dashboard")
MESSAGES = {"INVALID_INPUT": "Provide valid bounded JSON and exactly one state selector.",
            "LIMIT_EXCEEDED": "Input or output exceeds the supported limit.",
            "UNSAFE_PATH": "Profile storage or state name is unsafe.",
            "STATE_NOT_FOUND": "Named state is not present in this profile.",
            "IO_ERROR": "Private profile storage is unavailable.",
            "ENGINE_ERROR": "The engine could not process this state.",
            "APPROVAL_BOUNDARY": "Unsafe draft rejected; no usable plan returned.",
            "BUSY": "Another dashboard render is in progress."}


def error(code):
    return json.dumps({"ok": False, "error": {"code": code, "message": MESSAGES[code]}})


def approval(value):
    if isinstance(value, dict):
        if "checkout_available" in value or "approval_required" in value:
            require(value.get("checkout_available") is False and value.get("approval_required") is True,
                    "APPROVAL_BOUNDARY")
            if "items" in value:
                require(isinstance(value["items"], list), "APPROVAL_BOUNDARY")
                require(all(isinstance(row, dict) and row.get("approval_state") == "needs_human_approval"
                            for row in value["items"]), "APPROVAL_BOUNDARY")
        for child in value.values():
            approval(child)
    elif isinstance(value, list):
        for child in value:
            approval(child)


def validate_state(state):
    # Read-side legacy compatibility: constrain shapes, not canonical version tags.
    for key in ("items", "dietary_profiles", "substitutions", "sourcing_research", "pulses",
                "preferences", "visits", "corrections", "draft_edit_events", "adapter_matrix"):
        if key in state:
            require(isinstance(state[key], list) and all(isinstance(row, dict) for row in state[key]))
    for key in ("order", "consent", "privacy", "inventory_surface", "storage", "preferences_config"):
        if key in state:
            require(isinstance(state[key], dict))
    require(isinstance(state.get("items"), list) and isinstance(state.get("order"), dict))
    for profile in state.get("dietary_profiles", []):
        require(isinstance(profile.get("restrictions", []), list))
        require(all(isinstance(row, dict) for row in profile.get("restrictions", [])))
    for item in state["items"]:
        require(isinstance(item.get("name"), str) and bool(item["name"]))
        rows = item.get("product_evidence", [])
        require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows))


def secure_html(document):
    # Trust only scripts emitted by the unchanged renderer. User content must already
    # be escaped by it; CSP adds a second boundary against remote resources/navigation.
    hashes = ["'sha256-" + base64.b64encode(hashlib.sha256(script.encode()).digest()).decode() + "'"
              for script in re.findall(r"<script>(.*?)</script>", document, re.S)]
    # The existing correction panel uses six fixed inline click handlers. Permit
    # only those exact handler hashes, never general unsafe-inline scripts.
    hashes.extend("'sha256-" + base64.b64encode(hashlib.sha256(("capture('" + signal + "')").encode()).digest()).decode() + "'"
                  for signal in ("never_again", "buy_elsewhere", "wrong_format", "too_expensive", "good_default", "emergency_only"))
    policy = ("default-src 'none'; script-src 'unsafe-hashes' " + (" ".join(hashes) or "'none'") +
              "; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; "
              "font-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'")
    document = document.replace("</head>", "<style>.panel{min-width:0;overflow-x:auto}"
                                "header{overflow-wrap:anywhere}</style></head>", 1)
    return document.replace("<head>", '<head><meta http-equiv="Content-Security-Policy" content="' +
                            html.escape(policy, quote=True) + '">', 1)


def invoke(name, args):
    try:
        require(name in NAMES)
        require(isinstance(args, dict))
        size(json.dumps(args, ensure_ascii=False, allow_nan=False), ARG_LIMIT)
        allowed = {"state_json", "state_name"}
        if name in ("grocery_dietary", "grocery_plan"):
            allowed.add("objective")
        if name == "grocery_plan":
            allowed.add("mode")
        require(not (set(args) - allowed))
        require(("state_json" in args) != ("state_name" in args))
        if "objective" in args:
            require(isinstance(args["objective"], str) and args["objective"] in OBJECTIVES)
        if "mode" in args:
            require(args["mode"] in ("pickup", "delivery", "in_person"))
        text = args["state_json"] if "state_json" in args else read_state(args["state_name"])
        state = strict_json(text)
        validate_state(state)
        engine_args = {"state_json": json.dumps(state), **{key: args[key] for key in ("objective", "mode") if key in args}}
        if name == "grocery_dashboard":
            analysis = analyze_state(state)
            approval(analysis)
            data = write_dashboard(secure_html(render_dashboard(analysis)))
            data["items"] = len(analysis["items"])
        else:
            data = HANDLERS[name](engine_args)
            if name == "grocery_plan":
                require(isinstance(data, dict) and isinstance(data.get("items"), list)
                        and data.get("checkout_available") is False
                        and data.get("approval_required") is True, "APPROVAL_BOUNDARY")
            if name == "grocery_analyze":
                require(isinstance(data.get("cart_plan"), dict)
                        and isinstance(data["cart_plan"].get("items"), list)
                        and data["cart_plan"].get("checkout_available") is False
                        and data["cart_plan"].get("approval_required") is True, "APPROVAL_BOUNDARY")
            approval(data)
        result = json.dumps({"ok": True, "tool": name, "data": data, "privacy": "local-sensitive"}, allow_nan=False)
        size(result, RESULT_LIMIT)
        return result
    except BoundaryError as exc:
        return error(exc.code)
    except OSError as exc:
        return error(io_error(exc))
    except RuntimeError:
        return error("APPROVAL_BOUNDARY")
    except (ValueError, TypeError, OverflowError, RecursionError):
        return error("INVALID_INPUT")
    except Exception:
        return error("ENGINE_ERROR")
