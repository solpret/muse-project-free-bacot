#!/usr/bin/env python3
"""Append run 0131 (2026-11-10 01:31 WIB) new triaged items to snapshot.
- COSO v2 (track_c): AGE-EXCLUDED - saleStart 2026-11-06 22:19 WIB, ~75.5h old at run.
- AGENT 888 S2 (contracts): checked-not-a-lead - no free entry (mint reverts 'not eligible' per Boltbook post; no free views on-chain).
- GenesisTx (contracts): checked-not-a-lead - window closed, 238/238 minted, no free views.
No status changes to reported items; no deletions. Run AFTER merge.
"""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))

snap.setdefault("track_c", {})["COSO v2"] = {
    "sale": "0x7020368e5421008b92C16798589ac6d91812307e",
    "token": None,
    "address": "0x7020368e5421008b92C16798589ac6d91812307e",
    "name": "COSO v2", "symbol": "COSO",
    "shape": "sale-shape PARTIAL: mintShares+claimFree+freeMinted/freeClaimed+registrar=registry, NO quote/cost fn in ABI -> S1 FAILS; not the token itself -> S2 FAILS",
    "status": "age-excluded-2026-11-10",
    "totalShares": 491, "freeMinted": 491, "FREE_SHARES": 1000, "freePoolRemaining": 509,
    "TOTAL_SHARES": 5000, "TOTAL_SLOTS": 2000, "slotsFilled": 0,
    "saleStart": 1793978346, "saleStartWib": "2026-11-06 22:19:06 WIB",
    "saleDeadline": 1797866346, "poolOpen": 0, "poolOpenedAt": 0,
    "registrar": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sharesOf_user": 0, "walletStatus_user_first_word": 1,
    "quote_user_1": None,
    "website": None, "websiteGate": "NOT CHECKED - age already excludes (75.5h > 48h); no site search run for this item",
    "xVerified": False,
    "sourcifyVerified": True,
    "firstSeenBlock": 132633893, "lastReadBlock": 132633893, "lastReadWib": NOW_WIB,
    "discovery": "Boltbook front page run 0131 (post bangwi.ai ~14m ago): 'COSO v2: 488/1,000 free shares taken, 512 left' (blok 132627308 ~00:57 WIB).",
    "launchNote": ("Umur TERVERIFIKASI >48 jam: saleStart() on-chain = 1793978346 = 2026-11-06 22:19:06 WIB; "
                   "run 2026-11-10 01:31 WIB -> umur ~75,5 jam. GUGUR per aturan umur 48 jam (belum sold out: free 509/1000 tersisa)."),
    "gateNote": ("BUKAN lead/kandidat: umur >48 jam. TIDAK preview/mint, TIDAK dilaporkan ke chat (age-exclusion dicatat di run log + snapshot saja). "
                 "Bentuk sale: registrar() = registry Binance persis; claimFree + freeMinted/freeClaimed ada; TAPI tanpa fungsi quote/cost -> S1 gagal; bukan token itu sendiri -> S2 gagal."),
    "runNote0131_1110": "Run 0131: BARU di track_c (age-excluded). totalShares 491/5000, freeMinted 491/1000 (509 free tersisa), saleStart 2026-11-06 22:19 WIB (~75,5 jam). TIDAK preview/mint (umur >48 jam)."
}

snap.setdefault("contracts", {})["AGENT 888 S2"] = {
    "address": "0x1c963acf3743a2b2a3ee8359100e9cbeca82d424",
    "name": "AGENT 888 S2", "kind": "ERC721",
    "status": "checked-not-a-lead-2026-11-10",
    "totalSupply": 196, "totalMinted": None, "freeClaimed": None, "freeMinted": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": None, "mintOpen": 1,
    "owner": "0x86b39b6313f565ba18d988daa409ea192a28d950",
    "agentIdRegistry": None, "balanceOf_user": None,
    "website": None, "xVerified": False,
    "firstSeenBlock": None, "lastReadWib": NOW_WIB,
    "discovery": "Boltbook front page run 0131 (post 1328.ai ~9m ago): 'AGENT 888 S2 (0x1c96...) mintOpen=true, 60/888, tapi mint(1) value=0 revert \"not eligible\", tidak ada free entry'.",
    "launchNote": "Umur tidak diverifikasi - tidak perlu: tanpa free entry, bukan lead apapun.",
    "gateNote": "BUKAN lead/kandidat: tidak ada free entry (mint value=0 revert 'not eligible' menurut post; tanpa freeClaimed/freeMinted/FREE_SUPPLY view on-chain; tanpa agentIdRegistry view). TIDAK preview/mint, TIDAK dilaporkan.",
    "runNote0131_1110": "Run 0131: BARU, checked-not-a-lead. totalSupply 196, mintOpen 1, tanpa free view. Post Boltbook: mint gratis revert 'not eligible'."
}

snap.setdefault("contracts", {})["GenesisTx"] = {
    "address": "0xce43adb0b4bd650d410feb2eafdda3e1d30ca49e",
    "name": "GenesisTx", "kind": "ERC721",
    "status": "checked-not-a-lead-2026-11-10",
    "totalSupply": 238, "totalMinted": 238, "freeClaimed": None, "freeMinted": None,
    "FREE_SUPPLY": None, "MAX_SUPPLY": None, "mintOpen": None,
    "owner": "0x73d57ae7021b490f0ed6b45f4c43304c5e52d1a8",
    "agentIdRegistry": None, "balanceOf_user": None,
    "website": None, "xVerified": False,
    "firstSeenBlock": None, "lastReadWib": NOW_WIB,
    "discovery": "Boltbook front page run 0131 (post 1328.ai ~9m ago): 'Genesis Tx (0xce43...) owner ada withdraw+setMintActive, window sudah tutup, hanya 238 mint'.",
    "launchNote": "Umur tidak diverifikasi - tidak perlu: window tutup, bukan lead apapun.",
    "gateNote": "BUKAN lead/kandidat: window mint sudah tutup (totalSupply 238 = totalMinted 238, sesuai post); tanpa free view; owner punya withdraw+setMintActive (per post). TIDAK preview/mint, TIDAK dilaporkan.",
    "runNote0131_1110": "Run 0131: BARU, checked-not-a-lead. totalSupply 238 = totalMinted 238, window tutup, tanpa free view."
}

snap["runNote0131_1110_append"] = (f"Run 0131 append ({NOW_WIB}): COSO v2 BARU di track_c (age-excluded, saleStart 2026-11-06 22:19 WIB, ~75,5 jam, free 509/1000 tersisa); "
    "AGENT 888 S2 BARU checked-not-a-lead (tanpa free entry); GenesisTx BARU checked-not-a-lead (window tutup, 238/238).")
with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("APPENDED COSO v2 (track_c age-excluded) + AGENT 888 S2 + GenesisTx (checked-not-a-lead)")
