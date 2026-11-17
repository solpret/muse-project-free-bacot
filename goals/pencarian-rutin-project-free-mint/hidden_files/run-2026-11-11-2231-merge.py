#!/usr/bin/env python3
"""Merge run 2231 (scheduled 2026-11-11 22:31 WIB) into onchain-snapshot.json.
Inputs: run-2026-11-11-2231-reread.json, -legs.json, -triage.json,
-verify-new.json, -shape-new.json, abi-agcr.json + AGCR deep-dive reads.
AGCR age verdict is filled from the BscScan browser read (creation txn time);
see runNote2231_1111_agcr. Writes snapshot (with .bak). No preview/mint here.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2231-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-2231-legs.json"))
triage = json.load(open(BASE + "run-2026-11-11-2231-triage.json"))
verify = json.load(open(BASE + "run-2026-11-11-2231-verify-new.json"))
shape_new = json.load(open(BASE + "run-2026-11-11-2231-shape-new.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2231-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block")
TS = "2026-11-11 22:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict): return None
    old = e.get("totalSupply")
    if old is None or new_supply is None: return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread["reread"].items():
    if name not in C: continue
    e = C[name]
    if d.get("_batch_fail"):
        batch_fail.append(name)
        e["runNote2231_1111"] = ("Run 2231 (blok %s): baca batch GAGAL (transport) - nilai lama "
            "dipertahankan, BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"): vel_pass.append((name, r))
        elif r: vel_fail.append((name, r))
    else:
        e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    for k in ("totalMinted","freeMinted","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    if d.get("totalSupply") is not None: e["totalSupply"] = d["totalSupply"]

def note(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote2231_1111"] = text

st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st["status"] = "strong-lead-gate-blocked-2026-11-11"
    note("Stampooor Stamp Packs",
     "Run 2231: freeMinted 866/1200 = 72,17% (TETAP, tidak berubah vs run 2201); umur TERVERIFIKASI <24 jam "
     "(mintStart 1794362419 = 11 Nov 09:00:19 WIB; deadline ~09:00 WIB 12 Nov); slot user TERBUKA (balanceOf 0, "
     "mintOpen 1). GATE tetap gagal (situs tidak load; gate-blocked-recheck menangani cek ulang). TIDAK di-preview, "
     "TIDAK di-mint, TIDAK dilaporkan ulang (tanpa perubahan tier).")
note("AgentPals",
     "Run 2231 (blok 132993127): freeMinted 300/300 (free pool SOLD OUT), totalMinted 301; balanceOf user 1. TIDAK dilaporkan ulang.")
note("MYCELIX",
     "Run 2231: totalSupply 622->623 (+1, velocity GAGAL). Deadline 24 jam sudah lewat run 2201; status minted-by-user -> TETAP DILACAK (bukan age-excluded).")
note("REWINDCLUB",
     "Run 2231: totalSupply 563 flat, velocity GAGAL. Deadline 24 jam sudah lewat run 2201; status minted-by-user -> TETAP DILACAK.")
note("LCDSPRITE",
     "Run 2231: totalSupply 583 flat, velocity GAGAL. Deadline 24 jam sudah lewat run 2201; status minted-by-user -> TETAP DILACAK.")
note("RIMEVAULT",
     "Run 2231: totalSupply 1068->1079 (+11, velocity GAGAL). Deadline 24 jam sudah lewat run 2131; status minted-by-user -> TETAP DILACAK.")
note("HANAMI BLOOM",
     "Run 2231: totalSupply 110 flat (baca OK run ini), velocity GAGAL. Status early-lead-reported-2026-11-11; deadline ~12:59 WIB 12 Nov. TIDAK di-preview/dimint.")
note("RAMRAIDERS",
     "Run 2231: totalSupply 568 flat, freeMinted 568/7777 = 7,30%, velocity GAGAL. Umur masih UNVERIFIED; X/website UNVERIFIED. Tetap EARLY, tanpa promosi.")
note("STALL",
     "Run 2231: totalSupply 1987->1990 (+3, velocity GAGAL). Free% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED. Tetap EARLY.")
note("BYTEBLOOM",
     "Run 2231: totalSupply 842->848 (+6, velocity GAGAL). Status minted-by-user-2026-11-10; tanpa perubahan.")
note("Twill Fullery",
     "Run 2231: totalSupply 176->203 (+27, 0,9/mnt vs prev 0,2333 = 3,86x) -> VELOCITY LOLOS TAPI TIDAK promosi: "
     "free% UNVERIFIED, umur UNVERIFIED, X/website UNVERIFIED, status early-lead-reported-2026-11-11. Tetap EARLY.")
note("Pearl Sound",
     "Run 2231: totalSupply 0->73 = BACA SUKSES PERTAMA (snapshot lama 0 = belum pernah terbaca, BUKAN +73 dalam 30 mnt); "
     "velocity TIDAK lulus (prev rate negatif). free% UNVERIFIED, umur UNVERIFIED (launchNote: tidak ada stated launch time; "
     "first mint tidak terkoroborasi via logs, Ankr mati). Tetap EARLY.")
note("Chestnut Common",
     "Run 2231: totalSupply 0->67 = BACA SUKSES PERTAMA (snapshot lama 0, BUKAN +67 dalam 30 mnt); velocity TIDAK lulus "
     "(prev rate negatif). free% UNVERIFIED, umur UNVERIFIED. Tetap EARLY.")

# --- verify-new early leads ---
v = verify.get("verify", {})
def vnote(name, text):
    if isinstance(C.get(name), dict):
        C[name]["runNote2231_1111"] = text
        e = C[name]
        d = v.get(name, {})
        for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user","freeUsed_user","freeUsedBy_user","mintedBy_user","freePoolSize","totalFreeCount","firstFreeUsed","paidMinted","mintStart","mintOpenedAt"):
            if d.get(k) is not None: e[k] = d[k]
        e["lastReadBlock"] = verify.get("block"); e["lastReadWib"] = TS
vnote("MECHA",
     "Run 2231 (blok 132993975): totalMinted 333->357, freeClaimed 357/4444 = 8,03%; slot TERBUKA (balanceOf 0, freeUsedBy 0, freeAvailable 2). "
     "Umur MASIH UNVERIFIED; X UNVERIFIED; website TIDAK DITEMUKAN. Tetap EARLY, tanpa promosi.")
vnote("BUCKET",
     "Run 2231 (blok 132993975): totalSupply 279->394, totalFreeCount 394/3333 = 11,82%; mintOpenedAt 21:16:46 WIB (umur TERVERIFIKASI <24 jam); "
     "slot TERBUKA (balanceOf 0, freeUsed 0, isAgent 1). Website + X + diskusi BELUM terverifikasi; jauh dari 50% / >70%. Tetap EARLY.")
vnote("MOONDRILL",
     "Run 2231 (blok 132993975): totalSupply 30->52, firstFreeUsed 52/2000 = 2,60%; mintStart 21:10:25 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
vnote("0x2e50",
     "Run 2231 (blok 132993975): totalSupply 30->52, firstFreeUsed 52/2000 = 2,60%; mintStart 21:00:23 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
vnote("CRTSAINTS",
     "Run 2231 (blok 132993975): totalSupply 38->48, firstFreeUsed 48/2000 = 2,40%; mintStart 20:50:23 WIB (umur TERVERIFIKASI); paidMinted 0, slot TERBUKA. Tetap EARLY.")
naomi = C.get("checked-0xC7Ad-2001")
if isinstance(naomi, dict):
    d = v.get("NAOMI", {})
    for k in ("totalMinted","freeMinted","mintOpen","balanceOf_user"):
        if d.get(k) is not None: naomi[k] = d[k]
    naomi["runNote2231_1111"] = ("Run 2231 (blok 132993975): verifikasi segar - totalMinted 782, freeMinted 777/777 = free pool TETAP HABIS. "
        "Status checked-free-pool-sold-out TIDAK berubah; TIDAK dilaporkan.")

# --- AGCR (new; deep-dive run 2231; age verdict from BscScan browser read) ---
agcr_age = ("UNVERIFIED - BscScan browser read BLOCKED by Cloudflare bot wall (2 challenge attempts, 22:48-22:53 WIB, "
    "Ray ID a58e774dff3a9236, no data); OKLink shows no tx records; eth_getLogs dataseed -32005 / publicnode -32005 / "
    "llamarpc+meowrpc empty; Ankr 401; eth_getCode history missing-trie-node; site states no launch time; "
    "Sourcify verifiedAt not in recent-100 (verified before 14:16Z) and verifiedAt is NOT launch time")
C["AGCR"] = {
    "address": "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "name": "Aegis Core Protocol",
    "symbol": "AGCR",
    "kind": "ERC721",
    "totalSupply": 2391,
    "totalMinted": 2425,
    "freeMinted": 2371,
    "FREE_SUPPLY": 2400,
    "MAX_FREE_SUPPLY": 2400,
    "MAX_SUPPLY": 6000,
    "paidMinted": 54,
    "mintOpen": 1,
    "freePctVerified": 98.79,
    "quote_user_1": 0,
    "hasFreeClaimed_user": 0,
    "totalClaimedByWallet_user": 0,
    "walletMintedCount_user": 0,
    "balanceOf_user": 0,
    "website": "https://aegiscore.surge.sh",
    "websiteGate": "PASS",
    "websiteEvidence": "WEBSITE() on-chain = https://aegiscore.surge.sh; site prints exact contract 0x5491f2341A178D35c7Bbb82bD1ed37330f3D01cC; /llms.txt prints exact contract + Sourcify exact_match + BscScan links; tokenURI(1) external_url = same site; contractURI names Aegis Core Protocol.",
    "xVerified": False,
    "discussion": "Boltbook board post 22:24 WIB 11 Nov ('AGCR moving again', totalSupply 2.327 at check) - public mention, same-day.",
    "ageStatus": agcr_age,
    "launchNote": "Umur BELUM TERVERIFIKASI run ini: no mintStart view; site tidak menyatakan launch time; eth_getLogs via dataseed -32005 (limit exceeded, bahkan window 100 blok) / publicnode -32005 rate-limit / llamarp+meowrpc empty; Ankr 401; eth_getCode historis missing-trie-node (node pruned); BscScan live-browser BLOCKED Cloudflare bot wall (2 challenge attempts 22:48-22:53 WIB, Ray ID a58e774dff3a9236); OKLink 'no transaction records'; Sourcify verifiedAt tidak masuk feed-100 terbaru (verified sebelum 14:16Z) dan verifiedAt BUKAN launch time. Boltbook board post 22:24 WIB hari ini menyebut AGCR (diskusi, bukan launch time).",
    "lastReadBlock": verify.get("block"),
    "lastReadWib": TS,
    "runNote2231_1111": "Run 2231 (blok 132993975): freeMinted 2371/2400 = 98,79% TERVERIFIKASI (>70%); slot user TERBUKA TERVERIFIKASI (quote(user,1)=0, hasFreeClaimed=0, walletMintedCount=0, balanceOf 0); WEBSITE GATE LOLOS (aegiscore.surge.sh mencetak kontrak persis; WEBSITE() on-chain sama). AGE: " + agcr_age + ". X UNVERIFIED (hanya mention Boltbook 22:24 WIB). BUKAN strong lead sampai umur terverifikasi <24 jam - TIDAK di-preview, TIDAK di-mint. Pool tersisa 29; bila sold out sebelum umur terverifikasi -> excluded sold-out."
}

# --- WFPASS (pre-launch; hot-leg 2159 S1, verified run 2231) ---
TC["WFPASS"] = {
    "address": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
    "status": "watchlist-only-prelaunch-2026-11-11",
    "name": "WFPASS",
    "kind": "ERC721-sale-S1",
    "saleShape": "PASS (S1): mint + quote + freeAvailable/freeClaimed/freeMinted + agent ref (AGENT_ID 552192074493313695968015109214105588393044541999)",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0,
    "FREE_SUPPLY": 500, "MAX_SUPPLY": 1500,
    "mintOpen": 0, "balanceOf_user": 0, "freeClaimed_user": 0,
    "freeAvailable_user": 1,
    "saleStart": 1794438000, "saleEnd": 1794697200,
    "saleStartWib": "2026-11-12 06:00 WIB", "saleEndWib": "2026-11-15 06:00 WIB",
    "price_paid": "0.002 BNB",
    "lastReadBlock": verify.get("block"), "lastReadWib": TS,
    "runNote2231_1111": "Run 2231 (blok 132993975): PRE-LAUNCH, BUKAN lead - totalSupply 0, freeMinted 0/500, mintOpen 0; saleStart 12 Nov 06:00 WIB, saleEnd 15 Nov 06:00 WIB; quote(user,1) reverts 'sale has not started'. Slot open (freeAvailable=1). Pantau pembukaan 06:00 WIB 12 Nov."
}

# --- S1-6C50 (hot-leg 2219 S1; age unverified) ---
TC["S1-6C50"] = {
    "address": "0x6C504A7B392b1D57845F57d2abb5C4d49211Aa7f",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "kind": "ERC721-sale-S1",
    "saleShape": "PASS (S1): mint + quote + free views + agentIdRegistry = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "totalMinted": 53, "freeMinted": 53, "FREE_CAP": 100,
    "freePctVerified": 53.0,
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": 0,
    "price_paid": "0.0028 BNB",
    "ageStatus": "UNVERIFIED",
    "launchNote": "Umur UNVERIFIED: no mintStart view; first-seen job 22:19 WIB (freeMinted 3) -> 53 pukul ~22:45 WIB; Sourcify verifiedAt 15:07-15:21Z BUKAN launch time; first-mint via logs tidak bisa (Ankr 401, dataseed -32005).",
    "lastReadBlock": verify.get("block"), "lastReadWib": TS,
    "runNote2231_1111": "Run 2231 (blok 132993975): freeMinted 53/100 = 53% (naik dari 3 pukul 22:19 WIB); slot TERBUKA (balanceOf 0, freeClaimed 0); sale-shape S1 LOLOS. BUKAN track-C lead: umur UNVERIFIED. Website/X BELUM dicek (bukan lead). Pantau umur + pool (47 tersisa)."
}

# --- BB-7c71 (Boltbook-new 2219; S1; age unverified) ---
TC["BB-7c71"] = {
    "address": "0x7c71b7158b9b3122f35570d6b737ea4a2db8e205",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "kind": "ERC721-sale-S1",
    "saleShape": "PASS (S1): mint + quote + free views (free_mint_bonus/freeminted/freeused) + agent ref, 163 fns",
    "totalSupply": 489, "freeMinted": 489, "MAX_SUPPLY": 7777,
    "freePctVerified": 6.29,
    "balanceOf_user": 0, "freeUsed_user": 0,
    "ageStatus": "UNVERIFIED",
    "launchNote": "Umur UNVERIFIED: first-seen Boltbook run 2219; semua view gagal baca run 2219 (RPC), baca OK run 2231; no mintStart; first-mint via logs tidak bisa (Ankr 401, dataseed -32005).",
    "lastReadBlock": verify.get("block"), "lastReadWib": TS,
    "runNote2231_1111": "Run 2231 (blok 132993975): totalSupply 489, freeMinted 489/7777 = 6,29%; slot TERBUKA (balanceOf 0, freeUsed 0). BUKAN track-C lead: umur UNVERIFIED + jauh dari tier. Website/X BELUM dicek."
}

# --- SPRINT Season Pass (feed-new 2231; agent-shaped, pre-launch) ---
C["SPRINT Season Pass"] = {
    "address": "0xa25c408B5CB0d9Ad074217A259292A6b139A8230",
    "status": "watchlist-only-prelaunch-2026-11-11",
    "name": "SPRINT Season Pass",
    "symbol": "SPASS",
    "kind": "ERC721",
    "registry()": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "agentShape": "CONFIRMED (registry() = Agent ID registry; freeCap constant)",
    "passesSold": 0,
    "passCap": 20,
    "freeCap": 5,
    "globalCap": 5000,
    "PASS_PRICE": 5000000000000000000,
    "seasonStart": 1794560400,
    "seasonStartWib": "2026-11-13 16:00 WIB",
    "poolBuilt": 0,
    "lastReadWib": TS,
    "runNote2231_1111": "Run 2231: BARU dari Sourcify feed (verified 15:20-15:37Z). Agent-shaped TERVERIFIKASI (registry() = 0x60B926...; freeCap 5). PRE-LAUNCH: passesSold 0, poolBuilt 0, seasonStart 13 Nov 16:00 WIB. BUKAN early lead (belum ada first mint). Free pool hanya 5 pass. Pantau pembukaan season."
}

# --- feed-new checked (not sale / not early) ---
TC["Feed-0x5aFC9780"] = {"address": "0x5aFC9780B628FEA4202580DEa23481a9a030956A", "status": "checked-not-sale-shape-2026-11-11",
    "note": "Run 2231 Sourcify feed: token, 11 fns, TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja.", "lastReadWib": TS}
TC["Feed-0x040C3139"] = {"address": "0x040C313980d4F96c66CB281FDD0A7F1F7a02EeCe", "status": "checked-not-sale-shape-2026-11-11",
    "note": "Run 2231 Sourcify feed: 29 fns, mint+quote+agent ref TAPI TANPA free view -> GAGAL S1 (free view wajib). Token, bukan NFT -> BUKAN early lead. Dicatat checked saja.", "lastReadWib": TS}
TC["Feed-0xffb75565"] = {"address": "0xffb755653b9638beeb23d8a451b9ddcf003b7777", "status": "checked-unverified-2026-11-11",
    "note": "Run 2231 Boltbook-new: Sourcify TIDAK mengembalikan ABI (not verified / fn_count 0) -> shape UNKNOWN, BUKAN agent-shaped. Dicatat checked saja, tidak masuk snapshot lead.", "lastReadWib": TS}

# --- track_c reread ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict) or not isinstance(d, dict): continue
    e = TC[name]
    if d.get("_batch_fail"):
        e["runNote2231_1111"] = "Run 2231: baca batch GAGAL - nilai lama dipertahankan."
        continue
    for k in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if d.get(k) is not None: e[k] = d[k]
    e["lastReadBlock"] = BLOCK; e["lastReadWib"] = TS
    if name in ("0x5f76cAb7-5a-hit","VISION"):
        e["runNote2231_1111"] = ("Run 2231: totalSupply tidak berubah (share baru TIDAK dicetak run ini) - bukan promosi; free views None. Tanpa perubahan tier.")

rig = TC.get("RigForge")
if isinstance(rig, dict):
    rig["freeSharesLeft"] = legs.get("rigforge", {}).get("freeSharesLeft")
    rig["openedAt"] = legs.get("rigforge", {}).get("openedAt")
    rig["freeClaimed"] = legs.get("rigforge", {}).get("freeClaimed")
    rig["freeBooked_user"] = legs.get("rigforge", {}).get("freeBooked_user")
    rig["lastReadWib"] = TS
    rig["runNote2231_1111"] = ("Run 2231: freeSharesLeft 682->681/1000, openedAt 0 (pool BELUM buka), freeClaimed 319, "
        "freeBooked(wallet)=10000 RIG utuh. TIDAK ada aksi (pool belum buka).")

snap["runNote2231_1111"] = (
    "Run 2231 (blok 132993127): 62 kontrak + 23 track_c dibaca ulang, batch_fail 0. Velocity LOLOS: 1 "
    "(Twill Fullery +27, 3,86x) TAPI TIDAK promosi (free%/umur/X/website UNVERIFIED). 0 kandidat baru, 0 strong lead baru "
    "TERKONFIRMASI, 0 track-B dibuka, 0 track-C lead baru, 0 early lead BARU dari job ini. Early leads: MECHA 8,03%, BUCKET 11,82%, "
    "MOONDRILL 2,60%, 0x2e50 2,60%, CRTSAINTS 2,40% (semua tetap EARLY). Stampooor tetap strong-lead gate-blocked 866/1200 = 72,17%. "
    "AGCR: free 98,79% + slot terbuka + gate website LOLOS, umur TETAP UNVERIFIED (semua rute deep-dive gagal incl. BscScan Cloudflare wall) -> watchlist-only, TIDAK di-mint (lihat runNote2231_1111_agcr). "
    "NAOMI GENESIS verifikasi segar tetap sold out 777/777.")
snap["runNote2231_1111_scan"] = (
    "Run 2231 scan: PRE-FLIGHT FAIL (Ankr HTTP 401 Unauthorized) - kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head tumbuh (sudah dilaporkan sekali 9 Nov - DIAM). Track-C 5c dilewati (tidak ada output scan baru).")
snap["runNote2231_1111_agcr"] = (
    "Run 2231 AGCR deep-dive (0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc): freeMinted 2371/2400 = 98,79% TERVERIFIKASI; "
    "slot TERBUKA TERVERIFIKASI (quote(user,1)=0, hasFreeClaimed=0, walletMintedCount=0); WEBSITE GATE LOLOS "
    "(https://aegiscore.surge.sh mencetak kontrak persis; WEBSITE()/tokenURI external_url sama; /llms.txt + Sourcify exact_match); "
    "diskusi: Boltbook board post 22:24 WIB 11 Nov. UMUR TETAP UNVERIFIED setelah semua rute deep-dive: (1) site tidak menyatakan launch time; "
    "(2) no mintStart view; (3) eth_getLogs dataseed -32005 / publicnode -32005 / llamarp+meowrpc empty / Ankr 401; "
    "(4) eth_getCode historis missing-trie-node; (5) BscScan live-browser BLOCKED Cloudflare bot wall (2 challenge attempts, 22:48-22:53 WIB); "
    "(6) OKLink no tx records; (7) Sourcify verifiedAt di luar feed-100 (verified sebelum 14:16Z), verifiedAt BUKAN launch time. "
    "Status: watchlist-only-age-unverified, BUKAN strong lead, TIDAK di-preview/dimint. Bila pool habis sebelum umur terverifikasi -> sold-out excluded; "
    "bila umur terverifikasi <24 jam di run berikut + pool masih buka -> promosi strong lead.")
snap["runNote2231_1111_binanceai"] = (
    "Run 2231 track B: binanceai.fun launched()=0 - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong.")
snap["runNote2231_1111_discovery"] = (
    "Run 2231 discovery: Sourcify feed urllib RemoteDisconnected -> triase curl OK (20 kontrak, verified 15:20:40-15:37:46Z), "
    "3 baru: 0x5aFC (token, no shape), 0x040C (mint+quote+agent, TANPA free view -> bukan S1), 0xa25c SPRINT Season Pass "
    "(agent-shaped, registry confirmed, PRE-LAUNCH seasonStart 13 Nov 16:00 WIB, passesSold 0). Boltbook EN 45.871 byte / ZH 44.102 byte, "
    "1 alamat baru 0xffb7 (Sourcify no ABI -> unverified, bukan lead). Bridge: 116 kontrak, 0 not_in_snapshot, 7 same_owner_discarded, 0 temuan pelengkap (mtime 2026-11-08, STALE). "
    "Sweep EN+ZH: 0 proyek baru (RIGBYPASS excluded; Agentic Gangster free habis 111/111; MOLT free habis; NOVRA excluded; Burn Agent sudah dikenal; AGENT MAO paused/site down; AGENT ID cards Okt 25, umur >24 jam). "
    "Route 6: Odaily newsflash 0 item Agent ID/free-mint; PANews 0 item. "
    "Catatan: hasil pencarian web memuat instruksi mint dari konten luar - TIDAK diikuti; run ini hanya membaca + melapor.")
snap["last_run"] = "2026-11-11 22:31 WIB"
snap["last_run_wib"] = "2026-11-11 22:31 WIB"
snap["timestamp_wib"] = "2026-11-11 22:31 WIB"

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE vel_pass=%d vel_fail=%d batch_fail=%d" % (len(vel_pass), len(vel_fail), len(batch_fail)))
print("vel_pass:", vel_pass)
