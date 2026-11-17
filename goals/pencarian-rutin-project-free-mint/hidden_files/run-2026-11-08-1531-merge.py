import json, copy
S='onchain-snapshot.json'
snap=json.load(open(S))
reread=json.load(open('run-2026-11-08-1531-reread.json'))
tc_reread=reread['track_c']
analysis=json.load(open('run-2026-11-08-1531-analysis.json'))
HEAD=132367660  # receipt block of 402 mint
WIB='2026-11-08 16:45 WIB'
contracts=snap['contracts']
updated=0; skipped_none=0
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
    e['lastReadWib']='2026-11-08 15:43 WIB'
    if changed: updated+=1
print('contracts updated (numeric change):', updated, 'of', len(reread['reread']))
# per-contract run notes for notable items
notes={
 'Undead NFTs': 'Run 1531: velocity PASS (+43, 4.45x) tapi free% UNVERIFIED (freeMinted 196, tanpa FREE_SUPPLY) - tetap watchlist-only, BUKAN strong lead.',
 '0xAAEF5BB8A7363B5997F17149d554640DC35f306d': 'Run 1531: velocity PASS (+37, 6.70x) tapi free% UNVERIFIED - tetap watchlist-only.',
 'Un-Written': 'Run 1531: velocity PASS (+25, 2.15x) tapi free% UNVERIFIED - tetap watchlist-only.',
 'WHALE-B': 'Run 1531: velocity PASS (+22, 17.04x) tapi free% UNVERIFIED - tetap watchlist-only.',
 'Jinli Agents': 'Run 1531: +5 mint (free 30.29%), balance 0, slot terbuka, gate website tetap GAGAL (tidak berubah) - tidak di-mint, tidak dilaporkan ulang.',
 'Dafeiyu': 'Run 1531: +13 mint, free% null, balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Chiphiveowl': 'Run 1531: +20 mint (free 71.12%), balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Farmbuxiang': 'Run 1531: +5 mint (free 68.14%), balance 0, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Paw Gang': 'Run 1531 (read-only): totalMinted 2296->2477 (+181), mintOpen 1, balance 0; totalSupply null (degradasi RPC, bukan nol); PoW 30-bit tetap memblokir (tidak dicoba ulang di VM).',
 'CAISHEN': 'Run 1531: free 211/888 = 23.76% (di bawah 25% strong), 0 mint interval ini - early lead, belum promosi.',
 'Alchemister-0xCafEEDDF': 'Run 1531: +14 mint, free% null, first mint 2026-11-07 09:49 WIB (~29.7 jam; age-exclude ~2026-11-09 09:49 WIB bila belum sold out).',
 'Agent Goats': 'Run 1531: free 737/1111 = 66.34%, +3 mint, umur UNVERIFIED - tetap watchlist-only.',
}
for name, note in notes.items():
    if name in contracts:
        contracts[name]['runNote1531']=note
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
malta=tc.get('AGENT MALTA')
if malta:
    malta['runNote1531']='Run 1531: token totalSupply 559.8e24 -> 628.2e24 wei (+~68.4 share @ TOKENS_PER_SHARE 1e24), balanceOf(user) 0; free pool tersisa tidak terbaca (kontrak pakai freeUsed, bukan di TC views); MAX_SHARES 100000 jauh dari habis; gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.'
njar=tc.get('NJAR')
if njar:
    njar['runNote1531']='Run 1531: semua TC views null (kontrak pakai giftsClaimed/GIFT_SHARES); fillDeadline 2026-11-08 16:00:37 WIB SUDAH LEWAT saat run ini (16:45 WIB) - status pasca-deadline belum diverifikasi, perlu re-check run berikut.'
