#!/usr/bin/env python3
"""Osiris Guardians age walkback run 1801: earliest Transfer-from-zero via
dataseed eth_getLogs, address-filtered, 1000-block chunks forward from
131471151 (bridge window start). Read-only."""
import json, subprocess, time
OSIRIS = "0xd6fcf9db58a559aafbbf9fd823f4f081e6701311"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed.binance.org/"]
def post(ep, payload, timeout=30):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def get_logs(frm, to):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
        "address": OSIRIS, "fromBlock": hex(frm), "toBlock": hex(to),
        "topics": [TRANSFER, ZERO]}]}
    for ep in EPS:
        try:
            r = post(ep, payload, timeout=30)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                return r["result"]
        except Exception as e:
            last = str(e)[:120]
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                          "params":[hex(blk), False]}, timeout=30)
            ts = r.get("result", {}).get("timestamp")
            if ts: return int(ts, 16)
        except Exception: continue
    return None
out = {"chunks": [], "first_log": None}
frm = 131471151
for i in range(14):
    to = min(frm + 999, 131483364)
    t0 = time.time()
    logs = get_logs(frm, to)
    n = None if logs is None else len(logs)
    print(f"chunk {i+1}: {frm}-{to} logs={n} ({time.time()-t0:.1f}s)", flush=True)
    out["chunks"].append({"from": frm, "to": to, "logs": n})
    if logs:
        first = logs[0]
        blk = int(first["blockNumber"], 16)
        ts = block_ts(blk)
        out["first_log"] = {"block": blk, "tx": first.get("transactionHash"),
                            "timestamp": ts}
        print("FIRST LOG block", blk, "ts", ts, flush=True)
        break
    if to >= 131483364: break
    frm = to + 1
json.dump(out, open("run-2026-11-09-1801-osiris-age.json","w"), indent=1)
print("OSIRIS AGE DONE")
