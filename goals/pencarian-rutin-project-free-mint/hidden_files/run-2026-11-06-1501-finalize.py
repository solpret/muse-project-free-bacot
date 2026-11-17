#!/usr/bin/env python3
"""Finalize run 2026-11-06 1501 WIB (parent).
Merges leg-1 re-read (42 NFT + 18 track_c), 2 early leads (BOBBIE, AgentPad
Agent), 5 first-seen into seen file, 19 5c-checked into track-c store,
scan-state note. Does NOT touch the shared watermark (backfill owns it;
backfill has since advanced it to 131975548). Backs up shared files first.
"""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-06 run 1501"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1501")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1501")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1501")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1501")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1501-reread-lean.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1501-5c-checked.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))

BLOCK = reread["block"]  # 131976886
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

# --- 3. Add 2 early leads to contracts ---
snap["contracts"]["BOBBIE"] = {
    "address": "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207",
    "status": "early-lead-2026-11-06-1501",
    "name": "BOBBIE",
    "symbol": "BOBBIE",
    "kind": "ERC721",
    "agentShape": "Sourcify exact_match verifiedAt 2026-11-06 14:08:08 WIB (94 fns): agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact; FREE_SUPPLY 2000; freeAllocated/freeUsed; mint(uint8,uint256,address,uint256,bytes) payable voucher-gated + quote(address,uint256,bool) + mintStartsAt/mintEndsAt",
    "FREE_SUPPLY": 2000,
    "freeAllocated": 97,
    "freePctVerified": 4.85,
    "totalMinted": 77,
    "totalMintedNote": "ANOMALY (stated, not resolved): totalMinted read 68->70->77 during triage but only ~13 Transfer mints observed in [131900000, window] — likely settleMint/reserved minting without Transfer events; does not change the launch-age verdict",
    "mintStartsAt": "2026-11-06 14:40:09 WIB (on-chain)",
    "mintEndsAt": "2026-11-07 00:40:09 WIB (on-chain)",
    "mintOpen": True,
    "userSlot": {"mintedBy": 0, "freeUsed": 0, "slotOpen": True},
    "freePathNote": "NOT YET VERIFIED: mint() is payable + voucher-gated — the free path may need a voucher; freeAllocated counter exists and moves (94->97). Never previewed/minted (early lead only).",
    "firstSeenBlock": 131971127,
    "firstMintWib": "2026-11-06 14:46:04",
    "firstWindowMintBlock": 131975982,
    "firstWindowMintWib": "2026-11-06 15:22:30",
    "scanWindow": "131975781-131976780",
    "scanMints": 2,
    "scanMinters": 2,
    "launchNote": "VERIFIED <=48h: mintStartsAt() on-chain 2026-11-06 14:40:09 WIB; earliest Transfer mint block 131971127, 14:46:04 WIB (address-filtered Ankr getLogs [131900000, 131975981], 9 prior mints, none before mintStartsAt); age ~45-67 min at scan",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "UNVERIFIED run ini (not checked in scan sub-task). Gate methods A-N to be run if promotion is in view.",
    "baselineNote": "EARLY lead reported once run 1501. Never auto-minted/previewed. Promotes to strong lead only on all 3 strong-lead legs (age + >=25% free quota claimed + user slot open); to candidate only on ALL criteria + safety.",
}
snap["contracts"]["AgentPad Agent"] = {
    "address": "0x71f86082C3b32601f865c63980a9B686e887EAB1",
    "status": "early-lead-2026-11-06-1501",
    "name": "AgentPad Agent",
    "symbol": "AGENT",
    "kind": "ERC721",
    "agentShape": "PARTIAL — free-mint shape PASS, registry FAIL: Sourcify exact_match verifiedAt 2026-11-06 15:26:55 WIB (52 fns): mintFree() nonpayable no-arg; claimFree(uint256) payable; freeCapPerWallet 10; freeMintedBy; mintPaid + paidPriceWei ~0.00101 BNB (paid path exists). NO Agent ID registry reference in ABI or bytecode (registry_bytes False, no agentRegistry/agentId fn). Reported as EARLY per the disjunctive shape test (free-mint function/free-supply constant), with registry linkage explicitly UNVERIFIED.",
    "freeCapPerWallet": 10,
    "mintOpen": True,
    "totalMinted": 6,
    "userSlot": {"freeMintedBy": 0, "slotOpen": True},
    "freePctNote": "UNVERIFIED: freeCapPerWallet is a per-wallet cap, not a total pool — no total free-supply view found; free % cannot be computed yet",
    "firstSeenBlock": 131976627,
    "firstMintWib": "2026-11-06 15:27:20",
    "scanWindow": "131975781-131976780",
    "scanMints": 1,
    "scanMinters": 1,
    "launchNote": "VERIFIED <=48h, genuinely new: address-filtered Ankr getLogs [131900000, 131976626] found 0 prior mints; first mint block 131976627, 15:27:20 WIB (25 s after verification); age ~20 min at triage",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "UNVERIFIED run ini (not checked in scan sub-task). Gate methods A-N to be run if promotion is in view.",
    "baselineNote": "EARLY lead reported once run 1501 (parent decision: free-shape qualifies under the disjunctive early-shape test, registry linkage unverified — stays EARLY, never auto-minted/previewed; promotion needs all 3 strong-lead legs incl. a verifiable free-quota %). Also found by leg 5a Sourcify feed this run (mint-shaped, not a sale shape — no quote fn / free view / agent gate for track C).",
}

