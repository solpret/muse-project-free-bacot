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
new=["0x4D31F0b379a17DC169f29Ede06c65AA541742543","0x3C43a4E5696de5785f4587595411F5dB12E1a06c","0x526c066314313fE856548C4B2e366672b2b91092","0x9699D33599AcEd9480BBcB3a4af0A03408157777","0x97403A050402d9ef643B82115f609986C0a16b99","0x24F5e0679BEa9833738eEb4495706994bCA52117","0x20b44a87da27e98969E5F63894B83263D5a38cb0","0x88261c81b34bCCe7d319A5AD33CE02Fa8254473C","0x45861FEd21B7Dcda21B6bbd8DB6078FAe3c7F09C","0xD418E890daDE5EF895e3D1f85109AD4e2A996D26","0xce3d6Fa95cA16e0F4927882D2201a9D8C16476eA","0x41442e59c8360e76B2577382E1249b417758Eb04","0x6CB345C9058aACF92883F1636edefADAb2BB7249","0x29cc0DC0b87F530B8F7F11283Ee6CA8ca29Ba53E","0xc181d5f4B7B1534A4Cbf858561BfECB7189a2455","0xe76a7C425603c9Ece8F065ee9aBe303C6cdda5C6","0xbDaCd2907553B568e47cDA50476a13664c78e491","0xf05AB8e8C5CD3777adC27FA993979817891391A9","0xf2E77Fc2170a9b4bE96fe97A01972925327B856e","0xc200A0CF0B59E57ee31e64f21ed4473258837777"]
tests=[("name()",""),("symbol()",""),("decimals()",""),("totalSupply()",""),("FREE_SUPPLY()",""),("FREE_SLOTS()",""),("FREE_AMOUNT()",""),("freeMinted()",""),("freeClaimed(address)",u),("freeClaimed()",""),("freeLeft(address)",u),("freeSharesRemaining()",""),("freeSharesClaimed()",""),("freeUsed(address)",u),("mintedBy(address)",u),("quote(address,uint256)",u+one),("registry()",""),("agentRegistry()",""),("contractURI()",""),("tokenURI(uint256)","0"*63+"1")]
def shape(a):
    out={}
    for name,arg in tests:
        v=call(a,sel(name)+arg)
        if v is not None:
            out[name]=v if name in ("name()","symbol()","registry()","agentRegistry()","contractURI()","tokenURI(uint256)") else iv(v)
    return out
shape_out={}
with ThreadPoolExecutor(max_workers=15) as ex:
    for a,out in zip(new, ex.map(shape,new)):
        shape_out[a]=out; print("SHAPE",a,out,flush=True)
early=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u)]
items={"Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD","Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0","Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551","Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286","Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c08348ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1eC4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10","Nightagent":"0xfd8D2E77c8AC50b2b75924ba528321B3cF6dE87b","Octagent":"0x3364aa233254873107b015926b337f32c50d17f4","Sidecoo":"0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8"}
def collect(to,tests2):
    return {name: iv(call(to,sel(name)+arg)) for name,arg in tests2}
reread={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,early)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,out in ex.map(rr,items.items()): reread[n]=out; print("REREAD",n,out,flush=True)
reread["TrackB_MINT"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")])
reread["DROID"]=collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",[("FREE_SHARES()",""),("freeMinted()",""),("freeUsed(address)",u)])
print("REREAD TrackB",reread["TrackB_MINT"]); print("REREAD DROID",reread["DROID"])
json.dump({"shape":shape_out,"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0109-probe.json","w"),indent=1)
print("DONE block",reread["block"])
