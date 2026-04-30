---
name: iwatchme-deep-research
description: Deep Research Skill - 三阶段调研法（本地扫描 → 探索落盘 → 利用写作）。Phase 0 扫描本地 Obsidian Vault 优质资料，Phase 1 全力搜索并落盘，Phase 2 断网只读本地文件写报告 + 四层质检（technical-writing 标准）。触发词：「深度调研 XXX」/ 「deep research XXX」/ 「dr XXX」。
---

# Deep Research Skill

> **核心理念**：三阶段解耦 —— 本地扫描（已有知识激活）→ 探索落盘（互联网 → 本地文件）→ 利用写作（断网读本地文件）。
>
> **质检标准**：Phase 2 报告必须通过 technical-writing 四层质检，否则触发 rewrite。
>
> **依赖 skill**：`iwatchme-technical-writing`（技术写作规范，四层质检 + 文风禁区）

---

## 配置

```yaml
# ===== 用户路径配置（按自己的环境修改这三个变量即可） =====
local_vault_path: /Users/iwatchme/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes
workspace_path: /Users/iwatchme/Documents/iwatchme-skills
technical_writing_skill: /Users/iwatchme/Documents/iwatchme-skills/skills/iwatchme-technical-writing/SKILL.md
research_output_dir: {local_vault_path}/调研/
```

**Portability**：路径不存在时 Phase 0 静默跳过，不阻断全流程。其他用户改 `local_vault_path` + `workspace_path` + `research_output_dir` 三个变量即可。

---

## 术语

| 术语 | 含义 |
|------|------|
| **Phase 0 scan** | 扫描本地 Vault 相关文件，生成覆盖度评估 |
| **research dump** | 研究员对每个子问题的原始发现，写入本地 .md 文件 |
| **local context** | Phase 0 产出的本地知识摘要 |
| **master research** | dump + local context 汇总后的单一文件 |
| **四层质检** | L1 禁用词/硬伤 → L2 可读性 → L3 内容深度 → L4 活人感（technical-writing 标准） |

---

## 三阶段总览

```
用户输入 (题目)
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 0: 本地扫描 —— 激活已有知识资产                      │
│  目标: 在规划子问题之前，先摸清本地有什么                    │
│  策略: 扫描结果影响子问题范围（已有高覆盖 → 缩小搜索范围）    │
├──────────────────────────────────────────────────────────┤
│  PHASE 1: 探索 —— 调研 + 落盘                             │
│  目标: 把互联网的零散知识全部沉淀成本地文件                   │
│  原则: 全力搜索，不漏信号，断网前完成所有网络访问             │
├──────────────────────────────────────────────────────────┤
│  PHASE 2: 利用 —— 读文件 + 写作 + 四层质检                  │
│  目标: 基于本地干净文件进行高频迭代写作                       │
│  原则: 断网，只读本地文件                                   │
│  质检: technical-writing 四层标准，不通过则 rewrite          │
└──────────────────────────────────────────────────────────┘
```

---

## Phase 0: 本地文件扫描

**执行时机**：整个流程第一步，在规划任何子问题之前执行。

### 执行步骤

**Step 0a: 扫描目录**

对以下目录（存在才扫）执行 ripgrep 关键词扫描：

```
{local_vault_path}/Blog/
{local_vault_path}/Clippings/
{local_vault_path}/Notes/
{local_vault_path}/调研/
{local_vault_path}/StartUp/
{workspace_path}/MEMORY.md
{workspace_path}/memory/
```

关键词从 topic 提取 3-5 个核心概念。

```bash
rg -l --max-count 10 --type md "keyword1|keyword2|keyword3" "{dir}/" 2>/dev/null
```

**Step 0b: 读取高匹配文件**

对每个找到的文件，提取相关段落（最多 5 个最有价值的文件，每文件限制 100 行）：

```bash
rg -C 3 "{keyword}" "{file}" 2>/dev/null | head -100
```

**Step 0c: 写入 local context**

路径：`{research_output_dir}/{YYYY-MM-DD}-{slug}-研究材料/00-local-context.md`

格式：

```markdown
---
phase: 0
topic: {topic}
---

# Phase 0 - 本地知识扫描结果

## 扫描目录
- Blog/: 扫描了 X 个文件，命中 {N}
- Clippings/: 命中 {N}
- Notes/: 命中 {N}
- 调研/: （目录不存在，静默跳过）
...

## 命中文件

### {文件名1}
- **路径**: {path}
- **相关段落**: `{rg 输出片段，限制 80 行}`
- **对本题的价值**: 高/中/低

...

## 覆盖度评估

| 子维度 | 本地覆盖度 | 本地来源 |
|--------|-----------|---------|
| {维度1} | 高/中/低 | {文件列表} |
| {维度2} | 高/中/低 | {文件列表} |

## 子问题范围调整

- **{子问题A}**：本地高覆盖 → 缩小搜索范围，补充最新动态
- **{子问题B}**：本地无覆盖 → 正文搜索
```

