#!/usr/bin/env python3
"""Refresh the homepage's latest Substack posts from the publication RSS feed."""

from __future__ import annotations

from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
FEED_URL = "https://presingularity.substack.com/feed"
START_MARKER = "        <!-- AUTO-SUBSTACK:START -->"
END_MARKER = "        <!-- AUTO-SUBSTACK:END -->"
MAX_POSTS = 3


@dataclass(frozen=True)
class Post:
    title: str
    summary: str
    link: str
    date: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def plain_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(unescape(value))
    return " ".join(" ".join(parser.parts).split())


def normalized_link(link: str) -> str:
    return link.split("?", 1)[0].rstrip("/")


def fetch_posts() -> list[Post]:
    request = urllib.request.Request(
        FEED_URL,
        headers={"User-Agent": "mldoyle.github.io Substack sync"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        feed = ET.fromstring(response.read())

    posts: list[Post] = []
    for item in feed.findall("./channel/item"):
        title = plain_text(item.findtext("title") or "")
        summary = plain_text(item.findtext("description") or "")
        link = (item.findtext("link") or "").strip()
        published = (item.findtext("pubDate") or "").strip()

        if not title or not summary or not link or not published:
            continue

        posts.append(
            Post(
                title=title,
                summary=summary,
                link=link,
                date=parsedate_to_datetime(published).strftime("%b %Y"),
            )
        )
        if len(posts) == MAX_POSTS:
            break

    if not posts:
        raise RuntimeError("The Substack feed contained no usable posts; index.html was not changed.")
    return posts


def existing_rows(block: str) -> dict[str, str]:
    pattern = re.compile(
        r'(?P<row>        <a class="article-row" href="(?P<link>[^"]+)">.*?        </a>)',
        re.DOTALL,
    )
    return {
        normalized_link(match.group("link")): match.group("row")
        for match in pattern.finditer(block)
    }


def render_row(post: Post) -> str:
    return "\n".join(
        (
            f'        <a class="article-row" href="{escape(post.link, quote=True)}">',
            f'          <span class="article-date">{escape(post.date)}</span>',
            f'          <span class="article-title">{escape(post.title)}</span>',
            f'          <span class="article-summary">{escape(post.summary)}</span>',
            '          <span class="row-arrow" aria-hidden="true">↗</span>',
            "        </a>",
        )
    )


def main() -> None:
    source = INDEX_PATH.read_text(encoding="utf-8")
    if source.count(START_MARKER) != 1 or source.count(END_MARKER) != 1:
        raise RuntimeError("Substack markers are missing or duplicated; index.html was not changed.")

    before, remainder = source.split(START_MARKER, 1)
    current_block, after = remainder.split(END_MARKER, 1)
    saved_rows = existing_rows(current_block)
    rows = [saved_rows.get(normalized_link(post.link), render_row(post)) for post in fetch_posts()]

    refreshed_block = "\n" + "\n".join(rows) + "\n"
    refreshed_source = before + START_MARKER + refreshed_block + END_MARKER + after
    if refreshed_source != source:
        INDEX_PATH.write_text(refreshed_source, encoding="utf-8")
        print(f"Updated {INDEX_PATH.name} with {len(rows)} Substack posts.")
    else:
        print("Substack posts are already current.")


if __name__ == "__main__":
    main()
