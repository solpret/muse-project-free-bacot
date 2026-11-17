#!/usr/bin/env python3
"""Hot-leg 01:04 run - Leg 3 on-chain verification of new S1 sale-shape Botkirin."""
import json, urllib.request, base64
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR="0xe43818c2c6080e9d2bef53db14092806b51711d2"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed.binance.org","https://rpc.ankr.com/bsc"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data,timeout=6):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: o=json.load(r)
            if "error" in o: continue
            v=o.get("result")
            if not v or v=="0x": return None
            return v
        except Exception: continue
    return "deadline"
def call(sig,args=""): return raw(ADDR, sel(sig)+args)
def as_int(v):
    if v is None or v=="deadline": return v
    try: return int(v,16)
    except Exception: return v
def as_str(v):
    if v is None or v=="deadline": return v
    try:
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64+off-32:64+off-32+32] if False else b[64:96],"big")
        # standard ABI string: [0:32]=offset, [32:64]=len, [64:]=data
        ln=int.from_bytes(b[32:64],"big")
        return b[64:64+ln].decode("utf-8","replace")
    except Exception as e: return f"decode-err {e}: {v[:120]}"
def as_addr(v):
    if v is None or v=="deadline": return v
    return "0x"+v[-40:]
out={}
out["block"]=None
for rpc in RPCS:
    try:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
        req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=5) as r: o=json.load(r)
        out["block"]=int(o["result"],16); out["via"]=rpc; break
    except Exception: continue
for sig in ["name()","symbol()","totalSupply()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","FREE_PER_WALLET()","MAX_PER_WALLET()","PRICE()","mintOpen()"]:
    out[sig.split("(")[0]]=as_int(call(sig)) if sig not in ("name()","symbol()") else as_str(call(sig))
out["AGENT_ID"]=as_addr(call("AGENT_ID()"))
out["owner"]=as_addr(call("owner()"))
out["IMAGE"]=as_addr(call("IMAGE()"))
out["quote_user1"]=as_int(call("quote(address,uint256)",enc(USER)+enc_uint(1)))
out["freeFor_user1"]=as_int(call("freeFor(address,uint256)",enc(USER)+enc_uint(1)))
out["freeLeft_user"]=as_int(call("freeLeft(address)",enc(USER)))
out["freeUsed_user"]=as_int(call("freeUsed(address)",enc(USER)))
out["mintedBy_user"]=as_int(call("mintedBy(address)",enc(USER)))
out["balanceOf_user"]=as_int(call("balanceOf(address)",enc(USER)))
out["contractURI"]=as_str(call("contractURI()"))
# tokenURI(1) if any supply
if isinstance(out.get("totalSupply"),int) and out["totalSupply"]>0:
    out["tokenURI_1"]=as_str(call("tokenURI(uint256)",enc_uint(1)))
json.dump(out,open(f"{BASE}/hot-leg-2026-11-07-0104-leg3.json","w"),indent=1)
print(json.dumps(out,indent=1))
