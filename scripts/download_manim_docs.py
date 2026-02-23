#!/usr/bin/env python3
"""
Download the complete Manim Community Edition docs (v0.20.0)
and convert every page to clean Markdown files.

Requirements:
    pip install requests beautifulsoup4 markdownify

Usage:
    python download_manim_docs.py

Output:
    ./manim_docs_md/          ← all .md files mirroring the site structure
    ./manim_docs_md/_manifest.txt  ← sorted list of every file written
"""

import os
import re
import time
import logging
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
BASE_URL = "https://docs.manim.community/en/stable/"
OUTPUT_DIR = Path("manim_docs_md")
REQUEST_DELAY = 0.3           # seconds between requests
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
USER_AGENT = "ManimDocsScraper/1.0 (Flaming Horse project)"

# Only follow links under this prefix
ALLOWED_PREFIX = "https://docs.manim.community/en/stable/"

# Skip these URL patterns (not useful for Manim API grounding)
SKIP_PATTERNS = [
    r"/changelog/",
    r"/changelog\.html$",
    r"/contributing/",
    r"/contributing\.html$",
    r"/conduct\.html$",
    r"/genindex\.html$",
    r"/_modules/",
    r"/_sources/",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# HTML → Markdown conversion
# ──────────────────────────────────────────────
def html_to_markdown(html: str, page_url: str) -> str:
    """Extract main content from a Manim doc page and convert to Markdown."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    selectors_to_remove = [
        "nav", "script", "style", "footer",
        ".sidebar-scroll", ".toc-tree",
        "#furo-sidebar", ".related-pages",
        ".headerlink",                    # ¶ permalink anchors
        "[role='navigation']",
        ".page-info", ".announcement",
        "#searchbox",
        "button.copybtn",                 # copy-to-clipboard buttons
        ".admonition.todo",
    ]
    for selector in selectors_to_remove:
        for tag in soup.select(selector):
            tag.decompose()

    # Find the main content area
    main = (
            soup.select_one("article[role='main']")
            or soup.select_one(".body")
            or soup.select_one("main")
            or soup.select_one("#furo-main-content")
            or soup.body
            or soup
    )

    # Convert to markdown
    markdown = md(
        str(main),
        heading_style="ATX",
        bullets="-",
        code_language="python",
        strip=["img"],               # strip images (not useful for LLM)
        escape_asterisks=False,
        escape_underscores=False,
    )

    # Clean up excessive blank lines
    markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)
    # Remove trailing whitespace per line
    markdown = "\n".join(line.rstrip() for line in markdown.splitlines())
    # Add source URL as a comment header
    markdown = f"<!-- source: {page_url} -->\n\n{markdown.strip()}\n"

    return markdown


# ──────────────────────────────────────────────
# URL helpers
# ──────────────────────────────────────────────
def normalize_url(url: str) -> str:
    """Strip fragment and query string for deduplication."""
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment="", query=""))


def should_skip(url: str) -> bool:
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def url_to_filepath(url: str) -> Path:
    """Map a URL to a local .md file path."""
    parsed = urlparse(url)
    path = parsed.path
    # Strip the /en/stable/ prefix
    path = re.sub(r"^/en/stable/?", "", path)
    if not path or path.endswith("/"):
        path += "index.html"
    # .html → .md
    path = re.sub(r"\.html$", ".md", path)
    return OUTPUT_DIR / path


def extract_links(soup: BeautifulSoup, page_url: str) -> list:
    """Pull all internal doc links from the page."""
    links = []
    for a in soup.find_all("a", href=True):
        full = normalize_url(urljoin(page_url, a["href"]))
        if full.startswith(ALLOWED_PREFIX) and full.endswith(".html"):
            links.append(full)
    return links


# ──────────────────────────────────────────────
# Fetch with retries
# ──────────────────────────────────────────────
def fetch(url: str, session: requests.Session):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            log.warning(f"  Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
    return None


# ──────────────────────────────────────────────
# Main crawl loop
# ──────────────────────────────────────────────
def main():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    visited: set = set()
    queue: deque = deque()
    manifest: list = []

    seed = normalize_url(BASE_URL + "index.html")
    queue.append(seed)
    visited.add(seed)

    total = 0
    skipped = 0
    errors = 0

    log.info(f"Crawling Manim docs from {BASE_URL}")
    log.info(f"Output: {OUTPUT_DIR.resolve()}")
    log.info("")

    while queue:
        url = queue.popleft()

        if should_skip(url):
            skipped += 1
            continue

        time.sleep(REQUEST_DELAY)
        resp = fetch(url, session)
        if resp is None:
            errors += 1
            log.error(f"  FAILED: {url}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Discover new links
        for link in extract_links(soup, url):
            if link not in visited:
                visited.add(link)
                queue.append(link)

        # Convert and save
        try:
            markdown = html_to_markdown(resp.text, url)
        except Exception as e:
            errors += 1
            log.error(f"  CONVERT ERROR: {url} — {e}")
            continue

        filepath = url_to_filepath(url)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(markdown, encoding="utf-8")

        total += 1
        rel = filepath.relative_to(OUTPUT_DIR)
        manifest.append(str(rel))
        log.info(f"  [{total:>4d}] {rel}")

    # Write manifest
    manifest.sort()
    manifest_path = OUTPUT_DIR / "_manifest.txt"
    manifest_path.write_text("\n".join(manifest) + "\n", encoding="utf-8")

    log.info("")
    log.info("=" * 60)
    log.info(f"DONE  {total} pages saved  |  {skipped} skipped  |  {errors} errors")
    log.info(f"Output:   {OUTPUT_DIR.resolve()}")
    log.info(f"Manifest: {manifest_path.resolve()}")


if __name__ == "__main__":
    main()
