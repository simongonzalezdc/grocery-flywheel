"""grocery_flywheel.state — state management for Grocery Flywheel."""

from __future__ import annotations

import json as _json
import re as _re
from datetime import date as _date
from pathlib import Path as _Path
from typing import Any as _Any


def load_state(path: _Path) -> dict[str, _Any]:
    return _json.loads(_Path(path).read_text())


def save_state(path: _Path, state: dict[str, _Any]) -> None:
    path = _Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(_json.dumps(state, indent=2) + "\n")
    tmp.rename(path)


def make_fresh_state(
    store: str,
    order_date: str,
    total: float,
    surface_type: str = "personal_grocery",
    surface_label: str = "Home groceries",
) -> dict[str, _Any]:
    return {
        "as_of": _date.today().isoformat(),
        "inventory_surface": {"type": surface_type, "label": surface_label},
        "acquisition_channel": "manual_entry",
        "order": {"store": store, "date": order_date, "total": total},
        "items": [],
        "pulses": [],
        "preferences": [],
        "dietary_profiles": [],
        "substitutions": [],
        "sourcing_research": [],
        "retailers": [],
    }


def consumed_fraction(item: dict[str, _Any]) -> float:
    rf = item.get("remaining_fraction")
    tot = item.get("units_total")
    rem = item.get("units_remaining")
    cf = item.get("consumed_fraction")
    if rf is not None:
        v = 1.0 - float(rf)
        return max(0.0, min(1.0, v))
    if tot and tot > 0 and rem is not None:
        v = (tot - rem) / float(tot)
        return max(0.0, min(1.0, v))
    if cf is not None:
        return max(0.0, min(1.0, float(cf)))
    return 0.0


def _storage_hint(category: str, name: str) -> str:
    c = (category or "").lower()
    n = (name or "").lower()
    if "frozen" in c or "frozen" in n:
        return "frozen"
    pantry = ("dry", "canned", "rice", "bean", "pasta", "sauce", "grain")
    fridge = ("dairy", "cheese", "milk", "juice", "beverage")
    house = ("cleaning", "paper", "toiletry", "household")
    for marker in pantry:
        if marker in c:
            return "pantry"
    for marker in fridge:
        if marker in c:
            return "fridge"
    for marker in house:
        if marker in c:
            return "household"
    return "pantry"


def _norm(raw: dict[str, _Any]) -> dict[str, _Any]:
    storage = raw.get("storage")
    if storage is None:
        storage = _storage_hint(raw.get("category", ""), raw.get("name", ""))
    ut = raw.get("units_total")
    ur = raw.get("units_remaining")
    rf = raw.get("remaining_fraction")
    cf = raw.get("consumed_fraction")
    return {
        "name": str(raw.get("name", "Unknown")),
        "role": str(raw.get("role", "staple")),
        "category": str(raw.get("category", "")),
        "storage": storage,
        "spend": float(raw.get("spend", 0)),
        "units_total": int(ut) if ut is not None else None,
        "units_remaining": int(ur) if ur is not None else None,
        "remaining_fraction": float(rf) if rf is not None else None,
        "consumed_fraction": float(cf) if cf is not None else None,
        "notes": str(raw.get("notes", "")),
    }


def add_item(state: dict[str, _Any], item: dict[str, _Any]) -> dict[str, _Any]:
    byname = {i["name"]: i for i in state["items"]}
    norm = _norm(item)
    nm = item.get("name", "")
    if nm in byname:
        byname[nm].update(norm)
    else:
        state["items"].append(norm)
    state["as_of"] = _date.today().isoformat()
    return state


def update_item(
    state: dict[str, _Any], name: str, updates: dict[str, _Any]
) -> bool:
    n = name.lower()
    for item in state["items"]:
        ln = item["name"].lower()
        if n in ln or ln in n:
            item.update(_norm(updates))
            state["as_of"] = _date.today().isoformat()
            return True
    return False


def remove_item(state: dict[str, _Any], name: str) -> bool:
    n = name.lower()
    for i in range(len(state["items"]) - 1, -1, -1):
        if n in state["items"][i]["name"].lower():
            state["items"].pop(i)
            state["as_of"] = _date.today().isoformat()
            return True
    return False


def add_pulse(
    state: dict[str, _Any],
    note: str,
    parsed: list[dict[str, _Any]] | None = None,
) -> dict[str, _Any]:
    if parsed:
        for upd in parsed:
            nm = upd.get("name")
            if nm:
                update_item(state, nm, upd)
    state.setdefault("pulses", []).append({
        "date": _date.today().isoformat(),
        "note": note,
        "parsed": [str(p) for p in (parsed or [])],
    })
    state["as_of"] = _date.today().isoformat()
    return state


def parse_checkin_note(
    note: str, items: list[dict[str, _Any]]
) -> list[dict[str, _Any]]:
    updates: list[dict[str, _Any]] = []
    n = note.lower()
    # "N name left/remaining/done"
    for m in _re.finditer(r"(\d+)\s+(\w[\w\s]*?)\s+(?:left|remaining|done)", n):
        item = _best_match(m.group(2).strip(), items)
        if item:
            kw = {"name": item["name"], "units_remaining": int(m.group(1))}
            if "done" in n or "finish" in n:
                kw["units_remaining"] = 0
            updates.append(kw)
    # "ate N name"
    for m in _re.finditer(r"ate\s+(\d+)\s+(\w[\w\s]*?)(?:[,\.]|$)", n):
        item = _best_match(m.group(2).strip(), items)
        if item:
            prev = item.get("units_remaining") or item.get("units_total") or 1
            updates.append({"name": item["name"], "units_remaining": max(0, prev - int(m.group(1)))})
    # "opened name"
    for m in _re.finditer(r"(?:opened|started)\s+(\w[\w\s]*?)(?:[,\.]|$)", n):
        item = _best_match(m.group(1).strip(), items)
        if item:
            updates.append({"name": item["name"], "remaining_fraction": 1.0})
    return _dedup(updates)


def _best_match(name: str, items: list[dict[str, _Any]]) -> dict[str, _Any] | None:
    n = name.strip().lower()
    for item in items:
        if item["name"].lower() == n:
            return item
    for item in items:
        ln = item["name"].lower()
        if n in ln or ln in n:
            return item
    best, score = None, 0
    words = set(n.split())
    for item in items:
        s = len(words & set(item["name"].lower().split()))
        if s > score:
            best, score = item, s
    return best


def _dedup(updates: list[dict[str, _Any]]) -> list[dict[str, _Any]]:
    seen: set[str] = set()
    out: list[dict[str, _Any]] = []
    for upd in updates:
        k = upd.get("name", "")
        if k and k not in seen:
            seen.add(k)
            out.append(upd)
    return out


def add_preference(
    state: dict[str, _Any], key: str, signal: str, rule: str
) -> dict[str, _Any]:
    prefs = state.setdefault("preferences", [])
    for p in prefs:
        if p.get("key") == key:
            p.update({"signal": signal, "rule": rule})
            return state
    prefs.append({"key": key, "signal": signal, "rule": rule})
    return state


def new_order(
    state: dict[str, _Any], store: str, order_date: str, total: float
) -> dict[str, _Any]:
    state.setdefault("order_history", []).append(state["order"])
    state["order"] = {"store": store, "date": order_date, "total": total}
    state["as_of"] = _date.today().isoformat()
    return state
