from __future__ import annotations

import re
from typing import Any

from .contracts import RetailerProfile, to_dict

CORE_CAPABILITIES = [
    "purchase_history",
    "product_search",
    "price_lookup",
    "unit_price",
    "availability",
    "substitutions",
    "cart_plan",
    "order_submit",
]

LEGACY_CAPABILITY_ALIASES = {"cart_draft": "cart_plan"}

CAPABILITY_WEIGHTS = {
    "purchase_history": 5,
    "product_search": 3,
    "price_lookup": 3,
    "unit_price": 2,
    "availability": 2,
    "substitutions": 2,
    "cart_plan": 1,
    "order_submit": -10,
}

SECRET_KEY_PARTS = (
    "password",
    "token",
    "session_cookie",
    "api_key",
    "cookie",
    "secret",
    "credential",
)
SENSITIVE_CONTAINER_KEY_PARTS = ("auth", "authorization", "headers", "header", "session", "oauth")
SECRET_VALUE_RE = re.compile(
    r"(?i)\b("
    r"bearer\s+[a-z0-9._~+/=-]{8,}|"
    r"sk_(?:live|test)_[a-z0-9_]{8,}|"
    r"gh[pousr]_[a-z0-9_]{16,}|"
    r"xox[abprs]-[a-z0-9-]{16,}"
    r")\b"
)
SECRET_PHRASE_RE = re.compile(
    r"(?i)\b("
    r"password|passcode|api[\s_-]*key|access[\s_-]*token|refresh[\s_-]*token|"
    r"id[\s_-]*token|token|session(?:[\s_-]*(?:id|cookie))?|cookie|secret|credential"
    r")\b\s*[:=]"
)
ALLOWED_PROFILE_FIELDS = {
    "id",
    "name",
    "type",
    "region",
    "channels",
    "acquisition_methods",
    "capabilities",
    "constraints",
    "provenance",
    "schema_version",
}
ALLOWED_PROVENANCE_FIELDS = {
    "history_source",
    "price_source",
    "profile_source",
    "created_at",
    "notes",
}
KNOWN_CAPABILITY_FIELDS = set(CORE_CAPABILITIES) | set(LEGACY_CAPABILITY_ALIASES) | {
    "external_cart_draft"
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "retailer"


def normalize_capabilities(capabilities: Any) -> dict[str, bool]:
    if not isinstance(capabilities, dict):
        return {}
    normalized = {
        key: value if isinstance(value, bool) else False
        for key, value in capabilities.items()
    }
    for legacy, current in LEGACY_CAPABILITY_ALIASES.items():
        if legacy in normalized and current not in normalized:
            normalized[current] = normalized[legacy]
    return normalized


def secret_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            lowered = key_text.lower()
            if any(secret in lowered for secret in SECRET_KEY_PARTS):
                paths.append(path)
            if any(container in lowered for container in SENSITIVE_CONTAINER_KEY_PARTS):
                paths.append(path)
            paths.extend(secret_field_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(secret_field_paths(child, f"{prefix}[{index}]"))
    elif isinstance(value, str) and (
        SECRET_VALUE_RE.search(value) or SECRET_PHRASE_RE.search(value)
    ):
        paths.append(prefix or "<value>")
    return paths


def validate_profile_shape(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in profile:
        if field not in ALLOWED_PROFILE_FIELDS:
            errors.append(f"unsupported adapter profile field {field}")
    for field in ("id", "name", "type", "region"):
        if field in profile and not isinstance(profile[field], str):
            errors.append(f"{field} must be a string")
    for field in ("channels", "acquisition_methods", "constraints"):
        if field in profile:
            if not isinstance(profile[field], list):
                errors.append(f"{field} must be a list")
            else:
                for index, value in enumerate(profile[field]):
                    if not isinstance(value, str):
                        errors.append(f"{field}[{index}] must be a string")
    provenance = profile.get("provenance")
    if provenance is not None:
        if not isinstance(provenance, dict):
            errors.append("provenance must be an object")
        else:
            for field in provenance:
                if field not in ALLOWED_PROVENANCE_FIELDS:
                    errors.append(f"unsupported adapter provenance field {field}")
    raw_capabilities = profile.get("capabilities", {})
    if isinstance(raw_capabilities, dict):
        for capability in raw_capabilities:
            if capability not in KNOWN_CAPABILITY_FIELDS:
                errors.append(f"unknown adapter capability {capability}")
            if not isinstance(raw_capabilities[capability], bool):
                errors.append(f"capability {capability} must be boolean")
    return errors


def validate_retailer_profile(profile: dict[str, Any]) -> list[str]:
    """Return validation errors for a retailer adapter profile."""
    errors: list[str] = []
    required = ["id", "name", "type", "channels", "acquisition_methods", "capabilities"]
    for field in required:
        if field not in profile:
            errors.append(f"missing {field}")

    errors.extend(validate_profile_shape(profile))

    for path in secret_field_paths(profile):
        errors.append(
            f"adapter profiles must not store passwords, tokens, cookies, or API keys: {path}"
        )

    raw_capabilities = profile.get("capabilities", {})
    if not isinstance(raw_capabilities, dict):
        errors.append("capabilities must be an object")
        return errors
    capabilities = normalize_capabilities(raw_capabilities)

    for capability in CORE_CAPABILITIES:
        if capability not in capabilities:
            errors.append(f"missing capability {capability}")

    if capabilities.get("order_submit"):
        errors.append("order_submit must stay false for MVP adapter profiles")
    if capabilities.get("external_cart_draft"):
        errors.append("external_cart_draft requires a later ADR and is excluded from MVP")

    acquisition_methods = profile.get("acquisition_methods", [])
    if not isinstance(acquisition_methods, list):
        acquisition_methods = []
    if "retailer_history_import" in acquisition_methods and not capabilities.get("purchase_history"):
        errors.append("retailer_history_import requires purchase_history capability")

    return errors


def adapter_score(profile: dict[str, Any]) -> int:
    capabilities = normalize_capabilities(profile.get("capabilities", {}))
    return sum(
        weight
        for capability, weight in CAPABILITY_WEIGHTS.items()
        if capabilities.get(capability)
    )


def capability_matrix(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for profile in profiles:
        capabilities = normalize_capabilities(profile.get("capabilities", {}))
        rows.append(
            {
                "id": profile.get("id", ""),
                "name": profile.get("name", ""),
                "type": profile.get("type", ""),
                "score": adapter_score(profile),
                "acquisition_methods": profile.get("acquisition_methods", []),
                "enabled_capabilities": [
                    capability
                    for capability in CORE_CAPABILITIES
                    if capabilities.get(capability)
                ],
                "errors": validate_retailer_profile(profile),
            }
        )
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def best_import_profiles(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank profiles for first-run setup."""
    eligible = [
        profile
        for profile in profiles
        if normalize_capabilities(profile.get("capabilities", {})).get("purchase_history")
    ]
    return sorted(eligible, key=adapter_score, reverse=True)


def create_retailer_profile(
    *,
    name: str,
    type_: str,
    channels: list[str],
    acquisition_methods: list[str],
    capabilities: list[str],
    region: str = "custom",
) -> dict[str, Any]:
    enabled = {capability: False for capability in CORE_CAPABILITIES}
    for capability in capabilities:
        current = LEGACY_CAPABILITY_ALIASES.get(capability, capability)
        if current not in enabled:
            raise ValueError(f"unknown capability {capability!r}")
        enabled[current] = True
    enabled["order_submit"] = False
    profile = to_dict(
        RetailerProfile(
            id=f"custom.{slugify(name)}",
            name=name,
            type=type_,
            channels=channels,
            acquisition_methods=acquisition_methods,
            capabilities=enabled,
            region=region,
            provenance={
                "history_source": "user_configured",
                "price_source": "user_configured",
            },
        )
    )
    errors = validate_retailer_profile(profile)
    if errors:
        raise ValueError("; ".join(errors))
    return profile


def format_capability_table(rows: list[dict[str, Any]]) -> str:
    headers = ["id", "score", "acquisition", "enabled", "errors"]
    lines = [" | ".join(headers), " | ".join("-" * len(header) for header in headers)]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    str(row["id"]),
                    str(row["score"]),
                    ",".join(row["acquisition_methods"]),
                    ",".join(row["enabled_capabilities"]),
                    "; ".join(row["errors"]) or "ok",
                ]
            )
        )
    return "\n".join(lines)