# --- 4. Run notes ---
snap["runNote1501_1106"] = (
    "Run 1501: 2 EARLY lead baru (BOBBIE, AgentPad Agent) — dilaporkan sekali run ini. "
    "0 kandidat baru, 0 promosi strong lead, 0 pending claim baru/dibuka, 0 sellout baru, 0 slot user hilang, 0 age-exclusion. "
    "Leg 1 blok 131976886, interval ~52,4 mnt (estimasi 6990 blok x 0,45 dtk/blok) vs run 1431; 42 NFT + 18 track_c dibaca ulang. "
    "Velocity: 0 LOLOS — Crack +119 (0,32x), SEAT +53 (0,66x), Thronemind +9 (2,76x tapi <20 token) GAGAL; "
    "AgentB-c047 +86 dan AgentB-06ec +159 mint cepat tapi free % UNVERIFIED (tanpa free view) + tanpa prev rate -> velocity tidak bisa lolos, tetap EARLY. "
    "WeZards free % terverifikasi 1,8% (45/2500), slot user terbuka, umur ~31 mnt — tetap EARLY. "
    "StarAgent umur ~41,6 jam (first mint est. 2026-11-04 ~21:26 WIB), masih <=48 jam; melewati 48 jam ~21:26 WIB malam ini bila belum sold out; semua view-nya gagal baca run ini (UNVERIFIED, bukan nol). "
    "HIVE totalSupply 1253->1255; sudah minted-by-user 2026-11-02 (grandfathered) — aturan umur tidak menghapus item yang sudah di-mint. "
    "Track B binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0). "
    "Track C tanpa perubahan substansi (DROID freeMinted 617->619; OSK/NIULAI tetap belum dibuka; SENBAZURU opened pulih 1 tapi launched tetap 0; QAGENT-2 pool 6666/6666 flat; IMARS/FABE gagal baca). "
    "Bridge 115 kontrak, 7 same_owner_discarded, 0 not in snapshot. "
    "Leg 2 Boltbook EN pulih via curl -L (322 KB) + ZH; newest tetap 2026-11-05T09:20:52Z, 0 posting baru; MirrorPair 0x27cD34C8A5cc9376030f44d5fEc1a3DCCEeCa2a3 (payable unbind 0.001 BNB, bukan free mint). "
    "Leg 3 sweep 0 proyek baru; MINTS projects.json 0 entri baru (131 proyek). "
    "Leg 5a Sourcify 7 baru vs hot-leg-seen, 0 sale shape (ABI retry-exhausted via urllib, resolved via curl; 0x71f86082... = AgentPad, mint-shaped tapi bukan sale shape). "
    "Leg 6 komplemen 0 (Square/Odaily/PANews 0 mention Agent ID; DappBay tidak terpicu). "
    "RPC degraded sepanjang run (deadline hits, RemoteDisconnected dataseed1, 403 publicnode); semua bacaan null dicatat UNVERIFIED, bukan nol."
)
snap["runNote1501_scan_1106"] = (
    "Run 1501: SCAN SUKSES. Pre-flight OK 8,6 dtk (head 131976746, 300 logs / 50 blok). "
    "Window 131975781-131976780 (1000 blok terbaru), 20/20 chunk + 233/233 enrich, 40 panggilan Ankr, 0 error, ~19,7 mnt, partial=false. "
    "233 NFT (226 ERC721 + 7 ERC1155), 1726 NFT mints, 512 ERC-20 mint. 5 true first-seen: 2 EARLY lead (BOBBIE, AgentPad Agent) + Viking bukan agent-shaped + Niu Lai NFT bukan agent-shaped (totalSupply 21 vs 4 window mints, bulk predates window) + DNA EATER age-excluded (verifiedAt 2026-10-28, ~9 hari). "
    "Watermark TIDAK dimajukan run ini (backfill owns it; backfill sudah ke 131975548 saat finalize). "
    "Skipped gap 131963549-131975780 (12.232 blok) milik backfill. "
    "5c: 57 ERC-20 mint_count>=10, 38 sudah dicek, 19 baru dicek (cap 20, 0 dibuang sampling limit), 0 sale shape (semua Sourcify not_verified; 17/19 registry_bytes=True tapi tanpa ABI)."
)
snap["last_run"] = "2026-11-06 run 1501"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1501: 2 EARLY lead baru (BOBBIE, AgentPad Agent) — dilaporkan sekali. "
    "0 kandidat, 0 promosi, 0 track-B/track-C baru, 0 sellout, 0 age-exclusion. Scan route 4 SUKSES.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 5. Scan-state note (watermark untouched) ---
