#!/usr/bin/env python3
"""Main run 2026-11-02 16:01 WIB snapshot update (route 1 + promotions + sellouts + scan triage)."""
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
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1601.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1601-read.json"))
BLOCK = read["block"]
BT = blk_time(BLOCK)
print("main read block", BLOCK, "time", BT)
old_ts_wib = snap.get("timestamp_wib")
# interval from previous snapshot read time (lastReadWib of entries ~15:40) to BT, in minutes
def parse_wib(s):
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None
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
        v["velocityNote"] = f"Run 16:01 WIB (read block {BLOCK}): +{minted} tokens in ~{interval:.1f} min = {rate:.3f}/min, prev rate {old_rate} -> velocity {'PASSES' if passes else 'FAILS'}."
    v["supplyView"] = v.get("supplyView", "totalSupply")
# Promotions: Ghoulito + Zorith -> strong-lead gate-blocked
g = snap["contracts"]["Ghoulito"]
g["status"] = "strong-lead-gate-blocked-2026-11-02"
g["strongLeadLegsNote"] = ("Run 16:01 WIB: age verified (first mint 2026-11-02 14:54:45 WIB, ~1.7h) + free 160/313=51.12% verified "
    "(main read block 131215161, up from 119/313=38.02% at snapshot) + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint.")
g["gateNote"] = ("WEBSITE-ONLY GATE FAILED (methods A-G run 16:01: raw address search no site; Boltbook wave post LZFt0wIlrywp carries contracts only, no site/X links; "
    "Sourcify metadata has 0 URLs; no same-family site pattern with linkage; deployer group owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 factory wave; name search no site; DappBay AI category has no Ghoulito listing). X optional, absence not a blocker. DO NOT preview, DO NOT mint.")
z = snap["contracts"]["Zorith"]
z["status"] = "strong-lead-gate-blocked-2026-11-02"
z["totalSupply"] = 1635
z["freeMinted"] = 1635
z["freeLeft"] = 311
z["freePctVerified"] = 84.01
z["lastReadBlock"] = BLOCK
z["lastReadWib"] = BT
z["strongLeadLegsNote"] = ("Run 16:01 WIB: age verified (first mint 2026-11-02 15:00:26 WIB) + free 1635/1946=84.01% verified at fresh read "
    "(main read block 131215161: 1417/1946=72.82%, up from 360/1946=18.5% at snapshot) + slot open (freeAvailable(user)=2, freeClaimed(user)=0, hasAgentId=1, saleOpen=1, balance=0, AGENT_ID_REGISTRY on-chain) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint.")
z["gateNote"] = ("WEBSITE-ONLY GATE FAILED (methods A-G run 16:01: raw address search no BSC project hit, only unrelated Zora/Base tokens; name search no site; "
    "Sourcify metadata has 0 URLs; no Boltbook post naming Zorith found (scan-found); no same-family site pattern with linkage; no owner() view so deployer group unknown, which creates no website evidence; DappBay AI category has no Zorith listing). X optional, absence not a blocker. DO NOT preview, DO NOT mint.")
# Sellouts: remove Wispuff + Pelora, record in excluded
for nm, reason in [("Wispuff", "sold-out-2026-11-02: freeClaimed 340 = FREE_SUPPLY 340 at main read block 131215161 (was 332/340 at snapshot); totalSupply 348 incl paid mints"),
                   ("Pelora", "sold-out-2026-11-02: freeMinted 1946 = FREE_SUPPLY 1946, freeLeft 0, freeAvailable(user)=0 at fresh read after main read (main read: 1543/1946, freeLeft 403); early lead reported 15:01, never minted by user")]:
    if nm in snap["contracts"]:
        del snap["contracts"][nm]
    snap.setdefault("excluded", {})[nm] = reason
