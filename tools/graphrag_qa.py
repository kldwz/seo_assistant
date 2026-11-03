#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
graphrag_qa.py — Phase 2：基于本库图谱的 GraphRAG 问答

设计取向（轻量、复用你已有图谱，不另起炉灶重抽）：
  - 检索：本机 Embedding 模型做语义召回（比关键词更准）
  - 图扩展：召回命中页后，沿 wikilink + 语义边「走 1~2 跳邻居」补相关上下文
            —— 这是普通 RAG 没有、图谱带来的增量
  - 全局/综述题：你的模块天然是「社区」，离线生成每模块社区摘要，
            问「整体立场/对比/体系」时用社区摘要答（GraphRAG 的 community 思路）

真源仍是 markdown；本脚本产物（embeddings / 社区摘要）都是派生，可重跑重建。

依赖：OPENAI_BASE_URL / OPENAI_API_KEY（SiliconFlow 等 OpenAI 兼容网关）
      EMBED_MODEL 默认 Qwen/Qwen3-Embedding-0.6B，ANSWER_MODEL 默认 DeepSeek-V3

用法：
  python3 tools/graphrag_qa.py index            # 建索引（Embedding + 社区摘要）
  python3 tools/graphrag_qa.py ask "外链怎么做"   # 普通检索问答
  python3 tools/graphrag_qa.py ask "你这套对外链的整体立场是什么" --global   # 全局综述
