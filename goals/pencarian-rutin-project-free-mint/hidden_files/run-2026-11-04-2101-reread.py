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
tests=[("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("freeMinted()",""),("mintedBy(address)",u),("freeUsed(address)",u),("balanceOf(address)",u)]
items={"Robogent":"0x5eA7E757dfc4654f7478841BD30175bd7F186e24","Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627","Krakenbo":"0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0","Mothfarm":"0x74E64b8B2941F61Bb67801C7668a4307bC34D9E0","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","Noctagent":"0x9c60E147f10fF790A293889DDee1e2C4063e096d","Botsaturn":"0xd1E75De8e6B46E09a90126A122373Fac79578300","LunaBirds":"0xd514eb87c957514979360d9913e1bebcdd90129d","PixelTrump":"0x3054a5530f1852c33bd2749bfaf7155f162a581b","WDNFT":"0xac7c0e1f36e15dba7ed32bf6e72d83095ff8fd10","Mummyhive":"0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd","Glitchdroid":"0xe3F0085fd94D4Fb2AE9ACb4B49f6c0504E3546A0","Agentyyds":"0x8463abFC06173BdCaEDe96c4331C30A958789629","Pilotneon":"0x01D0f3b16C89615c924007ae85779B55A22552D0","Pilotphoenix":"0xc1A54df271a455E236169F8Ff65b084eBfB00E15","Agentzhenxiang":"0xdA3C6681Ce380896Ec6BD02d96f8AE0fAf2B828d","Pumpkinmind":"0x3F73A30A76E20c334689AC2D2e86cCadD2684A3E","Chipagent":"0xc3D831dB5f018ab9977724352ec773bA0AC3AE4a","Spookdroidling":"0x7e20f345435130Af72733Ce5742A6704b19cc574","Saturndroid":"0xb884dc59bBB4f66797F533e449546640b17549C8","Agentvolt":"0xB04af24bBFA0EF441091178E61A724163e2828Cc","Jolly":"0xdc11764a5664e333c8d303eb465e89a1caadb85b","Vampirko":"0x46fA92833621D0cC2C04EaC9f68ED7436fC14C7A","Neijuan":"0x608AE998F5046058d19ff8279a1E0478a91e086d","Agentarot":"0x50Cd1D1dde98733e949e238fd54dD346b0cb0249","Cybermoth":"0x5C5A54CEeDC27E72557bDC703062aF21e8264016","Unnamed-E6BA-1401":"0xe6BA3f94EECdd1F0d7A1235fdDE9A34D43d162c7","Unnamed-miner-E246-1401":"0xE246BD46dEE32C99A6d30B67636778bC61d6c186"}
def collect(to,ts): return {name: iv(call(to,sel(name)+arg)) for name,arg in ts}
reread={"block":block()}
def rr(kv):
    n,a=kv; return n,collect(a,tests)
with ThreadPoolExecutor(max_workers=15) as ex:
    for n,out in ex.map(rr,items.items()): reread[n]=out; print("REREAD",n,out,flush=True)
reread["Unnamed-miner-E246-1401"]["nextId()"]=iv(call(items["Unnamed-miner-E246-1401"],sel("nextId()")))
reread["Unnamed-miner-E246-1401"]["freeMinedCount()"]=iv(call(items["Unnamed-miner-E246-1401"],sel("freeMinedCount()")))
reread["TrackB_MINT"]=collect("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched()",""),("tokenClaimed(address)",u),("totalShares()",""),("isRefundPhase()",""),("failed()","")])
reread["FABE"]=collect("0xFabE022a5943462fee1Bd221791945DA57510BE8",[("launched()",""),("freeSharesClaimed(address)",u),("sharesMinted(address)",u),("freeSharesRemaining()",""),("FREE_SHARES()","")])
TC={"DROID":"0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","OSK":"0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37","IMARS":"0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","NIULAI":"0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF","KillZero":"0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97"}
tc_tests=[("launched()",""),("opened()",""),("freeMinted()",""),("totalMinted()",""),("FREE_SHARES()",""),("freeClaimed()",""),("totalMintCount()","")]
for n,a in TC.items(): reread[n]=collect(a,tc_tests); print("TC",n,reread[n],flush=True)
print("TrackB",reread["TrackB_MINT"]); print("FABE",reread["FABE"])
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-2101-reread.json","w"),indent=1)
print("DONE block",reread["block"])
# appended 2101: new items from run 1731
extra={"Saturnswarm":"0x238C995A1376e08395b970870A546C57aE184434","Photonode":"0x8df8327B50d8eb188BFd204e444343E28670323c","Chromemind":"0x688FFC0487162b6Ac7EdE1f10f070Ac717181C2e","Boohiveling":"0xC1dAf114e377242eEB76d180B24b491758Acb4f7","Neidroidjuan":"0x758c9665747466Ff4CBa2a3714CC4e9F7C9324b6","Qilingentle":"0x423d25764E4D3D792C08e04C759cE3b0FcDE8596","Hivejupiter":"0x8DF74cBe998F8d447E7c77dD5117aFB940605400","Servofarmix":"0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6","Swarmcentaur":"0x87B805eCDDaB0b376531cAf6d5aD9A52E641B100","ACAT":"0x28a38A372639E8C481aD41B9B16E52c3c6366ACC","FlyWheel":"0xe4c75B0D134Fa0ca3d95FA0A4e0d366E80e84311","DeY":"0xDB062c12bF0a14227e7Fe896a988950b050B51C1","BoxBigem":"0x3Ee92296D663378D42521273aAA4779BDa8e25dD","HIVE":"0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"}
for n,a in extra.items():
    reread[n]=collect(a,tests); print("EXTRA",n,reread[n],flush=True)
