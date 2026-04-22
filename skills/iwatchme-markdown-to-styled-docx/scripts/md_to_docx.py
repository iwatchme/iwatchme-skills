#!/usr/bin/env python3
"""
md_to_docx.py — Markdown / Obsidian Markdown → styled .docx

Usage:
    python3 md_to_docx.py input.md output.docx [--obsidian]
"""

import argparse
import re


def preprocess_obsidian(text):
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"!\[\[([^\]]+)\]\]", r"![\1](\1)", text)
    text = re.sub(r"%%.*?%%", "", text, flags=re.DOTALL)
    text = re.sub(
        r"(?<!\w)#[a-zA-Z\u4e00-\u9fff][a-zA-Z0-9\u4e00-\u9fff_/-]*",
        "",
        text,
    )
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_md", help="Path to input Markdown file")
    parser.add_argument("output_docx", help="Path to output .docx file")
    parser.add_argument(
        "--obsidian",
        action="store_true",
        help="Preprocess Obsidian-specific syntax before DOCX rendering",
    )
    args = parser.parse_args()

    with open(args.input_md, "r", encoding="utf-8") as handle:
        content = handle.read()

    if args.obsidian:
        content = preprocess_obsidian(content)

    from build_styled_docx import build_docx

    build_docx(content, args.output_docx)


if __name__ == "__main__":
    main()
