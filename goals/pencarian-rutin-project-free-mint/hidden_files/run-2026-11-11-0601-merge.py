#!/usr/bin/env python3
"""Merge run 2026-11-11 0601 readings into onchain-snapshot.json. Read-only except snapshot (backup first)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0601"
BLOCK = 132861001
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0601-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0601-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0601-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 06:01 WIB"
    return e

VEL = {
 "NIGHTFORGE": "Run 0601 (blok 132861001): totalSupply 712 flat vs 0531 (712), agentFreeUsed 709/2000 = 35,45% (>=25% ✓, probe blok 132861017, paidMinted 3) -> velocity GAGAL (0). Slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate buka ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0601 (blok 132861001): totalSupply 464->465 (+1), agentFreeUsed 465/2000 = 23,25% (<25%, probe blok 132861032) -> velocity GAGAL (<20). Tetap EARLY.",
 "REWINDCLUB": "Run 0601 (blok 132861001): totalSupply 428->437 (+9), agentFreeUsed 437/2000 = 21,85% (<25%, probe blok 132861049) -> velocity GAGAL (<20). Tetap EARLY.",
 "LCDSPRITE": "Run 0601 (blok 132861001): totalSupply 481->483 (+2), agentFreeUsed 483/2000 = 24,15% (<25%, probe blok 132861067) -> velocity GAGAL (<20). Tetap EARLY.",
 "Pico Alcazar": "Run 0601 (blok 132861001): totalSupply 316->320 (+4) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0601 (blok 132861001): totalSupply 305->307 (+2) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0601 (blok 132861001): totalSupply 313->316 (+3) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0601 (blok 132861001): totalSupply 1688->1695 (+7) -> velocity GAGAL (<20). Tetap EARLY.",
 "Arcane Stones": "Run 0601 (blok 132861001): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0601 (blok 132861001): totalSupply 407->409 (+2); freeMinted 402->404/225.000 = 0,18% -> tetap watchlist-only.",
 "CosmicSentinel": "Run 0601 (blok 132861001): totalSupply 395->409 (+14); freeMinted 390->404 -> velocity GAGAL (<20). Tetap watchlist-only.",
 "Dragon Agent": "Run 0601 (blok 132861001): totalSupply 907 flat -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0601 (blok 132861001): freeMinted 409->416 (+7, <20) -> velocity GAGAL run ini; tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0601 (blok 132861001): totalSupply 984 flat, freeMinted 984 -> velocity GAGAL.",
 "WORKER": "Run 0601 (blok 132861001): totalSupply 376->381 (+5) -> velocity GAGAL; umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0601: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0601 (blok 132861001): totalSupply 327 flat -> velocity GAGAL.",
 "RIMEVAULT": "Run 0601 (blok 132861001): totalSupply 544->555 (+11); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0601 (blok 132861001): totalSupply 519->520 (+1); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0601 (blok 132861001): totalSupply 644 flat; bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0601 (blok 132861001): totalSupply 1042 flat; bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0601 (blok 132861001): totalSupply 599->616 (+17); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0601 (blok 132861001): totalSupply None, freeMinted 0, freePhaseStart 0 -> masih prelaunch; watchlist-only-upcoming.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0601": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

TC_NOTES = {
 "11-11": "Run 0601: freeMinted 586 flat.",
 "NIUBI": "Run 0601: freeMinted 159 flat.",
 "DROID": "Run 0601: freeMinted 739 flat.",
 "960E-sale": "Run 0601: freeMinted 38 flat.",
 "FUGUI-set1-991": "Run 0601: freeMinted 423 flat.",
 "FUGUI-set2": "Run 0601: freeMinted 626 flat.",
 "ORYN-sale": "Run 0601: tetap paused (totalSupply None).",
 "PESI": "Run 0601: batch-fail persisten (nilai lama dipertahankan).",
 "YAMA PROJECT": "Run 0601: batch-fail persisten (nilai lama dipertahankan).",
}
for name, note in TC_NOTES.items():
    t = reread["track_c"].get(name, {})
    e = track_c.setdefault(name, {})
    if t.get("freeMinted") is not None:
        e["freeMinted"] = t["freeMinted"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 06:01 WIB"
    e["runNote0601_1111"] = note

# MOODENG free-pool SELLOUT: freeMinted 479->500/500 FREE_SHARES, dikonfirmasi segar
# blok 132861394 (freeMinted()=500, FREE_SHARES()=500, totalMinted()=500).
# Per aturan track C: laporkan sekali + hapus dari snapshot.
moodeng = track_c.pop("MOODENG", None)
snap["runNote0601_1111_moodeng_sellout"] = (
    "MOODENG SOLD OUT run 0601: freeMinted 479->500/500 FREE_SHARES "
    "(+21 dalam ~30 mnt; dikonfirmasi segar blok 132861394: freeMinted()=500, "
    "FREE_SHARES()=500, totalMinted()=500) -> free pool 0. Watchlist-only "
    "(agent-shape + website TETAP UNVERIFIED, tidak pernah lead/preview/mint). "
    "Dilaporkan sekali run ini + dihapus dari snapshot track_c.")
sellouts = snap.setdefault("sellouts", [])
sellouts.append({"name": "MOODENG", "sale": "0xbb45668788a08ceceea6b1a0d0f25c1b667e1668",
                 "token": "0x20ad4f682c828db41006ad5742a056abe9d4b1bc",
                 "freeMinted": 500, "FREE_SHARES": 500, "block": 132861394,
                 "wib": "2026-11-11 06:01 WIB", "run": "0601"})

snap["last_run_wib"] = "2026-11-11 06:01 WIB"
snap["last_run_note"] = ("Run 0601: MOODENG free pool SOLD OUT (500/500) - dilaporkan sekali + dihapus dari snapshot; "
    "0 kandidat/strong/early/track-B/track-C baru lainnya; 0 eksekusi; "
    "scan FAST-FAIL (Ankr 401); NIGHTFORGE tetap gate-blocked (free 709/2000 = 35,45%, umur <24 jam s.d. 14:37 WIB); "
    "AgentPals masih prelaunch; binanceai launched=0 (refund phase, tidak berubah).")
snap["runNote0601_1111"] = snap["last_run_note"]
snap["runNote0601_1111_scan"] = ("Pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 36,8 dtk "
    "(head 132861055; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09, kini ~40,5 jam). "
    "Scan leg FAST-FAIL run ini. Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~348.500 blok dan tumbuh).")
snap["runNote0601_1111_binanceai"] = "binanceai.fun: launched()=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132861001) - TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong."
snap["runNote0601_1111_discovery"] = ("Boltbook EN 200 47.602 byte + ZH 200 47.368 byte; 17 alamat (EN) / 17 (ZH), 0 baru vs snapshot + seen + hot-leg-seen. "
    "Sourcify feed 20 terbaru (verified 21:31-22:43Z), 0 baru vs hot-leg-seen; AgentPals tidak muncul di feed run ini. "
    "Sweep EN+ZH: 0 proyek baru (Agentic Gangster free sold out 111/111 - excluded; MOLT AGENT excluded-free-pool-exhausted; Horus AI phase 1 sold out; First-Dollar Grove age-excluded; AGENT MAO paused; Pixel Fox / Coracle / PocketDragons / AgentForge lama). "
    "Odaily 200 263.572 byte + PANews 200 119.505 byte, 0 keyword Agent ID / free mint / free share. Bridge: mtime 2026-11-09 01:21 WIB (STALE), 0 temuan baru. 5c: tanpa output scan baru (scan fast-fail) -> tidak ada backlog ERC-20 baru.")
snap["runNote0601_1111_age_exclusions"] = ("0 BARU run ini (window 05:31->06:01 WIB). Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; "
    "RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); UFO ~22:05 WIB 12 Nov. "
    "MOODENG dihapus karena sold out (bukan age-exclusion). Tidak ada item lain yang dihapus dari snapshot.")

with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE OK block", BLOCK, "| MOODENG removed:", moodeng is not None)
