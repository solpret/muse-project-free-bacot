#!/usr/bin/env python3
"""Main run 2026-11-02 17:31 WIB snapshot update (route 1 + promotions + sellouts + new early leads)."""
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
        except Exception:
            pass
    return None
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1731.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1731-read.json"))
BLOCK = read["block"]; BT = blk_time(BLOCK)
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
    old_ts = v.get("totalSupply"); old_rate = v.get("currentRatePerMin")
    old_read_dt = parse_wib(v.get("lastReadWib") or "")
    interval = (new_dt - old_read_dt).total_seconds() / 60.0 if (old_read_dt and new_dt) else None
    for rk, sk in GEN:
        if r.get(rk) is not None:
            v[sk] = r[rk]
    fc, fs, fm, fl = v.get("freeClaimed"), v.get("FREE_SUPPLY"), v.get("freeMinted"), v.get("freeLeft")
    if fc is not None and fs:
        v["freePctVerified"] = round(100 * fc / fs, 2)
    elif fm is not None and fl is not None and (fm + fl):
        v["freePctVerified"] = round(100 * fm / (fm + fl), 2)
    v["previousTotalSupply"] = old_ts
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = BT
    if old_ts is not None and v.get("totalSupply") is not None and interval:
        minted = v["totalSupply"] - old_ts
        v["mintedInInterval"] = minted; v["intervalMinutes"] = round(interval, 2)
        rate = minted / interval if interval else 0
        v["currentRatePerMin"] = round(rate, 3); v["previousRatePerMin"] = old_rate
        passes = (old_rate is not None and old_rate > 0 and rate >= 1.5 * old_rate and minted >= 20)
        v["velocityLegPasses"] = passes
        v["velocityNote"] = f"Run 17:31 WIB (read block {BLOCK}): +{minted} tokens in ~{interval:.2f} min = {rate:.3f}/min, ratio vs prior {old_rate} = {(rate/old_rate if old_rate else None)} -> velocity leg {'PASSES' if passes else 'FAILS'}."
# Promotions to strong-lead-gate-blocked (reported once in run 17:31 log)
PROMO = {
 "Griffito": "Run 17:31 WIB: age verified (first mint 2026-11-02 15:56:45 WIB, ~1.6h) + free 187/341=54.84% verified + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Reported once in run 17:31.",
 "Niuniubo": "Run 17:31 WIB: age verified (first mint 2026-11-02 15:56:47 WIB, ~1.6h) + free 169/318=53.14% verified + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Reported once in run 17:31.",
 "Witchibo": "Run 17:31 WIB: age verified (first mint 2026-11-02 15:56:49 WIB, ~1.6h) + free 193/316=61.08% verified + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Reported once in run 17:31.",
 "Circuitfox": "Run 17:31 WIB: age verified (first mint 2026-11-02 15:56:51 WIB, ~1.6h) + free 193/315=61.27% verified + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Reported once in run 17:31.",
 "Gourdwitch": "Run 17:31 WIB: age verified (first mint 2026-11-02 16:38:12 WIB, ~1h) + free 893/1672=53.41% verified + slot open (mintedBy=0, freeUsed=0, quote(user,1)=0, balance=0) = 3 strong-lead legs met, but WEBSITE-ONLY GATE FAILED, so NO preview/mint. Reported once in run 17:31.",
}
GATE = "WEBSITE-ONLY GATE FAILED (methods A-H run 17:31: raw address search no project site; name search no project site; Boltbook front page no naming post; Sourcify metadata 0 external URLs; no same-family site pattern with linkage; deployer-group check (0x190f factory for 4, 0xd76d wave for Gourdwitch); twitterapi.io not used (no handle candidate; X optional); DappBay AI category no listing (absence proves nothing); contractURI() decoded: name+description+seller_fee 500 only, NO external_link/external_url. DO NOT preview, DO NOT mint."
for n, note in PROMO.items():
    v = snap["contracts"][n]
    v["status"] = "strong-lead-gate-blocked-2026-11-02"
    v["strongLeadLegsNote"] = note; v["gateNote"] = GATE
