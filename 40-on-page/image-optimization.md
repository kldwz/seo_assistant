---
type: topic
source: 重述自 Ahrefs
tags: [seo, 页面, 图片, 速度]
status: ready
updated: 2026-11-02
---

# 图片优化

> 摘要：图片常常是拖慢网站、拖垮体验的元凶。优化图片=压缩体积+正确格式+写 alt 文本，兼顾速度与可理解。

## 三件事

1. **压缩与格式**
   - 用现代格式：WebP / AVIF 比 JPG/PNG 小很多。
   - 上传前压缩（工具如 squoosh、tinyjpg）。
   - 尺寸按需给，别传 4000px 大图却只显示 800px。

2. **alt 文本（替代文字）**
   - 给图片加 `alt="..."`，描述图片内容。
   - 好处：无障碍（读屏）、图片搜索流量、让谷歌理解图文关系。
   - 自然描述即可，别硬塞关键词。

3. **懒加载 / 响应式**
   - 非首屏图片懒加载（`loading="lazy"`），加快首屏。
   - 用 `srcset` 适配不同设备。

## 为什么重要

- 图片过大 → 页面加载慢 → Core Web Vitals 差 → 排名和用户都受影响（见 [`ux-core-web-vitals.md`](./ux-core-web-vitals.md)）。
- 图片搜索本身也是一块免费流量来源。

## 关联

- [[40-on-page/ux-core-web-vitals]] — 速度与体验指标
- [[60-technical/]] — 更底层的技术优化
