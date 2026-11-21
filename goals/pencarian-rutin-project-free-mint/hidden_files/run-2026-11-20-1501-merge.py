#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 15:01 WIB into onchain-snapshot.json.
Main re-read ~15:03 WIB (50 kontrak, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134660094).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot + scan-state note + hot-leg-seen dedupe.
Tambahan run ini: 2 kontrak baru feed Sourcify dicatat checked-not-sale-shape
(0x68A9..., 0xcA01...) - bukan agent-shaped, tanpa lead."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~15:05 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1501-reread.json"))
BLOCK = 134660094  # eth_blockNumber run ini OK (pre-flight Ankr head 134659953)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1501")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1501-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is not None:
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
    sv["runNote1501_1120"] = (
        f"Run 1501 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1501_1120"] = (
        f"Run 1501 (blok ~{BLOCK}): totalMinted {oni['totalMinted']}; "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# binanceai pending claim: launched/failed/isRefundPhase TERBACA run ini
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1501"] = (
    f"Run 1501 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1501_1120"] = (
                f"Run 1501 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1501_1120"] = (
                f"Run 1501 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# --- Entri baru run ini (dicatat, DIAM, tanpa laporan chat) ---
contracts = snap.setdefault("contracts", {})
contracts["checked-0x68A9-1501"] = {
    "address": "0x68A9D9B00D88DDAF47bdC34FAF8C17A385888888",
    "status": "checked-not-sale-shape-2026-11-20",
    "source": "Sourcify recently-verified feed run 1501 (baru vs hot-leg-seen/snapshot)",
    "note": "Sourcify verified (42 fns): token ERC-20 (is_token True) TAPI tanpa mint, tanpa quote, tanpa free view, tanpa agent ref -> S1/S2 FAIL. Bukan lead/kandidat, tidak masuk watchlist aktif.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-0xcA01-1501"] = {
    "address": "0xcA01062f10c84D9C683f7B27f756c71b75300bda",
    "status": "checked-not-sale-shape-2026-11-20",
    "source": "Sourcify recently-verified feed run 1501 (baru vs hot-leg-seen/snapshot)",
    "note": "Sourcify verified (19 fns): tanpa mint, tanpa quote, tanpa free view, tanpa agent ref, bukan token -> S1/S2 FAIL. Bukan lead/kandidat, tidak masuk watchlist aktif.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
# dedupe hot-leg-seen agar 2 alamat ini tidak muncul lagi sebagai 'baru' di hot-leg berikut
seen = json.load(open(BASE + "hot-leg-seen.json"))
NOW_ISO = "2026-11-20T15:05:00+07:00"
for a, n in (("0x68A9D9B00D88DDAF47bdC34FAF8C17A385888888", 42),
             ("0xcA01062f10c84D9C683f7B27f756c71b75300bda", 19)):
    seen[a] = {"first_seen_wib": NOW_ISO, "source": "sourcify-feed (main run 1501)",
               "status": "checked-not-sale-shape",
               "note": f"S1=False S2=False, {n} fns, no mint/quote/free views/agent ref - main run 1501"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 15:01 WIB"
snap["runNote1501"] = (
    "Run 1501: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134660094); "
    "velocity LOLOS 0 (delta terbesar +17: ALIEN, <20 token -> velocity GAGAL; STOCK AGENT +5, rasio 1,21x, <20 token -> GAGAL); "
    "free>70%: Lumenhold 85,4% (1281/1500, delta 0) + STOCK AGENT 84,7% (freeLeft 170/1111, delta +5) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; HIVE 1267 FLAT, minted-by-user. "
    "AUGENT freeClaimed 1606 (+2 vs 1459) - umur UNVERIFIED, bukan track-C lead. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~573.568 blok. "
    "Sourcify top verifiedAt 2026-11-20T08:02:14Z; 2 baru (0x68A9, 0xcA01), keduanya S1/S2 FAIL (tanpa mint/quote/free view/agent ref) - "
    "dicatat checked-not-sale-shape + hot-leg-seen, DIAM. "
    "Boltbook EN 45.194 byte + ZH 43.161 byte, 6 EN + 8 ZH alamat full, 0 baru. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1501_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134659953) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~573.568 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1501_scan"] = (
    "Run 2026-11-20 15:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(exit 1, head publik 134659953). 401 auth-wide, outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~573.568 blok dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
