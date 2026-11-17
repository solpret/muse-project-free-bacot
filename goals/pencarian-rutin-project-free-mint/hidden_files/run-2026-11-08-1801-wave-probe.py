#!/usr/bin/env python3
"""Run 1801: slot/owner probe for the 8-contract 14:56 WIB wave (Cassetto et al.).
Tries candidate slot/owner view selectors; read-only; writes own JSON only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
WAVE = {
    "Cassetto": "0x1f974998031c6DD8137E8D7aC6c2287357A2ddeb",
    "Candlewick": "0x9A67E1FD6409B91BD9751206c81fDf37Fc467aE6",
    "Coralume": "0xF10C1E17ae65e88e34253b951dD8EC274fa3AfEB",
    "Retrocam": "0x4c895E2eC1FB615d6bd28584644f5e778f64BC36",
    "Pixpad": "0x7b601C3D2050B021B3bd9d650D421f3F98436ab3",
    "Keyforge": "0xd9D4466342c993b43f02AE2e21D6F125a1Bd937F",
    "Hourglas": "0xc2027F9407eA355eeD5845Bb5e653aeed671f212",
    "Compasso": "0x6551529eC146020ee59B41265614b7a00A166A3f",
}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def to_addr(v):
    try:
        if v is None or v == "0x": return None
        return "0x" + v[-40:]
    except Exception: return None

NOARG = ["owner()", "contractURI()", "freeLeft()", "freeSupply()", "FREE_PER_WALLET()",
         "mintPrice()", "PRICE()", "name()", "symbol()"]
ADDRARG = ["freeClaimed(address)", "freeMinted(address)", "freeFor(address)",
           "freeUsed(address)", "mintedBy(address)", "claimedFree(address)",
           "freeMintedBy(address)", "hasMinted(address)", "balanceOf(address)"]
# quote(address,uint256): address + uint256(1)
QUOTE2 = "quote(address,uint256)"

def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=8, retries=0)
            if isinstance(out, dict) and "error" in out:
                return None, "revert"
            if isinstance(out, dict):
                return out.get("result"), None
            return None, "nodata"
        except Exception as e:
            continue
    return None, "transport-fail"

out = {}
for name, addr in WAVE.items():
    d = {"address": addr}
    for sig in NOARG:
        r, err = call(addr, sel(sig))
        key = sig.split("(")[0]
        if sig == "owner()":
            d[key] = to_addr(r) if r else None
        elif sig in ("name()", "symbol()"):
            d[key] = r
        else:
            d[key] = to_int(r)
        d[key + "_err"] = err
    for sig in ADDRARG:
        r, err = call(addr, sel(sig) + enc(USER))
        key = sig.split("(")[0] + "_user"
        d[key] = to_int(r)
        d[key + "_err"] = err
    r, err = call(addr, sel(QUOTE2) + enc(USER) + enc_u(1))
    d["quote_user_1"] = to_int(r); d["quote_user_1_err"] = err
    r, err = call(addr, sel("quote(uint256)") + enc_u(1))
    d["quote_1"] = to_int(r); d["quote_1_err"] = err
    out[name] = d
    print(name, {k: v for k, v in d.items() if not k.endswith("_err")}, flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-08-1801-wave-probe.json", "w"), indent=1)
print("WROTE wave probe")
