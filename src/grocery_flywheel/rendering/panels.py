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

``_item_verdict`` is the single dietary authority; every surface — ledger,
action list, substitutions, sourcing, easy food, at-risk table, evidence drawer,
headline counts and the downloaded draft — renders its output and may not infer
a clearance from another field. The page and the download are one action list
computed once (``_action_rows``), so the JSON cannot restock an item the page
holds, and the evidence drawer renders one row per engine evaluation.
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
    "candidate_evidence_current": "Candidate evidence current",
    "candidate_evidence_reviewed": "Candidate evidence reviewed",
    "missing_candidate_evidence": "No candidate evidence",
    "reviewed": "Candidate evidence reviewed",
    "not_required": "Evidence not required by this profile",
}
PRICE_LABELS = {
    "priced": "Priced",
    "unpriced": "No price captured",
    "estimated": "Estimated price",
    "gift": "Gift — price optional",
}
SOURCE_LABELS = {"normal store": "your usual store"}
SEVERITY = {"safe": 0, "warn": 1, "needs_review": 2, "blocked": 3}
BLOCK_BEHAVIOURS = {"block", "block_until_review", "blocked"}
CRITICAL_TIERS = {"critical", "safety_critical", "safety-critical", "allergy", "food_allergy"}
# THE presentation table. One state -> one token, one label, one meaning. Every
# dietary surface renders a verdict from ``_item_verdict``; no surface may derive
# a clearance from an item field of its own choosing (r2/r4/r5 fail-open class).
DIETARY_STATES: dict[str, tuple[str, str, str]] = {
    "blocked": ("missing", "Blocked",
                "Current evidence contradicts a restriction whose behaviour is block."),
    "needs_review": ("missing", "Needs review",
                     "A blocking restriction the engine cannot verify; never cleared."),
    "warning": ("warn", "Warning",
                "A warn-tier restriction. A warning is not a clearance."),
    "cleared": ("ok", "Cleared",
                "An explicit safe result with current evidence."),
    "not_evaluated": ("neutral", "Not evaluated",
                      "No evaluation for this item, or an evaluation that named no "
                      "item on this page."),
}


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
    """Render a recorded amount; a missing amount is never a fabricated $0.00."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return "not recorded"
    try:
        amount = float(str(value))
    except (TypeError, ValueError):
        return "not recorded"
    return f"{'-' if amount < 0 else ''}${abs(amount):.2f}"


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
    """One raw evaluation per item, keeping the most severe result (fail closed)."""
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


def _item_verdict(name: str, evaluation: dict[str, Any] | None) -> dict[str, Any]:
    """THE dietary verdict authority; every surface renders these fields only.

    ``cleared`` is true only for an explicit engine result of ``safe`` whose
    evidence status is ``current``. No caller may derive a clearance from the
    item's own ``dietary_status``, a price field, or a missing value.
    """
    result = _explicit_result((evaluation or {}).get("result"))
    evidence = str((evaluation or {}).get("evidence_status") or "").strip()
    tier = humanize_key((evaluation or {}).get("safety_tier") or "")
    reason = str((evaluation or {}).get("reason") or "").strip()
    if not result:
        state = "not_evaluated"
        detail = ("No dietary evaluation on file" if evaluation is None
                  else "The evaluation has no explicit result")
    elif result == "safe" and evidence != "current":
        state = "not_evaluated"
        detail = "Current evidence missing"
    elif result == "safe":
        state = "cleared"
        detail = " &middot; ".join(
            escape(part) for part in ("Current evidence", f"{tier} tier" if tier else "") if part)
    else:
        state = {"blocked": "blocked", "needs_review": "needs_review"}.get(result, "warning")
        detail = " &middot; ".join(
            escape(part) for part in (_label(EVIDENCE_LABELS, evidence) if evidence else "",
                                      f"{tier} tier" if tier else "") if part)
    token, label, meaning = DIETARY_STATES[state]
    return {
        "item": name, "result": result, "evidence": evidence, "tier": tier,
        "state": state, "token": token, "label": label, "detail": detail,
        "meaning": meaning, "reason": reason, "cleared": state == "cleared",
    }


def _orphan_verdict(evaluation: dict[str, Any]) -> dict[str, Any]:
    """An evaluation that names no item on this page: surfaced, never applied."""
    verdict = _item_verdict(str(evaluation.get("item") or ""), evaluation)
    verdict.update({
        "orphan": True,
        "raw_state": verdict["state"],
        "state": "not_evaluated",
        "token": DIETARY_STATES["not_evaluated"][0],
        "label": DIETARY_STATES["not_evaluated"][1],
        "meaning": DIETARY_STATES["not_evaluated"][2],
        "detail": "Evidence did not match an item on this page",
        "cleared": False,
    })
    return verdict


def _norm_name(value: object) -> str:
    """Case- and whitespace-insensitive key for joining only; never for display."""
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _verdict_for(verdict: dict[str, Any], name: object) -> dict[str, Any]:
    """Look one page name up in the authority; a missing verdict stays neutral."""
    key = str(name or "")
    return (verdict["verdicts"].get(key)
            or verdict["by_norm"].get(_norm_name(key))
            or _item_verdict(key, None))


def _dietary_verdict(analysis: dict[str, Any]) -> dict[str, Any]:
    evaluations = [row for row in (analysis.get("dietary_evaluations") or [])
                   if isinstance(row, dict)]
    items = analysis.get("items") or []
    profiles = analysis.get("dietary_profiles") or []
    page_names = [str(item.get("name") or "") for item in items if str(item.get("name") or "")]
    cart_names = [str(row.get("item") or "")
                  for row in (analysis.get("cart_plan") or {}).get("items") or []
                  if str(row.get("item") or "")]
    # A cart row is a name on the page even when the ledger has no matching item;
    # its evaluation must render there rather than surface as an orphan.
    for name in cart_names:
        if name not in page_names:
            page_names.append(name)
    ledger_norms = {_norm_name(name) for name in
                    (str(item.get("name") or "") for item in items)
                    if name}
    page_norms = {_norm_name(name) for name in page_names}
    # Join on casefolded, whitespace-collapsed names. The engine's own names are
    # never rewritten; only the lookup tolerates drift (r6 M5). An evaluation
    # that names no page item is an orphan: surfaced, never applied.
    by_norm: dict[str, list[dict[str, Any]]] = {}
    for row in evaluations:
        name = str(row.get("item") or "")
        if name and _explicit_result(row.get("result")):
            by_norm.setdefault(_norm_name(name), []).append(row)
    verdicts: dict[str, dict[str, Any]] = {}
    by_norm_verdicts: dict[str, dict[str, Any]] = {}
    for name in page_names:
        rows = by_norm.get(_norm_name(name)) or []
        if not rows:
            continue
        worst = max(rows, key=lambda row: SEVERITY[_explicit_result(row.get("result"))])
        verdict = _item_verdict(name, worst)
        verdicts[name] = verdict
        by_norm_verdicts[_norm_name(name)] = verdict
    orphans = [_orphan_verdict(row) for row in evaluations
               if str(row.get("item") or "")
               and _explicit_result(row.get("result"))
               and _norm_name(row.get("item")) not in page_norms]
    orphans.sort(key=lambda row: (-SEVERITY[_explicit_result(row.get("result"))],
                                  row["item"]))
    ledger_verdicts = [verdicts[name] for name in
                       (str(item.get("name") or "") for item in items)
                       if name in verdicts]
    results = [row["result"] for row in ledger_verdicts]
    counts = Counter(results)
    total = len(items)
    cleared = sum(1 for row in ledger_verdicts if row["cleared"])
    with_current = {row["item"] for row in ledger_verdicts if row["evidence"] == "current"}
    matched_rows = [row for row in evaluations
                    if _explicit_result(row.get("result"))
                    and _norm_name(row.get("item")) in ledger_norms]
    evidence_counts = Counter(row["evidence"] or "missing" for row in ledger_verdicts)
    warn_only = bool(matched_rows) and all(
        _explicit_result(row.get("result")) == "warn" for row in matched_rows)
    tiers = Counter(row["tier"] or "Preference" for row in ledger_verdicts)
    severity = max((SEVERITY[row["result"]] for row in ledger_verdicts), default=0)
    return {
        "evaluations": evaluations, "items": items, "profiles": profiles,
        "verdicts": verdicts, "by_norm": by_norm_verdicts, "page_norms": page_norms,
        "orphans": orphans,
        "total": total, "blocked": counts["blocked"], "needs_review": counts["needs_review"],
        "warn": counts["warn"], "safe": counts["safe"],
        "open": total - cleared, "cleared": cleared,
        "not_evaluated": total - len(ledger_verdicts),
        "evidence_gap": total - len(with_current), "current_items": len(with_current),
        "evidence_counts": evidence_counts, "warn_only": warn_only,
        "tiers": tiers, "severity": severity,
        "blocking": severity >= SEVERITY["needs_review"],
    }


def _verdict_parts(verdict: dict[str, Any], separator: str = " &middot; ") -> str:
    """Exact per-state counts; never an absolute claim over a mixed page."""
    parts: list[str] = []
    if verdict["total"]:
        parts.append(f"{verdict['cleared']} of {verdict['total']} cleared")
    if verdict["blocked"]:
        parts.append(f"{verdict['blocked']} blocked")
    if verdict["needs_review"]:
        count = verdict["needs_review"]
        parts.append(f"{count} {'needs' if count == 1 else 'need'} review")
    if verdict["warn"]:
        count = verdict["warn"]
        parts.append(f"{count} {_plural(count, 'warning')}")
    unverified_safe = verdict["safe"] - verdict["cleared"]
    if unverified_safe:
        parts.append(f"{unverified_safe} with evidence not current")
    if verdict["not_evaluated"]:
        parts.append(f"{verdict['not_evaluated']} not evaluated")
    return separator.join(parts)


def _verdict_headline(verdict: dict[str, Any]) -> str:
    total = verdict["total"]
    if not total:
        return "No items to evaluate yet."
    if verdict["blocked"]:
        count = verdict["blocked"]
        return (f"{count} {_plural(count, 'item is', 'items are')} blocked by your "
                "household dietary restrictions.")
    if verdict["cleared"] == total:
        return (f"All {total} {_plural(total, 'item is', 'items are')} cleared against "
                "current dietary evidence.")
    if verdict["cleared"]:
        remaining = total - verdict["cleared"]
        return (f"{verdict['cleared']} of {total} "
                f"{_plural(total, 'item is', 'items are')} cleared; {remaining} "
                f"{_plural(remaining, 'item is', 'items are')} not cleared.")
    return "No item has been cleared as safe for your household diet."


def _state_legend() -> str:
    body = "".join(
        f"<div><dt><span class='mark {DIETARY_STATES[key][0]}'>{escape(DIETARY_STATES[key][1])}</span></dt>"
        f"<dd>{escape(DIETARY_STATES[key][2])}</dd></div>"
        for key in ("blocked", "needs_review", "warning", "cleared", "not_evaluated"))
    return f"<dl class='state-legend'>{body}</dl>"


def _restriction_context(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    """Behaviour and severity of the configured restrictions, verbatim fields."""
    rows: list[str] = []
    behaviours: set[str] = set()
    tiers: set[str] = set()
    for profile in profiles:
        for restriction in profile.get("restrictions") or []:
            value = humanize_key(restriction.get("value") or restriction.get("type") or "")
            tier_raw = str(restriction.get("safety_tier") or "preference").strip().lower()
            behaviour_raw = str(restriction.get("behavior") or "warn").strip().lower()
            tiers.add(tier_raw)
            behaviours.add(behaviour_raw)
            rows.append(f"{value} (safety tier: {humanize_key(tier_raw)}; "
                        f"behaviour: {humanize_key(behaviour_raw)})")
    blocking = bool(behaviours & BLOCK_BEHAVIOURS) or bool(tiers & CRITICAL_TIERS)
    return {
        "text": "; ".join(rows) or "none recorded",
        "behaviours": behaviours, "tiers": tiers, "blocking": blocking,
        "warn_behaviour": bool(behaviours) and behaviours <= {"warn", "review", "needs_review"},
    }


def _action_plan(a: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Cart-plan rows, plus every blocked item the cart plan does not already name.

    The action area is one surface, so it must carry every blocked item even when
    the engine's cart plan has no row for it. Both lists render through the same
    verdict authority; no caller re-derives a state.
    """
    items = list((a.get("cart_plan") or {}).get("items") or [])
    verdict = _dietary_verdict(a)
    in_plan = {str(item.get("item") or "") for item in items}
    held = [row for row in verdict["verdicts"].values()
            if row["state"] == "blocked" and row["item"] not in in_plan]
    held.sort(key=lambda row: row["item"])
    return items, held, verdict


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
    restriction = _restriction_context(profile_rows)
    restriction_text = restriction["text"]

    headline = _verdict_headline(verdict)
    counts_text = _verdict_parts(verdict)
    counts_html = f"<p class='attention-counts'>{counts_text}</p>" if counts_text else ""
    if open_items:
        caption = "items blocked or not cleared" if verdict["blocked"] else "items unverified"
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
    if verdict["warn_only"] and open_items:
        engine_note = ("This household's restriction is configured to warn, so the engine "
                       "returns a warning for every item and clears none of them.")
    elif restriction["blocking"]:
        engine_note = ("This household's restriction is set to block: an item whose current "
                       "evidence matches it is returned as Blocked, and an item the engine "
                       "cannot verify is returned as Needs review — never as cleared.")
    else:
        engine_note = ("The engine clears an item only when current label evidence rules the "
                       "restriction out; a warning is not a clearance.")
    if verdict["evidence_gap"] and restriction["blocking"]:
        qualifier = ("Missing evidence is treated as not cleared: the engine never clears an "
                     "item it cannot verify.")
    elif verdict["evidence_gap"]:
        qualifier = "Missing evidence is a data gap, not proof of a safety failure."
    else:
        qualifier = ""
    qualifier_html = (f"<p class='attention-qualifier'>{escape(qualifier)}</p>"
                      if qualifier else "")
    orphan_note = ""
    if verdict["orphans"]:
        count = len(verdict["orphans"])
        orphan_note = (
            f"<p class='attention-qualifier'>{count} "
            f"{_plural(count, 'evaluation names', 'evaluations name')} an item not on this "
            "page and could not be applied; shown below as not evaluated. Check for a "
            "renamed or deleted item.</p>")
    if restriction["blocking"]:
        restriction_note = (
            f"<p><b>Restriction:</b> {escape(restriction_text)}. Block behaviour: matching "
            "evidence stops an item, and an item the engine cannot verify is never cleared.</p>")
    else:
        restriction_note = (
            f"<p><b>Restriction:</b> {escape(restriction_text)}. The engine flags every item "
            "it cannot clear; a warning is never a safety verdict.</p>")
    profile_note = (
        f"<p><b>Profile:</b> {profiles}. When evidence is missing this dashboard cannot "
        "tell you that anything is safe.</p>")
    context_html = (
        f"<details class='attention-context'><summary>Restriction and profile</summary>"
        f"<div class='detail-body'>{restriction_note}{profile_note}</div></details>")
    notes = f"<p>{escape(engine_note)}</p>{context_html}"
    panel_class = ("attention" if verdict["blocking"]
                   else "attention warn-tier" if open_items else "attention quiet")
    tier_note = ("blocked" if verdict["blocking"]
                 else "warning tier" if open_items else "cleared")
    head = _section_head("Needs attention today", f"Dietary evidence &middot; {tier_note}")

    action_rows, _action_verdict = _action_rows(a)
    jump_html = ""
    if action_rows:
        open_actions = sum(1 for row in action_rows if not row["cleared"])
        if open_actions:
            label = (f"Review the {open_actions} "
                     f"{_plural(open_actions, 'item')} that need a decision")
        else:
            label = (f"Review the {len(action_rows)} "
                     f"{_plural(len(action_rows), 'item')} before you shop")
        jump_html = (f"<a class='jump-link' href='#today'>{label}"
                     "<span aria-hidden='true'> &darr;</span></a>")

    rows = sorted(
        verdict["evaluations"],
        key=lambda row: (-SEVERITY.get(_explicit_result(row.get("result")), -1),
                         str(row.get("item") or "")))

    def evidence_row(row: dict[str, Any]) -> str:
        name = str(row.get("item") or "")
        orphan = _norm_name(name) not in verdict["page_norms"]
        own = _orphan_verdict(row) if orphan else _item_verdict(name, row)
        reason = row.get("reason") or "No reason recorded by the engine."
        if orphan:
            reason = (f"Could not be applied: engine result "
                      f"{_label(RESULT_LABELS, row.get('result'))}. {reason}")
        orphan_attr = " data-orphan='true'" if orphan else ""
        evidence = row.get("evidence_status")
        evidence_label = _label(EVIDENCE_LABELS, evidence) if evidence else "No evidence on file"
        return (f"<tr{orphan_attr}><td>{escape(name or 'Unnamed item')}</td>"
                f"<td data-raw-result='{escape(str(row.get('result') or ''))}'>"
                f"{escape(own['label'])}"
                f"<span class='mark-detail'>{own['detail']}</span></td>"
                f"<td data-raw-evidence='{escape(str(evidence or ''))}'>"
                f"{escape(evidence_label)}</td>"
                f"<td>{escape(reason)}</td></tr>")

    body = "".join(evidence_row(row) for row in rows)
    disclosure = ""
    if body:
        count = len(rows)
        disclosure = (
            f"<details class='evidence'><summary>See the evidence and the five-state "
            f"legend — {count} dietary {_plural(count, 'evaluation')}</summary>"
            "<div class='detail-body'><p class='table-caption'>Every evaluation the engine "
            "produced for this household profile, one row per evaluation. An item with more "
            "than one restriction can appear more than once; the item's badge uses the most "
            "severe result. An evaluation that names no item on this page is marked not "
            "evaluated; it never clears a row.</p>"
            "<table><colgroup><col style='width:26%'><col style='width:22%'>"
            "<col style='width:18%'><col style='width:34%'></colgroup>"
            "<thead><tr><th>Item</th>"
            "<th>Result</th><th>Evidence</th><th>Reason</th></tr></thead>"
            f"<tbody>{body}</tbody></table>{_state_legend()}</div></details>")

    return (f"<article class='panel span-12 {panel_class}'>{head}"
            f"<div class='attention-body'>{figure}"
            f"<div class='attention-verdict'><h3>{escape(headline)}</h3>"
            f"{counts_html}"
            f"{qualifier_html}{orphan_note}"
            f"<p>{escape(evidence_summary)}</p>{jump_html}</div></div>"
            f"<div class='attention-notes'>{notes}</div>"
            f"{disclosure}</article>")


