#!/usr/bin/env python3
"""00:01 run snapshot part 2: scan watermark/seen, track-c checked, snapshot note."""
import json
H = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
sc = json.load(open(H + "onchain-scan-2026-11-02-0001.json"))
# scan state
state = {"last_scanned_block": sc["to_block"], "last_scan_window_from": sc["from_block"],
         "last_scan_wib": "2026-11-02T00:01:00+07:00", "ankr_calls": sc["ankr_calls"], "errors": sc["errors"],
         "nft_contracts": len(sc["contracts"]),
         "note": "Run 00:01 WIB scan: 2000 blocks (capped; head 131085496 minus last_scanned 131081441 = 4055 > 2000, so only the most recent 2000 scanned; skipped gap 131081442-131083496 recorded, never scanned). Scan wall time ~14 min. Next run scans from last_scanned_block+1, capped at 2000 blocks."}
json.dump(state, open(H + "onchain-scan-state.json", "w"), indent=1)
# seen file: append scan contracts (address lowercase -> scan first_block)
seen = json.load(open(H + "onchain-scan-seen.json"))
before = len(seen["contracts"])
for c in sc["contracts"]:
    seen["contracts"].setdefault(c["address"].lower(), c["first_block"])
json.dump(seen, open(H + "onchain-scan-seen.json", "w"), indent=1)
print(f"seen: {before} -> {len(seen['contracts'])}")
# track-c checked: append 5c results
todo = json.load(open(H + "run-2026-11-02-0001-trackc-erc20-todo.json"))
res = json.load(open(H + "run-2026-11-02-0001-trackc-erc20.json"))
checked = json.load(open(H + "track-c-scan-checked.json"))
chk = checked.setdefault("checked", {})
for o in res:
    mc = next(e["mint_count"] for e in todo if e["address"].lower() == o["address"].lower())
    chk[o["address"]] = {"mint_count": mc, "shape_pass": bool(o.get("S1") or o.get("S2")),
                         "error": o.get("error"), "has_mint": o.get("has_mint"),
                         "quote_cost": o.get("has_quote"), "free_views": o.get("free_views", []),
                         "agent_reg_gate": o.get("agent_ref"), "fns_sample": (o.get("functions") or [])[:20]}
json.dump(checked, open(H + "track-c-scan-checked.json", "w"), indent=1)
print(f"track-c checked total: {len(chk)}")
# snapshot note append
snap = json.load(open(H + "onchain-snapshot.json"))
snap["note"] += (" Run 2026-11-02 00:01 WIB: HIVE 697 (+10, velocity still FAILS 0.66x, <20 tokens - outcome unchanged, no change report; still strong lead, NOT a candidate: X unverified), Bubblebruin 760/7777 = 9.77% verified free (still EARLY, age + X unverified, velocity still fails 0.27x; user slot USED by own mint 23:44 WIB), Zapcourier/Mothwraith/Cryonyx/Cathodex/Malabao first computable rates this run (3.36/2.76/2.80/3.31/3.14 per min; velocity NOT passed on velocity alone - no previous rate at run start; free % 17.7-25.7%, still far below 50% strong leg, X unverified), binanceai.fun still pending (launched false, totalShares 3093), hive-pollen still pending (launched false, pollenAgents 7463, slice ~13,399), BNBbaby still LEAD only (5908 shares, free 5661, slot open, NO X account found again - Track-C auto-mint NOT triggered, never previewed/minted), DOG still LEAD only (56 shares, FREE_SHARES 4000, slot open, no X), QILIN still checked-not-a-lead (user free used, freeCardsRemaining 584), SAFU Tower still checked-not-a-lead (freeClaimed total 3750). NEW: 1 EARLY lead Slimelings (agent-shaped ERC-721, first mints 23:48:59 WIB verified, 52 mints/46 minters, slot open by read, X unverified, free % unverified - never previewed/minted) and 2 NEW Track-C LEADS BNBPIG (sale 0xfd3d..., token BNBPIG, shares 1627, free 1554/5000, slot open, first Minted 21:38:37 WIB, NO X account - lead only) and SAMBARIO (sale 0xe15e..., token SAMBARIO/SAMBA, cards 11/7777, free 3322/3333, slot open, first token mint 23:24:26 WIB, NO X account - lead only). Oathbots Pass 0x1bB3... noted only, NOT a lead (holder-gated eligibleCollections/isHolder, no Agent ID registry/AgentGate evidence in ABI, age unverified, post itself flags a contract warning). SCAN SUCCEEDED: window 131083497-131085496 (2000 blocks, capped; skipped gap 131081442-131083496 recorded, never scanned), 80 Ankr calls, 0 errors, 412 NFT contracts, 3300 mints, 998 ERC20-mint contracts; first-seen triage: 129 first-seen, 15 verified+free/registry, all triaged as continuations (totals far above window mints) or free-exhausted (Subsonic Tribe 1111/1111) - no new early lead from scan; Slimelings appears in scan (41 window mints, first_block 131083738) but was already added via Sourcify, so no double report. Sourcify feed cross-check: same Slimelings + SAMBARIO sale in the 30-address poll (no double report). Track-C ERC-20 backlog: top 20 by window mint_count >=10 (skipping 30 previously checked + snapshot-known) shape-checked, 0 sale-shape passes (16 Sourcify-unverified, 4 verified non-sale); remainder beyond 20 dropped as sampling limit, stated. Watermark advanced to 131085496; seen file updated. NO track-A candidate, NO track-B opening/claim/block, NO track-C candidate - no auto-mint/auto-claim triggered (leads are never previewed/minted; early leads are never previewed/minted).")
json.dump(snap, open(H + "onchain-snapshot.json", "w"), indent=1)
print("snapshot note appended")
