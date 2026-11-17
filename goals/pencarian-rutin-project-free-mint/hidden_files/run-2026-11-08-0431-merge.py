#!/usr/bin/env python3
"""Merge run 0431 WIB 2026-11-08 into onchain-snapshot.json (pattern run 0401).
Backup first. Merges: reread (458 kontrak, blok 132275556), velocity rows+passes,
track_c moves, BNAgentFile gate+age verification, run notes. No new entries added.
"""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SNAP = HF + "onchain-snapshot.json"

shutil.copy(SNAP, SNAP + ".bak-20261108-0431")
snap = json.load(open(SNAP))
contracts = snap.setdefault("contracts", {})

# --- merge re-read (458 kontrak), blok 132275556 ---
rr = json.load(open(HF + "run-2026-11-08-0431-reread.json"))
reread = rr.get("reread", {})
updated = 0
for name, r in reread.items():
    e = contracts.get(name)
    if e is None:
        continue
    old_ts = e.get("totalSupply")
    new_ts = r.get("totalSupply")
    if new_ts is not None:
        e["previousTotalSupply"] = old_ts
        e["totalSupply"] = new_ts
        e["mintedInInterval"] = (new_ts - old_ts) if isinstance(old_ts, int) else None
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = rr.get("block", 132275556)
    e["lastReadWib"] = "2026-11-08 run 0431"
    updated += 1

# --- velocity ---
vel = json.load(open(HF + "run-2026-11-08-0431-velocity.json"))
for row in vel.get("rows", []):
    e = contracts.get(row["name"])
    if e is None:
        continue
    e["currentRatePerMin"] = row.get("ratePerMin")
    e["previousRatePerMin"] = row.get("prevRatePerMin")
    e["velocityRatio"] = row.get("ratioVsPrev")
    e["velocityLegPasses"] = row.get("velocityPasses")
    e["intervalMinutes"] = row.get("intervalMin")
for p in vel.get("passes", []):
    e = contracts.get(p["name"])
    if e is None:
        continue
    if p["name"] == "Zhenzhu":
        e["velocityNote0431"] = (
            "Run 0431: velocity PASS ARTEFAK (bukan promosi): Zhenzhu +4,06e12, ratio 1,88, "
            "tapi kontrak ERC20-claim (freePct None, watchlist-only-pelengkap-scan); "
            "mintedInInterval besar = klaim, bukan NFT; umur UNVERIFIED, xVerified false."
        )
    if p["name"] == "BOT-UNIT":
        e["velocityNote0431"] = (
            "Run 0431: velocity PASS (+100, 2031->2131, ratio 124,4 vs prev 0,029/mnt) — NFT asli "
            "(maxSupply 10000), TAPI freePct None (tanpa free view) + xVerified false -> TIDAK "
            "memenuhi strong lead (butuh >=25% free terverifikasi) maupun kandidat; sudah "
            "early-lead dilaporkan 2026-11-07 ~11:05, tidak dilaporkan ulang, tidak dipromosikan."
        )

# --- HIVE / Bubblebruin / Zapcourier run notes ---
notes0431 = {
    "HIVE Agents": "Run 0431 (blok 132275556): totalSupply 1256 flat vs run 0401 (1256), minted interval 0, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
    "Bubblebruin": "Run 0431 (blok 132275556): totalSupply 2020 (prev 2019), minted interval 1, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
    "Zapcourier": "Run 0431 (blok 132275556): totalSupply 715 flat vs run 0401 (715), minted interval 0, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
}
for n, txt in notes0431.items():
    if n in contracts:
        contracts[n]["runNote0431"] = txt

# --- track_c: record the 6 small movements (all terminal / no transition) ---
tc = snap.get("track_c", {})
for name, txt in {
    "Crack": "Run 0431: 3621->3623, minted-by-user, terminal, tidak berubah status.",
    "ORBITA": "Run 0431: 782->783 (x1e24, +1 share), minted-by-user, terminal, tidak berubah status.",
    "HobnorbAgent": "Run 0431: +1 share (x1e24), terminal, tidak berubah status.",
    "YammerjackAgent": "Run 0431: +1 share (x1e24), terminal, tidak berubah status.",
    "Draco Coin": "Run 0431: +2,5e22, terminal, tidak berubah status.",
    "Ninetailix": "Run 0431: 507->518, age-excluded, terminal, tidak berubah status.",
}.items():
    if name in tc and isinstance(tc[name], dict):
        tc[name]["runNote0431"] = txt

