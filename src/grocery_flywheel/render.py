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
      <article class="panel span-12">
        <h2>Current Read</h2>
        {render_operating_summary(analysis.get('operating_summary', {}))}
      </article>
      <article class="panel span-12">
        <h2>Data freshness</h2>
        {render_freshness(freshness_summary(analysis))}
      </article>
      <article class="panel span-12">
        <h2>Easy food (rotate before delivery)</h2>
        {easy_food_panel(analysis)}
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
        f"<td>{escape(row.get('source', ''))}</td>"
        f"<td>{render_spend(row)}</td><td>{row['consumed_fraction'] * 100:.0f}%</td>"
        f"<td>{escape(row['notes'])}</td></tr>"
        for row in rows
    )
    return f"<table><thead><tr><th>Item</th><th>Role</th><th>Category</th><th>Source</th><th>Spend</th><th>Consumed</th><th>Notes</th></tr></thead><tbody>{body}</tbody></table>"


def render_spend(row: dict[str, Any]) -> str:
    pricing_status = row.get("pricing_status", "priced")
    if pricing_status == "unknown" and float(row.get("spend", 0)) == 0:
        return "unpriced"
    if pricing_status == "gift" and float(row.get("spend", 0)) == 0:
        return "gift"
    return f"${float(row.get('spend', 0)):.2f}"


def render_operating_summary(summary: dict[str, Any]) -> str:
    if not summary:
        return "<p class='muted'>No current read configured.</p>"
    headline = escape(str(summary.get("headline", "")))
    next_action = escape(str(summary.get("next_action", "")))
    caveat = escape(str(summary.get("caveat", "")))
    return f"<p><strong>{headline}</strong></p><p>{next_action}</p><p class='muted'>{caveat}</p>"


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
        f"<p><span class='tag'>{escape(row['date'])}</span>{escape(row.get('note',''))}</p>"
        for row in rows[-5:]
    )


def render_bar(fraction: float) -> str:
    pct = max(0, min(100, round(float(fraction) * 100)))
    return f"<div class='bar' aria-label='{pct}% consumed'><span style='width:{pct}%'></span></div>"


def freshness_summary(analysis):
    from .freshness import item_freshness, sourcing_freshness
    from datetime import date
    today = date.fromisoformat(analysis["as_of"])
    item_fresh = [item_freshness(i, today=today) for i in analysis.get("items", [])]
    src_fresh = [sourcing_freshness(r, today=today) for r in analysis.get("sourcing_research", [])]
    stale_items = [f for f in item_fresh if f["pricing_stale"]]
    fresh_items = [f for f in item_fresh if not f["pricing_stale"]]
    stale_src = [s for s in src_fresh if s["stale"]]
    return {
        "stale_count": len(stale_items),
        "fresh_count": len(fresh_items),
        "stale_source_count": len(stale_src),
        "stale_items": stale_items[:6],
        "stale_sources": stale_src[:6],
    }


def render_freshness(summary):
    if summary["stale_count"] == 0 and summary["stale_source_count"] == 0:
        return f"<p class='muted'>{summary['fresh_count']} priced recently, no stale sourcing.</p>"
    bits = [f"<p class='muted'>{summary['fresh_count']} priced recently, {summary['stale_count']} unpriced or stale.</p>"]
    if summary["stale_count"]:
        names = ", ".join(
            f"{i['name']} ({i['age_label']}, {i['reason']})"
            for i in summary["stale_items"]
        )
        bits.append(f"<p><strong>{summary['stale_count']} unpriced or stale items:</strong> {escape(names)}</p>")
    if summary["stale_source_count"]:
        names = ", ".join(
            f"{s['item']} ({s['age_label']})" for s in summary["stale_sources"]
        )
        bits.append(f"<p><strong>{summary['stale_source_count']} stale sourcing rows:</strong> {escape(names)}</p>")
    return "".join(bits)


def easy_food_panel(analysis):
    from .easy_food import easy_food_summary, render_easy_food
    return render_easy_food(easy_food_summary(analysis))
