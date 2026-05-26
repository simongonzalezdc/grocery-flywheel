# MacBook Pro M1 Wipe Runbook

Status: superseded. User changed plan: do not wipe. Use cleanup mode instead.

Active plan: `01-ai-flywheel/macbook-pro-cleanup-policy.md`

## Current Reachability

Latest facts from the Mac mini:

- Tailscale node: `simons-macbook-pro`
- Tailscale IP: `100.123.79.5`
- Tailscale status now shows the node active on the tailnet.
- TCP port 22 is open.
- Post-wipe SSH authentication is still unverified.

## Recommended Target State

Use clean macOS, not Linux, on the M1 Pro.

Reason:

- Apple Silicon inference is most useful with macOS + Metal.
- Linux on Apple Silicon is possible but adds driver/runtime tradeoffs and does not improve the immediate flywheel enough.
- A wiped clean macOS worker can run Tailscale, SSH, Homebrew, ffmpeg, Ollama/llama.cpp Metal, and agent/client surfaces quickly.

## What I Can Do Remotely

If SSH or remote GUI access works, I can handle:

- inventory and backup triage
- install checks
- wipe/reinstall guidance
- post-wipe bootstrap
- Tailscale, SSH, Homebrew, ffmpeg, model tooling
- clamshell/node setup
- adding it to the cluster inventory

## What May Require Physical Interaction

Apple Silicon erase/reinstall can require:

- the Mac to be unlocked
- admin password
- Apple Account / Activation Lock prompts
- Recovery OS UI
- Wi-Fi selection if Ethernet is not attached
- confirming Erase All Content and Settings or Disk Utility erase steps

These are firmware/Recovery/Apple security boundaries; I can guide or remote-control if a GUI bridge is available, but I cannot bypass them.

## Official Apple Erase Paths

Preferred if logged into macOS Monterey or later:

- Erase Assistant / Erase All Content and Settings.

Fallback:

- Boot macOS Recovery on Apple Silicon.
- Use Disk Utility to erase `Macintosh HD` as APFS.
- Reinstall macOS.

Sources:

- Apple: Erase your Mac: https://support.apple.com/en-lamr/guide/mac-help/mchl7676b710
- Apple: Use Disk Utility to erase a Mac with Apple silicon: https://support.apple.com/en-us/102506
- Apple: Reinstall macOS: https://support.apple.com/en-lamr/guide/mac-help/-mchlp1599/mac

## Current Blocker

The wipe plan is no longer active. The remaining gate is control access for cleanup.

To finish setup remotely, one of these must become true:

1. SSH access works for the new admin user.
2. Tailscale SSH is enabled/working for the target.
3. Screen Sharing or Remote Management is enabled and reachable.

## Post-Wipe Bootstrap

After the clean OS is up:

```bash
softwareupdate --install-rosetta --agree-to-license || true
xcode-select --install || true
```

Install:

- Tailscale
- Homebrew
- git
- gh
- ffmpeg
- cmake
- Python/uv
- Node
- Ollama or llama.cpp Metal build

Then verify:

```bash
sw_vers
uname -m
system_profiler SPHardwareDataType
tailscale status
ssh simon@<macbook-pro-tailscale-ip> 'hostname'
```

## Bootstrap Target

Minimum useful worker state:

- Tailscale connected and named clearly.
- Remote Login enabled.
- Admin SSH key installed.
- Homebrew installed.
- `git`, `gh`, `ffmpeg`, `cmake`, `uv`, `node`, and model tooling installed.
- Machine facts recorded in the cluster inventory.