# --- BNAgentFile: website gate VERIFIED + age VERIFIED (closeout parent, run 0431) ---
bna = contracts.get("BNAgentFile")
if bna is not None:
    bna["website"] = "https://bnagent.si"
    bna["websiteEvidence"] = ("Skill.md bnagent.si mencetak kontrak persis "
        "0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1 + registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F "
        "(Leg 2 run 0431, metode G/H; site HTML sendiri 0 hit alamat). Site: 'Mint the free Agent File. "
        "A soulbound ID card, one per wallet, gas only.' Season Oct 25 - Nov 8.")
    bna["firstMintBlock"] = 132139986
    bna["firstMintWib"] = "2026-11-07 11:53:08 WIB"
    bna["firstMintTx"] = "0x4aec93aed974b3423c282163045e28e0e9e889b08d565132f740eb6b1c8d5a9f"
    bna["launchNote"] = ("Launch VERIFIED: first mint 2026-11-07 11:53:08 WIB (blok 132139986, tx "
        "0x4aec93aed974b3423c282163045e28e0e9e889b08d565132f740eb6b1c8d5a9f) via Ankr getLogs "
        "address-filtered binary search, 11 calls, 41 dtk (closeout parent run 0431); umur ~17,5 jam saat run 0431, <=48 jam.")
    bna["totalMinted"] = 5977
    bna["freePctNote"] = ("free% UNVERIFIED: ABI Sourcify exact_match TANPA satu pun free view "
        "(tanpa freeClaimed/FREE_SUPPLY/freeLeft/quote; mint() no-arg; registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F). "
        "totalMinted 5977 (run 0431) tapi tanpa cap tidak bisa dihitung %. Site menyatakan free soulbound one-per-wallet gas-only, "
        "tapi itu klaim site, bukan counter on-chain.")
    bna["userSlotNote"] = ("Slot user UNVERIFIED: tanpa freeClaimed(user)/freeLeft view; balanceOf(user)=0, mintOpen=1 (run 0431). "
        "Tidak pernah di-preview (watchlist-only).")
    bna["status"] = "watchlist-only-free-unverified-2026-11-08"
    bna["baselineNote"] = (bna.get("baselineNote", "") +
        " RUN 0431: website LOLOS (bnagent.si/skill.md cetak kontrak persis + registry) + umur TERVERIFIKASI "
        "~17,5 jam (first mint 2026-11-07 11:53:08 WIB). TETAP watchlist-only: free% UNVERIFIED (tanpa free view di ABI, "
        "tanpa cap) + slot user UNVERIFIED -> kaki strong lead (2) dan (3) gagal; X juga unverified. Soulbound per site "
        "(tidak bisa di-listing). BUKAN early/strong lead, BUKAN kandidat. Tidak dilaporkan.")

snap["last_run_wib"] = "2026-11-08T04:31:00+07:00"
snap["note_0431_scan"] = ("Run 0431 SUKSES window 132274597-132275596 (1000 blok, cap), 122 ERC721 + 1 ERC1155 + "
    "192 ERC-20 mint, 453 NFT mints, 40 Ankr calls, 0 error, SCAN_EXIT=0, ~18,3 mnt. 0 first-seen sejati. "
    "RWD 0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40 muncul 1 mint (registry=True, Sourcify IncompleteRead) — sudah "
    "ditangani hot-leg 0319, tidak dilaporkan ulang. 5c: 27 ERC-20 mint_count>=10, 21 sudah dicek, 6 baru dicek "
    "(0xa3c0e76eEf7ea68F5103c9BfbCcA39FF46be5F3A, 0x0035A93f6F0Fe132adb9f424C54A31AB50bc8a2B, "
    "0xE32Ddf09764C19Ec425Af748fE41853CC55Dc9De, 0x705D186de3c89C28E75FB897b675427Df1204FE0, "
    "0x319dE6b7C953693d1e610B924709eb584f64Bae2, 0x91804C75162bb3C381C439bc6D7521E4aeB1376e — semua Sourcify "
    "not_verified, 0 hit S1/S2). Skipped gap 132273098-132274596 (1.499 blok) untuk backfill; watermark TIDAK "
    "dimajukan (milik backfill; backfill paralel memajukannya ke 132275169 selama run). Preflight PASS 12,3 dtk.")
