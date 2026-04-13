from markdown_checker.checks.base import BaseCheck
from markdown_checker.checks.broken_paths import BrokenPathsCheck
from markdown_checker.checks.broken_urls import BrokenURLsCheck
from markdown_checker.checks.locale import URLsLocaleCheck
from markdown_checker.checks.tracking import PathsTrackingCheck, URLsTrackingCheck

# Maps the CLI --func argument value to the corresponding check instance.
REGISTRY: dict[str, BaseCheck] = {
    BrokenPathsCheck.name: BrokenPathsCheck(),
    BrokenURLsCheck.name: BrokenURLsCheck(),
    URLsTrackingCheck.name: URLsTrackingCheck(),
    PathsTrackingCheck.name: PathsTrackingCheck(),
    URLsLocaleCheck.name: URLsLocaleCheck(),
}

__all__ = ["REGISTRY", "BaseCheck"]
