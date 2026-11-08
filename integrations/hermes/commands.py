"""Deterministic slash routes through the host's tool dispatcher."""
import json
from pathlib import Path

from .containment import ARG_LIMIT, BoundaryError, size
from .engine.grocery_flywheel import __version__
from .tools import error

HELP = '''Grocery Flywheel: analyze, dietary, sourcing, plan, dashboard.
/grocery sample (sanitized demo); /grocery status
/grocery plan {"state_name":"sample.json","mode":"pickup"}
Use exactly one state_name or state_json. Named inputs: plugin-data/grocery-flywheel/state/.
Generated HTML: plugin-data/grocery-flywheel/dashboards/. No checkout or retailer access.
Local engine, but Hermes model calls/transcripts may disclose inputs/results. Obtain consent;
use a verified local/offline model for sensitive data. Dietary safe is not a medical guarantee.'''


def command(ctx, raw_args):
    try:
        size(raw_args, ARG_LIMIT)
        action, _, payload = raw_args.strip().partition(" ")
        if action in ("", "help"):
            return HELP if not payload.strip() else error("INVALID_INPUT")
        if action == "status" and not payload.strip():
            return json.dumps({"plugin": "0.1.0", "engine": __version__, "offline": True,
                               "checkout_available": False, "directories": ["state/", "dashboards/"]})
        if action == "sample" and not payload.strip():
            sample = (Path(__file__).parent / "examples/sample_state.json").read_text()
            return ctx.dispatch_tool("grocery_analyze", {"state_json": sample})
        if action not in ("analyze", "dietary", "sourcing", "plan", "dashboard"):
            return error("INVALID_INPUT") + "\n" + HELP
        # Argument values can contain a large state_json string: do not apply state
        # string-node limits to this outer envelope; adapters validate inner state.
        size(payload, ARG_LIMIT)
        args = json.loads(payload, object_pairs_hook=_unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(BoundaryError()))
        if not isinstance(args, dict):
            raise BoundaryError()
        return ctx.dispatch_tool("grocery_" + action, args)
    except (BoundaryError, ValueError, TypeError, RecursionError):
        return error("INVALID_INPUT") + "\n" + HELP


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BoundaryError()
        result[key] = value
    return result
