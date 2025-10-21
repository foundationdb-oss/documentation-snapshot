#!/usr/bin/env python3
"""
Dump public topics from a Discourse-hosted forum (read-only) into JSON files.

Usage:
    python tools/discourse_dump.py --base-url https://forums.foundationdb.org
                                   --output-dir archives/forums/2025-10-21

The script fetches paginated topic listings from `/latest.json`, then downloads
each topic's full JSON representation (`/t/{slug}/{id}.json`) and writes them to
`topics/{topic_id}.json`. Metadata about the crawl is saved to `metadata.json`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Dict, Iterable

import requests

DEFAULT_USER_AGENT = (
    "FoundationDB-Documentation-Snapshot/1.0 "
    "(https://github.com/foundationdb-oss/documentation-snapshot)"
)
TOPICS_PER_PAGE = 30
SLEEP_SECONDS = 0.5


def fetch_json(url: str, session: requests.Session, *, params: Dict | None = None) -> Dict:
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def iter_latest_topics(base_url: str, session: requests.Session) -> Iterable[Dict]:
    page = 0
    while True:
        page += 1
        url = f"{base_url}/latest.json"
        data = fetch_json(url, session, params={"page": page - 1})
        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break
        for topic in topics:
            yield topic
        if len(topics) < TOPICS_PER_PAGE:
            break
        time.sleep(SLEEP_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump public Discourse topics to JSON.")
    parser.add_argument("--base-url", required=True, help="Base URL of the Discourse forum (e.g., https://forums.foundationdb.org)")
    parser.add_argument("--output-dir", required=True, type=pathlib.Path, help="Directory to store the downloaded JSON files")
    parser.add_argument("--max-topics", type=int, default=None, help="Optional cap on number of topics to fetch (for testing)")
    parser.add_argument("--sleep", type=float, default=SLEEP_SECONDS, help="Seconds to pause between topic downloads")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    output_dir = args.output_dir.resolve()
    topics_dir = output_dir / "topics"
    topics_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    seen_ids = set()
    total = 0
    for topic in iter_latest_topics(base_url, session):
        topic_id = topic["id"]
        if topic_id in seen_ids:
            continue
        seen_ids.add(topic_id)
        slug = topic["slug"]
        topic_url = f"{base_url}/t/{slug}/{topic_id}.json"
        topic_data = fetch_json(topic_url, session)
        out_path = topics_dir / f"{topic_id}.json"
        out_path.write_text(json.dumps(topic_data, indent=2), encoding="utf-8")
        total += 1
        if args.max_topics and total >= args.max_topics:
            break
        time.sleep(args.sleep)

    metadata = {
        "source": base_url,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "topic_count": total,
        "output_dir": str(output_dir),
        "command": " ".join(sys.argv),
    }
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Captured {total} topics to {topics_dir}")


if __name__ == "__main__":
    main()