state["note_1501_scan"] = snap["runNote1501_scan_1106"]
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)

# --- 6. Seen file: add 5 first-seen (lowercase addr -> first-seen block) ---
# Earliest verified mint block where known (BOBBIE 131971127, AgentPad 131976627),
# else window first_block.
targets = {
    "0x3bf121dc4c5a1ba567f3ee801d0e447601726207": 131971127,
    "0x71f86082c3b32601f865c63980a9b686e887eab1": 131976627,
    "0x7776ce863a142f94094eff8a84d21f06138a49fd": 131976253,
    "0x9af2025482d998cf5a1b4235fbdbe8711359f925": 131975873,
    "0xba15f996307190bd738b66e7fe94abdf9a8951fa": 131976297,
}
added = 0
store = seen.setdefault("contracts", {})
for addr, fb in targets.items():
    if addr not in store:
        store[addr] = fb
        added += 1
seen.setdefault("_meta", {})["last_scan_wib"] = NOW_WIB
seen["_meta"]["last_scan_window"] = "131975781-131976780"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["contracts_count"] = len(store)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)

# --- 7. Merge 5c checked into track-c-scan-checked.json ---
# Run 1501 5c file: {"checked": [ {address, ...}, ... ]} — a LIST, unlike run 1431's dict.
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
print(f"contracts_now={len(snap['contracts'])} track_c_now={len(snap['track_c'])} excluded_now={len(snap.get('excluded',{}))}")
print(f"seen_added={added} seen_total={len(store)}")
print(f"5c before={before} after={after} new={len(new_entries)}")
print("backups: onchain-snapshot.json.bak-20261106-1501 (+state/seen/tcchecked)")
