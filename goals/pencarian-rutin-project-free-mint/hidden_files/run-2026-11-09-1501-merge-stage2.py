#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1501 WIB — incorporate Subagent A discovery
(run-2026-11-09-1501-discovery.json/.md) into the snapshot (already stage-1
merged) and finalize run notes. Discovery found 3 NEW contracts; all triaged
on-chain by parent in run-2026-11-09-1501-triage.py: BMT Agents free pool
exhausted (excluded), NIBULL sale NOT YET OPEN (track_c upcoming),
Burn Agent free pool exhausted + age >48h (excluded). No scan output
(pre-flight 401 fast-fail). Read-only w.r.t. chain; never mints/previews.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1501-merge.json,
run-2026-11-09-1501-runlog.md.
"""
import json, os, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
stage1 = json.load(open(f"{HF}/run-2026-11-09-1501-merge-stage1.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1501-discovery.json"))

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1501-stage2")
contracts = snap.get("contracts", {})

report = dict(stage1)
report["stage"] = 2
report["discovery"] = {
    "verdict": disc.get("verdict"),
    "new_watchlist_only": ["NIBULL (track_c upcoming, sale buka 2026-11-09 16:00 WIB)"],
    "new_excluded": ["BMT Agents (free pool habis 1000/1000)", "Burn Agent (free pool habis 300/300 + umur >48 jam)"],
    "sourcify_non_agent": disc.get("sourcify", {}).get("checked_not_agent_shaped", []),
    "sourcify_agent_gated_no_free_view": disc.get("sourcify", {}).get("agent_gated_but_no_free_view_not_leads", []),
    "bridge_new": [],
    "bridge_not_in_snapshot": ["BNB Bull Pass 0x64295d2dea0acb8d0ed0d00c009c7d25eb3a0446 (run-1 finding, 1 entity, bukan lead)"],
    "boltbook_not_contracts": ["OTV (alamat terpotong di excerpt Boltbook; berbayar 0,0012 BNB per catatan run 0431, bukan lead gratis baru)"],
}

# ---- incorporate discovery triage (parent on-chain verification, blok 132552663) ----
# BMT Agents: agent-shaped (agentId()=registry 0x60B9...), TAPI free pool HABIS
# (freeMinted 1000/1000, FREE_SUPPLY 1000; totalSupply 1000, MAX 2000, PRICE 0,005 BNB
# paid path). Slot user terbuka (freeClaimed(user)=0) tapi pool 0 -> tidak bisa mint.
# Dicatat excluded, TIDAK dilaporkan sebagai lead (tidak ada free mint tersisa).
if "BMT Agents" not in contracts:
    contracts["BMT Agents"] = {
        "address": "0x7d6e8528cc918afbd0ba5b0998c8a57860d2ded6",
        "status": "excluded-free-sold-out-2026-11-09",
        "name": "BMT Agents", "symbol": "BMTA", "kind": "ERC721",
        "totalSupply": 1000, "totalMinted": 1000, "freeMinted": 1000,
        "FREE_SUPPLY": 1000, "MAX_SUPPLY": 2000, "PRICE": 5000000000000000,
        "freePctVerified": 100.0, "agentId": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
        "freeClaimed_user": 0, "publicMintedBy_user": 0, "balanceOf_user": 0,
        "PUBLIC_PER_WALLET": 3,
        "firstSeenNote": "Boltbook front page ZH ~22:0x WIB 2026-11-08 (blok 132412576-132413181): totalSupply 920/2000, freeClaimed 920; waktu postingan = first-seen, BUKAN waktu peluncuran (umur peluncuran unverified, moot karena free pool habis).",
        "baselineNote": "Discovery run 1501 (Boltbook ZH) + triase on-chain parent blok 132552663: agent-shaped terverifikasi (agentId()=registry), free pool HABIS 1000/1000 -> excluded-free-sold-out, TIDAK dilaporkan sebagai lead.",
        "lastReadBlock": 132552663, "lastReadWib": "2026-11-09 ~15:5x WIB",
    }
# Burn Agent: FREE_SHARES 300, freeMinted 300 -> free pool HABIS; umur >48 jam
# (Quantum Audit 3 Nov: token 13 jam saat audit -> peluncuran ~2-3 Nov). Excluded.
if "Burn Agent" not in contracts:
    contracts["Burn Agent"] = {
        "address": "0x7de1606230aa70802caecf1a3e90039a6265b1c4",
        "status": "excluded-free-sold-out-2026-11-09",
        "name": "Burn Agent", "symbol": "BURN", "kind": "ERC20",
        "totalSupply": 869035699789294475375657269024, "totalMinted": 10339,
        "FREE_SHARES": 300, "freeMinted": 300, "freePctVerified": 100.0,
        "BASE_QUOTA": 10, "MAX_SHARES": 4440000, "OPEN_AT": 10000, "opened": 1,
        "pair": "0x53895464c524c6fdd82ad5189bf92d9b798c6a51", "balanceOf_user": 0,
        "launchNote": "Quantum Audit 3 Nov 2026: token berumur 13 jam saat audit -> peluncuran ~2-3 Nov 2026 -> ~6 hari pada 9 Nov (>48 jam, age-excluded). BUKAN koin 'Burn' scalp user.",
        "baselineNote": "Discovery run 1501 (sweep Blockspot/Quantum Audit) + triase on-chain parent blok 132552663: free pool HABIS 300/300 + umur >48 jam -> excluded, TIDAK dilaporkan sebagai lead.",
        "lastReadBlock": 132552663, "lastReadWib": "2026-11-09 ~15:5x WIB",
    }
# NIBULL: single-contract token+sale (S1 shape di level ABI), BELUM BUKA
# (startTime 1794214800 = 2026-11-09 16:00 WIB, opened=0, pair 0x0, soldShares 0).
# FREE_SHARES 500, TOTAL 10000, TOKENS_PER_SHARE 60.000.000, pricePerShare 0,002 BNB.
# registry() = 0xc44f... (BUKAN registry kanonik 0x60B9...) -> kaki registry AMBIGU;
# gate-function (walletAgent/hasBought/agentShares/claimed) ada. walletAgent(user)=0.
# Upcoming watchlist di track_c; run berikut (pasca-16:00 WIB) evaluasi ulang sebagai
# lead bila buka + pool/slot/registry terverifikasi. TIDAK dilaporkan sebagai lead kini.
tc = snap.get("track_c", {})
if "NIBULL" not in tc:
    tc["NIBULL"] = {
        "sale": "0x29666Bc0004824dc2B282c82aAC206b8b1711839",
        "token": "0x29666Bc0004824dc2B282c82aAC206b8b1711839",
        "status": "watchlist-only-upcoming-2026-11-09",
        "name": "NIBULL", "symbol": "NIBULL",
        "saleShape": "S1 (ABI): buy(shares,referrer) + quoteCost + FREE_SHARES + registry() + TOKENS_PER_SHARE + TOTAL_SHARES + soldShares + startTime/saleEnd + claim + claimRefund; Sourcify exact_match verifiedAt 2026-11-09T07:05:58Z",
        "FREE_SHARES": 500, "soldShares": 0, "TOTAL_SHARES": 10000,
        "TOKENS_PER_SHARE": 60000000000000000000000000,
        "pricePerShare": 2000000000000000,
        "startTime": 1794214800, "startTimeWib": "2026-11-09 16:00:00 WIB",
        "saleEnd": 1794474000, "saleEndWib": "2026-11-12 16:00:00 WIB",
        "opened": 0, "openedAt": 0, "isSaleEnded": 0, "pair": "0x0000000000000000000000000000000000000000",
        "registry": "0xc44f83991f945945917169028f9f1b3d3de0a4a2",
        "registryNote": "registry() BUKAN registry kanonik 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (0xc44f... = helper lookup agentIdOf per discovery); gate-function walletAgent/hasBought/agentShares/claimed ADA. Kaki registry AMBIGU - verifikasi ulang saat sale buka.",
        "walletAgent_user": 0, "hasBought_user": 0, "balanceOf_user": 0, "baseQuota": 10,
        "firstSeenNote": "Sourcify feed run 1501 (verifiedAt 2026-11-09T07:05:58Z = 14:05:58 WIB); verifiedAt BUKAN waktu peluncuran. Sale BELUM BUKA saat triase (opened=0, startTime 16:00 WIB hari ini).",
        "lastReadBlock": 132552663, "lastReadWib": "2026-11-09 ~15:5x WIB",
    }
snap["track_c"] = tc
report["discovery_incorporated"] = {
    "contracts_added": ["BMT Agents (excluded-free-sold-out)", "Burn Agent (excluded-free-sold-out)"],
    "track_c_added": ["NIBULL (watchlist-only-upcoming, buka 2026-11-09 16:00 WIB)"],
}

# ---- promotion screening (early leads with free% >= 25%, age <= 48h) ----
# Stage 1 velocity screening found 1 pass (Pandadroid +133, 42.87x, free% 55.04)
# BUT Pandadroid status = watchlist-only-same-owner-discarded-2026-11-03 -> discard
# di level triase = JANGAN promosi/eksekusi (pelajaran 2026-11-09 04:44). This is the
# independent strong-lead leg check: an early lead promotes only if age verified
# <=48h AND free >=25% AND user slot verified open. Checked from reread 1501 values:
promo = [
    "Pandadroid +133 (42.87x) free% 55.04 — velocity LOLOS TAPI status same-owner-discarded-2026-11-03 -> TIDAK promosi, TIDAK eksekusi, TIDAK laporan (discard = jangan eksekusi).",
    "Cassetto 38.94% (start 2026-11-08 14:56, age ~25h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "Retrocam 38.89% (start 2026-11-08 14:56, age ~25h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "Hourglas 43.44% (start 2026-11-08 14:56, age ~25h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "CAISHEN 29.84% (start 2026-11-08 14:55, age ~25h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "ShadowSquad 50.18% (start 2026-11-09 06:40) — already strong-lead-gate-failed-2026-11-09, no change; slot UNVERIFIED.",
    "0xbd4B4e7189ae9356514664146b0eD683601200A9 35.76% (start 2026-11-07 17:13, age ~46h) — slot USED (freeClaimed(user)=1, bal_user=1) -> no promotion.",
    "Lenx Agent Pass free% UNVERIFIED (freeClaimed/FREE_SUPPLY None) despite freeClaimed(user)=0 -> no promotion.",
    "BAHUANG3 / Meow Cards / MONEY — free% UNVERIFIED -> no promotion.",
    "Arachnoir — stays promotion-discarded-same-owner-2026-11-09 (owner 0xd76d... in same-owner-discards); free 93.42% moot.",
    "Agentyyds / Glitchdroid 99.17% — launch time UNVERIFIED (start=None) -> no promotion.",
]
report["promotion_screening"] = promo

# ---- finalize run notes ----
r1501 = json.load(open(f"{HF}/run-2026-11-09-1501-reread.json"))
snap["runNote1501_1109"] = (
    f"Run 1501: re-read {len(r1501.get('reread', {}))} kontrak + "
    f"{len(r1501.get('track_c', {}))} track_c "
    f"(blok 132550947, interval {report['interval_minutes']:.1f} mnt vs run 1431); "
    f"velocity LOLOS 1 (Pandadroid +133, 42.87x, free% 55.04) TAPI same-owner-discarded-2026-11-03 -> TIDAK promosi/eksekusi/laporan. "
    f"Promosi 0 (promotion screening: Cassetto/Retrocam/Hourglas/CAISHEN free% >=25% tapi slot user UNVERIFIED; 0xbd4B slot SUDAH terpakai; Lenx/BAHUANG3/Meow/MONEY free% UNVERIFIED; Arachnoir tetap same-owner-discarded; Agentyyds/Glitchdroid umur UNVERIFIED). "
    f"Age-exclusions: 0. Track-C: tidak ada sellout baru (NUSA freeMinted tetap 346). "
    f"Discovery (Subagent A): 3 kontrak BARU, semua ditriase on-chain parent — BMT Agents free pool HABIS 1000/1000 (excluded, bukan lead); "
    f"NIBULL 0x29666B sale BELUM BUKA (startTime 2026-11-09 16:00 WIB, FREE_SHARES 500, registry AMBIGU 0xc44f... bukan kanonik) -> track_c upcoming; "
    f"Burn Agent free pool HABIS 300/300 + umur >48 jam (excluded). Route 6: 0 item Agent ID (Odaily/PANews/Square/DappBay). "
    f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 (3,6 dtk + 3,6 dtk) — watermark TIDAK dimajukan (tetap 132512564, gap ~38.383 blok). "
    f"Binanceai tetap refund/failed. Bridge tidak berubah (116 kontrak; 1 tidak ada di snapshot: BNB Bull Pass, bukan lead). "
    f"5c: 2 ERC-20 sisa output scan 1231 dicek, 0 sale-shape. "
    f"TIDAK ADA LAPORAN KE MAIN CHAT (aturan diam: tidak ada kandidat/lead/promosi/perubahan yang wajib dilaporkan; 3 temuan discovery semuanya excluded/upcoming, dicatat di snapshot saja).")
snap["runNote1501_1109_discovery"] = (
    "Run 1501 discovery (Subagent A, read-only, Ankr tidak dipakai): Boltbook EN+ZH dibaca TAPI crawl basi (EN 13 jam, ZH 17 jam) — "
    "postingan terbaru setelah crawl tidak terlihat di kaki ini. Semua alamat Boltbook sudah di snapshot KECUALI BMT Agents 0x7d6e... (BARU, "
    "Boltbook ZH ~22:0x WIB 8 Nov: 920/2000, freeClaimed 920). OTV: alamat terpotong di excerpt, berbayar 0,0012 BNB per catatan run 0431. "
    "Sourcify feed 20 (crawl 07:50 UTC): 1 agent-shaped baru = NIBULL 0x29666B (S1 track-C, verifiedAt 14:05:58 WIB); 2 agent-gated tanpa free view "
    "(0xdA64..., 0x4424...); 18 bukan agent-shaped. Sweep EN+ZH: NOVRA (track_c, pool habis), AGC (dikenal, berbayar/refundable, bukan free mint), "
    "AGENT MAO (dikenal; alamat token artikel berbeda dari yang terlacak — dicatat), Subsonic Tribe + BNBmeme (sudah di snapshot), Burn Agent "
    "(Blockspot/Quantum Audit; kemungkinan age-excluded). Route 6: Binance Square hanya PTAH/Jager/panduan; Odaily (crawl 25 mnt) dan PANews "
    "(crawl 25 mnt) 0 item Agent ID; DappBay kategori AI dibaca, 'BMT' tidak ada hasil (ketidakhadiran bukan bukti). Triase parent (blok 132552663): "
    "BMT name 'BMT Agents'/symbol 'BMTA' terverifikasi on-chain, agentId()=registry kanonik, freeMinted 1000/1000 -> excluded-free-sold-out. "
    "NIBULL name/symbol 'NIBULL' terverifikasi on-chain; FREE_SHARES 500, soldShares 0, startTime 2026-11-09 16:00 WIB, opened=0, pair 0x0, "
    "registry()=0xc44f... (bukan kanonik; gate-function ada) -> track_c upcoming. Burn Agent FREE_SHARES 300/freeMinted 300 + umur ~6 hari -> excluded. "
    "Same-owner check: BMT/NIBULL/BURN tidak punya owner() (treasury()/opsWallet()/factory() saja) — cek owner/deployer WAJIB sebelum promosi/eksekusi bila ada yang naik tier; "
    "tidak ada item yang dipromosikan/dieksekusi run ini, tidak ada item BLOCKED oleh same-owner run ini (Pandadroid sudah discarded sejak 2026-11-03).")
snap["runNote1501_1109_age_exclusions"] = (
    f"Run 1501: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["runNote1501_1109_binanceai"] = (
    "Run 1501 (blok 132551014, probe dataseed ~15:25 WIB): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["last_run"] = "1501"
snap["last_run_wib"] = "2026-11-09 ~15:5x WIB"
snap["last_run_note"] = ("Run 1501: velocity lolos 1 (Pandadroid, discarded, tanpa promosi), promosi 0; discovery 3 baru (BMT excluded sold-out, "
                         "NIBULL upcoming buka 16:00 WIB, BURN excluded sold-out+age); scan fast-fail Ankr 401 (watermark tetap 132512564, gap "
                         "~38.383 blok); binanceai tetap refund; bridge tidak berubah; TIDAK ADA LAPORAN (aturan diam).")
snap["timestamp_wib"] = "2026-11-09 15:5x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
json.dump(report, open(f"{HF}/run-2026-11-09-1501-merge.json", "w"), indent=1)

runlog = f"""# Run log — free-mint-search 2026-11-09 15:01 WIB

