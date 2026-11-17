#!/usr/bin/env python3
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
            with urllib.request.urlopen(req,timeout=8) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
nft=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u)]
items={
"Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4e7f4e551","Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c08348ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1eC4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10",
"Mummyhive":"0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd","Glitchdroid":"0xe3F0085fd94D4Fb2AE9ACb4B49f6c0504E3546A0","Agentyyds":"0x8463abFC06173BdCaEDe96c4331C30A958789629","Pilotneon":"0x01D0f3b16C89615c924007ae85779B55A22552D0","Pilotphoenix":"0xc1A54df271a455E236169F8Ff65b084eBfB00E15","Agentzhenxiang":"0xdA3C6681Ce380896Ec6BD02d96f8AE0fAf2B828d","Pumpkinmind":"0x3F73A30A76E20c334689AC2D2e86cCadD2684A3","Chipagent":"0xc3D831dB5f018ab9977724352ec773bA0AC3AE4a","Spookdroidling":"0x7e20f345435130Af72733Ce5742A6704b19cc574","Saturndroid":"0xb884dc59bBB4f66797F533e449546640b17549C8","Agentvolt":"0xB04af24bBFA0EF441091178E61A724163e2828Cc","Jolly":"0xdc11764a5664e333c8d303eb465e89a1caadb85b",
}
def collect(to,tests): return {name: iv(call(to,sel(name)+arg)) for name,arg in tests}
reread={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,nft)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,out in ex.map(rr,items.items()): reread[n]=out; print("REREAD",n,out,flush=True)
reread["TrackB_MINT"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("tokenClaimed(address)",u),("isRefundPhase()",""),("failed()","")])
reread["DROID"]=collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",[("FREE_SHARES()",""),("freeMinted()",""),("freeUsed(address)",u)])
reread["OSK"]=collect("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",[("opened()",""),("FREE_SHARES()",""),("totalMinted()",""),("freeUsed(address)",u)])
reread["IMARS"]=collect("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",[("opened()",""),("FREE_SHARES()",""),("freeMinted()",""),("totalMinted()","")])
reread["NIULAI"]=collect("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",[("launched()",""),("freeClaimed()",""),("phase()","")])
reread["KillZero"]=collect("0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",[("launched()",""),("FREE_SHARES()",""),("totalFreeClaimed()",""),("totalMintCount()","")])
reread["FABE"]=collect("0xFabE022a5943462fee1Bd221791945DA57510BE8",[("launched()",""),("freeSharesClaimed(address)",u)])
print("REREAD TrackB",reread["TrackB_MINT"]); print("REREAD DROID",reread["DROID"]); print("REREAD OSK",reread["OSK"]); print("REREAD IMARS",reread["IMARS"]); print("REREAD NIULAI",reread["NIULAI"]); print("REREAD KillZero",reread["KillZero"]); print("REREAD FABE",reread["FABE"])

reread["E6BA"]=collect("0xe6BA3f94EECdd1F0d7A1235fdDE9A34D43d162c7",[("totalSupply()",""),("freeClaimed(address)",u),("mintedBy(address)",u),("balanceOf(address)",u)])
reread["E246"]=collect("0xE246BD46dEE32C99A6d30B67636778bC61d6c186",[("freeMinedCount()",""),("nextId()",""),("totalSupply()","")])
print("REREAD E6BA",reread["E6BA"]); print("REREAD E246",reread["E246"])
json.dump({"reread":reread},open("run-2026-11-04-1431-reread.json","w"),indent=1)
print("DONE block",reread["block"])
