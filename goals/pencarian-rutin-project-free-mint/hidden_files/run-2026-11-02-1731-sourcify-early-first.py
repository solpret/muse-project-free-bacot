#!/usr/bin/env python3
"""Main run 2026-11-02 17:31 WIB: first-mint walk (Ankr getLogs) for 8 agent-shaped first-seen contracts."""
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def first_mints(C, head, frm=131150000):
    logs = []; tok = None; pages = 0; err = None
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(head), "pageSize": 1000, "decodeLogs": False,
                  "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x" + "00" * 32], "address": C}
        if tok: params["pageToken"] = tok
        try: body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err = str(e)[:200]; break
        res = body.get("result", {}) if isinstance(body, dict) else {}
        got = [l for l in res.get("logs", []) if l.get("address", "").lower() == C.lower()]
        logs.extend(got); tok = res.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
        time.sleep(1)
    out = {"count": len(logs), "err": err, "pages": pages}
    if logs:
        blks = sorted(int(l["blockNumber"], 16) for l in logs)
        minters = set(l.get("topics", [])[2] for l in logs if len(l.get("topics", [])) >= 3)
        out.update({"first_block": blks[0], "last_block": blks[-1], "distinct_minters": len(minters)})
        for ep in EPS:
            try:
                b = _single(ep, "eth_getBlockByNumber", [hex(blks[0]), False], 8, retries=0); ts = int(b["timestamp"], 16)
                out["first_ts"] = ts; out["first_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"); break
            except Exception: pass
    return out
head = blk(); print("head", head)
TARGETS = {
 "MachineMuse": "0xED05274F0Fc42c53Fe2f02558f1afB5BeAd55A8d",
 "CopilotClub": "0x4EA51956dd8F4B3C04ffF36e0254Be1b04c051aF",
 "DelegateDAO": "0x9a1339B8Aaee25082e3e54aE09780905add63462",
}
out = {"head": head}
for name, C in TARGETS.items():
    r = first_mints(C, head); out[name] = r; print(name, json.dumps(r))
json.dump(out, open(BASE + "run-2026-11-02-1731-sourcify-early-first.json", "w"), indent=1)
