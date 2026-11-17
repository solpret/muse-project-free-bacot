#!/usr/bin/env python3
"""Parent triage run 2131 (v2): SHACHO CLUB 0x26E009350Ef80cb542785d57c27c686a582bf605
+ Jinchan free-pool check. Uses the proven 2031 firstmint pattern:
ankr_getLogs with blockchain/pageSize/decodeLogs, 20k-block chunks walking back,
logs under body['result']['logs'], 4-topic Transfer filter. Timestamps via
dataseed eth_getBlockByNumber (Ankr timestamps are fake). Read-only."""
import sys, json, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SHACHO = "0x26E009350Ef80cb542785d57c27c686a582bf605"
JINCHAN = "0xccc127D1A7Ef1e385757784a9878F7279BF3B19D"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=8, retries=0)
            if isinstance(out, dict) and "result" in out: return out["result"]
            if isinstance(out, dict) and "error" in out: return None
        except Exception: continue
    return None
def call_u(addr, sig, args=""):
    return to_int(call(addr, sel(sig) + args))
def call_s(addr, sig):
    r = call(addr, sel(sig))
    if not r: return None
    try:
        b = bytes.fromhex(r[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode()
    except Exception: return r
def head_block():
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}, timeout=10, retries=0)
            return int(r["result"], 16)
        except Exception: continue
    return None
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return ts, datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None, None

def first_mint(addr, head):
    earliest = None; total = 0; chunks = 0; empty_after = 0
    CH = 20000; frm = head
    while frm > head - 384000:
        to = frm; frm = max(0, frm - CH + 1); chunks += 1
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "address": addr, "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            return {"error": str(e)[:200], "earliest_block": earliest, "logs": total, "chunks": chunks}
        logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
        n4 = 0
        for lg in logs:
            if len(lg.get("topics", [])) == 4:
                blk = int(lg["blockNumber"], 16); total += 1; n4 += 1
                if earliest is None or blk < earliest: earliest = blk
        print(f"  chunk {frm}-{to}: {n4} mints, earliest so far {earliest}", flush=True)
        if earliest is not None and to < earliest:
            if n4 == 0:
                empty_after += 1
                if empty_after >= 3: break
            else:
                empty_after = 0
        time.sleep(1.0)
    return {"earliest_block": earliest, "logs": total, "chunks": chunks,
            "empty_chunks_after_earliest": empty_after, "walked_to_block": frm}

res = {"shacho": {"address": SHACHO}, "jinchan": {"address": JINCHAN}}
sh = res["shacho"]
for key, sig, args, kind in [
    ("owner", "owner()", "", "addr"), ("name", "name()", "", "str"),
    ("symbol", "symbol()", "", "str"), ("totalSupply", "totalSupply()", "", "u"),
    ("freeLeft", "freeLeft()", "", "u"), ("freeSupply", "freeSupply()", "", "u"),
    ("price", "price()", "", "u"), ("agentIds", "agentIds()", "", "addr"),
    ("freeOf_user", "freeOf(address)", enc_addr(USER), "u"),
    ("costOf_user_1", "costOf(address,uint256)", enc_addr(USER) + (1).to_bytes(32, "big").hex(), "u"),
    ("mintedBy_user", "mintedBy(address)", enc_addr(USER), "u"),
    ("mintsLeft_user", "mintsLeft(address)", enc_addr(USER), "u"),
]:
    try:
        if kind == "u":
            sh[key] = call_u(SHACHO, sig, args)
        elif kind == "str":
            sh[key] = call_s(SHACHO, sig)
        else:
            r = call(SHACHO, sel(sig) + args)
            sh[key] = ("0x" + r[-40:]) if r else None
    except Exception as e:
        sh[key] = f"ERROR {e}"[:120]
    print("  shacho", key, "=", sh[key], flush=True)
sh["agentIds_is_registry"] = (sh.get("agentIds") or "").lower() == REGISTRY

head = head_block()
print("HEAD", head, flush=True)
if head:
    fm = first_mint(SHACHO, head)
    sh["first_mint"] = fm
    if fm.get("earliest_block"):
        ts, wib = block_time_wib(fm["earliest_block"])
        sh["first_mint_block"] = fm["earliest_block"]
        sh["first_mint_ts"] = ts
        sh["first_mint_wib"] = wib
        print("FIRST MINT:", fm["earliest_block"], wib, flush=True)

jc = res["jinchan"]
for key, sig in [("totalMinted", "totalMinted()"), ("FREE_SUPPLY", "FREE_SUPPLY()"),
                 ("freeMinted", "freeMinted()"), ("freeClaimed", "freeClaimed()"),
                 ("freeLeft", "freeLeft()"), ("freeSupply", "freeSupply()"),
                 ("mintOpen", "mintOpen()")]:
    jc[key] = call_u(JINCHAN, sig)
    print("  jinchan", key, "=", jc[key], flush=True)

json.dump(res, open(BASE + "/run-2026-11-08-2131-shacho-triage.json", "w"), indent=1)
print("WROTE run-2026-11-08-2131-shacho-triage.json", flush=True)
