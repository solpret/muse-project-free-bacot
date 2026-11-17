#!/usr/bin/env python3
import json, urllib.request, time
from Crypto.Hash import keccak
ADDR="0x921150815bF267a17bb372E44e6e3f44a05f54af"
EPS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def jrpc(ep,method,params,timeout=10):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],"big"); return b[96:96+ln].decode()
    except Exception: return v
blk=131932982
for sig,args in [("name()",""),("symbol()",""),("tokenURI(uint256)",format(1,"064x"))]:
    got=None
    for ep in EPS:
        try:
            out=jrpc(ep,"eth_call",[{"to":ADDR,"data":sel(sig)+args},"latest"])
            if "error" in out: print(sig,"err",ep,out["error"],flush=True); continue
            got=out.get("result"); print(sig,"raw:",got,flush=True); break
        except Exception as e: print(sig,"fail",ep,repr(e),flush=True)
    if sig.startswith("tokenURI") and got:
        print("tokenURI decoded:",dec_str(got),flush=True)
    elif got: print(sig,"decoded:",dec_str(got),flush=True)
tfr="0x"+keccak.new(digest_bits=256,data=b"Transfer(address,address,uint256)").hexdigest()
zero="0x"+"0"*64
for w in (1000, 300):
    for ep in EPS:
        try:
            out=jrpc(ep,"eth_getLogs",[{"fromBlock":hex(blk-w),"toBlock":"latest","address":ADDR,"topics":[tfr,zero]}],timeout=20)
            if "error" in out: print("logs err w",w,ep,out["error"],flush=True); continue
            logs=out["result"]
            print("LOGS w",w,"via",ep,"count",len(logs),flush=True)
            if logs:
                f=logs[0]
                b=jrpc(ep,"eth_getBlockByNumber",[f["blockNumber"],False])
                ts=int(b["result"]["timestamp"],16)
                print("FIRST block",int(f["blockNumber"],16),"tx",f["transactionHash"],"time UTC",ts,time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(ts)),flush=True)
                json.dump({"first_block":int(f["blockNumber"],16),"first_tx":f["transactionHash"],"first_time_utc":ts,"count_window":len(logs),"window":w},open("run-2026-11-06-0954-9211-firstmint.json","w"),indent=1)
            break
        except Exception as e: print("logs fail w",w,ep,repr(e),flush=True)
    else:
        continue
    break
print("DONE")
