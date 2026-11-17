import json, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-08-1101-reread.json"))
NEW_BLOCK=rr['block']  # 132329835
INTERVAL=44.3
contracts=snap['contracts']
reread=rr['reread']
vel_pass_names={'Mechfarm','Weldagent','Agent Cards','Beatmind','Ore Raiders SHIP (checked-2026-11-05)','MORPHA','Skyagent','Zhenzhu','WAR3-1aa9','0xbd4B4e7189ae9356514664146b0eD683601200A9','AURISLE'}
n_upd=0
for name, e in contracts.items():
    if not isinstance(e,dict): continue
    d=reread.get(name)
    if d is None: continue
    n_upd+=1
    old_sup=e.get('totalSupply')
    if old_sup is None: old_sup=e.get('totalMinted')
    new_sup=d.get('totalSupply')
    if new_sup is None: new_sup=d.get('totalMinted')
    if isinstance(new_sup,int) and isinstance(old_sup,int):
        minted=new_sup-old_sup
        prev_rate=e.get('currentRatePerMin') or 0
        e['previousTotalSupply']=old_sup
        e['mintedInInterval']=minted
        e['intervalMinutes']=INTERVAL
        e['previousRatePerMin']=prev_rate if isinstance(prev_rate,(int,float)) else 0
        e['currentRatePerMin']=round(minted/INTERVAL,4)
        e['velocityLegPasses']=name in vel_pass_names
    if d.get('totalSupply') is not None: e['totalSupply']=d['totalSupply']
    if d.get('totalMinted') is not None: e['totalMinted']=d['totalMinted']
    if d.get('freeClaimed') is not None: e['freeClaimed']=d['freeClaimed']
    if d.get('freeMinted') is not None: e['freeMinted']=d['freeMinted']
    if d.get('FREE_SUPPLY') is not None: e['FREE_SUPPLY']=d['FREE_SUPPLY']
    if d.get('MAX_SUPPLY') is not None: e['MAX_SUPPLY']=d['MAX_SUPPLY']
    if d.get('mintOpen') is not None: e['mintOpen']=d['mintOpen']
    if d.get('balanceOf_user') is not None: e['userBalance']=d['balanceOf_user']
    if d.get('freeClaimed_user') is not None: e['freeClaimed_user']=d['freeClaimed_user']
    e['lastReadBlock']=NEW_BLOCK
    e['lastReadWib']="2026-11-08 run 1101"
print('contracts updated:', n_upd)
# track_c
tc_changes=0
for name, e in snap.get('track_c',{}).items():
    if not isinstance(e,dict): continue
    d=rr['track_c'].get(name)
    if d is None: continue
    if d.get('totalSupply') is not None and d['totalSupply']!=e.get('totalSupply'):
        e['totalSupply']=d['totalSupply']; tc_changes+=1
    if d.get('freeMinted') is not None: e['freeMinted']=d['freeMinted']
    e['lastReadBlock']=NEW_BLOCK
    e['lastReadWib']="2026-11-08 run 1101"
print('track_c supply changes:', tc_changes)
# Cedar Kiln update
ck=contracts.get('Cedar Kiln')
if ck:
    ck['lastReadBlock']=NEW_BLOCK
    ck['lastReadWib']="2026-11-08 run 1101 (recheck)"
    ck['runNote1101']="Run 1101: recheck ~12:0x WIB. Total mint on-chain TETAP 35 (hitung ulang 1031, 0 error, blok 132321293-132327909) + 0 mint baru sesudah blok 132327490 sampai head 132330202 (chunk sukses; 2 chunk 132325293-132327292 gagal RemoteDisconnected tapi tercakup hitungan 1031). Free phase (first 250) MASIH TERBUKA on-chain (35<250); slot user terverifikasi terbuka ulang (sim helper mint(1) value 0 OK dari wallet user, revert 0x41aaf0fd dari dead). Free% TETAP UNVERIFIED (tanpa counter global) -> tetap EARLY, belum strong lead (butuh free% >=25% terverifikasi + slot terbuka; umur <=48h terverifikasi, website gate PASSED run 1031). TIDAK di-preview/di-mint."
