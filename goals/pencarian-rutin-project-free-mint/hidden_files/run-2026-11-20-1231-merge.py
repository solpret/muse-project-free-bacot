#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 12:31 WIB into onchain-snapshot.json.
Main re-read ~12:33 WIB (49 kontrak, 380 eth_call, 252 errors - degradasi RPC
bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134639984).
ONI ditambahkan ke snapshot watchlist (early lead sudah dilaporkan sekali oleh
triase backfill ~12:26; run ini verifikasi independen).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru selain ONI."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~12:35 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1231-reread.json"))
BLOCK = 134639984  # eth_blockNumber run ini OK (pre-flight Ankr head 134639852)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1231")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1231-interim.json"))
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
    sv["runNote1231_1120"] = (
        f"Run 1231 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
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
pc["runNote1231"] = (
    f"Run 1231 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
            tc[key]["runNote1231_1120"] = (
                f"Run 1231 (blok ~{BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
        else:
            tc[key]["runNote1231_1120"] = (
                f"Run 1231 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 12:31 WIB"
# ONI: early lead temuan backfill, sudah dilaporkan sekali oleh triase ~12:26 WIB -
# run ini verifikasi independen (registry exact, freeMinted 208, MAX_SUPPLY 4444,
# first mint 12:01:21 WIB blok 132141081) dan menambahkannya ke watchlist snapshot
# karena triase tidak menulisnya ke snapshot (pencarian string: tidak ada di file).
# Bukan laporan baru: status early-lead-reported; baseline untuk tracking velocity/free%.
oni_verify = json.load(open(BASE + "run-2026-11-20-1231-oni-verify.json"))
snap.setdefault("contracts", {})["ONI"] = {
    "address": "0x74BDA11E34EB02121104Ff38471D91Fe1C37F81A",
    "name": "ONI", "symbol": "ONI", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-20",
    "source": "backfill-triage-2026-11-20-1226",
    "firstMintWib": "2026-11-20 12:01:21 WIB", "firstMintBlock": 132141081,
    "totalSupply": oni_verify.get("totalMinted"), "totalMinted": oni_verify.get("totalMinted"),
    "freeMinted": oni_verify.get("freeMinted"), "MAX_SUPPLY": oni_verify.get("MAX_SUPPLY"),
    "freePctInference": 20.8,
    "freePctNote": "208/1000 bila cap free 1000 per triase backfill (FREE_SLOTS/freeSupply revert saat baca run ini) - inferensi, bukan counter free terverifikasi",
    "registry": oni_verify.get("registry"),
    "owner": oni_verify.get("owner"),
    "balanceOf_user": oni_verify.get("balanceOf_user"),
    "userSlot": "UNVERIFIED: freeMintedByWallet/mintedBy/quote revert saat baca run ini",
    "website": None, "gate": "not-checked-yet",
    "currentRatePerMin": 5.9,
    "rateNote": "freeMinted 19 (12:01) -> 208 (12:33) = +189/~32 mnt, ~5,9/mnt - laju awal saja, belum ada baseline snapshot untuk velocity leg",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
    "runNote1231_1120": (
        f"Run 1231 (blok ~{BLOCK}): ditambahkan ke snapshot watchlist (triase backfill melaporkannya sekali ~12:26 "
        f"tanpa menulis snapshot). Verifikasi independen run ini: registry() exact 0x60B9..., freeMinted 208, "
        f"MAX_SUPPLY 4444, first mint 12:01:21 WIB (umur ~32 mnt, <24 jam), free% ~20,8% (inferensi cap 1000), "
        f"slot user UNVERIFIED, website/X belum dicek. Bukan strong lead/kandidat - baseline tracking saja. DIAM."),
}
snap["runNote1231"] = (
    "Run 1231: re-read 49 kontrak (380 call, 252 error RPC, blok merge 134639984); "
    "velocity LOLOS 0 (delta terbesar +3 ARKYN, <20 token); free>70%: Lumenhold 85,3% (1280/1500, quote 0, bal_user 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; STOCK AGENT GAGAL baca run ini (semua view transport error, nilai lama 83,8% dipertahankan). "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail. "
    "Sourcify 0 baru (top verified 2026-11-20T05:28:48Z), 0 shape hit. "
    "Boltbook EN 44.720 byte + ZH 42.775 byte, 1 baru 0x1D0e2289 (Sourcify n_fns 0, S1/S2 false, bukan NFT), 0 shape hit. Bridge 0 baru. "
    "Route-3 sweep: hasil search tidak lolos safety check - tidak ada verifikasi/tindakan dari hasil itu; item yang tampak semuanya sudah dikenal/dicatat sebelumnya "
    "(Mintu Bots berbayar-excluded; AGENT ID cards 26 hari; AGENT COSMOS 15 hari; JINCHAN sold-out-free 2026-11-08; GETAGENT sudah di track_c watchlist-only age-unverified) - 0 kandidat baru. "
    "ONI ditambahkan ke snapshot watchlist (early lead, sudah dilaporkan sekali triase backfill; verifikasi independen run ini, baseline tracking). "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1). bsccat freeMinted 565 (tidak berubah); AONE gagal baca (nilai lama dipertahankan). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1231_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134639852) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~553.467 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Catatan: onchain-scan-seen.json tidak ditemukan di hidden_files (dedupe skrip run memakai hot-leg-seen.json). "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
