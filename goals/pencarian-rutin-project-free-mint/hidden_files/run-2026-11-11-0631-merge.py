#!/usr/bin/env python3
"""Merge run 2026-11-11 0631 readings into onchain-snapshot.json. Read-only except snapshot (backup first)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0631"
BLOCK = 132864958
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0631-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0631-reread.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 06:31 WIB"
    return e

VEL = {
 "NIGHTFORGE": "Run 0631 (blok 132864958): totalSupply 712->716 (+4), agentFreeUsed 709->713/2000 = 35,65% (>=25% ✓, probe blok 132864995, paidMinted 3) -> velocity GAGAL (<20). Slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate buka ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0631 (blok 132864958): totalSupply 465->467 (+2), agentFreeUsed 465->467/2000 = 23,35% (<25%, probe blok 132865008) -> velocity GAGAL (<20). Tetap EARLY.",
 "REWINDCLUB": "Run 0631 (blok 132864958): totalSupply 437->442 (+5), agentFreeUsed 437->442/2000 = 22,10% (<25%, probe blok 132865020) -> velocity GAGAL (<20). Tetap EARLY.",
 "LCDSPRITE": "Run 0631 (blok 132864958): totalSupply 483->485 (+2), agentFreeUsed 483->485/2000 = 24,25% (<25%, probe blok 132865033) -> velocity GAGAL (<20). Tetap EARLY.",
 "Pico Alcazar": "Run 0631 (blok 132864958): totalSupply 320->328 (+8) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0631 (blok 132864958): totalSupply 307->314 (+7) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0631 (blok 132864958): totalSupply 316->325 (+9) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0631 (blok 132864958): totalSupply 1695->1727 (+32 dalam ~29,6 mnt = 1,08/mnt vs rate sebelumnya 0,235/mnt -> rasio ~4,6x DAN >=20 token) -> velocity LULUS run ini. TAPI umur peluncuran TETAP UNVERIFIED + free% TETAP UNVERIFIED (tanpa free counter) -> TIDAK promosi ke strong lead; tetap EARLY.",
 "Arcane Stones": "Run 0631 (blok 132864958): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0631 (blok 132864958): totalSupply 409->412 (+3); freeMinted 404->404? (lean: freeClaimed None) -> tetap watchlist-only.",
 "CosmicSentinel": "Run 0631 (blok 132864958): totalSupply 409->412 (+3) -> velocity GAGAL (<20). Tetap watchlist-only.",
 "Dragon Agent": "Run 0631 (blok 132864958): totalSupply 907 flat -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0631: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0631 (blok 132864958): totalSupply 984 flat -> velocity GAGAL.",
 "WORKER": "Run 0631 (blok 132864958): totalSupply 381->387 (+6) -> velocity GAGAL; umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0631: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0631 (blok 132864958): totalSupply 327 flat -> velocity GAGAL.",
 "RIMEVAULT": "Run 0631 (blok 132864958): totalSupply 555->569 (+14); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0631 (blok 132864958): totalSupply 520->523 (+3); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0631 (blok 132864958): totalSupply 644->646 (+2); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0631 (blok 132864958): totalSupply 1042->1045 (+3); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0631 (blok 132864958): totalSupply 616->634 (+18); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0631 (blok 132864958): totalSupply None, freeMinted 0, freePhaseStart 0 -> masih prelaunch; watchlist-only-upcoming.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0631": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

# free-probe fresh values
upd("NIGHTFORGE", agentFreeUsed=713)
upd("SOLDERCATS", agentFreeUsed=467)
upd("REWINDCLUB", agentFreeUsed=442)
upd("LCDSPRITE", agentFreeUsed=485)
# STALL velocity pass
upd("STALL", currentRatePerMin=1.08, velocityRatio=4.6, velocityLegPasses=True)

# WORKER #1 (baru dari Boltbook run ini) - watchlist-only-first-read
contracts["WORKER #1"] = {
    "address": "0x45527ff7971617add06f8b2d24e5b9aecb912fca",
    "name": "WORKER #1",
    "status": "watchlist-only-first-read-2026-11-11",
    "totalSupply": 657,
    "totalMinted": 657,
    "MAX_SUPPLY": 100000,
    "freeAvailable_user": 1,
    "balanceOf_user": 0,
    "owner": "0x41a192cb1cc16cc1ff98dfa9c338f436b41fa5b3",
    "website": "https://agent-worker.pages.dev",
    "websiteEvidence": "Metode G: /llms.txt agent-worker.pages.dev (7.307 byte) mencetak kontrak persis 0x45527ff7971617aDD06F8B2D24E5B9aeCB912fcA + WORKER #2 0xBeAD62a6...; config.js hanya mencetak #2. Gate website PASSED.",
    "gate": "website_verified",
    "launchNote": "UNVERIFIED: tidak ada mintStart/START_TIME view; Sourcify 404 UNVERIFIED; first public mention Boltbook agata.ai ~06:26 WIB 11 Nov (bukan launch time); first mint tidak terkoroborasi (Ankr getLogs mati 401).",
    "freePctNote": "UNVERIFIED: tidak ada free counter/cap view (freeAvailable(address) bool per-wallet saja); totalMinted 657/100.000 = 0,657% total BUKAN % free.",
    "agentShapeNote": "Parsial: freeAvailable(address) + Boltbook-verified mint(1) value 0; TAPI Sourcify UNVERIFIED (tanpa ABI), agentRegistry() revert, tanpa registry bytes evidence -> BUKAN early lead (first mint tidak terverifikasi in-run, 657 sudah ada sebelum run; umur + free% unverified).",
    "sameOwnerNote": "Owner 0x41a192cb... SAMA dengan WORKER #2 (0xbead62...); owner TIDAK ada di same-owner-discards.json (61 entri, dicek run 0631).",
    "velocityLegPasses": False,
    "velocityNote0631": "Run 0631 (blok 132865263): first read totalSupply 657, MAX_SUPPLY 100.000, freeAvailable(user)=1, bal_user=0. Bukan early lead; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
    "discovery": "Boltbook front page EN+ZH run 0631, post agata.ai ~06:26 WIB ('WORKER #1 ... recheck sendiri 657/100.000 — mint(1) value 0 lolos 2 RPC, gratis tepat 1/wallet, owner sama dengan #2').",
    "lastReadBlock": 132865263,
    "lastReadWib": "2026-11-11 06:31 WIB",
}

TC_NOTES = {
 "11-11": "Run 0631: freeMinted 586->587 (+1).",
 "NIUBI": "Run 0631: freeMinted 159 flat.",
 "DROID": "Run 0631: freeMinted 739 flat.",
 "960E-sale": "Run 0631: freeMinted 38 flat.",
 "FUGUI-set1-991": "Run 0631: freeMinted 423 flat.",
 "FUGUI-set2": "Run 0631: freeMinted 626 flat.",
 "ORYN-sale": "Run 0631: tetap paused (totalSupply None).",
 "PESI": "Run 0631: batch-fail persisten (nilai lama dipertahankan).",
 "YAMA PROJECT": "Run 0631: batch-fail persisten (nilai lama dipertahankan).",
}
for name, note in TC_NOTES.items():
    t = reread["track_c"].get(name, {})
    e = track_c.setdefault(name, {})
    if t.get("freeMinted") is not None:
        e["freeMinted"] = t["freeMinted"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 06:31 WIB"
    e["runNote0631_1111"] = note

snap["runNote0631_1111"] = (
    "Run 0631 2026-11-11 06:31 WIB (blok 132864958): 0 kandidat/strong/early/track-B/track-C baru; 0 eksekusi. "
    "STALL velocity LULUS run ini (+32, rasio ~4,6x) tapi umur + free% tetap UNVERIFIED -> tetap EARLY, tanpa promosi/laporan. "
    "NIGHTFORGE tetap strong lead gate-blocked (free 713/2000 = 35,65%, velocity GAGAL +4). "
    "WORKER #1 (0x45527ff797...) baru dari Boltbook -> watchlist-only-first-read (umur + free% UNVERIFIED, website PASSED via llms.txt, owner sama dengan WORKER #2, tidak di discards). "
    "Boltbook: MOODENG sellout 500/500 terkonfirmasi ulang (sudah dilaporkan 0601, tidak diulang); CharMasks CMK1 token bukan lead; NEON sold out 778/778. "
    "Sweep: Agentic Gangster freeMinted 111/111 (blok 132865556, snippet 19 mint basi) + NOVRA freeRemaining 0 -> exclusion tetap. "
    "Scan FAST-FAIL (Ankr 401, preflight 26,2 dtk, head 132864956); watermark tetap 132512564, gap ~352rb blok. "
    "Binanceai launched 0 (refund phase, tidak berubah). Bridge stale (mtime 8 Nov). Sourcify feed 0 baru vs hot-leg-seen. Odaily/PANews 0 keyword hit."
)
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE OK: contracts", len(contracts), "track_c", len(track_c))
