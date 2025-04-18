import shutil

import nox


@nox.session()
def tests(session):
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest", "tests/test_main.py")


@nox.session()
def lint(session):
    session.install("ruff")
    session.run("ruff", "check")


@nox.session
def clean(session):
    shutil.rmtree(".nox", ignore_errors=True)
