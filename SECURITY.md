# Security Policy

## Supported Versions

Security fixes target the current `main` branch and latest public release. Older local experiments are not supported unless the issue affects current public code too.

## Reporting a Vulnerability

Please do not open a public issue containing private household data, grocery history, dietary profiles, addresses, credentials, or exploit details.

Report security concerns through GitHub Security Advisories or email `security@kyanitelabs.tech` with:

- affected command, file, or data model field;
- impact and reproduction steps;
- whether private household, dietary, sourcing, or preference data was exposed;
- Python version and operating system.

Expected response: acknowledgement within 3 business days, triage within 7 business days, and a fix or mitigation plan based on severity.

## Project Security Notes

Grocery Flywheel is local-first and has no runtime network dependencies. State files can contain personal household data, so real user state files should stay outside the repository. Use the included examples for tests and demos.

Before a release, run:

```bash
pip install -e ".[dev]"
pytest
gitleaks dir . --no-banner --redact
```