- Re-read: {len(r1501.get('reread', {}))} kontrak + {len(r1501.get('track_c', {}))} track_c (blok 132550947, interval {report['interval_minutes']:.1f} mnt vs run 1431). Re-read selesai 927,3 dtk (dataseed lambat, 8-35 dtk/batch).
- Velocity LOLOS 1: Pandadroid +133 (42,87x, free% 55,04) — TAPI status watchlist-only-same-owner-discarded-2026-11-03 -> TIDAK promosi, TIDAK eksekusi, TIDAK laporan (discard = jangan eksekusi, pelajaran 2026-11-09 04:44). Promosi 0. Promotion screening (early lead free% >=25% + umur <=48h):
  - Cassetto 38,94% / Retrocam 38,89% / Hourglas 43,44% / CAISHEN 29,84% (umur ~25h) — slot user UNVERIFIED (freeClaimed(user) None) -> bukan strong lead.
  - ShadowSquad 50,18% — sudah strong-lead-gate-failed-2026-11-09, tanpa perubahan; slot UNVERIFIED.
  - 0xbd4B... 35,76% (umur ~46h) — slot user SUDAH terpakai (freeClaimed(user)=1, bal_user=1) -> bukan strong lead.
  - Lenx Agent Pass — free% UNVERIFIED walau freeClaimed(user)=0; BAHUANG3 / Meow Cards / MONEY free% UNVERIFIED -> bukan strong lead.
  - Arachnoir — tetap promotion-discarded-same-owner-2026-11-09 (owner 0xd76d... di same-owner-discards); free 93,42% moot.
  - Agentyyds / Glitchdroid 99,17% — umur peluncuran UNVERIFIED (start=None) -> bukan strong lead.
