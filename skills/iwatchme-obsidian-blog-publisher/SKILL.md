---
name: iwatchme-obsidian-blog-publisher
description: Use when preparing a Markdown article for an Obsidian-hosted blog: generate fixed YAML frontmatter, sanity-check code fences and mermaid blocks, and write the finished note into an Obsidian Blog folder via the Obsidian CLI.
---

# Obsidian Blog Publisher

把原始 Markdown 文章整理成可发布的博客文章，并通过 Obsidian CLI 写入当前 vault 的 `Blog/` 目录。

## 适用场景

- 用户要求“发布博客”
- 用户要求“给这篇文章生成 frontmatter”
- 用户要求“准备发布这篇 Markdown”
- 用户要求“写入 Obsidian Blog”
- 用户提供 `.md` 文件路径，并希望把它变成博客文章

## 不做的事

- 不直接复制到 iCloud / Obsidian 文件系统路径
- 不推送到 GitHub、静态站或其他博客平台
- 不把 frontmatter 字段做成可配置模板

## 输入要求

开始前先拿到文章的完整内容：

- 如果用户给了 Markdown 文件路径，先完整读取文件
- 如果用户直接贴了文章内容，就基于正文处理

不要只根据文件名生成标题、描述或 slug。

## 固定 frontmatter

目标 frontmatter 结构固定为：

```yaml
---
title: ""
description: ""
pubDate: ""
tags: []
draft: false
publish: true
slug: ""
---
```

字段约束：

- `title`：通常使用文章正文语言；内容偏中文时默认生成中文标题；20 个字符以内
- `description`：中文摘要；100-200 字最佳，脚本接受 50-300 字
- `pubDate`：必须用系统当天日期，格式 `YYYY-MM-DD`
- `tags`：1-3 个英文 tag，全部小写，1-2 个词
- `draft`：固定为 `false`
- `publish`：固定为 `true`
- `slug`：英文 kebab-case，建议 3-6 个词

如果源文件已经有 frontmatter，直接整体替换，不做合并。

## Markdown 检查

在写入 Obsidian 前，先检查正文：

- 所有 fenced code block 都应带语言标记，例如 ` ```ts `、` ```bash `
- 没有语言标记的代码块需要人工补齐；纯文本或 ASCII 图可用 ` ```text `
- 每个代码块都必须闭合
- Mermaid 代码块必须以图类型开头，例如 `graph TD`、`flowchart LR`、`sequenceDiagram`
- Mermaid 中的智能引号要改成直引号

`scripts/process_blog.py` 负责做确定性的 frontmatter 重写和 lint 提示，但不会自动修正文中歧义内容。

## 使用 `uv`

优先使用 skill 自带的 `uv` 环境。脚本目录约定和 `iwatchme-markdown-to-styled-docx-pdf` 一致：

```bash
cd <skill-install-dir>
scripts/bootstrap_uv.sh
```

其中 `<skill-install-dir>` 指包含 `SKILL.md` 和 `scripts/` 的目录。

## 使用脚本

标准调用：

```bash
scripts/process_blog.sh \
  --input <source.md> \
  --output /tmp/processed.md \
  --title "中文标题" \
  --description "中文描述……" \
  --pub-date "$(date +%Y-%m-%d)" \
  --tags kotlin,coroutine \
  --slug kotlin-coroutine-deep-dive
```

如果只想直接调用 Python，也应通过 `uv`：

```bash
UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
uv run --python .venv/bin/python python scripts/process_blog.py \
  --input <source.md> \
  --output /tmp/processed.md \
  --title "中文标题" \
  --description "中文描述……" \
  --pub-date "$(date +%Y-%m-%d)" \
  --tags kotlin,coroutine \
  --slug kotlin-coroutine-deep-dive
```

脚本行为：

1. 删除输入文件顶部已有的 frontmatter
2. 写入新的固定 frontmatter
3. 对无语言标记的代码块和 Mermaid 常见问题输出 warning
4. 将结果写到 `--output`

如果需要把 lint warning 视为失败，可附加 `--strict`。

## 写入 Obsidian

前提：

- `obsidian` CLI 已安装且可调用
- Obsidian 应用正在运行
- 这类命令本质上会拉起或连接桌面版 Obsidian；如果当前执行环境有沙箱限制，必须在沙箱外执行

强约束：

- 不要在沙箱里执行 `obsidian create`、`obsidian append` 这类写入命令
- 在沙箱里它们可能表现为无输出、直接失败，或进程异常退出；这不代表内容有问题，优先怀疑执行环境
- 一旦要写入 vault，就直接申请沙箱外执行，不要反复在沙箱里重试

先验证 CLI：

```bash
obsidian help
obsidian version
obsidian vault info=path
```

注意：

- 用 `obsidian help` 查看帮助，不要用 `obsidian --help`
- Homebrew 安装的 `obsidian` 通常只是桌面应用的 wrapper，不是独立后台服务
- 如果 `obsidian help` 正常，但 REST/API 端口连不上，不影响 CLI 写入；两者是不同通道
- 如果 Obsidian MCP / REST 端口连不上，例如 `ECONNREFUSED 127.0.0.1:27124`，不要把它当成 CLI 不可用；改走 `obsidian` CLI 即可

不要直接 `cp` 到 Obsidian/iCloud 路径。统一使用 Obsidian CLI 写入当前 vault 中的相对路径：

```bash
content=$(python3 -c "
import pathlib
text = pathlib.Path('/tmp/processed.md').read_text(encoding='utf-8')
print(text.replace('\\\\', '\\\\\\\\').replace('\"', '\\\\\"').replace('\n', '\\\\n'))
")

obsidian create path="Blog/文章标题.md" content="$content" silent overwrite
```

更稳的做法：

- 长文章不要依赖 shell 的多层引号和命令替换去传 `content=...`
- 优先用 `python3 -c` 调 `subprocess.run(["obsidian", ...])`
- `content` 参数传单个字符串，内容先做 `\n`、`\`、`"` 转义，再交给 CLI
- 如果直接把原始多行文本塞进参数，CLI 可能 `SIGABRT` 或者写入失败，这通常是参数传递问题，不是文章内容问题

推荐写法：

```bash
python3 -c '
from pathlib import Path
import subprocess

text = Path("/tmp/processed.md").read_text(encoding="utf-8")
content = text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n")

subprocess.run(
    [
        "obsidian",
        "create",
        "path=Blog/文章标题.md",
        f"content={content}",
        "silent",
        "overwrite",
    ],
    check=True,
)
'
```

约定：

- 目标路径始终是相对 vault 根目录的 `Blog/<title>.md`
- 文件名使用 frontmatter 中的 `title`
- `overwrite` 允许重复运行
- 如果 CLI 不可用或 Obsidian 未运行，要明确告诉用户，不要假装已发布

## 常见错误

- 标题过长
- `slug` 不是英文 kebab-case
- tag 超过 3 个或包含大写
- 用记忆里的日期而不是系统日期
- 直接尝试把文件写进 iCloud 路径
- 在沙箱里执行 Obsidian CLI 写入命令
- 用 shell 拼接超长多行 `content=` 参数，导致转义错乱或 `SIGABRT`
