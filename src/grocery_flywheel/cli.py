"""grocery_flywheel CLI — full command set."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from datetime import date, datetime, timezone
from pathlib import Path

from .state import (
    add_item, add_pulse, consumed_fraction, load_state,
    make_fresh_state, new_order, parse_checkin_note,
    save_state,
)
from .core import analyze_state


def _guess_storage(category: str, name: str) -> str:
    c = (category or "").lower()
    n = (name or "").lower()
    if "frozen" in c or "frozen" in n:
        return "frozen"
    for marker in ("dry", "canned", "rice", "bean", "pasta", "sauce", "grain"):
        if marker in c:
            return "pantry"
    for marker in ("dairy", "cheese", "milk", "juice", "beverage"):
        if marker in c:
            return "fridge"
    for marker in ("cleaning", "paper", "toiletry", "household"):
        if marker in c:
            return "household"
    return "pantry"


def state_path(args) -> Path:
    default = os.environ.get("GROCERY_STATE", "grocery-state.json")
    return Path(getattr(args, "state", None) or default).resolve()


def load(args):
    return load_state(state_path(args))


def save(args, state):
    save_state(state_path(args), state)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_init(args) -> None:
    p = state_path(args)
    if p.exists() and input("State exists. Overwrite? [y/N] ").strip().lower() != "y":
        print("Aborted."); return
    store = input("Store [Vons]: ").strip() or "Vons"
    default_date = date.today().isoformat()
    order_date = input(f"Order date [{default_date}]: ").strip() or default_date
    total = input("Order total ($): ").strip()
    state = make_fresh_state(store, order_date, float(total) if total else 0.0)
    print("\nAdd items. Leave name blank to finish.")
    while True:
        name = input("  Item name: ").strip()
        if not name:
            break
        item = {
            "name": name,
            "role": input("  Role [staple]: ").strip() or "staple",
            "category": input("  Category: ").strip(),
            "spend": float(input("  Price ($): ").strip() or 0),
            "units_total": int(input("  Units: ").strip() or 0) or None,
            "units_remaining": None,
            "storage": _guess_storage(input("  Category: ").strip(), name),
        }
        add_item(state, item)
        print(f"  + {name}\n")
    save(args, state)
    n_items = len(state["items"])
    print(f"State saved: {p} ({n_items} items)")


def cmd_status(args) -> None:
    state = load(args)
    order = state["order"]
    order_total = float(order.get("total", 0))
    as_of = date.fromisoformat(state["as_of"])
    order_date = date.fromisoformat(order["date"])
    days = max(1, (as_of - order_date).days)
    items = state.get("items", [])
    consumed_value = sum(
        float(i.get("spend", 0)) * consumed_fraction(i) for i in items
    )
    known_frac = consumed_value / order_total if order_total else 0
    est_total = round(days / known_frac, 1) if known_frac > 0 else None
    est_rem = round(max(0, est_total - days), 1) if est_total else None

    depleted = [(i, consumed_fraction(i)) for i in items if consumed_fraction(i) >= 1.0]
    low = [(i, consumed_fraction(i)) for i in items if 0.75 <= consumed_fraction(i) < 1.0]
    ok = [(i, consumed_fraction(i)) for i in items if consumed_fraction(i) < 0.75]

    def item_line(item, frac):
        rem = item.get("units_remaining")
        tot = item.get("units_total")
        fv = item.get("remaining_fraction")
        nm = item["name"]
        if rem is not None and tot and tot > 0:
            return f"  - {nm} -- {rem}/{tot} left ({frac:.0%})"
        if fv is not None:
            return f"  - {nm} -- {frac:.0%} consumed (~{int(fv*100)}% rem)"
        if frac > 0:
            return f"  - {nm} -- {frac:.0%} consumed"
        return f"  - {nm} -- ready"

    print("====== GROCERY FLYWHEEL STATUS ======")
    print(f"  Store: {order['store']} | Order: {order['date']} (${order_total:.2f})")
    print(f"  As of: {state['as_of']} ({days}d) | Items: {len(items)}")
    print(f"  Consumed: ${consumed_value:.2f} ({known_frac:.0%})")
    if est_rem:
        print(f"  Runway: ~{est_rem}d remaining (est {est_total}d total)")
    else:
        print("  Runway: Need more data")

    if depleted:
        print(f"\n  RED DEPLETED ({len(depleted)}):")
        for i, _ in depleted:
            print(f"     * {i['name']} [{i.get('role','')}]")
    if low:
        print(f"\n  YELLOW LOW ({len(low)}):")
        for i, f in low:
            print(item_line(i, f))
    if ok:
        print(f"\n  GREEN OK ({len(ok)}):")
        for i, f in ok:
            print(item_line(i, f))

    bridge = [i for i, _ in depleted if i.get("role") == "bridge_food"]
    if bridge:
        print(f"\n  BOLT REORDER:")
        for i in bridge:
            print(f"     * {i['name']}")

    prefs = state.get("preferences", [])
    if prefs:
        print(f"\n  BOOK Preferences ({len(prefs)}):")
        for pr in prefs[:5]:
            print(f"     * {pr.get('key','?')}: {pr.get('rule','')}")

    pulses = state.get("pulses")
    if pulses:
        last = pulses[-1].get("date", "?")
        print(f"\n  Last check-in: {last}")


def cmd_checkin(args) -> None:
    state = load(args)
    note = getattr(args, "quick", None)
    if not note:
        prompt = "Check-in. Describe changes.\n> "
        note = input(prompt).strip()
        if not note:
            print("Aborted."); return
    parsed = parse_checkin_note(note, state.get("items", []))
    add_pulse(state, note, parsed)
    save(args, state)
    if parsed:
        for p in parsed:
            print(f"    * {p['name']}")
    else:
        print(f'  OK: "{note}"')


def cmd_order(args) -> None:
    state = load(args)
    prev_store = state["order"].get("store", "Vons")
    store = input(f"Store [{prev_store}]: ").strip() or prev_store
    default_date = date.today().isoformat()
    dt = input(f"Date [{default_date}]: ").strip() or default_date
    total = float(input("Total ($): ").strip() or 0)
    new_order(state, store, dt, total)
    print("\nAdd items. Leave name blank to finish.")
    while True:
        name = input("  Item: ").strip()
        if not name:
            break
        cat = input("  Category: ").strip()
        item = {
            "name": name,
            "role": input("  Role [staple]: ").strip() or "staple",
            "category": cat,
            "spend": float(input("  Price ($): ").strip() or 0),
            "units_total": int(input("  Units: ").strip() or 0) or None,
            "units_remaining": None,
            "storage": _guess_storage(cat, name),
        }
        add_item(state, item)
        print(f"  + {name}\n")
    save(args, state)


def cmd_history(args) -> None:
    state = load(args)
    pulses = state.get("pulses", [])
    if pulses:
        print("Check-ins:")
    for p in pulses:
        print(f"\n  {p['date']}: {p['note']}")
        for e in (p.get("parsed") or []):
            print(f"    * {e}")
    order_history = state.get("order_history", [])
    if order_history:
        print("\nPast orders:")
    for o in order_history:
        print(f"  * {o.get('date','')} {o.get('store','')} ${o.get('total',0):.2f}")


def cmd_preferences(args) -> None:
    prefs = load(args).get("preferences", [])
    if not prefs:
        print("No preferences.")
        return
    for p in prefs:
        print(f"\n  [{p['key']}]")
        print(f"      {p.get('signal','')}")
        print(f"      {p.get('rule','')}")


def cmd_dashboard(args) -> None:
    from .render import render_dashboard
    out = Path(getattr(args, "output", None) or "dist/dashboard.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    text = render_dashboard(analyze_state(load(args)))
    out.write_text(text)
    print(f"  Written to {out}")
    if not getattr(args, "no_open", False):
        webbrowser.open(f"file://{out.resolve()}")


def cmd_monitor(args) -> None:
    state = load(args)
    analysis = analyze_state(state)
    alerts: list[str] = []

    db = [i for i in analysis["items"]
          if i["consumed_fraction"] >= 1.0 and i.get("role") == "bridge_food"]
    lw = [i for i in analysis["items"]
          if 0.75 <= i["consumed_fraction"] < 1.0]

    pulses = state.get("pulses", [])
    if pulses:
        last_date = date.fromisoformat(pulses[-1]["date"])
        silent_days = (date.today() - last_date).days
        if silent_days >= 3:
            alerts.append(f"No check-in {silent_days}d")
    if db:
        alerts.append(f"Reorder: " + ", ".join(i["name"] for i in db))
    if lw:
        alerts.append("Low: " + ", ".join(f"{i['name']} ({i['consumed_fraction']:.0%})" for i in lw))

    # Render dashboard
    from .render import render_dashboard
    out = Path(getattr(args, "output", None) or "dist/dashboard.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(analysis))

    # Log to monitor-log.json
    lp = out.parent / "monitor-log.json"
    log = json.loads(lp.read_text()) if lp.exists() else []
    log.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "alerts": alerts,
        "runway": analysis.get("estimated_days_remaining"),
    })
    lp.write_text(json.dumps(log[-90:], indent=2))

    quiet = getattr(args, "quiet", False)
    if alerts:
        if not quiet:
            for a in alerts:
                print(f"  {a}")
        for a in alerts:
            _notify("Grocery Flywheel", a)
    else:
        if not quiet:
            runway = analysis.get("estimated_days_remaining")
            print(f"  OK All good. ~{runway}d runway.")


def cmd_install(args) -> None:
    wf_dir = Path(__file__).resolve().parent.parent
    state_file = state_path(args)
    label = "com.grocery-flywheel.heartbeat"
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    pl = plist_dir / f"{label}.plist"
    python_path = Path(sys.executable).resolve()
    gf_path = Path(__file__).resolve()
    plist_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Label</key><string>{label}</string>
<key>ProgramArguments</key><array>
  <string>{python_path}</string>
  <string>{gf_path}</string>
  <string>--state</string>
  <string>{state_file}</string>
  <string>monitor</string>
  <string>--quiet</string>
</array>
<key>WorkingDirectory</key><string>{wf_dir}</string>
<key>StartCalendarInterval</key><array>
  <dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <dict><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
</array>
<key>RunAtLoad</key><true/>
<key>StandardOutPath</key><string>{wf_dir}/dist/hb-stdout.log</string>
<key>StandardErrorPath</key><string>{wf_dir}/dist/hb-stderr.log</string>
<key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict>
</plist>'''
    pl.write_text(plist_xml)
    subprocess.run(["launchctl", "unload", str(pl)], capture_output=True)
    r = subprocess.run(["launchctl", "load", str(pl)], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"  OK {label} at 9 AM + 7 PM")
    else:
        print(f"  FAIL: {r.stderr}")


def cmd_uninstall(args) -> None:
    pl = Path.home() / "Library" / "LaunchAgents" / "com.grocery-flywheel.heartbeat.plist"
    if pl.exists():
        subprocess.run(["launchctl", "unload", str(pl)], capture_output=True)
        pl.unlink()
        print("  OK uninstalled")
    else:
        print("  Not installed.")


def cmd_help(args) -> None:
    print(__doc__)


def _notify(title: str, msg: str) -> None:
    try:
        import shlex
        safe_msg = msg.replace('"', '\\"')
        subprocess.run(
            ["osascript", "-e", f'display notification "{safe_msg}" with title "{title}"'],
            capture_output=True, timeout=5
        )
    except Exception:
        pass


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(prog="grocery-flywheel")
    p.add_argument("--state", type=Path)
    s = p.add_subparsers(dest="command")
    s.add_parser("init")
    s.add_parser("status")
    s.add_parser("help")
    c = s.add_parser("checkin"); c.add_argument("--quick", "-q")
    s.add_parser("order")
    s.add_parser("history")
    s.add_parser("preferences")
    d = s.add_parser("dashboard")
    d.add_argument("--output", "-o", type=Path)
    d.add_argument("--no-open", action="store_true")
    m = s.add_parser("monitor")
    m.add_argument("--quiet", "-q", action="store_true")
    m.add_argument("--output", "-o", type=Path)
    s.add_parser("install")
    s.add_parser("uninstall")

    cmds = {
        "init": cmd_init,
        "status": cmd_status,
        "checkin": cmd_checkin,
        "order": cmd_order,
        "history": cmd_history,
        "preferences": cmd_preferences,
        "dashboard": cmd_dashboard,
        "monitor": cmd_monitor,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
        "help": cmd_help,
    }
    ns = p.parse_args()
    fn = cmds.get(ns.command)
    if fn:
        fn(ns)
    else:
        p.print_help()


if __name__ == "__main__":
    main()

