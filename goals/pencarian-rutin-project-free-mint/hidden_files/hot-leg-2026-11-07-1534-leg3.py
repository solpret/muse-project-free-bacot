#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 15:34 WIB — leg 3 verification for new S1 contract
0x75Ac13cF23a8dccC703D1496138251FD7f247890. Read-only on-chain reads + first-mint age.
No preview, no mint, no snapshot writes."""
import json, sys, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single as _fast_single
import ankr as ankr_mod
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x75Ac13cF23a8dccC703D1496138251FD7f247890"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
WIB = datetime.timezone(datetime.timedelta(hours=7))

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def call(to, data, timeout=8):
    for ep in EPS:
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], timeout, retries=0)
            if v is None or v == "0x":
                return None
            return v
        except Exception:
            continue
    return "transport-fail"

def call_int(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        return int(v, 16)
    except Exception:
        return v

def call_str(to, sig):
    v = call(to, sel(sig))
    if v is None or v == "transport-fail":
        return v
    try:
        raw = bytes.fromhex(v[2:])
        ln = int.from_bytes(raw[32:64], "big")
        return raw[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v

def call_tuple2(to, sig, args=""):
    v = call(to, sel(sig) + args)
    if v is None or v == "transport-fail":
        return v
    try:
        raw = bytes.fromhex(v[2:])
        return (int.from_bytes(raw[0:32], "big"), int.from_bytes(raw[32:64], "big"))
    except Exception:
        return v

def call_addr(to, sig):
    v = call(to, sel(sig))
    if isinstance(v, str) and v.startswith("0x") and len(v) == 66:
        return "0x" + v[-40:]
    return v

blk = None
for ep in EPS:
    try:
        blk = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if blk: blk = int(blk, 16); break
    except Exception:
        continue

d = {
    "name": call_str(ADDR, "name()"),
    "symbol": call_str(ADDR, "symbol()"),
    "decimals": call_int(ADDR, "decimals()"),
    "totalSupply": call_int(ADDR, "totalSupply()"),
    "AGENT_ID_REGISTRY": call_addr(ADDR, "AGENT_ID_REGISTRY()"),
    "agentIdRegistry": call_addr(ADDR, "agentIdRegistry()"),
    "FREE_PER_AGENT": call_int(ADDR, "FREE_PER_AGENT()"),
    "FREE_AMOUNT": call_int(ADDR, "FREE_AMOUNT()"),
    "FREE_SLOTS": call_int(ADDR, "FREE_SLOTS()"),
    "FREE_SUPPLY": call_int(ADDR, "FREE_SUPPLY()"),
    "MAX_SHARES": call_int(ADDR, "MAX_SHARES()"),
    "sharesSold": call_int(ADDR, "sharesSold()"),
    "freeSharesClaimed": call_int(ADDR, "freeSharesClaimed()"),
    "freeSharesRemaining": call_int(ADDR, "freeSharesRemaining()"),
    "freeClaimed": call_int(ADDR, "freeClaimed()"),
    "freeMinted": call_int(ADDR, "freeMinted()"),
    "mintOpen": call_int(ADDR, "mintOpen()"),
    "TOKENS_PER_SHARE": call_int(ADDR, "TOKENS_PER_SHARE()"),
    "PRICE_PER_SHARE": call_int(ADDR, "PRICE_PER_SHARE()"),
    "AGENT_PRICE_PER_SHARE": call_int(ADDR, "AGENT_PRICE_PER_SHARE()"),
    "MAX_PER_WALLET": call_int(ADDR, "MAX_PER_WALLET()"),
    "MAX_PER_TX": call_int(ADDR, "MAX_PER_TX()"),
    "totalRevenue": call_int(ADDR, "totalRevenue()"),
    "treasury": call_addr(ADDR, "treasury()"),
    "quote_user1": call_tuple2(ADDR, "quote(address,uint256)", enc(USER) + enc_uint(1)),
    "freeUsed_user": call_int(ADDR, "freeUsed(address)", enc(USER)),
    "freeLeft_user": call_int(ADDR, "freeLeft(address)", enc(USER)),
    "mintedBy_user": call_int(ADDR, "mintedBy(address)", enc(USER)),
    "balanceOf_user": call_int(ADDR, "balanceOf(address)", enc(USER)),
    "isAgent_user": call_int(ADDR, "isAgent(address)", enc(USER)),
}
out = {"block": blk, "address": ADDR, "contract": d}
print(json.dumps(out, indent=1))

# age: first Minted event, fallback Transfer-from-zero
_k = keccak.new(digest_bits=256); _k.update(b"Minted(address,uint256,uint256,bool)")
MINTED = "0x" + _k.hexdigest()
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "0" * 64
def block_ts(b):
    for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            v = _fast_single(ep, "eth_getBlockByNumber", [hex(b), False], 8, retries=0)
            if v and v.get("timestamp"):
                return int(v["timestamp"], 16)
        except Exception:
            continue
    return None

age = {}
try:
    r = ankr_mod.get_logs(ADDR, "earliest", "latest")
    logs = r.get("result", {}).get("logs", []) if isinstance(r, dict) else []
    minted = [l for l in logs if l.get("topics") and l["topics"][0].lower() == MINTED]
    minted.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
    age["total_logs"] = len(logs)
    age["minted_events"] = len(minted)
    now = datetime.datetime.now(WIB)
    if minted:
        f = minted[0]
        b = int(f["blockNumber"], 16)
        ts = block_ts(b)
        e = {"block": b, "tx": f["transactionHash"], "logIndex": int(f["logIndex"], 16), "block_timestamp": ts}
        if ts:
            dt = datetime.datetime.fromtimestamp(ts, WIB)
            e["wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
            e["age_hours"] = round((now.timestamp() - ts) / 3600, 2)
            e["age_le_48h"] = (now.timestamp() - ts) <= 48 * 3600
        age["first_minted"] = e
    else:
        tr = [l for l in logs if l.get("topics") and l["topics"][0].lower() == TRANSFER
              and len(l["topics"]) > 1 and l["topics"][1].lower() == ZERO]
        tr.sort(key=lambda l: (int(l["blockNumber"], 16), int(l["logIndex"], 16)))
        age["transfer_from_zero"] = len(tr)
        if tr:
            f = tr[0]
            b = int(f["blockNumber"], 16)
            ts = block_ts(b)
            e = {"block": b, "tx": f["transactionHash"], "block_timestamp": ts}
            if ts:
                dt = datetime.datetime.fromtimestamp(ts, WIB)
                e["wib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
                e["age_hours"] = round((now.timestamp() - ts) / 3600, 2)
                e["age_le_48h"] = (now.timestamp() - ts) <= 48 * 3600
            age["first_transfer_mint"] = e
except Exception as e:
    age["error"] = str(e)[:200]
out["age"] = age
json.dump(out, open(f"{HF}/hot-leg-2026-11-07-1534-leg3.json", "w"), indent=1)
print("AGE:", json.dumps(age, indent=1))
print("block", blk)
