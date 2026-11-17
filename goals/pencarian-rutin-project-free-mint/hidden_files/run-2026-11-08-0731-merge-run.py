#!/usr/bin/env python3
"""Merge run 0731 (ACTUAL) into onchain-snapshot.json. Writes snapshot (backup
first) + run-2026-11-08-0731-merge.json. Appends Dafeiyu + HokiKoi to seen.
Scan PARTIAL (chunks 20/20 OK, enrichment killed 47/165, SCAN_EXIT=124) -> watermark
TIDAK dimajukan (tetap 132293852); skipped gap dicatat di scan-state note."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re_ = json.load(open(f"{BASE}/run-2026-11-08-0731-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-08-0731-velocity.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}
age = json.load(open(f"{BASE}/run-2026-11-08-0731-age-sweep.json"))
age_verify = json.load(open(f"{BASE}/run-2026-11-08-0731-age-verify.json"))
early = json.load(open(f"{BASE}/run-2026-11-08-0731-early-verify.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-08-0731.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261108-0731")
audit = {"run": "0731", "removed": {}, "added": [], "notes": []}

# --- 1. numeric refresh ---
n_upd = 0
for name, d in re_["reread"].items():
    c = snap["contracts"].get(name)
    if not isinstance(c, dict):
        continue
    v = vel_rows.get(name, {})
    prev_ts = c.get("totalSupply")
    cur = d.get("totalSupply")
    if cur is None:
        cur = d.get("totalMinted")
    if cur is not None:
        c["previousTotalSupply"] = prev_ts
        c["totalSupply"] = cur
    if d.get("balanceOf_user") is not None:
        c["balanceOf_user"] = d["balanceOf_user"]
    c["lastReadBlock"] = re_["block"]
    c["lastReadWib"] = "2026-11-08 run 0731"
    if v:
        c["mintedInInterval"] = v.get("mintedInInterval")
        c["currentRatePerMin"] = v.get("ratePerMin")
        c["previousRatePerMin"] = v.get("prevRatePerMin")
        c["velocityRatio"] = v.get("ratioVsPrev")
        c["velocityLegPasses"] = v.get("velocityPasses")
    n_upd += 1
missing = [n for n, c in snap["contracts"].items()
           if isinstance(c, dict) and n not in re_["reread"]]
audit["notes"].append(f"numeric refresh: {n_upd} contracts from 0731 re-read (block {re_['block']}); "
                      f"not re-read this run ({len(missing)}): {missing}")
n_tc = 0
for name, d in re_.get("track_c", {}).items():
    c = snap.get("track_c", {}).get(name)
    if not isinstance(c, dict):
        continue
    for k in ("totalSupply", "balanceOf_user", "freeMinted",
              "freeSharesRemaining", "freeClaimed_user"):
        if d.get(k) is not None:
            c[k] = d[k]
    c["lastReadBlock"] = re_["block"]
    c["lastReadWib"] = "2026-11-08 run 0731"
    n_tc += 1
audit["notes"].append(f"track_c refresh: {n_tc} entries from 0731 re-read (block {re_['block']})")

# --- 2. REMOVE Ghostling + Voltoad (age-excluded >48h, not sold out) ---
for name, first_mint, mark in [
        ("Ghostling", "2026-11-06 07:27:17 WIB", "07:27:17"),
        ("Voltoad", "2026-11-06 07:25:59 WIB", "07:25:59")]:
    c = snap["contracts"].pop(name, None)
    av = age_verify.get(name, {}).get("views", {})
    audit["removed"][name] = {
        "address": (c or {}).get("address"),
        "reason": "age-excluded >48h, not sold out",
        "first_mint_verified": first_mint,
        "age_at_sweep_h": 48.5,
        "fresh_read_block": age_verify.get("block"),
        "fresh_views": av,
        "reread_totalSupply": vel_rows.get(name, {}).get("curSupply"),
        "prev_status": (c or {}).get("status"),
    }
    audit["notes"].append(
        f"REMOVED {name}: first mint {first_mint} (verified on-chain run 0601), age 48.5h at "
        f"sweep run 0731 (>48h); fresh read blok {age_verify.get('block')}: freeClaimed "
        f"{av.get('freeClaimed')}/FREE_SUPPLY {av.get('FREE_SUPPLY')} = "
        f"{round(100*av['freeClaimed']/av['FREE_SUPPLY'],2) if av.get('freeClaimed') is not None and av.get('FREE_SUPPLY') else '?'}%, "
        f"mintOpen {av.get('mintOpen')} -> BELUM sold out, jadi age-excluded + dihapus dari snapshot "
        f"(aturan 48 jam). Status sebelumnya {(c or {}).get('status')} (gate-blocked, sudah dilaporkan "
        f"sekali run 0601).")

# --- 3. ADD Dafeiyu + HokiKoi as early leads (parent-verified) ---
snap["contracts"]["Dafeiyu"] = {
    "address": "0xD8DE64ACB25A87D98F1E170BF082a01427772511",
    "status": "early-lead-reported-2026-11-08-0731",
    "name": "大肥鱼", "symbol": "DFY", "kind": "ERC721",
    "totalSupply": 178, "FREE_SUPPLY": 666, "MAX_SUPPLY": 6666,
    "freeClaimed": None, "freeMinted": None,
    "freePctVerified": None,
    "freePctNote": "UNVERIFIED: freeClaimed() no-arg reverts; freeAgentCount=1 (counter tak dijelaskan, "
                   "TIDAK dipakai sebagai free%). totalSupply 178 vs FREE_SUPPLY 666 TIDAK dipakai "
                   "sebagai % (total supply bukan free counter).",
    "mintOpen": None,
    "userSlotNote": "Slot open by read (freeClaimed(user)=0, mintedBy(user)=0, isFreeAgent(user)=0) - "
                    "NOT preview-verified (early leads are never previewed). isFreeAgent(user)=0: "
                    "semantik eligibility unverified.",
    "firstSeenBlock": 132297424,
    "firstMintWib": "2026-11-08 07:34:11 WIB",
    "firstMintNote": "First mint TERVERIFIKASI parent run 0731: triage scan window 132297297-132298296, "
                     "29 mints / 29 minters, earliest blok 132297424 = 2026-11-08 07:34:11 WIB "
                     "(timestamp via dataseed eth_getBlockByNumber).",
    "agentShapedNote": "AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry persis, "
                       "read parent run 0731); registry bytes di bytecode; Sourcify exact_match "
                       "(verifiedAt 2026-11-08T00:37:02Z) dengan free views FREE_SUPPLY/freeAgent/"
                       "freeAgentCount/freeClaimed/isFreeAgent/isFreeEligible + mint/mintedBy. "
                       "Ditemukan scan + feed Sourcify (cross-check) - dilaporkan SEKALI.",
    "owner": "0x0572f58673a0af3249e0b2ddf4f53a94fa50da11",
    "ownerNote": "Owner TIDAK ada di bridge same_owner_discarded (grep scan-bridge.json run 0731).",
    "legs0731": "Umur TERVERIFIKASI ~0,3 jam (<=48h). Free% UNVERIFIED (bukan strong lead, bukan "
                "kandidat). Velocity: first run (belum ada baseline). X discussion: unverified. "
                "Website gate: belum dicek (tidak ada eksekusi - early lead TIDAK PERNAH di-preview/di-mint).",
    "runNote0731": "Run 0731: EARLY LEAD dilaporkan sekali (scan route 4 first-seen + verifikasi parent + "
                   "Sourcify feed cross-check). totalSupply 178, FREE_SUPPLY 666 (blok 132300321).",
    "lastReadBlock": 132300321,
    "lastReadWib": "2026-11-08 run 0731",
}
audit["added"].append("Dafeiyu 0xD8DE64ACB25A87D98F1E170BF082a01427772511 (early-lead-reported-2026-11-08-0731)")
snap["contracts"]["HokiKoi"] = {
    "address": "0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36",
    "status": "early-lead-reported-2026-11-08-0731",
    "name": "HokiKoi", "symbol": "HKOI", "kind": "ERC721",
    "totalSupply": None, "totalMinted": 21, "freeMinted": 21, "FREE_CAP": 111, "MAX_SUPPLY": 2222,
    "freePctVerified": 18.92,
    "freePctNote": "VERIFIED: freeMinted 21 / FREE_CAP 111 = 18,92% (blok 132300321). Di bawah ambang "
                   "strong lead (25%) dan kandidat (50%). totalSupply() reverts - kontrak memakai totalMinted.",
    "mintOpen": True,
    "userSlotNote": "Slot UNVERIFIED: freeClaimed(address)/mintedBy(address) revert (fungsi tidak ada / "
                    "nama berbeda); tidak ada per-user view yang berhasil dibaca run ini. NOT preview-verified.",
    "firstSeenBlock": 132297641,
    "firstMintWib": "2026-11-08 07:35:48 WIB",
    "firstMintNote": "First mint TERVERIFIKASI parent run 0731: triage scan window 132297297-132298296, "
                     "7 mints / 7 minters, earliest blok 132297641 = 2026-11-08 07:35:48 WIB "
                     "(timestamp via dataseed eth_getBlockByNumber).",
    "agentShapedNote": "agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry persis, "
                       "read parent run 0731); Sourcify verified exact_match (verifiedAt "
                       "2026-11-08T00:15:44Z) dengan free views FREE_CAP/FREE_PER_WALLET/freeCount/"
                       "freeMint/freeMinted + freeMint/mint. Ditemukan scan + feed Sourcify (cross-check) - "
                       "dilaporkan SEKALI. CATATAN: feed script menandai S1=true (mint + PRICE + freeMinted + "
                       "registry) - ARTEFAK, BUKAN track-C: HokiKoi ERC721 NFT (bukan fungible share sale; "
                       "PRICE = harga paid-mint NFT), jadi ditangani sebagai early lead track-A, bukan lead track-C.",
    "owner": "0x13333df46ab3e95f4166370d571e7b73aad06370",
    "ownerNote": "Owner TIDAK ada di bridge same_owner_discarded (grep scan-bridge.json run 0731).",
    "legs0731": "Umur TERVERIFIKASI ~0,3 jam (<=48h). Free 18,92% <25% -> BUKAN strong lead, BUKAN "
                "kandidat. Velocity: first run (belum ada baseline). X discussion: unverified. "
                "Website gate: belum dicek (tidak ada eksekusi - early lead TIDAK PERNAH di-preview/di-mint).",
    "runNote0731": "Run 0731: EARLY LEAD dilaporkan sekali (scan route 4 first-seen + verifikasi parent + "
                   "Sourcify feed cross-check). freeMinted 21/111 = 18,92% (blok 132300321).",
    "lastReadBlock": 132300321,
    "lastReadWib": "2026-11-08 run 0731",
}
audit["added"].append("HokiKoi 0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36 (early-lead-reported-2026-11-08-0731)")

# --- 4. velocity / soldout / slot notes ---
audit["notes"].append(
    "Velocity pass run 0731 (baseline run 0601, blok 132289047 -> 132298298, interval ~69,4 mnt): "
    "Sidecoo +607 (rate 8,7486/mnt, ratio 80,41x), BOT-UNIT +165 (rate 2,3781/mnt, ratio 11,77x) - "
    "keduanya freePct None + slot unverified -> BUKAN strong lead/kandidat (sama seperti run 0701). "
    "Sold-out 35, set IDENTIK run 0601 (0 baru, 0 hilang). Slot change 0.")
audit["notes"].append(
    "Scan route 4 run 0731: PRE-FLIGHT LULUS 5,7 dtk (head 132298155); window 132297297-132298296 "
    "(1000 blok, cap); chunk 20/20 selesai (164 ERC721 + 1 ERC1155 + 245 ERC20-mint, 40 panggilan Ankr, "
    "0 error); enrichment STALL + timeout 780 dtk (47/165, SCAN_EXIT=124) - JSON parsial (46 kontrak "
    "ter-enrich). 119 kontrak ERC721 dalam window TIDAK ter-enrich -> alamatnya hilang run ini (dicatat, "
    "bukan diam-diam); watermark TIDAK dimajukan (tetap 132293852); skipped gap 132293853-132297296 "
    "(3.444 blok; backfill nonaktif). Triage dari JSON parsial: 2 first-seen sejati (Dafeiyu, HokiKoi). "
    "RWD tidak muncul di scan (sudah ditangani hot-leg 0319). Registry address 0x di scan.")
audit["notes"].append(
    "5c: ERC20 mint>=10 total 47; 43 sudah dicek; 4 baru dicek (0xcE30..., 0x4be8..., 0x3d5D..., "
    "0x2ee4...), 0 sale-shape hit; merged ke track-c-scan-checked.json.")
audit["notes"].append(
    "Track-B binanceai: launched 0, failed 1, isRefundPhase 1, totalShares 3110, reserves 0/0 "
    "(blok 132298315) - IDENTIK run 0701, tetap refund phase, tidak dilaporkan ulang. Grove: freeOpen 0, "
    "freeClaimed(user) false (blok 132298788, retry single-call setelah race gagal) - tidak berubah.")
audit["notes"].append(
    "Bridge scan-bridge.json sha b3f349f1 TIDAK berubah (115 kontrak) - 0 temuan pelengkap baru. "
    "Leg 2/3/6: Boltbook EN 45.793 B + ZH 45.775 B (07:41 WIB, 15 alamat, set identik); 0 proyek baru. "
    "Odaily + PANews 0 hit. DappBay tidak dipakai sebagai bukti. Route 5 Sourcify: 20 kontrak feed "
    "(verifiedAt 07:14-07:38 WIB); 0 S1/S2 baru yang valid (HokiKoi S1=true = artefak NFT, lihat "
    "catatan); 3 template paid-mint tanpa free view (0x83A9..., 0x3Bc8..., 0x6A0F...) - log saja.")

# --- 5. run note + last run ---
snap["runNote0731"] = (
    "Run 0731 (2026-11-08 ~07:31-08:00 WIB): 0 kandidat baru, 0 strong lead baru, 0 track-C "
    "lead/kandidat baru, 0 track-B baru. 2 EARLY LEAD BARU dilaporkan sekali: Dafeiyu (DFY) "
    "0xD8DE... - first mint 07:34:11 WIB, AGENT_ID_REGISTRY()=registry, free% UNVERIFIED "
    "(freeClaimed no-arg revert), slot open by read; HokiKoi (HKOI) 0x7405... - first mint 07:35:48 WIB, "
    "agentIdRegistry()=registry, free 21/111=18,92%, slot UNVERIFIED. Keduanya <25% (bukan strong lead). "
    "REMOVED age-excluded: Ghostling (48,5h, free 3825/7000=54,64%) + Voltoad (48,5h, free 4488/7000="
    "64,11%) - belum sold out, dihapus dari snapshot. Velocity pass Sidecoo +607 / BOT-UNIT +165 "
    "(freePct None, bukan promosi). Sold-out 35 identik 0601. Scan parsial (enrichment stall 47/165, "
    "SCAN_EXIT=124); watermark tetap 132293852; skipped gap 3.444 blok. Binanceai refund phase tetap; "
    "Grove tidak berubah; bridge tidak berubah; leg 2/3/6 + Sourcify 0 proyek baru.")
snap["last_run"] = "free-mint-search 2026-11-08 0731 WIB"
snap["last_run_wib"] = "2026-11-08 0731 WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
audit["notes"].append("snapshot written (backup onchain-snapshot.json.bak-20261108-0731); "
                      f"contracts now {len(snap['contracts'])}")

# --- 6. append first-seen to seen file ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
seen.setdefault("contracts", {})["0xd8de64acb25a87d98f1e170bf082a01427772511"] = 132297424
seen["contracts"]["0x74055b4afe2d8c7347e8d4c0fc23e704405f7a36"] = 132297641
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
audit["notes"].append("seen file: appended Dafeiyu (132297424) + HokiKoi (132297641); total contracts now "
                     f"{len(seen['contracts'])}")

# --- 7. scan-state: watermark NOT advanced; record partial + gap ---
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["last_scan_wib"] = "run 0731 2026-11-08 ~07:31-08:00 WIB (PARTIAL: chunks 20/20 OK, enrichment stall 47/165, SCAN_EXIT=124; watermark NOT advanced)"
state["skipped_gap"] = ("132293853-132297296 (3444 blok; window main scan 132297297-132298296 dimulai dari "
                        "head-999 karena gap ke watermark 4303 blok > cap 1000; backfill DINONAKTIFKAN user "
                        "~06:28 WIB, jadi gap ini TIDAK ditutup otomatis; PLUS 119 kontrak ERC721 dalam "
                        "window tidak ter-enrich - alamat hilang run ini)")
state["note"] = ("Scan run 0731 PARTIAL (40 panggilan Ankr, 0 error, partial=true). 2 first-seen: Dafeiyu "
                 "0xD8DE... + HokiKoi 0x7405... (triage dari JSON parsial 46 kontrak). Watermark tetap "
                 "132293852 karena scan gagal di enrichment (aturan: scan gagal -> watermark tidak maju).")
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
audit["notes"].append("scan-state: watermark KEPT at 132293852 (scan partial/failed); gap + note recorded.")

json.dump(audit, open(f"{BASE}/run-2026-11-08-0731-merge.json", "w"), indent=1)
print("MERGE DONE")
print(json.dumps(audit, indent=1)[:3000])
