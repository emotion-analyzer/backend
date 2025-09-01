import os
import shutil

import nox

nox.options.sessions = ["lint", "tests_without_report", "clean"]

@nox.session()
def remove_database(session):
    """Delete database."""
    if os.path.exists("database.db"):
        os.remove("database.db")


@nox.session()
def tests_without_report(session):
    """Test the application, don't generate a coverage report."""
    session.install("--upgrade", "pip")
    session.env["APP_ENV"] = "test.env"
    session.env["DATABASE_URL"] = "sqlite:///database.db"
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run("pytest", "tests")
    session.notify("remove_database")

@nox.session()
def tests_with_report(session):
    """Test the application, generate a coverage report."""
    session.install("--upgrade", "pip")
    session.env["APP_ENV"] = "test.env"
    session.env["DATABASE_URL"] = "sqlite:///database.db"
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run(
        "pytest",
        "tests",
        "--cov",
        "--cov-branch",
        "--cov-report=json"
    )
    session.notify("remove_database")

@nox.session()
def lint(session):
    """Verify code linting and formatting."""
    session.install("ruff")
    session.run("ruff", "check")

@nox.session
def clean(session):
    """Delete .nox directory (cache)."""
    shutil.rmtree(".nox", ignore_errors=True)
