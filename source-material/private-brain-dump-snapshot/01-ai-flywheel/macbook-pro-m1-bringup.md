# MacBook Pro M1 Pro Bring-Up

Status: user says the MacBook Pro M1 is coming online now.

Last checked from Mac mini:

- Tailscale entry: `simons-macbook-pro`, `100.123.79.5`
- Tailscale now reports the node active/direct.
- TCP port 22 is open.
- SSH currently fails with `Permission denied (publickey,password,keyboard-interactive)`, so control is not established yet.

Wipe/reset runbook: `01-ai-flywheel/macbook-pro-m1-wipe-runbook.md`

## First Bring-Up Target

This is now the fastest first hardware win.

Minimum useful online state:

1. Power connected.
2. Tailscale connected.
3. SSH reachable from the Mac mini.
4. Hostname and hardware facts recorded.
5. Persistent role assigned.

## Proposed Role

Use it as a clamshell Apple-Silicon worker:

- Metal inference for medium local models.
- Backup agent runner.
- Media preprocessing/transcoding helper.
- Local file mirror / sync client.
- Secondary dashboard/client if the Mac mini is busy.

## Verification Commands

From the Mac mini:

```bash
tailscale status | rg 'simons-macbook-pro'
ssh -o BatchMode=yes -o ConnectTimeout=5 simon@100.123.79.5 'hostname; sw_vers -productVersion; uname -m'
```

After SSH works:

```bash
ssh simon@100.123.79.5 'system_profiler SPHardwareDataType | awk -F": " "/Model Name|Model Identifier|Chip|Total Number of Cores|Memory/{print \\$1 \": \" \\$2}"'
ssh simon@100.123.79.5 'command -v ollama; command -v ffmpeg; command -v cmake; command -v llama-server'
```
