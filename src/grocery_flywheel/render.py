from __future__ import annotations

from html import escape
from typing import Any


def render_dashboard(analysis: dict[str, Any]) -> str:
    order = analysis["order"]
    surface = analysis.get("inventory_surface") or {}
    surface_label = surface.get("label") or surface.get("type") or "Inventory surface"
    acquisition_channel = analysis.get("acquisition_channel", "unknown")
    runway = (
        f"{analysis['estimated_days_remaining']} days remaining"
        if analysis["estimated_days_remaining"] is not None
        else "Not enough depletion data"
    )
    consumed_pct = analysis["known_consumed_fraction"] * 100

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Grocery Flywheel Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18201c;
      --muted: #66736c;
      --line: #d9dfda;
      --paper: #f7f4ee;
      --panel: #ffffff;
      --green: #2f7d5c;
      --blue: #2d5f91;
      --gold: #b36b12;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    header {{ display: grid; gap: 14px; margin-bottom: 22px; }}
    h1, h2 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: clamp(2rem, 6vw, 4.5rem); line-height: .95; }}
    h2 {{ font-size: 1rem; text-transform: uppercase; color: var(--muted); }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 0 rgba(0,0,0,.04);
    }}
    .span-4 {{ grid-column: span 4; }}
    .span-6 {{ grid-column: span 6; }}
    .span-12 {{ grid-column: span 12; }}
    .metric {{ font-size: 2rem; font-weight: 750; margin-top: 6px; }}
    .muted {{ color: var(--muted); }}
    table {{ width: 100%; border-collapse: collapse; font-size: .92rem; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: .78rem; text-transform: uppercase; }}
    .bar {{ height: 10px; background: #e8ece8; border-radius: 999px; overflow: hidden; min-width: 80px; }}
    .bar > span {{ display: block; height: 100%; background: var(--green); }}
    .tag {{ display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 3px 8px; margin: 3px 4px 3px 0; }}
    @media (max-width: 760px) {{
      main {{ padding: 18px; }}
      .span-4, .span-6 {{ grid-column: span 12; }}
      table {{ font-size: .85rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="muted">Local-first household replenishment</p>
      <h1>Grocery Flywheel</h1>
      <p>{escape(str(surface_label))} via {escape(str(acquisition_channel))}. {escape(order['store'])} run from {escape(order['date'])}, analyzed as of {escape(analysis['as_of'])}.</p>
    </header>
    <section class="grid">
      <article class="panel span-4">
        <h2>Known Depletion</h2>
        <div class="metric">${analysis['consumed_value']:.2f}</div>
        <p class="muted">{consumed_pct:.1f}% of order value observed consumed.</p>
      </article>
      <article class="panel span-4">
        <h2>Runway</h2>
        <div class="metric">{escape(runway)}</div>
        <p class="muted">Estimate is based on observed depletion, not a full pantry audit.</p>
      </article>
      <article class="panel span-4">
        <h2>Order Total</h2>
        <div class="metric">${float(order['total']):.2f}</div>
        <p class="muted">{analysis['days_elapsed']} elapsed day(s).</p>
      </article>
      <article class="panel span-6">
        <h2>Role Summary</h2>
        {render_role_table(analysis['role_summary'])}
      </article>
      <article class="panel span-6">
        <h2>Preference Signals</h2>
        {render_preferences(analysis['preferences'])}
      </article>
      <article class="panel span-6">
        <h2>Dietary Restrictions</h2>
        {render_dietary_profiles(analysis['dietary_profiles'])}
      </article>
      <article class="panel span-12">
        <h2>Data Freshness</h2>
        {render_freshness(analysis.get('freshness'))}
      </article>
      <article class="panel span-6">
        <h2>Easy Food</h2>
        {render_easy_food(analysis.get('easy_food', {}))}
      </article>
      <article class="panel span-6">
        <h2>Trip Overhead</h2>
        {render_visits(analysis.get('visits_summary', {}))}
      </article>
      <article class="panel span-12">
        <h2>Items</h2>
        {render_items(analysis['items'])}
      </article>
      <article class="panel span-6">
        <h2>Substitutions</h2>
        {render_substitutions(analysis['substitutions'])}
      </article>
      <article class="panel span-6">
        <h2>Sourcing Research</h2>
        {render_sourcing(analysis['sourcing_research'])}
      </article>
      <article class="panel span-12">
        <h2>Recent Pulses</h2>
        {render_pulses(analysis['pulses'])}
      </article>
    </section>
  </main>
</body>
</html>
"""


def render_role_table(rows: list[dict[str, Any]]) -> str:
    body = "\n".join(
        f"<tr><td>{escape(row['role'])}</td><td>${row['spend']:.2f}</td>"
        f"<td>${row['consumed']:.2f}</td><td>{render_bar(row['consumed_fraction'])}</td></tr>"
        for row in rows
    )
    return f"<table><thead><tr><th>Role</th><th>Spend</th><th>Consumed</th><th>Drawdown</th></tr></thead><tbody>{body}</tbody></table>"


def render_items(rows: list[dict[str, Any]]) -> str:
    body = "\n".join(
        f"<tr><td>{escape(row['name'])}</td><td>{escape(row['role'])}</td>"
        f"<td>{escape(row.get('category', ''))}</td>"
        f"<td>${row['spend']:.2f}</td><td>{row['consumed_fraction'] * 100:.0f}%</td>"
        f"<td>{escape(row['notes'])}</td></tr>"
        for row in rows
    )
    return f"<table><thead><tr><th>Item</th><th>Role</th><th>Category</th><th>Spend</th><th>Consumed</th><th>Notes</th></tr></thead><tbody>{body}</tbody></table>"


def render_preferences(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No preference signals yet.</p>"
    return "".join(
        f"<p><strong>{escape(row['key'])}</strong><br>{escape(row['signal'])}<br><span class='muted'>{escape(row['rule'])}</span></p>"
        for row in rows
    )


def render_dietary_profiles(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No dietary restriction profile configured.</p>"
    blocks = []
    for profile in rows:
        restrictions = profile.get("restrictions", [])
        chips = "".join(
            f"<span class='tag'>{escape(item.get('value', ''))}: {escape(item.get('behavior', 'review'))}</span>"
            for item in restrictions
        )
        blocks.append(
            f"<p><strong>{escape(profile.get('label', 'Dietary profile'))}</strong><br>{chips}</p>"
        )
    return "".join(blocks)


def render_substitutions(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No substitution candidates yet.</p>"
    body = "\n".join(
        f"<tr><td>{escape(row['candidate'])}</td><td>{escape(row['current'])}</td>"
        f"<td>${float(row['candidate_unit_price']):.3f}</td><td>{escape(row.get('fit', ''))}</td>"
        f"<td>{escape(row.get('read', ''))}</td></tr>"
        for row in rows
    )
    return f"<table><thead><tr><th>Candidate</th><th>Replaces</th><th>Unit</th><th>Fit</th><th>Read</th></tr></thead><tbody>{body}</tbody></table>"


def render_sourcing(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No sourcing research yet.</p>"
    body = []
    for row in rows:
        alternatives = row.get("alternatives", [])
        best = alternatives[0] if alternatives else {}
        body.append(
            f"<tr><td>{escape(row['item'])}</td><td>{escape(row.get('current_source', ''))}</td>"
            f"<td>{escape(best.get('source', ''))}</td><td>${float(best.get('unit_price', 0)):.3f}</td>"
            f"<td>{escape(best.get('savings', ''))}</td><td>{escape(row.get('recommendation', ''))}</td></tr>"
        )
    return "<table><thead><tr><th>Item</th><th>Current</th><th>Best alternative</th><th>Unit</th><th>Savings</th><th>Read</th></tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def render_pulses(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No pulses yet.</p>"
    return "".join(
        f"<p><span class='tag'>{escape(row['date'])}</span>{escape(row['text'])}</p>"
        for row in rows[-5:]
    )


def render_bar(fraction: float) -> str:
    pct = max(0, min(100, round(float(fraction) * 100)))
    return f"<div class='bar' aria-label='{pct}% consumed'><span style='width:{pct}%'></span></div>"


def render_freshness(summary: dict[str, Any] | None) -> str:
    """Render a small panel that shows how confident we are in item prices
    and sourcing research.

    The point is to make the user notice when data is going stale so they can
    refresh it, not to enforce a policy. Pricing and sourcing already
    document provenance as a first-class concept
    (see ``docs/SOURCING_RESEARCH_STAGE.md``); this panel is the visible
    surface of that.
    """
    if not summary:
        return "<p class='muted'>No freshness data.</p>"
    fresh = summary.get("fresh_count", 0)
    stale = summary.get("stale_count", 0)
    parts = [f"<p>{fresh} priced recently, {stale} unpriced or stale.</p>"]
    flagged = [
        f"{escape(r['name'])} ({escape(r['age_label'])}, {escape(r['reason'])})"
        for r in summary.get("items", []) if r["pricing_stale"]
    ]
    if flagged:
        parts.append("<p><strong>Flagged items:</strong> " + ", ".join(flagged) + "</p>")
    stale_sourcing = [
        f"{escape(r['item'])} ({escape(r['age_label'])})"
        for r in summary.get("stale_sourcing", [])
    ]
    if stale_sourcing:
        parts.append("<p><strong>Stale sourcing research:</strong> " + ", ".join(stale_sourcing) + "</p>")
    return "".join(parts)


def render_easy_food(summary: dict[str, Any] | None) -> str:
    """Render the easy-food rotation panel as HTML."""
    from .easy_food import render_easy_food as _render
    return _render(summary or {})


def render_visits(summary: dict[str, Any] | None) -> str:
    """Render the visit cost panel as HTML.

    The summary is expected to be the dict returned by
    ``cost_log.visits_summary``. If absent (e.g. older states without a
    visits array), show a placeholder.
    """
    if not summary:
        return "<p class='muted'>No visits recorded yet. Use <code>capture-visit</code> to log a trip.</p>"
    count = summary.get("visit_count", 0)
    if count == 0:
        return "<p class='muted'>No visits recorded yet.</p>"
    total_min = summary.get("total_minutes", 0)
    by_type = summary.get("by_type", {}) or {}
    by_type_min = summary.get("by_type_minutes", {}) or {}
    amortized = summary.get("amortized_cost_total", 0.0)
    parts = [
        f"<p><strong>{count}</strong> visit(s), <strong>{total_min}</strong> minutes total.</p>",
    ]
    if by_type:
        items = ", ".join(
            f"{escape(t)}: {by_type[t]} ({by_type_min.get(t, 0)} min)"
            for t in sorted(by_type)
        )
        parts.append(f"<p class='muted'>By type — {items}.</p>")
    if amortized:
        parts.append(f"<p>Amortized time cost: <strong>${amortized:.2f}</strong></p>")
    else:
        parts.append("<p class='muted'>Set an hourly value in the state to see amortized cost.</p>")
    return "".join(parts)
