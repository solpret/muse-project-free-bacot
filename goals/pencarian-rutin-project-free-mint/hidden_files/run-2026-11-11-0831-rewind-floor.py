#!/usr/bin/env python3
"""REWINDCLUB market floor: listingsPage(0,10). Read-only."""
import json, subprocess
from Crypto.Hash import keccak
MK="0xfb414d2288536f35eea77ba996effddb85e07574"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def post(ep,payload,timeout=25):
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
data=sel("listingsPage(uint256,uint256)")+"00"*31+"00"+"00"*31+"0a"
calls=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":MK,"data":data},"latest"]},
       {"jsonrpc":"2.0","id":2,"method":"eth_blockNumber","params":[]}]
for ep in EPS:
    try:
        r=post(ep,calls,timeout=25)
        if isinstance(r,list) and len(r)==2 and r[0].get("result"):
            raw=r[0]["result"]; b=bytes.fromhex(raw[2:])
            print("raw len",len(b),"block",int(r[1]["result"],16),flush=True)
            # decode 4 dynamic arrays: offsets at 0,32,64,96; each: [len][items...]
            def arr(off):
                o=int.from_bytes(b[off:off+32],"big"); n=int.from_bytes(b[o:o+32],"big")
                return [int.from_bytes(b[o+32+i*32:o+64+i*32],"big") for i in range(n)]
            def addrs(off):
                o=int.from_bytes(b[off:off+32],"big"); n=int.from_bytes(b[o:o+32],"big")
                return ["0x"+b[o+32+i*32+12:o+64+i*32].hex() for i in range(n)]
            def bools(off):
                o=int.from_bytes(b[off:off+32],"big"); n=int.from_bytes(b[o:o+32],"big")
                return [bool(int.from_bytes(b[o+32+i*32:o+64+i*32],"big")) for i in range(n)]
            ids=arr(0); sellers=addrs(32); prices=arr(64); valid=bools(96)
            print("ids:",ids,"sellers:",sellers,"prices:",prices,"valid:",valid,flush=True)
            floor=min([p for p,v in zip(prices,valid) if v]) if any(valid) else None
            print("FLOOR wei:",floor,"BNB:",floor/1e18 if floor else None,flush=True)
            json.dump({"ids":ids,"sellers":sellers,"prices":prices,"valid":valid,"floor_wei":floor,"block":int(r[1]["result"],16)},open("run-2026-11-11-0831-rewind-floor.json","w"),indent=1)
            break
    except Exception as e: print(ep,"err",e,flush=True)