- Age-exclusions baru: tidak ada. Track-C sellout baru: tidak ada (NUSA freeMinted tetap 346; tidak ada perubahan freeMinted track-C).
- Scan leg (route 4): FAST-FAIL — Ankr pre-flight 401 x2 (3,6 dtk + 3,6 dtk, blok 132547300-132547349). Watermark TETAP 132512564; gap ke head 132550947 ~38.383 blok dan tumbuh. Backfill ikut terdampak (401 sejak ~13:33 WIB). Reconnect Ankr (parent ~13:49 WIB) belum terverifikasi pulih. Route 5c: 2 ERC-20 sisa output scan 1231 dicek (0x4A11... + 0xf8A8...), 0 sale-shape S1/S2 — dicatat di track-c-scan-checked.json (kini 2011 entri).
- Track B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, saldo TOKEN 0 (blok 132551014, ~15:25 WIB). Sudah dilaporkan sekali; tidak dilaporkan ulang.
- Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC, 116 kontrak); 1 tidak ada di snapshot: BNB Bull Pass 0x64295d2d (run-1 finding, 1 entity, bukan lead) — bukan temuan pelengkap baru, tidak dipromosikan.
- Discovery (Subagent A) + triase parent (blok 132552663): 3 kontrak BARU, semuanya berakhir excluded/upcoming — BUKAN lead/kandidat:
  - BMT Agents (BMTA) 0x7d6e8528cc918afbd0ba5b0998c8a57860d2ded6 — Boltbook ZH ~22:0x WIB 8 Nov (920/2000 saat post). On-chain: name/symbol terverifikasi, agentId()=registry kanonik 0x60B9..., agent-shaped YA; TAPI freeMinted 1000/1000 (FREE_SUPPLY 1000) -> free pool HABIS -> excluded-free-sold-out-2026-11-09, dicatat di snapshot, TIDAK dilaporkan sebagai lead.
  - NIBULL 0x29666Bc0004824dc2B282c82aAC206b8b1711839 — Sourcify feed (verifiedAt 14:05:58 WIB), S1 track-C di level ABI. On-chain: name/symbol 'NIBULL', FREE_SHARES 500, soldShares 0, TOTAL_SHARES 10000, TOKENS_PER_SHARE 60.000.000, pricePerShare 0,002 BNB, startTime 2026-11-09 16:00 WIB, opened=0, pair 0x0 -> BELUM BUKA -> track_c watchlist-only-upcoming-2026-11-09. registry()=0xc44f... (BUKAN registry kanonik; gate-function walletAgent/hasBought/agentShares/claimed ada) -> kaki registry AMBIGU, verifikasi ulang saat sale buka. walletAgent(user)=0. Run berikut pasca-16:00 WIB evaluasi ulang sebagai lead.
  - Burn Agent (BURN) 0x7de1606230aa70802caecf1a3e90039a6265b1c4 — Blockspot/Quantum Audit. On-chain: FREE_SHARES 300, freeMinted 300 -> free pool HABIS; umur ~6 hari (Quantum Audit 3 Nov) -> excluded-free-sold-out-2026-11-09 (+age-excluded), dicatat di snapshot, TIDAK dilaporkan sebagai lead. Bukan koin 'Burn' scalp user.
  - Boltbook EN+ZH: crawl basi (EN 13 jam, ZH 17 jam) — postingan terbaru setelah crawl tidak terlihat; OTV alamat terpotong di excerpt (berbayar 0,0012 BNB, bukan lead baru).
  - Sourcify feed 20: 1 agent-shaped baru (NIBULL); 2 agent-gated tanpa free view; 18 bukan agent-shaped.
  - Sweep: NOVRA (track_c, pool habis), AGC (dikenal, berbayar/refundable), AGENT MAO (dikenal; alamat token artikel Substack berbeda dari yang terlacak — dicatat), Subsonic Tribe + BNBmeme (sudah di snapshot).
  - Route 6: 0 item Agent ID di Odaily/PANews; Square hanya PTAH/Jager/panduan; DappBay kategori AI tanpa 'BMT'.
  - Same-owner check: BMT/NIBULL/BURN tidak punya owner() (hanya treasury()/opsWallet()/factory()) — cek owner/deployer WAJIB sebelum promosi/eksekusi bila ada yang naik tier; tidak ada item yang dipromosikan/dieksekusi run ini.
- Eksekusi: 0 (tidak ada preview/mint/claim/swap).
- LAPORAN KE MAIN CHAT: TIDAK ADA (aturan diam — tidak ada kandidat/lead/promosi/perubahan yang wajib dilaporkan; 3 temuan discovery semuanya excluded/upcoming).

Files: run-2026-11-09-1501-reread.json, run-2026-11-09-1501-reread.log, run-2026-11-09-1501-binanceai.json,
run-2026-11-09-1501-preflight.py/.json, run-2026-11-09-1501-discovery.json/.md, run-2026-11-09-1501-triage.py/.json,
run-2026-11-09-1501-merge-stage1.py/.json, run-2026-11-09-1501-merge-stage2.py, run-2026-11-09-1501-merge.json,
run-2026-11-09-1501-runlog.md, onchain-snapshot.json (+.bak-2026-11-09-1501, +.bak-2026-11-09-1501-stage2).
"""
open(f"{HF}/run-2026-11-09-1501-runlog.md", "w").write(runlog)
print("MERGE STAGE 2 DONE. snapshot contracts now:", len(snap.get("contracts", {})))
print("last_run:", snap.get("last_run"))
