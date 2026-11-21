#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 21:01 WIB into onchain-snapshot.json.
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
NOW_WIB = "2026-11-20 ~21:11 WIB"
BLOCK = 134708292
reread = json.load(open(BASE + "run-2026-11-20-2101-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2101")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-2101-interim.json"))
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
        sv["runNote2101_1120"] = (
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
    sv["runNote2101_1120"] = (
        f"Run 2031 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"{v['supply_view']} {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# EIM: velocity GAGAL run ini (bukan kandidat/strong lead) - alasan eksplisit
eim = snap.get("contracts", {}).get("Everything Is Mine (EIM)", {})
if eim:
    eim["runNote2101_1120"] = (
        "Run 2101 (blok 134708292, interval ~30 mnt vs run 2031): totalMinted 1061->1069 (+8, 0.2667/mnt vs prev 0.8222 = 0.32x, <20 token) "
        "-> velocity GAGAL; free% UNVERIFIED (semua free view revert; totalMinted 1069/8888 = 12,0% total supply BUKAN free%) + "
        "umur launch UNVERIFIED + slot user UNVERIFIED + diskusi X UNVERIFIED -> BUKAN kandidat "
        "dan BUKAN strong lead. Website terverifikasi (everythingisfine.website) tidak mengubah vonis. "
        "Tidak ada promosi, tidak ada preview/mint. DIAM.")
# binanceai pending claim
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares", "tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote2101"] = (
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
            tc[key]["runNote2101_1120"] = (
                f"Run 2031 (blok ~{BLOCK}): freeMinted {old_fm}->{fm}. DIAM.")
        else:
            tc[key]["runNote2101_1120"] = (
                f"Run 2031 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# track-C recheck run ini: DROID/NIULAI/IMARS dibaca ulang via curl batch bsc-dataseed (BERHASIL)
tc = snap.get("track_c", {})
if "DROID" in tc:
    old_fm = tc["DROID"].get("freeMinted")
    tc["DROID"]["freeMinted"] = 760
    tc["DROID"]["runNote2101_1120"] = (
        f"Run 2101 (blok ~{BLOCK}): recheck BERHASIL - freeMinted {old_fm}->760 (+12), paused 0, launched() revert (view tidak ada); "
        f"status {tc['DROID'].get('status')} tidak berubah (umur/slot UNVERIFIED, bukan lead). DIAM.")
if "NIULAI" in tc:
    tc["NIULAI"]["launched"] = 0
    tc["NIULAI"]["runNote2101_1120"] = (
        f"Run 2101 (blok ~{BLOCK}): recheck BERHASIL - launched 0 (masih belum buka), freeMinted/paused revert; "
        f"status {tc['NIULAI'].get('status')} tidak berubah. DIAM.")
if "IMARS" in tc:
    tc["IMARS"]["runNote2101_1120"] = (
        f"Run 2101 (blok ~{BLOCK}): recheck BERHASIL - freeMinted 300 FLAT, launched()/paused() revert; "
        f"status {tc['IMARS'].get('status')} tidak berubah (excluded, pool habis). DIAM.")
# Coracle Agents: BARU dari sweep, sudah SOLD OUT on-chain -> excluded, tidak dilaporkan sebagai lead
snap.setdefault("contracts", {})["Coracle Agents"] = {
    "address": "0x2FCefA216dA37751E102399aCbe1dCC86Dc96eCf",
    "name": "Coracle Agents",
    "symbol": "CORA",
    "kind": "ERC721",
    "status": "excluded-sold-out-2026-11-20",
    "source": "sweep rute-3/5b run 2101 (subagen) + deep-dive parent: site + raw HTML + on-chain 2 endpoint",
    "website": "https://coracle-agents.pages.dev/",
    "totalSupply": 10000,
    "MAX_SUPPLY": 10000,
    "mintOpen": 1,
    "mintPrice": 500000000000000,
    "balanceOf_user": 0,
    "owner": "0x94CE8e0a835CCF85243BE3ae2B30ffd621Bd1901",
    "market": "0x598f5AF7Ccb5520F51848C7189402C25Ee2222b7",
    "voyage": "0x7F61f339C55Ae987888f936DB812B64b3D28e26c",
    "firstSeenWib": "2026-11-20 ~21:04 WIB",
    "lastReadBlock": BLOCK,
    "lastReadWib": "2026-11-20 ~21:11 WIB",
    "launchNote": "SOLD OUT terverifikasi on-chain (blok 134708292, dua endpoint independen bsc-dataseed + bsc-dataseed1): totalSupply 10000/10000 MAX_SUPPLY, ownerOf(1)=owner, ownerOf(5000) + ownerOf(10000) ada (holder berbeda). Site mencetak kontrak persis (NFT + Market di Transparency; registry 0x60B9...022F) = website evidence ADA, tapi koleksi sudah habis -> excluded-sold-out, BUKAN kandidat/lead. Roadmap situs masih menulis fase Mint 'Soon' dan counter '-' (tidak termuat) = stale, bukan bukti belum launch. Bentuk: 10.000 pixel captains, gate Agent ID, 2 pertama gratis/wallet lalu 0,0005 BNB, maks 10/wallet. Tidak pernah dilaporkan sebagai early lead (ditemukan saat sudah sold out).",
}
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 21:01 WIB"
snap["note"] = (
    "Run 2101: re-read 52 kontrak (blok 134708292, 132,1 dtk; Pocket Ai masuk reread set, totalMinted 2950->2955); "
    "velocity LOLOS 0 (EIM +8, ratio 0.32, GAGAL); "
    "free>70%: STOCK AGENT 85.0% FLAT + Lumenhold 85.4% FLAT tetap bukan strong lead (umur/website/slot UNVERIFIED); "
    "HIVE 1267 FLAT, balanceOf(user)=1, minted-by-user; ARKT-claim-62a7/AgentMintPass/AGATE-Pass baca GAGAL transport (chunk null), nilai lama dipertahankan; "
    "binanceai: launched=0, failed=1, isRefundPhase=1, totalShares 3110 - tetap pending/refund. DIAM; "
    "AONE freeMinted 10000 (sold out); bsccat freeMinted 583 FLAT; "
    "Coracle Agents BARU dari sweep -> SOLD OUT on-chain (10000/10000, 2 endpoint), dicatat excluded-sold-out, tidak dilaporkan; "
    "Sourcify 2 baru (0x006Bb55b, 0x9Aacde2a), 0 shape hit; Boltbook EN 45.328 byte (17 alamat) + ZH 43.578 byte (14 alamat), 2 baru (0x8ce906fc unverified; 0xf3556fa0 unverified tanpa shape), 0 shape hit; "
    "Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded); "
    "Pre-flight Ankr GAGAL HTTP 404 (sebelumnya 401 sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385; "
    "Track-C DROID freeMinted 748->760 (+12), NIULAI launched 0, IMARS freeMinted 300 FLAT; "
    "Sweep EN/ZH: tanpa proyek baru <24 jam terkonfirmasi (nama mentah DRIFTWIRE/Agent Island/BAHUANG3/BITCAT/JINMA tanpa bukti; YAMA sudah terlacak). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote2101"] = snap["note"]
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print(f"MERGE OK: updated={n_upd} null={n_null} block={BLOCK}")
