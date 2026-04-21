"""Small manual entrypoint for local vertical-slice testing."""

from __future__ import annotations

import json

from maryland_planning_simulator.graphs import run_planning_workflow
from maryland_planning_simulator.schemas import ProjectInput


def main() -> None:
    """Run one sample Maryland proposal through the planning graph."""
    project = ProjectInput(
        address="100 State Circle, Annapolis, MD",
        project_description="300-unit mixed-use apartment complex with ground-floor retail",
    )
    report = run_planning_workflow(project)
    print(json.dumps(report.model_dump(), indent=2))


if __name__ == "__main__":
    main()
