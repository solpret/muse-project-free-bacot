#!/usr/bin/env python3
"""Deep-dive Task 1 (v2): Glitchpilotfox first-mint age verification.
Contract 0xda552a0b709d09a2532689c6e39d981f527817b6
v1 tried dataseed eth_getLogs: FAILED on all endpoints, even 100-block ranges:
  {"code":-32005,"message":"limit exceeded"} (bsc-dataseed1, 2026-11-09 ~05:47 WIB).
Precedent (run 2026-11-06-0801): dataseed eth_getLogs failed for first-mint
checks too; Ankr get_logs module was the working route. So v2 uses the Ankr
module (ankr_post, pageSize 1000, one 1000-block probe window per target),
exactly the chunked-probe strategy from the task. Timestamps ONLY via
dataseed eth_getBlockByNumber (never Ankr).
Cutoff: 48h before 2026-11-09 ~05:35 WIB ~= block ~132087000 (head ~132474139,
~0.45s/block -> 384000 blocks/48h). A mint at a block whose timestamp is
>48h old PROVES age >48h.
"""
import sys, json, time, datetime, subprocess
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post

CONTRACT = "0xda552a0b709d09a2532689c6e39d981f527817b6"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
EPS = ["https://bsc-dataseed1.bnbchain.org",
       "https://bsc-dataseed2.bnbchain.org",
       "https://bsc-dataseed.binance.org"]

def probe(frm, to):
    """One 1000-block window via Ankr get_logs, Transfer-from-zero only."""
    t0 = time.time()
    total, first, pages, token = 0, None, 0, None
    try:
        while True:
            params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                      "pageSize": 1000, "decodeLogs": False, "address": CONTRACT,
                      "topics": [TRANSFER, ZERO_TOPIC]}
            if token:
                params["pageToken"] = token
            body = ankr_post("ankr_getLogs", params, timeout=30)
            result = body.get("result", {}) if isinstance(body, dict) else {}
            logs = result.get("logs", [])
            for lg in logs:
                total += 1
                b = int(lg.get("blockNumber", "0x0"), 16)
                tid = int(lg["topics"][3], 16) if len(lg.get("topics", [])) > 3 else None
                if first is None or b < first["blockNumber"]:
                    first = {"blockNumber": b, "tx": lg.get("transactionHash"), "tokenId": tid}
            token = result.get("nextPageToken")
            pages += 1
            if not token or pages >= 3:
                break
            time.sleep(2.2)
        return {"from": frm, "to": to, "status": "OK", "count": total,
                "secs": round(time.time() - t0, 1), "pages": pages,
                "first_log": first, "truncated_page_cap": pages >= 3 and bool(token)}
    except Exception as e:
        return {"from": frm, "to": to, "status": "READ_FAILURE", "count": None,
                "secs": round(time.time() - t0, 1), "pages": pages,
                "first_log": None, "error": repr(e)}

def block_ts(block):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                          "params": [hex(block), False]})
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-s", "--max-time", "25", "-X", "POST",
                                "-H", "Content-Type: application/json", "-d", payload, ep],
                               capture_output=True, text=True, timeout=30)
            d = json.loads(r.stdout)
            res = d.get("result")
            if res:
                ts = int(res["timestamp"], 16)
                wib = datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                return ts, wib, ep
        except Exception:
            continue
    return None, None, None

def main():
    probes = []
    targets = [132087000, 132060000, 132000000, 131800000, 131600000, 131400000, 131200000]
    for frm in targets:
        p = probe(frm, frm + 999)
        print(f"probe {frm}-{frm+999}: {p['status']} count={p['count']} first={p['first_log']} ({p['secs']}s)", flush=True)
        if p["status"] == "OK" and p["count"]:
            fb = p["first_log"]["blockNumber"]
            ts, wib, ep = block_ts(fb)
            p["first_log_block_timestamp_unix"] = ts
            p["first_log_block_wib"] = wib
            p["timestamp_endpoint"] = ep
            print(f"  first-log block {fb} ts {ts} = {wib}", flush=True)
        probes.append(p)
        json.dump({"contract": CONTRACT, "run": "2026-11-09-0501-deepdive",
                   "cutoff_48h_block_estimate": 132087000,
                   "cutoff_48h_wib": "2026-11-07 ~05:35 WIB",
                   "method": "Ankr ankr_getLogs module, pageSize 1000, 1000-block probe windows, Transfer topic0 + topic1=zero; timestamps via dataseed eth_getBlockByNumber only. Dataseed eth_getLogs FAILED first (-32005 limit exceeded, even 100-block range, all 3 dataseeds) - see dataseed_getLogs_failure.",
                   "dataseed_getLogs_failure": {"error": {"code": -32005, "message": "limit exceeded"}, "tried_ranges": ["1000-block", "100-block"], "endpoints": EPS, "time_wib": "2026-11-09 ~05:47 WIB"},
                   "probes": probes},
                  open("run-2026-11-09-0501-deepdive-glitchpilotfox.json", "w"), indent=1)
        time.sleep(1.5)
    print("saved", flush=True)

if __name__ == "__main__":
    main()
