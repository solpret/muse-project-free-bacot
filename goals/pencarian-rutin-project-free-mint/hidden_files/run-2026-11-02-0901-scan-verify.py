#!/usr/bin/env python3
"""Pre-window + first-mint verification for 6 scan first-seen agent-shaped candidates, run 2026-11-02 09:01 WIB.
Decisive: ANY Transfer-from-zero mint BEFORE scan window start 131158006? >0 -> continuation, checked-only.
Ankr getLogs as MODULE."""
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
WINDOW_START = 131158006
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            ts = int(b["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: pass
    return None
def logs_range(C, frm, to):
    logs = []; tok = None; err = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": C}
        if tok: params["pageToken"] = tok
        try: body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err = str(e)[:200]; break
        res = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend([l for l in res.get("logs", []) if l.get("address", "").lower() == C.lower()])
        tok = res.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
        time.sleep(1)
    return logs, err, bool(tok)
CANDS = {
 "Holotron": "0xA3bdab7105371D05Def2162Fca700235477DD1F8",
 "Agent 404": "0x16C3fb550CE75F90E8CBA8EE4EfD8fee820fbdD1",
 "Banshiko": "0x7e395317a0B57F63c729C248a1558Eb93d86dcA7",
 "Saturnelle": "0x79B0f57b631F3dF1781433a95bC8C2219792AF74",
 "Mobaiko": "0x387A03820eA1b6463DB070dbC9b62a8215D1420c",
 "Mantikoo": "0x0B9FF9e1A7C2b73a86344d314A38c9fc5B102833",
}
out = {}
for name, C in CANDS.items():
    pre, err, trunc = logs_range(C, 131060000, WINDOW_START - 1)
    first = None
    if not pre:
        # first mint in-window: fetch window logs to find first block
        w, werr, wtrunc = logs_range(C, WINDOW_START, 131160005)
        if w:
            fb = min(int(l["blockNumber"], 16) for l in w)
            first = {"block": fb, "wib": block_ts(fb), "count_window": len(w),
                     "minters": len({l["topics"][2] for l in w if len(l.get("topics", [])) > 2})}
        else:
            first = {"error": werr}
    st = {}
    for fn, arg in [("totalSupply()", ""), ("totalMinted()", ""), ("freeClaimed()", ""), ("freeMinted()", ""),
                    ("FREE_SUPPLY()", ""), ("freeSupply()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""),
                    ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
                    ("balanceOf(address)", enc_addr(USER)[2:]), ("AGENT_ID()", ""), ("REGISTRY()", "")]:
        st[fn] = iv(call(C, sel(fn) + arg))
    q = call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    st["quote_user_1_raw"] = q
    out[name] = {"address": C, "pre_window_logs": len(pre), "pre_error": err, "pre_truncated": trunc,
                 "first_mint": first, "state": st}
    print(name, json.dumps(out[name], indent=1))
json.dump(out, open(B + "run-2026-11-02-0901-scan-verify.json", "w"), indent=1)
