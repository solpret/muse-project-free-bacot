#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 00:29 WIB leg 4: focused read-only re-read of
priority snapshot items (curl transport, 25s/call, 8 workers).
Never writes snapshot/state/watermark. Writes run-2026-11-12-0029-reread.json.
"""
import json, time, subprocess, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-12-0029"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
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
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

# (name, address, views) — priority items only
ITEMS = [
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459",
     ["totalMinted()", "freeMinted()", "FREE_SUPPLY()", "freeAvailable()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)"]),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
     ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeAvailable()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)"]),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
     ["totalSupply()", "totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeAvailable()", "balanceOf(address)"]),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
     ["mintOpen()", "freeMinted()", "totalMinted()", "totalSupply()", "balanceOf(address)"]),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
     ["totalSupply()", "totalFreeCount()", "mintOpenedAt()", "balanceOf(address)", "freeUsed(address)"]),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("ORIGAMIX", "0x43CAb600E87B0F96e7a310049774797FC3DF5756",
     ["totalSupply()", "firstFreeUsed()", "paidMinted()", "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
    ("CAP7-Obrigado", "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
     ["totalSupply()", "freeMinted()", "sharesMinted()", "soldOut()", "phase()", "balanceOf(address)", "freeClaimed(address)"]),
    ("BotFighters", "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb",
     ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_CAP()", "balanceOf(address)"]),
    ("RIGFORGE", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
     ["freeSharesLeft()", "openedAt()", "freeClaimed()"]),
    ("BINANCEAI", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
     ["launched()"]),
]
# sold-out skips (already reported): AgentPals 300/300, NAOMI 777/777, S1-0x6C50 100/100

out = {"block": get_block(), "reread": {}, "started_wib": "2026-11-12 00:29 WIB",
       "skipped_reread_soldout": ["AgentPals 300/300", "NAOMI 777/777", "S1-0x6C50 100/100"]}
print("BLOCK", out["block"], flush=True)

def read_one(item):
    name, addr, views = item
    t = time.time()
    got = raw_batch(addr, views)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
        for v in views:
            d[v.split("(")[0] + ("_user" if "(address)" in v else "")] = None
    else:
        d.update(got)
    print(f"REREAD {name} ({time.time()-t:.1f}s): " +
          ", ".join(f"{k}={v}" for k, v in d.items() if k not in ("address", "_batch_fail")), flush=True)
    return name, d

with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_one, ITEMS):
        out["reread"][name] = d

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/run-{TS}-reread.json", "w"), indent=1)
print("REREAD DONE in", out["elapsed_s"], "s", flush=True)
