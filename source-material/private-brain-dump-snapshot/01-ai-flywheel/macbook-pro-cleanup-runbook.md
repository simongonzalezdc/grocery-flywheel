# MacBook Pro Cleanup Runbook

Purpose: clean the MacBook Pro M1 Pro without wiping it and without disturbing settings, credentials, account state, or network configuration.

## Phase 0: Access Check

Target:

- Host: `100.123.79.5`
- User: `simongonzalezdecruz`

Required before any cleanup:

```bash
ssh simongonzalezdecruz@100.123.79.5 'hostname; whoami; sw_vers -productVersion'
```

## Phase 1: Inventory Only

Run these first. No deletion.

```bash
hostname
sw_vers
uname -m
df -h /
du -sh ~/* 2>/dev/null | sort -h
find ~/Downloads ~/Desktop ~/Movies ~/Pictures ~/Documents -maxdepth 2 -type f -size +100M -print 2>/dev/null
find /Applications -maxdepth 1 -type d -name '*.app' -print | sort
```

Output to capture:

- total disk free
- largest user folders
- large files in user-visible folders
- app list
- obvious keep/delete recommendations

## Phase 2: Safe Cleanup

Allowed without extra review:

- empty Trash
- remove obvious installers in `~/Downloads`
- remove duplicate archives in `~/Downloads`
- remove temporary exported media or screen recordings after confirming they are not project inputs

Commands must be explicit-path deletes, not broad glob deletes, unless the matched list was reviewed immediately before deletion.

## Phase 3: App Cleanup

Allowed:

- delete removable third-party apps from `/Applications`

Preserve:

- Apple system apps
- Tailscale
- browsers unless duplicated
- terminal/dev tools
- password managers
- sync/cloud apps until their account state is understood

## Phase 4: Dev Artifact Cleanup

Only inside known project repos:

- `node_modules`
- `.next`
- `dist`
- `build`
- `target`
- `.venv`
- caches

Do not delete project source, `.git`, `.env`, database files, local storage, or uploads without explicit review.

## Phase 5: Worker Bootstrap

After cleanup:

```bash
command -v brew || true
command -v git || true
command -v ffmpeg || true
command -v cmake || true
command -v ollama || true
```

Install missing essentials only after inventory:

- Homebrew
- git
- gh
- ffmpeg
- cmake
- uv
- Node
- Ollama or llama.cpp Metal

