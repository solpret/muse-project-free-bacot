#!/usr/bin/env python3
"""Retry the 1 run-67 failed contract on the RUN-67 window (131870175-131877958)."""
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
contracts = ["0x050a11c2bfcf881b546983a20550a0e409bf69da"]
FROM, TO = 131870175, 131877958
hits, failed, total_logs = [], [], 0
for c in contracts:
    try:
        data = ankr_mod.get_logs(c, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        total_logs += len(logs)
        for lg in logs:
            topics = lg.get("topics") or []
            if topics and topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
                hits.append({"contract": c, "tx": lg.get("transactionHash"), "to": "0x"+topics[2][-40:]})
    except Exception as e:
        failed.append({"contract": c, "error": str(e)[:200]})
    time.sleep(0.5)
print(f"RETRY67 DONE contracts={len(contracts)} logs={total_logs} hits={len(hits)} failed={len(failed)}", flush=True)
for h in hits: print("HIT", h, flush=True)
json.dump({"window":"run67 131870175-131877958","hits":hits,"failed":failed,"total_logs":total_logs},
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run68-inbound-retry67.json","w"), indent=1)
