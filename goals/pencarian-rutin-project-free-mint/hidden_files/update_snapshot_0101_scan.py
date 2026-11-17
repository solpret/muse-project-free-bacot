#!/usr/bin/env python3
"""Snapshot + seen/state update run 0101 (2026-11-06 01:01 WIB) — ROUTE 4 scan.
Scan window 131859763-131861762 (2000 blok, cap), head scanned 131861762,
gap dilewati 131856448-131859762 (3315 blok, ~24.9 mnt chain time @0.45 dtk/blok).
269 NFT contracts, 1354 NFT mints, 562 ERC-20, 80 Ankr calls, 0 errors.
First-seen: 5 (semua registry=True). Triase:
- Tampesta: agent-shaped terverifikasi (Sourcify ABI: AGENT_ID=registry, agentGate,
  mintFree; MAX_FREE_PER_WALLET 2) TAPI BELUM LAUNCH: paused=1, phase=0,
  mintStart 2026-11-06 21:00 WIB, publicMinted=0; 22 'mint' adalah treasury mint
  ke owner (tokenId 1-22, 1 minter = owner). -> watchlist-only-upcoming, BUKAN early.
- V73/V74: BERBAYAR (sample mint tx 0.001 BNB), 8 mint/1 minter, totalMinted 2825.
- Mirage Owl Agent / Nebula Tiger Agent: BERBAYAR (sample mint tx 0.0005 BNB),
  1 mint/1 minter, anomali totalSupply=3333 vs 1 log (pre-mint < blok 130000000,
  pola sama dgn Krypt Titan dkk run 0001). -> watchlist-only-paid-only.
0 early lead baru, 0 kandidat, 0 strong lead dari scan run ini."""
import json, shutil

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
scan = json.load(open(HF + "onchain-scan-2026-11-06-0101.json"))
snap = json.load(open(HF + "onchain-snapshot.json"))
seen = json.load(open(HF + "onchain-scan-seen.json"))
state = json.load(open(HF + "onchain-scan-state.json"))

shutil.copy(HF + "onchain-scan-seen.json", HF + "onchain-scan-seen-0101.bak.json")
shutil.copy(HF + "onchain-scan-state.json", HF + "onchain-scan-state-0101.bak.json")

# --- seen file: append the 5 first-seen (absent from seen contracts) ---
tri = json.load(open(HF + "triage-firstseen-2026-11-06-0101.json"))["triage"]
added = 0
for c in scan["contracts"]:
    a = c["address"]
    if a.lower() not in {k.lower() for k in seen["contracts"]}:
        seen["contracts"][a] = c.get("first_block")
        added += 1
json.dump(seen, open(HF + "onchain-scan-seen.json", "w"), indent=1)

# --- scan state: advance watermark ONLY on success (scan sukses, 0 error) ---
state.update({
    "last_scanned_block": scan["to_block"],
    "last_scan_window_from": scan["from_block"],
    "last_scan_window_to": scan["to_block"],
    "last_scan_wib": "2026-11-06 run 0101",
    "ankr_calls": scan.get("ankr_calls"),
    "errors": scan.get("errors", []),
    "nft_contracts": 269,
    "erc20_mint_contracts": scan.get("erc20_mint_contracts"),
    "skipped_gap": "131856448-131859762 (3315 blok, window dari watermark 131856447 ke head scan 131861762 = 5315 blok > cap 2000; scan menutup 2000 blok terbaru 131859763-131861762)",
    "note": ("Scan run 0101 SUKSES (80 panggilan Ankr, 0 error). 5 first-seen registry=True: "
             "Tampesta (upcoming, mintStart 2026-11-06 21:00 WIB), V73/V74 paid-only 0.001 BNB, "
             "Mirage Owl Agent / Nebula Tiger Agent paid-only 0.0005 BNB. 0 early lead baru. "
             "Gap kumulatif sejak run 1831 ~40.100 blok tak ter-scan. CATATAN: rantai berjalan "
             "0,45 dtk/blok (terverifikasi 62.944 blok) — 30 mnt = ~4000 blok, jadi cap 2000 blok "
             "hanya menutup ~15 mnt; watermark tertinggal ~2000 blok/run."),
    "last_scan_window": "131859763-131861762",
    "ankr_calls_last_scan": scan.get("ankr_calls"),
    "errors_last_scan": scan.get("errors", []),
    "scan_started_wib": "2026-11-06 01:03",
    "scan_finished_wib": "2026-11-06 01:18",
    "head_at_scan_start": 131861588,
})
json.dump(state, open(HF + "onchain-scan-state.json", "w"), indent=1)

# --- snapshot: Tampesta upcoming + 4 paid-only ---
def add_entry(key, entry):
    if key not in snap["contracts"]:
        snap["contracts"][key] = entry

