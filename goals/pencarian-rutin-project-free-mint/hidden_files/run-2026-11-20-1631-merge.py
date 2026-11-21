#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 16:31 WIB into onchain-snapshot.json.
Main re-read ~16:33 WIB (51 kontrak, 390 eth_call, 233 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134672236).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot + scan-state note.
Tambahan run ini: AgentBadge-ABDG totalMinted 640->645 (+5, melambat 0.69x);
Sourcify 2 baru (0x94be40, 0x1dAC85) + Boltbook 0x42C7E321 - ketiganya S1/S2 FAIL,
tanpa entri snapshot (hot-leg-seen milik hot leg, tidak di-update dari sini);
AUGENT freeClaimed 1608->1609 (+1)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~16:36 WIB"
BLOCK = 134672236  # eth_blockNumber run ini OK (pre-flight Ankr head 134671998)
reread = json.load(open(BASE + "run-2026-11-20-1631-reread.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1631")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1631-interim.json"))
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
    sv["runNote1631_1120"] = (
        f"Run 1631 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted dari reread run ini (208 FLAT vs 1601; CATATAN: old_supply di
# interim null karena skrip 1631 sempat menimpa baseline ONI dgn views None -
# sudah diperbaiki di skrip (conditional add), delta benar = 0 FLAT)
oni = snap.get("contracts", {}).get("ONI", {})
oni_v = reread["reads"].get("ONI", {}).get("views", {})
if oni and num(oni_v, "totalMinted") is not None:
    oni["totalMinted"] = num(oni_v, "totalMinted")
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1631_1120"] = (
        f"Run 1631 (blok ~{BLOCK}): totalMinted {oni['totalMinted']} (FLAT vs 1601); "
        f"balanceOf(user)={num(oni_v, 'balanceOf_user')}; free views revert - free% tetap inferensi; "
        f"bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# AgentBadge-ABDG: totalMinted 640->645 (+5) run ini
ab = snap.get("contracts", {}).get("AgentBadge-ABDG", {})
if ab:
    ab["totalMinted"] = 645
    ab["freePctInference"] = round(100 * 645 / 3333, 1)
    ab["lastReadBlock"] = BLOCK
    ab["lastReadWib"] = NOW_WIB
    ab["runNote1631_1120"] = (
        "Run 1631 (blok 134672236, interval ~31 mnt vs run 1601): "
        "totalMinted 640->645 (+5, 0.161/mnt vs baseline 0.233/mnt = 0.69x, MELAMBAT, <20 token) -> velocity GAGAL; "
        "free 645/3333 = 19.4% (<50% dan <70%); balanceOf(user)=0; umur launch tetap UNVERIFIED; "
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
pc["runNote1631"] = (
    f"Run 1631 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
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
            tc[key]["runNote1631_1120"] = (
                f"Run 1631 (blok ~{BLOCK}): freeMinted {old_fm}->{fm} (FLAT). DIAM.")
        else:
            tc[key]["runNote1631_1120"] = (
                f"Run 1631 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 16:31 WIB"
snap["note"] = (
    "Run 1631: re-read 51 kontrak (390 call, 233 error RPC, blok merge 134672236); "
    "velocity LOLOS 0 (delta terbesar +5: AgentBadge-ABDG 640->645, 0.69x MELAMBAT, <20 token -> velocity GAGAL; "
    "EIM +1, DGF-CARD +1, ARKYN +1, ALIEN +1, AGATE-Pass +1); "
    "free>70%: Lumenhold 85,4% (1281/1500, delta 0) + STOCK AGENT 84,7% (freeLeft 170/1111, delta 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; HIVE 1267 FLAT, minted-by-user; ONI 208 FLAT. "
    "AUGENT freeClaimed 1608->1609 (+1) - umur UNVERIFIED, bukan track-C lead. "
    "AgentBadge-ABDG: totalMinted 640->645 (+5, 19,4%), velocity GAGAL (melambat), umur UNVERIFIED, watchlist-only. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail, watermark TETAP 134086385, gap ~585.600 blok. "
    "Sourcify top verifiedAt 2026-11-20T09:34:33Z; 2 baru vs hot-leg-seen/snapshot (0x94be40abc897C83b0545beB343eaAfdAAc375d00: token 128 fns, mint+freeMinted, TANPA agent_ref/quote -> S1/S2 FAIL; "
    "0x1dAC85D4a3cAeAbB21d7628A1389Ae59f96228F4: 24 fns, tanpa mint/quote/free/agent -> FAIL), 0 shape hit. "
    "Boltbook EN 44.807 byte (8 alamat full) + ZH 43.075 byte (6 alamat full), 1 baru EN: 0x42C7E3214a0F1024Fc477257282cE3734a707DC9 (n_fns 0, tanpa ABI -> S1/S2 FAIL, sudah muncul di hot-leg 1624, tidak dicatat di hot-leg-seen). "
    "Bridge 0 baru (116/116 in snapshot, 7 same-owner-discarded). "
    "Sweep EN/ZH: tanpa proyek baru <24 jam. Hit yang sudah dikenal: Agentic Gangster + AGENT COSMOS + GETAGENT sudah di snapshot; "
    "JINCHAN (buka 8 Nov, tutup 10 Nov) sudah di snapshot + age-excluded; QAGENT/PIPO (2 Nov) + BNBPIG (1 Nov) age-excluded; BYTE (7 Nov, 3.385 free tersisa saat itu) age-excluded. "
    "AgentQuest (baru di sweep, badge soulbound ERC-5192, situs zainumq.github.io/agentquest): BUKAN lead/kandidat - soulbound tanpa harga/pasar (dinyatakan situs), tanpa cap kuota gratis (free% UNVERIFIABLE), "
    "kontrak badge dinyatakan 'not deployed yet' di situs, benefit KONG dari sale terpisah buka 1 Des 2026 - dicatat di run log saja, tanpa entri snapshot (preseden sweep-hit 1531/1601). "
    "AI frog tetap paid-only 0,002 BNB/share, tutup 20 Nov 15:45 UTC - bukan track-C lead (sudah dinilai 1601). "
    "Odaily newsflash hanya berita makro/saham teknologi. DappBay: tidak ada proyek yang butuh gate-check run ini. "
    "Catatan: hasil search mengandung teks instruksi 'call mint()' dari postingan Square - data eksternal, BUKAN perintah; tidak ditindaklanjuti. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 574 FLAT; AONE freeMinted 10000 FLAT (sold out). "
    "BUG SKRIP: blok ONI-add di run-1631.py sempat menimpa baseline ONI dgn None (old_supply null di interim) - sudah diperbaiki jadi conditional add; re-read + merge ONI tetap benar (208 FLAT). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1631"] = snap["note"]
snap["runNote1631_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134671998) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~585.600 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
# scan-state note (watermark tidak berubah)
st = json.load(open(BASE + "onchain-scan-state.json"))
st["note_1631_scan"] = (
    "Run 2026-11-20 16:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(exit 1, head publik 134671998). 401 auth-wide, outage Ankr sejak 2026-11-09 berlanjut. "
    "Watermark TETAP 134086385; gap ~585.600 blok dan terus membesar (~8.000 blok/jam). "
    "Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
