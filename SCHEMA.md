# SCHEMA.md — SEO 知识库结构约定

> 本文件定义本知识库的目录结构、命名规范、页面模板与收录原则。
> 目标：让**新手**能按路径系统学，让 **AI 工具**接上后能基于本库准确回答 SEO 问题。

---

## 目录结构

```
seo-knowledge-base/
├── README.md          # 首页：定位 / 给谁 / 学习路径 / 目录速览
├── SCHEMA.md          # 本文件：结构约定
├── AGENTS.md          # 给 AI 的检索与回答说明书
├── LICENSE            # CC-BY-4.0（内容开放分享）
├── 00-start-here/     # 新手入口（从这里开始）
├── 10-fundamentals/   # 搜索引擎原理 + SEO 四大要素
├── 20-keyword/        # 关键词研究
├── 30-content/        # SEO 内容
├── 40-on-page/        # 页面 SEO
├── 50-links/          # 链接建设
├── 60-technical/      # 技术 SEO
├── 70-local/          # 本地 SEO
├── 80-ai-search/      # AI 搜索 / AEO / GEO
├── 90-saas-playbook/  # SaaS / 工具站 SEO 实战系统
├── glossary/          # 术语表（按分类 + A-Z 主索引）
└── references/        # 外部信源 L1 索引（只列出处，不搬原文）
```

## 页面命名规范

- 主题目录内页面：`kebab-case` 英文或中文语义名均可（如 `what-is-seo.md`、`search-intent.md`）。
- 目录内索引统一叫 `_INDEX.md`。
- 中文标题写在第一行 `# 标题`，文件名与标题解耦。

## 页面模板（frontmatter）

每页顶部统一 YAML：

```yaml
---
type: topic        # topic | concept | glossary | reference
source: 自有 | 重述自 Ahrefs | 重述自 saas-seo-playbook | 自有+重述
tags: [seo, 关键词]
status: ready      # ready | draft
updated: 2026-11-02
---
```

正文建议结构（概念/主题页）：

```markdown
# 标题

> 摘要：一句话说清这页讲什么。

## 是什么
## 为什么重要
## 怎么做（核心要点 / 步骤）
## 常见误区
## 延伸阅读
- [来源名](URL) — 一句话说明
## 关联
- [[其他页面]] — 关系
```

## 索引约定

- 每个主题目录必须有 `_INDEX.md`：分类表 + 每页一句话 + 变更记录。
- `glossary/_INDEX.md` 是术语 A-Z 主索引。
- `references/_INDEX.md` 是外部信源总表。
- 根 `README.md` 提供全库速览与学习路径。

## 收录与版权原则（硬性）

1. **自有内容**（作者本人推导/撰写的打法、教材、经验）可直接使用。
2. **第三方内容**（Ahrefs、saas-seo-playbook、哥飞等）一律**用自己话重述 + 标注延伸阅读出处**，**绝不整段复制原文**。
3. `references/` 只做 L1 索引（标题 + 链接 + 作者点评），不搬运正文。
4. 术语定义属公共知识，自行撰写；可在"延伸阅读"指向权威术语表。

## 双链约定

- 库内引用用 `[[相对路径去掉.md]]` 或相对链接 `./xxx.md`，便于 Obsidian 与 AI 检索。
- 修改/新增页面后，同步更新所在目录的 `_INDEX.md`。