---

## Phase 1a: 规划子问题 + 创建目录

1. 读取 Phase 0 输出的 `00-local-context.md`
2. 结合 topic 拆解 2-4 个子问题，Phase 0 高覆盖的明确标注缩小范围
3. 创建目录：

```bash
DATE=$(date +%Y-%m-%d)
TOPIC_SLUG=$(echo "{topic}" | sed 's/[^a-zA-Z0-9\u4e00-\u9fa5]/-/g')
OUT_DIR="{research_output_dir}/${DATE}-${TOPIC_SLUG}-研究材料"
mkdir -p "${OUT_DIR}/references"
```

4. 回执用户：`收到，开始处理。本地扫描命中 X 个文件。Phase 0 发现 {A} 子问题本地高覆盖，聚焦缺失部分。`

---

## Phase 1b: 并行研究员写 research dump

**关键约束：研究员的全部网络访问（web_search + web_fetch）必须在写 dump 文件之前完成，不在写作阶段访问网络。**

### 子问题规划（主 session）

根据 topic 和 Phase 0 结果，拆解 2-4 个子问题，每个附搜索策略：

| 子问题 | 搜索关键词 | 偏好来源 |
|--------|-----------|---------|
| {子问题A} | keyword1, keyword2 | 官方文档 / 源码仓库 |
| {子问题B} | keyword3, keyword4 | GitHub / 学术论文 |
| ... | ... | ... |

### Spawn 配置

每个子问题一个 researcher，同时 spawn，然后 `sessions_yield`：

```
runtime: subagent
mode: run
timeoutSeconds: 600
```

### Researcher Prompt（完整模板）

```
你是一个专业研究员。请针对以下子问题进行深度调研，并把发现写入本地文件。

## 研究问题
{sub_question}

## 搜索策略
{search_strategy}

## Phase 0 本地覆盖度标注
{从 00-local-context.md 提取该子问题的覆盖度行}
如果本地已有高覆盖：补充最新动态即可，不需要重复基础搜索。
如果本地无覆盖：正文搜索，不设限制。

## 核心执行原则
1. **调研阶段全力搜索**：所有 web_search + web_fetch 在写文件之前完成
2. **写文件阶段断网**：开始写 dump 文件时，不再访问网络
3. **一手资料优先**：源码 > 官方文档 > 论文 > 官方 Issue > 二手博客

## 搜索要求
- web_search 3-5 个不同角度的查询
- 至少 1 次专门搜源码/官方文档
- 精选 3-5 个最有价值的页面，用 web_fetch 抓取全文
- 交叉验证信息来源

## 输出要求：写入本地文件

**必须用 exec + python 写入文件，不在 prompt 里输出长文本。**

文件路径：`{OUT_DIR}/{sub_num}-{slug}-dump-{N}.md`

文件格式：
```markdown
---
source: research
sub_question: {sub_question}
researcher: researcher-{N}
phase: 1b
---

# 子问题: {sub_question}

## 核心发现（3-5 条）
- **{发现标题}**: {一句话描述} [来源: {source}]

## 详细分析

### {分析小节1}
{2-4 段详细分析，含内联引用 [source-n]}

### {分析小节2}
{...}

## 信息源
1. [{title}]({url}) — {一句话摘要} **[一手/二手]**
2. ...

## 质量自评
- 信息充分度: X/5
- 源可信度: X/5
- 一手资料占比: X/5
- 本地知识匹配度: 高/中/低
- 是否需要补充调研: 是/否（如是，说明缺什么）
```
```

## Phase 1c: 参考资料归档

研究员完成后，主 session 对所有 cite 的 URL 执行 web_fetch（未抓取过的），保存到：

```
{OUT_DIR}/references/{num}-{slug}.md
```

格式：
```markdown
---
source: {url}
title: {title}
fetched: {ISO timestamp}
research_topic: {topic}
sub_question: {sub_question}
---

{full content}
```

## Phase 1d: 缺口检查 + 编译 master-research

1. 读取所有 dump 文件，评估 `是否需要补充调研`
2. 如有缺口：主 session 直接补搜，不派新 researcher
3. 编译 master-research：

```bash
cat "{OUT_DIR}/00-local-context.md" \
    "{OUT_DIR}"/*-dump-*.md \
    > "{OUT_DIR}/master-research.md"
```

---

## Phase 2: 写作（断网模式）

**绝对约束：此阶段 agent 不得使用 web_search/web_fetch，只读本地文件。**

### Phase 2a: 验证

检查 `{OUT_DIR}/master-research.md` 存在且非空。不存在则报错，不继续写作。

### Phase 2b: 写作 Agent

