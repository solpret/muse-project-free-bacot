#!/usr/bin/env python3
"""Run 0901 re-read (read-only), same subset as run 0701."""
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
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
early=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u),("totalFreeMinted()","")]
items={
"Nano Narwhals":"0x3c1d49451791eE8bE33FD766A879b4A79B9a06e5","Neon Badgers":"0x662e144aFEF030E6e24236337c72FA3a53C15793","Byte Otters":"0x654461557A3CA8397EA21BA04A06a65bEC03b4Ba","Circuit Capybaras":"0xB2DD7a694eb8F85b92074Cf8070E615a4E84766C","Orbit Axolotls":"0xE1eF6f4AcBfe2d257C135b644FA4bFdd498536e7","Signal Owls":"0xFFe8ED361Ce18E9fa7C418C39272E1d9186cfdda","Echo Salamanders":"0xB7f871d9582D058Bb3B3D0c1aC7F1C2C27Ac7fa1","Vector Vultures":"0xC61B5c2c2399edAda510E4AB6782FBCAF892365E",
"Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","Mummyhive":"0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd","Glitchdroid":"0xe3F0085fd94D4Fb2AE9ACb4B49f6c0504E3546A0","Agentvolt":"0xB04af24bBFA0EF441091178E61A724163e2828Cc","Agentyyds":"0x8463abFC06173BdCaEDe96c4331C30A958789629","Pilotphoenix":"0xc1A54df271a455E236169F8Ff65b084eBfB00E15","Pilotneon":"0x01D0f3b16C89615c924007ae85779B55A22552D0","Agentzhenxiang":"0xdA3C6681Ce380896Ec6BD02d96f8AE0fAf2B828d","Pumpkinmind":"0x3F73A30A76E20c334689AC2D2e86cCadD2684A3E","Chipagent":"0xc3D831dB5f018ab9977724352ec773bA0AC3AE4a","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Spookdroidling":"0x7e20f345435130Af72733Ce5742A6704b19cc574","Saturndroid":"0xb884dc59bBB4f66797F533e449546640b17549C8",
"Kittynode":"0xb625B5ddA0a2EbB4b062c358d955685B71AabB51","Krillfarm":"0x0aA11F327313682CDF072AFFfF26D0dffC804483","Astrogent":"0x483CEf46ec23D5656896526408221074597b6ed6","Duneswarm":"0xBCACC3a237b11CFAe2b59D3E5E6D2B7f2c3EfF96","Kabutomind":"0x3b3C00d4616a4A48C115B8E321aa6B983A2BEb10","Cosmopilot":"0x3e68AbD88885979188b97b19e8986552F10265D2","Noctagent":"0x9c60E147f10fF790A293889DDee1eC4063e096d","Nightagent":"0xfd8D2E77c8AC50b2b75924ba528321B3cF6dE87b","Abysspilot":"0x11F1d538d571deC6042979b04200fC2B79Af7A7d","Onihive":"0x867B0142155E79A7C5473969DCa0531f605a84DF","Sproutdroid":"0xa917475929B07c414B6601C8892a18b780B8f3d3","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0",
"Jolly":"0xdc11764a5664e333c8d303eb465e89a1caadb85b","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10",
}
def collect(to,tests): return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
reread={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,early)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,out in ex.map(rr,items.items()): reread[n]=out; print("REREAD",n,out,flush=True)
reread["TrackB_MINT"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")])
reread["OSK"]=collect("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",[("opened()",""),("FREE_SHARES()",""),("totalMinted()","")])
reread["IMARS"]=collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",[("opened()",""),("freeMinted()",""),("FREE_SHARES()",""),("totalMinted()","")])
reread["NIULAI"]=collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",[("launched()",""),("freeClaimed()",""),("phase()","")])
print("REREAD TrackB",reread["TrackB_MINT"]); print("REREAD OSK",reread["OSK"]); print("REREAD IMARS",reread["IMARS"]); print("REREAD NIULAI",reread["NIULAI"])
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-0901-reread.json","w"),indent=1)
print("DONE block",reread["block"])
