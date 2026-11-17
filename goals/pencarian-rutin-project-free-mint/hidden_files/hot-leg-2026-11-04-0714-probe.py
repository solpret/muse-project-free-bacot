#!/usr/bin/env python3
"""Hot-leg 0714: threaded RPC probes (read-only): shape for 20 new Sourcify feed contracts + re-read subset (copy of 0654 items)."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: v=json.load(r)["result"]
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
feed=["0x0cF2b6a092D128c4c9863a223740b77984cfC1F7","0x2ac042f8e45CCCf91b8D7D86b69CC6Fe40f8Aa13","0x92DB21A81DAbC362A32975dE01dC731ab0DB3431","0xec56a80155B09105D7A4f1969A310DfdcdABF9c5","0xe175a2a041700D50A99080aC8782a1Abfb14D21e","0xe1C6b324d7E21c465D35f4084B7cC1bC7beC7777","0x646458B71b0333eCD1F27BAd6003a4c9876ABbe5","0x1d876d89Bde4a8271f5292e747B74Aae9Fa48679","0x9b3b0E29863De51E2b799f8E72Ed23Ae4f74388C","0xf9c6026cb45d52F61E1469523E86683da04f8F93","0xe9BA85A0943E337a3A1bE44DEc28aCE122Ea61cb","0x90531d79633560eBFe1afb353002A02FAFfa58F4","0x7Dd291F6eD842524F12F4CE28581eF29b4e1F5C2","0x581D88105c2FE31fC2f4E74a2516238dB149d994","0x427f3Ae15AdEA49E335349bf6007C3F062EBfa40","0xb89D270f877cA8cDdF683AB2e05dd4b9bB9383Ab","0x8b1D6af3c2AB8c2F5C4Ea260b06aD00e42123192","0xE3b84Aacb557586F43A9c21f73E4897AcE7523d3","0xaF19d44BA22681a2c0A44690cc1148CEEb31E030","0x5f4Ca33d911c55dcb4c7d2C1cC0887BfEc2F2fB6"]
views=["totalSupply()","decimals()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_SLOTS()","freeSharesRemaining()","freeAvailable()"]
def probe(a):
    out={}
    for v in views: out[v]=iv(call(a,sel(v)))
    for fn in ("agentRegistry()","registry()"):
        raw=call(a,sel(fn)); out[fn]=("0x"+raw[-40:]) if raw and len(raw)>=42 else None
    return a,out
shape={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,out in ex.map(probe,feed): shape[a]=out; print("SHAPE",a,out,flush=True)
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
early=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u)]
items={"Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD","Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0","Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551","Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286","Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1e2C4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10"}
def collect(to,tests):
    return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
reread={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,early)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,out in ex.map(rr,items.items()): reread[n]=out; print("REREAD",n,out,flush=True)
reread["TrackB_MINT"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")])
reread["DROID"]=collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",[("FREE_SHARES()",""),("freeMinted()",""),("freeUsed(address)",u)])
print("REREAD TrackB",reread["TrackB_MINT"]); print("REREAD DROID",reread["DROID"])
json.dump({"shape":shape,"reread":reread},open("hot-leg-2026-11-04-0714-probe.json","w"),indent=1)
print("DONE block",reread["block"])
