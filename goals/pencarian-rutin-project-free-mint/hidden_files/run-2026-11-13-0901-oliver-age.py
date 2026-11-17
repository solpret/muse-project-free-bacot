#!/usr/bin/env python3
"""OLIVER age deep-dive for free-mint-search run 2026-11-13 09:01 WIB.
Binary-search the first block where OLIVER totalSupply > 0 via historical
eth_call (public bsc-dataseed). If historical calls fail (pruned state),
record that route as failed. Read-only; writes
run-2026-11-13-0901-oliver-age.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
OLIVER = "0xad86e4d52e55709d1bda08f922853d4b109e0810"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=20):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def ts_at(block):
    """totalSupply(OLIVER) at a historical block; None on error."""
    data = sel("totalSupply()")
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": OLIVER, "data": data}, hex(block)]}, timeout=20)
            if isinstance(r, dict) and r.get("result") and r["result"] != "0x":
                return int(r["result"], 16)
            if isinstance(r, dict) and "error" in r:
                return ("error", str(r["error"])[:100])
        except Exception as e:
            continue
    return None
def block_ts(block):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(block), False]}, timeout=20)
            if isinstance(r, dict) and isinstance(r.get("result"), dict):
                return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
def main():
    t0 = time.time()
    out = {"started_wib": "2026-11-13T09:01+07:00"}
    head = None
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            head = int(r["result"], 16)
            break
        except Exception:
            continue
    out["head"] = head
    if not head:
        out["status"] = "no-head"
        json.dump(out, open(BASE + "run-2026-11-13-0901-oliver-age.json", "w"), indent=1)
        print(json.dumps(out)); return
    # Bounds: ~12 Nov 00:00 WIB (head - 33h*4800) and ~12 Nov 13:03 WIB (head - 20h*4800)
    lo = head - 33 * 4800
    hi = head - 20 * 4800
    out["bounds"] = {"lo_block": lo, "hi_block": hi}
    v_lo = ts_at(lo)
    v_hi = ts_at(hi)
    out["probe"] = {"totalSupply_lo": v_lo, "totalSupply_hi": v_hi}
    if isinstance(v_lo, tuple) or isinstance(v_hi, tuple) or v_lo is None or v_hi is None:
        out["status"] = "historical-call-failed"
        out["note"] = ("Historical eth_call failed on public endpoints (pruned state likely) - "
                       "first-mint block cannot be found this way; route recorded as tried+failed.")
        json.dump(out, open(BASE + "run-2026-11-13-0901-oliver-age.json", "w"), indent=1)
        print(json.dumps(out, indent=1)); return
    if v_lo > 0:
        out["status"] = "launched-before-lo-bound"
        out["note"] = "totalSupply already >0 at 12 Nov 00:00 WIB bound - launch earlier than bound; age >=24h likely."
    elif v_hi == 0:
        out["status"] = "not-launched-by-hi-bound"
        out["note"] = "totalSupply still 0 at 12 Nov 13:03 WIB - contradicts Boltbook post (630/1000 at 13:03 WIB); bounds wrong, re-check."
    else:
        a, b = lo, hi  # ts(a)==0, ts(b)>0
        while b - a > 1:
            m = (a + b) // 2
            v = ts_at(m)
            if v is None or isinstance(v, tuple):
                out["status"] = "binary-search-call-failed"
                out["failed_at_block"] = m
                json.dump(out, open(BASE + "run-2026-11-13-0901-oliver-age.json", "w"), indent=1)
                print(json.dumps(out, indent=1)); return
            if v == 0:
                a = m
            else:
                b = m
        out["first_supply_block"] = b
        out["totalSupply_at_first"] = ts_at(b)
        ts = block_ts(b)
        out["first_block_timestamp"] = ts
        if ts:
            import datetime
            dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
            out["first_block_wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
            age_h = (time.time() - ts) / 3600.0
            out["age_hours_at_run"] = round(age_h, 2)
            out["age_lt_24h"] = age_h < 24
        out["status"] = "found"
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(BASE + "run-2026-11-13-0901-oliver-age.json", "w"), indent=1)
    print(json.dumps(out, indent=1))
if __name__ == "__main__":
    main()