# AURISLE update
au=contracts.get('AURISLE')
if au:
    au['totalSupply']=227; au['totalMinted']=227; au['freeMinted']=227; au['MAX_SUPPLY']=1111; au['mintOpen']=1
    au['userBalance']=0
    au['previousTotalSupply']=132; au['mintedInInterval']=89; au['intervalMinutes']=INTERVAL
    au['previousRatePerMin']=0.266; au['currentRatePerMin']=round(89/INTERVAL,4); au['velocityLegPasses']=True
    au['lastReadBlock']=NEW_BLOCK; au['lastReadWib']="2026-11-08 run 1101"
    au['runNote1101']="Run 1101: velocity PASS (+89 mint, 2,01/mnt vs prev 0,266 = 7,6x, >=20 token). freeMinted=totalMinted=totalSupply=227 (semua mint gratis sejauh ini), MAX_SUPPLY 1111, mintOpen=1, balanceOf(user)=0. TAPI free% TETAP UNVERIFIED (FREE_SUPPLY()/freeLeft() revert - bukan artefak), slot user UNVERIFIED (freeClaimed(user)/freeMintedBy(user) revert), website gate TETAP UNVERIFIED (metode A/C/G/H/I run 2001, tanpa temuan baru run ini). BUKAN strong lead, BUKAN kandidat; tetap EARLY. TIDAK di-preview/di-mint."
# Ink Koi update
ik=contracts.get('0xbd4B4e7189ae9356514664146b0eD683601200A9')
if ik:
    ik['totalSupply']=1475; ik['freeMinted']=1467; ik['FREE_SUPPLY']=2777; ik['MAX_SUPPLY']=5555; ik['mintOpen']=1
    ik['freePctVerified']=round(1467/2777*100,2)
    ik['freeClaimed_user']=1; ik['userBalance']=1
    ik['previousTotalSupply']=1446; ik['mintedInInterval']=26; ik['intervalMinutes']=INTERVAL
    ik['previousRatePerMin']=0.23; ik['currentRatePerMin']=round(26/INTERVAL,4); ik['velocityLegPasses']=True
    ik['lastReadBlock']=NEW_BLOCK; ik['lastReadWib']="2026-11-08 run 1101"
    ik['runNote1101']="Run 1101: velocity PASS (+26, 0,59/mnt vs prev 0,23 = 2,5x, >=20 token). free% TERVERIFIKASI 52,83% (freeMinted 1467/2777). TAPI slot user TERTUTUP: freeClaimed(user)=1 + balanceOf(user)=1 (user sudah memegang 1). BUKAN strong lead (slot tertutup), BUKAN kandidat. Tetap early-lead-backfill; TIDAK di-preview/di-mint."
# Add CrudeFi + VVCREW
contracts['CrudeFi Refinery']={
 "address":"0x60FBe0ddC05A4B4bae047B816d77f5E6B68306E2","name":"CrudeFi Refinery","symbol":"CRUDEFI","kind":"ERC721",
 "status":"watchlist-only-registry-bytes-only-2026-11-08",
 "firstSeenBlock":132327836,"firstMintBlock":132327120,"firstMintWib":"2026-11-08 11:16:57 WIB",
 "totalMinted":86,"totalSupply":None,"freeClaimed":None,"FREE_SUPPLY":None,
 "registryBytesHit":True,"sourcify":"not_verified",
 "note":"First-seen run 1101 (scan window 132327745-132328744, 13 mint/13 minter in-window; total 86 mint). First mint TERVERIFIKASI 2026-11-08 11:16:57 WIB (Ankr getLogs address-filtered 200k blok + timestamp blok via fast_rpc dataseed) -> umur <=48h. Bytecode mengandung registry bytes 60b9...022F; Sourcify NOT verified -> free shape UNKNOWN. BUKAN early lead (preseden JINLI/Dafeiyu: registry-bytes-only + unverified = watchlist-only, bukan agent-shaped final). TIDAK dilaporkan, TIDAK di-preview/di-mint. Naik tier hanya bila ABI terverifikasi + free view + slot user terverifikasi.",
 "lastReadBlock":NEW_BLOCK,"lastReadWib":"2026-11-08 run 1101","userBalance":0}
