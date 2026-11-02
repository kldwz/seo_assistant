---
type: topic
source: 重述自 Ahrefs
tags: [seo, 技术, 速胜]
status: ready
updated: 2026-11-02
---

# 技术 SEO 速胜清单

> 摘要：不用成为工程师，也能先把这几件"性价比最高"的技术事做了，避免地基塌。

## 1. 上 HTTPS

安全连接是基本门槛。没 HTTPS 不仅排名吃亏，浏览器还会标"不安全"吓跑用户。现在免费证书（Let's Encrypt）很普遍，没有借口。

## 2. 移动友好

谷歌是**移动优先索引**：主要用你网站的移动版来排名。确保手机端排版正常、能点、不乱。用 Google 的 Mobile-Friendly Test 自查。

## 3. 速度

慢站既伤体验又伤排名。最快的入手点：压缩图片（见 [`40-on-page/image-optimization.md`](../40-on-page/image-optimization.md)）、上缓存/CDN、用轻量主题。用 PageSpeed Insights 看具体短板。

## 4. 清理重复内容

同样的内容多个 URL（带参数、www/非 www、http/https）会让谷歌不知道收哪个。用 canonical（见 [`crawl-and-index.md`](./crawl-and-index.md)）和 301 统一。

## 5. 修 404 / 死链

站内指向不存在页面的链接（死链）既伤体验也浪费抓取预算。定期扫一遍，修掉或 301 掉。

## 6. 保证重要页可达

每个重要页至少从首页/导航几步能点到，且有内链（见 [`40-on-page/internal-links.md`](../40-on-page/internal-links.md)）。别留孤儿页。

## 7. 提交 sitemap + 验证 GSC

见 [`crawl-and-index.md`](./crawl-and-index.md)。新站"被谷歌发现"的官方入口。

## 关联

- [[60-technical/seo-tools]] — 这些事用什么工具查
- [[60-technical/crawl-and-index]] — 抓取/索引细节
