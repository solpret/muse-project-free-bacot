#!/usr/bin/env python3
"""Finalize run 2026-11-10 0231: diff reread vs snapshot.
Writes run-2026-11-10-0301-finalize.json. Read-only wrt snapshot (no writes here).
"""
import json, math

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(HF + "onchain-snapshot.json"))
rr = json.load(open(HF + "run-2026-11-10-0301-reread.json"))
NEW_BLOCK = rr.get("block")
OLD_BLOCK = 132641351
INTERVAL_MIN = (NEW_BLOCK - OLD_BLOCK) * 0.45 / 60.0
print(f"interval_min(block-derived)={INTERVAL_MIN:.1f} new_block={NEW_BLOCK} old_block={OLD_BLOCK}")

def is_nft_count(v):
    # totalSupply as NFT count: small ints; ERC20 supplies are astronomic
    return v is not None and isinstance(v, int) and v < 10_000_000

contracts = snap.get("contracts", {})
out = {"interval_min": round(INTERVAL_MIN, 1), "new_block": NEW_BLOCK,
       "velocity_pass": [], "velocity_all": [], "soldout_new": [],
       "free25_new": [], "free50_new": [], "slot_lost": [], "slot_gained": [],
       "age_exclusion_candidates": [], "notable": []}

for name, new in rr.get("reread", {}).items():
    old = contracts.get(name)
    if not isinstance(new, dict):
        continue
    ts = new.get("totalSupply")
    ots = old.get("totalSupply") if isinstance(old, dict) else None
    minted = None
    if is_nft_count(ts) and is_nft_count(ots):
        minted = ts - ots
    # velocity
    if minted is not None and minted > 0:
        rate = minted / INTERVAL_MIN
        pr = old.get("previousRatePerMin") if isinstance(old, dict) else None
        ratio = (rate / pr) if pr else None
        rec = {"name": name, "minted": minted, "rate": round(rate, 3),
               "prev_rate": pr, "ratio": round(ratio, 2) if ratio else None}
        out["velocity_all"].append(rec)
        if minted >= 20 and ratio is not None and ratio >= 1.5:
            out["velocity_pass"].append(rec)
    # sold-out: freeClaimed newly reached FREE_SUPPLY
    fc, fs = new.get("freeClaimed"), new.get("FREE_SUPPLY")
    ofc = old.get("freeClaimed") if isinstance(old, dict) else None
    ofs = old.get("FREE_SUPPLY") if isinstance(old, dict) else None
    if fc is not None and fs and fc >= fs:
        if ofc is None or ofs is None or ofc < ofs:
            out["soldout_new"].append({"name": name, "freeClaimed": fc, "FREE_SUPPLY": fs,
                                        "old_freeClaimed": ofc})
    # free% crossings (verified views only)
    if fc is not None and fs:
        pct = fc / fs * 100
        opct = None
        if ofc is not None and ofs:
            opct = ofc / ofs * 100
        if opct is not None:
            if pct >= 25 and opct < 25:
                out["free25_new"].append({"name": name, "pct": round(pct, 1), "old_pct": round(opct, 1)})
            if pct >= 50 and opct < 50:
                out["free50_new"].append({"name": name, "pct": round(pct, 1), "old_pct": round(opct, 1)})
    # user slot changes
    nbal = new.get("balanceOf_user")
    obal = old.get("balanceOf_user") if isinstance(old, dict) else None
    nfc_u = new.get("freeClaimed_user")
    ofc_u = old.get("freeClaimed_user") if isinstance(old, dict) else None
    if obal == 0 and nbal and nbal > 0:
        out["slot_gained"].append({"name": name, "balance": nbal})
    # PIXEL MONSTERS + HIVE + AGMIN notable reads
    if name in ("PIXEL MONSTERS", "HIVE Agents", "Agent Miner", "Marbleworks", "WNO",
                "War Need Over", "TIME CARDS Genesis", "M3MO", "SakuraNFT"):
        out["notable"].append({"name": name, "totalSupply": ts, "freeClaimed": fc,
                               "freeMinted": new.get("freeMinted"), "FREE_SUPPLY": fs,
                               "balanceOf_user": nbal, "old_totalSupply": ots})

out["velocity_all"].sort(key=lambda x: -x["minted"])
out["velocity_pass"] = [v for v in out["velocity_all"] if v["minted"] >= 20 and v["ratio"] and v["ratio"] >= 1.5]
print(json.dumps(out, indent=1)[:6000])
json.dump(out, open(HF + "run-2026-11-10-0301-finalize.json", "w"), indent=1)
print("TRACK_C reread n:", len(rr.get("track_c", {})))
for k, v in list(rr.get("track_c", {}).items())[:90]:
    if isinstance(v, dict):
        print("TC", k, "ts=", v.get("totalSupply"), "fm=", v.get("freeMinted"), "bal=", v.get("balanceOf_user"))
