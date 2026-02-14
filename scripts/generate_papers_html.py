#!/usr/bin/env python3
"""
Generate the publications list in papers.html from structured JSON data.

Usage (from repo root):
    python scripts/generate_papers_html.py \
        --data data/papers.json \
        --html papers.html
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Union


MARKER_START = "<!-- BEGIN GENERATED PAPERS LIST -->"
MARKER_END = "<!-- END GENERATED PAPERS LIST -->"
HTML_INDENT = "        "


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render publications into papers.html")
    parser.add_argument("--data", default="data/papers.json", help="Path to the papers JSON file")
    parser.add_argument("--html", default="papers.html", help="Path to the HTML file to update")
    return parser.parse_args()


def format_author(author_entry: Union[Dict[str, Any], str]) -> str:
    if isinstance(author_entry, str):
        name = author_entry
        highlight = False
    else:
        name = author_entry.get("name", "")
        highlight = author_entry.get("highlight", False)
    if not name:
        return ""
    return f"<u>{name}</u>" if highlight else name


def build_publications_html(papers: List[Dict[str, Any]]) -> str:
    lines: List[str] = ['<ul class="publications">']
    for paper in papers:
        lines.append("    <li>")
        lines.append(f'        <strong>{paper["title"]}</strong> ({paper["year"]})<br>')

        publication = paper.get("publication")
        if publication and publication.get("name"):
            pub_line = f'        <em>{publication["name"]}</em>'
            note = publication.get("note")
            if note:
                pub_line += f" ({note})"
            lines.append(pub_line)
            lines.append("        <br>")

        authors = paper.get("authors", [])
        if authors:
            author_line = ", ".join(filter(None, (format_author(author) for author in authors)))
            if author_line:
                lines.append(f"        {author_line}<br>")

        links = paper.get("links", [])
        if links:
            link_line = " | ".join(f'<a href="{link["url"]}">{link["label"]}</a>' for link in links)
            lines.append(f"        {link_line}")

        lines.append("    </li>")
        lines.append("")

    if lines[-1] == "":
        lines.pop()
    lines.append("</ul>")

    indented_lines: List[str] = [
        f"{HTML_INDENT}{line}" if line else "" for line in lines
    ]
    return "\n".join(indented_lines)


def replace_section(html_text: str, new_section: str) -> str:
    try:
        start_idx = html_text.index(MARKER_START)
        end_idx = html_text.index(MARKER_END)
    except ValueError as exc:
        raise RuntimeError(
            "Could not find generation markers in papers.html. "
            "Ensure the file contains BEGIN/END markers."
        ) from exc

    before = html_text[: start_idx + len(MARKER_START)]
    after = html_text[end_idx:]
    return f"{before}\n{new_section}\n{after}"


def main() -> None:
    args = parse_args()
    json_path = Path(args.data)
    html_path = Path(args.html)

    papers_data = json.loads(json_path.read_text())
    rendered = build_publications_html(papers_data.get("papers", []))

    html_text = html_path.read_text()
    updated_html = replace_section(html_text, rendered)
    html_path.write_text(updated_html)


if __name__ == "__main__":
    main()
