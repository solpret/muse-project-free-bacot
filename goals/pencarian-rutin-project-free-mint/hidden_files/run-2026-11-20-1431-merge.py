#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 14:31 WIB into onchain-snapshot.json.
Main re-read ~14:33 WIB (50 kontrak, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134656065).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot + scan-state note. Tanpa perubahan status/lead baru.
Tambahan run ini: Boltbook 0x4b78Ed4d dicatat checked (bukan agent-shaped);
KITSUNE dicatat checked-age-excluded (launch ~15 Nov, totalMinted 350);
GETAGENT Sourcify tetap unverified -> watchlist-only."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~14:35 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1431-reread.json"))
BLOCK = 134656065  # eth_blockNumber run ini OK (pre-flight Ankr head 134655868)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1431")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1431-interim.json"))
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
    sv["runNote1431_1120"] = (
        f"Run 1431 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
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
    oni["runNote1431_1120"] = (
        f"Run 1431 (blok ~{BLOCK}): totalMinted {oni['totalMinted']}; "
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
pc["runNote1431"] = (
    f"Run 1431 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
            tc[key]["runNote1431_1120"] = (
                f"Run 1431 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1431_1120"] = (
                f"Run 1431 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# GETAGENT: Sourcify tetap unverified run ini
g = tc.get("GETAGENT", {})
if g:
    g["lastReadWib"] = NOW_WIB
    g["runNote1431_1120"] = (
        f"Run 1431 (blok ~{BLOCK}): Sourcify mint contract TETAP unverified (match None, 0 fns) -> "
        f"sale-shape S1/S2 tetap FAIL; situs getagent-bnb.web.app terbaca (kuota jendela ditampilkan, angka live tidak terekstrak). "
        f"Umur tetap UNVERIFIED. Tetap WATCHLIST-ONLY, bukan lead/kandidat, tidak di-preview/di-mint. DIAM.")
# --- Entri baru run ini (dicatat, DIAM, tanpa laporan chat) ---
contracts = snap.setdefault("contracts", {})
contracts["checked-0x4b78-1431"] = {
    "address": "0x4b78Ed4d04F58CdC1f6f3a02AE66Df64b449e9b9",
    "status": "checked-not-a-lead-2026-11-20",
    "source": "Boltbook EN+ZH front page run 1431 (baru vs seen/snapshot; juga baru di hot-leg 1424)",
    "note": "Sourcify unverified (n_fns 0); name()/symbol()/totalSupply()/totalMinted() SEMUA revert/kosong on-chain -> bukan agent-shaped, tanpa bukti registry/free-mint konkret. Bukan lead, tidak masuk watchlist aktif.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-KITSUNE-1431"] = {
    "address": "0xF09B7044FeEDc8154ccEBC1f12eB218fFB1508f9",
    "name": "KITSUNE", "symbol": "KITSUNE",
    "status": "checked-age-excluded-2026-11-20",
    "totalMinted": 350, "freeMinted": 350,
    "source": "Sweep rute 3/6 run 1431 (thecolony.ai, publikasi ~14 Nov; live numbers 15 Nov ~06:44 WIB)",
    "note": "Launch ~15 Nov 2026 (day-1 free drip 50 habis <1 jam; free pool 4000, drip 50/hari) -> umur ~5 hari > 24 jam = AGE-EXCLUDED. On-chain run ini: totalMinted 350, freeMinted 350; totalSupply()/FREE_SUPPLY() revert. Bukan lead/kandidat.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 14:31 WIB"
snap["runNote1431"] = (
    "Run 1431: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134656065); "
    "velocity LOLOS 0 (delta terbesar +4: STOCK AGENT); "
    "free>70%: Lumenhold 85,4% (1281/1500, delta 0) + STOCK AGENT 84,2% (freeLeft 175/1111, delta +4, rasio 4,0x tapi <20 token -> velocity GAGAL) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; HIVE 1267 FLAT, minted-by-user. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~569.483 blok. "
    "Sourcify 0 baru (20/20 sudah seen/snapshot), 0 shape hit. "
    "Boltbook EN 44.720 byte + ZH 43.044 byte, 9 alamat full, 1 baru 0x4b78Ed4d (Sourcify unverified, semua view revert) - "
    "dicatat checked-not-a-lead, DIAM. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep rute 3 EN/ZH + Square + Odaily/PANews: tanpa proyek baru - semua hit sudah di snapshot "
    "(GETAGENT watchlist-only, YAMA age-excluded, Agentic Gangster free sold out, First-Dollar Grove age-excluded, "
    "Oathbots age-excluded, AGENT COSMOS age-excluded, JINCHAN sold out/tutup 10 Nov, Mintu Bots paid-only, "
    "Protocol 42 bukan free mint). KITSUNE baru dari sweep -> dicatat checked-age-excluded (launch ~15 Nov, totalMinted 350). "
    "GETAGENT re-cek: Sourcify tetap unverified (match None, 0 fns) -> shape tetap FAIL, umur tetap UNVERIFIED, watchlist-only. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1431_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134655868) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~569.483 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1431_scan"] = (
    "Run 2026-11-20 14:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(exit 1, head publik 134655868). 401 auth-wide, outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~569.483 blok dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
