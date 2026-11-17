#!/usr/bin/env python3
"""Run 2026-11-06 2201 WIB: verify 0x57D41Ff... (Sourcify S1/S2 per ABI-name match,
hot-leg 2209 said NO agent gate). On-chain verification: agent_id() value,
registry bytes in bytecode, name/symbol, free pool, user slot, launch time.
Read-only."""
import json, urllib.request, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)
def as_int(v):
    try: return int(v, 16)
    except Exception: return None
def as_addr(v):
    if v and len(v) >= 66: return "0x" + v[-40:]
    return None
def as_str(v):
    if not v or len(v) < 130: return None
    try:
        ln = int(v[66:130], 16)
        return bytes.fromhex(v[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def getcode(to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r: return json.load(r)["result"]
        except Exception:
            continue
    return None

out = {"address": ADDR}
out["block"] = None
try:
    out["block"] = int(_single(RPCS[0], "eth_blockNumber", [], 8, retries=0), 16)
except Exception as e:
    out["block_error"] = str(e)

code = getcode(ADDR)
out["code_len"] = len(code) - 2 if code else None
out["registry_bytes_in_code"] = bool(code and REGISTRY[2:].lower() in code.lower())

views = {
    "name()": ("str", None), "symbol()": ("str", None), "decimals()": ("int", None),
    "totalSupply()": ("int", None), "mintOpen()": ("int", None),
    "freeLeft()": ("int", None), "PRICE()": ("int", None),
    "MAX_SUPPLY()": ("int", None), "max_supply()": ("int", None),
    "MAX_MINTS()": ("int", None), "max_mints()": ("int", None),
    "MINT_AMOUNT()": ("int", None), "mint_amount()": ("int", None),
    "MINT_DEADLINE()": ("int", None), "mint_deadline()": ("int", None),
    "MINT_DURATION()": ("int", None),
    "FREE_PER_WALLET()": ("int", None), "free_per_wallet()": ("int", None),
    "totalMints()": ("int", None), "totalMinted()": ("int", None),
    "agent_id()": ("addr", None), "AGENT_ID()": ("addr", None),
    "agentRegistry()": ("addr", None), "factory()": ("addr", None),
    "pair()": ("addr", None), "tradingOpen()": ("int", None),
    "WBNB()": ("addr", None),
    "mintedBy(address)": ("int", enc(USER)),
    "balanceOf(address)": ("int", enc(USER)),
    "quote(address,uint256)": ("raw", enc(USER) + format(1, "064x")),
}
for sig, (kind, args) in views.items():
    v = call(ADDR, sig, args or "")
    if v is None:
        out[sig] = None
    elif kind == "int":
        out[sig] = as_int(v)
    elif kind == "addr":
        out[sig] = as_addr(v)
    elif kind == "str":
        out[sig] = as_str(v)
    else:
        out[sig] = v

# quote return decoding: (cost, free?) - keep raw hex
json.dump(out, open(f"{BASE}/run-2026-11-06-2201-57d41-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
