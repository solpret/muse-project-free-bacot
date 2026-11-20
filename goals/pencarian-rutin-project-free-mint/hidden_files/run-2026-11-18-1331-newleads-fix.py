#!/usr/bin/env python3
"""Fix run 1331 newleads: the 35-call single batch was rejected by dataseed
(-32005 batch rate limit) so every contract recorded only totalSupply=revert.
Re-read the 6 interesting contracts with chunked (<=5) parallel batches.
Read-only."""
import json, subprocess, concurrent.futures as cf
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def post(payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def batch5(addr, views):
    calls=[]
    for label,sig,arg in views:
        data="0x"+sel(sig)
        if arg=="user": data+=enc_addr(USER)
        elif arg=="one": data+="%064x"%1
        elif arg=="user1": data+=enc_addr(USER)+"%064x"%1
        calls.append((addr,data))
    res=[]
    def one(chunk):
        payload=[{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":to,"data":d},"latest"]} for i,(to,d) in enumerate(chunk)]
        resp=post(payload)
        if not isinstance(resp,list): raise IOError(f"non-list: {str(resp)[:150]}")
        by={it["id"]:it for it in resp if isinstance(it,dict)}
        out=[]
        for i in range(len(chunk)):
            it=by.get(i+1,{})
            if "result" in it and it["result"] not in (None,"0x"):
                try: out.append(int(it["result"],16))
                except Exception: out.append(it["result"])
            elif "error" in it: out.append("revert")
            else: out.append(None)
        return out
    chunks=[calls[i:i+5] for i in range(0,len(calls),5)]
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        parts=list(ex.map(one,chunks))
    for p in parts: res+=p
    return {label:val for (label,sig,arg),val in zip(views,res)}
VIEWS=[("totalSupply","totalSupply()",None),("totalMinted","totalMinted()",None),
("mintingOpen","mintingOpen()",None),("mintOpen","mintOpen()",None),
("freeMinted","freeMinted()",None),("freeClaimed","freeClaimed()",None),
("freeLeft","freeLeft()",None),("FREE_SUPPLY","FREE_SUPPLY()",None),
("FREE_CAP","FREE_CAP()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
("name","name()",None),("symbol","symbol()",None),
("agentRegistry","agentRegistry()",None),("agentIdRegistry","agentIdRegistry()",None),
("agentId","agentId()",None),("quote_user_1","quote(address,uint256)","user1"),
("cost_user_1","cost(address,uint256)","user1"),
("balanceOf_user","balanceOf(address)","user"),
("freeMintedBy_user","freeMintedBy(address)","user"),
("mintedBy_user","mintedBy(address)","user"),
("freeClaimed_user","freeClaimed(address)","user"),
("freeUsed_user","freeUsed(address)","user"),
("claimable_user","claimable(address)","user"),
("claimed_user","claimed(address)","user"),
("hasClaimed_user","hasClaimed(address)","user"),
("endsAt","endsAt()",None),("endTime","endTime()",None),
("closesAt","closesAt()",None),("isOpen","isOpen()",None),
("saleOpen","saleOpen()",None),("freeSupply","freeSupply()",None),
("holdsAgentId_user","holdsAgentId(address)","user"),
("mintOpensAt","mintOpensAt()",None),("mintStart","mintStart()",None),
("startTime","startTime()",None),("openAt","openAt()",None),
("price","price()",None),("PRICE","PRICE()",None),
("paidMinted","paidMinted()",None),("paused","paused()",None),
("freeRemaining","freeRemaining()",None),("totalFree","totalFree()",None),
("freeCap","freeCap()",None),("maxPerWallet","maxPerWallet()",None)]
out={}
for addr,tag in [("0x02A9830b695229d0BcAa39d236778C257b87D85b","Urbanova-02a9"),
("0x83d30e4bb1793d85ac315ed8792d6c1ef1572715","ZoraAgent-83d3"),
("0xa2556377118dD333F9f09600DE0bBCf54Cbc69A0","PTAH-IAO-a255"),
("0xf92e693f43428d5cd1a85acb2cd8e242a717e964","OrinAgent-f92e"),
("0x7dF7fD03bD5b7a024B1341849AaD14758f12a4A8","Sourcify-7dF7"),
("0xc116b90c1Fb4e19cde4Fb93e7546841D4a54A6cB","Sourcify-c116")]:
    try:
        v=batch5(addr,VIEWS)
    except Exception as e:
        v={"error":f"{type(e).__name__}: {str(e)[:150]}"}
    out[tag]={"address":addr,"views":v}
    print(tag, json.dumps({k:val for k,val in v.items() if val not in (None,"revert")}, default=str))
json.dump(out,open(f"{HF}/run-2026-11-18-1331-newleads-fix.json","w"),indent=1)
print("saved run-2026-11-18-1331-newleads-fix.json")
