"""Streamlit frontend for the Maryland multi-agent planning simulator."""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

DEFAULT_API_BASE_URL = os.getenv("SIMULATOR_API_BASE_URL", "http://127.0.0.1:5000")
DEFAULT_ADDRESS = "100 State Circle, Annapolis, MD"
DEFAULT_PROJECT_DESCRIPTION = "300-unit mixed-use apartment complex with ground-floor retail"
REQUEST_TIMEOUT_SECONDS = 90


def main() -> None:
    """Render the Streamlit interface."""
    st.set_page_config(
        page_title="Maryland Urban Planning Simulator",
        page_icon="M",
        layout="wide",
    )

    _render_header()

    with st.sidebar:
        st.subheader("Connection")
        api_base_url = st.text_input(
            "Flask API Base URL",
            value=DEFAULT_API_BASE_URL,
            help="The Streamlit app sends proposals to the Flask /simulate endpoint.",
        ).rstrip("/")
        st.caption("Run the Flask API first, then point Streamlit at that base URL.")

        st.subheader("Sample Ideas")
        st.caption("Try Maryland-focused proposals such as transit-oriented housing, adaptive reuse, or mixed-use infill.")

    left_col, right_col = st.columns([1.1, 1.2], gap="large")

    with left_col:
        payload = _render_input_form()

    with right_col:
        st.subheader("How It Works")
        st.markdown(
            """
            1. Geocode the project site in Maryland.
            2. Run environmental, safety, transit, infrastructure, and economic reviews.
            3. Orchestrate a multi-agent debate.
            4. Return a structured impact report.
            """
        )

    if payload is not None:
        _submit_simulation(api_base_url=api_base_url, payload=payload)

    report = st.session_state.get("latest_report")
    if report:
        _render_report(report)
    elif st.session_state.get("latest_error"):
        st.error(st.session_state["latest_error"])


def _render_header() -> None:
    """Render the app title and short context."""
    st.title("Maryland Multi-Agent Urban Planning Simulator")
    st.caption(
        "A Maryland-only planning workflow that debates proposed development using GIS, civic, and market signals."
    )


def _render_input_form() -> dict[str, str] | None:
    """Render the proposal form and return payload data when submitted."""
    st.subheader("Project Input")
    with st.form("simulation_form", clear_on_submit=False):
        address = st.text_input(
            "Address or Area",
            value=DEFAULT_ADDRESS,
            help="Example: 100 State Circle, Annapolis, MD",
        )
        project_description = st.text_area(
            "Project Description",
            value=DEFAULT_PROJECT_DESCRIPTION,
            height=180,
            help="Describe the proposed Maryland development in plain language.",
        )
        submitted = st.form_submit_button("Run Simulation", use_container_width=True)

    if not submitted:
        return None

    return {
        "address": address.strip(),
        "project_description": project_description.strip(),
    }


