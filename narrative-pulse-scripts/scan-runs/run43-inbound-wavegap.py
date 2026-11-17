#!/usr/bin/env python3
"""Read-only run 43 inbound GAP closure: 13 EARLY-wave contracts added to the
Free Bacot snapshot at 03:37 WIB (routine job 03:01 run), i.e. AFTER the
original inbound list (713) was built. Any wave contract sorting below index
550 was therefore in neither the first pass nor the resume slice. This script
checks ALL 13 (cheap, idempotent) for zero-from Transfers to tracked wallets
over the full run window. No preview/mint/sign/login."""
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
WAVE = ['0x82cf5049146d8656d1d4877546110c29b4a1c71a', '0x3b843b46cdfa173e947e1d662629933af1d94231', '0xa422fbf16e0e2f81a38f74b1be8b770b97575529', '0x6f8815cd3c1b0895814a2d4911492e4ff5a5ef86', '0xdf4b0b420f0684e654931bc37b2f230df8e81704', '0xb4ac39e5040d4cc8e1f58fc8ba8743a41cc09def', '0xbc3c55a7b69c7c75b44bfef11302e9f64bd3cf0d', '0x6e50f1cad63adf483021e2e0de334c9bb5b5de7f', '0xf1968d3f690b2327afef1b8aa87a4fe9e1090591', '0x3c1be64a8c62f68b442e4189bcef5aaf23ea6b3d', '0x5ad666a89de917b4eabfb20de881a6776169d39c', '0x273fc2c7705b23eb129e35ac8da26348e6fc4980', '0x9578f8a40228f44f31a9e4bc179e1112f7fa4157']
FROM, TO = 131669962, 131687073
hits, failed, total_logs = [], [], 0
for c in WAVE:
    try:
        data = ankr_mod.get_logs(c, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        total_logs += len(logs)
        print(f"{c} logs={len(logs)}", flush=True)
        if len(logs) >= 1000:
            data2 = ankr_mod.get_logs(c, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
            logs = ((data2.get("result") or {}).get("logs") or [])
            print(f"  truncated -> topic-filtered logs={len(logs)}", flush=True)
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
        print(f"{c} ERROR {e}", flush=True)
    time.sleep(0.5)
print(f"WAVE GAP DONE contracts=13 logs={total_logs} hits={len(hits)} failed={len(failed)}", flush=True)
for h in hits: print("HIT", h, flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": 13, "total_logs": total_logs,
           "hits": hits, "failed": failed},
          open("/home/hatch/workspace/narrative-pulse/scan-runs/run43-inbound-wavegap.json", "w"), indent=1)
print("saved run43-inbound-wavegap.json", flush=True)
