import json
S='onchain-snapshot.json'
snap=json.load(open(S))
reread=json.load(open('run-2026-11-08-1601-reread.json'))
tc_reread=reread['track_c']
HEAD=132369478  # reread block
WIB_REREAD='2026-11-08 16:35 WIB'
WIB_NOW='2026-11-08 16:54 WIB'
contracts=snap['contracts']
updated=0
NUM=['totalSupply','totalMinted','freeClaimed','freeMinted','FREE_SUPPLY','MAX_SUPPLY','mintOpen','balanceOf_user','freeClaimed_user']
for name, rd in reread['reread'].items():
    e=contracts.get(name)
    if e is None: continue
    changed=False
    for f in NUM:
        v=rd.get(f)
        if v is not None and e.get(f)!=v:
            e[f]=v; changed=True
    e['lastReadBlock']=reread['block']
    e['lastReadWib']=WIB_REREAD
    if changed: updated+=1
print('contracts updated (numeric change):', updated, 'of', len(reread['reread']))
notes={
 'Undead NFTs': 'Run 1601: +10 mint (702->712), velocity false, free% UNVERIFIED (freeMinted 206, tanpa FREE_SUPPLY) - early lead, belum promosi.',
 'CAISHEN': 'Run 1601: free 214/888 = 24.1% (di bawah 25% strong), +3 mint - early lead, belum promosi.',
 'Pixel Laptop': 'Run 1601: +2 mint, free% null - early lead, belum promosi.',
 'NEKART': 'Run 1601: +3 mint, free% null - early lead, belum promosi.',
 'Alchemister': 'Run 1601: +17 mint, free% null - early lead, belum promosi.',
 'Jinli Agents': 'Run 1601: +1 mint (free 30.41%), balance 0, slot terbuka, gate website tetap GAGAL (tidak berubah) - tidak di-mint, tidak dilaporkan ulang.',
 'Dafeiyu': 'Run 1601: +19 mint, free% null, balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Chiphiveowl': 'Run 1601: +8 mint (free 72.12%), balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Farmbuxiang': 'Run 1601: +2 mint (free 68.43%), balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Paw Gang': 'Run 1601 (read-only): totalMinted 2477->2896 (+419), mintOpen 1, balance 0; totalSupply null (kontrak tanpa view totalSupply, bukan nol); totalMinted >2503 -> fase 4 (PoW 33-bit); PoW tetap memblokir (tidak dicoba ulang di VM).',
 'Ink Koi': 'Run 1601: velocity PASS (+203, 11.98x) free% VERIFIED 61.94% (1720/2777), umur ~22.8h - TAPI slot user SUDAH terpakai (freeClaimed(user)=1, balance 1 sejak run 0831) - BUKAN kandidat/strong lead, tidak promosi.',
 'Gourdmare': 'Run 1601: velocity PASS (+108, 68.2x) free% VERIFIED 56.3% - TAPI status promotion-discarded-same-owner-2026-11-03 - TIDAK PERNAH dipromosikan/dilaporkan.',
 'HIVE Agents': 'Run 1601: totalSupply flat 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan.',
 'Agent Goats': 'Run 1601: free 737/1111 = 66.34%, umur UNVERIFIED - tetap watchlist-only.',
}
for name, note in notes.items():
    if name in contracts:
        contracts[name]['runNote1601_1108']=note
# track_c updates
tc=snap['track_c']
tc_updated=0
for name, rd in tc_reread.items():
    e=tc.get(name)
    if e is None: continue
    for f in ['totalSupply','freeMinted','freeSharesRemaining','balanceOf_user','freeClaimed_user']:
        v=rd.get(f)
        if v is not None and e.get(f)!=v:
            e[f]=v; tc_updated+=1
