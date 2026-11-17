#!/usr/bin/env python3
"""Kicks first-mint + metaURI/tokenURI probe, run 2026-11-14 05:31 WIB.
Read-only; writes run-2026-11-14-0531-kicks-firstmint.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x5726100e0D9ACB20cFB13e80e0fe42DF146730A8"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=120):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

# 1) metaURI + tokenURI(1)
calls = [
 {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
  "params": [{"to": ADDR, "data": "0x" + sel("metaURI()")}, "latest"]},
 {"jsonrpc": "2.0", "id": 2, "method": "eth_call",
  "params": [{"to": ADDR, "data": "0x" + sel("tokenURI(uint256)") + format(1, "064x")}, "latest"]},
]
meta_uri = token_uri = None
for ep in EPS:
    try:
        res = post_rpc(ep, calls, timeout=120)
        if isinstance(res, list) and len(res) == 2 and all(isinstance(r, dict) and "result" in r for r in res):
            meta_uri, token_uri = res[0]["result"], res[1]["result"]; print("views via", ep, flush=True); break
    except Exception as e:
        print("views ep", ep, "exc", str(e)[:80], flush=True)

# 2) first mint: Transfer from zero, chunked 1000-block ranges, newest-first search from 133426358 down to 133415000
ZERO = "0x0000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def get_logs(ep, frm, to):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                           "topics": [TRANSFER, "0x000000000000000000000000" + ZERO[2:]]}]}
    return post_rpc(ep, payload, timeout=120)

first_block = None; first_tx = None; scanned = []
hi = 133426358
for lo in range(hi - 999, 133414999, -1000):
    got = None
    for ep in EPS:
        try:
            res = get_logs(ep, lo, min(lo + 999, hi))
            if isinstance(res, dict) and "result" in res:
                got = res["result"]; break
            print(f"logs {lo}-{min(lo+999,hi)} ep {ep} err {str(res)[:80]}", flush=True)
        except Exception as e:
            print(f"logs {lo}-{min(lo+999,hi)} ep {ep} exc {str(e)[:80]}", flush=True)
    scanned.append((lo, min(lo + 999, hi), None if got is None else len(got)))
    print(f"chunk {lo}-{min(lo+999,hi)}: {None if got is None else len(got)} logs ({time.time()-t0:.0f}s)", flush=True)
    if got:
        first = min(got, key=lambda l: int(l["blockNumber"], 16))
        first_block = int(first["blockNumber"], 16); first_tx = first["transactionHash"]
        break
    if lo <= 133415000: break

# 3) block timestamp of first mint
ts = None
if first_block is not None:
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(first_block), False]}, timeout=120)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                ts = int(res["result"]["timestamp"], 16); break
        except Exception: continue

out = {"started_wib": "2026-11-14T05:31+07:00", "metaURI_raw": meta_uri, "tokenURI_1_raw": token_uri,
       "first_mint_block": first_block, "first_mint_tx": first_tx, "first_mint_ts": ts,
       "scanned_chunks": scanned, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0531-kicks-firstmint.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("metaURI_raw", "tokenURI_1_raw")}, indent=1))
print("metaURI_raw:", (meta_uri or "")[:200])
print("tokenURI_1_raw:", (token_uri or "")[:200])
