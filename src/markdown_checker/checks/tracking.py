"""The ``check_urls_tracking``/``check_paths_tracking`` checks: flag links missing a ``wt.mc_id`` tracking ID."""

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownPath
from markdown_checker.models import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService


class URLsTrackingCheck(BaseCheck[MarkdownURL]):
    """Check that URLs on configured tracking domains include a tracking ID."""

    name = "check_urls_tracking"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownURL]:
        """Flag every URL in ``links.urls`` whose host matches
        ``config.tracking_domains`` but is missing a ``wt.mc_id`` query
        parameter (see :meth:`MarkdownLinkBase.has_tracking
        <markdown_checker.models.base.MarkdownLinkBase.has_tracking>`). URLs
        on other hosts, or matching ``config.skip_domains``/
        ``skip_urls_containing``, are ignored. Sets
        ``issue="is missing tracking id"`` (error-level) on each match.
        ``service`` is unused: this check does no network I/O.
        """
        config = config or Config()
        skip_domains = config.skip_domains
        skip_urls_containing = config.skip_urls_containing
        tracking_domains = config.tracking_domains

        detected_issues: list[MarkdownURL] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(domain.lower() in hostname for domain in skip_domains) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if any(domain.lower() in hostname for domain in tracking_domains) and not url.has_tracking():
                url.issue = "is missing tracking id"
                detected_issues.append(url)
        return detected_issues


class PathsTrackingCheck(BaseCheck[MarkdownPath]):
    """Check that relative paths include a tracking ID."""

    name = "check_paths_tracking"
    link_type = "paths"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownPath]:
        """Flag every path in ``links.paths`` missing a ``wt.mc_id`` query
        parameter (see :meth:`MarkdownLinkBase.has_tracking
        <markdown_checker.models.base.MarkdownLinkBase.has_tracking>`),
        setting ``issue="is missing tracking id"`` (error-level) on each.
        Unlike ``check_urls_tracking``, there is no domain filter: every
        path is checked. ``config`` and ``service`` are unused.
        """
        detected_issues: list[MarkdownPath] = []
        for path in links.paths:
            if not path.has_tracking():
                path.issue = "is missing tracking id"
                detected_issues.append(path)
        return detected_issues
