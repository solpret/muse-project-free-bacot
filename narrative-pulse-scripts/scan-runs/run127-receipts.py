#!/usr/bin/env python3
"""Read-only run 127 receipts + paid derivation (single fetch).
Candidates: all non-approve in-window txs from run127-sent.json.
fast_rpc.batch (6, ~4s pause) with race fallback per tx, same mint-log parse
as prior runs (Transfer/TransferSingle/TransferBatch from zero address to a
tracked wallet). Paid map derived from the same receipts: Transfer (any
from != zero) to a tracked wallet -> token -> wallets. No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc

HOME = Path.home()
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
APPROVE = sel("approve(address,uint256)")
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
T_BATCH = topic("TransferBatch(address,address,address,uint256[],uint256[])")
ZERO_PAD = "0x" + "0" * 64

sent = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run127-sent.json"))
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}

cands, seen = [], set()
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        if t["hash"] in seen:
            continue
        seen.add(t["hash"])
        if t["input_prefix"] == APPROVE:
            continue
        cands.append((w, t))
print(f"receipt candidates={len(cands)} (non-approve, deduped by hash) max_block={sent['max_block']}", flush=True)
PARTIAL = HOME / "workspace/narrative-pulse/scan-runs/run127-receipts-partial.json"
receipts = {}
if PARTIAL.exists():
    try:
        receipts = json.load(open(PARTIAL))
        print(f"resuming from partial: {len(receipts)} receipts already fetched", flush=True)
    except Exception as e:
        print(f"partial load failed ({e}); starting fresh", flush=True)
        receipts = {}
cands_all = list(cands)
cands = [(w, t) for (w, t) in cands if t["hash"] not in receipts]
print(f"candidates remaining after resume: {len(cands)}", flush=True)
for j in range(0, len(cands), 6):
    chunk = cands[j:j+6]
    try:
        res = fast_rpc.batch([("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk])
    except Exception as e:
        print(f"batch {j} ERROR {e}; race fallback", flush=True)
        res = []
        for _, t in chunk:
            try:
                res.append(fast_rpc.race("eth_getTransactionReceipt", [t["hash"]]))
            except Exception as e2:
                res.append(None)
                print(f"  race {t['hash'][:12]} ERROR {e2}", flush=True)
    if not isinstance(res, list) or len(res) != len(chunk):
        res = (res if isinstance(res, list) else []) + [None] * len(chunk)
        res = res[:len(chunk)]
    for (w, t), r in zip(chunk, res):
        receipts[t["hash"]] = r
    if (j + 6) % 60 == 0:
        print(f"  {j+6}/{len(cands)}", flush=True)
        json.dump(receipts, open(PARTIAL, "w"))
    time.sleep(4.0)
json.dump(receipts, open(PARTIAL, "w"))
cands = cands_all

parsed, paid = {}, {}
for w, t in cands:
    r = receipts.get(t["hash"])
    if r is None:
        parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                             "value": t["value"], "time_wib": t["time_wib"], "status": "receipt_null"}
        continue
    logs = r.get("logs") or []
    mint_logs = []
    for lg in logs:
        topics = lg.get("topics") or []
        if not topics:
            continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[2], "data": lg.get("data")})
            # zero-from transfers are mints, not paid receives; skip paid map
        elif topics[0] in (T_SINGLE, T_BATCH) and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
            mint_logs.append({"contract": lg.get("address"), "to_topic": topics[3], "data": lg.get("data"), "batch": True})
        elif topics[0] == T_TRANSFER and len(topics) >= 3 and topics[2] in tracked_padded:
            tok = (lg.get("address") or "").lower()
            paid.setdefault(tok, set()).add("0x" + topics[2][-40:])
    parsed[t["hash"]] = {"wallet": w, "to": t["to"], "selector": t["input_prefix"],
                         "value": t["value"], "time_wib": t["time_wib"],
                         "receipt_status": r.get("status"), "n_logs": len(logs), "mint_logs": mint_logs}
json.dump(parsed, open(HOME / "workspace/narrative-pulse/scan-runs/run127-receipts.json", "w"), indent=1)
paid_out = {k: sorted(v) for k, v in paid.items()}
json.dump(paid_out, open(HOME / "workspace/narrative-pulse/scan-runs/run127-paid.json", "w"), indent=1)
n_mint = sum(1 for v in parsed.values() if v.get("mint_logs"))
n_null = sum(1 for v in parsed.values() if v.get("status") == "receipt_null")
n_s1 = sum(1 for v in parsed.values() if v.get("receipt_status") == "0x1")
n_s0 = sum(1 for v in parsed.values() if v.get("receipt_status") == "0x0")
print(f"RECEIPTS DONE total={len(parsed)} with_mint_logs={n_mint} null={n_null} status1={n_s1} status0={n_s0} paid_tokens={len(paid_out)}", flush=True)
for h, v in parsed.items():
    if v.get("mint_logs"):
        print(f"MINT {h} wallet={v['wallet'][:10]} to={v['to']} sel={v['selector']} val={v['value']} time={v['time_wib']} logs={v['mint_logs']}", flush=True)
mx = max((len(v) for v in paid_out.values()), default=0)
print(f"PAID max_wallets_per_token={mx}", flush=True)
for k, v in sorted(paid_out.items(), key=lambda kv: -len(kv[1]))[:20]:
    print(f"  {k} wallets={len(v)}", flush=True)
