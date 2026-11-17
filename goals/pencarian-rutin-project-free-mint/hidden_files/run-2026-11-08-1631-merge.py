import json
S='onchain-snapshot.json'
snap=json.load(open(S))
reread=json.load(open('run-2026-11-08-1631-reread.json'))
tc_reread=reread['track_c']
HEAD=132373045
WIB_REREAD='2026-11-08 17:02 WIB'
WIB_NOW='2026-11-08 17:40 WIB'
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
 'Ink Koi': 'Run 1631: velocity PASS (+47, 5.89x) free% VERIFIED 63.6% (1767/2777), umur ~23.9h - TAPI slot user SUDAH terpakai (freeClaimed(user)=1, balance 1 sejak run 0831) - BUKAN kandidat/strong lead, tidak promosi.',
 'Gourdmare': 'Run 1631: velocity PASS (+26, 34.8x) free% 59.2% - TAPI status promotion-discarded-same-owner-2026-11-03 - TIDAK PERNAH dipromosikan/dilaporkan.',
 'HIVE Agents': 'Run 1631: totalSupply flat 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan.',
 'Paw Gang': 'Run 1631 (read-only): totalMinted 2896->3002 (+106), mintOpen 1, balance 0; PoW tetap memblokir (tidak dicoba ulang di VM).',
 'Jinli Agents': 'Run 1631: 273->277 (+4), free% 30.9%, slot terbuka, gate website tetap GAGAL (tidak berubah) - tidak di-mint, tidak dilaporkan ulang.',
 'Dafeiyu': 'Run 1631: 666 (0), free% UNVERIFIED, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Chiphiveowl': 'Run 1631: 582->584 (+2), free% 72.4%, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
 'Farmbuxiang': 'Run 1631: 480 (0), free% 68.4%, slot terbuka, gate website tetap GAGAL - tidak di-mint, tidak dilaporkan ulang.',
}
for name, note in notes.items():
    if name in contracts:
        contracts[name]['runNote1631_1108']=note
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
# --- REMOVE Voltlings (sold out) ---
volt_removed=None
if 'Voltlings' in contracts:
    volt_removed='freeMinted 84/111 (run 1601) -> 111/111 (run 1631, blok 132373045): free pool HABIS, totalSupply 111. Strong lead gate-failed run 1601, user tidak sempat mint (gate website gagal, tidak pernah di-preview). Status terminal sold-out; dihapus dari snapshot run 1631, dilaporkan sekali.'
    contracts.pop('Voltlings', None)
print('Voltlings removed:', volt_removed is not None)
# --- ORBITA sold out note (keep entry: minted-by-user record) ---
if 'ORBITA' in tc:
    tc['ORBITA']['totalSupply']=1000000000000000000000000000
    tc['ORBITA']['runNote1631_1108']='Run 1631: totalSupply 997e24 -> 1000e24 = 1.000/1.000 share - free pool HABIS (sold out), konsisten post Boltbook. Status minted-by-user-2026-11-07 (terminal): user sudah memegang 1 share gratis (balanceOf 1e24 = 1.000.000 ORBITA, tidak berubah). Entri dipertahankan sebagai catatan mint user.'
    print('ORBITA noted sold out')
