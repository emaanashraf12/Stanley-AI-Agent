import requests

from bs4 import BeautifulSoup

from urllib.parse import (
    urljoin,
    urlparse,
    urlunparse
)

from collections import deque


class WebsiteCrawler:

    def __init__(
        self,
        base_url,
        max_pages=None
    ):

        self.base_url = (
            base_url.rstrip("/")
        )

        self.max_pages = max_pages

        self.base_domain = (
            urlparse(
                self.base_url
            ).netloc.lower()
        )

        self.visited = set()

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(compatible; StanleyToursKnowledgeBase/1.0)"
                )
            }
        )

    # ==========================================================
    # NORMALIZE URL
    # ==========================================================

    def normalize_url(
        self,
        url
    ):

        if not url:
            return None

        url = urljoin(
            self.base_url + "/",
            url
        )

        parsed = urlparse(
            url
        )

        # Only HTTP / HTTPS pages
        if parsed.scheme not in (
            "http",
            "https"
        ):
            return None

        # Remove fragments such as:
        # /packages#section
        parsed = parsed._replace(
            fragment=""
        )

        # Remove common tracking query parameters by
        # removing query strings entirely.
        #
        # This prevents duplicate indexing such as:
        # /package?id...
        # /package?utm_source...
        parsed = parsed._replace(
            query=""
        )

        normalized = urlunparse(
            parsed
        )

        # Avoid duplicate:
        # /about
        # /about/
        if (
            normalized.endswith("/")
            and normalized != self.base_url + "/"
        ):

            normalized = (
                normalized.rstrip("/")
            )

        return normalized

    # ==========================================================
    # VALID INTERNAL PAGE
    # ==========================================================

    def is_valid_url(
        self,
        url
    ):

        if not url:
            return False

        parsed = urlparse(
            url
        )

        if parsed.netloc.lower() != self.base_domain:
            return False

        path = parsed.path.lower()

        # ------------------------------------------------------
        # Skip non-HTML assets
        # ------------------------------------------------------

        blocked_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".ico",
            ".css",
            ".js",
            ".xml",
            ".zip",
            ".rar",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot"
        )

        if path.endswith(
            blocked_extensions
        ):
            return False

        # ------------------------------------------------------
        # Do not crawl WordPress administrative/system pages
        # ------------------------------------------------------

        blocked_paths = (
            "/wp-admin",
            "/wp-login",
            "/wp-json",
            "/wp-content/",
            "/wp-includes/"
        )

        for blocked in blocked_paths:

            if blocked in path:
                return False

        return True

    # ==========================================================
    # CRAWL
    # ==========================================================

    def crawl(
        self
    ):

        start_url = self.normalize_url(
            self.base_url
        )

        queue = deque(
            [start_url]
        )

        queued = {
            start_url
        }

        pages = []

        failed = []

        while queue:

            # Optional safety limit.
            # None = crawl until no new internal pages remain.
            if (
                self.max_pages is not None
                and len(self.visited) >= self.max_pages
            ):
                break

            url = queue.popleft()

            queued.discard(
                url
            )

            if url in self.visited:
                continue

            if not self.is_valid_url(
                url
            ):
                continue

            print(
                "Crawling:",
                url
            )

            try:

                response = self.session.get(
                    url,
                    timeout=15,
                    allow_redirects=True
                )

                if response.status_code != 200:

                    print(
                        "Skipped:",
                        response.status_code,
                        url
                    )

                    failed.append(
                        url
                    )

                    self.visited.add(
                        url
                    )

                    continue

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        ""
                    ).lower()
                )

                # Only index HTML pages
                if (
                    "text/html"
                    not in content_type
                ):

                    print(
                        "Skipped non-HTML:",
                        url
                    )

                    self.visited.add(
                        url
                    )

                    continue

                final_url = self.normalize_url(
                    response.url
                )

                if not self.is_valid_url(
                    final_url
                ):
                    continue

                self.visited.add(
                    url
                )

                self.visited.add(
                    final_url
                )

                soup = BeautifulSoup(
                    response.text,
                    "lxml"
                )

                pages.append(
                    {
                        "url": final_url,
                        "html": response.text
                    }
                )

                # --------------------------------------------------
                # Discover internal links
                # --------------------------------------------------

                for link in soup.find_all(
                    "a",
                    href=True
                ):

                    next_url = self.normalize_url(
                        link.get(
                            "href"
                        )
                    )

                    if not next_url:
                        continue

                    if not self.is_valid_url(
                        next_url
                    ):
                        continue

                    if next_url in self.visited:
                        continue

                    if next_url in queued:
                        continue

                    queue.append(
                        next_url
                    )

                    queued.add(
                        next_url
                    )

            except Exception as exc:

                print(
                    "CRAWL ERROR:",
                    url,
                    repr(exc)
                )

                failed.append(
                    url
                )

                self.visited.add(
                    url
                )

        print()
        print(
            "=========================================="
        )
        print(
            "CRAWL COMPLETE"
        )
        print(
            "=========================================="
        )
        print(
            "HTML pages collected:",
            len(pages)
        )
        print(
            "URLs visited:",
            len(self.visited)
        )
        print(
            "Failed URLs:",
            len(failed)
        )
        print(
            "=========================================="
        )

        return pages