from __future__ import annotations

from typing import Any


PRESET_RESTRICTIONS = {
    "peanut_allergy": {"safety_tier": "critical", "tokens": ["peanut"]},
    "tree_nut_allergy": {"safety_tier": "critical", "tokens": ["almond", "walnut", "cashew", "tree nut"]},
    "celiac": {"safety_tier": "critical", "tokens": ["wheat", "gluten", "barley", "rye"]},
    "vegan": {"safety_tier": "lifestyle", "tokens": ["milk", "egg", "beef", "chicken", "pork", "honey"]},
    "kosher": {"safety_tier": "lifestyle", "tokens": ["pork", "shellfish"]},
    "halal": {"safety_tier": "lifestyle", "tokens": ["pork", "alcohol"]},
}

CRITICAL_TIERS = {"critical", "safety_critical", "safety-critical", "allergy", "food_allergy"}
LIFESTYLE_TIERS = {"lifestyle", "strong_preference", "preference_strong"}
BLOCK_BEHAVIORS = {"block", "block_until_review", "blocked"}
WARN_BEHAVIORS = {"warn", "review", "needs_review"}
VALUE_ALIASES = {
    "peanuts": "peanut_allergy",
    "peanut": "peanut_allergy",
    "tree_nuts": "tree_nut_allergy",
    "tree nuts": "tree_nut_allergy",
    "gluten": "celiac",
    "gluten_free": "celiac",
}


def evidence_is_current(evidence: dict[str, Any]) -> bool:
    return bool(evidence.get("evidence_type") and evidence.get("source") and evidence.get("checked_date"))


def evidence_has_label_content(evidence: dict[str, Any]) -> bool:
    return any(label_parts(evidence))


def label_parts(evidence: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for field in ("ingredients", "allergen_statements", "certifications"):
        value = evidence.get(field, [])
        values = value if isinstance(value, list) else [value]
        parts.extend(part.strip() for part in values if isinstance(part, str) and part.strip())
    return parts


def item_evidence(item: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in item.get("product_evidence", []) if evidence_is_current(row)]


def item_label_evidence(item: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in item_evidence(item) if evidence_has_label_content(row)]


def normalize_restriction_value(restriction: dict[str, Any]) -> str:
    raw = str(restriction.get("value") or restriction.get("type") or "").lower().strip()
    return VALUE_ALIASES.get(raw, raw)


def normalize_safety_tier(restriction: dict[str, Any], preset: dict[str, Any]) -> str:
    raw = str(restriction.get("safety_tier") or preset.get("safety_tier", "preference")).lower()
    if raw in CRITICAL_TIERS:
        return "critical"
    if raw in LIFESTYLE_TIERS:
        return "lifestyle"
    return "preference"


def normalize_behavior(restriction: dict[str, Any]) -> str:
    raw = str(restriction.get("behavior", "warn")).lower()
    if raw in BLOCK_BEHAVIORS:
        return "block"
    if raw in WARN_BEHAVIORS:
        return "warn"
    return raw


def has_critical_dietary_profile(profiles: list[dict[str, Any]]) -> bool:
    for profile in profiles:
        for restriction in profile.get("restrictions", []):
            value = normalize_restriction_value(restriction)
            preset = PRESET_RESTRICTIONS.get(value, {})
            if normalize_safety_tier(restriction, preset) == "critical":
                return True
    return False


def dietary_result(
    *,
    item: dict[str, Any],
    profile_id: str,
    restriction: str,
    result: str,
    safety_tier: str,
    evidence_status: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "item": item["name"],
        "profile_id": profile_id,
        "restriction": restriction,
        "result": result,
        "safety_tier": safety_tier,
        "evidence_status": evidence_status,
        "reason": reason,
        "privacy_class": "sensitive_dietary_profile",
        "schema_version": item.get("schema_version"),
    }


def evaluate_item_for_restriction(
    item: dict[str, Any], profile_id: str, restriction: dict[str, Any]
) -> dict[str, Any]:
    value = normalize_restriction_value(restriction)
    preset = PRESET_RESTRICTIONS.get(value, {})
    safety_tier = normalize_safety_tier(restriction, preset)
    behavior = normalize_behavior(restriction)
    tokens = list(preset.get("tokens", [value]))
    evidence_rows = item_evidence(item)
    label_evidence_rows = item_label_evidence(item)

    if safety_tier == "critical" and not evidence_rows:
        return dietary_result(
            item=item,
            profile_id=profile_id,
            restriction=value,
            result="needs_review",
            safety_tier=safety_tier,
            evidence_status="missing",
            reason="Safety-critical restriction needs ingredient, allergen, or certification evidence with type, source, and checked date.",
        )

    if safety_tier == "critical" and not label_evidence_rows:
        return dietary_result(
            item=item,
            profile_id=profile_id,
            restriction=value,
            result="needs_review",
            safety_tier=safety_tier,
            evidence_status="ambiguous",
            reason="Safety-critical restriction has product evidence but no ingredient, allergen, or certification label content.",
        )

    haystack = " ".join(
        str(part).lower()
        for evidence in label_evidence_rows
        for part in label_parts(evidence)
    )
    matched = [token for token in tokens if token and token in haystack]
    if matched:
        return dietary_result(
            item=item,
            profile_id=profile_id,
            restriction=value,
            result="blocked" if safety_tier == "critical" or behavior == "block" else "warn",
            safety_tier=safety_tier,
            evidence_status="current",
            reason=f"Evidence matched: {', '.join(matched)}.",
        )

    if safety_tier == "critical":
        result = "safe"
        reason = "Current product evidence did not match the safety-critical restriction."
    elif safety_tier == "lifestyle":
        result = "warn" if behavior != "block" else "blocked"
        reason = "Lifestyle restriction defaults to review unless the user config says block."
    else:
        result = "warn" if behavior == "warn" else "safe"
        reason = "Preference restriction evaluated."
    return dietary_result(
        item=item,
        profile_id=profile_id,
        restriction=value,
        result=result,
        safety_tier=safety_tier,
        evidence_status="current" if label_evidence_rows else "missing",
        reason=reason,
    )


def evaluate_dietary_profiles(
    items: list[dict[str, Any]], profiles: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    evaluations = []
    for profile in profiles:
        profile_id = profile.get("profile_id", "default")
        for restriction in profile.get("restrictions", []):
            for item in items:
                evaluations.append(evaluate_item_for_restriction(item, profile_id, restriction))
    return evaluations
