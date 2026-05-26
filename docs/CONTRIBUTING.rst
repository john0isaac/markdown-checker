Contribution
============

How to `contribute to the project <https://docs.github.com/en/get-started/quickstart/contributing-to-projects>`_?

While contributing, each contributor should keep the
:doc:`Code of Conduct <CODE_OF_CONDUCT>` in mind.

This repository is open for everyone to contribute and is maintained by
`John Aziz <https://github.com/john0isaac>`_.

Develop Locally
---------------

Install all dependencies and the package in editable mode:

.. code-block:: shell

	 uv sync

Activate the virtual environment:

.. code-block:: shell

	 source .venv/bin/activate

Any changes you make to the source will take effect immediately.

First Steps
-----------

These are the most common commands you will use:

- ``pytest``: Run the unit tests.
- ``mypy``: Run the type checker.
- ``ruff``: Run the linter and formatter tools.
- ``tox run -e docs``: Build the documentation.

These are some more specific commands if you need them:

- ``tox parallel``: Run all test environments that will be run in CI, in
	parallel. Python versions that are not installed are skipped.
- ``pre-commit``: Run the linter and formatter tools. Only staged files are
	checked, and this runs automatically before each commit.
- ``pre-commit run --all-files``: Run the pre-commit hooks against all files,
	including unchanged and unstaged files.
- ``tox run -e py3.11``: Run unit tests with a specific Python version. The
	version must be installed.
- ``tox run -e style``: Run all pre-commit hooks on all files via tox.
- ``tox run -e typing``: Run all typing checks.
- ``tox run -e docs``: Build the documentation in strict mode.
- ``tox run -e docs-auto``: Serve the documentation locally with auto-reload.
- ``tox run -e update-actions``: Update GitHub Actions pins.
- ``tox run -e update-pre_commit``: Update pre-commit hook pins.
- ``tox run -e update-requirements``: Update the ``uv.lock`` file.

.. tip::

	 ``tox run`` and ``tox parallel`` can be shortened to ``tox r`` and
	 ``tox p``.
