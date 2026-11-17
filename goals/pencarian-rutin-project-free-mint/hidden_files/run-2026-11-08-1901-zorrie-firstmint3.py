#!/usr/bin/env python3
"""Zorrie first-mint bounded search, run 1901. Read-only.
Scans [132360000, 132375000] in 1000-block chunks via Ankr, collects ALL
Zorrie mint blocks, writes them + earliest block + timestamp (dataseed)."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
A = "0x47feee72353358a61618cE640265F9f406f88E47"
LO, HI = 132360000, 132375000
found = []
frm = HI - 999
while frm >= LO:
    to_b = min(frm + 999, HI)
    try:
        logs, _ = scan.ankr_logs(frm, to_b, [scan.TRANSFER, scan.ZERO_TOPIC])
    except Exception as e:
        print(f"chunk {frm}-{to_b} ERROR {e}", flush=True); break
    mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
    for l in mine:
        found.append({"block": int(l["blockNumber"], 16), "tx": l.get("transactionHash"), "tokenId": int(l["topics"][3], 16) if len(l.get("topics", [])) >= 4 else None})
    print(f"chunk {frm}-{to_b}: {len(logs)} logs, {len(mine)} zorrie mints (total {len(found)})", flush=True)
    frm -= 1000
found.sort(key=lambda x: x["block"])
print("ALL zorrie mints in range:", json.dumps(found))
earliest = found[0]["block"] if found else None
ts_wib = None
if earliest:
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(earliest), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                ts_wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                break
        except Exception:
            continue
    print("earliest block:", earliest, "->", ts_wib)
json.dump({"mints": found, "first_mint_block": earliest, "first_mint_wib": ts_wib, "range": [LO, HI]},
          open(BASE + "/run-2026-11-08-1901-zorrie-firstmint.json", "w"), indent=1)
print("DONE")
