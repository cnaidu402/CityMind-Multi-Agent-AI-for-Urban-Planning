"""Development server entrypoint for the Flask API."""

from __future__ import annotations

import os

from maryland_planning_simulator.api import create_app

app = create_app()


def main() -> None:
    """Run the local Flask development server."""
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
