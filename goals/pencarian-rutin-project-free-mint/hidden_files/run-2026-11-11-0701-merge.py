#!/usr/bin/env python3
"""Merge run 2026-11-11 0701 readings into onchain-snapshot.json. Read-only except snapshot (backup first)."""
import json, shutil, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0701"
BLOCK = 132869000
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0701-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0701-reread.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 07:01 WIB"
    return e

VEL = {
 "NIGHTFORGE": "Run 0701 (blok 132869000): totalSupply 716 flat (+0), agentFreeUsed 713/2000 = 35,65% (>=25% ✓, probe blok 132869151, paidMinted 3) -> velocity GAGAL (<20). Slot terbuka (bal_user 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate buka ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0701 (blok 132869000): totalSupply 467->469 (+2), agentFreeUsed 469/2000 = 23,45% (<25%, probe blok 132869160) -> velocity GAGAL (<20). Tetap EARLY.",
 "REWINDCLUB": "Run 0701 (blok 132869000): totalSupply 442->447 (+5), agentFreeUsed 447/2000 = 22,35% (<25%, probe blok 132869168) -> velocity GAGAL (<20). Tetap EARLY.",
 "LCDSPRITE": "Run 0701 (blok 132869000): totalSupply 485->489 (+4), agentFreeUsed 489/2000 = 24,45% (<25%, probe blok 132869174) -> velocity GAGAL (<20). Tetap EARLY.",
 "Pico Alcazar": "Run 0701 (blok 132869000): totalSupply 328->329 (+1) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0701 (blok 132869000): totalSupply 314->317 (+3) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0701 (blok 132869000): totalSupply 325->329 (+4) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0701 (blok 132869000): totalSupply 1727->1735 (+8 dalam ~30,3 mnt = 0,264/mnt vs rate sebelumnya 1,08/mnt -> rasio ~0,24x) -> velocity GAGAL run ini (lulus run 0631). Umur + free% TETAP UNVERIFIED -> tetap EARLY, tanpa promosi.",
 "Arcane Stones": "Run 0701 (blok 132869000): totalSupply 650 flat -> velocity GAGAL. Tetap EARLY.",
 "Cosmic Sentinel": "Run 0701 (blok 132869000): totalSupply 412->414 (+2); freeMinted 409 -> tetap watchlist-only.",
 "CosmicSentinel": "Run 0701 (blok 132869000): totalSupply 412->414 (+2) -> velocity GAGAL (<20). Tetap watchlist-only.",
 "Dragon Agent": "Run 0701 (blok 132869000): totalSupply 907 flat -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0701: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0701 (blok 132869000): totalSupply 984 flat -> velocity GAGAL.",
 "WORKER": "Run 0701 (blok 132869000): totalSupply 387->410 (+23 dalam ~30,3 mnt = 0,759/mnt vs interval sebelumnya +6/~29,6 mnt = 0,203/mnt -> rasio ~3,7x DAN >=20 token) -> velocity LULUS run ini. TAPI umur + free% TETAP UNVERIFIED (tanpa free counter; 410/100.000 = 0,41% total BUKAN % free) -> TIDAK promosi ke strong lead; tetap watchlist-only-first-read, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0701: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0701 (blok 132869000): totalSupply 327 flat -> velocity GAGAL.",
 "RIMEVAULT": "Run 0701 (blok 132869000): totalSupply 569->576 (+7); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0701 (blok 132869000): totalSupply 523->529 (+6); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0701 (blok 132869000): totalSupply 646->650 (+4); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0701 (blok 132869000): totalSupply 1045 flat; bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0701 (blok 132869000): totalSupply 634->640 (+6); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0701: batch reread gagal semua view (None) - degradasi baca, nilai lama dipertahankan. Hot-leg 0659 (blok ~132868508, lebih segar): freeMinted 22->28/300 (9,33%), slot user terbuka, tetap watchlist-only (9,33% < 25%, website UNVERIFIED) - BUKAN lead/kandidat, TIDAK di-preview/TIDAK di-mint.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0701": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

# free-probe fresh values
upd("NIGHTFORGE", agentFreeUsed=713)
upd("SOLDERCATS", agentFreeUsed=469)
upd("REWINDCLUB", agentFreeUsed=447)
upd("LCDSPRITE", agentFreeUsed=489)
# STALL velocity fail this run; WORKER velocity pass (no promotion)
upd("STALL", currentRatePerMin=0.264, velocityRatio=0.24, velocityLegPasses=False)
upd("WORKER", currentRatePerMin=0.759, previousRatePerMin=0.203, velocityRatio=3.74, velocityLegPasses=True)

# WORKER #1 fresh read with block capture
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
w1 = "0x45527ff7971617aDD06F8B2D24E5B9aeCB912fcA"
calls = [{"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": w1, "data": sel("totalSupply()")}, "latest"]},
         {"jsonrpc": "2.0", "id": 2, "method": "eth_blockNumber", "params": []}]
