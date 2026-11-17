#!/usr/bin/env python3
"""Read-only run 117 inbound retry: 15 contracts that failed in slices with
'Remote end closed connection without response'. Same window 132318096-132325598.
Same hit parse as run111-inbound110.py. No preview/mint/sign/login."""
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
FROM, TO = 132342276, 132349881
contracts = [
 "0x4c54c3d3cc77f2c9ece2452d5670a6cc2805534d",
 "0x4c95633c4dd0c508b9d429a5efdade97ab782787",
 "0x58055f6535b6bf7b33123521a905c61afbd99406",
 "0x64295d2dea0acb8d0ed0d00c009c7d25eb3a0446",
 "0x6eee003e2aebe75be551ac509eb485cc25e404fb",
 "0x6fc11cf9b5995a41196dc257060930e6880ddbca",
 "0x7b04d2b20462b11d019e3fea2c957a3e593b0fa7",
 "0x7d390e37ed41a359f276d8764ca15432704b99b7",
 "0x88a4c4bd8071213b2bc20ec8ee80b0b456eb8486",
 "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0",
 "0xf46ed98e467fc20709ec2b199882cd116b5c1cf4",
 "0x7856088e94e41497f24bce9029d3ecffde672ba0",
 "0x2b029e80bc89900fb658b103e8c0b621c1ddad94",
 "0xbfb45b37841056b8b585349cc41ba18cd2fff7fa",
 "0x03904443ea101ecb72111c67ec9e0695ea805790",
]
hits, failed, total_logs, truncated = [], [], 0, []
for i, c in enumerate(contracts):
    for attempt in range(3):
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
            print(f"[{i+1}] {c} OK logs={len(logs)} hits={len(hits)}", flush=True)
            break
        except Exception as e:
            print(f"[{i+1}] {c} attempt {attempt+1} ERROR {e}", flush=True)
            if attempt == 2:
                failed.append({"contract": c, "error": str(e)[:200]})
            time.sleep(5)
    time.sleep(1.0)
print(f"RETRY DONE contracts={len(contracts)} logs={total_logs} hits={len(hits)} failed={len(failed)} truncated={truncated}", flush=True)
for h in hits: print("HIT", h, flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": len(contracts), "total_logs": total_logs,
           "hits": hits, "failed": failed, "truncated": truncated},
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run117-inbound117-retry.json", "w"), indent=1)
print("saved run117-inbound117-retry.json", flush=True)
