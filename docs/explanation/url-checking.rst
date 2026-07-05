How URL Checking Works
========================

``check_broken_urls`` (and the other URL-based checks) can end up sending
thousands of requests across a large repository. This page explains the
pipeline that makes that practical without hammering any single host, and
why some failures are reported as warnings rather than errors.

The life of a URL
--------------------

1. **Extraction.** Every markdown link destination is extracted per file
   (see :doc:`link-detection`) and classified as a URL if it starts with
   ``http://``/``https://`` (protocol-relative ``//host/...`` links are
   normalized to ``https://``).

2. **Normalization and dedupe.** Before checking, each URL is normalized
   (scheme and host lowercased, trailing slash and fragment dropped; the
   query string is kept). If the same normalized URL appears in fifty
   files, it is only ever requested once - every other occurrence shares
   the same in-flight result.

3. **Per-host queueing and pacing.** Requests are grouped by host and paced
   with a minimum delay between two requests to the same host
   (``--per-host-delay``), so a link-heavy file doesn't burst a host with
   many simultaneous requests just because it happens to link to it
   repeatedly.

4. **The request itself.** Each URL is checked with a ``HEAD`` request
   first; if that isn't a success, a ``GET`` is attempted as a fallback,
   since some servers reject ``HEAD`` but allow ``GET``. A successful
   (``2xx``) response on either is treated as ``alive``.

5. **Hard-failure retries.** If neither request succeeds and there's no
   rate-limit or auth signal, the attempt is retried with exponential
   backoff up to ``--retries`` times before being reported as ``broken``.

6. **Rate limiting and auth errors return immediately.** A ``429`` (or any
   non-success response carrying ``Retry-After``) is reported as
   ``rate_limited`` right away - it is *not* retried in place. Likewise, a
   ``401``/``403`` response is reported as ``unverifiable`` immediately:
   the server is reachable but blocking automated access, and retrying
   won't change that. Retrying either case would only generate more
   traffic against a host that's already unhappy with us.

7. **Host circuit breaker.** When a host produces two rate-limited
   responses in a row, it's treated as persistently throttled: every other
   URL already queued for that host is resolved as ``rate_limited``
   without spending a network request on each, and the host is blocked
   from new requests until its ``Retry-After`` window elapses.

8. **Backpressure.** The number of URL checks in flight at once is bounded
   (``max_pending`` in the underlying configuration), so checking a huge
   repository doesn't grow memory unboundedly - submitting more work simply
   waits for a slot to free up.

Why warnings don't fail the build
-------------------------------------

``rate_limited``, ``unverifiable``, and ``transient_error`` all mean the
checker *couldn't determine* whether the link is actually broken - the host
is either throttling, blocking bots, or momentarily unreachable. Treating
these the same as a confirmed ``404`` would make CI fail on
infrastructure noise rather than real broken links, so they're reported as
warnings instead: visible, but never blocking. Only ``broken`` (a
confirmed non-2xx response with no rate-limit/auth signal) is an
error. See :doc:`../reference/exit-codes` for the full status table.

Overlapping file processing
-------------------------------

Separately from URL-level concurrency, files themselves are processed
through an adaptive window: a file's links are submitted for checking as
soon as they're extracted, without waiting for earlier files' checks to
finish first. This overlaps link extraction and I/O wait time across
files, while still bounding how many files can be "in flight"
simultaneously so memory use stays predictable regardless of how many
links a single file happens to contain.
