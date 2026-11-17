#!/usr/bin/env python3
"""Main run 2026-11-02 17:01 WIB snapshot update (route 1 + promotions + sellouts + scan triage + 5c)."""
import json, sys, shutil, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def blk_time(bn):
    for ep in EPS:
        try:
            blk = _single(ep, "eth_getBlockByNumber", [hex(bn), False], 8, retries=0)
            ts = int(blk["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
        except Exception:
            pass
    return None
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1701.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1701-read.json"))
BLOCK = read["block"]
BT = blk_time(BLOCK)
print("main read block", BLOCK, "time", BT)
def parse_wib(s):
    try: return datetime.datetime.fromisoformat(s)
    except Exception: return None
new_dt = parse_wib(BT)
GEN = [("totalSupply()", "totalSupply"), ("freeClaimed()", "freeClaimed"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
       ("freeMinted()", "freeMinted"), ("freeLeft()", "freeLeft"), ("mintedBy(address)", "userMintedBy"),
       ("freeUsed(address)", "userFreeUsed"), ("balanceOf(address)", "userBalance")]
for name, v in snap["contracts"].items():
    if str(v.get("status", "")).startswith("minted-by-user"):
        continue
    if name not in read:
        continue
    r = read[name]
    old_ts = v.get("totalSupply")
    old_rate = v.get("currentRatePerMin")
    old_read_dt = parse_wib(v.get("lastReadWib") or "")
    interval = None
    if old_read_dt and new_dt:
        interval = (new_dt - old_read_dt).total_seconds() / 60.0
    for rk, sk in GEN:
        if r.get(rk) is not None:
            v[sk] = r[rk]
    fc, fs, fm, fl = v.get("freeClaimed"), v.get("FREE_SUPPLY"), v.get("freeMinted"), v.get("freeLeft")
    if fc is not None and fs:
        v["freePctVerified"] = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl):
        v["freePctVerified"] = round(100 * fm / (fm + fl), 2)
    v["previousTotalSupply"] = old_ts
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = BT
    if old_ts is not None and v.get("totalSupply") is not None and interval:
        minted = v["totalSupply"] - old_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = round(interval, 2)
        rate = minted / interval if interval else 0
        v["currentRatePerMin"] = round(rate, 3)
        v["previousRatePerMin"] = old_rate
        passes = (old_rate is not None and old_rate > 0 and rate >= 1.5 * old_rate and minted >= 20)
        v["velocityLegPasses"] = bool(passes)
        v["velocityNote"] = f"Run 17:01 WIB (read block {BLOCK}): +{minted} tokens in ~{interval:.1f} min = {rate:.3f}/min, prev rate {old_rate} -> velocity {'PASSES' if passes else 'FAILS'}."
    v["supplyView"] = v.get("supplyView", "totalSupply")
# --- Promotions to strong-lead gate-blocked ---
GATE_NOTE_COMMON = ("WEBSITE-ONLY GATE FAILED (methods A-G run 17:01: raw address search no project site; name search no project site; "
    "Sourcify metadata 0 external URLs; no same-family site pattern with linkage; no candidate site whose /llms.txt or /skill.md to check; "
    "DappBay AI category checked, no listing (absence proves nothing); X optional under 2026-11-02 ~14:14 WIB amendment, absence not a blocker. "
    "DO NOT preview, DO NOT mint.")
promoters = {
 "Krakenbo": ("Run 17:01 WIB: age verified (first mint 2026-11-02 07:22:29 WIB, ~10h) + free 453/903=50.17% verified (main read block 131222308, up from 438/903=48.50% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Deployer group owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 factory wave, not exempt."),
 "Gongxibao": ("Run 17:01 WIB: age verified (first mint 2026-11-02 14:54:43 WIB, ~2.3h) + free 176/327=53.82% verified (main read block 131222308, up from 143/327=43.73% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Deployer group owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 factory wave (Boltbook wave post LZFt0wIlrywp carries contracts only, no site/X links), not exempt."),
 "Nightsable": ("Run 17:01 WIB: age verified (first mint 2026-11-02 01:10:59 WIB, ~16h) + free 397/794=50.00% verified (main read block 131222308, up from 396/794=49.87% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Already reported as gate-blocked by hot-leg 16:29 WIB (parent-verified); this run only updates snapshot status, does NOT re-report. Deployer owner()=0xa054275580c6d1c9077543907ac5798f2494ecce."),
 "NightshadeClub": ("Run 17:01 WIB: age verified (first mint 2026-11-01 09:27:57 WIB, ~32h) + free 493/983=50.15% verified (main read block 131222308, up from 489/983=49.75% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Already reported as gate-blocked by hot-leg 16:29 WIB; this run only updates snapshot status, does NOT re-report. Deployer owner()=0x8a3b31dd69c6ab76b2dda2711b32eaad8646e173."),
 "Neonfawn": ("Run 17:01 WIB: age verified (first mint 2026-11-02 14:54:46 WIB, ~2.3h) + free 182/310=58.71% verified (main read block 131222308, up from 151/310=48.71% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Already reported as gate-blocked by hot-leg 16:19 WIB; this run only updates snapshot status, does NOT re-report. Deployer group owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 factory wave, not exempt."),
 "Nanobee": ("Run 17:01 WIB: age verified (first mint 2026-11-02 14:54:49 WIB, ~2.3h) + free 174/330=52.73% verified (main read block 131222308, up from 148/330=44.85% at snapshot) "
    "+ slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Already reported as gate-blocked by hot-leg 16:49/16:58 WIB (parent-verified); this run only updates snapshot status, does NOT re-report. Deployer group owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 factory wave, not exempt."),
}
for nm, note in promoters.items():
    if nm in snap["contracts"]:
        snap["contracts"][nm]["status"] = "strong-lead-gate-blocked-2026-11-02"
        snap["contracts"][nm]["strongLeadLegsNote"] = note
        snap["contracts"][nm]["gateNote"] = GATE_NOTE_COMMON
# --- Sold-out removals ---
for nm, reason in [
    ("Zorith", "sold-out-2026-11-02: freeMinted 1946 = FREE_SUPPLY 1946, freeLeft 0 at main read block 131222308 (was 1635/1946 at snapshot); previously strong-lead gate-blocked, reported 16:01 WIB"),
    ("Varion", "sold-out-2026-11-02: freeMinted 1946 = FREE_SUPPLY 1946, freeLeft 0 at main read block 131222308 (was 735/1946 at snapshot); early lead reported 15:01 WIB, never minted by user"),
    ("Chimerito", "sold-out-2026-11-02: freeClaimed 332 = FREE_SUPPLY 332 at main read block 131222308; already reported sold out by hot-leg 16:39 WIB, main run only removes from snapshot, does NOT re-report"),
    ("Mercubo", "sold-out-2026-11-02: freeClaimed 303 = FREE_SUPPLY 303 at main read block 131222308; already reported sold out by hot-leg 16:39 WIB, main run only removes, does NOT re-report"),
    ("Vampibo", "sold-out-2026-11-02: freeClaimed 313 = FREE_SUPPLY 313 at main read block 131222308; already reported sold out by hot-leg 16:39 WIB, main run only removes, does NOT re-report"),
    ("Neonpanda", "sold-out-2026-11-02: freeClaimed 302 = FREE_SUPPLY 302 at main read block 131222308; already reported sold out by hot-leg 16:29 WIB, main run only removes, does NOT re-report"),
]:
    if nm in snap["contracts"]:
        del snap["contracts"][nm]
    snap.setdefault("excluded", {})[nm] = reason
# Jin Agent: free pool exhausted, user eligibility 0 -> excluded (never a lead)
snap.setdefault("excluded", {})["Jin Agent"] = ("free-pool-exhausted-2026-11-02: sale/token 0x086Ab11dF23e8FD37398C41180466D24d85ed5FB (JIN, site jin-agent.online per Boltbook post) freeMinted 4444 = FREE_CAP 4444; "
    "eligibility(user,'6am'/'masgayut'/'masgayut.ai') = identity 0, 0, 0; paid lane 67/10000 at PRICE 0.002 BNB (paid-only now). Boltbook triage only, never a lead, never previewed/minted.")
# --- New early leads (scan route 4) ---
verify = json.load(open(BASE + "run-2026-11-02-1701-scan-early-verify.json"))
first = json.load(open(BASE + "run-2026-11-02-1701-scan-early-first.json"))
scan = json.load(open(BASE + "run-2026-11-02-1701-scan-firstseen.json"))
scan_by_addr = {c["address"].lower(): c for c in scan}
extra_notes = {
 "Fenara": "Free % UNVERIFIED (no freeClaimed/FREE_SUPPLY view on this template; totalMinted 228 = 228 Transfer logs, FREE_WALLET_LIMIT 222, freeWalletsUsed 222 = limit reached, so the free-wallet lane reads EXHAUSTED for new wallets; mintedBy(user)=0, freeUsed(user)=0, balance=0, mintOpen=1; quote view reverts). Early lead only; never previewed/minted.",
 "Kigae": "Free 98/2024=4.84% verified via freeMinted/FREE_SUPPLY (freeLeft 1926, pool open); user-specific free view UNVERIFIED (mintedBy/freeUsed/freeMinted(address) revert; hasAgentId(user)=1; quote(user,1)=0.0009 BNB reads as the paid price, not the free cost). Early lead only; never previewed/minted.",
}
for nm in ["Fenara", "Glasscore", "Kigae", "Gourdwitch", "Gargrowl", "Neonpurrix", "Qilinara", "Wraithmoth"]:
    v = verify[nm]; f = first[nm]; sc = scan_by_addr[v and ""] if False else None
    sc = None
    for c in scan:
        if c["address"].lower() == {"Fenara": "0x857e3c15985a0c0bb0de11f18459390d754a10da", "Glasscore": "0xe2826b507da79a642aa1fce108aa8dd11ce67e3f", "Kigae": "0x33fd00af8bff3db611d3222d394da33eaaa6a566", "Gourdwitch": "0x30405b8442cf2f1c488f256a8df12e1a2e22e581", "Gargrowl": "0x2bd4983c8f5e734d6e24d4dba04f4c722a88f9df", "Neonpurrix": "0xd2136c5af996d264414cbf981e7b1804ba80177c", "Qilinara": "0x46d0ee06a3b919091b006d7818c3ae405e0f3774", "Wraithmoth": "0x6575c26173d8a18ad4823aaf3b0906de2ff1b568"}[nm]:
            sc = c
    pct = round(100 * v["freeClaimed"] / v["FREE_SUPPLY"], 2) if v.get("freeClaimed") is not None and v.get("FREE_SUPPLY") else None
    if nm == "Kigae": pct = 4.84
    addr = {"Fenara": "0x857e3C15985A0c0bB0De11F18459390D754A10DA", "Glasscore": "0xe2826b507Da79a642aa1fce108Aa8dD11cE67e3f", "Kigae": "0x33fd00aF8bfF3db611D3222D394da33eaaa6a566", "Gourdwitch": "0x30405B8442Cf2F1C488F256A8DF12e1A2e22E581", "Gargrowl": "0x2BD4983c8f5E734D6E24d4Dba04F4C722a88F9DF", "Neonpurrix": "0xd2136C5aF996D264414cbF981E7B1804ba80177C", "Qilinara": "0x46d0eE06a3b919091B006D7818C3Ae405E0f3774", "Wraithmoth": "0x6575c26173d8A18Ad4823Aaf3b0906DE2ff1B568"}[nm]
    reg = [v.get(k) for k in ("AGENT_ID", "AGENT_ID_REGISTRY", "AGENT_REGISTRY", "agentRegistry") if v.get(k)]
    snap["contracts"][nm] = {
        "address": addr, "name": v.get("name"), "symbol": v.get("symbol"), "kind": "ERC721",
        "totalSupply": v.get("totalSupply"), "freeClaimed": v.get("freeClaimed"), "FREE_SUPPLY": v.get("FREE_SUPPLY"),
        "freePctVerified": pct, "mintOpen": True,
        "userMintedBy": v.get("mintedBy"), "userFreeUsed": v.get("freeUsed"), "userBalance": v.get("balance"),
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed)." if nm not in extra_notes else extra_notes[nm],
        "firstSeenBlock": sc["first_block"] if sc else f["first_block"], "scanMints": sc["mint_count"] if sc else None,
        "scanMinters": sc["distinct_minters"] if sc else None,
        "lastReadBlock": BLOCK, "lastReadWib": BT, "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: {f['count']} Transfer-from-zero logs in Ankr walk from block 131150000, first block {f['first_block']}, {f['first_wib']} (scan-window first block was {sc['first_block'] if sc else 'n/a'}). Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 17:01 WIB via on-chain scan route 4.",
        "baselineNote": f"EARLY lead reported once 2026-11-02 run 17:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY, template family) and registry read {reg} = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free {pct}%, below 50% or unverified; X unverified; velocity not yet computable (first baseline stored this run).",
        "status": "early-lead-reported-2026-11-02", "supplyView": "totalSupply" if v.get("totalSupply") is not None else "totalMinted",
    }
    if nm == "Fenara":
        snap["contracts"][nm]["totalMinted"] = 228
        snap["contracts"][nm]["freeWalletsUsed"] = 222
        snap["contracts"][nm]["FREE_WALLET_LIMIT"] = 222
    if nm == "Kigae":
        snap["contracts"][nm]["freeMinted"] = 98
        snap["contracts"][nm]["freeLeft"] = 1926
# pending claims + track_c numbers from main read
pc = snap.get("pending_claims", {})
if "binanceai.fun" in pc:
    pc["binanceai.fun"]["launched"] = False
    pc["binanceai.fun"]["tokenClaimed"] = False
    pc["binanceai.fun"]["totalShares"] = 3110
    pc["binanceai.fun"]["lastReadBlock"] = BLOCK
    pc["binanceai.fun"]["lastReadWib"] = BT
if "hive-pollen" in pc:
    pc["hive-pollen"]["launched"] = False
    pc["hive-pollen"]["phase"] = 1
    pc["hive-pollen"]["pollenAgents"] = 7762
    pc["hive-pollen"]["paidSold"] = 1035
    pc["hive-pollen"]["lastReadBlock"] = BLOCK
    pc["hive-pollen"]["lastReadWib"] = BT
snap["timestamp_wib"] = BT
snap["note"] = ("Main run 17:01 WIB 2026-11-02: watchlist re-read block 131222308; scan window 131220276-131222275 (gap 131215154-131220275 skipped, 5122 blocks, cap 2000); "
    "new strong-lead gate-blocked reported once: Krakenbo, Gongxibao (Nightsable/NightshadeClub/Neonfawn/Nanobee already gate-blocked by hot-leg, status updated only, not re-reported); "
    "sold out + removed, reported once: Zorith, Varion (Chimerito/Mercubo/Vampibo/Neonpanda already sold-out-reported by hot-leg, removed silently); "
    "new early leads (8): Fenara, Glasscore, Kigae, Gourdwitch, Gargrowl, Neonpurrix, Qilinara, Wraithmoth; "
    "track-B binanceai.fun + hive-pollen still pending (launched false); Jin Agent free pool exhausted (excluded); HONGBAO slot already used (no re-report); route 5c 0 sale-shape pass.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]))
# scan-seen append (23 first-seen)
seen = json.load(open(BASE + "onchain-scan-seen.json"))
first_seen = json.load(open(BASE + "run-2026-11-02-1701-scan-firstseen.json"))
added = 0
for c in first_seen:
    if c["address"] not in seen["contracts"]:
        seen["contracts"][c["address"]] = {"first_seen_block": c.get("first_block"), "last_block": c.get("last_block"),
            "window": "131220276-131222275", "run": "2026-11-02-1701", "kind": c.get("kind"), "name": c.get("name"),
            "symbol": c.get("symbol"), "mint_count": c.get("mint_count"), "distinct_minters": c.get("distinct_minters")}
        added += 1
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
print("scan-seen contracts:", len(seen["contracts"]), "added:", added)
# scan-state advance (scan succeeded, 0 errors)
state = json.load(open(BASE + "onchain-scan-state.json"))
state.update({"last_scanned_block": 131222275, "last_scan_window_from": 131220276, "last_scan_window_to": 131222275,
    "last_scan_wib": BT, "ankr_calls": 80, "errors": 0, "nft_contracts": 352, "erc20_mint_contracts": 657,
    "skipped_gap": "131215154-131220275 (5122 blocks, 2000-block cap)",
    "note": "Scan 17:01 run: 352 NFT contracts, 657 ERC-20 mint contracts, 80 Ankr calls, 0 errors. First-seen true: 23 (8 agent-shaped verified individually, 15 recorded only).",
    "last_scan_window": "131220276-131222275", "ankr_calls_last_scan": 80, "errors_last_scan": 0, "from_block": 131220276, "to_block": 131222275,
    "last_scan": BT, "last_scan_run": "2026-11-02-1701", "contracts_in_window": 352, "erc20_mint_contracts_in_window": 657})
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
# track-c checked append
chk = json.load(open(BASE + "track-c-scan-checked.json"))
todo = json.load(open(BASE + "run-2026-11-02-1701-trackc-erc20-todo.json"))
before = len(chk.get("checked", []))
for x in todo:
    if x["address"] not in chk["checked"]:
        chk["checked"].append(x["address"])
chk["note"] = f"Run 17:01 WIB: 5c shape-check 20/20 fail (0 S1/S2); checked {before} -> {len(chk['checked'])}."
json.dump(chk, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("track-c checked:", before, "->", len(chk["checked"]))