def _status_line(a: dict[str, Any]) -> str:
    """One persistent line above every section: the dietary state, in words."""
    if not (a.get("dietary_profiles") or []):
        return ("<p class='masthead-status quiet'>No dietary profile configured. "
                "Dietary checks are off until you add one.</p>")
    verdict = _dietary_verdict(a)
    total = verdict["total"]
    if verdict["blocked"]:
        count = verdict["blocked"]
        not_cleared = verdict["open"]
        return (f"<p class='masthead-status alert'>{count} "
                f"{_plural(count, 'item is', 'items are')} blocked by your household "
                f"dietary restrictions; {not_cleared} of {total} "
                f"{_plural(total, 'item is', 'items are')} not cleared. "
                "<span class='status-note'>See Needs attention today.</span></p>")
    if verdict["open"]:
        cleared = (f"{verdict['cleared']} of {total} cleared; " if verdict["cleared"] else "")
        return (f"<p class='masthead-status warn'>{cleared}{verdict['open']} of {total} "
                f"{_plural(total, 'item is', 'items are')} not cleared. "
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
    """Existing dietary fields, copied for the downloadable draft.

    Covers every ledger item, every cart-plan row and every held item, so the
    download cannot omit a name the page asks the household to act on (r6 M8).
    """
    verdict = _dietary_verdict(a)
    cart_items, held, _plan_verdict = _action_plan(a)
    names: list[str] = []
    for item in list(a.get("items") or []) + list(cart_items):
        name = str(item.get("name") or item.get("item") or "")
        if name and name not in names:
            names.append(name)
    for row in held:
        if row["item"] and row["item"] not in names:
            names.append(row["item"])
    rows = []
    for name in names:
        evaluation = _verdict_for(verdict, name)
        rows.append({
            "item": name,
            "result": evaluation["result"] or "not_evaluated",
            "state": evaluation["state"],
            "cleared": evaluation["cleared"],
            "evidence_status": evaluation["evidence"] or "none",
            "reason": evaluation["reason"] or "No dietary evaluation on file.",
        })
    for orphan in verdict["orphans"]:
        rows.append({
            "item": orphan["item"],
            "result": "not_evaluated",
            "raw_result": orphan["result"],
            "state": "not_evaluated",
            "cleared": False,
            "evidence_status": orphan["evidence"] or "none",
            "reason": "Evidence did not match an item on this page. "
                      + (orphan["reason"] or "No reason recorded."),
        })
    restrictions = [
        {"value": restriction.get("value") or restriction.get("type"),
         "safety_tier": restriction.get("safety_tier") or "preference",
         "behavior": restriction.get("behavior") or "warn"}
        for profile in a.get("dietary_profiles") or []
        for restriction in profile.get("restrictions") or []
    ]
    action_rows, _verdict = _action_rows(a)
    return {
        "items_total": verdict["total"],
        # The two collections are counted separately: ``action_items_total`` is the
        # page's action list (cart plan + held rows), ``engine_plan_items_total`` is
        # the raw cart plan. A single ambiguous count read as both (r7 minor).
        "action_items_total": len(action_rows),
        "engine_plan_items_total": len(cart_items),
        "items_not_cleared": verdict["open"],
        "items_cleared": verdict["cleared"],
        "headline": _verdict_headline(verdict),
        "counts": _verdict_parts(verdict, separator="; "),
        # The same five-state meanings the page's legend renders, so the download
        # cannot define "Not evaluated" with the engine's clearance wording (r7).
        "state_legend": {
            key: {"label": DIETARY_STATES[key][1], "meaning": DIETARY_STATES[key][2]}
            for key in ("blocked", "needs_review", "warning", "cleared", "not_evaluated")
        },
        "restrictions": restrictions,
        "items": rows,
        "note": ("Dietary state is copied from the engine. A warning or an absent "
                 "evaluation is not a clearance."),
    }


def _action_rows(a: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The action area's rows, computed once and rendered twice: page and draft.

    ``hold`` is true for every row the household must not buy (any non-cleared
    row). ``held_out_of_plan`` is the narrower fact that the engine cart plan has
    no row for the item; a needs-review cart row can be held without being out of
    plan, so the two flags cannot be collapsed (r7 `held:false` contradiction).
    """
    items, held, verdict = _action_plan(a)
    rows: list[dict[str, Any]] = []
    for row in held:
        reason = row["reason"] or "No reason recorded by the engine."
        rows.append({
            "item": row["item"], "engine_action": None, "display_action": "Do not buy",
            "qualifier": f"— blocked: {reason}", "state": row["state"],
            "cleared": False, "hold": True, "held_out_of_plan": True,
            "reason": reason, "source": "",
            "why": "Held out of the cart plan until this block is resolved.",
        })
    for item in items:
        name = str(item.get("item") or "")
        evaluation = _verdict_for(verdict, name)
        action, qualifier = _action_text(item.get("action"), evaluation)
        reason = str(item.get("reason") or "").strip() or "No reason recorded by the engine."
        rows.append({
            "item": name, "engine_action": str(item.get("action") or "") or None,
            "display_action": action, "qualifier": qualifier,
            "state": evaluation["state"], "cleared": bool(evaluation["cleared"]),
            "hold": not evaluation["cleared"], "held_out_of_plan": False,
            "reason": reason,
            "source": _source_label(item.get("source")), "why": reason,
        })
    return rows, verdict


def _draft_payload(a: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    """The downloaded draft: one authoritative action list plus the raw plan.

    ``items[]`` at the top level is the page's action list — the only
    instruction-bearing collection in the file. The engine cart plan is preserved
    verbatim under ``engine_plan``, which is reference data, not a shopping
    instruction. A household can therefore read or print the download without
    meeting an unqualified restock on an uncleared row (r6 B1, r7 blocker).
    """
    action_rows, _verdict = _action_rows(a)
    items = [
        {"item": row["item"], "display_action": row["display_action"],
         "engine_action": row["engine_action"], "state": row["state"],
         "cleared": row["cleared"], "hold": row["hold"],
         "held_out_of_plan": row["held_out_of_plan"],
         "qualifier": row["qualifier"], "reason": row["reason"],
         "source": row["source"]}
        for row in action_rows
    ]
    return {
        "schema": "grocery-flywheel.dashboard-draft/2",
        "note": ("Download-only draft. items[] is the action list this page shows; "
                 "nothing is bought and nothing is written back to your state file."),
        "mode": plan.get("mode"),
        "approval_required": plan.get("approval_required"),
        "checkout_available": plan.get("checkout_available"),
        "items": items,
        "items_note": (
            "items[] is the page's action list and the only instruction-bearing "
            "collection here. hold=true means do not buy; cleared=true is required "
            "before restocking. engine_plan below is the engine's cart plan preserved "
            "verbatim, including its raw source slugs, and is not a shopping "
            "instruction."),
        "dietary_context": _dietary_context(a),
        "engine_plan": json.loads(json.dumps(plan)),
    }


def _action_text(engine_action: object, verdict: dict[str, Any]) -> tuple[str, str]:
    """Engine action plus the dietary qualifier it must carry, if any."""
    base = _label(ACTION_LABELS, engine_action)
    if verdict["cleared"]:
        return base, ""
    if verdict["state"] == "blocked":
        return "Do not buy", "— blocked by dietary evidence"
    if base == "Restock":
        # A buy verb never stands on a row that has not been cleared (r6 minor).
        base = "Hold restock"
    if verdict["state"] == "needs_review":
        return base, "— not dietarily cleared: resolve evidence first"
    if verdict["state"] == "warning":
        return base, "— not dietarily cleared: warning on file"
    return base, "— not dietarily cleared: no dietary evaluation"


def _cart_plan(a: dict[str, Any]) -> str:
    plan = a.get("cart_plan") or {}
    action_rows, verdict = _action_rows(a)
    total_actions = len(action_rows)
    cleared_actions = sum(1 for row in action_rows if row["cleared"])
    held_actions = total_actions - cleared_actions
    if cleared_actions == total_actions:
        head_note = f"{total_actions} {_plural(total_actions, 'item')} &middot; all cleared"
    elif cleared_actions:
        head_note = (f"{total_actions} {_plural(total_actions, 'item')} &middot; "
                     f"{cleared_actions} cleared &middot; {held_actions} need a decision")
    else:
        head_note = f"{total_actions} {_plural(total_actions, 'item')} &middot; none cleared"
    head = _section_head(
        "Today &middot; before you shop",
        head_note,
    )
    note = ("<p class='approve-note'>Every purchasable item needs your approval. "
            "No checkout surface exists.</p>")
    if not action_rows:
        return (f"<article class='panel span-12 today' id='today'>{head}"
                "<h3 class='card-headline'>No cart plan yet.</h3>"
                f"{note}<p class='lede'>Add sourcing research or deplete an item, then "
                "render this page again.</p></article>")

    rows = []
    for index, row in enumerate(action_rows, 1):
        mark = _dietary_mark(_verdict_for(verdict, row["item"]))
        if row["held_out_of_plan"]:
            rows.append(
                f"<li class='action-hold' data-action-item='{escape(row['item'], quote=True)}'>"
                f"<span class='action-num'>{index:02d}</span>"
                f"<span class='action-item'>{escape(row['item'])}"
                f"<span class='action-why'>{escape(row['why'])}</span>"
                f"<span class='action-diet'><span class='eyebrow-inline'>Dietary</span> "
                f"{mark}</span></span>"
                "<span class='action-source'><span class='eyebrow-inline'>Action</span> "
                f"{escape(row['display_action'])} "
                f"<span class='action-qualifier'>{escape(row['qualifier'])}</span>"
                "</span></li>")
            continue
        qualifier_html = (f"<span class='action-qualifier'>{escape(row['qualifier'])}</span>"
                          if row["qualifier"] else "")
        rows.append(
            f"<li data-action-item='{escape(row['item'], quote=True)}'>"
            f"<span class='action-num'>{index:02d}</span>"
            f"<span class='action-item'>{escape(row['item'])}"
            f"<span class='action-why'>{escape(row['why'])}</span>"
            f"<span class='action-diet'><span class='eyebrow-inline'>Dietary</span> "
            f"{mark}</span></span>"
            "<span class='action-source'><span class='eyebrow-inline'>Action</span> "
            f"{escape(row['display_action'])} {qualifier_html}<br>"
            f"<span class='eyebrow-inline'>Source</span> "
            f"{escape(row['source'])}</span></li>")
    draft = _draft_payload(a, plan)
    export = ("<button class='primary' id='buy-list-download' type='button' data-plan='"
              + escape(json.dumps(draft, sort_keys=True), quote=True) + "'>Download draft JSON</button>"
              "<script>document.getElementById('buy-list-download').addEventListener('click', function () {"
              "var url = URL.createObjectURL(new Blob([this.dataset.plan], {type:'application/json'}));"
              "var link = document.createElement('a'); link.href = url; link.download = 'buy-list.json';"
              "document.body.appendChild(link); link.click(); link.remove();"
              "setTimeout(function () { URL.revokeObjectURL(url); }, 1000);});</script>"
              "<span class='section-note'>A .json file you can read or print, including the "
              "dietary state and the action list above. Nothing is bought, and nothing is "
              "written back to your state file.</span>")

    approval = _label(APPROVAL_LABELS, (plan.get("items") or [{}])[0].get("approval_state"))
    approval_phrase = ("every item needs your approval before anything is bought."
                       if approval == APPROVAL_LABELS["needs_human_approval"]
                       else f"approval state: {escape(approval)}.")
    ledger_count = len(a.get("items") or [])
    meta = (f"Mode <b>{escape(humanize_key(plan.get('mode') or 'pickup'))}</b> &middot; "
            f"approval required before anything is bought: <b>yes</b> &middot; "
            f"checkout available: <b>no</b> &middot; prices behind these numbers, whole "
            f"ledger ({ledger_count} {_plural(ledger_count, 'item')}): "
            f"<b>{_price_bucket_text(a)}</b> &middot; {approval_phrase}")
    held_count = sum(1 for row in action_rows if row["held_out_of_plan"])
    blocked_note = ""
    if held_count:
        blocked_note = (f" {held_count} {_plural(held_count, 'item is', 'items are')} blocked "
                        "by dietary evidence and must not be bought.")
    return (f"<article class='panel span-12 today' id='today'>{head}"
            f"<h3 class='card-headline'>Review {total_actions} "
            f"{_plural(total_actions, 'item')} before your next shop.{blocked_note}</h3>"
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


def _note_cell(text: object) -> str:
    note = str(text or "No note recorded.")
    if len(note) <= 160:
        return escape(note)
    return (f"<details class='note-disclosure'><summary>Read the note "
            f"({len(note)} characters)</summary><p class='muted'>{escape(note)}</p></details>")


def _at_risk(a: dict[str, Any]) -> str:
    rows = [item for item in a.get("items") or []
            if float(item.get("consumed_fraction") or 0) >= 0.5]
    if not rows:
        return "<p class='muted'>No item has passed half of its observed life yet.</p>"
    rows.sort(key=lambda item: float(item.get("consumed_fraction") or 0), reverse=True)
    verdict = _dietary_verdict(a)
    body = "".join(
        f"<tr><td data-label='Item'><span class='cell-value'>"
        f"{escape(str(item['name']))}</span></td>"
        f"<td data-label='Role' data-role='{escape(str(item.get('role') or ''))}'>"
        f"<span class='cell-value'>{escape(_role(item.get('role')))}</span></td>"
        f"<td data-label='Consumed'><span class='cell-value'>"
        f"{float(item.get('consumed_fraction') or 0) * 100:.0f}%</span></td>"
        f"<td data-label='Drawn down'><span class='cell-value'>"
        f"{_bar(float(item.get('consumed_fraction') or 0))}</span></td>"
        f"<td data-label='Spend'><span class='cell-value'>"
        f"{_money(item.get('spend'))}</span></td>"
        f"<td data-label='Dietary'><span class='cell-value'>"
        f"{_dietary_mark(_verdict_for(verdict, item['name']))}</span></td>"
        f"<td data-label='Note'><span class='cell-value'>"
        f"{_note_cell(item.get('notes'))}</span></td></tr>"
        for item in rows
    )
    return ("<p class='table-caption'>Items at or past half their observed life. A restock "
            "of any row waits for its dietary state.</p>"
            "<table class='at-risk'><colgroup><col style='width:22%'><col style='width:13%'>"
            "<col style='width:9%'><col style='width:14%'><col style='width:10%'>"
            "<col style='width:16%'><col style='width:16%'></colgroup>"
            "<thead><tr><th>Item</th><th>Role</th><th>Consumed</th><th>Drawn down</th>"
            "<th>Spend</th><th>Dietary</th><th>Note</th></tr></thead>"
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
        f"({share:.1f}%)</span></div>")
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
        entries = [str(part) for field in ("ingredients", "allergen_statements", "certifications")
                   for part in (row.get(field) or [])]
        content = (", ".join(entries) if entries else
                   "No ingredient, allergen or certification text recorded.")
        parts.append(f"<details><summary>{escape(label)}</summary>"
                     f"<p class='muted'>{escape(content)}</p></details>")
    return "".join(parts)


def _dietary_mark(verdict: dict[str, Any] | None = None) -> str:
    """Render exactly one verdict from ``_item_verdict``. No other input is read.

    The function deliberately cannot see an item's own ``dietary_status``: a
    clearance exists only when the authority says ``cleared``. The receipt
    attributes are copied from the verdict, never stamped from the state, and
    the sage token requires ``cleared is True`` (r6 M6).
    """
    verdict = verdict or _item_verdict("", None)
    state = str(verdict.get("state") or "not_evaluated")
    if state == "cleared" and verdict.get("cleared") is not True:
        state = "not_evaluated"
    if state not in DIETARY_STATES:
        state = "not_evaluated"
    token, label, _meaning = DIETARY_STATES[state]
    attrs = (f" data-item='{escape(str(verdict.get('item') or ''), quote=True)}'"
             f" data-verdict='{escape(state, quote=True)}'"
             f" data-raw-status='{escape(str(verdict.get('result') or 'not_evaluated'), quote=True)}'")
    result = str(verdict.get("result") or "")
    evidence = str(verdict.get("evidence") or "")
    if result:
        attrs += f" data-result='{escape(result, quote=True)}'"
    if evidence:
        attrs += f" data-evidence='{escape(evidence, quote=True)}'"
    tier = str(verdict.get("tier") or "")
    if tier:
        attrs += f" data-tier='{escape(tier, quote=True)}'"
    detail = str(verdict.get("detail") or "")
    detail_html = f"<span class='mark-detail'>{detail}</span>" if detail else ""
    return (f"<span class='mark {token}'{attrs}>{escape(label)}</span>{detail_html}")


def _price_label(status: str, stale: bool) -> tuple[str, str]:
    """Price states never borrow the sage clearance token (committee M9)."""
    if status == "unpriced":
        return ("No price captured", "neutral")
    if status == "estimated":
        return ("Estimated price", "warn")
    if status == "gift":
        return ("Gift — price optional", "neutral")
    if stale:
        return ("Stale price on file", "warn")
    return ("Priced", "plain")


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
        elif stale and detail in ("", "no check date"):
            # A stale price with no check date is unknown, not asserted stale.
            return ("Price on file · date unknown", "warn", "staleness unknown")
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


def _price_buckets(a: dict[str, Any]) -> dict[str, int]:
    """Buckets derived from the rendered price label, so the words cannot disagree.

    A stale flag with no check date renders "Price on file · date unknown"; it is
    counted as ``unknown``, never as ``stale`` (r6 minor: "9 stale" against nine
    rows that said "staleness unknown").
    """
    counts = {"priced": 0, "stale": 0, "unknown": 0, "unpriced": 0,
              "estimated": 0, "gift": 0}
    key_by_label = {
        "Priced": "priced",
        "Stale price on file": "stale",
        "Price on file · date unknown": "unknown",
        "No price captured": "unpriced",
        "Estimated price": "estimated",
        "Gift — price optional": "gift",
    }
    for row in (a.get("freshness") or {}).get("items") or []:
        label, _css, _detail = _price_state({}, row)
        counts[key_by_label.get(label, "unpriced")] += 1
    return counts


def _price_bucket_text(a: dict[str, Any]) -> str:
    counts = _price_buckets(a)
    if not any(counts.values()):
        return "no prices on file"
    parts = [f"{counts['priced']} priced", f"{counts['stale']} stale",
             f"{counts['unknown']} price date unknown",
             f"{counts['unpriced']} no price", f"{counts['estimated']} estimated"]
    if counts["gift"]:
        parts.append(f"{counts['gift']} gift")
    return " &middot; ".join(parts)


def _spend_cell(item: dict[str, Any], fresh: dict[str, Any] | None) -> str:
    """A recorded amount, or an explicit unknown. Unpriced is not a $0.00 zero."""
    spend = item.get("spend")
    label, _css, _detail = _price_state(item, fresh)
    zero = False
    try:
        zero = float(str(spend)) == 0
    except (TypeError, ValueError):
        zero = False
    if label == "No price captured" and (spend is None or zero):
        pct = float(item.get("consumed_fraction") or 0) * 100
        return ("<span class='cell-value'>not recorded</span>"
                f"<span class='cell-sub'>unpriced placeholder &middot; {pct:.0f}% consumed</span>")
    return (f"<span class='cell-value'>{_money(spend)}</span>"
            f"<span class='cell-sub'>{float(item.get('consumed_fraction') or 0) * 100:.0f}% consumed</span>")


def _items(a: dict[str, Any]) -> str:
    items = a.get("items") or []
    order = a.get("order") or {}
    order_total = float(order.get("total") or 0)
    tracked = sum(float(item.get("spend") or 0) for item in items)
    unattributed = round(order_total - tracked, 2)
    head = _section_head(
        "The ledger",
        f"{len(items)} {_plural(len(items), 'item')} &middot; {_money(tracked)} tracked "
        f"&middot; {_money(unattributed)} unattributed &middot; {_money(order_total)} order",
    )
    if not items:
        return (f"<article class='panel span-12 ledger'>{head}"
                "<p class='muted'>No items in the ledger yet.</p></article>")
    verdict = _dietary_verdict(a)
    fresh = _freshness_map(a)
    states = [_verdict_for(verdict, str(item.get("name")))[ "state"] for item in items]
    caption = ("Every item the engine holds, with price state, dietary state and "
               "product evidence.")
    if set(states) == {"not_evaluated"}:
        caption += (" No item has a dietary evaluation on file; “Not evaluated” is "
                    "not a clearance.")
    elif set(states) == {"cleared"}:
        caption += (f" All {len(items)} items are cleared against current dietary evidence.")
    elif len(set(states)) == 1:
        only = states[0]
        caption += (f" All {len(items)} items share the same dietary display "
                    f"({DIETARY_STATES[only][1]}); the attention panel explains why.")
    body = "".join(
        f"<tr><td><span class='cell-value'>{escape(str(item['name']))}</span>"
        f"<span class='cell-sub'>{escape(_role(item.get('role')))} &middot; "
        f"{escape(humanize_key(item.get('category') or ''))}</span></td>"
        f"<td>{_spend_cell(item, fresh.get(str(item.get('name'))))}</td>"
        f"<td><span class='cell-value'>{_price_mark(item, fresh.get(str(item.get('name'))))}</span></td>"
        f"<td><span class='cell-value'>{_dietary_mark(_verdict_for(verdict, str(item.get('name'))))}</span></td>"
        f"<td><span class='cell-value'>{_evidence_drawer(item)}</span></td></tr>"
        for item in items
    )
    reconcile = (
        f"<p class='reconcile'>Order total <b>{_money(order_total)}</b>; the {len(items)} "
        f"{_plural(len(items), 'item')} tracked above account for <b>{_money(tracked)}</b>. "
        f"<b>{_money(unattributed)}</b> of the order total is not attributed to any "
        "tracked item, so totals and runway are estimates, not a reconciliation.</p>")
    table = (
        "<table><colgroup><col style='width:30%'><col style='width:13%'>"
        "<col style='width:17%'><col style='width:21%'><col style='width:19%'>"
        "</colgroup><thead><tr><th>Item</th><th>Spend</th><th>Price</th>"
        "<th>Dietary</th><th>Product evidence</th></tr></thead>"
        f"<tbody>{body}</tbody></table>")
    return (f"<article class='panel span-12 ledger'>{head}"
            f"<p class='table-caption'>{escape(caption)}</p>"
            f"{table}{reconcile}</article>")


# --- supporting panels (progressive disclosure) -------------------------

def _first_wow(a: dict[str, Any]) -> str:
    wow = a.get("first_wow") or {}
    savings = float(wow.get("estimated_unit_savings", 0) or 0)
    if savings > 0:
        savings_value = _money(savings)
        savings_note = ("Sum of the per-unit savings recorded in the engine's sourcing "
                        "and substitution rows.")
    else:
        savings_value = "None recorded"
        savings_note = ("No realised saving is recorded in the engine's sourcing or "
                        "substitution rows. The candidate rows are modelled estimates, "
                        "not recorded savings.")
    candidates = sum(len(row.get("alternatives") or [])
                     for row in a.get("sourcing_research") or [])
    candidate_values = ("None recorded" if not candidates
                        else f"{candidates} modelled saving {_plural(candidates, 'row')}")
    best = str(wow.get("best_sourcing_move") or "").strip()
    verdict = _dietary_verdict(a)
    best_html = ""
    if best:
        norm_best = _norm_name(best)
        best_item = ""
        for name in verdict["verdicts"]:
            key = _norm_name(name)
            if key and (norm_best == key or norm_best.startswith(key + " ")) \
                    and len(key) > len(_norm_name(best_item)):
                best_item = name
        best_verdict = (_verdict_for(verdict, best_item) if best_item
                        else _item_verdict("", None))
        best_html = (f"Engine's headline move: {escape(best)}. Dietary state for this "
                     f"item: {_dietary_mark(best_verdict)}. ")
    candidate_note = best_html + ("Confidence and check dates vary by row — see Sourcing "
                                  "research. Alternatives carry no dietary evaluation; the "
                                  "mark applies to the item you already buy.")
    return f"""
      <article class="panel">
        <h2>Savings and sourcing</h2>
        <div class="card-row">
          <div><h3 class="stat-label">Recorded savings</h3>
            <div class="metric">{escape(savings_value)}</div>
            <p class="muted stat-note">{escape(savings_note)}</p></div>
          <div><h3 class="stat-label">Sourcing candidates</h3>
            <div class="metric small">{escape(candidate_values)}</div>
            <p class="muted stat-note">{candidate_note}</p></div>
          <div><h3 class="stat-label">Runway</h3>
            <div class="metric small">{escape(_runway_text(a))}</div></div>
        </div>
        <p class="muted">{escape(str(wow.get('headline', '')))}</p>
      </article>"""


def _role_rows(a: dict[str, Any]) -> list[dict[str, Any]]:
    """Role rows whose displayed ``consumed`` cents add to the order-level figure.

    The engine rounds each role to the cent, so the displayed rows can sum to a
    cent less than ``consumed_value`` (r7 minor). Apportion that difference by
    largest remainder: every row stays within one cent of the engine's own value
    and the column adds to the figure the runway prints.
    """
    rows = [dict(row) for row in a.get("role_summary") or []]
    if not rows:
        return rows
    exact: dict[str, float] = {}
    have_items = False
    for item in a.get("items") or []:
        if "consumed_value" not in item:
            continue
        have_items = True
        role = str(item.get("role") or "")
        exact[role] = exact.get(role, 0.0) + float(item.get("consumed_value") or 0)
    if not have_items:
        return rows
    target = int(round(float(a.get("consumed_value") or 0) * 100))
    floors = [math.floor(exact.get(str(row.get("role") or ""), 0.0) * 100 + 1e-9)
              for row in rows]
    difference = target - sum(floors)
    ranked = sorted(
        range(len(rows)),
        key=lambda index: exact.get(str(rows[index].get("role") or ""), 0.0) * 100
        - floors[index],
        reverse=difference > 0,
    )
    for index in ranked[:abs(difference)]:
        floors[index] += 1 if difference > 0 else -1
    for row, cents in zip(rows, floors):
        row["consumed"] = cents / 100
    return rows


def _role_summary(a: dict[str, Any]) -> str:
    body = "\n".join(
        f"<tr><td>{escape(_role(r['role']))}</td><td>{_money(r['spend'])}</td>"
        f"<td>{_money(r['consumed'])}</td><td>{_bar(r['consumed_fraction'])}</td></tr>"
        for r in _role_rows(a)
    )
    caption = ("<p class='table-caption'>Consumed amounts are apportioned so the "
               "column adds to the order-level observed depletion the runway prints; "
               "each row stays within one cent of the engine's own rounding.</p>")
    return ("<article class='panel span-6'><h2>Role Summary</h2>"
            + caption +
            "<table><colgroup><col style='width:30%'><col style='width:22%'>"
            "<col style='width:22%'><col style='width:26%'></colgroup>"
            "<thead><tr><th>Role</th><th>Spend</th><th>Consumed</th><th>Drawdown</th></tr></thead>"
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
    verdict = _dietary_verdict(a)
    rendered = []
    for row in summary["items"]:
        evaluation = _verdict_for(verdict, row.get("name"))
        if evaluation["cleared"]:
            instruction = "rotate into a meal before the next top-up duplicates it."
        elif evaluation["state"] == "not_evaluated":
            instruction = "do not rotate until a dietary evaluation clears it."
        else:
            instruction = "do not rotate until current evidence clears it."
        rendered.append(
            f"<li><strong>{escape(str(row['name']))}</strong> "
            f"({escape(_role(row['role']))}, {escape(str(row['age_label']))}) — "
            f"{escape(instruction)}"
            "<span class='easy-diet'><span class='eyebrow-inline'>Dietary</span> "
            f"{_dietary_mark(evaluation)}"
            "</span></li>")
    items = "".join(rendered)
    count = int(summary["count"])
    return (f"<article class='panel span-6'><h2>Easy Food</h2>"
            f"<p><strong>{count}</strong> unopened {_plural(count, 'top-up')}. "
            "The rotation line follows the dietary verdict: only a cleared item is "
            "told to rotate.</p>"
            f"<ul>{items}</ul></article>")


def _freshness(a: dict[str, Any]) -> str:
    summary = a.get("freshness")
    if not summary:
        return ("<article class='panel span-12'><h2>Data Freshness</h2>"
                "<p class='muted'>No freshness data.</p></article>")
    rows = summary.get("items") or []
    if rows:
        counts = _price_buckets(a)
        parts = [f"<p><b>{counts['priced']}</b> priced recently &middot; "
                 f"<b>{counts['stale']}</b> stale price &middot; "
                 f"<b>{counts['unknown']}</b> price on file, date unknown &middot; "
                 f"<b>{counts['unpriced']}</b> no price &middot; "
                 f"<b>{counts['estimated']}</b> estimated.</p>"]
    else:
        parts = ["<p class='muted'>No prices on file.</p>"]
    flagged = []
    for row in summary.get("items", []):
        if not row.get("pricing_stale"):
            continue
        label, _css, detail = _price_state({}, row)
        age = str(row.get("age_label") or "")
        suffix = "" if detail == "staleness unknown" or not age else f" ({escape(age)})"
        flagged.append(f"{escape(row['name'])} — {escape(label)}{suffix}")
    if flagged:
        parts.append("<p><strong>Flagged items:</strong> " + ", ".join(flagged) + "</p>")
    stale_sourcing = [f"{escape(r['item'])} ({escape(r['age_label'])})"
                      for r in summary.get("stale_sourcing", [])]
    if stale_sourcing:
        parts.append("<p><strong>Stale sourcing research:</strong> " + ", ".join(stale_sourcing) + "</p>")
    parts.append("<p class='muted'>One price vocabulary across this page: Priced, "
                 "Price on file · date unknown, Stale price on file, No price captured, "
                 "Estimated price, Gift.</p>")
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


def _substitution_verdict(row: dict[str, Any], verdict: dict[str, Any]) -> dict[str, Any]:
    """The candidate's own engine state, rendered through the same authority (r6 M3).

    A candidate that is also a page item uses that item's verdict. Otherwise the
    row's engine ``dietary_status``/``evidence_status`` are translated into the
    authority's vocabulary — never discarded as "Not evaluated" and never
    upgraded to a clearance without current evidence.
    """
    candidate = str(row.get("candidate") or "")
    if _norm_name(candidate) in verdict["page_norms"]:
        return _verdict_for(verdict, candidate)
    result = _explicit_result(row.get("dietary_status"))
    if not result:
        return _item_verdict(candidate, None)
    evidence = str(row.get("evidence_status") or "").strip()
    mapped = {"candidate_evidence_current": "current",
              "candidate_evidence_reviewed": "reviewed",
              "missing_candidate_evidence": "missing"}.get(evidence, evidence)
    verdict = _item_verdict(candidate, {
        "result": result, "evidence_status": mapped,
        "safety_tier": row.get("safety_tier") or "",
        "reason": row.get("read") or row.get("recommendation") or "",
    })
    detail_override = {"missing_candidate_evidence": "No candidate evidence",
                       "candidate_evidence_reviewed": "Candidate evidence reviewed"}
    if evidence in detail_override and not verdict["cleared"]:
        verdict["detail"] = f"{detail_override[evidence]} &middot; {verdict['tier']} tier"
    return verdict


def _substitutions(a: dict[str, Any]) -> str:
    rows = a.get("substitutions", [])
    if not rows:
        return ("<article class='panel span-6'><h2>Substitutions</h2>"
                "<p class='muted'>No substitution candidates yet.</p></article>")
    verdict = _dietary_verdict(a)
    body = "\n".join(
        f"<tr><td>{escape(r['candidate'])}</td><td>{escape(r['current'])}</td>"
        f"<td>{_money(r.get('candidate_unit_price'))}</td>"
        f"<td>{escape(humanize_key(r.get('fit', '')))}</td>"
        f"<td>{_dietary_mark(_substitution_verdict(r, verdict))}</td>"
        f"<td>{escape(r.get('read', ''))}</td></tr>"
        for r in rows
    )
    return ("<article class='panel span-6'><h2>Substitutions</h2>"
            "<p class='table-caption'>Candidate substitutes from your state. The dietary "
            "mark is the candidate's own engine state: “Not evaluated” means the engine "
            "recorded no evaluation for the candidate, which is not a clearance.</p>"
            "<table><colgroup><col style='width:22%'><col style='width:20%'>"
            "<col style='width:10%'><col style='width:12%'><col style='width:20%'>"
            "<col style='width:16%'></colgroup>"
            "<thead><tr><th>Candidate</th><th>Replaces</th><th>Unit</th><th>Fit</th>"
            "<th>Dietary</th><th>Read</th></tr></thead>"
            f"<tbody>{body}</tbody></table></article>")


def _sourcing(a: dict[str, Any]) -> str:
    rows = a.get("sourcing_research", [])
    if not rows:
        return ("<article class='panel span-6'><h2>Sourcing Research</h2>"
                "<p class='muted'>No sourcing research yet.</p></article>")
    verdict = _dietary_verdict(a)
    freshness = {str(row.get("item")): row
                 for row in (a.get("freshness") or {}).get("sourcing") or []}
    records = []
    for row in rows:
        name = str(row.get("item") or "")
        evaluation = _verdict_for(verdict, name)
        alternatives = row.get("alternatives") or []
        alt_html = "".join(
            f"<p class='source-alt'><b>{escape(str(alt.get('source') or 'Unnamed source'))}</b> "
            f"&middot; {_money(alt.get('unit_price'))} per unit &middot; "
            f"{escape(str(alt.get('savings') or 'no saving recorded'))} modelled saving "
            f"<span class='muted'>({escape(humanize_key(alt.get('confidence') or 'unknown'))} "
            f"confidence; checked {escape(human_date(alt.get('checked_date')))}; constraints: "
            f"{escape(', '.join(str(c) for c in alt.get('constraints') or []) or 'none recorded')})"
            "</span></p>"
            for alt in alternatives)
        stale = bool((freshness.get(name) or {}).get("stale"))
        stale_html = ("<p class='source-stale'>The engine marks this research as possibly "
                      "out of date.</p>" if stale else "")
        records.append(
            f"<div class='source-row'><p class='source-title'>{escape(name)}"
            f"<span class='muted'> &middot; current source "
            f"{escape(str(row.get('current_source') or 'not recorded'))}, "
            f"{_money(row.get('current_unit_price'))} per unit</span></p>"
            f"{alt_html}"
            f"<p class='muted'>{escape(str(row.get('recommendation') or ''))}</p>"
            f"{stale_html}"
            f"<p class='source-diet'><span class='eyebrow-inline'>Dietary &middot; "
            f"this item, not the alternatives</span> "
            f"{_dietary_mark(evaluation)}</p></div>")
    basis = ("<p class='basis-note'><b>Unit prices</b> are the engine's per-unit figures; "
             "the state file records no pack size, so no unit label can be stated. Savings "
             "are modelled from the engine's sourcing multiplier, not a checked shelf price. "
             "Percentages are the engine's, computed from its unrounded unit prices; "
             "the prices shown are rounded to the cent, so a percentage will not always "
             "reproduce exactly from them. Alternatives carry no dietary evaluation here; "
             "the mark applies to the item you already buy.</p>")
    return ("<article class='panel span-6'><h2>Sourcing Research</h2>" + basis
            + "<div class='source-list'>" + "".join(records) + "</div></article>")


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
    caption = ("<p class='table-caption'>Free-text household notes, recorded as written. "
               "They are not reconciled against the ledger or the depletion model.</p>")
    if not rows:
        return ("<article class='panel span-12'><h2>Recent Pulses</h2>"
                f"{caption}<p class='muted'>No pulses yet.</p></article>")
    body = "".join(
        # tolerant field access: some hand-edited states use 'note' (compat fix, 2026-08-14)
        f"<p><span class='tag'>{escape(human_date(r['date']))}</span>"
        f"<span class='tag'>unverified note</span> "
        f"{escape(r.get('text', r.get('note', '')))}</p>"
        for r in rows[-5:]
    )
    return (f"<article class='panel span-12'><h2>Recent Pulses</h2>"
            f"{caption}{body}</article>")


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
        if not markup:
            continue
        # The summary is the visible title; the panel's own heading stays in the
        # body for heading navigation, visually hidden so the title is not drawn
        # twice (committee minor: summaries replaced the section h2s).
        match = re.search(r"<h2>(.*?)</h2>", markup, re.S)
        title = match.group(1) if match else label
        body = (markup.replace(match.group(0),
                               f"<h2 class='visually-hidden'>{match.group(1)}</h2>", 1)
                if match else markup)
        parts.append(f"<details class='disclosure'><summary>{title}</summary>"
                     f"<div class='disclosure-grid'>{body}</div></details>")
    return page_shell(header_line(analysis), _status_line(analysis),
                      _responsive_table_labels("\n".join(parts)))