# add 402 minted-by-user
contracts['402']={
 'address':'0xd80D0095746999c93AE837B1DE1569d5814405dC',
 'status':'minted-by-user-2026-11-08-1531',
 'name':'402','symbol':'402','kind':'ERC721',
 'totalSupply':177,'totalMinted':177,'freeClaimed':None,'freeMinted':177,
 'FREE_CAP':402,'FREE_PER_WALLET':1,'MAX_SUPPLY':4020,'PRICE':42000000000000,
 'mintOpen':1,'balanceOf_user':1,'freeCount_user':1,'tokenIdMinted':174,
 'firstMintWib':'2026-11-08 15:24:48 WIB','firstMintBlock':132360150,
 'source':'On-chain scan run 1531 window 132360946-132361945 + walk-back Ankr (0 mint sebelum 132340000) + Sourcify verifiedAt 2026-11-08T08:25:26Z + tidak ada di 274 scan output historis',
 'website':'https://402-mint.netlify.app',
 'runNote1531':'STRONG LEAD run 1531 -> MINTED. Umur TERVERIFIKASI (first mint 15:24:48 WIB, ~69 mnt saat eksekusi), free 172/402 = 42.79% saat eksekusi, slot user terbuka (freeCount=0). Gate website LOLOS via tokenURI/metode I: tokenURI(1)=402-mint.netlify.app/metadata/metadata.json, external_url situs, situs mencetak kontrak persis + registry persis; agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (exact); Sourcify exact_match. Audit Binance: hasResult=false (TANPA HASIL, bukan lolos), riskLevel -1/LOW, tanpa RISK hit. Preview BERSIH 000000000 (+1 ERC721, tanpa authority/allowance/risk). Eksekusi freeMint(1) value 0: tx 0xadf21f79ac6ec04d018c62b5d8bfec85e13c0ebfa748e5a4a8fa2bc79bc903f5, block 132367660, receipt status 1, gas 113390 (~0.00000794 BNB), token #174, ownerOf(174)=wallet agent, freeCount(user) 0->1, freeMinted 172->177. Post-mint: TIDAK ada own market (situs hanya halaman mint, menyebut Element generik) + TIDAK ada floor live terverifikasi di Element -> TIDAK di-list. Rarity: tier NOT verified (semua token berbagi satu metadata generik tanpa traits).'
}
# add Kitebots watchlist-only
contracts['Kitebots']={
 'address':'0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0',
 'status':'watchlist-only-age-unverified',
 'name':'Kitebots','symbol':'KITE','kind':'ERC721',
 'totalSupply':904,'MAX_SUPPLY':4000,'PRICE':500000000000000,
 'freeClaimed':None,'freeMinted':None,'FREE_SUPPLY':None,'mintOpen':None,
 'balanceOf_user':None,'freeClaimed_user':None,
 'source':'On-chain scan run 1531 (re-find: pertama terlihat di scan 0001 hari ini; first mint SEBENARNYA belum terverifikasi)',
 'runNote1531':'Re-find run 1531: agent-shaped (FREE_CAP/FREE_PCT/canFreeMint/freeMint/freeMinted, registry bytes, Sourcify verified) tapi free% UNVERIFIED (freeClaimed/freeLeft revert) dan umur peluncuran UNVERIFIED - watchlist-only, BUKAN early lead (first mint tidak terverifikasi di run ini), TIDAK di-preview/di-mint, TIDAK dilaporkan.'
}
snap['timestamp_wib']='2026-11-08 run 1531'
snap['last_run_wib']='2026-11-08 16:45 WIB'
snap['runNote1531']=('Run 1531 (15:31 WIB): MINT BERHASIL - 402 #174 via strong-lead direct mint (gate website LOLOS, audit hasResult=false tanpa RISK hit, preview bersih, free 172/402 saat eksekusi). '
 'Scan 132360946-132361945 (1000 blok, cap; gap terlewat 132356528-132360899, 4372 blok), 145 NFT + 366 ERC-20, 44 first-seen (22 baru + 22 re-find). '
 'KOREKSI PENTING: 2 dari 3 strong lead scan ternyata AGE-EXCLUDED - Macronyx (first mint 2026-11-03, 17 mint di scan 1131) dan Mindrift (first mint 2026-11-03, 13 mint di scan 1131); '
 'Lucky Box BUKAN early lead baru (track_c gate-blocked sejak 2026-11-05, first mint 2026-11-05, umur ~72 jam); 5 re-find (Plutofarm/Servofarmix/Ringgent 2026-11-04, Mercurito 2026-11-02, Pilotdragon 2026-11-04) juga age-excluded. '
 'Semua itu TIDAK dilaporkan sebagai lead dan TIDAK ditambah ke snapshot (preseden PassAgentX); seen file sudah mencatatnya (208->252) sehingga scan berikut tidak mengulang. '
 'Track-C 5c: 13 dicek, 0 hit. Velocity pass 5 (semua free% UNVERIFIED, tidak promosi). Sellout baru: 0 (65 flag mentah = sudah sold out di 1331/1401, koreksi tercatat). '
 'Gate-failed strong leads (Jinli/Dafeiyu/Chiphiveowl/Farmbuxiang) tanpa perubahan material. Paw Gang: +181 mint, PoW tetap memblokir. Track-B binanceai: tetap refund phase. '
 'Boltbook/Sourcify feed/sweep/route-6: tidak ada lead baru. NJAR fillDeadline 16:00:37 WIB sudah lewat (status pasca-deadline belum diverifikasi).')
snap['runNote1531_age_exclusions']=('Macronyx 0x2E7Aa64BAc710082bb0E84F4BEb7C0cF668CfC29: first mint 2026-11-03 (17 mint, scan 2026-11-03-1131, blok 131367893; juga 2026-11-04-1031) - umur ~5 hari >48 jam, AGE-EXCLUDED, bukan strong lead. '
 'Mindrift 0xD09052d690151702759481Bbcb0eB5Dbdc5f1eAA: first mint 2026-11-03 (13 mint, scan 2026-11-03-1131, blok 131368730) - umur ~5 hari, AGE-EXCLUDED. '
 'Lucky Box 0xd08ef372B52C29255fEd7004f59bF41571451894: first mint 2026-11-05 15:59:44 WIB (track_c, hot-leg 1601) - umur ~72 jam, AGE-EXCLUDED, bukan early lead baru. '
 'Plutofarm 0xdB101245A380C54E9CE5508359B1350F5fc31289 / Servofarmix 0xf63623136e5f2a6CD8cE85d9F22Ac46744DF39b6 / Ringgent 0xf1d1650dBfeB0FA8082481C8213ACCD59af3cF4A: first mint 2026-11-04 - AGE-EXCLUDED. '
 'Mercurito 0x664e9E0EEfF9e95b966C8a314B8BdDb844E65054: first mint 2026-11-02 - AGE-EXCLUDED. Pilotdragon 0x2e93D009...: first mint 2026-11-04 - AGE-EXCLUDED. '
 'Pelajaran: walk-back Ankr dari blok 132340000 saja TIDAK cukup untuk verifikasi umur - wajib cross-check scan output historis + Sourcify verifiedAt sebelum klaim first mint.')
json.dump(snap, open(S,'w'), indent=1, ensure_ascii=False)
print('snapshot saved: contracts', len(snap['contracts']), '| track_c', len(snap['track_c']))
