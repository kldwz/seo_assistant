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
        first = rel.split("/")[0]
        module = "(根)" if first.endswith(".md") else first
        nodes[fid] = {
            "id": fid,
            "title": title,
            "module": module,
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
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>SEO 知识库 · 关系图谱</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.30.2/dist/cytoscape.min.js"></script>
<style>
  :root{--bg:#0f1115;--panel:#171a21;--line:#2a2f3a;--txt:#e6e6e6;--mut:#8b93a1}
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;font-family:-apple-system,Segoe UI,Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--txt)}
  #bar{position:fixed;top:0;left:0;right:0;height:52px;display:flex;align-items:center;gap:14px;padding:0 16px;background:var(--panel);border-bottom:1px solid var(--line);z-index:20;flex-wrap:wrap}
  #bar strong{font-size:15px}
  #bar input{background:var(--bg);border:1px solid var(--line);color:var(--txt);padding:7px 11px;border-radius:7px;width:240px;font-size:13px}
  #bar .stat{font-size:12px;color:var(--mut)}
  #legend{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
  #legend .lg{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--mut);cursor:pointer;user-select:none;padding:2px 6px;border-radius:6px}
  #legend .lg:hover{background:#22262f}
  #legend .lg.off{opacity:.35;text-decoration:line-through}
  #legend .dot{width:11px;height:11px;border-radius:3px}
  #cy{position:absolute;top:52px;left:0;right:340px;bottom:0}
  #side{position:absolute;top:52px;right:0;width:340px;bottom:0;background:var(--panel);border-left:1px solid var(--line);padding:18px;overflow:auto}
  #side h2{font-size:16px;margin:0 0 6px}
  #side .mod{display:inline-block;font-size:11px;padding:2px 8px;border-radius:10px;color:#0f1115;font-weight:600;margin-bottom:10px}
  #side .tags{margin:8px 0;font-size:12px;color:var(--mut)}
  #side .tags span{display:inline-block;background:#22262f;border-radius:5px;padding:2px 7px;margin:2px 4px 2px 0}
  #side a{color:#4f8cff;text-decoration:none;font-size:13px}
  #side a:hover{text-decoration:underline}
  #side .sec{margin-top:16px;font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.5px}
  #side ul{margin:6px 0;padding-left:18px;font-size:13px;line-height:1.7}
  #side li a{color:#cfd6e0}
  #side .empty{color:var(--mut);font-size:13px;margin-top:30px;text-align:center}
  #hint{position:absolute;bottom:12px;left:12px;font-size:11px;color:var(--mut);background:rgba(23,26,33,.8);padding:6px 10px;border-radius:6px;z-index:5}
</style>
</head>
<body>
<div id="bar">
  <strong>SEO 知识库 · 关系图谱</strong>
  <input id="search" placeholder="搜索节点（标题/路径）…"/>
  <span class="stat" id="stat"></span>
  <span id="legend"></span>
</div>
<div id="cy"></div>
<div id="side"><div class="empty">单击任意节点<br/>查看详情与关联页面</div></div>
<div id="hint">滚轮缩放 · 拖拽平移 · 单击高亮邻居 · 点击图例筛选模块</div>
<script>
const DATA = __DATA__;
const MOD_COLORS = {
  "00-start-here":"#34d399","10-fundamentals":"#60a5fa","20-keyword":"#f472b6",
  "30-content":"#fbbf24","40-on-page":"#a78bfa","50-links":"#f87171","60-technical":"#22d3ee",
  "70-local":"#fb923c","80-ai-search":"#c084fc","90-saas-playbook":"#2dd4bf",
  "glossary":"#9ca3af","references":"#94a3b8","(根)":"#e5e7eb"
};
const MOD_LABELS = {
  "00-start-here":"入门","10-fundamentals":"基础","20-keyword":"关键词","30-content":"内容",
  "40-on-page":"页面SEO","50-links":"外链","60-technical":"技术SEO","70-local":"本地SEO",
  "80-ai-search":"AI搜索","90-saas-playbook":"SaaS实战","glossary":"术语表","references":"信源","(根)":"元文件"
};
const colorOf = m => MOD_COLORS[m] || "#9ca3af";
const cy = cytoscape({
  container: document.getElementById('cy'),
  elements: (function(){
    const els = [];
    DATA.nodes.forEach(n=>els.push({data:{id:n.id, label:n.title, module:n.module, tags:n.tags, deg:n.degree}}));
    DATA.edges.forEach(e=>els.push({data:{id:e.source+'->'+e.target, source:e.source, target:e.target}}));
    return els;
  })(),
  style:[
    {selector:'node', style:{
      'label':(n)=> n.data('deg')>=6 ? n.data('label') : '',
      'color':'#0f1115','font-size':11,'font-weight':600,'text-valign':'center',
      'width':(n)=>14+Math.min(n.data('deg')*2.2,34), 'height':(n)=>14+Math.min(n.data('deg')*2.2,34),
      'background-color':(n)=>colorOf(n.data('module')),
      'border-width':(n)=> n.data('deg')>=10?3:1, 'border-color':'#0f1115',
      'text-outline-color':'#ffffff','text-outline-width':0
    }},
    {selector:'node.hub', style:{'label':'data(label)'}},
    {selector:'node.hl', style:{'border-color':'#ffffff','border-width':3}},
    {selector:'node.dim', style:{'opacity':0.12}},
    {selector:'edge', style:{'width':1,'line-color':'#39414f','curve-style':'bezier','opacity':0.55}},
    {selector:'edge.hl', style:{'line-color':'#ffcc4f','width':2.4,'opacity':1}},
    {selector:'edge.dim', style:{'opacity':0.04}}
  ],
  layout:{name:'cose', animate:false, padding:50, nodeRepulsion:26000, idealEdgeLength:130, gravity:0.45, numIter:2500, componentSpacing:200}
});
document.getElementById('stat').textContent =
  `节点 ${DATA.stats.node_count} · 边 ${DATA.stats.edge_count} · 孤立 ${DATA.stats.orphan_count}`;
