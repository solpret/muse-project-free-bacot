#!/usr/bin/env python3
"""Read-only run 107 inbound leg: Ankr getLogs address-filtered per known contract.
Run-106 inbound list (1734) + run-107 deployments + new rotation tokens. No preview/mint/sign/login."""
import json, sys, time, re
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
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
contracts = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run108-inbound-contracts.json"))  # FROZEN list for run 84: run83 list + run83 deployment addrs
import sys as _sys
PART = _sys.argv[1] if len(_sys.argv) > 1 else "full"
START = int(_sys.argv[2]) if len(_sys.argv) > 2 else 0
END = int(_sys.argv[3]) if len(_sys.argv) > 3 else len(contracts)
contracts = contracts[START:END]
SENT = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run108-sent.json"))
FROM, TO = 132273609, SENT["max_block"]
print(f"part={PART} contracts={len(contracts)} window={FROM}-{TO} tracked={len(uniq)}", flush=True)
hits, failed, total_logs, truncated = [], [], 0, []
for i, c in enumerate(contracts):
    try:
        data = ankr_mod.get_logs(c, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        total_logs += len(logs)
        if len(logs) >= 1000:
            truncated.append(c)
            try:
                data2 = ankr_mod.get_logs(c, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
                logs2 = ((data2.get("result") or {}).get("logs") or [])
                print(f"  truncated {c}: topic-filtered logs={len(logs2)}", flush=True)
                logs = logs2
            except Exception as e:
                print(f"  truncated {c}: topic-filtered ERROR {e}", flush=True)
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
    except Exception as e:
        failed.append({"contract": c, "error": str(e)[:200]})
        print(f"[{i+1}] {c} ERROR {e}", flush=True)
    if (i+1) % 50 == 0: print(f"[{i+1}/{len(contracts)}] logs={total_logs} hits={len(hits)} failed={len(failed)} truncated={len(truncated)}", flush=True)
    time.sleep(0.5)
print(f"INBOUND DONE contracts={len(contracts)} logs={total_logs} hits={len(hits)} failed={len(failed)} truncated={truncated}", flush=True)
for h in hits: print("HIT", h, flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": len(contracts), "total_logs": total_logs,
           "hits": hits, "failed": failed, "truncated": truncated},
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run108-inbound107-" + PART + ".json", "w"), indent=1)
print("saved run108-inbound107-" + PART + ".json", flush=True)
