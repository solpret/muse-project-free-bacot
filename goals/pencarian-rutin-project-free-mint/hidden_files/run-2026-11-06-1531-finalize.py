#!/usr/bin/env python3
"""Finalize run 2026-11-06 1531 WIB (parent).
Merges leg-1 re-read (42 NFT + 18 track_c), 0 new early leads, 0 first-seen,
0 newly 5c-checked. Scan SUCCEEDED (1000-block window, watermark untouched,
backfill owns it). Backs up shared files first.
GAP noted: BOBBIE + AgentPad Agent (added to snapshot by run-1501 finalize)
were NOT in leg-1's fixed 42-contract re-read set, so their snapshot entries
keep 1501 values this run; next run's re-read set must be snapshot-driven.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1531"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1531")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1531")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1531")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1531")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1531-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1531-5c-checked.json"))
vel = json.load(open(f"{BASE}/run-2026-11-06-1531-velocity.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))

BLOCK = reread["block"]  # 131981348
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None values only, match by address) ---
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
        if k in ("sale", "address"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. Velocity PASS rows + KING free % (explicit, from velocity.json) ---
INTERVAL_MIN = vel.get("interval_min")
for row in vel.get("rows", []):
    name, view, prev, now, delta, rate, prev_rate, ratio, passed = row
    if name not in snap.get("contracts", {}):
        continue
    e = snap["contracts"][name]
    if prev is not None:
        e["previousTotalSupply"] = prev
    if delta is not None:
        e["mintedInInterval"] = delta
    if INTERVAL_MIN is not None:
        e["intervalMinutes"] = INTERVAL_MIN
    if rate is not None:
        e["currentRatePerMin"] = rate
    if prev_rate is not None:
        e["previousRatePerMin"] = prev_rate
    e["supplyView"] = view
    e["velocityLegPasses"] = passed
    if passed:
        e["velocityNote"] = (
            f"Run 1531: velocity LOLOS ({rate}/mnt vs prev {prev_rate} = {ratio}x, "
            f"+{delta} token); free % UNVERIFIED (tanpa free view) -> tetap EARLY, "
            f"bukan strong lead."
        )
# KING Agent: free % newly verified this run (916/3333)
king = snap["contracts"].get("KING Agent")
if king is not None:
    king["freePctVerified"] = 27.48
    king["velocityNote"] = (
        "Run 1531: free % terverifikasi 27,48% (freeQuota 3333, remainingFree 2417, "
        "totalMinted 916); totalMinted gagal dibaca sebagai velocity (prev null). "
        "Sudah strong-lead-gate-blocked -> perubahan status kaki, bukan promosi baru."
    )

# --- 4. Run notes ---
snap["runNote1531_1106"] = (
    "Run 1531: 0 kandidat baru, 0 promosi strong lead, 0 EARLY lead baru, 0 pending claim baru/dibuka, "
    "0 sellout baru, 0 slot user hilang, 0 age-exclusion. "
    "Leg 1 blok 131981348, interval ~33,5 mnt (4462 blok x 0,45 dtk/blok) vs run 1501; 42 NFT + 18 track_c dibaca ulang. "
    "Velocity: 2 LOLOS pertama kali — AgentB-c047 +153 (4,5719 vs 1,6404 = 2,79x) dan AgentB-06ec +244 (7,2912 vs 3,0329 = 2,40x) — "
    "tetap EARLY karena free % UNVERIFIED (tanpa free view), kaki strong-lead (b) >=25% belum terpenuhi; slot user terbuka, umur ~1,9 / ~1,6 jam. "
    "KING Agent free % kini terverifikasi 27,48% (freeQuota 3333, remainingFree 2417, totalMinted 916, costOf(user,1)=0, mintOpen=1) — sudah strong lead gate-blocked, perubahan status kaki saja, bukan promosi. "
    "WeZards free % 2,4% (freeMinted 60/2500), slot terbuka, tetap EARLY. "
    "StarAgent totalSupply 1599 (pulih dari null), umur ~42,5 jam (first mint est. 2026-11-04 ~21:26 WIB); melewati 48 jam ~21:26 WIB malam ini bila belum sold out. "
    "HIVE totalSupply 1255 flat; sudah minted-by-user 2026-11-02 (grandfathered). "
    "GAP: BOBBIE + AgentPad Agent (early lead run 1501) TIDAK masuk set re-read leg 1 run ini (daftar tetap 42 kontrak pra-1501) — entrinya di snapshot mempertahankan nilai 1501; set re-read run berikutnya harus snapshot-driven. "
    "Track B binanceai tetap refund/failed (launched gagal baca run ini = UNVERIFIED, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0). "
    "Track C tanpa perubahan substansi (IMARS opened=1 tapi pool 300/300 penuh — sudah diketahui; DROID opened 0, freeMinted 619 flat; QAGENT-2/SENBAZURU hanya bacaan pulih). "
    "Bridge 115 kontrak, 7 same_owner_discarded, 0 not in snapshot. "
    "Leg 2 Boltbook EN+ZH via curl (322.064 byte; boltbook.fun kini hanya landing page, API tetap di boltbook.ai); newest tetap 2026-11-05T09:20:52Z, 0 posting baru; MirrorPair 0x27cD34C8A5cc9376030f44d5fEc1a3DCCEeCa2a3 (payable unbind, bukan free mint). "
    "Leg 3 sweep 0 proyek baru; MINTS projects.json 0 entri baru (131 proyek). "
    "Leg 5a Sourcify 20 feed, 0 baru vs hot-leg-seen, 0 sale shape. "
    "Leg 6 komplemen 0 (Square/Odaily/PANews 0 mention Agent ID; DappBay tidak terpicu). "
    "RPC degraded sepanjang run (null = UNVERIFIED, bukan nol)."
)
snap["runNote1531_scan_1106"] = (
    "Run 1531: SCAN SUKSES. Pre-flight OK 10,3 dtk (head 131981412, 313 logs / 50 blok). "
    "Window 131980476-131981475 (1000 blok terbaru, cap 1000), 20/20 chunk + 182/182 enrich, 40 panggilan Ankr, 0 error, ~14 mnt, partial=false. "
    "182 NFT (178 ERC721 + 4 ERC1155), 2750 NFT mints, 478 ERC-20 mint. 0 first-seen (182/182 sudah di seen file 8.266 entri) — 0 EARLY lead baru; "
    "BOBBIE + AgentPad Agent muncul lagi di window tapi sudah seen, tidak dilaporkan ulang. "
    "Watermark TIDAK dimajukan run ini (backfill owns it; 131975548). "
    "Skipped gap 131975549-131980475 (4.927 blok) milik backfill. "
    "5c: 49 ERC-20 mint_count>=10, 49 sudah dicek, 0 baru dicek (cap 20, 0 dibuang sampling limit), 0 sale shape. "
    "Caveat: banyak enrich Sourcify error IncompleteRead run ini (flaky) — registry-bytes + name/symbol tetap lengkap untuk 182 kontrak."
)
snap["last_run"] = "2026-11-06 run 1531"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1531: 0 kandidat, 0 promosi, 0 EARLY lead baru, 0 track-B/track-C baru, "
    "0 sellout, 0 age-exclusion. 2 velocity PASS (AgentB-c047/06ec) tetap EARLY; KING free % terverifikasi 27,48%. Scan route 4 SUKSES.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 5. Scan-state note (watermark untouched) ---
state["note_1531_scan"] = snap["runNote1531_scan_1106"]
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)

# --- 6. Seen file: 0 added; update _meta only ---
store = seen.setdefault("contracts", {})
seen.setdefault("_meta", {})["last_scan_wib"] = NOW_WIB
seen["_meta"]["last_scan_window"] = "131980476-131981475"
seen["_meta"]["last_scan_added"] = 0
seen["_meta"]["contracts_count"] = len(store)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)

# --- 7. Merge 5c checked (0 new this run — no-op) ---
raw = checked5c.get("checked", [])
new_entries = {}
if isinstance(raw, list):
    for item in raw:
        a = (item.get("address") or "").lower()
        if a:
            new_entries[a] = item
elif isinstance(raw, dict):
    new_entries = {k.lower(): v for k, v in raw.items()}
store5c = tcchecked.setdefault("checked", {}) if isinstance(tcchecked, dict) else {}
before = len(store5c)
for a, v in new_entries.items():
    if a not in store5c:
        store5c[a] = v
after = len(store5c)
json.dump(tcchecked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1, ensure_ascii=False)

print(f"merged_nft={merged_nft} merged_trackc={merged_tc}")
print(f"contracts_now={len(snap['contracts'])} track_c_now={len(snap['track_c'])}")
print(f"seen_added=0 seen_total={len(store)}")
print(f"5c before={before} after={after} new={len(new_entries)}")
print("backups: onchain-snapshot.json.bak-20261106-1531 (+state/seen/tcchecked)")
