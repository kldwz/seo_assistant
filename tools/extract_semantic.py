#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_semantic.py — Phase 1：在 wikilink 图之上抽取「语义关系」层

为什么需要它：wikilink 只覆盖你手写的显式引用。很多真实存在的隐含关联
（如「程序化 SEO → 新站必死」「整站打内页 → 内链」）没写成 [[双链]]，
LLM 逐模块把它们抽成 (源, 关系, 目标, 依据) 三元组，合进 graph.json 的
semantic_edges，与 wikilink 边分离、可审计、不污染你手写的结构。

约束（防幻觉）：
  - 源节点 = 本模块页面；目标节点 ∈ 全库已知页面 id（词汇表白名单）
  - 若某条目标不在白名单，丢弃
  - 与已有 wikilink 边重复的 (source,target) 丢弃

依赖：环境变量 OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL_ID（SiliconFlow 等 OpenAI 兼容网关）

用法：
  python3 tools/extract_semantic.py            # 全量抽取
  python3 tools/extract_semantic.py --module 50-links   # 只抽某个模块
  python3 tools/extract_semantic.py --limit 3            # 只跑前 3 个模块（调试）
"""
import os
import re
import sys
import json
import subprocess
import tempfile
import argparse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_JSON = os.path.join(REPO_ROOT, "graph", "graph.json")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def file_id(rel):
    return rel[:-3] if rel.endswith(".md") else rel


def load_pages():
    pages = {}
    for dirpath, _, filenames in os.walk(REPO_ROOT):
        if "/.git" in dirpath or dirpath.endswith("/tools") or dirpath.endswith("/graph"):
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, REPO_ROOT)
            fid = file_id(rel)
            with open(full, encoding="utf-8") as f:
                text = f.read()
            m = FRONTMATTER_RE.match(text)
            body = text[m.end():] if m else text
            hm = H1_RE.search(body)
            title = hm.group(1).strip() if hm else os.path.basename(rel)[:-3]
            module = rel.split("/")[0]
            if module.endswith(".md"):
                module = "(根)"
            # 内容摘要：去 wikilink 语法、截断
            clean = WIKILINK_RE.sub(lambda x: x.group(1).split("|")[0].split("#")[0], body)
            clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
            excerpt = clean.strip()[:900]
            pages[fid] = {"id": fid, "title": title, "module": module, "excerpt": excerpt}
    return pages


def call_llm(system, user):
    body = {
        "model": os.environ.get("OPENAI_MODEL_ID", "deepseek-chat"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    try:
        out = subprocess.run(
            ["curl", "-s", f"{os.environ['OPENAI_BASE_URL'].rstrip('/')}/chat/completions",
             "-H", f"Authorization: Bearer {os.environ['OPENAI_API_KEY']}",
             "-H", "Content-Type: application/json", "-d", f"@{path}"],
            capture_output=True, text=True, timeout=120,
        )
        data = json.loads(out.stdout)
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"  [warn] LLM 调用失败: {e}")
        return None
    finally:
        os.remove(path)


def extract_for_module(module, mod_pages, vocab):
    vocab_lines = "\n".join(f"- {v['id']} ｜ {v['title']}" for v in vocab)
    pages_block = "\n\n".join(
        f"### 页面 {p['id']}（{p['title']}）\n{p['excerpt']}" for p in mod_pages
    )
    system = (
        "你是 SEO 知识库的图谱工程师。任务：从给定模块的正文中，抽取页面之间"
        "『真实存在但没写成超链接』的语义关系。\n"
        "规则：\n"
        "1. 每条关系形如 {source, relation, target, rationale}。\n"
        "2. source 必须是本模块中的页面 id；target 必须来自下方『全库页面词汇表』中的 id（白名单，不得自造）。\n"
        "3. relation 用 2~6 字中文短语概括关系类型，如：依赖/前提/包含/对比/扩展/反例/因果/适用/补充。\n"
        "4. rationale 用一句话说明为什么这两条有关联（基于内容，不是空话）。\n"
        "5. 只抽有意义的、能帮新手建立知识连接的关联；不要凑数，最多 15 条。\n"
        "6. 输出严格 JSON：{\"relations\":[...]}。"
    )
    user = (
        f"本模块：{module}\n\n"
        f"== 本模块页面正文 ==\n{pages_block}\n\n"
        f"== 全库页面词汇表（target 只能从这里选）==\n{vocab_lines}\n\n"
        "请输出 JSON。"
    )
    raw = call_llm(system, user)
    if not raw:
        return []
    try:
        obj = json.loads(raw)
        rels = obj.get("relations", [])
    except Exception:
        print(f"  [warn] {module} 返回非 JSON，跳过")
        return []
    results = []
    for r in rels:
        s, t = r.get("source"), r.get("target")
        if s not in {p["id"] for p in mod_pages}:
            continue
        if t not in {v["id"] for v in vocab}:
            continue
        if s == t:
            continue
        results.append({
            "source": s, "relation": r.get("relation", "关联"),
            "target": t, "rationale": r.get("rationale", ""),
        })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", help="只处理某模块（如 50-links）")
    ap.add_argument("--limit", type=int, help="只跑前 N 个模块（调试）")
    ap.add_argument("--model", help="覆盖使用的模型 id")
    args = ap.parse_args()

    MODEL = args.model or os.environ.get("OPENAI_MODEL_ID") or "Pro/deepseek-ai/DeepSeek-V3"
    # 网关常见占位名在此环境无效，落到可用默认
    if MODEL in ("deepseek-chat", "gpt-3.5-turbo", ""):
        MODEL = "Pro/deepseek-ai/DeepSeek-V3"
    os.environ["OPENAI_MODEL_ID"] = MODEL

    pages = load_pages()
    vocab = list(pages.values())
    by_module = {}
    for p in pages.values():
        by_module.setdefault(p["module"], []).append(p)

    # 已有 wikilink 边集合，用于去重
    existing = set()
    if os.path.exists(GRAPH_JSON):
        g = json.load(open(GRAPH_JSON, encoding="utf-8"))
        for e in g.get("edges", []):
            existing.add((e["source"], e["target"]))

    modules = sorted(by_module.keys())
    if args.module:
        modules = [m for m in modules if m == args.module]
    if args.limit:
        modules = modules[: args.limit]

    all_sem = []
    for mod in modules:
        print(f"[extract] 模块 {mod} （{len(by_module[mod])} 页）…")
        rels = extract_for_module(mod, by_module[mod], vocab)
        kept = [r for r in rels if (r["source"], r["target"]) not in existing]
        dup = len(rels) - len(kept)
        all_sem.extend(kept)
        print(f"          抽到 {len(rels)} 条，去重(wikilink) {dup}，保留 {len(kept)}")

    # 合并进 graph.json（保留历史已抽结果：若只跑单模块，先读旧再补）
    g = json.load(open(GRAPH_JSON, encoding="utf-8")) if os.path.exists(GRAPH_JSON) else {"edges": []}
    old = g.get("semantic_edges", [])
    if args.module or args.limit:
        # 增量：用新结果覆盖该模块相关项，保留其它模块旧结果
        mod_ids = {p["id"] for p in by_module.get(args.module, [])} if args.module else None
        kept_old = [e for e in old if mod_ids is None or (e["source"] not in mod_ids)]
        merged = kept_old + all_sem
    else:
        merged = all_sem
    # 去重（同 source,target,relation）
    seen = set()
    final = []
    for e in merged:
        k = (e["source"], e["target"], e["relation"])
        if k in seen:
            continue
        seen.add(k)
        final.append(e)
    g["semantic_edges"] = final
    g.setdefault("stats", {})["semantic_edge_count"] = len(final)
    json.dump(g, open(GRAPH_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 单独存一份可读审计文件
    json.dump(final, open(os.path.join(REPO_ROOT, "graph", "semantic_edges.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n完成：语义关系 {len(final)} 条 → graph/graph.json + graph/semantic_edges.json")


if __name__ == "__main__":
    main()
