"""Self-contained warm pantry-ledger shell; analysis stays in the engine.

Direction A from Design t_0abdce8f: paper ground, ink, one copper action,
hairline rules, system serif display. No fetched font, image or script.

Round 4 layout contracts (Product r3 review + committee majors M1-M9):

* every data table is ``table-layout:fixed`` with an explicit ``<colgroup>`` so
  an unbroken 2,000-character token wraps inside its column instead of blowing
  the table to 17,000 px;
* on narrow screens a ledger record is a two-column grid and every value cell
  carries a ``.cell-value`` wrapper, so the sub-line sits under the *value*,
  never under the label;
* brick is reserved for blocked evidence; a preference-tier warning is ochre;
* sage means a dietary clearance only. A price state never wears the sage token.
"""
from __future__ import annotations

from html import escape

CSS = """
:root {
  color-scheme: light;
  --bg:#F6F1E7; --panel:#FFFDF8; --panel-2:#EFE8DA;
  --edge:#D8CCB6; --edge-strong:#8A7F6E; --ink:#241F19; --muted:#5A5145; --faint:#8A7F6E;
  --copper:#A2512A; --copper-deep:#8A4222; --sage:#3F6B45;
  --ochre:#8A5B12; --brick:#A32D22;
  --display:"Iowan Old Style",Palatino,"Palatino Linotype",Georgia,"Times New Roman","Liberation Serif",serif;
  --body:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","Liberation Sans",Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;
  --step--1:clamp(0.78rem,0.75rem + 0.12vw,0.84rem);
  --step-0:clamp(0.95rem,0.91rem + 0.18vw,1.05rem);
  --step-1:clamp(1.12rem,1.04rem + 0.36vw,1.32rem);
  --step-2:clamp(1.35rem,1.20rem + 0.70vw,1.75rem);
  --step-3:clamp(1.70rem,1.40rem + 1.40vw,2.55rem);
  --step-4:clamp(2.15rem,1.60rem + 2.60vw,3.80rem);
  --measure:66ch;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:var(--body); font-size:var(--step-0); line-height:1.6;
  font-variant-numeric:tabular-nums; }
main { max-width:74rem; margin:auto; padding:32px 24px 80px; }
header.masthead { border-bottom:2px solid var(--ink); padding-bottom:20px; margin-bottom:32px; }
h1,h2,h3,p { margin:0 0 12px; }
h1 { font-family:var(--display); font-size:var(--step-3); line-height:1.05; font-weight:600;
  text-wrap:balance; }
h3 { font-family:var(--display); font-size:var(--step-2); line-height:1.2; font-weight:600;
  text-wrap:balance; }
p { max-width:var(--measure); }
.muted { color:var(--muted); }
.cell-sub, .mark-detail { display:block; font-weight:400; font-size:var(--step--1);
  color:var(--muted); }
.stat-label { font-family:var(--body); font-size:var(--step--1); letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); margin:0 0 4px; font-weight:600; }
.stat-note { font-size:var(--step--1); margin:6px 0 0; }
.eyebrow { text-transform:uppercase; letter-spacing:.15em; font-size:var(--step--1);
  color:var(--muted); margin-bottom:8px; }
.masthead-meta { display:flex; flex-wrap:wrap; gap:6px 24px; font-size:var(--step--1);
  color:var(--muted); }
.masthead-meta b { color:var(--ink); font-weight:600; }
.masthead-notes { margin-top:8px; }
.card-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:24px; }
.card-row h2 { font-family:var(--body); font-size:var(--step--1); letter-spacing:.08em;
  text-transform:uppercase; color:var(--muted); margin-bottom:4px; }
.metric { font-family:var(--display); font-size:var(--step-2); font-weight:600;
  line-height:1.2; margin:4px 0; }
.metric.small { font-family:var(--body); font-size:var(--step-0); font-weight:600; }
.masthead-status { display:flex; flex-wrap:wrap; align-items:baseline; gap:4px 12px;
  position:sticky; top:0; z-index:4;
  margin:16px 0 0; padding:12px 16px; font-weight:600; font-size:var(--step-0);
  border:1px solid var(--edge); border-left:5px solid var(--edge);
  background:var(--panel); max-width:none; }
.masthead-status.alert { border-left-color:var(--brick); color:var(--brick); }
.masthead-status.warn { border-left-color:var(--ochre); color:var(--ochre); }
.masthead-status.clear { border-left-color:var(--sage); color:var(--sage); }
.masthead-status .status-note { font-weight:400; color:var(--muted); }
.grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:32px 40px; }
.panel { min-width:0; background:transparent; border:0; padding:0; overflow-wrap:break-word; word-break:normal; }
.span-4 { grid-column:span 4; } .span-6 { grid-column:span 6; } .span-12 { grid-column:span 12; }
.section-head { display:flex; align-items:baseline; justify-content:space-between;
  gap:16px; flex-wrap:wrap; border-bottom:1px solid var(--edge);
  padding-bottom:8px; margin-bottom:16px; }
.section-label { font-family:var(--body); font-size:var(--step--1); letter-spacing:.16em;
  text-transform:uppercase; font-weight:700; color:var(--ink); margin:0; }
.section-note { font-size:var(--step--1); color:var(--muted); }
.eyebrow-inline { text-transform:uppercase; letter-spacing:.14em; font-size:var(--step--1);
  color:var(--muted); font-weight:700; }
.attention { background:var(--panel); border:1px solid var(--edge);
  border-left:8px solid var(--brick); padding:20px 24px 22px; }
.attention.warn-tier { border-left-color:var(--ochre); }
.attention.quiet { border-left-color:var(--edge); }
.attention h2, .attention h3 { color:var(--ink); }
.attention-figure { font-family:var(--display); font-size:var(--step-4); line-height:.95;
  color:var(--brick); font-weight:600; margin:0 0 4px; }
.attention.warn-tier .attention-figure { color:var(--ochre); }
.attention-figure small { display:block; font-family:var(--body); font-size:var(--step--1);
  letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin-top:8px;
  line-height:1.3; font-weight:600; }
.attention-body { display:grid; grid-template-columns:minmax(6.5rem,auto) minmax(0,1fr);
  gap:12px 28px; align-items:start; }
.attention-verdict h3 { margin-bottom:8px; }
.attention-qualifier { font-size:var(--step-0); font-weight:600; color:var(--ink);
  margin:0 0 10px; max-width:60ch; }
.attention-counts { font-size:var(--step--1); color:var(--muted); margin:0 0 8px;
  max-width:60ch; }
.jump-link { display:inline-flex; align-items:center; gap:.4em; min-height:44px;
  margin:2px 0 0; font-weight:600; text-underline-offset:3px; }
.attention-context { margin:8px 0 0; }
.attention-context > summary { padding:6px 0; min-height:32px; font-size:var(--step--1); }
#today { scroll-margin-top:5.5rem; }
.attention-notes { display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px 32px; margin-top:16px; padding-top:12px; border-top:1px solid var(--edge); }
.attention-notes p { font-size:var(--step--1); color:var(--muted); margin:0; max-width:60ch; }
.attention-notes b { color:var(--ink); font-weight:600; }
.today { background:var(--panel); border:1px solid var(--edge);
  border-top:5px solid var(--ink); padding:24px; }
.card-headline { font-family:var(--display); font-size:var(--step-2); line-height:1.15;
  font-weight:600; margin-bottom:12px; max-width:none; text-wrap:balance; }
.lede { font-size:var(--step-1); line-height:1.45; max-width:56ch; text-wrap:balance; }
.action-list { list-style:none; margin:16px 0 0; padding:0; }
.action-list li { display:grid; grid-template-columns:2.5rem 1fr minmax(9rem,auto);
  gap:12px; align-items:baseline; padding:10px 0; border-top:1px solid var(--edge); }
.action-list li:first-child { border-top:0; }
.action-num { font-family:var(--mono); font-size:var(--step--1); color:var(--muted); }
.action-item { font-weight:600; }
.action-why { display:block; font-weight:400; font-size:var(--step--1); color:var(--muted); }
.action-source { font-size:var(--step--1); color:var(--muted); text-align:right; }
.action-qualifier { display:block; color:var(--brick); font-weight:600; }
.action-hold { border-left:3px solid var(--brick); padding-left:0.9rem !important; }
.action-hold .action-num { color:var(--brick); font-weight:700; }
.btn-row { display:flex; flex-wrap:wrap; align-items:center; gap:12px; margin-top:16px; }
.today-meta { font-size:var(--step--1); color:var(--muted); border-top:1px solid var(--edge);
  margin:14px 0 0; padding-top:12px; max-width:none; }
.today-meta b { color:var(--ink); font-weight:600; }
.approve-note { font-size:var(--step--1); color:var(--ochre); }
.runway-math { display:flex; flex-wrap:wrap; gap:12px 40px; margin:20px 0 0;
  padding-top:16px; border-top:1px solid var(--edge); }
.runway-math div { min-width:10rem; }
.runway-math .math-label { font-size:var(--step--1); color:var(--muted); display:block; }
.runway-math .math-value { font-family:var(--display); font-size:var(--step-2);
  font-weight:600; line-height:1.2; }
.ruler { margin:20px 0 0; }
.ruler svg { display:block; width:100%; height:auto; max-width:100%; }
.legend { display:flex; flex-wrap:wrap; gap:6px 24px; font-size:var(--step--1);
  color:var(--muted); margin-top:12px; }
.legend-item { display:inline-flex; align-items:center; gap:.45em; }
.legend-swatch { width:.85rem; height:.85rem; border-radius:2px; flex:none; }
.legend-swatch.filled { background:var(--ink); }
.legend-swatch.outline { background:transparent; border:1px solid var(--edge-strong); }
.legend-swatch.marker { width:3px; height:1rem; border-radius:1px; background:var(--copper); }
.ruler-caption { display:flex; flex-wrap:wrap; gap:4px 24px; font-size:var(--step--1);
  color:var(--muted); margin-top:12px; }
.ruler-caption b { color:var(--ink); font-weight:600; }
.mark { display:inline-flex; align-items:center; gap:.4em; font-size:var(--step--1);
  font-weight:600; }
.mark.missing { color:var(--brick); }
.mark.warn { color:var(--ochre); }
.mark.ok { color:var(--sage); }
.mark.plain { color:var(--ink); }
.mark.neutral { color:var(--muted); font-weight:400; }
.tag { display:inline-block; border:1px solid var(--edge); border-radius:3px;
  padding:3px 9px; margin:3px 4px 3px 0; font-size:var(--step--1); }
.tag.critical { border-color:var(--brick); color:var(--brick); }
.tag.review { border-color:var(--ochre); color:var(--ochre); }
.tag.ok { border-color:var(--sage); color:var(--sage); }
table { width:100%; border-collapse:collapse; table-layout:fixed; font-size:var(--step-0); }
th,td { border-bottom:1px solid var(--edge); padding:10px 8px; text-align:left;
  vertical-align:top; overflow-wrap:break-word; word-break:normal; hyphens:none; }
th { color:var(--muted); font-size:var(--step--1); font-weight:600; }
col { min-width:0; }
.table-caption { font-size:var(--step--1); color:var(--muted); padding:0 0 8px;
  max-width:var(--measure); }
.table-caption b { color:var(--ink); font-weight:600; }
.bar { display:block; height:8px; background:#E3D9C6; border:1px solid var(--edge-strong);
  border-radius:2px; overflow:hidden; min-width:3rem; box-sizing:border-box; }
.bar > span { display:block; height:100%; background:var(--copper); }
.bar.hot > span { background:var(--brick); }
.reconcile { font-size:var(--step--1); color:var(--muted);
  border-left:3px solid var(--edge); padding:8px 12px; margin-top:14px; }
button,select { font:inherit; color:var(--ink); background:var(--panel);
  border:1px solid var(--edge); border-radius:3px; padding:10px 14px;
  min-height:44px; max-width:100%; }
button { cursor:pointer; } button:hover { border-color:var(--copper); }
button.primary { background:var(--copper); border-color:var(--copper); color:#FFF8F1; font-weight:600; }
button.primary:hover { background:var(--copper-deep); border-color:var(--copper-deep); }
a { color:var(--copper); }
:focus-visible { outline:3px solid #7A3A1C; outline-offset:3px; }
.skip-link { position:absolute; left:-9999px; top:0; padding:12px; background:var(--panel); }
.skip-link:focus { left:12px; top:12px; z-index:10; }
details { margin:10px 0; min-width:0; }
summary { cursor:pointer; padding:12px 0; min-height:44px; color:var(--muted); }
details.evidence > summary { color:var(--copper); font-weight:600; }
.disclosure { grid-column:span 12; border-top:1px solid var(--edge); }
.disclosure > summary { font-size:var(--step-1); color:var(--ink); font-weight:600; }
.disclosure h2 { font-family:var(--body); font-size:var(--step--1); letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
.disclosure-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(22rem,100%),1fr));
  gap:24px 40px; padding:4px 0 24px; }
.disclosure-grid .panel { grid-column:auto; }
.detail-body { padding:8px 0 16px; }
.state-legend { display:grid; grid-template-columns:repeat(auto-fit,minmax(10.5rem,1fr));
  gap:6px 20px; margin:14px 0 0; padding:12px 0 0; border-top:1px solid var(--edge); }
.state-legend div { margin:0; }
.state-legend dt { margin:0; }
.state-legend dd { margin:2px 0 0; font-size:var(--step--1); color:var(--muted); }
@media (min-width:1100px) {
 .state-legend { grid-template-columns:repeat(5,minmax(0,1fr)); }
}
.legend-note { font-size:var(--step--1); color:var(--muted); margin:10px 0 0; }
.basis-note { border-left:3px solid var(--edge-strong); padding:8px 12px; margin:0 0 16px;
  font-size:var(--step--1); color:var(--muted); max-width:var(--measure); }
.basis-note b { color:var(--ink); }
.tier-note { font-size:var(--step--1); color:var(--ink); margin:8px 0 0; }
.action-diet { display:block; font-size:var(--step--1); color:var(--muted); margin-top:4px; }
.easy-diet { display:block; font-size:var(--step--1); color:var(--muted); margin-top:2px; }
.source-list { margin-top:4px; }
.source-row { border-top:1px solid var(--edge); padding:12px 0; }
.source-row:first-child { border-top:0; padding-top:4px; }
.source-title { font-weight:600; margin-bottom:4px; }
.source-alt { margin:0 0 6px; }
.source-stale { color:var(--ochre); font-size:var(--step--1); margin:2px 0 6px; }
.source-diet { margin:6px 0 0; font-size:var(--step--1); }
.note-disclosure { margin:0; }
.note-disclosure > summary { padding:6px 0; min-height:32px; font-size:var(--step--1); }
.visually-hidden { position:absolute; width:1px; height:1px; margin:-1px; padding:0;
  overflow:hidden; clip-path:inset(50%); white-space:nowrap; border:0; }
footer { margin-top:56px; border-top:2px solid var(--ink); padding-top:24px;
  color:var(--muted); font-size:var(--step--1); }
footer p { max-width:var(--measure); }
@media (max-width:700px) {
 table,tbody,tr,td { display:block; width:100%; }
 colgroup { display:none; }
 thead { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); }
 tr { padding:10px 0; border-bottom:1px solid var(--edge); }
 td { border:0; padding:2px 0; }
 td::before { content:attr(data-label); display:block; color:var(--muted);
  font-size:var(--step--1); letter-spacing:.04em; }
 td:empty { display:none; }
 td:first-child { font-weight:600; padding-top:6px; }
 /* Dense ledger records: label and value on one line, the sub-line under the value. */
 .ledger td, .at-risk td { display:grid; grid-template-columns:6.2rem minmax(0,1fr);
   gap:0 10px; padding:4px 10px; }
 .ledger td::before, .at-risk td::before { margin:0; padding:0; grid-column:1; grid-row:1; }
 .ledger td > .cell-value, .at-risk td > .cell-value { grid-column:2; grid-row:1; min-width:0; }
 .ledger td > .cell-sub, .ledger td > .mark-detail,
 .at-risk td > .cell-sub, .at-risk td > .mark-detail { grid-column:2; grid-row:auto; }
 .ledger td:first-child, .at-risk td:first-child { padding-top:10px; }
 .ledger td:last-child, .at-risk td:last-child { padding-bottom:10px; }
}
@media (max-width:760px) {
 main { padding:24px 16px 48px; }
 .grid { gap:28px 0; }
 .span-4,.span-6 { grid-column:span 12; }
 .attention { padding:14px 14px 16px; border-left-width:6px; }
 .attention-body { grid-template-columns:1fr; gap:6px; }
 .attention-figure { font-size:var(--step-3); margin-bottom:2px; }
 .attention-figure small { margin-top:4px; }
 .attention-verdict h3 { font-size:var(--step-1); line-height:1.25; margin-bottom:6px; }
 /* The qualifier stays at body size on mobile (design contract, r6 M7). */
 .attention-qualifier { margin-bottom:8px; }
 .attention-verdict > p { margin-bottom:6px; }
 .attention-notes { grid-template-columns:1fr; gap:6px; margin-top:10px; padding-top:10px; }
 .today { padding:16px; }
 .action-list li { grid-template-columns:2.5rem 1fr; gap:8px; padding:10px 0; }
 .action-source { grid-column:2; text-align:left; }
 .action-why { font-size:var(--step--1); }
 .card-row { grid-template-columns:1fr; gap:16px; }
 .runway-math div { min-width:8rem; }
}
@media print {
 body { background:#fff; color:#000; }
 main { max-width:none; padding:0; }
 .skip-link { display:none; }
 .masthead-status { position:static; }
 a { color:#000; text-decoration:underline; }
 .attention,.today { break-inside:avoid; }
 .disclosure { break-inside:avoid; }
 .disclosure > summary { color:#000; }
}
@media (prefers-reduced-motion:reduce) {
 *,*::before,*::after { animation:none!important; transition:none!important; scroll-behavior:auto!important; }
}
"""


