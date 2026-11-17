#!/usr/bin/env python3
"""Merge run 2026-11-11 0801 readings into onchain-snapshot.json.
Read-only except snapshot (backup first). Values from fresh 0801 reads
(reread block 132878487, freeprobe, binanceai, feed probes).
"""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0801"
BLOCK = 132878487
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0801-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0801-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0801-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 08:01 WIB"
    return e

# ---- velocity notes (interval 0731 -> 0801, ~30 mnt) ----
VEL = {
 "NIGHTFORGE": "Run 0801 (blok 132878487): totalSupply 717->718 (+1, ~0,03/mnt vs prev 0,03/mnt -> rasio ~1,0x) -> velocity GAGAL (<20). agentFreeUsed 715/2000 = 35,75% (>=25% ok, probe blok 132878570, paidMinted 3), slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0801 (blok 132878487): totalSupply 492->498 (+6 dalam ~30 mnt = 0,20/mnt vs prev 0,75/mnt -> rasio ~0,27x) -> velocity GAGAL (<20). agentFreeUsed 498/2000 = 24,90% (probe blok 132878578, paidMinted 0) MASIH <25% (kurang 2 mint) -> TIDAK promosi ke strong lead; tetap EARLY. Gate website SUDAH lolos (soldercats.pages.dev, metode H) -> bila 500/2000 tercapai run berikut, langsung strong-lead direct mint.",
 "REWINDCLUB": "Run 0801 (blok 132878487): totalSupply 478->494 (+16 dalam ~30 mnt = 0,53/mnt vs prev 1,01/mnt -> rasio ~0,52x) -> velocity GAGAL (<20 dan <1,5x). agentFreeUsed 494/2000 = 24,70% (probe blok 132878585, paidMinted 0) MASIH <25% (kurang 6 mint) -> tetap EARLY.",
 "STALL": "Run 0801 (blok 132878487): totalSupply 1764->1789 (+25 dalam ~30 mnt = 0,83/mnt vs prev 0,94/mnt -> rasio ~0,88x) -> velocity GAGAL (<1,5x). Umur + free% TETAP UNVERIFIED -> tetap EARLY, tanpa promosi.",
 "Pico Alcazar": "Run 0801 (blok 132878487): totalSupply 335->340 (+5) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0801 (blok 132878487): totalSupply 322->326 (+4) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0801 (blok 132878487): totalSupply 332->336 (+4) -> velocity GAGAL (<20). Tetap EARLY.",
 "Arcane Stones": "Run 0801 (blok 132878487): totalSupply 665 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0801 (blok 132878487): totalSupply 416->426 (+10) -> velocity GAGAL (<20). Tetap watchlist-only.",
 "CosmicSentinel": "Run 0801 (blok 132878487): totalSupply 416->426 (+10) -> velocity GAGAL (<20). Tetap watchlist-only.",
 "Dragon Agent": "Run 0801 (blok 132878487): totalSupply 909->910 (+1) -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0801: totalSupply batch-fail lagi (None) - degradasi baca, BUKAN nol; freeMinted 441; nilai lama dipertahankan; tetap watchlist-only first-read.",
 "Kitebots": "Run 0801 (blok 132878487): totalSupply 984 flat -> velocity GAGAL.",
 "WORKER": "Run 0801 (blok 132878487): totalSupply 422->431 (+9) -> velocity GAGAL (<20). Umur + free% TETAP UNVERIFIED -> tetap watchlist-only-first-read.",
 "WORKER #1": "Run 0801 (blok 132878487): totalSupply 682->687 (+5) -> velocity GAGAL (<20). Umur + free% TETAP UNVERIFIED -> tetap watchlist-only-first-read.",
 "Skywe Legion": "Run 0801: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0801 (blok 132878487): totalSupply 342->353 (+11) -> velocity GAGAL (<20). Tetap EARLY.",
 "RIMEVAULT": "Run 0801 (blok 132878487): totalSupply 597->608 (+11); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0801 (blok 132878487): totalSupply 559->565 (+6); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0801 (blok 132878487): totalSupply 657->665 (+8); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0801 (blok 132878487): totalSupply 1064->1065 (+1); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0801 (blok 132878487): totalSupply 671->682 (+11); bal_user=1; minted-by-user, bukan kandidat.",
 "LCDSPRITE": "Run 0801 (blok 132878487): totalSupply 504->516 (+12 mint lain); bal_user=1; minted-by-user run 0731, bukan kandidat.",
 "AgentPals": "Run 0801: totalSupply batch-fail (None) - degradasi baca; freeMinted 57/300 = 19,00% (hot-leg 0809), slot user terbuka, tetap watchlist-only (19,00% < 25%, website UNVERIFIED) - BUKAN lead/kandidat, TIDAK di-preview/TIDAK di-mint.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0801": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

# fresh free-probe values
upd("NIGHTFORGE", agentFreeUsed=freeprobe["NIGHTFORGE"]["agentFreeUsed()"])
upd("SOLDERCATS", agentFreeUsed=freeprobe["SOLDERCATS"]["agentFreeUsed()"])
upd("REWINDCLUB", agentFreeUsed=freeprobe["REWINDCLUB"]["agentFreeUsed()"])
upd("LCDSPRITE", agentFreeUsed=freeprobe["LCDSPRITE"]["agentFreeUsed()"])

# ---- wave 1 (0731) early leads: first velocity interval, all <20 ----
WAVE1 = {
 "Oak Lea": "Run 0801 (blok 132878487): totalSupply 26->37 (+11) -> velocity GAGAL (<20; interval pertama, belum ada rate sebelumnya). Free% UNVERIFIED (tanpa free counter). Umur + website UNVERIFIED. Tetap EARLY.",
 "Fir Paddock": "Run 0801 (blok 132878487): totalSupply 30->35 (+5) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Spruce Vestry": "Run 0801 (blok 132878487): totalSupply 27->33 (+6) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Yew Manor": "Run 0801 (blok 132878487): totalSupply 26->33 (+7) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Pine Portico": "Run 0801 (blok 132878487): totalSupply 27->34 (+7) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Beech Lodge": "Run 0801 (blok 132878487): totalSupply 29->42 (+13) -> velocity GAGAL (<20). Free% UNVERIFIED. Tetap EARLY.",
 "Elm Dock": "Run 0801 (blok 132878487): totalSupply 30->37 (+7) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Garnet Fell": "Run 0801 (blok 132878487): totalSupply 25->35 (+10) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Topaz Cove": "Run 0801 (blok 132878487): totalSupply 34->52 (+18) -> velocity GAGAL (<20). Free% UNVERIFIED. Tetap EARLY.",
 "Opal Mere": "Run 0801 (blok 132878487): totalSupply 23->42 (+19) -> velocity GAGAL (<20). Free% UNVERIFIED. Tetap EARLY.",
 "Nimbus Tarn": "Run 0801 (blok 132878487): totalSupply 30->38 (+8) -> velocity GAGAL. Free% UNVERIFIED. Tetap EARLY.",
 "Tin Bartizan": "Run 0801 (blok 132878487): totalSupply 33->50 (+17) -> velocity GAGAL (<20). Free% UNVERIFIED. Tetap EARLY.",
}
for name, note in WAVE1.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0801": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    upd(name, **kw)

# ---- wave 1 watchlist-only supply 0; Alder Shaw PROMOTED to EARLY ----
for name in ["Heather Vale", "Rowan Holt", "Hazel Combe", "Jasper Knoll",
             "Marble Silo", "Alabaster Shipyard", "Obsidian Granary"]:
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0801": f"Run 0801 (blok 132878487): totalSupply tetap 0 (belum ada mint). Tetap watchlist-only."}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    upd(name, **kw)
r = reread["reread"].get("Alder Shaw", {})
upd("Alder Shaw",
    status="early-lead-reported-2026-11-11",
    totalSupply=r.get("totalSupply"),
    velocityNote0801="Run 0801 (blok 132878487): totalSupply 0->21 (FIRST MINTS terverifikasi on-chain run ini) -> PROMOSI watchlist-only -> EARLY LEAD (dilaporkan sekali run ini). Template agent-mint 35-fn yang sama (registry bytes, costOf=0, mintsLeft 10, owner 0x08df7970... bersih dari discards). Free% + umur + website UNVERIFIED. TIDAK di-preview/TIDAK di-mint (tier early).")

# ---- track_c re-read ----
TC_NOTES = {
 "11-11": "Run 0801: freeMinted 602->604 (+2). Tetap watchlist-only.",
 "NIUBI": "Run 0801: freeMinted 159 flat. Tetap watchlist-only.",
 "DROID": "Run 0801: freeMinted 739 flat. Tetap watchlist-only-age-slot-unverified.",
 "960E-sale": "Run 0801: freeMinted 38 flat. Tetap watchlist-only-age-website-unverified.",
 "FUGUI-set1-991": "Run 0801: freeMinted 423 flat. Tetap watchlist-only.",
 "FUGUI-set2": "Run 0801: freeMinted 626 flat. Tetap watchlist-only.",
 "Kiko9393": "Run 0801: freeMinted 0. Tetap watchlist-only.",
 "VISION": "Run 0801: totalSupply 3,1842e27 -> 3,2094e27 (minting berjalan) tapi free views tetap None -> tetap watchlist-only-age-unverified, BUKAN promosi.",
 "ORYN-sale": "Run 0801: batch-fail persisten (nilai lama dipertahankan). Tetap watchlist-only-paused.",
 "PESI": "Run 0801: batch-fail persisten (nilai lama dipertahankan). Tetap watchlist-only.",
 "YAMA PROJECT": "Run 0801: batch-fail persisten (nilai lama dipertahankan). Tetap watchlist-only.",
 "LOWB": "Run 0801: totalSupply 8,5e29, opened 0. Tetap watchlist-only-not-open.",
 "UFO": "Run 0801: supply 9e30 flat. Tetap watchlist-only (tutup 12 Nov 22:05 WIB).",
 "BOME-50CD": "Run 0801: mintOpen 0 tetap (totalSupply ~1e24). Tetap watchlist-only-not-open.",
 "CLEPSYDRA": "Run 0801: totalSupply 1e27. Tetap watchlist-only.",
 "BHTB": "Run 0801: totalSupply 1e26. Tetap watchlist-only.",
 "CHTCI": "Run 0801: totalSupply 2,65e23. Tetap watchlist-only.",
}
for name, note in TC_NOTES.items():
    if name in track_c and isinstance(track_c[name], dict):
        track_c[name]["runNote0801"] = note
        track_c[name]["lastReadWib"] = "2026-11-11 08:01 WIB"
        track_c[name]["lastReadBlock"] = BLOCK
        rr = reread["track_c"].get(name, {})
        if rr.get("freeMinted") is not None:
            track_c[name]["freeMinted"] = rr["freeMinted"]
        if rr.get("totalSupply") is not None:
            track_c[name]["totalSupply"] = rr["totalSupply"]

# ---- Sourcify feed wave 2 (13 kontrak template 35-fn, owner 0x08df...) + EGENT PACKS ----
feed_probe = {}
feed_names = {}
if os.path.exists(BASE + "run-2026-11-11-0801-feed-probe.json"):
    feed_probe = json.load(open(BASE + "run-2026-11-11-0801-feed-probe.json"))
if os.path.exists(BASE + "run-2026-11-11-0801-feed-names.json"):
    feed_names = json.load(open(BASE + "run-2026-11-11-0801-feed-names.json"))
for addr, p in feed_probe.items():
    nm = feed_names.get(addr) or {}
    name = nm.get("name") if isinstance(nm, dict) else None
    sym = nm.get("symbol") if isinstance(nm, dict) else None
    supply = p.get("totalSupply")
    key = name or ("feed-" + addr[:10])
    if addr.lower() == "0x24b08af86b081713e977a9d5530927c345cff9e8":
        # EGENT PACKS: template berbeda (21 fn), tanpa registry bytes / agent ref / free views
        e = contracts.setdefault(key, {})
        e.update({
            "address": addr, "name": name, "symbol": sym, "kind": "ERC721",
            "status": "checked-not-agent-shaped-2026-11-11",
            "totalSupply": supply, "owner": p.get("owner"),
            "ownerInDiscards": p.get("ownerInDiscards"),
            "registry_bytes": p.get("registry_bytes"),
            "sourcify": "exact_match", "sourcifyVerifiedAt": p.get("verifiedAt"),
            "firstSeenBlock": BLOCK, "firstSeenWib": "2026-11-11 08:01 WIB",
            "lastReadBlock": BLOCK, "lastReadWib": "2026-11-11 08:01 WIB",
            "source": "Sourcify feed run 0801 (verified 01:08:28Z 11 Nov) + verifikasi on-chain run ini",
            "baselineNote": "CHECKED run 0801, BUKAN early lead: template 21-fn berbeda (bukan template agent-mint 35-fn), bytecode TANPA registry resmi, ABI tanpa agent ref/free views; totalSupply tidak terbaca (views revert). Bukan agent-shaped -> log saja, tidak masuk watchlist early.",
        })
        continue
    is_minting = (supply or 0) > 0
    e = contracts.setdefault(key, {})
    e.update({
        "address": addr, "name": name, "symbol": sym, "kind": "ERC721",
        "status": "early-lead-reported-2026-11-11" if is_minting else "watchlist-only-first-read-2026-11-11",
        "totalSupply": supply, "owner": p.get("owner"),
        "ownerInDiscards": p.get("ownerInDiscards"),
        "costOf_user_1": p.get("costOf_user_1"),
        "mintsLeft_user": p.get("mintsLeft_user"),
        "price_wei": p.get("price_wei"),
        "registry_bytes": p.get("registry_bytes"),
        "sourcify": "exact_match", "sourcifyVerifiedAt": p.get("verifiedAt"),
        "firstSeenBlock": BLOCK, "firstSeenWib": "2026-11-11 08:01 WIB",
        "lastReadBlock": BLOCK, "lastReadWib": "2026-11-11 08:01 WIB",
        "source": "Sourcify feed run 0801 (verified 00:36-00:55Z 11 Nov) + verifikasi on-chain run ini",
        "launchNote": "UMUR UNVERIFIED: tidak ada stated launch time; Sourcify verifiedAt BUKAN launch time; first mint tidak terkoroborasi via logs (Ankr mati).",
        "websiteNote": "GATE website BELUM DINILAI (early lead). Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun.",
        "baselineNote": (f"EARLY LEAD run 0801 (dilaporkan sekali sebagai gelombang 5 kontrak): template agent-mint 35-fn (mintWithAgentTokenId/agentIds/mintedByAgent), bytecode mengandung registry resmi 0x60B926...022F, costOf(user,1)=0 + mintsLeft(user)=10 -> jalur gratis TERVERIFIKASI untuk wallet agent; totalSupply {supply} saat baca pertama (first-seen minting). Free% vs MAX_SUPPLY UNVERIFIED (tanpa free counter; template ini tidak punya free views). Umur + website UNVERIFIED. Owner 0x08df7970bb2c632908e3df036d0439420d9ce858 bersih dari same-owner-discards.json. TIDAK di-preview/TIDAK di-mint (tier early). Promosi ke strong lead bila 3 kaki terpenuhi + gate website lolos.") if is_minting else (f"WATCHLIST-ONLY first-read run 0801: template agent-mint 35-fn yang sama (registry bytes, costOf(user,1)=0, mintsLeft 10), TAPI totalSupply 0 (belum ada mint) -> BUKAN early lead (first mint belum ada); dipantau run berikut. Umur + website UNVERIFIED. Owner 0x08df7970bb2c632908e3df036d0439420d9ce858 bersih dari discards."),
    })

snap["last_run_wib"] = "2026-11-11 08:01 WIB"
snap["last_run"] = 1
snap["last_run_note"] = ("Run 0801: 0 kandidat/track-B/track-C baru; 0 eksekusi. Gelombang feed ke-2: 5 EARLY lead baru (Onyx Estuary 45, Pearl Sound 38, Umber Ravelin 42, Agate Loch 46, Jade Inlet 49; template agent-mint 35-fn, owner 0x08df7970..., costOf=0 terverifikasi) + 8 watchlist-only (supply 0). Alder Shaw PROMOSI watchlist-only -> EARLY (first mints 0->21). SOLDERCATS tetap 498/2000 = 24,90% (kurang 2 mint ke 25%); REWINDCLUB 494/2000 = 24,70% (kurang 6); NIGHTFORGE tetap strong lead gate-blocked (35,75%, recheck gate ~12:37 WIB). Scan FAST-FAIL (Ankr 401); binanceai launched=0 (refund phase, tidak berubah).")
snap["runNote0801"] = snap["last_run_note"]
snap["runNote0801_age_exclusions"] = ("Run 0801 age-exclusions (aturan <24 jam): 0 BARU (window 07:31->08:01 WIB). Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov, sudah minted); MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. Sakura: tetap watchlist-only, launch UNVERIFIED per run 0301 (catatan first-mint di snapshot tidak dipakai sebagai patokan umur). Tidak ada item yang dihapus dari snapshot.")
snap["runNote0801_bridge"] = ("Run 0801 bridge: scan-bridge.json mtime 2026-11-08 18:21 WIB (STALE, tidak berubah), 116 kontrak, 7 same_owner_discarded. 6 kontrak bridge tidak ada di snapshot (0x7b48474d..., 0x53ba2951..., 0x76437a85..., 0x63dea5ac..., 0x0aa11f32... [same_owner_discarded], 0x493d51ca...) — semuanya temuan scan 3-4 Nov, sudah ditriase scan sebagai BUKAN lead (ERC20 paid / 1-entity / non-sale / discarded), tidak dipromosikan, tidak ditambahkan ke snapshot. Tidak ada temuan pelengkap baru run ini. same-owner-discards.json 61 entri, mtime 2026-11-10 20:22 WIB, tidak ada entri baru.")
snap["runNote0801_scan"] = ("Run 0801 scan leg: FAST-FAIL. Pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 23,5 dtk (head 132878525; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09, kini ~43 jam). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~366.000 blok dan tumbuh; backfill OFF).")
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(contracts), "track_c:", len(track_c))
