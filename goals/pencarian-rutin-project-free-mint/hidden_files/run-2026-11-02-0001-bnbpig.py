#!/usr/bin/env python3
"""00:01 run: verify BNBPIG (Boltbook lead) + Oathbots first-mint check. Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:150]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        sig = name.replace("quote1(", "quote(").replace("quote0(", "quote(")
        val, err = call(to, sel(sig) + arg)
        try: iv = int(val, 16) if val else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": val, "error": err if val is None else None}
    return out
def words(val):
    if not val: return None
    b = bytes.fromhex(val[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
SALE = "0xfd3d4e0d7a81534addd11f96fdd8008f942097f9"
TOK = "0x936b97cd42f482ef96c7903448e2522dc9e1bd4f"
tests = [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_SHARES()", ""),
    ("MAX_FREE()", ""), ("mintingOpen()", ""), ("poolOpen()", ""),
    ("freeAvailable(address)", enc_addr(USER)[2:]), ("freeClaimed(address)", enc_addr(USER)[2:]),
    ("mintedBy(address)", enc_addr(USER)[2:]), ("hasAgentId(address)", enc_addr(USER)[2:]),
    ("paidBy(address)", enc_addr(USER)[2:]), ("paidRemainingFor(address)", enc_addr(USER)[2:]),
    ("quote1(uint256)", enc_uint(1)[2:]), ("agentId()", ""), ("registry()", "")]
res = {"sale": collect(SALE, tests)}
res["sale_quote0"] = collect(SALE, [("quote0(uint256)", enc_uint(0)[2:])])
res["token"] = collect(TOK, [("name()", ""), ("symbol()", ""), ("decimals()", ""), ("totalSupply()", ""), ("balanceOf(address)", enc_addr(USER)[2:])])
# Sourcify ABI for sale
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{SALE}?fields=abi", headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r: meta = json.loads(r.read().decode())
    abi = meta.get("abi", [])
    fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
    res["sourcify"] = {"verified": True, "functions": fns}
except Exception as e:
    res["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}
# First Minted event for BNBPIG sale via Ankr getLogs (Minted topic = keccak of Minted(address,uint256,uint256,uint256,uint256)? BNBbaby used that; try Transfer-based first-mint for token + sale logs)
# Generic: getLogs for sale address is not supported chain-wide? ankr_getLogs takes topics only; use Transfer logs for token contract filtered client-side is not possible via topics address filter... ankr supports 'address'? Try params with address field.
def ankr_logs(params):
    body = ankr_post("ankr_getLogs", params, timeout=30)
    return body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00"*32
try:
    logs = ankr_logs({"blockchain": "bsc", "fromBlock": hex(131060000), "toBlock": "latest", "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO]})
    # filter by address client-side for token + oathbots
    for addr, key in [(TOK, "pig_token_transfer_mints"), ("0x1bB3701DA38D1572984Cd200821d1162d6783435", "oathbots_transfer_mints")]:
        mine = [l for l in logs if l.get("address","").lower() == addr.lower()]
        mine_sorted = sorted(mine, key=lambda l: int(l.get("blockNumber","0x0"),16))
        res[key] = {"count_in_range": len(mine_sorted), "first_block": int(mine_sorted[0]["blockNumber"],16) if mine_sorted else None, "last_block": int(mine_sorted[-1]["blockNumber"],16) if mine_sorted else None}
except Exception as e:
    res["ankr_error"] = f"{type(e).__name__}: {str(e)[:200]}"
# Oathbots reads
OATH = "0x1bB3701DA38D1572984Cd200821d1162d6783435"
res["oathbots"] = collect(OATH, [("totalSupply()", ""), ("paused()", ""), ("mintOpen()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]), ("name()", ""), ("symbol()", "")])
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{OATH}?fields=abi", headers={"User-Agent": "free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r: meta = json.loads(r.read().decode())
    abi = meta.get("abi", [])
    res["oathbots_sourcify"] = {"verified": True, "functions": sorted({e["name"] for e in abi if e.get("type") == "function"})}
except Exception as e:
    res["oathbots_sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}
print(json.dumps(res, indent=1))
json.dump(res, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0001-bnbpig.json", "w"), indent=1)
