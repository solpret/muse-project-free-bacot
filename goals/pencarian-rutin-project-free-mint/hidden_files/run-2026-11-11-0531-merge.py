#!/usr/bin/env python3
"""Merge run 2026-11-11 0531 readings into onchain-snapshot.json. Read-only except snapshot (backup first)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0531"
BLOCK = 132857028
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0531-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0531-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0531-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 05:31 WIB"
    return e

VEL = {
 "NIGHTFORGE": "Run 0531 (blok 132857028): totalSupply 712 flat vs 0501 (712), agentFreeUsed 709/2000 = 35,45% (>=25% ✓, probe blok 132857128, paidMinted 3) -> velocity GAGAL (0). Slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate buka ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0531 (blok 132857028): totalSupply 462->464 (+2), agentFreeUsed 464/2000 = 23,2% (<25%, probe blok 132857137) -> velocity GAGAL (<20). Tetap EARLY.",
 "REWINDCLUB": "Run 0531 (blok 132857028): totalSupply 427->428 (+1), agentFreeUsed 428/2000 = 21,4% (<25%, probe blok 132857146) -> velocity GAGAL (<20). Tetap EARLY.",
 "LCDSPRITE": "Run 0531 (blok 132857028): totalSupply 480->481 (+1), agentFreeUsed 481/2000 = 24,05% (<25%, probe blok 132857155) -> velocity GAGAL (<20). Tetap EARLY.",
 "Pico Alcazar": "Run 0531 (blok 132857028): totalSupply 307->316 (+9) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0531 (blok 132857028): totalSupply 293->305 (+12) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0531 (blok 132857028): totalSupply 307->313 (+6) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0531 (blok 132857028): totalSupply 1683->1688 (+5) -> velocity GAGAL (<20). Tetap EARLY.",
 "Arcane Stones": "Run 0531 (blok 132857028): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0531 (blok 132857028): totalSupply 404->407 (+3); freeMinted 399->402/225.000 = 0,18% -> tetap watchlist-only.",
 "Dragon Agent": "Run 0531 (blok 132857028): totalSupply 906->907 (+1) -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0531 (blok 132857028): freeMinted 398->409 (+11, <20) -> velocity GAGAL run ini (0501 sempat LOLOS +24); tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0531 (blok 132857028): totalSupply 984 flat, freeMinted 984 -> velocity GAGAL.",
 "WORKER": "Run 0531 (blok 132857028): totalSupply 366->376 (+10) -> velocity GAGAL; umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0531: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0531 (blok 132857028): totalSupply 327 flat -> velocity GAGAL.",
 "RIMEVAULT": "Run 0531 (blok 132857028): totalSupply 520->544 (+24); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0531 (blok 132857028): totalSupply 515->519 (+4); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0531 (blok 132857028): totalSupply 643->644 (+1); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0531 (blok 132857028): totalSupply 1041->1042 (+1); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0531 (blok 132857028): totalSupply 581->599 (+18); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0531 (blok 132857028): totalSupply None, freeMinted 0, freePhaseStart 0 (0501) -> masih prelaunch; watchlist-only-upcoming.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0531": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

TC_NOTES = {
 "MOODENG": "Run 0531: freeMinted 469->479 (+10) - TAPI agent-shape TETAP UNVERIFIED + website UNVERIFIED -> watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "11-11": "Run 0531: freeMinted 586 flat.",
 "NIUBI": "Run 0531: freeMinted 159 flat.",
 "DROID": "Run 0531: freeMinted 739 flat.",
 "960E-sale": "Run 0531: freeMinted 38 flat.",
 "FUGUI-set1-991": "Run 0531: freeMinted 423 flat.",
 "FUGUI-set2": "Run 0531: freeMinted 626 flat.",
 "ORYN-sale": "Run 0531: tetap paused (totalSupply None).",
 "PESI": "Run 0531: batch-fail persisten (nilai lama dipertahankan).",
 "YAMA PROJECT": "Run 0531: batch-fail persisten (nilai lama dipertahankan).",
}
for name, note in TC_NOTES.items():
    t = reread["track_c"].get(name, {})
    e = track_c.setdefault(name, {})
    if t.get("freeMinted") is not None:
        e["freeMinted"] = t["freeMinted"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 05:31 WIB"
    e["runNote0531_1111"] = note

snap["last_run_wib"] = "2026-11-11 05:31 WIB"
snap["last_run_note"] = ("Run 0531: 0 kandidat/strong/early/track-B/track-C baru; 0 eksekusi; "
    "scan FAST-FAIL (Ankr 401); NIGHTFORGE tetap gate-blocked (free 709/2000 = 35,45%, umur <24 jam s.d. 14:37 WIB); "
    "GangDotFun velocity GAGAL run ini (+11, <20); AgentPals masih prelaunch; binanceai launched=0 (refund phase, tidak berubah).")
snap["runNote0531_1111"] = snap["last_run_note"]
snap["runNote0531_1111_scan"] = ("Pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 25,9 dtk "
    "(head 132856988; kuota Ankr 0% s.d. 1 Des 2026). Scan leg FAST-FAIL run ini. Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~344.000 blok dan tumbuh).")
snap["runNote0531_1111_binanceai"] = "binanceai.fun: launched()=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132857165) - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong."
snap["runNote0531_1111_discovery"] = ("Boltbook EN 200 47.127 byte + ZH 200 47.303 byte; 12 alamat (EN) / 12 (ZH), 0 baru vs snapshot + seen + hot-leg-seen. "
    "Sourcify feed 20 terbaru (verified 21:29-22:23Z), 0 baru vs hot-leg-seen (total 11.040); AgentPals muncul lagi (dikenal, upcoming). "
    "Sweep EN+ZH: 0 proyek baru (Agentic Gangster free sold out - excluded; MOLT AGENT excluded-free-pool-exhausted; Horus AI phase 1 sold out; First-Dollar Grove age-excluded; Subsonic Tribe/Oathbots/Laser Agents/Pixel Fox lama). "
    "Odaily 200 263.593 byte + PANews 200 119.534 byte, 0 keyword Agent ID / free mint / free share. Bridge: mtime 2026-11-09 01:21 WIB (STALE), 0 temuan baru. 5c: tanpa output scan baru (scan fast-fail) -> tidak ada backlog ERC-20 baru.")
snap["runNote0531_1111_age_exclusions"] = ("0 BARU run ini (window 05:01->05:31 WIB). Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; "
    "RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. "
    "Tidak ada item yang dihapus dari snapshot.")

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE OK block", BLOCK)
