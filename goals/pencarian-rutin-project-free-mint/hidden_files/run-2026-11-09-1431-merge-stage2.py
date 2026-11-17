#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1431 WIB — incorporate Subagent A discovery
(run-2026-11-09-1431-discovery.json/.md) into the snapshot (already stage-1
merged) and finalize run notes. Discovery found NOTHING new this run, so no
new contract entries are added. No scan output (pre-flight 401 fast-fail).
Read-only w.r.t. chain; never mints/previews.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1431-merge.json,
run-2026-11-09-1431-runlog.md.
"""
import json, os, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
stage1 = json.load(open(f"{HF}/run-2026-11-09-1431-merge-stage1.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1431-discovery.json"))

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1431-stage2")
contracts = snap.get("contracts", {})

report = dict(stage1)
report["stage"] = 2
report["discovery"] = {
    "verdict": disc.get("verdict"),
    "new_watchlist_only": [],
    "new_excluded": [],
    "sourcify_non_agent": [],
    "bridge_new": [],
    "bridge_not_in_snapshot": ["PANBA ERC20 (run-36)", "Unnamed ERC20 paid 0.15 BNB (run-70)",
                                "ETHBack Dividend Tracker paid 0.1 BNB (run-123)"],
    "boltbook_not_contracts": ["0x9baca74188d885725ac50a6e16bfa6b52f2c06bc (no code)",
                               "0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2 (code read inconclusive, shape-check False)"],
}

# ---- promotion screening (early leads with free% >= 25%, age <= 48h) ----
# Stage 1 velocity screening found 0 passes; this is the independent strong-lead
# leg check: an early lead promotes only if age verified <=48h AND free >=25%
# AND user slot verified open. Checked from reread 1431 values:
promo = [
    "Cassetto 38.93% (start 2026-11-08 14:56, age ~24h) — slot UNVERIFIED (freeClaimed(user) reverts/None) -> no promotion.",
    "Retrocam 38.87% (start 2026-11-08 14:56, age ~24h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "Hourglas 43.43% (start 2026-11-08 14:56, age ~24h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "CAISHEN 29.5% (start 2026-11-08 14:55, age ~24h) — slot UNVERIFIED (freeClaimed(user) None) -> no promotion.",
    "ShadowSquad 50.18% (start 2026-11-09 06:40) — already strong-lead-gate-failed-2026-11-09, no change; slot UNVERIFIED.",
    "0xbd4B4e7189ae9356514664146b0eD683601200A9 35.76% (start 2026-11-07 17:13, age ~46h) — slot USED (freeClaimed(user)=1, bal_user=1) -> no promotion.",
    "Lenx Agent Pass free% UNVERIFIED (freeClaimed/FREE_SUPPLY None) despite freeClaimed(user)=0 -> no promotion.",
    "BAHUANG3 / Meow Cards / MONEY — free% UNVERIFIED -> no promotion.",
    "Arachnoir — stays promotion-discarded-same-owner-2026-11-09 (owner 0xd76d... in same-owner-discards); free 93.42% moot.",
]
report["promotion_screening"] = promo

# ---- finalize run notes ----
r1431 = json.load(open(f"{HF}/run-2026-11-09-1431-reread.json"))
snap["runNote1431_1109"] = (
    f"Run 1431: re-read {len(r1431.get('reread', {}))} kontrak + "
    f"{len(r1431.get('track_c', {}))} track_c "
    f"(blok 132547312, interval {report['interval_minutes']:.1f} mnt vs run 1401); "
    f"velocity LOLOS 0 — promosi 0 (promotion screening: Cassetto/Retrocam/Hourglas/CAISHEN free% >=25% tapi slot "
    f"user UNVERIFIED; 0xbd4B slot SUDAH terpakai; Lenx/BAHUANG3/Meow/MONEY free% UNVERIFIED; Arachnoir tetap same-owner-discarded). "
    f"Age-exclusions: 0. Track-C: tidak ada sellout baru (NUSA freeMinted tetap 346). "
    f"Discovery (Subagent A): TIDAK ADA early/strong/kandidat/track-B/track-C baru — 0 kontrak baru. Dua alamat Boltbook dari hot leg "
    f"14:44 bukan kontrak/agent-shaped (0x9baca... tanpa kode; 0xA587... shape-check False). Sourcify feed identik dengan poll hot leg "
    f"14:44. MINTS tidak berubah (hanya featured BERBAYAR baru). Route 6: 0 item Agent ID (Odaily/PANews/Square/DappBay). "
    f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 (17,1 dtk + 6,6 dtk) — watermark TIDAK dimajukan (tetap 132512564, gap ~34.748 blok). "
    f"Binanceai tetap refund/failed. Bridge tidak berubah (mtime 2026-11-08 18:21 UTC; 3 temuan lama non-snapshot: PANBA ERC20, "
    f"Unnamed ERC20 berbayar 0,15 BNB, ETHBack Dividend Tracker berbayar 0,1 BNB — bukan lead baru). "
    f"TIDAK ADA LAPORAN KE MAIN CHAT (aturan diam: tidak ada kandidat/lead/perubahan yang wajib dilaporkan).")
snap["runNote1431_1109_discovery"] = (
    "Run 1431 discovery (Subagent A, read-only, Ankr tidak dipakai): Boltbook EN+ZH — semua alamat terlihat sudah ada di "
    "snapshot/hot-leg-seen (Rose Genesis, WAR3, First-Dollar Grove, Fleet, NUSA, PAWG, EMBER, Pathwyrm, HELM, Pokechain, Jinchan, "
    "Lambdwyn, BMT Agents, Hivebyte, Kappaxis, ALL ACCESS), tidak ada yang baru; DIGENT di Robinhood Chain (di luar scope BSC); "
    "boltbook.com mati, tidak dipakai. Dua alamat Boltbook hot leg 14:44 diverifikasi on-chain: 0x9baca... eth_getCode 0x (bukan "
    "kontrak), 0xA587... pembacaan kode tidak konklusif (RPC terdegradasi) tapi shape-check hot leg False — bukan lead. Sourcify "
    "feed 20 (verifiedAt 14:05-14:43 WIB) identik dengan poll hot leg 14:44; 2 terbaru sudah di-shape-check hot leg (S1/S2 False). "
    "Sweep EN+ZH via indeks MINTS (60 proyek, update 11:46 IST, tidak berubah sejak 14:01): satu-satunya 'baru' vs snapshot adalah 3 "
    "featured BERBAYAR (Horror Protocol $3, DNA EATER $3-30, SYNTAX SOULS $5) — gugur free-only. Burn Agent, NOVRA, AGENT MAO, MOLT "
    "AGENT sudah dikenal. Route 6: Binance Square hanya panduan/NOVRA/MOLT; Odaily (07:54 UTC) dan PANews (07:55 UTC) 0 item Agent "
    "ID; DappBay kategori AI tanpa hasil. Bridge: 3 kontrak tidak ada di snapshot (turun dari 8 di run 1401 — 5 lainnya sudah masuk "
    "snapshot via track_c/excluded) — semuanya temuan scan lama, sudah dilaporkan job scan; bukan temuan pelengkap baru, tidak "
    "dipromosikan. Same-owner check: tidak ada kontrak baru, tidak ada owner baru diperiksa, tidak ada item BLOCKED run ini.")
snap["runNote1431_1109_age_exclusions"] = (
    f"Run 1431: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["runNote1431_1109_binanceai"] = (
    "Run 1431 (blok 132547343, probe dataseed ~14:47 WIB): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["last_run"] = "1431"
snap["last_run_wib"] = "2026-11-09 ~15:1x WIB"
snap["last_run_note"] = ("Run 1431: velocity lolos 0, promosi 0; discovery 0 baru; scan fast-fail Ankr 401 (watermark tetap 132512564, gap "
                         "~34.748 blok); binanceai tetap refund; bridge 3 temuan lama non-lead; TIDAK ADA LAPORAN (aturan diam).")
snap["timestamp_wib"] = "2026-11-09 15:1x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
json.dump(report, open(f"{HF}/run-2026-11-09-1431-merge.json", "w"), indent=1)

runlog = f"""# Run log — free-mint-search 2026-11-09 14:31 WIB

