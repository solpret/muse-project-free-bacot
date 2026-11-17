#!/usr/bin/env python3
"""Merge run 1731 (17:31 WIB) into onchain-snapshot.json. Read-only except snapshot + run log."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
r17=json.load(open(BASE+"run-2026-11-16-1731-reread.json"))
r16=json.load(open(BASE+"run-2026-11-16-1701-reread.json"))
v17=json.load(open(BASE+"run-2026-11-16-1731-verify.json"))
fs=json.load(open(BASE+"run-2026-11-16-1731-feedshape.json"))
feed=json.load(open(BASE+"run-2026-11-16-1731-sourcify.json"))
INTERVAL_MIN=(r17['block']-r16['block'])*0.45/60.0  # ~29.9
print("interval_min", round(INTERVAL_MIN,1), "blocks", r16['block'], "->", r17['block'])

def supply_of(views):
    # prefer totalMinted when snapshot tracks it, else totalSupply
    return views
def get_supply(entry, views):
    # choose the view the snapshot entry tracks: totalMinted if entry has it non-null, else totalSupply
    if entry.get('totalMinted') is not None and views.get('totalMinted') is not None:
        return views.get('totalMinted'), 'totalMinted'
    if views.get('totalSupply') is not None:
        return views.get('totalSupply'), 'totalSupply'
    return views.get('totalMinted'), 'totalMinted'

updated=[]
vel_pass=[]
for name, rd in r17['reads'].items():
    views=rd.get('views') or {}
    # find snapshot entry by name, else by address
    entry=s['contracts'].get(name)
    if entry is None:
        for k,v in s['contracts'].items():
            if isinstance(v,dict) and (v.get('address') or '').lower()==rd['address'].lower():
                entry=v; name=k; break
    if entry is None:
        print("SKIP (not in snapshot):", name); continue
    new_sup, view = get_supply(entry, views)
    prev_sup = entry.get('totalSupply') if view=='totalSupply' else entry.get('totalMinted')
    # snapshot fields may be stale vs 1701 reread; prefer 1701 reread as baseline
    prev_views=(r16['reads'].get(name) or {}).get('views') or {}
    prev16 = prev_views.get(view)
    if prev16 is not None: prev_sup=prev16
    minted=None
    if new_sup is not None and prev_sup is not None: minted=new_sup-prev_sup
    prev_rate=entry.get('currentRatePerMin')
    rate=None if minted is None else minted/INTERVAL_MIN
    ratio=None
    if rate is not None and prev_rate:
        ratio=rate/prev_rate
    passes = bool(minted is not None and minted>=20 and ratio is not None and ratio>=1.5)
    if passes: vel_pass.append((name, minted, round(rate,3), round(ratio,2)))
    # update fields
    entry['previousTotalSupply']=prev_sup
    if view=='totalSupply': entry['totalSupply']=new_sup
    else: entry['totalMinted']=new_sup
    if views.get('freeMinted') is not None: entry['freeMinted']=views['freeMinted']
    if views.get('freeClaimed') is not None: entry['freeClaimed']=views['freeClaimed']
    if views.get('mintOpen') is not None: entry['mintOpen']=views['mintOpen']
    entry['previousRatePerMin']=prev_rate
    entry['currentRatePerMin']=rate
    entry['velocityLegPasses']=passes
    entry['lastReadBlock']=r17['block']
    entry['lastReadWib']="2026-11-16 ~17:31 WIB"
    entry['supplyView']=view
    note=f"Run 1731 (blok {r17['block']}, interval ~{INTERVAL_MIN:.1f} mnt vs run 1701): "
    if minted is None: note+=f"supply {view} {new_sup} (baseline {prev_sup} tak terbaca) -> velocity TIDAK dihitung"
    else: note+=f"{prev_sup}->{new_sup} (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {'None' if ratio is None else round(ratio,2)}x) -> velocity {'LOLOS' if passes else 'GAGAL'}"
    if views.get('freeMinted') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeMinted {views['freeMinted']}/{entry['FREE_SUPPLY']} = {views['freeMinted']/entry['FREE_SUPPLY']*100:.1f}%"
    if views.get('freeClaimed') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeClaimed {views['freeClaimed']}/{entry['FREE_SUPPLY']} = {views['freeClaimed']/entry['FREE_SUPPLY']*100:.1f}%"
    note+="; DIAM." if not passes else "; velocity lolos TAPI bukan kandidat/strong lead (lihat kaki lain)."
    entry['runNote1731_1116']=note
    updated.append(name)
# SPARKS duplicate entry 'First-Dollar Sparks' same address
sp=s['contracts'].get('First-Dollar Sparks')
if sp is not None:
    sp['totalSupply']=1041; sp['totalMinted']=1041; sp['previousTotalSupply']=1036
    sp['previousRatePerMin']=0.7931034482758621; sp['currentRatePerMin']=round(5/INTERVAL_MIN,4)
    sp['velocityLegPasses']=False; sp['lastReadBlock']=r17['block']; sp['lastReadWib']="2026-11-16 ~17:31 WIB"
    sp['runNote1731_1116']="Run 1731 (blok 133908291): 1036->1041 (+5, 0.167/mnt vs prev 0.793 = 0.21x) -> velocity GAGAL; free% UNVERIFIED + umur UNVERIFIED -> BUKAN kandidat, BUKAN strong lead. Watchlist-only. DIAM."
# Punch Card (verify script, block 133908589)
pc=s['contracts']['Punch Card']
pv=v17['reads']['PunchCard']['views']
pc['totalSupply']=pv['totalSupply']; pc['totalMinted']=pv['totalMinted']; pc['freeMinted']=pv['freeMinted']
pc['previousTotalSupply']=529; pc['previousRatePerMin']=round(29/29.9,4); pc['currentRatePerMin']=round(72/30.63,4)
pc['velocityLegPasses']=True; pc['lastReadBlock']=133908589; pc['lastReadWib']="2026-11-16 ~17:31 WIB"
pc['runNote1731_1116']="Run 1731 (blok 133912637): totalSupply 529->601 (+72, 2.351/mnt vs prev 0.970 = 2.42x) -> velocity LOLOS (>=1.5x DAN >=20 token); freeMinted 600/5555 = 10.8% (masih <50% kandidat, <70% strong lead); mintOpen 1, mintPriceFor(user,1)=0, mintedCount(user)=0, bal_user=0. Umur terverifikasi <24 jam. Early lead saja, TANPA promosi. DIAM."
# BUBB
bubb=s['contracts']['Agent Bubble']
bv=v17['reads']['BUBB']['views']
bubb['totalSupply']=bv['totalSupply']; bubb['totalMinted']=bv['totalMinted']; bubb['freeMinted']=bv['freeMinted']
bubb['previousTotalSupply']=1777; bubb['previousRatePerMin']=None; bubb['currentRatePerMin']=None
bubb['velocityLegPasses']=False; bubb['lastReadBlock']=133908589; bubb['lastReadWib']="2026-11-16 ~17:31 WIB"
bubb['runNote1731_1116']="Run 1731 (blok 133912637): totalSupply 1777->1782 (+5), freeMinted 1638/2222 = 73.7% (>70% ambang strong lead) TAPI umur peluncuran TETAP UNVERIFIED (pertama terlihat 13 Nov, tanpa stated launch/first-mint) + X unverified + website unverified -> BUKAN strong lead, BUKAN kandidat. Slot user terbuka (bal_user=0, mintOpen 1). Watchlist-only. DIAM."
# New triage entries
s['contracts']['Boltbook-87b3']={"address":"0x87b354e2014d2e418927a1105dd219a2e7b063b0","status":"checked-age-excluded-2026-11-16","name":"Boltbook-87b3","kind":"ERC721","totalSupply":322,"MAX_SUPPLY":4444,"mintOpen":1,"mintStart":1794406225,"freeLeft":1679,"balanceOf_user":0,"lastReadBlock":133912737,"lastReadWib":"2026-11-16 ~17:31 WIB","launchNote":"Umur TERVERIFIKASI >=24 jam: mintStart() on-chain 1794406225 = 2026-11-11 21:10:25 WIB -> umur ~5 hari 20 jam saat run. AGE-EXCLUDED.","baselineNote":"Triase Boltbook run 1731 (front page EN 17:31 WIB). Sourcify verified 84 fns — daftar fn IDENTIK dengan HEXCOVEN (freeMintX, freeLeft, FIRST_FREE_CAP, xCheck/xDigest/xSigner) TAPI TANPA registry reference dan TANPA AgentGate/agent fn -> BUKAN agent-shaped (template X-gate). BUKAN early lead (first mint bukan di run ini + umur >24 jam). TIDAK pernah dilaporkan sebagai lead -> DIAM.","xVerified":False,"velocityVerified":False}
s['contracts']['Poffzi']={"address":"0x3D7A6e3d007990B36ab092404C9027a3CD989C14","status":"watchlist-only-pre-launch-2026-11-16","name":"Poffzi","symbol":"PFZI","kind":"ERC721","totalSupply":0,"totalMinted":0,"freeMinted":0,"FREE_SUPPLY":100,"MAX_SUPPLY":700,"mintOpen":0,"saleOpen":0,"saleStart":1794844811,"saleEnd":1795449611,"PRICE":1500000000000000,"agentIdRegistry":552192074493313695968015109214105588393044541999,"hasAgentId_user":1,"quote_user_1":0,"freeAvailable_user":0,"balanceOf_user":0,"lastReadBlock":133912737,"lastReadWib":"2026-11-16 ~17:31 WIB","launchNote":"BELUM LAUNCH: saleStart on-chain 1794844811 = 2026-11-16 23:00:11 WIB (saleEnd 2026-11-23 23:00:11 WIB); totalSupply 0, mintOpen 0, saleOpen 0 saat run 17:31 WIB.","baselineNote":"Ditemukan hot-leg 1719 (Sourcify feed, S1 shape) + dikonfirmasi run 1731 (verify-retry, blok 133912737). Bentuk sale S1 (mint+quote+free views+agentIdRegistry) per cek hot-leg; website https://poffzi-orbit.pages.dev/ via contractURI external_link (hot-leg: site mencetak kontrak). Free pool 100, 1/wallet, paid 600 @ 0.0015 BNB. Watchlist-only PRE-LAUNCH: bukan lead, bukan kandidat, TIDAK pernah preview/mint; dipantau saat sale buka 23:00 WIB.","website":"https://poffzi-orbit.pages.dev/","xVerified":False,"velocityVerified":False}
# MORFO age-exclusion (early lead reported 2026-11-13 run 2201; removal per age rule)
morfo_removed = s['contracts'].pop('MORFO', None)
s['runNote1731_1116_morfo_age_exclusion']="Run 1731: MORFO 0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186 AGE-EXCLUDED + DIHAPUS dari snapshot (early lead dilaporkan sekali run 2201, 13 Nov). Bukti: totalMinted 415 sudah terbaca on-chain run 2201 13 Nov 22:01 WIB -> minting terbuka paling lambat 22:01 WIB 13 Nov; deploy 13 Nov 11:16 WIB -> launch dalam [11:16, 22:01] 13 Nov -> umur 67,5-78,3 jam saat run 17:31 WIB 16 Nov (>24 jam); totalMinted kini 900/25000 (3,6%), BELUM sold out; free% UNVERIFIED (tanpa free view). Dihapus dari watchlist aktif per aturan umur; dilaporkan sekali sebagai perubahan."
s.setdefault('age_exclusions',[]).append({"contract":"MORFO","address":"0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186","run":"1731","removed_wib":"2026-11-16 ~17:31 WIB","reason":"age >=24h verified by bound (415 minted by 13 Nov 22:01 WIB)","totalMinted":900})
# RigForge + BinanceAI notes
for name, note in [
 ("RigForge", None),
]:
    pass
# track_c feedshape (dedupe by address)
tc=s.setdefault('track_c',{})
existing={ (v.get('address') or '').lower() for v in tc.values() if isinstance(v,dict)}
added=0
vmap={x['address']: x.get('verifiedAt') for x in feed.get('results',[])}
for o in fs:
    a=o['address']
    if a.lower()=='0x3d7a6e3d007990b36ab092404c9027a3cd989c14': continue  # Poffzi: S1 per hot-leg 1719, recorded as contract
    if a.lower() in existing: continue
    key="Feed-0x"+a[2:6]
    tc[key]={"address":a,"status":"checked-not-sale-shape-2026-11-16",
             "note":f"Run 1731 Sourcify feed (verified {vmap.get(a)}): S1={o.get('S1')} S2={o.get('S2')}; mint={o.get('has_mint')} quote={o.get('has_quote')} free_views={o.get('free_views')} agent_ref={o.get('agent_ref')} fns={o.get('n_fns')}. Bukan lead track-C; first-mint tidak terverifikasi (Ankr 401) -> bukan early lead.",
             "lastReadWib":"2026-11-16 ~17:31 WIB"}
    existing.add(a.lower()); added+=1
s['last_run']="free-mint-search 2026-11-16 17:31 WIB — 1 PERUBAHAN DILAPORKAN: MORFO age-excluded (early lead 13 Nov, umur terverifikasi >=67,5 jam, dihapus dari watchlist); 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 eksekusi/preview; 1 velocity lolos (Punch Card +72, tanpa promosi); Poffzi pre-launch ditambahkan watchlist-only (sale buka 23:00 WIB); Boltbook-87b3 age-excluded; scan fast-fail Ankr 401"
s['runNote1731_1116']="Run 1731 (17:31 WIB, blok reread 133912375, 37/37 OK, 80,6 dtk; verify blok 133912637, retry 133912737): 1 PERUBAHAN: MORFO age-excluded (umur terverifikasi 67,5-78,3 jam via bound 415 minted 13 Nov 22:01 WIB, 900/25000 belum sold out) - dihapus dari snapshot, dilaporkan sekali. Velocity LOLOS: Punch Card +72 (2,42x, free 10,8% - early lead saja). Semua reread lain velocity GAGAL (maks +5 Bold Leonidas). BUBB freeMinted 1638/2222 = 73,7% TAPI umur unverified -> bukan strong lead. BinanceAI-mint tetap refund (launched 0/failed 1/isRefundPhase 1). RigForge tetap belum buka (openedAt 0, freeSharesLeft 637). LumenFindings age-excluded (genesisStart tetap, totalSpecimens 6640). Poffzi pre-launch ditambahkan watchlist-only (saleStart 23:00:11 WIB, S1, site poffzi-orbit.pages.dev). Boltbook-87b3 age-excluded (~5 hari 20 jam, template X-gate spt HEXCOVEN). Scan pre-flight Ankr 401 (head 133912339), watermark tetap 132512564, gap ~1.399.775 blok. Bridge: 116 kontrak, 0 baru vs snapshot. Discovery: Boltbook EN+ZH 12 alamat unik, 0 baru vs snapshot+seen+hot-leg (87b3 baru vs snapshot utama saja); Sourcify 20 (0 S1/S2 per daftar sempit main-job; Poffzi S1 per hot-leg 1719); sweep EN+ZH hanya proyek lama; Odaily 0 hit. Deadline umur berikutnya: ABYSSCABLE ~19:39 WIB."
json.dump(s, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("updated reread:", len(updated))
print("vel_pass:", vel_pass)
print("feedshape added to track_c:", added)
print("contracts now:", len(s['contracts']), "track_c:", len(s.get('track_c',{})))
