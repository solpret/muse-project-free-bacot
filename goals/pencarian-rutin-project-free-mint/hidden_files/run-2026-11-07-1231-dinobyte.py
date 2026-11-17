#!/usr/bin/env python3
"""Verify DINOBYTE (Boltbook new) + KALOS + 2 feed contracts. Read-only.
Writes run-2026-11-07-1231-dinobyte.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch, race
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, sig, arg=None):
    data=sel(sig)+(enc(arg) if arg else "")
    for ep in ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/"]:
        try:
            r=batch([("eth_call",[{"to":addr,"data":data},"latest"])], endpoint=ep, timeout=8)
            return r[0]
        except Exception: continue
    return None
def ti(v):
    try: return int(v,16)
    except Exception: return None
def ts(v):
    try:
        b=bytes.fromhex(v[2:])
        if len(b)>=64:
            ln=int.from_bytes(b[64:96],"big"); return b[96:96+ln].decode(errors="replace")
    except Exception: return None
    return None
def block_ts(n):
    try:
        r=batch([("eth_getBlockByNumber",[hex(n),False])], endpoint="https://bsc-dataseed1.bnbchain.org/", timeout=10)
        return int(r[0]["timestamp"],16)
    except Exception: return None
def first_mint(addr, floor_blocks=30000):
    head=int(race("eth_blockNumber",[]),16)
    frm=head-floor_blocks; b=frm; first=None; calls=0
    while b<=head and first is None:
        e=min(b+999,head); calls+=1
        try:
            r=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(b),"toBlock":hex(e),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":addr.lower()},timeout=30)
            logs=r.get("result",{}).get("logs",[])
            if logs: first={"block":int(logs[0]["blockNumber"],16),"tx":logs[0]["transactionHash"],"count_in_chunk":len(logs)}
        except Exception as ex:
            return {"error":str(ex),"calls":calls,"searched_from":frm,"head":head}
        b=e+1
    return {"first":first,"calls":calls,"searched_from":frm,"head":head}
CANDS={
 "DINOBYTE":"0xd713ddfd37b8ff759afaeedaedad632d1985ed9c",
 "KALOS":"0xd45bdd6aa5e4a6c5446a02cd1d3ec662f3ed55e6",
 "FEED-9A02":"0x9A020F20Ef0fD41db05D3cc1e2b54D63936d94D8",
 "FEED-A900":"0xa900873E65B5F391B6E37d80a98A6b26D07613B8",
}
VIEWS=["name()","symbol()","totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","owner()","AGENT_ID()","agentRegistry()","PRICE()","FREE_PER_WALLET()","contractURI()"]
out={}
for name,addr in CANDS.items():
    d={"address":addr}
    for sig in VIEWS:
        v=call(addr,sig)
        key=sig.split("(")[0]
        d[key]=ts(v) if key in ("name","symbol","contractURI") else (v if key in ("owner","agentRegistry") else ti(v))
    d["quote_user_1"]=ti(call(addr,"quote(address,uint256)",USER) or "")
    # quote signature may differ; try quote(uint256) too
    if d["quote_user_1"] is None:
        q=call(addr,"quote(uint256)")
        d["quote_user_1"]=ti(q) if q else None
    d["freeLeft_user"]=ti(call(addr,"freeLeft(address)",USER) or "")
    d["mintedBy_user"]=ti(call(addr,"mintedBy(address)",USER) or "")
    d["balanceOf_user"]=ti(call(addr,"balanceOf(address)",USER) or "")
    fm=first_mint(addr)
    d["first_mint_search"]=fm
    if fm.get("first"):
        blk=fm["first"]["block"]; t=block_ts(blk)
        d["first_mint_block"]=blk; d["first_mint_ts"]=t
        if t: d["first_mint_wib"]=time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(t+7*3600))
    out[name]=d
    print(name, json.dumps(d), flush=True)
json.dump(out,open("run-2026-11-07-1231-dinobyte.json","w"),indent=1)
print("DINOBYTE-VERIFY DONE",flush=True)
