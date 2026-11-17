#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-08 02:01 WIB (run 0201) — CORRECTED.
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
TRUE run-0201 facts (do NOT reuse run-0131 numbers):
- Reread blok 132254789: 444 kontrak + 69 track_c, 105 supply-None (nilai lama
  dipertahankan; None = artefak baca, BUKAN nol). Main reread timed out at
  700 dtk (432/444); catch-up script completed the remaining 12 + 69 track_c.
- Velocity: 1 pass — Alchemister-0xCafEEDDF +28 ratio 1,72 TAPI free% UNVERIFIED
  -> tetap early-lead, 0 promosi. BOT-UNIT (passer 0131) GAGAL run ini (+61, 0,61).
- Sold out: 35, set IDENTIK run 0131, 0 baru.
- Horus AI sellout + KAGENT-b341 refund phase SUDAH dilaporkan + excluded di run
  0131; run ini hanya KONFIRMASI ulang (hopkin-kagent: Horus totalSupply 2000,
  KAGENT phase()=4) — TIDAK dilaporkan ulang, TIDAK di-pop ulang.
- HOPKIN GENESIS: age-excluded (>48h, first-seen blok 131387835 = 2026-11-03
  13:50:18 WIB), registry bytes FALSE, tanpa free view -> BUKAN lead, TIDAK
  ditambah ke snapshot.
- Scan: pre-flight PASS 6,0 dtk (head 132254750); window 132253790-132254789
  (1000 blok, cap); chunk 20/20 selesai (111 NFT: 108 ERC721 + 3 ERC1155;
  234 ERC-20 mint; 40 Ankr calls, 0 error); enrich STALL di 35/111 -> timeout
  700 dtk (SCAN_EXIT=124, partial=True, 34 enriched terselamatkan). Triage:
  0 first-seen baru. 5c: 3 baru dicek, 0 sale-shape hit.
- Age-sweep: 0 dihapus (kept 49 grandfathered; unverified-launch 381).
- Binanceai track-B (blok 132254807): launched 0, failed 1, isRefundPhase 1 —
  IDENTIK run 0131, sudah dilaporkan, tidak dilaporkan ulang. Grove freeOpen 0.
- Watermark TIDAK dimajukan (milik backfill); scan-state hanya ditambah
  note_0201_scan. Discovery note ditambahkan terpisah sesudah subagent
  discovery menyerahkan ringkasannya (finalize ini TIDAK menulisnya).
