import json
from pathlib import Path

import pytest

from grocery_flywheel.contracts import SCHEMA_VERSION, canonical_state
from grocery_flywheel.core import analyze_state, item_consumed_fraction
from grocery_flywheel.importers import import_normalized_history
from grocery_flywheel.retailer_adapter import (
    best_import_profiles,
    capability_matrix,
    validate_retailer_profile,
)


ROOT = Path(__file__).resolve().parents[1]


def analysis_state(extra: dict | None = None, *, items: list[dict] | None = None) -> dict:
    return canonical_state(
        as_of="2026-05-26",
        order={"store": "Example", "date": "2026-05-20", "total": 10},
        items=items or [],
        acquisition_channel="retailer_history_import",
        extra=extra,
    )


def analysis_item(**overrides) -> dict:
    item = {
        "schema_version": SCHEMA_VERSION,
        "name": "Example item",
        "spend": 5,
        "confidence": "medium",
        "privacy_class": "sensitive_purchase_history",
        "product_evidence": [],
    }
    item.update(overrides)
    return item


def test_item_consumed_fraction_from_units():
    item = {"units_total": 8, "units_remaining": 2}
    assert item_consumed_fraction(item) == 0.75


def test_item_consumed_fraction_from_remaining_fraction():
    item = {"remaining_fraction": 0.25}
    assert item_consumed_fraction(item) == 0.75


def test_sample_state_produces_runway_and_preference_signal():
    state = json.loads((ROOT / "examples" / "sample_state.json").read_text())
    analysis = analyze_state(state)

    assert analysis["consumed_value"] > 15
    assert analysis["estimated_days_remaining"] is not None
    assert analysis["acquisition_channel"] == "retailer_history_import"
    assert analysis["inventory_surface"]["type"] == "personal_grocery"
    assert any(item["role"] == "critical_household_essential" for item in analysis["items"])
    assert any(row["item"] == "Dish soap" for row in analysis["sourcing_research"])
    assert analysis["dietary_profiles"][0]["profile_id"] == "household-default"
    assert any(pref["key"] == "avoid_diced_chicken" for pref in analysis["preferences"])


def test_substitution_prefers_better_fit_even_when_unit_price_is_tied():
    state = json.loads((ROOT / "examples" / "sample_state.json").read_text())
    analysis = analyze_state(state)

    top = analysis["substitutions"][0]
    assert top["candidate"] == "Tyson grilled strips"
    assert top["fit"] == "better"


def test_substitution_ranking_is_objective_aware():
    state = analysis_state(
        {
            "substitutions": [
                {
                    "current": "Coffee",
                    "candidate": "Cheap split trip",
                    "current_unit_price": 1.0,
                    "candidate_unit_price": 0.4,
                    "fit": "same",
                    "trip_friction": 0.9,
                },
                {
                    "current": "Coffee",
                    "candidate": "Easy nearby option",
                    "current_unit_price": 1.0,
                    "candidate_unit_price": 0.95,
                    "fit": "same",
                    "trip_friction": 0.0,
                },
            ]
        }
    )

    assert analyze_state(state, objective="lowest_cost")["substitutions"][0]["candidate"] == "Cheap split trip"
    assert analyze_state(state, objective="fewer_trips")["substitutions"][0]["candidate"] == "Easy nearby option"


def test_unknown_substitution_candidate_needs_review_for_safety_critical_profile():
    state = canonical_state(
        as_of="2026-05-26",
        order={"store": "Example", "date": "2026-05-20", "total": 10},
        acquisition_channel="retailer_history_import",
        dietary_profiles=[
            {
                "profile_id": "critical",
                "restrictions": [
                    {
                        "value": "peanut_allergy",
                        "safety_tier": "critical",
                        "behavior": "block",
                    }
                ],
            }
        ],
        items=[
            analysis_item(
                name="Known safe milk",
                role="drink",
                spend=5,
                product_evidence=[
                    {
                        "schema_version": SCHEMA_VERSION,
                        "evidence_type": "ingredient_label",
                        "source": "package",
                        "checked_date": "2026-05-26",
                        "ingredients": ["milk", "cocoa"],
                    }
                ],
            )
        ],
        extra={
            "substitutions": [
                {
                    "current": "Known safe milk",
                    "candidate": "Unknown protein drink",
                    "current_unit_price": 1.0,
                    "candidate_unit_price": 0.5,
                    "fit": "better",
                }
            ]
        },
    )

    substitution = analyze_state(state, objective="allergy_safe")["substitutions"][0]

    assert substitution["dietary_status"] == "needs_review"
    assert substitution["evidence_status"] == "missing_candidate_evidence"


