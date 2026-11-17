import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed1.defibit.io/","https://bsc-dataseed-public.bnbchain.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=10) as r: j=json.load(r)
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
feed=['0x056c0222cE93E415fe5E7974577715E722E439C9','0x025D5A1eD084636770FAD86229ac97D2f25f9244','0x8402Febcd6fFE2043eD36f7107712BB9a2FDE0fc','0x1619452C940230aaa10676e9f10bf204fB797777','0x3aa0c21ca50e47ca210289C14263e50D5f063b74','0xA588dF8311255069c05604c2e7C7465ECDCc4c88','0x3342Da62BD986B306A1D9da2c4395Cd300420582','0x78Fb44801E01Fd8e290568EDA975C79848fbdC64','0xF8CF986488DD675043021d8340DEE809A71AE1A7','0x857169CdE48cf9fD8874E26a43FbbcA838Fc56a1','0x5cFbe7a6968D7ACDA9cd127370fc0017DB19b486','0xdDBE18962479a683aEC5a78eB775340Ab51a9c1b','0x5AD666A89De917b4EabFB20De881A6776169d39c','0xb0Eb05D28c02CabfB42f26715153B4dB84CeEC38','0x13876666D7dbF30c4c63dbEBF370234E9417bd09','0xC4251a0e2ed024E5070a72692D535ddD3cb85aEF','0x69c2BA04381934AB3cD30Fd7Ffc00dfa41f989f1','0x981Ff66639414c41C80c9D89D39748e0840c7777','0x48CCcb8426aFC610212d9Ab376C36FE3E1E071Db','0x50cF1C98C46Cf78F04f2F61161EAdA02944fBc02']
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
        with urllib.request.urlopen(req,timeout=10) as r: out["block"]=int(json.load(r)["result"],16); break
    except Exception: continue
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-05-0249-probe.json","w"),indent=1)
print("DONE",out.get("block"))
