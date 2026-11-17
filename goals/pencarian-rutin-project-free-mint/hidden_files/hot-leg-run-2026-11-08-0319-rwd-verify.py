#!/usr/bin/env python3
"""Hot-leg 0319 leg-3 verification: REWARD (RWD) 0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40.
Read-only: single-call state reads + eth_call simulation of mint(0,1) from user wallet + first-mint via Ankr getLogs."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(addr, sig, args=None, ret="int"):
    data = sel(sig)
    if args:
        for a in args:
            data += enc_addr(a) if isinstance(a, str) and a.startswith("0x") else enc_u(a)
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=8)
            if ret == "int":
                return to_int(res[0])
            return res[0]
        except Exception as e:
            last = e
            continue
    return None

def single_str(addr, sig):
    # string return: offset(32) + len(32) + data
    raw = single(addr, sig, ret="raw")
    if not raw or len(raw) < 130:
        return None
    try:
        ln = int(raw[66:130], 16)
        return bytes.fromhex(raw[130:130 + ln * 2]).decode(errors="replace")
    except Exception:
        return None

out = {}
views = [
    ("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
    ("freeMintedTotal", "freeMintedTotal()", None), ("FREE_CAP", "FREE_CAP()", None),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
    ("TIER_FREE", "TIER_FREE()", None), ("TIER_PAID", "TIER_PAID()", None),
    ("PRICE_FREE_USD", "PRICE_FREE_USD()", None), ("PRICE_PAID_USD", "PRICE_PAID_USD()", None),
    ("quote_tier0", "quote(uint8)", [0]), ("quote_tier1", "quote(uint8)", [1]),
    ("tierMinted0", "tierMinted(uint8)", [0]), ("tierMinted1", "tierMinted(uint8)", [1]),
    ("mintActive", "mintActive()", None),
    ("balanceOf_user", "balanceOf(address)", [USER]),
    ("mintedCount_user", "mintedCount(address)", [USER]),
    ("freeMinted_user", "freeMinted(address)", [USER]),
    ("isAgent_user", "isAgent(address)", [USER]),
    ("bnbPrice", "bnbPrice()", None),
]
for name, sig, args in views:
    out[name] = single(ADDR, sig, args)
out["name"] = single_str(ADDR, "name()")
out["symbol"] = single_str(ADDR, "symbol()")
out["baseURI"] = single_str(ADDR, "baseURI()")
out["owner"] = single(ADDR, "owner()", ret="raw")
out["agentRegistry"] = single(ADDR, "agentRegistry()", ret="raw")
out["claimContract"] = single(ADDR, "claimContract()", ret="raw")
out["priceFeed"] = single(ADDR, "priceFeed()", ret="raw")

# --- eth_call simulation: mint(0,1) value 0 FROM user wallet (read-only) ---
mint_data = sel("mint(uint8,uint256)") + enc_u(0) + enc_u(1)
sim = {"ok": None, "error": None}
for ep in EPS:
    try:
        res = batch([("eth_call", [{"to": ADDR, "from": USER, "value": "0x0", "data": mint_data}, "latest"])], endpoint=ep, timeout=10)
        sim["ok"] = True
        sim["return"] = res[0]
        sim["endpoint"] = ep
        break
    except Exception as e:
        sim["error"] = str(e)[:400]
        sim["endpoint"] = ep
        # try next endpoint to confirm
        continue
out["sim_mint01_value0_from_user"] = sim

# --- first mint via Ankr getLogs: Minted event ---
try:
    from ankr import ankr_post
    topic0 = "0x" + keccak.new(digest_bits=256, data=b"Minted(uint256,address,bool,uint8,uint8)").hexdigest()
    out["minted_topic0"] = topic0
    b = batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)
    head = int(b[0], 16)
    out["head_block"] = head
    params = {"blockchain": "bsc", "fromBlock": hex(head - 300000), "toBlock": hex(head),
              "address": ADDR.lower(), "topics": [topic0], "pageSize": 1000, "decodeLogs": False}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = body.get("logs", []) if isinstance(body, dict) else []
    out["ankr_logs_n"] = len(logs)
    out["ankr_error"] = body.get("error") if isinstance(body, dict) and body.get("error") else None
    if logs:
        first = min(logs, key=lambda l: int(l.get("blockNumber", "0x0"), 16))
        fb = int(first["blockNumber"], 16)
        out["first_mint_block"] = fb
        out["first_mint_tx"] = first.get("transactionHash")
        # block timestamp via dataseed (NOT Ankr - fake timestamps)
        for ep in EPS:
            try:
                blk = batch([("eth_getBlockByNumber", [hex(fb), False])], endpoint=ep, timeout=10)
                ts = int(blk[0]["timestamp"], 16)
                out["first_mint_ts"] = ts
                from datetime import datetime, timezone, timedelta
                out["first_mint_wib"] = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
                out["first_mint_block_endpoint"] = ep
                break
            except Exception as e:
                out["first_mint_ts_error"] = str(e)[:200]
                continue
        out["first_mint_log_sample"] = {k: first.get(k) for k in ("blockNumber", "transactionHash", "topics")}
except Exception as e:
    out["ankr_exception"] = f"{type(e).__name__}: {e}"

json.dump(out, open(f"{BASE}/hot-leg-2026-11-08-0319-rwd-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