# New early leads
new_early = {
 "NeuralAtlas": {"address": "0xCe6392aF7Fd84e5AA8a77ED6636c45Bf756dAB94", "name": "NeuralAtlas", "symbol": "NATL", "kind": "ERC721",
   "totalSupply": 309, "freeClaimed": 304, "FREE_SUPPLY": 1319, "freePctVerified": 23.05, "mintOpen": True,
   "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
   "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed).",
   "firstSeenBlock": 131173198, "firstMintWib": "2026-11-02 11:00:04 WIB", "scanMints": 309, "scanMinters": 309,
   "lastReadBlock": BLOCK, "lastReadWib": BT, "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: 309 Transfer-from-zero logs = totalSupply 309, first block 131173198, 2026-11-02 11:00:04 WIB (paged Ankr walk from block 131060000). Sourcify verifiedAt 2026-11-02T09:02:43Z is verification time, NOT launch time. NOTE: contract was in main scan-seen since run 11:31 WIB as Sourcify-UNVERIFIED (registry-bytes hit only, no free shape) and was correctly NOT reported then; this run it verifies S1-literal (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + AGENT_ID registry on-chain), so it is reported as an early lead NOW, once.",
   "baselineNote": "EARLY lead reported once 2026-11-02 run 16:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI S1-literal + AGENT_ID() reads registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free 23.05%, far below 50%; X unverified; velocity not yet computable.",
   "status": "early-lead-reported-2026-11-02", "supplyView": "totalSupply"},
 "AgentMirage": {"address": "0xAB0e8a3E05B846dceBF2C93Fd5f8648B210Ba7D4", "name": "AgentMirage", "symbol": "MRGE", "kind": "ERC721",
   "totalSupply": 350, "freeClaimed": 297, "FREE_SUPPLY": 1326, "freePctVerified": 22.4, "mintOpen": True,
   "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
   "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed).",
   "firstSeenBlock": 131173207, "firstMintWib": "2026-11-02 11:00:08 WIB", "scanMints": 350, "scanMinters": 350,
   "lastReadBlock": BLOCK, "lastReadWib": BT, "xVerified": False, "velocityVerified": False,
   "launchNote": "First mint verified on-chain: 350 Transfer-from-zero logs vs totalSupply 349 at verify time (logs trail supply by 1, stated plainly), first block 131173207, 2026-11-02 11:00:08 WIB (paged Ankr walk from block 131060000). Sourcify verifiedAt 2026-11-02T09:02:36Z is verification time, NOT launch time. NOTE: same 11:31 scan-seen-unverified history as NeuralAtlas; reported as early lead NOW, once, on this run's S1 verification.",
   "baselineNote": "EARLY lead reported once 2026-11-02 run 16:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI S1-literal + AGENT_ID() reads registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free 22.40%, far below 50%; X unverified; velocity not yet computable.",
   "status": "early-lead-reported-2026-11-02", "supplyView": "totalSupply"},
}
scan_verify = json.load(open(BASE + "run-2026-11-02-1601-scan-early-verify.json"))
scan_first = json.load(open(BASE + "run-2026-11-02-1601-scan-early-first.json"))
scan_meta = {"Griffito": ("0x3a8b62d76900145Cb574315e01215c3b294ea402", "GRIFFITO", 53, 53, 131213155),
             "Niuniubo": ("0x200aC8776A5351C29c4D854012ffC1794a7DfA79", "NIUNIUBO", 51, 51, 131213158),
             "Witchibo": ("0x30e2ED57e433671907d7AEB01a7E7514e17FD649", "WITCHIBO", 49, 49, 131213161),
             "Circuitfox": ("0xD12B23694A910dBC74EF50aDBaC6aB4F6b34F55C", "CIRCUITFOX", 49, 49, 131213164),
             "Plutoko": ("0xF5Cf199D08A7B9bFE5C1Fc44ef5eabdae4314A56", "PLUTOKO", 46, 46, 131213179),
             "Orbitessa": ("0xF3278Ec0416cD913354b061dA5FBa23Ac84a5020", "ORBIT", 26, 26, 131213566),
             "Gloamwick": ("0x08c4804bd4a2bD04f993E4508354D23a7492e817", "GLOAM", 17, 17, 131213213)}
for nm, (addr, sym, sm, smn, sfb) in scan_meta.items():
    v = scan_verify[nm]; f = scan_first[nm]
    pct = round(100 * v["freeClaimed"] / v["FREE_SUPPLY"], 2) if v.get("freeClaimed") is not None and v.get("FREE_SUPPLY") else None
    owner_note = "owner()=0x190f1f0caff480e207f42586f9fbe4c691a27066 (deployer group 0x190f)" if nm in ("Griffito", "Niuniubo", "Witchibo", "Circuitfox", "Plutoko") else "owner()=0xd76d5918fb337667b22fe37ae2055b5542cf8dc9"
    new_early[nm] = {"address": addr, "name": nm, "symbol": sym, "kind": "ERC721",
        "totalSupply": v["totalSupply"], "freeClaimed": v["freeClaimed"], "FREE_SUPPLY": v["FREE_SUPPLY"], "freePctVerified": pct, "mintOpen": True,
        "userMintedBy": v["mintedBy"], "userFreeUsed": v["freeUsed"], "userBalance": v["balance"],
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balanceOf(user)=0 - NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": sfb, "firstMintWib": f["earliest_wib"], "scanMints": sm, "scanMinters": smn,
        "lastReadBlock": BLOCK, "lastReadWib": BT, "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: earliest Transfer-from-zero at block {f['earliest_block']}, {f['earliest_wib']} (paged Ankr walk from block 131150000; {f['logs_in_range']} logs in 131150000-131213153, none earlier in that range; scan-window first block was {sfb}). Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 16:01 WIB via on-chain scan route 4.",
        "baselineNote": f"EARLY lead reported once 2026-11-02 run 16:01 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify verified ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) + AGENT_ID() reads registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain; {owner_note}. Free {pct}%, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
        "status": "early-lead-reported-2026-11-02", "supplyView": "totalSupply"}
