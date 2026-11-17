#!/usr/bin/env python3
"""Bianren free-shape deep read: free pool vs freeMinted, user slot."""
import json, urllib.request
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR="0xd24A02198e12B35faDE9DD8334Fb7f6333CD05eF"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,timeout=6):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=timeout) as r: out=json.load(r)
            if "error" in out: continue
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(sig,args=""): return raw(ADDR,sel(sig)+args)
views=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_POOL()","FREE_SUPPLY()","FREE_PER_WALLET()","FREE_AMOUNT()","MAX_SUPPLY()","mintOpen()","mintPrice()","price()","quote(address,uint256)","freeOf(address)","freeRemaining()","freeLeft(address)","freeFor(address)","mintedBy(address)","freeUsed(address)","balanceOf(address)","agentRegistry()","AGENT_ID()"]
d={}
for sig in views:
    key=sig.split("(")[0]
    if "address" in sig and "uint256" in sig: v=call(sig,enc(USER)+format(1,"064x")); key+="_user_1"
    elif "address" in sig: v=call(sig,enc(USER)); key+="_user"
    else: v=call(sig)
    d[key]=v
    print(key,v,flush=True)
json.dump(d,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-06-1101-bianren2.json","w"),indent=1)
