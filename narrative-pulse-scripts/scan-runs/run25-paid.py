#!/usr/bin/env python3
"""Read-only paid-trend parse run22: re-fetch receipts for non-approve in-window txs,
collect Transfer logs to tracked wallets (from != zero) -> token -> wallets. No mint/sign."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
HOME = Path.home()
sent = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run25-sent.json"))
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0"*24 + w[2:] for w in uniq}
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
APPROVE = sel("approve(address,uint256)")
cands = []
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if t["input_prefix"] == APPROVE: continue
        cands.append((w, t))
print(f"candidates={len(cands)}", flush=True)
tok2wallets = {}
nulls = 0
for j in range(0, len(cands), 6):
    chunk = cands[j:j+6]
    try:
        res = fast_rpc.batch([("eth_getTransactionReceipt", [t["hash"]]) for _, t in chunk])
    except Exception as e:
        print(f"batch {j} ERROR {e}; race fallback", flush=True)
        res = []
        for _, t in chunk:
            try: res.append(fast_rpc.race("eth_getTransactionReceipt", [t["hash"]]))
            except Exception: res.append(None)
    for (w, t), r in zip(chunk, res if isinstance(res, list) else []):
        if r is None: nulls += 1; continue
        for lg in r.get("logs") or []:
            topics = lg.get("topics") or []
            if len(topics) >= 3 and topics[0] == T_TRANSFER and topics[2] in tracked_padded:
                tok = (lg.get("address") or "").lower()
                tok2wallets.setdefault(tok, set()).add("0x" + topics[2][-40:])
    if (j+6) % 60 == 0: print(f"  {j+6}/{len(cands)} tokens={len(tok2wallets)} nulls={nulls}", flush=True)
    time.sleep(4.0)
out = {k: sorted(v) for k, v in tok2wallets.items()}
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run25-paid.json", "w"), indent=1)
mx = max((len(v) for v in out.values()), default=0)
print(f"PAID DONE tokens={len(out)} max_wallets_per_token={mx} null_receipts={nulls}", flush=True)
for k, v in sorted(out.items(), key=lambda kv: -len(kv[1]))[:15]:
    print(f"  {k} wallets={len(v)} {v}", flush=True)
