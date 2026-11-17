#!/usr/bin/env python3
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def code(to):
    for ep in EPS:
        try: return _single(ep, "eth_getCode", [to, "latest"], 8, retries=0)
        except Exception: pass
    return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode(errors="replace")
    except Exception: return None
def sourcify(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{addr}", headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        abi = d.get("stdJson", {}).get("output", {}).get("abi", []) if isinstance(d, dict) else []
        names = sorted({f.get("name") for f in abi if f.get("name")})
        return ("verified", names, d.get("stdJson", {}).get("metadata", {}).get("sources", {}) if isinstance(d, dict) else {})
    except Exception as e:
        return (f"ERR {type(e).__name__} {str(e)[:80]}", [], {})
out = {}
targets = {
 "Crtdroid": "0xDe67dc24C9B37af22bC6C995cA99e86809b01286",
 "New5084": "0x508468BAD31de925a533b88B17a233EC377C641d",
 "NewAD417": "0xaD41704C3FeeA9E0085627C081D1cf3E647ff3Ee",
}
views = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "freeLeft()", "FREE_SUPPLY()", "FREE_CAP()", "mintedBy(address)", "freeUsed(address)",
         "balanceOf(address)", "owner()", "AGENT_ID()", "agentIdRegistry()", "agentRegistry()",
         "REGISTRY()", "costFor(uint256)", "quote(address,uint256)", "freeWallets(address)", "contractURI()"]
for name, addr in targets.items():
    c = code(addr)
    d = {"code_len": (len(c)-2)//2 if c and c != "0x" else 0}
    for sig in views:
        arg = ""
        if "(address)" in sig: arg = enc(USER)
        elif "(uint256)" in sig: arg = "0"*63+"1"
        elif sig.startswith("quote"): arg = enc(USER)+"0"*63+"1"
        raw = call(addr, sel(sig)+arg)
        if sig in ("name()", "symbol()"):
            d[sig] = dec_str(raw) if raw else None
        else:
            d[sig] = iv(raw)
    st, names, _ = sourcify(addr)
    d["sourcify"] = st; d["abi_names"] = names
    out[name] = d
    print("==", name, addr, "code", d["code_len"], "sourcify", st)
    print("  ", {k: v for k, v in d.items() if k not in ("abi_names",) and v is not None})
    print("   abi:", names[:60])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0431-verify.json","w"), indent=1)
