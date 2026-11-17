#!/usr/bin/env python3
"""Hot-leg 11:34 leg-3 follow-up: pool constants + names (fixed parse) + first-mint age via Ankr. Read-only, bounded ~75s."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
C1 = "0xc4695f19dE428EA37169bBD058463588D511554a"
C2 = "0x05debe4445232205ae7e79d02cb5de5aa0641eff"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
CUTOFF = 132080731  # ~48h before block 132138331
NOW_TS = 1794036900  # ~2026-11-07 11:35 WIB epoch approx (refined below via block ts)
t0 = time.time()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data, timeout=8):
    for ep in EPS:
        if time.time() - t0 > 70: return "deadline"
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
        except Exception: continue
    return None
def cint(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v in (None, "deadline"): return v
    try: return int(v, 16)
    except Exception: return v
def cstr(to, sig):
    v = call(to, sel(sig))
    if v in (None, "deadline") or not isinstance(v, str) or len(v) < 130: return v
    try:
        ln = int(v[66:130], 16)
        raw = bytes.fromhex(v[130:130 + ln * 2])
        return raw.decode("utf-8", "replace")
    except Exception: return v
def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            if isinstance(b, dict) and b.get("timestamp"): return int(b["timestamp"], 16)
        except Exception: continue
    return None
def wib(ts): return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts + 7 * 3600)) if ts else None
def logs_page(addr, fb, tb, page_token=None):
    p = {"blockchain": "bsc", "fromBlock": hex(fb), "toBlock": hex(tb), "address": addr,
         "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 100, "decodeLogs": False}
    if page_token: p["pageToken"] = page_token
    body = ankr_post("ankr_getLogs", p, timeout=30)
    r = body.get("result", {}) if isinstance(body, dict) else {}
    return r.get("logs", []), r.get("nextPageToken")
out = {}
out["c1"] = {"name": cstr(C1, "name()"), "symbol": cstr(C1, "symbol()"),
             "totalMints": cint(C1, "totalMints()"), "MAX_MINTS": cint(C1, "MAX_MINTS()"),
             "FREE_PER_WALLET": cint(C1, "FREE_PER_WALLET()"), "MAX_PER_WALLET": cint(C1, "MAX_PER_WALLET()"),
             "MINT_DEADLINE": cint(C1, "MINT_DEADLINE()"), "MINT_DURATION": cint(C1, "MINT_DURATION()"),
             "PRICE": cint(C1, "PRICE()"), "MINT_AMOUNT": cint(C1, "MINT_AMOUNT()"),
             "MAX_SUPPLY": cint(C1, "MAX_SUPPLY()"), "pair": None}
pv = cint(C1, "pair()")
out["c1"]["pair"] = ("0x" + format(pv, "040x")) if isinstance(pv, int) and pv else pv
out["c2"] = {"name": cstr(C2, "name()"), "symbol": cstr(C2, "symbol()")}
# Age: any mint before cutoff?
for label, addr in (("c1", C1), ("c2", C2)):
    d = {}
    try:
        logs, _ = logs_page(addr, 131000000, CUTOFF)
        d["pre_cutoff_mint_logs_page1"] = len(logs)
        d["pre_cutoff_earliest_block"] = int(logs[0]["blockNumber"], 16) if logs else None
    except Exception as e:
        d["pre_cutoff_error"] = f"{type(e).__name__}: {str(e)[:120]}"
    try:
        logs2, _ = logs_page(addr, CUTOFF + 1, 132138331)
        d["post_cutoff_mint_logs_page1"] = len(logs2)
        eb = int(logs2[0]["blockNumber"], 16) if logs2 else None
        d["first_mint_block_post_cutoff"] = eb
        if eb:
            ts = block_ts(eb)
            d["first_mint_ts"] = ts
            d["first_mint_wib"] = wib(ts)
    except Exception as e:
        d["post_cutoff_error"] = f"{type(e).__name__}: {str(e)[:120]}"
    out[label + "_age"] = d
out["cutoff_block_48h"] = CUTOFF
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-07-1134-verify2.json", "w"), indent=1)
print(json.dumps(out, indent=1))
