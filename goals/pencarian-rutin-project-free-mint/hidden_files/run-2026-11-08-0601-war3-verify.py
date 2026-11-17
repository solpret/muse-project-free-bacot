#!/usr/bin/env python3
"""WAR3 post-mint verification, run 0601 — read-only. Confirms ownership of
token #2511 (tx 0xb77e8f... from run 0501), balances, free counters, tokenURI."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
WAR3 = "0x1Aa9797cC762b838388566daa45a56b1709F4Bbe"
WW3  = "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc256(n): return hex(n)[2:].rjust(64, "0")
def call(to, data, ep, timeout=10):
    try:
        r = batch([("eth_call", [{"to": to, "data": data}, "latest"])], endpoint=ep, timeout=timeout)
        return r[0]
    except Exception as e:
        return f"ERR:{e}"
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
out = {"tx": "0xb77e8f27014d7b14ab8d35ad403bc4aa7adeab219b6a7d386366f7a1cd911b9b"}
calls = {
 "ownerOf(2511)": (WAR3, sel("ownerOf(uint256)") + enc256(2511)),
 "balanceOf(user) WAR3": (WAR3, sel("balanceOf(address)") + enc(USER)),
 "totalSupply WAR3": (WAR3, sel("totalSupply()")),
 "freeMinted WAR3": (WAR3, sel("freeMinted()")),
 "tokenURI(2511)": (WAR3, sel("tokenURI(uint256)") + enc256(2511)),
 "WW3 balanceOf(user)": (WW3, sel("balanceOf(address)") + enc(USER)),
 "WW3 totalSupply": (WW3, sel("totalSupply()")),
}
for ep in EPS:
    res = {}
    ok = True
    for name, (to, data) in calls.items():
        v = call(to, data, ep)
        res[name] = v if isinstance(v, str) and v.startswith("ERR") else v
        if isinstance(v, str) and v.startswith("ERR"): ok = False
    out["endpoint"] = ep
    out["raw"] = res
    if ok: break
# decode
raw = out["raw"]
def dec_int(name):
    v = raw.get(name)
    return to_int(v) if isinstance(v, str) and v.startswith("0x") else v
out["ownerOf_2511"] = raw.get("ownerOf(2511)")
out["balanceOf_user"] = dec_int("balanceOf(user) WAR3")
out["totalSupply"] = dec_int("totalSupply WAR3")
out["freeMinted"] = dec_int("freeMinted WAR3")
out["ww3_balance_user"] = dec_int("WW3 balanceOf(user)")
out["ww3_totalSupply"] = dec_int("WW3 totalSupply")
# tokenURI decode: offset 32B, len 32B, bytes
tu = raw.get("tokenURI(2511)")
out["tokenURI_raw"] = tu
if isinstance(tu, str) and tu.startswith("0x") and len(tu) > 130:
    try:
        ln = int(tu[130:194], 16)
        out["tokenURI"] = bytes.fromhex(tu[194:194+ln*2]).decode()
    except Exception as e:
        out["tokenURI_decode_err"] = str(e)
try:
    out["block"] = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception as e:
    out["block"] = f"ERR:{e}"
json.dump(out, open("run-2026-11-08-0601-war3-verify.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("raw",)}, indent=1)[:3000])
