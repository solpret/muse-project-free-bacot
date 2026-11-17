#!/usr/bin/env python3
"""Scan POA Minted events 133550000..head (5000-block chunks, parallel) + first-mint block timestamp. Read-only."""
import json, subprocess, time, concurrent.futures
from Crypto.Hash import keccak
ADDR="0x4D0923060D6f657dF4C2567b629e1C3ab8DBc5F5"
EP="https://bsc-dataseed.binance.org/"
def topic(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()
MINTED=topic("Minted(address,uint256,uint256,uint256)")
TRANSFER=topic("Transfer(address,address,uint256)")
ZERO="0x"+"0"*64
def rpc(method,params,timeout=60):
    p={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(p)],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
head=int(rpc("eth_blockNumber",[])["result"],16)
print("head",head,"MINTED topic",MINTED)
def chunk(a,b):
    r=rpc("eth_getLogs",[{"fromBlock":hex(a),"toBlock":hex(b),"address":ADDR,"topics":[MINTED]}])
    if "result" not in r: return (a,b,None,str(r)[:200])
    return (a,b,r["result"],None)
ranges=[(a,min(a+999,head)) for a in range(133550000,head+1,1000)]
t0=time.time()
all_logs=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    for a,b,logs,err in ex.map(lambda ab: chunk(*ab),ranges):
        if err: print("chunk",a,b,"ERR",err)
        else:
            print("chunk",a,b,"logs",len(logs))
            all_logs+=logs
print("chunks elapsed",round(time.time()-t0,1),"total Minted logs",len(all_logs))
free_tot=paid_tot=0
first=None
for lg in sorted(all_logs,key=lambda x:int(x["blockNumber"],16)):
    d=lg["data"][2:]
    w=[int(d[i:i+64],16) for i in range(0,len(d),64)]
    # Minted(minter, ?, ?, ?) — assume words: freeCount, paidCount, tokenId? print first few raw
    if first is None: first=lg
    free_tot+=w[1]; paid_tot+=w[2]
if first is None:
    print("NO Minted logs found in range - first mint earlier than 133550000 or event sig mismatch")
    json.dump({"head":head,"n_logs":0,"note":"no logs in 133550000..head"},open("run-2026-11-15-0031-probe-poa-logs.json","w"),indent=1)
else:
    print("first Minted log block", int(first["blockNumber"],16), "topics", first["topics"], "data words", [int(first["data"][2:][i:i+64],16) for i in range(0,len(first["data"][2:]),64)])
    print("sum word1:",free_tot,"sum word2:",paid_tot)
    fb=int(first["blockNumber"],16)
    blk=rpc("eth_getBlockByNumber",[hex(fb),False])
    ts=int(blk["result"]["timestamp"],16)
    import datetime
    print("first-mint block",fb,"timestamp",ts, datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"))
    json.dump({"head":head,"n_logs":len(all_logs),"sum_w1":free_tot,"sum_w2":paid_tot,
               "first_block":fb,"first_ts":ts,
               "first_log":first},open("run-2026-11-15-0031-probe-poa-logs.json","w"),indent=1)
