#!/usr/bin/env python3
"""Read-only run 114 inbound retry: 35 contracts that failed in slices with
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
FROM, TO = 132318096, 132325598
contracts = ["0x56e2604a33f1ccbc00376046a767cce45b50f592", "0x77a0c1114f7e2579afbfd14b36dccf2a347bea19", "0xf1822144176ad13c5bccfe33a23129c37ca5bdcd", "0xfe8d985cb19380805b01cf7fcfc65c3819e030c8", "0x17adf24db4774860579d97bddaaa0144a8b796f3", "0xcc24bb6879bf314c735e846e5027b365fa1243d4", "0xe8c99fa23bddf91ec1144310a04af3fc95498e8a", "0xe8f4ea18e0e4198cdd18f04ec23c306766f8476c", "0x48957749563340f20c09dacaac1f6d7395b381d5", "0x5ad7ff101c4470104dcde1f640524addc68d226d", "0x5f7f05d0c16a03b7790179fe8c6c94e55c9ac3aa", "0x619922e3b6e145704c6a3117979b36230d464965", "0x6376705064892100790290a1dbb215cc0b3f25f0", "0xbe7ed5018da1e9a7e63d8fbb3dd6fb4522906bee", "0xd6bc84d7709465fda77a0d293792f36182ca7093", "0xd6fc0ffae073a59b1e88a7372486e0aa39da331b", "0xb4d680d788331455330f46c2bc8d14547bdcdfdd", "0x5ed285578f9dd35519a55e3eb10d42b9c620f3a8", "0x0e1ef7d7190f863b8f519dc2340a328df246afea", "0x0f2a925fdfe36ae9adafb1c4eb3fcd5895ddea60", "0x11f956dca387571fee9a7281c449009d71b4cca8", "0xa297d0636313277e0f70cd73eebcd4239fb43dd2", "0xc25850d442b8961e4a31be52e3c0c738f730f0e1", "0xc43d7cf11fc0af3ba21db56eb109bbeaab5accb1", "0x31816787f4b8ae82b9c13f5379b8c1ad935b504a", "0x143485635f7a8d6d1a9a2261fc190c6c1ab5f9db", "0x5b6dd1d258cdc1e5871378d529920eea40744f02", "0x8cbe5c2357a6f7f5c56f8a701125f643908b2918", "0xaa2913ed59ad005fc6b0246505aa931c10bb3e6e", "0x504e13fd32b192299c21a2f30432584d1ff2dd17", "0x73a63a8aefd63767c19b05401159f06f8eed2cc4", "0xbf6d218bea44104216343f481882d6912a4a4b79", "0x44550db028ce1767bbce82583c48c123b38d42a7", "0xcfb30966881dc36e86d901d90d44559cb6536ac4", "0xeb6e8b601e528d9dfa9cb702727b96fb34aad69e"]
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
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run114-inbound114-retry.json", "w"), indent=1)
print("saved run114-inbound114-retry.json", flush=True)
