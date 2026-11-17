import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=5) as r: j=json.load(r)
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
feed=['0xEfA739e51E76f286c010fC19a0D3ED86919C167c','0xe06FbCce9b843931253D36AFD2ACa75E8be78112','0x0805E3C5CC73ba1D0bBfb08C412E9726b93c6A28','0x1FD392fFF2c80be3ff7226487d2A0D8f93e48c43','0xFF7Af2eB89583f3F706540915485F541bf1E30C0','0x9258DEd610e75acFB21CF7c05D18F06Ae205e256','0xc1bfd9B64b776B8F2d36C17E088b919001CB36EA','0xBe8Fa7C0AC1EEa5d4f9E730948920b602C017777','0xEcdf21967dbA8D1453e0CC843145493Cf607d9AF','0x3A2fdb08def9975cb5c37a154Ce557fA6167425B','0xe73f162e0728e62Ee1ebC50DA1E79333Acd1E8bC','0x352A7f23061A4B789e754cd58a8387e598D540b6','0x097db58EaC55Ad8B2a4f8dE14efD6521d54a6cF2','0x0437eF244A54Eb31eF9F1A7539A8F1c864AF6205','0x0aaC0ff763b6C71B24E2017A3aA4E7bE3290f3bE','0x1F00DC58758398bfC2C32A31B9772D5D321746cB','0x2DcdB4337FbBa58Be37d4d9a73e92722A6606A99','0x7053392cf7766ba375dfFF4208e47D43940dc34a','0x462704785f8F05f108E512937Ffb9ef362f57777','0x7B224D32625Ba4C0595F1D7E88238eE5Fa15Ac87']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    for n,arg in [("freeClaimed()",u),("freeClaimed(address)",""),("freeMinted()",""),("FREE_SUPPLY()",""),("FREE_SLOTS()",""),("FREE_CARDS()",""),("quote(address,uint256)",u+one),("freeAvailable(address)",u),("freeFor(address,uint256)",u+one),("mintOpen()",""),("totalMinted()","")]:
        # freeClaimed(address) needs arg; handle: use u for address variants
        data=sel(n)+(u if "address" in n and "uint256" not in n else arg)
        o[n]=iv(call(a,data))
    o['agentRegistry']=call(a,sel("agentRegistry()"))
    o['registry']=call(a,sel("registry()"))
    return o
out={"shape":{}}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out["shape"][a]=o; print("SHAPE",a,o,flush=True)
# reread (reuse items from 0154 script)
import importlib.util
# inline reread items
items={"Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD","Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0","Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551","Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286","Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c08348ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1eC4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10","Nightagent":"0xfd8D2E77c8AC50b2b75924ba528321B3cF6dE87b","Octagent":"0x3364aa233254873107b021926b337f32c50d17f4","Sidecoo":"0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8","StonkAgent":"0x97aa313cc690bb1a4aa4d92c306edaa50fa3a4e1","Pilotqilin":"0xca540b3520FCcD562C9cD57D000Ee828fB18223f","Neonmind":"0x0e42d40ff176ae2156b0da3668f9a5eb0565ffd6","Saturnode":"0x6124b3ae64adA7b73581CcD01fEF89e583E8742c","TOPA":"0xD9CC8C95dA13B0600DF1b3f6879A1892a0631392"}
tests=[("totalSupply()",""),("totalMinted()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("FREE_CARDS()",""),("MAX_SUPPLY()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u),("quote(address,uint256)",u+one),("freeFor(address,uint256)",u+one),("mintOpen()","")]
def collect(to): return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
out["reread"]={}
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,o in zip(items, ex.map(lambda a: collect(items[a]), items)): out["reread"][n]=o; print("REREAD",n,o,flush=True)
out["TrackB"]={name: iv(call("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",sel(name)+arg)) for name,arg in [("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")]}
out["DROID"]={name: iv(call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel(name)+arg)) for name,arg in [("FREE_SHARES()",""),("freeMinted()",""),("freeUsed(address)",u)]}
out["AgentAcres"]={name: iv(call("0x7a582f91fc6fED51C77b5199585F8050926d8bE0",sel(name)+arg)) for name,arg in [("totalPlotsMinted()",""),("freePlotsClaimed()",""),("freePlotsRemaining()",""),("freeWindowOpen()",""),("freeClaimedBy(address)",u),("balanceOf(address)",u)]}
# block
p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
for ep in EPS:
    try:
        req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=5) as r: out["block"]=int(json.load(r)["result"],16); break
    except Exception: continue
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0219-probe.json","w"),indent=1)
print("DONE",out.get("block"))
