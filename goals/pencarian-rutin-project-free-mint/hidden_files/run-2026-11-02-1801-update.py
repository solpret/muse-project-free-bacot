#!/usr/bin/env python3
"""Main run 2026-11-02 18:01 WIB snapshot update (route 1 + promotions + sellouts + new early leads)."""
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
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-02-1801.bak.json")
snap = json.load(open(BASE + "onchain-snapshot.json"))
read = json.load(open(BASE + "run-2026-11-02-1801-read.json"))
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
        v["velocityNote"] = f"Run 18:01 WIB (read block {BLOCK}): +{minted} tokens in ~{interval:.2f} min = {rate:.3f}/min, ratio vs prior {old_rate} = {(rate/old_rate if old_rate else None)} -> velocity leg {'PASSES' if passes else 'FAILS'}."
snap["timestamp_wib"] = BT
snap["note"] = "Run 18:01 WIB: generic re-read only (promotions/sellouts handled separately if any); prior run note preserved in log. promotions gate-blocked (reported once); 2 hot-leg-reported sellouts removed silently; 3 Sourcify-feed early leads added; track-B still pending; no execution."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]))
