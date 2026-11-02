---
type: topic
source: 重述自 saas-seo-playbook
tags: [seo, 关键词, 优先级, 规划]
status: ready
updated: 2026-11-02
---

# 关键词优先级与页面规划（Topic Map / Keyword-to-Page）

> 摘要：找到一堆词之后，先打哪个？怎么把词落到具体页面？用"优先级打分 + 主题地图 + 词页映射"三步解决。

## 第一步：排优先级

拿到候选词清单后，用几个维度打分排序（saas-seo-playbook 的"关键词优先级"思路，重述）：

| 维度 | 权重参考 | 说明 |
|---|---|---|
| 商业价值 | 高 | 离转化越近越优先 |
| 难度 KD | 高（反向） | 新站优先低难度 |
| 流量潜力 | 中 | 实际能拿的点击 |
| 覆盖速度 | 中 | 做个页面就能上，还是要做一整套 |

排完你会得到一张"先做哪些、后做哪些"的清单。**新站别贪多，先打 10~20 个能赢的词立住基本盘**。

## 第二步：Topic Map（主题地图）

别把关键词当成孤立的点，要把它们归成"主题簇"：

- 一个**支柱页（Pillar）**讲大主题（如"AI 去背景"）。
- 多个**簇页（Cluster）**讲子话题（如"批量去背景""证件照去背景""去背景 vs 抠图"）。
- 簇页内链回支柱页，形成主题权威。

这样谷歌更容易理解"你这个站就是讲 X 的专家"，整站权重互相带动。

## 第三步：Keyword-to-Page（词页映射）

明确"每个搜索意图，由哪个页面承接"，避免两个页面抢同一个词（自家内耗）：

- 信息词 → 博客 / 教程页
- 商业词 → 对比 / 榜单 / 评测页
- 交易词 → 产品 / 定价 / 注册页

**一条原则：一个词尽量只由一个页面主打**，否则页面之间互相竞争，谁都排不好。

## 用 URL 结构把规划固化

规划好之后，用 URL 把"书的结构"定下来（saas-seo-playbook 的比喻：把网站规划成一本书）：

```
/ai-background-remover/        ← 支柱页
/ai-background-remover/batch   ← 簇页
/ai-background-remover/id-photo
/compare/remove-bg-vs-...      ← 对比页（商业词）
```

清晰的结构 = 清晰的意图分配 = 谷歌更好理解。

## 关联

- [[20-keyword/keyword-research-basics]] — 怎么找词
- [[20-keyword/keyword-metrics]] — 打分用的指标
- [[90-saas-playbook/keyword-to-page]] — SaaS 实战里怎么落地这一套
- [[40-on-page/internal-links]] — 内链如何支撑 Topic Map