reread["DeY_extra"]={"freeCount":iv(call(extra["DeY"],sel("freeCount()"))),"FREE_SLOTS":iv(call(extra["DeY"],sel("FREE_SLOTS()"))),"freeByAddress_user":iv(call(extra["DeY"],sel("freeByAddress(address)")+u))}
reread["BoxBigem_extra"]={"freeMinted":iv(call(extra["BoxBigem"],sel("freeMinted()"))),"freeRemaining":iv(call(extra["BoxBigem"],sel("freeRemaining()")))}
reread["ACAT_extra"]={"freeMinted":iv(call(extra["ACAT"],sel("freeMinted()"))),"mintOpen":iv(call(extra["ACAT"],sel("mintOpen()")))}
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-2101-reread.json","w"),indent=1)
print("DONE2101 block",reread["block"])
# appended 2101: EARLY + watchlist-only baru run 1931
extra2101={"Farmbuxiang":"0x6810056D235c949f425b394dE590835096dd6AdC","Pilotdragon":"0x2e93D00967fb9ac4961F3B23206F259100Cca638","AgentAcresPlot":"0x7a582f91fc6fED51C77b5199585F8050926d8bE0","GothicGargoyles":"0x1979c22cfEa94aa2215edC97AED703f651158369","Butterfli":"0xc698186Ce921EBC8d3b27e9f2E890Ba785659a3B","CARDEDTEST":"0x150A46112fD3dfb7873d348eF15C8EC438854304","PACKB8Cf":"0xB8Cf650b96810F9f84b8D63353590911E437455b"}
for n,a in extra2101.items():
    reread[n]=collect(a,tests); print("EXTRA2101",n,reread[n],flush=True)
reread["AgentAcresPlot_extra"]={"freePlotsRemaining":iv(call(extra2101["AgentAcresPlot"],sel("freePlotsRemaining()"))),"totalPlotsMinted":iv(call(extra2101["AgentAcresPlot"],sel("totalPlotsMinted()"))),"freePlotsClaimed":iv(call(extra2101["AgentAcresPlot"],sel("freePlotsClaimed()")))}
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-2101-reread.json","w"),indent=1)
print("DONE2101 block",reread["block"])
# appended 2101: EARLY 2001 + trackC 翻倍猫
extra2101={"Ringgent":"0xf1d1650dBfeB0FA8082481C8213ACCD59af3cF4A","Mindvolt":"0x2f47305baEdC1B1F28461cD6b488404A908B1BEA","Ghostbot":"0x0c654BEF00dAd6925F64B72151C4a504F1C00Bcd","Nodeneon":"0xE54873f96A7a73FA1E39fe6C8B69aB178c87b3D6"}
for n,a in extra2101.items():
    reread[n]=collect(a,tests); print("EXTRA2101",n,reread[n],flush=True)
reread["Fanbeimao"]={"freeSold":iv(call("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",sel("freeSold()"))),"freeCap":iv(call("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",sel("freeCap()"))),"isFreeOpen":iv(call("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",sel("isFreeOpen()"))),"startAt":iv(call("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",sel("startAt()")))}
print("FANBEIMAO",reread["Fanbeimao"],flush=True)
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-2101-reread.json","w"),indent=1)
print("DONE2101 block",reread["block"])
# appended 2101: EARLY 2031 + track-C SENBAZURU re-read
extra2101={"Hivefacai":"0xd337F2cb906CD5c571eDF4a28DbE66a2447A6281","Botphoenix":"0x221F42a2516Dd4462C572F84b777a6f4e94135a4"}
for n,a in extra2101.items():
    reread[n]=collect(a,tests); print("EXTRA2101",n,reread[n],flush=True)
reread["SENBAZURU"]={"freeClaimed":iv(call("0xb21583A08581278BcF925351a99C61A4562C62f0",sel("freeClaimed()"))),"FREE_CAP":iv(call("0xb21583A08581278BcF925351a99C61A4562C62f0",sel("FREE_CAP()"))),"opened":iv(call("0xb21583A08581278BcF925351a99C61A4562C62f0",sel("opened()"))),"hasFreeShare_user":iv(call("0xb21583A08581278BcF925351a99C61A4562C62f0",sel("hasFreeShare(address)")+u))}
print("SENBAZURU",reread["SENBAZURU"],flush=True)
json.dump({"reread":reread},open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-04-2101-reread.json","w"),indent=1)
print("DONE2101 block",reread["block"])
