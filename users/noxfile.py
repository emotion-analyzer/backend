import os
import shutil

from dotenv import dotenv_values
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
    env_vars = {}
    env_vars.update(dotenv_values("test.env"))
    env_vars.update(dotenv_values("../util/database.test.env"))
    session.install("--upgrade", "pip")
    session.env["APP_ENV"] = "test.env"
    session.env["DATABASE_URL"] = "sqlite:///database.db"
    session.env["TESTING"] = "1"
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run("pytest", "tests", env=env_vars)
    session.notify("remove_database")

@nox.session()
def tests_with_report(session):
    """Test the application, generate a coverage report."""
    env_vars = {}
    env_vars.update(dotenv_values("test.env"))
    env_vars.update(dotenv_values("../util/database.test.env"))
    session.install("--upgrade", "pip")
    session.env["APP_ENV"] = "test.env"
    session.env["TESTING"] = "1"
    session.env["DATABASE_URL"] = "sqlite:///database.db"
    session.install("-r", "requirements.txt", "-r", "dev-requirements.txt")
    session.run(
        "pytest",
        "tests",
        "--cov",
        "--cov-branch",
        "--cov-report=json",
        env=env_vars
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
