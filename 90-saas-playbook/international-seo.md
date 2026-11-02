---
type: topic
source: 重述自 saas-seo-playbook
tags: [seo, SaaS, 国际化, 多语言]
status: ready
updated: 2026-11-02
---

# 国际化 SEO（多语言 / 多地区）

> 摘要：想把产品卖到海外不同语言/地区，要处理 hreflang、子域/子目录选择、本地化内容三件事。

## 为什么单独讲

出海 SaaS 天然面对多语言市场。但"翻译一下页面"不等于"能在该国排上去"——搜索引擎需要明确信号才知道"这个页面是给哪国、说哪种语言的用户看的"。

## 三件核心事

1. **hreflang 标记**
   - 告诉谷歌"同一内容的不同语言/地区版本分别给谁"，避免被当成重复内容，也能把对的版本推给对的人。
   - 例如 `hreflang="en-us"`、`hreflang="zh-cn"`。

2. **结构选择：子域 vs 子目录 vs 独立域**
   - `example.com/zh/`、`zh.example.com`、`example.cn` 各有取舍。
   - 子目录（如 `/zh/`）最省权重积累；独立国家域权威独立但要分别经营。
   - 作者自己的做法是"一个 niche 一个子域"，便于专注整站打内页（见 [`site-foundation.md`](./site-foundation.md)）。

3. **真正本地化，而非机翻**
   - 机翻内容质量差，且常被判低质。要本地化：用词习惯、例子、甚至本地支付方式/信任符号都不同。
   - 本地化的内容才可能在本地搜索里排上去。

## 起步建议

先把一个主力市场（语言）做扎实，再扩。别一上来铺十种语言却都半吊子。

## 关联

- [[90-saas-playbook/site-foundation]] — 子域架构如何服务国际化
- [[60-technical/crawl-and-index]] — hreflang 与 canonical 别冲突
