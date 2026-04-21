"""Infrastructure review agent for hospitals and grocery access."""

from __future__ import annotations

from maryland_planning_simulator.schemas import AgentFinding
from maryland_planning_simulator.tools import evaluate_local_infrastructure


def evaluate_infrastructure_access(lat: float, lon: float, project_description: str) -> AgentFinding:
    """
    Assess local infrastructure by combining hospital and food-access signals.

    This first scoring pass is intentionally transparent:
    - concern if the site looks like a food desert or both amenities are far away
    - neutral if fallback data was required
    - support otherwise
    """
    result = evaluate_local_infrastructure(lat=lat, lon=lon)
    errors = result.get("errors", [])
    used_mock_fallback = bool(result.get("used_mock_fallback"))

    if errors and not used_mock_fallback:
        return AgentFinding(
            agent_name="Infrastructure Agent",
            category="infrastructure",
            stance="neutral",
            approved=False,
            summary=(
                "Infrastructure review could not complete because both hospital and grocery lookups failed. "
                "The project should be routed for manual review."
            ),
            argument=(
                "Core amenity access could not be verified, so the infrastructure case for this project is "
                "too uncertain to automate confidently."
            ),
            key_risks=["Hospital and food-access checks both failed."],
            key_benefits=["The tool surfaced the infrastructure-data failure explicitly."],
            confidence="low",
            recommended_conditions=["Validate nearby hospital and grocery access with live data before approval."],
            evidence=result,
            error="; ".join(errors),
        )

    hospital_distance = float(result["nearest_hospital_meters"])
    grocery_distance = float(result["nearest_grocery_meters"])
    food_desert_warning = bool(result["food_desert_warning"])

    if used_mock_fallback:
        return AgentFinding(
            agent_name="Infrastructure Agent",
            category="infrastructure",
            stance="neutral",
            approved=True,
            summary=(
                f"The proposed development '{project_description}' received a provisional infrastructure review "
                "using fallback values because one or more live data sources were unavailable."
            ),
            argument=(
                "The site may be viable from an infrastructure standpoint, but the current conclusion is only "
                "provisional because fallback values replaced part of the live evidence."
            ),
            key_risks=["One or more infrastructure values came from fallback data."],
            key_benefits=["The workflow remained operational instead of crashing on external API failure."],
            confidence="low",
            recommended_conditions=["Refresh hospital and grocery checks with live data before final approval."],
            evidence=result,
            error="; ".join(errors) if errors else None,
        )

    if food_desert_warning or (hospital_distance > 5000 and grocery_distance > 1600):
        return AgentFinding(
            agent_name="Infrastructure Agent",
            category="infrastructure",
            stance="concern",
            approved=False,
            summary=(
                f"The proposed development '{project_description}' appears to have weaker basic service access, "
                f"with the nearest hospital about {int(round(hospital_distance))} meters away and the nearest "
                f"grocery about {int(round(grocery_distance))} meters away."
            ),
            argument=(
                "Core services appear relatively far from the site, which weakens the case that the proposal is "
                "well-supported by everyday infrastructure."
            ),
            key_risks=[
                "Potential food access gap or food-desert condition.",
                "Longer travel distance to a hospital.",
            ],
            key_benefits=["Infrastructure issues were identified early in screening."],
            confidence="medium",
            recommended_conditions=[
                "Mitigate food-access and service gaps before approval, especially for residential uses."
            ],
            evidence=result,
        )

    return AgentFinding(
        agent_name="Infrastructure Agent",
        category="infrastructure",
        stance="support",
        approved=True,
        summary=(
            f"The proposed development '{project_description}' has acceptable nearby core amenities, with the "
            f"nearest hospital about {int(round(hospital_distance))} meters away and the nearest grocery about "
            f"{int(round(grocery_distance))} meters away."
        ),
        argument=(
            "The site appears to have workable access to basic services, which supports day-to-day livability "
            "for future residents or users."
        ),
        key_risks=["Infrastructure screening currently focuses on hospitals and grocery access only."],
        key_benefits=["Acceptable proximity to a hospital and grocery option."],
        confidence="medium",
        recommended_conditions=["Confirm local service capacity during later site and transportation review."],
        evidence=result,
    )
