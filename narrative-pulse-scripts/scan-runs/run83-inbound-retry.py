#!/usr/bin/env python3
"""Run 83 follow-up: retry inbound-leg contracts that FAILED in a finished chunk.
Usage: run83-inbound-retry.py <json1> [<json2> ...]  (reads 'failed' lists).
Same window as the main leg (132023418 - run83 max_block). Up to 3 attempts per
contract. Read-only. No preview/mint/sign/login."""
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
SENT = json.load(open(HOME / "workspace/narrative-pulse/scan-runs/run83-sent.json"))
FROM, TO = 132023418, SENT["max_block"]
contracts, seen = [], set()
for path in sys.argv[1:]:
    d = json.load(open(path))
    for f in d.get("failed", []):
        c = f["contract"].lower()
        if c not in seen:
            seen.add(c); contracts.append(c)
TAG = sys.argv[1].split("run83-inbound-")[-1].replace(".json", "") if len(sys.argv) == 2 else "multi"
print(f"retry tag={TAG} contracts={len(contracts)} window={FROM}-{TO}", flush=True)
out = {"from": FROM, "to": TO, "hits": [], "failed": [], "total_logs": 0,
       "truncated": [], "contracts_checked": len(contracts)}
for i, c in enumerate(contracts):
    done = False
    for attempt in range(3):
        try:
            data = ankr_mod.get_logs(c, FROM, TO)
            logs = ((data.get("result") or {}).get("logs") or [])
            out["total_logs"] += len(logs)
            if len(logs) >= 1000:
                out["truncated"].append(c)
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
                    out["hits"].append({"contract": c, "kind": "ERC721/20 Transfer",
                        "to": "0x" + topics[2][-40:],
                        "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                        "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
                elif topics[0] == T_SINGLE and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
                    out["hits"].append({"contract": c, "kind": "ERC1155 TransferSingle",
                        "to": "0x" + topics[3][-40:],
                        "token_id": int(topics[4], 16) if len(topics) >= 5 else None,
                        "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
            done = True
            break
        except Exception as e:
            print(f"[{i+1}] {c} attempt {attempt+1} ERROR {str(e)[:120]}", flush=True)
            time.sleep(3)
    if not done:
        out["failed"].append({"contract": c, "error": "3 attempts failed"})
    if (i+1) % 10 == 0:
        print(f"[{i+1}/{len(contracts)}] logs={out['total_logs']} hits={len(out['hits'])} failed={len(out['failed'])}", flush=True)
    time.sleep(0.5)
print(f"RETRY DONE contracts={len(contracts)} logs={out['total_logs']} hits={len(out['hits'])} failed={len(out['failed'])} truncated={len(out['truncated'])}", flush=True)
for h in out["hits"]: print("HIT", h, flush=True)
json.dump(out, open(HOME / f"workspace/narrative-pulse/scan-runs/run83-inbound-retry-{TAG}.json", "w"), indent=1)
print(f"saved run83-inbound-retry-{TAG}.json", flush=True)
