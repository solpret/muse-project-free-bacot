#!/usr/bin/env python3
"""Read-only run 115 inbound retry: 35 contracts that failed in slices with
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
FROM, TO = 132325599, 132333593
contracts = ["0xa96b43fc51ef1cf5dd9f72da26fc67d63036c806", "0xaa911256fa3ca8f6cff699fc6190905261350cf0", "0xad6278f2903dd406ab3b86c02971bfbbc6386628", "0xb792bf600df37eb7638fb16434e813fc0c90c3c8", "0xb7e18a0c3c593b256ecb1c57dda9bfbc2141bf38", "0xbb30a6c4bafa060c586eb13128f2250b6285f823", "0xbd6087fc30f2395344020cb190255c56cbc517bd", "0xc33e5b32ecdc6926c02b2a3fab5adf5d5e59c2e0", "0xc36fd9884ac52eb406b80d4e91328b39251f54ab", "0xc698186ce921ebc8d3b27e9f2e890ba785659a3b", "0xc9bf67564043573a06685205c4c5296d7d37bc74", "0xca8820d36bec22e462a45b6f658d3f7bb2542a82", "0xcbf6c4c0d46bd858fd384a484e343cb8cd0c50e5", "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28", "0xcdce49721d2fed646d4c1a34a51ec001cd879449", "0xd697bb3e5d19d56b4575ee4bf77033ef26093e14", "0xd9a49df66443ba35e7a96bee63b0b8913f47c22c", "0xda552a0b709d09a2532689c6e39d981f527817b6", "0xde3e3e9e2f87f285f0f26ea54923a933b10df140", "0xe9e1fad4b2d43a7620c1c2ca588f174710000000", "0xf81b542c41f982a7d7a8e2ee8cab5feee6203218", "0xdd6be646fe14b2f220e5d0144d0f06767c50a716", "0x5656cbb041e7fc17c788976e8ddb5e1c9f5841f9"]
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
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run115-inbound115-retry2.json", "w"), indent=1)
print("saved run115-inbound115-retry2.json", flush=True)
