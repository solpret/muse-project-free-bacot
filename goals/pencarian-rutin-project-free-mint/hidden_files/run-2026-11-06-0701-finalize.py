#!/usr/bin/env python3
"""Run 2026-11-06 0701 WIB FINALIZE: merge backfill triage + early-verify results, add the 3
early leads to the snapshot, and CORRECT the watermark notes written by the 0701 apply
(the backfill advanced last_scanned_block 131895548 -> 131897548 during this run; this run's
own scan did NOT advance it). Backups written first."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0701"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0701b")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-0701b")

# --- 1. Correct the triage JSON with the curl ABI + Ankr verification results ---
tri = json.load(open(f"{BASE}/run-{TS}-backfill-triage.json"))
ver = json.load(open(f"{BASE}/run-{TS}-early-verify.json"))
ret = json.load(open(f"{BASE}/run-{TS}-early-verify-retry.json"))
TS_WIB = {"Silent Hydra Agent": "2026-11-06 05:22:50",
          "Cipher Wraith Agent": "2026-11-06 05:28:05",
          "Umbra Lynx Agent": "2026-11-06 05:33:20"}
STATE = {
    "Silent Hydra Agent": {"totalSupply": 3333, "totalMinted": 1, "spotsLeft": 3332,
                           "MAX_SUPPLY": 3333, "PRICE": 500000000000000},
    "Cipher Wraith Agent": {"totalSupply": 3333, "totalMinted": None, "spotsLeft": 3332,
                            "MAX_SUPPLY": 3333, "PRICE": 500000000000000},
    "Umbra Lynx Agent": {"totalSupply": None, "totalMinted": 1, "spotsLeft": 3332,
                         "MAX_SUPPLY": 3333, "PRICE": 500000000000000},
}
for item in tri["nft_first_seen"]:
    name = item["name"]
    item["agent_shaped"] = True
    item["agent_shape_evidence"] = ("Sourcify ABI (curl re-fetch, 29 functions) contains AGENT_REGISTRY + "
        "mint + quote; classify() GATE_WORDS misses 'AGENT_REGISTRY' (underscore) - blind spot noted, "
        "shape decided on the ABI itself, not the classify gate field.")
    item["gate_fns_corrected"] = ["AGENT_REGISTRY"]
    item["first_mint_verified"] = ret[name]["first_mint_verified"]
    item["earlier_mints_before_first_block"] = ret[name]["earlier_mints_before_first_block"]
    item["first_mint_wib"] = TS_WIB[name]
    item["state"] = STATE[name]
    item["quote_user_1"] = None
    item["quote_note"] = ("quote(user,1) reverts/fails on all RPCs (early-verify + retry scripts, 3 RPCs) - "
        "free/paid for the user slot UNVERIFIED; PRICE()=0.0005 BNB is the paid price; no free view in ABI.")
json.dump(tri, open(f"{BASE}/run-{TS}-backfill-triage.json", "w"), indent=1)

# --- 2. Add the 3 early leads to the snapshot ---
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
ADDR = {
    "Silent Hydra Agent": ("0x56C7776351BaDf99D33A602026aAAD7Afc5E4dF4", "SILH", 131896042),
    "Cipher Wraith Agent": ("0x50e9958a50B239f96fC64b9e1A06A3850D24063a", "CIPW", 131896743),
    "Umbra Lynx Agent": ("0x1062c963F5F11A5A55831B7e818E55b052B59947", "UMBL", 131897443),
}
for name, (addr, sym, fb) in ADDR.items():
    st = STATE[name]
    s["contracts"][name] = {
        "address": addr,
        "status": "early-lead-reported-2026-11-06",
        "name": name,
        "symbol": sym,
        "kind": "ERC721",
        "totalSupply": st["totalSupply"],
        "totalMinted": st["totalMinted"],
        "spotsLeft": st["spotsLeft"],
        "MAX_SUPPLY": st["MAX_SUPPLY"],
        "PRICE": st["PRICE"],
        "freeClaimed": None,
        "freePctVerified": None,
        "mintOpen": None,
        "userMintedBy": 0,
        "userBalance": 0,
        "userSlotNote": ("Slot UNVERIFIED: quote(user,1) reverts/fails on all RPCs (early-verify + retry, "
            "3 RPCs); mintedBy(user)=0, balanceOf(user)=0; PRICE 0.0005 BNB; no free view in ABI."),
        "firstSeenBlock": fb,
        "firstMintWib": TS_WIB[name],
        "scanMints": 1,
        "scanMinters": 1,
        "scanWindow": "131895549-131897548 (backfill chunk)",
        "lastReadBlock": None,
        "lastReadWib": "2026-11-06 run 0701 (state reads via eth_call latest ~07:24 WIB; block not captured)",
        "xVerified": False,
        "velocityVerified": False,
        "launchNote": (f"First mint verified on-chain: first Transfer-from-zero at block {fb}, "
            f"{TS_WIB[name]} WIB (Ankr getLogs address-filtered 131880000..{fb-1}: 0 earlier mints). "
            "No project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time "
            "(Umbra verifiedAt 2026-11-05T22:33:39Z). First-seen by this job in run 0701 via backfill chunk "
            "(main route-4 scan stalled)."),
        "baselineNote": ("EARLY lead reported once 2026-11-06 run 0701. Never auto-minted/previewed. "
            "Agent-shape verified: Sourcify ABI (29 functions, identical across the three) contains "
            "AGENT_REGISTRY + mint + quote; classify() GATE_WORDS misses 'AGENT_REGISTRY' (underscore blind "
            "spot - recorded). Free leg UNVERIFIED: no free view in ABI, quote(user,1) reverts on all RPCs, "
            "PRICE 0.0005 BNB. Same operator: OWNER = first minter 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5 "
            "for all three (factory wave; same-owner rule may discard a later promotion). Age verified "
            "<=48h (~1.9h at report). Promotes to strong lead only on all 3 strong-lead legs; to candidate "
            "only on ALL criteria + safety."),
        "owner": "0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5",
        "source": "backfill-131895549-131897548",
        "supplyView": "totalMinted",
        "supplyQuirk": ("totalSupply() reads 3333 (=MAX_SUPPLY) while totalMinted=1; spotsLeft 3332 is the "
            "meaningful remaining count."),
    }

# --- 3. Correct the watermark notes (backfill advanced it, not this run's scan) ---
s["runNote0701"] = ("Run 0701: 3 EARLY leads baru (Silent Hydra / Cipher Wraith / Umbra Lynx - dari chunk backfill "
    "131895549-131897548; dilaporkan sekali run ini) + 1 sellout (Agent Harvest Land free pool 5000/5000, dihapus "
    "dari watchlist). Selain itu SILENT: no new candidate/strong lead/track-C; scan route 4 GAGAL/STALL ke-5 "
    "berturut-turut (timeout 780, 0 byte log, SCAN_EXIT=124). KING totalMinted 515->562 (+47, velocity 1,09x GAGAL, "
    "free inferensi 16,9% <25%); MILLION 74->84 (+10); HIVE flat 1253; SEAT +294 (watchlist-only). Boltbook newest "
    "post unchanged (2026-11-05T09:20:52Z); Sourcify 4 kontrak baru dicek (S1/S2=false semua); 5c: 3 ERC-20 baru "
    "dicek (bukan sale-shape); Odaily/PANews 0 mention Agent ID; bridge 0 not-in-snapshot; binanceai tetap "
    "refund/failed (launched=0).")
s["runNote0701_scan"] = ("Run 0701: SCAN (route 4, percobaan run ini) GAGAL/STALL ke-5 berturut-turut (timeout 780, "
    "0 byte log, SCAN_EXIT=124; pola sama run 0431/0531/0601/0631). Scan run ini TIDAK memajukan watermark. "
    "KOREKSI: watermark TETAP dimajukan selama run ini - oleh proses BACKFILL terpisah (chunk 131895549-131897548, "
    "80 panggilan Ankr, 0 error, selesai 07:04 WIB) dari 131895548 ke 131897548; chunk itu yang menjadi cakupan "
    "route-4 run ini (3 first-seen NFT + 5c dari outputnya). Window kedua backfill (131897549-131899548) masih "
    "berjalan saat run ini selesai - triase-nya tugas run berikut. Gap yang belum ter-cover: 131897549-131911xxx+ "
    "(~13.500 blok). CATATAN BLOCK-RATE: BSC kini ~0,45 dtk/blok (4257 blok dalam 31,9 mnt antar bacaan 0631->0701; "
    "terverifikasi via timestamp blok 131905343=06:32:35 dan 131909600=07:04:31 WIB) - asumsi body '~600 blok per "
    "30 mnt' sudah usang; cap 2000 blok kini hanya menutup ~15 mnt, gap tumbuh ~2000 blok/run.")
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0701_scan_failed"] = ("Run 0701: SCAN (route 4, percobaan run ini) GAGAL/STALL ke-5 berturut-turut (timeout 780, "
    "0 byte log, SCAN_EXIT=124; pola sama run 0431/0531/0601/0631). Scan run ini TIDAK memajukan watermark. "
    "KOREKSI: watermark dimajukan SELAMA run ini oleh proses BACKFILL terpisah (chunk 131895549-131897548, 80 "
    "panggilan Ankr, 0 error, selesai 07:04 WIB): 131895548 -> 131897548. Chunk kedua (131897549-131899548) masih "
    "berjalan saat run ini selesai. Gap belum ter-cover: 131897549-131911xxx+.")
st["last_scan_failed_wib"] = "2026-11-06 run 0701"
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("finalized: contracts now", len(s["contracts"]), "| watermark:", st["last_scanned_block"])
