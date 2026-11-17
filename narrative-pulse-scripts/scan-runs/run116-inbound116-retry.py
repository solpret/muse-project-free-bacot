#!/usr/bin/env python3
"""Read-only run 116 inbound retry: 23 contracts that failed in slices with
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
FROM, TO = 132333594, 132342275
contracts = [
 "0x18824b586b0112775fb64072528a5637a2a9ce6b",
 "0x203c330f7cb6762b0bd759a337a86f938fb8de4e",
 "0x434d97b0987d7024a8d4c59900eb22b54299a4bb",
 "0x43901e3014c8b23b800b109e581f8eb4a2b99fcf",
 "0x4f3fe54dccd31d514ef38d7762e961dd7c18f598",
 "0x50bb9d64e50d00d1eb3023fd7ff7ea6586d346ac",
 "0x515506d261e33a20c42f311ae3b626551cd2b748",
 "0x6cb2f32c3c3d0b9f393101221aafd4e512157fd7",
 "0x86a49a9e391c5dc143d2d8b2e8bb77e8bb61ede9",
 "0x9e6969f6326081074b77b26ee8e35124f160d1d4",
 "0xb1e23c65a3dda306491090db5be2e0084e4957ef",
 "0xb34105002b19ef0ce43b59011fe848df5c8b174f",
 "0xc433a98bcccc90556de112742ba97ffea7882fcc",
 "0xd06518ea638cab567328ccd7b67e43a119c275e0",
 "0xd819ce2173106b7c388eafb3a4ca49697e9fd0df",
 "0xd8587bc4c84335c606bc6427859615b189509aa3",
 "0xe5523bf6aa0f92acc7d2898f65596a0a088a8f0f",
 "0xed078863ab0b1c562480a2b320c4dba4cf70bcf3",
 "0xf5a77f01b73eab3981d6b899aa13c94ffbb6252c",
 "0xf7712d5d014c17f4036023f49eba01a27585026d",
 "0xf8eb3086f7bf2dc69d90e9223eeda1e89cd08ba9",
 "0xfbb5054f63a85f2408c3566fb374fe1cd702778a",
 "0xfd303cc064e8bcf18d820ed6252f80c53b4e4f93"
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
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run116-inbound116-retry.json", "w"), indent=1)
print("saved run116-inbound116-retry.json", flush=True)
