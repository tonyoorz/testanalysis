#!/usr/bin/env python3
"""wiki-lint: 断链 + 孤儿页扫描（tonystark vault）

- 断链: [[target]] 在 vault 中无对应 .md（含路径别名 | 与 #heading 剥离）
- 孤儿页: 20/30/40/50/60 层中既无入链也无出链的页面
  （Home/Index/Sources 清单不算孤儿豁免，正常计入入链来源）
"""
import os
import re
import sys
from collections import defaultdict

VAULT = os.path.join(os.path.dirname(__file__), "..", "..")
VAULT = os.path.realpath(VAULT)
LINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")

# 只把 wiki 维护层纳入孤儿判定；10 Sources 原文只判定断链来源
WIKI_LAYERS = ("20 Sessions", "30 Topics", "40 Tools", "50 Syntheses", "60 Knowledge")

pages = {}            # relpath (no .md) -> abs .md path
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in (".obsidian", ".git", ".zcode", ".claude", ".trash")]
    for f in files:
        if f.endswith(".md"):
            rel = os.path.relpath(os.path.join(root, f), VAULT)[:-3]
            pages[rel] = os.path.join(root, f)

by_basename = defaultdict(list)
for rel in pages:
    by_basename[os.path.basename(rel)].append(rel)

outlinks = defaultdict(set)   # src rel -> set(target rel)
inlinks = defaultdict(set)    # target rel -> set(src rel)
broken = []                   # (src, raw_target)

for rel, path in pages.items():
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"WARN read {rel}: {e}", file=sys.stderr)
        continue
    for m in LINK_RE.finditer(text):
        raw = m.group(1).strip()
        target = raw.split("|")[0].split("#")[0].strip()
        if not target:
            continue
        # embed 语法 ![[...]] 已被覆盖（target 相同）
        if target in pages:
            resolved = target
        elif target in by_basename and len(by_basename[target]) == 1:
            resolved = by_basename[target][0]
        elif target.endswith(".md") and target[:-3] in pages:
            resolved = target[:-3]
        else:
            broken.append((rel, raw))
            continue
        outlinks[rel].add(resolved)
        inlinks[resolved].add(rel)

orphans = [rel for rel in pages
           if rel.startswith(WIKI_LAYERS)
           and not inlinks[rel] and not outlinks[rel]]

print(f"== wiki-lint: {len(pages)} md pages ==")
print(f"BROKEN_LINKS: {len(broken)}")
for src, raw in sorted(broken):
    print(f"  {src} -> [[{raw}]]")
print(f"ORPHANS: {len(orphans)}")
for rel in sorted(orphans):
    print(f"  {rel}")
print(f"SUMMARY broken={len(broken)} orphans={len(orphans)}")
