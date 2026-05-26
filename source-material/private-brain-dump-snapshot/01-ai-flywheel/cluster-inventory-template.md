# Cluster Inventory Template

Use this for every node before assigning production work.

## Node Record

| Field | Value |
| --- | --- |
| Name |  |
| Hostname |  |
| Tailscale IP |  |
| LAN IP |  |
| OS |  |
| CPU |  |
| RAM |  |
| GPU / accelerator |  |
| VRAM / unified memory |  |
| Always on? |  |
| Power/network notes |  |
| Primary role |  |
| Secondary role |  |
| Do-not-use-for |  |

## Access

| Check | Status |
| --- | --- |
| Tailscale visible |  |
| SSH reachable |  |
| Auth works |  |
| Screen sharing / remote GUI |  |
| Admin available |  |

## Tooling

| Tool | Version / Status |
| --- | --- |
| Tailscale |  |
| SSH |  |
| Homebrew / apt |  |
| git |  |
| gh |  |
| Python / uv |  |
| Node |  |
| ffmpeg |  |
| cmake |  |
| Docker |  |
| NVIDIA driver / Metal |  |
| CUDA / ROCm |  |
| Ollama |  |
| llama.cpp |  |
| LM Studio |  |
| vLLM / SGLang |  |

## Benchmarks

| Workload | Model | Backend | Result |
| --- | --- | --- | --- |
| llama.cpp decode |  |  |  |
| llama.cpp prefill |  |  |  |
| OpenAI-compatible chat latency |  |  |  |
| video/keyframe analysis |  |  |  |
| ffmpeg transcode |  |  |  |

## Routing Decision

Production roles:

- `orchestrator`
- `coding-inference`
- `vision-video`
- `media-preprocess`
- `dashboard-client`
- `burst-worker`
- `public-webhook`

Final assignment:

- Primary:
- Secondary:
- Notes:

