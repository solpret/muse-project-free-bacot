#!/usr/bin/env python3
"""Run 0301 merge: priority re-reads + ACORE same-owner discard + SAKURA watchlist-only + FEG sold-out + UFO watchlist-only + MOODENG/LOWB updates. No executions."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0301-premerge")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]; TC=s.get("track_c", {})
BLOCK=132837064
def upd(name, note, **kw):
    e=C.setdefault(name, {})
    e.update(kw)
    e["runNote0301_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 03:01 WIB"
upd("REWINDCLUB","Run 0301 (blok 132837064): totalSupply 406->409 (+3, ~0,10/mnt vs prev ~0,27/mnt = 0,37x DAN <20 token) velocity GAGAL; agentFreeUsed 409/2000 = 20,45% (<25%); slot terbuka; mintStart 2026-11-10 21:49 WIB (umur ~5,2 jam, TERVERIFIKASI <24 jam; deadline ~21:49 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=409, agentFreeUsed=409, balanceOf_user=0, agentFreeByWallet_user=0)
upd("LCDSPRITE","Run 0301 (blok 132837064): totalSupply 457->461 (+4, ~0,13/mnt vs prev ~0,47/mnt = 0,28x DAN <20) velocity GAGAL; agentFreeUsed 461/2000 = 23,05% (<25%); slot terbuka; mintStart 2026-11-10 21:52 WIB (umur ~5,15 jam, TERVERIFIKASI <24 jam; deadline ~21:52 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=461, agentFreeUsed=461, balanceOf_user=0, agentFreeByWallet_user=0)
upd("RIMEVAULT","Run 0301 (blok 132837064): totalSupply 474->483 (+9, ~0,30/mnt vs prev ~0,67/mnt = 0,45x DAN <20) velocity GAGAL; agentFreeUsed 483/2000 = 24,15% (<25%) - tetap EARLY, TANPA promosi (butuh 17 mint lagi ke 500/2000); slot terbuka; mintStart 2026-11-10 21:27 WIB (umur ~5,6 jam, TERVERIFIKASI <24 jam; deadline ~21:27 WIB 11 Nov). Post sensus 04:51 WIB: totalSupply 480 di blok 132.835.769 (konsisten).",
    totalSupply=483, agentFreeUsed=483, balanceOf_user=0, agentFreeByWallet_user=0)
upd("MYCELIX","Run 0301 (blok 132837064): totalSupply 473->485 (+12, ~0,40/mnt vs prev ~0,23/mnt = 1,74x TAPI <20 token) velocity GAGAL; agentFreeUsed 485/2000 = 24,25% (<25%) - tetap EARLY, TANPA promosi (butuh 15 mint lagi ke 500/2000); slot terbuka; mintStart 2026-11-10 21:47 WIB (umur ~5,25 jam, TERVERIFIKASI <24 jam; deadline ~21:47 WIB 11 Nov).",
    totalSupply=485, agentFreeUsed=485, balanceOf_user=0, agentFreeByWallet_user=0)
upd("NIGHTFORGE","Run 0301 (blok 132837064): totalSupply 692->702 (+10, <20) velocity GAGAL; agentFreeUsed 699/2000 = 34,95% (tetap >=25% strong-leg %); slot terbuka (agentFreeByWallet 0, balanceOf 0); gate TETAP BLOCKED - recheck run ini (H+I+J+G): nightforge.pages.dev + /llms.txt + /skill.md + /launch.json + /agent.json + /meta/collection.json SEMUA mengembalikan HTML infografis medis 23.809 byte, 0 kecocokan kontrak; contractURI/tokenURI kosong. TIDAK di-mint; deadline umur 2026-11-11 14:37 WIB.",
    totalSupply=702, agentFreeUsed=699, balanceOf_user=0, agentFreeByWallet_user=0)
upd("SOLDERCATS","Run 0301 (blok 132837064): totalSupply 447->456 (+9, <20) velocity GAGAL; agentFreeUsed 456/2000 = 22,8% (<25%); slot terbuka; gate website PASSED (metode H); mintStart 2026-11-10 21:35 WIB (umur ~5,45 jam, TERVERIFIKASI <24 jam; deadline ~21:35 WIB 11 Nov); tetap EARLY, tanpa promosi.",
    totalSupply=456, agentFreeUsed=456, balanceOf_user=0, agentFreeByWallet_user=0)
upd("Pico Alcazar","Run 0301 (blok 132837064): totalSupply 263->273 (+10, interval velocity ke-3); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=273, balanceOf_user=0)
upd("Tiling Hammock","Run 0301 (blok 132837064): totalSupply 256->265 (+9, interval velocity ke-3); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=265, balanceOf_user=0)
upd("Hexel Pantry","Run 0301 (blok 132837064): totalSupply 267->276 (+9, interval velocity ke-3); mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=276, balanceOf_user=0)
upd("STALL","Run 0301 (blok 132837064): totalSupply 1630->1640 (+10, <20) velocity GAGAL; mintOpen 1, balanceOf(user)=0; free% + umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi.",
    totalSupply=1640, balanceOf_user=0)
upd("Arcane Stones","Run 0301 (blok 132837064): totalSupply 648 (tetap); balanceOf(user)=0; website terverifikasi; umur TETAP UNVERIFIED; tetap EARLY, tanpa promosi. Post Boltbook: free mint berakhir di 4.111.",
    totalSupply=648, balanceOf_user=0)
upd("Cosmic Sentinel","Run 0301 (blok 132837064): totalSupply 388->391, freeMinted 383 (reread; free view None run ini, nilai lama dipertahankan); balanceOf(user)=0; tetap watchlist-only.",
    totalSupply=391, balanceOf_user=0)
upd("Dragon Agent","Run 0301 (blok 132837064): totalSupply 904->906 (+2); balanceOf(user)=0, slot terbuka; free% + umur TETAP UNVERIFIED - DITAHAN preseden run 2026-11-10 (launch unverified), BUKAN age-excluded; tetap watchlist-only, tanpa promosi. Post jaykojay.ai: DAGENT 'totalSupply 904 dua kali baca, 27 menit, nol mint baru' (konsisten).",
    totalSupply=906, balanceOf_user=0)
upd("GangDotFun","Run 0301 (blok 132837064): batch reread GAGAL (transport; totalSupply None) - nilai lama dipertahankan (totalMinted 330, freeMinted 330); BUKAN nol. Post ghostagent.ai: recheck 343/500 gratis, mint() sim bersih 2 RPC, TAPI tanpa Agent-ID gate (free lane terbuka untuk alamat mana pun) -> tetap watchlist-only first-read, tanpa promosi.",
    balanceOf_user=0)
upd("Kitebots","Run 0301 (blok 132837064): totalSupply 983 (tetap), freeMinted 983/4.000 = 24,6% (inferensi vs MAX; FREE_SUPPLY view tetap None); paidMinted 0; balanceOf(user)=0; velocity GAGAL (+0); umur TETAP UNVERIFIED; tetap watchlist-only-age-unverified.",
    totalSupply=983, freeMinted=983, balanceOf_user=0)
upd("ORBITJANITOR","Run 0301: totalSupply 635->637 (+2); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=637, balanceOf_user=1)
upd("EMBERANVIL","Run 0301: totalSupply 1029->1032 (+3); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=1032, balanceOf_user=1)
upd("BYTEBLOOM","Run 0301: totalSupply 572->574 (+2); balanceOf(user)=1 - slot terpakai terkonfirmasi; tanpa perubahan.",
    totalSupply=574, balanceOf_user=1)
# ACORE — same-owner discarded (owner 0x1103...a9dd = gelombang costOf/mintsLeft 11 kontrak, discards 2026-11-06)
C["ACORE"]={
 "address":"0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
 "status":"promotion-discarded-same-owner-2026-11-11",
 "name":"Agent Core (ACORE)",
 "kind":"ERC721",
 "totalSupply":1529,
 "freeLeft":477,
 "MAX_SUPPLY":2000,
 "freePctVerified":76.15,
 "freePctNote":"Terverifikasi via freeLeft view: (2000-477)/2000 = 76,15% free terpakai.",
 "mintOpen":1,
 "balanceOf_user":0,
 "costOf_user_1":0,
 "price_second_mint":200000000000000,
 "owner":"0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd",
 "sourcify":"exact_match, verifiedAt 2026-11-08T13:12:32Z (verification time, BUKAN launch time)",
 "agentShape":"UNVERIFIED: registry-bytes 0x60B9...022F ABSEN dari bytecode; agentRegistry()/REGISTRY()/agentId()/agentGate()/AGENT_REGISTRY() SEMUA revert; costOf(user,1)=0, price()=0,0002 BNB (mint ke-2) - pola costOf/mintsLeft sama dengan gelombang yang dibuang.",
 "launchNote":"UNVERIFIED: tidak ada launch time yang dinyatakan proyek; riwayat pace dari post qlp.ai (1.044 pagi -> 1.364 siang -> 1.445 sore -> 1.448 21:52 WIB 10 Nov -> 1.523 run ini) menunjukkan launch 10 Nov pagi, TAPI tanpa stated launch time / first-mint block (Ankr getLogs mati 401) = UNVERIFIED.",
 "gate":"website UNVERIFIED: post qlp.ai 'No official website or token details could be verified'.",
 "discardReason":"Owner 0x1103...a9dd SAMA dengan 11 kontrak gelombang costOf/mintsLeft yang dibuang 2026-11-06 (Toucan Play, jelly.exe, Los Flamingos, Moonhowlers, Counting Sheep, Tusk & Trunk, getpuffr, Hippo Social Club, LLAMA DRAMA, Danger Noodles, SHACHO CLUB) - dicek di same-owner-discards.json run ini SEBELUM promosi apa pun. TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; TIDAK PERNAH di-preview/di-mint.",
 "source":"Boltbook post qlp.ai /p/AqOZlMetNBMv (Two free lanes, 03:xx WIB) + probe on-chain run 0301 (blok 132837949) + owner() + same-owner-discards.json.",
 "velocityNote":"Pace jatuh: ~70 mint/5,5 jam semalam (~0,21/mnt); freeLeft 487->479->477.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
 "runNote0301_1111":"Run 0301: temuan baru via Boltbook TAPI SAME-OWNER-DISCARDED (owner = gelombang costOf/mintsLeft 11 kontrak, dibuang 2026-11-06). free% 76,15% + slot terbuka + costOf 0 TIDAK mengubah status: bukan lead, tidak dilaporkan sebagai lead, tidak pernah di-preview/di-mint. Ditambahkan ke same-owner-discards.json run ini.",
}
# SAKURA — watchlist-only first-read
C["SAKURA"]={
 "address":"0xF2705A84602369069782624279837A08bdbBf6D6",
 "status":"watchlist-only-first-read-2026-11-11",
 "name":"SAKURA growth NFT",
 "kind":"ERC721",
 "totalSupply":1442,
 "freeMinted":1417,
 "FREE_SUPPLY":6000,
 "MAX_SUPPLY":6666,
 "freePctVerified":23.62,
 "mintOpen":1,
 "balanceOf_user":0,
 "owner":"0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2",
 "ownerDiscardsCheck":"owner TIDAK ada di same-owner-discards.json (dicek run 0301).",
 "sourcify":"NOT verified (per komentar coder143.ai di post; ABI tidak terkonfirmasi di luar sim).",
 "agentShape":"UNVERIFIED: registry-bytes ABSEN dari bytecode; agentRegistry()/REGISTRY()/agentId()/agentGate()/AGENT_REGISTRY() SEMUA revert.",
 "launchNote":"UNVERIFIED: tidak ada launch time yang dinyatakan; post qlp.ai hanya menyebut +25 free semalam (1.390 -> 1.415).",
 "gate":"website UNVERIFIED: tidak ada situs yang ditemukan/disebut di post.",
 "mintNote":"mintFree() value 0 sims bersih di 2 node per komentar coder143.ai; freeMint()/mint() revert dari wallet-nya. Paid tier 0,001 BNB/NFT - JANGAN bayar.",
 "source":"Boltbook post qlp.ai /p/AqOZlMetNBMv + probe on-chain run 0301 (blok 132837949).",
 "boundary":"WATCHLIST ONLY first-read. Bukan early lead (first mint bukan run ini; 1.417 sudah terminting; agent-shape unverified). Promosi ke strong lead hanya bila: agent-shape terverifikasi + umur terverifikasi <24 jam + free% >=25% + slot terbuka + website terverifikasi.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
 "runNote0301_1111":"Run 0301: temuan baru via Boltbook - freeMinted 1.417/6.000 = 23,6% (<25%), slot terbuka, mintFree() sim bersih; agent-shape + umur + website UNVERIFIED -> watchlist-only first-read, bukan lead, tidak pernah di-preview/di-mint.",
}
# Track C updates
def updtc(name, note, **kw):
    e=TC.setdefault(name, {})
    e.update(kw)
    e["runNote0301_1111"]=note
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-11 03:01 WIB"
updtc("11-11","Run 0301: freeMinted 583->585 (+2); post musegod.ai 'Four more free mints' (minted 22:09 WIB 10 Nov; free pool 1.000 share, 471 saat mint; 140.160.000 token dari 4 mint malam itu); tetap tracked, tanpa perubahan status.",
    freeMinted=585)
for n in ["NIUBI","DROID","FUGUI-set1-991","FUGUI-set2","960E-sale"]:
    if n in TC:
        TC[n]["lastReadBlock"]=BLOCK; TC[n]["lastReadWib"]="2026-11-11 03:01 WIB"
        TC[n]["runNote0301_1111"]=f"Run 0301: freeMinted tetap ({TC[n].get('freeMinted')}); tanpa perubahan."
if "VISION" in TC:
    TC["VISION"]["totalSupply"]=3049200000000000000000000000
    TC["VISION"]["lastReadBlock"]=BLOCK; TC["VISION"]["lastReadWib"]="2026-11-11 03:01 WIB"
    TC["VISION"]["runNote0301_1111"]="Run 0301: totalSupply drift 3,0294e27 -> 3,0492e27 (totalSupply saja, tanpa free view); tanpa perubahan status."
# MOODENG update
m=TC.get("MOODENG", {})
m.update({
 "freeMinted":398, "totalMinted":398,
 "sourcifyCorrection":"KOREKSI run 0301: Sourcify exact_match TERKONFIRMASI via endpoint BENAR /v2/contract/56/ (singular) - verifiedAt 2026-11-10T16:54:09Z. Catatan run 0231 'Sourcify v2 404' adalah artefak endpoint SALAH (/v2/contracts/ plural).",
 "settleNote":"Risiko settle (post jaykojay.ai /p/drLuv9eFWi-C): TOTAL_SHARES 10.000, paid masih 0 - pool baru settle bila 9.500 paid x 0,003 BNB = 28,5 BNB masuk. Free share = angka di kertas sampai ada yang bayar duluan.",
 "status":"watchlist-only-agent-shape-unverified-2026-11-11",
 "runNote0301_1111":"Run 0301: freeMinted 338->398/500 = 79,6% (+60 dalam ~30 mnt, laju cepat); mintedBy(user)=0; paidMinted view revert (paid tidak terbaca langsung); Sourcify exact_match TERKONFIRMASI (koreksi endpoint run 0231); agent-shape TETAP UNVERIFIED (registry-bytes absen, agent fns revert) + settle butuh 28,5 BNB paid -> tetap watchlist-only, bukan lead, tidak pernah di-preview/di-mint. Deadline umur 02:00 WIB 12 Nov.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
})
TC["MOODENG"]=m
# LOWB update
l=TC.get("LOWB", {})
l.update({
 "totalFreeMinted":646, "totalMinted":657,
 "opened":0,
 "agentShapeNote":"agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F PERSIS (dikonfirmasi ulang run 0301 sebagai uint256) - agent-shaped TERKONFIRMASI. costOf()/quote()/priceOf()/getQuote() SEMUA revert; PRICE()=0,002 BNB (no-arg price view, BUKAN quote/cost per-user) -> strict S1 TETAP gagal (tanpa fungsi quote/cost).",
 "discussion":"Post musegod.ai /p/o7NX4BXQ4p1U: minted 19:14 WIB 10 Nov (value-0 sim), free pool 1.000 share, 351 claimed saat mint; deadline 2026-11-14 19:00 WIB, no pair yet.",
 "status":"watchlist-only-not-open-2026-11-10",
 "runNote0301_1111":"Run 0301: opened TETAP 0 (free mint jalan meski opened=0 - opened kemungkinan flag pool, bukan mint); totalFreeMinted 391->646/1000 = 64,6%; sharesOf(user)=0; agentRegistry persis (re-konfirmasi); strict S1 tetap gagal (tanpa quote/cost fn) + website unverified -> tetap watchlist-only-not-open, bukan lead, tidak pernah di-preview/di-mint.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
})
TC["LOWB"]=l
# FEG — sold out, excluded
TC["FEG"]={
 "sale":"0xb9d0CA9b63C564443AfE64B77ef91B3bA763e5f1",
 "token":"0x701d2eea5049eb3e9c69f7b6dff4c5f010eae54c",
 "status":"excluded-sold-out-2026-11-11",
 "freeMinted":1000, "FREE_SHARES":1000,
 "source":"Boltbook post lloyd.ai (FEG free lane is closed): claimFreeShare() reverts FreeGone, 1.000/1.000 claimed, 1 free share = 10.000 FEG; paid lane terpisah.",
 "note":"Free pool HABIS (1000/1000) - sold out; dicatat excluded, BUKAN lead, tidak dilaporkan sebagai lead.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
 "runNote0301_1111":"Run 0301: free lane CLOSED (1.000/1.000 claimed, claimFreeShare reverts FreeGone); excluded-sold-out, bukan lead.",
}
# UFO — watchlist-only (shape unverified + permit gate manusia)
TC["UFO"]={
 "sale":"0xE4059eA596392AcA14100af6CDC9481c330E2728",
 "status":"watchlist-only-shape-unverified-permit-gate-2026-11-11",
 "saleShape":"UNVERIFIED: totalSupply() 9e30 terbaca di kontrak sale (konsisten klaim artikel 9.000.000.000.000 UFO); FREE_SHARES() = 1.000; TAPI name()/symbol()/decimals()/totalSupply-token views campur (name/symbol/decimals revert), freeMinted()/freeClaimed()/freeSharesRemaining()/freeRemaining() SEMUA revert, quote()/costOf() revert, agentRegistry()/REGISTRY() revert, registry-bytes ABSEN dari bytecode -> strict S1 GAGAL (tanpa quote/cost + free view + registry) dan S2 GAGAL (tanpa name/symbol/decimals + free views + registry).",
 "sourcify":"exact_match, verifiedAt 2026-11-10T15:06:52Z (= 22:06:52 WIB).",
 "ageNote":"VERIFIED <24 jam (bounded): jendela 2 hari tutup Kamis 12 Nov 22:05 WIB (artikel The Colony) + Sourcify verifiedAt 22:06:52 WIB 10 Nov -> launch ~22:05 WIB 10 Nov; umur run ini ~4,9 jam.",
 "permitGate":"Klaim gratis BUTUH permit EIP-712 off-chain yang diterbitkan server permit SETELAH manusia memposting tentang UFO di X (aturan share-first, ditegakkan kontrak via parameter permit di claimFree/mint). Langkah manusia, BUKAN langkah agent - slot TIDAK terbuka untuk agent run ini. TIDAK PERNAH di-preview/di-mint tanpa permit.",
 "sharesOf_user":0,
 "source":"Search ZH run 0301 (The Colony: UFO LIVE, 1.000 free shares, 2-day window) + llms.txt https://ufo-bsc.netlify.app/llms.txt + probe on-chain run 0301.",
 "boundary":"WATCHLIST ONLY. Bukan track-C lead (shape gagal + slot tidak terbuka karena permit gate). Promosi hanya bila shape terverifikasi + permit bisa diperoleh agent + pool/slot terbuka + website terverifikasi.",
 "lastReadBlock":BLOCK, "lastReadWib":"2026-11-11 03:01 WIB",
 "runNote0301_1111":"Run 0301: temuan baru via sweep ZH - 1.000 free share (1/share = 3.000.000.000 UFO), jendela tutup 12 Nov 22:05 WIB, umur TERVERIFIKASI ~4,9 jam; TAPI sale-shape GAGAL (strict S1/S2) + klaim butuh permit EIP-712 off-chain pasca-postingan X manusia -> watchlist-only, bukan lead, tidak pernah di-preview/di-mint.",
}
s["last_run_wib"]="2026-11-11 03:01 WIB"
s["last_run_block"]=BLOCK
s["runNote0301_1111"]="Run 0301: TIDAK ADA kandidat/strong lead/early lead/track-C lead baru. ACORE temuan baru via Boltbook TAPI SAME-OWNER-DISCARDED (owner 0x1103 = gelombang costOf/mintsLeft 11 kontrak, dibuang 2026-11-06; free% 76,15% + slot terbuka + costOf 0 tidak mengubah status). SAKURA watchlist-only first-read (23,6% <25%, agent-shape + umur + website unverified). FEG sold out 1000/1000 (excluded). UFO watchlist-only (shape gagal + permit gate manusia). MOODENG 398/500, LOWB 646/1000, NIGHTFORGE 34,95% tetap gate-blocked. RIMEVAULT 24,15% + MYCELIX 24,25% masih <25%; velocity semua GAGAL. Scan Ankr FAST-FAIL (401). Binanceai launched=0 (tetap). DIAM (tidak ada laporan chat)."
s["runNote0301_1111_scan"]="Run 0301 scan: PRE-FLIGHT Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 31,8 dtk (head 132837050; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09, kini ~37,5 jam). Scan leg FAST-FAIL. Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~324.500 blok dan tumbuh). Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini)."
s["runNote0301_1111_binanceai"]="Run 0301 track-B: binanceai.fun launched()=0, tokenClaimed(user)=0, token balanceOf(user)=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong."
s["runNote0301_1111_discovery"]="Run 0301 discovery: Sourcify feed 20 terbaru (verified 19:26:43-20:01:59Z), 1 baru vs hot-leg-seen (0x88D7624E..., exact_match 20:01:59Z): semua view revert (bukan ERC-721/ERC-20 shaped), registry-bytes False -> 0 sale-shape, 0 early lead. Boltbook EN 200 45.389 byte + ZH 200 45.179 byte, 9 alamat unik, 0 baru vs snapshot+hot-leg-seen (ACORE/SAKURA/FEG dari isi post, bukan dari daftar alamat front page). Post baru: musegod.ai 'Four more free mints' (LOWB, HAJIMI free 500/500 GONE, BARA free 50/50 GONE, 11-11 585); qlp.ai 'Two free lanes' (ACORE 487->479 freeLeft, SAKURA 1.417/6.000); jaykojay.ai MOODENG skip (settle butuh 28,5 BNB paid); receive.ai WNO (1.843 free tersisa; share-first X; user SUDAH klaim 10 Nov - tanpa aksi); ghostagent.ai GangDotFun tanpa Agent-ID gate; 9dasand72.ai sensus 04:51 WIB (ClafEye 6.227, THYRK 4.095, RIMEVAULT 480). Sweep EN+ZH: Agentic Gangster free sold out 111/111 (excluded); UFO (baru, watchlist-only); NOVRA free habis (AirdropBuzz); AgentForge/Pixel Fox/Gloomies/Oathbots/Horus lama (Okt, age-excluded). Rute 6: Odaily 200 (264.078 byte) + PANews 200 (119.487 byte), 0 keyword Agent ID/free mint/free share. Bridge: 116 kontrak, mtime 2026-11-08 18:21:53 WIB (STALE); tidak ada temuan pelengkap baru."
s["runNote0301_1111_age_exclusions"]="Run 0301 age-exclusions (aturan <24 jam): window 02:31->03:01 WIB: 0 BARU. Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; RIMEVAULT ~21:27 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. ACORE/SAKURA launch UNVERIFIED (bukan age-excluded, watchlist-only). Dragon Agent TIDAK di-exclude (launch UNVERIFIED, preseden ditahan 10 Nov). Tidak ada item yang dihapus dari snapshot."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
# ACORE -> same-owner-discards.json
d=json.load(open(f"{BASE}/same-owner-discards.json"))
if not any(e.get("contract","").lower()=="0xf4bacf30fb8f69373f63d99c657f53dd7774af1d" for e in d):
    d.append({
      "contract":"0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
      "discarded_wib":"2026-11-11T03:01:00+07:00",
      "owner":"0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd",
      "owner_source":"owner() fresh run 0301 + komentar Boltbook (cyroo.ai/cukim.ai)",
      "project":"ACORE / Agent Core",
      "reason":"owner 0x1103 sama dengan gelombang costOf/mintsLeft 11 kontrak yang dibuang 2026-11-06 (Toucan Play, jelly.exe, Los Flamingos, Moonhowlers, Counting Sheep, Tusk & Trunk, getpuffr, Hippo Social Club, LLAMA DRAMA, Danger Noodles, SHACHO CLUB) - pola sama: costOf()/mintsLeft, mint pertama gratis, price()=0.0002 BNB utk mint ke-2+. Ditemukan via Boltbook run 0301; free% 76,15% + slot terbuka TIDAK mengubah status. Discard di level triase = jangan laporkan sebagai lead, jangan eksekusi."
    })
    json.dump(d, open(f"{BASE}/same-owner-discards.json","w"), indent=1)
    print("ACORE added to same-owner-discards.json; total entries:", len(d))
else:
    print("ACORE already in discards")
print("MERGE DONE; contracts:", len(C), "track_c:", len(TC))
