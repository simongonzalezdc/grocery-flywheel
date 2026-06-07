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
from .cost_log import add_visit, add_purchase, visits_summary, VISIT_TYPES


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
        note = input("Check-in. Describe changes.\n> ").strip()
        if not note:
            print("Aborted."); return
    _do_checkin(args, state, note)


def _do_checkin(args, state, note: str) -> None:
    parsed = parse_checkin_note(note, state.get("items", []))
    add_pulse(state, note, parsed)
    save(args, state)
    if parsed:
        for p in parsed:
            print(f"    * {p['name']}")
    else:
        print(f"  OK: \"{note}\"")


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


def _briefing(state, args) -> None:
    """Morning briefing: quick status + interactive check-in prompt."""
    items = state.get("items", [])
    order = state["order"]
    order_total = float(order.get("total", 0))
    as_of = date.fromisoformat(state["as_of"])
    order_date = date.fromisoformat(order["date"])
    days = max(1, (as_of - order_date).days)
    consumed_value = sum(float(i.get("spend", 0)) * consumed_fraction(i) for i in items)
    known_frac = consumed_value / order_total if order_total else 0
    est_rem = None
    if known_frac > 0:
        est = round(days / known_frac, 1)
        est_rem = round(max(0, est - days), 1)

    print("Good morning! Here is your grocery status.")
    print(f"  Runway: ~{est_rem}d remaining" if est_rem else "  Runway: need more data")

    depleted = [i for i in items if consumed_fraction(i) >= 1.0]
    low = [i for i in items if 0.75 <= consumed_fraction(i) < 1.0]
    if depleted:
        names = ", ".join(i["name"] for i in depleted)
        print(f"  Depleted: {names}")
    if low:
        names = ", ".join(i["name"] for i in low)
        print(f"  Low: {names}")
    if not depleted and not low:
        print("  All good.")

    print()
    print("Check-in? Type what you ate/used, or Enter to skip.")
    print("Examples: \"2 coffees, eggo waffles\", \"none\", \"opened tofu\"")
    note = input("> ").strip()
    if not note:
        print("  Skipped.")
        return
    _do_checkin(args, state, note)

    # After check-in, refresh dashboard + log (same as monitor)
    analysis = analyze_state(state)
    from .render import render_dashboard
    out = Path(getattr(args, "output", None) or "dist/dashboard.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_dashboard(analysis))
    lp = out.parent / "monitor-log.json"
    log = json.loads(lp.read_text()) if lp.exists() else []
    log.append({
        "ts": datetime.now(timezone.utc).isoformat(),
        "alerts": [],
        "runway": analysis.get("estimated_days_remaining"),
    })
    lp.write_text(json.dumps(log[-90:], indent=2))
    print(f"  State updated. ~{analysis.get('estimated_days_remaining')}d runway.")


def cmd_monitor(args) -> None:
    state = load(args)

    # Briefing mode: short status + check-in prompt (for 9 AM fire)
    if getattr(args, "briefing", False):
        _briefing(state, args)
        return

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
    python_path = Path(sys.executable).resolve()
    plist_dir = Path.home() / 'Library' / 'LaunchAgents'
    plist_dir.mkdir(parents=True, exist_ok=True)
    base_args = [str(python_path), '-m', 'grocery_flywheel.cli',
                 '--state', str(state_file), 'monitor']

    def _plist_xml(label, hour, extra_args):
        argv = base_args + extra_args
        arg_lines = '\n'.join(f'  <string>{a}</string>' for a in argv)
        header = '<?xml version="1.0" encoding="UTF-8"?>\n'
        header += '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        header += '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        header += '<plist version="1.0">\n<dict>\n'
        header += f'<key>Label</key><string>{label}</string>\n'
        header += '<key>ProgramArguments</key><array>\n'
        header += arg_lines + '\n</array>\n'
        header += f'<key>WorkingDirectory</key><string>{wf_dir}</string>\n'
        header += f'<key>StartCalendarInterval</key><dict>'
        header += f'<key>Hour</key><integer>{hour}</integer>'
        header += '<key>Minute</key><integer>0</integer></dict>\n'
        header += '<key>RunAtLoad</key><true/>\n'
        header += '<key>EnvironmentVariables</key><dict>\n'
        header += f'<key>PYTHONPATH</key><string>{wf_dir}/src</string>\n'
        header += '<key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>\n'
        header += '</dict>\n</dict>\n</plist>\n'
        return header

    def _write_plist(label, hour, extra_args):
        xml = _plist_xml(label, hour, extra_args)
        pl = plist_dir / f'{label}.plist'
        pl.write_text(xml)
        subprocess.run(['launchctl', 'unload', str(pl)], capture_output=True)
        r = subprocess.run(['launchctl', 'load', str(pl)], capture_output=True, text=True)
        return r.returncode == 0, r.stderr

    m_ok, m_err = _write_plist('com.grocery-flywheel.morning', 9, ['--briefing'])
    e_ok, e_err = _write_plist('com.grocery-flywheel.evening', 19, ['--quiet'])

    if m_ok: print('  OK installed: com.grocery-flywheel.morning (9 AM, briefing)')
    else: print(f'  FAIL morning: {m_err}')
    if e_ok: print('  OK installed: com.grocery-flywheel.evening (7 PM, quiet monitor)')
    else: print(f'  FAIL evening: {e_err}')


def cmd_uninstall(args) -> None:
    plist_dir = Path.home() / 'Library' / 'LaunchAgents'
    for label in ('com.grocery-flywheel.morning', 'com.grocery-flywheel.evening'):
        pl = plist_dir / f'{label}.plist'
        if pl.exists():
            subprocess.run(['launchctl', 'unload', str(pl)], capture_output=True)
            pl.unlink()
            print(f'  OK removed: {label}')
        else:
            print(f'  Not installed: {label}')


def cmd_capture_visit(args) -> None:
    """Interactive capture of a shopping visit: type, duration, amortized cost, purchases."""
    state = load(args)
    from datetime import date as _date
    visit = add_visit(
        state,
        date=_date.today().isoformat(),
        visit_type=args.visit_type,
        duration_min=args.duration_min,
        amortized_cost=args.amortized_cost or 0.0,
        notes=args.notes or "",
    )
    save(args, state)
    print(f"  OK visit {visit['id']} ({visit['type']}, {visit['duration_min']} min)")
    if args.quick:
        return
    while True:
        raw = input("Add a purchase? (blank to finish)\n> ").strip()
        if not raw:
            break
        try:
            name, price = raw.rsplit(" ", 1)
            price = float(price)
        except ValueError:
            print("  Format: 'item name PRICE' (e.g., 'Costco tofu 8.99')")
            continue
        add_purchase(state, visit_id=visit["id"], name=name, price=price)
        save(args, state)
        print(f"  + {name} (${price:.2f})")
    s = visits_summary(state)
    print(f"  Cumulative: {s['visit_count']} visits, ${s['total_spend']:.2f} spend, {s['total_duration_min']} min")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="grocery-flywheel")
    parser.add_argument("--state", help="Path to grocery state JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Create a new state file")
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status", help="Print current grocery status")
    status.set_defaults(func=cmd_status)

    checkin = sub.add_parser("checkin", help="Record a depletion check-in")
    checkin.add_argument("--quick", help="Non-interactive check-in note")
    checkin.set_defaults(func=cmd_checkin)

    order = sub.add_parser("order", help="Start a new order interactively")
    order.set_defaults(func=cmd_order)

    history = sub.add_parser("history", help="Show check-in and order history")
    history.set_defaults(func=cmd_history)

    preferences = sub.add_parser("preferences", help="Show learned preferences")
    preferences.set_defaults(func=cmd_preferences)

    dashboard = sub.add_parser("dashboard", help="Render dashboard HTML")
    dashboard.add_argument("--output", default="dist/dashboard.html", help="Output HTML path")
    dashboard.add_argument("--no-open", action="store_true", help="Do not open the dashboard after writing")
    dashboard.set_defaults(func=cmd_dashboard)

    monitor = sub.add_parser("monitor", help="Run monitor/briefing and refresh dashboard")
    monitor.add_argument("--output", default="dist/dashboard.html", help="Output HTML path")
    monitor.add_argument("--briefing", action="store_true", help="Interactive morning briefing")
    monitor.add_argument("--quiet", action="store_true", help="Suppress non-alert output")
    monitor.set_defaults(func=cmd_monitor)

    install = sub.add_parser("install", help="Install LaunchAgent monitors")
    install.set_defaults(func=cmd_install)

    uninstall = sub.add_parser("uninstall", help="Uninstall LaunchAgent monitors")
    uninstall.set_defaults(func=cmd_uninstall)

    capture = sub.add_parser("capture-visit", help="Record a shopping visit: type, time, cost, purchases")
    capture.add_argument("--visit-type", required=True, choices=sorted(VISIT_TYPES), help="Type of shopping visit")
    capture.add_argument("--duration-min", required=True, type=int, help="Approximate visit duration in minutes")
    capture.add_argument("--amortized-cost", type=float, default=0.0, help="Amortized cost (gas, membership, etc.)")
    capture.add_argument("--notes", default="", help="Optional note about the visit")
    capture.add_argument("--quick", action="store_true", help="Skip interactive purchase entry")
    capture.set_defaults(func=cmd_capture_visit)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
