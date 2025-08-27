import shutil

import nox

nox.options.sessions = ["lint", "tests_without_report", "clean"]

@nox.session(python=["3.11"])
def tests_with_report(session):
    """Test the application, generate a coverage report."""
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run(
        "pytest",
        "tests",
        "--cov",
        "--cov-branch",
        "--cov-report=json"
    )
    session.notify("clean")

@nox.session(python=["3.11"])
def tests_without_report(session):
    """Test the application, don't generate a coverage report."""
    session.install("--upgrade", "pip")
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run("pytest", "tests")
    session.notify("clean")

@nox.session(python=["3.11"])
def lint(session):
    """Verify code linting and formatting."""
    session.install("ruff")
    session.run("ruff", "check")

@nox.session(python=["3.11"])
def clean(session):
    """Delete .nox directory (cache)."""
    shutil.rmtree(".nox", ignore_errors=True)
