#!/usr/bin/env python3
"""Merge run 0601 into onchain-snapshot.json. Writes snapshot (backup first)
+ run-2026-11-08-0601-merge.json (audit record)."""
import json, shutil, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re_ = json.load(open(f"{BASE}/run-2026-11-08-0601-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-08-0601-velocity.json"))
vel_rows = {r["name"]: r for r in vel["rows"]}
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261108-0601")
audit = {"run": "0601", "removed": {}, "added": [], "updated_war3": {}, "notes": []}
# --- 1. numeric refresh for all re-read contracts ---
n_upd = 0
for name, d in re_["reread"].items():
    c = snap["contracts"].get(name)
    if not isinstance(c, dict):
        continue
    v = vel_rows.get(name, {})
    prev_ts = c.get("totalSupply")
    cur = d.get("totalSupply")
    if cur is None:
        cur = d.get("totalMinted")
    if cur is not None:
        c["previousTotalSupply"] = prev_ts
        c["totalSupply"] = cur
    if d.get("balanceOf_user") is not None:
        c["balanceOf_user"] = d["balanceOf_user"]
    c["lastReadBlock"] = re_["block"]
    c["lastReadWib"] = "2026-11-08 run 0601"
    if v:
        c["mintedInInterval"] = v.get("mintedInInterval")
        c["currentRatePerMin"] = v.get("ratePerMin")
        c["previousRatePerMin"] = v.get("prevRatePerMin")
        c["velocityRatio"] = v.get("ratioVsPrev")
        c["velocityLegPasses"] = v.get("velocityPasses")
    n_upd += 1
audit["notes"].append(f"numeric refresh: {n_upd} contracts from 0601 re-read (block {re_['block']})")
# --- 2. WAR3 minted-by-user ---
w = snap["contracts"]["WAR3-1aa9"]
w["status"] = "minted-by-user-2026-11-08"
w["mintTx"] = "0xb77e8f27014d7b14ab8d35ad403bc4aa7adeab219b6a7d386366f7a1cd911b9b"
w["mintBlock"] = 132287716
w["mintGas"] = 206841
w["mintTokenId"] = 2511
w["totalSupply"] = 2516
w["freeMinted"] = 2327
w["balanceOf_user"] = 1
w["userBalance"] = 1
w["ww3_balance_user"] = 10000
w["ww3_contract"] = "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0"
w["rarity0601"] = "Tier Unrevealed (tokenURI https://war3.xyz/meta/unrevealed.json; reveal after mint window ends 2026-11-12 14:22:01 WIB)"
w["marketplace0601"] = "No live venue (war3.xyz FAQ: No built-in marketplace; Element fallback not verified contract-matched) - NOT listed"
w["runNote0601"] = ("Run 0601: MINT BERHASIL run 0501 (tx 0xb77e8f..., blok 132287716, gas 206841, "
  "token #2511, +10.000 WW3); verifikasi pasca-mint run 0601: ownerOf(2511)=agent, balanceOf=1, "
  "WW3=10.000, totalSupply 2516, freeMinted 2327 (blok 132288992). Rarity Unrevealed; marketplace tidak ada venue live.")
audit["updated_war3"] = {k: w[k] for k in ("status", "mintTx", "mintBlock", "mintGas", "mintTokenId", "balanceOf_user")}
# --- 3. age-exclusion removals ---
for name, reason in [
  ("KING Agent", "first mint 2026-11-06 04:31:20 WIB, age 50.5h >48h at run 0601; status strong-lead-gate-blocked-2026-11-06; not sold out (totalMinted last verified 976/10000, remainingFree 2357)"),
  ("FOD Agent", "first mint 2026-11-06 05:42:23 WIB, age 49.3h >48h at run 0601; status early-lead-reported-2026-11-06"),
]:
    if name in snap["contracts"]:
        audit["removed"][name] = {"entry": snap["contracts"].pop(name), "reason": reason}
        audit["notes"].append(f"REMOVED age-excluded: {name} - {reason}")
# --- 4. add Ghostling + Voltoad (strong-lead legs pass, gate FAILED) ---
gate_methods = ("(A) raw-address search: no site (unrelated BaseScan noise); (B) Boltbook post 1328.ai 6awBVCCNUkeV: no links, author states no website/X, skip under hard gate; "
  "(C) Sourcify metadata: no URLs; (D) same-family (Voltoad/Dinobyte/Saturnagent/Thetavox template): no site; (E) owner 0x53043412... (live EOA, group Voltoad+Ghostling): no site; "
  "(G) name search: no Ghostling site; (H) contractURI base64: no external_link; (I) tokenURI: no external_url; (J) ABI grep: no website/siteURL/domain/external fns; "
  "(K) GitHub code search: search-index noise only; (L) BscScan token page (live browser 06:51-06:54 WIB): no Website, no social links, only 'Click here to update token information'; "
  "(M) site:vercel.app/pages.dev/deed.page/surge.sh: no hit; (N) registry-profile hop: not applicable, author post already states no website")
