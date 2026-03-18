#!/usr/bin/env python3
"""Fetch Show HN text posts from the last week and rank by em-dash density."""

import argparse
import json
import html
import re
import time
import urllib.request
import urllib.parse

ALGOLIA_API = "https://hn.algolia.com/api/v1/search_by_date"
EM_DASH = "\u2014"
EN_DASH = "\u2013"


def fetch_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def strip_html(text):
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text)


def get_show_hn_text_posts():
    one_week_ago = int(time.time()) - 7 * 24 * 60 * 60
    items = []
    page = 0

    while True:
        params = urllib.parse.urlencode({
            "tags": "show_hn",
            "numericFilters": f"created_at_i>{one_week_ago}",
            "hitsPerPage": 100,
            "page": page,
        })
        data = fetch_json(f"{ALGOLIA_API}?{params}")
        hits = data.get("hits", [])
        if not hits:
            break
        for hit in hits:
            if hit.get("story_text"):
                items.append(hit)
        page += 1
        if page >= data.get("nbPages", 0):
            break

    return items


def dash_density(text, strictly_em):
    if not text:
        return 0.0
    count = text.count(EM_DASH)
    if not strictly_em:
        count += text.count(EN_DASH)
    return count / len(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strictly-em-dashes", action="store_true",
                        help="Only count em dashes (—), not en dashes (–)")
    args = parser.parse_args()

    print("Fetching Show HN text posts from the last week...")
    items = get_show_hn_text_posts()
    print(f"Found {len(items)} text posts.\n")

    results = []
    for item in items:
        title = item.get("title", "")
        body = strip_html(item.get("story_text", ""))
        combined = f"{title}\n{body}"
        density = dash_density(combined, args.strictly_em_dashes)
        results.append((density, title, item.get("objectID")))

    results.sort(reverse=True)

    densities = [d for d, _, _ in results]
    posts_with_dashes = sum(1 for d in densities if d > 0)
    avg_density = sum(densities) / len(densities) if densities else 0
    median_density = sorted(densities)[len(densities) // 2] if densities else 0
    max_density = densities[0] if densities else 0

    print(f"Posts with at least one dash: {posts_with_dashes}/{len(results)} ({posts_with_dashes / len(results) * 100:.1f}%)")
    print(f"Average density: {avg_density * 100:.4f}%")
    print(f"Median density: {median_density * 100:.4f}%")
    print(f"Max density: {max_density * 100:.4f}%")
    print()

    for i, (density, title, item_id) in enumerate(results, 1):
        pct = f"{density * 100:.4f}%"
        url = f"https://news.ycombinator.com/item?id={item_id}"
        print(f"{i}. {pct} — {title} ({url})")


if __name__ == "__main__":
    main()