w1_block, w1_supply = None, None
for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                              "-H", "Content-Type: application/json", "-d", json.dumps(calls)],
                             capture_output=True, text=True, timeout=30).stdout
        r = json.loads(out)
        if isinstance(r, list) and len(r) == 2:
            w1_supply = to_int(r[0].get("result")); w1_block = int(r[1]["result"], 16)
            break
    except Exception:
        continue
print("WORKER #1 fresh:", w1_supply, "block", w1_block)
if w1_supply is not None:
    e = contracts.setdefault("WORKER #1", {})
    e["totalSupply"] = w1_supply
    e["totalMinted"] = w1_supply
    e["lastReadBlock"] = w1_block
    e["lastReadWib"] = "2026-11-11 07:01 WIB"
    e["velocityNote0701"] = f"Run 0701 (blok {w1_block}): totalSupply 657->659 (+2) -> velocity GAGAL (<20). Umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka; watchlist-only-first-read, TIDAK di-preview/TIDAK di-mint."

TC_NOTES = {
 "11-11": "Run 0701: freeMinted 587 flat.",
 "NIUBI": "Run 0701: freeMinted 159 flat.",
 "DROID": "Run 0701: freeMinted 739 flat.",
 "960E-sale": "Run 0701: freeMinted 38 flat.",
 "FUGUI-set1-991": "Run 0701: freeMinted 423 flat.",
 "FUGUI-set2": "Run 0701: freeMinted 626 flat.",
 "ORYN-sale": "Run 0701: tetap paused (totalSupply None).",
 "PESI": "Run 0701: batch-fail persisten (nilai lama dipertahankan).",
 "YAMA PROJECT": "Run 0701: batch-fail persisten (nilai lama dipertahankan).",
 "VISION": "Run 0701: totalSupply 3,0978e27 -> 3,159e27 (+61,2 jt token) - minting berjalan; freeMinted None (tanpa free view); status tetap watchlist-only-age-unverified, BUKAN promosi.",
 "0x5f76cAb7-5a-hit": "Run 0701: totalSupply sama dengan VISION (kontrak sama) 3,0978e27 -> 3,159e27; views tetap unverified; status tetap watchlist-only-shape-verified-views-unverified.",
}
for name, note in TC_NOTES.items():
    t = reread["track_c"].get(name, {})
    e = track_c.setdefault(name, {})
    if t.get("freeMinted") is not None:
        e["freeMinted"] = t["freeMinted"]
    if t.get("totalSupply") is not None:
        e["totalSupply"] = t["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 07:01 WIB"
    e["runNote0701_1111"] = note

snap["runNote0701_1111"] = (
    "Run 0701 2026-11-11 07:01 WIB (blok 132869000): 0 kandidat/strong/early/track-B/track-C baru; 0 eksekusi. "
    "WORKER velocity LULUS run ini (+23, rasio ~3,7x) tapi umur + free% tetap UNVERIFIED -> tetap watchlist-only-first-read, tanpa promosi/laporan. "
    "STALL velocity GAGAL run ini (+8, rasio 0,24x; lulus run 0631). "
    "NIGHTFORGE tetap strong lead gate-blocked (free 713/2000 = 35,65%, velocity GAGAL +0; recheck gate ~12:37 WIB). "
    "WORKER #1 657->659 (+2), velocity GAGAL. AgentPals batch-fail reread; hot-leg 0659: freeMinted 28/300 (9,33%), tetap watchlist-only. "
    "Boltbook: 1 alamat 'baru' 0x2ab4adfbe79... ternyata hash transaksi klaim BOLT (post nicodart.ai, blok 132867994), BUKAN kontrak - false positive regex, bukan lead. "
    "Sweep: WNO sudah minted-by-user 10 Nov (hasil pencarian basi); Agentic Gangster sold out 111/111; MOLT/NOVRA free pool habis; Horus phase 1 sold out; First-Dollar Grove age-excluded; UFO sudah di track_c. "
    "Sourcify feed 0 baru vs hot-leg-seen (2 teratas sudah dicek hot-leg 0659, bukan sale-shape). "
    "Scan FAST-FAIL (Ankr 401, preflight 17,6 dtk, head 132869168); watermark tetap 132512564, gap ~356rb blok. "
    "Binanceai launched 0 (refund phase, tidak berubah). Bridge stale (mtime 8 Nov), same-owner-discards mtime 10 Nov 20:22 (tidak ada entri baru dicek). Odaily/PANews 0 keyword hit. "
    "VISION totalSupply +61,2 jt token (minting berjalan) tapi free views tetap None -> tetap watchlist-only-age-unverified, bukan promosi."
)
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE OK: contracts", len(contracts), "track_c", len(track_c))