CHANNEL_LABELS = {
    "retailer_history_import": "Retailer history import",
    "normal_store": "Regular grocery store",
    "in_store": "In-store capture",
    "online": "Online order",
    "unknown": "Unknown channel",
}


def page_shell(header_html: str, status_html: str, panels_html: str) -> str:
    """Assemble a local document without fetched assets or fonts."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Grocery Flywheel Dashboard</title>
  <style>{CSS}</style>
</head>
<body>
  <a class="skip-link" href="#household-review">Skip to household review</a>
  <main id="dashboard" tabindex="-1">
    <header class="masthead">
      <p class="eyebrow">Your household ledger &middot; local and private</p>
      <h1>Grocery Flywheel</h1>
      {header_html}
    </header>
    {status_html}
    <section id="household-review" tabindex="-1" class="grid" aria-label="Household review">
{panels_html}
    </section>
    <footer>
      <p><strong>About these numbers.</strong> Runway and totals are estimates from the
      records in your state file, not a pantry audit. Prices are not live retailer
      prices. A dietary warning is not a clearance. No retailer connection. No
      checkout. Review every suggestion yourself. This page does not save approvals
      or changes to your household state.</p>
      <p>Collapsed sections print as their titles only; open a section before printing
      to include its detail.</p>
    </footer>
  </main>
</body>
</html>
"""


