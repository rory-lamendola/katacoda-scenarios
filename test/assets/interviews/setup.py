"""Installation config for interviews."""

import setuptools

# pylint: disable=invalid-name
#
# add dependencies on local, in-tree components to `requirements.txt`
# instead of here
install_reqs = [
    "alembic",
    "dictalchemy",
    "flask",
    "flask_restful",
    "psycopg2-binary",
    "sqlalchemy",
    "uwsgi",
    "pals",
    "healthcheck",
]

tests_require = [
    "bandit",
    "black",
    "coverage",
    "flake8",
    "flake8-broken-line",
    "flake8-bugbear",
    "flake8-docstrings",
    "flake8-tidy-imports",
    "isort",
    "mypy",
    "pylint",
    "pytest",
    "pytest-cov",
    "pytest-postgresql",
    "pytest-randomly",
    "tox",
    "tox-pyenv",
    "yamllint",
]

setuptools.setup(
    name="interviews",
    packages=setuptools.find_namespace_packages(
        include=["interviews*"], exclude=["*.test"]),
    package_data={"interviews": ["py.typed"]},
    setup_requires=[
        "setuptools_scm",
        "pytest-runner",
    ],
    
    description="interviews",
    author="Petal Card Inc.",
    install_requires=install_reqs,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={"loadtest.scenario":[]},
    zip_safe=False,
)
