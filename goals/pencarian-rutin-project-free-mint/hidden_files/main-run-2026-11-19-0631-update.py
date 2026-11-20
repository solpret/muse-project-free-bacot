#!/usr/bin/env python3
"""Main run free-mint-search 2026-11-19 06:31 WIB — snapshot update (surgical).
Loads the snapshot fresh, applies this run's verified reads, atomic replace.
Read values only; failed reads keep old values (never zero).
"""
import json, os, tempfile

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
P = BASE + "onchain-snapshot.json"
s = json.load(open(P))
C = s["contracts"]
BLK = 134401533
NOW = "2026-11-19 ~06:31 WIB"

def note(key, text):
    C[key]["runNote0631_1119"] = text

# HIVE Agents: 1265 flat, velocity fails
h = C["HIVE Agents"]
h["previousTotalSupply"] = 1265
h["totalSupply"] = 1265
h["mintedInInterval"] = 0
h["intervalMinutes"] = 30.5
h["currentRatePerMin"] = 0.0
h["previousRatePerMin"] = 0.0
h["velocityLegPasses"] = False
h["lastReadBlock"] = BLK
h["lastReadWib"] = NOW
h["balanceOf_user"] = 1
note("HIVE Agents", f"Run 0631 (blok {BLK}, interval ~30.5 mnt vs run 0601): totalSupply 1265->1265 (+0, 0.0/mnt vs prev 0.0 = Nonex) -> velocity GAGAL; balanceOf(user)=1; minted-by-user. DIAM.")

# Bubblebruin: 2630 flat, freeClaimed 2624/7777 = 33.7%
b = C["Bubblebruin"]
b["previousTotalSupply"] = 2630
b["totalSupply"] = 2630
b["freeClaimed"] = 2624
b["freePctVerified"] = round(2624 / 7777 * 100, 1)
b["mintedInInterval"] = 0
b["intervalMinutes"] = 30.5
b["currentRatePerMin"] = 0.0
b["lastReadBlock"] = BLK
b["lastReadWib"] = NOW
b["balanceOf_user"] = 1
note("Bubblebruin", f"Run 0631 (blok {BLK}): totalSupply 2630 FLAT, freeClaimed 2624/7777 = 33.7%, balanceOf(user)=1, minted-by-user. DIAM.")

# STOCK AGENT: free 75.2% (>70%) but age unverified + website gate failed -> no promotion
st = C["STOCK AGENT"]
st["totalSupply"] = 835
st["freeLeft"] = 276
st["FREE_SUPPLY"] = 1111
st["freePctVerified"] = round(835 / 1111 * 100, 1)
st["lastReadWib"] = NOW
st["lastReadBlock"] = BLK
st["balanceOf_user"] = 0
note("STOCK AGENT", f"Run 0631 (blok {BLK}): totalSupply 835, freeLeft 276, freeClaimed 835/1111 = 75.2% (>70% strong-lead bar), slot user TERBUKA (balanceOf 0; quote 0 di hot-leg 0619). TAPI umur UNVERIFIED + website gate BELUM lolos (contractURI revert, no site) -> BUKAN strong lead, TIDAK promosi, TIDAK mint. Tanpa perubahan vs 0619.")

# Lumenhold: free 83.9% but age unverified -> not strong lead
lh = C["Lumenhold"]
lh["totalSupply"] = 1264
lh["freeClaimed"] = 1259
lh["FREE_SUPPLY"] = 1500
lh["freePctVerified"] = round(1259 / 1500 * 100, 1)
lh["lastReadWib"] = NOW
lh["lastReadBlock"] = BLK
lh["balanceOf_user"] = 0
note("Lumenhold", f"Run 0631 (blok {BLK}): totalSupply 1264, freeClaimed 1259/1500 = 83.9% (>70%), slot user TERBUKA (balanceOf 0). TAPI umur UNVERIFIED -> BUKAN strong lead, BUKAN kandidat. Tanpa perubahan vs 0619.")

# AGATE-Pass / ARKYN: reads failed this run (revert/empty) - keep old values, record failure
for k in ("AGATE-Pass", "ARKYN"):
    C[k]["lastReadWib"] = NOW
    note(k, f"Run 0631 (blok {BLK}): baca on-chain GAGAL (totalSupply revert/kosong; fast_rpc batch 429 + single-call empty) - nilai lama dipertahankan, BUKAN nol; balanceOf(user)=0 terbaca. Tanpa perubahan status.")

