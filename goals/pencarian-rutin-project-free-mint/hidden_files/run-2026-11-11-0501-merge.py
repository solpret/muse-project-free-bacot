#!/usr/bin/env python3
"""Merge run 2026-11-11 0501 readings into onchain-snapshot.json. Read-only except snapshot (backup first)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0501"
BLOCK = 132853451
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0501-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0501-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0501-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 05:01 WIB"
    return e

VEL = {
 "NIGHTFORGE": "Run 0501 (blok 132853451): totalSupply 709->712 (+3), agentFreeUsed 709/2000 = 35,45% (>=25% ✓, probe blok 132854098, paidMinted 3) -> velocity GAGAL (<20). Slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (hot-leg 0449) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0501 (blok 132853451): totalSupply 461->462 (+1), agentFreeUsed 462/2000 = 23,1% (<25%, probe blok 132854112) -> velocity GAGAL (<20). Tetap EARLY.",
 "REWINDCLUB": "Run 0501 (blok 132853451): totalSupply 421->427 (+6), agentFreeUsed 427/2000 = 21,35% (<25%, probe blok 132854121) -> velocity GAGAL (<20). Tetap EARLY.",
 "LCDSPRITE": "Run 0501 (blok 132853451): totalSupply 475->480 (+5), agentFreeUsed 480/2000 = 24,0% (<25%, probe blok 132854131) -> velocity GAGAL (<20). Tetap EARLY.",
 "Pico Alcazar": "Run 0501 (blok 132853451): totalSupply 300->307 (+7) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0501 (blok 132853451): totalSupply 286->293 (+7) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0501 (blok 132853451): totalSupply 295->307 (+12) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0501 (blok 132853451): totalSupply 1670->1683 (+13) -> velocity GAGAL (<20). Tetap EARLY.",
 "Arcane Stones": "Run 0501 (blok 132853451): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0501 (blok 132853451): totalSupply 400->404 (+4); freeMinted 395->399/225.000 = 0,18% -> tetap watchlist-only.",
 "Dragon Agent": "Run 0501 (blok 132853451): totalSupply 906 flat -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0501 (blok 132853451): freeMinted 374->398 (+24, 0,80/mnt vs prev 0,23/mnt = 3,4x) -> velocity LOLOS (>=1,5x DAN >=20) TAPI TIDAK promosi: tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0501 (blok 132853451): totalSupply 984 flat, freeMinted 984 -> velocity GAGAL.",
 "WORKER": "Run 0501 (blok 132853451): totalSupply 360->366 (+6) -> velocity GAGAL; umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0501: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0501 (blok 132853451): totalSupply 326->327 (+1) -> velocity GAGAL.",
 "RIMEVAULT": "Run 0501 (blok 132853451): totalSupply 506->520 (+14); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0501 (blok 132853451): totalSupply 511->515 (+4); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0501 (blok 132853451): totalSupply 641->643 (+2); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0501 (blok 132853451): totalSupply 1039->1041 (+2); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0501 (blok 132853451): totalSupply 578->581 (+3); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0501 (blok 132853451): totalSupply None, freeMinted 0 (tetap); freePhaseStart 0 per hot-leg 0449 -> masih prelaunch, watchlist-only-upcoming, TIDAK di-preview/TIDAK di-mint.",
}
for name, note in VEL.items():
    r = reread.get("reread", {}).get(name, {})
    e = upd(name)
    if r.get("totalSupply") is not None:
        e["previousTotalSupply"] = e.get("totalSupply")
        e["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        e["freeMinted"] = r["freeMinted"]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["runNote0501_1111"] = note
    e["velocityLegPasses"] = (name == "GangDotFun")
for name, d in freeprobe.items():
    e = contracts.get(name, {})
    if d.get("agentFreeUsed()") is not None:
        e["agentFreeUsed"] = d["agentFreeUsed()"]
    if d.get("paidMinted()") is not None:
        e["paidMinted"] = d["paidMinted()"]

# Track-C re-reads
for name, v in reread.get("track_c", {}).items():
    e = track_c.get(name)
    if not isinstance(e, dict):
        continue
    if v.get("freeMinted") is not None:
        e["freeMinted"] = v["freeMinted"]
    if v.get("totalSupply") is not None:
        e["totalSupply"] = v["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 05:01 WIB"
tc = track_c.get("MOODENG", {})
tc["runNote0501"] = "Run 0501: freeMinted 458->469 (+11); agent-shape TETAP UNVERIFIED + website UNVERIFIED -> watchlist-only, TIDAK di-preview/TIDAK di-mint."
for k in ("NIUBI", "DROID", "960E-sale", "FUGUI-set1-991", "FUGUI-set2", "11-11"):
    e = track_c.get(k)
    if isinstance(e, dict):
        e["runNote0501"] = f"Run 0501: freeMinted {e.get('freeMinted')} (tetap); watchlist-only, tanpa perubahan."
for k in ("PESI", "YAMA PROJECT"):
    e = track_c.get(k)
    if isinstance(e, dict):
        e["runNote0501"] = "Run 0501: batch baca gagal semua view (None) - degradasi baca persisten, BUKAN nol; nilai lama dipertahankan; watchlist-only."
snap["last_run_wib"] = "2026-11-11 05:01 WIB"
snap["last_run_note"] = "Run 0501: 0 kandidat/strong/early/track-B/track-C baru; 0 eksekusi; scan FAST-FAIL (Ankr 401); NIGHTFORGE tetap gate-blocked; GangDotFun velocity lolos tapi tanpa Agent-ID gate (bukan promosi); AgentPals masih prelaunch."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGED OK; contracts:", len(contracts), "track_c:", len(track_c))