def _submit_simulation(api_base_url: str, payload: dict[str, str]) -> None:
    """Send the project proposal to the Flask API and store the latest response."""
    if not payload["address"] or not payload["project_description"]:
        st.session_state["latest_report"] = None
        st.session_state["latest_error"] = "Both address and project description are required."
        return

    simulate_url = f"{api_base_url}/simulate"
    with st.spinner("Running the planning simulation..."):
        try:
            response = requests.post(simulate_url, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        except requests.RequestException as exc:
            st.session_state["latest_report"] = None
            st.session_state["latest_error"] = (
                f"Could not reach the Flask API at {simulate_url}. "
                f"Make sure the backend is running. Details: {exc}"
            )
            return

    try:
        response_payload = response.json()
    except ValueError:
        st.session_state["latest_report"] = None
        st.session_state["latest_error"] = (
            f"The API returned a non-JSON response with status {response.status_code}."
        )
        return

    if response.ok:
        st.session_state["latest_report"] = response_payload
        st.session_state["latest_error"] = None
        return

    st.session_state["latest_report"] = None
    st.session_state["latest_error"] = response_payload.get(
        "error",
        f"Simulation failed with status {response.status_code}.",
    )


def _render_report(report: dict[str, Any]) -> None:
    """Render the simulation results."""
    st.divider()
    st.subheader("Simulation Report")

    approved = bool(report.get("approved"))
    approval_label = "Approved" if approved else "Not Approved"
    display_plain_summary = _get_display_plain_summary(report)
    if approved:
        st.success(f"Final Decision: {approval_label}")
    else:
        st.error(f"Final Decision: {approval_label}")

    top_left, top_right, top_far_right = st.columns(3)
    coordinates = report.get("coordinates", {})
    debate = report.get("debate", {})

    with top_left:
        st.metric("Latitude", coordinates.get("latitude", "N/A"))
    with top_right:
        st.metric("Longitude", coordinates.get("longitude", "N/A"))
    with top_far_right:
        st.metric("Assessments", len(report.get("assessments", [])))

    st.markdown("**Plain-Language Takeaway**")
    st.write(display_plain_summary)

    st.markdown("**Final Synthesis**")
    st.write(report.get("final_synthesis", "No final synthesis returned."))

    synthesis_meta = []
    if report.get("synthesis_provider"):
        synthesis_meta.append(f"Provider: `{report['synthesis_provider']}`")
    if report.get("synthesis_model"):
        synthesis_meta.append(f"Model: `{report['synthesis_model']}`")
    if synthesis_meta:
        st.caption(" | ".join(synthesis_meta))
    if report.get("synthesis_error"):
        st.warning(report["synthesis_error"])

    _render_debate_section(debate)
    _render_assessments_section(report.get("assessments", []))
    _render_raw_json(report)


def _render_debate_section(debate: dict[str, Any]) -> None:
    """Render the debate summary and conditions."""
    st.markdown("**Debate Summary**")
    if debate.get("debate_summary"):
        st.write(debate["debate_summary"])
    else:
        st.info("No debate summary was returned.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("**Consensus Points**")
        _render_string_list(debate.get("consensus_points", []), empty_message="No consensus points recorded.")
        st.markdown("**Recommended Conditions**")
        _render_string_list(
            debate.get("recommended_conditions", []),
            empty_message="No recommended conditions recorded.",
        )
    with col2:
        st.markdown("**Conflicts**")
        _render_string_list(debate.get("conflicts", []), empty_message="No major agent conflicts recorded.")
        st.markdown("**Agent Votes**")
        votes = debate.get("agent_votes", {})
        if isinstance(votes, dict) and votes:
            for agent_name, stance in votes.items():
                st.write(f"`{agent_name}`: {stance}")
        else:
            st.caption("No agent votes recorded.")


def _render_assessments_section(assessments: list[dict[str, Any]]) -> None:
    """Render each agent assessment as its own expandable card."""
    st.markdown("**Agent Assessments**")
    if not assessments:
        st.info("No agent assessments were returned.")
        return

    for assessment in assessments:
        agent_name = assessment.get("agent_name", "Unknown Agent")
        stance = assessment.get("stance", "unknown")
        title = f"{agent_name} | {stance}"
        with st.expander(title, expanded=False):
            st.write(assessment.get("summary", "No summary provided."))
            if assessment.get("argument"):
                st.markdown("**Argument**")
                st.write(assessment["argument"])
            st.markdown("**Confidence**")
            st.write(assessment.get("confidence", "unknown"))
            st.markdown("**Key Benefits**")
            _render_string_list(assessment.get("key_benefits", []), empty_message="No benefits listed.")
            st.markdown("**Key Risks**")
            _render_string_list(assessment.get("key_risks", []), empty_message="No risks listed.")
            st.markdown("**Recommended Conditions**")
            _render_string_list(
                assessment.get("recommended_conditions", []),
                empty_message="No conditions listed.",
            )
            if assessment.get("error"):
                st.warning(assessment["error"])
            with st.expander("Evidence", expanded=False):
                st.json(assessment.get("evidence", {}))


def _render_raw_json(report: dict[str, Any]) -> None:
    """Expose the full JSON payload for debugging and API consumers."""
    with st.expander("Raw JSON Report", expanded=False):
        st.json(report)


def _render_string_list(items: list[Any], empty_message: str) -> None:
    """Render a flat string list or a fallback caption."""
    if not isinstance(items, list) or not items:
        st.caption(empty_message)
        return

    for item in items:
        st.write(f"- {item}")


def _get_display_plain_summary(report: dict[str, Any]) -> str:
    """Return backend plain-language summary when present, otherwise derive one."""
    plain_summary = report.get("plain_language_summary")
    if isinstance(plain_summary, str) and plain_summary.strip():
        return plain_summary

    approved = bool(report.get("approved"))
    assessments = report.get("assessments", [])
    supportive_categories = []
    blocked_categories = []

    if isinstance(assessments, list):
        for item in assessments:
            category = item.get("category")
            stance = item.get("stance")
            item_approved = bool(item.get("approved"))
            if isinstance(category, str):
                label = "economics" if category == "economic" else category
                if stance == "support" and label not in supportive_categories:
                    supportive_categories.append(label)
                if (stance == "concern" or (stance == "neutral" and not item_approved)) and label not in blocked_categories:
                    blocked_categories.append(label)

    support_text = _humanize_categories(supportive_categories)
    blocked_text = _humanize_categories(blocked_categories)

    if approved:
        if support_text:
            return (
                f"This project looks strong overall, especially on {support_text}, "
                "so the simulator approves it at the current screening stage."
            )
        return (
            "The simulator approves it because no agent found a "
            "blocking issue in the current review."
        )

    if blocked_text and support_text:
        return (
            f"This project looks promising on {support_text}, but it is not approved yet "
            f"because {blocked_text} needs more reliable data or manual review."
        )

    return (
        "This project is not approved yet because some required checks still need "
        "stronger data or manual review."
    )


def _humanize_categories(categories: list[str]) -> str:
    """Turn a list like ['environment', 'transit', 'economics'] into readable text."""
    if not categories:
        return ""
    if len(categories) == 1:
        return categories[0]
    if len(categories) == 2:
        return f"{categories[0]} and {categories[1]}"
    return f"{', '.join(categories[:-1])}, and {categories[-1]}"


if __name__ == "__main__":
    main()
