# MacBook Pro Cleanup Policy

Status: active plan changed. Do not wipe. Clean up files and removable applications while preserving settings.

## Intent

Turn the MacBook Pro M1 Pro into a useful AI flywheel worker with much less effort than a full wipe.

## Preserve

Do not delete:

- macOS system apps or system files
- user accounts
- passwords, Keychain, certificates, SSH keys, browser profiles, Apple Account/iCloud state
- Tailscale configuration
- network settings
- developer credentials and auth state unless explicitly requested
- `~/Library`, `/Library`, `/System`, `/usr`, `/opt/homebrew`, or hidden dotfiles by default
- project repos under `~/workspaces`, Desktop repos, or other code directories until inventoried

## Safe Delete Candidates

Delete or uninstall after inventory:

- obvious unused third-party apps in `/Applications`
- large installers: `.dmg`, `.pkg`, `.zip`, `.tar.gz`
- duplicate downloads
- old screenshots and screen recordings
- trash contents
- generated build artifacts in known repos only when safe: `node_modules`, `.next`, `target`, `dist`, caches
- app-specific data only when the app is being removed and it is not auth/settings-critical

## Review Before Delete

Before deleting anything substantial, produce:

- top largest directories
- top largest files
- third-party apps list
- obvious keep/delete recommendation

## Cleanup Flow

1. Establish SSH or Screen Sharing access.
2. Inventory disk usage and apps.
3. Classify items into keep/delete/review.
4. Delete low-risk files first.
5. Uninstall apps only when they are clearly removable.
6. Leave settings and auth state intact.
7. Install/verify worker dependencies.

Operational runbook: `01-ai-flywheel/macbook-pro-cleanup-runbook.md`

## Current Access Blocker

MacBook Pro is on Tailscale at `100.123.79.5`, but SSH authentication is still rejected for:

- `simon`
- `simongonzalezdecruz`

Next unlock needed:

- enable Remote Login for the actual admin account, or
- add this Mac mini's SSH public key to the MacBook Pro admin account, or
- enable Screen Sharing / Remote Management.
