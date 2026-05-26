# AI Flywheel Baseline and ROI Stack

Date: 2026-05-20
Workspace: `/Users/simongonzalezdecruz/Documents/Codex/2026-05-19/this-is-a-high-priority-brain`

## Executive Baseline

Highest-leverage conclusion: the setup should compound through **capability routing**, not through one giant heterogeneous distributed model. The machines should expose reliable per-node services, report metrics, and receive work by role:

- Mac mini M4 16 GB: orchestration, UI, queueing, light local inference, video/content pipeline control.
- Linux NUC / Ubuntu node: already the strongest self-hosted inference lane in The Factory, with LM Studio-hosted Qwen models documented as the major zero-cost upgrade.
- MacBook Pro M1 Pro: bring back as a clamshell Apple-Silicon inference/agent runner node.
- MacBook Air: opportunistic burst worker, not a primary always-on service.
- Dell XPS 17 with NVIDIA GPU: likely the best CUDA lab node for llama.cpp MTP, vLLM/SGLang, Mobile-VideoGPT, and Qwen video experiments.
- Jetson Orin Nano 8 GB: edge vision/video node, not a general large-LLM worker.
- GMKTech G2 Plus: small client/control-plane node, probably better as dashboard, file-ingest, router/control UI, or kiosk than inference.
- Android TV projector: ambient output surface for dashboards, video review, calendar, queue visibility, and content playback.
- VPS / srv1542844: public service surface, cron jobs, dashboards, queue control, and external-access glue.

Current local evidence:

- Active machine is `Mac mini (Mac16,10), Apple M4, 10 cores, 16 GB RAM`, macOS 26.4.
- Installed locally: `ollama`, `ffmpeg`, `tailscale`, `ssh`, `cmake`; `llama-server` / `llama-cli` are not currently on PATH.
- Tailscale currently sees `nucbox` active, `simons-macbook-air` active, `srv1542844` idle, and `simons-macbook-pro` offline for 65 days.
- The Factory already documents a move from local Ollama to an external LM Studio NUC endpoint with Qwen3.5/Qwen3-Coder models.
- The Kyanite Vocal Tarot Studio worktree exists and has real studio tests passing: 11 targeted tests passed.
- The recent Desktop videos exist, but `ffprobe` reports `moov atom not found`, so they are not currently readable MP4s.

## ROI Priority Stack

### P0: Make The AI Flywheel Measurable

Build a single node inventory and benchmark harness before changing architecture.

Output to collect per node:

- Hostname, Tailscale IP, OS, CPU, RAM, GPU/VRAM, backend: Metal/CUDA/CPU/Vulkan.
- Available model server: LM Studio, llama.cpp, Ollama, vLLM, SGLang.
- Models available, context length, quant, tokens/sec prefill, tokens/sec decode, max stable concurrency.
- Health endpoint, metrics endpoint, and routing role.

Why this is highest ROI: every later choice depends on measured throughput, not vibes. The Factory already has model routing assumptions; the cluster needs the same discipline across all machines.

### P1: Use Per-Node Servers, Not One Giant Distributed Inference Cluster

Production default:

- Run independent OpenAI-compatible servers per node.
- Put a simple router in front of them.
- Route by capability: coding, summarization, vision, video, batch cleanup, verifier, edge camera/video.

Lab-only:

- llama.cpp RPC can expose remote devices over TCP/RDMA, but treat it as experimental and private-network-only.
- Do not build the main flywheel around cross-machine tensor/model splitting until it beats per-node routing in benchmarks.

Primary source:

- llama.cpp RPC docs: https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md
- llama.cpp README backend support: https://github.com/ggml-org/llama.cpp

### P2: Immediate Cluster Bring-Up Order

1. Reconnect the MacBook Pro M1 Pro to Tailscale, power, Ethernet if possible, clamshell mode, SSH, and a persistent model server. This is now the fastest first hardware win.
2. Verify the NUC LM Studio endpoint from The Factory and record actual active models.
3. Add the Dell XPS 17 as the CUDA experiment node for llama.cpp MTP, vLLM/SGLang, and video models. Linux is the preferred direction, but wiping remains gated on explicit authorization.
4. Install JetPack / CUDA / PyTorch on the Jetson Orin Nano and assign it only edge-video tasks.
5. Put the GMKTech G2 Plus on the network as a tiny always-on client/dashboard/control terminal.
6. Use the Android TV projector as a status wall and content review surface.
7. Keep MacBook Air opportunistic; do not let it block the always-on topology.

### P3: llama.cpp MTP and Speculative Decoding

Current state:

- llama.cpp speculative docs now list `draft-mtp` plus n-gram speculative modes.
- MTP support for Qwen3.6 landed very recently in llama.cpp PR #22673.
- `ngram-mod` is lower-risk and should be A/B tested first for code edits, transcript cleanup, and repeated-token workloads.

Benchmark lanes:

