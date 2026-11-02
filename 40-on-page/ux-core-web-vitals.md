---
type: topic
source: 重述自 Ahrefs
tags: [seo, 页面, 体验, Core Web Vitals]
status: ready
updated: 2026-11-02
---

# 用户体验与 Core Web Vitals

> 摘要：谷歌把"页面体验"当排名因素。Core Web Vitals 是三个核心指标——加载慢、乱跳、不好点，都会被扣分。

## Core Web Vitals 三指标

| 指标 | 测什么 | 好的标准 |
|---|---|---|
| **LCP** 最大内容绘制 | 主要内容多快加载完 | ≤ 2.5 秒 |
| **CLS** 累积布局偏移 | 页面元素会不会乱跳 | ≤ 0.1（基本不跳） |
| **INP** 交互到响应 | 点击后多久有反应 | ≤ 200 毫秒 |

简单记：**快（LCP）、稳（CLS）、灵（INP）**。

## 其他体验信号

- **移动友好**：现在主流是移动优先索引，手机端体验差直接拖全局。
- **HTTPS**：安全连接是基本门槛。
- **无侵入广告**：别用遮满屏的弹窗/插屏广告。
- **可读性**：排版、字号、对比度。

## 怎么改善（新手）

- 上 CDN、开缓存、压缩图片（见 [`image-optimization.md`](./image-optimization.md)）。
- 减少阻塞渲染的脚本；用轻量主题/框架。
- 给图片和广告位预留尺寸，避免 CLS 跳动。
- 用 PageSpeed Insights / Search Console 的"核心网页指标"报告看具体哪里差。

## 关联

- [[60-technical/crawl-and-index]] — 更底层技术优化
- [[60-technical/seo-tools]] — 测速与诊断工具
