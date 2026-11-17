import json, shutil, datetime
BASE='/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files'
shutil.copy(f'{BASE}/onchain-snapshot.json', f'{BASE}/onchain-snapshot-2031.bak.json')
s=json.load(open(f'{BASE}/onchain-snapshot.json'))
rr=json.load(open(f'{BASE}/run-2026-11-05-2031-reread-lean.json'))
blk=rr['block']
prev_block=131821320  # snapshot baseline (run 1931 read block)
interval_min=(blk-prev_block)*3/60
print('merge block',blk,'interval %.1f min'%interval_min)
# --- Route 1 updates (nulls never overwrite) ---
for name,d in rr['reread'].items():
    ent=s['contracts'].get(name)
    if ent is None:
        print('skip orphan',name); continue
    prev=ent.get('totalSupply')
    cur=d.get('totalSupply')
    view='totalSupply'
    if cur is None:
        cur=d.get('totalMinted'); view='totalMinted'
    if prev is not None and cur is not None and view=='totalSupply':
        delta=cur-prev
        rate=delta/interval_min if interval_min else 0
        prev_rate=ent.get('currentRatePerMin')
        ratio=(rate/prev_rate) if prev_rate else None
        vel = bool(ratio is not None and ratio>=1.5 and delta>=20)
        ent['previousTotalSupply']=prev
        ent['totalSupply']=cur
        ent['mintedInInterval']=delta
        ent['intervalMinutes']=round(interval_min,1)
        ent['currentRatePerMin']=round(rate,3)
        ent['previousRatePerMin']=prev_rate
        ent['velocityLegPasses']=vel
        ent['supplyView']=view
        ent[f'velocityNote2031']='Run 2031 (blok %d, interval %.1f mnt vs run 1931): %d->%d (+%d, %.3f/mnt vs prev %.3f = %s) -> velocity %s.'%(blk,interval_min,prev,cur,delta,rate,prev_rate or 0,'None' if ratio is None else '%.2fx'%ratio,'LOLOS' if vel else 'GAGAL')
    elif cur is not None:
        ent['totalSupply']=cur
    for k in ('freeClaimed','freeMinted','balanceOf_user'):
        if d.get(k) is not None:
            ent[k if k!='balanceOf_user' else 'balanceOf_user']=d[k]
    ent['lastReadBlock']=blk
    ent['lastReadWib']='2026-11-05 run 2031'
    print('updated',name,'totalSupply',ent.get('totalSupply'),'vel',ent.get('velocityLegPasses'))
# --- Track C updates (nulls never overwrite) ---
for key,d in rr['track_c'].items():
    ent=s.get('track_c',{}).get(key)
    if ent is None: continue
    for k in ('freeMinted','totalMinted','sharesMinted','freeSharesRemaining','opened','launched','saleEnded','phase'):
        if d.get(k) is not None: ent[k]=d[k]
    ent['lastReadBlock']=blk
# NJAR probe
njar=json.load(open(f'{BASE}/run-2026-11-05-2031-njar-probe.json'))
nj=s['track_c'].get('NJAR')
if nj is not None:
    if njar.get('giftsClaimed') is not None: nj['giftsClaimed']=njar['giftsClaimed']
    if njar.get('giftsClaimed') is not None: nj['giftsLeft']=2000-njar['giftsClaimed']
    if njar.get('live') is not None: nj['live']=njar['live']
    if njar.get('paidSharesSold') is not None: nj['paidSharesSold']=njar['paidSharesSold']
    nj['runNote2031']='Run 2031 (blok %d): giftsClaimed 468->500 (1.500 tersisa), live=1, paidSharesSold 3; giftTaken/hasAgent null run ini (nilai lama dipertahankan: gift terbuka). Gate TETAP GAGAL; tidak di-preview/di-mint; tidak dilaporkan ulang.'%njar['block']
# --- Mossminds / BNBCACHE early recheck ---
er=json.load(open(f'{BASE}/run-2026-11-05-2031-early-recheck.json'))
mm=s['contracts'].get('Mossminds')
if mm is not None:
    d=er['Mossminds']
    if d.get('totalSupply') is not None: mm['totalSupply']=d['totalSupply']
    if d.get('freeMinted') is not None: mm['freeMinted']=d['freeMinted']
    if d.get('FREE_CAP') is not None: mm['FREE_CAP']=d['FREE_CAP']
    mm['freePctVerified']=round(430/2880*100,2)
    mm['runNote2031']='Run 2031 (blok %d): totalSupply 225->431, freeMinted 430/2880 = 14,93%%, slot TERBUKA (canFreeMint=1, claimedFree=0, balance 0). Tetap early (free <25%%), TIDAK promosi, TIDAK di-preview/di-mint.'%er['block']
    mm['lastReadBlock']=er['block']
