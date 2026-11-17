#!/usr/bin/env python3
"""Probe DogeRageFi 0x097ff90f (Boltbook ZH lead, run 0401). Read-only view probes, chunked batches."""
import json, subprocess, time
from Crypto.Hash import keccak
ADDR="0x097ff90fce52f4f0e1f41d6f8c799db9cd67099f"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed.binance.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-rpc.publicnode.com/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
sigs=["name()","symbol()","decimals()","totalSupply()","freeMinted()","freeClaimed()","FREE_SLOTS()","FREE_SUPPLY()","FREE_AMOUNT()","agentRegistry()","AGENT_ID()","mintOpen()","mintPrice()","paused()","owner()","totalMinted()","freeLeft()","freeSupply()","freeSharesRemaining()","claimOpen()","launched()","maxSupply()","MAX_SUPPLY()"]
addr_sigs=["freeClaimed(address)","balanceOf(address)","mintedBy(address)","freeUsed(address)","freeFor(address)","holdsAgentId(address)","hasAgentId(address)"]
calls=[]; meta=[]
for s in sigs:
    calls.append((s, sel(s)))
for s in addr_sigs:
    calls.append((s+"[user]", sel(s)+enc_addr(USER)))
def post(ep, payload, timeout=90):
    r=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+10)
    return json.loads(r.stdout)
out={}
for ci in range(0, len(calls), 8):
    chunk=calls[ci:ci+8]
    payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":d},"latest"]} for i,(m,d) in enumerate(chunk)]
    done=False
    for ep in EPS:
        try:
            res=post(ep,payload)
            if isinstance(res,list) and len(res)==len(chunk):
                for (m,d),it in zip(chunk,res):
                    if not isinstance(it,dict) or "error" in it or it.get("result") in (None,"0x"):
                        out[m]=None
                    else:
                        v=it["result"]
                        try:
                            if m.startswith(("name","symbol")):
                                raw=bytes.fromhex(v[2:]); ln=int.from_bytes(raw[64:96],'big')
                                out[m]=raw[96:96+ln].decode(errors='replace')
                            else: out[m]=int(v,16)
                        except Exception: out[m]="raw:"+v[:130]
                done=True; break
        except Exception as e:
            print("ep fail",ep,str(e)[:80]); continue
    if not done:
        for m,d in chunk: out[m]="BATCH_FAIL"
        print("chunk FAIL", [m for m,_ in chunk])
    time.sleep(4)
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-16-0401-drf-probe.json","w"), indent=1)
