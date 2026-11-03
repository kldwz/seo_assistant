#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_graph.py — 从 SEO 知识库的 markdown 抽取 wikilink 关系图（Phase 0）

真源 = markdown 文件；本脚本产出派生视图：
  - graph/graph.json      机器可读（节点/边/标签/孤立页/断链），供 RAG / 图库消费
  - graph/index.html      自带数据，双击即可在浏览器看交互式知识图谱

用法：
  python3 tools/build_graph.py
（在仓库根目录或任意位置均可，脚本自动定位仓库根 = 本文件上级目录）
"""
import os
import re
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH_DIR = os.path.join(REPO_ROOT, "graph")

# ---------- 解析工具 ----------
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
TAGS_LINE_RE = re.compile(r"^tags:\s*(.+)$", re.MULTILINE)
TAG_LIST_RE = re.compile(r"-\s*([^\s]+)")
TITLE_RE = re.compile(r"^title:\s*(.+)$", re.MULTILINE)
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def parse_frontmatter(text):
    fm = {}
    m = FRONTMATTER_RE.match(text)
    if not m:
        return fm, text
    block = m.group(1)
    body = text[m.end():]
    # title
    tm = TITLE_RE.search(block)
    if tm:
        fm["title"] = tm.group(1).strip().strip('"').strip("'")
    # tags: 支持 `tags: [a, b]` 或 yaml 列表
    tl = TAGS_LINE_RE.search(block)
    tags = []
    if tl:
        inline = tl.group(1).strip()
        if inline.startswith("["):
            tags = [t.strip().strip('"').strip("'") for t in inline.strip("[]").split(",") if t.strip()]
        else:
            # 可能是多行列表，向后找 - 项
            rest = block[tl.end():]
            tags = [t for t in TAG_LIST_RE.findall(rest)]
            # 也包含同行里的
            if not tags and inline:
                tags = [inline]
    fm["tags"] = [t for t in tags if t]
    return fm, body


def extract_title(fm, body, fallback):
    if fm.get("title"):
        return fm["title"]
    hm = H1_RE.search(body)
    if hm:
        return hm.group(1).strip()
    return fallback


def file_id(rel_path):
    return rel_path[:-3] if rel_path.endswith(".md") else rel_path


def main():
    md_files = []
    for dirpath, _, filenames in os.walk(REPO_ROOT):
        # 跳过工具/图输出自身与 .git
        if "/.git" in dirpath or dirpath.endswith("/tools") or dirpath.endswith("/graph"):
            continue
        for fn in filenames:
            if fn.endswith(".md"):
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, REPO_ROOT)
                md_files.append((rel, full))
    md_files.sort()

    # 建立 id -> (title, tags, rel) 索引，支持歧义解析
    id_index = {}
    for rel, full in md_files:
        fid = file_id(rel)
        id_index[fid.lower()] = fid

    def resolve_target(raw):
        # 去别名/锚点，归一
        target = raw.split("|")[0].split("#")[0].strip()
        target = target.strip("./")
        if not target:
            return None
        key = target.lower()
        if key in id_index:
            return id_index[key]
        # 模糊匹配：id 以 /target 结尾 或 == target
        for k, v in id_index.items():
            base = v.split("/")[-1].lower()
            if base == key or k.endswith("/" + key):
                return v
        return None

    nodes = {}
    edges = []
    edge_keys = set()
    missing = []
    seen_titles = {}

    # 第一遍：建立全部节点（含标题/标签），避免边引用尚未创建的节点
    for rel, full in md_files:
        fid = file_id(rel)
        with open(full, encoding="utf-8") as f:
            text = f.read()
        fm, body = parse_frontmatter(text)
        title = extract_title(fm, body, os.path.basename(rel)[:-3])
        if title in seen_titles:
            title = f"{title}（{fid}）"
        seen_titles[title] = fid
        nodes[fid] = {
            "id": fid,
            "title": title,
            "tags": fm.get("tags", []),
            "degree": 0,
        }

    # 第二遍：抽取 wikilink 边
    for rel, full in md_files:
        fid = file_id(rel)
        with open(full, encoding="utf-8") as f:
            text = f.read()
        _, body = parse_frontmatter(text)
        for wl in WIKILINK_RE.findall(body):
            tgt = resolve_target(wl)
            if tgt is None:
                missing.append({"from": fid, "raw": wl.split("|")[0].split("#")[0].strip()})
                continue
            if tgt == fid:
                continue  # 自链跳过
            ek = (fid, tgt)
            if ek in edge_keys:
                continue
            edge_keys.add(ek)
            edges.append({"source": fid, "target": tgt})
            nodes[fid]["degree"] += 1
            nodes[tgt]["degree"] += 1

    # 孤立页（无任何边）
    orphans = [n["id"] for n in nodes.values() if n["degree"] == 0]

    graph = {
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "orphan_count": len(orphans),
            "missing_link_count": len(missing),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
        "orphans": orphans,
        "missing": missing,
    }

    os.makedirs(GRAPH_DIR, exist_ok=True)
    with open(os.path.join(GRAPH_DIR, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    write_html(graph)
    print(f"节点 {len(nodes)} | 边 {len(edges)} | 孤立页 {len(orphans)} | 断链 {len(missing)}")
    if missing:
        print("断链清单：")
        for m in missing:
            print(f"  {m['from']}  ->  [[{m['raw']}]]")
    print(f"输出：{GRAPH_DIR}/graph.json  +  {GRAPH_DIR}/index.html")


def write_html(graph):
    data = json.dumps(graph, ensure_ascii=False)
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>SEO 知识库 · 关系图谱</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.30.2/dist/cytoscape.min.js"></script>
<style>
  html,body{margin:0;height:100%;font-family:-apple-system,Segoe UI,Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:#0f1115;color:#e6e6e6}
  #bar{position:fixed;top:0;left:0;right:0;height:48px;display:flex;align-items:center;gap:12px;padding:0 16px;background:#171a21;border-bottom:1px solid #2a2f3a;z-index:10}
  #bar input{background:#0f1115;border:1px solid #2a2f3a;color:#e6e6e6;padding:6px 10px;border-radius:6px;width:280px;font-size:13px}
  #bar .stat{font-size:12px;color:#8b93a1}
  #cy{position:absolute;top:48px;left:0;right:0;bottom:0}
  .hint{font-size:12px;color:#8b93a1}
</style>
</head>
<body>
<div id="bar">
  <strong>SEO 知识库关系图谱</strong>
  <input id="search" placeholder="搜索节点（标题/路径）…"/>
  <span class="stat" id="stat"></span>
  <span class="hint">滚轮缩放 · 拖拽平移 · 单击高亮邻居</span>
</div>
<div id="cy"></div>
<script>
const DATA = __DATA__;
const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: (function(){
    const els = [];
    DATA.nodes.forEach(n=>els.push({data:{id:n.id, label:n.title, tags:n.tags.join(','), deg:n.degree}}));
    DATA.edges.forEach(e=>els.push({data:{id:e.source+'->'+e.target, source:e.source, target:e.target}}));
    return els;
  })(),
  style:[
    {selector:'node', style:{
      'label':'data(label)', 'color':'#cfd6e0', 'font-size':10, 'text-valign':'bottom', 'text-margin-y':4,
      'width':(n)=>8+Math.min(n.data('deg'),20), 'height':(n)=>8+Math.min(n.data('deg'),20),
      'background-color':'#4f8cff', 'text-wrap':'wrap', 'text-max-width':'120px', 'text-outline-color':'#0f1115', 'text-outline-width':2
    }},
    {selector:'edge', style:{'width':1,'line-color':'#39414f','curve-style':'bezier','opacity':0.7}},
    {selector:'node.hl', style:{'background-color':'#ffcc4f','border-width':2,'border-color':'#fff'}},
    {selector:'node.dim', style:{'opacity':0.15}},
    {selector:'edge.hl', style:{'line-color':'#ffcc4f','width':2.5,'opacity':1}},
    {selector:'edge.dim', style:{'opacity':0.05}}
  ],
  layout:{name:'cose', animate:false, padding:40, nodeRepulsion:12000, idealEdgeLength:90, gravity:0.3}
});
document.getElementById('stat').textContent =
  `节点 ${DATA.stats.node_count} · 边 ${DATA.stats.edge_count} · 孤立 ${DATA.stats.orphan_count} · 断链 ${DATA.stats.missing_link_count}`;
const search = document.getElementById('search');
search.addEventListener('input', ()=>{
  const q = search.value.trim().toLowerCase();
  if(!q){ cy.elements().removeClass('hl dim'); return; }
  const hit = cy.nodes().filter(n=> n.data('label').toLowerCase().includes(q) || n.id().toLowerCase().includes(q));
  const nb = hit.closedNeighborhood();
  cy.elements().addClass('dim');
  hit.removeClass('dim').addClass('hl');
  nb.removeClass('dim');
  nb.edges().addClass('hl');
});
cy.on('tap','node',(e)=>{
  const n=e.target; const nb=n.closedNeighborhood();
  cy.elements().addClass('dim');
  nb.removeClass('dim');
  n.removeClass('dim').addClass('hl');
  nb.edges().addClass('hl');
});
cy.on('tap',(e)=>{ if(e.target===cy){ cy.elements().removeClass('hl dim'); }});
</script>
</body>
</html>
"""
    html = html.replace("__DATA__", data)
    with open(os.path.join(GRAPH_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
