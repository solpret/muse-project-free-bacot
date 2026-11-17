#!/usr/bin/env python3
"""Age check for PX24-group (run 2026-11-13 07:01): binary-search first block
with totalSupply()>0 via eth_call at historical blocks, then block timestamp.
Read-only. Writes run-2026-11-13-0701-age.json."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
TS = sel("totalSupply()")
def post(ep, payload, timeout=20):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def call_at(addr, block):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": TS}, hex(block)]}
    for ep in EPS:
        try:
            r = post(ep, payload)
            if isinstance(r, dict) and "result" in r:
                if r["result"] in (None, "0x"):
                    return 0  # contract not yet deployed at that block => supply 0
                return int(r["result"], 16)
        except Exception:
            continue
    return None
def block_ts(block):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
               "params": [hex(block), False]}
    for ep in EPS:
        try:
            r = post(ep, payload)
            if isinstance(r, dict) and isinstance(r.get("result"), dict):
                return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None
def first_mint(name, addr, lo, hi):
    # invariant: totalSupply(lo)==0, totalSupply(hi)>0 (verify hi first)
    hi_v = call_at(addr, hi)
    if hi_v is None or hi_v == 0:
        return {"name": name, "address": addr, "error": "totalSupply(hi) not >0", "hi_value": hi_v}
    lo_v = call_at(addr, lo)
    if lo_v is None:
        return {"name": name, "address": addr, "error": "totalSupply(lo) unreadable"}
    if lo_v > 0:
        return {"name": name, "address": addr, "error": "totalSupply(lo) already >0; launch before lo", "lo_value": lo_v}
    # binary search first block with supply>0
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = call_at(addr, mid)
        if v is None:
            return {"name": name, "address": addr, "error": "unreadable mid block", "mid": mid}
        if v > 0:
            hi = mid
        else:
            lo = mid
    ts = block_ts(hi)
    import datetime
    wib = None
    if ts:
        wib = (datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)
               .astimezone(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
    return {"name": name, "address": addr, "first_mint_block": hi,
            "first_mint_ts": ts, "first_mint_wib": wib,
            "totalSupply_at_first_block": call_at(addr, hi)}
def main():
    t0 = time.time()
    head = None
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})
            head = int(r["result"], 16); break
        except Exception:
            continue
    lo = head - 40000
    targets = {
        "PX24": "0xe712510fcb27935e657e41ebb97982d6b123136c",
        "SKRR": "0x9081f02876c173d0c69f042959cfd0d61c668b17",
        "ME30": "0xa545c8726bcf4acf840dac521b369911fe2abc8d",
        "CY24": "0x731d879ee2cd4bbf32efef9178d51d5c1441d052",
    }
    out = {"head": head, "lo_block": lo, "results": {}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(first_mint, n, a, lo, head): n for n, a in targets.items()}
        for f in concurrent.futures.as_completed(futs):
            out["results"][futs[f]] = f.result()
    out["elapsed_s"] = round(time.time() - t0, 1)
    print(json.dumps(out, indent=1))
    json.dump(out, open(BASE + "run-2026-11-13-0701-age.json", "w"), indent=1)
if __name__ == "__main__":
    main()
