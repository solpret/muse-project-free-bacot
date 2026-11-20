#!/usr/bin/env python3
"""Retry ARKYN + ORIN2 reads via direct curl batch (dataseed) + dataseed1, per run-script fallback pattern."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def curl_batch(calls, url, timeout=15):
    out = []
    for i in range(0, len(calls), 5):
        chunk = calls[i:i+5]
        payload = [{"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for j,(t,d) in enumerate(chunk)]
        r = subprocess.run(["curl","-s","--max-time",str(timeout),url,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
        if r.returncode != 0 or not r.stdout: raise IOError(f"curl rc={r.returncode}")
        resp = json.loads(r.stdout.decode())
        by = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by.get(j+1, {})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out.append(int(it["result"],16))
                except Exception: out.append(it["result"])
            else: out.append(None)
    return out
ARKYN="0x69b0b5756671680766d232eb4b0f39a34be5d852"; ORIN2="0xa04513d85e02e1a1623a985269b3ebd46fa76b98"
views=["totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintActive()","mintOpen()","freeRemaining()","freeLeft()","mintPrice()","PAID_PRICE()","freeMintedBy(address)","mintedBy(address)","freeUsed(address)","balanceOf(address)"]
calls, meta = [], []
for addr,name in ((ARKYN,"ARKYN"),(ORIN2,"ORIN2")):
    for v in views:
        d="0x"+sel(v)
        if "(address)" in v: d+=enc_addr(USER)
        calls.append((addr,d)); meta.append((name,addr,v))
res=None; ep=None
for url in ("https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"):
    try:
        res=curl_batch(calls,url); ep=url; break
    except Exception as e:
        print("curl fail",url,e, file=sys.stderr)
out={"endpoint":ep}
for (name,addr,v),val in zip(meta,res or []):
    out.setdefault(name,{"address":addr,"views":{}})["views"][v]=val
print(json.dumps(out,indent=1))
json.dump(out, open("run-2026-11-17-1531-verify2.json","w"), indent=1)
