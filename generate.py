#!/usr/bin/env python3
"""Generate output.md from a public Google Sheets CSV export.

Usage:
    python generate.py --url "<CSV_EXPORT_URL>" --out small_plates.md

The script accepts the CSV URL via `--url` or the environment variable `CSV_URL`.
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import requests
except Exception:
    requests = None

# Load .env into environment if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass
class Row:
    topic: str
    body: str
    sources: List[str]
    timestamp: datetime


def fetch_csv(url: str) -> str:
    if requests is None:
        raise RuntimeError("requests is required to fetch remote CSV. Add it to dependencies.")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    raw = resp.content
    # Try common encodings: UTF-8 with BOM, UTF-8, then latin-1 as a fallback
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    # Last resort: replace invalid chars
    return raw.decode("utf-8", errors="replace")


def parse_timestamp(value: str) -> datetime:
    value = value.strip()
    # try ISO formats first
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    # Try common Google Sheets display formats
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    # fallback: naive parse using fromisoformat
    try:
        return datetime.fromisoformat(value)
    except Exception:
        raise ValueError(f"Unrecognized timestamp format: '{value}'")


def normalize_header(h: str) -> str:
    return h.strip().lower()


def map_headers(headers: List[str]) -> Dict[str, int]:
    """Map incoming CSV headers to required fields: topic, body, sources, timestamp."""
    mapping = {}
    for i, h in enumerate(headers):
        n = normalize_header(h)
        if n in ("topic", "topics"):
            mapping["topic"] = i
        elif n in ("body", "text", "content"):
            mapping["body"] = i
        elif n.startswith("source") or "sources" in n:
            mapping["sources"] = i
        elif n in ("timestamp", "time", "date"):
            mapping["timestamp"] = i
    required = {k: mapping[k] for k in ("topic", "body", "sources", "timestamp") if k in mapping}
    if len(required) != 4:
        raise ValueError(f"Couldn't map headers to required fields. Found: {mapping}")
    return required


def parse_rows(csv_text: str) -> List[Row]:
    # Use StringIO to ensure correct newline handling and avoid encoding issues
    sio = io.StringIO(csv_text)
    reader = csv.reader(sio)
    rows = list(reader)
    if not rows:
        return []
    headers = rows[0]
    mapping = map_headers(headers)
    parsed: List[Row] = []
    for r in rows[1:]:
        if len(r) <= max(mapping.values()):
            continue
        topic = r[mapping["topic"]].strip()
        body = r[mapping["body"]].strip()
        sources_raw = r[mapping["sources"]].strip()
        sources = [s.strip() for s in sources_raw.split(";") if s.strip()]
        ts_raw = r[mapping["timestamp"]].strip()
        try:
            ts = parse_timestamp(ts_raw)
        except Exception:
            # If timestamp parsing fails, use epoch 0 to sort it early
            ts = datetime.fromtimestamp(0)
        parsed.append(Row(topic=topic, body=body, sources=sources, timestamp=ts))
    return parsed


def title_case_topic(t: str) -> str:
    return t.strip().title()


def render_markdown(rows: List[Row]) -> str:
    # Group by normalized topic (case-insensitive), preserve original casing for display by title-casing
    groups: Dict[str, List[Row]] = defaultdict(list)
    for r in rows:
        key = r.topic.strip().lower()
        groups[key].append(r)

    # Sort topics alphabetically by title-cased display name
    topics = sorted(groups.keys(), key=lambda k: title_case_topic(k))

    out_lines: List[str] = []
    out_lines.append("# Table of Contents")
    for k in topics:
        display = title_case_topic(k)
        anchor = display.lower().replace(" ", "-")
        out_lines.append(f"- [{display}](#{anchor})")
    out_lines.append("")

    for k in topics:
        display = title_case_topic(k)
        out_lines.append(f"## {display}")
        # sort rows by timestamp oldest -> newest
        topic_rows = sorted(groups[k], key=lambda r: r.timestamp)
        # build per-topic source list and mapping
        source_list: List[str] = []
        # track per-paragraph superscript numbers
        para_supers: List[List[int]] = []
        for r in topic_rows:
            this_nums: List[int] = []
            for s in r.sources:
                source_list.append(s)
                this_nums.append(len(source_list))
            para_supers.append(this_nums)
        # render paragraphs
        for r, nums in zip(topic_rows, para_supers):
            sup = ""
            if nums:
                sup = f"<sup>{','.join(str(n) for n in nums)}</sup>"
            out_lines.append(f"- {r.body}{sup}")
        out_lines.append("")
        # render sources subsection
        out_lines.append(f"### {display} Sources")
        for i, s in enumerate(source_list, start=1):
            out_lines.append(f"{i}) {s}")
        out_lines.append("")

    return "\n".join(out_lines)


def generate(csv_url: str, out_path: str = "small_plates.md") -> None:
    csv_text = fetch_csv(csv_url)
    rows = parse_rows(csv_text)
    md = render_markdown(rows)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Public CSV export URL for the Google Sheet", default=os.getenv("CSV_URL"))
    parser.add_argument("--out", help="Output Markdown path", default="small_plates.md")
    args = parser.parse_args(argv)
    if not args.url:
        print("Error: --url or CSV_URL env var must be provided", file=sys.stderr)
        return 2
    generate(args.url, args.out)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