bc=s['contracts'].get('BNB CACHE Server')
if bc is not None:
    bc['runNote2031']='Run 2031 (blok %d): totalSupply/free reads null (gagal baca, nilai lama dipertahankan: free 71/777); balanceOf(user)=0, freeClaimedBy(user)=0. Tetap early, tidak ada perubahan tier.'%er['block']
    bc['lastReadBlock']=er['block']
# --- Phoenixgent AGE-EXCLUDED ---
px=s['contracts'].pop('Phoenixgent',None)
if px is not None:
    px['status']='excluded-age-over-48h-2026-11-05'
    px['ageExclusionNote']='Run 2031: first mint TERVERIFIKASI 2026-11-03 17:34:16 WIB (blok 131417687); baca segar blok 131826296: totalSupply 1023, freeClaimed 1019/2000 = 50,95%, mintOpen=1, belum sold out; umur ~51,3 jam > 48 jam. DIHAPUS dari contracts -> excluded (age-over-48h). Free % lewati 50% TIDAK menyelamatkan (aturan umur). Sebelumnya strong-lead-gate-blocked; gate tidak pernah lolos, tidak pernah di-mint.'
    s.setdefault('excluded',{})['Phoenixgent']=px
    print('Phoenixgent -> excluded')
# --- NAOMI GENESIS AGE-EXCLUDED (never in snapshot; record so not re-discovered) ---
s.setdefault('excluded',{})['NAOMI GENESIS']={
 'address':'0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9',
 'status':'excluded-age-over-48h-2026-11-05',
 'freeMinted':312,'FREE_SUPPLY':777,'totalMinted':316,'MAX_SUPPLY':7777,
 'ageExclusionNote':'Run 2031 subagent B (Boltbook adamsaja.ai): deployed ~30 Okt 2026, launch ~30 Okt -> >48 jam; freeMinted 312/777 (465 belum diklaim), totalMinted 316/7777, paid 4x0,0015 BNB, mintOpen true, X @0xadamonly. Free slot masih terbuka tapi terlalu tua. Bukti launch: deployment ~30 Okt (bukan first-mint on-chain penuh) - dicatat sebagai excluded agar tidak ditemukan ulang sebagai baru.'
}
print('NAOMI -> excluded')
# --- AgentBox EARLY LEAD (new) ---
s['contracts']['AgentBox']={
 'address':'0x08393dad165d90e7258501fE1dfb5F3498644011',
 'status':'early-lead-reported-2026-11-05',
 'name':'AgentBox','symbol':'ABOX','kind':'MysteryBox',
 'totalOpened':4117,'MAX_BOXES':9999,
 'freeOpened':3361,'xOpened':162,'paidOpenedApprox':594,
 'freePctNote':'free_ counter 3351 ~ FreeBoxOpened 3361; free quota TIDAK ada cap di kontrak (free_ adalah counter, bukan cap) -> % free UNVERIFIED (3361/9999 = 33,6% hanya inferensi, bukan free-quota %).',
 'mintOpen':True,'price':0.001,
 'freeEligible_user':{'ok':1,'hasAgentId':1,'used':0},
 'userSlotNote':'Slot TERBUKA (freeEligible(user) ok=1, hasAgentId=1, used=0; boxesOf(user) kosong) - TIDAK preview-verified (early leads are never previewed).',
 'firstSeenBlock':131766040,
 'firstOpenWib':'2026-11-05 12:47:33 WIB',
 'saleStartWib':'2026-11-05 12:47:28 WIB',
 'saleEndWib':'2026-11-15 12:47:28 WIB',
 'lastReadBlock':131828515,'lastReadWib':'2026-11-05 run 2031',
 'xVerified':False,'velocityVerified':False,
 'website':'https://agentboxnft.xyz',
 'websiteNote':'VERIFIED run 2031: site MB_CONFIG mencetak MYSTERYBOX 0x08393dad... persis + AGENT_REGISTRY 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + BOX_TOKEN/BOX_NFT. Metode (G).',
 'launchNote':'First open TERVERIFIKASI on-chain: first BoxOpened/FreeBoxOpened blok 131766040 = 2026-11-05 12:47:33 WIB (Ankr getLogs dari DEPLOY_BLOCK 131763362; 4125 BoxOpened, 3361 FreeBoxOpened, 162 XBoxOpened). Sale start on-chain saleState() 12:47:28 WIB. Umur ~8 jam saat baca, TERVERIFIKASI <=48 jam. Site: v1 deployed 2026-11-05 11:09:54 +07, v2 redeployed 2026-11-05 (X free box).',
 'baselineNote':'EARLY lead dilaporkan sekali run 2031 (Boltbook 0xkelsey.ai, b/alpha). Agent-shaped: bytecode 19.085 B mengandung registry bytes; site ABI: openFree() no-arg + freeEligible() + saleState().free_. Free % UNVERIFIED (tanpa free cap), velocity belum terhitung (baseline pertama), X account UNVERIFIED (diskusi Boltbook ada; lane X-free terpisah via Worker+Turnstile, X_CAP 500). TIDAK di-preview/di-mint sebagai early lead. Promosi ke strong lead butuh free % >=25% terverifikasi + slot terbuka + umur <=48 jam.',
 'agentShape':'registry bytes in bytecode (19.085 B) + openFree()/freeEligible() in site-embedded ABI + AGENT_REGISTRY in site config',
 'velocityLegPasses':False,
 'supplyView':'totalOpened',
 'previousTotalSupply':None,'previousRatePerMin':None,
 'currentRatePerMin':None,'mintedInInterval':None,'intervalMinutes':None,
 'discussionNote':'Boltbook 0xkelsey.ai: "openFree() is only half the flow - the reveal is a separate call, and my free box paid 100 ABOX" (first-hand).'
}
print('AgentBox added as early lead')
# --- Galaxy Agents watchlist-only (NOT agent-shaped) ---
s['contracts']['Galaxy Agents']={
 'address':'0xa388bba8e4ed07043bae8cc68a00e9aec42f72f4',
 'status':'watchlist-only-not-early-2026-11-05',
 'name':'Galaxy Agents','symbol':'GAGT','kind':'ERC721',
 'totalMinted':145,'MAX_SUPPLY':200,
 'freePctNote':'Tidak ada free view; totalMinted 145/200 = 72,5% total, BUKAN % free.',
 'userBalance':0,
 'firstSeenBlock':131810355,'firstMintWib':'2026-11-05 18:40:02 WIB',
 'lastReadBlock':131828234,'lastReadWib':'2026-11-05 run 2031',
 'xVerified':False,'velocityVerified':False,
 'launchNote':'First mint TERVERIFIKASI on-chain: first Transfer-from-zero blok 131810355 = 2026-11-05 18:40:02 WIB (Ankr getLogs; koreksi jendela pertama yang melewatkan 53 log). Umur TERVERIFIKASI <=48 jam.',
 'baselineNote':'Watchlist-only, BUKAN early lead: agent-shape TIDAK terverifikasi (Sourcify 404; bytecode 5.536 B TANPA registry bytes - parent re-verifikasi via eth_getCode). Boltbook huynguyen.ai (ZH-only): free mint #127, 79/200 tersisa saat posting, tx value 0. TIDAK dipromosikan sampai agent-shape terbukti.',
 'velocityLegPasses':False,'supplyView':'totalMinted',
 'previousTotalSupply':None,'previousRatePerMin':None,'currentRatePerMin':None,
 'mintedInInterval':None,'intervalMinutes':None
}
print('Galaxy Agents added watchlist-only')
# --- 5 paid-only watchlist-only (scan first-seen) ---
paid={
 'HashDoge':{'address':'0xf6E6c51fe4bA9317a1CaA476A8FbDC3401a47D36','symbol':'HDOGE','firstSeenBlock':131824018,'firstMintWib':'2026-11-05 20:15:10 WIB','scanMints':76,'scanMinters':47,'note':'agentRegistry()=registry, requireAgent=1; tanpa free function/view di ABI terverifikasi; mine() berbayar, mintPrice ~0,002955 BNB (dynamic epoch pricing); totalMined 242; startTime 19:32:35 WIB, openedAt 20:15:06 WIB. Umur TERVERIFIKASI <=48 jam. User slot N/A (tanpa free lane).'},
 'HASH ERAS':{'address':'0xB8b23307BEe243E36e464665f4B7825a4afC7e73','symbol':'ERA','firstSeenBlock':131825018,'firstMintWib':'2026-11-05 20:30:03 WIB','scanMints':21,'scanMinters':21,'note':'agentId() constant = registry (tanpa getter AGENT_REGISTRY); MINT_START 2026-11-05 20:30:00 WIB, MINT_END 2026-11-08 20:30:00 WIB, PRICE 0,0005 BNB, MAX_SUPPLY 4444, totalSupply 41; mintedBy(user)=0. Umur TERVERIFIKASI. Tanpa free lane.'},
 'AgentDraw Pass':{'address':'0x53e43b924e016598942b857ea5B00D37Fc278dE5','symbol':'ADPASS','firstSeenBlock':131821361,'firstMintWib':'2026-11-05 20:02:36 WIB','scanMints':11,'scanMinters':11,'note':'agentId() constant = registry; FOUNDER_PRICE 0,001 BNB (500 supply, 0 minted), PLAYER_SUPPLY 2222 (42 minted, 2180 tersisa). First mint di dalam gap scan yang dilewati, diverifikasi langsung via Ankr. Umur TERVERIFIKASI. Tanpa free lane.'},
 'Rune Bear Agent':{'address':'0x3D1F1DAd36DFe781ee813B8d7fe8aF69f332f620','symbol':'RUNB','firstSeenBlock':131824640,'firstMintWib':'2026-11-05 20:27:13 WIB','scanMints':1,'scanMinters':1,'note':'AGENT_REGISTRY()=registry on-chain; PRICE 0,0005 BNB, MAX_SUPPLY 3333, totalMinted 1. Template sama dengan Aether Core. Umur TERVERIFIKASI. Tanpa free lane.'},
 'Sigma Ibis Agent':{'address':'0x8d22b007b404EF49bDCdB9819e0981D9eD514E8D','symbol':'SIGI','firstSeenBlock':131825338,'firstMintWib':'2026-11-05 20:32:27 WIB','scanMints':1,'scanMinters':1,'note':'Template identik dengan RUNB (factory wave Aether Core/Ember Byte). First mint 20:32:27 WIB. Umur TERVERIFIKASI. Tanpa free lane.'},
}
for name,v in paid.items():
    s['contracts'][name]={
     'address':v['address'],'status':'watchlist-only-paid-only-2026-11-05',
     'name':name,'symbol':v['symbol'],'kind':'ERC721',
     'firstSeenBlock':v['firstSeenBlock'],'scanMints':v['scanMints'],'scanMinters':v['scanMinters'],
     'lastReadBlock':131826008,'lastReadWib':'2026-11-05 run 2031',
     'xVerified':False,'velocityVerified':False,'velocityLegPasses':False,
     'launchNote':'First mint TERVERIFIKASI on-chain: blok %d = %s (Ankr getLogs).'%(v['firstSeenBlock'],v['firstMintWib']),
     'baselineNote':'Watchlist-only paid-only (bukan early lead): registry cocok tapi tanpa free lane. '+v['note'],
     'supplyView':'totalSupply','previousTotalSupply':None,'previousRatePerMin':None,'currentRatePerMin':None,
     'mintedInInterval':None,'intervalMinutes':None
    }
    print('added paid-only',name)
