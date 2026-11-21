#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 20:31 WIB into onchain-snapshot.json.
Main re-read ~20:33-20:35 WIB (51 kontrak, blok 134704039).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama;
lastReadBlock/Wib hanya di-update bila new_supply terbaca (bukan None).
Temuan run ini: velocity LOLOS 1 (EIM totalMinted 913->1061, +148, 0.8222/mnt
vs prev 0.0323 = 25.46x) TAPI free% UNVERIFIED + umur UNVERIFIED + slot user
UNVERIFIED -> BUKAN kandidat/strong lead, DIAM; STOCK AGENT 944 (85.0%) +
Lumenhold 85.4% tetap bukan strong lead (umur/website/slot UNVERIFIED);
HIVE 1267 FLAT, balanceOf(user)=1, minted-by-user; binanceai launched=0,
failed=1, isRefundPhase=1 - tetap pending/refund; AONE freeMinted 10000
(sold out); bsccat freeMinted 574->583 (+9 token).
Sourcify 2 baru, 0 shape hit. Boltbook EN 45.118 byte (12 alamat) + ZH
43.006 byte (9 alamat), 0 baru. Bridge 0 baru (116/116 in snapshot,
7 same-owner-discarded). Pre-flight Ankr 401 (sejak 9 Nov) - scan leg
fast-fail, watermark TETAP 134086385. Track-C DROID/NIULAI/IMARS recheck
GAGAL transport (semua endpoint publik timeout/429) - nilai lama dipertahankan.
Sweep EN/ZH: tanpa proyek baru <24 jam terkonfirmasi (GETAGENT, AGENT COSMOS,
AGENTID, JINCHAN, Agentic Gangster, Odyssey, BNB ORBIT - semuanya lama/dikenal).
TIDAK ada lead/kandidat/eksekusi baru - DIAM.
CATATAN: Pocket Ai (ditambah snapshot run 1731) TIDAK masuk reread set run ini
karena view-list run ini disalin dari run-2026-11-20-1731-reread.json yang
dibangun sebelum Pocket Ai ditambahkan - run berikut WAJIB memasukkannya.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~20:41 WIB"
BLOCK = 134704039
reread = json.load(open(BASE + "run-2026-11-20-2031-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2031")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-2031-interim.json"))
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
        sv["runNote2031_1120"] = (
            f"Run 2031 (blok ~{BLOCK}): baca GAGAL (transport-degraded, nilai lama "
            f"({old_sup}) dipertahankan, velocity TIDAK dihitung; bukan kandidat/strong lead. DIAM.")
        n_null += 1
        continue
    sv["previousTotalSupply"] = old_sup
    if v["supply_view"] == "totalMinted":
        sv["totalMinted"] = new_sup
    else:
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
    sv["runNote2031_1120"] = (
        f"Run 2031 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"{v['supply_view']} {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# EIM: velocity LOLOS tapi bukan kandidat/strong lead - alasan eksplisit
eim = snap.get("contracts", {}).get("Everything Is Mine (EIM)", {})
if eim:
    eim["runNote2031_1120"] = (
        "Run 2031 (blok 134704039, interval 180 mnt vs run 1731): totalMinted 913->1061 (+148, 0.8222/mnt vs prev 0.0323 = 25.46x, >=20 token) "
        "-> velocity LOLOS, TAPI free% UNVERIFIED (semua free view revert; totalMinted 1061/8888 = 11,9% total supply BUKAN free%) + "
        "umur launch UNVERIFIED + slot user UNVERIFIED (harga/kuota user revert) + diskusi X UNVERIFIED -> BUKAN kandidat "
        "(butuh free% >=50% terverifikasi + umur <24 jam terverifikasi + diskusi X + website) dan BUKAN strong lead "
        "(free% >70% tak terverifikasi + umur tak terverifikasi + slot tak terverifikasi). Website terverifikasi "
        "(everythingisfine.website mencetak kontrak persis) tidak mengubah vonis. Tidak ada promosi, tidak ada preview/mint. DIAM.")
# binanceai pending claim
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares", "tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote2031"] = (
    f"Run 2031 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads (bsccat + AONE)
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote2031_1120"] = (
                f"Run 2031 (blok ~{BLOCK}): freeMinted {old_fm}->{fm}. DIAM.")
        else:
            tc[key]["runNote2031_1120"] = (
                f"Run 2031 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# track-C not-open recheck GAGAL transport run ini - nilai lama dipertahankan
for key in ("DROID", "NIULAI", "IMARS"):
    if key in tc:
        tc[key]["runNote2031_1120"] = (
            f"Run 2031 (blok ~{BLOCK}): recheck GAGAL transport (batch_race timeout + call_many HTTP 429/timeout di semua endpoint publik) - "
            f"launched/freeMinted/paused TIDAK terbaca ulang; nilai lama dipertahankan; status {tc[key].get('status')} tidak berubah. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 20:31 WIB"
snap["note"] = (
    "Run 2031: re-read 51 kontrak (blok 134704039, 57,6 dtk); "
    "velocity LOLOS 1 (EIM totalMinted 913->1061, +148, 25.46x) TAPI free%/umur/slot UNVERIFIED -> BUKAN kandidat/strong lead, DIAM; "
    "free>70%: STOCK AGENT 85.0% (944/1111, freeLeft 167) + Lumenhold 85.4% tetap bukan strong lead (umur/website/slot UNVERIFIED); "
    "HIVE 1267 FLAT, balanceOf(user)=1, minted-by-user; ONI/AONE: AONE freeMinted 10000 (sold out); bsccat freeMinted 583 (+9); "
    "binanceai: launched=0, failed=1, isRefundPhase=1, totalShares 3110 - tetap pending/refund. DIAM; "
    "Sourcify 2 baru (0x037c80b5, 0x92BAf58d), 0 shape hit; Boltbook EN 45.118 byte (12 alamat) + ZH 43.006 byte (9 alamat), 0 baru; "
    "Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded); "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385; "
    "Track-C DROID/NIULAI/IMARS recheck GAGAL transport (timeout/429 semua endpoint) - nilai lama dipertahankan; "
    "Sweep EN/ZH: tanpa proyek baru <24 jam terkonfirmasi (GETAGENT/AGENT COSMOS/AGENTID/JINCHAN/Agentic Gangster/Odyssey/BNB ORBIT - lama/dikenal). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM. "
    "CATATAN: Pocket Ai tidak masuk reread set run ini (view-list disalin dari 1731-reread sebelum Pocket Ai ditambah) - run berikut WAJIB memasukkannya.")
snap["runNote2031"] = snap["note"]
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print(f"MERGE OK: updated={n_upd} null={n_null} block={BLOCK}")
