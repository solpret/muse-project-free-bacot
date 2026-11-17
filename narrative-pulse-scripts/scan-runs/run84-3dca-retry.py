#!/usr/bin/env python3
"""Run 84 retry (run-83 window): topic-filtered re-check of
0x3dca077eb687df96cc987da0035c8fad89ae716c, whose beyond-1000 logs were
UNVERIFIED in run 83 (Ankr full-range x3, split halves x2, fast_rpc all
timed out). Window 132023418-132031246. Topics: Transfer from zero address
to any tracked wallet. Tries Ankr full-range, then Ankr split halves,
then fast_rpc eth_getLogs split halves. Read-only."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import ankr as ankr_mod
import fast_rpc

def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
ZERO_PAD = "0x" + "0" * 64
HOME = Path.home()
CONTRACT = "0x3dca077eb687df96cc987da0035c8fad89ae716c"
FROM, TO = 132023418, 132031246
tier = json.load(open(HOME / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = sorted("0x" + "0" * 24 + w[2:] for w in uniq)
TOPICS = [T_TRANSFER, ZERO_PAD, tracked_padded]

def scan_logs(logs):
    hits = []
    for lg in logs or []:
        topics = lg.get("topics") or []
        if len(topics) >= 3 and topics[0] == T_TRANSFER and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            hits.append({"tx": lg.get("transactionHash"), "block": lg.get("blockNumber"),
                         "to": "0x" + topics[2][-40:], "token_id": int(topics[3], 16) if len(topics) >= 4 else None})
    return hits

out = {"contract": CONTRACT, "window": [FROM, TO], "attempts": [], "hits": [], "verified": False}
# Attempt 1: Ankr topic-filtered full range
try:
    data = ankr_mod.get_logs(CONTRACT, FROM, TO, topics=TOPICS)
    logs = ((data.get("result") or {}).get("logs") or [])
    out["attempts"].append({"route": "ankr_topic_full", "logs": len(logs), "ok": True})
    out["hits"] = scan_logs(logs)
    out["verified"] = True
    print(f"ankr full-range OK logs={len(logs)} hits={len(out['hits'])}", flush=True)
except Exception as e:
    out["attempts"].append({"route": "ankr_topic_full", "ok": False, "error": str(e)[:200]})
    print(f"ankr full-range ERROR {e}", flush=True)

if not out["verified"]:
    # Attempt 2: Ankr split halves
    mid = (FROM + TO) // 2
    all_logs, ok = [], True
    for a, b in ((FROM, mid), (mid + 1, TO)):
        try:
            data = ankr_mod.get_logs(CONTRACT, a, b, topics=TOPICS)
            logs = ((data.get("result") or {}).get("logs") or [])
            all_logs.extend(logs)
            out["attempts"].append({"route": f"ankr_topic_{a}-{b}", "logs": len(logs), "ok": True})
            print(f"ankr half {a}-{b} OK logs={len(logs)}", flush=True)
        except Exception as e:
            ok = False
            out["attempts"].append({"route": f"ankr_topic_{a}-{b}", "ok": False, "error": str(e)[:200]})
            print(f"ankr half {a}-{b} ERROR {e}", flush=True)
    if ok:
        out["hits"] = scan_logs(all_logs)
        out["verified"] = True

if not out["verified"]:
    # Attempt 3: fast_rpc eth_getLogs split halves
    all_logs, ok = [], True
    mid = (FROM + TO) // 2
    for a, b in ((FROM, mid), (mid + 1, TO)):
        try:
            logs = fast_rpc.race("eth_getLogs", [{"address": CONTRACT, "fromBlock": hex(a),
                "toBlock": hex(b), "topics": TOPICS}])
            all_logs.extend(logs or [])
            out["attempts"].append({"route": f"fast_rpc_{a}-{b}", "logs": len(logs or []), "ok": True})
            print(f"fast_rpc half {a}-{b} OK logs={len(logs or [])}", flush=True)
        except Exception as e:
            ok = False
            out["attempts"].append({"route": f"fast_rpc_{a}-{b}", "ok": False, "error": str(e)[:200]})
            print(f"fast_rpc half {a}-{b} ERROR {e}", flush=True)
    if ok:
        out["hits"] = scan_logs(all_logs)
        out["verified"] = True

print(f"3DCA RETRY DONE verified={out['verified']} hits={len(out['hits'])}", flush=True)
for h in out["hits"]: print("HIT", h, flush=True)
json.dump(out, open(HOME / "workspace/narrative-pulse/scan-runs/run84-3dca-retry.json", "w"), indent=1)
print("saved run84-3dca-retry.json", flush=True)
