# Hardware Topology

This is the current working topology for the AI flywheel. It is evidence plus role assignment, not a final infrastructure diagram.

## Nodes

| Node | Known Facts | Best Role | ROI Judgment |
| --- | --- | --- | --- |
| Mac mini M4 | Active host, 16 GB RAM, Tailscale, ffmpeg, Ollama, cmake | Orchestrator, UI, router, local light inference, media pipeline control | Primary always-on control plane |
| Linux NUC / Ubuntu node | Active on Tailscale as `nucbox`; The Factory docs say LM Studio hosts Qwen models | Self-hosted coding/review/summarization inference | Verify first because it is already integrated |
| MacBook Pro M1 Pro | Tailscale node exists; user is bringing it online now | Clamshell Apple-Silicon worker, backup orchestrator, Metal inference | First bring-up priority |
| MacBook Air | Active on Tailscale | Opportunistic burst worker, portable capture/client | Useful but not a dependency |
| Dell XPS 17 NVIDIA | User reports a discrete graphics card; Linux wipe/install is under consideration | CUDA lab node for llama.cpp MTP, vLLM/SGLang, Mobile-VideoGPT, Qwen video | Potentially highest experiment throughput; destructive wipe requires explicit go |
| Jetson Orin Nano 8 GB | 6-core ARM Cortex CPU, 8 GB RAM | Edge video/vision node, Mobile-VideoGPT experiment, camera/projector sidecar | Do not use as general LLM node |
| GMKTech G2 Plus | Brand new small PC | Client, dashboard kiosk, queue monitor, file-ingest station, remote-control terminal | Good utility node, probably not inference-first |
| Android TV projector | Smart projector with embedded Android computer | Ambient dashboard, video review wall, content playback, household status display | High experiential leverage, low compute expectations |
| VPS / srv1542844 | Tailscale node visible | Public endpoint, dashboard, cron/automation, webhook target | Internet-facing glue, not local heavy compute |

## Role Principle

Use **capability routing**:

- Strong inference boxes serve models.
- Weak or tiny computers become clients, dashboards, capture stations, routers, or edge sensors.
- The best flywheel is measured throughput plus a queue, not every device running the same workload.

## Immediate Additions From Latest Brain Dump

GMKTech G2 Plus:

- Make it a low-power always-on client.
- Candidate jobs: inbox/file dropbox, Tailscale dashboard, Grafana/status screen, model-router control panel, kiosk for The Factory, local network utility box.
- Avoid making it a first inference target unless benchmarks prove a useful tiny-model niche.

Android TV projector:

- Treat as an output surface: status wall, content review theater, ambient calendar, “what should I do next?” queue, tarot/video playback.
- Possible fun/high-ROI use: a living-room AI operations wall fed by the Mac mini or GMKTech, not compute running on the projector itself.
