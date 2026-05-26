# Active Execution Board

Updated: 2026-05-20
Scope: local brain-dump workspace plus Vons draft pickup cart work. No Gmail, Calendar, GitHub, checkout, payment, or order-finalization actions were executed in this pass.

## Completed Actions With Evidence

| Done | Evidence |
| --- | --- |
| Workspace file map inspected. | `rg --files` found local folders `00-inbox/`, `01-ai-flywheel/`, `02-content-engine/`, `03-ops-inbox-calendar-files/`, `04-research/`, and `90-archive/`. |
| No nested workspace instructions found. | `find . -name AGENTS.md` returned no child `AGENTS.md` files under this workspace. |
| Existing inbox operating rule identified. | `00-inbox/README.md` says raw items must become next actions, flywheel notes, content notes, research notes, or archive/reference items. |
| Prior inbox cleanup actions captured from local notes. | `03-ops-inbox-calendar-files/inbox-action-queue.md` records 33 Facebook notifications archived, 705 LinkedIn job alerts archived, 901 Gmail Promotions archived, Codex labels applied, Honda draft deleted, and Norm Reeves threads labeled. |
| Current inbox action counts captured from local notes. | `03-ops-inbox-calendar-files/inbox-action-queue.md` records Inbox `8,932`, unread `8,137`, `Codex/Action` `10`, `Codex/Finance` `5`, and `Codex/GitHub Review` `7`. |
| Current action items captured from local notes. | `03-ops-inbox-calendar-files/inbox-action-queue.md` lists PuenteWorks banking/W-9, Norm Reeves/Honda Financial, Amex payment verification, Capital One Apple Pay verification, GitHub PR review/check work, and FedEx/Chewy delivery. |
| Vons pickup draft cart optimized and recorded. | `03-ops-inbox-calendar-files/vons-pickup-draft.md` records the 18-item draft cart, $89.03 estimated subtotal after savings, pickup store, unit-price decisions, no-thought food stack, non-organic tradeoffs, and no-checkout status. |
| Vons cart decision analysis created. | `03-ops-inbox-calendar-files/vons-cart-decision-analysis.md` compares the major cart decisions visually by unit cost, executive-function role, replacement logic, and ROI rank. |
| Vons moka-pot coffee correction executed. | `03-ops-inbox-calendar-files/vons-moka-coffee-analysis.md` now records the user correction: Lavazza was removed and 2 Cafe Bustelo vacuum-pack bricks were added because Bustelo wins on price-per-function for moka-pot daily coffee. |
| Vons required additions executed. | Live cart verified `Cart (23)`, $113.08 after savings / $135.07 before savings; Chocolate Fairlife was already present, Florida's Natural Ruby Red Grapefruit Juice was added, and the remembered "bear" chicken was found as Just Bare and added as the Buy Again fillets. |
| Cluster baseline captured. | `01-ai-flywheel/ai-flywheel-baseline-2026-05-20.md` records the Mac mini M4 control plane, NUC, MacBook Pro, MacBook Air, Dell XPS, Jetson, GMKTech, Android TV projector, and VPS roles. |
| Live cluster inventory captured. | `01-ai-flywheel/cluster-inventory-live.json` records `simons-mac-mini`, `nucbox`, `simons-macbook-air`, `simons-macbook-pro`, and `srv1542844` with Tailscale IPs and current access status. |
| MacBook Pro cleanup direction corrected away from wipe. | `01-ai-flywheel/macbook-pro-cleanup-policy.md` says the active plan is cleanup, not wipe; `01-ai-flywheel/macbook-pro-m1-wipe-runbook.md` says the wipe runbook is superseded. |
| Video triage evidence captured. | `02-content-engine/video-triage.md` records two broken MP4s with `moov atom not found`, one healthy MOV, and a generated contact sheet path. |

## Blocked Items With Exact Blocker

