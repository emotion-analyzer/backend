import os
import shutil

import nox


@nox.session()
def tests(session):
    """Test the application."""
    session.env["TESTING"] = "1"
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest", "tests/test_main.py")
    # This should be done in a cleaner way.
    if os.path.exists("database.db"):
        os.remove("database.db")


@nox.session()
def lint(session):
    """Verify code linting and formatting."""
    session.install("ruff")
    session.run("ruff", "check")


@nox.session
def clean(session):
    """Delete .nox directory (cache)."""
    shutil.rmtree(".nox", ignore_errors=True)