"""
import json, os

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132254789  # reread block run 0201

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-08-0201-reread.json"))
vel = json.load(open(HF + "run-2026-11-08-0201-velocity.json"))
age = json.load(open(HF + "run-2026-11-08-0201-age-sweep.json"))

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
    c["lastReadWib"] = "2026-11-08 run 0201"
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
    c["runNote0201"] = ("Run 0201 (blok %d): totalSupply %s, minted interval %s, velocity %s."
                        % (BLOCK, c.get("totalSupply"), c.get("mintedInInterval"), c.get("velocityLegPasses")))

tc_updated = 0
for name, rd in reread.get("track_c", {}).items():
    t = snap.get("track_c", {}).get(name)
    if t is None:
        continue
    tc_updated += 1
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if rd.get(f) is not None:
            t[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        t["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        t["freeClaimed_user"] = rd["freeClaimed_user"]
    t["lastReadBlock"] = BLOCK
    t["lastReadWib"] = "2026-11-08 run 0201"

# --- Alchemister: velocity passes, free% unverified -> stays early-lead ---
alch = snap["contracts"].get("Alchemister-0xCafEEDDF")
if alch is not None:
    alch["runNote0201"] = ("Run 0201 (blok 132254789): velocity LOLOS (+28, 5188->5216, rate 0,9543/mnt, "
                           "ratio 1,72 vs prev 0,5539) TAPI free% TETAP UNVERIFIED (tidak ada counter free "
                           "yang terbaca) -> BUKAN strong lead (kaki >=25% tidak terverifikasi) dan BUKAN "
                           "kandidat; umur first mint UNVERIFIED; website UNVERIFIED. Tetap early-lead, "
                           "tidak di-preview/di-mint.")
bu = snap["contracts"].get("BOT-UNIT")
if bu is not None:
    bu["runNote0201"] = ("Run 0201 (blok 132254789): velocity GAGAL (+61, 1800->1861, rate 2,0791/mnt, "
                         "ratio 0,61 vs prev) — passer run 0131 (+110, 9,44x) tidak bertahan; free% "
                         "TETAP UNVERIFIED -> tetap early-lead, 0 promosi.")

# --- Horus AI + KAGENT-b341: already excluded in run 0131; verify presence, do NOT re-pop/re-report ---
excluded = snap.get("excluded", {})
assert "Horus AI" in excluded, "Horus AI missing from excluded (expected from run 0131)"
assert "KAGENT-b341" in excluded, "KAGENT-b341 missing from excluded (expected from run 0131)"

# --- Agent Grove: no change (grove-check run 0201, blok 132257614) ---
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote0201"] = ("Run 0201 (blok 132257614, grove-check): freeOpen 0, freeClaimed(user) false — "
                            "NO CHANGE vs 0101/0131.")

snap["last_run"] = "2026-11-08 run 0201"
snap["last_run_wib"] = "2026-11-08T02:01:00+07:00"
snap["timestamp_wib"] = "2026-11-08 run 0201"
snap["runNote0201"] = (
    "Run 0201 (02:01 WIB): reread blok 132254789, %d kontrak + %d track_c, 105 supply-None "
    "(nilai lama dipertahankan; None = artefak baca, BUKAN nol). Reread utama timeout 700 dtk "
    "(432/444) — catch-up menyelesaikan 12 sisa + 69 track_c. Velocity: 1 pass — "
    "Alchemister-0xCafEEDDF +28 ratio 1,72 TAPI free%% UNVERIFIED -> tetap early-lead, 0 promosi; "
    "BOT-UNIT passer 0131 GAGAL run ini (+61, 0,61). Sold out 35, set IDENTIK run 0131, 0 baru. "
    "Horus AI sellout (totalSupply 2000) + KAGENT-b341 refund phase (phase=4) SUDAH dilaporkan + "
    "excluded di run 0131 — run ini hanya konfirmasi ulang via hopkin-kagent, TIDAK dilaporkan ulang. "
    "HOPKIN GENESIS 0x2728c134... (baru di front page Boltbook run 0131): first-seen blok 131387835 = "
    "2026-11-03 13:50:18 WIB -> umur >48 jam (age-excluded), registry bytes false, tanpa free view -> "
    "BUKAN lead, TIDAK ditambah ke snapshot. Age-sweep: 0 dihapus (kept 49 grandfathered; "
    "unverified-launch 381). Binanceai track-B: launched 0, failed 1, refund phase, blok 132254807 — "
    "identik run 0131, tetap pending, tidak dilaporkan ulang. Grove freeOpen 0 — tanpa perubahan. "
    "TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim)." % (updated, tc_updated)
)
snap["runNote0201_scan"] = (
    "Run 0201 scan: pre-flight PASS 6,0 dtk (head 132254750, ankr_getLogs 50 blok OK 151 logs). Window "
    "132253790-132254789 (1000 blok terbaru, cap), chunk 20/20 selesai: 111 NFT (108 ERC721 + 3 ERC1155) + "
    "234 ERC-20 mint, 40 Ankr calls, 0 error. Enrichment STALL di 35/111 -> timeout 700 dtk "
    "(SCAN_EXIT=124, pola stall berulang); partial=True, 34 kontrak ter-enrich terselamatkan di JSON. "
    "HIVE tidak ada di window. Triage: 0 first-seen baru (enriched 34, known 34); 87 kontrak baru ke "
    "seen file (parent merge). 5c: 36 ERC-20 mint>=10, 33 sudah dicek, 3 baru dicek "
    "(0xCaE7B3fA... mint 21, 0x7d874808... mint 16, 0x64f4F7eF... mint 13; ketiganya not_verified, "
    "no-shape), 0 sale-shape hit; track-c-scan-checked.json +3 (parent merge). WATERMARK TIDAK "
    "DIMAJUKAN run ini (milik backfill; last_scanned_block tetap 132252507 milik backfill)."
)
snap["runNote0201_binanceai"] = (
    "Run 0201 track-B binanceai re-check (blok 132254807): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 0131; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

# --- scan-state: add note only, never touch last_scanned_block ---
st = json.load(open(HF + "onchain-scan-state.json"))
wm_before = st.get("last_scanned_block")
st["note_0201_scan"] = (
    "Run 0201 scan: pre-flight PASS 6,0 dtk (head 132254750). Window 132253790-132254789 (1000 blok), "
    "chunk 20/20: 111 NFT + 234 ERC-20 mint, 40 Ankr calls, 0 error. Enrich STALL 35/111 -> timeout "
    "700 dtk (SCAN_EXIT=124, partial=True, 34 enriched terselamatkan). Triage 0 first-seen; 5c 3 baru "
    "dicek, 0 hit. Watermark TIDAK dimajukan run ini (milik backfill)."
)
with open(HF + "onchain-scan-state.json.tmp", "w") as f:
    json.dump(st, f, indent=1)
os.replace(HF + "onchain-scan-state.json.tmp", HF + "onchain-scan-state.json")

# --- seen merge: recompute from scan output vs FRESH seen file ---
seen = json.load(open(HF + "onchain-scan-seen.json"))
seen_contracts = seen.get("contracts", {})
if not isinstance(seen_contracts, dict):
    seen_contracts = {}
    seen["contracts"] = seen_contracts
scan = json.load(open(HF + "onchain-scan-2026-11-08-0201.json"))
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
added_seen = 0
for c in scan.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen_contracts and a != REG.lower():
        seen_contracts[a] = {"first_seen_block": c.get("first_block"), "first_seen_run": "0201",
                             "first_seen": "run-0201-scan"}
        added_seen += 1
for e in scan.get("erc20_mint_contracts_list", []):
    a = (e.get("address") or "").lower()
    if a and a not in seen_contracts:
        seen_contracts[a] = {"first_seen_block": e.get("first_block"), "first_seen_run": "0201",
                             "first_seen": "run-0201-scan"}
        added_seen += 1
with open(HF + "onchain-scan-seen.json.tmp", "w") as f:
    json.dump(seen, f, indent=1)
os.replace(HF + "onchain-scan-seen.json.tmp", HF + "onchain-scan-seen.json")

# --- track-c-scan-checked merge (+3 from 5c) ---
fivec = json.load(open(HF + "run-2026-11-08-0201-5c.json"))
checked = json.load(open(HF + "track-c-scan-checked.json"))
added_checked = []
new_addrs = [c["address"] for c in fivec.get("checked", [])]
if isinstance(checked, list):
    have = {str(x).lower() for x in checked}
    for a in new_addrs:
        if a.lower() not in have:
            checked.append(a)
            added_checked.append(a)
elif isinstance(checked, dict):
    sub = checked.get("checked")
    if isinstance(sub, list):
        have = {str(x).lower() for x in sub}
        for a in new_addrs:
            if a.lower() not in have:
                sub.append(a)
                added_checked.append(a)
    elif isinstance(sub, dict):
        for a in new_addrs:
            if a.lower() not in sub:
                sub[a.lower()] = {"run": "0201", "verdict": "no-shape"}
                added_checked.append(a)
    else:
        checked["checked"] = list(new_addrs)
        added_checked = list(new_addrs)
with open(HF + "track-c-scan-checked.json.tmp", "w") as f:
    json.dump(checked, f, indent=1)
os.replace(HF + "track-c-scan-checked.json.tmp", HF + "track-c-scan-checked.json")

# --- save snapshot atomically ---
with open(HF + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(HF + "onchain-snapshot.json.tmp", HF + "onchain-snapshot.json")

print(f"FINALIZE-0201 DONE updated={updated} none_supply={none_supply} tc_updated={tc_updated} "
      f"age_remove={len(age['candidates'])} horus/kagent=already-excluded-0131-confirmed "
      f"seen_added={added_seen} checked_added={added_checked} watermark_still={wm_before}")