Prompt：
```
你是一个资深技术分析师。请根据本地研究材料撰写深度调研报告。

## 报告主题
{topic}

## 断网约束（最高优先级）
本次写作阶段你不得使用 web_search、web_fetch 或任何联网工具。
你只能读取以下本地文件：
- {OUT_DIR}/master-research.md（必读）
- {OUT_DIR}/00-local-context.md（必读）
- {OUT_DIR}/references/*.md（按需读）

## 文风规范（必须遵守）

写作必须遵守 `iwatchme-technical-writing` skill 的全部规范。
完整规范路径：{technical_writing_skill}

核心禁区速查（违反即不合格）：

**禁止词类**
1. 大厂黑话（赋能/闭环/底座/抓手/落地/对齐/沉淀/打通/链路…）
2. 汇报腔（综上所述/一言以蔽之/值得重点关注/不难看出/显然…）
3. 网络梗（YYDS/绝绝子/破防/拿捏/炸裂/封神…）
4. AI 清嗓词（说实话/实际上/值得注意的是/关键的是…）
5. AI 强调词（这一点很重要/毫无疑问/显而易见…）
6. AI 填充词（在当今社会/随着技术的不断发展/从根本上说…）
7. AI 元叙述（接下来我将/下面我们来看/让我们来探讨…）
8. AI 模糊词（具有深远意义/影响巨大/至关重要/不可或缺…）
9. 夸张比喻（核弹级提升/雪崩式炸裂/魔法般生效…）

**禁止句式**
10. 否定-纠正结构："不是 A，而是 B" → 直接说 B
11. 假想读者错误："很多人会以为" → 直接说正确事实
12. 比喻降格："你可以把 X 理解成 Y" → 直接技术陈述
13. 口水过渡词："其实"/"更准确地说" → 直接说
14. 虚假引导语："先别急着"/"先记住一点" → 直接进入描述
15. 物理动作动词：立住/扛住/打透/站稳 → 用中性动词
16. "不是 X，而是 Y" 族句式，全文限 2 次以内

**开头规则**
三句内必须完成：1）讲什么；2）为什么值得看；3）读者能带走什么。
禁止从"随着 AI 时代到来"、"在当今社会"开讲。

**活人感标准**
读完觉得是同行在认真分享，不是 AI 批量输出。
- 有真实工作流痕迹
- 判断明确且交代边界
- 技术表达敢写实
- 结尾克制，不升华，不上价值

## 本地资产激活记录（Phase 0）
{从 00-local-context.md 提取覆盖度矩阵}
报告应区分：哪些是本地已有知识，哪些是本次新研究发现。

## 写作要求

### 格式
1. 标题: `# 深度调研：{topic}`
2. 元信息: 调研时间、耗时
3. 摘要: 200-300 字，概括核心结论
4. 正文: 按逻辑组织（不是子问题堆砌），段落间有过渡
5. 参考资料: 编号列表，标注 [一手] / [二手] / [本地: {path}]

### 质量标准
- 禁止堆砌搜索结果，要有分析综合
- 禁止无引用的断言
- 禁止空洞结尾（不能用结论复述全文，不能上价值）
- 禁止仅以二手博客为论据
- 每个论点有 [n] 引用支撑
- 技术细节给出源码行号/文件路径
- 适当使用表格对比
- 判断明确，但必须交代依据和边界

### 语言
- 中文为主，技术术语保留英文
- 专业但不晦涩，有观点
- 字数: 4000-6000 字

