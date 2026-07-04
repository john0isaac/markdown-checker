from abc import ABC
from abc import abstractmethod
from typing import cast
from typing import Generic
from typing import Literal
from typing import TypeVar

from markdown_checker.models import Config
from markdown_checker.models import MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService

TLink = TypeVar("TLink", bound=MarkdownLinkBase, covariant=True)


class BaseCheck(Generic[TLink], ABC):
    """Abstract base class for all link checks."""

    name: str
    link_type: Literal["paths", "urls"]

    @abstractmethod
    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[TLink]:
        """
        Run the check against the extracted links.

        Args:
            links (MarkdownLinks): Extracted URLs and paths from a file.
            config: Runtime configuration for the check run.
            service: Optional shared URL-checking pipeline (dedupe memo,
                per-host pacing, circuit breaker). Only used by checks with
                link_type "urls"; ignored otherwise. When None, URL checks
                fall back to a private, run-scoped service instance.

        Returns:
            List of links that failed the check, each with an .issue set.
        """
        raise NotImplementedError

    def submit(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> object:
        """
        Begin checking without blocking the caller, returning an opaque
        "pending" token to be finished later via ``collect()``.

        The default implementation simply runs the check synchronously and
        hands the finished result to ``collect()`` unchanged - appropriate
        for checks with no network I/O to overlap with other files. Checks
        that can hand work off to a shared service (e.g. URL checks) should
        override both ``submit()`` and ``collect()`` to split the non-blocking
        submission from the blocking wait for results.

        Args:
            links (MarkdownLinks): Extracted URLs and paths from a file.
            config: Runtime configuration for the check run.
            service: Optional shared URL-checking pipeline.

        Returns:
            An opaque token to pass to ``collect()``.
        """
        return self.run(links=links, config=config, service=service)

    def collect(self, pending: object) -> list[TLink]:
        """
        Resolve a pending token from ``submit()`` into final results.

        Args:
            pending: The token returned by a matching ``submit()`` call.

        Returns:
            List of links that failed the check, each with an .issue set.
        """
        return cast(list[TLink], pending)