def test_retailer_profiles_validate_and_rank_import_paths():
    profiles = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())

    errors = [error for profile in profiles for error in validate_retailer_profile(profile)]
    assert errors == []

    matrix = capability_matrix(profiles)
    assert matrix[0]["id"] == "generic.browser_retailer"
    assert "purchase_history" in matrix[0]["enabled_capabilities"]

    import_profiles = best_import_profiles(profiles)
    assert [profile["id"] for profile in import_profiles] == [
        "generic.browser_retailer",
        "generic.warehouse_or_online",
    ]


def test_retailer_profile_rejects_order_submission_for_mvp():
    profile = {
        "id": "bad.submitter",
        "name": "Bad Submitter",
        "type": "grocery",
        "channels": ["delivery"],
        "acquisition_methods": ["retailer_history_import"],
        "capabilities": {
            "purchase_history": True,
            "product_search": True,
            "price_lookup": True,
            "unit_price": True,
            "availability": True,
            "substitutions": True,
            "cart_draft": True,
            "order_submit": True,
        },
    }

    assert "order_submit must stay false for MVP adapter profiles" in validate_retailer_profile(profile)


def test_retailer_profile_rejects_stored_secret_fields():
    profile = {
        "id": "bad.secret",
        "name": "Bad Secret",
        "type": "grocery",
        "channels": ["delivery"],
        "acquisition_methods": ["retailer_history_import"],
        "oauth": {"client_secret": "do-not-store"},
        "capabilities": {
            "purchase_history": True,
            "product_search": True,
            "price_lookup": True,
            "unit_price": True,
            "availability": True,
            "substitutions": True,
            "cart_plan": True,
            "order_submit": False,
        },
    }

    assert (
        "adapter profiles must not store passwords, tokens, cookies, or API keys: oauth.client_secret"
        in validate_retailer_profile(profile)
    )


def test_retailer_profile_rejects_secret_values_under_neutral_keys():
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]
    profile["provenance"]["history_source"] = "Bearer sk_live_1234567890"

    assert any(
        "provenance.history_source" in error
        for error in validate_retailer_profile(profile)
    )


def test_retailer_profile_rejects_secret_phrases_under_neutral_notes():
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]

    for phrase in (
        "password: hunter2",
        "cookie=sessionid",
        "api key: abc123",
        "api_key: abc123",
        "api-key: abc123",
        "token=abc123",
        "access token=abc123",
        "session: abc123",
        "session id: abc123",
        "session-cookie=abc123",
    ):
        profile["provenance"]["notes"] = phrase
        assert any(
            "provenance.notes" in error
            for error in validate_retailer_profile(profile)
        )


def test_retailer_profile_rejects_malformed_field_types():
    profile = json.loads((ROOT / "examples" / "retailer_profiles.json").read_text())[0]
    profile["id"] = 123
    profile["channels"] = "pickup"
    profile["acquisition_methods"] = 0
    profile["capabilities"]["purchase_history"] = "yes"

    errors = validate_retailer_profile(profile)

    assert "id must be a string" in errors
    assert "channels must be a list" in errors
    assert "acquisition_methods must be a list" in errors
    assert "capability purchase_history must be boolean" in errors


def test_dietary_status_propagates_into_sourcing_recommendations():
    state = canonical_state(
        as_of="2026-05-26",
        order={"store": "Example", "date": "2026-05-20", "total": 14},
        acquisition_channel="retailer_history_import",
        dietary_profiles=[
            {
                "profile_id": "doc-shape",
                "restrictions": [
                    {
                        "type": "food_allergy",
                        "value": "peanuts",
                        "safety_tier": "safety_critical",
                        "behavior": "block_until_review",
                    }
                ],
            }
        ],
        items=[
            analysis_item(
                name="Cafe Bustelo bricks",
                role="coffee",
                category="coffee",
                spend=13.84,
                unit_price=0.692,
                product_evidence=[],
            )
        ],
    )

    analysis = analyze_state(state, objective="allergy_safe")
    coffee = analysis["sourcing_research"][0]

    assert analysis["items"][0]["dietary_status"] == "needs_review"
    assert coffee["dietary_status"] == "needs_review"
    assert coffee["recommendation"] == "Needs dietary review before buying"
    assert coffee["alternatives"][0]["dietary_status"] == "needs_review"


def test_analyze_state_fails_closed_for_malformed_public_api_input():
    payload = json.loads((ROOT / "examples" / "imports" / "example-history.json").read_text())
    state = import_normalized_history(payload)
    state["sourcing_research"] = [{"alternatives": []}]

    with pytest.raises(ValueError, match="sourcing_research\\[0\\].item must be a string"):
        analyze_state(state)
