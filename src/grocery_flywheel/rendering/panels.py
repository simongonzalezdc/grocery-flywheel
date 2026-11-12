"""The panel registry and the dashboard composition.

A panel is a function from analysis to HTML. The registry stays the single
list of panels; ``render_dashboard`` decides the reading order:

    masthead status -> attention -> one action -> runway -> ledger -> evidence

The order is the design decision from t_0abdce8f: the dietary verdict cannot
be scrolled past, the action comes second, depletion third, and every other
original panel stays reachable in a native disclosure. No engine semantics
live here — only presentation of fields the engine already produced.

Two display rules are load-bearing and fail closed:

* A dietary result of ``safe`` is shown as Cleared only when an evaluation for
  that item exists *and* its evidence status is current. A missing status, an
  unknown status, or a ``safe`` field without current evidence renders
  "Not evaluated" — never a success token.
* Price state comes from the freshness record the page already computes, so
  the ledger and the freshness panel speak one vocabulary.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from html import escape
from typing import Any, Callable

from .layout import header_line, human_date, humanize_key, page_shell

PanelRender = Callable[[dict[str, Any]], str]

ROLE_LABELS = {
    "bridge_food": "Bridge food",
    "critical_household_essential": "Household essential",
    "pantry_base": "Pantry base",
    "flavor_unlock": "Flavour unlock",
}
ACTION_LABELS = {
    "review_alternate_source": "Compare an alternate source",
    "check_aisle_price": "Check the shelf price",
    "restock": "Restock",
}
APPROVAL_LABELS = {"needs_human_approval": "Needs your approval"}
RESULT_LABELS = {
    "blocked": "Blocked",
    "needs_review": "Needs review",
    "warn": "Warning",
    "safe": "Cleared",
}
EVIDENCE_LABELS = {
    "current": "Current evidence",
    "missing": "No label evidence",
    "stale": "Evidence out of date",
    "ambiguous": "No usable label content",
    "unrecognized_restriction": "Restriction not recognised",
}
PRICE_LABELS = {
    "priced": "Priced",
    "unpriced": "No price captured",
    "estimated": "Estimated price",
    "gift": "Gift — price optional",
}
SOURCE_LABELS = {"normal store": "your usual store"}
SEVERITY = {"safe": 0, "warn": 1, "needs_review": 2, "blocked": 3}
RESULT_CLASS = {"blocked": "missing", "needs_review": "missing", "warn": "warn", "safe": "ok"}


def _panel(name: str, span: str, render: PanelRender) -> dict[str, Any]:
    return {"name": name, "span": span, "render": render}


def _plural(count: int, one: str, many: str | None = None) -> str:
    return one if count == 1 else (many or one + "s")


def _label(mapping: dict[str, str], value: object) -> str:
    raw = str(value or "")
    return mapping.get(raw, humanize_key(raw))


def _role(value: object) -> str:
    return ROLE_LABELS.get(str(value or ""), humanize_key(value))


def _section_head(label: str, note: str = "") -> str:
    note_html = f"<span class='section-note'>{note}</span>" if note else ""
    return (f"<div class='section-head'><h2 class='section-label'>{label}</h2>"
            f"{note_html}</div>")


def _money(value: object) -> str:
    try:
        return f"${float(value or 0):.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def _days(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "unknown"
    return str(int(number)) if number == int(number) else f"{number:g}"


def _explicit_result(value: object) -> str:
    raw = str(value or "").strip().lower()
    return raw if raw in SEVERITY else ""


def _verdict_rows(evaluations: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """One evaluation per item, keeping the most severe result (fail closed)."""
    by_item: dict[str, dict[str, Any]] = {}
    for row in evaluations:
        name = str(row.get("item") or "")
        result = _explicit_result(row.get("result"))
        if not name or not result:
            continue
        current = by_item.get(name)
        if current is None or SEVERITY[result] > SEVERITY[_explicit_result(current.get("result"))]:
            by_item[name] = row
    return by_item


# --- attention ----------------------------------------------------------

def _dietary_verdict(analysis: dict[str, Any]) -> dict[str, Any]:
    evaluations = analysis.get("dietary_evaluations") or []
    items = analysis.get("items") or []
    profiles = analysis.get("dietary_profiles") or []
    by_item = _verdict_rows(evaluations)
    results = [_explicit_result(row.get("result")) for row in by_item.values()]
    counts = Counter(results)
    total = len(items)
    cleared = sum(1 for row in by_item.values()
                  if _explicit_result(row.get("result")) == "safe"
                  and str(row.get("evidence_status") or "") == "current")
    with_current = {name for name, row in by_item.items()
                    if str(row.get("evidence_status") or "") == "current"}
    evidence_counts = Counter(str(row.get("evidence_status") or "missing")
                              for row in evaluations)
    warn_only = bool(evaluations) and all(
        _explicit_result(row.get("result")) == "warn" for row in evaluations)
    return {
        "evaluations": evaluations, "items": items, "profiles": profiles,
        "by_item": by_item,
        "total": total, "blocked": counts["blocked"], "needs_review": counts["needs_review"],
        "warn": counts["warn"], "open": total - cleared, "cleared": cleared,
        "evidence_gap": total - len(with_current), "current_items": len(with_current),
        "evidence_counts": evidence_counts, "warn_only": warn_only,
    }


def _state_legend() -> str:
    entries = (
        ("missing", "Blocked",
         "The engine's evidence contradicts this household restriction."),
        ("missing", "Needs review",
         "Evidence is missing, stale, ambiguous or unrecognised; a person must check it."),
        ("warn", "Warning",
         "A warn-tier restriction, or evidence that does not settle the question. Never a clearance."),
        ("ok", "Cleared",
         "Current label evidence rules this restriction out."),
        ("neutral", "Not evaluated",
         "No evaluation exists for this item. Treated as unverified."),
    )
    body = "".join(
        f"<div><dt><span class='mark {css}'>{escape(word)}</span></dt>"
        f"<dd>{escape(meaning)}</dd></div>"
        for css, word, meaning in entries)
    return f"<dl class='state-legend'>{body}</dl>"


def _dietary(a: dict[str, Any]) -> str:
    profile_rows = a.get("dietary_profiles") or []
    verdict = _dietary_verdict(a)
    head = _section_head("Needs attention today", "Dietary evidence")
    if not profile_rows:
        return (f"<article class='panel span-12 attention quiet'>{head}"
                "<h3>No dietary restriction profile configured.</h3>"
                "<p class='muted'>This dashboard makes no dietary claim. Add a profile in "
                "your state file to evaluate items against it.</p></article>")

    total = verdict["total"]
    open_items = verdict["open"]
    profiles = "; ".join(
        escape(str(profile.get("label") or profile.get("profile_id") or "Household profile"))
        for profile in profile_rows
    )
    restrictions = []
    for profile in profile_rows:
        for restriction in profile.get("restrictions") or []:
            value = humanize_key(restriction.get("value") or restriction.get("type") or "")
            tier = humanize_key(restriction.get("safety_tier") or "preference")
            behaviour = humanize_key(restriction.get("behavior") or "warn")
            restrictions.append(f"{value} (safety tier: {tier}; behaviour: {behaviour})")
    restriction_text = "; ".join(restrictions) or "none recorded"

    if verdict["blocked"]:
        headline = (f"{verdict['blocked']} {_plural(verdict['blocked'], 'item is', 'items are')} "
                    "blocked by your household dietary restrictions.")
    elif open_items:
        headline = "No item has been cleared as safe for your household diet."
    elif total:
        headline = (f"All {total} {_plural(total, 'item is', 'items are')} cleared against "
                    "current dietary evidence.")
    else:
        headline = "No items to evaluate yet."
    if open_items:
        caption = "items blocked or unverified" if verdict["blocked"] else "items unverified"
        figure = (f"<div class='attention-figure'>{open_items}/{total}"
                  f"<small>{caption}</small></div>")
    else:
        figure = (f"<div class='attention-figure' style='color:var(--sage)'>"
                  f"{verdict['cleared']}/{total}<small>items cleared</small></div>")

    if verdict["evidence_gap"]:
        evidence_summary = (
            f"{verdict['evidence_gap']} of {total} {_plural(total, 'item has', 'items have')} no "
            "current ingredient, allergen, or certification evidence on file."
        )
    else:
        evidence_summary = f"Every one of the {total} items carries current label evidence."
    engine_note = (
        "This household's restriction is configured to warn, so the engine returns a "
        "warning for every item and clears none of them."
        if verdict["warn_only"] and open_items else
        "The engine clears an item only when current label evidence rules the "
        "restriction out; a warning is not a clearance."
    )
    caveat = (f"Profile: {profiles}. <b>Missing evidence is a data gap, not proof of a "
              "safety failure.</b> But it means this dashboard cannot tell you anything "
              "is safe.")
    tier_note = (f"Restriction: {escape(restriction_text)}. The engine flags every item it "
                 "cannot clear; a warning is never a safety verdict.")

    rows = sorted(
        verdict["evaluations"],
        key=lambda e: (-SEVERITY.get(_explicit_result(e.get("result")), 0),
                       str(e.get("item") or "")),
    )
    body = "".join(
        f"<tr><td>{escape(str(e.get('item') or ''))}</td>"
        f"<td data-raw-result='{escape(str(e.get('result') or ''))}'>"
        f"{escape(_label(RESULT_LABELS, e.get('result')))}</td>"
        f"<td data-raw-evidence='{escape(str(e.get('evidence_status') or ''))}'>"
        f"{escape(_label(EVIDENCE_LABELS, e.get('evidence_status')))}</td>"
        f"<td>{escape(str(e.get('reason') or ''))}</td></tr>"
        for e in rows
    )
    disclosure = ""
    if body:
        disclosure = (
            f"<details class='evidence'><summary>See the evidence — "
            f"{len(rows)} dietary {_plural(len(rows), 'evaluation')}</summary>"
            "<div class='detail-body'><p class='table-caption'>Every evaluation the engine "
            "produced for this household profile.</p><table><thead><tr><th>Item</th>"
            "<th>Result</th><th>Evidence</th><th>Reason</th></tr></thead>"
            f"<tbody>{body}</tbody></table></div></details>")

    return (f"<article class='panel span-12 attention'>{head}"
            f"<div class='attention-body'>{figure}<div>"
            f"<h3>{escape(headline)}</h3><p>{escape(evidence_summary)}</p>"
            f"<p>{escape(engine_note)}</p>"
            f"<p class='tier-note'>{tier_note}</p>"
            "</div></div>"
            f"<p class='attention-caveat'>{caveat}</p>"
            f"{_state_legend()}"
            f"{disclosure}</article>")


def _status_line(a: dict[str, Any]) -> str:
    """One persistent line above every section: the dietary state, in words."""
    if not (a.get("dietary_profiles") or []):
        return ("<p class='masthead-status quiet'>No dietary profile configured. "
                "Dietary checks are off until you add one.</p>")
    verdict = _dietary_verdict(a)
    total = verdict["total"]
    if verdict["blocked"]:
        return (f"<p class='masthead-status alert'>{verdict['blocked']} of {total} "
                f"{_plural(total, 'item is', 'items are')} blocked by your household "
                "dietary restrictions. <span class='status-note'>See Needs attention "
                "today.</span></p>")
    if verdict["open"]:
        return (f"<p class='masthead-status warn'>{verdict['open']} of {total} "
                f"{_plural(total, 'item is', 'items are')} unverified. "
                "<span class='status-note'>Dietary evidence needs attention before you "
                "shop.</span></p>")
    return (f"<p class='masthead-status clear'>All {total} "
            f"{_plural(total, 'item is', 'items are')} cleared against current dietary "
            "evidence.</p>")


# --- one action ---------------------------------------------------------

def _source_label(value: object) -> str:
    raw = str(value or "No source recorded")
    return SOURCE_LABELS.get(raw.strip().lower(), raw)


def _dietary_context(a: dict[str, Any]) -> dict[str, Any]:
    """Existing dietary fields, copied for the downloadable draft."""
    verdict = _dietary_verdict(a)
    rows = []
    for item in a.get("items") or []:
        name = str(item.get("name") or "")
        evaluation = verdict["by_item"].get(name)
        result = _explicit_result((evaluation or {}).get("result"))
        evidence = str((evaluation or {}).get("evidence_status") or "none")
        cleared = result == "safe" and evidence == "current"
        rows.append({
            "item": name,
            "result": result or "not_evaluated",
            "cleared": cleared,
            "evidence_status": evidence,
            "reason": str((evaluation or {}).get("reason")
                          or "No dietary evaluation on file."),
        })
    restrictions = [
        {"value": restriction.get("value") or restriction.get("type"),
         "safety_tier": restriction.get("safety_tier") or "preference",
         "behavior": restriction.get("behavior") or "warn"}
        for profile in a.get("dietary_profiles") or []
        for restriction in profile.get("restrictions") or []
    ]
    return {
        "items_total": verdict["total"],
        "items_not_cleared": verdict["open"],
        "items_cleared": verdict["cleared"],
        "headline": ("No item has been cleared as safe for your household diet."
                     if verdict["open"] else
                     "Every item is cleared against current dietary evidence."
                     if verdict["total"] else "No items to evaluate."),
        "restrictions": restrictions,
        "items": rows,
        "note": ("Dietary state is copied from the engine. A warning or an absent "
                 "evaluation is not a clearance."),
    }


def _draft_payload(a: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    draft = json.loads(json.dumps(plan))
    draft["presentation"] = {
        "schema": "grocery-flywheel.dashboard-draft/1",
        "note": ("Download-only draft. Nothing is bought and nothing is written back "
                 "to your state file."),
        "dietary_context": _dietary_context(a),
    }
    return draft


def _cart_plan(a: dict[str, Any]) -> str:
    plan = a.get("cart_plan") or {}
    items = plan.get("items") or []
    head = _section_head(
        "Today &middot; one thing",
        f"{len(items)} {_plural(len(items), 'item')} &middot; every one needs your approval",
    )
    note = ("<p class='approve-note'>Everything needs your approval. "
            "No checkout surface exists.</p>")
    if not items:
        return (f"<article class='panel span-12 today'>{head}"
                "<h3 class='card-headline'>No cart plan yet.</h3>"
                f"{note}<p class='lede'>Add sourcing research or deplete an item, then "
                "render this page again.</p></article>")

    verdict = _dietary_verdict(a)
    items_by_name = {str(row.get("name")): row for row in a.get("items") or []}
    rows = []
    for index, item in enumerate(items, 1):
        reason = str(item.get("reason") or "").strip() or "No reason recorded by the engine."
        source = _source_label(item.get("source"))
        action = _label(ACTION_LABELS, item.get("action"))
        name = str(item.get("item") or "")
        row = items_by_name.get(name) or {}
        evaluation = verdict["by_item"].get(name)
        rows.append(
            f"<li><span class='action-num'>{index:02d}</span>"
            f"<span class='action-item'>{escape(name)}"
            f"<span class='action-why'>{escape(reason)}</span>"
            f"<span class='action-diet'><span class='eyebrow-inline'>Dietary</span> "
            f"{_dietary_mark(row.get('dietary_status'), evaluation)}</span></span>"
            f"<span class='action-source'>{escape(action)}"
            f"<br>{escape(source)}</span></li>")
    draft = _draft_payload(a, plan)
    export = ("<button class='primary' id='buy-list-download' type='button' data-plan='"
              + escape(json.dumps(draft, sort_keys=True), quote=True) + "'>Download draft JSON</button>"
              "<script>document.getElementById('buy-list-download').addEventListener('click', function () {"
              "var url = URL.createObjectURL(new Blob([this.dataset.plan], {type:'application/json'}));"
              "var link = document.createElement('a'); link.href = url; link.download = 'buy-list.json';"
              "document.body.appendChild(link); link.click(); link.remove();"
              "setTimeout(function () { URL.revokeObjectURL(url); }, 1000);});</script>"
              "<span class='section-note'>A .json file you can read or print, including the "
              "dietary state above. Nothing is bought, and nothing is written back to your "
              "state file.</span>")

    freshness = a.get("freshness") or {}
    stale = int(freshness.get("stale_count") or 0)
    priced = int(freshness.get("fresh_count") or 0)
    price_note = (f"{stale} of {len(a.get('items') or [])} stale or unpriced"
                  if len(a.get("items") or []) else "no prices on file")
    if priced and not stale:
        price_note = f"all {priced} priced recently"
    approval = _label(APPROVAL_LABELS, (items[0] or {}).get("approval_state"))
    meta = (f"Mode <b>{escape(humanize_key(plan.get('mode') or 'pickup'))}</b> &middot; "
            f"approval required before anything is bought: <b>yes</b> &middot; "
            f"checkout available: <b>no</b> &middot; prices behind these numbers are "
            f"<b>{escape(price_note)}</b> &middot; every item is <b>{escape(approval)}</b>.")
    return (f"<article class='panel span-12 today'>{head}"
            f"<h3 class='card-headline'>Review {len(items)} "
            f"{_plural(len(items), 'item')} before your next shop.</h3>"
            "<p class='lede'>Nothing here is bought for you. There is no checkout, no "
            "retailer login and no basket to send — this list is yours to take to the "
            "shelf.</p>"
            f"<ul class='action-list'>{''.join(rows)}</ul>"
            f"<div class='btn-row'>{export}</div>"
            f"{note}<p class='today-meta'>{meta}</p></article>")


# --- runway -------------------------------------------------------------

def _runway_text(a: dict[str, Any]) -> str:
    remaining = a.get("estimated_days_remaining")
    return f"{_days(remaining)} days remaining" if remaining is not None else "Not enough depletion data"


def _ruler(a: dict[str, Any]) -> str:
    remaining = a.get("estimated_days_remaining")
    if remaining is None:
        return ""
    elapsed = max(0.0, float(a.get("days_elapsed") or 0))
    total = elapsed + float(remaining)
    if total <= 0:
        return ""
    ticks = max(1, min(60, math.ceil(total)))
    filled = min(ticks, max(0, round(elapsed / total * ticks)))
    cell, gap = 18, 3
    width = ticks * (cell + gap) - gap
    rects = []
    for index in range(ticks):
        x = index * (cell + gap)
        if index < filled:
            paint = "fill='var(--ink)' stroke='var(--ink)'"
        else:
            paint = "fill='none' stroke='var(--edge-strong)'"
        rects.append(f"<rect x='{x}' y='10' width='{cell}' height='26' rx='2' "
                     f"{paint} stroke-width='1'/>")
    marker = filled * (cell + gap) - gap / 2
    label = (f"Runway ruler: {_days(elapsed)} days observed, "
             f"{_days(remaining)} days remaining.")
    return (f"<div class='ruler'><svg viewBox='0 0 {width} 46' role='img' "
            f"preserveAspectRatio='xMidYMid meet' aria-label='{escape(label)}'>"
            f"{''.join(rects)}"
            f"<line x1='{marker}' y1='4' x2='{marker}' y2='42' "
            "stroke='var(--copper)' stroke-width='2'/></svg>"
            "<div class='legend'>"
            "<span class='legend-item'><span class='legend-swatch filled'></span>"
            f"Days since the order — {_days(elapsed)} elapsed</span>"
            "<span class='legend-item'><span class='legend-swatch outline'></span>"
            f"Days of runway left — {_days(remaining)}</span>"
            "<span class='legend-item'><span class='legend-swatch marker'></span>Today</span>"
            "</div></div>")


def _at_risk(a: dict[str, Any]) -> str:
    rows = [item for item in a.get("items") or []
            if float(item.get("consumed_fraction") or 0) >= 0.5]
    if not rows:
        return "<p class='muted'>No item has passed half of its observed life yet.</p>"
    rows.sort(key=lambda item: float(item.get("consumed_fraction") or 0), reverse=True)
    body = "".join(
        f"<tr><td>{escape(str(item['name']))}</td>"
        f"<td data-role='{escape(str(item.get('role') or ''))}'>{escape(_role(item.get('role')))}</td>"
        f"<td>{float(item.get('consumed_fraction') or 0) * 100:.0f}%</td>"
        f"<td>{_bar(float(item.get('consumed_fraction') or 0))}</td>"
        f"<td>{_money(item.get('spend'))}</td>"
        f"<td>{escape(str(item.get('notes') or 'No note recorded.'))}</td></tr>"
        for item in rows
    )
    return ("<p class='table-caption'>Items at or past half their observed life.</p>"
            "<table><thead><tr><th>Item</th><th>Role</th><th>Consumed</th><th>Drawn down</th>"
            "<th>Spend</th><th>Note</th></tr></thead>"
            f"<tbody>{body}</tbody></table>")


def _runway_math(a: dict[str, Any]) -> str:
    """Runway arithmetic, deliberately quieter than the attention figure."""
    order = a.get("order") or {}
    total = float(order.get("total") or 0)
    consumed = float(a.get("consumed_value") or 0)
    share = a.get("known_consumed_fraction") or 0
    remaining = a.get("estimated_days_remaining")
    runway = (f"{_days(remaining)} days" if remaining is not None
              else "No estimate")
    runway_note = ("Based on observed depletion, not a pantry audit."
                   if remaining is not None else "Not enough depletion data yet.")
    return (
        "<div class='runway-math'>"
        f"<div><span class='math-label'>Observed depletion</span>"
        f"<span class='math-value'>{_money(consumed)}</span>"
        f"<span class='math-label'>{float(share) * 100:.1f}% of order value observed consumed</span></div>"
        f"<div><span class='math-label'>Estimated runway</span>"
        f"<span class='math-value'>{escape(runway)}</span>"
        f"<span class='math-label'>{escape(runway_note)}</span></div>"
        f"<div><span class='math-label'>Order total</span>"
        f"<span class='math-value'>{_money(total)}</span>"
        f"<span class='math-label'>{int(a.get('days_elapsed') or 0)} "
        f"{_plural(int(a.get('days_elapsed') or 0), 'day')} since the order</span></div>"
        "</div>")


def _metrics(a: dict[str, Any]) -> str:
    return f"<article class='panel span-12'>{_runway_math(a)}</article>"


def _runway(a: dict[str, Any]) -> str:
    remaining = a.get("estimated_days_remaining")
    elapsed = max(0.0, float(a.get("days_elapsed") or 0))
    total = elapsed + float(remaining) if remaining is not None else None
    order_total = float((a.get("order") or {}).get("total") or 0)
    tracked = sum(float(item.get("spend") or 0) for item in a.get("items") or [])
    unattributed = round(order_total - tracked, 2)
    consumed = float(a.get("consumed_value") or 0)
    share = (consumed / order_total * 100) if order_total else 0.0
    head = _section_head("What will run out",
                         "Estimate from observed depletion, not a pantry audit")
    if remaining is None:
        return (f"<article class='panel span-12 runway'>{head}"
                "<h3>Not enough depletion data for a runway estimate.</h3>"
                "<p class='muted'>Depletion pulses are needed before this page can say "
                "how many days of cover are left.</p>"
                f"{_runway_math(a)}</article>")
    basis = (
        "<p class='basis-note'><b>How this is estimated:</b> the full order total "
        f"({_money(order_total)}), including {_money(unattributed)} not attributed to a "
        f"tracked item, spread dollar-weighted over {_days(elapsed)} observed "
        f"{_plural(int(elapsed) or 1, 'day')}. It is not a pantry audit.</p>")
    caption = (
        "<div class='ruler-caption'>"
        f"<span><b>{_days(elapsed)} days</b> observed since "
        f"{escape(human_date((a.get('order') or {}).get('date')))}</span>"
        f"<span><b>{_days(remaining)} days</b> of runway left of an estimated "
        f"{_days(total)}</span>"
        f"<span><b>{_money(consumed)}</b> of {_money(order_total)} seen consumed "
        f"({share:.0f}%)</span></div>")
    return (f"<article class='panel span-12 runway'>{head}"
            f"{basis}{_ruler(a)}{caption}{_at_risk(a)}{_runway_math(a)}</article>")


# --- ledger -------------------------------------------------------------

def _evidence_drawer(item: dict[str, Any]) -> str:
    rows = item.get("product_evidence") or []
    if not rows:
        return "<span class='mark neutral'>No label evidence</span>"
    parts = []
    for row in rows:
        label = (f"{humanize_key(row.get('evidence_type', 'evidence'))} · "
                 f"{row.get('source', '')} · {human_date(row.get('checked_date'))}")
        content = ", ".join(
            str(part) for field in ("ingredients", "allergen_statements", "certifications")
            for part in (row.get(field) or [])[:4]
        )
        parts.append(f"<details><summary>{escape(label)}</summary>"
                     f"<p class='muted'>{escape(content)}</p></details>")
    return "".join(parts)


def _dietary_mark(status: object, evaluation: dict[str, Any] | None = None) -> str:
    """Fail-closed mark: Cleared needs an explicit safe result with current evidence."""
    raw = _explicit_result(status)
    evidence = str((evaluation or {}).get("evidence_status") or "").strip()
    if not raw:
        return ("<span class='mark neutral' data-raw-status='not_evaluated'>Not evaluated</span>"
                "<span class='mark-detail'>No dietary evaluation on file</span>")
    if raw == "safe" and (evaluation is None or evidence != "current"):
        detail = ("Current evidence missing" if evaluation is not None
                  else "No dietary evaluation on file")
        return ("<span class='mark neutral' data-raw-status='not_evaluated'>Not evaluated</span>"
                f"<span class='mark-detail'>{escape(detail)}</span>")
    css = RESULT_CLASS.get(raw, "neutral")
    detail = _label(EVIDENCE_LABELS, evidence) if evaluation is not None and evidence else ""
    detail_html = (f"<span class='mark-detail'>{escape(detail)}</span>" if detail else "")
    return (f"<span class='mark {css}' data-raw-status='{escape(raw)}'>"
            f"{escape(_label(RESULT_LABELS, raw))}</span>{detail_html}")


def _price_label(status: str, stale: bool) -> tuple[str, str]:
    if status == "unpriced":
        return ("No price captured", "neutral")
    if status == "estimated":
        return ("Estimated price", "warn")
    if status == "gift":
        return ("Gift — price optional", "neutral")
    if stale:
        return ("Stale price on file", "warn")
    return ("Priced", "ok")


def _price_state(item: dict[str, Any], fresh: dict[str, Any] | None) -> tuple[str, str, str]:
    """One price vocabulary for ledger, freshness panel and action list."""
    if fresh:
        status = str(fresh.get("pricing_status") or "priced")
        stale = bool(fresh.get("pricing_stale"))
        detail = str(fresh.get("age_label") or "")
        if status == "unpriced":
            detail = ""
        elif status == "estimated":
            detail = "low confidence"
        elif status == "gift":
            detail = ""
    else:
        status = str(item.get("pricing_status") or "").strip()
        if not status:
            return ("No price captured", "neutral", "")
        stale = False
        detail = ""
    label, css = _price_label(status, stale)
    return (label, css, detail)


def _price_mark(item: dict[str, Any], fresh: dict[str, Any] | None) -> str:
    label, css, detail = _price_state(item, fresh)
    detail_html = (f"<span class='mark-detail'>{escape(detail)}</span>" if detail else "")
    raw = str((fresh or {}).get("pricing_status") or item.get("pricing_status") or "")
    attr = f" data-raw-price='{escape(raw)}'" if raw else ""
    return (f"<span class='mark {css}'{attr}>{escape(label)}</span>{detail_html}")


def _freshness_map(a: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = (a.get("freshness") or {}).get("items") or []
    return {str(row.get("name") or ""): row for row in rows}


def _items(a: dict[str, Any]) -> str:
    items = a.get("items") or []
    order = a.get("order") or {}
    order_total = float(order.get("total") or 0)
    tracked = sum(float(item.get("spend") or 0) for item in items)
    unattributed = round(order_total - tracked, 2)
    consumed = float(a.get("consumed_value") or 0)
    head = _section_head(
        "The ledger",
        f"{len(items)} {_plural(len(items), 'item')} &middot; {_money(order_total)} "
        f"&middot; {_money(consumed)} consumed",
    )
    if not items:
        return (f"<article class='panel span-12 ledger'>{head}"
                "<p class='muted'>No items in the ledger yet.</p></article>")
    verdict = _dietary_verdict(a)
    fresh = _freshness_map(a)
    results = {_explicit_result((verdict["by_item"].get(str(item.get("name"))) or {})
                                .get("result")) for item in items}
    caption = ("Every item the engine holds, with price state, dietary state and "
               "product evidence.")
    if results == {""}:
        caption += (" No item has a dietary evaluation on file; “Not evaluated” is "
                    "not a clearance.")
    elif len(results) == 1:
        only = next(iter(results))
        caption += (f" All {len(items)} items share the same dietary result "
                    f"({_label(RESULT_LABELS, only)}); the attention panel explains why.")
    body = "".join(
        f"<tr><td><span class='ledger-item'>{escape(str(item['name']))}</span>"
        f"<span class='cell-sub'>{escape(_role(item.get('role')))} &middot; "
        f"{escape(humanize_key(item.get('category') or ''))}</span></td>"
        f"<td>{_money(item.get('spend'))}"
        f"<span class='cell-sub'>{float(item.get('consumed_fraction') or 0) * 100:.0f}% consumed</span></td>"
        f"<td>{_price_mark(item, fresh.get(str(item.get('name'))))}</td>"
        f"<td>{_dietary_mark(item.get('dietary_status'), verdict['by_item'].get(str(item.get('name'))))}</td>"
        f"<td>{_evidence_drawer(item)}</td></tr>"
        for item in items
    )
    reconcile = (
        f"<p class='reconcile'>Order total <b>{_money(order_total)}</b>; the {len(items)} "
        f"{_plural(len(items), 'item')} tracked above account for <b>{_money(tracked)}</b>. "
        f"<b>{_money(unattributed)}</b> of the order total is not attributed to any "
        "tracked item, so totals and runway are estimates, not a reconciliation.</p>")
    return (f"<article class='panel span-12 ledger'>{head}"
            f"<p class='table-caption'>{escape(caption)}</p>"
            "<table><thead><tr><th>Item</th><th>Spend</th><th>Price</th>"
            "<th>Dietary</th><th>Product evidence</th></tr></thead>"
            f"<tbody>{body}</tbody></table>{reconcile}</article>")


# --- supporting panels (progressive disclosure) -------------------------

def _first_wow(a: dict[str, Any]) -> str:
    wow = a.get("first_wow") or {}
    savings = float(wow.get("estimated_unit_savings", 0) or 0)
    if savings > 0:
        savings_value = _money(savings)
        savings_note = ("Sum of the per-unit savings in the engine's sourcing and "
                        "substitution rows.")
    else:
        savings_value = "None recorded"
        savings_note = ("The engine's sourcing rows record no per-unit saving to sum; "
                        "this is not a $0.00 claim about the order.")
    return f"""
      <article class="panel">
        <h2>Savings and sourcing</h2>
        <div class="card-row">
          <div><h3 class="stat-label">Recorded unit savings</h3>
            <div class="metric">{escape(savings_value)}</div>
            <p class="muted stat-note">{escape(savings_note)}</p></div>
          <div><h3 class="stat-label">Best sourcing move</h3>
            <div class="metric small">{escape(str(wow.get('best_sourcing_move', '—')))}</div></div>
          <div><h3 class="stat-label">Runway</h3>
            <div class="metric small">{escape(_runway_text(a))}</div></div>
        </div>
        <p class="muted">{escape(str(wow.get('headline', '')))}</p>
      </article>"""


def _role_summary(a: dict[str, Any]) -> str:
    body = "\n".join(
        f"<tr><td>{escape(_role(r['role']))}</td><td>{_money(r['spend'])}</td>"
        f"<td>{_money(r['consumed'])}</td><td>{_bar(r['consumed_fraction'])}</td></tr>"
        for r in a.get("role_summary", [])
    )
    return ("<article class='panel span-6'><h2>Role Summary</h2>"
            "<table><thead><tr><th>Role</th><th>Spend</th><th>Consumed</th><th>Drawdown</th></tr></thead>"
            f"<tbody>{body}</tbody></table></article>")


def _preferences(a: dict[str, Any]) -> str:
    rows = a.get("preferences", [])
    if not rows:
        return "<article class='panel span-6'><h2>Preference Signals</h2><p class='muted'>No preference signals yet.</p></article>"
    body = "".join(
        f"<p><strong>{escape(humanize_key(r['key']))}</strong><br>{escape(r.get('signal', ''))}<br>"
        f"<span class='muted'>{escape(r.get('rule', ''))}</span></p>"
        for r in rows
    )
    return f"<article class='panel span-6'><h2>Preference Signals</h2>{body}</article>"


def _easy_food(a: dict[str, Any]) -> str:
    summary = a.get("easy_food") or {}
    if not summary or summary.get("count", 0) == 0:
        return ("<article class='panel span-6'><h2>Easy Food</h2>"
                "<p class='muted'>No unopened top-ups in the easy-food window.</p></article>")
    items = "".join(
        f"<li><strong>{escape(str(r['name']))}</strong> "
        f"({escape(_role(r['role']))}, {escape(str(r['age_label']))}) — "
        "rotate into a meal before the next top-up duplicates it.</li>"
        for r in summary["items"]
    )
    count = int(summary["count"])
    return (f"<article class='panel span-6'><h2>Easy Food</h2>"
            f"<p><strong>{count}</strong> unopened {_plural(count, 'top-up')}:</p>"
            f"<ul>{items}</ul></article>")


def _freshness(a: dict[str, Any]) -> str:
    summary = a.get("freshness")
    if not summary:
        return ("<article class='panel span-12'><h2>Data Freshness</h2>"
                "<p class='muted'>No freshness data.</p></article>")
    parts = [f"<p><b>{summary.get('fresh_count', 0)}</b> priced recently, "
             f"<b>{summary.get('stale_count', 0)}</b> stale or unpriced.</p>"]
    flagged = []
    for row in summary.get("items", []):
        if not row.get("pricing_stale"):
            continue
        label, _css = _price_label(str(row.get("pricing_status") or "priced"), True)
        flagged.append(f"{escape(row['name'])} — {escape(label)} "
                       f"({escape(row['age_label'])})")
    if flagged:
        parts.append("<p><strong>Flagged items:</strong> " + ", ".join(flagged) + "</p>")
    stale_sourcing = [f"{escape(r['item'])} ({escape(r['age_label'])})"
                      for r in summary.get("stale_sourcing", [])]
    if stale_sourcing:
        parts.append("<p><strong>Stale sourcing research:</strong> " + ", ".join(stale_sourcing) + "</p>")
    parts.append("<p class='muted'>One price vocabulary across this page: Priced, "
                 "Stale price on file, No price captured, Estimated price, Gift.</p>")
    return ("<article class='panel span-12'><h2>Data Freshness</h2>"
            + "".join(parts) + "</article>")


def _trips(a: dict[str, Any]) -> str:
    summary = a.get("visits_summary") or {}
    if not summary or summary.get("visit_count", 0) == 0:
        return ("<article class='panel span-6'><h2>Trip Overhead</h2>"
                "<p class='muted'>No visits recorded yet. Use <code>capture-visit</code> to log a trip.</p></article>")
    by_type = summary.get("by_type", {}) or {}
    by_type_min = summary.get("by_type_minutes", {}) or {}
    count = int(summary["visit_count"])
    lines = [f"<p><strong>{count}</strong> {_plural(count, 'visit')}, "
             f"<strong>{summary.get('total_minutes', 0)}</strong> minutes total.</p>"]
    if by_type:
        items = ", ".join(
            f"{escape(humanize_key(t))}: {by_type[t]} ({by_type_min.get(t, 0)} min)"
            for t in sorted(by_type))
        lines.append("<p class='muted'>By type — <span data-visit-types='"
                     f"{escape(', '.join(sorted(by_type)))}'>{items}</span>.</p>")
    amortized = summary.get("amortized_cost_total", 0.0)
    lines.append(
        f"<p>Amortized time cost: <strong>{_money(amortized)}</strong></p>" if amortized
        else "<p class='muted'>Set an hourly value in the state to see amortized cost.</p>"
    )
    return "<article class='panel span-6'><h2>Trip Overhead</h2>" + "".join(lines) + "</article>"


def _substitutions(a: dict[str, Any]) -> str:
    rows = a.get("substitutions", [])
    if not rows:
        return ("<article class='panel span-6'><h2>Substitutions</h2>"
                "<p class='muted'>No substitution candidates yet.</p></article>")
    body = "\n".join(
        f"<tr><td>{escape(r['candidate'])}</td><td>{escape(r['current'])}</td>"
        f"<td>{_money(r.get('candidate_unit_price'))}</td>"
        f"<td>{escape(humanize_key(r.get('fit', '')))}</td>"
        f"<td>{_dietary_mark(r.get('dietary_status'))}</td>"
        f"<td>{escape(r.get('read', ''))}</td></tr>"
        for r in rows
    )
    return ("<article class='panel span-6'><h2>Substitutions</h2>"
            "<p class='table-caption'>Candidate substitutes from your state. "
            "“Not evaluated” means no dietary evaluation exists for the candidate; "
            "it is not a clearance.</p>"
            "<table><thead><tr><th>Candidate</th><th>Replaces</th><th>Unit</th><th>Fit</th>"
            "<th>Dietary</th><th>Read</th></tr></thead>"
            f"<tbody>{body}</tbody></table></article>")


def _sourcing(a: dict[str, Any]) -> str:
    rows = a.get("sourcing_research", [])
    if not rows:
        return ("<article class='panel span-6'><h2>Sourcing Research</h2>"
                "<p class='muted'>No sourcing research yet.</p></article>")
    body = []
    for row in rows:
        alternatives = row.get("alternatives", [])
        best = alternatives[0] if alternatives else {}
        body.append(
            f"<tr><td>{escape(row['item'])}</td><td>{escape(row.get('current_source', ''))}</td>"
            f"<td>{escape(best.get('source', ''))}</td><td>{_money(best.get('unit_price'))}</td>"
            f"<td>{escape(str(best.get('savings', '')))}</td>"
            f"<td>{escape(row.get('recommendation', ''))}</td></tr>"
        )
    return ("<article class='panel span-6'><h2>Sourcing Research</h2>"
            "<table><thead><tr><th>Item</th><th>Current</th><th>Best alternative</th><th>Unit</th>"
            "<th>Savings</th><th>Read</th></tr></thead><tbody>" + "".join(body) + "</tbody></table></article>")


def _corrections_capture(a: dict[str, Any]) -> str:
    consent = a.get("consent") or {}
    if consent.get("correction_telemetry") not in ("local_only", "hosted_opt_in"):
        return ""
    item_names = [r["name"] for r in a.get("items", [])]
    options = "".join(f"<option>{escape(str(n))}</option>" for n in item_names)
    signals = ("never_again", "buy_elsewhere", "wrong_format", "too_expensive",
               "good_default", "emergency_only")
    buttons = "".join(
        f"<button class='correction' data-signal='{s}' onclick=\"capture('{s}')\">"
        f"{escape(humanize_key(s))}</button>"
        for s in signals
    )
    return f"""
      <article class="panel span-12" id="corrections">
        <h2>Correction Capture</h2>
        <p class="muted">Capture signals in this page only. Download JSONL to keep them; nothing is saved to household state or sent anywhere.</p>
        <p><label for="correction-item">Item to correct</label><br><select id="correction-item">{options}</select></p>
        <p>{buttons}</p>
        <p><button class="correction" id="correction-download" type="button">Download JSONL</button>
        <span class="muted" id="correction-count" role="status"></span></p>
        <script>
          var log = [];
          function capture(signal) {{
            var item = document.getElementById("correction-item").value;
            log.push({{"item": item, "signal": signal, "created_at": new Date().toISOString().slice(0, 10)}});
            document.getElementById("correction-count").textContent = log.length + " captured";
          }}
          document.getElementById("correction-download").addEventListener("click", function () {{
            var blob = new Blob([log.map(function (e) {{ return JSON.stringify(e); }}).join("\\n")], {{type: "application/jsonl"}});
            var url = URL.createObjectURL(blob);
            var link = document.createElement("a");
            link.href = url; link.download = "corrections.jsonl";
            document.body.appendChild(link); link.click(); link.remove();
            setTimeout(function () {{ URL.revokeObjectURL(url); }}, 1000);
          }});
        </script>
      </article>"""


def _pulses(a: dict[str, Any]) -> str:
    rows = a.get("pulses", [])
    if not rows:
        return "<article class='panel span-12'><h2>Recent Pulses</h2><p class='muted'>No pulses yet.</p></article>"
    body = "".join(
        # tolerant field access: some hand-edited states use 'note' (compat fix, 2026-08-14)
        f"<p><span class='tag'>{escape(human_date(r['date']))}</span>"
        f"{escape(r.get('text', r.get('note', '')))}</p>"
        for r in rows[-5:]
    )
    return f"<article class='panel span-12'><h2>Recent Pulses</h2>{body}</article>"


def _bar(fraction: float) -> str:
    pct = max(0, min(100, round(float(fraction) * 100)))
    css = "bar hot" if pct >= 80 else "bar"
    return (f"<span class='{css}' role='img' aria-label='{pct}% consumed'>"
            f"<span style='width:{pct}%'></span></span>")


# --- the registry --------------------------------------------------------

PANELS: list[dict[str, Any]] = [
    _panel("first_wow", "span-12", _first_wow),
    _panel("metrics", "span-12", _metrics),
    _panel("role_summary", "span-6", _role_summary),
    _panel("preferences", "span-6", _preferences),
    _panel("dietary", "span-12", _dietary),
    _panel("easy_food", "span-6", _easy_food),
    _panel("freshness", "span-12", _freshness),
    _panel("trips", "span-6", _trips),
    _panel("cart_plan", "span-12", _cart_plan),
    _panel("items", "span-12", _items),
    _panel("substitutions", "span-6", _substitutions),
    _panel("sourcing", "span-6", _sourcing),
    _panel("corrections_capture", "span-12", _corrections_capture),
    _panel("pulses", "span-12", _pulses),
]

DISCLOSURES: tuple[tuple[str, str], ...] = (
    ("first_wow", "Savings and sourcing overview"),
    ("role_summary", "Spending by household role"),
    ("preferences", "Preference signals"),
    ("freshness", "Price freshness and uncertainty"),
    ("trips", "Trip overhead"),
    ("easy_food", "Easy food rotation"),
    ("substitutions", "Substitution comparisons"),
    ("sourcing", "Sourcing research"),
    ("corrections_capture", "Download-only correction capture"),
    ("pulses", "Recent depletion pulses"),
)


def _responsive_table_labels(document: str) -> str:
    """Retain semantic tables and repeat their trusted headings on narrow records.

    Only panel-generated tags are matched: user text is already HTML-escaped.
    No user content becomes markup or executable data here.
    """
    def table(match: re.Match[str]) -> str:
        markup = match.group(0)
        labels = re.findall(r"<th>(.*?)</th>", markup, re.S)

        def row(match: re.Match[str]) -> str:
            index = 0

            def cell(match: re.Match[str]) -> str:
                nonlocal index
                label = labels[index] if index < len(labels) else ""
                index += 1
                attrs = match.group(1) or ""
                if "data-label" in attrs:
                    return match.group(0)
                return f'<td{attrs} data-label="{escape(label, quote=True)}">'

            return re.sub(r"<td(\s[^>]*)?>", cell, match.group(0))

        return re.sub(r"<tr[^>]*>.*?</tr>", row, markup, flags=re.S)

    return re.sub(r"<table[^>]*>.*?</table>", table, document, flags=re.S)


def render_dashboard(analysis: dict[str, Any]) -> str:
    """Attention, one action, runway, ledger, then every original panel."""
    renderers = {panel["name"]: panel["render"] for panel in PANELS}
    parts = [renderers["dietary"](analysis),
             renderers["cart_plan"](analysis),
             _runway(analysis),
             renderers["items"](analysis)]
    for name, label in DISCLOSURES:
        markup = renderers[name](analysis)
        if markup:
            parts.append(f"<details class='disclosure'><summary>{label}</summary>"
                         f"<div class='disclosure-grid'>{markup}</div></details>")
    return page_shell(header_line(analysis), _status_line(analysis),
                      _responsive_table_labels("\n".join(parts)))
