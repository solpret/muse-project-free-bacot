#!/usr/bin/env python3
"""Read-only run 5 inbound leg: Ankr getLogs address-filtered per known contract,
window 131374720-131382231, plus DigDown residual sub-range retry (topic-filtered
first, then small slices). No preview/mint/sign/login."""
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
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
        "0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903",
        "0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc",
        "0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
tracked_set = set(uniq)

contracts = json.load(open("/tmp/tracked-scan-run5-contracts-all.json"))
# add new run5 contracts
for c in ["0x1cf9e60218493149ace7dc953497c07175aa625e","0x1591f1ed9f3dbec3a922dc63f5782daf17eeba1e",
          "0xacf150d9ec909e3d339bf4c6d090b18495674e66","0x08be8a0727b6fc801171c1f4f4dd547ea44ca339",
          "0x0d463ce4ad0c24ab902f7443ef6c725207c6eb9f","0xf00d595f9fbb8308fb03eeec7406e6883b157413",
          "0xd8e24465f2f5a8fb9b3b24e3042f26a4b10c020f"]:
    if c not in contracts: contracts.append(c)
contracts = sorted(set(contracts))
FROM, TO = 131374720, 131382231
print(f"contracts={len(contracts)} window={FROM}-{TO} tracked={len(uniq)}", flush=True)
hits, failed, total_logs, truncated = [], [], 0, []
for i, c in enumerate(contracts):
    try:
        data = ankr_mod.get_logs(c, FROM, TO)
        logs = ((data.get("result") or {}).get("logs") or [])
        total_logs += len(logs)
        if len(logs) >= 1000: truncated.append(c)
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
        print(f"[{i+1}] {c} ERROR {e}", flush=True)
    if (i+1) % 50 == 0: print(f"[{i+1}/{len(contracts)}] logs={total_logs} hits={len(hits)} failed={len(failed)} truncated={len(truncated)}", flush=True)
    time.sleep(0.5)
print(f"INBOUND DONE contracts={len(contracts)} logs={total_logs} hits={len(hits)} failed={len(failed)} truncated={truncated}", flush=True)
for h in hits: print("HIT", h, flush=True)

# --- DigDown residual: 131367286-131368347, topic-filtered attempt ---
DIG = "0xf464550f1d744793893c0ce09b89269ed726d796"
residual = {"contract": DIG, "range": [131367286, 131368347]}
try:
    data = ankr_mod.get_logs(DIG, 131367286, 131368347, topics=[T_TRANSFER, ZERO_PAD, sorted(tracked_padded)])
    logs = ((data.get("result") or {}).get("logs") or [])
    residual["topic_filtered"] = {"logs": len(logs), "hits": []}
    for lg in logs:
        topics = lg.get("topics") or []
        if topics and topics[0] == T_TRANSFER and len(topics) >= 3 and topics[1] == ZERO_PAD and topics[2] in tracked_padded:
            residual["topic_filtered"]["hits"].append({"to": "0x" + topics[2][-40:], "token_id": int(topics[3], 16) if len(topics) >= 4 else None,
                                                        "block": lg.get("blockNumber"), "tx": lg.get("transactionHash")})
    print("DIGDOWN topic-filtered:", residual["topic_filtered"], flush=True)
except Exception as e:
    residual["topic_filtered_error"] = str(e)[:300]
    print("DIGDOWN topic-filtered ERROR:", e, flush=True)
json.dump({"from": FROM, "to": TO, "contracts_checked": len(contracts), "total_logs": total_logs,
           "hits": hits, "failed": failed, "truncated": truncated, "residual": residual},
          open("/tmp/tracked-scan-run5-inbound.json", "w"), indent=1)
print("saved /tmp/tracked-scan-run5-inbound.json", flush=True)
