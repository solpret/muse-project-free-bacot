#!/usr/bin/env python3
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception as e: err=str(e)[:100]
    return "ERR:"+err
def iv(v):
    try: return int(v,16)
    except Exception: return None
def txt(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],"big"); return b[64:64+ln].decode(errors="ignore")
    except Exception: return None
def addr(v):
    try: return "0x"+v[-40:]
    except Exception: return None
TARGETS=[
 "0x127F979E67383D882181fE6D408f30D954991317","0xdDF44Ae265172aB3141ecABaA3d823Edd9129581",
 "0x0594Be0719F16BD2e30B3b238f4336B0AB891dAd","0x1DfC6d367d107921CEB93cd7f7FC7f50d553FA55",
 "0x5606C2d70e390dd0ec0B0C3079d567063faD415C","0x3Ff101ca8786A88AfF24674380cd0E811E442797",
 "0xcdeF985C3B7179880b78DB8DD3e266eC97420f5C","0x26D47f91a72035778a768Fbc7D6F78949f9e5A2B",
 "0x961F7999F616EE70252A6aFf711584B9cdd9404c","0xf7f329477603d6Df2E89bdef41f82Aa122c14A4f",
 "0x1A9088f4254ef27f3cd7329E39d8Be4BB92B1bb3",
]
def blk():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
head=blk(); print("head",head, flush=True)
out={"head":head}
for C in TARGETS:
    r={}
    r["name"]=txt(call(C,sel("name()"))); r["symbol"]=txt(call(C,sel("symbol()")))
    r["totalMinted"]=iv(call(C,sel("totalMinted()"))); r["totalFreeMinted"]=iv(call(C,sel("totalFreeMinted()")))
    r["totalPaidMinted"]=iv(call(C,sel("totalPaidMinted()"))); r["freeAllocation"]=iv(call(C,sel("freeAllocation()")))
    r["remainingFreeSupply"]=iv(call(C,sel("remainingFreeSupply()"))); r["maxSupply"]=iv(call(C,sel("maxSupply()")))
    r["agentRegistry"]=addr(call(C,sel("agentRegistry()")))
    r["freeMintedByWallet"]=iv(call(C,sel("freeMintedByWallet(address)")+enc(USER)))
    r["balance"]=iv(call(C,sel("balanceOf(address)")+enc(USER)))
    r["owner"]=addr(call(C,sel("owner()")))
    print(C, r, flush=True)
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(131240000),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,"topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs",params,timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(2.5)
    fm={"count":len(logs),"err":err,"pages":pages}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        fm.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blks[0]),False],8,retries=0); ts=int(b["timestamp"],16)
                fm["first_wib"]=datetime.datetime.fromtimestamp(ts,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"); break
            except Exception: pass
    r["first"]=fm; print(" first",fm, flush=True)
    out[C]=r
    time.sleep(2.5)
json.dump(out, open(BASE+"run-2026-11-02-2101-sourcify-verify.json","w"), indent=1)
print("DONE")
