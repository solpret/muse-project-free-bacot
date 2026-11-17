#!/usr/bin/env python3
"""Run 64 detail-2: creation receipts via fast_rpc.batch + per-token sample buy
verification (pair Transfer + token0/token1). Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

TOKS = ["0x7526782e635c2f4f9d63a7d4736194158d937777",
        "0x3e612ed93b07239efc7db9da05ff07b7ad6f7777",
        "0x455e2e30de81c25ec7788d6c08431dbfc2b77777",
        "0x729a625d9649bbe2802d2cbb4d4ba6c1bb477777"]
sent = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-sent.json"))
paid = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-paid.json"))

# 1) creation receipts via batch
cre = []
for w, rr in sent["results"].items():
    if not rr.get("ok"): continue
    for t in rr["in_window"]:
        if t["input_prefix"] == "0x60806040":
            cre.append((w, t))
print("creation txs:", len(cre), flush=True)
receipts = {}
for j in range(0, len(cre), 6):
    chunk = cre[j:j+6]
    try:
        res = fast_rpc.batch([("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk])
    except Exception as e:
        print(f"batch {j} ERROR {e}; race fallback", flush=True)
        res = []
        for _, t in chunk:
            try: res.append(fast_rpc.race("eth_getTransactionReceipt", [t["hash"]]))
            except Exception: res.append(None)
    if not isinstance(res, list) or len(res) != len(chunk):
        res = (res if isinstance(res, list) else []) + [None] * len(chunk)
        res = res[:len(chunk)]
    for (w, t), r in zip(chunk, res):
        receipts[t["hash"]] = r
    time.sleep(4.0)
created = []
for w, t in cre:
    r = receipts.get(t["hash"])
    ca = (r or {}).get("contractAddress")
    st = (r or {}).get("status")
    created.append({"hash": t["hash"], "wallet": w, "contract": ca, "status": st,
                    "time_wib": t["time_wib"], "value": t["value"], "block": t["block"]})
json.dump(created, open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-created.json", "w"), indent=1)
n_ok = sum(1 for c in created if c["contract"])
n_s1 = sum(1 for c in created if c["status"] == "0x1")
n_null = sum(1 for c in created if not c["contract"] and c["status"] is None)
print(f"CREATED done: {len(created)} txs, {n_ok} addresses read, {n_s1} status1, {n_null} unreadable", flush=True)
for c in created:
    mark = " <-- IS TOP4 ASI" if (c["contract"] or "").lower() in [x.lower() for x in TOKS] else ""
    if mark or not c["contract"]:
        print(f"  {c['hash'][:14]} {c['wallet'][:10]} {c['contract']} {c['time_wib']}{mark}", flush=True)
print("ASI deployed in-window:", [c["contract"] for c in created if (c["contract"] or "").lower() in [x.lower() for x in TOKS]], flush=True)
print("distinct deployer wallets:", len(set(c["wallet"] for c in created)), flush=True)
import collections
print("creations per wallet:", dict(collections.Counter(c["wallet"][:10] for c in created)), flush=True)

# 2) per-token sample buy verification
T_TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
def call(to, data):
    for _ in range(3):
        try: return fast_rpc.race("eth_call", [{"to": to, "data": data}, "latest"])
        except Exception as e:
            print("call retry", e, flush=True); time.sleep(3)
    return None
BUY = "0xb6f9de95"
for tok in TOKS:
    ws = paid[tok]
    sample = None
    for w in ws:
        rr = sent["results"].get(w)
        if not rr or not rr.get("ok"): continue
        for t in rr["in_window"]:
            if t["input_prefix"] == BUY:
                sample = (w, t); break
        if sample: break
    r = fast_rpc.race("eth_getTransactionReceipt", [sample[1]["hash"]])
    pair = None; amt = None
    for lg in r.get("logs") or []:
        if (lg.get("address") or "").lower() == tok.lower() and (lg.get("topics") or [None])[0] == T_TRANSFER:
            pair = "0x" + lg["topics"][1][-40:]
            amt = int(lg["data"], 16)
            print(f"SAMPLE {tok[:10]} tx={sample[1]['hash'][:14]} wallet={sample[0][:10]} time={sample[1]['time_wib']} value={sample[1]['value']} pair={pair} amount_raw={amt}", flush=True)
            break
    if pair:
        for fn in ["token0()", "token1()"]:
            rr2 = call(pair, sel(fn))
            print(f"  pair {fn} {('0x'+rr2[-40:]) if rr2 else None}", flush=True)
    else:
        print(f"SAMPLE {tok[:10]} NO pair Transfer of token in first buy tx {sample[1]['hash'][:14]}", flush=True)
print("DONE", flush=True)
