#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将《你无法真正理解没做过的事情》md 转换为 chiyolyn.github.io 风格的 HTML 文章页。"""
import re, html

SRC = "~/Documents/chiyo-blog/Dive Club 第 176 期：设计 Claude Code（以及接下来会发生什么）/你无法真正理解没做过的事情.md"
DST = "~/Documents/code/chiyolyn.github.io/posts/designing-claude-code.html"

lines = open(SRC, encoding="utf-8").read().split("\n")

def esc(t):
    return html.escape(t, quote=False)

def inline(t):
    """已转义文本上的行内处理：**加粗**、裸 URL 链接化"""
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\((#[^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"(https?://[^\s<）)】\"']+)",
               r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    return t

body = []          # article html
toc_jilu = []      # (id, title) 记录部分
toc_yiwen = []     # (id, title) 译文部分
sec_n = 0
t_n = 0
para = []

def flush_para():
    global para
    if not para:
        return
    joined = "<br>\n".join(para)
    # 翻译/编校署名行
    if para[0].startswith("翻译："):
        body.append(f'<p class="note">{joined}</p>')
    else:
        body.append(f"<p>{joined}</p>")
    para = []

i = 1  # 跳过第 1 行标题
while i < len(lines):
    raw = lines[i]
    line = raw.rstrip()
    s = line.strip()

    if not s:
        flush_para()
        i += 1
        continue

    if s.startswith("标题：") or s.startswith("用在首页的摘要："):
        i += 1
        continue

    # 话题标签行（按 md 里的位置渲染为小灰字）
    if s.startswith("#ClaudeCode"):
        flush_para()
        body.append(f'<p class="note">{esc(s)}</p>')
        i += 1
        continue

    # 一级标题：译文部分分隔
    if s == "# 播客逐字稿 译文":
        flush_para()
        body.append('<h2 id="transcript" style="margin-top:2.8em">播客逐字稿 · 译文</h2>')
        i += 1
        continue

    # 二级标题（记录部分）
    m = re.match(r"^##\s+(.+)$", s)
    if m:
        flush_para()
        sec_n += 1
        sid = f"sec-{sec_n}"
        title = m.group(1)
        toc_jilu.append((sid, title))
        body.append(f'<h2 id="{sid}">{esc(inline(title)) if False else inline(esc(title))}</h2>')
        i += 1
        continue

    # 三级标题（译文小节，带时间戳）
    m = re.match(r"^###\s+\[(\d\d:\d\d:\d\d)\]\s+(.+)$", s)
    if m:
        flush_para()
        t_n += 1
        tid = f"t-{t_n}"
        toc_yiwen.append((tid, m.group(2)))
        body.append(
            f'<h3 id="{tid}"><span class="time">[{m.group(1)}]</span> {inline(esc(m.group(2)))}</h3>'
        )
        i += 1
        continue

    # 分隔线
    if re.match(r"^-{3,}$", s):
        flush_para()
        if body:  # 文章开头的分隔线不产生额外空隙
            body.append('<div class="vspace"></div>')
        i += 1
        continue

    # Obsidian 图片
    if s.startswith("![["):
        flush_para()
        body.append(
            '<figure class="photo"><img src="../images/clawd-terminal.png" alt="Claude Code 终端里的 Clawd" loading="lazy"></figure>'
        )
        i += 1
        continue

    # blockquote
    if s.startswith(">"):
        flush_para()
        qlines = []
        while i < len(lines) and lines[i].strip().startswith(">"):
            qlines.append(inline(esc(re.sub(r"^\s*>\s?", "", lines[i].strip()))))
            i += 1
        body.append("<blockquote>" + "<br>\n".join(qlines) + "</blockquote>")
        continue

    # <small> 注释（可能跨行，保留内部 <br>）
    if s.startswith("<small>"):
        flush_para()
        buf = [s]
        while "</small>" not in buf[-1] and i + 1 < len(lines):
            i += 1
            buf.append(lines[i].strip())
        inner = " ".join(buf)
        inner = re.sub(r"</?small>", "", inner)
        inner = esc(inner).replace("&lt;br&gt;", "<br>")
        inner = inline(inner)
        body.append(f'<p class="note">{inner}</p>')
        i += 1
        continue

    para.append(inline(esc(s)))
    i += 1

flush_para()
article_html = "\n    ".join(body)

def toc_links(items):
    return "\n".join(
        f'    <a href="#{i}">{t}</a>' for i, t in items
    )

toc_html = f"""<nav class="toc" id="toc">
  <div class="toc-group">记录</div>
{toc_links(toc_jilu)}
  <div class="toc-group" style="margin-top:16px"><a href="#transcript">译文</a></div>
{toc_links(toc_yiwen)}
</nav>"""

page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>你无法真正理解没做过的事情 · Chiyo</title>
<meta name="keywords" content="Claude Code, Clawd, Artifacts, Claude Tag, 设计师, Meaghan Choi">
<meta name="description" content="读 Meaghan Choi 播客（Dive Club 第 176 期：设计 Claude Code）：记录与全文译文。">
<style>
  :root {
    --bg: #f8fafc;
    --text: #1e293b;
    --muted: #64748b;
    --faint: #94a3b8;
    --accent: #0e7490;
    --border: #e2e8f0;
  }
  * { box-sizing: border-box; }
  html { font-size: 14px; scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
      "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    line-height: 1.9;
    -webkit-font-smoothing: antialiased;
  }

  .wrap { max-width: 640px; margin: 0 auto; padding: 48px 24px 96px; }

  .topbar { font-size: 0.85rem; margin-bottom: 48px; }
  .topbar a { color: var(--muted); text-decoration: none; transition: color .15s; }
  .topbar a:hover { color: var(--accent); }

  .post-header h1 {
    margin: 0 0 6px;
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.4;
  }
  .post-header .subtitle { font-size: 0.85rem; color: var(--muted); margin-bottom: 6px; }
  .post-header .date {
    font-size: 0.78rem; color: var(--faint);
    font-variant-numeric: tabular-nums; letter-spacing: 0.04em;
  }
  .post-header .tags {
    margin-top: 10px;
    font-size: 0.78rem;
    color: var(--faint);
    letter-spacing: 0.02em;
  }

  /* 右侧大纲：仅宽屏显示 */
  .toc {
    position: fixed;
    top: 120px;
    left: calc(50% + 352px);
    width: 200px;
    font-size: 0.84rem;
    line-height: 1.55;
    max-height: calc(100vh - 160px);
    overflow-y: auto;
  }
  .toc .toc-group {
    font-size: 0.84rem;
    letter-spacing: 0.12em;
    color: var(--faint);
    margin-bottom: 6px;
  }
  .toc .toc-group a {
    color: inherit;
    text-decoration: none;
    transition: color .15s;
  }
  .toc .toc-group a:hover { color: var(--accent); }
  .toc a {
    display: block;
    color: var(--faint);
    text-decoration: none;
    padding: 3px 0 3px 10px;
    border-left: 2px solid var(--border);
    margin: 1px 0;
    transition: color .15s, border-color .15s;
  }
  .toc a:hover { color: var(--accent); }
  .toc a.active { color: var(--accent); border-left-color: var(--accent); }
  @media (max-width: 1180px) { .toc { display: none; } }

  article { margin-top: 40px; font-size: 0.95rem; }
  article p { margin: 1.1em 0; }
  article h2 { margin: 2.6em 0 0.6em; font-size: 1.08rem; font-weight: 700; }
  article h3 { margin: 2.4em 0 0.6em; font-size: 1.0rem; font-weight: 700; }
  article h3 .time {
    color: var(--faint);
    font-weight: 400;
    font-size: 0.82em;
    font-variant-numeric: tabular-nums;
    margin-right: 2px;
  }
  article a {
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid var(--border);
    word-break: break-all;
  }
  article a:hover { border-bottom-color: var(--accent); }
  blockquote {
    margin: 1.4em 0;
    padding: 2px 0 2px 16px;
    border-left: 3px solid var(--border);
    color: var(--muted);
    font-size: 0.9rem;
  }
  figure.photo { margin: 1.6em 0; }
  figure.photo img {
    max-width: 100%;
    border-radius: 6px;
    border: 1px solid var(--border);
  }
  .vspace { height: 1.5em; }
  .note {
    color: var(--faint);
    font-size: 0.82rem;
    line-height: 1.7;
  }
  .copyright {
    margin: 64px 0 0;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    color: var(--faint);
    font-size: 0.75rem;
  }
  .copyright a {
    color: inherit;
    text-decoration: none;
    border-bottom: 1px solid var(--border);
  }
  .copyright a:hover { color: var(--accent); border-bottom-color: var(--accent); }
</style>
</head>
<body>
__TOC__
<div class="wrap">

  <div class="topbar"><a href="../index.html">← 首页</a></div>

  <header class="post-header">
    <h1>你无法真正理解没做过的事情</h1>
    <div class="date">2026-08-22</div>
  </header>

  <article>
    __ARTICLE__
  </article>

  <p class="copyright">© 2026 <a href="https://github.com/chiyolyn" target="_blank" rel="noopener">Chiyo</a> · 本文采用 CC BY-NC-ND 4.0 许可，转载请注明出处</p>

</div>

<script>
(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (!links.length) return;
  var map = links.map(function (a) {
    var el = document.getElementById(a.getAttribute('href').slice(1));
    return { a: a, el: el };
  }).filter(function (x) { return x.el; });
  function onScroll() {
    var current = null;
    for (var i = 0; i < map.length; i++) {
      if (map[i].el.getBoundingClientRect().top <= 120) current = map[i];
      else break;
    }
    links.forEach(function (a) { a.classList.remove('active'); });
    if (current) current.a.classList.add('active');
  }
  document.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
</script>
</body>
</html>
"""

page = page.replace("__TOC__", toc_html).replace("__ARTICLE__", article_html)
open(DST, "w", encoding="utf-8").write(page)
print("written:", DST)
print("toc 记录:", len(toc_jilu), "译文:", len(toc_yiwen))
