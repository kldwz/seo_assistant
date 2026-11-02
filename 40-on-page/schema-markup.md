---
type: topic
source: 重述自 Ahrefs
tags: [seo, 页面, schema, 结构化数据]
status: ready
updated: 2026-11-02
---

# Schema 标记（结构化数据）

> 摘要：Schema 是用特殊代码（JSON-LD 等）告诉搜索引擎"这段内容是什么类型"——文章、商品、评分、FAQ 等，有助于拿到富媒体结果。

## 解决什么问题

正常文字，谷歌要"猜"这是篇博客还是个商品。Schema 标记相当于你**主动贴上标签**，降低误解，并可能让你在搜索结果里展示得更丰富（星级、价格、FAQ 折叠等），从而提升点击率。

## 常见类型

- `Article` / `BlogPosting`：文章
- `Product` / `Offer`：商品与价格
- `FAQPage`：问答，可在结果里直接展开
- `Review` / `AggregateRating`：评分
- `HowTo`、`Breadcrumb`、`Organization` 等

## 怎么做（新手角度）

- 用 **JSON-LD** 格式（谷歌推荐，放在 `<head>` 或 `<body>` 里一段 script）。
- 多数建站工具/CMS 有插件自动生成（如 WordPress 的 rankmath / Yoast）。
- 写完后用 Google 的 Rich Results Test 验证是否能识别。

## 注意

- Schema 是"争取更好展示"的加分项，**不是排名直接因子**，也别为了富媒体去造假评分（会被罚）。
- 优先做对你最有用的几种（博客站做 Article/FAQ，电商做 Product）。

## 关联

- [[60-technical/seo-tools]] — 验证工具
- [[40-on-page/tdk]] — 更基础的页面优化
