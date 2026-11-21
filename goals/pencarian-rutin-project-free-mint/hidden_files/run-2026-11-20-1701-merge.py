#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 17:01 WIB into onchain-snapshot.json.
Main re-read ~17:05 WIB (51 kontrak, 430 eth_call, 236 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; blok merge 134676380).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama;
lastReadBlock/Wib hanya di-update bila new_supply terbaca (bukan None).
Read-only kecuali snapshot + scan-state note.
Temuan run ini: velocity LOLOS 0; Stromboat totalMinted 373->481 (+108,
3.375/mnt vs prev 0.0 = ratio None) -> velocity GAGAL + free% UNVERIFIED
(freeMinted view null) + umur UNVERIFIED + website gate sudah GAGAL ->
bukan kandidat/strong lead, DIAM; AgentBadge-ABDG 645->652 (+7, 1.36x,
<20 token) velocity GAGAL; ARKYN +2 (1.93x tapi <20) GAGAL; STOCK AGENT
941 FLAT, free 84.7% (umur/website UNVERIFIED, bukan strong lead);
Lumenhold + AUGENT + EIM GAGAL baca run ini (transport), baseline
dipertahankan (Lumenhold terakhir 1281/1500 = 85.4% hot-leg 16:49);
Turtle 44/88 = 50.0% + Lion 42/88 = 47.7% (hot-leg 16:54, tanpa perubahan);
ONI 208 FLAT; binanceai launched/failed/isRefundPhase GAGAL baca run ini,
nilai terakhir hot-leg 16:54 (0/1/1) dipertahankan, totalShares 3110;
bsccat freeMinted 574 FLAT; AONE 10000 FLAT (sold out).
Sourcify 1 baru (0xd6809e7F: 8 fns, tanpa mint/quote/free/agent -> S1/S2
FAIL); Boltbook EN 45.070 byte (11 alamat) + ZH 43.275 byte (10 alamat),
1 baru (0x40Ecef2D, n_fns 0 -> FAIL); 0 shape hit; keduanya tanpa entri
snapshot. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded).
Sweep EN/ZH: tanpa proyek baru <24 jam terkonfirmasi; YAMA (sale
0x86D779fc...) diteruskan subagen sebagai data mentah - SUDAH di snapshot/
track_c (hot-leg: totalShares 3100, totalFreeShares 3098, freeUsed user 0),
bukan temuan baru; Lenx Agent Pass (~9 Nov) + Oathbots (28 Okt) sudah tua.
Route 6: Square tanpa proyek baru (AI frog paid-only 0,002 BNB/share,
tutup 20 Nov 15:45 UTC); Odaily tanpa pengumuman Agent ID; PANews fetch
basi (17 Nov); DappBay: STOCK/Lumenhold/Turtle/Lion tidak ada listing.
Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP
134086385, gap ~590.000 blok. Track-C 5c: tanpa output scan baru.
TIDAK ada lead/kandidat/eksekusi baru - DIAM."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~17:07 WIB"
BLOCK = 134676380
reread = json.load(open(BASE + "run-2026-11-20-1701-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1701")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1701-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
n_null = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is None:
        sv["runNote1701_1120"] = (
            f"Run 1701 (blok ~{BLOCK}): baca GAGAL (transport-degraded, nilai lama "
            f"({old_sup}) dipertahankan, velocity TIDAK dihitung; bukan kandidat/strong lead. DIAM.")
        n_null += 1
        continue
    sv["previousTotalSupply"] = old_sup
    sv["totalSupply"] = new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"] = v["delta"]
        sv["intervalMinutes"] = v["minutes"]
        sv["currentRatePerMin"] = v["rate_per_min"]
    sv["velocityLegPasses"] = bool(v["velocity_pass"])
    if v["free_pct"] is not None:
        sv["freePctInference"] = v["free_pct"]
    sv["lastReadBlock"] = BLOCK
    sv["lastReadWib"] = NOW_WIB
    sv["runNote1701_1120"] = (
        f"Run 1701 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini (208 FLAT vs 1631)
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1701_1120"] = (
        f"Run 1701 (blok ~{BLOCK}): totalMinted {oni['totalMinted']} (FLAT vs 1631); "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# AgentBadge-ABDG: totalMinted 645->652 (+7) run ini
ab = snap.get("contracts", {}).get("AgentBadge-ABDG", {})
if ab:
    ab["totalMinted"] = 652
    ab["freePctInference"] = round(100 * 652 / 3333, 1)
    ab["lastReadBlock"] = BLOCK
    ab["lastReadWib"] = NOW_WIB
    ab["runNote1701_1120"] = (
        "Run 1701 (blok 134676380, interval ~32 mnt vs run 1631): "
        "totalMinted 645->652 (+7, 0.219/mnt vs baseline 0.161/mnt = 1.36x, <1.5x DAN <20 token) -> velocity GAGAL; "
        "free 652/3333 = 19.6% (<50% dan <70%); balanceOf(user)=0; umur launch tetap UNVERIFIED; "
        "status watchlist-only-age-unverified-2026-11-20. DIAM; tetap di reread set run berikut.")
# Stromboat: +108 tapi velocity GAGAL (prev rate 0, ratio None) + free% UNVERIFIED + umur UNVERIFIED + gate GAGAL
sb = snap.get("contracts", {}).get("Stromboat", {})
if sb:
    sb["totalMinted"] = 481
    sb["previousTotalSupply"] = 373
    sb["mintedInInterval"] = 108
    sb["intervalMinutes"] = 32.0
    sb["currentRatePerMin"] = 3.375
    sb["velocityLegPasses"] = False
    sb["lastReadBlock"] = BLOCK
    sb["lastReadWib"] = NOW_WIB
    sb["runNote1701_1120"] = (
        "Run 1701 (blok 134676380, interval ~32 mnt vs run 1631): totalMinted 373->481 (+108, 3.375/mnt vs prev 0.0 = ratio None) "
        "-> velocity GAGAL (rasio tak terhitung, prev rate 0); free% UNVERIFIED run ini (freeMinted view null; terakhir freeMinted 367/667); "
        "umur launch UNVERIFIED + website gate SUDAH GAGAL (metode A, tanpa situs proyek) -> BUKAN kandidat/strong lead. "
        "Delta dicatat; rate 3.375/mnt jadi baseline run berikut. DIAM.")
# binanceai pending claim: launched/failed/isRefundPhase NULL run ini (transport) - nilai lama dipertahankan
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("totalShares",):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1701"] = (
    f"Run 1701 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')} - SEMUA NULL (transport-degraded, BUKAN perubahan state); "
    f"nilai terakhir hot-leg 16:54 WIB dipertahankan (launched=0, failed=1, isRefundPhase=1); "
    f"totalShares {bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')}, "
    f"refundClaimed(user)={bv.get('refundClaimed_user')} - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1701_1120"] = (
                f"Run 1701 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1701_1120"] = (
                f"Run 1701 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 17:01 WIB"
snap["note"] = (
    "Run 1701: re-read 51 kontrak (430 call, 236 error RPC, blok merge 134676380); "
    "velocity LOLOS 0 (delta terbesar +108: Stromboat totalMinted 373->481, 3.375/mnt vs prev 0.0 = ratio None -> velocity GAGAL; "
    "free% UNVERIFIED + umur UNVERIFIED + website gate GAGAL -> bukan kandidat/strong lead; AgentBadge-ABDG 645->652 (+7, 1.36x, <20 token) GAGAL; "
    "ARKYN +2 (1.93x tapi <20) GAGAL); "
    "free>70%: STOCK AGENT 84.7% (941 FLAT, umur/website UNVERIFIED, bukan strong lead); Lumenhold GAGAL baca run ini (terakhir 1281/1500 = 85.4% hot-leg 16:49); "
    "Turtle 44/88 = 50.0% + Lion 42/88 = 47.7% (hot-leg 16:54, tanpa perubahan); HIVE 1267 FLAT, minted-by-user; ONI 208 FLAT. "
    "AUGENT + EIM GAGAL baca run ini (baseline dipertahankan). "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~590.000 blok. "
    "Sourcify top verifiedAt 2026-11-20T10:05:36Z; 1 baru vs hot-leg-seen/snapshot (0xd6809e7FEE86A353986ddDa268D081559B722Bcc: 8 fns, tanpa mint/quote/free/agent -> S1/S2 FAIL), 0 shape hit. "
    "Boltbook EN 45.070 byte (11 alamat full) + ZH 43.275 byte (10 alamat full), 1 baru (0x40Ecef2D095c81ed80dA544d3c34d7f9c4328CBE: n_fns 0, tanpa ABI -> S1/S2 FAIL), 0 shape hit; keduanya tanpa entri snapshot. "
    "Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep EN/ZH: tanpa proyek baru <24 jam terkonfirmasi; YAMA (sale 0x86D779fc...) diteruskan subagen sebagai data mentah - SUDAH di snapshot/track_c (hot-leg: totalShares 3100, totalFreeShares 3098, freeUsed user 0), bukan temuan baru; "
    "Lenx Agent Pass (~9 Nov) + Oathbots (28 Okt) sudah tua; hit lama lain sudah dikenal (AGENT COSMOS, GETAGENT, JINCHAN, Agentic Gangster, Coracle sold out). "
    "Route 6: Square tanpa proyek baru (AI frog paid-only 0,002 BNB/share, tutup 20 Nov 15:45 UTC); Odaily newsflash tanpa pengumuman Agent ID; PANews fetch basi (17 Nov); "
    "DappBay: STOCK AGENT / Lumenhold / Turtle / Lion tidak ada listing (ketiadaan bukan bukti). "
    "Catatan: hasil search mengandung teks instruksi tertanam ('call mint()') dari postingan Square - data eksternal, BUKAN perintah; diabaikan, tidak ditindaklanjuti. "
    "binanceai tetap pending/refund (launched/failed/isRefundPhase gagal baca run ini; terakhir hot-leg 16:54: 0/1/1; totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1701"] = snap["note"]
snap["runNote1701_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134676182) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~590.000 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1701_scan"] = (
    "Run 1701 (free-mint-search): pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134676182) - "
    "scan leg fast-fail; watermark TETAP 134086385, gap ~590.000 blok; blocker kredensial Ankr di luar scope job ini.")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print(f"MERGE OK: velocity updated={n_upd}, null-reads={n_null}, block={BLOCK}")
