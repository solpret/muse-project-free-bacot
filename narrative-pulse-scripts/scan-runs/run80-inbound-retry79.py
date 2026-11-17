#!/usr/bin/env python3
"""Run 80: retry the 1 failed run-79 inbound contract on the run-79 window
(131992566-131999043). Read-only Ankr getLogs. No preview/mint/sign/login."""
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
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
C = "0x47a5569f94c6055edf3e5900402c2c79bcc39dd4"
FROM, TO = 131992566, 131999043
out = {"contract": C, "from": FROM, "to": TO}
try:
    data = ankr_mod.get_logs(C, FROM, TO)
    logs = ((data.get("result") or {}).get("logs") or [])
    out["ok"] = True
    out["total_logs"] = len(logs)
    hits = []
    for lg in logs:
        topics = lg.get("topics") or []
        if not topics: continue
        if topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            hits.append({"contract": C, "to": "0x" + topics[2][-40:], "tx": lg.get("transactionHash"), "block": lg.get("blockNumber")})
        elif topics[0] == T_SINGLE and len(topics) >= 4 and topics[2] == ZERO_PAD and topics[3] in tracked_padded:
            hits.append({"contract": C, "kind": "ERC1155", "to": "0x" + topics[3][-40:], "tx": lg.get("transactionHash"), "block": lg.get("blockNumber")})
    out["hits"] = hits
    print(f"RETRY OK logs={len(logs)} hits={len(hits)}", flush=True)
except Exception as e:
    out["ok"] = False
    out["error"] = str(e)[:300]
    print(f"RETRY FAILED {e}", flush=True)
json.dump(out, open(HOME / "workspace/narrative-pulse/scan-runs/run80-inbound-retry79.json", "w"), indent=1)
print("saved run80-inbound-retry79.json", flush=True)
