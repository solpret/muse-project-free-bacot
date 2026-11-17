#!/usr/bin/env python3
"""First-mint + state verification for 2 Sourcify new agent-shaped NFTs, run 2026-11-02 09:01 WIB.
Decisive question: first Transfer-from-zero mint time (from block 131060000). Ankr getLogs as MODULE."""
import sys, time, json, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
def dec_str(v):
    if not v or not v.startswith("0x"): return None
    raw = bytes.fromhex(v[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64: return raw[64:64+ln].decode("utf-8", "replace")
        except Exception: pass
    return None
def head():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            ts = int(b["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: pass
    return None
out = {"head": head()}
for C in ["0x2a91b304eE74162007730CF1da24C1d8C137c627", "0x259b5Da3f44a44C89bcA5EE2297582c41c758d0F"]:
    logs = []; tok = None; err = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(131060000), "toBlock": hex(out["head"]),
                  "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": C}
        if tok: params["pageToken"] = tok
        try: body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err = str(e)[:200]; break
        res = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend([l for l in res.get("logs", []) if l.get("address", "").lower() == C.lower()])
        tok = res.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
        time.sleep(1)
    first = None
    if logs:
        fb = min(int(l["blockNumber"], 16) for l in logs)
        first = {"block": fb, "wib": block_ts(fb), "count_in_range": len(logs),
                 "minters": len({l["topics"][2] for l in logs if len(l.get("topics", [])) > 2})}
    st = {}
    for fn, arg in [("name()", ""), ("symbol()", ""), ("totalSupply()", ""), ("freeClaimed()", ""),
                    ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""),
                    ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
                    ("balanceOf(address)", enc_addr(USER)[2:])]:
        v = call(C, sel(fn) + arg)
        st[fn] = dec_str(v) if fn in ("name()", "symbol()") else iv(v)
    q = call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    st["quote_user_1_raw"] = q
    out[C] = {"first_mint": first, "state": st, "logs_error": err, "truncated": bool(tok)}
    print(C, json.dumps(out[C], indent=1))
json.dump(out, open(B + "run-2026-11-02-0901-sourcify-verify.json", "w"), indent=1)
