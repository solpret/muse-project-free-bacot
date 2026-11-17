import json, pathlib, shutil
base=pathlib.Path.home()/"workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_p=base/"onchain-snapshot.json"
shutil.copy(snap_p, base/"onchain-snapshot-1001.bak.json")
snap=json.load(open(snap_p))
def upd(key, **kw):
    e=snap["contracts"].get(key)
    if e is None:
        print("MISS", key); return
    e.update(kw)
# Reread (block 131741330) vs run 0931 log values
upd("HIVE Agents", totalSupply=1240, previousTotalSupply=1240, mintedInInterval=0, velocityLegPasses=False,
    lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001 (blok 131741330): 1240 flat vs 0931 (1240) -> velocity GAGAL.")
upd("Tigora-E8c4", totalMinted=553, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: totalMinted 543 (0931) -> 553 (+10, <20) -> velocity GAGAL.")
upd("BNBRunnerz-2674", totalSupply=2995, totalMinted=2995, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 2970 (0931) -> 2995 (+25, >=20) tapi rasio vs interval sebelumnya +19 = 1,32x (<1,5x) -> velocity GAGAL.")
upd("Shroomies-2AE7", totalSupply=804, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 797 (0931) -> 804 (+7, <20) -> velocity GAGAL.")
upd("Blobbies-a7fB", totalSupply=1333, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 1325 (0931) -> 1333 (+8, <20) -> velocity GAGAL (lolos velocity-saja 0931 hilang).")
upd("Robogent", totalSupply=1198, freeClaimed=1194, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 1198 flat, freeClaimed 1194 tidak berubah -> tetap strong-lead-gate-blocked, tanpa perubahan tier.")
upd("Jolly", totalMinted=3319, freeMinted=3319, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: totalMinted 3315 (0931) -> 3319 (+4, <20) -> velocity GAGAL; tetap strong-lead-gate-blocked, TIDAK dilaporkan ulang.")
upd("HACKED", totalSupply=2974, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 2948 (0931) -> 2974 (+26, >=20) tapi rasio vs interval sebelumnya +36 = 0,72x -> velocity GAGAL; minted-by-user, bukan promosi; balanceOf(user)=2.")
upd("SoulAgent", totalSupply=608, totalMinted=608, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 594 (0931) -> 608 (+14, <20) -> velocity GAGAL (lolos velocity-saja 0931 hilang); tetap EARLY.")
upd("PERSONA-A930", totalSupply=1095, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 1093 (0931) -> 1095 (+2, <20) -> velocity GAGAL; tetap EARLY.")
upd("RigOrb-539e", totalSupply=368, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: reread 347/probe 349 (0931) -> 368 (+19..21, borderline) + mintOpen 1, priceFor(user,1)=0, mintedCount(user)=0; free views revert -> % UNVERIFIED, umur/website unverified -> tetap EARLY, BUKAN strong lead, TIDAK di-preview/di-mint.")
upd("StarAgent-7d39", totalSupply=874, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 869 (0931) -> 874 (+5, <20) -> velocity GAGAL; tetap EARLY.")
upd("Saturnode", totalSupply=1598, freeClaimed=1575, FREE_SUPPLY=4000, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001 (probe Boltbook ZH): 764 (run 0101 2026-11-04) -> 1598; freeClaimed 1575/4000 = 39,4% terverifikasi, mintOpen 1, mintedBy(user)=0, quote(user,1)=0; umur peluncuran TETAP UNVERIFIED + website unverified -> BUKAN promosi strong lead (butuh umur terverifikasi <=48 jam), tetap EARLY, TIDAK di-preview/di-mint.")
upd("MoonCat", totalSupply=555, totalMinted=555, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001 (probe Boltbook ZH): 497 (run 0701) -> 555 (post ZH 533, konsisten minting berjalan); tetap watchlist-only-boltbook-noted.")
upd("ACOS-3aed", totalSupply=2638, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001 (probe Boltbook ZH): 2387 -> 2638 (post 2625); post ZH menyatakan selector value-0 revert (bukan bukti gratis user); tetap watchlist-only-age-pct-website-unverified.")
upd("Pumpkinfarm-77E3", totalSupply=406, freeClaimed=405, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: Boltbook EN post #379/#381 + probe segar: 188 (run 2201 2026-11-04) -> 406; freeClaimed 405/999 = 40,5% terverifikasi, mintOpen 1, mintedBy(user)=0, quote(user,1)=0 (bacaan run ini); umur peluncuran TETAP UNVERIFIED + website unverified (contractURI tanpa external_link per snapshot) -> BUKAN promosi strong lead, tetap EARLY, TIDAK di-preview/di-mint.")
upd("DYOR-8695", totalSupply=730, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 117 (fresh 0931) -> 730 (lonjakan minting; jendela scan 0931 saja 177 mint/177 minter); MAX 11111, mintOpen 1, balanceOf(user)=0; free views revert -> % gratis UNVERIFIED, slot user UNVERIFIED, umur/website UNVERIFIED -> tetap EARLY, BUKAN promosi, TIDAK di-preview/di-mint.")
upd("PixelLaptop-273f", totalSupply=477, FREE_SUPPLY=1800, lastReadBlock=131741627, lastReadWib="2026-11-05 run 1001",
    velocityNote1001="Run 1001: 453 (0931) -> 477 (+24); FREE_SUPPLY 1800, MAX 3333, balanceOf(user)=0; freeClaimed/freeMinted revert -> % gratis UNVERIFIED (477/3333 = 14,3% adalah % total, BUKAN % gratis), slot/umur/website UNVERIFIED -> tetap EARLY, TIDAK di-preview/di-mint.")
# AFROG by address
for k,e in snap["contracts"].items():
    if isinstance(e,dict) and (e.get("address") or "").lower()=="0x4fea4ed6e70389245c41b2c9d85e8032e3c6ce31":
        e.update(totalSupply=212, freeClaimed=212, FREE_SUPPLY=1111, lastReadBlock=131741330, lastReadWib="2026-11-05 run 1001",
            velocityNote1001="Run 1001: 198 (0931) -> 212 (+14, <20); free 212/1111 = 19,1% (<25%) -> tetap EARLY, BUKAN promosi.")
        print("AFROG key:", k)
# New watchlist-only entries (log-only, NOT reported as leads)
snap["contracts"]["PCAT-9b9e"]={"address":"0x9b9e0a4358449eebf4437877a9b36e26c24ce703","status":"watchlist-only-boltbook-2026-11-05","name":"PIXEL CAT CLUB","symbol":"PCAT","kind":"ERC721","totalSupply":2384,"freeMinted":2384,"MAX_SUPPLY":10000,"mintOpen":1,"balanceOf(user)":0,"firstSeenNote":"Boltbook ZH post recheck 2344/10000 (08:57 WIB) + probe run 1001: 2384; situs klaim post https://pixelcat.pages.dev/ (BELUM dicek gate: belum diverifikasi mencetak kontrak persis); free views lain + agentRegistry revert/transport (bukan vonis); umur/website/slot user UNVERIFIED; sudah ada di scan-seen -> BUKAN early.","lastReadBlock":131741627,"lastReadWib":"2026-11-05 run 1001"}
snap["contracts"]["KOAI-6dFE"]={"address":"0x6dFE0D2E3Ab6f2bD5F3875557eb0e5c5Fe4B05c7","status":"watchlist-only-boltbook-2026-11-05","name":"KOAI","kind":"ERC721","totalSupply":7249,"MAX_SUPPLY":10000,"mintOpen":1,"balanceOf(user)":0,"firstSeenNote":"Boltbook ZH post: KOAI #7231 minted free 2026-11-05 (tx block 131732853, Sourcify exact_match klaim post) + probe run 1001: 7249; free/agent views revert (bukan vonis); umur/website/slot user UNVERIFIED; sudah ada di scan-seen -> BUKAN early.","lastReadBlock":131741627,"lastReadWib":"2026-11-05 run 1001"}
snap["contracts"]["SPOTS-UMBH-4915"]={"address":"0x49150574b740c5a75FaC272446f9cBB7c27b02C2","status":"watchlist-only-sourcify-feed-2026-11-05","name":"UMBH","symbol":"UMBH","kind":"ERC20 spots sale","saleShape":"S1-PARTIAL (bukan penuh): ABI Sourcify 38 fungsi (mint + quote + AGENT_REGISTRY + WEBSITE/TWITTER) TANPA free-share view terdaftar; spotsLeft 4999/5000, totalSpotsMinted 1, PRICE 0,0002 BNB, quote(user,1) REVERT (bukan bukti slot gratis), mintedBy(user)=0, balanceOf(user)=0.","websiteConstant":"https://agenticspace.xyz","twitterConstant":"@agenticspaceBnb","gateNote":"Konstanta WEBSITE/TWITTER on-chain saja; situs BELUM dicek mencetak kontrak persis -> gate BELUM lolos; BUKAN lead track-C, TIDAK di-preview/di-mint.","lastReadBlock":131741627,"lastReadWib":"2026-11-05 run 1001"}
snap["contracts"]["SPOTS-NEBD-86CA"]={"address":"0x86CA531ffB29A0B7bc17A5f3973F7B431a9263A4","status":"watchlist-only-sourcify-feed-2026-11-05","name":"Nebula Drop","symbol":"NEBD","kind":"ERC20 spots sale","saleShape":"S1-PARTIAL (bukan penuh): ABI Sourcify 38 fungsi identik template agenticspace (mint + quote + AGENT_REGISTRY + WEBSITE/TWITTER) TANPA free-share view terdaftar; spotsLeft 4999/5000, totalSpotsMinted 1, PRICE gagal baca transport (template sama 0,0002 BNB pada 2 saudara), quote(user,1) REVERT, mintedBy(user)=0, balanceOf(user)=0; juga 1 mint di jendela scan 0931 (ERC20 list).","websiteConstant":"https://agenticspace.xyz","twitterConstant":"@agenticspaceBnb","gateNote":"Situs BELUM dicek mencetak kontrak persis -> gate BELUM lolos; BUKAN lead track-C, TIDAK di-preview/di-mint.","lastReadBlock":131741627,"lastReadWib":"2026-11-05 run 1001"}
snap["contracts"]["SPOTS-FLUB-1216"]={"address":"0x12167D06c9CecC0b5EAFD166892CFbf8240fd971","status":"watchlist-only-sourcify-feed-2026-11-05","name":"Flux Byte","symbol":"FLUB","kind":"ERC20 spots sale","saleShape":"S1-PARTIAL (bukan penuh): ABI Sourcify gagal fetch transport berulang (bukan vonis) TETAPI probe on-chain menunjukkan template identik (spotsLeft 4999/5000, totalSpotsMinted 1, PRICE 0,0002 BNB, WEBSITE/TWITTER sama, AGENT_REGISTRY sama); quote(user,1) REVERT, mintedBy(user)=0, balanceOf(user)=0; TANPA free-share view terverifikasi.","websiteConstant":"https://agenticspace.xyz","twitterConstant":"@agenticspaceBnb","gateNote":"Situs BELUM dicek mencetak kontrak persis -> gate BELUM lolos; BUKAN lead track-C, TIDAK di-preview/di-mint.","lastReadBlock":131741627,"lastReadWib":"2026-11-05 run 1001"}
snap["timestamp_wib"]="2026-11-05 run 1001"
snap["last_run_wib"]="2026-11-05 run 1001"
snap["runNote1001"]="Run 1001: 0 kandidat track-A, 0 strong lead/promosi, 0 lead/kandidat track-C, 0 pending claim baru/dibuka, 0 auto-mint/klaim, 0 EARLY baru. Watchlist-only baru (log-only, TIDAK dilaporkan): PCAT, KOAI (Boltbook ZH), SPOTS UMBH/NEBD/FLUB (feed Sourcify, S1-partial). First-seen scan 0931 (3): SAOBNFT/V12/DuskWyrm -> log-only + seen, BUKAN early (bukti agent-shape konkret tidak ada). Saturnode/Pumpkinfarm tetap EARLY (umur unverified memblokir promosi walau % gratis + quote 0 terbaca). ShibAgent R2 tetap STOPPED (perintah user 2026-11-05 08:49 WIB). Sidecoo probe 5/6 selesai saat log ditulis (baris Sidecoo tertunda transport RPC) - bukan kandidat/lead, diambil run berikut."
snap["runNote1001_scan"]="Scan 0931 diproses run 1001: jendela 131737321-131739320 (2000 blok, cap), 80 panggilan Ankr, 0 error, 249 kontrak NFT/1155, 458 ERC-20 mint. Watermark 131733301 -> 131739320; gap 131733302-131737320 dilewati dan dicatat (cap 2000). ERC20 backlog: 60 mint>=10, 20 teratas di-shape-check, 0 lolos S1/S2; 11 definitif dicatat checked (1746 -> 1757), 9 gagal transport TANPA ABI dicatat sebagai sampling/transport limit (bukan checked). Scan baru run 1001 DIMULAI (PID 23676, log scan-1001.log masih 0 byte saat log ditulis); watermark jendela baru BELUM dimajukan; run berikut WAJIB memeriksa onchain-scan-2026-11-05-1001.json dulu, jangan scan ganda."
json.dump(snap, open(snap_p,"w"), indent=1)
print("snapshot updated, contracts:", len(snap["contracts"]))
# seen file
seen=json.load(open(base/"onchain-scan-seen.json"))
seen["contracts"]["0xea45d5dcc55700183b87016dd38d17f6f1a6ed8b"]=131738636
seen["contracts"]["0x11df7fd6bf179d7173184c82e2917b62905e773c"]=131738692
seen["contracts"]["0xf592a1917cb4fdf5d9ad666b6426da2f8585d0d4"]=131738983
json.dump(seen, open(base/"onchain-scan-seen.json","w"), indent=1)
print("seen contracts now:", len(seen["contracts"]))
# scan state
st=json.load(open(base/"onchain-scan-state.json"))
st.update({"last_scanned_block":131739320,"last_scan_window_from":131737321,"last_scan_window_to":131739320,"last_scan_wib":"2026-11-05 run 1001","ankr_calls":80,"errors":[],"nft_contracts":249,"erc20_mint_contracts":458,"skipped_gap":"131733302-131737320 (cap 2000: scan 0931 mengambil 2000 blok terbaru 131737321-131739320; gap dari watermark 131733301 dilewati dan dicatat)","note":"Scan run 0931 DIPROSES run 1001 (exit 0, 80 panggilan Ankr, 0 error); watermark maju ke 131739320."})
json.dump(st, open(base/"onchain-scan-state.json","w"), indent=1)
print("scan-state updated")
# track-c checked +11 definitive
chk=json.load(open(base/"track-c-scan-checked.json"))
adds=["0xFaD229b3155a73fD8dB851E079558A884b009999","0xE07150DD3A870fF0115Fc4e3c80529f92e294D89","0x5ce033B2bFCa3Af30b3e8C8457DeaF776A8b695a","0x826923122A8521Be36358Bdc53d3B4362B6f46E5","0xc4bf86ABA5cCEC21E19b94C95CcB212359F471Df","0x7d3D3C4bFa280BE71cfA596a00CD45b2dD4af0FF","0x35803e77c3163FEd8A942536C1c8e0d5bF90f906","0x9F10a122a921d25Fa9084955c87c3FcAB103267F","0x80de13A10A23c6577fC482fab0B1a933ac9799EA","0x302DF4C0E3DD5Dcb36D59344b60D11D05617Fe5e","0xa6344A67780e2da01928FEFd9E558D792d7986dc"]
for a in adds:
    chk["checked"][a]={"source":"run-2026-11-05-1001-erc20-shape","result":"shape-fail-or-sourcify-404, 0 S1/S2"}
json.dump(chk, open(base/"track-c-scan-checked.json","w"), indent=1)
print("track-c-checked now:", len(chk["checked"]))
