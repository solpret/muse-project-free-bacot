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
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
one="0"*63+"1"
tests=[("totalSupply()",""),("totalMinted()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("FREE_CARDS()",""),("MAX_SUPPLY()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u),("quote(address,uint256)",u+one),("freeFor(address,uint256)",u+one),("mintOpen()","")]
items={"Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD","Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0","Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551","Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286","Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c08348ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1eC4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10","Nightagent":"0xfd8D2E77c8AC50b2b75924ba528321B3cF6dE87b","Octagent":"0x3364aa233254873107b015926b337f32c50d17f4","Sidecoo":"0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8",
"StonkAgent":"0x97aa313cc690bb1a4aa4d92c306edaa50fa3a4e1","Pilotqilin":"0xca540b3520FCcD562C9cD57D000Ee828fB18223f","Neonmind":"0x0e42d40ff176ae2156b0da3668f9a5eb0565ffd6","Saturnode":"0x6124b3ae64adA7b73581CcD01fEF89e583E8742c","TOPA":"0xD9CC8C95dA13B0600DF1b3f6879A1892a0631392"}
def collect(to):
    return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
out={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,o in ex.map(rr,items.items()): out[n]=o; print("REREAD",n,o,flush=True)
out["TrackB_MINT"]={name: iv(call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",sel(name)+arg)) for name,arg in [("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")]}
out["DROID"]={name: iv(call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel(name)+arg)) for name,arg in [("FREE_SHARES()",""),("freeMinted()",""),("freeUsed(address)",u)]}
print("TrackB",out["TrackB_MINT"]); print("DROID",out["DROID"])
out["AgentAcres"]={name: iv(call("0x7a582f91fc6fED51C77b5199585F8050926d8bE0",sel(name)+arg)) for name,arg in [("totalPlotsMinted()",""),("freePlotsClaimed()",""),("freePlotsRemaining()",""),("freeWindowOpen()",""),("freeClaimedBy(address)",u),("balanceOf(address)",u)]}
print("AgentAcres",out["AgentAcres"])
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0154-probe.json","w"),indent=1)
print("DONE block",out["block"])
