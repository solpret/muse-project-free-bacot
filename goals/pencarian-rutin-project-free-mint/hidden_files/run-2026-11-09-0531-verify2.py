#!/usr/bin/env python3
"""Round-2 verify run 2026-11-09 0531 WIB.
- 0x2CCb... beast: FREE_CAP/freeCount/freeAllowance(user)/mintStart/payout/
  kindLeft/paidCount/name/symbol (proper ABI-string decode).
- First-mint age probes for BOTH contracts via Ankr ankr_getLogs
  (address-filtered, Transfer topic, topic1=zero), binary search on
  'any from-zero log in range'. Block timestamps ONLY via dataseed
  eth_getBlockByNumber (Ankr timestamps are fake).
Writes run-2026-11-09-0531-verify2.json.
"""
import json, subprocess, sys, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def eth_call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def call_int(addr, sig, args=""):
    return to_int(eth_call(addr, sel(sig) + args))

def call_addr(addr, sig):
    v = eth_call(addr, sel(sig))
    if v and len(v) >= 66:
        return "0x" + v[-40:]
    return None

def call_str(addr, sig, args=""):
    v = eth_call(addr, sel(sig) + args)
    try:
        if not v or v == "0x":
            return None
        b = bytes.fromhex(v[2:])
        if len(b) < 64:
            return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None

def block_ts(block):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(block), False]}, timeout=25)
            if isinstance(res, dict) and isinstance(res.get("result"), dict):
                return int(res["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

def any_from_zero_mint(addr, frm, to):
    """True if any Transfer log from zero address exists in [frm,to]."""
    try:
        res = ankr_post("ankr_getLogs", {
            "blockchain": "bsc", "address": addr,
            "fromBlock": str(frm), "toBlock": str(to),
            "topics": [TRANSFER, ZERO_TOPIC],
            "pageSize": 1000,
        }, timeout=55)
        logs = res.get("result", {}).get("logs", [])
        return len(logs) > 0, len(logs)
    except Exception as e:
        return None, str(e)[:150]

def first_mint_block(addr, lo, hi):
    """Binary search first block with a from-zero Transfer log in [lo,hi]."""
    ok, n = any_from_zero_mint(addr, lo, hi)
    if ok is False:
        return None, "no-mints-in-range"
    if ok is None:
        return None, f"probe-error: {n}"
    # invariant: mints exist in [lo,hi]
    while lo < hi:
        mid = (lo + hi) // 2
        ok, n = any_from_zero_mint(addr, lo, mid)
        if ok is None:
            return None, f"probe-error-mid: {n}"
        if ok:
            hi = mid
        else:
            lo = mid + 1
    return lo, "found"

out = {"run": "2026-11-09-0531", "verify2": {}}
BEAST = "0x2CCb3fA957E69AbD46A6651CC1444EF2Ea9bd591"
b = {"address": BEAST}
b["name"] = call_str(BEAST, "name()")
b["symbol"] = call_str(BEAST, "symbol()")
b["FREE_CAP"] = call_int(BEAST, "FREE_CAP()")
b["PAID_CAP"] = call_int(BEAST, "PAID_CAP()")
b["freeCount"] = call_int(BEAST, "freeCount()")
b["paidCount"] = call_int(BEAST, "paidCount()")
b["freeAllowance_user"] = call_int(BEAST, "freeAllowance(address)", enc(USER))
b["mintStart"] = call_int(BEAST, "mintStart()")
b["mintEnd"] = call_int(BEAST, "mintEnd()")
b["TIER1_END"] = call_int(BEAST, "TIER1_END()")
b["payout"] = call_addr(BEAST, "payout()")
b["agentId"] = call_addr(BEAST, "agentId()")
b["tokenURI_5"] = call_str(BEAST, "tokenURI(uint256)", "0" * 63 + "5")
b["tokenURI_1"] = call_str(BEAST, "tokenURI(uint256)", "0" * 63 + "1")
out["verify2"]["beast"] = b
print("BEAST:", json.dumps(b, default=str), flush=True)

CMP = "0xcd1bb8013e924e26ed4131a69304f2969c4f8d28"
c = {"address": CMP}
c["name"] = call_str(CMP, "name()")
c["symbol"] = call_str(CMP, "symbol()")
c["owner"] = call_addr(CMP, "owner()")
c["PRICE"] = call_int(CMP, "PRICE()")
c["FREE_PER_WALLET"] = call_int(CMP, "FREE_PER_WALLET()")
c["MAX_PER_WALLET"] = call_int(CMP, "MAX_PER_WALLET()")
c["freeLeft"] = call_int(CMP, "freeLeft()")
c["freeFor"] = call_int(CMP, "freeFor()")
c["contractURI_str"] = call_str(CMP, "contractURI()")
out["verify2"]["compasyn"] = c
print("COMPASYN:", json.dumps(c, default=str), flush=True)

# --- first-mint age probes ---
for label, addr, lo, hi in [
    ("compasyn", CMP, 131300000, 132459053),
    ("beast", BEAST, 132300000, 132476750),
]:
    print(f"FIRST-MINT {label} range {lo}-{hi}", flush=True)
    fb, note = first_mint_block(addr, lo, hi)
    ts = block_ts(fb) if fb else None
    import datetime
    wib = None
    if ts:
        wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out["verify2"][label + "_first_mint"] = {"block": fb, "note": note, "timestamp": ts, "wib": wib}
    print(f"FIRST-MINT {label}: block={fb} note={note} wib={wib}", flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0531-verify2.json", "w"), indent=1)
print("VERIFY2 DONE")
