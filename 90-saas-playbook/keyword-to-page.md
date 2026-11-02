---
type: topic
source: 重述自 saas-seo-playbook
tags: [seo, SaaS, 规划, Topic Map, URL]
status: ready
updated: 2026-11-02
---

# 从关键词到页面（Topic Map / Keyword-to-Page / URL 结构）

> 摘要：把零散关键词组织成"主题地图"，明确每个意图由哪个页面承接，并用 URL 把网站规划成一本书。

## 1. 关键词研究 → Topic Map

别把词当孤岛。按主题聚类，形成"支柱页 + 簇页"结构（详见 [`20-keyword/keyword-priority.md`](../20-keyword/keyword-priority.md)）：

- 支柱页讲大主题（如"AI 去背景"）。
- 簇页讲子话题（如"批量去背景""证件照去背景"）。
- 簇页内链回支柱页，互相支撑主题权威。

## 2. Keyword-to-Page：一个意图一个承接页

明确每个搜索意图由谁承接，避免内耗：

| 意图 | 承接页面 |
|---|---|
| 信息词 | 博客 / 教程 |
| 商业词 | 对比 / 榜单 / 评测 |
| 交易词 | 产品 / 定价 / 注册 |

**一条词尽量只由一个页面主打**，否则自家页面互相抢排名，谁都排不好。

## 3. URL 结构：把网站规划成一本书

URL 应当反映上述规划，清晰、稳定、可读：

```
/remove-background/            ← 支柱
/remove-background/batch       ← 簇页
/remove-background/id-photo
/compare/remove-bg-vs-...      ← 商业词页
/pricing                       ← 交易词页
```

- 层级对应主题从属关系。
- 别用无意义参数（`?id=12`）。
- **稳定不随便改**；要改必做 301（见 [`60-technical/crawl-and-index.md`](../60-technical/crawl-and-index.md)）。

## 作者的补充：整站打内页

作者自有打法（重述）：当某个词 SERP 前十大多是"大站的一个内页"而非独立首页时，你用一个**专注的整站**去打那个内页，反而更容易赢——因为大站内页只是它海量内容里的一页，而你整站只讲这一件事。

## 关联

- [[90-saas-playbook/site-foundation]] — 地基怎么搭才撑得起这套结构
- [[40-on-page/internal-links]] — 内链如何把 Topic Map 连起来
