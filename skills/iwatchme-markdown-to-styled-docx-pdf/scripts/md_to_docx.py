#!/usr/bin/env python3
"""
md_to_docx.py — Markdown / Obsidian Markdown → styled .docx (+ optional .pdf)

Usage:
    python3 md_to_docx.py input.md output.docx [--obsidian] [--docx-only]
"""

import argparse
from pathlib import Path
import re
import shutil
import subprocess


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


def convert_docx_to_pdf(output_docx):
    bundled_soffice = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    soffice = str(bundled_soffice) if bundled_soffice.exists() else shutil.which("soffice")
    if not soffice:
        raise RuntimeError(
            "未检测到 LibreOffice/soffice，请先安装 LibreOffice，或改用 --docx-only 仅生成 docx。"
        )

    docx_path = Path(output_docx).expanduser().resolve()
    outdir = docx_path.parent
    profile_dir = Path("/tmp/codex-libreoffice-profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            soffice,
            f"-env:UserInstallation={profile_dir.as_uri()}",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(outdir),
            str(docx_path),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    pdf_path = docx_path.with_suffix(".pdf")
    if not pdf_path.exists():
        raise RuntimeError(f"Expected PDF was not created: {pdf_path}")

    return pdf_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_md", help="Path to input Markdown file")
    parser.add_argument("output_docx", help="Path to output .docx file")
    parser.add_argument(
        "--obsidian",
        action="store_true",
        help="Preprocess Obsidian-specific syntax before DOCX rendering",
    )
    parser.add_argument(
        "--docx-only",
        action="store_true",
        help="Skip PDF conversion after DOCX rendering",
    )
    args = parser.parse_args()

    with open(args.input_md, "r", encoding="utf-8") as handle:
        content = handle.read()

    if args.obsidian:
        content = preprocess_obsidian(content)

    from build_styled_docx import build_docx

    build_docx(content, args.output_docx)
    if not args.docx_only:
        pdf_path = convert_docx_to_pdf(args.output_docx)
        print(f"[OK] 已生成: {pdf_path}")


if __name__ == "__main__":
    main()
