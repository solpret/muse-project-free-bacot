#!/usr/bin/env python3
"""Merge run 0931 (2026-11-08) results into snapshot / seen / scan-state / tc-checked.
Tailored for this run: generic reread+velocity update, ONE new entry
(OinkHash Pigs 0x1a904Da7, early lead), watermark + seen + 5c merge.
Does NOT re-apply run 0831 new entries (already in snapshot; their gate-failed
statuses from run 0831 must not regress). Preserves all existing snapshot keys.
Run once."""
import json, datetime

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = datetime.timezone(datetime.timedelta(hours=7))
NOW = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
rr = json.load(open(f"{HF}/run-2026-11-08-0931-reread.json"))
vv = json.load(open(f"{HF}/run-2026-11-08-0931-velocity.json"))
scan = json.load(open(f"{HF}/onchain-scan-2026-11-08-0931.json"))
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
state = json.load(open(f"{HF}/onchain-scan-state.json"))
tc = json.load(open(f"{HF}/track-c-scan-checked.json"))
f5 = json.load(open(f"{HF}/run-2026-11-08-0931-5c.json"))

REREAD_BLOCK = rr["block"]
contracts = snap["contracts"]

# ---- 1. reread + velocity update for existing entries ----
vel_by_addr = {}
for row in vv.get("rows", []):
    a = (row.get("address") or "").lower()
    if a:
        vel_by_addr[a] = row

updated = 0
for key, entry in contracts.items():
    row = rr["reread"].get(key)
    if row:
        if row.get("totalSupply") is not None:
            entry["totalSupply"] = row["totalSupply"]
        for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
                  "MAX_SUPPLY", "mintOpen", "freeClaimed_user", "balanceOf_user"):
            if row.get(f) is not None:
                entry[f] = row[f]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 0931"
        updated += 1
    vrow = vel_by_addr.get((entry.get("address") or "").lower())
    if vrow:
        cur = vrow.get("curSupply")
        if cur is not None:
            entry["previousTotalSupply"] = vrow.get("prevSupply")
            entry["currentRatePerMin"] = vrow.get("ratePerMin")
            entry["previousRatePerMin"] = vrow.get("prevRatePerMin")
            entry["velocityRatio"] = vrow.get("ratioVsPrev")
            entry["run0931_velocity"] = (
                f"Run 0931 (blok {REREAD_BLOCK}, interval {vrow.get('intervalMin')} mnt): "
                f"{vrow.get('prevSupply')}->{cur} (+{vrow.get('mintedInInterval')}, "
                f"{vrow.get('ratePerMin')}/mnt vs prev {vrow.get('prevRatePerMin')} = "
                f"{vrow.get('ratioVsPrev')}x) -> velocity "
                f"{'LOLOS' if vrow.get('passes') else 'GAGAL'}."
            )
        else:
            entry["run0931_velocity"] = (
                f"Run 0931 (blok {REREAD_BLOCK}): no fresh supply read "
                f"(degradasi RPC) - nilai lama dipertahankan, BUKAN perubahan state."
            )
print("reread-updated entries:", updated)

# ---- 1b. track_c fresh reads (totalSupply + lastRead only) ----
tc_updated = 0
for key, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    row = rr.get("track_c", {}).get(key)
    if row and row.get("totalSupply") is not None:
        entry["totalSupply"] = row["totalSupply"]
        entry["lastReadBlock"] = REREAD_BLOCK
        entry["lastReadWib"] = "2026-11-08 run 0931"
        tc_updated += 1
print("track_c updated:", tc_updated)

# ---- 2. new entry: OinkHash Pigs 0x1a904Da7 (EARLY LEAD, scan first-seen) ----
contracts["0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B"] = {
    "address": "0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B",
    "status": "early-lead-reported-2026-11-08",
    "name": "OinkHash Pigs",
    "symbol": "OINK",
    "kind": "ERC721",
    "totalSupply": 1017,
    "freeClaimed": None,
    "FREE_SUPPLY": None,
    "freePctVerified": None,
    "mintOpen": 1,
    "mintPrice": 1500000000000000,
    "userBalance": 0,
    "freeClaimed_user": 0,
    "userSlotNote": "Slot open by read: freeClaimed(user)=false, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed).",
    "firstSeenBlock": 132312506,
    "scanWindow": "132312491-132313490",
    "scanMints": 38,
    "scanMinters": 38,
    "lastReadBlock": REREAD_BLOCK,
    "lastReadWib": "2026-11-08 run 0931",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 132311872, 2026-11-08 09:22:34 WIB (Ankr getLogs address-filtered from block 132300000; 1.013 from-zero logs since then, 872 in block 132311000-132311999 - burst awal). Age verified <=48h. No project-stated launch time found; Sourcify verifiedAt 2026-11-08T02:18:55Z (verification time, NOT launch time). First-seen by this job in run 0931 via on-chain scan.",
    "baselineNote": "EARLY lead reported once 2026-11-08 run 0931. Never auto-minted/previewed. Agent-shape verified: Sourcify exact_match ABI 56 fns (AGENT_ID, FREE_HASH, freeClaimed(address), freeMint() no-arg, isFree(uint256), mint/mintOpen/mintPrice) + registry-bytes hit. Owner 0x615c47be32512f42ff3b8cd1f5f688e93fe3a929 - SAME owner as OinkHash Pigs f710 (early lead run 0831) + Ink Koi; NOT in same-owner-discards. Second new OinkHash contract today (project migration 'Moved to new contracts on Nov 8, 2026'). free% UNVERIFIED: no global free counter readable (totalMinted/freeMinted/FREE_SUPPLY/MAX_SUPPLY/isFree()/freeLeft() all revert on eth_call). Website oinkhash.fun does NOT print this exact contract (same as f710) -> gate UNVERIFIED for future promotion. Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety.",
    "freePctNote": "UNVERIFIED: totalSupply 1017, mintPrice 0.0015 BNB (paid lane), freeMint() no-arg exists but no readable global free counter; freeClaimed(user)=false, balanceOf(user)=0.",
    "runNote0931": "Run 0931: EARLY LEAD (temuan scan, first-seen). First mint 09:22:34 WIB, 38 mints/38 minters di window scan, totalSupply 1017. Dilaporkan sekali sebagai EARLY, TIDAK di-preview/di-mint.",
}

