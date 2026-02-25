import shutil

from dotenv import dotenv_values
import nox

nox.options.sessions = ["lint", "tests_without_report", "clean"]

@nox.session(python=["3.11"])
def tests_with_report(session):
    """Test the application, generate a coverage report."""
    env_vars = {}
    env_vars.update(dotenv_values("test.env"))
    env_vars.update(dotenv_values("../util/rabbit_mq.test.env"))
    session.run(
        "pytest",
        "tests",
        "--cov",
        "--cov-branch",
        "--cov-report=json",
        env=env_vars
    )
    session.notify("clean")

@nox.session(python=["3.11"])
def tests_without_report(session):
    """Test the application, don't generate a coverage report."""
    env_vars = {}
    env_vars.update(dotenv_values("test.env"))
    env_vars.update(dotenv_values("../util/rabbit_mq.test.env"))
    session.install("--upgrade", "pip")
    session.install("-r", "dev-requirements.txt")
    session.install("pydantic")
    session.install("python-dotenv")
    #session.run("pytest", "tests", env=env_vars)
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
