#!/usr/bin/env python3
"""Run 0131 verify: wave 1511-1515, RuninAI, Compass/Fountain free counters. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
def dec_str(v):
    if not v: return None
    b=bytes.fromhex(v[2:])
    if len(b)>=64:
        ln=int.from_bytes(b[32:64],"big")
        if 0<ln<=len(b)-64: return b[64:64+ln].decode('utf-8','replace')
    return None
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0),16)
        except Exception: pass
def words(v):
    if not v: return None
    b=bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
def first_mints(C, head):
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
    out={"count":len(logs),"err":err}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        out.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep, "eth_getBlockByNumber", [hex(blks[0]), False], 8, retries=0); out["first_ts"]=int(b["timestamp"],16); break
            except Exception: pass
    return out

head=blk(); print("head",head)
out={"head":head}
WAVE={
 "Gourdwick":"0x0ae19c56570d1d8b7878c309c13847a737738ead",
 "Kitsunaru":"0x96838f487f3551db0a25a401ab221843b72b715e",
 "Nightsable":"0xc4f2797f050835daf3d24c1764eca60ac4168f21",
 "Lensorb":"0x1edfd1e6c6b132e88f5b09b1dbe025037b5b0539",
 "Nimaluo":"0xd531f1b8b56882c48ab5fe9be8c4855a54c90f26",
}
for nm,C in WAVE.items():
    r={"address":C,"name":dec_str(call(C,sel("name()"))),"symbol":dec_str(call(C,sel("symbol()")))}
    for fn in ["totalSupply()","freeClaimed()","freeLeft()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","PRICE()","FREE_PER_WALLET()"]:
        r[fn]=iv(call(C,sel(fn)))
    r["AGENT_ID"]=call(C,sel("AGENT_ID()"))
    r["mintedBy_user"]=iv(call(C,sel("mintedBy(address)")+enc_addr(USER)[2:]))
    r["freeUsed_user"]=iv(call(C,sel("freeUsed(address)")+enc_addr(USER)[2:]))
    r["freeFor_user"]=iv(call(C,sel("freeFor(address)")+enc_addr(USER)[2:]))
    r["balance_user"]=iv(call(C,sel("balanceOf(address)")+enc_addr(USER)[2:]))
    v=call(C,sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]); r["quote_user_1_words"]=words(v)
    r["first_mints"]=first_mints(C,head)
    out[nm]=r; print(nm, json.dumps(r))
RUN="0xfB50746BCc9D585AEb49cd410Fa0100b657ce9e6"
r={"address":RUN,"name":dec_str(call(RUN,sel("name()"))),"symbol":dec_str(call(RUN,sel("symbol()"))),"decimals":iv(call(RUN,sel("decimals()")))}
for fn in ["totalSupply()","freeClaimed()","freeShares()","maxShares()","phase()","startedAt()","endsAt()","launched()","launchFailed()","sold()","totalPaidTokens()","eligibleSupply()","pair()","perShare()"]:
    r[fn]=iv(call(RUN,sel(fn)))
r["pair_raw"]=call(RUN,sel("pair()"))
r["identity_user"]=call(RUN,sel("identity(address)")+enc_addr(USER)[2:])
r["freeClaimedById_user_addr"]=call(RUN,sel("freeClaimedById(address)")+enc_addr(USER)[2:])
r["remainingFor_user"]=words(call(RUN,sel("remainingFor(address)")+enc_addr(USER)[2:]))
r["freeTokensOf_user"]=iv(call(RUN,sel("freeTokensOf(address)")+enc_addr(USER)[2:]))
r["balance_user"]=iv(call(RUN,sel("balanceOf(address)")+enc_addr(USER)[2:]))
r["mintedById_user"]=call(RUN,sel("mintedById(address)")+enc_addr(USER)[2:])
r["quotaPerId"]=iv(call(RUN,sel("quotaPerId()")))
r["costFor_user"]=words(call(RUN,sel("costFor(address)")+enc_addr(USER)[2:])) if False else None
# costFor signature unknown; try quote(address,uint256) and quote(uint256)
for sig in ["quote(address,uint256)","quote(uint256)"]:
    arg=enc_addr(USER)[2:]+enc_uint(1)[2:] if "address" in sig else enc_uint(1)[2:]
    r[sig]=words(call(RUN,sel(sig)+arg))
r["first_mints"]=first_mints(RUN,head)
out["RuninAI"]=r; print("RuninAI", json.dumps(r))
for nm,C in (("Compass","0xBEeBD269A7636591823BCD5fdf0E378b33f24112"),("Windmill","0x35C9CDed0eC5d2b9A9f365b87Ef954b19E08465f"),("Fountain","0x81Fc58bD054b95de96ea4Bf37A4bD45E9B6e1f4e")):
    r={"address":C}
    for fn in ["totalMinted()","totalSupply()","FREE_SUPPLY()","MAX_SUPPLY()","currentPrice()","mintOpen()","freeClaimed()","freeCount()"]:
        r[fn]=iv(call(C,sel(fn)))
    r["agentIdRegistry"]=call(C,sel("agentIdRegistry()")); r["agentRegistry"]=call(C,sel("agentRegistry()"))
    r["mintedBy_user"]=iv(call(C,sel("mintedBy(address)")+enc_addr(USER)[2:]))
    r["costFor1"]=iv(call(C,sel("costFor(uint256)")+enc_uint(1)[2:]))
    r["balance_user"]=iv(call(C,sel("balanceOf(address)")+enc_addr(USER)[2:]))
    out[nm]=r; print(nm, json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0131-verify.json","w"), indent=1)
