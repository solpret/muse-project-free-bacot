#!/usr/bin/env python3
"""Merge run 0331 readings into snapshot. Read-only on other state; writes snapshot only."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-11-0331-reread.json"))
BLOCK=r.get("block")  # 132841039
WIB="2026-11-11 03:31 WIB"
contracts=snap.setdefault("contracts",{})
# --- route 1: update reread contracts (only non-None values) ---
for name,d in r.get("reread",{}).items():
    e=contracts.setdefault(name,{"address":d.get("address"),"status":"watchlist-only-first-read-2026-11-11"})
    for k in ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"]:
        if d.get(k) is not None:
            e[k]=d[k]
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]=WIB
# agentFreeUsed mirrors totalSupply for SMITH-family early leads where free==total
for name in ["REWINDCLUB","LCDSPRITE","RIMEVAULT","MYCELIX"]:
    if name in contracts and contracts[name].get("totalSupply") is not None:
        contracts[name]["agentFreeUsed"]=contracts[name]["totalSupply"]
# velocity notes (interval 0301->0331 ~30 mnt)
vel={
 "REWINDCLUB":(409,414,20.7),"LCDSPRITE":(461,465,23.25),"RIMEVAULT":(483,491,24.55),
 "MYCELIX":(485,494,24.7),"SOLDERCATS":(456,457,22.85),"NIGHTFORGE":(702,702,34.95),
 "Pico Alcazar":(273,277,None),"Tiling Hammock":(265,266,None),"Hexel Pantry":(276,277,None),
 "STALL":(1640,1647,None),"Arcane Stones":(648,650,None),"Cosmic Sentinel":(391,395,None),
 "ORBITJANITOR":(637,638,None),"EMBERANVIL":(1032,1034,None),"BYTEBLOOM":(574,575,None),
 "Dragon Agent":(906,906,None),
}
for name,(old,new,pct) in vel.items():
    if name not in contracts: continue
    d=new-old
    pct_s=f" free {pct}% dari cap 2.000" if pct is not None else ""
    contracts[name]["runNote0331_1111"]=(
        f"Run 0331: totalSupply {old}->{new} (+{d}/~30 mnt, ~{d/30:.2f}/mnt, <20 token) velocity GAGAL;"
        f"{pct_s}; slot user terbuka; tetap {contracts[name].get('status')} (tanpa promosi).")
# NIGHTFORGE gate note
contracts["NIGHTFORGE"]["runNote0331_1111"]=(
    "Run 0331: totalSupply tetap 702, agentFreeUsed 699/2.000 = 34,95% (kaki strong-leg % tetap terpenuhi), "
    "slot user terbuka, gate TETAP BLOCKED (recheck terakhir run 0301: situs masih infografis medis, 0 kecocokan kontrak; "
    "tidak di-recheck ulang run ini, 30 mnt sesudahnya). TIDAK di-mint. Deadline umur 2026-11-11 14:37 WIB.")
# --- route 5: track_c re-read ---
tc=snap.setdefault("track_c",{})
for name,d in r.get("track_c",{}).items():
    e=tc.get(name)
    if not isinstance(e,dict): continue
    for k in ["totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"]:
        if d.get(k) is not None:
            e[k]=d[k]
    e["lastReadWib"]=WIB
# --- new watchlist entries ---
contracts["WORKER"]={
 "address":"0xbead62a6c6b9a43ece68645f2328e0ebd015dbf2","name":"WORKER","symbol":"WORKER","kind":"ERC721",
 "status":"watchlist-only-first-read-2026-11-11","totalSupply":353,"totalMinted":353,"MAX_SUPPLY":100000,
 "PRICE":200000000000000,"mintOpen":None,"balanceOf_user":0,"freeAvailable_user":1,"freeUsed_user":0,
 "agentIdRegistry":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "owner":"0x41a192cb1cc16cc1ff98dfa9c338f436b41fa5b3",
 "website":"https://agent-worker.pages.dev",
 "websiteEvidence":"Metode D/H/I: tokenURI #1 image host agent-worker.pages.dev; config.js situs mencetak kontrak persis 0xBeAD62a6C6B9a43eCE68645F2328e0eBD015dBf2. Gate website PASSED.",
 "launchNote":"UNVERIFIED: Boltbook ayloyd.ai 2026-11-11 03:24 WIB (344/100.000, blok 132.839.640) tanpa waktu launch dinyatakan; Sourcify verifiedAt 2026-11-10T16:21:55Z BUKAN launch time; first mint tidak terkoroborasi (Ankr getLogs mati, RPC publik tolak eth_getLogs).",
 "freePctNote":"UNVERIFIED: tidak ada free counter/cap view (freeAvailable(address) bool per-wallet saja); totalMinted 353/100.000 = 0,35% total BUKAN % free.",
 "userSlotNote":"Slot TERBUKA (freeAvailable(user)=1, freeUsed(user)=0, balanceOf(user)=0, baca segar run 0331).",
 "firstSeenWib":"2026-11-11 03:31 WIB","firstSeenBlock":132841039,"lastReadBlock":BLOCK,"lastReadWib":WIB,
 "note":"Temuan BARU via Boltbook front page EN+ZH run 0331 (post ayloyd.ai, kontrak kedua bernama WORKER; kontrak WORKER pertama 0x45527ff... TIDAK ada di snapshot). Agent-shaped (registry persis) + website PASSED + slot terbuka, TAPI umur + free% UNVERIFIED -> watchlist-only, BUKAN early lead (first mint bukan run ini, 344 sudah ter-mint saat pertama terlihat), BUKAN strong lead, TIDAK di-preview/TIDAK di-mint. Risiko dicatat post: owner EOA bisa setImageBaseURI/setUpgradePrice/withdraw BNB.",
 "xVerified":False,"velocityVerified":False,"velocityLegPasses":False}
contracts["Skywe Legion"]={
 "address":"0x7256f522e8867de57ea747eeaf83d604d08c47c2","name":"Skywe Legion","symbol":"LEGN","kind":"ERC721",
 "status":"watchlist-only-first-read-2026-11-11","totalMinted":339,"maxSupply":5555,"mintOpen":1,
 "maxPerWallet":10,"paidPrice":500000000000000,"mintedBy_user":0,"balanceOf_user":None,
 "REGISTRY":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "owner":"0x7999b0492bfa8007729e80e97d0d10c5bf02b1f2",
 "website":None,
 "launchNote":"UNVERIFIED: Boltbook takoyaki.ai re-verifikasi 03:25 WIB (314/5.555, blok 132.839.266) tanpa waktu launch dinyatakan; Sourcify verifiedAt 2026-11-10T18:27:49Z BUKAN launch time; first mint tidak terkoroborasi.",
 "freePctNote":"UNVERIFIED: tidak ada free counter/cap view (costOf family); totalMinted 339/5.555 = 6,1% total BUKAN % free.",
 "userSlotNote":"Slot diduga TERBUKA (mintedBy(user)=0, mintOpen=1; costOf(user,1)=0 menurut post takoyaki.ai — panggilan costOf langsung run ini gagal, dilabeli post-corroborated, bukan verifikasi langsung).",
 "firstSeenWib":"2026-11-11 03:31 WIB","firstSeenBlock":132841039,"lastReadBlock":BLOCK,"lastReadWib":WIB,
 "note":"Temuan BARU via Boltbook front page EN run 0331. Agent-shaped (REGISTRY persis + agentGate + costOf), owner 0x7999b049... TIDAK ada di same-owner-discards.json (61 entri). Umur + free% + website UNVERIFIED -> watchlist-only, BUKAN early lead (first mint bukan run ini), BUKAN strong lead, TIDAK di-preview/TIDAK di-mint.",
 "xVerified":False,"velocityVerified":False,"velocityLegPasses":False}
contracts["SOLACE"]={
 "address":"0x0759c26e1fbe339a7e4282f29b719f56e72f9a1b","name":"SOLACE","symbol":"SOLACE","kind":"ERC20",
 "status":"checked-not-lead-paid-only-2026-11-11",
 "firstSeenWib":"2026-11-11 03:31 WIB","lastReadWib":WIB,
 "note":"Boltbook qlp.ai run 0331: 'free' mint SOLACE ternyata biaya 0,0002 BNB (revert + kode situs sepakat); ABI: FREE_MINT_FEE/PAID_MINT_FEE, window tutup 14 Nov 2026 01:05 WIB, 4.444 mint x 135.000 SOLACE. BUKAN gratis -> excluded paid-only, tidak dilaporkan sebagai lead, tidak masuk watchlist aktif."}
contracts["CandleGame-0x05f23bfe"]={
 "address":"0x05f23bfeb3115d6e1905d039f2c70e6928846956","name":"\u70ed\u706b\u516b\u5366","symbol":"\u70ed\u706b","kind":"game-contract",
 "status":"watchlist-only-not-launched-2026-11-11","FREE_QUOTA":500,"freeUsed":304,"totalBoarded":304,
 "gameStart":1794574800,"gameEnd":1794920400,"registry":"0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
 "freeClaimed_user":0,
 "firstSeenWib":"2026-11-11 03:31 WIB","lastReadWib":WIB,
 "note":"Alamat dari Boltbook front page (konteks post tidak terlacak di teks EN/ZH). Kontrak GAME (pods/oil/heartbeat/claim), BUKAN NFT mint: gameStart on-chain 2026-11-13 20:00 WIB (BELUM launch), gameEnd 2026-11-17 20:00 WIB, FREE_QUOTA 500, freeUsed 304, registry persis, freeClaimed(user)=0. Bukan kandidat track A/B/C; dicatat sebagai upcoming watchlist-only, TIDAK di-preview/TIDAK di-mint."}
contracts["0x8269Ea1629644219a88dbB053D34E8e877596B00"]={
 "address":"0x8269Ea1629644219a88dbB053D34E8e877596B00","kind":"unknown",
 "status":"checked-not-lead-unverified-2026-11-11",
 "firstSeenWib":"2026-11-11 03:31 WIB","lastReadWib":WIB,
 "note":"Alamat dari Boltbook front page run 0331 (konteks post tidak terlacak). eth_getCode ada (4.536 byte) TAPI Sourcify 404 (unverified, tanpa ABI) -> agent-shape tidak bisa dicek. Dicatat saja, tidak dilaporkan, tidak masuk watchlist aktif."}
# ORYN track_c entry
tc["ORYN-sale"]={
 "sale":"0x96135a41FA155752dc7154CDcaA480f2fBEC1493","token":"0x9599fd07ad1de244ede8e11680102d96988702f8",
 "name":"ORYN sale (round-based claimFree)","status":"watchlist-only-paused-2026-11-11",
 "saleShape":"VARIAN claimFree/freePoolRemaining (S1/S2 kosakata mint/quote MELEWATKAN varian ini — flag hot-leg 0309): claimFree() no-arg + freePoolRemaining + FREE_POOL + hasAgentId + identityContract; TANPA quote/cost fn",
 "FREE_POOL":45000000000,"freePoolRemaining":44985870000,"freePoolPaidOut":14130000,
 "currentFreeRound":1,"freeClaimsThisRound":10,"CLAIMS_PER_FREE_ROUND":5000,
 "LOT_PRICE":1400000000000000,"totalLotsSold":0,"liquidityOpened":0,"paused":1,
 "identityContract":"0xcd245b57f7b0f65f03123226603a4c69393ab609",
 "hasAgentId_user":1,"hasFreeClaimed_user":0,
 "launchNote":"UNVERIFIED: Sourcify verifiedAt 2026-11-10T20:08:47Z BUKAN launch time; first claim tidak terkoroborasi (BscScan API non-JSON, Ankr getLogs mati).",
 "websiteNote":"UNVERIFIED: search alamat kontrak + 'ORYN' 0 hit relevan (metode A/G run 0331); hasil hanya token ORN/ORY lain.",
 "firstSeenWib":"2026-11-11 03:31 WIB","lastReadWib":WIB,
 "note":"Temuan hot-leg 0309, diteruskan ke job utama 0331. Free pool ~99,99% sisa + slot user terbuka (hasFreeClaimed=0, hasAgentId=1), TAPI paused=1 (claimFree TIDAK terbuka saat ini) + umur + website UNVERIFIED -> watchlist-only, BUKAN track-C lead, TIDAK di-preview/TIDAK di-mint. Pantau: unpause + verifikasi umur/website."}
# run notes
snap["runNote0331_1111"]=(
 "Run 0331 (2026-11-11 03:31-~03:5x WIB, blok re-read 132841039): DIAM (tidak ada laporan chat). "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru, 0 track-B claim baru/dibuka. "
 "BARU watchlist-only: WORKER/tORKER 0xbead62a6... (Boltbook ayloyd.ai 03:24 WIB; agent-shaped registry persis + website PASSED via agent-worker.pages.dev config.js + slot terbuka; umur + free% UNVERIFIED; totalSupply 353/100.000) "
 "dan Skywe Legion 0x7256f522... (Boltbook takoyaki.ai; REGISTRY+agentGate+costOf; totalMinted 339/5.555; owner 0x7999b049... TIDAK di discards; umur + free% + website UNVERIFIED). "
 "SOLACE 0x0759c26e... = paid-only (free mint biaya 0,0002 BNB) -> excluded, tidak dilaporkan. "
 "Game 0x05f23bfe... (FREE_QUOTA 500, gameStart 2026-11-13 20:00 WIB, belum launch) -> watchlist-only-not-launched. "
 "0x8269Ea16... Sourcify unverified -> dicatat saja. "
 "ORYN sale 0x96135a41... masuk track_c watchlist-only-paused (paused=1, pool ~99,99% sisa, umur+website UNVERIFIED). "
 "Prioritas: RIMEVAULT 491/2.000=24,55% (+8), MYCELIX 494/2.000=24,7% (+9) — masih <25%, velocity GAGAL (<20 token); "
 "SOLDERCATS 457/2.000=22,85% (+1); REWINDCLUB 414 (20,7%), LCDSPRITE 465 (23,25%); NIGHTFORGE tetap 702, gate-blocked, deadline umur 14:37 WIB. "
 "Track_c: 11-11 freeMinted 585->586; VISION drift; 0 lead baru. 0 eksekusi.")
snap["runNote0331_1111_scan"]=(
 "Run 0331 scan FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 35,4 dtk (head 132842215; "
 "kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09, kini ~38 jam). Scan leg TIDAK dijalankan (amendemen 2026-11-06). "
 "Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~329.650 blok dan tumbuh). 5c dilewati (tanpa output scan).")
snap["runNote0331_1111_discovery"]=(
 "Run 0331 discovery: Boltbook EN 45.722 byte (HTTP 200 — PULIH setelah 6 run gagal 0-byte berturut-turut) + ZH 45.897 byte; "
 "9 alamat unik front page, 2 baru vs snapshot (WORKER bead62, Skywe Legion) + 5 dicek (SOLACE paid-only, game 05f23bfe, 0x8269Ea16 unverified, 0xe0FeCB4A tanpa code/EOA, STALL/RIMEVAULT/BOLT sudah di snapshot). "
 "Sourcify feed 20 terbaru: 1 baru vs hot-leg-seen 0xcd245B57... (verified 20:32:00Z) = identityContract ORYN, bukan sale-shape. "
 "Odaily 264.078 byte + PANews 119.455 byte, 0 keyword Agent ID/free mint/free share. Bridge scan-bridge.json mtime 2026-11-08 18:21:53 WIB (STALE, tidak berubah); tidak ada temuan pelengkap baru.")
snap["runNote0331_1111_binanceai"]=(
 "Run 0331 track B: binanceai.fun launched()=0, tokenClaimed(user)=0, token balanceOf(user)=0 — TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong.")
snap["runNote0331_1111_age_exclusions"]=(
 "Run 0331 age exclusions: 0 BARU (window 03:01->03:31 WIB). Deadline umur berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; "
 "RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); "
 "MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. WORKER/Skywe Legion launch UNVERIFIED (watchlist-only, bukan age-excluded). "
 "Tidak ada item yang dihapus dari snapshot.")
snap["last_run_wib"]=WIB
snap["timestamp_wib"]=WIB
with open(f"{BASE}/onchain-snapshot.json","w") as f:
    json.dump(snap,f,indent=1)
print("MERGED ok. contracts:",len(snap["contracts"]),"track_c:",len(snap["track_c"]))
print("WORKER in snapshot:", "WORKER" in snap["contracts"], "| Skywe:", "Skywe Legion" in snap["contracts"], "| ORYN tc:", "ORYN-sale" in snap["track_c"])