print('track_c fields updated:', tc_updated)
# NJAR post-deadline note (entry removed below, note kept in runNote)
# --- AGE EXCLUSIONS (verified launch >48h, not sold out) ---
removed={
 'Agent Wallet': 'first mint 2026-11-05 21:56:35 WIB (blok 131836550), umur ~67 jam; nextTokenId()=25 (naik dari 11), tanpa MAX cap di ABI, mint gratis nonpayable masih terbuka - BUKAN sold out.',
 'AgentX': 'first mint 2026-11-06 01:21:38 WIB (blok 131864930), umur ~63 jam; totalSupply 1984/2500 - BUKAN sold out.',
 'HI-SCORE': 'first mint 2026-11-06 01:08:42 WIB (blok 131865618), umur ~64 jam; totalSupply 331 (+1 interval ini, masih minting) - BUKAN sold out.',
 'LastCall': 'first mint 2026-11-06 02:04:23 WIB (blok 131869584), umur ~63 jam; totalMinted 298/10000 - BUKAN sold out.',
 'CantonTron': 'first mint 2026-11-06 09:50:40 WIB (blok 131931747), umur ~55 jam; totalMinted 968/3333 - BUKAN sold out. Juga dihapus dari track_c (status track-c-blocked-gate-failed-2026-11-06).',
 'AgentB-c047': 'first mint 2026-11-06 14:03:03 WIB (blok ~131965391), umur ~51 jam; totalMinted 902/10000 - BUKAN sold out.',
 'AgentB-06ec': 'first mint 2026-11-06 14:24:06 WIB (blok ~131968198), umur ~50 jam; totalMinted 898/10000 - BUKAN sold out.',
 'AgentPad Agent': 'first mint 2026-11-06 15:27:20 WIB (blok 131976627), umur ~49 jam; totalMinted 169/10000 - BUKAN sold out.',
 'Muster': 'first mint 2026-11-06 15:04:44 WIB (blok 131973615), umur ~50 jam; totalMinted 1/888 - BUKAN sold out.',
}
for name in removed:
    contracts.pop(name, None)
print('age-excluded removed from contracts:', len(removed))
# --- TRACK_C removals ---
tc_removed={}
if 'NJAR' in tc:
    tc_removed['NJAR']='sale 0x816458b734d17d59058762deaadd9b952bad6985: fillDeadline 2026-11-08 16:00:37 WIB LEWAT, live()=0 (sale CLOSED), giftsClaimed 836/2000, paidSharesSold 6, tradingOpen() 0->1, saleStart 2026-11-05 16:00:37 WIB (umur ~72 jam >48 jam), user balance 0, tidak pernah klaim. Status lama: track-c-lead-gate-blocked-2026-11-05.'
    tc.pop('NJAR', None)
if 'CantonTron' in tc:
    tc_removed['CantonTron']='lihat age-exclusions di atas (first mint 2026-11-06 09:50:40 WIB, umur ~55 jam). Status lama: blocked-gate-failed-2026-11-06.'
    tc.pop('CantonTron', None)
