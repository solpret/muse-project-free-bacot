#!/usr/bin/env python3
"""First-mint verification WANGCAI + YUANBAO, run 2026-11-14 06:01 WIB.
eth_getLogs Transfer-from-zero, 100-block chunks, oldest-first, publicnode/dataseed.
Plus contractURI()/tokenURI(1) reads for gate method (H)/(I). Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDRS = {"WANGCAI": "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd",
         "YUANBAO": "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E"}
EPS = ["https://bsc-rpc.publicnode.com/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def get_logs(addr, frm, to):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": addr,
                           "topics": [TRANSFER, ZERO_TOPIC]}]}
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=60)
            if isinstance(res, dict) and "result" in res:
                return res["result"], ep
        except Exception:
            continue
    return None, None
def block_ts(blk):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(blk), False]}, timeout=60)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                return int(res["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
def call(addr, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": data}, "latest"]}
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=60)
            if isinstance(res, dict) and isinstance(res.get("result"), str) and res["result"] != "0x":
                return res["result"]
        except Exception:
            continue
    return None
out = {}
HEAD = 133438663
for name, addr in ADDRS.items():
    first_block = first_tx = None
    lo, hi = 133436000, HEAD
    chunks = [(a, min(a + 99, hi)) for a in range(lo, hi + 1, 100)]
    for a, b in chunks:
        logs, ep = get_logs(addr, a, b)
        print(f"{name} chunk {a}-{b}: {None if logs is None else len(logs)} logs ({time.time()-t0:.0f}s)", flush=True)
        if logs:
            f = min(logs, key=lambda l: int(l["blockNumber"], 16))
            first_block = int(f["blockNumber"], 16); first_tx = f["transactionHash"]
            break
    ts = block_ts(first_block) if first_block else None
    # gate pointers (H)/(I)
    curi = call(addr, sel("contractURI()"))
    turi = call(addr, sel("tokenURI(uint256)") + format(1, "064x"))
    out[name] = {"first_mint_block": first_block, "first_mint_tx": first_tx,
                 "first_mint_ts": ts, "contractURI_raw": (curi[:400] if curi else None),
                 "tokenURI1_raw": (turi[:600] if turi else None)}
    print(name, "=>", json.dumps(out[name], indent=1)[:900], flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-0601-firstmint.json", "w"), indent=1)
print("DONE", json.dumps(out, indent=1)[:1500])
