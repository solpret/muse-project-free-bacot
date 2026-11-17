#!/usr/bin/env python3
"""Pumpkinfarm leg-3 fast verify: pool/slot fresh + first-mint age via getLogs (dataseed, real block timestamps)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

ADDR = "0x77e38295603a06654a6ed3ed0849e6aa50749963"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
out = {}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(addr, sig, args=None, ep=None):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    eps = [ep] if ep else EPS
    for e in eps:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=e, timeout=8)
            return to_int(res[0])
        except Exception:
            continue
    return None

def call_str(addr, sig, ep=None):
    data = sel(sig)
    for e in (EPS if not ep else [ep]):
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=e, timeout=8)
            raw = res[0]
            if raw and raw != "0x":
                b = bytes.fromhex(raw[2:])
                # string: offset(32)+len(32)+data
                ln = int.from_bytes(b[32:64], "big")
                return b[64:64+ln].decode("utf-8", "replace")
            return None
        except Exception:
            continue
    return None

reads = {}
for sig in ["totalSupply()", "freeClaimed()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()", "PRICE()", "balanceOf(address)"]:
    key = sig.split("(")[0] + ("_user" if "(address)" in sig else "")
    reads[key] = single(ADDR, sig, [USER] if "(address)" in sig else None)
reads["freeLeft_user"] = single(ADDR, "freeLeft(address)", [USER])
reads["freeUsed_user"] = single(ADDR, "freeUsed(address)", [USER])
reads["freeFor_user1"] = single(ADDR, "freeFor(address,uint256)", [USER, 1])
reads["quote_user1"] = single(ADDR, "quote(address,uint256)", [USER, 1])
reads["name"] = call_str(ADDR, "name()")
reads["symbol"] = call_str(ADDR, "symbol()")
out["reads"] = reads

# block number
try:
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)
    cur = int(b[0], 16)
except Exception as e:
    cur = None
    out["block_error"] = str(e)
out["current_block"] = cur

# getLogs: Transfer from zero address, chunked windows backward
import urllib.request
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"
def get_logs(ep, frm, to):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
        "params": [{"address": ADDR, "fromBlock": hex(frm), "toBlock": hex(to),
                    "topics": [TRANSFER_TOPIC, ZERO_TOPIC]}]}).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    if "error" in d:
        raise RuntimeError(str(d["error"])[:200])
    return d.get("result", [])

def block_ts(ep, blk):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
        "params": [hex(blk), False]}).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    return int(d["result"]["timestamp"], 16)

first_block = None
if cur:
    # scan backward in 100k-block windows; stop at first window containing logs, then narrow
    W = 100000
    hi = cur
    found_window = None
    for _ in range(12):
        lo = max(0, hi - W)
        logs = []
        err = None
        for ep in EPS:
            try:
                logs = get_logs(ep, lo, hi)
                err = None
                break
            except Exception as e:
                err = str(e)[:120]
        out.setdefault("scan_windows", []).append({"from": lo, "to": hi, "n_logs": len(logs), "err": err})
        if logs:
            found_window = (lo, hi, logs)
            break
        hi = lo - 1
        if hi <= 0:
            break
    if found_window:
        lo, hi, logs = found_window
        first_block = min(int(l["blockNumber"], 16) for l in logs)
        # narrow: check earlier half of that window for even earlier logs
        lo2 = max(0, lo - W)
        try:
            logs2 = get_logs(EPS[0], lo2, first_block - 1)
            if logs2:
                first_block = min(int(l["blockNumber"], 16) for l in logs2)
                out["narrow_extra"] = len(logs2)
        except Exception as e:
            out["narrow_err"] = str(e)[:120]
        out["first_mint_block"] = first_block
        try:
            ts = block_ts(EPS[0], first_block)
            from datetime import datetime, timezone, timedelta
            wib = timezone(timedelta(hours=7))
            out["first_mint_time_wib"] = datetime.fromtimestamp(ts, wib).strftime("%Y-%m-%d %H:%M:%S WIB")
            out["first_mint_ts"] = ts
        except Exception as e:
            out["first_mint_ts_error"] = str(e)[:120]

print(json.dumps(out, indent=1, default=str))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-08-0604-pumpkin-verify.json", "w"), indent=1)
