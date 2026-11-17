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
new=['0x5625ec03f6e845975168d4B410c13c491Ad83f07', '0xcAB52dCee96655a4aA44296E961F400d7c521577', '0x825ed2B1A5eE2874739d362F363ADB8f6B056fE6', '0x2D349E517e98452DD7f430Aa04Db72ec439D7E18', '0x82c9c988d1b3bd76a17EB82a9F1028FAD6B0fC33', '0xDe7D6B62dB537bC9066C9Ac12a6B2087C6528390', '0xFE81daC95f41b4012E83D36206f618589E0a2c38', '0x9D550538141406051c870B2ae18F7dB3dbDdC33a', '0xA1FeF343DCC58C5AE7DF57152ee75434C4f93F3D', '0x58a7730265f616609fbc308b34fC01590F988d47', '0x51794cB4675E028FF72A7e76573F433E964016Fc', '0xc17A1ed8A9e0b00BE64403C8fbA301940dd13dE9', '0x371bD1b7B8bA25B2E70171ee3b93800D84e471F6', '0xb8A2b961b40FD64eA5457b50AF19137Ca52Fee37', '0xbe1921086748cd3F33E32522B486637C77bE0C5a', '0xec35f2C067f0A4A3360c5Fec74348b8Ee626164f', '0xeB2Cb2EBd1143c9aA2047A0cCe8387Cd6090A8bd', '0xa483E8378CE6bCE5a9816Ad461e0B489758931bF', '0x782F789193d6609b70B8c4d388E57DDfF5b6A893', '0x1BDACD864F1b76cAB7dC65E6f44d7491db367777']
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
json.dump({"shape":shape_out,"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0024-probe.json","w"),indent=1)
print("DONE block",reread["block"])