snap["note_0431_reread"] = ("Run 0431 re-read 458/463 kontrak, blok 132275556, 823,6 dtk. 5 kontrak tanpa alamat "
    "(sama 0401: Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph). Free views None di semua 458 kontrak "
    "(degradasi revert; counter snapshot dipertahankan). 110 kontrak tanpa totalSupply/totalMinted (0401: 105). "
    "Velocity: 2 pass — Zhenzhu ARTEFAK ERC20-claim (+4,06e12, ratio 1,88); BOT-UNIT +100 ratio 124,4 (NFT asli, "
    "tapi freePct None + X unverified -> TIDAK promosi; sudah early-lead 2026-11-07 ~11:05). Sold out 35, set IDENTIK "
    "0401. Age sweep 0 removal (49 kept, 396 launch-unverified — naik dari 384 karena 12 entri baru 0401). "
    "Track-B binanceai TIDAK BERUBAH (launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed(user) 0, "
    "reserves 0/0). Grove freeOpen 0. Track_c: 6 gerakan kecil, semua terminal (Crack 3623, ORBITA 783, HobnorbAgent +1, "
    "YammerjackAgent +1, Draco Coin +2,5e22, Ninetailix 518). Koreksi Leg 3: age-sweep MEM-parse firstMintWib "
    "(field check di first_mint_time) — BOT-UNIT lolos sweep karena umur <=48 jam, bukan karena regex gagal; "
    "catatan firstMintWib BOT-UNIT (02:56:47 WIB) vs firstMintBlock 132124477 (~09:37 WIB per laju blok) tidak konsisten, "
    "dicatat, tidak memengaruhi keputusan (keduanya <48 jam).")
snap["note_0431_discovery"] = ("Run 0431 Boltbook.fun EN 45.065 B / ZH 45.261 B (berotasi dari 0401). Baru: Agentic Miner "
    "($AGM, minter 0x9f45F04A8D6718671cfbeF2740A4eF40cb3337e2, token 0xf197c8b38fa3f3c0764717d4f6d512aa017efe7a, "
    "Sourcify exact_match keduanya) — 'free mint'-nya deposit 0,002 BNB/share yang direfund setelah 24 jam; semua sim "
    "value-0 revert -> BUKAN lead di track mana pun. Juga baru: elepo.ai snapshot post (Fleet/OTV/Bound Agent/Night "
    "Shift); FREEDROP closed 500/500. Route 3: 0 baru (MINTS index byte-identical 0401). Sourcify 5a: 20 kontrak, "
    "0 S1/S2; 5 agent-shape adalah satu factory wave paid spot sale (PineDene, HazelIng, SedgePike, ElmMire, FirHolt) "
    "tanpa free view — bukan lead. Route 6: 0 baru. Bridge TIDAK BERUBAH (sha256 b3f349f1..., 115 kontrak, 7 discarded, "
    "0 promosi). Follow-up: Agent Harvest freeMinted 5.000/5.000 sold out; Bound Agent 10.000/10.000 sold out; OTV kini "
    "berbayar 0,0012 BNB (ketiganya hit indeks basi, bukan di snapshot). BNAgentFile: website evidence LENGKAP "
    "(bnagent.si/skill.md cetak kontrak persis + registry) — lihat note_0431_bna.")
snap["note_0431_bna"] = ("BNAgentFile 0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1 — closeout parent run 0431: (1) Website LOLOS "
    "(bnagent.si/skill.md cetak kontrak persis + registry 0x60B926...22F; metode G/H). (2) Umur TERVERIFIKASI: first mint "
    "2026-11-07 11:53:08 WIB, blok 132139986, tx 0x4aec93aed974b3423c282163045e28e0e9e889b08d565132f740eb6b1c8d5a9f "
    "(Ankr getLogs address-filtered binary search, 11 calls, 41 dtk); umur ~17,5 jam <=48 jam. (3) free% TETAP UNVERIFIED: "
    "ABI exact_match tanpa satu pun free view (tanpa freeClaimed/FREE_SUPPLY/freeLeft/quote; mint() no-arg; registry() = "
    "0x60B926...22F); totalMinted 5977 tanpa cap. (4) Slot user UNVERIFIED (balanceOf 0, mintOpen 1, tanpa per-user free view). "
    "Site menyatakan free soulbound one-per-wallet gas-only. KEPUTUSAN: tetap watchlist-only "
    "(status watchlist-only-free-unverified-2026-11-08) — kaki strong lead (2) dan (3) gagal; BUKAN early/strong lead, "
    "BUKAN kandidat, tidak dilaporkan, tidak di-preview/mint.")
snap["runNote0431_binanceai"] = ("Binanceai tetap refund/failed run 0431: launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0, reserves 0/0 (blok 132275556). pending_claims tetap "
    "kosong; tidak ada laporan ulang.")
snap["note_0431_closeout"] = ("Run 0431: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead baru, 0 track-C "
    "lead/kandidat baru, 0 track-B opening, 0 eksekusi. BNAgentFile naik bukti (website + umur terverifikasi) tapi tetap "
    "watchlist-only karena free% + slot unverified. GLOOP pre-launch tetap FLAG PoW — buka 2026-11-08 19:00 WIB, perlu "
    "keputusan scope parent/user sebelum buka. PER ATURAN DIAM: tidak ada laporan chat dari run ini.")

json.dump(snap, open(SNAP, "w"), indent=1)
print("MERGE-0431 DONE updated_reread=", updated, "contracts=", len(contracts))
