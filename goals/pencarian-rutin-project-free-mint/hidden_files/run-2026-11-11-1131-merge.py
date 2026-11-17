#!/usr/bin/env python3
"""Merge run 1131 (scheduled 2026-11-11 11:31 WIB) into onchain-snapshot.json.
Writes snapshot (with .bak). Inputs: run-2026-11-11-1131-reread.json (block
132904919, 59 contracts + 22 track_c), run-2026-11-11-1131-legs.json (feed +
Boltbook urllib FAIL + bridge + binanceai), run-2026-11-11-1131-probe.json
(CAP7 fresh + 0x8653 + 0xb3cf), run-2026-11-11-1131-probe2.json (0x8653 ABI +
CAP7 tokenURI + route 6), boltbook-en/zh-1131 (curl OK), hot-leg 1124 values.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1131-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1131-legs.json"))
probe = json.load(open(BASE + "run-2026-11-11-1131-probe.json"))
probe2 = json.load(open(BASE + "run-2026-11-11-1131-probe2.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1131-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 11:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict):
        return None
    old = e.get("totalSupply")
    if old is None or new_supply is None:
        return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = None
    if prev_rate and prev_rate > 0:
        ratio = round(rate / prev_rate, 2)
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

# --- 1. reread updates (generic) ---
for name, d in reread["reread"].items():
    if name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        e["runNote1131"] = ("Run 1131 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        old = e.get("totalSupply")
        if old is None:
            e["totalSupply"] = ns
            e["lastReadBlock"] = BLOCK
            e["lastReadWib"] = TS
            e["runNote1131"] = ("Run 1131 (blok %s): totalSupply pertama terbaca %s (sebelumnya None) - "
                                "baseline dicatat, velocity belum lulus; freeMinted=%s; bal_user=%s; status %s."
                                % (BLOCK, ns, d.get("freeMinted"), d.get("balanceOf_user"), e.get("status")))
        else:
            r = vel(name, ns)
            diff, rate, ratio = r if r else (None, None, None)
            e["runNote1131"] = ("Run 1131 (blok %s): totalSupply %s->%s (+%s, %s/mnt vs prev %s = %sx) -> velocity %s; "
                                "bal_user=%s; freeMinted=%s; status %s."
                                % (BLOCK, e.get("previousTotalSupply"), ns, diff, rate,
                                   e.get("previousRatePerMin"), ratio,
                                   "LOLOS" if e.get("velocityLegPasses") else "GAGAL",
                                   d.get("balanceOf_user"), d.get("freeMinted"), e.get("status")))
    if d.get("freeClaimed") is not None:
        e["freeClaimed"] = d["freeClaimed"]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None:
        e["MAX_SUPPLY"] = d["MAX_SUPPLY"]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS

# --- 2. Stampooor: 577->627 (+50, 1.67/mnt vs prev 1.43 = 1.16x) velocity GAGAL; 627/1200 = 52,25% ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": 627, "totalSupply": 627, "freeMinted": 627,
               "freeAvailable_user": 1, "lastReadBlock": BLOCK, "lastReadWib": TS})
    st["runNote1131"] = ("Run 1131: totalSupply 577->627 (+50, 1,67/mnt vs prev 1,43 = 1,16x) -> velocity GAGAL. "
        "Free 627/1200 = 52,25% (LEWAT 50% kandidat) TAPI velocity gagal -> BUKAN kandidat; jauh di bawah 70% "
        "strong lead. Slot user TERBUKA (balanceOf 0). Umur TERVERIFIKASI <24 jam (mintStart 11 Nov ~09:00 WIB). "
        "X + website UNVERIFIED. Tetap EARLY. TIDAK di-preview/di-mint.")

# --- 3. Jade Vault 0x7Eb9: 398->422 (+24, 0.80/mnt vs prev 0.80 = 1.0x) velocity GAGAL ---
jv = C.get("0x7Eb9")
if isinstance(jv, dict):
    jv.update({"totalMinted": 422, "totalSupply": 422, "lastReadBlock": BLOCK, "lastReadWib": TS})
    jv["runNote1131"] = ("Run 1131: totalMinted 398->422 (+24, 0,80/mnt vs prev 0,80 = 1,0x) -> velocity GAGAL. "
        "Tetap EARLY: free% UNVERIFIED (template tanpa free counter), umur + website + X UNVERIFIED. "
        "TIDAK di-preview/di-mint.")

# --- 4. NIGHTFORGE: 740->742 (+2) velocity GAGAL; ~37,1% ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    nf.update({"totalSupply": 742, "freePctVerified": 37.1,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    nf["runNote1131"] = ("Run 1131: totalSupply 740->742 (+2) -> velocity GAGAL; agentFreeUsed ~742/2000 = 37,1% "
        "(jauh di bawah ambang strong lead >70% per amandemen 11 Nov 09:18 WIB). Slot terbuka (balanceOf 0). "
        "Deadline umur 14:37 WIB 11 Nov belum lewat - TAPI per amandemen >70%, NIGHTFORGE BUKAN strong lead "
        "jadi deadline recheck gate moot untuk jalur strong lead. Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 5. AgentPals: 77->79 (+2, 2.0x tapi <20) velocity GAGAL; 79/300 = 26,3% ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap.update({"totalSupply": 79, "freeMinted": 79, "totalMinted": 79,
               "status": "watchlist-only-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    ap["runNote1131"] = ("Run 1131: totalSupply 77->79 (+2, 2,0x tapi <20 token) -> velocity GAGAL. Free phase LIVE "
        "sejak 11 Nov 06:33:57 WIB; 79/300 = 26,3% (<50% kandidat, <70% strong lead). Slot user terbuka "
        "(balanceOf 0). Website UNVERIFIED. Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 6. STALL: velocity LOLOS (+20, 1.54x) tapi free% + umur UNVERIFIED -> tetap EARLY ---
stall = C.get("STALL")
if isinstance(stall, dict):
    stall["runNote1131"] = ("Run 1131: totalSupply 1849->1869 (+20, 0,67/mnt vs prev 0,43 = 1,54x) -> velocity LOLOS "
        "(pertama kali lolos sejak early lead 10 Nov). TAPI free% MASIH UNVERIFIED (free views null) DAN umur "
        "peluncuran MASIH UNVERIFIED (tanpa mintStart view; koroborasi first-mint mustahil, Ankr 401) -> BUKAN "
        "kandidat (butuh >=50% free terverifikasi) dan BUKAN strong lead (butuh >70% free + umur <24 jam "
        "terverifikasi). Website TERVERIFIKASI (agentmarket.exchange), X UNVERIFIED. Tetap EARLY. "
        "TIDAK di-preview/di-mint. Perubahan velocity dicatat di run log saja (bukan promosi tier).")

# --- 7. WORKER: velocity LOLOS (+26, 3.71x) tapi free% UNVERIFIED -> tetap watchlist-only ---
wk = C.get("WORKER")
if isinstance(wk, dict):
    wk["runNote1131"] = ("Run 1131: totalSupply 465->491 (+26, 0,87/mnt vs prev 0,23 = 3,71x) -> velocity LOLOS. "
        "TAPI free% UNVERIFIED (tidak ada free counter/cap view; freeAvailable(address) bool per-wallet saja; "
        "totalMinted 491/100.000 BUKAN % free) -> BUKAN kandidat dan BUKAN strong lead. Website "
        "agent-worker.pages.dev, X UNVERIFIED. Tetap watchlist-only. TIDAK di-preview/di-mint. Perubahan "
        "velocity dicatat di run log saja (bukan promosi tier).")

# --- 8. Bot Fighters + ABYSSCABLE: tidak di-re-read job utama run ini; pakai nilai hot-leg 1124 ---
bf = C.get("Bot Fighters")
if isinstance(bf, dict):
    bf.update({"totalSupply": 31, "totalMinted": 31, "freeMinted": 31,
               "lastReadBlock": 132904796, "lastReadWib": "2026-11-11 11:24 WIB (hot leg)"})
    bf["runNote1131"] = ("Run 1131: Bot Fighters 27->31/500 (6,2%) per hot-leg 1124 (blok ~132904796) - job utama "
        "tidak re-read BOTF run ini (di luar daftar PRIO; hot leg melacak tiap 5 mnt). Slot user TERBUKA, umur "
        "MASIH UNVERIFIED (first-mint milik scan leg job utama; Ankr 401). Tetap watchlist-only-age-unverified. "
        "TIDAK di-preview/di-mint.")
ab = C.get("ABYSSCABLE")
if isinstance(ab, dict):
    ab.update({"totalSupply": 770, "agentFreeUsed": 770, "freePct": 38.5,
               "lastReadBlock": 132904796, "lastReadWib": "2026-11-11 11:24 WIB (hot leg)"})
    ab["runNote1131"] = ("Run 1131: ABYSSCABLE 766->770/2000 (38,5%) per hot-leg 1124. Umur TERVERIFIKASI <24 jam "
        "(mintStart 10 Nov ~19:38 WIB; deadline ~19:39 WIB 11 Nov). Website UNVERIFIED. Tetap watchlist-only. "
        "TIDAK di-preview/di-mint.")

# --- 9. track_c updates from reread (non-None only) ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict):
        continue
    e = TC[name]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    if name == "11-11":
        e["runNote1131"] = "Run 1131: freeMinted 614 flat vs run 1101; tetap watchlist-only-age-website-unverified."

# --- 10. CAP7 -> track_c, lead-track-c + GATE FAILED (sweep penuh (A)-(N) run ini) ---
cap7 = probe["cap7"]
TC["CAP7"] = {
    "sale": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
    "address": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
    "token": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
    "name": "Obrigado Capitao (CAP7)",
    "kind": "track-c-sale",
    "status": "lead-track-c-gate-failed-2026-11-11",
    "saleShape": "S1 PASS (mint+costOf+freeClaimed/freeMinted+registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, exact_match, verifiedAt 2026-11-11T04:25:17Z)",
    "FREE_SHARES": 640, "freeMinted": 72, "sharesMinted": 72, "paidMinted": 0, "soldOut": 0, "phase": 1,
    "PRICE": 2000000000000000, "saleStart": 1794371051, "saleStartWib": "2026-11-11 11:24:11 WIB",
    "SALE_WINDOW": 1209600, "deadlineWib": "2026-11-25 11:24:11 WIB",
    "freePoolLeft": 568, "freePctClaimed": 11.25,
    "userSlotOpen": True, "balanceOf_user": 0,
    "ageVerified": True, "ageNote": "saleStart() on-chain 1794371051 = 11:24:11 WIB 11 Nov; deadline 25 Nov. CAVEAT: timestamp first-mint TIDAK terkoroborasi via logs (public RPC eth_getLogs -32005; Ankr getLogs 401) - umur bersandar pada saleStart on-chain + arus mint live (37 free mint dalam ~4 mnt pertama, 72 pada blok 132905591).",
    "website": None, "gate": "FAILED-full-sweep-A-N-2026-11-11",
    "gateNote": ("GATE FAILED run 1131 (sweep penuh (A)-(N); hot leg 1124 hanya light sweep, didelegasikan ke job utama): "
        "(A) raw address search: no hit; (B) Boltbook EN+ZH: no mention; (C) Sourcify metadata: exact_match, no project URL in sources; "
        "(D) same-family patterns: no site found via search, no guessing; (E) owner 0xe9a232aefaa230a38bc9fec961eea19134903308, bukan grup factory dikenal; "
        "deployer-address web search: no relevant hit; (F) X check N/A (no handle found elsewhere to confirm); "
        "(G) name search 'Obrigado Capitao/CAP7': hanya merchandise tribute Ronaldo, no project site; (H) contractURI(): none; "
        "(I) tokenURI(0): execution reverted, no URL; (J) ABI: no site function; (K) GitHub code search: needs auth (limitation stated), web search by exact address no hit; "
        "(L) BscScan token page: text fetch 403, live browser blocked Cloudflare bot wall ('Just a moment...') 11:37-11:38 WIB - INCONCLUSIVE, bukan absence; "
        "(M) site:pages.dev/vercel.app/deed.page + CAP7/Obrigado: no results; (N) no Boltbook author post to hop from, no project Agent ID profile resolvable. "
        "TIDAK di-preview, TIDAK di-mint. Lead sudah dilaporkan sekali oleh hot leg 1124 (gate pending); verdict gate FAILED ini dilaporkan sekali run ini."),
    "lastReadBlock": BLOCK, "lastReadWib": TS,
    "runNote1131": ("Run 1131: CAP7 BARU masuk track_c dari hot-leg 1124 (lead dilaporkan sekali di sana). Re-read segar blok 132905591: "
        "freeMinted 37->72/640 (11,25%, 568 tersisa), paidMinted 0, soldOut 0, phase 1, PRICE 0,002 BNB/share, free path claimFree() no-arg, "
        "slot user TERBUKA (agentId ada, freeClaimed false, balanceOf 0). GATE FAILED (sweep penuh (A)-(N), lihat gateNote). "
        "TIDAK di-preview/di-mint."),
}
print("ADDED track_c CAP7 gate-failed")

# --- 11. Foundry Faces 0x8653 -> contracts, watchlist-only-age-unverified (totalMinted 0) ---
C["Foundry Faces"] = {
    "address": "0x8653B09bDaD22c99915910962167F132E514331F",
    "name": "Foundry Faces", "symbol": "FACES", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "totalSupply": None, "totalMinted": 0, "freeMinted": None, "freeClaimed": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": 11111, "mintOpen": 1, "balanceOf_user": 0,
    "agentShaped": "Sourcify exact_match, verifiedAt 2026-11-11T04:31:40Z; ABI: mintFree + holdsAgentId + AGENT_ID + mintPaid + priceFor + TIER1/2/3_PRICE (39 fns); bytecode/ABI menunjukkan referensi Agent ID + fungsi free-mint.",
    "ageNote": "Umur peluncuran UNVERIFIED: totalMinted=0 pada blok 132905591 (belum ada mint sama sekali - mintOpen=1 tapi arus mint belum mulai); first-mint TIDAK terverifikasi (Ankr getLogs 401; public RPC eth_getLogs -32005 bahkan rentang 100 blok). BUKAN early lead (syarat first mints terverifikasi on-chain belum terpenuhi). Dipantau hot leg tiap 5 mnt; promosi bila first mints terverifikasi + umur <24 jam.",
    "website": None, "gate": "not-checked-no-mints-yet",
    "xVerified": False,
    "lastReadBlock": BLOCK, "lastReadWib": TS,
    "runNote1131": ("Run 1131: BARU dari Sourcify feed (verified 11:31:40 WIB). Foundry Faces (FACES), MAX_SUPPLY 11111, mintOpen 1, "
        "totalMinted 0 - BELUM ADA MINT. Agent-shaped (mintFree + holdsAgentId + AGENT_ID). BUKAN early lead (first mints belum "
        "terverifikasi). Watchlist-only-age-unverified. TIDAK di-preview/di-mint."),
}
print("ADDED contracts Foundry Faces")

# --- 12. 0xb3cf -> contracts, checked-not-verified (Sourcify 404) agar tidak di-flag 'baru' lagi ---
C["0xb3cf86fe"] = {
    "address": "0xb3cf86fe905ad1d4c3a4eb55e01123e06e334c4c",
    "kind": "checked-not-verified",
    "status": "checked-not-verified-contract-2026-11-11",
    "note": "Muncul di Boltbook EN+ZH front page run 1131 (baru vs hot-leg-seen+snapshot). Sourcify ABI endpoint HTTP 404 (bukan kontrak terverifikasi; kemungkinan false-positive hex string seperti topic-hash). BUKAN agent-shaped dari bukti yang ada, BUKAN lead. Dicatat agar run berikut tidak menandainya 'baru' lagi.",
    "lastReadBlock": BLOCK, "lastReadWib": TS,
    "runNote1131": "Run 1131: 0xb3cf86fe... BARU dari Boltbook EN+ZH; Sourcify 404 -> checked-not-verified, bukan lead, tidak dilaporkan.",
}
print("ADDED contracts 0xb3cf86fe checked")

# --- 13. top-level run notes ---
snap["last_run_wib"] = TS
snap["timestamp_wib"] = TS
snap["last_run_note"] = ("Run 1131: 0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead BARU (CAP7 sudah dilaporkan hot leg 1124). "
    "GATE FAILED CAP7 (sweep penuh (A)-(N)) -> TIDAK di-preview/di-mint; dilaporkan sekali run ini. "
    "BARU dicatat watchlist-only (TIDAK dilaporkan): Foundry Faces 0x8653 (totalMinted 0, belum ada mint, umur unverified). "
    "Stampooor 577->627 (52,25%, velocity GAGAL 1,16x, tetap EARLY); Jade Vault 398->422 (velocity GAGAL, tetap EARLY); "
    "STALL velocity LOLOS (+20, 1,54x) tapi free%+umur UNVERIFIED -> tetap EARLY; WORKER velocity LOLOS (+26, 3,71x) tapi free% UNVERIFIED -> tetap watchlist-only; "
    "NIGHTFORGE 742 flat (37,1%, tetap watchlist-only <70%); AgentPals 79/300 = 26,3%; Bot Fighters 31/500; ABYSSCABLE 770/2000 (38,5%). "
    "Feed Sourcify 20 kontrak: 1 baru (Foundry Faces, early-shape). Boltbook EN+ZH via curl OK (46.560 + 46.699 byte, 17 alamat, 1 baru 0xb3cf Sourcify 404). "
    "Scan FAST-FAIL (pre-flight Ankr 401). binanceai launched=0 (refund phase).")
snap["runNote1131"] = snap["last_run_note"]
snap["runNote1131_scan"] = ("Scan run 1131 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized "
    "(10,1 dtk). Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564; "
    "gap ke head ~392.000 blok dan tumbuh; backfill OFF). Track-C 5c dilewati run ini (tidak ada output scan baru).")
snap["runNote1131_binanceai"] = ("Run 1131: launched()=0 (blok %s) - TIDAK BERUBAH (refund phase, sudah dilaporkan "
    "sekali). pending_claims: binanceai.fun tetap pending, TIDAK di-preview/diklaim." % BLOCK)
snap["runNote1131_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah sejak run 1001), "
    "116 kontrak, 7 same_owner_discarded; not_in_snapshot 0 (6 temuan pelengkap sudah dicatat run 1101) - 0 temuan pelengkap baru run ini. "
    "Tidak ada kontrak feed baru di bridge; tidak ada discard baru.")
snap["runNote1131_discovery"] = ("Discovery run 1131: Sourcify feed 20 kontrak (verified 03:57-04:31Z): 1 baru - Foundry Faces 0x8653 "
    "(early-shape: is_nft + mintFree fn, agent_ref false; totalMinted 0 -> BUKAN early lead, watchlist-only). 2 abi-timeout lama (0xddf252ad, "
    "0x5273f49b) kini Sourcify HTTP 404 (BUKAN kontrak - 0xddf252ad... adalah Transfer topic hash; STOP retry keduanya di run berikut). "
    "Boltbook EN 46.560 byte + ZH 46.699 byte via curl (urllib gagal IncompleteRead; hot leg EN pulih 1124): 17 + 17 alamat, 1 baru 0xb3cf "
    "(Sourcify 404, checked-not-verified). Sweep EN+ZH: 0 proyek baru - Agentic Gangster (free-pool-exhausted, sudah tercatat), Pocket Ai "
    "(sudah di snapshot), Subsonic Tribe/BNBmeme/BN Agent File/PIXEL PETS/Skynet (post 26 Okt, lama), First-Dollar Grove (age-excluded, sudah "
    "tercatat), AGENT MAO (lama), Pixel Fox/AgentForge/PocketDragons (lama). Leg 6: Odaily newsflash 276.614 byte + PANews 120.127 byte dibaca - "
    "0 keyword hit Agent ID/free-mint.")
snap["runNote1131_age_exclusions"] = ("Run 1131: 0 age-exclusion BARU. Deadline berjalan: NIGHTFORGE 14:37 WIB 11 Nov "
    "(mintStart 10 Nov 14:37 WIB; 37,1% - watchlist-only; per amandemen >70% deadline recheck gate moot untuk jalur strong lead); "
    "ABYSSCABLE ~19:39 WIB 11 Nov (mintStart 10 Nov ~19:38 WIB; 38,5% - watchlist-only); AgentPals ~06:33 WIB 12 Nov; MOODENG ~02:00 WIB "
    "12 Nov (SUDAH sold out 500/500, dilaporkan hot leg 06:01 - entri track_c snapshot utama kosong, tanpa aksi); UFO ~22:05 WIB 12 Nov. "
    "SIDECOIN buka hari ini 20:00 WIB, kontrak masih unpublished (catatan hot leg 1124) - pantau 20:00. Bot Fighters: umur UNVERIFIED "
    "(bukan age-excluded) - watchlist-only. Foundry Faces: umur UNVERIFIED (totalMinted 0) - watchlist-only, bukan age-excluded.")
snap["runNote1131_cap7_gate"] = TC["CAP7"]["gateNote"]
snap["runNote1131_retries"] = ("RETRY LIST: STOP retry 0xddf252ad1be2c89b69c2b068fc378daa952ba7f1 + 0x5273f49b5f88aa36f9418e3c5f1c39378062a999 "
    "di run berikut - keduanya kini Sourcify HTTP 404 (bukan kontrak; 0xddf252ad... = Transfer event topic hash yang lolos regex alamat di Boltbook). "
    "Hapus dari daftar retry legs.py run berikut (jangan salin mentah dari run 1131).")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE. contracts:", len(C), "track_c:", len(TC))
