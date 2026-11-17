#!/usr/bin/env python3
"""Assemble run 1731 triage JSON from scan + verify files. Read-only (writes only the triage file)."""
import json
scan = json.load(open("onchain-scan-2026-11-08-1731.json"))
feed_shape = json.load(open("run-2026-11-08-1731-feed-shape.json"))
fivec = json.load(open("run-2026-11-08-1731-5c.json"))
b2 = json.load(open("run-2026-11-08-1731-bahuang2-verify.json"))
fv = json.load(open("run-2026-11-08-1731-feed-verify.json"))
tv = json.load(open("run-2026-11-08-1731-triage-verify.json"))
triage = {
  "run": "1731",
  "date_wib": "2026-11-08",
  "run_finished_wib": "2026-11-08 ~17:52 WIB",
  "scan_window": {"from_block": scan["from_block"], "to_block": scan["to_block"], "latest_block": scan["latest_block"]},
  "scan_partial": scan["partial"],
  "scan_ankr_calls": scan["ankr_calls"],
  "scan_errors": scan["errors"],
  "scan_nft_contracts": len(scan["contracts"]),
  "scan_nft_mints": sum(c.get("mint_count", 0) for c in scan["contracts"]),
  "scan_erc20_mint_contracts": len(scan["erc20_mint_contracts_list"]),
  "hive_agents_found": scan["hive_agents_found"],
  "watermark_before": 132373209,
  "watermark_decision": "ADVANCE to 132377461 (full scan, partial=false, 0 errors) — PARENT MERGES; this leg does NOT write state/seen/snapshot.",
  "skipped_gap": "132373210-132376461 (3252 blocks; window from watermark to head 4203 blocks > cap 1000; scan covered most recent 1000 only; backfill OFF)",
  "preflight": {"head": 132377412, "logs_50_blocks": 324, "seconds": 5.2, "total_seconds": 8.1, "result": "OK"},
  "ankr_calls_total_run": 56,
  "ankr_calls_breakdown": {"preflight": 1, "scan": 40, "bahuang2_first_mint_reverify": 1, "monolith_tx_value_check": 7, "monolith_tokenid_check": 7},
  "scan_duration_minutes": "~13 (scan start ~17:34 WIB, finished ~17:47 WIB, incl enrichment 111/111)",
  "first_seen_total": 5,
  "first_seen": {
    "0x57CC350b844484Eac0DE444526d295C90F9cCbB5": {
      "name": "BAHUANG2", "symbol": "BAHUANG2", "kind": "ERC721",
      "classification": "EARLY LEAD (report once by parent; add to snapshot watchlist; NEVER preview/mint as early lead)",
      "scan": {"mint_count_in_window": 114, "distinct_minters": 57, "first_block_in_window": 132376581, "registry_bytes_hit": True, "sourcify": "verified"},
      "first_mint": {"block": 132375730, "wib": "2026-11-08 17:21:43 WIB", "tx": "0x085210b23124e0bafd81c6a9e10b5a24da97afab8e53d8560557f9521e8845bf", "verified": "Ankr getLogs re-verified this run (4 Transfer logs at block 132375730); mintStart 1794133293 = 17:21:33 WIB corroborates launch",
       "note": "first mint is in the skipped gap 132373210-132376461; caught by direct verify, not by scan window"},
      "agent_shape": {"agentId()": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry EXACT)", "registry_bytes_hit": True, "free_funcs": ["FREE_CAP", "FREE_PER_WALLET", "FREE_REWARD", "freeCount", "freeMint", "freeMinted"], "owner()": "ABSENT from ABI (no owner fn) -> same-owner check N/A"},
      "free_quota": {"FREE_CAP": 3000, "freeMinted_at_1719": 32, "freeMinted_at_~1735": 196, "pct": "6.53%", "totalMinted": 194, "FREE_PER_WALLET": 2, "freeCount(agent_wallet)": 0, "user_slot": "OPEN"},
      "velocity_note": "freeMinted 32 -> 196 in ~16 min (+164); fast but below 25% strong-lead and 50% candidate thresholds",
      "age": "~14-18 min at verify (<=48h OK)",
      "legs": {"age_verified_le48h": True, "free_pct_ge25": False, "user_slot_open": True, "website_gate": "NOT CHECKED by this leg (parent)", "x_discussion": "NOT CHECKED by this leg (parent)"}
    },
    "0xcdA4A0EF9C0a626b2450168fd8F90f62C51A569b": {
      "name": "MONOLITH", "symbol": "MNTH", "kind": "ERC721",
      "classification": "EARLY LEAD (report once by parent; add to snapshot watchlist; NEVER preview/mint as early lead)",
      "scan": {"mint_count_in_window": 7, "distinct_minters": 7, "first_block_in_window": 132377160, "registry_bytes_hit": True, "sourcify": "not_verified"},
      "first_mint": {"first_observed_block": 132377160, "first_observed_wib": "2026-11-08 17:32:27 WIB (dataseed block timestamp)", "tokenIds_in_window": [1, 2, 3, 4, 5, 6, 7], "totalSupply": 8, "caveat": "token 0 minted BEFORE the window (time unverified; walk-back over skipped gap not performed). 7/8 supply minted within ~7 min of first observed mint; launch plausibly minutes before window, age <=48h likely but first-mint minute not 100% verified"},
      "agent_shape": {"agentRegistry()": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry EXACT via view)", "registry_bytes_hit": True, "free_views": "freeMinted/FREE_CAP/FREE_SUPPLY/freeLeft/freeClaimed(agent) ALL revert (no such fns) — free proven via tx values, not views", "sourcify": "not_verified"},
      "free_proof": "all 7 in-window mint txs value=0 BNB (7 distinct minters; txs 0x0095b7d7..., 0x094c1be9..., 0x0dce1e3d..., 0x2741ce38..., 0x3624572f..., 0x917aeb51..., 0xdb0b40ad...); gas-only mints verified on-chain",
      "same_owner": "owner() 0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3 — same-owner-discards.json entry for this owner is an EXCEPTION ('TIDAK dibuang oleh aturan same-owner', BNB Faucet, discarded_wib null) -> NOT discarded",
      "legs": {"age_verified_le48h": "LIKELY (first observed mint 17:32:27 WIB) but token-0 mint time unverified", "free_pct": "UNVERIFIED (no free-cap view; totalSupply 8, 7 free mints in-window)", "user_slot_open": "UNVERIFIED (freeClaimed(agent) reverts; no free-mint fn view)", "website_gate": "NOT CHECKED by this leg (parent)", "x_discussion": "NOT CHECKED by this leg (parent)"}
    },
    "0x57E3F981791C3BE85d74e74A2F402D7D00F6eD9C": {
      "name": "OBSIDIAN CARD", "symbol": "OBSID", "kind": "ERC721",
      "classification": "SAME-OWNER DISCARD — never promote/report as lead",
      "scan": {"mint_count_in_window": 4, "distinct_minters": 4, "first_block_in_window": 132377391, "registry_bytes_hit": True, "sourcify": "verified"},
      "evidence": {"owner()": "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd (10 entries in same-owner-discards.json: Toucan Play / jelly.exe / Los Flamingos / Moonhowlers / Counting Sheep / Tusk & Trunk / getpuffr / Hippo Social Club / LLAMA DRAMA / Danger Noodles — costOf/mintsLeft wave, discarded)", "totalSupply": 15, "note": "15 totalSupply vs 4 in-window mints -> first mint predates window; age unverified anyway; discard is decisive", "freeLeft": 1096, "mintOpen": 1}
    },
    "0xf415E7A2de78ab57A4428A75D0062e8a999d8B0F": {
      "name": "Aequitas Boost", "symbol": "AEQB", "kind": "ERC721",
      "classification": "NOT agent-shaped — never report",
      "scan": {"mint_count_in_window": 10, "distinct_minters": 1, "first_block_in_window": 132377402, "registry_bytes_hit": False, "sourcify": "verified"},
      "evidence": "registry=False, free_shaped=[]; totalSupply/totalMinted/agentId/owner views all revert/error"
    },
    "0x4bb41DB7e49dFa27000EF299E372aC649A197752": {
      "name": "Barrels for Rum", "symbol": "BARRELS", "kind": "ERC721",
      "classification": "NOT agent-shaped — never report",
      "scan": {"mint_count_in_window": 1, "distinct_minters": 1, "first_block_in_window": 132376926, "registry_bytes_hit": False, "sourcify": "verified"},
      "evidence": "registry=False, free_shaped=[]; owner 0xbc9d5a23f2e55286650aae5573c524703aeb4724 not in discards"
    }
  },
  "refinds": {
    "oddlode_drills": "0xce18531F9F639ca2351CA15FB2032D925b917472 — 168 mints in window; ALREADY MINTED by user in run 1631 (tx 0xf515f49ce73580ec7f6cf541b1170e6122380f5de45e58e53e47eaf3b8beeb1a, #814, receipt 1, block 132376388) — do NOT re-report",
    "snapshot_known_refound": ["0xbd4B4e7189ae9356514664146b0eD683601200A9", "0x6c724401f0C99E63d0119c17c97665f07c978Ef3", "0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B", "0xAAEF5BB8A7363B5997F17149d554640DC35f306d", "0xE7a548606eECB32a93B227411b6343B0399DC7C0", "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8", "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4"],
    "total_refinds": 106,
    "note": "first-seen counted vs seen['contracts'] (11491, lowercase keys) + top-level address keys + known_older_leads + snapshot contracts; 0 of the 5 first-seen appear in any historical onchain-scan-*.json"
  },
  "feed_s1_s2": {
    "feed_results": 20,
    "bahuang2": "in feed (verifiedAt 17:21:58 WIB, exact_match) — NFT, handled as early lead above, NOT track-C",
    "nusa_sale_0x7D08289E962f5aEc00d56D67322eb2FD056B687c": {"status": "TRACK-C LEAD already reported by hot-leg 17:04:38 WIB — do NOT re-report", "fresh_read_this_run": {"freeMinted": 14, "MAX_FREE": 560, "sharesMinted": 14, "paidShares": 0, "soldOut": 0, "closed": 0, "freeAvailable(agent)": True, "freeClaimed(agent)": False, "hasMinted(agent)": False, "quotaOf(agent)": 7}, "note": "freeMinted 4 (17:04) -> 9 (hot-leg ~17:19) -> 14 (this run ~17:50); pool open, slot open; website gate still pending (parent); NOT in main snapshot track_c yet — parent merge pending"},
    "kiko9393_0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf": {"status": "watchlist-only-age-unverified (NOT a lead, NOT reported)", "fresh_read_this_run": {"freeMinted": 0, "sharesMinted": 0, "paidShares": 0, "MAX_FREE": 560, "soldOut": False, "closed": False, "freeAvailable(agent)": True, "freeClaimed(agent)": False, "quotaOf(agent)": 7, "deployedAt": "2026-11-08 16:49:52 WIB"}, "note": "S1 sale-shape PASS, agentId()=registry exact, but STILL zero mints — age unverified (deploy time alone is not launch time). Re-check next run for first mint."},
    "token_69_0x184701d8E75C96639734D439BA7949796Af7F285": {"status": "EXCLUDED — free pool exhausted, not reported", "evidence": "name/symbol '69'/'69', totalMinted 70, FREE_CAP 69, freeMinted 69/69, mintOpen=1, registry bytes TRUE (hot-leg agent=False was ABI-only; bytecode proves registry ref) — sold out regardless"},
    "others": "0xEBbA172c (mint, no free, no quote) and all remaining 15 feed items: no S1/S2 sale shape (mint/quote/free/registry legs incomplete)"
  },
  "track_c_5c": {
    "erc20_mint_count_ge10": 41, "already_checked": 39, "newly_checked_this_run": 2,
    "targets": ["0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f (mint_count 57, no-shape)", "0xb50dC583cC6F83750c36789F52d51E12dA664444 (mint_count 21, no-shape)"],
    "hits": 0, "dropped_by_sampling_cap": 0,
    "note": "targets written to run-2026-11-08-1731-5c-targets.json; results to run-2026-11-08-1731-5c.json; track-c-scan-checked.json NOT written by this leg (parent merges)"
  },
  "notes": [
    "No preview/mint/claim/sign/approve/transaction performed by this leg.",
    "No writes to snapshot/state/seen/track-c-scan-checked.json (read-only per task); only run-2026-11-08-1731-* files written.",
    "twitterapi.io never called (dead, 402).",
    "First-seen genuine-new check: seen file + snapshot + grep over all historical onchain-scan-*.json (0 hits for all 5). Caveat: skipped gap 132373210-132376461 unscanned — a pre-window mint hiding there cannot be excluded by scan alone; BAHUANG2 first mint was verified directly in the gap; MONOLITH token-0 mint time unverified; OBSIDIAN 11 pre-window mints prove gap-hidden history exists.",
    "BAHUANG2 freeMinted (196) slightly exceeds totalMinted (194) as read — recorded as observed, not reconciled; does not affect early-lead verdict.",
    "Feed-shape script reg flag is ABI-JSON-only (False for all incl. registry-proven contracts); registry verified separately via eth_getCode bytes for BAHUANG2/1847/KIKO (all TRUE)."
  ]
}
json.dump(triage, open("run-2026-11-08-1731-triage.json", "w"), indent=1)
print("WROTE triage.json; first_seen:", list(triage["first_seen"].keys()))
