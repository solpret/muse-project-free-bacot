#!/usr/bin/env python3
"""Decode recent BOBBIE mint tx calldata — READ-ONLY. Run 1931."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BOBBIE = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 64
RPC = "https://bsc-dataseed.binance.org"

def rpc_call(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

head = rpc_call("eth_blockNumber", [])
head_n = int(head["result"], 16)
print("head", head_n)
frm = head_n - 2000
logs = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
                 "toBlock": hex(head_n), "address": BOBBIE.lower(),
                 "topics": [TRANSFER, ZERO]}, timeout=60)
print("logs raw keys:", list(logs.keys()) if isinstance(logs, dict) else type(logs))
res = logs.get("result", {}) if isinstance(logs, dict) else {}
entries = res.get("logs", []) if isinstance(res, dict) else []
print("mint logs in window:", len(entries))
txs = []
seen = set()
for e in entries:
    h = e.get("transactionHash")
    if h and h not in seen:
        seen.add(h); txs.append(h)
print("distinct mint txs:", len(txs))
for h in txs[-5:]:
    tx = rpc_call("eth_getTransactionByHash", [h])
    t = tx.get("result") or {}
    inp = t.get("input", "")
    print("TX", h, "from", t.get("from"), "value", t.get("value"), "input_len", len(inp))
    if inp and len(inp) > 10:
        print("  selector:", inp[:10])
        # decode mint(uint8,uint256,address,uint256,bytes): qty(32) quotedFree(32) referrer(32) deadline(32) offset(32) len(32) bytes...
        try:
            body = inp[10:]
            words = [body[i:i+64] for i in range(0, len(body), 64)]
            qty = int(words[0], 16) if len(words) > 0 else None
            qfree = int(words[1], 16) if len(words) > 1 else None
            ref = "0x" + words[2][-40:] if len(words) > 2 else None
            deadline = int(words[3], 16) if len(words) > 3 else None
            off = int(words[4], 16) if len(words) > 4 else None
            vlen = int(words[5], 16) if len(words) > 5 else None
            print(f"  qty={qty} quotedFree={qfree} referrer={ref} voucherDeadline={deadline} voucherOffset={off} voucherLen={vlen}")
        except Exception as ex:
            print("  decode EXC", ex)
json.dump({"head": head_n, "txs": txs}, open("run-2026-11-07-1931-bobbie-minttxs.json", "w"), indent=1)
