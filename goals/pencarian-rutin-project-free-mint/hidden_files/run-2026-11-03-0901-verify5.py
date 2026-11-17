#!/usr/bin/env python3
"""Run 0901: verify 5 agent-shaped first-seen NFT candidates + pre-window Ankr check. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(to,data):
    for ep in EPS:
        try:
            v=_single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
            return int(v,16) if v else None
        except Exception: pass
    return None
def block():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
CANDS={"Animora":"0x150699b44B36b542B9F954272bDD0aC3fDD9519b","Golemar":"0x4e06728894F3f31CbB32B97d6905639FfE2a147B","Homunqul":"0x5539dD54c00094Cbd186f08AA2d8fF3A8c098ddE","Praxion":"0xEA1e4AA5ecD147035eB005aDc8013959bA852799","Eidolyn":"0x94c4834B186938F95EDC67FF0536Ac17F3102523"}
VIEWS=["totalSupply()","freeClaimed()","FREE_SUPPLY()","freeLeft()","mintOpen()"]
out={"block":block()}
for n,a in CANDS.items():
    d={v: call(a, sel(v)) for v in VIEWS}
    d["mintedBy_user"]=call(a, sel("mintedBy(address)")+enc(USER))
    d["freeUsed_user"]=call(a, sel("freeUsed(address)")+enc(USER))
    d["balance_user"]=call(a, sel("balanceOf(address)")+enc(USER))
    out[n]=d; print(n, d, flush=True)
# Pre-window Ankr: one 2000-block chunk immediately before scan window (131349241-131351240)
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
for n,a in CANDS.items():
    try:
        body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(131349241),"toBlock":hex(131351240),"address":a,"pageSize":1000,"decodeLogs":False,"topics":[TRANSFER,ZERO]}, timeout=30)
        res=body.get("result",body) if isinstance(body,dict) else body
        logs=res.get("logs",[]) if isinstance(res,dict) else []
        out[n]["prewindow_131349241_131351240_mints"]=len(logs)
        print(n, "prewindow mints", len(logs), flush=True)
    except Exception as e:
        out[n]["prewindow_error"]=str(e)[:160]; print(n, "prewindow ERROR", str(e)[:160], flush=True)
json.dump(out, open(BASE+"run-2026-11-03-0901-verify5.json","w"), indent=1)
