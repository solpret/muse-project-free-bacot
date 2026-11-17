#!/usr/bin/env python3
"""Main run 2026-11-03 08:31 full re-read of non-minted snapshot contracts. Read-only.
Uses fast_rpc batch calls. A None result is a READ FAILURE, never zero: verified
snapshot values are only overwritten by successful (non-None) reads."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
VIEWS = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
         ("balanceOf(address)", enc_addr(USER)[2:])]
snap = json.load(open(BASE + "onchain-snapshot.json"))
targets = [(k, v["address"]) for k, v in snap["contracts"].items()
           if "minted" not in v.get("status", "") and v.get("address")]
calls, meta = [], []
for name, addr in targets:
    for vn, arg in VIEWS:
        calls.append((addr, sel(vn) + arg)); meta.append((name, vn))
print("targets", len(targets), "calls", len(calls), flush=True)
results = {}
CH = 180
for i in range(0, len(calls), CH):
    chunk = calls[i:i + CH]
    try:
        res = call_many(chunk)
    except Exception as e:
        print("batch chunk failed", i, type(e).__name__, str(e)[:120], flush=True)
        res = [None] * len(chunk)
    for (name, vn), r in zip(meta[i:i + CH], res):
        try: iv = int(r, 16) if r else None
        except Exception: iv = None
        results.setdefault(name, {})[vn] = iv
    print("chunk", i, "done", flush=True)
block = int(race("eth_blockNumber", []), 16)
out = {"block": block, "reads": results}
json.dump(out, open(BASE + "run-2026-11-03-0831-reread-all.json", "w"), indent=1)
print("block", block)
# Summarise changes vs snapshot (only successful reads)
for name, addr in targets:
    v = snap["contracts"][name]; r = results[name]
    ts, fc, fs = r["totalSupply()"], r["freeClaimed()"], r["FREE_SUPPLY()"]
    old_ts, old_fc = v.get("totalSupply"), v.get("freeClaimed")
    pct = round(fc / fs * 100, 2) if (fc is not None and fs) else v.get("freePctVerified")
    slot = "open" if (r["mintedBy(address)"] == 0 and r["freeUsed(address)"] == 0) else ("used?" if r["mintedBy(address)"] not in (None, 0) or r["freeUsed(address)"] not in (None, 0) else "unread")
    if ts != old_ts or fc != old_fc:
        print(f"CHANGE {name}: ts {old_ts}->{ts} fc {old_fc}->{fc} fs {fs} pct {pct} slot {slot} status {v.get('status')}")
    elif pct is not None and pct >= 25:
        print(f"NEAR+ {name}: ts {ts} fc {fc} fs {fs} pct {pct} slot {slot} status {v.get('status')}")
print("done")
