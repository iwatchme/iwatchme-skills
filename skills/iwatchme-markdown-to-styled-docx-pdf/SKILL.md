---
name: iwatchme-markdown-to-styled-docx-pdf
description: Use when converting Markdown or Obsidian Markdown into styled DOCX and PDF files, especially for resume-style export that should preserve the current header, section, and bullet formatting.
---

# Markdown to Styled DOCX/PDF

这个技能用于把本地 Markdown 内容导出成固定样式的 `.docx`，并默认继续生成同名 `.pdf`，保留当前简历模板的排版行为。

## 适用场景

- 用户要求“把这个 Markdown 转成 docx”
- 用户要求“把这个 Markdown 转成 pdf”
- 用户要求“把这个 Markdown 转成 docx 和 pdf”
- 用户要求“把 Obsidian 笔记导出为 Word”
- 用户要求“把 Obsidian 笔记导出为 PDF”
- 用户要求“把简历导出成 Word/PDF”
- 用户要求“保持当前简历模板样式生成 .docx/.pdf”
- 用户要求“先生成 docx，再转 pdf”

## 不做的事

- 不处理 Google Drive / Google Docs 下载
- 不上传文件
- 不输出 base64
- 不使用 pandoc 生成最终文档

## 输入格式

优先支持 YAML frontmatter：

```markdown
---
name: 张三
email: zhangsan@example.com
phone: +86 13800000000
city: 上海
target: 产品经理
---
```

也兼容旧格式：

```markdown
# 张三
📧 zhangsan@example.com | 📱 +86 13800000000 | 意向城市：上海
```

工作经历推荐使用纯嵌套列表：

```markdown
## 工作经历

- 资深开发工程师 | 哔哩哔哩 | 2021.04–至今
  剪辑业务 / 播放业务
  - 核心项目：B站跨端模板引擎从0到1构建
    - 主导跨端模板引擎从 0 到 1 建设，设计基于 Protobuf 的统一模板协议。
    - 建设端侧适配层与兼容机制，支撑模板能力规模化生产。
  - 主导播放页分层作用域架构设计与落地，建立多级 Scope 体系。
```

## Obsidian 预处理

如果输入来自 Obsidian，先运行 `scripts/md_to_docx.py --obsidian`。该模式会先清理：

- `[[笔记名]]` → `笔记名`
- `[[笔记名|显示文字]]` → `显示文字`
- `![[图片.png]]` → `![图片.png](图片.png)`
- `%%注释%%` → 删除
- `#tag` → 删除

## 转换流程

推荐用 skill 自带的 `uv` 启动脚本。脚本已经固化了清华镜像：

```bash
cd <skill-install-dir>
scripts/bootstrap_uv.sh
```

其中 `<skill-install-dir>` 指这个 skill 的安装目录，也就是包含 `SKILL.md` 和 `scripts/` 的目录。
如果不想先 `cd`，也可以直接调用脚本的完整路径；脚本会根据自身位置自动定位 skill 根目录。

标准 Markdown：

```bash
scripts/render_docx.sh input.md output.docx
```

默认会同时生成与 `output.docx` 同目录、同文件名的 `output.pdf`。

Obsidian Markdown：

```bash
scripts/render_docx.sh input.md output.docx --obsidian
```

如果只想生成 `.docx`，可显式跳过 PDF：

```bash
scripts/render_docx.sh input.md output.docx --docx-only
```

也可以直接调用核心渲染器：

```bash
UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
uv run --python .venv/bin/python python scripts/build_styled_docx.py input.md output.docx
```

## 环境约定

- 默认使用项目目录下的 `.venv`
- 默认使用 `UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`
- 初始化环境时显式安装 `python-docx` 和 `lxml`
- 不依赖 `uv sync` 去安装当前项目包本身
- 若需要导出 PDF，本机需已安装 `LibreOffice`，并且 `soffice` 可在 `PATH` 中调用

## 已验证命令

以下命令已经在本机跑通过：

```bash
cd <skill-install-dir>
scripts/bootstrap_uv.sh
scripts/render_docx.sh \
  '<input.md>' \
  '<output.docx>'
```

## 样式规则

- `# 姓名` 或 frontmatter 中的 `name`：头部姓名
- 联系信息行：头部邮箱 / 电话 / 意向城市
- `## 章节名`：蓝色标题和底部横线
- `- title | company | date`：职位 / 公司 / 日期行
- 职位项下首个缩进行：灰色副标题
- 职位项下 `- 核心项目：xxx` 或 `- 基础项目：xxx`：一级项目符号
- 核心项目项下继续缩进的 `- 详情`：二级空心圆点
- 职位项下普通 `- 职责描述`：一级普通列表

## 工作经历约束

- 工作经历职位行必须使用 `title | company | date`
- 工作经历只支持 3 层列表：职位、项目/职责、项目详情
- 三级详情只能挂在 `核心项目：` 或 `基础项目：` 下面
- 为避免打断现有笔记，脚本暂时仍能读取旧的职位写法，但新文档应统一使用列表驱动语法

## 实施要求

- 要保持 `build_styled_docx.py` 的输出样式与现有 skill 一致
- 默认先生成 `.docx`，再调用 `LibreOffice` 的 `soffice --headless` 生成同名 `.pdf`
- 若用户只要求导出 `.docx`，可使用 `--docx-only`
- 该 skill 的触发应同时覆盖 `.docx` 导出、`.pdf` 导出、以及 `.docx -> .pdf` 的连续导出需求
