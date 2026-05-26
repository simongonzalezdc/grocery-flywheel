# Dell XPS 17 Linux Plan

Status: candidate plan only. Wiping/repartitioning is destructive and must not happen until explicitly authorized for that machine.

## Recommendation

Yes, Linux is probably the correct direction for the Dell XPS 17 if the goal is CUDA, video models, vLLM/SGLang, llama.cpp MTP, and stable remote worker behavior.

## Why The Dell Matters

The Dell is likely the cleanest CUDA experiment node:

- NVIDIA GPU support is the main unlock.
- Mobile-VideoGPT and Qwen video experiments are CUDA-first.
- llama.cpp MTP and speculative decoding should be benchmarked on NVIDIA.
- vLLM/SGLang support will be more natural than on Apple Silicon or Jetson.

## OS Choice

Current source check:

- Ubuntu 26.04 LTS was released on 2026-04-23 and is supported until April 2031.
- Canonical says Ubuntu 26.04 LTS includes native AI/ML toolkit support such as NVIDIA CUDA and AMD ROCm.
- NVIDIA CUDA installation docs remain the source of truth for validated CUDA distributions and install methods.

Practical recommendation:

- Prefer Ubuntu LTS.
- Use Ubuntu 26.04 LTS if the Dell GPU, driver branch, and CUDA tooling validate cleanly.
- Fall back to Ubuntu 24.04 LTS if a specific CUDA/vLLM/PyTorch stack is more mature there.

Sources:

- Ubuntu 26.04 LTS release: https://ubuntu.com/blog/canonical-releases-ubuntu-26-04-lts-resolute-raccoon
- Ubuntu 26.04 release notes: https://documentation.ubuntu.com/release-notes/26.04/
- NVIDIA CUDA Linux installation guide: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html

## Safe Pre-Wipe Checklist

Before any wipe:

1. Identify exact Dell model, CPU, GPU, VRAM, RAM, SSD layout.
2. Confirm whether any files, licenses, browser profiles, SSH keys, or app configs need backup.
3. Create recovery media or confirm Windows recovery is not needed.
4. Download Ubuntu installer and prepare a USB.
5. Confirm BIOS settings: Secure Boot, SATA/NVMe mode, virtualization, boot order.
6. Decide full wipe vs dual boot. For the flywheel, full wipe is cleaner.

## Post-Install Target State

Install:

- Tailscale
- OpenSSH server
- NVIDIA driver
- CUDA toolkit
- Docker with NVIDIA container runtime
- Python/uv
- git/GitHub CLI
- ffmpeg
- llama.cpp CUDA build
- vLLM or SGLang test environment

Run first benchmark:

```bash
nvidia-smi
nvcc --version
python3 - <<'PY'
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda')
PY
```

Then run llama.cpp/vLLM model benchmarks and add results to the cluster inventory.