"""
import os
import re
import sys
import json
import math
import argparse
import subprocess
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_JSON = os.path.join(REPO_ROOT, "graph", "graph.json")
EMB_JSON = os.path.join(REPO_ROOT, "graph", "embeddings.json")
COMM_JSON = os.path.join(REPO_ROOT, "graph", "community_summaries.json")

EMBED_MODEL = os.environ.get("EMBED_MODEL", "Qwen/Qwen3-Embedding-0.6B")
ANSWER_MODEL = os.environ.get("ANSWER_MODEL", "Pro/deepseek-ai/DeepSeek-V3")
if ANSWER_MODEL in ("deepseek-chat", "gpt-3.5-turbo", ""):
    ANSWER_MODEL = "Pro/deepseek-ai/DeepSeek-V3"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

GLOBAL_KW = ["整体", "全局", "总结", "所有", "对比", "立场", "哲学", "怎么看",
             "综述", "全库", "体系", "核心观点", "区别", "本质", "一句话概括", "你的看法"]


# ---------------- 基础工具 ----------------
def file_id(rel):
    return rel[:-3] if rel.endswith(".md") else rel


def load_pages(full=False):
    pages = {}
    for dirpath, _, filenames in os.walk(REPO_ROOT):
        if "/.git" in dirpath or dirpath.endswith("/tools") or dirpath.endswith("/graph"):
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            fullp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fullp, REPO_ROOT)
            fid = file_id(rel)
            with open(fullp, encoding="utf-8") as f:
                text = f.read()
            m = FRONTMATTER_RE.match(text)
            body = text[m.end():] if m else text
            hm = H1_RE.search(body)
            title = hm.group(1).strip() if hm else os.path.basename(rel)[:-3]
            module = rel.split("/")[0]
            if module.endswith(".md"):
                module = "(根)"
            clean = WIKILINK_RE.sub(lambda x: x.group(1).split("|")[0].split("#")[0], body)
            clean = re.sub(r"```.*?```", "", clean, flags=re.DOTALL)
            clean = re.sub(r"\n{2,}", "\n", clean).strip()
            pages[fid] = {
                "id": fid, "title": title, "module": module,
                "text": clean if full else clean[:1200],
            }
    return pages


def _curl_json(url, body, timeout=120):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(body, f, ensure_ascii=False)
    try:
        out = subprocess.run(
            ["curl", "-s", url, "-H", f"Authorization: Bearer {os.environ['OPENAI_API_KEY']}",
             "-H", "Content-Type: application/json", "-d", f"@{path}"],
            capture_output=True, text=True, timeout=timeout,
        )
        return json.loads(out.stdout)
    finally:
        os.remove(path)


def embed(text):
    d = _curl_json(f"{os.environ['OPENAI_BASE_URL'].rstrip('/')}/embeddings",
                   {"model": EMBED_MODEL, "input": text[:8000]})
    return d["data"][0]["embedding"]


def chat(system, user, temperature=0.3):
    d = _curl_json(f"{os.environ['OPENAI_BASE_URL'].rstrip('/')}/chat/completions",
                   {"model": ANSWER_MODEL,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}],
                    "temperature": temperature})
    return d["choices"][0]["message"]["content"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------------- index ----------------
def cmd_index():
    pages = load_pages()
    print(f"[index] 嵌入 {len(pages)} 页 …")
    embs = {}
    i = 0
    for fid, p in pages.items():
        embs[fid] = embed(p["text"])
        i += 1
        if i % 10 == 0:
            print(f"  已嵌入 {i}/{len(pages)}")
    json.dump(embs, open(EMB_JSON, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"[index] 向量已存 {EMB_JSON}")

    # 社区摘要：按模块
    by_mod = {}
    for p in pages.values():
        by_mod.setdefault(p["module"], []).append(p)
    comm = {}
    print("[index] 生成模块社区摘要 …")
    for mod, ps in by_mod.items():
        block = "\n\n".join(f"### {p['title']}\n{p['text'][:500]}" for p in ps)
        sys_p = ("你是这个 SEO 知识库的模块编辑。请基于下面某模块各页的摘要，"
                 "写一段 250 字以内的『社区摘要』：提炼该模块核心知识点、"
                 "作者在该主题上的关键立场/实战结论（尤其抓住『作者与主流不同』或『踩坑红线』），"
                 "以及它和其余模块的关系。中文、不要列表堆砌。")
        user_p = f"模块：{mod}\n\n{block}"
        try:
            comm[mod] = chat(sys_p, user_p, temperature=0.3)
            print(f"  ✓ {mod}")
        except Exception as e:
            print(f"  [warn] {mod} 失败: {e}")
            comm[mod] = ""
    json.dump(comm, open(COMM_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[index] 社区摘要已存 {COMM_JSON}")


# ---------------- ask ----------------
def build_graph_adj():
    g = json.load(open(GRAPH_JSON, encoding="utf-8"))
    adj = {}
    for e in g.get("edges", []):
        adj.setdefault(e["source"], []).append(e["target"])
        adj.setdefault(e["target"], []).append(e["source"])
    for e in g.get("semantic_edges", []):
        adj.setdefault(e["source"], []).append(e["target"])
        adj.setdefault(e["target"], []).append(e["source"])
    return adj


def cmd_ask(question, global_mode=False, topk=5, hops=1):
    embs = json.load(open(EMB_JSON, encoding="utf-8"))
    pages = load_pages(full=True)
    adj = build_graph_adj()
    qvec = embed(question)

    scored = sorted(((fid, cosine(qvec, vec)) for fid, vec in embs.items()),
                    key=lambda x: -x[1])
    # 全局/综述模式：用社区摘要
    if global_mode or any(k in question for k in GLOBAL_KW):
        comm = json.load(open(COMM_JSON, encoding="utf-8"))
        comm_vecs = {m: embed(s) for m, s in comm.items() if s}
        mod_rank = sorted(((m, cosine(qvec, v)) for m, v in comm_vecs.items()), key=lambda x: -x[1])
        top_mods = [m for m, _ in mod_rank[:3]]
        ctx = "## 相关模块社区摘要（全局视图）\n"
        for m in top_mods:
            ctx += f"\n### 模块 {m}\n{comm[m]}\n"
        mode_note = "（检测到全局/综述类问题，已用模块社区摘要作答）"
    else:
        # 普通模式：语义召回 + 沿图扩召回邻居
        seeds = [fid for fid, _ in scored[:topk]]
        ctx_ids = set(seeds)
        frontier = list(seeds)
        for _ in range(hops):
            nxt = []
            for s in frontier:
                for nb in adj.get(s, []):
                    if nb not in ctx_ids:
                        ctx_ids.add(nb)
                        nxt.append(nb)
            frontier = nxt
        # 按相关度排序上下文页
        rank = {fid: s for fid, s in scored}
        ordered = sorted(ctx_ids, key=lambda x: -rank.get(x, 0))
        ctx = "## 相关页面（含图谱邻居扩展）\n"
        for fid in ordered[:14]:
            p = pages[fid]
            ctx += f"\n### {p['title']}（{fid}）\n{p['text'][:1100]}\n"
        mode_note = f"（语义召回 top{topk} + 图扩展 {hops} 跳，共 {len(ctx_ids)} 页）"

    system = ("你是『kldwz 的 SEO 知识库』的 AI 助手，面向 SEO 新手。\n"
              "规则：\n"
              "1. 只基于下面提供的【上下文】回答，不得编造上下文之外的 SEO 建议；\n"
              "2. 回答要准确、对新手友好、给出可执行结论；\n"
              "3. 在提到某观点/数据时，用 （来源：页面路径）标注出处；\n"
              "4. 若上下文不足以回答，明确说『本库暂未覆盖』，不要硬编。")
    user = f"{ctx}\n\n## 用户问题\n{question}\n\n请回答，并附'参考页面'列表（用页面路径）。"
    answer = chat(system, user, temperature=0.3)
    print("=" * 60)
    print(f"问题：{question}  {mode_note}")
    print("=" * 60)
    print(answer)
    print("\n--- 召回页面 ---")
    if global_mode or any(k in question for k in GLOBAL_KW):
        for m in top_mods:
            print(f"  [社区] {m}")
    else:
        for fid in ordered[:14]:
            print(f"  {fid}  (相关度 {rank.get(fid,0):.2f})")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("index")
    p_ask = sub.add_parser("ask")
    p_ask.add_argument("question")
    p_ask.add_argument("--global", dest="global_mode", action="store_true")
    p_ask.add_argument("--topk", type=int, default=5)
    p_ask.add_argument("--hops", type=int, default=1)
    args = ap.parse_args()
    if args.cmd == "index":
        cmd_index()
    elif args.cmd == "ask":
        cmd_ask(args.question, args.global_mode, args.topk, args.hops)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
