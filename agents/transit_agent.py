"""Transit access review agent for the Maryland planning simulator."""

from __future__ import annotations

from maryland_planning_simulator.schemas import AgentFinding
from maryland_planning_simulator.tools import find_nearest_transit_stop

STRONG_TRANSIT_ACCESS_METERS = 800
MODERATE_TRANSIT_ACCESS_METERS = 1600


def evaluate_transit_access(lat: float, lon: float, project_description: str) -> AgentFinding:
    """
    Score a site's transit accessibility using the nearest seeded stop.

    The thresholds are intentionally simple for the first build:
    - under 800m: strong support
    - 800m to 1600m: neutral / mixed
    - over 1600m: concern
    """
    result = find_nearest_transit_stop(lat=lat, lon=lon)
    error = result.get("error")

    if error:
        return AgentFinding(
            agent_name="Transit Agent",
            category="transit",
            stance="neutral",
            approved=False,
            summary=(
                "Transit review could not complete because the nearest-stop calculation failed. "
                "The project should be flagged for manual review."
            ),
            argument=(
                "Transit accessibility could not be verified, so the project should not receive a confident "
                "mobility-related recommendation automatically."
            ),
            key_risks=["Transit access was not verifiable due to tool failure."],
            key_benefits=["The system surfaced the mobility data gap explicitly."],
            confidence="low",
            recommended_conditions=["Verify transit access using a live Maryland transit source before approval."],
            evidence=result,
            error=error,
        )

    distance_meters = float(result["distance_meters"])
    walking_minutes = result["walking_minutes"]
    stop_name = result["nearest_stop_name"]
    stop_mode = result["nearest_stop_mode"]

    if distance_meters <= STRONG_TRANSIT_ACCESS_METERS:
        stance = "support"
        approved = True
        summary = (
            f"The proposed development '{project_description}' has strong transit access. "
            f"The nearest stop is {stop_name} ({stop_mode}), about {int(round(distance_meters))} meters "
            f"away or roughly {walking_minutes} walking minutes."
        )
        argument = (
            "The site is close enough to a major seeded transit anchor to support reduced car dependence and "
            "better multimodal accessibility."
        )
        key_risks = ["Transit result is based on seeded major-stop data, not a full live network."]
        key_benefits = ["Strong proximity to a major transit node.", "Supports transit-oriented development logic."]
        confidence = "medium"
        recommended_conditions = ["Consider pedestrian access and streetscape improvements to the stop."]
    elif distance_meters <= MODERATE_TRANSIT_ACCESS_METERS:
        stance = "neutral"
        approved = True
        summary = (
            f"The proposed development '{project_description}' has moderate transit access. "
            f"The nearest stop is {stop_name} ({stop_mode}), about {int(round(distance_meters))} meters "
            f"away or roughly {walking_minutes} walking minutes."
        )
        argument = (
            "Transit access is present but not especially strong, so the site can support some multimodal use "
            "while still depending partly on auto access."
        )
        key_risks = ["Transit proximity is only moderate in the current screening model."]
        key_benefits = ["There is still a reachable major transit stop within the review threshold."]
        confidence = "medium"
        recommended_conditions = ["Strengthen bike, walk, and shuttle connections if transit use is a project goal."]
    else:
        stance = "concern"
        approved = False
        summary = (
            f"The proposed development '{project_description}' appears relatively far from seeded major transit. "
            f"The nearest stop is {stop_name} ({stop_mode}), about {int(round(distance_meters))} meters "
            f"away or roughly {walking_minutes} walking minutes."
        )
        argument = (
            "The site appears too far from the seeded major transit network to rely on transit as a strong "
            "planning justification without additional mobility interventions."
        )
        key_risks = ["Weak access to seeded major transit.", "Higher likelihood of car dependence."]
        key_benefits = ["A transit anchor still exists within the wider regional context."]
        confidence = "medium"
        recommended_conditions = ["Provide mobility demand management or local shuttle/transit enhancements."]

    return AgentFinding(
        agent_name="Transit Agent",
        category="transit",
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