contracts['Vikings Valley Crew']={
 "address":"0x6F75244bfe2b1e27d9BB963C47e2AAF45b10D308","name":"Vikings Valley Crew","symbol":"VVCREW","kind":"ERC721",
 "status":"watchlist-only-not-early-2026-11-08",
 "firstSeenBlock":132328269,"totalSupply":431,"totalMinted":None,
 "registryBytesHit":False,"sourcify":"not_verified",
 "note":"First-seen run 1101 (1 mint/1 minter in-window). Tanpa registry bytes, Sourcify not_verified, totalSupply 431 (mature) -> BUKAN agent-shaped, BUKAN early lead. TIDAK dilaporkan, TIDAK di-preview/di-mint.",
 "lastReadBlock":NEW_BLOCK,"lastReadWib":"2026-11-08 run 1101","userBalance":0}
# 9 sold-out re-labels (age-flagged but verified sold out -> age rule does not apply)
SOLD9=[('WAGagent','2026-11-05 13:04:34'),('Aether Core','2026-11-05 20:00:58'),('Silent Hydra Agent','2026-11-06 05:22:50'),('Cipher Wraith Agent','2026-11-06 05:28:05'),('Umbra Lynx Agent','2026-11-06 05:33:20'),('Nebula Ape Agent','2026-11-06 05:38:37'),('Shadow Yeti Agent','2026-11-06 05:49:07'),('Storm Sprite Agent','2026-11-06 05:54:23'),('Void Jaguar Agent','2026-11-06 05:59:39')]
for name, fm in SOLD9:
    e=contracts.get(name)
    if isinstance(e,dict):
        old=e.get('status')
        e['status']='sold-out-2026-11-08'
        e['soldOutNote1101']=f"Run 1101: totalSupply==MAX_SUPPLY terverifikasi segar (blok {NEW_BLOCK}); first mint {fm} WIB (>48 jam) TAPI sold out -> aturan umur 48 jam TIDAK berlaku (sold-out sudah excluded). Status lama '{old}' dikoreksi ke sold-out. TIDAK di-age-remove, TIDAK dilaporkan sebagai sellout baru (nilai tidak berubah sejak run 1031)."
print('sold-out relabels:', len(SOLD9))
# run note + last_run
snap['runNote1101']=("Run 1101 (2026-11-08, blok reread 132329835, interval 44,3 mnt): reread 475 kontrak + 70 track_c; velocity 11 pass tapi 0 promotable "
 "(Mechfarm/Weldagent/Beatmind same-owner-discarded; Agent Cards + WAR3 minted-by-user; Skyagent age-excluded; Zhenzhu artefak ERC-20; Ore Raiders checked-not-early; MORPHA shape-unverified; "
 "AURISLE free%+slot+website unverified; Ink Koi free% 52,83% TAPI slot user TERTUTUP freeClaimed(user)=1). soldOut: 0 baru (42 kontrak terverifikasi sold-out pada bacaan segar, set tidak berubah vs run 1031; 9 item yang di-flag age-sweep ternyata sold out totalSupply==MAX_SUPPLY -> status dikoreksi ke sold-out-2026-11-08, BUKAN age-remove). slotChanged 0. "
 "Age-sweep: remove=0 (9 flag awal semuanya sold out), kept-verified-launch=14, unverified-launch=278. "
 "Track B binanceai tidak berubah (blok 132329661: launched=0, failed=1, isRefundPhase=1, tokenClaimed_user=0, balance 0; sudah dilaporkan run 1701 2026-11-07). "
 "Track C: 70 item, 4 hanya berubah totalSupply (Crack, ORBITA, PLNK, HobnorbAgent); 0 lead/kandidat baru. "
 "Bridge: file tidak berubah sejak 2026-11-06 02:48, 115 kontrak, 0 entri baru. "
 "Boltbook EN+ZH (curl -L; fetch tanpa -L gagal 0 byte): 15 alamat, 8 baru-vs-seen, 0 lead (BFG Binance Fleet Genesis 1000/1000 SOLD OUT; sisanya 404/unverified/tanpa shape). "
 "Sourcify feed 20 kontrak -> 0 S1/0 S2/0 mint-shaped (8x template 33-fn paid share-sale tanpa free view; 1x Skunks free-window tanpa agent ref); feed susulan hot-leg 1159: 11 dicek -> 0 S1/0 S2. "
 "Sweep EN+ZH + Square/Odaily: 0 proyek baru (Nidavellir sudah excluded run 2101, free window tutup; JAGENT berbayar 1 USDT; Ptah sudah held). "
 "Scan OK (1000 blok 132327745-132328744, 176 NFT, 338 ERC-20, 0 error, 40 Ankr calls, partial=false; watermark 132313490 -> 132328744; skipped gap 132313491-132327744, backfill off). "
 "First-seen x2, 0 EARLY lead: CrudeFi Refinery 0x60FBe0dd (first mint 11:16:57 WIB, registry-bytes saja, unverified -> watchlist-only) + Vikings Valley Crew 0x6F75244b (1 mint, tanpa registry, unverified -> watchlist-only-not-early). "
 "5c: 2 baru dicek (0x69274640 unverified, 0xb95d1a2F tanpa agent/free), 0 sale shape. "
 "Cedar Kiln: total mint TETAP 35, mint terakhir blok 132327490, free phase (first 250) MASIH TERBUKA, slot user terverifikasi terbuka ulang (sim OK); free% tetap UNVERIFIED -> tetap EARLY, TIDAK di-preview/di-mint.")
