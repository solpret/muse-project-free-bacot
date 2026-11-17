#!/usr/bin/env python3
"""Merge run 2026-11-11 0731 readings into onchain-snapshot.json.
Read-only except snapshot (backup first). Values come from the FRESH
0731 reads (reread block 132873113, freeprobe, binanceai, feed probes).
Does NOT copy the stale 0701 merge template."""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0731"
BLOCK = 132873113
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0731-premerge")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0731-reread.json"))
freeprobe = json.load(open(BASE + "run-2026-11-11-0731-freeprobe.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

def upd(name, **kw):
    e = contracts.setdefault(name, {})
    e.update(kw)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 07:31 WIB"
    return e

# ---- velocity notes (interval 0701 -> 0731, ~30.8 mnt, 4113 blok) ----
VEL = {
 "NIGHTFORGE": "Run 0731 (blok 132873113): totalSupply 716->717 (+1, ~0,03/mnt vs prev +4 = 0,13/mnt -> rasio ~0,24x) -> velocity GAGAL (<20). agentFreeUsed 714/2000 = 35,70% (>=25% ✓, probe blok 132873113, paidMinted 3), slot terbuka (bal_user 0, agentFreeByWallet 0), umur terverifikasi <24 jam (deadline 14:37 WIB), TAPI gate website TETAP BLOCKED (recheck gate buka ~12:37 WIB) -> TIDAK di-mint.",
 "SOLDERCATS": "Run 0731 (blok 132873113): totalSupply 469->492 (+23 dalam ~30,8 mnt = 0,75/mnt vs prev +2 = 0,07/mnt -> rasio ~11,2x DAN >=20 token) -> velocity LULUS run ini. TAPI agentFreeUsed 492/2000 = 24,60% (probe blok 132873130, paidMinted 0) MASIH <25% -> TIDAK promosi ke strong lead; tetap EARLY, pantau run berikut (tinggal 8 slot lagi ke 25%).",
 "REWINDCLUB": "Run 0731 (blok 132873113): totalSupply 447->478 (+31 dalam ~30,8 mnt = 1,01/mnt vs prev +5 = 0,17/mnt -> rasio ~6,0x DAN >=20 token) -> velocity LULUS run ini. TAPI agentFreeUsed 478/2000 = 23,90% (probe blok 132873146, paidMinted 0) MASIH <25% -> TIDAK promosi ke strong lead; tetap EARLY, pantau run berikut.",
 "LCDSPRITE": "Run 0731: STRONG-LEAD DIRECT MINT BERHASIL. agentFreeUsed 501/2000 = 25,05% saat probe (>=25% ✓), velocity GAGAL (+12 <20) - strong-lead direct mint tidak butuh velocity. Minted #504 via mint(1) value 0, tx 0xa53db9ecc0f485bbedb4a2286cf86c506c9f47e0a073fcb59e098807e6f05f34, blok 132874232, receipt 1, gas 263482 (~0,0000206 BNB); ownerOf(504)=wallet agent, balanceOf 0->1, agentFreeByWallet 0->1, agentFreeUsed 501->504. Website TERVERIFIKASI (llms.txt mencetak kontrak persis, dicek ulang segar). Audit Binance hasResult=false (tanpa hasil, bukan lolos), GoPlus tanpa data (NFT); preview bersih 000000000 (+1 ERC721 #504). UNREVEALED Sealed Cartridge (tier tidak terverifikasi; tercatat di nft-rarity-inventory.md). Own market Link Cable Swap 0x7746e0a71ef07873df558555f4640b88319daa93 (fee 3%) listedCount 0 -> TIDAK ada floor -> TIDAK di-list. Mint reward claimable 10.000 DOT (TOKEN 0x174afa551d6fb103c728f4b9a78706ed6756b428), pair PCS 0x0 -> belum di-claim, pantau pair.",
 "Pico Alcazar": "Run 0731 (blok 132873113): totalSupply 329->335 (+6) -> velocity GAGAL (<20). Tetap EARLY.",
 "Tiling Hammock": "Run 0731 (blok 132873113): totalSupply 317->322 (+5) -> velocity GAGAL (<20). Tetap EARLY.",
 "Hexel Pantry": "Run 0731 (blok 132873113): totalSupply 329->332 (+3) -> velocity GAGAL (<20). Tetap EARLY.",
 "STALL": "Run 0731 (blok 132873113): totalSupply 1735->1764 (+29 dalam ~30,8 mnt = 0,94/mnt vs prev +8 = 0,26/mnt -> rasio ~3,5x DAN >=20 token) -> velocity LULUS run ini. TAPI umur + free% TETAP UNVERIFIED -> tetap EARLY, tanpa promosi.",
 "Arcane Stones": "Run 0731 (blok 132873113): totalSupply 650->665 (+15) -> velocity GAGAL (<20). Tetap EARLY.",
 "Cosmic Sentinel": "Run 0731 (blok 132873113): totalSupply 414->416 (+2); freeMinted 411 -> tetap watchlist-only.",
 "CosmicSentinel": "Run 0731 (blok 132873113): totalSupply 414->416 (+2) -> velocity GAGAL (<20). Tetap watchlist-only.",
 "Dragon Agent": "Run 0731 (blok 132873113): totalSupply 907->909 (+2) -> velocity GAGAL; umur + free% TETAP UNVERIFIED. Watchlist-only.",
 "GangDotFun": "Run 0731: totalSupply batch-fail lagi (None) - degradasi baca, BUKAN nol; freeMinted 441; nilai lama dipertahankan; tanpa Agent-ID gate + free% UNVERIFIED -> tetap watchlist-only first-read.",
 "Kitebots": "Run 0731 (blok 132873113): totalSupply 984 flat -> velocity GAGAL.",
 "WORKER": "Run 0731 (blok 132873113): totalSupply 410->422 (+12) -> velocity GAGAL (<20). Umur + free% TETAP UNVERIFIED -> tetap watchlist-only-first-read.",
 "WORKER #1": "Run 0731 (blok 132873113): totalSupply 659->682 (+23 dalam ~30,8 mnt = 0,75/mnt vs prev +2 = 0,07/mnt -> rasio ~11,2x DAN >=20 token) -> velocity LULUS run ini. TAPI umur + free% TETAP UNVERIFIED (tanpa free counter; 682/100.000 = 0,68% total BUKAN % free) -> TIDAK promosi; tetap watchlist-only-first-read, TIDAK di-preview/TIDAK di-mint.",
 "Skywe Legion": "Run 0731: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan; umur + free% + website TETAP UNVERIFIED; watchlist-only.",
 "NIGHTFORGE B": "Run 0731 (blok 132873113): totalSupply 327->342 (+15) -> velocity GAGAL (<20). Tetap EARLY.",
 "RIMEVAULT": "Run 0731 (blok 132873113): totalSupply 576->597 (+21); bal_user=1; minted-by-user, bukan kandidat.",
 "MYCELIX": "Run 0731 (blok 132873113): totalSupply 529->559 (+30); bal_user=1; minted-by-user, bukan kandidat.",
 "ORBITJANITOR": "Run 0731 (blok 132873113): totalSupply 650->657 (+7); bal_user=1; minted-by-user, bukan kandidat.",
 "EMBERANVIL": "Run 0731 (blok 132873113): totalSupply 1045->1064 (+19); bal_user=1; minted-by-user, bukan kandidat.",
 "BYTEBLOOM": "Run 0731 (blok 132873113): totalSupply 640->671 (+31); bal_user=1; minted-by-user, bukan kandidat.",
 "AgentPals": "Run 0731: totalSupply batch-fail (None) - degradasi baca; freeMinted 38/300 = 12,67% (sama dengan hot-leg 0729), slot user terbuka, tetap watchlist-only (12,67% < 25%, website UNVERIFIED) - BUKAN lead/kandidat, TIDAK di-preview/TIDAK di-mint.",
}
for name, note in VEL.items():
    r = reread["reread"].get(name, {})
    kw = {"velocityNote0731": note}
    if r.get("totalSupply") is not None:
        kw["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None:
        kw["freeMinted"] = r["freeMinted"]
    upd(name, **kw)

# fresh free-probe values
upd("NIGHTFORGE", agentFreeUsed=freeprobe["NIGHTFORGE"]["agentFreeUsed()"])
upd("SOLDERCATS", agentFreeUsed=freeprobe["SOLDERCATS"]["agentFreeUsed()"])
upd("REWINDCLUB", agentFreeUsed=freeprobe["REWINDCLUB"]["agentFreeUsed()"])
upd("LCDSPRITE", agentFreeUsed=504,
    status="minted-by-user-2026-11-11",
    mintedTokenId=504,
    mintTx="0xa53db9ecc0f485bbedb4a2286cf86c506c9f47e0a073fcb59e098807e6f05f34",
    mintBlock=132874232, mintGasUsed=263482,
    mintToken="0x174afa551d6fb103c728f4b9a78706ed6756b428",
    mintRewardClaimable=10000,
    market="0x7746e0a71ef07873df558555f4640b88319daa93",
    marketListedCount=0)

# ---- track_c re-read (flat unless noted) ----
TC_NOTES = {
 "11-11": "Run 0731: freeMinted 602 flat; slot user 0. Tetap watchlist-only.",
 "NIUBI": "Run 0731: freeMinted 159 flat. Tetap watchlist-only.",
 "DROID": "Run 0731: freeMinted 739 flat. Tetap watchlist-only.",
 "960E-sale": "Run 0731: freeMinted 38 flat. Tetap watchlist-only.",
 "FUGUI-set1-991": "Run 0731: freeMinted 423 flat. Tetap watchlist-only.",
 "FUGUI-set2": "Run 0731: freeMinted 626 flat. Tetap watchlist-only.",
 "VISION": "Run 0731: totalSupply 3,159e27 -> 3,1842e27 (minting berjalan) tapi free views tetap None -> tetap watchlist-only-age-unverified, BUKAN promosi.",
 "ORYN-sale": "Run 0731: paused tetap (batch-fail persisten, nilai lama dipertahankan). Tetap watchlist-only-paused.",
 "PESI": "Run 0731: batch-fail persisten (nilai lama dipertahankan); gate-blocked sudah dilaporkan, tanpa perubahan yang bisa ditentukan.",
 "YAMA PROJECT": "Run 0731: batch-fail persisten (nilai lama dipertahankan). Tetap watchlist-only.",
 "LOWB": "Run 0731: totalFreeMinted 693 (hot-leg 0729), opened 0. Tetap watchlist-only-not-open.",
 "UFO": "Run 0731: supply 9e30 flat. Tetap watchlist-only (tutup 12 Nov 22:05 WIB).",
 "BOME-50CD": "Run 0731: mintOpen 0 tetap. Tetap watchlist-only-not-open.",
}
for name, note in TC_NOTES.items():
    if name in track_c and isinstance(track_c[name], dict):
        track_c[name]["runNote0731"] = note
        r = reread["track_c"].get(name, {})
        if r.get("freeMinted") is not None:
            track_c[name]["freeMinted"] = r["freeMinted"]
        if r.get("totalSupply") is not None:
            track_c[name]["totalSupply"] = r["totalSupply"]

# ---- Sourcify feed wave (20 kontrak, template 35-fn agent-mint) ----
feed_probe = {}
feed_names = {}
if os.path.exists(BASE + "run-2026-11-11-0731-feed-probe.json"):
    feed_probe = json.load(open(BASE + "run-2026-11-11-0731-feed-probe.json"))
if os.path.exists(BASE + "run-2026-11-11-0731-feed-names.json"):
    feed_names = json.load(open(BASE + "run-2026-11-11-0731-feed-names.json"))
for addr, p in feed_probe.items():
    nm = feed_names.get(addr) or {}
    if isinstance(nm, dict):
        name = nm.get("name")
        sym = nm.get("symbol")
    elif isinstance(nm, list) and nm:
        name = nm[0]
        sym = nm[1] if len(nm) > 1 else None
    else:
        name = None
        sym = None
    supply = p.get("totalSupply")
    key = name or ("feed-" + addr[:10])
    is_minting = (supply or 0) > 0
    e = contracts.setdefault(key, {})
    e.update({
        "address": addr,
        "name": name,
        "symbol": sym,
        "kind": "ERC721",
        "status": "early-lead-reported-2026-11-11" if is_minting else "watchlist-only-first-read-2026-11-11",
        "totalSupply": supply,
        "owner": p.get("owner"),
        "ownerInDiscards": p.get("ownerInDiscards"),
        "costOf_user_1": p.get("costOf_user_1"),
        "mintsLeft_user": p.get("mintsLeft_user"),
        "price_wei": p.get("price_wei"),
        "registry_bytes": p.get("registry_bytes"),
        "sourcify": "exact_match",
        "sourcifyVerifiedAt": p.get("verifiedAt"),
        "firstSeenBlock": BLOCK,
        "firstSeenWib": "2026-11-11 07:31 WIB",
        "lastReadBlock": BLOCK,
        "lastReadWib": "2026-11-11 07:31 WIB",
        "source": "Sourcify feed run 0731 (verified 00:31-00:34Z 11 Nov) + verifikasi on-chain run ini",
        "launchNote": "UMUR UNVERIFIED: tidak ada stated launch time; Sourcify verifiedAt BUKAN launch time; first mint tidak terkoroborasi via logs (Ankr mati).",
        "websiteNote": "GATE website BELUM DINILAI (early lead). Bila promosi mendekat, gate wajib dinilai penuh (methods A-N) sebelum preview/mint apa pun.",
        "baselineNote": ("EARLY LEAD run 0731 (dilaporkan sekali sebagai gelombang 12 kontrak): template agent-mint 35-fn (mintWithAgentTokenId/agentIds/mintedByAgent), bytecode mengandung registry resmi 0x60B926...022F, agentIds()=registry resmi; costOf(user,1)=0 + mintsLeft(user)=10 + sim mintWithAgentTokenId/mint(1) value 0 SUKSES di Oak Lea -> jalur gratis TERVERIFIKASI untuk wallet agent; totalSupply %s saat baca pertama (first-seen minting). Free%% vs MAX_SUPPLY UNVERIFIED (tanpa free counter; template ini tidak punya free views). Umur + website UNVERIFIED. Owner %s bersih dari same-owner-discards.json. TIDAK di-preview/TIDAK di-mint (tier early). Promosi ke strong lead bila 3 kaki terpenuhi + gate website lolos." % (supply, p.get("owner"))) if is_minting else ("WATCHLIST-ONLY first-read run 0731: template agent-mint 35-fn yang sama (registry bytes, costOf(user,1)=0, mintsLeft 10), TAPI totalSupply 0 (belum ada mint) -> BUKAN early lead (first mint belum ada); dipantau run berikut. Umur + website UNVERIFIED. Owner %s bersih dari discards." % p.get("owner")),
    })

snap["last_run_wib"] = "2026-11-11 07:31 WIB"
snap["last_run"] = 1
snap["last_run_note"] = ("Run 0731: LCDSPRITE #504 MINT BERHASIL (strong-lead direct mint, tx 0xa53db9ecc0f485bbedb4a2286cf86c506c9f47e0a073fcb59e098807e6f05f34, blok 132874232, gas 263482, receipt 1; ownerOf(504)=agent; market own listedCount 0 -> tidak di-list; rarity UNREVEALED Sealed Cartridge). "
 "Gelombang feed baru: 12 EARLY lead (template agent-mint 35-fn, gratis costOf=0 terverifikasi, supply 23-34) + 8 watchlist-only (supply 0). "
 "SOLDERCATS velocity LULUS tapi 24,60% <25%; REWINDCLUB velocity LULUS tapi 23,90% <25% — keduanya tetap EARLY. "
 "NIGHTFORGE tetap strong lead gate-blocked (35,70%, velocity gagal, recheck gate ~12:37 WIB). "
 "0 kandidat/track-B/track-C baru; scan FAST-FAIL (Ankr 401); binanceai launched=0 (refund phase, tidak berubah).")
snap["runNote0731"] = snap["last_run_note"]
with open(BASE + "onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(contracts), "track_c:", len(track_c))
