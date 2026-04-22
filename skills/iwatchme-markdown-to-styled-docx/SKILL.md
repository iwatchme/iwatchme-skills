---
name: iwatchme-markdown-to-styled-docx
description: Use when converting Markdown or Obsidian Markdown into styled DOCX files, especially for resume-style export that should preserve the current header, section, and bullet formatting.
---

# Markdown to Styled DOCX

这个技能用于把本地 Markdown 内容导出成固定样式的 `.docx`。

## 输入要求

必须使用 YAML frontmatter：

```markdown
---
name: 张三
email: zhangsan@example.com
phone: +86 13800000000
city: 上海
target: 产品经理
---
```

正文规则：

```markdown
## 工作经历

- 资深开发工程师 | 哔哩哔哩 | 2021.04–至今
  剪辑业务 / 播放业务
  - 核心项目：B站跨端模板引擎从0到1构建
    - 主导跨端模板引擎从 0 到 1 建设，设计基于 Protobuf 的统一模板协议。
    - 建设端侧适配层与兼容机制，支撑模板能力规模化生产。
  - 主导播放页分层作用域架构设计与落地，建立多级 Scope 体系。
```

- `- left | right` 或 `- left | middle | right`
- 如果条目后面没有缩进内容，渲染成紧凑列表项
- 如果条目后面有副标题或子项，渲染成结构化表头
- 一级子项写成 `- 标签：内容`
- 二级子项继续缩进写 `- 详情`

## Obsidian 预处理

如果输入来自 Obsidian，先运行 `scripts/md_to_docx.py --obsidian`。该模式会先清理：

- `[[笔记名]]` → `笔记名`
- `[[笔记名|显示文字]]` → `显示文字`
- `![[图片.png]]` → `![图片.png](图片.png)`
- `%%注释%%` → 删除
- `#tag` → 删除

## 环境

这个 skill 使用 `uv` 管理依赖，并在 skill 目录下维护 `.venv`。

```bash
cd <skill-install-dir>
scripts/bootstrap_uv.sh
```

## 转换

```bash
scripts/render_docx.sh input.md output.docx
```

```bash
scripts/render_docx.sh input.md output.docx --obsidian
```

也可以直接运行核心脚本：

```bash
uv run --python .venv/bin/python scripts/md_to_docx.py input.md output.docx --obsidian
```

## 边界

- 只生成 `.docx`
- 不负责 `.pdf` 转换
- 不处理上传、下载、云端文档
