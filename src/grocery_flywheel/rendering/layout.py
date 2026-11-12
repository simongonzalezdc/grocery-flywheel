"""Self-contained warm pantry-ledger shell; analysis stays in the engine."""
from __future__ import annotations

from html import escape

CSS = """
:root {
  color-scheme: light;
  --bg:#F6F1E7; --panel:#FFFDF8; --panel-edge:#D8CCB6;
  --ink:#241F19; --muted:#5A5145; --green:#3F6B45; --green-dim:#3F6B45;
  --blue:#2F5E86; --gold:#8A5B12; --red:#A32D22; --copper:#A2512A;
  --display:"Iowan Old Style",Palatino,"Palatino Linotype",Georgia,serif;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;
  font-size:1rem; line-height:1.6; font-variant-numeric:tabular-nums; }
main { max-width:1184px; margin:auto; padding:32px 24px 80px; }
header { border-bottom:2px solid var(--ink); padding-bottom:24px; margin-bottom:32px; }
h1,h2,h3,p { margin:0 0 12px; }
h1 { font-family:var(--display); font-size:clamp(2rem,5vw,3.5rem); line-height:1.1; font-weight:600; }
h2 { font-family:var(--display); font-size:1.6rem; font-weight:600; line-height:1.2; }
header p { max-width:75ch; }
.eyebrow { text-transform:uppercase; letter-spacing:.15em; font-size:.8rem; color:var(--muted); }
.grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:24px; }
.panel { min-width:0; background:transparent; border:0; border-top:1px solid var(--panel-edge);
  padding:24px 0; overflow-wrap:anywhere; }
.span-4 { grid-column:span 4; } .span-6 { grid-column:span 6; } .span-12 { grid-column:span 12; }
.metric { font-family:var(--display); font-size:2.4rem; font-weight:600; line-height:1.2; margin:8px 0; }
.muted { color:var(--muted); }
.card-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:32px; }
.card-row h2 { font-family:inherit; font-size:.85rem; letter-spacing:.08em; text-transform:uppercase; }
.card-row > div { min-width:0; }
.attention { background:#EFE8DA; border-left:4px solid var(--gold); padding:24px; }
.attention h2 { color:var(--gold); }
.review-task { background:var(--panel); border-top:5px solid var(--ink); padding:24px; }
.review-task > h2 { font-size:2rem; }
.section-intro { color:var(--muted); max-width:66ch; }
.approve-note { color:var(--gold); }
.wow { border-left:0; }
.tag { display:inline-block; border:1px solid var(--panel-edge); border-radius:3px;
  padding:3px 9px; margin:3px 4px 3px 0; font-size:.85rem; }
.tag.critical { border-color:var(--red); color:var(--red); }
.tag.review { border-color:var(--gold); color:var(--gold); }
.tag.ok { border-color:var(--green); color:var(--green); }
table { width:100%; border-collapse:collapse; table-layout:fixed; font-size:.95rem; }
th,td { border-bottom:1px solid var(--panel-edge); padding:14px 8px; text-align:left;
  vertical-align:top; overflow-wrap:anywhere; }
th { color:var(--muted); font-size:.8rem; font-weight:600; }
.bar { height:8px; background:#E3D9C6; border-radius:2px; overflow:hidden; }
.bar > span { display:block; height:100%; background:var(--green-dim); }
button,select,.download-link { font:inherit; color:var(--ink); background:var(--panel);
  border:1px solid var(--panel-edge); border-radius:3px; padding:10px 14px;
  min-height:44px; max-width:100%; }
button { cursor:pointer; } button:hover { border-color:var(--copper); }
button.primary { background:var(--copper); border-color:var(--copper); color:#FFF8F1; }
button.primary:hover { background:#8A4222; }
a { color:var(--copper); }
:focus-visible { outline:3px solid #7A3A1C; outline-offset:3px; }
.skip-link { position:absolute; left:-9999px; top:0; padding:12px; background:var(--panel); }
.skip-link:focus { left:12px; top:12px; z-index:2; }
details { margin:8px 0; min-width:0; }
summary { cursor:pointer; padding:12px 0; min-height:44px; color:var(--muted); }
.disclosure { grid-column:span 12; border-top:1px solid var(--panel-edge); }
.disclosure > summary { font-size:1.15rem; color:var(--ink); }
.disclosure .panel { border-top:0; padding:16px 0; }
footer { margin-top:48px; border-top:2px solid var(--ink); padding-top:24px; color:var(--muted); }
@media (max-width:760px) {
 main { padding:24px 16px 48px; }
 .span-4,.span-6 { grid-column:span 12; }
 .card-row { grid-template-columns:1fr; gap:20px; }
 .attention,.review-task { padding:20px 16px; }
 table,tbody,tr,td { display:block; width:100%; }
 thead { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); }
 tr { padding:12px 0; border-bottom:1px solid var(--panel-edge); }
 td { border:0; padding:5px 0; }
 td::before { content:attr(data-label); display:block; color:var(--muted); font-size:.8rem; }
 td:first-child { font-weight:600; }
}
@media (prefers-reduced-motion:reduce) {
 *,*::before,*::after { animation:none!important; transition:none!important; scroll-behavior:auto!important; }
}
"""


def page_shell(header_html: str, panels_html: str) -> str:
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
  <a class="skip-link" href="#dashboard">Skip to household review</a>
  <main id="dashboard" tabindex="-1">
    <header>
      <p class="eyebrow">Your household ledger · local and private</p>
      <h1>Grocery Flywheel</h1>
      {header_html}
    </header>
    <section class="grid" aria-label="Household review">
{panels_html}
    </section>
    <footer>No retailer connection. No checkout. Review every suggestion yourself.
      This page does not save approvals or changes to your household state.</footer>
  </main>
</body>
</html>
"""


def header_line(analysis: dict) -> str:
    order = analysis["order"]
    surface = analysis.get("inventory_surface") or {}
    surface_label = surface.get("label") or surface.get("type") or "Inventory surface"
    channel = analysis.get("acquisition_channel", "unknown")
    objective = analysis.get("objective_label")
    objective_note = f" Objective: {escape(str(objective))}." if objective else ""
    warnings = analysis.get("data_warnings") or []
    warning_html = (
        "<p style='color: var(--gold)'>⚠ " + escape(" ".join(warnings)) + "</p>"
        if warnings else ""
    )
    return (
        f"<p>{escape(str(surface_label))} via {escape(str(channel))}. "
        f"{escape(order['store'])} run from {escape(order['date'])}, "
        f"analyzed as of {escape(analysis['as_of'])}.{objective_note}</p>"
        f"{warning_html}"
    )
