#!/usr/bin/env python3
"""Final probe: contractURI + Wisp user views. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n,"064x")
def data(sig,args):
    d=sel(sig)
    for a in args:
        if isinstance(a,str) and a.startswith("0x") and len(a)==42: d+=enc_addr(a)
        else: d+=enc_u(int(a))
    return d
def rpc(method,params,timeout=30):
    for _ in range(3):
        try:
            out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})],capture_output=True,text=True,timeout=timeout+10).stdout
            j=json.loads(out)
            if isinstance(j,dict) and "result" in j: return j["result"]
        except Exception: time.sleep(2)
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(v):
    if not v or len(v)<130: return None
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],'big')
        return b[96:96+ln].decode('utf-8',errors='ignore')
    except Exception: return None
def dec_uri(v):
    # string return (dynamic) or raw bytes
    if not v or v=="0x": return None
    try:
        b=bytes.fromhex(v[2:])
        if len(b)>=96:
            ln=int.from_bytes(b[64:96],'big')
            if 0<ln<=len(b)-96: return b[96:96+ln].decode('utf-8',errors='ignore')
        return b.decode('utf-8',errors='ignore').strip('\x00')
    except Exception: return None
out={}
for name,addr in [("LEGBEE","0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149"),("WISPAGENT","0x84629f583e7eafba8f5f336b6943e8f23f8ae7bb")]:
    d={}
    for sig in ["contractURI()","tokenURI(uint256)"]:
        args=[1] if "uint256" in sig else []
        r=rpc("eth_call",[{"to":addr,"data":data(sig,args)},"latest"])
        d[sig.split("(")[0]]=dec_uri(r) if isinstance(r,str) else None
    if name=="WISPAGENT":
        for sig,args in [("hasFreeMinted(address)",[USER]),("mintedPerWallet(address)",[USER]),("freeMintedPerWallet(address)",[USER]),("mintedCount(address)",[USER]),("freeMintsLeft()",[]),("getFreeLeft()",[]),("freeMintPrice()",[]),("mintCost()",[])]:
            r=rpc("eth_call",[{"to":addr,"data":data(sig,args)},"latest"])
            d[sig.split("(")[0]+"_user" if args else sig.split("(")[0]]=to_int(r[:66]) if (isinstance(r,str) and len(r)>=66) else r
    out[name]=d
    print(name, json.dumps(d,indent=1))
json.dump(out,open("run-2026-11-16-0001-triage4.json","w"),indent=1)
