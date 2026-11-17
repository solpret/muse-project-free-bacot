#!/usr/bin/env python3
import json, sys, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
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
def dec_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
targets={"Hexagent":"0x7BA27f90c7b509af1dFBDa2a788Fe4488ff3aab4","Halo Agent":"0x56503C6540411ABa95824A047c50651dcE625Fb3"}
views=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeLeft()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","freeUsed(address)","balanceOf(address)","owner()","AGENT_ID()","agentIdRegistry()","agentRegistry()","costFor(uint256)","quote(address,uint256)"]
out={"block":block()}
for name,addr in targets.items():
    d={}
    for sig in views:
        arg=""
        if "(address)" in sig: arg=enc(USER)
        elif "(uint256)" in sig: arg="0"*63+"1"
        elif sig.startswith("quote"): arg=enc(USER)+"0"*63+"1"
        d[sig]=iv(call(addr, sel(sig)+arg))
    d["name"]=dec_str(call(addr, sel("name()")))
    d["symbol"]=dec_str(call(addr, sel("symbol()")))
    uri=dec_str(call(addr, sel("contractURI()")))
    d["contractURI_raw"]=uri
    try: d["contractURI_decoded"]=base64.b64decode(uri).decode(errors="replace") if uri else None
    except Exception: d["contractURI_decoded"]=None
    out[name]=d
    print(name, "block", out["block"], d)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0401-fresh.json","w"), indent=1)
