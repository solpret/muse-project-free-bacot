#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 15:31 WIB into onchain-snapshot.json.
Main re-read ~15:33 WIB (50 kontrak, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134663982).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot + scan-state note + hot-leg-seen dedupe.
Tambahan run ini: 1 kontrak baru feed Sourcify dicatat checked-not-sale-shape
(0xE152...); AgentBadge-ABDG one-off re-read (totalMinted 629->633) + masuk
reread set run berikut."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~15:37 WIB"
BLOCK = 134663982  # eth_blockNumber run ini OK (pre-flight Ankr head 134663818)
reread = json.load(open(BASE + "run-2026-11-20-1531-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1531")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1531-interim.json"))
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
    sv["runNote1531_1120"] = (
        f"Run 1531 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
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
    oni["runNote1531_1120"] = (
        f"Run 1531 (blok ~{BLOCK}): totalMinted {oni['totalMinted']}; "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# AgentBadge-ABDG: one-off re-read run ini (bukan di reread set 1501)
ab = snap.get("contracts", {}).get("AgentBadge-ABDG", {})
if ab:
    ab["totalMinted"] = 633
    ab["freePctInference"] = round(100 * 633 / 3333, 1)
    ab["lastReadBlock"] = 134664062
    ab["lastReadWib"] = NOW_WIB
    ab["runNote1531_1120"] = (
        "Run 1531 (blok 134664062, one-off read, interval ~29 mnt vs run 1501): "
        "totalMinted 629->633 (+4, 0.138/mnt vs baseline Boltbook 0.173/mnt = 0.80x, <20 token) -> velocity GAGAL; "
        "free 633/3333 = 19.0% (<50% dan <70%); balanceOf(user)=0; umur launch tetap UNVERIFIED; "
        "status watchlist-only-age-unverified-2026-11-20. DIAM; masuk reread set run berikut.")
    # masukkan ke reread file agar run berikut membaca ulang
    err = {"error": "{'code': 3, 'message': 'execution reverted: 0x', 'data': '0x'}"}
    reread["reads"]["AgentBadge-ABDG"] = {
        "address": "0x126AF9585953004cbB9c5a0B37FC5616DD5F3B43",
        "views": {"totalMinted": 633, "totalSupply": err, "freeMinted": err,
                  "FREE_SUPPLY": err, "freeSupply": err, "freeLeft": err,
                  "mintOpen": err, "name": "AgentBadge", "symbol": "ABDG",
                  "balanceOf_user": 0, "contractURI": err, "owner": err}}
    json.dump(reread, open(BASE + "run-2026-11-20-1531-reread.json", "w"), indent=1)
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
pc["runNote1531"] = (
    f"Run 1531 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
            tc[key]["runNote1531_1120"] = (
                f"Run 1531 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1531_1120"] = (
                f"Run 1531 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# --- Entri baru run ini (dicatat, DIAM, tanpa laporan chat) ---
contracts = snap.setdefault("contracts", {})
contracts["checked-0xE152-1531"] = {
    "address": "0xE1527b6E5f622F5A3b87C7D02670406056c10823",
    "status": "checked-not-sale-shape-2026-11-20",
    "source": "Sourcify recently-verified feed run 1531 (baru vs hot-leg-seen/snapshot)",
    "note": "Sourcify verified (14 fns): token ERC-20 (is_token True) TAPI tanpa mint, tanpa quote, tanpa free view, tanpa agent ref -> S1/S2 FAIL. Bukan lead/kandidat, tidak masuk watchlist aktif.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
# dedupe hot-leg-seen agar alamat ini tidak muncul lagi sebagai 'baru' di hot-leg berikut
seen = json.load(open(BASE + "hot-leg-seen.json"))
NOW_ISO = "2026-11-20T15:37:00+07:00"
seen["0xE1527b6E5f622F5A3b87C7D02670406056c10823"] = {
    "first_seen_wib": NOW_ISO, "source": "sourcify-feed (main run 1531)",
    "status": "checked-not-sale-shape",
    "note": "S1=False S2=False, 14 fns, token, no mint/quote/free views/agent ref - main run 1531"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 15:31 WIB"
snap["note"] = (
    "Run 1531: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134663982); "
    "velocity LOLOS 0 (delta terbesar +2: First-Dollar Sparks, <20 token -> velocity GAGAL; STOCK AGENT FLAT 941); "
    "free>70%: Lumenhold 85,4% (1281/1500, delta 0) + STOCK AGENT 84,7% (freeLeft 170/1111, delta 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; HIVE 1267 FLAT, minted-by-user. "
    "AUGENT freeClaimed 1606->1607 (+1) - umur UNVERIFIED, bukan track-C lead. "
    "AgentBadge-ABDG one-off: totalMinted 629->633 (+4, 19,0%), velocity GAGAL, umur UNVERIFIED, watchlist-only. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~577.000 blok. "
    "Sourcify top verifiedAt 2026-11-20T08:33:02Z; 1 baru (0xE152), S1/S2 FAIL - dicatat checked-not-sale-shape + hot-leg-seen, DIAM. "
    "Boltbook EN 45.719 byte + ZH 43.777 byte, 10 EN + 8 ZH alamat full, 0 baru. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep EN/ZH + Odaily: tanpa proyek baru <24 jam (Oathbots 28 Okt, AGENT ID cards 25 Okt, AgentKoi 25 Okt, RIGBYPASS ~10 hari - semua age-excluded; "
    "GETAGENT/AGENT COSMOS/BNB ORBIT sudah di snapshot). Odaily hanya berita makro. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1531"] = snap["note"]
snap["runNote1531_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134663818) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~577.000 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1531_scan"] = (
    "Run 2026-11-20 15:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(exit 1, head publik 134663818). 401 auth-wide, outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~577.000 blok dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
