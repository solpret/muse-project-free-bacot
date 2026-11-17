#!/usr/bin/env python3
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
# --- scan seen: append 14 first-seen ---
seen = json.load(open(BASE + "onchain-scan-seen.json"))
firstseen = json.load(open(BASE + "run-2026-11-03-0131-scan-firstseen.json"))
contracts = seen.setdefault("contracts", {})
if isinstance(contracts, list):
    contracts = {c: {} for c in contracts}
    seen["contracts"] = contracts
for c in firstseen:
    contracts[c["address"]] = {"first_seen_block": 131287526, "first_seen_wib": "2026-11-03T01:33:00+07:00",
        "mint_count_window": c.get("mint_count"), "distinct_minters": c.get("distinct_minters"),
        "symbol": c.get("symbol"), "name": c.get("name"), "sourcify": c.get("sourcify"), "source": "onchain-scan-2026-11-03-0131"}
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
print("seen contracts now:", len(contracts))
# --- scan state: advance watermark to head scanned, record gap ---
state = json.load(open(BASE + "onchain-scan-state.json"))
scan = json.load(open(BASE + "onchain-scan-2026-11-03-0131.json"))
prev_gap = state.get("skipped_gap", "")
new_gap = "131285648-131287525 (1878 blocks, window capped at 2000; scan covered only most recent 2000 blocks 131287526-131289525)"
state["last_scanned_block"] = scan["to_block"]
state["last_scan_window_from"] = scan["from_block"]
state["last_scan_window_to"] = scan["to_block"]
state["last_scan_wib"] = "2026-11-03T01:44:00+07:00"
state["ankr_calls"] = scan["ankr_calls"]
state["errors"] = scan["errors"]
state["nft_contracts"] = len(scan["contracts"])
state["erc20_mint_contracts"] = scan["erc20_mint_contracts"]
state["skipped_gap"] = (prev_gap + " ; " + new_gap) if prev_gap else new_gap
state["note"] = ("Scan 0131 run: window 131287526-131289525 (cap 2000 blocks; head-last=3862), 80 Ankr calls, 0 errors, "
                 "350 NFT contracts, 706 ERC-20 mint contracts. First-seen new: 14 (2 agent-shaped early leads Opera/Silk).")
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
print("state last_scanned_block:", state["last_scanned_block"])
# --- track-c checked: add 20 from 5c ---
tc = json.load(open(BASE + "track-c-scan-checked.json"))
checked = tc.setdefault("checked", {})
if isinstance(checked, list):
    checked = {a: {} for a in checked}; tc["checked"] = checked
shape = json.load(open(BASE + "run-2026-11-03-0131-trackc-5c.json"))
for a, v in shape.items():
    checked[a] = {"checked_wib": "2026-11-03T01:33:00+07:00", "source": "scan-0131-5c", "result": v.get("status")}
json.dump(tc, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("track-c checked now:", len(checked))
# --- snapshot: add Opera + Silk early leads ---
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap["contracts"]["Opera Agent"] = {
  "address": "0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c", "name": "Opera Agent", "symbol": "OPERA", "kind": "ERC721",
  "status": "early-lead-reported-2026-11-03", "totalMinted": 162, "FREE_SUPPLY": 460, "MAX_SUPPLY": 1842,
  "freePctNote": "totalMinted 162/460 FREE_SUPPLY = 35.22% (totalMinted-based; no freeClaimed view; costFor(1)=0 supports free lane, NOT a verified free counter)",
  "mintOpen": True, "userMintedBy": 0, "userBalance": 0,
  "firstSeenBlock": 131287764, "firstMintWib": "2026-11-03T01:19:34+07:00",
  "launchNote": "First mint VERIFIED on-chain: pre-window walk 131260000-131287525 found 0 from-zero mints; window first Transfer-from-zero block 131287764, 2026-11-03 01:19:34 WIB, tx 0x5279dbef7b9dbc698467b8f270a91a96319216c43ee76709927ed3be99e72921; window mints 109/53 minters (scan), fresh totalMinted 162 at block 131291325.",
  "baselineNote": "EARLY lead run 0131 (never previewed/minted). Agent-shape verified: Sourcify verified ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry). X unverified, website unverified (raw-address search -> unrelated Opera browser results only). Velocity not yet computable (first run).",
  "lastReadBlock": 131291325, "lastReadWib": "2026-11-03T01:33:00+07:00", "xVerified": False, "velocityVerified": False}
snap["contracts"]["Silk Agent"] = {
  "address": "0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e", "name": "Silk Agent", "symbol": "SILK", "kind": "ERC721",
  "status": "early-lead-reported-2026-11-03", "totalMinted": 90, "FREE_SUPPLY": 387, "MAX_SUPPLY": 1549,
  "freePctNote": "totalMinted 90/387 FREE_SUPPLY = 23.26% (totalMinted-based; no freeClaimed view; costFor(1)=0 supports free lane, NOT a verified free counter)",
  "mintOpen": True, "userMintedBy": 0, "userBalance": 0,
  "firstSeenBlock": 131288516, "firstMintWib": "2026-11-03T01:25:13+07:00",
  "launchNote": "First mint VERIFIED on-chain: pre-window walk 131260000-131287525 found 0 from-zero mints; window first Transfer-from-zero block 131288516, 2026-11-03 01:25:13 WIB, tx 0xfebeb980d00c8f5353bf0574baf90dc2db6153ec9e1982e2ffb17c9f9a40a97b; window mints 58/18 minters (scan), fresh totalMinted 90 at block 131291325.",
  "baselineNote": "EARLY lead run 0131 (never previewed/minted). Agent-shape verified: Sourcify verified ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry). X unverified, website unverified (raw-address search -> unrelated results only). Velocity not yet computable (first run).",
  "lastReadBlock": 131291325, "lastReadWib": "2026-11-03T01:33:00+07:00", "xVerified": False, "velocityVerified": False}
snap["timestamp_wib"] = "2026-11-03T01:33:00+07:00"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot contracts now:", len(snap["contracts"]))
