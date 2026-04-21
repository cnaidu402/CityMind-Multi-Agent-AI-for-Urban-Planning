"""Safety review agent based on recent Baltimore Part 1 crime density."""

from __future__ import annotations

from maryland_planning_simulator.schemas import AgentFinding
from maryland_planning_simulator.tools import count_baltimore_crime_incidents

# These thresholds are intentionally transparent and easy to adjust after we
# calibrate them against real Baltimore neighborhoods.
HIGH_CRIME_THRESHOLD = 50
MODERATE_CRIME_THRESHOLD = 20


def evaluate_public_safety(lat: float, lon: float, project_description: str) -> AgentFinding:
    """
    Review public-safety context using a 500-meter, one-year crime count.

    Because Open Baltimore only covers Baltimore City, a future statewide
    version should route to county-specific safety sources when outside city
    limits. For now we surface that coverage explicitly in the evidence.
    """
    result = count_baltimore_crime_incidents(lat=lat, lon=lon)
    error = result.get("error")

    if error:
        return AgentFinding(
            agent_name="Safety Agent",
            category="safety",
            stance="neutral",
            approved=False,
            summary=(
                "Safety review could not complete because the Baltimore crime dataset was unavailable or "
                "not compatible with this location. The project should be routed for manual review."
            ),
            argument=(
                "Without a valid crime-density response, the public-safety risk profile is too uncertain for "
                "a confident automated vote."
            ),
            key_risks=["Safety signal is incomplete because the live crime dataset could not be used."],
            key_benefits=["The system detected and surfaced a coverage or API issue instead of failing silently."],
            confidence="low",
            recommended_conditions=["Confirm crime context with a local public-safety dataset before approval."],
            evidence=result,
            error=error,
        )

    incident_count = int(result["incident_count_last_year"])
    if incident_count >= HIGH_CRIME_THRESHOLD:
        stance = "concern"
        approved = False
        summary = (
            f"The proposed development '{project_description}' sits in a high-crime context based on "
            f"{incident_count} Part 1 incidents within 500 meters over the last year."
        )
        argument = (
            "The local safety context is materially challenging, and a project here should not move forward "
            "without a stronger mitigation plan for resident and public safety."
        )
        key_risks = [
            "High recent Part 1 crime concentration near the site.",
            "Potential need for design, lighting, and security mitigation.",
        ]
        key_benefits = ["The location still may benefit from investment if paired with strong safety planning."]
        confidence = "high"
        recommended_conditions = [
            "Require a site-specific safety and operations mitigation plan before approval."
        ]
    elif incident_count >= MODERATE_CRIME_THRESHOLD:
        stance = "neutral"
        approved = True
        summary = (
            f"The proposed development '{project_description}' is in a moderate public-safety context with "
            f"{incident_count} Part 1 incidents within 500 meters over the last year."
        )
        argument = (
            "The site is not free of safety concerns, but the crime context is moderate rather than clearly "
            "disqualifying, so the project can proceed with conditions."
        )
        key_risks = ["Moderate recent crime activity within walking distance of the site."]
        key_benefits = ["Safety conditions appear manageable with standard design and operations measures."]
        confidence = "medium"
        recommended_conditions = [
            "Include baseline lighting, visibility, and security design measures in project plans."
        ]
    else:
        stance = "support"
        approved = True
        summary = (
            f"The proposed development '{project_description}' is in a comparatively lower-crime context with "
            f"{incident_count} Part 1 incidents within 500 meters over the last year."
        )
        argument = (
            "The current crime signal does not indicate a major safety barrier, so public-safety conditions "
            "are more supportive than restrictive at this screening stage."
        )
        key_risks = ["Crime screening is currently limited to Baltimore City open-data coverage."]
        key_benefits = ["Lower recent Part 1 crime count relative to the defined thresholds."]
        confidence = "medium"
        recommended_conditions = ["Maintain standard Crime Prevention Through Environmental Design practices."]

    return AgentFinding(
        agent_name="Safety Agent",
        category="safety",
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