snap['last_run']="free-mint-search 2026-11-08 1101 WIB"
snap['last_run_wib']="2026-11-08 12:09 WIB"
with open(f"{BASE}/onchain-snapshot.json.tmp","w") as f: json.dump(snap,f,indent=1)
import os; os.replace(f"{BASE}/onchain-snapshot.json.tmp", f"{BASE}/onchain-snapshot.json")
print('snapshot saved')
# seen file: append 2 first-seen
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen['contracts']["0x60fbe0ddc05a4b4bae047b816d77f5e6b68306e2"]=132327836
seen['contracts']["0x6f75244bfe2b1e27d9bb963c47e2aaf45b10d308"]=132328269
with open(f"{BASE}/onchain-scan-seen.json.tmp","w") as f: json.dump(seen,f,indent=1)
os.replace(f"{BASE}/onchain-scan-seen.json.tmp", f"{BASE}/onchain-scan-seen.json")
print('seen updated, total:', len(seen['contracts']))
# track-c-scan-checked: append 2 to 'checked' list
chk=json.load(open(f"{BASE}/track-c-scan-checked.json"))
lst=chk.get('checked',[])
for a in ["0x6927464044087e5102234417031bE92f62D27bF4","0xb95d1a2F2259a411183c731374798Cf69B4349E0"]:
    if a not in lst: lst.append(a)
chk['checked']=lst
chk["0x6927464044087e5102234417031bE92f62D27bF4"]={"source":"run-1101-5c","status":"checked-not-sale-shape","mint_count":14,"note":"S1=False S2=False (Sourcify not_verified)"}
chk["0xb95d1a2F2259a411183c731374798Cf69B4349E0"]={"source":"run-1101-5c","status":"checked-not-sale-shape","mint_count":10,"note":"S1=False S2=False (mint ada, tanpa quote/free/agent)"}
with open(f"{BASE}/track-c-scan-checked.json.tmp","w") as f: json.dump(chk,f,indent=1)
os.replace(f"{BASE}/track-c-scan-checked.json.tmp", f"{BASE}/track-c-scan-checked.json")
print('checked updated, list n:', len(lst))
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st['last_scanned_block']=132328744
st['last_scan_window_from']=132327745
st['last_scan_window_to']=132328744
st['last_scan_wib']="2026-11-08 12:09 WIB"
st['ankr_calls']=40
st['errors']=[]
st['nft_contracts']=176
st['erc20_mint_contracts']=338
st['skipped_gap']="132313491-132327744 (14254 blok; backfill dinonaktifkan user; window scan hanya 1000 blok terbaru)"
st['note']="Scan run 1101 OK (1000 blok 132327745-132328744, 176 NFT + 338 ERC-20, 0 error, partial=false, 40 Ankr calls). 2 first-seen: CrudeFi Refinery 0x60FBe0dd (registry-bytes-only, unverified -> watchlist-only) + Vikings Valley Crew 0x6F75244b (1 mint, no registry -> watchlist-only-not-early). Watermark 132313490 -> 132328744."
with open(f"{BASE}/onchain-scan-state.json.tmp","w") as f: json.dump(st,f,indent=1)
os.replace(f"{BASE}/onchain-scan-state.json.tmp", f"{BASE}/onchain-scan-state.json")
print('scan state saved')