snap["contracts"]["Ghostling"] = {
  "address": "0x6a4847cb5f658943222fbd23d2520049f824789d",
  "status": "strong-lead-gate-blocked-2026-11-08",
  "name": "Ghostling", "symbol": "GHOSTLING", "kind": "ERC721",
  "totalSupply": 3757, "freeClaimed": 3757, "FREE_SUPPLY": 7000, "MAX_SUPPLY": 7777,
  "freePctVerified": 53.67, "mintOpen": True,
  "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
  "userSlotNote": "Slot open: freeLeft(user)=3, freeUsed(user)=0, mintedBy(user)=0, freeFor(user,1)=1, quote(user,1)=0, balance 0 (blok 132290038 hot-leg 0619; run 0601 totalSupply 3757/freeClaimed 3757)",
  "firstSeenBlock": 131912632,
  "firstMintWib": "2026-11-06 07:27:17 WIB",
  "ageHoursAt0601": 47.3,
  "lastReadBlock": 132288992, "lastReadWib": "2026-11-08 run 0601",
  "xVerified": False, "velocityVerified": False,
  "launchNote": "First mint verified on-chain run 0601: first Transfer-from-zero at block 131912632, 2026-11-06 07:27:17 WIB (Ankr getLogs binary search + chunked verification 0 mint in [131906767,131912631]); Sourcify verifiedAt 2026-10-29T12:27:53Z (verification time, NOT launch time). Age window closes 2026-11-08 07:27:17 WIB.",
  "baselineNote": "Strong-lead legs PASS run 0601 (age 47.3h <=48h verified, free 3757/7000=53.67% verified, slot user open) BUT MANDATORY WEBSITE GATE FAILED - no preview, no mint. Reported once run 0601. Sourcify exact_match; AGENT_ID()=registry 0x60B926...22F (hot-leg 0619). Owner 0x53043412c4F2436f68e56bB9638EbEBB099Fb3C1 (same as Voltoad); owner-only withdraw()/setMintOpen()/setRoyalty() per 1328.ai source review - secondary risk, audit never run (gate fails first). PRICE 0.00005 BNB paid lane; FREE_PER_WALLET 3.",
  "gateStatus": "FAILED - no verified website",
  "gateMethods0601": gate_methods,
  "supplyView": "totalSupply",
}
snap["contracts"]["Voltoad"] = {
  "address": "0xbc95e0a5bb1305958ba3263c6e9943b7a2554757",
  "status": "strong-lead-gate-blocked-2026-11-08",
  "name": "Voltoad", "symbol": "VOLTOAD", "kind": "ERC721",
  "totalSupply": 4440, "freeClaimed": 4440, "FREE_SUPPLY": 7000, "MAX_SUPPLY": 7777,
  "freePctVerified": 63.43, "mintOpen": True,
  "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
  "userSlotNote": "Slot open: freeLeft(user)=3, freeUsed(user)=0, quote(user,1)=0, balance 0 (run 0601 fresh read)",
  "firstSeenBlock": 131912458,
  "firstMintWib": "2026-11-06 07:25:59 WIB",
  "ageHoursAt0601": 47.4,
  "lastReadBlock": 132288992, "lastReadWib": "2026-11-08 run 0601",
  "xVerified": False, "velocityVerified": False,
  "launchNote": "First mint verified on-chain run 0601: first Transfer-from-zero at block 131912458, 2026-11-06 07:25:59 WIB (Ankr getLogs binary search + chunked verification 0 mint in [131906767,131912457]). Age window closes 2026-11-08 07:25:59 WIB.",
  "baselineNote": "Strong-lead legs PASS run 0601 (age 47.4h <=48h verified, free 4440/7000=63.43% verified, slot user open) BUT MANDATORY WEBSITE GATE FAILED (run 0501 methods A-G: no site; same owner/template as Ghostling) - no preview, no mint. Reported once run 0601. Sourcify exact_match (verified 2026-10-29). Owner 0x53043412...; owner-only withdraw() can drain contract BNB; setMintOpen()/setRoyalty() owner-controlled (1328.ai source review).",
  "gateStatus": "FAILED - no verified website (run 0501 A-G + family evidence run 0601)",
  "supplyView": "totalSupply",
}
audit["added"].append("Ghostling")
audit["added"].append("Voltoad")
# --- 5. add Agent Goats (watchlist-only) ---
snap["contracts"]["Agent Goats"] = {
  "address": "0x0e9e0a3b46dc0d36a1ab64f553dd8a0693e6aaa6",
  "status": "watchlist-only-age-unverified-2026-11-08",
  "name": "Agent Goats", "symbol": None, "kind": "ERC721",
  "totalSupply": 654, "freeClaimed": 655, "FREE_SUPPLY": 1111, "MAX_SUPPLY": 2222,
  "freePctVerified": 58.96, "mintOpen": True,
  "userMintedBy": 0, "userFreeUsed": None, "userBalance": 0,
  "userSlotNote": "Slot UNVERIFIED: quote()/freeLeft()/freeUsed()/freeFor() all revert (functions absent); mintedBy(user)=0 + balance 0 only. Boltbook author claims mint(1) value-0 eth_call passes - NOT independently verified.",
  "lastReadBlock": 132292272, "lastReadWib": "2026-11-08 run 0601",
  "xVerified": False, "velocityVerified": False,
  "launchNote": "Launch time UNVERIFIED (no project-stated launch time; first-mint check not done run 0601). Boltbook post ~06:23 WIB: 650/1111, ~14/h crawl.",
  "baselineNote": "Boltbook lead run 0601 (front page EN+ZH). Free counter 655/1111=58.96% (note: freeClaimed 655 > totalSupply 654 by 1 - counter quirk, stated plainly). Age + slot unverified -> watchlist-only, NOT early (not first-seen minting), NOT strong lead, no report, no preview/mint. Owner 0x23f5cdd233925ea83369a495b95f825ed710fbaa.",
  "supplyView": "totalSupply",
}
audit["added"].append("Agent Goats")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
json.dump(audit, open(f"{BASE}/run-2026-11-08-0601-merge.json", "w"), indent=1)
print("MERGE DONE contracts:", len(snap["contracts"]), "removed:", list(audit["removed"].keys()), "added:", audit["added"])
print("WAR3:", audit["updated_war3"])