// 图例
const legend = document.getElementById('legend');
const mods = [...new Set(DATA.nodes.map(n=>n.module))].sort();
const offMods = new Set();
mods.forEach(m=>{
  const lg = document.createElement('span'); lg.className='lg';
  lg.innerHTML = `<span class="dot" style="background:${colorOf(m)}"></span>${MOD_LABELS[m]||m}`;
  lg.onclick = ()=>{
    if(offMods.has(m)){ offMods.delete(m); lg.classList.remove('off'); }
    else { offMods.add(m); lg.classList.add('off'); }
    cy.nodes().forEach(n=>{ n.style('display', offMods.has(n.data('module'))?'none':'element'); });
  };
  legend.appendChild(lg);
});
// 悬停显示标签
cy.on('mouseover','node',e=>{ if(e.target.data('deg')<6) e.target.style('label', e.target.data('label')); });
cy.on('mouseout','node',e=>{ if(e.target.data('deg')<6 && !e.target.hasClass('hl')) e.target.style('label',''); });
// 详情面板
function showDetail(n){
  const id = n.id();
  const title = n.data('label'), mod = n.data('module');
  const tags = (n.data('tags')||[]).map(t=>`<span>${t}</span>`).join('');
  const nb = n.neighborhood('node').filter(x=>x.id()!==id);
  const ins = n.incomers('edge').map(e=>e.source().data('label'));
  const outs = n.outgoers('edge').map(e=>e.target().data('label'));
  const gh = `https://github.com/kldwz/seo_assistant/blob/main/${id}.md`;
  const list = arr => arr.length ? `<ul>${arr.map(x=>`<li>${x}</li>`).join('')}</ul>` : '<div style="color:#8b93a1;font-size:12px">无</div>';
  document.getElementById('side').innerHTML =
    `<h2>${title}</h2>
     <span class="mod" style="background:${colorOf(mod)}">${MOD_LABELS[mod]||mod} · ${mod}</span>
     <div class="tags">${tags||'<span style="color:#8b93a1">无标签</span>'}</div>
     <a href="${gh}" target="_blank">在 GitHub 打开原文 →</a>
     <div class="sec">指向（本页链到）</div>${list(outs)}
     <div class="sec">被指向（谁链到本页）</div>${list(ins)}`;
}
const search = document.getElementById('search');
search.addEventListener('input', ()=>{
  const q = search.value.trim().toLowerCase();
  if(!q){ cy.elements().removeClass('hl dim'); document.getElementById('side').innerHTML='<div class="empty">单击任意节点<br/>查看详情与关联页面</div>'; return; }
  const hit = cy.nodes().filter(n=> n.data('label').toLowerCase().includes(q) || n.id().toLowerCase().includes(q));
  const nb = hit.closedNeighborhood();
  cy.elements().addClass('dim');
  hit.removeClass('dim');
  nb.removeClass('dim');
  nb.edges().addClass('hl');
});
cy.on('tap','node',e=>{
  const n=e.target; const nb=n.closedNeighborhood();
  cy.elements().addClass('dim');
  nb.removeClass('dim');
  n.removeClass('dim').addClass('hl');
  nb.edges().addClass('hl');
  showDetail(n);
});
cy.on('tap',e=>{ if(e.target===cy){ cy.elements().removeClass('hl dim'); document.getElementById('side').innerHTML='<div class="empty">单击任意节点<br/>查看详情与关联页面</div>'; }});
</script>
</body>
</html>
"""
    html = html.replace("__DATA__", data)
    with open(os.path.join(GRAPH_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
