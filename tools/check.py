#!/usr/bin/env python3
"""Validate the repository: headers, links, sizes, generated files, private paths.

    python3 tools/check.py

Exit code 1 if anything is an error. Size above 25 KB is only a warning (reference tables may exceed it).
"""
import os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from refdocs import *
import index, importlib
bp = importlib.import_module("build-prompts")

WARN_KB, MAX_KB = 25, 50
GENERATED = {"Programming/prompts/LH5801-Assembly-Prompt.md"}  # paste-ready: no header, it would pollute the prompt
EXEMPT_SIZE = {"CPU/LH5801-Instruction-Set.md", "Programming/prompts/LH5801-Assembly-Prompt.md"}
LINK = re.compile(r"\]\(([^)\s]+)\)")
PRIVATE = re.compile(r"~/(Development|SynologyDrive)|/Users/")
errors, warns = [], []

def err(m): errors.append(m)

all_md = []
for dp, dn, fs in os.walk(ROOT):
    dn[:] = [d for d in dn if not d.startswith(".") and d != "node_modules"]
    for f in fs:
        if f.endswith(".md"):
            all_md.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))

for t in topics():
    if not os.path.exists(os.path.join(ROOT, t, "README.md")):
        err(f"{t}/: no README.md")
    for f in docs(t):
        if f in GENERATED: continue
        title, h = header(read(f))
        for k in HEADER_KEYS:
            if k not in h: err(f"{f}: header line '{k}:' missing")
        if h.get("Status") and h["Status"] not in STATUSES:
            err(f"{f}: Status '{h['Status']}' not in {STATUSES}")
        size = kb(f)
        if size > MAX_KB and f not in EXEMPT_SIZE: err(f"{f}: {size} KB > {MAX_KB} KB, split it")
        elif size > WARN_KB and f not in EXEMPT_SIZE: warns.append(f"{f}: {size} KB > {WARN_KB} KB")

for f in all_md:
    text = read(f)
    fence = False
    for n, ln in enumerate(text.split("\n"), 1):
        if ln.lstrip().startswith(("```", "~~~")): fence = not fence
        if fence: continue
        for m in LINK.finditer(ln):
            tgt = m.group(1).split("#")[0]
            if not tgt or re.match(r"^[a-z]+:", tgt): continue
            p = os.path.normpath(os.path.join(os.path.dirname(os.path.join(ROOT, f)), tgt))
            if not os.path.exists(p): err(f"{f}:{n}: broken link {m.group(1)}")
        if PRIVATE.search(ln) and not f.startswith("sources/evidence"):
            err(f"{f}:{n}: private path in a public document: {ln.strip()[:80]}")

if index.__dict__["render"] and any(
        (open(os.path.join(ROOT, r), encoding="utf8").read() if os.path.exists(os.path.join(ROOT, r)) else None) != t
        for r, t in index.render().items()):
    err("INDEX.md or a topic README table is stale: run tools/index.py")
if open(os.path.join(ROOT, bp.OUT), encoding="utf8").read() != bp.build():
    err(f"{bp.OUT} is stale: run tools/build-prompts.py")

ev = os.path.join(ROOT, "skills", "sharp-pc1500-1600", "evals.md")
if os.path.exists(ev):
    for m in re.finditer(r"`([A-Za-z0-9_./-]+\.md)`", open(ev, encoding="utf8").read()):
        if not os.path.exists(os.path.join(ROOT, m.group(1))) and "/" in m.group(1):
            err(f"skills/sharp-pc1500-1600/evals.md: {m.group(1)} does not exist")

for w in warns: print("warning:", w)
for e in errors: print("error:", e)
print(f"{len(all_md)} Markdown files, {len(errors)} errors, {len(warns)} warnings")
sys.exit(1 if errors else 0)
