#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1401 WIB — incorporate Subagent A discovery
(run-2026-11-09-1401-discovery.json/.md) into the snapshot (already stage-1
merged) and finalize run notes. No scan output (pre-flight 401 fast-fail).
Read-only w.r.t. chain; never mints/previews.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1401-merge.json,
run-2026-11-09-1401-runlog.md.
"""
import json, os, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
stage1 = json.load(open(f"{HF}/run-2026-11-09-1401-merge-stage1.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-1401-discovery.json"))

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-2026-11-09-1401-stage2")
contracts = snap.get("contracts", {})

report = dict(stage1)
report["stage"] = 2
report["discovery"] = {
    "verdict": "no new early/strong/candidate/track-B/track-C lead",
    "new_watchlist_only": ["BN Agent File"],
    "new_excluded": ["Black Hole", "PIXEL", "Agent Bunnies"],
    "sourcify_non_agent": ["0x393de7D77d00aE265AC37Dbd8DF9B6C9E51242c2 (PackagePurchase)"],
    "bridge_new": [],
}

# ---- 1. BN Agent File — watchlist-only, mature newly-noticed (NOT an early lead) ----
contracts["BN Agent File"] = {
    "address": "0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1",
    "status": "watchlist-only-mature-newly-noticed-2026-11-09",
    "name": "BN Agent File",
    "symbol": "BNAF",
    "kind": "ERC721",
    "totalSupply": None,
    "totalMinted": 6519,
    "supplyView": "totalMinted (totalSupply() reverts)",
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": None,
    "SERIES_COUNT": 12,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "userBalance": 0,
    "firstSeenBlock": 132544199,
    "lastReadBlock": 132544199,
    "lastReadWib": "2026-11-09 14:3x WIB",
    "xVerified": False,
    "velocityVerified": False,
    "velocityLegPasses": False,
    "freePctVerified": None,
    "website": None,
    "websiteNote": "MINTS website null; project-name search found no project site (methods A+G tried). Gate website FAILED as far as verified.",
    "owner": "0xb95a4f80acb466df37a51bf9bf8b353ebb990cfd",
    "ownerNote": "Owner NOT in same-owner-discards.json (checked run 1401).",
    "launchNote": ("Age UNVERIFIED: no project-stated launch time; first mint not verified on-chain "
                   "(Ankr 401; dataseed multi-day getLogs not feasible). MINTS added_at 2026-10-29T20:49:54Z "
                   "(index presence ~11 days) suggests >48h but is an index-listing bound, not a verified launch time — "
                   "kept watchlist-only pending corroboration, NOT age-excluded on this evidence alone."),
    "baselineNote": ("DITEMUKAN run 1401 via MINTS index (thecolony.ai, rank 32, score 80, status free_live). "
                     "Agent-shaped VERIFIED parent (registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain, "
                     "totalMinted 6519, mintOpen 1, SERIES_COUNT 12; totalSupply() reverts). Soulbound (not transferable) "
                     "per MINTS — cannot be listed/sold even if free. No free-counter views in ABI (no freeClaimed/freeMinted/"
                     "FREE_SUPPLY) so free% UNVERIFIED; no quote/cost function so user slot UNVERIFIED. NOT an early lead "
                     "(first mints not verified on-chain in this run; mature ~11-day index presence, not a fresh launch — "
                     "precedent 0x4AB41152 run 0831). NOT a strong lead, NOT a candidate. Website gate FAILED (no site found)."),
    "runNote1401_1109": ("Run 1401: first read (blok 132544199): registry()=registry, totalMinted 6519, mintOpen 1, "
                         "SERIES_COUNT 12, bal_user 0; age/website/free%/slot/X all UNVERIFIED. Watchlist-only; no report."),
    "previousTotalSupply": None,
    "mintedInInterval": None,
    "intervalMinutes": None,
    "currentRatePerMin": None,
    "previousRatePerMin": None,
}

# ---- 2. Black Hole — free lane closed (excluded, record only) ----
contracts["Black Hole"] = {
    "address": "0xc84e8281153387e9f35c99ce316075e3c38dd388",
    "status": "excluded-free-closed-2026-11-09",
    "name": "Black Hole",
    "symbol": "BHOLE",
    "kind": "ERC721",
    "totalSupply": 7805,
    "MAX_SUPPLY": 10000,
    "TIER1_CAP": 7000,
    "FREE_PER_WALLET": 2,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "userBalance": 0,
    "mintedBy_user": 1,
    "quote_user_1": 887403887503454,
    "lastReadBlock": 132544199,
    "lastReadWib": "2026-11-09 14:3x WIB",
    "xVerified": False,
    "website": "http://blackhole-nft.pages.dev",
    "websiteNote": "VERIFIED run 1401: site prints the exact contract (mint instructions + contract section).",
    "owner": "0x098b16c55a0aede71341a19747cc667963b8e19a",
    "ownerNote": "Owner NOT in same-owner-discards.json (checked run 1401).",
    "launchNote": "Age UNVERIFIED (no stated launch time; MINTS added_at 2026-10-29 suggests >48h). Moot — free lane closed.",
    "baselineNote": ("DITEMUKAN run 1401 via MINTS index (rank 46, score 53, added 2026-10-29). Agent-shaped VERIFIED "
                     "(agentId()=registry, agentGateEnabled()=1, FREE_PER_WALLET 2, TIER1_CAP 7000). Free lane CLOSED: site "
                     "states 'Free mint is over… Ended at 7,000 minted'; on-chain totalSupply 7805 > TIER1_CAP 7000; "
                     "quote(user,1) = 887403887503454 wei (~0.000887 BNB) > 0; mintedBy(user)=1. NOT a lead; record only, never report."),
    "runNote1401_1109": "Run 1401: free lane closed (totalSupply 7805 > 7000, quote user > 0) — excluded, no report.",
}

# ---- 3. PIXEL — phase 2, no free mints (excluded; same project body already ruled out) ----
contracts["PIXEL"] = {
    "address": "0x68f21fef10a02f82d147192fc317e70de99dd882",
    "status": "excluded-free-phase-over-2026-11-09",
    "name": "PIXEL",
    "symbol": "PIXEL",
    "kind": "ERC721",
    "totalSupply": 7034,
    "MAX_SUPPLY": 10000,
    "PHASE1_SUPPLY": 7000,
    "mintOpen": 1,
    "balanceOf_user": 0,
    "userBalance": 0,
    "mintedBy_user": 0,
    "remainingForWallet_user": 5,
    "lastReadBlock": 132544199,
    "lastReadWib": "2026-11-09 14:3x WIB",
    "xVerified": False,
    "website": "https://pixelagents.pages.dev",
    "websiteNote": "VERIFIED run 1401: site prints the exact contract. Site counter still reads 57/10,000 (stale, same as body note).",
    "owner": "0x61a7ef378eced7e110f48d169bed7e9e0063b8d2",
    "ownerNote": "Owner NOT in same-owner-discards.json (checked run 1401).",
    "launchNote": "Age UNVERIFIED (no stated launch time; MINTS added_at 2026-10-30 suggests >48h). Moot — free phase over.",
    "baselineNote": ("DITEMUKAN run 1401 via MINTS index (rank 47, score 53, added 2026-10-30). Agent-shaped VERIFIED "
                     "(AGENT_ID_REGISTRY()=registry, PHASE1_SUPPLY 7000). Free lane CLOSED: phase 1 (tokens 1–7,000, first 2 free) "
                     "over; phase 2 (7,001–10,000) $1.00 each, NO free mints; on-chain totalSupply 7034 > 7000 confirms phase 2. "
                     "Same project the body already ruled out (PIXEL, site counter 57/10000). NOT a lead; record only, never report."),
    "runNote1401_1109": "Run 1401: phase 2 (totalSupply 7034 > 7000), no free mints — excluded, no report.",
}

# ---- 4. Agent Bunnies — free tier sold out + user slot used (excluded, record only) ----
contracts["Agent Bunnies"] = {
    "address": "0x546d13c0b614f4403471e6d6c4e83548e73308dc",
    "status": "excluded-user-slot-used-2026-11-09",
    "name": "Agent Bunnies",
    "symbol": "BUNNY",
    "kind": "ERC721",
    "totalSupply": 5065,
    "MAX_SUPPLY": 10000,
    "FREE_PER_WALLET": 2,
    "mintLive": 1,
    "balanceOf_user": 0,
    "userBalance": 0,
    "freeMinted_user": 2,
    "freeRemaining_user": 0,
    "totalMintedBy_user": 2,
    "lastReadBlock": 132544199,
    "lastReadWib": "2026-11-09 14:3x WIB",
    "xVerified": False,
    "website": "https://agentbunnies.pages.dev",
    "websiteNote": "VERIFIED run 1401: site prints the exact contract (mint instructions).",
    "owner": "0x36b400dce9ade513097332ee13c5b14f0a389616",
    "ownerNote": "Owner NOT in same-owner-discards.json (checked run 1401).",
    "launchNote": "Age UNVERIFIED (no stated launch time; MINTS added_at 2026-10-31 suggests >48h). Moot — free tier sold out + slot used.",
    "baselineNote": ("DITEMUKAN run 1401 via MINTS index (rank 48, score 53, added 2026-10-31). Agent-shaped VERIFIED "
                     "(agentIdContract()=registry, FREE_PER_WALLET 2, mintLive 1). Free tier CLOSED: site states 'The free tier "
                     "sold out at 5,000. Every mint now costs $0.60'; on-chain totalSupply 5065 > 5000. User slot USED: "
                     "freeMinted(user)=2, freeRemaining(user)=0 (2 free mints used; tokens no longer held, balanceOf=0). "
                     "NOT a lead; record only, never report."),
    "runNote1401_1109": "Run 1401: free tier sold out (5065 > 5000) + user slot used 2/2 — excluded, no report.",
}

# ---- 5. finalize run notes ----
vel_notes = report.get("velocity_notes", [])
snap["runNote1401_1109"] = (
    f"Run 1401: re-read {len(json.load(open(f'{HF}/run-2026-11-09-1401-reread.json')).get('reread', {}))} kontrak + "
    f"{len(json.load(open(f'{HF}/run-2026-11-09-1401-reread.json')).get('track_c', {}))} track_c "
    f"(blok 132542627, interval {report['interval_minutes']:.1f} mnt vs run 1301); "
    f"velocity LOLOS {len(report['velocity_pass'])}: {', '.join(v['name'] for v in report['velocity_pass'])} — "
    f"promosi 0: {'; '.join(vel_notes)}. "
    f"Age-exclusions: {len(report['age_exclusions'])}. "
    f"Discovery (Subagent A): TIDAK ADA early/strong/kandidat/track-B/track-C baru. Baru dicatat: BN Agent File "
    f"0x6B1719EE… (agent-shaped terverifikasi parent, totalMinted 6519, soulbound, website TIDAK ditemukan, umur/free%/slot "
    f"unverified) → watchlist-only-mature-newly-noticed, BUKAN early lead; Black Hole 0xc84e82… (free lane tutup di 7.000, "
    f"totalSupply 7805, quote user > 0), PIXEL 0x68f21f… (fase 2, totalSupply 7034 > 7000, tanpa free — proyek yang sama dengan "
    f"yang body sudah rule-out), Agent Bunnies 0x546d13… (free tier habis di 5.000, totalSupply 5065, slot user sudah terpakai 2/2) "
    f"→ ketiganya excluded, hanya dicatat, TIDAK dilaporkan. Sourcify baru 0x393de7… = PackagePurchase, bukan agent-shaped. "
    f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 — watermark TIDAK dimajukan (tetap 132512564, gap ~30.093 blok). "
    f"Binanceai tetap refund/failed. Bridge tidak berubah (mtime 2026-11-08 18:21 UTC; 8 temuan lama, bukan baru). "
    f"TIDAK ADA LAPORAN KE MAIN CHAT (aturan diam: tidak ada kandidat/lead/perubahan yang wajib dilaporkan).")
snap["runNote1401_1109_discovery"] = (
    "Run 1401 discovery (Subagent A, read-only, Ankr tidak dipakai): Boltbook EN+ZH — semua alamat terlihat sudah ada di "
    "snapshot/hot-leg-seen (Rose Genesis, First-Dollar Grove, PAWG, EMBER, Pathwyrm, HELM, Fleet, Pokechain, Jinchan, Lambdwyn, "
    "BMT Agents, Hivebyte, Kappaxis, ALL ACCESS), tidak ada yang baru; boltbook.com mati, tidak dipakai. Sourcify feed 20 "
    "(verifiedAt 13:50–14:13 WIB): 19 sudah di hot-leg-seen; hanya 0x393de7… baru = PackagePurchase (buyPackageBNB/USDT), bukan "
    "agent-shaped. Sweep EN+ZH via indeks MINTS (57 proyek, update 2026-11-09 11:46 IST): 47 dikenal; 10 baru vs snapshot+hotleg, "
    "6 sudah di snapshot excluded (Xuanwu Seed, Ombrello, Hackou AI Pass, Agentic Pixels, CIOW Citizens, AGENT NFT — age-excluded "
    "2026-11-07); 4 sisanya = BN Agent File / Black Hole / PIXEL / Agent Bunnies (di atas). NOVRA sudah di track_c (pool habis); "
    "AGENT MAO sudah di track_c (age-excluded); Agent Zet fase gratis habis; HOPKIN tanpa alamat kontrak (tidak dikejar). Route 6: "
    "Odaily/PANews 0 item Agent ID; Binance Square hanya NOVRA (dikenal/habis) + panduan umum; DappBay kategori AI tanpa listing "
    "proyek terkait. Bridge: 8 kontrak tidak ada di snapshot — semuanya temuan scan lama (run-13 s.d. run-123), sudah dilaporkan job "
    "scan; 7 mint berbayar/dividend/ERC20, 1 PANBA ERC20 — bukan temuan pelengkap baru, tidak dipromosikan. Same-owner check: owner "
    "keempat kontrak baru tidak cocok dengan 12 owner discard; tidak ada item BLOCKED run ini.")
snap["runNote1401_1109_age_exclusions"] = (
    f"Run 1401: age-exclusions baru: {json.dumps(report['age_exclusions'])}; "
    f"kept (sold out, age N/A): {json.dumps(report['age_candidates_kept'])}.")
snap["last_run"] = "1401"
snap["last_run_wib"] = "2026-11-09 ~14:4x WIB"
snap["last_run_note"] = ("Run 1401: velocity lolos 4 tanpa promosi; discovery: 0 lead baru (BN Agent File watchlist-only; Black Hole + "
                         "PIXEL + Agent Bunnies free-path tutup, excluded); scan fast-fail Ankr 401 (watermark tetap 132512564, gap "
                         "~30.093 blok); binanceai tetap refund; TIDAK ADA LAPORAN (aturan diam).")
snap["timestamp_wib"] = "2026-11-09 14:4x WIB"

def save_atomic(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, path)

save_atomic(f"{HF}/onchain-snapshot.json", snap)
json.dump(report, open(f"{HF}/run-2026-11-09-1401-merge.json", "w"), indent=1)

runlog = f"""# Run log — free-mint-search 2026-11-09 14:01 WIB

