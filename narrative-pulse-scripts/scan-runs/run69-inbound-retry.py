#!/usr/bin/env python3
"""Read-only retry of run-69 inbound a/b transient-failed contracts on the RUN-69
window (131886470-131896158). Same hit logic as run69-inbound.py.
Writes run69-inbound-retry.json (schema matches run69-inbound-{a,b}.json).
No preview/mint/sign/login."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import ankr as ankr_mod
def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
T_SINGLE = topic("TransferSingle(address,address,address,uint256,uint256)")
ZERO_PAD = "0x" + "0" * 64
HOME = Path.home()
D = HOME / "workspace/narrative-pulse/scan-runs"
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
FROM, TO = 131886470, 131896158
ia = json.load(open(D / "run69-inbound-a.json"))
ib = json.load(open(D / "run69-inbound-b.json"))
contracts = sorted({f["contract"].lower() for f in ia["failed"]} | {f["contract"].lower() for f in ib["failed"]})
print(f"retrying {len(contracts)} contracts on window {FROM}-{TO}", flush=True)
hits, failed, total_logs, truncated = [], [], 0, []
for i, c in enumerate(contracts):
    try:
        data = ankr_mod.get_logs(c, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        total_logs += len(logs)
        if len(logs) >= 1000:
            truncated.append(c)
            data2 = ankr_mod.get_logs(c, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
            logs = ((data2.get("result") or {}).get("logs") or [])
            print(f"  truncated {c}: topic-filtered logs={len(logs)}", flush=True)
        for lg in logs:
            topics = lg.get("topics") or []
            if not topics: continue
            if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
                hits.append({"contract": c, "kind": "ERC721/20 Transfer", "to": "0x" + topics[2][-40:],
                             "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
            elif topics[0] == T_SINGLE and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
                hits.append({"contract": c, "kind": "ERC1155 TransferSingle", "to": "0x" + topics[3][-40:],
                             "token_id": int(topics[4], 16) if len(topics) >= 5 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
        print(f"[{i+1}/{len(contracts)}] {c} OK logs={len(logs)}", flush=True)
    except Exception as e:
        failed.append({"contract": c, "error": str(e)[:200]})
        print(f"[{i+1}/{len(contracts)}] {c} ERROR {e}", flush=True)
    time.sleep(0.5)
print(f"RETRY DONE contracts={len(contracts)} logs={total_logs} hits={len(hits)} failed={len(failed)}", flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": len(contracts), "total_logs": total_logs,
           "hits": hits, "failed": failed, "truncated": truncated},
          open(D / "run69-inbound-retry.json", "w"), indent=1)
print("saved run69-inbound-retry.json", flush=True)
