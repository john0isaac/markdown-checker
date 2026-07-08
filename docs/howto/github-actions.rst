How to Run markdown-checker in GitHub Actions
=================================================

Goal: check markdown/notebook files on every pull request and get the
results posted back as a comment or as inline annotations.

Use the official action
---------------------------

The `action-check-markdown <https://github.com/marketplace/actions/check-markdown>`_
GitHub Action wraps markdown-checker and automatically posts its Markdown
report as a pull request comment.

Add a workflow file such as ``.github/workflows/check-markdown.yml``,
replacing ``guide-url`` with the URL of your own contribution guide:

.. code-block:: yaml

    name: Check Markdown

    on:
      pull_request:
        paths:
          - "**.md"
          - "**.ipynb"

    permissions:
      contents: read

    jobs:
      check-broken-paths:
        runs-on: ubuntu-latest
        permissions:
          pull-requests: write
          contents: read
        steps:
          - uses: actions/checkout@v7
          - uses: john0isaac/action-check-markdown@v1.3.0
            with:
              github-token: ${{ secrets.GITHUB_TOKEN }}
              command: check_broken_paths
              directory: ./
              guide-url: "https://github.com/<owner>/<repo>/blob/main/CONTRIBUTING.md"

The ``command`` input selects which check to run it
supports ``check_broken_paths``, ``check_paths_tracking``,
``check_urls_tracking``, and ``check_urls_locale``
``check_broken_urls``. Add a separate job (or step) per command if you want
to run more than one check in the same workflow.

Verify it worked
------------------

Open a pull request that touches a checked file and confirm the comment (for
the wrapper action) or inline annotations (for a direct CLI step) appear.
See :doc:`report-formats` and :doc:`../reference/report-formats` for what
each format looks like, and :doc:`../reference/exit-codes` for how CI mode
changes exit-code and warning behaviour.
