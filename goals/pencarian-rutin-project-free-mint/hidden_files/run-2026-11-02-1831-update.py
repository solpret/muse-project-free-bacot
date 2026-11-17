#!/usr/bin/env python3
import json, shutil, datetime, sys
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
        except Exception: pass
    return None
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1831.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1831-read.json"))
BLOCK = read["block"]; BT = blk_time(BLOCK)
print("main read block", BLOCK, "time", BT)
def parse_wib(s):
    try: return datetime.datetime.fromisoformat(s)
    except Exception: return None
new_dt = parse_wib(BT)
GEN = [("totalSupply()", "totalSupply"), ("freeClaimed()", "freeClaimed"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
       ("freeMinted()", "freeMinted"), ("freeLeft()", "freeLeft"), ("mintedBy(address)", "userMintedBy"),
       ("freeUsed(address)", "userFreeUsed"), ("balanceOf(address)", "userBalance")]
vel_pass=[]
for name, v in snap["contracts"].items():
    if str(v.get("status", "")).startswith("minted-by-user"): continue
    if name not in read: continue
    r = read[name]
    old_ts = v.get("totalSupply"); old_rate = v.get("currentRatePerMin")
    old_read_dt = parse_wib(v.get("lastReadWib") or "")
    interval = (new_dt - old_read_dt).total_seconds() / 60.0 if (old_read_dt and new_dt) else None
    for rk, sk in GEN:
        if r.get(rk) is not None: v[sk] = r[rk]
    fc, fs, fm, fl = v.get("freeClaimed"), v.get("FREE_SUPPLY"), v.get("freeMinted"), v.get("freeLeft")
    if fc is not None and fs: v["freePctVerified"] = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl): v["freePctVerified"] = round(100 * fm / (fm + fl), 2)
    v["previousTotalSupply"] = old_ts
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = BT
    if old_ts is not None and v.get("totalSupply") is not None and interval:
        minted = v["totalSupply"] - old_ts
        v["mintedInInterval"] = minted; v["intervalMinutes"] = round(interval, 2)
        rate = minted / interval if interval else 0
        v["currentRatePerMin"] = round(rate, 3); v["previousRatePerMin"] = old_rate
        passes = (old_rate is not None and old_rate > 0 and rate >= 1.5 * old_rate and minted >= 20)
        v["velocityLegPasses"] = passes
        v["velocityNote"] = f"Run 18:31 WIB (read block {BLOCK}): +{minted} tokens in ~{interval:.2f} min = {rate:.3f}/min, ratio vs prior {old_rate} = {(rate/old_rate if old_rate else None)} -> velocity leg {'PASSES' if passes else 'FAILS'}."
        if passes: vel_pass.append((name, minted, round(rate,3), old_rate))
print("velocity passes:", vel_pass)
# Plutoko promotion -> gate-blocked strong lead (gate checked A-G, no preview/mint)
pl = snap["contracts"]["Plutoko"]
pl["status"] = "strong-lead-gate-blocked-2026-11-02"
pl["baselineNote"] = "PROMOTED to strong lead in run 18:31 WIB (reported once): first mint block 131212738, 2026-11-02 15:56:43 WIB (age ~2.8h, verified), free 185/348 = 53.16% verified (fresh read: totalSupply 185, freeClaimed 185, FREE_SUPPLY 348; re-read block 131233850: 184/348 = 52.87%), user slot open (mintedBy 0, freeUsed 0, balance 0, quote(user,1) = 0). Gate website FAILED methods (A)-(G) + DappBay check, so NOT previewed, NOT minted. X optional, not a blocker."
pl["gateNote"] = "Gate website-only FAILED 2026-11-02 run 18:31 WIB: (A) raw contract-address search - no project site, only unrelated PlutoCoin/generic results; (B) Boltbook front page EN text fetch (crawled 11:13 UTC) + ZH direct fetch - no post naming Plutoko, ZH address list does not contain the contract; EN direct fetch returned 0 bytes but text fetch succeeded; (C) Sourcify full contract JSON - 0 external URLs, verifiedAt 2026-11-02T08:56:51Z (verification, not site); (D) no same-family site pattern with linkage; (E) deployer group owner 0x190f1f0caff480e207f42586f9fbe4c691a27066 - factory wave, NOT exempt; (F) twitterapi.io not used (no handle candidate; X optional); (G) project-name search - no project site, no candidate site whose agent docs could be checked; DappBay category AI - no Plutoko listing (absence not proof, recorded as checked). contractURI() decoded (info only, method H adoption still pending): name + description + seller_fee_basis_points 500, NO external_link/external_url."
pl["freePctVerified"] = 53.16
# New early leads from Sourcify feed (verified in run-2026-11-02-1831-sourcify-verify.json)
ver = json.load(open(BASE + "run-2026-11-02-1831-sourcify-verify.json"))
new_leads = {
 "Yydspanda": "0x9421429eF629db0175323b6F14804AE6b3528883",
 "Nexobyte": "0x7A75c1F85B2c047954E9B59e1a998F15091A9BC8",
 "Lumigeisha": "0x11aBA96f117b396A0EfCc919fa54FFcc8319E64d",
 "Stitchvolt": "0xAA911256Fa3Ca8F6Cff699FC6190905261350cF0",
 "Dragonito": "0x56E2604A33F1ccBc00376046a767cCE45B50F592",
}
for name, addr in new_leads.items():
    r = ver[addr]; fm = r["first"]
    pct = round(100*r["freeClaimed"]/r["FREE_SUPPLY"],2) if r["freeClaimed"] is not None and r["FREE_SUPPLY"] else None
    snap["contracts"][name] = {
        "address": addr, "status": "early-lead-reported-2026-11-02",
        "name": r["name"], "symbol": r["symbol"], "kind": "ERC721",
        "totalSupply": r["totalSupply"], "freeClaimed": r["freeClaimed"], "FREE_SUPPLY": r["FREE_SUPPLY"],
        "freePctVerified": pct, "mintOpen": True,
        "userMintedBy": r["mintedBy"], "userFreeUsed": r["freeUsed"], "userBalance": r["balance"],
        "userSlotNote": "Slot open by mintedBy(user)=0 + freeUsed(user)=0 + balance 0 + quote(user,1)=0 reads; NOT preview-verified (early leads are never previewed).",
        "firstSeenBlock": fm["first_block"],
        "lastReadBlock": BLOCK, "lastReadWib": BT,
        "xVerified": False, "velocityVerified": False,
        "launchNote": f"First mint verified on-chain: first Transfer-from-zero at block {fm['first_block']}, {fm['first_wib']} (Ankr getLogs walk from block 130000000; {fm['count']} logs, {fm['distinct_minters']} distinct minters). Sourcify verifiedAt is verification time, NOT launch time. First-seen by this job in run 18:31 WIB via Sourcify feed.",
        "baselineNote": f"EARLY lead reported once 2026-11-02 run 18:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % {pct}%, below 50%; X unverified; velocity not yet computable (first baseline stored this run).",
        "supplyView": "totalSupply",
    }
snap["timestamp_wib"] = BT
snap["note"] = "Run 18:31 WIB: Plutoko promoted to strong lead but GATE-BLOCKED (reported once, not previewed/minted); 5 new early leads added (Yydspanda, Nexobyte, Lumigeisha, Stitchvolt, Dragonito); track-B still pending; no execution; scan triage pending at snapshot write time."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]))