# --- ADD Oddlode Drills (minted-by-user) ---
contracts['Oddlode Drills']={
 "address": "0xce18531F9F639ca2351CA15FB2032D925b917472",
 "status": "minted-by-user-2026-11-08",
 "name": "Oddlode Drills",
 "symbol": "DRILL",
 "kind": "ERC721",
 "totalSupply": 824,
 "totalMinted": 824,
 "freeClaimed": None,
 "freeMinted": 824,
 "FREE_SUPPLY": 1000,
 "MAX_SUPPLY": 5000,
 "mintOpen": 1,
 "balanceOf_user": 1,
 "freeClaimed_user": 1,
 "freePctVerified": 82.4,
 "firstMintWib": "2026-11-08 16:59:25 WIB",
 "firstMintBlock": 132372757,
 "mintOpenTime": 1794131952,
 "owner": "0x615c47be32512f42ff3b8cd1f5f688e93fe3a929",
 "website": "https://oddlode.space",
 "gate": "PASS run 1631 - (H) contractURI https://oddlode.space/nft/contract.json (external_link https://oddlode.space) + (G) /skill.md mencetak kontrak persis Drills 0xce18... + Mine + ODLE + pair + registry 0x60B926...22F; mendokumentasikan mintFree() value 0, .ai Agent ID wajib, sekali per wallet, 1000 total.",
 "mintTx": "0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a",
 "mintBlock": 132376388,
 "mintedTokenId": 814,
 "mintGas": 209498,
 "runNote1631_1108": "STRONG LEAD run 1631 -> MINTED BY USER (strong-lead direct mint). 3 kaki terverifikasi: umur first mint 16:59:25 WIB (blok 132372757, mintOpenTime 16:59:12 WIB); free 570/1000 = 57.0% saat triase, 778/1000 = 77.8% saat verifikasi segar parent (~17:27 WIB), 824/1000 saat verifikasi pasca-mint; slot user TERBUKA (freeClaimed(user)=0, balanceOf=0, isAgent(user)=1). Gate website LOLOS (lihat field gate). Audit Binance saat mint: hasResult=false (TIDAK ADA HASIL, bukan lolos), isSupported=true, riskLevel -1, tanpa RISK hit. Preview bersih 000000000 (+1 ERC721 #814, tanpa authority/allowance/risk, value 0). Eksekusi: mintFree() value 0, tx 0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a, blok 132376388, receipt 1, gas 209498; balanceOf 0->1, freeClaimed(user) 0->1, freeMinted 778->824, ownerOf(814) = wallet agent. Post-mint: rarity Type Free / Level 1 / Power 8 (metadata https://oddlode.space/meta/814 + drillInfo on-chain cocok); marketplace own = kontrak Drills sendiri (list/buy, fee 3%) TAPI free drill TIDAK BISA di-list (list hanya untuk paid drills) dan paidMinted masih 0 -> 0 live listings (sampel 6 token: 0 live) - TIDAK di-list (aturan auto-list: tanpa own market live / floor live -> tidak listing). Utilitas: place di Mine untuk mining ODLE/BNB per ronde 4 jam."
}
print('Oddlode added as minted-by-user')
# --- ADD Kiko9393 to track_c (watchlist-only, age unverified) ---
tc['Kiko9393']={
 "sale": "0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf",
 "token": "0x37266a6d1310bb1579c3721061b5366168602560",
 "status": "watchlist-only-age-unverified-2026-11-08",
 "saleShape": "S1 PASS (mint(uint256,address) + quote(uint256) + freeAvailable/freeClaimed/freeMinted + agentId() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis, Sourcify verified)",
 "tokenName": "Kiko9393",
 "tokenSymbol": "KIKO9393",
 "MAX_FREE": 560,
 "MAX_SHARES": 800,
 "freeMinted": 0,
 "sharesMinted": 0,
 "PRICE": 500000000000000000,
 "TOKENS_PER_SHARE": 1000000000000000000000000,
 "deployedAtWib": "2026-11-08 16:49:52 WIB",
 "freeAvailable_user": True,
 "freeClaimed_user": False,
 "hasAgentId_user": True,
 "claimable_user": 0,
 "ageNote": "UNVERIFIED: sharesMinted=0, freeMinted=0 - belum ada satu pun mint sejak deploy 16:49:52 WIB; pembukaan sale belum terkoroborasi mint pertama; waktu deploy saja BUKAN launch time. BUKAN lead, TIDAK di-preview/TIDAK di-mint. Website proyek belum ditemukan (gate akan gagal bila dicek).",
 "source": "Sourcify recently-verified feed run 1631 (verifiedAt 2026-11-08T09:51:26Z) + verifikasi on-chain parent",
 "lastReadWib": "2026-11-08 17:05 WIB"
}
print('Kiko9393 added to track_c watchlist-only')
# --- run notes ---
snap['runNote1631_1108']="Run 1631 (16:31 WIB, selesai ~17:40 WIB): STRONG LEAD BARU Oddlode Drills (DRILL) 0xce18531F9F639ca2351CA15FB2032D925b917472 -> MINTED BY USER via strong-lead direct mint (lihat entri 'Oddlode Drills'): tx 0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a, blok 132376388, token #814, receipt 1, gas 209498; gate website LOLOS (oddlode.space/skill.md mencetak kontrak persis); audit Binance hasResult=false (tanpa hasil, bukan lolos); preview bersih 000000000. Voltlings SOLD OUT (freeMinted 111/111) -> dihapus dari snapshot, dilaporkan sekali. ORBITA sold out (1.000/1.000 share), user sudah pegang 1 share - entri dipertahankan. Kiko9393 (sale 0x34aE86...) masuk track_c watchlist-only (umur unverified, 0 mint). Scan route 4 PENUH (window 132372210-132373209, 176 NFT/847 mint, 329 ERC20, 40 Ankr calls, 0 error, partial=false); watermark 132361945 -> 132373209; skipped gap 132361946-132372209 (10.264 blok, backfill off). First-seen 3: Oddlode (strong lead), DIVIDEND re-find same-owner-discarded, Chipmunks re-find bukan agent-shaped. 5c: 6 baru dicek, 0 hit. Re-read blok 132373045: 506/511 kontrak + 69/85 track_c; velocity pass 3 (Ink Koi slot terpakai, Gourdmare same-owner, Zhenzhu artefak) - tanpa promosi; 0 perubahan slot user; 0 kandidat age-exclusion; binanceai tetap refund phase. Boltbook EN+ZH: tanpa proyek baru (ORBITA track_c; Zigzoo PAID-ONLY; Ringhelm/0xef870a age-excluded; BRE/BADGE di luar scope). Feed Sourcify 20 item: hanya Kiko9393 lolos bentuk sale. Rute 3: hanya item lama. Rute 6: Odaily/PANews/DappBay 0 sebutan. Bridge: tidak berubah sejak 2026-11-06."
snap['runNote1631_1108_scan']="Scan run 1631: pre-flight LULUS 1,2 dtk; window 132372210-132373209 (head 132373209, 17:02:45 WIB); 20/20 chunk, 0 error, 40 Ankr calls; 176 NFT / 847 mint / 329 ERC20-mint; HIVE tidak di window; watermark -> 132373209; skipped gap 132361946-132372209 (10.264 blok). First-seen 3 (Oddlode strong lead; DIVIDEND same-owner re-find; Chipmunks bukan agent-shaped re-find). Seen 11.488 -> 11.491 kunci. 5c: 50 ERC20 mint_count>=10, 6 baru dicek, 0 hit S1/S2; track-c-scan-checked 1507 -> 1513."
snap['last_run']='free-mint-search 2026-11-08 1631 WIB'
snap['last_run_wib']='2026-11-08 17:40 WIB'
json.dump(snap, open(S,'w'), indent=1)
print('contracts now:', len(snap['contracts']), 'track_c now:', len(snap['track_c']))
print('DONE')
