#!/usr/bin/env python3
import json, urllib.request, time
from Crypto.Hash import keccak
ADDR="0x921150815bF267a17bb372E44e6e3f44a05f54af"
EPS=["https://rpc.ankr.com/bsc","https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def jrpc(ep,method,params,timeout=10):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r: return json.load(r)
blk=None
for ep in EPS:
    try:
        blk=int(jrpc(ep,"eth_blockNumber",[])["result"],16); print("BLOCK",blk,"via",ep,flush=True); break
    except Exception as e: print("block fail",ep,repr(e),flush=True)
for sig,args in [("name()",""),("symbol()",""),("tokenURI(uint256)",format(1,"064x"))]:
    for ep in EPS:
        try:
            out=jrpc(ep,"eth_call",[{"to":ADDR,"data":sel(sig)+args},"latest"])
            print(sig,"raw:",out.get("result"),"err:",out.get("error"),flush=True); break
        except Exception as e: print(sig,"fail",ep,repr(e),flush=True)
tfr="0x"+keccak.new(digest_bits=256,data=b"Transfer(address,address,uint256)").hexdigest()
zero="0x"+"0"*64
for ep in EPS:
    try:
        out=jrpc(ep,"eth_getLogs",[{"fromBlock":hex(blk-5000),"toBlock":"latest","address":ADDR,"topics":[tfr,zero]}],timeout=20)
        if "error" in out: print("logs err",ep,out["error"],flush=True); continue
        logs=out["result"]
        print("LOGS via",ep,"count",len(logs),flush=True)
        if logs:
            f=logs[0]
            print("FIRST block",int(f["blockNumber"],16),"tx",f["transactionHash"],flush=True)
            b=jrpc(ep,"eth_getBlockByNumber",[f["blockNumber"],False])
            ts=int(b["result"]["timestamp"],16)
            print("FIRST time UTC",ts,"=",time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(ts)),flush=True)
            json.dump({"first_block":int(f["blockNumber"],16),"first_tx":f["transactionHash"],"first_time_utc":ts,"count_5000":len(logs)},open("run-2026-11-06-0954-9211-firstmint.json","w"),indent=1)
        break
    except Exception as e: print("logs fail",ep,repr(e),flush=True)
print("DONE")
