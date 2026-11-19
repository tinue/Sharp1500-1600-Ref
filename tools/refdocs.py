"""Shared helpers for the tools in this folder (standard library only)."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NON_TOPIC = {"tools", "skills", "sources", "node_modules"}
STATUSES = ("draft", "cited", "ROM-verified", "emulator-verified")
HEADER_KEYS = ("Summary", "Scope", "Sources", "Status")

def topics():
    """Topic folders: every top-level folder except tools/skills/sources and hidden ones."""
    out = []
    for n in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, n)
        if os.path.isdir(p) and n not in NON_TOPIC and not n.startswith("."):
            out.append(n)
    return out

def docs(topic):
    """Reference documents of a topic, as repo-relative paths (README.md excluded, subfolders included)."""
    res = []
    base = os.path.join(ROOT, topic)
    for dp, _, fs in os.walk(base):
        for f in sorted(fs):
            if f.endswith(".md") and f != "README.md":
                res.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
    return sorted(res)

def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf8") as f:
        return f.read()

def header(text):
    """(title, {Summary, Scope, Sources, Status}) from the first lines of a document."""
    lines = text.split("\n")
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else ""
    h = {}
    for ln in lines[1:14]:
        m = re.match(r"^(Summary|Scope|Sources|Status):\s*(.*)$", ln)
        if m:
            h[m.group(1)] = m.group(2).strip()
    return title, h

def machines(scope):
    a, b = "PC-1500" in scope, "PC-1600" in scope
    return "1500+1600" if a and b else ("1600" if b else "1500")

def kb(rel):
    return max(1, round(os.path.getsize(os.path.join(ROOT, rel)) / 1024))
