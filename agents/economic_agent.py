"""Economic feasibility review agent for the Maryland planning simulator."""

from __future__ import annotations

from maryland_planning_simulator.schemas import AgentFinding
from maryland_planning_simulator.tools import estimate_economic_outlook

STRONG_RENT_THRESHOLD_USD = 2300
STRONG_APPRECIATION_THRESHOLD_PCT = 22.0
MINIMUM_RENT_THRESHOLD_USD = 1900
MINIMUM_APPRECIATION_THRESHOLD_PCT = 15.0


def evaluate_economic_feasibility(lat: float, lon: float, project_description: str) -> AgentFinding:
    """
    Assess economic feasibility using seeded rent and appreciation metrics.

    The first scoring rules are intentionally simple and transparent so they
    can be recalibrated once a live market-data provider is introduced.
    """
    result = estimate_economic_outlook(lat=lat, lon=lon)
    error = result.get("error")

    if error:
        return AgentFinding(
            agent_name="ROI / Economic Agent",
            category="economic",
            stance="neutral",
            approved=False,
            summary=(
                "Economic review could not complete because market reference data was unavailable. "
                "The project should be flagged for manual financial review."
            ),
            argument=(
                "Without a usable market reference, the project's feasibility and return outlook cannot be "
                "judged confidently."
            ),
            key_risks=["Economic feasibility signal is missing."],
            key_benefits=["The workflow identified the need for manual underwriting or market review."],
            confidence="low",
            recommended_conditions=["Validate rents and appreciation with a live market-data source."],
            evidence=result,
            error=error,
        )

    average_rent = float(result["average_monthly_rent_usd"])
    appreciation = float(result["five_year_appreciation_pct"])
    market_name = result["market_name"]

    if average_rent >= STRONG_RENT_THRESHOLD_USD and appreciation >= STRONG_APPRECIATION_THRESHOLD_PCT:
        stance = "support"
        approved = True
        summary = (
            f"The proposed development '{project_description}' maps to the seeded {market_name} market, "
            f"which shows strong economics with average rent around ${int(round(average_rent))}/month "
            f"and about {appreciation:.1f}% five-year appreciation."
        )
        argument = (
            "The reference market suggests both healthy rent support and appreciation momentum, which makes "
            "the project more economically defensible at a screening level."
        )
        key_risks = ["Economic result is based on seeded market reference data, not a live provider."]
        key_benefits = ["Strong rent support.", "Strong appreciation signal."]
        confidence = "medium"
        recommended_conditions = ["Validate pro forma assumptions against a live market-data source."]
    elif average_rent < MINIMUM_RENT_THRESHOLD_USD or appreciation < MINIMUM_APPRECIATION_THRESHOLD_PCT:
        stance = "concern"
        approved = False
        summary = (
            f"The proposed development '{project_description}' maps to the seeded {market_name} market, "
            f"which shows weaker economics with average rent around ${int(round(average_rent))}/month "
            f"and about {appreciation:.1f}% five-year appreciation."
        )
        argument = (
            "The seeded market outlook is not strong enough to clearly support the proposal's economic case, "
            "so the project should not be approved on financial grounds alone."
        )
        key_risks = ["Lower rent support.", "Weaker appreciation trend."]
        key_benefits = ["The market may still support a revised or lower-intensity program."]
        confidence = "medium"
        recommended_conditions = ["Revisit program scale, phasing, or financing assumptions before approval."]
    else:
        stance = "neutral"
        approved = True
        summary = (
            f"The proposed development '{project_description}' maps to the seeded {market_name} market, "
            f"which shows moderate economics with average rent around ${int(round(average_rent))}/month "
            f"and about {appreciation:.1f}% five-year appreciation."
        )
        argument = (
            "The economics are plausible but not overwhelmingly strong, so the project looks feasible with "
            "normal financial diligence rather than aggressive optimism."
        )
        key_risks = ["Only moderate rent and appreciation support in the reference market."]
        key_benefits = ["Economic conditions appear viable enough for further review."]
        confidence = "medium"
        recommended_conditions = ["Confirm feasibility with a live comparable-rent and land-value review."]

    return AgentFinding(
        agent_name="ROI / Economic Agent",
        category="economic",
        stance=stance,
        approved=approved,
        summary=summary,
        argument=argument,
        key_risks=key_risks,
        key_benefits=key_benefits,
        confidence=confidence,
        recommended_conditions=recommended_conditions,
        evidence=result,
    )
