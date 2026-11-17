#!/usr/bin/env python3
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: j=json.load(r)
            v=j.get("result")
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def block():
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
GEN=[("totalSupply()",""),("totalMinted()",""),("freeClaimed()",""),("freeMinted()",""),("FREE_SUPPLY()",""),("mintOpen()",""),("balanceOf(address)",u),("mintedBy(address)",u),("freeClaimed(address)",u)]
items={
 "HIVE":"0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
 "Tigora":"0xE8c46E7c734259FEc1A78Fc846DcFaD94Ecb70E5",
 "BNBRunnerz":"0x8AAA14b24e71cC93672939ba3e3C3e9DE2674d27",
 "Shroomies":"0x2AE712138a74202daBB8FFC93117AA53754F54D0",
 "Blobbies":"0xa7fBAB4a96d6900122Dc51FDC839CFE5C89B23b3",
 "Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24",
 "Jolly":"0xdc11764a5664e333c8d303eb465e89a1caadb85b",
 "HACKED":"0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77",
 "SoulAgent":"0x8fdB9411753c58476A41F7B88a44989F8D687d63",
 "PERSONA":"0xA930C4466431B0331C911846f297D7D4e063249D",
}
def collect(to,tests): return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
out={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,GEN)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,o in ex.map(rr,items.items()): out[n]=o; print("REREAD",n,o,flush=True)
out["HACKED_extra"]=collect(items["HACKED"],[("freeDone(address)",u),("remainingFor(address)",u),("isAiHolder(address)",u),("maxSupply()", ""),("MAX_SUPPLY()","")])
out["Soul_extra"]=collect(items["SoulAgent"],[("quoteFor(address,uint256)",u+one),("mintedPerWallet(address)",u),("FREE_TIER_END()",""),("hasAgentId(address)",u)])
out["PERSONA_extra"]=collect(items["PERSONA"],[("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("freeMinted(address)",u),("mintEndsAt()","")])
out["BINANCEAI"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("totalShares()",""),("isRefundPhase()",""),("failed()",""),("tokenClaimed(address)",u)])
out["FABE"]=collect("0xFabE022a5943462fee1Bd221791945DA57510BE8",[("launched()",""),("freeSharesRemaining()",""),("freeSharesClaimed(address)",u)])
out["SENBAZURU"]=collect("0xb21583A08581278BcF925351a99C61A4562C62f0",[("freeClaimed()",""),("opened()",""),("hasFreeShare(address)",u)])
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0301-reread.json","w"),indent=1)
print("DONE block",out["block"])