for nm, v in new_early.items():
    snap["contracts"][nm] = v
# pending claims + track_c numbers from main read
pc = snap.get("pending_claims", {})
if "binanceai.fun" in pc:
    pc["binanceai.fun"]["launched"] = False
    pc["binanceai.fun"]["tokenClaimed"] = False
    pc["binanceai.fun"]["totalShares"] = 3108
    pc["binanceai.fun"]["lastReadBlock"] = BLOCK
    pc["binanceai.fun"]["lastReadWib"] = BT
snap["timestamp_wib"] = BT
snap["note"] = ("Main run 16:01 WIB 2026-11-02: watchlist re-read block 131215161; scan window 131213154-131215153 (gap 131210321-131213153 skipped, 2833 blocks, cap 2000); "
    "new strong-lead gate-blocked: Ghoulito, Zorith (no preview/mint); sold out + removed: Wispuff, Pelora; new early leads (9): NeuralAtlas, AgentMirage, Griffito, Niuniubo, Witchibo, Circuitfox, Plutoko, Orbitessa, Gloamwick; "
    "track-B binanceai.fun still pending (launched false); route 5c 0 sale-shape pass.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]))
# scan-seen append
seen = json.load(open(BASE + "onchain-scan-seen.json"))
first = json.load(open(BASE + "run-2026-11-02-1601-scan-firstseen.json"))
added = 0
for c in first:
    if c["address"] not in seen["contracts"]:
        seen["contracts"][c["address"]] = {"first_seen_block": c.get("first_block"), "last_block": c.get("last_block"),
            "window": "131213154-131215153", "run": "2026-11-02-1601", "kind": c.get("kind"), "name": c.get("name"),
            "symbol": c.get("symbol"), "mint_count": c.get("mint_count"), "distinct_minters": c.get("distinct_minters")}
        added += 1
json.dump(seen, open(BASE + "onchain-scan-seen.json", "w"), indent=1)
print("scan-seen contracts:", len(seen["contracts"]), "added:", added)
# scan-state advance (scan succeeded, 0 errors)
state = json.load(open(BASE + "onchain-scan-state.json"))
state.update({"last_scanned_block": 131215153, "last_scan_window_from": 131213154, "last_scan_window_to": 131215153,
    "last_scan_wib": BT, "ankr_calls": 80, "errors": 0, "nft_contracts": 443, "erc20_mint_contracts": 749,
    "skipped_gap": "131210321-131213153 (2833 blocks, 2000-block cap)",
    "note": "Scan 16:01 run: 443 NFT contracts, 12081 NFT mints, 749 ERC-20 mint contracts, 80 Ankr calls, 0 errors. First-seen true: 20 (7 agent-shaped verified individually, 13 recorded only).",
    "last_scan_window": "131213154-131215153", "ankr_calls_last_scan": 80, "errors_last_scan": 0, "from_block": 131213154, "to_block": 131215153,
    "last_scan": BT, "last_scan_run": "2026-11-02-1601", "contracts_in_window": 443, "erc20_mint_contracts_in_window": 749})
json.dump(state, open(BASE + "onchain-scan-state.json", "w"), indent=1)
# track-c checked append
chk = json.load(open(BASE + "track-c-scan-checked.json"))
todo = json.load(open(BASE + "run-2026-11-02-1601-trackc-erc20-todo.json"))
before = len(chk.get("checked", []))
for x in todo:
    if x["address"] not in chk["checked"]:
        chk["checked"].append(x["address"])
chk["note"] = f"Run 16:01 WIB: 5c shape-check 20/20 fail (0 S1/S2); checked {before} -> {len(chk['checked'])}."
json.dump(chk, open(BASE + "track-c-scan-checked.json", "w"), indent=1)
print("track-c checked:", before, "->", len(chk["checked"]))
