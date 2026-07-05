Using ``markdown-checker`` in GitHub Actions
============================================

You can run this tool within a GitHub workflow using the
`action-check-markdown <https://github.com/marketplace/actions/check-markdown>`_
GitHub action.

The action will automatically post the output of the tool to your GitHub pull
request as a comment.

Example usage
--------------

Add a workflow file such as ``.github/workflows/check-markdown.yml`` with the
following contents, replacing ``guide-url`` with the URL of your own
contribution guide:

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
          - uses: actions/checkout@v4
          - uses: john0isaac/action-check-markdown@v1.1.0
            with:
              github-token: ${{ secrets.GITHUB_TOKEN }}
              command: check_broken_paths
              directory: ./
              guide-url: "https://github.com/<owner>/<repo>/blob/main/CONTRIBUTING.md"

The ``command`` input selects which check to run. Available options are
``check_broken_paths``, ``check_paths_tracking``, ``check_urls_tracking``, and
``check_urls_locale``. Add a separate job (or step) per command if you want to
run more than one check in the same workflow.