- Re-read: 582 kontrak + 81 track_c (blok 132542627, interval {report['interval_minutes']:.1f} mnt vs run 1301).
- Velocity LOLOS 4, promosi 0:
  - BNBRunnerz-2674 +65 (22.85x) — free% UNVERIFIED, umur UNVERIFIED, website TIDAK ditemukan → bukan strong lead/kandidat.
  - Sidecoo +44 (6.87x) — free% UNVERIFIED (semua free view revert, MAX_SUPPLY tak terbatas) → bukan strong lead/kandidat.
  - 0x4AB41152 +109 (4.32x) — mature newly-noticed, umur/free% UNVERIFIED → bukan strong lead/kandidat.
  - Bubblebruin +71 (33.26x) — SUDAH DIMILIKI user → moot.
- Age-exclusions baru: tidak ada. Track-C sellout baru: tidak ada (NUSA freeMinted 337→346).
- Scan leg (route 4): FAST-FAIL — Ankr pre-flight 401 x2 (9,2 dtk + 8,3 dtk, blok 132542607–132542657). Watermark TETAP 132512564; gap ke head 132542657 ~30.093 blok dan tumbuh. Backfill ikut terdampak. Reconnect Ankr (parent ~13:49 WIB) belum terverifikasi pulih.
- Track B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, saldo TOKEN 0. Sudah dilaporkan sekali; tidak dilaporkan ulang.
- Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC); 8 temuan lama, bukan baru.
- Discovery (Subagent A): Boltbook EN+ZH, Sourcify feed 20, sweep EN+ZH (MINTS), route 6 (Odaily/PANews/Square/DappBay) — TIDAK ADA early/strong/kandidat/track-B/track-C baru.
  - BN Agent File 0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1 → watchlist-only-mature-newly-noticed (agent-shaped terverifikasi parent: registry()=registry, totalMinted 6519, mintOpen 1, SERIES_COUNT 12; soulbound; website TIDAK ditemukan; umur/free%/slot unverified; MINTS added 2026-10-29). BUKAN early lead (first mint tidak terverifikasi on-chain; mature ~11 hari).
  - Black Hole 0xc84e8281153387e9f35c99ce316075e3c38dd388 → excluded-free-closed (free lane tutup di 7.000, totalSupply 7805, quote user ~0.000887 BNB > 0).
  - PIXEL 0x68f21fef10a02f82d147192fc317e70de99dd882 → excluded-free-phase-over (fase 2, totalSupply 7034 > 7000, $1 tanpa free; proyek sama dengan yang body rule-out).
  - Agent Bunnies 0x546d13c0b614f4403471e6d6c4e83548e73308dc → excluded-user-slot-used (free tier habis di 5.000, totalSupply 5065, freeMinted(user)=2, freeRemaining(user)=0).
  - Sourcify baru 0x393de7D77d00aE265AC37Dbd8DF9B6C9E51242c2 = PackagePurchase, bukan agent-shaped.
  - Same-owner check: tidak ada item BLOCKED run ini.
- Eksekusi: 0 (tidak ada preview/mint/claim/swap).
- LAPORAN KE MAIN CHAT: TIDAK ADA (aturan diam — tidak ada kandidat/lead/perubahan yang wajib dilaporkan).

Files: run-2026-11-09-1401-reread.json, run-2026-11-09-1401-reread.log, run-2026-11-09-1401-binanceai.json,
run-2026-11-09-1401-discovery.json/.md, run-2026-11-09-1401-merge-stage1.py/.json, run-2026-11-09-1401-merge-stage2.py,
run-2026-11-09-1401-merge.json, onchain-snapshot.json (+.bak-2026-11-09-1401, +.bak-2026-11-09-1401-stage2).
"""
open(f"{HF}/run-2026-11-09-1401-runlog.md", "w").write(runlog)
print("MERGE STAGE 2 DONE. snapshot contracts now:", len(snap.get("contracts", {})))
print("added:", ["BN Agent File", "Black Hole", "PIXEL", "Agent Bunnies"])
