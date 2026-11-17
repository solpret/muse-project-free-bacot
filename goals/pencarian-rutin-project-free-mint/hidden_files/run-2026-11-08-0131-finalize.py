#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-08 01:31 WIB (run 0131).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
- 0 kandidat, 0 strong-lead baru, 0 early-lead baru, 0 track-C lead/kandidat baru.
- 1 free-pool SELLOUT baru: Horus AI (totalSupply 2000 = FREE_SUPPLY 2000) -> excluded.
- KAGENT-b341 -> excluded (refund phase=4, SUDAH dilaporkan hot-leg 0139; tidak dilaporkan ulang).
- HOPKIN GENESIS: age-excluded (>48h, first-seen blok 131387835 = 2026-11-03 13:50 WIB), TIDAK ditambah ke snapshot.
- BOT-UNIT: velocity lolos lagi (ratio 9,44) TAPI free% UNVERIFIED -> tetap early-lead.
- Watermark TIDAK dimajukan (milik backfill); scan-state hanya ditambah note_0131_scan.
- Merge seen (95 baru dari scan window) + track-c-scan-checked (+2 dari 5c).
"""
import json, os

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132250877  # reread block

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-08-0131-reread.json"))
vel = json.load(open(HF + "run-2026-11-08-0131-velocity.json"))
age = json.load(open(HF + "run-2026-11-08-0131-age-sweep.json"))

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
    c["lastReadWib"] = "2026-11-08 run 0131"
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
    c["runNote0131"] = ("Run 0131 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-08 run 0131"

# --- BOT-UNIT: velocity passes, free% unverified -> stays early-lead ---
bu = snap["contracts"].get("BOT-UNIT")
if bu is not None:
    bu["runNote0131"] = ("Run 0131 (blok 132250877): velocity LOLOS lagi (+110, 1800->1910, rate 3,38/mnt, "
                         "ratio 9,44 vs prev 0,36) TAPI free% TETAP UNVERIFIED (tidak ada counter free yang terbaca; "
                         "mintMode=0 FirstFree per-wallet, bukan pool global) -> BUKAN strong lead (kaki >=25% tidak "
                         "terverifikasi) dan BUKAN kandidat; umur first mint 2026-11-07 02:56:47 WIB (~22,9 jam, <=48 jam); "
                         "website https://bot-unit.xyz terverifikasi; slot user terbuka (quote 0, hasFreeMint True, "
                         "balanceOf(user)=0). Tetap early-lead, tidak di-preview/di-mint. Pola sama seperti run 1701.")

# --- Horus AI: free pool SOLD OUT -> excluded (lapor sekali via run ini) ---
horus = snap["contracts"].pop("Horus AI", None)
snap.setdefault("excluded", {})["Horus AI"] = {
    "address": "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E",
    "track": "A",
    "status": "excluded-sold-out-free-pool-2026-11-08",
    "note": ("Run 0131: free pool HABIS — totalSupply 2000 = FREE_SUPPLY 2000 (reread blok 132250877; "
             "verifikasi segar parent run-2026-11-08-0131-hopkin-kagent.json: totalSupply 2000, FREE_SUPPLY 2000, "
             "MAX_SUPPLY 10000, mintOpen 1). Boltbook 01:45 WIB masih 1.998/2.000; tutup ~01:52 WIB. "
             "User balanceOf=0 (tidak pernah mint; free path PARTIAL/UNVERIFIED sejak awal, early lead saja). "
             "Dilaporkan SEKALI sebagai perubahan (sellout) di run ini; dihapus dari kontrak aktif."),
    "prev_status": (horus or {}).get("status"),
    "firstMintWib": (horus or {}).get("firstMintWib"),
}

# --- KAGENT-b341: refund phase -> excluded (SUDAH dilaporkan hot-leg 0139; tidak dilaporkan ulang) ---
kag = snap["contracts"].pop("KAGENT-b341", None)
snap.setdefault("excluded", {})["KAGENT-b341"] = {
    "address": "0xb34105002B19EF0ce43B59011fE848df5c8B174f",
    "track": "C/B-claim",
    "status": "excluded-refund-phase-2026-11-08",
    "note": ("Run 0131: phase()=4 Refunds terverifikasi on-chain parent (~02:00 WIB, "
             "run-2026-11-08-0131-hopkin-kagent.json) + hot-leg 0139 blok 132250879; launched=0, sold 44/10000, "
             "freeClaimed 3748/4444 (696 slot gratis tak terpakai). User: balance 50.000 KAGENT, "
             "validFreeAllocation=0, paidShares=0 -> TIDAK ada refund untuk user (refund hanya 44 pembeli berbayar); "
             "claimFree() sudah tidak bisa (phase!=Minting). SUDAH dilaporkan hot-leg (MEMORY.md) + dihapus dari "
             "pending-swaps.json 01:57 WIB (9->8 entri) -> run ini TIDAK melaporkan ulang, hanya memindahkan dari "
             "kontrak aktif ke excluded. 50.000 KAGENT tetap di wallet agent."),
    "prev_status": (kag or {}).get("status"),
}

# --- Agent Grove: no change ---
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote0131"] = ("Run 0131 (blok 132249107, grove-check): freeOpen 0, freeClaimed(user) false — "
                            "NO CHANGE vs 0101.")

snap["last_run"] = "2026-11-08 run 0131"
snap["last_run_wib"] = "2026-11-08T01:31:00+07:00"
snap["timestamp_wib"] = "2026-11-08 run 0131"
snap["runNote0131"] = (
    "Run 0131 (01:31 WIB): reread blok 132250877, %d kontrak + %d track_c, 652,7 dtk, %d supply-None "
    "(nilai lama dipertahankan). Velocity: 1 pass — BOT-UNIT +110 ratio 9,44 TAPI free%% UNVERIFIED -> tetap "
    "early-lead, 0 promosi. 1 free-pool SELLOUT baru: Horus AI totalSupply 2000 = FREE_SUPPLY 2000 "
    "(Boltbook 01:45 WIB masih 1.998/2.000; user tidak memegang) -> dilaporkan sekali + excluded. "
    "KAGENT-b341 masuk phase 4 Refunds (verifikasi on-chain parent + hot-leg 0139; user tidak dapat refund, "
    "50.000 KAGENT tetap di wallet; sudah dilaporkan hot-leg + dihapus dari pending-swaps) -> dipindah ke "
    "excluded, TIDAK dilaporkan ulang. HOPKIN GENESIS 0x2728c134... (baru di front page Boltbook): first-seen blok "
    "131387835 = 2026-11-03 13:50 WIB -> umur >48 jam (age-excluded), registry bytes false, tanpa free view -> "
    "BUKAN lead, TIDAK ditambah ke snapshot. Age-sweep: 0 dihapus (kept 49 grandfathered; unverified-launch 383). "
    "Binanceai track-B: launched 0, failed 1, refund phase, blok 132251024 — identik 1701-0101, tetap pending, "
    "tidak dilaporkan ulang. Grove freeOpen 0 — tanpa perubahan. TIDAK ada eksekusi oleh run ini "
    "(tidak ada mint/preview/claim)." % (updated, tc_updated, none_supply)
)
snap["runNote0131_scan"] = (
    "Run 0131 scan: pre-flight PASS (head 132250869, ankr_getLogs 50 blok OK 354 logs, 2,5 dtk). Window "
    "132249931-132250930 (1000 blok terbaru, cap), 135 NFT (133 ERC721 + 2 ERC1155) + 267 ERC-20 "
    "mint, 40 Ankr calls, 0 error, partial=False. HIVE tidak ada di window. Triage: 0 first-seen baru "
    "(enriched 135, known 134); 95 kontrak baru ke seen file (parent merge). 5c: 38 ERC-20 mint>=10, 36 sudah "
    "dicek, 2 baru dicek (0x8887D493... mint 22, 0xcfEdF85c... mint 12; keduanya not_verified, no-shape), "
    "0 sale-shape hit; track-c-scan-checked.json +2 (parent merge). WATERMARK TIDAK DIMAJUKAN run ini "
    "(milik backfill; last_scanned_block tetap milik backfill)."
)
snap["runNote0131_discovery"] = (
    "Run 0131 discovery (subagent): Boltbook boltbook.fun EN 46.791 B / ZH 47.002 B (HTTP 200), 16 alamat mentah, "
    "11 unik, EN=ZH identik, 0 free-share keyword hit. Klasifikasi: Horus/KAGENT/BOLT/ONES di snapshot; FREEDROP "
    "excluded same-owner-discarded; BoltRewards footer infrastruktur; HOPKIN GENESIS + $BUNNY + DNSIEGE/SIEGE + "
    "Tera Card + BRAINROT ZOO/Gacha Gang/Ticker Pets/Odyssey scan-seen/hot-leg-seen, bukan first-seen, bukan lead. "
    "MINTS index 58 proyek, 0 baru. Sourcify 5a: 20 kontrak, 0 S1/S2/0 agent-mint (4 near-miss registry=False). "
    "Square/Odaily/PANews: hanya item lama, 0 site link baru. DappBay: tanpa match Hopkin/Coracle. Bridge TIDAK "
    "berubah (sha256 b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 promosi). 0 lead baru dari kaki ini."
)
snap["runNote0131_binanceai"] = (
    "Run 0131 track-B binanceai re-check (blok 132251024): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-0101; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

# --- scan-state: add note only, never touch last_scanned_block ---
st = json.load(open(HF + "onchain-scan-state.json"))
wm_before = st.get("last_scanned_block")
st["note_0131_scan"] = (
    "Run 0131 scan: pre-flight PASS 2,5 dtk (head 132250869). Window 132249931-132250930 (1000 blok), "
    "135 NFT + 267 ERC-20 mint, 40 Ankr calls, 0 error, partial=False. Triage 0 first-seen; 5c 2 baru dicek, "
    "0 hit. Watermark TIDAK dimajukan run ini (milik backfill)."
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
scan = json.load(open(HF + "onchain-scan-2026-11-08-0131.json"))
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
added_seen = 0
for c in scan.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen_contracts and a != REG.lower():
        seen_contracts[a] = {"first_seen_block": c.get("first_block"), "first_seen_run": "0131",
                             "first_seen": "run-0131-scan"}
        added_seen += 1
for e in scan.get("erc20_mint_contracts_list", []):
    a = (e.get("address") or "").lower()
    if a and a not in seen_contracts:
        seen_contracts[a] = {"first_seen_block": e.get("first_block"), "first_seen_run": "0131",
                             "first_seen": "run-0131-scan"}
        added_seen += 1
with open(HF + "onchain-scan-seen.json.tmp", "w") as f:
    json.dump(seen, f, indent=1)
os.replace(HF + "onchain-scan-seen.json.tmp", HF + "onchain-scan-seen.json")

# --- track-c-scan-checked merge (+2 from 5c) ---
fivec = json.load(open(HF + "run-2026-11-08-0131-5c.json"))
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
                sub[a.lower()] = {"run": "0131", "verdict": "no-shape"}
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

print(f"FINALIZE-0131 DONE updated={updated} none_supply={none_supply} tc_updated={tc_updated} "
      f"age_remove={len(age['candidates'])} horus->excluded kagent->excluded "
      f"seen_added={added_seen} checked_added={added_checked} watermark_still={wm_before}")
