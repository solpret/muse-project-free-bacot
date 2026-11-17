#!/usr/bin/env python3
"""Retry for free-mint-search run 2026-11-12 17:31 WIB: the 8 targets that
BATCH-FAILed in verify.py (batches too big: LEAN+FINDING_EXTRA ~45 calls).
Lean view sets (~17 calls) + contractURI string reads.
Read-only; writes run-2026-11-12-1731-retry.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception: continue
    return None
def raw_string(addr, sig):
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if not r or r == "0x": return None
            b = bytes.fromhex(r[2:])
            if len(b) >= 64:
                off = int.from_bytes(b[:32], "big"); ln = int.from_bytes(b[32:64], "big")
                if 0 < ln < 20000 and off + 32 + ln <= len(b):
                    return b[32 + off:32 + off + ln].decode("utf-8", errors="replace")
            return b.decode("utf-8", errors="replace").strip("\x00")
        except Exception: continue
    return None
def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
        "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
        "mintedBy(address)", "freeMintedBy(address)", "freeLeft()", "freeRemaining()",
        "paidMinted()", "mintStart()", "saleStart()", "START_TIME()", "startTime()",
        "mintOpensAt()", "FREE_MAX()", "freeSupply()", "agentFreeUsed()", "totalFreeMinted()",
        "owner()", "MAX_PER_WALLET()", "price()"]
TARGETS = [
    ("OLIVER AGENTS", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("Cobalt Agent", "0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0"),
    ("NAPPER", "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("SYNERGYPASS", "0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e"),
    ("DRAGON-0xad0d", "0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998"),
    ("AGENT COSMOS", "0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69"),
    ("AGENT ID card", "0x486d0947caa3d70c19e38f6c789489d39291e9e7"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
]
block = get_block()
res = {"started_wib": "2026-11-12 17:31 WIB", "block": block, "reads": {}}
for name, addr in TARGETS:
    r = raw_batch(addr, LEAN)
    e = {"address": addr, "views": r}
    if r:
        e["summary"] = {k: v for k, v in r.items() if v is not None}
    e["contractURI"] = raw_string(addr, "contractURI()")
    res["reads"][name] = e
    print(name, e.get("summary", "BATCH-FAIL"), "URI:", str(e.get("contractURI"))[:100] if e.get("contractURI") else None, flush=True)
res["elapsed_s"] = round(time.time() - t0, 1)
json.dump(res, open(BASE + "run-2026-11-12-1731-retry.json", "w"), indent=1)
print("BLOCK", block, "ELAPSED", res["elapsed_s"])