## 输出
将报告写入：{research_output_dir}/{YYYY-MM-DD}-{slug}-深度调研.md
```

---

## Phase 2c: 四层质检（technical-writing 标准）

**执行时机**：报告草稿产出后、正式交付前。如质检不通过，触发 rewrite。

### 依赖 skill

`iwatchme-technical-writing` skill（文风禁区 + 四层质检体系）

路径：`/Users/iwatchme/Documents/iwatchme-skills/skills/iwatchme-technical-writing/SKILL.md`

**执行方式**：主 session 读取报告草稿 + technical-writing SKILL.md，按其中的「六、质检体系」执行四层质检。

**不得使用联网工具**，全部基于本地文件内容判断。

### L1 硬性规则（零容忍）

逐项检查，全部零命中方可通过：

| 检查项 | 禁用内容 |
|--------|---------|
| 禁用词 | 大厂黑话 + AI 清嗓词 + AI 强调词 + AI 填充词（详见 technical-writing 3.1 节）|
| 事实硬伤 | 版本、路径、工具名、类名、参数值、数据、URL 有误 |
| 代码规范 | 代码块未标注语言；省略代码无注释；贴代码截图 |
| 数据规范 | 数据无单位、无条件、无基线 |
| 格式一致 | 中英文空格不一致；Markdown 标题层级混乱；链接失效 |
| 夸张比喻 | 核弹级/雪崩式/魔法般/一招封神 等 |

**通过标准**：六项全部零命中。

### L2 可读性检查

| 检查项 | 标准 |
|--------|------|
| 开头 | 三句内进入主题并交代读者收益 |
| 节奏 | 有长短句交替；高密度部分有呼吸点 |
| 结构 | 段落之间有自然过渡；每个板块有明确核心观点 |
| 读者视角 | 读完每段能答"这一段在说什么"；无需要回头重读的逻辑跳跃 |

**通过标准**：开头必须通过；其余至少 3/4 项通过。

### L3 内容深度检查

| 检查项 | 标准 |
|--------|------|
| 论据支撑 | 每个核心判断至少有经验/数据/代码/图/引用之一支撑 |
| 知识输出 | 从"为什么存在"讲起再到"怎么工作" |
| 独创性 | 有"换了别人写不出这个角度"的内容 |
| 对立面 | 涉及判断时考虑反方观点 |
| 可执行性 | 仅限教程/方法论类：每个建议落到具体动作 |

**通过标准**：论据支撑和知识输出必须通过；其余至少 2/3 通过。

### L4 活人感终审

| 检查项 | 判断标准 |
|--------|---------|
| 温度感 | 情绪表达是体感的还是知识性的 |
| 独特性 | 有作者个人视角的痕迹还是完全猜不出是谁写的 |
| 姿态 | 语气是同行分享还是导师教学 |
| 心流 | 从头到尾读有没有注意力断掉的地方 |

**通过标准**：整体感觉"像是真人写的"。

### 质检报告格式

```markdown
## 四层质检报告

**L1 硬性规则** pass/fail
- 禁用词：X 处命中（列出命中的词或句式）
- 事实硬伤：X 处（具体位置和错误内容）
- 代码规范：X 处不一致
- 数据规范：X 处缺失
- 格式一致：X 处不一致
- 夸张比喻：X 处命中

**L2 可读性** pass/fail
- 开头：pass/fail（具体问题）
- 节奏：pass/fail（具体问题）
- 结构：pass/fail（具体问题）
- 读者视角：pass/fail（具体问题）

**L3 内容深度** pass/fail
- 论据支撑：pass/fail（缺失位置）
- 知识输出：pass/fail
- 独创性：pass/fail
- 对立面：pass/fail/不适用
- 可执行性：pass/fail/不适用

**L4 活人感** pass/fail
- 温度感：pass/fail
- 独特性：pass/fail
- 姿态：pass/fail
- 心流：pass/fail

**总评**: 4 层全部通过 / 需修复后重检 / 建议人工复审
**最需修复**: [1-3 个具体问题，具体到段落]
```

### rewrite 触发逻辑

| 质检结果 | 处理 |
|---------|------|
| L1 不通过 | **强制 rewrite**，列出命中的禁用词/硬伤位置 |
| L2 不通过（开头未过） | **强制 rewrite** |
| L2 不通过（其他项） | 可选 rewrite，明确告知具体段落 |
| L3 论据支撑/知识输出不通过 | **强制 rewrite**，指出缺乏支撑的具体判断 |
| L4 整体不通过 | **强制 rewrite**，给出"哪个段落 AI 味重"的具体指引 |
| 全部通过 | 进入 Phase 3 交付 |

rewrite 完成后再执行一次 Phase 2c 质检，通过才能交付。

---

## Phase 3: 交付

1. **报告路径**：`{research_output_dir}/{YYYY-MM-DD}-{slug}-深度调研.md`
2. **发送用户**：
   - 标题 + 摘要预览（前 5 行）
   - 全文
   - 附注：`已完成。报告共 X 字，Phase 0 命中 {N} 个本地文件，Phase 1 抓取 {Z} 个来源，Phase 2c 四层质检 [通过/强制 rewrite X 轮]，参考资料 {M} 篇已归档。`

---

## 一手资料优先原则

| 优先级 | 资料类型 |
|--------|----------|
| 1 | 源码 |
| 2 | 官方文档 |
| 3 | 学术论文（arxiv 等） |
| 4 | 官方 Issue / Release Notes |
| 5 | 官方博客 |
| — | 二手博客（仅作线索，必须追溯到一手） |

---

## 错误处理

| 场景 | 处理 |
|------|------|
| Phase 0 扫描目录不存在 | **静默跳过** |
| Phase 0 ripgrep 无结果 | 正常继续，输出"本地无命中" |
| technical-writing skill 文件不存在 | **报错提示用户安装 iwatchme-technical-writing skill** |
| 研究员超时 | 缩小范围重试 1 次 |
| Phase 2c 质检不通过 | 触发 rewrite，修复后再质检 |
| 写文件到 Vault 失败 | 降级到 /tmp，通知用户 |
