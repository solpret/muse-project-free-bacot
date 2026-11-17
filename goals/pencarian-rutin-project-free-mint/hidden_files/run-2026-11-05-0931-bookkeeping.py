import json, os
base = os.path.expanduser('~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files')
snap = json.load(open(f'{base}/onchain-snapshot.json'))
C = snap['contracts']
# --- re-read updates (block 131737367; early probe block later, RigOrb 349) ---
def upd(key, **kw):
    if key in C and isinstance(C[key], dict):
        C[key].update(kw)
upd('HIVE Agents', totalSupply=1240, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('Blobbies-a7fB', totalSupply=1325, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('SoulAgent', totalSupply=594, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('PERSONA-A930', totalSupply=1093, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('Robogent', totalSupply=1198, freeClaimed=1194, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('Jolly', totalMinted=3315, freeMinted=3315, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('StarAgent-7d39', totalSupply=869, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
upd('Cogito-COG-A', totalSupply=4675, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737744,
    note='Boltbook.fun post 09:15 WIB recheck (Limitless/Cogito/SEAT) + fresh read run 0931: totalSupply 4543->4675, mintedBy(user)=0, balanceOf(user)=0; free views revert, Sourcify 404, age/website unverified; NOT a lead, NOT promoted.')
# AFROG key: find by address
for k, v in C.items():
    if isinstance(v, dict) and v.get('address', '').lower() == '0x4fea4ed6e70389245c41b2c9d85e8032e3c6ce31':
        v.update(totalSupply=198, freeClaimed=198, lastReadWib='2026-11-05 run 0931', lastReadBlock=131737367)
# --- new entries ---
C['DYOR-8695'] = {
    'address': '0x86956Bc830EB62110820Ae79164BeF61c7E31936', 'name': 'DYOR', 'symbol': 'DYOR', 'kind': 'ERC721',
    'status': 'early-lead-reported-2026-11-05', 'tier': 'EARLY',
    'totalSupply': 117, 'MAX_SUPPLY': 11111, 'mintOpen': 1, 'userBalance': 0,
    'owner': '0xc94feb34f9508ee165818e8a402d9dc8423c0d05',
    'agentIdRegistry': '0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F',
    'firstSeenBlock': 131732800, 'scanWindow': '131731302-131733301', 'scanMints': 2, 'scanMinters': 1,
    'lastReadBlock': 131737744, 'lastReadWib': '2026-11-05 run 0931',
    'note': 'EARLY run 0931: first-seen in scan window 0901 (2 mints/1 minter), agent-shaped on-chain via agentRegistry()==registry; Sourcify feed exact_match 2026-11-05T01:43:33Z (direct ABI fetch 404 run ini, transport, bukan vonis); free views revert -> % gratis/slot user UNVERIFIED; age/website UNVERIFIED; NEVER preview/mint as early.'}
C['PixelLaptop-273f'] = {
    'address': '0x273fc2c7705b23eb129e35ac8da26348e6fc4980', 'name': 'Pixel Laptop', 'symbol': 'PLAPTOP', 'kind': 'ERC721',
    'status': 'early-lead-reported-2026-11-05', 'tier': 'EARLY',
    'totalSupply': 453, 'FREE_SUPPLY': 1800, 'MAX_SUPPLY': 3333, 'userBalance': 0,
    'owner': '0x14e75dbd5ffd8c2768bb5561cd50ec2adb025a4a',
    'firstSeenBlock': None, 'boltbookPost': 'Pixel Laptop recheck, front page EN 2026-11-05 (post block 131734675/696: totalSupply 392)',
    'lastReadBlock': 131737744, 'lastReadWib': '2026-11-05 run 0931',
    'note': 'EARLY run 0931 (Boltbook secondary source, first mints verified on-chain in run: 392 at post block -> 453 fresh read): agent-shaped via FREE_SUPPLY constant 1800; Sourcify 404 (not verified); freeClaimed/freeMinted revert -> % gratis UNVERIFIED (453/3333=13,6% adalah % total supply, BUKAN % gratis); slot user UNVERIFIED (freeClaimed(user) transport 403 + claimedFree revert); age/website UNVERIFIED; NEVER preview/mint as early.'}
C['LIMITLESS-c7aa'] = {
    'address': '0xc7aa008c2369ff00322c49d526f33529bb692a86', 'name': 'LIMITLESS', 'kind': 'ERC721',
    'status': 'watchlist-only-boltbookfun-2026-11-05',
    'totalSupply': 3988, 'MAX_SUPPLY': 10000, 'userBalance': 0,
    'owner': '0x6fdd67332aae7d04c2e159f15722f11b1b8b938a',
    'lastReadBlock': 131737744, 'lastReadWib': '2026-11-05 run 0931',
    'note': 'Boltbook.fun post 09:15 WIB recheck + fresh read run 0931: totalSupply 3977(post)->3988; free views + agentRegistry revert, Sourcify 404, quote(user,1) read 0 (fungsi quote tidak teridentifikasi, BUKAN bukti slot gratis); age/website UNVERIFIED; NOT a lead, NOT promoted.'}
C['SEAT-f11e'] = {
    'address': '0xf11e9405b23ca0f53e6135162a85545d780a3737', 'name': 'Agent Arena / SEAT', 'kind': 'ERC721',
    'status': 'watchlist-only-boltbookfun-2026-11-05',
    'totalSupply': 626, 'MAX_SUPPLY': 5000, 'mintOpen': 1,
    'owner': '0x8a4e6a11789507f39898b840b351c9b102e4c3e7',
    'lastReadBlock': 131737744, 'lastReadWib': '2026-11-05 run 0931',
    'note': 'Boltbook.fun post 09:15 WIB recheck + fresh read run 0931: totalSupply 618(post)->626, mintedBy(user)=0; free views + agentRegistry revert, Sourcify transport error (bukan vonis); age/website UNVERIFIED; NOT a lead, NOT promoted.'}
snap['runNote0931'] = ('Re-read blok 131737367: HIVE 1240 flat; Tigora totalMinted 527->543 (+16, <20, velocity GAGAL); BNBRunnerz 2951->2970 (+19, <20, GAGAL); '
    'Shroomies 791->797 (+6); Blobbies 1302->1325 (+23, velocity SAJA lolos: >=20 dan >=1,5x interval +15, TAPI umur/%/website unverified -> BUKAN promosi); '
    'Robogent 1198 flat, freeClaimed 1194 (gate-blocked, tak berubah); Jolly totalMinted 3306->3315 (+9, gate-blocked); HACKED 2912->2948 (+36, minted-by-user); '
    'SoulAgent 574->594 (+20, velocity SAJA lolos: >=20 dan >=1,5x interval +13, TAPI umur/%/website unverified -> tetap EARLY); PERSONA 1087->1093 (+7); '
    'RigOrb 329->347/349 (free views revert, % UNVERIFIED, tetap EARLY); StarAgent 853->869 (+16, velocity pass 0901 hilang); AFROG 177->198, free 198/1111=17,8% (<25%, tetap EARLY). '
    'Early probe: Pulsekeep 212->243 (12,2%<25%), Tensortug 88->96 (4,8%), PassAgentX totalSupply 488->735 (+247, <1,5x interval +187 -> velocity GAGAL; % vs free cap UNVERIFIED), Bathybots 105->111 (5,6%) — semua tetap EARLY. '
    'Track-C: OSK opened 0/totalMinted 2275 flat; NIULAI launched 0/phase 4 (arti enum belum terverifikasi); KillZero launched 0; DROID opened 0/545 flat; IMARS opened 0/free 300/300 habis; ASOC freeClaimed(user) 0/saleEnded 0; '
    'SENBAZURU opened 1/freeClaimed 166->191, hasFreeShare(user)=0, tetap gate-blocked (bukan perubahan tier); FABE launched 0/freeSharesRemaining 2821 (pulih dari gagal transport 0901, nilai sama dengan terakhir diketahui)/user 1; BINANCEAI launched 0/refund+failed (sudah diketahui); QAGENT pool habis 6666/6666. '
    'ShibAgentR2 freeClaimed 86->90 (sisa 410), phase 1, sold 0 — TETAP STOPPED per perintah user 2026-11-05 08:49, TIDAK ada preview/mint.')
snap['runNote0931_scan'] = ('Scan 0901 DIPROSES run ini (selesai, exit 0, 80 panggilan Ankr, 0 error): jendela 131731302-131733301, 303 kontrak NFT/1155, 441 kontrak ERC-20 mint. '
    'Watermark 131726227 -> 131733301; gap 131726228-131731301 dilewati dan dicatat (cap 2000, scan mengambil 2000 blok terbaru saat run 0901). '
    'First-seen sejati 3: DYOR (agent-shaped: agentRegistry()==registry, Sourcify feed exact_match -> EARLY, dilaporkan run ini), V74 + Maverick (bukan agent-shaped: registry revert/Sourcify unverified/error, free views revert -> log-only + seen, BUKAN early). '
    'Route 5c: 68 ERC-20 mint_count>=10, 9 belum terperiksa -> semuanya shape-check: Sourcify 404/transport + free views revert, 0 lolos S1/S2; checked 1723 -> 1732. '
    'Scan baru run 0931 DIMULAI di background (onchain_nft_scan.py --chunk 50 --blocks 2000 --out onchain-scan-2026-11-05-0931.json, log scan-0931.log); pada saat run log ditulis masih berjalan — watermark untuk jendela baru BELUM dimajukan, run berikut wajib memeriksa outputnya dulu.')
snap['timestamp_wib'] = '2026-11-05 run 0931'
snap['last_run_wib'] = '2026-11-05 run 0931'
json.dump(snap, open(f'{base}/onchain-snapshot.json', 'w'), indent=1)
# --- seen ---
seen = json.load(open(f'{base}/onchain-scan-seen.json'))
seen['contracts']['0xc8bb757247ca3d440677950f04bb000360f88138'] = 131732430
seen['contracts']['0x86956bc830eb62110820ae79164be f61c7e31936'.replace(' ', '')] = 131732800
seen['contracts']['0x5bf37927ea62b0ab11c64e20d215e39a38c21193'] = 131731826
seen['_meta']['last_scan_wib'] = '2026-11-05 run 0931'
seen['_meta']['last_scan_window'] = '131731302-131733301'
json.dump(seen, open(f'{base}/onchain-scan-seen.json', 'w'), indent=1)
# --- track-c checked ---
chk = json.load(open(f'{base}/track-c-scan-checked.json'))
for a in ['0x3e613baCd4A9b7E5398FA8fFe856AA1e27a3A66A', '0x7233a7c50dfD20758223451a1e7b496B7E2Fd639', '0xe073791b476728A85899f2A9626A906fd7c32cc1', '0xfC310CFC3827920A006C9Ca1E98b5090A203fbb4', '0x0c84aED253EaaB9b7263665D7e213B7aEC718f23', '0x832cc56b564663045609423a063a3d7dEbDCfEdc', '0x9E575b649C63cbAE4994aD51D27Aa97f76bD404F', '0x0607A5a7F0D0965b89826700756fD6B44284972d', '0x37CC60790a649820752973FA661fef9badaDDeE1']:
    chk['checked'][a] = {'source': 'run-2026-11-05-0931-5c', 'result': 'not-sale-shape: Sourcify 404/transport, free views revert'}
json.dump(chk, open(f'{base}/track-c-scan-checked.json', 'w'), indent=1)
# --- scan state ---
st = json.load(open(f'{base}/onchain-scan-state.json'))
st['last_scanned_block'] = 131733301
st['last_scan_window_from'] = 131731302
st['last_scan_window_to'] = 131733301
st['last_scan_wib'] = '2026-11-05 run 0931'
st['ankr_calls'] = 80
st['errors'] = []
st['nft_contracts'] = 303
st['erc20_mint_contracts'] = 441
st['skipped_gap'] = '131726228-131731301 (cap 2000: scan run 0901 mengambil 2000 blok terbaru 131731302-131733301; gap dari watermark 131726227 dilewati dan dicatat)'
st['note'] = 'Scan run 0901 DIPROSES run 0931 (exit 0, 80 panggilan Ankr, 0 error); watermark maju ke 131733301.'
json.dump(st, open(f'{base}/onchain-scan-state.json', 'w'), indent=1)
print('snapshot contracts:', len(snap['contracts']), 'seen:', len(seen['contracts']), 'checked:', len(chk['checked']))
