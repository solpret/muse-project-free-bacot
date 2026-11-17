#!/usr/bin/env python3
"""Run 64 detail-3: per-token sample buy verification for the 3 remaining ASI
tokens (find a buy tx whose receipt carries a Transfer of THAT token from a
PCS pair, then verify pair token0/token1). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
T_TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
TOKS = ["0x7526782e635c2f4f9d63a7d4736194158d937777",
        "0x3e612ed93b07239efc7db9da05ff07b7ad6f7777",
        "0x455e2e30de81c25ec7788d6c08431dbfc2b77777"]
sent = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-sent.json"))
paid = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-paid.json"))
BUY = "0xb6f9de95"

def call(to, data):
    for _ in range(3):
        try: return fast_rpc.race("eth_call", [{"to": to, "data": data}, "latest"])
        except Exception as e:
            print("call retry", e, flush=True); time.sleep(3)
    return None

for tok in TOKS:
    ws = paid[tok]
    cands = []
    for w in ws:
        rr = sent["results"].get(w)
        if not rr or not rr.get("ok"): continue
        for t in rr["in_window"]:
            if t["input_prefix"] == BUY:
                cands.append((w, t))
        if len(cands) >= 40: break
    found = None
    for j in range(0, len(cands), 6):
        chunk = cands[j:j+6]
        try:
            res = fast_rpc.batch([("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk])
        except Exception:
            res = [None] * len(chunk)
        for (w, t), r in zip(chunk, res):
            if not r: continue
            for lg in r.get("logs") or []:
                if (lg.get("address") or "").lower() == tok.lower() and (lg.get("topics") or [None])[0] == T_TRANSFER:
                    pair = "0x" + lg["topics"][1][-40:]
                    amt = int(lg["data"], 16)
                    found = (w, t, pair, amt)
                    break
            if found: break
        if found: break
        time.sleep(2.0)
    if found:
        w, t, pair, amt = found
        print(f"SAMPLE {tok[:10]} tx={t['hash'][:14]} wallet={w[:10]} time={t['time_wib']} value={t['value']} pair={pair} amount_raw={amt}", flush=True)
        for fn in ["token0()", "token1()"]:
            rr2 = call(pair, sel(fn))
            print(f"  pair {fn} {('0x'+rr2[-40:]) if rr2 else None}", flush=True)
    else:
        print(f"SAMPLE {tok[:10]} NOT FOUND in {len(cands)} sampled buy txs", flush=True)
print("DONE", flush=True)
