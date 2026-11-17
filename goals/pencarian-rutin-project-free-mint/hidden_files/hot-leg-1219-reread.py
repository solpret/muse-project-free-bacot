#!/usr/bin/env python3
"""hot-leg 2026-11-09 12:19 re-read: same 30 priority items as the 12:09 run
(block 132527092 baseline) + Lambdwyn (S1 in snapshot) + DigDown (bridge,
in snapshot). Raw JSON-RPC batches via nodereal (per-item errors isolated).
Read-only. Writes hot-leg-2026-11-09-1219-reread.json + prints diffs."""
import json, subprocess, sys
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def enc_addr(a):
    return a.lower().replace("0x", "").rjust(64, "0")

def enc_uint(n):
    return format(n, "064x")

NOARG = ["totalSupply", "totalMinted", "totalMints", "freeMinted", "freeClaimed",
         "freeMintedTotal", "freeLeft", "freeUsed", "FREE_CAP", "FREE_SUPPLY",
         "FREE_SHARES", "FREE_QUOTA", "FREE_PER_WALLET", "remainingFree",
         "MAX_SUPPLY", "MAX_FREE", "sharesMinted", "sold", "phase", "launched",
         "soldOut", "closed", "finalized", "mintOpen", "mintActive"]
ADDRARG = ["balanceOf", "mintedBy", "freeClaimed", "freeLeft", "freeUsed",
           "freeCount", "freeMinted", "mintedCount", "freeAvailable",
           "hasMinted", "quotaOf", "freeTakenBy", "priceFor"]
ADDRUINT = ["quote", "freeFor"]

def calldata(field):
    """field like 'totalSupply', 'balanceOf_user', 'quote_user1' -> hex data or None"""
    if field in ("address", "_batch_fail"):
        return None
    if field.endswith("_user1"):
        fn = field[:-6]
        if fn in ADDRUINT:
            return sel(f"{fn}(address,uint256)") + enc_addr(USER) + enc_uint(1)
        return None
    if field.endswith("_user"):
        fn = field[:-5]
        if fn in ADDRARG:
            return sel(f"{fn}(address)") + enc_addr(USER)
        return None
    if field in NOARG:
        return sel(f"{field}()")
    return None

def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {"_curl_error": p.stdout[:200] + p.stderr[:200]}

def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"):
        return None
    try:
        return int(r, 16)
    except Exception:
        return None

def main():
    prev = json.load(open(BASE + "hot-leg-2026-11-09-1209-reread.json"))
    items = prev["items"]
    # add Lambdwyn + DigDown (bridge, in snapshot)
    items["Lambdwyn"] = {"address": "0xca7a3faa22ac4abbf5528b41ac7d12b28651aa6b",
                         "totalSupply": None, "freeClaimed": None, "FREE_SUPPLY": None,
                         "freeLeft_user": None, "freeUsed_user": None, "mintedBy_user": None,
                         "quote_user1": None, "mintOpen": None, "balanceOf_user": None}
    items["DigDown"] = {"address": "0xf464550f1d744793893c0ce09b89269ed726d796",
                        "totalSupply": None, "freeClaimed": None, "balanceOf_user": None,
                        "mintedBy_user": None, "mintOpen": None}
    # build calls
    jobs = []  # (item, field, to, data)
    for name, entry in items.items():
        for field in entry:
            data = calldata(field)
            if data:
                jobs.append((name, field, entry["address"], data))
    out = {"block": None, "items": {}}
    # current block
    p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                        "-H", "Content-Type: application/json",
                        "--data", '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                       capture_output=True, text=True)
    try:
        out["block"] = int(json.loads(p.stdout)["result"], 16)
    except Exception:
        out["block"] = None
    # batch in chunks of 25
    results = {}
    for i in range(0, len(jobs), 25):
        chunk = jobs[i:i + 25]
        resp = run_batch([(to, data) for (_, _, to, data) in chunk])
        if isinstance(resp, dict) and "_curl_error" in resp:
            for (name, field, to, data) in chunk:
                results[(name, field)] = None
            continue
        if isinstance(resp, dict):
            resp = [resp]
        for j, item in enumerate(resp):
            name, field, to, data = chunk[j]
            if isinstance(item, dict) and "result" in item:
                results[(name, field)] = decode(item["result"])
            else:
                results[(name, field)] = None
    for name, entry in items.items():
        row = {"address": entry["address"]}
        for field in entry:
            if field == "address":
                continue
            row[field] = results.get((name, field))
        out["items"][name] = row
    # diff vs 12:09 baseline
    diffs = []
    for name, row in out["items"].items():
        base = prev["items"].get(name, {})
        for field, val in row.items():
            if field == "address":
                continue
            old = base.get(field)
            if old is None and val is None:
                continue
            if old != val:
                diffs.append({"item": name, "field": field, "old": old, "new": val})
    out["diffs_vs_1209"] = diffs
    json.dump(out, open(BASE + "hot-leg-2026-11-09-1219-reread.json", "w"), indent=1)
    print("block:", out["block"], "calls:", len(jobs))
    print("DIFFS:", json.dumps(diffs, indent=1))
    print("NULLS:", json.dumps({f"{n}.{f}": v for (n, f), v in results.items() if v is None}))

if __name__ == "__main__":
    main()
