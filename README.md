# markdown-to-styled-docx-pdf

Agent Skills repository for converting Markdown or Obsidian Markdown into styled DOCX and PDF files.

This repository follows an Agent Skills-style layout so the same repo can be used by multiple agent clients, including Claude-compatible plugin flows and Codex-style `SKILL.md` discovery.

## Layout

```text
.claude-plugin/
skills/
  markdown-to-styled-docx-pdf/
    SKILL.md
    scripts/
    examples/
```

## Install

### Agent Skills clients

Add or clone this repository using your client's standard Agent Skills flow.

Example:

```bash
npx skills add git@github.com:iwatchme/iwatchme-skills.git
```

### Claude-compatible plugin flows

Use the repository root as the plugin root so `.claude-plugin/` and `skills/` are both available.

### Codex CLI

Copy the `skills/` directory into your Codex skills path, or install from a GitHub repo/path if your setup supports it.

Example repo/path:

```bash
--repo iwatchme/iwatchme-skills --path skills/markdown-to-styled-docx-pdf
```

## Skill

- `markdown-to-styled-docx-pdf`: Convert Markdown or Obsidian Markdown into styled DOCX and PDF while preserving the current resume-oriented output style.
