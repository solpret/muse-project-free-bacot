#!/usr/bin/env python3
"""Deep verify two Sourcify-feed shape hits, run 1831. Read-only."""
import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak
import onchain_nft_scan as scan

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDRS = ["0xaCeF3B62B958ED7F49dFc73885609b4d270B9bD0",
         "0x3d8Fe93184848941693dECdF1820967b3F684787"]

def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def enc_uint(n): return format(n, "064x")
def call(addr, data, timeout=15):
    last = None
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception as e:
            last = e
    return {"error": str(last)}
def dec_uint(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:]); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None

discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner","")).lower() for d in discards if isinstance(d, dict)}

out = {}
for A in ADDRS:
    r = {}
    def tc(sig, args=""):
        return call(A, sel(sig) + args)
    r["name"] = dec_str(tc("name()"))
    r["symbol"] = dec_str(tc("symbol()"))
    r["decimals"] = dec_uint(tc("decimals()"))
    r["totalSupply"] = dec_uint(tc("totalSupply()"))
    r["totalMinted"] = dec_uint(tc("totalMinted()"))
    r["MAX_SUPPLY"] = dec_uint(tc("MAX_SUPPLY()"))
    r["FREE_SUPPLY"] = dec_uint(tc("FREE_SUPPLY()"))
    r["FREE_CAP"] = dec_uint(tc("FREE_CAP()"))
    r["freeClaimed"] = dec_uint(tc("freeClaimed()"))
    r["freeMinted"] = dec_uint(tc("freeMinted()"))
    r["freeLeft"] = dec_uint(tc("freeLeft()"))
    r["mintOpen"] = dec_uint(tc("mintOpen()"))
    r["price"] = dec_uint(tc("price()"))
    r["owner_raw"] = tc("owner()")
    if isinstance(r["owner_raw"], str) and r["owner_raw"].startswith("0x") and len(r["owner_raw"]) == 66:
        r["owner"] = "0x" + r["owner_raw"][-40:]
    else:
        r["owner"] = None
    r["agentId_raw"] = tc("agentId()")
    r["agentRegistry_raw"] = tc("agentRegistry()")
    r["AGENT_ID_raw"] = tc("AGENT_ID()")
    r["balanceOf_user"] = dec_uint(tc("balanceOf(address)", enc_addr(AGENT)))
    r["freeClaimed_user"] = dec_uint(tc("freeClaimed(address)", enc_addr(AGENT)))
    r["freeUsed_user"] = dec_uint(tc("freeUsed(address)", enc_addr(AGENT)))
    # code + registry bytes
    code = None
    for ep in EPS:
        try:
            code = batch([("eth_getCode", [A, "latest"])], endpoint=ep, timeout=15)[0]
            break
        except Exception:
            continue
    r["code_len"] = len(code) - 2 if code else None
    r["registry_bytes_in_code"] = (REG_BYTES in code.lower()) if code else None
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    print(json.dumps({A: r}, indent=1), flush=True)
    out[A] = r

json.dump(out, open(BASE + "/run-2026-11-08-1831-feed-verify.json", "w"), indent=1)
print("WROTE run-2026-11-08-1831-feed-verify.json")
