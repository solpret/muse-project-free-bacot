#!/usr/bin/env python3
"""Verify REWINDCLUB mint tx + post-mint state + tokenURI/market. Read-only."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
TX="0xee5d66abe548f0959909dddbd0816d146ae975cf053e0fb6bb35abd531a46071"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RC="0x39b451abbd53365e2277084cb60f9a2c5ad6e698"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def dec_str(v):
    try:
        if not v or v=="0x": return None
        b=bytes.fromhex(v[2:])
        off=int.from_bytes(b[0:32],"big"); ln=int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
receipt=None
for i in range(24):
    for ep in EPS:
        try:
            r=post(ep,{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":[TX]},timeout=25)
            if r.get("result"): receipt=r["result"]; break
        except Exception: continue
    if receipt: break
    print(f"poll {i}: no receipt yet",flush=True); time.sleep(5)
out={"tx":TX,"receipt":receipt}
if receipt:
    print("block",int(receipt["blockNumber"],16),"status",int(receipt["status"],16),"gasUsed",int(receipt["gasUsed"],16),"gasPrice",receipt.get("effectiveGasPrice"),flush=True)
    tid="00000000000000000000000000000000000000000000000000000000000001f6"
    calls=[
     {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":RC,"data":sel("ownerOf(uint256)")+tid},"latest"]},
     {"jsonrpc":"2.0","id":2,"method":"eth_call","params":[{"to":RC,"data":sel("balanceOf(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":3,"method":"eth_call","params":[{"to":RC,"data":sel("agentFreeUsed()")},"latest"]},
     {"jsonrpc":"2.0","id":4,"method":"eth_call","params":[{"to":RC,"data":sel("agentFreeByWallet(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":5,"method":"eth_call","params":[{"to":RC,"data":sel("totalSupply()")},"latest"]},
     {"jsonrpc":"2.0","id":6,"method":"eth_call","params":[{"to":RC,"data":sel("tokenURI(uint256)")+tid},"latest"]},
     {"jsonrpc":"2.0","id":7,"method":"eth_call","params":[{"to":RC,"data":sel("claimable(address)")+enc(USER)},"latest"]},
     {"jsonrpc":"2.0","id":8,"method":"eth_blockNumber","params":[]},
    ]
    for ep in EPS:
        try:
            r=post(ep,calls,timeout=25)
            if isinstance(r,list) and len(r)==8:
                out["post"]={"ownerOf_502":("0x"+r[0].get("result","")[-40:]) if r[0].get("result") else None,
                  "balanceOf_user":to_int(r[1].get("result")),"agentFreeUsed":to_int(r[2].get("result")),
                  "agentFreeByWallet_user":to_int(r[3].get("result")),"totalSupply":to_int(r[4].get("result")),
                  "tokenURI":dec_str(r[5].get("result")),"claimable_user":r[6].get("result"),"block":int(r[7]["result"],16)}
                print("POST:",json.dumps(out["post"]),flush=True); break
        except Exception as e: print(ep,"err",e,flush=True)
uri=(out.get("post") or {}).get("tokenURI") or ""
meta=None
if uri.startswith("http"):
    try:
        req=urllib.request.Request(uri,headers={"User-Agent":"free-bacot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as resp: meta=json.loads(resp.read().decode())
        print("META:",json.dumps(meta)[:1500],flush=True)
    except Exception as e: print("META ERR",e,flush=True)
out["metadata"]=meta
json.dump(out,open("run-2026-11-11-0831-verify-rewind.json","w"),indent=1)
