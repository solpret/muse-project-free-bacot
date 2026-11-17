#!/usr/bin/env python3
"""Triage 3 Sourcify-feed contracts with mint+free views but no ABI registry ref.
Checks name/symbol/totalSupply/free views + AGENT_ID/agentRegistry reads + first mint via Ankr getLogs.
Read-only; writes run-2026-11-07-1231-feed-triage.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak
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
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def to_str(v):
    try:
        b=bytes.fromhex(v[2:])
        if len(b)>=64:
            off=int.from_bytes(b[32:64],"big"); ln=int.from_bytes(b[64:96],"big")
            return b[96:96+ln].decode(errors="replace")
    except Exception: return None
    return None
CANDS=["0xd45bDd6aA5E4a6c5446a02cD1D3Ec662f3Ed55E6","0x9A020F20Ef0fD41db05D3cc1e2b54D63936d94D8","0xa900873E65B5F391B6E37d80a98A6b26D07613B8"]
out={}
for addr in CANDS:
    d={"address":addr}
    d["name"]=to_str(call(addr,"name()") or "")
    d["symbol"]=to_str(call(addr,"symbol()") or "")
    d["totalSupply"]=to_int(call(addr,"totalSupply()") or "")
    d["freeClaimed"]=to_int(call(addr,"freeClaimed()") or "")
    d["freeMinted"]=to_int(call(addr,"freeMinted()") or "")
    d["FREE_SUPPLY"]=to_int(call(addr,"FREE_SUPPLY()") or "")
    d["mintOpen"]=to_int(call(addr,"mintOpen()") or "")
    d["AGENT_ID"]=to_int(call(addr,"AGENT_ID()") or "")
    d["agentRegistry"]=call(addr,"agentRegistry()")
    # first mint: Transfer from zero, search back 200k blocks in 1000-block chunks via Ankr
    from fast_rpc import race as _race
    head=int(_race("eth_blockNumber",[]),16)
    first=None; total_logs=0
    frm=max(head-200000,0)
    # binary-ish scan: chunked from frm upward, stop at first hit
    b=frm
    while b<=head and first is None:
        e=min(b+999,head)
        try:
            r=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(b),"toBlock":hex(e),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":addr.lower()},timeout=30)
            logs=r.get("result",{}).get("logs",[])
            total_logs+=len(logs)
            if logs:
                first={"block":int(logs[0]["blockNumber"],16),"tx":logs[0]["transactionHash"]}
        except Exception as ex:
            first={"error":str(ex)}; break
        b=e+1
    d["first_mint"]=first; d["head"]=head; d["logs_scanned"]=total_logs
    out[addr]=d
    print(addr,"name=",d["name"],"sym=",d["symbol"],"supply=",d["totalSupply"],"freeClaimed=",d["freeClaimed"],"FREE_SUPPLY=",d["FREE_SUPPLY"],"AGENT_ID=",d["AGENT_ID"],"first_mint=",first,flush=True)
json.dump(out,open("run-2026-11-07-1231-feed-triage.json","w"),indent=1)
print("FEED-TRIAGE DONE",flush=True)