- Re-read: {len(r1431.get('reread', {}))} kontrak + {len(r1431.get('track_c', {}))} track_c (blok 132547312, interval {report['interval_minutes']:.1f} mnt vs run 1401).
- Velocity LOLOS 0, promosi 0. Promotion screening (early lead free% >=25% + umur <=48h):
  - Cassetto 38.93% / Retrocam 38.87% / Hourglas 43.43% / CAISHEN 29.5% (umur ~24h) — slot user UNVERIFIED (freeClaimed(user) None) -> bukan strong lead.
  - ShadowSquad 50.18% — sudah strong-lead-gate-failed-2026-11-09, tanpa perubahan; slot UNVERIFIED.
  - 0xbd4B... 35.76% (umur ~46h) — slot user SUDAH terpakai (freeClaimed(user)=1, bal_user=1) -> bukan strong lead.
  - Lenx Agent Pass — free% UNVERIFIED walau freeClaimed(user)=0; BAHUANG3 / Meow Cards / MONEY free% UNVERIFIED -> bukan strong lead.
  - Arachnoir — tetap promotion-discarded-same-owner-2026-11-09 (owner 0xd76d... di same-owner-discards); free 93.42% moot.
- Age-exclusions baru: tidak ada. Track-C sellout baru: tidak ada (NUSA freeMinted tetap 346; tidak ada perubahan freeMinted track-C).
- Scan leg (route 4): FAST-FAIL — Ankr pre-flight 401 x2 (17,1 dtk + 6,6 dtk, blok 132547300-132547349). Watermark TETAP 132512564; gap ke head 132547312 ~34.748 blok dan tumbuh. Backfill ikut terdampak. Reconnect Ankr (parent ~13:49 WIB) belum terverifikasi pulih. Route 5c tanpa output scan baru.
- Track B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, saldo TOKEN 0 (blok 132547343, ~14:47 WIB). Sudah dilaporkan sekali; tidak dilaporkan ulang.
- Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC); 3 kontrak tidak ada di snapshot (turun dari 8 di run 1401 — 5 lainnya sudah masuk snapshot via track_c/excluded): PANBA ERC20 (run-36), Unnamed ERC20 BERBAYAR 0,15 BNB (run-70), ETHBack Dividend Tracker BERBAYAR 0,1 BNB (run-123). Semuanya temuan scan lama, sudah dilaporkan job scan; bukan temuan pelengkap baru, tidak dipromosikan.
- Discovery (Subagent A): Boltbook EN+ZH, Sourcify feed 20, sweep EN+ZH (MINTS), route 6 (Odaily/PANews/Square/DappBay) — TIDAK ADA early/strong/kandidat/track-B/track-C baru; 0 kontrak baru.
  - Dua alamat Boltbook hot leg 14:44: 0x9baca74188d885725ac50a6e16bfa6b52f2c06bc tanpa kode kontrak (bukan kontrak); 0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2 shape-check False (bukan agent-shaped).
  - Sourcify feed identik dengan poll hot leg 14:44 (verifiedAt 14:05-14:43 WIB); 2 terbaru sudah di-shape-check hot leg (S1/S2 False).
  - MINTS tidak berubah sejak run 14:01; hanya 3 featured BERBAYAR yang "baru" (Horror Protocol $3, DNA EATER $3-30, SYNTAX SOULS $5) — gugur free-only.
  - Route 6: 0 item Agent ID di Odaily/PANews; Square hanya panduan/NOVRA/MOLT; DappBay tanpa hasil.
  - Same-owner check: tidak ada kontrak baru, tidak ada item BLOCKED run ini.
- Eksekusi: 0 (tidak ada preview/mint/claim/swap).
- LAPORAN KE MAIN CHAT: TIDAK ADA (aturan diam — tidak ada kandidat/lead/perubahan yang wajib dilaporkan).

Files: run-2026-11-09-1431-reread.json, run-2026-11-09-1431-reread.log, run-2026-11-09-1431-binanceai.json,
run-2026-11-09-1431-preflight.py/.json, run-2026-11-09-1431-discovery.json/.md, run-2026-11-09-1431-merge-stage1.py/.json,
run-2026-11-09-1431-merge-stage2.py, run-2026-11-09-1431-merge.json, onchain-snapshot.json (+.bak-2026-11-09-1431, +.bak-2026-11-09-1431-stage2).
"""
open(f"{HF}/run-2026-11-09-1431-runlog.md", "w").write(runlog)
print("MERGE STAGE 2 DONE. snapshot contracts now:", len(snap.get("contracts", {})))
print("last_run:", snap.get("last_run"))
