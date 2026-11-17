#!/usr/bin/env python3
"""Leg 2 Boltbook run 2001: fetch front pages (already saved), deep-read every
front-page post EN+ZH, extract addresses, compare vs snapshot/scan-seen/hot-leg-seen.
Read-only. No preview/mint/claim."""
import json, os, re, subprocess, sys, html

BASE = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
TAG = "2001"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ADDR = re.compile(r"0x[0-9a-fA-F]{40}")
POSTLINK = re.compile(r'href="/p/([A-Za-z0-9_-]+)\?lang=(en|zh)"')
AUTHORLINK = re.compile(r'href="/u/([A-Za-z0-9_.-]+)\?lang=')

def fetch(url, out):
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return "cached"
    r = subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", out,
                        "-w", "%{http_code}", "--max-time", "45", url],
                       capture_output=True, text=True)
    return r.stdout.strip()

def strip_tags(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()

def post_title(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S | re.I)
    return html.unescape(m.group(1)).strip() if m else ""

def post_meta(h):
    # author handle + time hints from visible text
    txt = strip_tags(h)
    m = re.search(r"([A-Za-z0-9_.-]+\.ai)\b", txt)
    author = m.group(1) if m else ""
    return author, txt

en = open(f"{BASE}/boltbook-2026-11-07-2001-en.html", encoding="utf-8", errors="replace").read()
zh = open(f"{BASE}/boltbook-2026-11-07-2001-zh.html", encoding="utf-8", errors="replace").read()
posts_en = dict(POSTLINK.findall(en))
posts_zh = dict(POSTLINK.findall(zh))
print(f"front EN posts: {len(posts_en)}  ZH posts: {len(posts_zh)}")
print(f"EN ids: {sorted(posts_en)}")
print(f"ZH ids: {sorted(posts_zh)}")
print(f"ZH-only ids: {sorted(set(posts_zh) - set(posts_en))}")
print(f"EN-only ids: {sorted(set(posts_en) - set(posts_zh))}")

all_ids = sorted(set(posts_en) | set(posts_zh))
posts = {}
for pid in all_ids:
    out = f"{BASE}/boltbook-2026-11-07-2001-post-{pid}.html"
    code = fetch(f"https://boltbook.fun/p/{pid}?lang=en", out)
    h = open(out, encoding="utf-8", errors="replace").read() if os.path.exists(out) else ""
    addrs = sorted(set(a for a in ADDR.findall(h)))
    author, txt = post_meta(h)
    posts[pid] = {
        "title": post_title(h),
        "file": os.path.basename(out),
        "http": code,
        "size": len(h),
        "author": author,
        "in_en": pid in posts_en,
        "in_zh": pid in posts_zh,
        "addresses": addrs,
        "text_snippet": txt[:600],
    }
    print(f"post {pid} http={code} size={len(h)} author={author} addrs={len(addrs)} title={post_title(h)[:90]}")

# author pages: authors of posts with addresses or free-mint keywords
authors = sorted({p["author"] for p in posts.values() if p["author"]})
print("authors found:", authors)
author_pages = {}
for a in authors:
    handle = a.replace(".ai", "")
    out = f"{BASE}/boltbook-2026-11-07-2001-author-{handle}.html"
    code = fetch(f"https://boltbook.fun/u/{handle}?lang=en", out)
    h = open(out, encoding="utf-8", errors="replace").read() if os.path.exists(out) else ""
    addrs = sorted(set(x for x in ADDR.findall(h)))
    author_pages[a] = {"file": os.path.basename(out), "http": code,
                       "size": len(h), "addresses": addrs}
    print(f"author {a} http={code} size={len(h)} addrs={len(addrs)}")

# address comparison
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))["contracts"]
snap_addrs = {v.get("address", "").lower(): k for k, v in snap.items()
              if isinstance(v, dict) and v.get("address")}
scan_seen = json.load(open(f"{BASE}/onchain-scan-seen.json")).get("contracts", {})
scan_seen_l = {k.lower(): v for k, v in scan_seen.items()}
hot = json.load(open(f"{BASE}/hot-leg-seen.json"))
hot_l = {k.lower(): v for k, v in hot.items()}

all_addrs = {}
for pid, p in posts.items():
    for a in p["addresses"]:
        all_addrs.setdefault(a, {"posts": [], "authors": set()})
        all_addrs[a]["posts"].append(pid)
for a, info in author_pages.items():
    for x in info["addresses"]:
        all_addrs.setdefault(x, {"posts": [], "authors": set()})
        all_addrs[x]["authors"].add(a)

addresses = {}
n_snap = n_scan = n_hot = n_new = 0
for a in sorted(all_addrs, key=str.lower):
    al = a.lower()
    if al in snap_addrs:
        st, n_snap = f"SNAPSHOT:{snap_addrs[al]}", n_snap + 1
    elif al in scan_seen_l:
        st, n_scan = f"SEEN first-seen-block {scan_seen_l[al]}", n_scan + 1
    elif al in hot_l:
        st, n_hot = f"HOT-LEG-SEEN {json.dumps(hot_l[al])[:220]}", n_hot + 1
    else:
        st, n_new = "NEW (not snapshot/seen/hot-leg)", n_new + 1
    addresses[a] = {"status": st, "note": "",
                    "posts": all_addrs[a]["posts"],
                    "author_pages": sorted(all_addrs[a]["authors"])}

out = {
    "run": "2001", "date_wib": "2026-11-07 20:01 WIB",
    "front_en": {"url": "https://boltbook.fun/?lang=en", "bytes": len(en)},
    "front_zh": {"url": "https://boltbook.fun/?lang=zh", "bytes": len(zh)},
    "posts_read": len(posts),
    "author_pages_read": sorted(author_pages.keys()),
    "total_unique_addresses": len(addresses),
    "breakdown": {"snapshot": n_snap, "scan_seen": n_scan, "hot_leg_seen": n_hot, "new": n_new},
    "posts": posts,
    "author_pages": author_pages,
    "addresses": addresses,
}
json.dump(out, open(f"{BASE}/boltbook-2026-11-07-2001-posts.json", "w"), indent=1, ensure_ascii=False)
print(f"TOTAL posts={len(posts)} authors={len(author_pages)} addrs={len(addresses)} "
      f"snap={n_snap} scan={n_scan} hot={n_hot} NEW={n_new}")
for a, v in addresses.items():
    if v["status"].startswith("NEW"):
        print("NEW:", a, "posts:", v["posts"], "author_pages:", v["author_pages"])
