#!/usr/bin/env python3
"""Run 106 inbound same-run retry (read-only): the 10 contracts that failed with
Ankr 'Remote end closed connection' in chunks a (2), b2 (1), b3a (3), b3b (2), b3c (2)."""
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
SENT = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run106-sent.json"))
FROM, TO = 132260250, SENT["max_block"]
CONTRACTS = ['0x05debe4445232205ae7e79d02cb5de5aa0641eff', '0x1062c963f5f11a5a55831b7e818e55b052b59947', '0xa74081fd9bc9623a2d9321223c35b41016a7fd65', '0xcd1bb8013e924e26ed4131a69304f2969c4f8d28', '0xd1d3b730b154838b7b5f0c072de7ba66ffbbe72b', '0xd79fa409edac394614c721195eece440f016e188', '0xc2d5ebfd9c2052e5dd96f800e06943126063da1a', '0x4d8575dda648e7ec2bf09915538b8c936a119d73', '0xbf64b11e33b308c0897c719bb8475d296a66009e', '0xcc07cbd07cb2a59557612fcaeb6d57eaacfa2e85']
hits, failed, total_logs, truncated = [], [], 0, []
for i, c in enumerate(CONTRACTS):
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
        print(f"[{i+1}] {c} logs={len(logs)} hits={len(hits)}", flush=True)
    except Exception as e:
        failed.append({"contract": c, "error": str(e)[:200]})
        print(f"[{i+1}] {c} ERROR {e}", flush=True)
    time.sleep(0.5)
print(f"RETRY DONE contracts={len(CONTRACTS)} logs={total_logs} hits={len(hits)} failed={len(failed)}", flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": len(CONTRACTS), "total_logs": total_logs,
           "hits": hits, "failed": failed, "truncated": truncated},
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run106-inbound106-retry.json", "w"), indent=1)
print("saved run106-inbound106-retry.json")
