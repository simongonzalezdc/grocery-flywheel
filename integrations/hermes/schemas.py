"""Five model-facing schemas; adapters independently enforce them."""
from .engine.grocery_flywheel.optimization import OBJECTIVES
from .tools import NAMES


def schema(name):
    properties = {"state_json": {"type": "string", "description": "Explicit inline state; may enter model/transcript."},
                  "state_name": {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}\.json$"}}
    if name in ("grocery_dietary", "grocery_plan"):
        properties["objective"] = {"type": "string", "enum": sorted(OBJECTIVES)}
    if name == "grocery_plan":
        properties["mode"] = {"type": "string", "enum": ["pickup", "delivery", "in_person"], "default": "pickup"}
    return {"name": name, "description": {
        "grocery_analyze": "Analyze replenishment using the existing local engine.",
        "grocery_dietary": "Evaluate supplied dietary evidence; not a medical guarantee.",
        "grocery_sourcing": "Summarize supplied sourcing questions; no live retailer research.",
        "grocery_plan": "Draft an internal cart for human review; never checkout.",
        "grocery_dashboard": "Write a private local HTML dashboard; never open or serve it."
    }[name], "parameters": {"type": "object", "properties": properties, "additionalProperties": False,
                              "oneOf": [{"required": ["state_json"]}, {"required": ["state_name"]}]}}


SCHEMAS = {name: schema(name) for name in NAMES}
