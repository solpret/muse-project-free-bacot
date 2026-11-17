#!/usr/bin/env python3
"""Run 0401 verify: 5 new Sourcify wave contracts (agent shape). Read-only."""
import json, sys, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_u(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
def dec_str(v):
    if not v: return None
    b=bytes.fromhex(v[2:])
    if len(b)>=64:
        ln=int.from_bytes(b[32:64],"big")
        if 0<ln<=len(b)-64: return b[64:64+ln].decode("utf-8","replace")
    return None
def blk():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
CANDS=["0x626cd91e26Da5AC49B713Ab14894f54AbC4DC4DB","0xaB453745b37634C27d65b347B3aC514882cB2F37","0xcc5608A7F5A5Bc8F1bEABcD010A8C0066a0243Ae","0xB5a083bd9E8E330085e8F459F13f080d4F8fE5B4","0x33D66b461E55d6969ACfAe0C95dACf158F8d04B0"]
head=blk(); out={"head":head}
for C in CANDS:
    d={}
    d["name"]=dec_str(call(C, sel("name()"))); d["symbol"]=dec_str(call(C, sel("symbol()")))
    for fn in ["totalSupply()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","FREE_PER_WALLET()","PRICE()"]:
        d[fn]=iv(call(C, sel(fn)))
    d["AGENT_ID_raw"]=call(C, sel("AGENT_ID()"))
    d["mintedBy_user"]=iv(call(C, sel("mintedBy(address)")+enc(USER)[2:]))
    d["freeUsed_user"]=iv(call(C, sel("freeUsed(address)")+enc(USER)[2:]))
    d["balance_user"]=iv(call(C, sel("balanceOf(address)")+enc(USER)[2:]))
    v=call(C, sel("quote(address,uint256)")+enc(USER)[2:]+enc_u(1)[2:])
    if v:
        b=bytes.fromhex(v[2:]); d["quote_user_1"]=[int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
    else:
        v2=call(C, sel("quote(uint256)")+enc_u(1)[2:])
        d["quote_1"]=v2
    # first mints
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(131060000),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,
                "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(1)
    lg={"count":len(logs),"err":err,"pages":pages}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        lg.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blks[0]),False],8,retries=0)
                ts=int(b["timestamp"],16); lg["first_wib"]=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat(); break
            except Exception: pass
    d["logs"]=lg
    out[C]=d
    print(C, d["name"], d["symbol"], "tot", d["totalSupply()"], "free", d["freeClaimed()"], "FS", d["FREE_SUPPLY()"], "open", d["mintOpen()"], "AGENT_ID", d["AGENT_ID_raw"], "userMinted", d["mintedBy_user"], "quote", d.get("quote_user_1"), "logs", lg)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0401-wave.json","w"), indent=1)
