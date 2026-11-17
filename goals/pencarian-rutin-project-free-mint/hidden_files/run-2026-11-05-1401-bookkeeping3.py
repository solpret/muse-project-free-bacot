#!/usr/bin/env python3
"""Run 1401 stage-3 bookkeeping (final): add Neurolucha as gate-blocked strong lead.
Gate outcome: FAILED - no verified website via methods (A)-(N); (L) BscScan live
browser read 2026-11-05 ~14:29 WIB found NO website/social field and source NOT
verified on BscScan (Sourcify verified separately). No preview, no mint."""
import json, shutil

D = '/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/'
shutil.copy(D + 'onchain-snapshot.json', D + 'onchain-snapshot-1401-stage3.bak.json')
snap = json.load(open(D + 'onchain-snapshot.json'))
verify = json.load(open(D + 'run-2026-11-05-1401-verify-new.json'))
v = verify['Neurolucha']

entry = {
    'address': '0x56eBED63452Bb02B975ceE02949DA3C02466725b',
    'name': 'Neurolucha',
    'symbol': 'NLUCHA',
    'kind': 'ERC721',
    'totalSupply': 335,
    'freeMinted': 335,
    'FREE_CAP': 800,
    'MAX_SUPPLY': 4000,
    'freePctVerified': 41.88,
    'balanceOf(user)': 0,
    'claimedFree(user)': 0,
    'canFreeMint(user)': 1,
    'paidMinted': 0,
    'mintOpen': 'revert-on-read',
    'owner': 'revert-on-read',
    'firstMintBlock': 131755452,
    'firstMintTx': '0xe11fabf40854b6bd593d4d9a418699553cfd5002a1433efb9103803898642b29',
    'firstMintWib': '2026-11-05T11:48:07+07:00',
    'firstSeenBlock': 131771337,
    'scanMints': 2,
    'scanMinters': 2,
    'scanWindow': '131771337-131773336',
    'status': 'strong-lead-gate-blocked-2026-11-05',
    'launchNote': 'First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero): blok 131755452 = 2026-11-05 11:48:07 WIB; umur TERVERIFIKASI ~3 jam saat run (<=48 jam).',
    'baselineNote': ('STRONG LEAD dilaporkan run 1401 TAPI GATE-BLOCKED: free 335/800 = 41,88% (>=25%), umur terverifikasi <=48 jam, '
                     'slot user terbuka (claimedFree=0, canFreeMint=1). TIDAK di-preview/TIDAK di-mint karena gate website GAGAL.'),
    'gateNote': ('Gate website GAGAL run 1401, metode (A)-(N) semua dicoba: (A) pencarian alamat mentah nihil; (B) grep Boltbook EN/ZH hari ini nihil; '
                 '(C) metadata Sourcify tanpa URL http (compiler 0.8.26); (D) pola situs keluarga tidak ditemukan; (E) owner() revert - grup deployer tidak bisa ditetapkan; '
                 '(F) N/A - tidak ada handle untuk dikonfirmasi; (G) pencarian nama "Neurolucha" nihil; (H) contractURI() revert; '
                 '(I) tokenURI(1) base64 JSON tanpa external_url/http ("Masked AI wrestler... Fully on-chain art"); (J) ABI 40 fungsi, tidak ada fungsi situs; '
                 '(K) pencarian indeks GitHub nihil (pencarian kode asli butuh auth - keterbatasan dicatat); '
                 '(L) BscScan via live browser ~14:29 WIB: halaman token terbaca penuh - MAX TOTAL SUPPLY 335, HOLDERS 335, TRANSFERS 336, reputasi UNKNOWN, '
                 'TIDAK ADA kolom Website/Social (hanya "Click here to update the token information"), source TIDAK terverifikasi di BscScan '
                 '(terverifikasi di Sourcify secara terpisah - nuansa dicatat); (M) filter site: vercel/pages/surge/deed tanpa hasil; '
                 '(N) tidak ada post Boltbook yang menyebut Neurolucha sehingga hop author-bio tidak bisa dibangun. X UNVERIFIED.'),
    'lastReadBlock': 131777112,
    'lastReadWib': '2026-11-05 run 1401',
    'velocityVerified': False,
    'xVerified': False,
}
snap['contracts']['Neurolucha'] = entry
snap['runNote1401'] = ('Run 1401 (2026-11-05 14:01 WIB): 8 lead baru dari scan on-chain (jendela 131771337-131773336, cap 2000, gap 131769376-131771336 dilewati). '
    '1 STRONG LEAD gate-blocked: Neurolucha (NLUCHA) 335/800 = 41,88%, umur ~3 jam, slot terbuka - gate website GAGAL (A)-(N), TIDAK di-preview/di-mint. '
    '7 EARLY lead: Roguefall 9,4%, Agent Goats 9,72%, Agent Owls 9,36%, Hirelings-A 5,75%, Hirelings-B 4,25%, Forklings 6,25%, Auspibots 6,45% - semua website/X unverified. '
    'Robogent AGE-EXCLUDED (first mint 2026-11-03 12:20:32 WIB, umur ~49,7 jam >48 jam, belum sold out). Jolly tetap gate-blocked (umur ~38,6 jam, velocity FAIL). '
    'AFROG tetap watchlist-only (28,35% tapi umur unverified). Track-C 5c: 8 kontrak baru di-shape-check, 0 lolos. Bridge: tidak berubah (113 kontrak). '
    'Scan: 239 NFT + 559 ERC-20 mint contracts, 80 panggilan Ankr, 0 error. Gap scan 131769376-131771336 tidak tercakup.')
snap['last_run_wib'] = '2026-11-05 run 1401'
snap['last_run_note'] = snap['runNote1401']
json.dump(snap, open(D + 'onchain-snapshot.json', 'w'), indent=1)
print('Neurolucha added as', entry['status'])
print('contracts now:', len(snap['contracts']))
print('OK stage-3 done')
