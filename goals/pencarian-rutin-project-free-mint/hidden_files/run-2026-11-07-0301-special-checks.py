#!/usr/bin/env python3
"""Special checks run 2026-11-07 0301 WIB (on-chain leg, read-only):
- Jager Agent 0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27 (early lead run 0201/backfill)
- HUNT PASS 0x885128Cf234c768F1353e2C1432D55873C6b67dD (early lead backfill)
- AGENT888 0xAe9230F154F7fC38edeFe6404cE1e37478DAa6AE first-mint verification
  (first Transfer-from-zero in scan window; block timestamp via eth_getBlockByNumber)
Never preview/mint/approve/sign.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc.publicnode.com/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def call(addr, sig, ep_idx=0):
    data = sel(sig)
    if "(address)" in sig: data += enc(USER)
    elif "(address,uint256)" in sig: data += enc(USER) + enc_u(1)
    for i in range(len(EPS)):
        ep = EPS[(ep_idx + i) % len(EPS)]
        try:
            return _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], 10, retries=0)
        except Exception as e:
            last = f"ERROR: {e}"
    return last

def read(addr, views):
    out = {"contract": addr}
    for sig in views:
        r = call(addr, sig)
        out[sig] = r
        time.sleep(0.12)
    return out

JAGER_AGENT = "0xD8EBDDE362B0a72F7D61b5eD990742B940E30D27"
HUNT = "0x885128Cf234c768F1353e2C1432D55873C6b67dD"
VIEWS_JA = ["name()", "symbol()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()",
            "FREE_SUPPLY()", "freeSupply()", "freeMinted()", "freeClaimed()",
            "mintOpen()", "owner()", "freeClaimed(address)", "freeMintCount(address)",
            "mintedBy(address)", "balanceOf(address)"]
VIEWS_HUNT = ["name()", "symbol()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()",
              "FREE_SUPPLY()", "freeMinted()", "mintOpen()", "mintedBy(address)",
              "balanceOf(address)"]

try:
    blk = int(_single(EPS[0], "eth_blockNumber", [], 10, retries=0), 16)
except Exception:
    blk = None

ja = read(JAGER_AGENT, VIEWS_JA); ja["_block"] = blk
hunt = read(HUNT, VIEWS_HUNT); hunt["_block"] = blk
json.dump(ja, open(f"{BASE}/run-2026-11-07-0301-jageragent-check.json", "w"), indent=1)
json.dump(hunt, open(f"{BASE}/run-2026-11-07-0301-huntpass-check.json", "w"), indent=1)
print("JAGER-AGENT", {k: (to_int(v) if isinstance(v, str) and v.startswith("0x") else v) for k, v in ja.items() if k in ("totalMinted()", "MAX_SUPPLY()", "freeMinted()", "balanceOf(address)", "owner()", "_block")})
print("HUNT", {k: (to_int(v) if isinstance(v, str) and v.startswith("0x") else v) for k, v in hunt.items() if k in ("totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()", "balanceOf(address)", "_block")})

# AGENT888 first-mint verification: Transfer from zero, contract filter, window 132069175-132070174
AGENT888 = "0xAe9230F154F7fC38edeFe6404cE1e37478DAa6AE"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
out888 = {"contract": AGENT888, "window": [132069175, 132070174]}
try:
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132069175),
        "toBlock": hex(132070174), "pageSize": 1000, "decodeLogs": False,
        "topics": [TRANSFER, ZERO]}, timeout=30)
    logs = [l for l in body.get("result", {}).get("logs", [])
            if l.get("address", "").lower() == AGENT888.lower()]
    logs.sort(key=lambda l: int(l.get("blockNumber", "0x0"), 16))
    out888["first_mint_logs"] = [
        {"block": int(l["blockNumber"], 16), "tx": l.get("transactionHash"),
         "to": "0x" + l["topics"][2][-40:], "tokenId": int(l["topics"][3], 16)}
        for l in logs]
    out888["mint_count_in_window"] = len(logs)
    if logs:
        first_blk = int(logs[0]["blockNumber"], 16)
        out888["first_block"] = first_blk
        b = _single(EPS[0], "eth_getBlockByNumber", [hex(first_blk), False], 10, retries=0)
        ts = int(b["timestamp"], 16)
        out888["first_block_timestamp"] = ts
        import datetime
        out888["first_block_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
except Exception as e:
    out888["error"] = str(e)
# Fresh views for AGENT888
v888 = read(AGENT888, ["name()", "symbol()", "totalSupply()", "totalMinted()", "MAX_SUPPLY()",
                       "FREE_SUPPLY()", "freeMinted()", "mintOpen()", "price()", "PRICE()",
                       "owner()", "balanceOf(address)"])
out888["views"] = v888
out888["_block"] = blk
json.dump(out888, open(f"{BASE}/run-2026-11-07-0301-agent888-check.json", "w"), indent=1)
print("AGENT888", json.dumps({k: out888.get(k) for k in ("first_block", "first_block_wib", "mint_count_in_window")}, indent=1))
print("AGENT888 views", {k: (to_int(v) if isinstance(v, str) and v.startswith("0x") else v) for k, v in v888.items() if k in ("totalSupply()", "totalMinted()", "MAX_SUPPLY()", "balanceOf(address)")})
print("DONE")