print('track_c removed:', list(tc_removed.keys()))
# --- ADD Voltlings (strong lead, gate FAILED) ---
contracts['Voltlings']={
 'address':'0xB1f4f9c3Bb8533064fFec75dFab1Be88833b3a32',
 'status':'strong-lead-2026-11-08-gate-failed',
 'name':'Voltlings','symbol':'VOLT','kind':'ERC721',
 'totalSupply':84,'totalMinted':84,'freeClaimed':None,'freeMinted':84,
 'FREE_SUPPLY':111,'MAX_SUPPLY':1111,'PAID_SUPPLY':1000,'PAID_PER_WALLET':50,
 'PRICE_1':300000000000000,'PRICE_2':500000000000000,
 'mintOpen':1,'balanceOf_user':0,'claimedFree_user':0,
 'freePctVerified':75.68,
 'firstMintWib':'2026-11-08 16:32:01 WIB','firstMintBlock':132369105,
 'owner':'0x6b4e26a6d993b9bfea79ada431113257d2dedee6',
 'source':'Sourcify recently-verified feed run 1601 (verifiedAt 2026-11-08T09:32:08Z) + on-chain scan run 1601 window 132368443-132369442 (9 mint/9 minter) + cross-check 411 file onchain-scan-*.json (tidak ada di scan historis manapun)',
 'website':None,
 'gate':'FAILED run 1601 - metode A-N dicoba, TIDAK ADA website terverifikasi. (A) pencarian alamat mentah: tanpa hasil; (B) Boltbook EN+ZH 2x fetch (~16:35, ~16:55 WIB): tanpa sebutan Voltlings; (C) Sourcify source/metadata: tanpa URL; (D) pola same-family: tanpa hasil; (E) owner 0x6b4e26a6... bukan di same-owner-discards, tanpa grup dikenal; (F) n/a - tidak ada handle ditemukan di tempat lain; (G) pencarian nama proyek: tanpa situs (hanya AgentVOLT yang BERBEDA + Nidavellir/AGENT MAO yang sudah dikenal); (H) tanpa contractURI; (I) tokenURI(1) metadata tanpa external_url (keys: name/description/image/attributes saja); (J) ABI tanpa fungsi site/URL; (K) GitHub: tanpa repo; (L) BscScan token page via live browser: TANPA Website/X/Telegram/Discord/sosial, TANPA Token Info diserahkan (hanya tautan X milik BscScan di footer); (M) site:vercel.app/pages.dev/deed.page: tanpa hasil; (N) registry handleOf(owner) kosong, tanpa author-bio hop.',
 'xNote':'TIDAK ADA akun X proyek ditemukan; X opsional, bukan penghambat - yang menggagalkan gate adalah TIDAK ADA website.',
 'runNote1601_1108':'STRONG LEAD run 1601 -> GATE GAGAL, TIDAK di-preview/TIDAK di-mint, dilaporkan sekali. 3 kaki strong lead TERVERIFIKASI: (a) umur first mint 2026-11-08 16:32:01 WIB (blok 132369105, timestamp blok via dataseed; Sourcify verifiedAt 16:32:08 WIB; walk-back Ankr 0 mint sebelum 132320000; cross-check 411 scan historis: tidak ada) ~17 mnt saat triase, <=48 jam; (b) free 61/111 = 55.0% saat triase, 84/111 = 75.7% saat merge (~16:54 WIB) - laju ~1-4/menit, 27 free tersisa; (c) slot user TERBUKA (claimedFree(user)=0, balanceOf(user)=0, registry balanceOf(user)=1 Agent ID). Agent-shaped: Sourcify exact_match; AGENT_ID constant = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis (dibaca dari source); mintFree() gated (Agent ID + belum claimedFree), FREE_SUPPLY 111, FREE_PER_WALLET 1 (claimedFree mapping), mintStart=0 (tanpa batas waktu), paid 0.0003/0.0005 BNB (PRICE_1/PRICE_2, STEP 500), MAX_SUPPLY 1111. Rarity: tier Common/Rare/Epic/Legendary/Mythic dari source (kuota 600/300/150/50/11); token #1 Common (PWR 15 GRD 47 SPD 16 LCK 48). Owner 0x6b4e26a6... bukan di same-owner-discards. Gate website GAGAL (lihat field gate) -> TIDAK ADA audit Binance / preview (gate didahulukan, eksekusi dilarang). Status snapshot: strong-lead-gate-failed; gate WAJIB dicek ulang bila situs muncul di run berikut (proyek baru 17 menit, situs bisa muncul belakangan).'
}
snap['timestamp_wib']='2026-11-08 run 1601'
snap['last_run_wib']=WIB_NOW
snap['runNote1601_1108']=('Run 1601 (16:01 WIB, selesai ~16:54 WIB): STRONG LEAD BARU - Voltlings (VOLT) 0xB1f4f9c3Bb8533064fFec75dFab1Be88833b3a32 - 3 kaki strong lead terverifikasi (umur first mint 16:32:01 WIB; free 61/111 = 55.0% saat triase, 84/111 = 75.7% saat merge; slot user terbuka + Agent ID dipegang) TAPI GATE WEBSITE GAGAL (metode A-N, termasuk BscScan live: tanpa website/sosial/Token Info) -> TIDAK di-preview/TIDAK di-mint, dilaporkan sekali sebagai strong lead + alasan penghambat. '
 'Scan 132368443-132369442 (1000 blok, cap; gap terlewat 132361946-132368442, 6497 blok; backfill off): PARTIAL - chunks 20/20, enrichment STALL 93/97, di-kill 16:46:30 WIB; 92/97 ter-enrich, ERC20 lengkap (358), 40 panggilan Ankr, 0 error. Watermark TIDAK dimajukan (tetap 132361945). First-seen 34 (31 re-find scan historis -> AGE-EXCLUDED; 3 benar-benar baru: Voltlings, Drift Sigil PAID-ONLY, TIGENT bukan agent-shaped). Seen 252->286. 5c: 42 ERC-20 mint_count>=10, 5 baru dicek, 0 hit S1/S2; track-c-scan-checked 1501->1506. '
 'Re-read blok 132369478: 514/519 kontrak + 71/71 track-C; 256 berubah; velocity pass 4 (Gourdmare same-owner discard; bridge-0x6eee + Zhenzhu artefak ERC-20; Ink Koi slot user sudah terpakai) - tidak ada promosi. Sellout baru: 0 (65 flag = sudah sold out di 1331/1401). Slot user berubah: 0. Gate-failed strong leads (Jinli/Dafeiyu/Chiphiveowl/Farmbuxiang) tanpa perubahan material. Paw Gang: totalMinted 2477->2896 (+419), fase 4 PoW, tetap diblokir. Track-B binanceai: tetap refund phase (launched 0, failed 1, isRefundPhase 1). '
 'NJAR: sale CLOSED pasca-deadline (live=0, tradingOpen 0->1, umur ~72 jam) -> dihapus dari track_c. 9 age-excluded dihapus dari snapshot (lihat runNote1601_1108_age_exclusions). '
 'Boltbook EN+ZH: tanpa lead proyek baru (hanya ORBITA 4 shares left - sudah di track_c; Dafeiyu tanpa perubahan). Sourcify feed 20 entri: 17 paid-only factory wave (mint+quote, tanpa free view) + Voltlings. Route 3/6: tanpa lead baru (HOPKIN sudah age-excluded + gate-failed). Bridge: tidak berubah sejak 2026-11-06 (115 kontrak; 33 belum di snapshot, semua first-seen 2026-11-03..06, age-excluded).')
