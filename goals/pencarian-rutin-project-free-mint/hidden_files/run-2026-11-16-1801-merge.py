#!/usr/bin/env python3
"""Merge run 1801 (18:01 WIB) into onchain-snapshot.json. Read-only except snapshot."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
r18=json.load(open(BASE+"run-2026-11-16-1801-reread.json"))
r17=json.load(open(BASE+"run-2026-11-16-1731-reread.json"))
v18=json.load(open(BASE+"run-2026-11-16-1801-verify.json"))
vr=json.load(open(BASE+"run-2026-11-16-1801-verify-retry.json"))
fs=json.load(open(BASE+"run-2026-11-16-1801-feedshape.json"))
feed=json.load(open(BASE+"run-2026-11-16-1801-sourcify.json"))
INTERVAL_MIN=(r18['block']-r17['block'])*0.45/60.0
print("interval_min", round(INTERVAL_MIN,1), "blocks", r17['block'], "->", r18['block'])

def get_supply(entry, views):
    if entry.get('totalMinted') is not None and views.get('totalMinted') is not None:
        return views.get('totalMinted'), 'totalMinted'
    if views.get('totalSupply') is not None:
        return views.get('totalSupply'), 'totalSupply'
    return views.get('totalMinted'), 'totalMinted'

updated=[]; vel_pass=[]
for name, rd in r18['reads'].items():
    views=rd.get('views') or {}
    entry=s['contracts'].get(name)
    if entry is None:
        for k,v in s['contracts'].items():
            if isinstance(v,dict) and (v.get('address') or '').lower()==rd['address'].lower():
                entry=v; name=k; break
    if entry is None:
        print("SKIP (not in snapshot):", name); continue
    new_sup, view = get_supply(entry, views)
    prev_sup = entry.get('totalSupply') if view=='totalSupply' else entry.get('totalMinted')
    prev_views=(r17['reads'].get(name) or {}).get('views') or {}
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
    entry['previousTotalSupply']=prev_sup
    if view=='totalSupply': entry['totalSupply']=new_sup
    else: entry['totalMinted']=new_sup
    if views.get('freeMinted') is not None: entry['freeMinted']=views['freeMinted']
    if views.get('freeClaimed') is not None: entry['freeClaimed']=views['freeClaimed']
    if views.get('mintOpen') is not None: entry['mintOpen']=views['mintOpen']
    entry['previousRatePerMin']=prev_rate
    entry['currentRatePerMin']=rate
    entry['velocityLegPasses']=passes
    entry['lastReadBlock']=r18['block']
    entry['lastReadWib']="2026-11-16 ~18:01 WIB"
    entry['supplyView']=view
    note=f"Run 1801 (blok {r18['block']}, interval ~{INTERVAL_MIN:.1f} mnt vs run 1731): "
    if minted is None: note+=f"supply {view} {new_sup} (baseline {prev_sup} tak terbaca) -> velocity TIDAK dihitung"
    else: note+=f"{prev_sup}->{new_sup} (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {'None' if ratio is None else round(ratio,2)}x) -> velocity {'LOLOS' if passes else 'GAGAL'}"
    if views.get('freeMinted') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeMinted {views['freeMinted']}/{entry['FREE_SUPPLY']} = {views['freeMinted']/entry['FREE_SUPPLY']*100:.1f}%"
    if views.get('freeClaimed') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeClaimed {views['freeClaimed']}/{entry['FREE_SUPPLY']} = {views['freeClaimed']/entry['FREE_SUPPLY']*100:.1f}%"
    note+="; DIAM." if not passes else "; velocity lolos TAPI bukan kandidat/strong lead (lihat kaki lain)."
    entry['runNote1801_1116']=note
    updated.append(name)
# SPARKS duplicate entry 'First-Dollar Sparks' same address
sp=s['contracts'].get('First-Dollar Sparks')
if sp is not None:
    sp['totalSupply']=1049; sp['totalMinted']=1049; sp['previousTotalSupply']=1045
    sp['previousRatePerMin']=0.16666666666666666; sp['currentRatePerMin']=round(4/INTERVAL_MIN,4)
    sp['velocityLegPasses']=False; sp['lastReadBlock']=r18['block']; sp['lastReadWib']="2026-11-16 ~18:01 WIB"
    sp['runNote1801_1116']="Run 1801 (blok 133916418): 1045->1049 (+4, 0.132/mnt vs prev 0.167 = 0.79x) -> velocity GAGAL; free% UNVERIFIED + umur UNVERIFIED -> BUKAN kandidat, BUKAN strong lead. Watchlist-only. DIAM."
# Punch Card (verify-retry, block 133916739): 601 -> 627 (+26)
pc=s['contracts']['Punch Card']
pv=vr['reads']['PunchCard']['views']
pc['totalSupply']=pv['totalSupply']; pc['totalMinted']=pv['totalMinted']; pc['freeMinted']=pv['freeMinted']
pc['previousTotalSupply']=601; pc['previousRatePerMin']=2.3506; pc['currentRatePerMin']=round(26/30.77,4)
pc['velocityLegPasses']=False; pc['lastReadBlock']=133916739; pc['lastReadWib']="2026-11-16 ~18:01 WIB"
pc['runNote1801_1116']="Run 1801 (blok 133916739): totalSupply 601->627 (+26, 0.845/mnt vs prev 2.351 = 0.36x) -> velocity GAGAL (<1.5x); freeMinted 626/5555 = 11.3% (masih <50% kandidat, <70% strong lead); mintOpen 1, mintPriceFor(user,1)=0, mintedCount(user)=0, bal_user=0. Early lead saja, TANPA promosi. DIAM."
# BUBB (verify, block from verify.json)
bubb=s['contracts']['Agent Bubble']
bv=v18['reads']['BUBB']['views']
bubb['totalSupply']=bv['totalSupply']; bubb['totalMinted']=bv['totalMinted']; bubb['freeMinted']=bv['freeMinted']
bubb['previousTotalSupply']=1782; bubb['previousRatePerMin']=None; bubb['currentRatePerMin']=None
bubb['velocityLegPasses']=False; bubb['lastReadBlock']=v18['block']; bubb['lastReadWib']="2026-11-16 ~18:01 WIB"
bubb['runNote1801_1116']="Run 1801 (blok %s): totalSupply 1782->1783 (+1), freeMinted 1639/2222 = 73.8%% (>70%% ambang strong lead) TAPI umur peluncuran TETAP UNVERIFIED (pertama terlihat 13 Nov, tanpa stated launch/first-mint) + X unverified + website unverified -> BUKAN strong lead, BUKAN kandidat. Slot user terbuka (bal_user=0, mintOpen 1). Watchlist-only. DIAM." % v18['block']
# Poffzi (verify-retry): still pre-launch
pf=s['contracts']['Poffzi']
pfv=vr['reads']['Poffzi']['views']
pf['totalSupply']=pfv['totalSupply']; pf['totalMinted']=pfv['totalMinted']; pf['freeMinted']=pfv['freeMinted']
pf['mintOpen']=pfv['mintOpen']; pf['saleOpen']=pfv['saleOpen']
pf['lastReadBlock']=133916739; pf['lastReadWib']="2026-11-16 ~18:01 WIB"
pf['runNote1801_1116']="Run 1801 (blok 133916739, retry sesudah chunk verify pertama gagal total via publicnode): totalSupply 0, mintOpen 0, saleOpen 0, saleStart 1794844811 = 2026-11-16 23:00:11 WIB — TETAP PRE-LAUNCH. Watchlist-only, dipantau saat sale buka 23:00 WIB. DIAM."
# Vezlune (new, verified this run): pre-launch, saleStart 19:00:11 WIB, website verified via contractURI
s['contracts']['Vezlune']={"address":"0xA9531f2C18E9398b50c13f1a108EbE7462927154","status":"watchlist-only-pre-launch-2026-11-16","name":"Vezlune","symbol":"VZLN","kind":"ERC721","totalSupply":0,"totalMinted":0,"freeMinted":0,"FREE_SUPPLY":100,"MAX_SUPPLY":700,"mintOpen":0,"saleOpen":0,"saleStart":1794830411,"saleEnd":1795435211,"balanceOf_user":0,"lastReadBlock":v18['block'],"lastReadWib":"2026-11-16 ~18:01 WIB","launchNote":"BELUM LAUNCH: saleStart on-chain 1794830411 = 2026-11-16 19:00:11 WIB (saleEnd +7 hari); totalSupply 0, mintOpen 0, saleOpen 0 saat run 18:01 WIB.","baselineNote":"Ditemukan via hot-leg watchlist reminder (Sourcify feed, template sama dgn Poffzi — 73 fns, agentIdRegistry + freeMint/freeMintedBy + quote + mint) + dikonfirmasi run 1801 (verify, blok %s). Website TERVERIFIKASI via contractURI external_link https://vezlune-cut.pages.dev/ (HTTP 200, mencetak kontrak persis). Free pool 100, paid 600 @ 0.0015 BNB. Watchlist-only PRE-LAUNCH: bukan lead, bukan kandidat, TIDAK pernah preview/mint; dipantau saat sale buka 19:00 WIB." % v18['block'],"website":"https://vezlune-cut.pages.dev/","gate":"website_verified_via_contractURI","xVerified":False,"velocityVerified":False}
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
             "note":f"Run 1801 Sourcify feed (verified {vmap.get(a)}): S1={o.get('S1')} S2={o.get('S2')}; mint={o.get('has_mint')} quote={o.get('has_quote')} free_views={o.get('free_views')} agent_ref={o.get('agent_ref')} fns={o.get('n_fns')}. Bukan lead track-C; first-mint tidak terverifikasi (Ankr 401) -> bukan early lead.",
             "lastReadWib":"2026-11-16 ~18:01 WIB"}
    existing.add(a.lower()); added+=1
s['last_run']="free-mint-search 2026-11-16 18:01 WIB — SILENT: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 eksekusi/preview, 0 perubahan; Vezlune pre-launch ditambahkan watchlist-only (sale buka 19:00 WIB, website terverifikasi); Punch Card velocity gagal (+26, 0.36x); BUBB 73.8% free tapi umur unverified; scan fast-fail Ankr 401"
s['runNote1801_1116']="Run 1801 (18:01 WIB, blok reread 133916418, 36/36 OK, 74,6 dtk; verify blok %s, retry 133916739): SILENT — 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 eksekusi/preview, 0 perubahan status. Velocity: TIDAK ADA yang lolos (maks +4 SPARKS; Punch Card +26 tapi 0.36x vs prev -> GAGAL; free 626/5555 = 11,3%%, early lead saja). BUBB freeMinted 1639/2222 = 73,8%% TAPI umur unverified -> bukan strong lead. BinanceAI-mint tetap refund (launched 0/failed 1/isRefundPhase 1, dari run 1731 — views gagal dibaca run ini, tidak berubah asumsi). RigForge tetap belum buka (openedAt 0, freeSharesLeft 637, run 1731). Poffzi tetap pre-launch (saleStart 23:00:11 WIB). BARU: Vezlune 0xA9531f2C18E9398b50c13f1a108EbE7462927154 ditambahkan watchlist-only-pre-launch (saleStart 19:00:11 WIB, FREE_SUPPLY 100/MAX 700, template sama dgn Poffzi, website TERVERIFIKASI https://vezlune-cut.pages.dev/ via contractURI — mencetak kontrak persis); bukan lead/kandidat, TIDAK dilaporkan sebagai lead. Scan pre-flight Ankr 401 (head 133916333), watermark tetap 132512564, gap ~1.403.769 blok. Bridge: 116 kontrak, 0 baru vs snapshot. Discovery: Boltbook EN+ZH 11 alamat unik, 0 baru; Sourcify 20 (0 S1/S2 per daftar sempit main-job; 14 baru dicatat checked-not-sale-shape di track_c); sweep EN+ZH hanya proyek lama (AGENT COSMOS/Grove/AGENTID/Jinchan sudah di snapshot, age-excluded/sold out); Odaily 0 hit. Deadline umur berikutnya: ABYSSCABLE ~19:39 WIB." % v18['block']
import copy
json.dump(s, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("updated reread:", len(updated))
print("vel_pass:", vel_pass)
print("feedshape added to track_c:", added)
print("contracts now:", len(s['contracts']), "track_c:", len(s.get('track_c',{})))