add_entry("Tampesta", {
    "address": "0x6aA51bd62C0c6B0bA206e25952F4063a7e0CCE79",
    "name": "Tampesta", "symbol": "TMPST", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-06",
    "totalSupply": 22, "totalMinted": 22, "maxSupply": 2222,
    "firstSeenBlock": 131860529,
    "firstMintWib": "2026-11-06 00:56:28 WIB",
    "mintStartWib": "2026-11-06 21:00 WIB",
    "phase": 0, "paused": True, "publicMinted": 0,
    "MAX_FREE_PER_WALLET": 2, "price_BNB": 0.0042,
    "lastReadBlock": 131862037, "lastReadWib": "2026-11-06 run 0101",
    "baselineNote": ("First-seen scan run 0101, BUKAN early lead: agent-shaped terverifikasi "
        "(Sourcify ABI: AGENT_ID()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, agentGate, "
        "mintFree, MAX_FREE_PER_WALLET=2) TAPI BELUM LAUNCH — paused=1, phase=0, "
        "mintStart 2026-11-06 21:00 WIB, publicMinted=0. 22 Transfer-from-zero adalah treasury "
        "mint ke owner (tokenId 1-22, 1 minter = owner 0x30d0e10b2a001c61f986ed356f6d10dd986c74ce, "
        "sample tx value 0). Dilacak sebagai upcoming; promosi hanya bila mint publik dibuka "
        "dan kaki strong-lead terpenuhi. X/website UNVERIFIED."),
})
add_entry("V73", {
    "address": "0x88a739Ba8957a23D492f3ea765e830fa86E2f13D",
    "name": "V73", "symbol": "V93", "kind": "ERC721",
    "status": "watchlist-only-paid-only-2026-11-06",
    "totalMinted": 2825, "price_BNB": 0.002,
    "firstSeenBlock": 131860681, "firstMintWib": "2026-11-06 00:57:36 WIB",
    "lastReadBlock": 131862037, "lastReadWib": "2026-11-06 run 0101",
    "baselineNote": ("First-seen scan run 0101, BUKAN early: BERBAYAR — sample mint tx value "
        "0.001 BNB (0x38d7ea4c680000), 8 mint / 1 minter, price()=0.002 BNB, "
        "Sourcify not_verified. Bukan lead."),
})
add_entry("V74", {
    "address": "0x8307A49E8a0A3ba0429aE6aCf0191858ae05d818",
    "name": "V74", "symbol": "V94", "kind": "ERC721",
    "status": "watchlist-only-paid-only-2026-11-06",
    "totalMinted": 2825, "price_BNB": 0.002,
    "firstSeenBlock": 131861462, "firstMintWib": "2026-11-06 01:03:27 WIB",
    "lastReadBlock": 131862037, "lastReadWib": "2026-11-06 run 0101",
    "baselineNote": ("First-seen scan run 0101, BUKAN early: BERBAYAR — sample mint tx value "
        "0.001 BNB (0x38d7ea4c680000), 8 mint / 1 minter, price()=0.002 BNB, "
        "Sourcify not_verified. Minternya sama dengan V73 (0x9355eef9273f051f1be83ec1ba11000cedf02e69). "
        "Bukan lead."),
})
add_entry("Mirage Owl Agent", {
    "address": "0xf473070a363CfBdefd9711dB5B4c9aeB79205477",
    "name": "Mirage Owl Agent", "symbol": "MIRO", "kind": "ERC721",
    "status": "watchlist-only-paid-only-2026-11-06",
    "totalSupply": 3333, "totalMinted": 1, "MAX_SUPPLY": 3333,
    "firstSeenBlock": 131860365, "firstMintWib": "2026-11-06 00:55:14 WIB",
    "lastReadBlock": 131862037, "lastReadWib": "2026-11-06 run 0101",
    "baselineNote": ("First-seen scan run 0101, BUKAN early: BERBAYAR — sample mint tx value "
        "0.0005 BNB (0x1c6bf52634000), 1 mint / 1 minter. ANOMALI: totalSupply=3333 pada "
        "1 log mint (pre-mint < blok 130000000, pola sama dgn Krypt Titan dkk run 0001). "
        "Sourcify error RemoteDisconnected (retry). Bukan lead."),
})
add_entry("Nebula Tiger Agent", {
    "address": "0xD52cDEb5f3CA763aB75738752A0b740aFEDDF652",
    "name": "Nebula Tiger Agent", "symbol": "NEBT", "kind": "ERC721",
    "status": "watchlist-only-paid-only-2026-11-06",
    "totalSupply": 3333, "totalMinted": 1, "MAX_SUPPLY": 3333,
    "firstSeenBlock": 131861064, "firstMintWib": "2026-11-06 01:00:28 WIB",
    "lastReadBlock": 131862037, "lastReadWib": "2026-11-06 run 0101",
    "baselineNote": ("First-seen scan run 0101, BUKAN early: BERBAYAR — sample mint tx value "
        "0.0005 BNB (0x1c6bf52634000), 1 mint / 1 minter. ANOMALI: totalSupply=3333 pada "
        "1 log mint (pre-mint < blok 130000000, pola sama dgn Krypt Titan dkk run 0001). "
        "Minter sama dengan Mirage Owl Agent (0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5). "
        "Sourcify error RemoteDisconnected (retry). Bukan lead."),
})

snap["runNote0101_scan"] = (
    "Run 0101 scan rute 4 SUKSES: jendela 131859763-131861762 (2000 blok, cap), gap dilewati "
    "131856448-131859762 (3315 blok); 269 NFT + 562 ERC-20, 1354 NFT mints, 80 panggilan Ankr, "
    "0 error. 5 first-seen (registry=True): Tampesta -> watchlist-only-upcoming (mintStart "
    "2026-11-06 21:00 WIB, paused, publicMinted 0); V73/V74 paid-only 0.001 BNB; Mirage Owl "
    "Agent / Nebula Tiger Agent paid-only 0.0005 BNB. 0 early lead baru dari scan. Seen file "
    f"9519 -> {len(seen['contracts'])} (+{added}). Watermark -> 131861762.")
snap["last_run_wib"] = "2026-11-06 run 0101"
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print(f"seen appended: {added} (total {len(seen['contracts'])})")
print("wrote snapshot + seen/state + backups")
