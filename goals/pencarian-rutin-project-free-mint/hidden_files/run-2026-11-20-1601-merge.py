#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 16:01 WIB into onchain-snapshot.json.
Main re-read ~16:03 WIB (51 kontrak, 430 eth_call, 256 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134668051).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot + scan-state note.
Tambahan run ini: AgentBadge-ABDG totalMinted 633->640 (+7); tidak ada kontrak
baru feed Sourcify (0 baru vs hot-leg-seen/snapshot) -> tidak ada entri checked baru,
tidak ada update hot-leg-seen."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~16:05 WIB"
BLOCK = 134668051  # eth_blockNumber run ini OK (pre-flight Ankr head 134667870)
reread = json.load(open(BASE + "run-2026-11-20-1601-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1601")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1601-interim.json"))
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
    sv["runNote1601_1120"] = (
        f"Run 1601 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini (208 FLAT vs 1531)
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1601_1120"] = (
        f"Run 1601 (blok ~{BLOCK}): totalMinted {oni['totalMinted']} (FLAT vs 1531); "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# AgentBadge-ABDG: totalMinted 633->640 (+7) run ini
ab = snap.get("contracts", {}).get("AgentBadge-ABDG", {})
if ab:
    ab["totalMinted"] = 640
    ab["freePctInference"] = round(100 * 640 / 3333, 1)
    ab["lastReadBlock"] = BLOCK
    ab["lastReadWib"] = NOW_WIB
    ab["runNote1601_1120"] = (
        "Run 1601 (blok 134668051, interval ~30 mnt vs run 1531): "
        "totalMinted 633->640 (+7, 0.233/mnt vs baseline 0.173/mnt = 1.35x, <20 token) -> velocity GAGAL; "
        "free 640/3333 = 19.2% (<50% dan <70%); balanceOf(user)=0; umur launch tetap UNVERIFIED; "
        "status watchlist-only-age-unverified-2026-11-20. DIAM; tetap di reread set run berikut.")
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
pc["runNote1601"] = (
    f"Run 1601 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
            tc[key]["runNote1601_1120"] = (
                f"Run 1601 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1601_1120"] = (
                f"Run 1601 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 16:01 WIB"
snap["note"] = (
    "Run 1601: re-read 51 kontrak (430 call, 256 error RPC, blok merge 134668051); "
    "velocity LOLOS 0 (delta terbesar +7: AgentBadge-ABDG 633->640, 1.35x tapi <20 token -> velocity GAGAL; "
    "AgentEcho +3 (2.9x, <20), First-Dollar Sparks +3 (1.45x, <20)); "
    "free>70%: Lumenhold 85,4% (1281/1500, delta 0) + STOCK AGENT 84,7% (freeLeft 170/1111, delta 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; HIVE 1267 FLAT, minted-by-user; ONI 208 FLAT. "
    "AUGENT freeClaimed 1607->1608 (+1) - umur UNVERIFIED, bukan track-C lead. "
    "AgentBadge-ABDG: totalMinted 633->640 (+7, 19,2%), velocity GAGAL, umur UNVERIFIED, watchlist-only. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~578.000 blok. "
    "Sourcify top verifiedAt 2026-11-20T08:52:49Z; 0 baru vs hot-leg-seen/snapshot, 0 shape-check. "
    "Boltbook EN 45.391 byte + ZH 43.612 byte, 12 EN + 12 ZH alamat full, 0 baru. Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep EN/ZH: tanpa proyek baru <24 jam (Oathbots 28 Okt, AGENT ID cards 25 Okt, AGENT COSMOS + GETAGENT + SNAKE + Agentic Gangster sudah di snapshot; "
    "AI frog launchpad 0xc1db6Be921e351615CC20FDE2dfe64ac6C4c6AF4 Sourcify exact_match, 41 fns, mint+costOf+AGENT_REGISTRY TAPI 0 free view -> S1/S2 FAIL, "
    "paid-only 0.002 BNB/share, tutup 20 Nov 15:45 UTC - bukan track-C lead, dicatat di run log saja; Coracle Agents belum deploy - upcoming saja; "
    "UFO/NEBULA 10 Nov - age-excluded). Odaily newsflash hanya berita makro/saham teknologi. DappBay: tidak ada proyek yang butuh gate-check run ini. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1601"] = snap["note"]
snap["runNote1601_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134667870) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~578.000 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1601_scan"] = (
    "Run 2026-11-20 16:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(exit 1, head publik 134667870). 401 auth-wide, outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~578.000 blok dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
