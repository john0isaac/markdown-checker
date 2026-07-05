"""The ``check_urls_locale`` check: flags URLs containing a locale segment (e.g. ``/en-us/``)."""

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService

_BUILTIN_SKIP_DOMAINS: list[str] = [
    "www.nvidia.com",
]
"""Domains that are always exempt from this check, in addition to
``config.skip_domains`` (e.g. NVIDIA's docs always include a locale segment).
"""


class URLsLocaleCheck(BaseCheck[MarkdownURL]):
    """Check that URLs do not contain a country/language locale segment."""

    name = "check_urls_locale"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownURL]:
        """Flag every URL in ``links.urls`` whose path contains a locale
        segment (see :meth:`MarkdownLinkBase.has_locale
        <markdown_checker.models.base.MarkdownLinkBase.has_locale>`), unless
        its host is in ``config.skip_domains``, :data:`_BUILTIN_SKIP_DOMAINS`,
        or its URL matches ``config.skip_urls_containing``. Sets
        ``issue="has locale"`` (error-level) on each match. ``service`` is
        unused: this check does no network I/O.
        """
        config = config or Config()
        effective_skip = [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]
        skip_urls_containing = config.skip_urls_containing

        detected_issues: list[MarkdownURL] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(domain.lower() in hostname for domain in effective_skip) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if url.has_locale():
                url.issue = "has locale"
                detected_issues.append(url)
        return detected_issues
