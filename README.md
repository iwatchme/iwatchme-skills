# iwatchme-skills

Agent Skills repository containing reusable skills for document export and Obsidian blog publishing.

This repository follows an Agent Skills-style layout so the same repo can be used by multiple agent clients, including Claude-compatible plugin flows and Codex-style `SKILL.md` discovery.

## Layout

```text
.claude-plugin/
skills/
  iwatchme-markdown-to-styled-docx/
    SKILL.md
    scripts/
    examples/
  iwatchme-obsidian-blog-publisher/
    SKILL.md
    scripts/
  iwatchme-technical-writing/
    SKILL.md
  iwatchme-deep-research/
    SKILL.md
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
--repo iwatchme/iwatchme-skills --path skills/iwatchme-markdown-to-styled-docx
```

## Skills

- `iwatchme-markdown-to-styled-docx`: Convert Markdown or Obsidian Markdown into styled DOCX while preserving the current resume-oriented output style.
- `iwatchme-obsidian-blog-publisher`: Prepare a Markdown article for an Obsidian-hosted blog by generating fixed frontmatter, linting code/mermaid blocks, and writing the note into the vault via Obsidian CLI.
- `iwatchme-technical-writing`: Technical article writing standards with anti-AI-style quality checks, four-layer review system, and polish mode. Can be used standalone or as a dependency of deep-research.
- `iwatchme-deep-research`: Three-phase deep research workflow (local scan → explore & dump → offline writing + quality review). Depends on `iwatchme-technical-writing` for writing standards and quality checks.
