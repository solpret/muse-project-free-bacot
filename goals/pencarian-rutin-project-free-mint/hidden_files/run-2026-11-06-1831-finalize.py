#!/usr/bin/env python3
"""Finalize run 2026-11-06 1831 WIB (parent).
Merges leg-1 re-read (52 NFT + 18 track_c; leg-1 block 132001310), velocity rows
(41 rows; interval 8.76 min by block delta — caveat: 1801 block_now was fetched
fresh after its leg-1, so the true snapshot gap is larger; only Crack passes
velocity and it is already-minted/paid-second-mint, NOT a candidate),
Boltbook-verify reads (MoonCat/WHALE-A/B/Swarmdrake/Lion's Share/Muster/
PixelTrump/HIVE), first-seen verify reads (Kaiju/Peepers/PropertyAgent/
Goblins/Sprouts), 5c (15 new checked, 0 sale shape), Sourcify feed (0 strict
S1/S2; near-pass Pubzz engine 0x9f10 -> track_c watchlist-only, free pool
unverified + age unverified).
NEW EARLY leads (scan first-seen, Sourcify re-verified by direct curl after
scan enrichment said IncompleteRead): Kaiju, Peepers, Goblins, Sprouts
(AgentGate ABI, costOf(user,1)=0, price 0.002 BNB, free % + age UNVERIFIED);
PropertyAgent (agentRegistry exact + freeQuota 88 + remainingFree 0 -> free
pool EXHAUSTED, costOf 0.001 BNB paid; early lead with dead free leg).
AGE-EXCLUSIONS (verified >48h, not sold out): Swarmdrake (first-seen block
131470551 = 2026-11-04 00:10:50 WIB, age 66h20m; 568/666, free 563/666) and
PixelTrump (first-seen block 131463433 = 2026-11-03 23:17:26 WIB, age 67h14m;
3326/3333, 7 left) -> removed from contracts, moved to excluded, reported once.
Watchlist-only adds (Boltbook-noted, shape unverified): WHALE-A, WHALE-B,
Muster (Sourcify NOT verified; first mints 2026-11-06 16:15/16:22/15:04 WIB).
Scan PARTIAL (timeout 780s cut enrichment at 187/216; chunk phase OK, 40 Ankr
calls, 0 errors, JSON usable). Watermark NOT advanced (backfill owns it;
gap 131989173-132000434 backfill's; main scan covered 132000435-132001434).
0 preview/mint/claim/approve/sign/transaksi.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1831"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1831")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1831")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1831")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1831")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1831-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1831-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1831-velocity.json"))
scan = json.load(open(f"{BASE}/run-2026-11-06-1831-scan.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
bbverify = json.load(open(f"{BASE}/run-2026-11-06-1831-boltbook-verify.json"))
fsverify = json.load(open(f"{BASE}/run-2026-11-06-1831-firstseen-verify.json"))

BLOCK = vel.get("block_now") or 132001310
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None only, match by address) ---
addr2name = {}
for name, e in snap.get("contracts", {}).items():
    if not isinstance(e, dict):
        continue
    a = (e.get("address") or "").lower()
    if a:
        addr2name[a] = name
for name, vals in reread.get("reread", {}).items():
    if not isinstance(vals, dict):
        continue
    a = (vals.get("address") or "").lower()
    key = addr2name.get(a) or (name if name in snap.get("contracts", {}) and isinstance(snap["contracts"].get(name), dict) else None)
    if not key:
        continue
    e = snap["contracts"][key]
    for k, v in vals.items():
        if k in ("address",):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1

# --- 2. Leg-1 track_c re-read merge (match by sale address) ---
sale2name = {}
for name, e in snap.get("track_c", {}).items():
    if not isinstance(e, dict):
        continue
    s = (e.get("sale") or "").lower()
    if s:
        sale2name[s] = name
for name, vals in reread.get("track_c", {}).items():
    if not isinstance(vals, dict):
        continue
    s = (vals.get("sale") or vals.get("address") or "").lower()
    key = sale2name.get(s) or (name if name in snap.get("track_c", {}) and isinstance(snap["track_c"].get(name), dict) else None)
    if not key:
        continue
    e = snap["track_c"][key]
    for k, v in vals.items():
        if k in ("address", "sale"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. Velocity rows merge ---
vel_by_name = {}
for row in vel.get("rows", []):
    vel_by_name[row[0]] = row
for name, row in vel_by_name.items():
    e = snap.get("contracts", {}).get(name)
    if not isinstance(e, dict):
        continue
    if row[4] is not None:
        e["mintedInInterval"] = row[4]
    if row[5] is not None:
        e["currentRatePerMin"] = row[5]
    if row[6] is not None:
        e["previousRatePerMin"] = row[6]
    e["velocityLegPasses"] = bool(row[8])
    e["intervalMinutes"] = vel.get("interval_min")
    e["velocityNote"] = f"Run 1831: view {row[1]}, {row[2]}->{row[3]} (+{row[4]}), rate {row[5]}/mnt vs prev {row[6]} = {row[7]}x, passes={row[8]}"

# --- 4. Boltbook-verify merge (existing entries; non-None only) ---
BB_MERGE = {"MoonCat": "MoonCat", "Swarmdrake": "Swarmdrake",
            "LionsShare": "Lion's Share", "PixelTrump": "Pixel Trump",
            "HIVE": "HIVE Agents"}
for src, key in BB_MERGE.items():
    vals = bbverify.get(src, {})
    e = snap.get("contracts", {}).get(key)
    if not isinstance(e, dict):
        print("BB MERGE SKIP (not in snapshot):", key)
        continue
    for k, v in vals.items():
        if k in ("address", "sourcify", "firstMint", "firstSeenBlockTs"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB

# --- 5. NEW EARLY leads from scan (first-seen verify reads) ---
SCAN_NEW = {
 "Kaiju": {"addr": "0xC6d31279d529F3219575447A7Fbe888E176369a9", "symbol": "KAIJU",
           "window": (11, 11, 132000478), "max": 1812},
 "Peepers": {"addr": "0x318692c7c8DABDf3dAaf4Ed0F1d3646f70070fb9", "symbol": "PEEP",
             "window": (10, 10, 132000454), "max": 1909},
 "Goblins": {"addr": "0x712373aCF9c1C17806fEF4C8687c7F33128D37F3", "symbol": "GOBL",
             "window": (6, 6, 132000531), "max": 1745},
 "Sprouts": {"addr": "0x5B5922F98bA068E7474cC57E2ecbd11c4DB7De79", "symbol": "SPRT",
             "window": (5, 5, 132000547), "max": 1280},
}
for name, meta in SCAN_NEW.items():
    v = fsverify.get(name, {})
    snap["contracts"][f"{name}-1831"] = {
        "address": meta["addr"],
        "name": name,
        "symbol": meta["symbol"],
        "kind": "ERC721",
        "status": "early-lead-2026-11-06-1831",
        "agentShape": "Sourcify VERIFIED (direct curl retry after scan enrichment IncompleteRead): mintWithAgentTokenId, agentIds, agentTokenIdOf, mintedByAgent (AgentGate); NO free-mint fn / free-supply constant in ABI",
        "firstSeenBlock": meta["window"][2],
        "firstSeenWib": "2026-11-06 run 1831 (scan window 132000435-132001434)",
        "windowMints": meta["window"][0],
        "windowMinters": meta["window"][1],
        "totalSupply": v.get("totalSupply"),
        "MAX_SUPPLY": meta["max"],
        "mintOpen": v.get("mintOpen"),
        "balanceOf_user": v.get("balanceOf_user"),
        "mintedBy_user": v.get("mintedBy_user"),
        "costOf_user_1": v.get("costOf_user_1"),
        "PRICE": v.get("price"),
        "freePct": "UNVERIFIED (no free view in ABI/contract)",
        "userSlot": "costOf(user,1)=0 read on-chain (first mint free in this template); balanceOf 0, mintedBy 0 — NOT preview-verified (early leads are never previewed)",
        "age": "UNVERIFIED (totalSupply >> window mints, first mint predates window; launch time not verified)",
        "website": "NOT CHECKED (gate methods not run for early lead; gate applies before execution only)",
        "lastReadBlock": BLOCK,
        "lastReadWib": NOW_WIB,
    }

# PropertyAgent: agent-shaped BUT free pool exhausted at detection
pv = fsverify.get("PropertyAgent", {})
snap["contracts"]["PropertyAgent-1831"] = {
    "address": "0x8bfA8AF37E85Cd5232B57DC1276671769F97Ed41",
    "name": "Property Agent",
    "symbol": "PAGT",
    "kind": "ERC721",
    "status": "early-lead-2026-11-06-1831-free-pool-exhausted",
    "agentShape": "Sourcify VERIFIED (direct curl retry): agentGateOn, agentRegistry, freeQuota, remainingFree, costOf, mint; agentRegistry() on-chain = 552192074493313695968015109214105588393044541999 = registry exact; agentGateOn=1",
    "firstSeenBlock": 132001377,
    "firstSeenWib": "2026-11-06 run 1831 (scan window 132000435-132001434)",
    "windowMints": 7,
    "windowMinters": 5,
    "totalMinted": pv.get("totalMinted"),
    "freeQuota": pv.get("freeQuota"),
    "remainingFree": pv.get("remainingFree"),
    "mintOpen": pv.get("mintOpen"),
    "balanceOf_user": pv.get("balanceOf_user"),
    "mintedBy_user": pv.get("mintedBy_user"),
    "costOf_user_1": pv.get("costOf_user_1"),
    "freePool": "EXHAUSTED at detection: freeQuota 88 = totalMinted 88, remainingFree 0; costOf(user,1)=0.001 BNB (paid) — NO free slot; cannot promote to strong lead/candidate",
    "age": "UNVERIFIED (totalMinted 88 >> 7 window mints, first mint predates window)",
    "website": "NOT CHECKED (gate methods not run for early lead; gate applies before execution only)",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW_WIB,
}

# --- 6. Watchlist-only adds (Boltbook-noted, agent-shape UNVERIFIED) ---
for src, key, note in [
    ("WHALE-A", "WHALE-A", "Boltbook post ~18:30 WIB: 4805/5000 (96,1%); on-chain totalSupply 4820/5000; Sourcify NOT verified; all free views null; first mint blok 131983037 = 2026-11-06 16:15:25 WIB (age ~2h16m, <=48h) — shape unknown, NOT an early lead."),
    ("WHALE-B", "WHALE-B", "Boltbook post ~18:30 WIB: 1437/5000; on-chain totalSupply 1446/5000; Sourcify NOT verified; all free views null; first mint blok 131984017 = 2026-11-06 16:22:46 WIB — shape unknown, NOT an early lead."),
    ("Muster", "Muster", "Boltbook post ~18:29 WIB: totalMinted 1/888, 0 growth in 30 min; on-chain totalMinted 1, MAX_SUPPLY 888; Sourcify NOT verified; all free views null; first mint blok 131973615 = 2026-11-06 15:04:44 WIB — shape unknown, NOT an early lead."),
]:
    v = bbverify.get(src, {})
    snap["contracts"][key] = {
        "address": v.get("address"),
        "status": "watchlist-only-boltbook-noted-2026-11-06",
        "totalSupply": v.get("totalSupply"),
        "totalMinted": v.get("totalMinted"),
        "MAX_SUPPLY": v.get("MAX_SUPPLY"),
        "mintOpen": v.get("mintOpen"),
        "balanceOf_user": v.get("balanceOf_user"),
        "mintedBy_user": v.get("mintedBy_user"),
        "firstMintBlock": (v.get("firstMint") or {}).get("firstMintBlock"),
        "firstMintWib": note,
        "sourcify": (v.get("sourcify") or {}).get("verified"),
        "lastReadBlock": BLOCK,
        "lastReadWib": NOW_WIB,
    }

# --- 7. Track-C watchlist-only: Pubzz sale engine (Sourcify feed near-pass) ---
snap["track_c"]["Pubzz-9f10"] = {
    "sale": "0x9f10c0D8b8E5eFB8706243b1E9336A19E924CCeF",
    "token": "0x26529bc51b13047c3606e888c67e92d4b0037b7c",
    "name": "Pubzz",
    "symbol": "PUBZZ",
    "status": "watchlist-only-unverified-2026-11-06",
    "note": "Sourcify feed 2026-11-06 11:29:37Z (AgentMintEngine.sol): mintFree + freeMinted(address) + registry exact + isAgent(user)=1 + tokenPrice 5e18. FAILS strict S1 (no quote() fn; no free-pool view; freeMintedCount()=0; no FREE_SUPPLY/freeSharesRemaining) -> free pool UNVERIFIED, age UNVERIFIED (verifiedAt is not launch time). NOT a track-C lead; watchlist-only.",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW_WIB,
}

# --- 8. AGE-EXCLUSIONS: Swarmdrake + PixelTrump (verified >48h, not sold out) ---
excluded = snap.setdefault("excluded", {})
for key, addr, sym, note in [
    ("Swarmdrake", "0x3807470b75f332461d8aae40501e83a7e1fe1819", "SWARM",
     "Age-excluded run 1831: first-seen block 131470551 = 2026-11-04 00:10:50 WIB (Ankr block timestamp, verified run 1831) -> first mint <= that, age 66h20m > 48h; totalSupply 568/666, freeClaimed 563/666 (84,5%), 103 left incl. 103 free — NOT sold out. Strong-lead legs were otherwise met (free % verified, slot open, quote 0) but age rule removes regardless of %/velocity."),
    ("Pixel Trump", "0x3054a5530F1852C33bD2749BFAF7155F162A581b", "PTRUMP",
     "Age-excluded run 1831: first-seen block 131463433 = 2026-11-03 23:17:26 WIB (Ankr block timestamp, verified run 1831) -> first mint <= that, age 67h14m > 48h; totalSupply 3326/3333, 7 left — NOT sold out. Site pixeltrump.pages.dev + X @PixelTrumpBSC known, but age rule removes regardless."),
]:
    old = snap.get("contracts", {}).pop(key, None)
    excluded[key] = {
        "address": addr, "symbol": sym, "track": "A",
        "status": "excluded-age-over-48h-2026-11-06",
        "note": note,
        "previousStatus": (old or {}).get("status"),
        "lastTotalSupply": (old or {}).get("totalSupply"),
    }

# --- 9. Seen-file maintenance ---
seen_contracts = seen.setdefault("contracts", {})
added_seen = 0
for c in scan.get("contracts", []):
    a = c["address"].lower()
    if a not in seen_contracts:
        seen_contracts[a] = c.get("first_block")
        added_seen += 1
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- 10. 5c checked merge ---
store = tcchecked
if isinstance(store, dict) and "checked" in store and isinstance(store["checked"], dict):
    checked_dict = store["checked"]
else:
    checked_dict = store if isinstance(store, dict) else {}
    store = {"checked": checked_dict}
added5c = 0
existing_lower = {k.lower() for k in checked_dict.keys()}
for r in checked5c.get("checked", []):
    a = r["address"].lower()
    if a not in existing_lower:
        checked_dict[r["address"]] = {"run": "2026-11-06-1831", "S1": r.get("S1"), "S2": r.get("S2"),
                                       "sourcify": r.get("sourcify"), "mint_count": r.get("mint_count")}
        existing_lower.add(a)
        added5c += 1
json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- 11. Run notes ---
snap["runNote1831_1106"] = (
    "Run 1831: 5 NEW EARLY leads (Kaiju, Peepers, Goblins, Sprouts + PropertyAgent free-pool-exhausted), "
    "2 AGE-EXCLUSIONS (Swarmdrake, PixelTrump — reported once + removed). 0 kandidat, 0 strong lead baru, "
    "0 sellout, 0 pending claim baru/terbuka/gagal, 0 track-C lead/kandidat baru, 0 slot user hilang. "
    "0 preview/mint/claim/approve/sign/transaksi. "
    "Leg 1 (584,6 dtk, block 132001310, interval blok 8,76 mnt vs 1801 — CAVEAT: blok 1801 di-fetch segar "
    "setelah leg-1-nya, jadi gap snapshot-sebenarnya lebih besar; rate/rasio velocity run ini cenderung "
    "terestimasi tinggi): velocity hanya Crack LOLOS (38 mint, 11,65x) — Crack sudah minted-by-user + "
    "second mint BERBAYAR 0,001 BNB, BUKAN kandidat. PassAgentX +19 (<20), Hivefacai +20 tapi prev_rate "
    "None (baseline), SEAT 1,67x tapi +7 (<20). KING Agent totalMinted null run ini (RPC degraded, nilai "
    "lama 942 dipertahankan). CATAI semua view null run ini (degraded, nilai lama dipertahankan). "
    "Mindvolt 683/freeClaimed 683/700 (97,6%), Hivefacai 678/677/700 (96,7%), Quantumfarm 652/651/777 "
    "(83,8%, quote 0) — ketiganya progres saja, gate TETAP FAILED; deadline QF 21:00:37 WIB malam ini, "
    "Soul 23:53:44, StarAgent ~21:26 (belum lewat). Botphoenix 600/599 FLAT — BUKAN sold out, klaim "
    "Boltbook 'SOLD OUT 600/600' tetap salah. HIVE totalSupply 1255; klaim post Boltbook (2 hari lalu) "
    "bahwa free tier TUTUP + quote 0,00015 BNB TIDAK terverifikasi — freeClaimed()/quote() null di 2 run "
    "(fungsi kemungkinan tidak ada di kontrak; BUKAN bukti tutup/buka). "
    "MoonCat 1029/1111 (92,6% total) tapi semua free view null -> free % + slot MASIH UNVERIFIED, "
    "tetap watchlist-only. Lion's Share 580/1450, costOf(user,1)=0, price 0,0002 BNB, free % UNVERIFIED "
    "-> tetap EARLY. Track C tanpa perubahan substansi (FABE launched null run ini — hot-leg 1804: "
    "launched()=0, freeSharesRemaining 2821, share held; SENBAZURU phase 1, launched 0; DROID 622 flat; "
    "IMARS freeMinted null run ini; QAGENT-2 sharesMinted 6702; SAFUAI opened 1). Track B: binanceai "
    "launched 0 + isRefundPhase 1 (sudah excluded, tidak dilaporkan ulang). Bridge 115 kontrak, "
    "7 discarded, 0 not in snapshot. "
    "Sourcify feed: 0 strict S1/S2; near-pass Pubzz engine 0x9f10 -> track_c watchlist-only (free pool "
    "unverified, age unverified); factory wave 7 kontrak template sale (0x3058 dkk, termasuk 0x3058 yang "
    "sudah dinilai bukan track C run 1801) -> bukan track C (tanpa free view di ABI). "
    "Route 3/6: tidak ada lead baru terkonfirmasi (semua item indeks MINTS sudah ada di snapshot; "
    "Razor Agent belum deploy; $SWARM berbayar; Subsonic/BNBmeme/BN Agent File/PIXEL PETS/Skynet >48 jam)."
)
snap["runNote1831_scan_1106"] = (
    "Run 1831: SCAN PARTIAL (timeout 780 dtk memotong enrichment di 187/216; chunk phase SELESAI, "
    "40 panggilan Ankr, 0 error, partial=true, JSON usable). Window 132000435-132001434 (1000 blok, cap 1000). "
    "186 NFT enriched, 471 ERC-20 mint. Pre-flight OK 19,7 dtk (head 132001348, 723 logs/50 blok). "
    "Triase: 6 first-seen sejati (absen seen+snapshot): Kaiju/Peepers/Goblins/Sprouts/PropertyAgent -> "
    "Sourcify VERIFIED via direct curl retry (scan enrichment IncompleteRead — fetch Sourcify scan TIDAK "
    "reliabel) -> 5 EARLY LEAD BARU (PropertyAgent free pool habis); Maneki Neko Coin -> Sourcify NOT "
    "verified -> seen saja. Minerly/Dropnix sudah ada di seen (bukan first-seen). "
    "Watermark TIDAK dimajukan (backfill owns it; backfill di 131989172). Skipped gap 131989173-132000434 "
    "milik backfill (main scan 1801 berakhir 131998466; gap 131998467-132000434 juga backfill). "
    "5c: 55 ERC-20 mint_count>=10, 40 sudah dicek, 15 baru dicek (0 dibuang sampling limit), 0 sale shape "
    "(semua Sourcify not_verified; registry_bytes=true tapi ABI unverified = bentuk unknown). "
    "Seen: +186 kontrak."
)
snap["last_run"] = "2026-11-06 run 1831"
snap["last_run_wib"] = "2026-11-06 run 1831"
snap["timestamp_wib"] = "2026-11-06T19:00:00+07:00"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added_seen={added_seen} added5c={added5c}")
print(f"contracts={len(snap.get('contracts',{}))} track_c={len(snap.get('track_c',{}))} excluded={len(snap.get('excluded',{}))}")