def header_line(analysis: dict) -> str:
    order = analysis["order"]
    surface = analysis.get("inventory_surface") or {}
    surface_label = surface.get("label") or surface.get("type") or "Inventory surface"
    channel = CHANNEL_LABELS.get(str(analysis.get("acquisition_channel") or ""),
                                 humanize_key(str(analysis.get("acquisition_channel", "unknown"))))
    objective = analysis.get("objective_label")
    warnings = analysis.get("data_warnings") or []
    warning_html = (
        "<p class='masthead-notes' style='color:var(--ochre)'>Warning: "
        + escape(" ".join(str(w) for w in warnings)) + "</p>"
        if warnings else ""
    )
    objective_html = (f"<p class='masthead-notes'>Objective: {escape(str(objective))}.</p>"
                      if objective else "")
    return (
        "<div class=\"masthead-meta\">"
        f"<span>{escape(str(surface_label))} via {escape(channel)}</span>"
        f"<span>Order <b>{escape(str(order['store']))}</b>, {escape(human_date(order['date']))}</span>"
        f"<span>Order total <b>${float(order['total']):.2f}</b></span>"
        f"<span>As of <b>{escape(human_date(analysis['as_of']))}</b></span>"
        f"<span>{int(analysis.get('days_elapsed') or 0)} days observed</span>"
        "</div>"
        f"{objective_html}"
        f"{warning_html}"
    )


MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def human_date(value: object) -> str:
    """Render an ISO engine date as a household-readable date; never invent one."""
    text = str(value or "").strip()
    parts = text.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        year, month, day = (int(p) for p in parts)
        if 1 <= month <= 12:
            return f"{day} {MONTHS[month - 1]} {year}"
    return text or "date unknown"


def humanize_key(value: object) -> str:
    """Turn an engine key into a readable phrase, keeping the raw key out of prose."""
    text = str(value or "").replace("_", " ").strip()
    return text[:1].upper() + text[1:] if text else ""
