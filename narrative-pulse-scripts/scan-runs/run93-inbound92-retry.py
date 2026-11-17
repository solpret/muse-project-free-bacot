#!/usr/bin/env python3
"""Run 93: retry of the TWO failed inbound contracts from run 92 (chunk a contract 236,
chunk b3 contract 238). Run-92 window 132109989-132119034.
Topic-filtered: Transfer from zero address to a tracked wallet. Read-only."""
import json, sys
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
tracked_padded = sorted({"0x" + "0" * 24 + w[2:] for w in uniq})
CONTRACTS = ["0x3bf121dc4c5a1ba567f3ee801d0e447601726207",
             "0xfceafd4bd5c69b24fe2662b1fb69d6dd7872ee52"]
FROM, TO = 132109989, 132119034
out = {"window": [FROM, TO], "contracts": []}
for C in CONTRACTS:
    entry = {"contract": C, "from": FROM, "to": TO, "ok": False}
    try:
        data = ankr_mod.get_logs(C, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        print(f"{C} unfiltered logs={len(logs)}", flush=True)
        hits = []
        if len(logs) >= 1000:
            data2 = ankr_mod.get_logs(C, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, tracked_padded])
            logs2 = ((data2.get("result") or {}).get("logs") or [])
            print(f"{C} truncated; topic-filtered logs={len(logs2)}", flush=True)
            logs = logs2
        for lg in logs:
            topics = lg.get("topics") or []
            if not topics: continue
            if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
                hits.append({"contract": C, "kind": "ERC721/20 Transfer", "to": "0x" + topics[2][-40:],
                             "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
            elif topics[0] == T_SINGLE and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
                hits.append({"contract": C, "kind": "ERC1155 TransferSingle", "to": "0x" + topics[3][-40:],
                             "token_id": int(topics[4], 16) if len(topics) >= 5 else None,
                             "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
        entry.update({"ok": True, "logs": len(logs), "hits": hits})
        print(f"{C} RETRY DONE logs={len(logs)} hits={len(hits)}", flush=True)
        for h in hits: print("HIT", h, flush=True)
    except Exception as e:
        entry.update({"ok": False, "error": str(e)[:300]})
        print(f"{C} RETRY FAILED {e}", flush=True)
    out["contracts"].append(entry)
json.dump(out, open("/home/hatch/workspace/narrative-pulse/scan-runs/run93-inbound92-retry.json", "w"), indent=1)
print("saved run93-inbound92-retry.json")
