import nox

PYTHON = ["3.13"]


@nox.session
def format(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("isort", ".")
    session.run("ruff", "format")


@nox.session
def coverage(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("coverage", "report", "-m")
    session.run("docstr-coverage", "--skip-private", "--skip-magic", "powercli")


@nox.session
def docs(session: nox.Session) -> None:
    session.install(".[docs]")
    session.run("sphinx-build", "-M", "html", "docs", "docs/_build")


@nox.session(python=PYTHON)
def tests(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("pytest")


@nox.session(python=PYTHON)
def lint(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("mypy", ".")
    session.run("ruff", "check")


@nox.session
def spelling(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("codespell")
