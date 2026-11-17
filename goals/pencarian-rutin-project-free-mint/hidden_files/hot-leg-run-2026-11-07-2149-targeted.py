#!/usr/bin/env python3
"""Hot-leg 2149 targeted follow-up #2: exact-view reads for both new S1s + age check for Agentdragon."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 110
t0 = time.time()
out = {}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 138:
        return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

# --- Agentdragon 0x2df7 exact views ---
A = "0x2df7435f5bce0577bee213e13da68313c74d7d0b"
d = {}
for sig, key in [("FREE_SUPPLY()", "FREE_SUPPLY"), ("MAX_SUPPLY()", "MAX_SUPPLY"),
                 ("FREE_PER_WALLET()", "FREE_PER_WALLET"), ("MAX_PER_WALLET()", "MAX_PER_WALLET"),
                 ("PRICE()", "PRICE"), ("AGENT_ID()", "AGENT_ID"), ("owner()", "owner"),
                 ("freeClaimed()", "freeClaimed"), ("freeLeft(address)", "freeLeft_user"),
                 ("freeUsed(address)", "freeUsed_user"), ("mintedBy(address)", "mintedBy_user"),
                 ("quote(address,uint256)", "quote_user1"), ("mintOpen()", "mintOpen"),
                 ("totalSupply()", "totalSupply"), ("balanceOf(address)", "balanceOf_user"),
                 ("name()", "name"), ("symbol()", "symbol"),
                 ("contractURI()", "contractURI"), ("tokenURI(uint256)", "tokenURI_1")]:
    if sig.startswith("quote("):
        d[key] = call(A, sig, enc(USER) + enc_uint(1))
    elif sig.startswith("tokenURI("):
        d[key] = call(A, sig, enc_uint(1))
    elif "address" in sig:
        d[key] = call(A, sig, enc(USER))
    else:
        d[key] = call(A, sig)
for k in ("name", "symbol", "contractURI", "tokenURI_1"):
    if d.get(k):
        d[k] = decode_str(d[k])
out["agentdragon_exact"] = d

# --- 0xa46D exact views (tiered NFT sale) ---
B = "0xa46D33862124Da90385cEb58acba63718729DEe0"
e = {}
for sig, key in [("FREE_CAP()", "FREE_CAP"), ("FREE_PER_WALLET()", "FREE_PER_WALLET"),
                 ("MAX_SUPPLY()", "MAX_SUPPLY"), ("PRICE_FREE_USD()", "PRICE_FREE_USD"),
                 ("PRICE_PAID_USD()", "PRICE_PAID_USD"), ("TIER_FREE()", "TIER_FREE"),
                 ("TIER_PAID()", "TIER_PAID"), ("agentRegistry()", "agentRegistry"),
                 ("owner()", "owner"), ("mintActive()", "mintActive"),
                 ("totalSupply()", "totalSupply"), ("totalMinted()", "totalMinted"),
                 ("freeMintedTotal()", "freeMintedTotal"), ("freeMinted(address)", "freeMinted_user"),
                 ("mintedCount(address)", "mintedCount_user"), ("balanceOf(address)", "balanceOf_user"),
                 ("quote(uint8)", "quote_tier_free"), ("tierMinted(uint8)", "tierMinted_free"),
                 ("name()", "name"), ("symbol()", "symbol"), ("baseURI()", "baseURI")]:
    if sig.startswith("quote(") or sig.startswith("tierMinted("):
        tier = e.get("TIER_FREE")
        arg = enc_uint(tier) if isinstance(tier, int) else enc_uint(0)
        e[key] = call(B, sig, arg)
    elif "address" in sig:
        e[key] = call(B, sig, enc(USER))
    else:
        e[key] = call(B, sig)
for k in ("name", "symbol", "baseURI"):
    if e.get(k):
        e[k] = decode_str(e[k])
out["a46d_exact"] = e

# --- Age check for Agentdragon: first mint via getLogs Transfer from zero address ---
TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO_TOPIC = "0x" + "0" * 64
blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
out["block"] = blk
age = {"transfer_topic": TRANSFER}
if blk:
    # search backwards in windows of 10000 blocks (~1.2h at 0.45s/blk... actually ~75min) until first mint found
    end = blk
    first_block = None
    total_logs = 0
    for w in range(6):
        start = max(0, end - 10000)
        got = None
        for ep in EPS:
            try:
                v = _fast_single(ep, "eth_getLogs", [{"fromBlock": hex(start), "toBlock": hex(end),
                    "address": A, "topics": [TRANSFER, ZERO_TOPIC]}], 15, retries=0)
                if isinstance(v, list):
                    got = v; break
            except Exception:
                continue
        if got is None:
            age["error"] = f"getLogs failed window {start}-{end}"
            break
        total_logs += len(got)
        if got:
            first_block = min(int(x["blockNumber"], 16) for x in got)
            age["window_with_first_mint"] = [start, end]
            age["logs_in_window"] = len(got)
            break
        end = start - 1
        if time.time() > DEADLINE:
            age["error"] = "deadline during window scan"
            break
    age["first_mint_block"] = first_block
    age["windows_scanned"] = w + 1
    if first_block:
        ts = None
        for ep in EPS:
            try:
                b = _fast_single(ep, "eth_getBlockByNumber", [hex(first_block), False], 8, retries=0)
                if b and b.get("timestamp"):
                    ts = int(b["timestamp"], 16); break
            except Exception:
                continue
        age["first_mint_timestamp"] = ts
        if ts:
            import datetime
            age["first_mint_wib"] = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            age["age_hours_at_run"] = round((time.time() - ts) / 3600, 2)
out["agentdragon_age"] = age
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-2026-11-07-2149-targeted.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
