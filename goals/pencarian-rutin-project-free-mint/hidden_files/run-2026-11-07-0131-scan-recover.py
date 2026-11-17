#!/usr/bin/env python3
"""Recover the 45 unenriched scan contracts for run 0131. READ-ONLY.
Re-fetches window 132053652-132054651 (same as killed scan) via Ankr module,
Transfer + TransferSingle, chunk 50, no enrich here except listing.
Saves full contract lists; parent triage enriches only true first-seen.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
FROM, TO, CHUNK = 132058847, 132059846, 50
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TS_SINGLE = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO = "0x" + "00" * 32
def ankr_logs(fb, tb, topics):
    logs, tok, pages = [], None, 0
    while True:
        p = {"blockchain": "bsc", "fromBlock": hex(fb), "toBlock": hex(tb), "pageSize": 1000, "decodeLogs": False, "topics": topics}
        if tok: p["pageToken"] = tok
        body = ankr_post("ankr_getLogs", p, timeout=30)
        r = body.get("result", {})
        logs += r.get("logs", [])
        tok = r.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
    return logs, pages
erc721, erc1155, erc20 = {}, {}, {}
calls = 0; t0 = time.time(); errors = []
def add(store, addr, log):
    e = store.setdefault(addr, {"mint_count": 0, "minters": set(), "first_block": None, "last_block": None})
    e["mint_count"] += 1
    blk = int(log.get("blockNumber", "0x0"), 16)
    e["first_block"] = blk if e["first_block"] is None else min(e["first_block"], blk)
    e["last_block"] = blk if e["last_block"] is None else max(e["last_block"], blk)
    return e
cf = FROM
while cf <= TO:
    ct = min(cf + CHUNK - 1, TO)
    try:
        logs, _ = ankr_logs(cf, ct, [TRANSFER, ZERO]); calls += 1
    except Exception as e:
        errors.append(f"Transfer {cf}-{ct}: {e}"); print(f"ERROR Transfer {cf}-{ct}: {e}", flush=True); break
    for log in logs:
        topics = log.get("topics", []); addr = log.get("address", "")
        if len(topics) == 4:
            e = add(erc721, addr, log); e["minters"].add("0x" + topics[2][-40:])
        elif len(topics) == 3:
            e = add(erc20, addr, log); e["minters"].add("0x" + topics[2][-40:])
    time.sleep(2.2)
    try:
        ts_logs, _ = ankr_logs(cf, ct, [TS_SINGLE, None, ZERO]); calls += 1
    except Exception:
        try:
            ts_logs, _ = ankr_logs(cf, ct, [TS_SINGLE]); calls += 1
        except Exception as e:
            errors.append(f"TS {cf}-{ct}: {e}"); ts_logs = []
    for log in (ts_logs or []):
        topics = log.get("topics", [])
        if len(topics) >= 3 and topics[2].lower() == ZERO:
            e = add(erc1155, log.get("address", ""), log)
            e["minters"].add("0x" + topics[3][-40:] if len(topics) >= 4 else "?")
    time.sleep(2.2)
    print(f"chunk {cf}-{ct}: ERC721 {len(erc721)}, ERC1155 {len(erc1155)}, ERC20 {len(erc20)}", flush=True)
    cf = ct + 1
def dump(store):
    return [{"address": a, "mint_count": e["mint_count"], "distinct_minters": len(e["minters"]),
             "first_block": e["first_block"], "last_block": e["last_block"]}
            for a, e in sorted(store.items(), key=lambda kv: -kv[1]["mint_count"])]
out = {"from_block": FROM, "to_block": TO, "ankr_calls": calls, "errors": errors,
       "erc721": dump(erc721), "erc1155": dump(erc1155),
       "erc20_mint_contracts_list": dump(erc20), "elapsed_s": round(time.time()-t0, 1)}
json.dump(out, open(f"{BASE}/onchain-scan-2026-11-07-0131-recover.json", "w"), indent=1)
print(f"RECOVER DONE in {time.time()-t0:.1f}s calls={calls} erc721={len(erc721)} erc1155={len(erc1155)} erc20={len(erc20)} errors={errors}", flush=True)
