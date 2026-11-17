#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 19:01 WIB (run 1901).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
Read-only inputs; writes snapshot + run log only.
"""
import json, copy

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132199089

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-1901-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-1901-velocity.json"))
age = json.load(open(HF + "run-2026-11-07-1901-age-sweep.json"))

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
    c["lastReadWib"] = "2026-11-07 run 1901"
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
    c["runNote1901"] = (
        f"Run 1901 (blok {BLOCK}): totalSupply {c.get('totalSupply')} "
        f"(prev {c.get('previousTotalSupply')}), minted interval "
        f"{vrow['mintedInInterval'] if vrow else 'n/a'}, "
        f"velocity {'LOLOS' if (vrow and vrow['velocityPasses']) else 'GAGAL'}"
        f"{' — free% UNVERIFIED, no promotion' if (vrow and vrow['velocityPasses']) else ''}; "
        f"balanceOf(user)={c.get('balanceOf_user', c.get('userBalance'))}; "
        f"free views None (degradasi eth_call, nilai snapshot dipertahankan)."
        if vrow else
        f"Run 1901 (blok {BLOCK}): totalSupply {c.get('totalSupply')}; "
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
    t["lastReadWib"] = "2026-11-07 run 1901"

# age exclusions: remove the 3 candidates
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
            "supply": cand.get("curSupply"),
            "maxSupply": cand.get("maxSupply"),
            "status_before": cand.get("status"),
            "removed_run": "2026-11-07 run 1901",
            "removed_wib": "2026-11-07 ~19:47 WIB",
            "reason": f"Umur peluncuran terverifikasi {cand['ageHours']} jam (>48 jam) dan belum sold out "
                      f"({cand.get('curSupply')}/{cand.get('maxSupply')}); dihapus dari watchlist aktif per aturan umur 48 jam.",
        })

snap["last_run"] = "2026-11-07 run 1901"
snap["last_run_wib"] = "2026-11-07 19:47 WIB"
snap["timestamp_wib"] = "2026-11-07 19:47 WIB"
snap["runNote1901_1107"] = (
    "Run 1901: reread 449/454 kontrak (blok 132199089, 576,6 dtk; 107 supply None = degradasi eth_call, "
    "nilai lama dipertahankan); velocity 4 LOLOS (Alchemister +166 5,44x; UNKNOWN-720a +148 2,47x; "
    "Alchemister-0xCafEEDDF +41 2,37x; AgentVOLT +29 3,50x) — semua free% UNVERIFIED -> 0 promosi; "
    "sold-out 35 (0 baru); slot berubah 0. Age-exclusion 3 dihapus: Kitebots, AgentFounder, AgentPass-Dd3c "
    "(semua ~48,4-48,5 jam, belum sold out). Bridge tidak berubah. Scan partial (preflight PASS 23,5 dtk; "
    "window 132198133-132199132; enrichment stall 83/157); 5 first-seen semuanya same-owner discard "
    "(owner 0x11038f4a...). Sourcify feed 0 hit; 5c 8 dicek 0 hit. Track B: binanceai refund phase, Grove "
    "belum buka — tanpa perubahan. Yokai sold out 1440/1440 (website terverifikasi via tokenURI, tidak relevan); "
    "Saturnode age-excluded 96,9 jam + gate gagal. KZMB sudah dilaporkan 10:45 WIB (gate-blocked), tidak dilapor ulang. "
    "0 kandidat/lead baru, 0 eksekusi — run DIAM (tanpa laporan chat)."
)
snap["runNote1901_1107_scan"] = (
    "Run 1901 scan: preflight PASS 23,5 dtk (head 132199089); window 132198133-132199132 (1000 blok, cap); "
    "gap 132188666-132198132 (9.467 blok) untuk backfill; watermark TIDAK dimajukan (tetap 132188665, milik backfill); "
    "chunk 20/20, 148 ERC721 + 4 ERC1155 + 499 ERC-20-mint; enrichment STALL 83/157 -> timeout 700 dtk "
    "(SCAN_EXIT=124, pola berulang); 82 kontrak ter-enrich, partial=True; 5 first-seen same-owner discard."
)
snap["runNote1901_1107_gate_forwards"] = (
    "Yokai 0x8066D9C5802dA311c274CEd3620817734AD8e985: SOLD OUT 1440/1440 (first mint 2026-11-06 18:10:27 WIB); "
    "website TERGOLONG via tokenURI (yokai-nft.pages.dev mencetak kontrak 3x) tapi tidak relevan karena sold out. "
    "Saturnode 0x6124b3ae64adA7b73581CcD01fEF89e583E8742c: AGE-EXCLUDED (first mint 2026-11-03 18:47:22 WIB, 96,9 jam) "
    "+ gate website GAGAL (metode A/C/D/H/I/J/M tanpa situs; owner = deployer factory-wave Ringgent/Botphoenix/Ghostbot/Mindvolt). "
    "Keduanya bukan lead/kandidat dan tidak masuk snapshot."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print(f"contracts updated: {updated} (none_supply {none_supply}); track_c updated: {tc_updated} (none {tc_none})")
print(f"removed age-excluded: {removed}")
print(f"contracts now: {len(snap['contracts'])}; track_c: {len(snap['track_c'])}; age_exclusions: {len(snap['age_exclusions'])}")
