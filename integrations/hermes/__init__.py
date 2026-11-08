"""Native Hermes integration. Import and registration are household-data inert."""
from pathlib import Path
from .commands import command
from .schemas import SCHEMAS
from .tools import invoke


def register(ctx):
    if not all(callable(getattr(ctx, name, None)) for name in
               ("register_tool", "register_command", "register_skill", "dispatch_tool")):
        raise RuntimeError("Grocery Flywheel requires Hermes >=0.23.0 with native tools, commands and skills.")
    for name, schema in SCHEMAS.items():
        def handler(args, _name=name, **kwargs):
            return invoke(_name, args)
        ctx.register_tool(name=name, toolset="grocery", schema=schema, handler=handler)
    ctx.register_command("grocery", lambda raw_args: command(ctx, raw_args),
                         description="Local grocery planning; human approval, no checkout",
                         args_hint="<action> [JSON]")
    ctx.register_skill("grocery", Path(__file__).parent / "skills/grocery/SKILL.md")
