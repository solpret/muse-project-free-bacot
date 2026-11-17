#!/usr/bin/env python3
"""NOVA AGENT verify — run 2026-11-10 06:01 WIB. Read-only.
Boltbook lead (agata.ai post 06:31 WIB): 0x1b6E6F62528DE674C12BC2C04C159336d3DB049e.
Reads views via fast_rpc + dataseed curl fallback; eth_getCode registry-byte check;
Sourcify verification status; first-seen block timestamp."""
import json, sys, time, subprocess, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import call_many, race
NOVA="0x1b6E6F62528DE674C12BC2C04C159336d3DB049e"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="0x60b9262456de011f7d15a54cdd8c48baa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def toint(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
VIEWS=["name()","symbol()","totalSupply()","MAX_SUPPLY()","FREE_SUPPLY()","FREE_PER_WALLET()",
 "MAX_PER_WALLET()","mintOpen()","freeClaimed()","freeMinted()","freeLeft()","balanceOf(address)",
 "freeClaimed(address)","mintedBy(address)","owner()","contractURI()","baseURI()",
 "AGENT_ID_REGISTRY()","agentRegistry()","AGENT_REGISTRY()","price()","priceFor(address)",
 "quote(uint256)","spotsLeft()","totalMinted()","mintPrice()"]
calls=[]
keys=[]
for sig in VIEWS:
    base=sig.split("(")[0]
    if "(address)" in sig:
        calls.append((NOVA, sel(sig)+enc(USER))); keys.append(base+"_user")
    elif "(uint256)" in sig:
        calls.append((NOVA, sel(sig)+"0"*63+"1")); keys.append(base+"_1")
    else:
        calls.append((NOVA, sel(sig))); keys.append(base)
out={"contract":NOVA,"block":None,"views":{},"code_registry":None,"sourcify":None,"firstseen_block_ts":None}
try:
    out["block"]=int(race("eth_blockNumber",[]),16)
except Exception as e:
    out["block_error"]=repr(e)
try:
    res=call_many(calls)
    for k,v in zip(keys,res):
        out["views"][k]=toint(v)
except Exception as e:
    out["views_error"]=repr(e)
# raw string views: contractURI/baseURI/name/symbol need decoded output - re-read raw
try:
    raw=call_many([(NOVA, sel("contractURI()")),(NOVA, sel("baseURI()")),(NOVA, sel("name()")),(NOVA, sel("symbol()"))])
    out["views_raw"]={"contractURI":raw[0][:200] if raw[0] else None,"baseURI":raw[1][:200] if raw[1] else None,"name":raw[2][:200] if raw[2] else None,"symbol":raw[3][:200] if raw[3] else None}
except Exception as e:
    out["views_raw_error"]=repr(e)
try:
    code=race("eth_getCode",[NOVA,"latest"])
    out["code_len"]=len(code)//2-1 if code else 0
    out["code_registry"]=REG[2:].lower() in code.lower() if code else None
except Exception as e:
    out["code_error"]=repr(e)
# Sourcify
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contract/56/%s"%NOVA, headers={"User-Agent":"curl"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j=json.load(r); out["sourcify"]={"match":j.get("match"),"status":r.status}
except Exception as e:
    out["sourcify"]={"error":repr(e)}
# first-seen block timestamp
try:
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(131197893),False]}).encode()
    req=urllib.request.Request("https://bsc-dataseed1.bnbchain.org", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        b=json.load(r)["result"]; out["firstseen_block_ts"]=int(b["timestamp"],16)
except Exception as e:
    out["firstseen_block_ts_error"]=repr(e)
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-10-0601-nova-verify.json","w"), indent=1)
