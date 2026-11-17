#!/usr/bin/env python3
"""Merge run 1701 (17:01 WIB) into onchain-snapshot.json. Read-only except snapshot + run log."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
r17=json.load(open(BASE+"run-2026-11-16-1701-reread.json"))
r16=json.load(open(BASE+"run-2026-11-16-1631-reread.json"))
v17=json.load(open(BASE+"run-2026-11-16-1701-verify.json"))
fs=json.load(open(BASE+"run-2026-11-16-1701-feedshape.json"))
feed=json.load(open(BASE+"run-2026-11-16-1701-sourcify.json"))
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
    # snapshot fields may be stale vs 1631 reread; prefer 1631 reread as baseline
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
    entry['lastReadWib']="2026-11-16 ~17:01 WIB"
    entry['supplyView']=view
    note=f"Run 1701 (blok {r17['block']}, interval ~{INTERVAL_MIN:.1f} mnt vs run 1631): "
    if minted is None: note+=f"supply {view} {new_sup} (baseline {prev_sup} tak terbaca) -> velocity TIDAK dihitung"
    else: note+=f"{prev_sup}->{new_sup} (+{minted}, {rate:.3f}/mnt vs prev {prev_rate} = {'None' if ratio is None else round(ratio,2)}x) -> velocity {'LOLOS' if passes else 'GAGAL'}"
    if views.get('freeMinted') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeMinted {views['freeMinted']}/{entry['FREE_SUPPLY']} = {views['freeMinted']/entry['FREE_SUPPLY']*100:.1f}%"
    if views.get('freeClaimed') is not None and entry.get('FREE_SUPPLY'):
        note+=f"; freeClaimed {views['freeClaimed']}/{entry['FREE_SUPPLY']} = {views['freeClaimed']/entry['FREE_SUPPLY']*100:.1f}%"
    note+="; DIAM." if not passes else "; velocity lolos TAPI bukan kandidat/strong lead (lihat kaki lain)."
    entry['runNote1701_1116']=note
    updated.append(name)
# SPARKS duplicate entry 'First-Dollar Sparks' same address
sp=s['contracts'].get('First-Dollar Sparks')
if sp is not None:
    sp['totalSupply']=1041; sp['totalMinted']=1041; sp['previousTotalSupply']=1036
    sp['previousRatePerMin']=0.7931034482758621; sp['currentRatePerMin']=round(5/INTERVAL_MIN,4)
    sp['velocityLegPasses']=False; sp['lastReadBlock']=r17['block']; sp['lastReadWib']="2026-11-16 ~17:01 WIB"
    sp['runNote1701_1116']="Run 1701 (blok 133908291): 1036->1041 (+5, 0.167/mnt vs prev 0.793 = 0.21x) -> velocity GAGAL; free% UNVERIFIED + umur UNVERIFIED -> BUKAN kandidat, BUKAN strong lead. Watchlist-only. DIAM."
# Punch Card (verify script, block 133908589)
pc=s['contracts']['Punch Card']
pv=v17['reads']['PunchCard']['views']
pc['totalSupply']=pv['totalSupply']; pc['totalMinted']=pv['totalMinted']; pc['freeMinted']=pv['freeMinted']
pc['previousTotalSupply']=500; pc['previousRatePerMin']=13/29.9; pc['currentRatePerMin']=round(29/29.9,4)
pc['velocityLegPasses']=True; pc['lastReadBlock']=133908589; pc['lastReadWib']="2026-11-16 ~17:01 WIB"
pc['runNote1701_1116']="Run 1701 (blok 133908589): totalSupply 500->529 (+29, 0.970/mnt vs prev 0.435 = 2.23x) -> velocity LOLOS (>=1.5x DAN >=20 token); freeMinted 528/5555 = 9.5% (masih <50% kandidat, <70% strong lead); mintOpen 1, mintPriceFor(user,1)=0, mintedCount(user)=0, bal_user=0. Umur terverifikasi <24 jam. Early lead saja, TANPA promosi. DIAM."
# BUBB
bubb=s['contracts']['Agent Bubble']
bv=v17['reads']['BUBB']['views']
bubb['totalSupply']=bv['totalSupply']; bubb['totalMinted']=bv['totalMinted']; bubb['freeMinted']=bv['freeMinted']
bubb['previousTotalSupply']=1621; bubb['previousRatePerMin']=None; bubb['currentRatePerMin']=None
bubb['velocityLegPasses']=False; bubb['lastReadBlock']=133908589; bubb['lastReadWib']="2026-11-16 ~17:01 WIB"
bubb['runNote1701_1116']="Run 1701 (blok 133908589): totalSupply 1621->1777 (+156 sejak 15 Nov 04:35), freeMinted 1633/2222 = 73.5% (>70% ambang strong lead) TAPI umur peluncuran TETAP UNVERIFIED (pertama terlihat 13 Nov, tanpa stated launch/first-mint) + X unverified + website unverified -> BUKAN strong lead, BUKAN kandidat. Slot user terbuka (bal_user=0, mintOpen 1). Watchlist-only. DIAM."
# New triage entries
s['contracts']['HEXCOVEN']={"address":"0xd3d5d57e4942cedcb6864c1dce1e9808544dd30d","status":"checked-age-excluded-2026-11-16","name":"HEXCOVEN","symbol":"WITCH","kind":"ERC721","totalSupply":337,"MAX_SUPPLY":9999,"mintOpen":1,"PRICE":50000000000000,"firstFreeUsed":336,"paidMinted":1,"FIRST_FREE_CAP":2000,"lastReadBlock":133908589,"lastReadWib":"2026-11-16 ~17:01 WIB","launchNote":"Umur TERVERIFIKASI >=24 jam: mintStart() on-chain 1794397822 = 2026-11-11 ~18:50 WIB -> umur ~4 hari 22 jam saat run. AGE-EXCLUDED.","baselineNote":"Triase Boltbook run 1701 (post ~16:58 WIB: 333/9.999, freeLeft 9.666). Sourcify verified 84 fns: freeMintX + FIRST_FREE_CAP + freeLeft, TAPI TANPA registry reference (0x60B9...022F tidak ada di source) dan TANPA AgentGate/agent fn; gate X (xCheck/xDigest/xSigner), plain wallet lolos mint (post follow-up) -> BUKAN agent-shaped. BUKAN early lead (first mint bukan di run ini + umur >24 jam). TIDAK pernah dilaporkan sebagai lead -> DIAM.","xVerified":False,"velocityVerified":False}
s['contracts']['Orin Agent']={"address":"0x91921eb375fe32706f8cd92376f613f923d01771","status":"watchlist-only-2026-11-16","name":"Orin Agent","kind":"ERC721","totalSupply":4900,"MAX_SUPPLY":5000,"mintOpen":None,"balanceOf_user":0,"lastReadBlock":133908589,"lastReadWib":"2026-11-16 ~17:01 WIB","launchNote":"Umur UNVERIFIED: tanpa stated launch time; Sourcify UNVERIFIED (404); pertama terlihat post Boltbook recheck 16:58 WIB 16 Nov (4.900/5.000).","baselineNote":"Triase Boltbook run 1701. Pola 99%-club (sama seperti VornAgent-8c2f): totalSupply 4900/5000, SEMUA free view revert (freeClaimed/freeMinted/FREE_SUPPLY) -> free% UNVERIFIED (tidak boleh ganti % total supply); Sourcify unverified -> agent-shape tidak terverifikasi. BUKAN early lead (first mint bukan di run ini), BUKAN strong lead (free% + umur unverified). Watchlist-only. TIDAK pernah preview/mint.","xVerified":False,"velocityVerified":False}
s['contracts']['Pulse District']={"address":"0xf6cc6364c0d7764a5a751c08314db181df5b825c","status":"checked-not-lead-2026-11-16","name":"Pulse District","symbol":"CY25","kind":"ERC721","totalSupply":360,"MAX_SUPPLY":1738,"mintOpen":1,"balanceOf_user":0,"lastReadBlock":133908589,"lastReadWib":"2026-11-16 ~17:01 WIB","launchNote":"Umur UNVERIFIED: tanpa stated launch time / first-mint; pertama terlihat post Boltbook 16 Nov (359/1.738).","baselineNote":"Triase Boltbook run 1701. Sourcify verified 35 fns: agentIds/agentTokenIdOf/mintWithAgentTokenId/mintedByAgent (Agent-ID-token gated) TAPI TANPA registry reference dan TANPA free view (tanpa freeMinted/freeClaimed/freeLeft) -> free% UNVERIFIED; BUKAN early lead (first mint bukan di run ini). BUKAN kandidat/strong lead. TIDAK pernah preview/mint.","xVerified":False,"velocityVerified":False}
s['contracts']['LABTOK']={"address":"0x849368938eA0092c809A687FaC0b3ECA3940561f","status":"checked-not-lead-2026-11-16","name":"LABTOK","symbol":"LBT","kind":"ERC20","totalSupply":1000000000000000000000000,"lastReadBlock":133908589,"lastReadWib":"2026-11-16 ~17:01 WIB","baselineNote":"Triase Boltbook run 1701 (post analisis metadata/bytecode). ERC20 totalSupply 1e24, Sourcify UNVERIFIED (404), tanpa sale-shape (bukan NFT mint, bukan share sale S1/S2). BUKAN lead. TIDAK pernah preview/mint.","xVerified":False,"velocityVerified":False}
s['contracts']['bridge-0x10b80088']={"address":"0x10b80088fdaf9363d83671be66b64f231f9e92f6","status":"checked-age-excluded-2026-11-16","source":"scan-bridge","lastReadWib":"2026-11-16 ~17:01 WIB","baselineNote":"Temuan pelengkap scan (bridge run-16, mint 3 Nov 23:42-23:45 WIB, pola PACTURE, free, 1 entity). Ditambahkan ke snapshot run 1701 pada re-read rutin pertama per aturan bridge; umur first-mint ~13 hari (>24 jam) -> AGE-EXCLUDED. Tidak pernah dilaporkan sebagai lead -> DIAM (tidak dilaporkan).","xVerified":False,"velocityVerified":False}
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
    if a.lower() in existing: continue
    key="Feed-0x"+a[2:6]
    tc[key]={"address":a,"status":"checked-not-sale-shape-2026-11-16",
             "note":f"Run 1701 Sourcify feed (verified {vmap.get(a)}): S1={o.get('S1')} S2={o.get('S2')}; mint={o.get('has_mint')} quote={o.get('has_quote')} free_views={o.get('free_views')} agent_ref={o.get('agent_ref')} fns={o.get('n_fns')}. Bukan lead track-C; first-mint tidak terverifikasi (Ankr 401) -> bukan early lead.",
             "lastReadWib":"2026-11-16 ~17:01 WIB"}
    existing.add(a.lower()); added+=1
s['last_run']="free-mint-search 2026-11-16 17:01 WIB — DIAM: 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 eksekusi/preview; 1 velocity lolos (Punch Card, tanpa promosi); 4 triase baru (HEXCOVEN age-excluded, Orin watchlist-only, Pulse + LABTOK checked-not-lead); scan fast-fail Ankr 401"
s['runNote1701_1116']="Run 1701 (17:01 WIB, blok reread 133908291, 37/37 OK, 79,9 dtk; verify blok 133908589): DIAM. Velocity LOLOS: Punch Card +29 (2,23x, free 9,5% - early lead saja). Semua reread lain velocity GAGAL (maks +5 SPARKS). BUBB freeMinted 1633/2222 = 73,5% TAPI umur unverified -> bukan strong lead. BinanceAI-mint tetap refund (launched 0/failed 1/isRefundPhase 1). RigForge tetap belum buka (openedAt 0, freeSharesLeft 638). LumenFindings age-excluded (genesisStart tetap). Scan pre-flight Ankr 401 (head 133908734), watermark tetap 132512564. Bridge: 116 kontrak, 1 not-in-snapshot (0x10b8 PACTURE-pattern, age-excluded, diam). Discovery: Boltbook EN+ZH 13 alamat unik, 3 baru ditriase (HEXCOVEN age-excluded ~5 hari, Orin watchlist-only, Pulse checked-not-lead) + LABTOK checked-not-lead; Sourcify 20 (0 S1/S2); sweep EN hanya proyek lama; Odaily 0 hit. Tidak ada age-exclusion baru (deadline terdekat ABYSSCABLE ~19:39 WIB)."
json.dump(s, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("updated reread:", len(updated))
print("vel_pass:", vel_pass)
print("feedshape added to track_c:", added)
print("contracts now:", len(s['contracts']), "track_c:", len(s.get('track_c',{})))
