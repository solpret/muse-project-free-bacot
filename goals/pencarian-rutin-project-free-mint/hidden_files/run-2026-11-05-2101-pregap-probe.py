#!/usr/bin/env python3
"""READ-ONLY follow-up: earliest-mint probe in the pre-gap range for 6 contracts
whose totalSupply implies mints before GAP_START (131826009).
Range: 131773400 (~48h before run) .. 131826008.
No preview/mint/sign.
"""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

ZERO_TOPIC = "0x" + "00" * 32
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
FROM = 131773400
TO = 131826008

TARGETS = [
    ("0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e", "GHOST"),
    ("0x1eF7588Dff561b7390D3AF23d06E684D64217419", "Sonofluidic"),
    ("0xFefEf878814BdF807b7789bd79dF772A1FFA6AfD", "Chiguachipmunk"),
    ("0x6A1081EAE3e1Cb9adE1fC5ceC10eF37d6574a9Fc", "Cerberuscorgi"),
    ("0xa739052D3C90bB73AA01AaFED09F0F7f166D2F8F", "Cablecobra"),
    ("0xDDE0cE49540Da95B8EbD273766c5249b5366a2B7", "Bluetoothbison"),
]

out = []
for addr, name in TARGETS:
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc",
            "fromBlock": hex(FROM), "toBlock": hex(TO),
            "pageSize": 1000, "decodeLogs": False,
            "address": [addr], "topics": [TRANSFER, ZERO_TOPIC]}, timeout=30)
        logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        blocks = sorted(int(l.get("blockNumber", "0x0"), 16) for l in logs)
        nxt = body.get("result", {}).get("nextPageToken")
        rec = {"address": addr, "name": name, "range": [FROM, TO],
               "logs_in_range": len(logs), "earliest_block": blocks[0] if blocks else None,
               "latest_block": blocks[-1] if blocks else None, "nextPageToken_present": bool(nxt)}
    except Exception as e:
        rec = {"address": addr, "name": name, "range": [FROM, TO], "error": str(e)}
    out.append(rec)
    print(addr, name, rec)
    # block timestamp for earliest, if any
    if rec.get("earliest_block"):
        import urllib.request
        for url in ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]:
            try:
                payload = json.dumps({"jsonrpc": "2.0", "method": "eth_getBlockByNumber",
                                      "params": [hex(rec["earliest_block"]), False], "id": 1}).encode()
                req = urllib.request.Request(url, data=payload,
                                             headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(req, timeout=10) as r:
                    d = json.load(r)
                ts = int((d.get("result") or {}).get("timestamp", "0x0"), 16)
                rec["earliest_timestamp"] = ts
                rec["earliest_wib"] = datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                print("   earliest_wib:", rec["earliest_wib"])
                break
            except Exception:
                continue

with open("run-2026-11-05-2101-pregap-probe.json", "w") as f:
    json.dump(out, f, indent=1)
print("wrote run-2026-11-05-2101-pregap-probe.json")
