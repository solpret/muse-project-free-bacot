#!/usr/bin/env python3
"""Merge run 2026-11-09 01:01 WIB. Reloads snapshot fresh (backfill/hot-leg may
have written concurrently), applies reread + triage + scan findings on top.
Writes snapshot + seen file. Never touches the scan-state watermark."""
import json, shutil
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 33.28  # block 132435285 ts 00:48:36 -> block 132439722 ts 01:21:53 WIB

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0101-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0101-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
NEW_BLOCK = rr.get("block")
updated = 0; degraded = 0; vel_pass = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0101 (blok {NEW_BLOCK}, 01:21 WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("ratePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            e["previousTotalSupply"] = prev_sup; e["mintedInInterval"] = minted
            e["intervalMinutes"] = INTERVAL; e["currentRatePerMin"] = rate
            e["previousRatePerMin"] = prev_rate; e["velocityRatio"] = ratio
            e["velocityLegPasses"] = vpass
        e["totalSupply"] = new_sup
        note = f"Run 0101 (blok {NEW_BLOCK}, 01:21 WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 01:21 WIB"
    e["runNote0101_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

tc_updated = 0
for name, e in TC.items():
    if not isinstance(e, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    if r.get("freeMinted") is not None:
        e["freeMinted"] = r["freeMinted"]
    if r.get("totalSupply") is not None:
        e["totalSupply"] = r["totalSupply"]
    e["runNote0101_1109"] = f"Run 0101: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- Pokechain SOLD OUT: early lead reported 2026-11-08, now 15555/15555 ---
removed = []
if "Pokechain" in C:
    e = C.pop("Pokechain")
    s.setdefault("sellouts", []).append({
        "name": "Pokechain", "address": "0x4EF929aF00cB93993c3D01834C4DA79200d31e32",
        "totalMinted": 15555, "MAX_SUPPLY": 15555,
        "evidence": "Sold out terverifikasi on-chain run ini (totalMinted()=15555 = MAX_SUPPLY 15555, baca langsung) + Boltbook EN+ZH 2026-11-09 ~01:12-01:20 WIB (3 node sepakat; 15.067 -> 15.555 dalam ~30 mnt). Kontrak TIDAK PERNAH terverifikasi Sourcify (404).",
        "status_before": e.get("status"), "removed_run": "2026-11-09 run 0101",
        "removed_wib": NOW_STR,
        "reason": "Early lead dilaporkan sekali 2026-11-08; kini sold out -> laporkan sekali + hapus dari snapshot per aturan early-lead."})
    removed.append("Pokechain")

# --- HokiKoi free pool exhausted (minted-by-user; run-log note only) ---
if "HokiKoi" in C:
    C["HokiKoi"]["runNote0101_1109"] = ("Run 0101: FREE_CAP=111, freeMinted=111 -> free pool HABIS (100%). "
        "totalMinted=111. Status tetap minted-by-user-2026-11-08 (user sudah mint); tanpa laporan chat.")
    C["HokiKoi"]["freeMinted"] = 111
    C["HokiKoi"]["FREE_CAP"] = 111

# --- Ninetailix free pool exhausted (already age-excluded; run-log note only) ---
if "Ninetailix" in TC and isinstance(TC["Ninetailix"], dict):
    TC["Ninetailix"]["runNote0101_1109"] = ("Run 0101: freeClaimed()=518/518 = 100% (baca langsung) -> free pool HABIS. "
        "totalSupply 519. Status tetap age-excluded-2026-11-08; tanpa laporan chat.")
    TC["Ninetailix"]["freeClaimed"] = 518

# --- Gryphlume: age-excluded seen-only (never in snapshot, never a lead) ---
s.setdefault("age_exclusions", []).append({
    "name": "Gryphlume", "address": "0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c",
    "firstMintWib": "<=2026-11-02 ~13:30 WIB (mint terverifikasi blok 131192800, walkback masih menemukan mint di blok lebih awal)",
    "ageHours": "~164+",
    "evidence": "Boltbook EN+ZH 2026-11-09 ~01:17 WIB me-recheck (568/996, free 560/796) seolah baru. Verifikasi run ini: seen file first-seen blok 131197799; Ankr getLogs 131196799-131198799 menemukan 1 mint di 131197799; walkback menemukan mint di 131196800-131197799 (2), 131195800-131196799 (5), 131194800-131195799 (10), 131193800-131194799 (9), 131192800-131193799 (21) - first mint LEBIH AWAL lagi. Bacaan segar run ini: totalSupply 575, freeClaimed 567/796=71,2%, MAX 996, mintOpen 1, balanceOf(user)=0. Bytecode mengandung alamat registry (agent-shaped) tapi umur menggugurkan.",
    "supply": 575, "maxSupply": 996, "free": "567/796 = 71,2%",
    "status_before": "seen-only (tidak pernah masuk snapshot / tidak pernah dilaporkan sebagai lead)",
    "removed_run": "2026-11-09 run 0101",
    "reason": "Umur peluncuran TERVERIFIKASI >48 jam (first mint pada/sebelum 2026-11-02 ~13:30 WIB, umur ~164+ jam) dan belum sold out (575/996) -> AGE-EXCLUDED per aturan umur 48 jam; bukan lead/kandidat; tidak dilaporkan ke chat (hanya dicatat, preseden Bonejestra run 0031)."})

# --- AGENT BOTS + AGENT PASS: agent-shaped, watchlist-only (age unverified) ---
C["AGENT BOTS"] = {
    "address": "0xef4Fa905b107A431FcaEB50F1183B712dc3eb9D6",
    "status": "watchlist-only-age-unverified-2026-11-09",
    "name": "AGENT BOTS", "symbol": "ABOT", "kind": "ERC721",
    "totalSupply": 263, "MAX_SUPPLY": 1888, "mintOpen": 1,
    "freeLeft": 1625, "freeClaimed": None, "FREE_SUPPLY": None,
    "firstSeenBlock": 132438844, "scanWindow": "132438824-132439823",
    "scanMints": 1, "scanMinters": 1,
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 01:21 WIB",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Usia peluncuran UNVERIFIED: first mint di window scan run ini (blok 132438844) BUKAN first mint - walkback 3000 blok sebelumnya menemukan 1 mint di 132436824-132437823. Launch time belum terverifikasi.",
    "baselineNote": "BUKAN early lead (first-seen minting TIDAK terverifikasi - ada mint lebih awal). Agent-shaped: Sourcify verified, registry bytes hit, free views freeLeft/freeOf/setFree. Baseline run 0101: totalSupply 263/1888, freeLeft 1625 (=1888-263, semua sisa free), mintOpen 1, balanceOf(user)=0.",
    "runNote0101_1109": "Run 0101: ditambahkan sebagai watchlist-only (age unverified).",
}
C["AGENT PASS"] = {
    "address": "0x6a90E032D50C6FF44608167f7a8634c77ACAeE34",
    "status": "watchlist-only-age-unverified-2026-11-09",
    "name": "AGENT PASS", "symbol": "APASS", "kind": "ERC721",
    "totalSupply": 289, "MAX_SUPPLY": 1111, "mintOpen": 1,
    "freeLeft": 822, "freeClaimed": None, "FREE_SUPPLY": None,
    "firstSeenBlock": 132438935, "scanWindow": "132438824-132439823",
    "scanMints": 1, "scanMinters": 1,
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 01:21 WIB",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Usia peluncuran UNVERIFIED: first mint di window scan run ini (blok 132438935) BUKAN first mint - walkback 3000 blok sebelumnya menemukan 1 mint di 132437824-132438823. Launch time belum terverifikasi.",
    "baselineNote": "BUKAN early lead (first-seen minting TIDAK terverifikasi - ada mint lebih awal). Agent-shaped: Sourcify verified, registry bytes hit, free views freeLeft/freeOf/setFree. Baseline run 0101: totalSupply 289/1111, freeLeft 822 (=1111-289, semua sisa free), mintOpen 1, balanceOf(user)=0.",
    "runNote0101_1109": "Run 0101: ditambahkan sebagai watchlist-only (age unverified).",
}

# --- YAOQIAN: track-C watchlist-only (shape + age unverified) ---
TC["YAOQIAN"] = {
    "sale": "0x75148608e41C4f3A325F4DBC040B2B60CDc772d6",
    "address": "0x75148608e41C4f3A325F4DBC040B2B60CDc772d6",
    "status": "watchlist-only-shape-age-unverified-2026-11-09",
    "name": "YAOQIAN", "symbol": "YAOQIAN",
    "freeClaimed": 56, "sold": 94, "maxShares": 5000, "deadline": 1794205868,
    "deadlineWib": "2026-11-09 13:31 WIB", "phase": 1,
    "ageNote": "Usia peluncuran UNVERIFIED (tidak ada first-share-mint terverifikasi; Sourcify 404; quote null).",
    "shapeNote": "Sale-shape UNVERIFIED: Sourcify 404 (tidak ada ABI); quote(user,1)/quote(1) null; bytecode TIDAK mengandung alamat registry. BUKAN lead (shape tidak lolos S1/S2).",
    "source": "Boltbook EN+ZH 2026-11-09 ~01:20 WIB (free 56/1000, sold 94, tutup 13:31 WIB hari ini).",
    "runNote0101_1109": "Run 0101: ditambahkan sebagai track_c watchlist-only (shape + age unverified); tidak dilaporkan sebagai lead.",
}

# --- seen file: append scan contracts not yet seen ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = json.load(open(f"{BASE}/run-2026-11-09-0101-scan.json"))
added = 0
for c in sc.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen.setdefault("contracts", {})[a] = c.get("first_block") or sc.get("from_block")
        added += 1
seen.setdefault("_meta", {})["note_0101"] = (
    "Run 0101: scan FULL 132438824-132439823 (partial=false, 40 Ankr calls, 0 error, 113 NFT + 267 ERC-20-mint); "
    f"{added} first-seen appended ke seen['contracts'] (AGENT BOTS + AGENT PASS agent-shaped tapi BUKAN early lead - mint lebih awal terverifikasi; "
    "MechaWar/Agent Farm/Panbuff tidak agent-shaped). Skipped gap 132436705-132438823 (2119 blok, watermark 132436704 milik backfill, TIDAK dimajukan).")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- top-level run note ---
s["last_run"] = "0101"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0101 (01:01 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} (01:21:53 WIB, interval 33,28 mnt vs blok 132435285 00:48:36 WIB): "
    f"{updated} kontrak + {tc_updated} track_c, 0 batch_fail, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol). "
    f"Velocity strict: {len(vel_pass)} lolos {vel_pass} - HACKED lolos tapi TIDAK promosi (minted-by-user + free% unverified); 0 promosi lain. "
    "Scan leg FULL (pre-flight OK 14,6 dtk, head 132439751; window 132438824-132439823, 1000 blok cap, 40 Ankr calls, 0 error, partial=false; 113 NFT + 267 ERC-20-mint; "
    "skipped gap 132436705-132438823 (2119 blok); watermark 132436704 TIDAK dimajukan (milik backfill)). "
    "Sourcify feed: 2 baru sejak hot-leg 0109 (0x2fA0, 0xD41c) - detail 404, 0 sale-shape. 5c: 3 baru dicek (0x52e3, 0x643A, 0xc577 - semua Sourcify 404), 0 hit S1/S2. "
    "Boltbook EN+ZH: Pokechain SOLD OUT 15555/15555 (terverifikasi on-chain run ini) - dilaporkan sekali + dihapus dari snapshot; "
    "Gryphlume recheck 568/996 - first mint <=2026-11-02 ~13:30 WIB (umur ~164+ jam) -> age-excluded seen-only, tanpa laporan chat; "
    "YAOQIAN (tutup 13:31 WIB, free 56/1000) -> track_c watchlist-only (shape+age unverified); "
    "Backdoor Pass 0x9c6a... (395->464) BUKAN agent-shaped (Sourcify 404, registry bytes tidak ada, free views null) -> bukan lead, hanya dicatat; "
    "Bonejestra 572/963 (sudah age-excluded); NUSA flat 245/560 (gate FAILED tetap); AgentVOLT B drain 459,61M VOLT + frozen 5.045 (watchlist-only, user bal 0, hanya dicatat); "
    "ZSEAT claim ZENA open 363/2000 (user bal 0, bukan entitlement user); helm.ai 553/555 (2 tersisa, gate FAILED tetap); Saturnode 3798/4000 (94,2%, age unverified, velocity GAGAL). "
    "Scan first-seen baru: AGENT BOTS + AGENT PASS agent-shaped tapi BUKAN early lead (mint lebih awal di 3000 blok sebelum window) -> watchlist-only; "
    "MechaWar/Agent Farm/Panbuff tidak agent-shaped -> seen-only. "
    "HokiKoi free pool HABIS 111/111 (minted-by-user, tanpa laporan); Ninetailix free pool HABIS 518/518 (sudah age-excluded, tanpa laporan). "
    "Binanceai tetap refund phase (grove-check 01:01 WIB blok 132437034: launched=0, failed=1, isRefundPhase=1). Bridge: 116 kontrak, 0 baru. "
    "Web sweep EN+ZH + route 6: 0 kandidat baru (semua hasil 24 Okt-7 Nov: PTAH, AgentForge, Pixel Fox, PocketDragons, NOVRA free pool sudah habis 8 Nov, AGENT MAO paused, HOPKIN). "
    "0 kandidat, 0 strong lead baru, 0 early lead baru, 0 auto-mint.")
s["runNote0101_1109"] = s["last_run_note"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE updated={updated} degraded={degraded} tc={tc_updated} vel_pass={vel_pass} removed={removed} seen_added={added}")
print("contracts now:", len(s["contracts"]), "track_c now:", len(s["track_c"]))