```bash
llama-server -m model.gguf --spec-default --metrics

llama-server -m model.gguf \
  --spec-type ngram-mod \
  --spec-ngram-mod-n-match 24 \
  --spec-ngram-mod-n-min 48 \
  --spec-ngram-mod-n-max 64 \
  --metrics

llama-server -hf ggml-org/Qwen3.6-27B-MTP-GGUF \
  --spec-type draft-mtp \
  --spec-draft-n-max 2 \
  --metrics
```

Primary sources:

- llama.cpp speculative docs: https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md
- llama.cpp MTP PR: https://github.com/ggml-org/llama.cpp/pull/22673

### P4: Video Model Decision

Likely model from the YouTube clue:

1. **Mobile-VideoGPT-0.5B**: best match for “small Qwen plus lightweight vision/video stack” and the Jetson Orin Nano goal.
2. **Qwen3.5-0.8B**: newer native tiny multimodal Qwen model with image/video input and MTP-serving recipes.
3. **FastVLM-0.5B**: best Apple-first real-time visual captioning lane, weaker as true temporal video.
4. **Qwen2.5-VL-3B**: larger, higher-quality fallback when exact video reasoning matters more than sub-1B edge fit.

First implementation:

- Dell XPS 17: run Mobile-VideoGPT and Qwen3.5-0.8B via CUDA stack.
- Jetson: Mobile-VideoGPT-0.5B first because it has the strongest edge-video fit.
- Mac mini / MacBook Pro: FastVLM or Qwen3.5 image/keyframe lane first; do not make them the first video temporal benchmark.

Primary sources:

- Mobile-VideoGPT: https://huggingface.co/Amshaker/Mobile-VideoGPT-0.5B
- Mobile-VideoGPT repo: https://github.com/Amshaker/Mobile-VideoGPT
- Qwen3.5-0.8B: https://huggingface.co/Qwen/Qwen3.5-0.8B
- FastVLM: https://huggingface.co/apple/FastVLM-0.5B

### P5: Kyanite Vocal Tarot Content Pipeline

Current local state:

- Existing worktree: `/Users/simongonzalezdecruz/workspaces/content-factory-app-kyanite-vocal-tarot`
- Existing app plan: `/Users/simongonzalezdecruz/Desktop/Content Studio.app/.omx/plans/prd-kyanite-vocal-tarot-studio-20260514T050953Z.md`
- Code already has studio sessions, layers, local storage, export spec generation, Kyanite terminology guardrails, and PENDING export records.
- Targeted tests passed: `node --import tsx --test src/lib/studio/kyanite-studio.test.ts src/lib/studio/storage.test.ts`

Gap:

- Export currently persists deterministic intent; it does not actually render final TikTok output yet.
- The two recent Desktop MP4 files are currently unreadable because the MP4 metadata atom is missing.

Highest-ROI content move:

1. Recover or replace the unreadable MP4s.
2. Feed a valid video into the Kyanite Studio import flow.
3. Add a real render worker that turns export intent into an MCP Video output.
4. Use vision/keyframes for tarot card identification, but keep exact card ID auditable.
5. Publish the first rough clip fast; treat polish as iteration two.

### P6: Tarot Vision Workflow

Best architecture:

`video -> keyframes -> blur filter -> card crop -> reference match -> vision/API verifier -> controlled meaning corpus -> captions/export`

Do not rely only on a general vision model to “guess tarot.” Exact card identification is deck-dependent and should be matched against a reference deck where possible.

API/local hybrid:

- Use video models or Gemini-style video input to find reveal moments.
- Use frame crops and reference matching for exact card ID and orientation.
- Use a controlled meanings library for interpretation.
- Send only uncertain crops to stronger API vision.

### P7: Stone / Symbolism Notes For Content

Use these as poetic content cues, not medical/scientific claims.

- Lapis lazuli: truth, wisdom, spiritual authority, clear seeing.
- Carnelian: vitality, courage, luck, embodied creative fire.
- Flint: survival, protection, spark, decisive action.

Suggested Kyanite-language translation:

- Lapis lazuli = signal clarity / authority of the blue channel.
- Carnelian = activation energy / embodied throughput.
- Flint = ignition primitive / survival spark / decisive edge.

## Immediate Next Actions

1. Build `cluster-inventory.json` from Tailscale + SSH + per-node probes.
2. Bring MacBook Pro M1 Pro back online as a clamshell node.
3. Verify NUC LM Studio endpoint and The Factory model routing still works.
4. Prepare Dell XPS 17 as CUDA benchmark node.
5. Setup Jetson Orin Nano only after the router and benchmark harness exist.
6. Recover or re-record valid tarot/singing video assets.
7. Finish Kyanite Studio render worker so the app outputs actual clips, not just export intent.

## Open Questions To Elicit Later

Ask only when execution requires the answer:

- Where is the Dell XPS 17 on the network, and what NVIDIA GPU/VRAM does it have?
- Is the Jetson currently flashed with JetPack, and can it join Tailscale?
- Is the MacBook Pro physically available for clamshell setup now?
- Were the broken videos created by the same recorder/app as any healthy sample video we can use for MP4 repair?
- Which deck was used in the videos?