snap['runNote1601_1108_age_exclusions']=('Age-excluded run 1601 (launch TERVERIFIKASI >48 jam, belum sold out -> DIHAPUS dari snapshot):\n'
 'Agent Wallet 0x1aeEf8218815F7639eA3544D5c57122675A00805: first mint 2026-11-05 21:56:35 WIB (blok 131836550), umur ~67 jam; nextTokenId()=25 (naik dari 11), tanpa MAX cap di ABI, mint gratis nonpayable masih terbuka - BUKAN sold out.\n'
 'AgentX 0x59D96D8B4B82Abb350868E897F25F8e021360823: first mint 2026-11-06 01:21:38 WIB (blok 131864930), umur ~63 jam; totalSupply 1984/2500 - BUKAN sold out.\n'
 'HI-SCORE 0xA74081fd9bc9623A2d9321223C35b41016A7fd65: first mint 2026-11-06 01:08:42 WIB (blok 131865618), umur ~64 jam; totalSupply 331 (+1 interval ini, masih minting) - BUKAN sold out.\n'
 'LastCall 0x6aBC7d97ab07bBA5d5efa6a9eD58ec3CA3892305: first mint 2026-11-06 02:04:23 WIB (blok 131869584), umur ~63 jam; totalMinted 298/10000 - BUKAN sold out.\n'
 'CantonTron 0x921150815bF267a17bb372E44e6e3f44a05f54af: first mint 2026-11-06 09:50:40 WIB (blok 131931747), umur ~55 jam; totalMinted 968/3333 - BUKAN sold out. Juga dihapus dari track_c.\n'
 'AgentB-c047 0xc047F826E9E53D853c5683290EE50B6F02496529: first mint 2026-11-06 14:03:03 WIB (blok ~131965391), umur ~51 jam; totalMinted 902/10000 - BUKAN sold out.\n'
 'AgentB-06ec 0x06ecAE09523DA3698640728cc205305df5C33988: first mint 2026-11-06 14:24:06 WIB (blok ~131968198), umur ~50 jam; totalMinted 898/10000 - BUKAN sold out.\n'
 'AgentPad Agent 0x71f86082C3b32601f865c63980a9B686e887EAB1: first mint 2026-11-06 15:27:20 WIB (blok 131976627), umur ~49 jam; totalMinted 169/10000 - BUKAN sold out.\n'
 'Muster 0x74a7c48e18ac557bdbb43c2e4d0e3820dff3eb77: first mint 2026-11-06 15:04:44 WIB (blok 131973615), umur ~50 jam; totalMinted 1/888 - BUKAN sold out.')