# ---- 3. run notes ----
snap["runNote0931"] = (
    "Run 0931 (2026-11-08, blok reread 132313421, 744,9 dtk): reread 470 kontrak + 70 track_c; "
    "velocity 0 pass, 0 promotable; soldOut 35 (set sama dengan run 0831, tanpa sellout baru); "
    "slotChanged 0. Movers terbesar semua same-owner-discarded / early-lead free%-unverified "
    "(Vesperfang +21 free% 56,4; Dronegent +26; Gourdmare +21; Rimeagent +91 free% 16,62; "
    "Kelpiare +30; Neptivane +29) -> TIDAK promosi. Age-sweep: remove=0. "
    "Track B binanceai tidak berubah (launched=0, failed=1, isRefundPhase=1, tokenClaimed_user=0, "
    "balance 0; sudah dilaporkan run 1701 2026-11-07). Cabinette totalSupply 2.750 (+168), "
    "MECHFARM-1fab 2.187 (+25) - keduanya tetap gate-failed (sudah dilaporkan run 0831), tidak berubah. "
    "OinkHash Pigs f710 totalSupply 853 (+12), tetap early-lead (free% unverified). "
    "Paw Gang totalSupply tidak terbaca segar run ini (degradasi RPC, nilai lama dipertahankan); "
    "Boltbook: totalMinted ~1.526/3.333 (~45,8%), free% unverified -> tetap early-lead-2026-11-07, "
    "belum strong lead. Kappaxis totalSupply 1.221 (sesuai post Boltbook 1.221/2.308) tapi free views "
    "None -> free% UNVERIFIED, tetap watchlist-only. HACKAG 4.362/5.555 (same-owner-discarded). "
    "AGOAT: alamat kontrak TIDAK ditemukan di post Boltbook maupun pencarian web -> unverified, "
    "tidak masuk snapshot. Feed Sourcify: 4 kontrak baru sejak hot-leg 0924, semuanya gagal S1/S2 "
    "(mint+quote, tanpa free view, tanpa registry). Bridge: 115 kontrak, mtime 2026-11-06 02:48 UTC, "
    "tidak ada entri baru. Odaily newsflash: tidak ada item Agent-ID free-mint. "
    "EARLY LEAD x1 (temuan scan): OinkHash Pigs 0x1a904Da7 (first mint 09:22:34 WIB, 38 mints/38 minters "
    "di window, agent-shaped, free% unverified, slot terbuka). BAHUANG 0x0524d947 (1 mint, Sourcify "
    "not_verified, tanpa registry/free) -> bukan agent-shaped, tidak masuk snapshot, tidak dilaporkan.")
snap["runNote0931_scan"] = (
    "Run 0931 SCAN SUKSES (partial=false): pre-flight OK 10,4 dtk (head 132313444, 403 logs/50 blok). "
    "Window 132312491-132313490 (1000 blok, cap), 20/20 chunk + 152/152 enrich, 40 panggilan Ankr, 0 error. "
    "152 NFT + 235 ERC-20 mint. True first-seen: 2 (OinkHash Pigs 0x1a904Da7 = EARLY lead; "
    "BAHUANG 0x0524d947 bukan agent-shaped). Watermark 132308469 -> 132313490. "
    "Skipped gap 132308470-132312490 (backfill dinonaktifkan user). "
    "5c: 235 ERC20, 38 mint_count>=10, 37 sudah dicek, 1 baru dicek, 0 dibuang sampling limit, "
    "0 hit S1/S2 (0x75C71Cd8 not_verified, registry_bytes=True tapi tanpa ABI).")
snap["last_run"] = "free-mint-search 2026-11-08 0931 WIB"

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]))

# ---- 4. seen file: append all scan contracts ----
added = 0
for c in scan["contracts"]:
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen["contracts"][a] = c.get("first_block")
        added += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)
print("seen appended:", added, "| seen total:", len(seen["contracts"]))

# ---- 5. scan-state watermark ----
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = NOW
state["ankr_calls"] = scan.get("ankr_calls")
state["errors"] = scan.get("errors", [])
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = len(scan.get("erc20_mint_contracts_list", []))
state["skipped_gap"] = "132308470-132312490 (backfill dinonaktifkan user; window scan hanya 1000 blok terbaru)"
state["note_0931_scan"] = snap["runNote0931_scan"]
json.dump(state, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("watermark ->", scan["to_block"])

# ---- 6. track-c-scan-checked merge (5c) ----
checked_list = {a.lower() for a in tc.get("checked", [])}
top_keys = {k.lower() for k in tc.keys() if k != "checked"}
merged = 0
for c in f5["checked"]:
    a = c["address"]
    if a.lower() in checked_list or a.lower() in top_keys:
        continue
    tc[a] = {"source": "run-2026-11-08-0931-5c", "status": "checked-not-sale-shape",
             "mint_count": c.get("mint_count"),
             "note": f"S1=False S2=False (Sourcify {c.get('sourcify')}, registry_bytes={c.get('registry_bytes')}, fns={c.get('fns')})"}
    merged += 1
json.dump(tc, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)
print("tc-checked merged:", merged)
print("MERGE DONE")
