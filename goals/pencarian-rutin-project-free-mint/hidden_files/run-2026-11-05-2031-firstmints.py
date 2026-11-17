#!/usr/bin/env python3
"""Subagent B run 2031 first-mint checks (read-only, Ankr getLogs as module):
Galaxy Agents + the two AGI sale contracts. Plus receipt check of the
poster's Galaxy mint tx."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def block_ts(n):
    body = json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber", "params": [hex(n), False], "id": 1}).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as r:
                j = json.load(r)
            if j.get('result'): return int(j['result']['timestamp'], 16)
        except Exception:
            pass
    return None
def first_mint(addr, from_block):
    logs = []; page = None; calls = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(from_block), "toBlock": "latest",
                  "address": addr.lower(), "topics": [TRANSFER, ZERO], "pageSize": 1000}
        if page: params["pageToken"] = page
        body = ankr_post("ankr_getLogs", params, timeout=30); calls += 1
        res = body.get('result', {}) if isinstance(body, dict) else {}
        ls = res.get('logs', []) or []
        logs.extend(ls)
        page = res.get('nextPageToken')
        if not page or calls >= 10: break
    if not logs: return None, 0, calls, 0, None
    blocks = sorted(int(l['blockNumber'], 16) for l in logs)
    minters = len({l['topics'][2] for l in logs if len(l.get('topics', [])) > 2})
    return blocks[0], len(logs), calls, minters, blocks[-1]
out = {}
for label, addr, fb in [
    ("GalaxyAgents", "0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4", 131815000),
    ("AGI-4731", "0x4731f2816290168f6b894D4c391527fFB767ffB9", 131815000),
    ("AGI-bC8b", "0xbC8b1b791C81EC97024632Ac05ED27a71F5392Aa", 131815000),
]:
    try:
        b, n, calls, minters, lastb = first_mint(addr, fb)
        ts = block_ts(b) if b else None
        print(f"{label}: firstBlock={b} logsInRange={n} minters={minters} lastBlock={lastb} ankrCalls={calls} ts={ts}", flush=True)
        out[label] = {'firstBlock': b, 'logsInRange': n, 'minters': minters, 'lastBlock': lastb, 'ankrCalls': calls, 'firstMintTs': ts, 'fromBlock': fb}
    except Exception as e:
        print(f"{label}: ERROR {e}", flush=True)
        out[label] = {'error': str(e)}
# receipt of poster's Galaxy mint tx
tx = "0xe10e2510745f5fa0759022333cc2d80ec641cc881a42b462a97999474ae9b064"
for ep in EPS:
    try:
        body = json.dumps({"jsonrpc": "2.0", "method": "eth_getTransactionReceipt", "params": [tx], "id": 1}).encode()
        req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"}, method='POST')
        with urllib.request.urlopen(req, timeout=10) as r:
            j = json.load(r)
        rec = j.get('result')
        if rec:
            out["galaxy_poster_tx_receipt"] = {"blockNumber": int(rec["blockNumber"], 16), "status": rec.get("status"),
                "to": rec.get("to"), "from": rec.get("from"), "gasUsed": int(rec.get("gasUsed", "0x0"), 16),
                "logs": len(rec.get("logs", []))}
            print("poster tx receipt:", json.dumps(out["galaxy_poster_tx_receipt"]), flush=True)
            break
    except Exception as e:
        print("receipt err", ep, e, flush=True)
json.dump(out, open("run-2026-11-05-2031-firstmints.json", "w"), indent=1)
print("saved run-2026-11-05-2031-firstmints.json")
