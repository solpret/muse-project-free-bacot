#!/usr/bin/env python3
"""Run 1531 fix: correct first-mint search for HashDoge (HI must be its scan
first_block 131785022, not window start) + extend PRCAR search lower +
proper name()/symbol() ABI-string decode. Updates verify-new.json in place."""
import json, sys, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed3.bnbchain.org"]
HD = "0x870126112Ef8863F490B518E19A1c79800E6E4BB"
PR = "0x230F661b80DCa58B9C57b49ed0438e16640bEDb4"

def any_mint(addr, lo, hi):
    params = {"blockchain": "bsc", "fromBlock": hex(lo), "toBlock": hex(hi),
              "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": addr}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
    for lg in logs:
        if len(lg.get("topics", [])) == 4:
            return int(lg["blockNumber"], 16)
    return None

def first_mint(addr, lo, hi):
    if any_mint(addr, lo, hi) is None:
        return None
    while lo < hi:
        mid = (lo + hi) // 2
        if any_mint(addr, lo, mid) is not None:
            hi = mid
        else:
            lo = mid + 1
    return lo

def block_ts(n):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(n), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return int(json.load(r)["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def eth_call(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                out = json.load(r)
            if "error" in out:
                return None
            return out["result"]
        except Exception:
            continue
    return None

def decode_str(v):
    if not v or v == "0x":
        return None
    h = v[2:]
    try:
        ln = int(h[64:128], 16)
        return bytes.fromhex(h[128:128 + ln * 2]).decode(errors="replace")
    except Exception:
        return v

res = json.load(open(f"{BASE}/run-2026-11-05-1531-verify-new.json"))
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))

# HashDoge: search [131770000, 131785022] (scan first_block inclusive)
b = first_mint(HD, 131770000, 131785022)
ts = block_ts(b) if b else None
wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat() if ts else None
res["HashDoge_firstMint"] = {"block": b, "ts": ts, "wib": wib,
                             "age_hours": round((now.timestamp() - ts) / 3600, 2) if ts else None,
                             "note": "corrected search range [131770000, scan first_block 131785022]; prior run wrongly capped HI at window start 131784571"}
print("HashDoge firstMint", res["HashDoge_firstMint"], flush=True)
# PRCAR: extend lower [131740000, 131775312] to confirm no earlier mint
b2 = first_mint(PR, 131740000, 131775312)
print("PRCAR earlier-window check [131740000,131775312]:", b2, flush=True)
res["Parking Rush Cars_firstMint"]["lower_extension_check"] = {
    "range": [131740000, 131775312], "earlier_mint_block": b2,
    "note": "None = 131775313 is earliest >= 131740000; mints before 131740000 not checked (contract absent from all scanned windows + snapshot)"}

# proper name/symbol decode
for name, addr in [("HashDoge", HD), ("Parking Rush Cars", PR)]:
    nm = decode_str(eth_call(addr, sel("name()")))
    sy = decode_str(eth_call(addr, sel("symbol()")))
    res[name + "_read"]["name()"] = nm
    res[name + "_read"]["symbol()"] = sy
    print(name, "name=", nm, "symbol=", sy, flush=True)
    # startTime WIB for HashDoge
    if name == "HashDoge":
        st = res[name + "_read"].get("startTime()")
        if isinstance(st, int):
            res[name + "_read"]["startTime_wib"] = datetime.datetime.fromtimestamp(
                st, datetime.timezone(datetime.timedelta(hours=7))).isoformat()

json.dump(res, open(f"{BASE}/run-2026-11-05-1531-verify-new.json", "w"), indent=1)
print("DONE")