# Sold outs already reported by hot-leg 17:34 -> remove silently, record in excluded
for n, note in [
 ("Jiayoutigo", "sold-out-2026-11-02: freeClaimed 316/316 at main read block 131227032; already reported sold out by hot-leg 17:34 WIB, main run only removes, does NOT re-report"),
 ("Botowl", "sold-out-2026-11-02: freeClaimed 321/321 at main read block 131227032; already reported sold out by hot-leg 17:34 WIB, main run only removes, does NOT re-report"),
]:
    if n in snap["contracts"]:
        snap.setdefault("excluded", {})[n] = note; del snap["contracts"][n]
# New early leads from Sourcify feed (first mints verified via full Ankr walk from block 130000000, counts match totalSupply exactly)
EARLY = {
 "MachineMuse": {"address": "0xED05274F0Fc42c53Fe2f02558f1afB5BeAd55A8d", "symbol": "MUSE", "totalSupply": 173, "freeClaimed": 159, "FREE_SUPPLY": 679, "freePctVerified": 23.42,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131010531, 2026-11-01 14:39:45 WIB (Ankr getLogs walk from block 130000000; 173 logs = totalSupply 173, all mints in range). Age ~27h at run time, within 48h. Sourcify verifiedAt 2026-11-02T10:44:38Z (verification time, NOT launch time). First-seen by this job in run 17:31 WIB via Sourcify feed.",
   "owner": "0x8a3b31dd69c6ab76b2dda2711b32eaad8646e173"},
 "CopilotClub": {"address": "0x4EA51956dd8F4B3C04ffF36e0254Be1b04c051aF", "symbol": "CPLT", "totalSupply": 195, "freeClaimed": 195, "FREE_SUPPLY": 672, "freePctVerified": 29.02,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131010545, 2026-11-01 14:39:51 WIB (Ankr getLogs walk from block 130000000; 195 logs = totalSupply 195, all mints in range). Age ~27h at run time, within 48h. Sourcify verifiedAt 2026-11-02T10:44:10Z (verification time, NOT launch time). First-seen by this job in run 17:31 WIB via Sourcify feed.",
   "owner": "0x90e8b1c93c80758e2bd5032c7acec382501cb84b"},
 "DelegateDAO": {"address": "0x9a1339B8Aaee25082e3e54aE09780905add63462", "symbol": "DLGT", "totalSupply": 225, "freeClaimed": 211, "FREE_SUPPLY": 686, "freePctVerified": 30.76,
   "launchNote": "First mint verified on-chain: first Transfer-from-zero at block 131010533, 2026-11-01 14:39:45 WIB (Ankr getLogs walk from block 130000000; 225 logs = totalSupply 225, all mints in range). Age ~27h at run time, within 48h. Sourcify verifiedAt 2026-11-02T10:43:58Z (verification time, NOT launch time). First-seen by this job in run 17:31 WIB via Sourcify feed.",
   "owner": "0xfc68e21c3b9d1803b746a0031cbcf4e429d86bc"},
}
for n, e in EARLY.items():
    snap["contracts"][n] = {
        "address": e["address"], "status": "early-lead-reported-2026-11-02", "name": n, "symbol": e["symbol"], "kind": "ERC721",
        "totalSupply": e["totalSupply"], "freeClaimed": e["freeClaimed"], "FREE_SUPPLY": e["FREE_SUPPLY"],
        "freePctVerified": e["freePctVerified"], "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
        "userSlotNote": "Slot open by read: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, balance 0 - NOT preview-verified (early leads are never previewed).",
        "launchNote": e["launchNote"],
        "baselineNote": "EARLY lead reported once 2026-11-02 run 17:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY) and AGENT_ID() reads the registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Free % below 50%; X unverified; velocity not yet computable (first baseline stored this run). Gate website NOT yet checked (gate only checked at promotion to strong lead/candidate).",
        "lastReadBlock": BLOCK, "lastReadWib": BT, "xVerified": False, "velocityVerified": False, "velocityLegPasses": False,
        "supplyView": "totalSupply", "owner": e["owner"],
    }
snap["timestamp_wib"] = BT
snap["note"] = "Run 17:31 WIB: 5 strong-lead promotions gate-blocked (reported once); 2 hot-leg-reported sellouts removed silently; 3 Sourcify-feed early leads added; track-B still pending; no execution."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]))
