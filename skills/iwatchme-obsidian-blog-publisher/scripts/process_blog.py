#!/usr/bin/env python3
"""Process a markdown article for Obsidian Blog publishing.

Given a source markdown file, a set of frontmatter values, and an output
path, this script:

  1. Strips any existing YAML frontmatter block from the source.
  2. Writes a new frontmatter block with the provided values plus
     ``draft: false`` and ``publish: true``.
  3. Runs light sanity checks on the body (code-block language tags,
     mermaid-block quoting) and emits warnings on stderr.
  4. Writes the combined result to the output path.

Field rules (validated — violations cause a non-zero exit):

  * title       : 1–20 characters (CJK counts as 1 each, same as Python's len).
  * description : 50–300 characters, warn outside 100–200 per the user's spec.
  * pub_date    : YYYY-MM-DD.
  * tags        : 1–3 items, each 1–2 words, lowercase, hyphen-allowed.
  * slug        : kebab-case ASCII, at least two hyphen-separated tokens.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date as date_type
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.DOTALL)
FENCE_OPEN_RE = re.compile(r"^(```+)(\s*)(\S*)?\s*$")
SMART_QUOTES = ("\u201c", "\u201d", "\u2018", "\u2019")


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block if present."""
    if text.startswith("---"):
        match = FRONTMATTER_RE.match(text)
        if match:
            return text[match.end():]
    return text


def validate_title(title: str) -> None:
    if not title.strip():
        raise ValueError("title must not be empty")
    if len(title) > 20:
        raise ValueError(
            f"title must be 20 characters or fewer, got {len(title)}: {title!r}"
        )


def validate_description(description: str) -> None:
    size = len(description)
    if size < 50:
        raise ValueError(f"description is too short ({size} chars); aim for 100-200")
    if size > 300:
        raise ValueError(f"description is too long ({size} chars); aim for 100-200")
    if not (100 <= size <= 200):
        print(
            f"warning: description is {size} chars; the spec asks for 100-200",
            file=sys.stderr,
        )


def validate_pub_date(pub_date: str) -> None:
    try:
        date_type.fromisoformat(pub_date)
    except ValueError as exc:
        raise ValueError(f"pub_date must be YYYY-MM-DD, got {pub_date!r}") from exc


def validate_tags(tags: list[str]) -> None:
    if not 1 <= len(tags) <= 3:
        raise ValueError(f"tags must have 1-3 items, got {len(tags)}: {tags}")
    for tag in tags:
        if not tag:
            raise ValueError("tags must not contain empty strings")
        if len(tag.split("-")) > 2:
            raise ValueError(
                f"each tag should be 1-2 words (hyphen-separated), got {tag!r}"
            )
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", tag):
            raise ValueError(
                f"tags must be lowercase ASCII with optional hyphens, got {tag!r}"
            )


def validate_slug(slug: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", slug):
        raise ValueError(
            "slug must be kebab-case with at least two tokens "
            f"(e.g. kotlin-coroutine-deep-dive), got {slug!r}"
        )


def quote_yaml_string(value: str) -> str:
    """Quote a string for YAML only when needed."""
    if not value:
        return '""'
    risky_chars = set('":#{}[]|>&*!%@`')
    needs_quoting = (
        value != value.strip()
        or any(c in value for c in risky_chars)
        or value.startswith(("-", "?", ","))
        or ": " in value
    )
    if not needs_quoting:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_frontmatter(
    title: str,
    description: str,
    pub_date: str,
    tags: list[str],
    slug: str,
) -> str:
    lines = ["---"]
    lines.append(f"title: {quote_yaml_string(title)}")
    lines.append(f"description: {quote_yaml_string(description)}")
    lines.append(f"pubDate: {pub_date}")
    lines.append("tags:")
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.append("draft: false")
    lines.append("publish: true")
    lines.append(f"slug: {slug}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def lint_body(body: str) -> list[str]:
    warnings: list[str] = []
    lines = body.splitlines()

    in_fence = False
    fence_marker: str | None = None
    fence_lang: str | None = None
    fence_start_line = -1
    mermaid_buffer: list[str] = []

    for line_number, line in enumerate(lines, start=1):
        match = FENCE_OPEN_RE.match(line)
        if match and (not in_fence or line.startswith(fence_marker or "")):
            marker = match.group(1)
            lang = (match.group(3) or "").strip()
            if not in_fence:
                in_fence = True
                fence_marker = marker
                fence_lang = lang or None
                fence_start_line = line_number
                mermaid_buffer = []
                if not lang:
                    warnings.append(
                        f"line {line_number}: code fence has no language tag; "
                        "add one (e.g. ```python) so syntax highlighting works"
                    )
            elif marker.startswith(fence_marker):
                if fence_lang == "mermaid":
                    _lint_mermaid(mermaid_buffer, fence_start_line, warnings)
                in_fence = False
                fence_marker = None
                fence_lang = None
                mermaid_buffer = []
            continue
        if in_fence and fence_lang == "mermaid":
            mermaid_buffer.append(line)

    if in_fence:
        warnings.append(
            f"line {fence_start_line}: code fence opened but never closed; "
            "the rest of the file is being swallowed as code"
        )

    return warnings


def _lint_mermaid(buffer: list[str], start_line: int, warnings: list[str]) -> None:
    joined = "\n".join(buffer)
    if any(quote in joined for quote in SMART_QUOTES):
        warnings.append(
            f"line {start_line}: mermaid block contains smart quotes "
            '(“ ” ‘ ’); replace with straight quotes (") or mermaid will fail to parse'
        )

    stripped = [line.strip() for line in buffer if line.strip()]
    if not stripped:
        warnings.append(f"line {start_line}: mermaid block appears to be empty")
        return

    first = stripped[0]
    diagram_types = (
        "graph ",
        "flowchart ",
        "sequenceDiagram",
        "stateDiagram",
        "classDiagram",
        "erDiagram",
        "gantt",
        "pie",
        "journey",
        "gitGraph",
        "mindmap",
        "timeline",
    )
    if not any(first.startswith(diagram_type) for diagram_type in diagram_types):
        warnings.append(
            f"line {start_line}: mermaid block does not start with a diagram "
            f"type declaration (got {first!r}); mermaid may fail to render"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, help="Path to source markdown file")
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the processed markdown file (creates parent dirs)",
    )
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument(
        "--pub-date",
        required=True,
        help="Publication date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--tags",
        required=True,
        help="Comma-separated tag list, e.g. kotlin,coroutine",
    )
    parser.add_argument("--slug", required=True)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat lint warnings as errors (non-zero exit).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    try:
        validate_title(args.title)
        validate_description(args.description)
        validate_pub_date(args.pub_date)
        validate_tags(tags)
        validate_slug(args.slug)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"error: input file does not exist: {input_path}", file=sys.stderr)
        return 2

    text = input_path.read_text(encoding="utf-8")
    body = strip_frontmatter(text).lstrip("\n")
    warnings = lint_body(body)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    frontmatter = render_frontmatter(
        title=args.title,
        description=args.description,
        pub_date=args.pub_date,
        tags=tags,
        slug=args.slug,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(frontmatter + body, encoding="utf-8")

    print(f"wrote {output_path} ({len(warnings)} warning(s))")
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
