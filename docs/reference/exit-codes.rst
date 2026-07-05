Exit Codes and Issue Severity
=================================

Exit codes
------------

- ``0``: no issues, or only warning-level issues, were found.
- ``1``: at least one error-level issue was found.

Only error-level issues fail a run; warning-level issues are always
reported but never change the exit code.

Error vs. warning
--------------------

- ``check_broken_paths``, ``check_paths_tracking``, ``check_urls_tracking``,
  and ``check_urls_locale`` only ever produce error-level issues.
- ``check_broken_urls`` produces a mix, depending on the
  :class:`~markdown_checker.models.url.URLCheckResult` returned for each URL:

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Status
     - Level
     - Meaning
   * - ``alive``
     - -
     - A ``2xx`` HTTP response was received. The link is healthy; no issue
       is reported.
   * - ``broken``
     - error
     - All retries returned non-``2xx`` responses (e.g. ``404 Not Found``)
       with no rate-limit or auth signal.
   * - ``rate_limited``
     - warning
     - A ``429 Too Many Requests`` (or another non-success response
       carrying a ``Retry-After`` header) was observed.
   * - ``transient_error``
     - warning
     - Every attempt failed with a network-level error (e.g. DNS failure,
       connection timeout) - no HTTP response was ever received.
   * - ``unverifiable``
     - warning
     - Both HEAD and GET returned ``401 Unauthorized`` or
       ``403 Forbidden``. The server is reachable but is blocking automated
       access (e.g. bot protection); the resource's real status can't be
       determined.

If a URL sees a mix of rate-limiting and transient network failures across
its retries, the outcome is reported as ``rate_limited`` unless a hard HTTP
failure was also observed - any hard failure makes the final outcome
``broken``.

Where output goes
--------------------

In local mode, warnings are printed to the terminal (yellow) after any
error output; in CI mode (``$CI=true``), they're emitted as GitHub Actions
``::warning`` annotations instead. See :doc:`report-formats` for how each
``--report-format`` represents severity.
