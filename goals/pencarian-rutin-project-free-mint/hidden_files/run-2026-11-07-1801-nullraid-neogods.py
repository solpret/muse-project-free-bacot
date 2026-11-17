#!/usr/bin/env python3
"""Verify NULLRAID + NeoGods for run 1801 (Boltbook leg-2 flag).
Read-only: contract views, first-mint via Ankr getLogs, contractURI.
Writes run-2026-11-07-1801-nullraid-neogods.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
from fast_rpc import batch
from ankr import ankr_post

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
NULLRAID = "0xdec01cdfb41e7871fb7ca7b12b1572ce292743c0"
NEOGODS = "0x2746bb6c6ec8fc968b8f0159618af1bb30ab593d"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return res[0]
        except Exception:
            continue
    return None

def call_str(addr, sig):
    raw = call(addr, sig)
    if not raw or raw == "0x": return None
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            if 0 < ln <= len(b) - 64:
                return b[64:64+ln].decode("utf-8", "replace")
        if len(b) == 32:
            return b.rstrip(b"\x00").decode("utf-8", "replace") or None
    except Exception:
        return None
    return raw

out = {"block": None}
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=10)[0], 16)
except Exception as e:
    print("BLOCK FAIL", e, flush=True)

def first_mint(addr, lo, hi):
    """Earliest Transfer-from-zero for addr in [lo,hi]; pageSize 1000.
    Returns (block, txhash, count) or (None,None,count)."""
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(lo),
            "toBlock": hex(hi), "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, ZERO, None, None], "address": addr}, timeout=30)
    except Exception as e:
        print(f"  getLogs {addr[:10]} {lo}-{hi} FAIL {e}", flush=True)
        return None, None, None
    logs = body.get("result", {}).get("logs", [])
    # ankr topics filter may ignore address param; filter locally
    logs = [l for l in logs if l.get("address", "").lower() == addr.lower()]
    if not logs:
        return None, None, 0
    logs.sort(key=lambda l: int(l.get("blockNumber", "0x0"), 16))
    first = logs[0]
    return int(first["blockNumber"], 16), first.get("transactionHash"), len(logs)

def block_ts(blk):
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=10)
            return int(res[0]["timestamp"], 16)
        except Exception:
            continue
    return None

# --- NULLRAID ---
print("== NULLRAID", NULLRAID, flush=True)
nr = {}
for sig in ["phase()", "totalSupply()", "freeMints()", "FREE_CAP()", "MAX_SUPPLY()",
            "price()", "paused()", "remainingInPhase()"]:
    nr[sig] = to_int(call(NULLRAID, sig))
    print(f"  {sig} = {nr[sig]}", flush=True)
for sig in ["freeClaimed(address)", "quote(address,uint256)"]:
    try:
        if "quote" in sig:
            # quote(address,uint256): user,1
            data = sel(sig) + enc(USER) + "1".rjust(64, "0")
            raw = None
            for ep in EPS:
                try:
                    raw = batch([("eth_call", [{"to": NULLRAID, "data": data}, "latest"])], endpoint=ep, timeout=10)[0]
                    break
                except Exception:
                    continue
            nr[sig] = raw
        else:
            nr[sig] = to_int(call(NULLRAID, sig, USER))
    except Exception as e:
        nr[sig] = f"ERR {e}"
    print(f"  {sig} = {nr[sig]}", flush=True)
nr["contractURI"] = call_str(NULLRAID, "contractURI()")
print("  contractURI =", nr["contractURI"], flush=True)
# Post-mint verification (minted #503 post-run-1731): freeClaims(user) must be 1, balanceOf(user) 1, ownerOf(503)=user
nr["freeClaims(address)"] = to_int(call(NULLRAID, "freeClaims(address)", USER))
nr["balanceOf(address)"] = to_int(call(NULLRAID, "balanceOf(address)", USER))
_raw_owner = call(NULLRAID, "ownerOf(uint256)", None) if False else None
import subprocess
print(f"  freeClaims(user) = {nr['freeClaims(address)']}", flush=True)
print(f"  balanceOf(user) = {nr['balanceOf(address)']}", flush=True)
# ownerOf(503) raw (address return, 32-byte)
_data = sel("ownerOf(uint256)") + "503".rjust(64, "0")
_raw = None
for _ep in EPS:
    try:
        _raw = batch([("eth_call", [{"to": NULLRAID, "data": _data}, "latest"])], endpoint=_ep, timeout=10)[0]
        break
    except Exception:
        continue
nr["ownerOf(503)"] = ("0x" + _raw[-40:]) if _raw and len(_raw) >= 42 else _raw
print(f"  ownerOf(503) = {nr['ownerOf(503)']} (user={USER})", flush=True)
head = out["block"]
fb, ftx, n = first_mint(NULLRAID, 132100000, head)
nr["firstMintBlock"] = fb
nr["firstMintTx"] = ftx
nr["mintsInRange"] = n
print(f"  first mint block={fb} tx={ftx} count-in-range={n}", flush=True)
if fb:
    ts = block_ts(fb)
    nr["firstMintTs"] = ts
    import datetime
    if ts:
        print("  first mint time WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"), flush=True)
out["nullraid"] = nr

# --- NEOGODS ---
print("== NEOGODS", NEOGODS, flush=True)
ng = {}
for sig in ["totalSupply()", "MAX_SUPPLY()", "mintOpen()", "price()"]:
    ng[sig] = to_int(call(NEOGODS, sig))
    print(f"  {sig} = {ng[sig]}", flush=True)
for sig in ["freeClaimed(address)", "freeMinted()", "FREE_SUPPLY()"]:
    ng[sig] = to_int(call(NEOGODS, sig, USER)) if "address" in sig else to_int(call(NEOGODS, sig))
    print(f"  {sig} = {ng[sig]}", flush=True)
ng["contractURI"] = call_str(NEOGODS, "contractURI()")
print("  contractURI =", ng["contractURI"], flush=True)
fb2, ftx2, n2 = first_mint(NEOGODS, 132100000, head)
ng["firstMintBlock"] = fb2
ng["firstMintTx"] = ftx2
ng["mintsInRange"] = n2
print(f"  first mint block={fb2} tx={ftx2} count-in-range={n2}", flush=True)
if fb2:
    ts = block_ts(fb2)
    ng["firstMintTs"] = ts
    import datetime
    if ts:
        print("  first mint time WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"), flush=True)
out["neogods"] = ng
json.dump(out, open(f"{BASE}/run-2026-11-07-1801-nullraid-neogods.json", "w"), indent=1)
print("DONE", flush=True)
