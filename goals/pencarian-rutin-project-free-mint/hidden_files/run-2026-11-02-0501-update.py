import json
def gi(d,n):
    v=d.get(n,{})
    return v.get('int') if isinstance(v,dict) else v
def w(d,n):
    v=d.get(n,{})
    return v.get('words') if isinstance(v,dict) else None
snap=json.load(open('onchain-snapshot.json'))
main=json.load(open('run-2026-11-02-0501-read.json'))
extra=json.load(open('run-2026-11-02-0501-read-extra.json'))
cilok=json.load(open('run-2026-11-02-0501-cilok.json'))
verify=json.load(open('run-2026-11-02-0501-verify.json'))
MAIN_INT=26.25; EXTRA_INT=25.92; CILOK_INT=25.5
def upd(name, new_total, new_free, free_cap, interval, block, readwib, note_extra=""):
    c=snap['contracts'][name]
    old_total=c.get('totalSupply') if c.get('totalSupply') is not None else c.get('totalMinted')
    old_rate=c.get('currentRatePerMin')
    minted=new_total-old_total
    rate=round(minted/interval,3) if interval else None
    passes=bool(old_rate is not None and minted>=20 and rate>=1.5*old_rate)
    c['previousTotalSupply']=old_total; c['totalSupply']=new_total
    if new_free is not None: c['freeClaimed']=new_free
    if free_cap: c['freePctVerified']=round(new_free/free_cap*100,2) if new_free is not None else c.get('freePctVerified')
    c['mintedInInterval']=minted; c['intervalMinutes']=interval
    c['previousRatePerMin']=old_rate; c['currentRatePerMin']=rate
    c['velocityLegPasses']=passes
    c['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~{interval} min = {rate}/min, ratio vs prior {old_rate} = {round(rate/old_rate,2) if old_rate else None}x, so the velocity leg still FAILS. Stored as new baseline." if old_rate else f"Run 05:01 WIB: +{minted} tokens in ~{interval} min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline."
    if passes: c['velocityNote']=c['velocityNote'].replace('still FAILS','PASSES')
    c['lastReadBlock']=block; c['lastReadWib']=readwib
    if note_extra: c['velocityNote']+=" "+note_extra
    return c
B_MAIN=main['block']; B_EXTRA=extra['block']; B_CILOK=cilok['block']
W_MAIN="2026-11-02T05:03:44+07:00"; W_EXTRA="2026-11-02T05:04:19+07:00"; W_CILOK="2026-11-02T05:04:22+07:00"
# HIVE (inference)
h=snap['contracts']['HIVE Agents']; old=h['totalSupply']; minted=gi(main['HIVE'],'totalSupply()')-old
rate=round(minted/MAIN_INT,3); h['previousTotalSupply']=old; h['totalSupply']=gi(main['HIVE'],'totalSupply()')
h['mintedInInterval']=minted; h['intervalMinutes']=MAIN_INT; h['previousRatePerMin']=h['currentRatePerMin']; h['currentRatePerMin']=rate
h['velocityLegPasses']=False; h['freePctInference']=round(h['totalSupply']/1000*100,1)
h['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {h['previousRatePerMin']} = {round(rate/h['previousRatePerMin'],2)}x, so the velocity leg still FAILS. Stored as new baseline."
h['lastReadBlock']=B_MAIN; h['lastReadWib']=W_MAIN
upd('Bubblebruin', gi(main['Bubblebruin'],'totalSupply()'), gi(main['Bubblebruin'],'freeClaimed()'), 7777, MAIN_INT, B_MAIN, W_MAIN)
upd('Zapcourier', gi(main['Zapcourier'],'totalSupply()'), gi(main['Zapcourier'],'freeClaimed()'), 712, MAIN_INT, B_MAIN, W_MAIN)
upd('Mothwraith', gi(main['Mothwraith'],'totalSupply()'), gi(main['Mothwraith'],'freeClaimed()'), 869, MAIN_INT, B_MAIN, W_MAIN)
upd('Cryonyx', gi(main['Cryonyx'],'totalSupply()'), gi(main['Cryonyx'],'freeClaimed()'), 809, MAIN_INT, B_MAIN, W_MAIN)
upd('Cathodex', gi(main['Cathodex'],'totalSupply()'), gi(main['Cathodex'],'freeClaimed()'), 763, MAIN_INT, B_MAIN, W_MAIN)
upd('Malabao', gi(main['Malabao'],'totalSupply()'), gi(main['Malabao'],'freeClaimed()'), 844, MAIN_INT, B_MAIN, W_MAIN)
upd('Voltabyte', gi(main['Voltabyte'],'totalSupply()'), gi(main['Voltabyte'],'freeClaimed()'), 925, MAIN_INT, B_MAIN, W_MAIN)
upd('Saturnin', gi(main['Saturnin'],'totalSupply()'), gi(main['Saturnin'],'freeClaimed()'), 838, MAIN_INT, B_MAIN, W_MAIN)
upd('Kirinova', gi(main['Kirinova'],'totalSupply()'), gi(main['Kirinova'],'freeClaimed()'), 711, MAIN_INT, B_MAIN, W_MAIN)
upd('Ghostbloom', gi(main['Ghostbloom'],'totalSupply()'), gi(main['Ghostbloom'],'freeClaimed()'), 942, MAIN_INT, B_MAIN, W_MAIN)
upd('Junepup', gi(main['Junepup'],'totalSupply()'), gi(main['Junepup'],'freeClaimed()'), 724, MAIN_INT, B_MAIN, W_MAIN)
upd('Gourdwick', gi(main['Gourdwick'],'totalSupply()'), gi(main['Gourdwick'],'freeClaimed()'), 868, MAIN_INT, B_MAIN, W_MAIN)
upd('Kitsunaru', gi(main['Kitsunaru'],'totalSupply()'), gi(main['Kitsunaru'],'freeClaimed()'), 865, MAIN_INT, B_MAIN, W_MAIN)
upd('Nightsable', gi(main['Nightsable'],'totalSupply()'), gi(main['Nightsable'],'freeClaimed()'), 794, MAIN_INT, B_MAIN, W_MAIN)
upd('Lensorb', gi(main['Lensorb'],'totalSupply()'), gi(main['Lensorb'],'freeClaimed()'), 776, MAIN_INT, B_MAIN, W_MAIN)
upd('Nimaluo', gi(main['Nimaluo'],'totalSupply()'), gi(main['Nimaluo'],'freeClaimed()'), 828, MAIN_INT, B_MAIN, W_MAIN)
upd('Orbitty', gi(main['Orbitty'],'totalSupply()'), gi(main['Orbitty'],'freeClaimed()'), 884, MAIN_INT, B_MAIN, W_MAIN)
upd('Neonwolfy', gi(main['Neonwolfy'],'totalSupply()'), gi(main['Neonwolfy'],'freeClaimed()'), 850, MAIN_INT, B_MAIN, W_MAIN)
upd('Sphinxel', gi(main['Sphinxel'],'totalSupply()'), gi(main['Sphinxel'],'freeClaimed()'), 799, MAIN_INT, B_MAIN, W_MAIN)
upd('Witchlet', gi(main['Witchlet'],'totalSupply()'), gi(main['Witchlet'],'freeClaimed()'), 929, MAIN_INT, B_MAIN, W_MAIN)
upd('Venuspi', gi(main['Venuspi'],'totalSupply()'), gi(main['Venuspi'],'freeClaimed()'), 840, MAIN_INT, B_MAIN, W_MAIN)
upd('Neonraven', gi(main['Neonraven'],'totalSupply()'), gi(main['Neonraven'],'freeClaimed()'), 722, MAIN_INT, B_MAIN, W_MAIN)
upd('Griffinko', gi(main['Griffinko'],'totalSupply()'), gi(main['Griffinko'],'freeClaimed()'), 712, MAIN_INT, B_MAIN, W_MAIN)
upd('Tangpinku', gi(main['Tangpinku'],'totalSupply()'), gi(main['Tangpinku'],'freeClaimed()'), 875, MAIN_INT, B_MAIN, W_MAIN)
# Slimelings (no free cap)
s=snap['contracts']['Slimelings']; old=s['totalSupply']; minted=gi(main['Slimelings'],'totalSupply()')-old; rate=round(minted/MAIN_INT,3)
s['previousTotalSupply']=old; s['totalSupply']=gi(main['Slimelings'],'totalSupply()'); s['mintedCount']=gi(main['Slimelings'],'mintedCount()'); s['freeCount']=gi(main['Slimelings'],'freeCount()')
s['mintedInInterval']=minted; s['intervalMinutes']=MAIN_INT; s['previousRatePerMin']=s['currentRatePerMin']; s['currentRatePerMin']=rate; s['velocityLegPasses']=False
s['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {s['previousRatePerMin']} = {round(rate/s['previousRatePerMin'],2)}x, so the velocity leg still FAILS. Stored as new baseline."
s['lastReadBlock']=B_MAIN; s['lastReadWib']=W_MAIN
# Vorpry
v=snap['contracts']['Vorpry']; old=v['totalSupply']; minted=gi(main['Vorpry'],'totalSupply()')-old; rate=round(minted/MAIN_INT,3)
v['previousTotalSupply']=old; v['totalSupply']=gi(main['Vorpry'],'totalSupply()'); v['totalMinted']=gi(main['Vorpry'],'totalMinted()'); v['openLeft']=gi(main['Vorpry'],'openLeft()')
v['mintedInInterval']=minted; v['intervalMinutes']=MAIN_INT; v['previousRatePerMin']=v['currentRatePerMin']; v['currentRatePerMin']=rate; v['velocityLegPasses']=False
v['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {v['previousRatePerMin']} = {round(rate/v['previousRatePerMin'],2) if v['previousRatePerMin'] else None}x, so the velocity leg still FAILS. Stored as new baseline."
v['lastReadBlock']=B_MAIN; v['lastReadWib']=W_MAIN
# Mirror Pair
mp=snap['contracts']['Mirror Pair']; mp['mintedPairs']=gi(main['MirrorPair'],'mintedPairs()'); mp['lastReadBlock']=B_MAIN; mp['lastReadWib']=W_MAIN
mp['velocityNote']="Run 05:01 WIB: mintedPairs still 2 (was 2) - no new pair; velocity not computable."
# Pixcade (totalMinted view)
p=snap['contracts']['Pixcade']; old=p['totalMinted']; minted=gi(main['Pixcade'],'totalMinted()')-old; rate=round(minted/MAIN_INT,3)
p['previousTotalSupply']=old; p['totalMinted']=gi(main['Pixcade'],'totalMinted()'); p['freeMinted']=gi(main['Pixcade'],'freeMinted()')
p['freePctVerified']=round(p['freeMinted']/1500*100,2); p['mintedInInterval']=minted; p['intervalMinutes']=MAIN_INT; p['previousRatePerMin']=p['currentRatePerMin']; p['currentRatePerMin']=rate; p['velocityLegPasses']=False
p['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~{MAIN_INT} min = {rate}/min, ratio vs prior {p['previousRatePerMin']} = {round(rate/p['previousRatePerMin'],2)}x, so the velocity leg still FAILS. Stored as new baseline."
p['lastReadBlock']=B_MAIN; p['lastReadWib']=W_MAIN
# Extra group
upd('Agents NormiePunks', gi(extra['Agents NormiePunks'],'totalSupply()'), None, None, EXTRA_INT, B_EXTRA, W_EXTRA)
upd('Medusine', gi(extra['Medusine'],'totalSupply()'), gi(extra['Medusine'],'freeClaimed()'), 868, EXTRA_INT, B_EXTRA, W_EXTRA)
upd('Hotpotsage', gi(extra['Hotpotsage'],'totalSupply()'), gi(extra['Hotpotsage'],'freeClaimed()'), 784, EXTRA_INT, B_EXTRA, W_EXTRA)
upd('Mummyrelic', gi(extra['Mummyrelic'],'totalSupply()'), gi(extra['Mummyrelic'],'freeClaimed()'), 785, EXTRA_INT, B_EXTRA, W_EXTRA)
upd('Ravenhex', gi(extra['Ravenhex'],'totalSupply()'), gi(extra['Ravenhex'],'freeClaimed()'), 925, EXTRA_INT, B_EXTRA, W_EXTRA)
upd('Orbitmarshal', gi(extra['Orbitmarshal'],'totalSupply()'), gi(extra['Orbitmarshal'],'freeClaimed()'), 831, EXTRA_INT, B_EXTRA, W_EXTRA)
# Cilok group
c=snap['contracts']['Cilok Cats: White Paw Genesis']; c['totalMinted']=gi(cilok['Cilok'],'totalMinted()'); c['freeMinted']=gi(cilok['Cilok'],'freeMinted()'); c['lastReadBlock']=B_CILOK; c['lastReadWib']=W_CILOK
c['velocityNote']="Run 05:01 WIB: totalMinted still 1 (was 1) - no new mint; velocity not computable."
upd('Gearpixel', gi(cilok['Gearpixel'],'totalSupply()'), gi(cilok['Gearpixel'],'freeClaimed()'), 832, CILOK_INT, B_CILOK, W_CILOK)
upd('Skelebop', gi(cilok['Skelebop'],'totalSupply()'), gi(cilok['Skelebop'],'freeClaimed()'), 902, CILOK_INT, B_CILOK, W_CILOK)
# NULLSECTOR (verify block)
n=snap['contracts']['NULLSECTOR']; old=n['totalSupply']; minted=gi(verify['NULLSECTOR'],'totalSupply()')-old; rate=round(minted/26.0,3)
n['previousTotalSupply']=old; n['totalSupply']=gi(verify['NULLSECTOR'],'totalSupply()'); n['mintedInInterval']=minted; n['intervalMinutes']=26.0
n['previousRatePerMin']=n.get('currentRatePerMin'); n['currentRatePerMin']=rate; n['velocityLegPasses']=False
n['velocityNote']=f"Run 05:01 WIB: +{minted} tokens in ~26.0 min = {rate}/min - first comparable rate, so the velocity leg does NOT pass. Stored as new baseline."
n['lastReadBlock']=verify['block']; n['lastReadWib']="2026-11-02T05:06:38+07:00"
# REMOVALS: Root Agent (free pool exhausted: totalMinted 424 > FREE_SUPPLY 422, costFor flipped 0 -> 0.0005 BNB) -> report once + remove
root_old=snap['contracts'].pop('Root Agent', None)
# BNBPIG sold out, already reported by hot leg 04:49 WIB -> remove without re-report
pig_old=snap['track_c'].pop('BNBPIG', None)
# Track C updates
tc=snap['track_c']
tc['BNBbaby']['sharesMinted']=gi(main['BNBbaby'],'sharesMinted()'); tc['BNBbaby']['freeMinted']=gi(main['BNBbaby'],'freeMinted()'); tc['BNBbaby']['paidShares']=gi(main['BNBbaby'],'paidShares()')
tc['DOG']['sharesMinted']=gi(main['DOG'],'sharesMinted()')
tc['QILIN']['cardsSold']=gi(main['QILIN'],'cardsSold()'); tc['QILIN']['freeCardsRemaining']=gi(main['QILIN'],'freeCardsRemaining()'); tc['QILIN']['freeGiven']=gi(main['QILIN'],'freeGiven()')
tc['SAMBARIO']['cardsSold']=gi(main['SAMBARIO'],'cardsSold()'); tc['SAMBARIO']['freeCardsRemaining']=gi(main['SAMBARIO'],'freeCardsRemaining()'); tc['SAMBARIO']['freeGiven']=gi(main['SAMBARIO'],'freeGiven()')
tc['a7Be']['sharesMinted']=gi(main['a7Be'],'sharesMinted()'); tc['a7Be']['freeSharesMinted']=gi(main['a7Be'],'freeSharesMinted()')
tc['NIUBI']['sharesMinted']=gi(main['NIUBI'],'sharesMinted()'); tc['NIUBI']['freeMinted']=gi(main['NIUBI'],'freeMinted()')
tc['零元购']['soldFree']=gi(main['ZeroYuanGou'],'soldFree()'); tc['零元购']['soldPaid']=gi(main['ZeroYuanGou'],'soldPaid()'); tc['零元购']['totalSold']=gi(main['ZeroYuanGou'],'totalSold()')
tc['JUBAO']['freeClaimed']=gi(main['JUBAO'],'freeClaimed()'); tc['ZCMAO']['freeClaimed']=gi(main['ZCMAO'],'freeClaimed()'); tc['JINLONG']['freeClaimed']=gi(main['JINLONG'],'freeClaimed()')
# Pending claims
snap['pending_claims']['binanceai.fun']['lastCheckBlock']=B_MAIN; snap['pending_claims']['binanceai.fun']['lastCheckWib']=W_MAIN
snap['pending_claims']['hive-pollen']['pollenAgents']=gi(main['Pollen_MINT'],'pollenAgents()'); snap['pending_claims']['hive-pollen']['lastCheckBlock']=B_MAIN; snap['pending_claims']['hive-pollen']['lastCheckWib']=W_MAIN
snap['timestamp_wib']="2026-11-02T05:01:00+07:00"
snap['note']=("Run 05:01 WIB: contracts = %d (40 previous - Root Agent removed: free pool exhausted + costFor flipped to paid; BNBPIG removed: sold out, already reported by hot leg 04:49 WIB). "
              "No track-A candidate passes all criteria; no new strong/early lead; no new track-C lead/candidate; pending claims unchanged." % len(snap['contracts']))
json.dump(snap, open('onchain-snapshot.json','w'), indent=1)
print('contracts now', len(snap['contracts']), 'track_c now', len(tc))
print('Root removed?', root_old is not None, 'BNBPIG removed?', pig_old is not None)
for name in ['HIVE Agents','Zapcourier','Cathodex','NULLSECTOR','Pixcade','Witchlet']:
    cc=snap['contracts'][name]; print(name, cc.get('totalSupply'), cc.get('freePctVerified'), cc.get('freePctInference'), cc.get('mintedInInterval'), cc.get('currentRatePerMin'), cc.get('velocityLegPasses'))