snap['runNote1601_1108_scan']=('Scan run 1601: pre-flight LULUS 7,3 dtk (head 132369401, 50 blok, 1000 logs=pageSize cap). Window 132368443-132369442 (1000 blok, cap), 20/20 chunk + 92/97 enrich, 40 panggilan Ankr, 0 error, partial=true (STALL enrichment 93/97 ERC1155 0xb27B78C82502fEBe169e557ff2345675FdCB2b35, tanpa output 09:43:04-09:46:30 UTC, di-kill manual 16:46:30 WIB; 5 kontrak tak ter-enrich, 4 tak teridentifikasi, akan ter-scan ulang karena watermark tidak maju). 97 NFT + 358 ERC-20 mint. HIVE Agents tidak ada di window. First-seen per seen+snapshot: 34 (31 re-find scan historis -> AGE-EXCLUDED: Vesperfang/Arachnoir/Gourdmare minting sejak 2026-11-02, ~6 hari; 3 benar-benar baru: Voltlings, Drift Sigil PAID-ONLY, TIGENT bukan agent-shaped). Watermark 132361945 TIDAK dimajukan; skipped gap 132361946-132368442 (6497 blok, backfill off). Track-C 5c: 42 ERC-20 mint_count>=10, 5 baru dicek (cap 20), 0 hit S1/S2; track-c-scan-checked 1501->1506. Seen 252->286.')
snap['runNote1601_1108_njar']=('NJAR 0x816458b734d17d59058762deaadd9b952bad6985 (token 0x0b0b8df4d7df0b2cdd00877b476a447a8a1824ee): fillDeadline 2026-11-08 16:00:37 WIB LEWAT; live()=0 - sale CLOSED; giftsClaimed 836/2000 (was 569); paidSharesSold 6 (was 3); token tradingOpen() 0->1 (kini transferable); saleStart 2026-11-05 16:00:37 WIB (umur ~72 jam >48 jam); user balance 0, tidak pernah klaim. DIHAPUS dari track_c run 1601 (age-excluded + sale closed).')
json.dump(snap, open(S,'w'), indent=1, ensure_ascii=False)
print('snapshot saved: contracts', len(snap['contracts']), '| track_c', len(snap['track_c']))
print('Voltlings in snapshot:', 'Voltlings' in snap['contracts'])
for n in removed:
    print('removed check:', n, n in snap['contracts'])
print('NJAR in track_c:', 'NJAR' in snap['track_c'], '| CantonTron in track_c:', 'CantonTron' in snap['track_c'])
