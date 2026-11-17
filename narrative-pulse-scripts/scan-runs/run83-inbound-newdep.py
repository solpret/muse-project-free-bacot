#!/usr/bin/env python3
"""Run 83 follow-up: topic-filtered getLogs for the 14 contracts CREATED by
tracked wallets during the run-83 window (not in the frozen inbound list).
Checks for zero-from Transfer/TransferSingle to a tracked wallet in the same
window. Read-only. No preview/mint/sign/login."""
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
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
dep = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run83-deployments.json"))
FROM, TO = 132023418, 132031246
out = {"from": FROM, "to": TO, "hits": [], "failed": [], "total_logs": 0, "checked": len(dep)}
for c in dep:
    try:
        data = ankr_mod.get_logs(c, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
        logs = ((data.get("result") or {}).get("logs") or [])
        out["total_logs"] += len(logs)
        print(c, "zero-from->tracked Transfer logs:", len(logs), flush=True)
        for lg in logs:
            topics = lg.get("topics") or []
            out["hits"].append({"contract": c, "kind": "ERC721/20 Transfer",
                "to": "0x" + topics[2][-40:],
                "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
        data2 = ankr_mod.get_logs(c, FROM, TO, topics=[T_SINGLE, None, ZERO_PAD, sorted(tracked_padded)])
        logs2 = ((data2.get("result") or {}).get("logs") or [])
        out["total_logs"] += len(logs2)
        print(c, "zero-from->tracked TransferSingle logs:", len(logs2), flush=True)
        for lg in logs2:
            topics = lg.get("topics") or []
            out["hits"].append({"contract": c, "kind": "ERC1155 TransferSingle",
                "to": "0x" + topics[3][-40:],
                "token_id": int(topics[4], 16) if len(topics) >= 5 else None,
                "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
    except Exception as e:
        out["failed"].append({"contract": c, "error": str(e)[:200]})
        print(c, "ERROR", e, flush=True)
    time.sleep(0.5)
print(f"NEWDEP DONE checked={out['checked']} logs={out['total_logs']} hits={len(out['hits'])} failed={len(out['failed'])}", flush=True)
for h in out["hits"]: print("HIT", h, flush=True)
json.dump(out, open(HOME / "workspace/narrative-pulse/scan-runs/run83-inbound-newdep.json", "w"), indent=1)
print("saved run83-inbound-newdep.json", flush=True)
