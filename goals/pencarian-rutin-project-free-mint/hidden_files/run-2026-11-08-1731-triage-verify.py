#!/usr/bin/env python3
"""Deep verify first-seen agent-shaped: OBSIDIAN 0x57E3F981, MONOLITH 0xcdA4A0EF, plus Aequitas/Barrels totals. Read-only."""
import sys, json, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def selector(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def enc_uint(n): return format(n, "064x")
def raw_call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e: last = e
    raise last
def dec_uint(h):
    if not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_bool(h):
    v = dec_uint(h); return None if v is None else bool(v)
def dec_str(h):
    if not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def tc(addr, sig, args=""):
    try: return raw_call(addr, selector(sig) + args)
    except Exception as e: return f"ERR:{type(e).__name__}"

def block_time(blk):
    for ep in EPS:
        try:
            b = batch([("eth_getBlockByNumber", [hex(blk), False])], endpoint=ep, timeout=15)[0]
            return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r).get("abi")
    except Exception as e:
        return None

out = {}
# --- OBSIDIAN CARD ---
O = "0x57E3F981791C3BE85d74e74A2F402D7D00F6eD9C"
abi = sourcify_abi(O)
fns = sorted({f.get("name","") for f in abi if f.get("type")=="function"}) if abi else None
o = {"sourcify_abi_fns": fns}
o["name"] = dec_str(tc(O, "name()"))
o["symbol"] = dec_str(tc(O, "symbol()"))
o["totalSupply"] = dec_uint(tc(O, "totalSupply()"))
o["totalMinted"] = dec_uint(tc(O, "totalMinted()"))
o["freeLeft"] = dec_uint(tc(O, "freeLeft()"))
o["freeOf_agent"] = dec_uint(tc(O, "freeOf(address)", enc_addr(AGENT)))
o["freeMinted"] = dec_uint(tc(O, "freeMinted()"))
o["FREE_CAP"] = dec_uint(tc(O, "FREE_CAP()"))
o["FREE_SUPPLY"] = dec_uint(tc(O, "FREE_SUPPLY()"))
o["mintOpen"] = dec_uint(tc(O, "mintOpen()"))
o["agentId"] = tc(O, "agentId()")
o["agentRegistry"] = tc(O, "agentRegistry()")
o["AGENT_REGISTRY"] = tc(O, "AGENT_REGISTRY()")
o["owner"] = tc(O, "owner()")
o["first_block"] = 132377391
o["first_block_time"] = block_time(132377391)
o["in_window_mints"] = 4
print("OBSIDIAN:", json.dumps(o, indent=1), flush=True)
out["OBSIDIAN"] = o

# --- MONOLITH (unverified: probe common selectors) ---
M = "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b"
m = {"sourcify": "not_verified"}
m["name"] = dec_str(tc(M, "name()"))
m["symbol"] = dec_str(tc(M, "symbol()"))
m["totalSupply"] = dec_uint(tc(M, "totalSupply()"))
m["totalMinted"] = dec_uint(tc(M, "totalMinted()"))
m["freeMinted"] = dec_uint(tc(M, "freeMinted()"))
m["FREE_CAP"] = dec_uint(tc(M, "FREE_CAP()"))
m["FREE_SUPPLY"] = dec_uint(tc(M, "FREE_SUPPLY()"))
m["freeLeft"] = dec_uint(tc(M, "freeLeft()"))
m["freeClaimed_agent"] = dec_uint(tc(M, "freeClaimed(address)", enc_addr(AGENT)))
m["agentId"] = tc(M, "agentId()")
m["agentRegistry"] = tc(M, "agentRegistry()")
m["owner"] = tc(M, "owner()")
m["first_block"] = 132377160
m["first_block_time"] = block_time(132377160)
m["in_window_mints"] = 7
print("MONOLITH:", json.dumps(m, indent=1), flush=True)
out["MONOLITH"] = m

# --- Aequitas + Barrels: totals only ---
for addr, label in [("0xf415E7A2de78ab57A4428A75D0062e8a999d8B0F","AEQUITAS"),("0x4bb41DB7e49dFa27000EF299E372aC649A197752","BARRELS")]:
    r = {"name": dec_str(tc(addr, "name()")), "symbol": dec_str(tc(addr, "symbol()")),
         "totalSupply": dec_uint(tc(addr, "totalSupply()")), "totalMinted": dec_uint(tc(addr, "totalMinted()")),
         "agentId": tc(addr, "agentId()"), "owner": tc(addr, "owner()")}
    print(label, json.dumps(r), flush=True)
    out[label] = r

json.dump(out, open("run-2026-11-08-1731-triage-verify.json", "w"), indent=1)
print("WROTE triage-verify.json")
