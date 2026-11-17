#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 20:01 WIB (run 2001).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json,
adds AURISLE early lead (parent-verified), removes BNB CACHE Server
(age-exclusion), updates BOBBIE counters from leg-3 fresh read.
Read-only inputs; writes snapshot + scan-state note only."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132208595

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2001-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2001-velocity.json"))
age = json.load(open(HF + "run-2026-11-07-2001-age-sweep.json"))

vel_by_name = {row["name"]: row for row in vel["rows"]}
updated = 0
none_supply = 0
for name, rd in reread["reread"].items():
    c = snap["contracts"].get(name)
    if c is None:
        continue
    updated += 1
    if rd.get("totalSupply") is not None:
        c["previousTotalSupply"] = c.get("totalSupply")
        c["totalSupply"] = rd["totalSupply"]
    else:
        none_supply += 1
    for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if rd.get(f) is not None:
            c[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        c["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        c["freeClaimed_user"] = rd["freeClaimed_user"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-07 run 2001"
    vrow = vel_by_name.get(name)
    if vrow:
        c["mintedInInterval"] = vrow["mintedInInterval"]
        c["intervalMinutes"] = vrow["intervalMin"]
        c["currentRatePerMin"] = vrow["ratePerMin"]
        c["previousRatePerMin"] = vrow["prevRatePerMin"]
        c["velocityRatio"] = vrow["ratioVsPrev"]
        c["velocityLegPasses"] = vrow["velocityPasses"]
        if vrow.get("freePct") is not None:
            c["freePctVerified"] = vrow["freePct"]
            c["freePctInference"] = vrow["freePct"]
    c["runNote2001"] = (
        f"Run 2001 (blok {BLOCK}): totalSupply {c.get('totalSupply')} "
        f"(prev {c.get('previousTotalSupply')}), minted interval "
        f"{vrow['mintedInInterval'] if vrow else 'n/a'}, "
        f"velocity {'LOLOS' if (vrow and vrow['velocityPasses']) else 'GAGAL'}"
        f"{' — free% UNVERIFIED, no promotion' if (vrow and vrow['velocityPasses']) else ''}; "
        f"balanceOf(user)={c.get('balanceOf_user', c.get('userBalance'))}; "
        f"free views None (degradasi eth_call, nilai snapshot dipertahankan)."
        if vrow else
        f"Run 2001 (blok {BLOCK}): totalSupply {c.get('totalSupply')}; "
        f"free views None (degradasi eth_call, nilai snapshot dipertahankan)."
    )

# track_c reread
tc_updated = 0
tc_none = 0
for name, rd in reread.get("track_c", {}).items():
    t = snap.get("track_c", {}).get(name)
    if t is None:
        continue
    tc_updated += 1
    if rd.get("totalSupply") is not None:
        t["totalSupply"] = rd["totalSupply"]
    else:
        tc_none += 1
    for f in ("freeMinted", "freeSharesRemaining"):
        if rd.get(f) is not None:
            t[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        t["balanceOf_user"] = rd["balanceOf_user"]
    t["lastReadBlock"] = BLOCK
    t["lastReadWib"] = "2026-11-07 run 2001"

# age exclusions: remove the 1 candidate (BNB CACHE Server, 48.0h)
removed = []
for cand in age["candidates"]:
    name = cand["name"]
    if name in snap["contracts"]:
        entry = snap["contracts"].pop(name)
        removed.append(name)
        snap.setdefault("age_exclusions", []).append({
            "name": name,
            "address": cand["address"],
            "firstMintWib": cand["firstMintWib"],
            "ageHours": cand["ageHours"],
            "supply": entry.get("totalSupply"),
            "maxSupply": entry.get("TOTAL_SERVERS"),
            "freeClaimed": entry.get("freeServersClaimed"),
            "freeCap": entry.get("FREE_SERVERS_TOTAL"),
            "freePctVerified": entry.get("freePctVerified"),
            "status_before": cand.get("status"),
            "removed_run": "2026-11-07 run 2001",
            "removed_wib": "2026-11-07 ~21:00 WIB",
            "reason": f"Umur peluncuran terverifikasi {cand['ageHours']} jam (>48 jam) dan belum sold out "
                      f"(totalSupply {entry.get('totalSupply')}/{entry.get('TOTAL_SERVERS')}, "
                      f"free {entry.get('freeServersClaimed')}/{entry.get('FREE_SERVERS_TOTAL')} = "
                      f"{entry.get('freePctVerified')}%, free window sudah tutup 2026-11-06 20:00:03 WIB); "
                      f"dihapus dari watchlist aktif per aturan umur 48 jam.",
        })

# AURISLE — new EARLY lead (scan first-seen, parent-verified run 2001)
snap["contracts"]["AURISLE"] = {
    "address": "0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D",
    "name": "AURISLE",
    "symbol": "AURISLE",
    "kind": "ERC721",
    "status": "early-lead-2026-11-07",
    "totalSupply": 32,
    "totalMinted": 32,
    "freeMinted": 32,
    "FREE_SUPPLY": None,
    "MAX_SUPPLY": None,
    "freePctVerified": None,
    "freePctNote": "free% UNVERIFIED: FREE_SUPPLY tidak terbaca (Sourcify not_verified; FREE_SUPPLY()/freeLeft() None). freeMinted 32 = totalSupply 32 -> semua mint sejauh ini gratis, tapi % kuota tidak bisa dihitung.",
    "firstSeenBlock": 132208133,
    "firstMintWib": "2026-11-07 20:24:21 WIB",
    "firstMintNote": "First mint TERVERIFIKASI on-chain (scan window 132207681-132208680; timestamp blok via fast_rpc dataseed). Umur TERVERIFIKASI <=48 jam (first mint ~36 mnt sebelum verifikasi parent). Stated launch time proyek BELUM terverifikasi (tidak ada website/post ditemukan).",
    "scanMints": 6,
    "scanMinters": 6,
    "agentShape": "AGENT-SHAPED: bytecode mengandung registry bytes 60b9...022F; AGENT_ID() -> 0x60b9262456de011f7d15a54cdd8c48baaa8b022f (match, verifikasi ulang leg 4 via fast_rpc dataseed1; registry=None di output scan adalah artefak getCode timeout saat enrichment).",
    "owner": "0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2",
    "same_owner_discarded": False,
    "userBalance": 0,
    "balanceOf_user": 0,
    "freeClaimed_user": None,
    "freeClaimed_userNote": "freeClaimed(user)/freeMintedBy(user) gagal dibaca run ini (None = artefak RPC, bukan nol); slot user UNVERIFIED.",
    "quoteNote": "quote(address,uint256[,bool]) + getQuote(address,uint256) semua None (revert/tidak ada fungsi) — quote user UNVERIFIED.",
    "gateNote2001": "Gate website UNVERIFIED (bukan gagal final — early lead): metode A (contract-address search) + C (Sourcify not_verified, tanpa metadata URL) + G (project-name search 'AURISLE') + H (contractURI() None) + I (tokenURI() None) — tidak ada website/X ditemukan. TIDAK PERNAH di-preview/mint sebagai early lead.",
    "xNote": "X UNVERIFIED (opsional, bukan gate).",
    "velocityNote": "Velocity belum dihitung (baru first-seen run ini; baseline dicatat run ini).",
    "lastReadBlock": 132213007,
    "lastReadWib": "2026-11-07 run 2001",
    "runNote2001": "Run 2001: EARLY lead baru dari scan on-chain (first-seen). Dilaporkan sekali ke chat utama sebagai EARLY (bukan kandidat). Naik tier hanya bila kaki strong lead terpenuhi (umur <=48h TERVERIFIKASI via first mint; free% + slot user masih UNVERIFIED).",
}

# BOBBIE counters — leg-3 fresh read (site API), block 132208914
b = snap["contracts"].get("BOBBIE")
if b is not None:
    b["freeAllocated"] = 1602
    b["freePctVerified"] = 80.1
    b["totalMinted"] = 1683
    b["totalMintedNote2001"] = "totalMinted 1683 via /api/mint-window (leg 3, blok 132208914); eth_call totalMinted() gagal run ini (all-None, artefak RPC)."
    b["lastReadBlock"] = 132208914
    b["lastReadWib"] = "2026-11-07 run 2001"

snap["last_run"] = "2026-11-07 run 2001"
snap["last_run_wib"] = "2026-11-07 21:00 WIB"
snap["timestamp_wib"] = "2026-11-07 21:00 WIB"
snap["runNote2001_1107"] = (
    "Run 2001: reread 443/448 kontrak (blok 132208595, 1291 dtk; 104 supply None = degradasi eth_call, "
    "nilai lama dipertahankan; track_c 46/69 all-None, memburuk dari 32/69 run 1931 — artefak RPC); "
    "velocity 2 LOLOS: Horus AI (+67, 1,83/mnt, rasio 2,53x) — free% UNVERIFIED -> 0 promosi; "
    "bridge-0x09bf... adalah artefak wei ERC-20, BUKAN lolos. Pelolos 1931 semua gagal (MORPHA 0,36; "
    "Alchemister 0,34; UNKNOWN-720a 0,37; AgentVOLT 0,62). Sold-out 35 (0 baru); slot berubah 0; "
    "HIVE Agents flat 1256 (+0). Age-exclusion 1 dihapus: BNB CACHE Server (48,0 jam, free 250/777 = 32,18%, "
    "free window sudah tutup). EARLY lead baru: AURISLE 0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D "
    "(first mint 2026-11-07 20:24:21 WIB, 6 mint/6 minter di window, freeMinted 32 = totalSupply 32; "
    "AGENT_ID() match registry; FREE_SUPPLY + quote + slot user UNVERIFIED; website UNVERIFIED) — "
    "dilaporkan sekali sebagai EARLY. Bridge 0 promosi. Scan SUKSES partial=false (preflight PASS 13,2 dtk; "
    "window 132207681-132208680; 135 NFT + 326 ERC-20; 6 first-seen, 1 EARLY lead). Sourcify feed 0 hit; "
    "5c 5 baru dicek 0 hit. Track B: binanceai tetap refund phase (launched 0, failed 1; isRefundPhase/totalShares "
    "gagal baca run ini — artefak RPC), Grove freeOpen 0 — tanpa perubahan. KZMB sharesSold 734-740/1.000, "
    "gate tetap gagal, tidak dilapor ulang. HELM 51,0% pertama kali lewati 50% tapi gate gagal + klaster "
    "same-owner dibuang — bukan kandidat. 0 kandidat, 0 eksekusi — laporan EARLY lead AURISLE + age-exclusion "
    "BNB CACHE Server ke chat utama."
)
snap["runNote2001_1107_scan"] = (
    "Run 2001 scan: preflight PASS 13,2 dtk (head 132208581, 411 log/50 blok); window 132207681-132208680 "
    "(1000 blok terbaru, cap); gap 132188666-132207680 (19.015 blok) untuk backfill; watermark TIDAK dimajukan "
    "(tetap 132188665, milik backfill); chunk 20/20, 0 error, 40 panggilan Ankr, ~28 mnt; 135 NFT (969 mint) + "
    "326 ERC-20-mint; partial=false. 6 first-seen: AURISLE (EARLY lead), Nebula Nomads, FU, Paw Gang "
    "(registry match tapi tanpa free view -> likely paid-only), ETERNAL AGENT NFT, TapeAI Agent TEST. "
    "Seen file +128 -> 10.875. Caveat: Sourcify error massal terulang (101/135 error: 72 IncompleteRead, "
    "17 URLError, 12 RemoteDisconnected; hanya 14 verified) — enrichment terbatas pada registry_bytes_hit."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print(f"contracts updated: {updated} (none_supply {none_supply}); track_c updated: {tc_updated} (none {tc_none})")
print(f"removed age-excluded: {removed}")
print(f"contracts now: {len(snap['contracts'])}; track_c: {len(snap['track_c'])}; age_exclusions: {len(snap['age_exclusions'])}")

# scan-state note (watermark untouched)
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_2001_scan"] = (
    "Run 2001 scan SUKSES (preflight PASS 13,2 dtk; window 132207681-132208680, 1000 blok cap; "
    "135 NFT + 326 ERC-20; 6 first-seen, 1 EARLY lead AURISLE; seen +128 -> 10.875). "
    "Watermark TIDAK dimajukan (tetap 132188665, milik backfill); gap 132188666-132207680 untuk backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)
print("scan-state note_2001_scan written; last_scanned_block still:", st["last_scanned_block"])