| Blocked Item | Exact Blocker | Evidence |
| --- | --- | --- |
| Remote MacBook Pro cleanup execution | SSH authentication is rejected for the available MacBook Pro accounts; control is not established. | `01-ai-flywheel/macbook-pro-cleanup-policy.md` says SSH auth is rejected for `simon` and `simongonzalezdecruz`; `01-ai-flywheel/macbook-pro-m1-bringup.md` says SSH fails with `Permission denied (publickey,password,keyboard-interactive)`. |
| MacBook Pro worker bootstrap | Same access blocker as cleanup: Remote Login/key/GUI access must work before installing or verifying worker dependencies. | `01-ai-flywheel/macbook-pro-cleanup-runbook.md` requires `ssh simongonzalezdecruz@100.123.79.5 'hostname; whoami; sw_vers -productVersion'` before cleanup. |
| Recent tarot/singing MP4 import | Both recent Desktop MP4s are unreadable because the MP4 metadata atom is missing. | `02-content-engine/video-triage.md` and `02-content-engine/README.md` say `ffprobe` / remux failed with `moov atom not found`. |
| NUC model-serving use | Checked model ports are closed, so no model server is currently exposed on the recorded ports. | `01-ai-flywheel/cluster-inventory-live.json` records closed ports for LM Studio `1234`, Ollama `11434`, llama-server `8080`, and llama RPC `50052`. |
| External inbox/calendar/GitHub execution | Current instruction forbids touching Gmail, Calendar, and external repos. | User instruction for this lane: inspect workspace files only; do not touch Gmail/Calendar/external repos. |
| Dell XPS Linux wipe/install | Destructive wipe/install is not authorized in this lane. | `01-ai-flywheel/hardware-topology.md` says Linux wipe/install is under consideration; destructive wipe requires explicit go. |
| Calendar scheduling | Live calendar connector/access is not available in this Codex session. | `03-ops-inbox-calendar-files/README.md` says live calendar access is not currently available and calendar work should be staged as proposed blocks. |
| Vons cart count discrepancy and user removals | Earlier local note recorded 18 items, but the later live Vons cart showed 14 before coffee. After removing Lavazza and adding 2 Bustelo bricks, live cart showed 16 items and $82.54 after savings. After required additions, live cart showed 23 items and $113.08 after savings. | `03-ops-inbox-calendar-files/vons-pickup-draft.md` records the discrepancy, inferred removed items, the coffee correction, and the required additions. |

## Next 10 Executable Actions Ranked By ROI

| ROI Rank | Action | Specific Tool / Action Needed | Output |
| --- | --- | --- | --- |
| 1 | Unlock MacBook Pro remote control. | On the MacBook Pro GUI: enable Remote Login for the real admin account or add the Mac mini SSH public key to that admin account. Then run `ssh simongonzalezdecruz@100.123.79.5 'hostname; whoami; sw_vers -productVersion'` from the Mac mini. | A passing SSH identity check or the exact remaining SSH error. |
| 2 | Run MacBook Pro inventory without deleting anything. | After SSH works, run the Phase 1 commands from `01-ai-flywheel/macbook-pro-cleanup-runbook.md`: `df -h /`, `du -sh ~/*`, large-file find, and `/Applications` app list. | Disk/app inventory and keep/delete/review candidates. |
| 3 | Update cluster inventory with verified MacBook Pro facts. | Edit `01-ai-flywheel/cluster-inventory-live.json` after the SSH inventory returns hardware, OS, disk, and tooling facts. | MacBook Pro record moves from `tailscale_visible_ssh_denied` to verified reachable state. |
| 4 | Verify NUC model server state from the NUC itself. | Run SSH to `nucbox` / `100.113.174.74` and check local listeners with `ss -ltnp` plus LM Studio/Ollama/llama-server process checks. | Confirmed reason ports are closed: service stopped, bound to localhost, different port, or missing. |
| 5 | Start or expose exactly one NUC OpenAI-compatible model endpoint. | Use the existing NUC model server path documented by The Factory; verify with `curl http://100.113.174.74:<port>/v1/models`. | One reachable model endpoint for routing experiments. |
| 6 | Recover or replace source video for content pipeline. | Use `ffprobe` on original files, then either recover from a healthy source/export, use the healthy MOV at `Downloads/fb14c53e19f041c6b9ac0ff423906e98.MOV`, or re-record the tarot/singing clip. | One decodable source video path for Kyanite Studio import. |
| 7 | Run a fresh keyframe/contact-sheet pass on the valid source video. | Use `ffmpeg` to extract keyframes and generate a contact sheet under `02-content-engine/keyframes/<asset-id>/`. | Inspectable visual sheet tied to the real source asset. |
| 8 | Convert the inbox action queue into a top-five execution pass. | In Gmail only when allowed: open `Codex/Action`, `Codex/Finance`, and `Codex/Norm Reeves`; execute or draft the highest-risk item first. | Five items moved from categorized to handled, waiting, or explicitly blocked. |
| 9 | Resolve GitHub review/check queue only when external repo access is allowed. | Use `gh pr view` for `KyaniteLabs/mcp-video#310`, `#309`, and `KyaniteLabs/Elixis#92`; inspect comments/checks before editing anything. | Each PR marked merge-ready, needs-fix, or blocked with exact reason. |
| 10 | Stage calendar blocks from local priorities without live calendar writes. | Edit only the local ops note first: propose blocks for MacBook Pro unlock, NUC endpoint verification, content source recovery, and inbox finance/car review. | Local calendar staging list ready for connector-backed scheduling later. |

## Current Stop Condition

This lane stops here because the Vons pickup cart was updated into a draft-only, approval-ready state and the local decision record now captures both the cart and the low-executive-function meal logic. No checkout, payment, or order finalization was executed.