# --- AGI sale pair (feed): watchlist-only note, not leads ---
s.setdefault('track_c',{})
for nm,addr in [('AGI-sale-4731','0x4731f2810000000000000000000000000000000000'),('AGI-sale-bC8b','0xbC8b1b7900000000000000000000000000000000')]:
    pass  # full addresses in B feed-shape file; recorded in run log only, not snapshot (free pool unverified + launched=0)
# --- top-level notes ---
s['runNote2031']='Run 2031: 1 EARLY LEAD BARU (AgentBox, dilaporkan sekali); 1 AGE-EXCLUDED (Phoenixgent, >48 jam, belum sold out); NAOMI GENESIS age-excluded (dicatat di excluded); 5 watchlist-only paid-only baru (HashDoge, HASH ERAS, AgentDraw Pass, Rune Bear, Sigma Ibis); Galaxy Agents watchlist-only-not-early (bukan agent-shaped). 0 kandidat, 0 strong lead baru/promosi, 0 track-C lead/kandidat, 0 pending claim baru/dibuka. Scan: window 131824009-131826008 (2000 blok), gap 131821316-131824008 (2693 blok) dilewati; watermark -> 131826008; seen 7985->8292. Mossminds 431 (free 430/2880 = 14,93%, slot terbuka) tetap early. NJAR giftsClaimed 500/2000, gate tetap gagal. BINANCEAI tetap refund/failed. Jolly lewat 48 jam 2026-11-05 23:27 WIB (dicatat untuk run mendatang).'
s['runNote2031_scan']='Run 2031 scan: 80 panggilan Ankr, 0 error, ~19 mnt (20:37-20:56 WIB); 261 NFT, 631 ERC-20; first-seen 8 NFT (0 early lead baru); 5c: 20 dicek, 0 sale-shaped; feed sale-shape 0.'
s['last_run_wib']='2026-11-05 run 2031'
s['last_run_note']=s['runNote2031']
json.dump(s,open(f'{BASE}/onchain-snapshot.json','w'),indent=1)
print('contracts:',len(s['contracts']),'track_c:',len(s.get('track_c',{})) ,'excluded:',len(s.get('excluded',{})))
print('MERGE DONE')
