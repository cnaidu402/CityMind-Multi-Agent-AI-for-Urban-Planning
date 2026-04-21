"""Environmental review agent for Maryland Critical Area impact."""

from __future__ import annotations

from maryland_planning_simulator.schemas import AgentFinding
from maryland_planning_simulator.tools import check_maryland_critical_area


def evaluate_environmental_impact(lat: float, lon: float, project_description: str) -> AgentFinding:
    """
    Review whether the proposed site intersects Maryland's Critical Area.

    The first version intentionally uses a narrow, high-signal rule:
    projects inside a Critical Area trigger concern and a non-approval vote.
    """
    result = check_maryland_critical_area(lat=lat, lon=lon)
    error = result.get("error")

    if error:
        return AgentFinding(
            agent_name="Environmental Agent",
            category="environment",
            stance="neutral",
            approved=False,
            summary=(
                "Environmental review could not confirm Critical Area status due to an upstream data error. "
                "The project should be flagged for manual review before approval."
            ),
            argument=(
                "Because the Critical Area check failed, the environmental record is incomplete and the site "
                "should not receive automated environmental clearance."
            ),
            key_risks=["Critical Area status is unverified due to data failure."],
            key_benefits=["Environmental review pipeline identified the need for manual escalation."],
            confidence="low",
            recommended_conditions=["Verify Critical Area status against Maryland iMAP before approval."],
            evidence=result,
            error=error,
        )

    is_in_critical_area = bool(result["is_in_critical_area"])
    if is_in_critical_area:
        return AgentFinding(
            agent_name="Environmental Agent",
            category="environment",
            stance="concern",
            approved=False,
            summary=(
                f"The proposed development '{project_description}' overlaps Maryland's Critical Area. "
                "That creates a likely environmental permitting constraint and should block automatic approval."
            ),
            argument=(
                "The site intersects a Maryland Critical Area polygon, so the proposal faces a direct "
                "environmental constraint rather than a minor contextual concern."
            ),
            key_risks=[
                "Potential Chesapeake Bay Critical Area permitting constraints.",
                "Higher likelihood of environmental mitigation requirements.",
            ],
            key_benefits=["Environmental constraint was detected early in automated review."],
            confidence="high",
            recommended_conditions=[
                "Complete a formal environmental and permitting review before any site approval.",
            ],
            evidence=result,
        )

    return AgentFinding(
        agent_name="Environmental Agent",
        category="environment",
        stance="support",
        approved=True,
        summary=(
            f"The proposed development '{project_description}' does not appear to intersect Maryland's "
            "Critical Area in the current iMAP layers."
        ),
        argument=(
            "Current Maryland iMAP layers do not show the site inside a Critical Area polygon, so this "
            "proposal does not trigger the strongest environmental red flag in the current screening stage."
        ),
        key_risks=["Environmental screening is still limited to Critical Area status in this version."],
        key_benefits=["No direct Critical Area overlap detected in the current environmental screen."],
        confidence="medium",
        recommended_conditions=["Continue with normal environmental due diligence during later review."],
        evidence=result,
    )
