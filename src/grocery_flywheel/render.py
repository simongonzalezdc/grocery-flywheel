from __future__ import annotations

import json
from html import escape
from typing import Any

from .privacy import CORRECTION_TELEMETRY_VALUES


def script_json(value: Any) -> str:
    return (
        json.dumps(value)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


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
    first_wow = analysis.get("first_wow", {})

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Grocery Flywheel Command Center</title>
  <style>
    :root {{
      color-scheme: dark;
      --ink: #f6f3ec;
      --muted: #b7b0a6;
      --line: #33363f;
      --paper: #07080b;
      --panel: #12141a;
      --panel-2: #181b22;
      --green: #67d49d;
      --blue: #8fb8ff;
      --gold: #f2b84b;
      --red: #ff7f7a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(circle at 20% 0%, #1b2028 0, #07080b 38rem);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 24px; }}
    header {{ display: grid; gap: 18px; min-height: 72vh; align-content: center; }}
    h1, h2, h3 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: clamp(2.7rem, 7vw, 6.5rem); line-height: .9; max-width: 11ch; }}
    h2 {{ font-size: .78rem; text-transform: uppercase; color: var(--muted); }}
    h3 {{ font-size: 1.05rem; }}
    button, .button {{
      background: var(--ink);
      color: var(--paper);
      border: 0;
      border-radius: 999px;
      padding: 10px 14px;
      font-weight: 750;
      max-width: 100%;
      white-space: normal;
    }}
    .muted {{ color: var(--muted); }}
    .hero-copy {{ max-width: 68ch; color: var(--muted); font-size: 1.05rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }}
    .panel {{
      background: color-mix(in srgb, var(--panel) 94%, white 6%);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 0 rgba(255,255,255,.05);
      min-width: 0;
    }}
    .first-wow {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }}
    .wow-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 128px;
      min-width: 0;
    }}
    .metric {{ font-size: 2rem; font-weight: 800; margin-top: 6px; }}
    .span-4 {{ grid-column: span 4; }}
    .span-5 {{ grid-column: span 5; }}
    .span-6 {{ grid-column: span 6; }}
    .span-7 {{ grid-column: span 7; }}
    .span-12 {{ grid-column: span 12; }}
    .table-scroll {{ width: 100%; max-width: 100%; min-width: 0; overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .92rem; table-layout: auto; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 10px 8px; text-align: left; vertical-align: top; }}
    th, td {{ overflow-wrap: normal; }}
    th {{ color: var(--muted); font-size: .76rem; text-transform: uppercase; }}
    .bar {{ height: 10px; background: #2a2d35; border-radius: 999px; overflow: hidden; min-width: 80px; }}
    .bar > span {{ display: block; height: 100%; background: var(--green); }}
    .tag {{ display: inline-block; border: 1px solid var(--line); border-radius: 999px; padding: 3px 8px; margin: 3px 4px 3px 0; max-width: 100%; overflow-wrap: anywhere; }}
    .tag.warn {{ border-color: var(--gold); color: var(--gold); }}
    .tag.block {{ border-color: var(--red); color: var(--red); }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .toolbar button {{ flex: 1 1 130px; }}
    select, textarea, pre {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      color: var(--ink);
      padding: 10px;
      font: inherit;
    }}
    textarea {{ min-height: 72px; resize: vertical; margin: 8px 0; }}
    pre {{ min-height: 84px; white-space: pre-wrap; overflow-wrap: anywhere; }}
    details {{ border-top: 1px solid var(--line); padding-top: 10px; margin-top: 10px; }}
    summary {{ cursor: pointer; color: var(--blue); }}
    @media (max-width: 760px) {{
      main {{ padding: 16px; }}
      header {{ min-height: auto; padding: 16px 0; }}
      h1 {{ font-size: 2.65rem; }}
      .hero-copy {{ font-size: .98rem; }}
      .first-wow, .grid {{ grid-template-columns: 1fr; }}
      .first-wow {{ gap: 8px; }}
      .wow-card {{ min-height: 104px; padding: 12px; }}
      .span-4, .span-5, .span-6, .span-7, .span-12 {{ grid-column: span 1; }}
      table {{ font-size: .82rem; min-width: 640px; }}
      .metric {{ font-size: 1.55rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="muted">Local-first household command center</p>
      <h1>Grocery Flywheel</h1>
      <p class="hero-copy">{escape(str(surface_label))} via {escape(str(acquisition_channel))}. {escape(order['store'])} run from {escape(order['date'])}, analyzed as of {escape(analysis['as_of'])}. Objective: {escape(analysis.get('objective_label', 'Balanced ROI'))}.</p>
      <section class="first-wow" aria-label="First wow">
        <article class="wow-card">
          <h2>Potential Unit Savings</h2>
          <div class="metric">${float(first_wow.get('estimated_unit_savings', 0)):.2f}</div>
          <p class="muted">{escape(first_wow.get('headline', 'Savings baseline ready'))}</p>
        </article>
        <article class="wow-card">
          <h2>Best Sourcing Move</h2>
          <div class="metric">{escape(first_wow.get('best_sourcing_move', 'Review sourcing'))}</div>
        </article>
        <article class="wow-card">
          <h2>Runway</h2>
          <div class="metric">{escape(runway)}</div>
          <p class="muted">{consumed_pct:.1f}% of order value observed consumed.</p>
        </article>
      </section>
    </header>
    <section class="grid">
      <article class="panel span-4">
        <h2>Order Total</h2>
        <div class="metric">${float(order['total']):.2f}</div>
        <p class="muted">{analysis['days_elapsed']} elapsed day(s).</p>
      </article>
      <article class="panel span-4">
        <h2>Known Depletion</h2>
        <div class="metric">${analysis['consumed_value']:.2f}</div>
        <p class="muted">Observed from explicit pulses and item states.</p>
      </article>
      <article class="panel span-4">
        <h2>Adapter Status</h2>
        {render_adapter_status(analysis)}
      </article>
      <article class="panel span-5">
        <h2>Role Summary</h2>
        {render_role_table(analysis['role_summary'])}
      </article>
      <article class="panel span-7">
        <h2>Sourcing Alternatives</h2>
        {render_sourcing(analysis['sourcing_research'])}
      </article>
      <article class="panel span-6">
        <h2>Dietary Restrictions</h2>
        {render_dietary_profiles(analysis['dietary_profiles'], analysis.get('dietary_evaluations', []))}
      </article>
      <article class="panel span-6">
        <h2>Correction Actions</h2>
        {render_correction_actions(analysis)}
      </article>
      <article class="panel span-12">
        <h2>Internal Cart Plan</h2>
        {render_cart_plan(analysis.get('cart_plan', {}))}
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
        <h2>Evidence Drawer</h2>
        {render_evidence(analysis)}
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
    return f"<div class='table-scroll'><table><thead><tr><th>Role</th><th>Spend</th><th>Consumed</th><th>Drawdown</th></tr></thead><tbody>{body}</tbody></table></div>"


def render_items(rows: list[dict[str, Any]]) -> str:
    body = "\n".join(
        f"<tr><td>{escape(row['name'])}</td><td>{escape(row['role'])}</td>"
        f"<td>{escape(row.get('category', ''))}</td>"
        f"<td>${row['spend']:.2f}</td><td>{row['consumed_fraction'] * 100:.0f}%</td>"
        f"<td>{escape(row.get('confidence', 'medium'))}</td><td>{escape(row['notes'])}</td></tr>"
        for row in rows
    )
    return f"<div class='table-scroll'><table><thead><tr><th>Item</th><th>Role</th><th>Category</th><th>Spend</th><th>Consumed</th><th>Confidence</th><th>Notes</th></tr></thead><tbody>{body}</tbody></table></div>"


def render_adapter_status(analysis: dict[str, Any]) -> str:
    profiles = analysis.get("retailer_profiles", [])
    matrix = analysis.get("adapter_matrix", [])
    if not profiles and not matrix:
        return "<p class='muted'>No adapter profile attached.</p>"
    if matrix:
        return "".join(
            render_adapter_row(row)
            for row in matrix[:3]
        )
    return "".join(f"<span class='tag'>{escape(str(profile))}</span>" for profile in profiles)


def render_adapter_row(row: dict[str, Any]) -> str:
    errors = row.get("errors", [])
    error_html = "".join(
        f"<span class='tag block'>{escape(error)}</span>"
        for error in errors
    )
    status = error_html or "<span class='tag'>valid</span>"
    return (
            f"<p><strong>{escape(row.get('name', row.get('id', 'Adapter')))}</strong><br>"
            f"<span class='tag'>score {row.get('score', 0)}</span>"
            f"<span class='tag'>{escape(', '.join(row.get('acquisition_methods', [])))}</span>"
            f"{status}</p>"
    )


def render_dietary_profiles(rows: list[dict[str, Any]], evaluations: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No dietary restriction profile configured.</p>"
    blocks = []
    for profile in rows:
        restrictions = profile.get("restrictions", [])
        chips = "".join(
            f"<span class='tag'>{escape(item.get('value', ''))}: {escape(item.get('behavior', 'review'))}</span>"
            for item in restrictions
        )
        blocks.append(f"<p><strong>{escape(profile.get('label', 'Dietary profile'))}</strong><br>{chips}</p>")
    flagged = [row for row in evaluations if row.get("result") in {"needs_review", "blocked", "warn"}]
    for row in flagged[:6]:
        klass = "block" if row["result"] == "blocked" else "warn"
        blocks.append(
            f"<p><span class='tag {klass}'>{escape(row['result'])}</span>"
            f"{escape(row['item'])}: {escape(row['reason'])}</p>"
        )
    return "".join(blocks)


def render_correction_actions(analysis: dict[str, Any]) -> str:
    signals = [
        ("wrong_format", "Wrong format"),
        ("too_expensive", "Too expensive"),
        ("buy_elsewhere", "Buy elsewhere"),
        ("never_again", "Never again"),
        ("dietary_conflict", "Dietary conflict"),
        ("good_default", "Good default"),
        ("emergency_only", "Emergency only"),
    ]
    items = [str(row.get("name", "")) for row in analysis.get("items", []) if row.get("name")]
    selected_items = items or ["General correction"]
    options = "".join(
        f"<option value='{escape(item)}'>{escape(item)}</option>"
        for item in selected_items
    )
    raw_consent = analysis.get("consent")
    consent = raw_consent if isinstance(raw_consent, dict) else {}
    default_consent_value = "local_only" if raw_consent is None else "disabled"
    consent_value = str(consent.get("correction_telemetry", default_consent_value))
    if consent_value not in CORRECTION_TELEMETRY_VALUES:
        consent_value = "disabled"
    enabled = consent_value in {"local_only", "hosted_opt_in"}
    disabled = "" if enabled else " disabled"
    buttons = "".join(
        f"<button type='button' data-correction='{escape(key)}' title='{escape(label)}'{disabled}>{escape(label)}</button>"
        for key, label in signals
    )
    schema_version = script_json(analysis.get("schema_version", ""))
    storage = script_json(consent_value)
    return f"""
        <select id="correction-item" aria-label="Correction item">{options}</select>
        <textarea id="correction-note" aria-label="Correction note" placeholder="Optional note"></textarea>
        <div class='toolbar'>{buttons}<button type='button' id='download-corrections'{disabled}>Download JSONL</button></div>
        <pre id="correction-export" aria-live="polite">[]</pre>
        <p class='muted'>Telemetry: {escape(consent_value)}.</p>
        <script>
        (() => {{
          const schemaVersion = {schema_version};
          const storage = {storage};
          const enabled = storage === "local_only" || storage === "hosted_opt_in";
          const events = [];
          window.groceryFlywheelCorrectionEvents = events;
          window.groceryFlywheelCreateCorrection = (signal) => {{
            if (!enabled) return null;
            const item = document.getElementById("correction-item")?.value || "General correction";
            const note = document.getElementById("correction-note")?.value || "";
            const event = {{
              schema_version: schemaVersion,
              privacy_class: "sensitive_correction_telemetry",
              item,
              signal,
              note,
              source: "dashboard_local_export",
              created_at: new Date().toISOString().slice(0, 10),
              storage
            }};
            events.push(event);
            const exportNode = document.getElementById("correction-export");
            if (exportNode) exportNode.textContent = events.map((row) => JSON.stringify(row)).join("\\n");
            return event;
          }};
          document.querySelectorAll("[data-correction]").forEach((button) => {{
            button.addEventListener("click", () => {{
              window.groceryFlywheelCreateCorrection(button.dataset.correction);
            }});
          }});
          document.getElementById("download-corrections")?.addEventListener("click", () => {{
            if (!events.length) return;
            const blob = new Blob([events.map((row) => JSON.stringify(row)).join("\\n") + "\\n"], {{type: "application/jsonl"}});
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "grocery-flywheel-corrections.jsonl";
            link.click();
            URL.revokeObjectURL(link.href);
          }});
        }})();
        </script>
    """


def render_cart_plan(plan: dict[str, Any]) -> str:
    if not plan.get("items"):
        return "<p class='muted'>No restock plan yet.</p>"
    body = "".join(
        f"<tr><td>{escape(row['item'])}</td><td>{escape(row['action'])}</td><td>{escape(row.get('source', ''))}</td>"
        f"<td>{escape(row.get('approval_state', 'needs_human_approval'))}</td><td>{escape(row.get('reason', ''))}</td></tr>"
        for row in plan["items"]
    )
    return (
        f"<p><span class='tag'>mode {escape(plan.get('mode', 'pickup'))}</span>"
        f"<span class='tag'>approval required</span><span class='tag'>checkout unavailable</span></p>"
        f"<div class='table-scroll'><table><thead><tr><th>Item</th><th>Action</th><th>Source</th><th>Approval</th><th>Reason</th></tr></thead><tbody>{body}</tbody></table></div>"
    )


def render_substitutions(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No substitution candidates yet.</p>"
    body = "\n".join(
        f"<tr><td>{escape(row['candidate'])}</td><td>{escape(row['current'])}</td>"
        f"<td>${float(row['candidate_unit_price']):.3f}</td><td>{escape(row.get('fit', ''))}</td>"
        f"<td>{escape(row.get('read', ''))}</td></tr>"
        for row in rows
    )
    return f"<div class='table-scroll'><table><thead><tr><th>Candidate</th><th>Replaces</th><th>Unit</th><th>Fit</th><th>Read</th></tr></thead><tbody>{body}</tbody></table></div>"


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
            f"<td>{escape(str(best.get('savings', '')))}</td><td>{escape(best.get('confidence', row.get('confidence', '')))}</td>"
            f"<td>{escape(best.get('checked_date', ''))}</td><td>{escape(', '.join(best.get('constraints', [])))}</td>"
            f"<td>{escape(row.get('recommendation', ''))}</td></tr>"
        )
    return "<div class='table-scroll'><table><thead><tr><th>Item</th><th>Current</th><th>Best alternative</th><th>Unit</th><th>Savings</th><th>Confidence</th><th>Checked</th><th>Constraints</th><th>Read</th></tr></thead><tbody>" + "".join(body) + "</tbody></table></div>"


def render_evidence(analysis: dict[str, Any]) -> str:
    details = []
    for item in analysis.get("items", []):
        evidence = item.get("product_evidence") or []
        if not evidence:
            continue
        rows = "".join(
            f"<p><span class='tag'>{escape(row.get('evidence_type', 'evidence'))}</span>"
            f"{escape(row.get('source', ''))} checked {escape(row.get('checked_date', ''))}</p>"
            for row in evidence
        )
        details.append(f"<details><summary>{escape(item['name'])}</summary>{rows}</details>")
    if not details:
        return "<p class='muted'>No product evidence attached yet; safety-critical dietary results will need review.</p>"
    return "".join(details)


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
