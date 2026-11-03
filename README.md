# SEO 知识库 · seo_assistant

> 一个**面向新手**、**可被 AI 直接消费**的 SEO 知识库。
> 目的：让不懂 SEO 的人能按路径系统学；让 AI 工具接上后能基于本库准确回答 SEO 问题。

本库内容采用 CC-BY-4.0 开放协议，可自由阅读、引用、二次创作（注明出处即可）。

---

## 这是什么

- **不是**又一份零散技巧合集，而是一套把 SEO 当"长期竞争系统"来讲的知识体系：搜索引擎怎么工作 → 怎么找词 → 怎么做内容 → 怎么优化页面 → 怎么建外链 → 怎么修技术 → 怎么在 AI 搜索时代生存 → 怎么用这套系统做 SaaS/工具站。
- 内容以**作者自有实战经验为主干**，并参考了 Ahrefs 官方指南、saas-seo-playbook（MIT）等公开资料（均已重述并标注出处，不抄原文）。
- 结构与你熟悉的 Obsidian 知识库一致：每个主题一个目录 + `_INDEX.md` 索引 + 术语表 + 信源索引。

## 给谁看

- 完全不懂 SEO 的小白，想搞懂"SEO 到底是什么、怎么入门"。
- 独立开发者 / 出海站长 / SaaS 创业者，想用 SEO 拿免费搜索流量。
- **AI 工具**（Cursor、Claude Code、各类 RAG / Agent）：把本仓库作为知识源接上，即可回答用户的 SEO 问题。使用前请先读 [`AGENTS.md`](./AGENTS.md)。

## 新手三步学习路径

1. **先搞懂是什么**：读 [`00-start-here/what-is-seo.md`](./00-start-here/what-is-seo.md) 和 [`beginners-myths.md`](./00-start-here/beginners-myths.md)。
2. **按顺序学主干**：按 [`00-start-here/learning-path.md`](./00-start-here/learning-path.md) 的路线图，从 `10-fundamentals` 一路学到 `90-saas-playbook`。
3. **遇到名词就查表**：任何不懂的术语，先去 [`glossary/`](./glossary/_INDEX.md) 查。

## 全目录速览

| 区块 | 讲什么 | 入口 |
|---|---|---|
| 00 新手入口 | SEO 是什么 / 学习路径 / 常见误区 | [`00-start-here/`](./00-start-here/_INDEX.md) |
| 10 基础 | 搜索引擎原理 + SEO 四大要素 | [`10-fundamentals/`](./10-fundamentals/_INDEX.md) |
| 20 关键词 | 搜索意图 / 找词 / 优先级 / Topic Map | [`20-keyword/`](./20-keyword/_INDEX.md) |
| 30 内容 | SEO 内容 / E-E-A-T / 信息增量 | [`30-content/`](./30-content/_INDEX.md) |
| 40 页面 SEO | TDK / 内链 / Schema / 图片 / UX | [`40-on-page/`](./40-on-page/_INDEX.md) |
| 50 链接 | 外链基础 / 怎么做 / 什么有用 | [`50-links/`](./50-links/_INDEX.md) |
| 60 技术 SEO | 抓取 / 索引 / Core Web Vitals | [`60-technical/`](./60-technical/_INDEX.md) |
| 70 本地 SEO | 本地搜索可见度 | [`70-local/`](./70-local/_INDEX.md) |
| 80 AI 搜索 | AEO / GEO / AI Overviews | [`80-ai-search/`](./80-ai-search/_INDEX.md) |
| 90 SaaS 实战 | 一套可落地的 SEO 作战系统 | [`90-saas-playbook/`](./90-saas-playbook/_INDEX.md) |
| 术语表 | 220+ SEO 术语速查 | [`glossary/`](./glossary/_INDEX.md) |
| 信源索引 | 外部资料出处与点评 | [`references/`](./references/_INDEX.md) |

## 给 AI 工具

请先阅读 [`AGENTS.md`](./AGENTS.md) —— 它规定了 AI 应如何在本库内检索、引用与回答，确保回答准确、有出处、对新手友好。

## 知识图谱（可视化）

本库附带一个自动生成的关系图谱（Phase 0 显式 `[[双链]]` + Phase 1 LLM 抽取的语义关系）：

- **本地查看**：双击打开 [`graph/index.html`](./graph/index.html)（自带数据，无需联网即可看；按模块上色、可筛选、点击看详情）。
- **机器消费**：[`graph/graph.json`](./graph/graph.json) 含全部节点/边/语义关系；[`graph/semantic_edges.json`](./graph/semantic_edges.json) 是语义关系层的独立审计文件。
- **重新生成**：`python3 tools/build_graph.py`（重抽语义层：`python3 tools/extract_semantic.py`）。markdown 为真源，图谱为派生视图，改了文档重跑即可。

## 基于图谱的问答（GraphRAG）

本库附带一个轻量 GraphRAG 问答管线 [`tools/graphrag_qa.py`](./tools/graphrag_qa.py)，把图谱当图结构层来用：

- **检索**：本机 Embedding 模型做语义召回（比关键词准）；
- **图扩展**：命中页后沿 `[[双链]]` + 语义边**走 1~2 跳邻居**补上下文（普通 RAG 没有的增量）；
- **全局/综述题**：用按模块预生成的**社区摘要**答"整体立场/体系/对比"这类跨页题。

```bash
export OPENAI_BASE_URL=...   # OpenAI 兼容网关（如 SiliconFlow）
export OPENAI_API_KEY=...
python3 tools/graphrag_qa.py index              # 建索引（Embedding + 社区摘要）
python3 tools/graphrag_qa.py ask "外链怎么做"     # 普通问答
python3 tools/graphrag_qa.py ask "你这套对外链的整体立场" --global  # 全局综述
```

产物：`graph/embeddings.json`（页向量）、`graph/community_summaries.json`（模块摘要）。均为派生，可重跑重建。

## 版权与署名

- 本库原创内容：CC-BY-4.0，署名 `kldwz / seo_assistant` 即可自由使用。
- 参考的第三方资料（Ahrefs、saas-seo-playbook 等）在各页"延伸阅读"中标注，版权归原作者所有，本库仅做重述与点评。
