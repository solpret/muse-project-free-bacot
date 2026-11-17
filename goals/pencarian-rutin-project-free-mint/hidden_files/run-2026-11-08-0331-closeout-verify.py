#!/usr/bin/env python3
"""Parent closeout verification run 0331 WIB 2026-11-08 (read-only).
1. BYTE sale 0x98199FDe995eA29E3BC960B338A282a7E3FeF746: fresh free pool/quote/slot
   + first-mint block via binary search on cardsSold() at block, + block timestamp
   via dataseed (Ankr timestamps are fake - never use Ankr for block time).
2. Vorn/Cinder/Mira: name/symbol/totalSupply + registry-bytes check in bytecode.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"  # agent wallet (baw)
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(addr, sig, args=None, block="latest", ret="int"):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, block])], endpoint=ep, timeout=10)
            if ret == "int": return to_int(res[0])
            return res[0]
        except Exception:
            continue
    return None

def call_str(addr, sig, block="latest"):
    raw = call(addr, sig, block=block, ret="raw")
    if not raw or len(raw) < 130: return None
    try:
        ln = int(raw[66:130], 16)
        return bytes.fromhex(raw[130:130 + ln * 2]).decode(errors="replace")
    except Exception:
        return None

def get_code(addr):
    for ep in EPS:
        try:
            res = batch([("eth_getCode", [addr, "latest"])], endpoint=ep, timeout=10)
            return res[0]
        except Exception:
            continue
    return None

def block_ts(blocknum):
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blocknum), False])], endpoint=ep, timeout=10)
            b = res[0]
            return to_int(b.get("timestamp")) if isinstance(b, dict) else None
        except Exception:
            continue
    return None

def head_block():
    for ep in EPS:
        try:
            res = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
            return to_int(res[0])
        except Exception:
            continue
    return None

out = {"run": "0331-closeout-verify", "ts_wib": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 7*3600))}
head = head_block()
out["head"] = head

# ---- 1. BYTE ----
BYTE_SALE = "0x98199FDe995eA29E3BC960B338A282a7E3FeF746"
BYTE_TOK = "0xCA19f39A451e43698E71F25279c01A809C37fe7c"
byte = {}
for name, sig, args in [
    ("cardsSold", "cardsSold()", None),
    ("freeCardsRemaining", "freeCardsRemaining()", None),
    ("pricePerShare", "pricePerShare()", None),
    ("quote_user1", "quote(address,uint256)", [USER, 1]),
    ("freeClaimed_user", "freeClaimed(address)", [USER]),
    ("quotaLeft_user", "quotaLeft(address)", [USER]),
    ("maxPerTx", "maxPerTx()", None),
]:
    byte[name] = call(BYTE_SALE, sig, args)
byte["token_totalSupply"] = call(BYTE_TOK, "totalSupply()")
byte["token_name"] = call_str(BYTE_TOK, "name()")
byte["token_symbol"] = call_str(BYTE_TOK, "symbol()")
out["BYTE"] = byte

# Binary search first block where cardsSold > 0. Lower bound: 2026-11-04 00:00 WIB
# ~ head minus 4 days of blocks (~0.45s/block -> ~768k blocks). Use head-800000.
lo, hi = max(0, (head or 132267263) - 800000), (head or 132267263)
# invariant: cardsSold(lo) == 0/None (not yet launched), cardsSold(hi) > 0
first_gt = None
steps = 0
while lo < hi and steps < 40:
    mid = (lo + hi) // 2
    v = call(BYTE_SALE, "cardsSold()", block=hex(mid))
    steps += 1
    if v is None or v == 0:
        lo = mid + 1
    else:
        hi = mid
        first_gt = mid
if first_gt is not None:
    ts = block_ts(first_gt)
    import datetime
    wib = datetime.datetime.utcfromtimestamp(ts) + datetime.timedelta(hours=7) if ts else None
    out["BYTE"]["first_mint_block"] = first_gt
    out["BYTE"]["first_mint_ts"] = ts
    out["BYTE"]["first_mint_wib"] = str(wib) if wib else None
    out["BYTE"]["binary_search_steps"] = steps
    # age at run time 2026-11-08 03:31 WIB
    run_ts = 1793422260  # placeholder replaced below
    import datetime as dt
    run_dt = dt.datetime(2026, 11, 8, 3, 31, tzinfo=dt.timezone(dt.timedelta(hours=7)))
    if wib:
        age_h = (run_dt.replace(tzinfo=None) - wib).total_seconds() / 3600
        out["BYTE"]["age_hours_at_0331"] = round(age_h, 2)
else:
    out["BYTE"]["first_mint_block"] = None
    out["BYTE"]["binary_search_steps"] = steps

# ---- 2. Vorn / Cinder / Mira ----
for label, addr in [
    ("Vorn", "0x978c968a371f6adf98abe32915fae09111d11293"),
    ("Cinder", "0xf9876bb12dec4f15faed042525effdb75b3e5a41"),
    ("Mira", "0xa545c7aa04885bbd9cf7ae450ae52c40dcb9e449"),
]:
    code = get_code(addr)
    item = {
        "address": addr,
        "name": call_str(addr, "name()"),
        "symbol": call_str(addr, "symbol()"),
        "totalSupply": call(addr, "totalSupply()"),
        "totalMinted": call(addr, "totalMinted()"),
        "code_len": len(code) if code else None,
        "registry_bytes": (REGISTRY in code.lower()) if code else None,
    }
    out[label] = item

with open(f"{BASE}/run-2026-11-08-0331-closeout-verify.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