# Mine Card: 1405 (was 1390 at 00:01), not agent-shaped, watchlist-only
mc = C["Mine Card"]
mc["totalSupply"] = 1405
mc["totalMinted"] = 1405
mc["lastReadWib"] = NOW
mc["lastReadBlock"] = BLK
note("Mine Card", f"Run 0631 (blok {BLK}): totalSupply 1405 (00:01: 1390, Boltbook ~06:38: 1404) - gerak lambat; balanceOf(user)=0. Bukan agent-shaped (tanpa registry, launchNote 17 Nov) -> bukan lead. Tanpa perubahan status.")

# Kigae: NEW checked entry - age-excluded (launch <= 4 Nov, ~17 days)
C["Kigae"] = {
    "address": "0x33fd00af8bff3db611d3222d394da33eaaa6a566",
    "status": "checked-age-excluded-2026-11-19",
    "totalSupply": 1109,
    "freeMinted": 1091,
    "FREE_SUPPLY": 2024,
    "freeLeft": 933,
    "MAX_SUPPLY": 2888,
    "freePctVerified": round(1091 / 2024 * 100, 1),
    "balanceOf_user": 0,
    "lastReadBlock": BLK,
    "lastReadWib": NOW,
    "launchNote": "Umur AGE-EXCLUDED: pertama terlihat hot-leg 2026-11-02 17:04 WIB (sourcify-feed); Boltbook tesnetra.ai: 768 minted pada 4 Nov -> launch <= 4 Nov, umur ~15-17 hari pada 19 Nov, JAUH >24 jam. Fase buka 72 jam. BUKAN kandidat/strong lead.",
    "baselineNote": "Diverifikasi on-chain run 0631 19 Nov (blok 134401533): totalSupply 1109, freeMinted 1091/2024 = 53.9% (>50%), freeLeft 933, balanceOf(user)=0 (slot belum dipakai). Velocity baseline pertama dicatat (tidak lolos - belum ada rate sebelumnya + pace historis lambat 768->1109 dalam 15 hari). X discussion: post Boltbook tesnetra.ai + qihuy cross-check 1.106/2.888. TIDAK dilaporkan (age-excluded, bukan perubahan status); tidak masuk watchlist aktif; hanya dilaporkan lagi bila fase/batch mint BARU terverifikasi.",
}
# DeepShard: NEW watchlist-only entry (age + free% unverified)
C["DeepShard"] = {
    "address": "0xC463960af285b7EDA0909D362Ae31783597C2076",
    "status": "watchlist-only-age-free-unverified-2026-11-19",
    "totalSupply": 259,
    "MAX_SUPPLY": 3333,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "lastReadBlock": BLK,
    "lastReadWib": NOW,
    "firstSeenWib": "2026-11-19T00:51:25+07:00",
    "launchNote": "Umur UNVERIFIED: pertama terlihat hot-leg 00:51 WIB 19 Nov (sourcify-feed); Sourcify exact_match 2026-11-18; tidak ada stated launch time; first-mint getLogs terblokir Ankr 401.",
    "baselineNote": "Watchlist-only run 0631: totalSupply 259/3333 = 7.8% (post Boltbook drhmwt.ai: 254 di blok 134401026, mint() value 0 lolos sim wallet Agent-ID, gate Agent-ID ON). Shape-check hot-leg 00:51: S1/S2 false (mint=True, quote=False, free=[] TANPA free view, agent=True) -> free% UNVERIFIED, bukan track-C. Bukan early lead (first mint sebelum run ini, 254 sudah minted saat first read). Dilaporkan hanya bila umur terverifikasi <24h + free% terverifikasi + promosi tier.",
}

# pending claim binanceai.fun: still refund/failed phase
pc = s["pending_claims"]["binanceai.fun"]
pc["launched"] = 0
pc["failed"] = 1
pc["isRefundPhase"] = 1
pc["tokenClaimed_user"] = 0
pc["totalShares"] = 3110
pc["lastReadWib"] = NOW
pc["runNote0631_1119"] = f"Run 0631 (blok {BLK}): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares=3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM."

# Sourcify batch checked this run (compact, one key)
s["checkedSourcify0631_1119"] = (
    "Run 0631: 5 kontrak baru feed Sourcify di-shape-check (S1/S2 + agent-shape): "
    "0x867884e9 (28 fns, mint=True, agent=False, free=[]) 0x84045F43 (18 fns, mint=False, agent=False) "
    "0x796A08bd (64 fns, mint=False, agent=False) 0x7aFb047e (63 fns, quote=True, agent=False) "
    "0x5210F29f (60 fns, mint=False, agent=False) - SEMUA S1/S2 false, tanpa agent ref, tanpa free view -> bukan lead, tidak masuk snapshot."
)

fd, tmp = tempfile.mkstemp(dir=BASE, prefix="snapshot-", suffix=".tmp")
with os.fdopen(fd, "w") as f:
    json.dump(s, f, indent=1)
os.replace(tmp, P)
print("snapshot updated OK; contracts:", len(C))
