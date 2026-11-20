#!/usr/bin/env python3
"""Analyze run 1031 reread vs snapshot (velocity, free%, slot, sold-out) + classify Boltbook addrs."""
import json, re
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
rr = json.load(open(f"{HF}/run-2026-11-18-1031-reread.json"))
reads = rr["reads"]
BLOCK = rr["block"]
PREV_BLOCK = 134236491
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min, calls {rr['n_calls']}, errs {rr['errors']}")

addr2key = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        addr2key[v["address"].lower()] = k

# velocity: compare totalSupply/totalMinted vs snapshot stored value
for name, d in reads.items():
    v = d["views"]
    key = name if name in snap.get("contracts", {}) else addr2key.get(d["address"].lower())
    sv = v.get("totalSupply")
    if sv is None:
        sv = v.get("totalMinted")
        view = "totalMinted"
    else:
        view = "totalSupply"
    prev = None
    if key and isinstance(snap["contracts"].get(key), dict):
        prev = snap["contracts"][key].get("totalSupply") if view == "totalSupply" else snap["contracts"][key].get("totalMinted")
        if prev is None:
            prev = snap["contracts"][key].get("totalMinted") if view == "totalSupply" else snap["contracts"][key].get("totalSupply")
    if prev is None or sv is None or not isinstance(sv, int) or not isinstance(prev, int):
        print(f"{name}: {view}={sv} prev={prev} (no baseline / non-int) key={key}")
        continue
    minted = sv - prev
    rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0
    prev_rate = None
    if key:
        prev_rate = snap["contracts"][key].get("currentRatePerMin")
    ratio = (rate / prev_rate) if prev_rate else None
    vel = (ratio is not None and ratio >= 1.5 and minted >= 20)
    # free% where readable
    free_note = ""
    for fv, cap in (("freeClaimed", None), ("freeMinted", None)):
        pass
    print(f"{name}: {view} {prev}->{sv} (+{minted}, {rate:.3f}/mnt, prev_rate={prev_rate}, ratio={ratio if ratio is None else round(ratio,2)}x) VEL={'PASS' if vel else 'fail'} key={key}")

# free% summary for key free-view contracts
print("--- free views ---")
for name in ["Bubblebruin", "AgentBubble", "Lumenhold", "Matrix", "AGCLUB", "STOCK AGENT", "PunchCard", "CAT402", "DRAGON", "ADRAW", "JADE", "THYRK"]:
    if name in reads:
        print(name, reads[name]["views"])
print("--- bsccat ---")
print(rr["bsccat"]["views"])
print("--- pepe ---")
print(rr["pepe"])
print("--- binanceai / RigForge ---")
for n in ["binanceai-mint", "RigForge"]:
    print(n, reads.get(n, {}).get("views"))
print("--- ARKT-claim ---")
print(reads.get("ARKT-claim-62a7", {}).get("views"))

# Boltbook classification
print("--- boltbook addrs vs snapshot ---")
run = json.load(open(f"{HF}/run-2026-11-18-1031.json"))
html_en = open(f"{HF}/run-2026-11-18-1031-boltbook-en.html").read()
for a in run["boltbook_en"]["addresses"]:
    k = addr2key.get(a.lower())
    # context: strip tags around address
    idx = html_en.lower().find(a.lower())
    ctx = ""
    if idx >= 0:
        seg = re.sub(r"<[^>]+>", " ", html_en[max(0, idx-600):idx+100])
        ctx = " ".join(seg.split())[:220]
    print(f"{a} snapshot_key={k} ctx={ctx}")
