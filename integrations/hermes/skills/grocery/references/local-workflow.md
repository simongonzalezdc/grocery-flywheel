# Local workflow

Data lives under the effective HERMES_HOME/plugin-data/grocery-flywheel/.
User-managed state/*.json is never overwritten by this plugin. Explicitly import sanitized
state by manually copying it there (directories mode 0700, files preferably 0600).
No arbitrary filesystem reads, automatic discovery, mutations, network, checkout or telemetry.
Inline state is not saved by the plugin; the host may retain it in transcripts.

Use the existing engine CLI outside this plugin for import, trip capture and corrections.
Consult that installed engine's --help; the native plugin adds no capture/mutation tool.
Generated dashboards/*.html are private (0600), retained until user-controlled export/deletion.
Disable with `hermes plugins disable grocery-flywheel`; restart the session to remove tools.
Removing installed code must preserve plugin-data; never delete household history as rollback.
The namespaced skill is `grocery-flywheel:grocery`.
