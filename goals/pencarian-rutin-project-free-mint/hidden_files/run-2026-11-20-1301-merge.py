#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 13:01 WIB into onchain-snapshot.json.
Main re-read ~13:03 WIB (50 kontrak incl. ONI, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134644071).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~13:05 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1301-reread.json"))
BLOCK = 134644071  # eth_blockNumber run ini OK (pre-flight Ankr head 134643943)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1301")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1301-interim.json"))
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
    sv["runNote1301_1120"] = (
        f"Run 1301 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted tetap 208 (tidak berubah vs 1231), balanceOf(user)=0.
oni = snap.get("contracts", {}).get("ONI", {})
if oni:
    oni["totalMinted"] = 208
    oni["freeMinted"] = 208
    oni["balanceOf_user"] = 0
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1301_1120"] = (
        f"Run 1301 (blok ~{BLOCK}): totalMinted 208 FLAT vs 1231 (208); free views revert "
        f"(FREE_SUPPLY/freeSupply/freeLeft/quote/freeMintedByWallet) - free% tetap inferensi 20,8%; "
        f"balanceOf(user)=0; slot user UNVERIFIED; website/X belum dicek. Bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# binanceai pending claim: launched/failed/isRefundPhase TERBACA run ini
# (launched=0, failed=1, isRefundPhase=1, totalShares 3110) - tanpa perubahan,
# tetap fase refund (sudah dilaporkan sekali 2026-11-02).
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1301"] = (
    f"Run 1301 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1301_1120"] = (
                f"Run 1301 (blok ~{BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
        else:
            tc[key]["runNote1301_1120"] = (
                f"Run 1301 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 13:01 WIB"
snap["runNote1301"] = (
    "Run 1301: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134644071); "
    "velocity LOLOS 0 (delta terbesar +4 Kageveil Genesis, <20 token); free>70%: Lumenhold 85,3% (1280/1500, quote 0, bal_user 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; STOCK AGENT 83,8% (freeLeft 180/1111, quote 0, bal_user 0) TERBACA run ini - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; S1-new-1F37Bd89 48,9% + S1-new-dddB9129 46,6% di bawah 50% track-A dan 70% strong-lead. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail. "
    "Sourcify 0 baru (top verified 2026-11-20T05:59:46Z), 0 shape hit. "
    "Boltbook EN 45.366 byte + ZH 43.576 byte, 1 baru 0xe13ad644 (Sourcify n_fns 0, S1/S2 false, bukan NFT), 0 shape hit. Bridge 0 baru. "
    "Sweep rute 3+6 (subagent): 0 temuan baru terverifikasi. Satu nama baru UNVERIFIED: Coracle Agents (coracle-agents.pages.dev, 10.000 pixel AI captains, "
    "2 pertama gratis/wallet) - situs TIDAK mencetak alamat kontrak, tanggal peluncuran TIDAK ditemukan, TIDAK ada bukti diskusi publik, mint kemungkinan BELUM DIBUKA "
    "('Mint ... Soon', counter '-'); watchlist-only unverified (tanpa alamat kontrak, tidak masuk snapshot kontrak), BUKAN lead/kandidat, DIAM. "
    "ONI totalMinted 208 FLAT, bal_user 0, free% tetap inferensi 20,8%. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1). bsccat freeMinted 565 (tidak berubah); AONE freeMinted 10000 (totalSupply gagal baca, nilai lama dipertahankan). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1301_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134643943) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~557.558 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
