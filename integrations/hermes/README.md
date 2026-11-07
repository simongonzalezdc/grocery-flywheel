# Native Hermes integration (local candidate)

This is a thin adapter around **this repository's unchanged engine**, not another
engine or an MCP sidecar. Linux/macOS POSIX, Python >=3.11, Hermes >=0.23.0.
Only Linux has been exercised in the candidate evidence. Build before installing:
`integrations/hermes` by itself is not an installable bundle.

## Install in a disposable profile

From the engine repository, using an already provisioned trusted Hermes runtime:

```bash
export QA_ROOT="$(mktemp -d "${TMPDIR:-$HOME/.cache}/grocery-hermes.XXXXXX")"
python3 scripts/build_hermes_plugin.py --output "$QA_ROOT/bundle"
export HERMES_HOME="$QA_ROOT/profile"
unset HERMES_PROFILE
mkdir -p "$HERMES_HOME/plugins"
cp -R "$QA_ROOT/bundle/grocery-flywheel" "$HERMES_HOME/plugins/grocery-flywheel"
hermes plugins doctor "$HERMES_HOME/plugins/grocery-flywheel" --ci
hermes plugins validate "$HERMES_HOME/plugins/grocery-flywheel"
hermes plugins list
hermes plugins enable grocery-flywheel
hermes plugins list
hermes
```

The launcher may bootstrap its own dependencies for a new home. In an air-gapped
installation, provision Hermes and its locked dependencies first. The plugin has
zero Python/runtime dependencies and does not install anything at load time.
The bundle's ENGINE-MANIFEST.json pins source and every included engine file.
Installation in a real profile requires its owner's approval; do not overwrite
an existing installation or data directory on the strength of these instructions.

## Use

```text
/grocery help
/grocery status
/grocery sample
/skill grocery-flywheel:grocery
```

`sample` runs sanitized analysis without importing or persisting sample state.
For the five named-state examples, explicitly import the bundled sanitized sample:

```bash
install -d -m 700 "$HERMES_HOME/plugin-data" \
  "$HERMES_HOME/plugin-data/grocery-flywheel" \
  "$HERMES_HOME/plugin-data/grocery-flywheel/state"
install -m 600 "$QA_ROOT/bundle/grocery-flywheel/examples/sample_state.json" \
  "$HERMES_HOME/plugin-data/grocery-flywheel/state/sample.json"
```

Then in Hermes:

```text
/grocery analyze {"state_name":"sample.json"}
/grocery dietary {"state_name":"sample.json","objective":"allergy_safe"}
/grocery sourcing {"state_name":"sample.json"}
/grocery plan {"state_name":"sample.json","mode":"pickup"}
/grocery dashboard {"state_name":"sample.json"}
```

Exactly five native tools: `grocery_analyze`, `grocery_dietary`, `grocery_sourcing`,
`grocery_plan`, `grocery_dashboard`, in toolset `grocery`. Every call requires
exactly one `state_name` or inline JSON-string `state_json`. Native discovery
alone is not a promise that an operator's toolset selection exposes it to a model;
select the grocery toolset in that session if needed. No model is needed for
slash dispatch. Other than dietary/plan, top-level objective is rejected; set the
existing state objective instead. Modes: pickup, delivery, in_person.

Dashboard returns its generated relative artifact name and readback SHA-256,
never HTML or a caller-controlled output path. Open the file manually under
`$HERMES_HOME/plugin-data/grocery-flywheel/`. No HTTP listener is started.
The original dashboard's optional correction capture remains browser-local
until the human explicitly downloads JSONL; it does not mutate engine state.

## Existing external engine workflows

These commands belong to the separately installed existing engine, not new native
mutation tools. Paths are explicit user-chosen inputs to that CLI, not accepted by
the native plugin. Back up real state before changing it; use sanitized data first.

```bash
grocery-flywheel import normalized examples/imports/example-history.json \
  --output "$HERMES_HOME/plugin-data/grocery-flywheel/state/imported.json"
grocery-flywheel-capture-visit \
  "$HERMES_HOME/plugin-data/grocery-flywheel/state/imported.json" \
  --type in_store --started-at 2026-06-07T10:00 --duration-min 45
grocery-flywheel corrections add \
  "$HERMES_HOME/plugin-data/grocery-flywheel/state/imported.json" \
  --item "Example item" --signal never_again --note "Explicit sanitized correction"
```

## Privacy and approval boundary

The engine/plugin makes no network, provider, subprocess, retailer, telemetry or
checkout calls. **Hermes is not the engine**: inline inputs and returned analysis
can enter its configured model and retained session transcripts. Obtain user
intent before using real household/dietary data in chat; recommend a verified
local model/offline host configuration for sensitive data and review transcript
retention. Do not promise that a remote model is private merely because the
engine is offline. `safe` is an evidence-token verdict, never medical assurance.
Sourcing summarizes supplied research questions; it does not research live prices.
Every draft requires human review; checkout_available=false and all item approval
states are needs_human_approval. There is no native approve/checkout operation.

Inputs: <=60,000 UTF-8 bytes, strict JSON object, depth<=32, nodes<=10,000,
strings<=8,192 bytes, arrays<=500. Slash/argument envelope<=65,536 bytes.
Results<=256 KiB, HTML<=2 MiB. Unknown arguments/paths are rejected. State names
are ASCII basenames, not arbitrary files. Profile directories must be owner-private
0700 and non-symlink; output files are0600. Unsafe or unsupported storage fails
closed. No automatic imports, scans, migration, deletion or hidden state cache.
Python executes with host-user permissions: containment is not an OS sandbox.

## Runtime identity prerequisite

Acceptance must use a version-identifiable clean Hermes checkout or installed
release. A bare source archive can report version `unknown`; Hermes permits
unknown development versions, so such a run cannot prove `requires_hermes`
enforcement. Both harnesses reject that ambiguous identity before testing.
The tested clean Git checkouts correctly rejected an incompatible `>=999.0.0`
manifest during enable; validator syntax checks alone are not that evidence.

## Verify and rollback

From the repository, with its dev/test environment installed:

```bash
python3 -m pytest -o addopts='' -p no:cacheprovider tests/
python3 scripts/check_docs_links.py
ruff check .
gitleaks dir . --redact
python3 scripts/verify_hermes_plugin.py --bundle "$QA_ROOT/bundle/grocery-flywheel" \
  --scratch "$QA_ROOT/acceptance" --offline --report "$QA_ROOT/acceptance.json"
node scripts/verify_hermes_dashboard.mjs "$QA_ROOT/acceptance/sample-dashboard.html" \
  "$QA_ROOT/browser"
```

The native harness must run with the selected Hermes runtime's interpreter and
source importable, not a fake SDK fixture. It exercises actual host registry,
slash dispatch and namespaced skill loading without spending model tokens.
Browser verification uses an installed Chrome (CHROME_PATH override), no npm
packages/downloads. It is a test harness, not a browser launched by the plugin.

```bash
hermes plugins disable grocery-flywheel
# Start a fresh session: five grocery tools, /grocery and namespaced skill absent.
hermes plugins remove grocery-flywheel
```

Disable/remove installed **code only**. Plugin data, source state and dashboards
must remain for user-controlled export/deletion and reuse after reinstall. Never
delete household history as rollback. No service restart. PR publication, CI,
Security approval/merge, catalog/release and live-profile installation are separate
gates; local candidate evidence is not publication or production acceptance.
