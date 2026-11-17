#!/usr/bin/env python3
"""Run 2301 targeted Ankr verifications (read-only), retry-tolerant.
Pulsekeep first-mint (age deep-dive), Hivefacai sold-out count, Crack VAULT first/count."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
LATEST = 132039757

def logs(ca, fb, tb, topics=None, tries=3):
    out, tok, pages = [], None, 0
    while True:
        p = {"blockchain": "bsc", "address": [ca], "fromBlock": hex(fb), "toBlock": hex(tb),
             "pageSize": 1000, "decodeLogs": False}
        if topics: p["topics"] = topics
        if tok: p["pageToken"] = tok
        body = None
        for a in range(tries):
            try:
                body = ankr_post("ankr_getLogs", p, timeout=30); break
            except Exception as e:
                print(f"  retry {a+1}/{tries} {ca[:10]} {fb}-{tb}: {type(e).__name__}", flush=True)
                time.sleep(3)
        if body is None: raise RuntimeError(f"ankr_getLogs failed {ca} {fb}-{tb}")
        r = body.get("result", {})
        out.extend(r.get("logs", []))
        tok = r.get("nextPageToken")
        pages += 1
        if not tok or pages >= 10: break
        time.sleep(1.0)
    return out

res = {}
# Pulsekeep: walk back from window start in expanding ranges; first range with logs bounds the first mint.
pk_first = None
for fb, tb in [(131719353,131719402),(131718403,131719352),(131709403,131718402),(131699403,131709402)]:
    ls = logs("0x65c89bD01A03B9B9B73eD29d3B3aF8D2eb034DFc", fb, tb, [TRANSFER, ZERO])
    print(f"PULSEKEEP {fb}-{tb}: {len(ls)} mints", flush=True)
    if ls:
        pk_first = int(ls[0]["blockNumber"], 16)
        res["pulsekeep_first_mint_block"] = pk_first
        res["pulsekeep_first_mint_range"] = [fb, tb]
        break
    res.setdefault("pulsekeep_empty_ranges", []).append([fb, tb])
if pk_first is None:
    res["pulsekeep_first_mint_block"] = "earlier than 131699403 (not bounded this run)"
print("PULSEKEEP first mint block:", pk_first, flush=True)
# Hivefacai: count mints in 2 chunks (address-filtered, ~700 total)
hf = logs("0xd337F2cb906CD5c571eDF4a28DbE66a2447A6281", 131632091, 131850000, [TRANSFER, ZERO])
hf += logs("0xd337F2cb906CD5c571eDF4a28DbE66a2447A6281", 131850001, LATEST, [TRANSFER, ZERO])
res["hivefacai_mints"] = len(hf)
res["hivefacai_first_block"] = int(hf[0]["blockNumber"], 16) if hf else None
res["hivefacai_last_block"] = int(hf[-1]["blockNumber"], 16) if hf else None
print("HIVEFACAI mints:", len(hf), "first:", res["hivefacai_first_block"], "last:", res["hivefacai_last_block"], flush=True)
# Crack VAULT: first mint + count
cv = logs("0x8ed2139be8ac9598e513959ed8922fab1781122f", 131000000, LATEST, [TRANSFER, ZERO])
res["crackvault_mints"] = len(cv)
res["crackvault_first_block"] = int(cv[0]["blockNumber"], 16) if cv else None
print("CRACKVAULT mints:", len(cv), "first:", res["crackvault_first_block"], flush=True)
json.dump(res, open("run-2026-11-06-2301-targeted-ankr.json", "w"), indent=1)
print("DONE", flush=True)
