#!/usr/bin/env python3
"""Velocity + sellout/slot scan for run 0831 — computed from 0831 reread vs 0801 reread.
Baseline = run 0801 reread (block 132302277); prev_rate = 0801 velocity ratePerMin.
Snapshot free counters used for freePct (fresh free views revert on these contracts).
Read-only on inputs; writes run-2026-11-08-0831-velocity.json.
Interval from block diff x 0.45 s/block.
"""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re = json.load(open(f"{BASE}/run-2026-11-08-0831-reread.json"))
prev_re = json.load(open(f"{BASE}/run-2026-11-08-0801-reread.json"))
prev_vel = json.load(open(f"{BASE}/run-2026-11-08-0801-velocity.json"))
prev_rows = {r["name"]: r for r in prev_vel["rows"]}
CUR_BLOCK = re["block"]
PREV_BLOCK = prev_re["block"]
SEC_PER_BLOCK = 0.45

def _num(x):
    if isinstance(x, bool): return None
    if isinstance(x, int): return x
    if isinstance(x, str):
        try: return int(x, 16) if x.startswith("0x") else int(x)
        except Exception: return None
    return None

def freepct(d, s):
    fc = _num(d.get("freeClaimed"))
    if fc is None: fc = _num(d.get("freeMinted"))
    if fc is None: fc = _num(s.get("freeClaimed"))
    if fc is None: fc = _num(s.get("freeMinted"))
    cap = _num(d.get("FREE_SUPPLY")) or _num(s.get("FREE_SUPPLY")) or _num(s.get("freeSupply"))
    if fc is not None and cap:
        return round(100.0 * fc / cap, 2), fc, cap, "freeCounter/FREE_SUPPLY"
    return None, fc, cap, None

rows = []
for name, d in re["reread"].items():
    s = snap["contracts"].get(name, {})
    cur = _num(d.get("totalSupply"))
    if cur is None:
        cur = _num(d.get("totalMinted"))
    p = prev_re["reread"].get(name, {})
    prev = _num(p.get("totalSupply"))
    if prev is None:
        prev = _num(p.get("totalMinted"))
    pv = prev_rows.get(name, {})
    prev_rate = pv.get("ratePerMin")
    row = {"name": name, "address": d.get("address"),
           "prevSupply": prev, "curSupply": cur, "prevBlock": PREV_BLOCK,
           "prevRatePerMin": prev_rate}
    fp, fc, cap, how = freepct(d, s)
    row["freePct"] = fp; row["freeCounter"] = fc; row["freeCap"] = cap; row["freePctHow"] = how
    if isinstance(prev, int) and isinstance(cur, int) and isinstance(PREV_BLOCK, int) and isinstance(CUR_BLOCK, int):
        interval_min = (CUR_BLOCK - PREV_BLOCK) * SEC_PER_BLOCK / 60.0
        minted = cur - prev
        rate = minted / interval_min if interval_min > 0 else None
        ratio = (rate / prev_rate) if (rate is not None and isinstance(prev_rate, (int, float)) and prev_rate and prev_rate > 0) else None
        passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        row.update({"intervalMin": round(interval_min, 2), "mintedInInterval": minted,
                    "ratePerMin": round(rate, 4) if rate is not None else None,
                    "ratioVsPrev": round(ratio, 2) if ratio is not None else None,
                    "velocityPasses": passes})
    else:
        reason = "no-fresh-supply" if not (isinstance(prev, int) and isinstance(cur, int)) else "stale-baseline"
        row.update({"intervalMin": None, "mintedInInterval": None, "ratePerMin": None,
                    "ratioVsPrev": None, "velocityPasses": False, "velocityNote": reason})
    maxs = _num(d.get("MAX_SUPPLY")) or _num(s.get("MAX_SUPPLY"))
    row["maxSupply"] = maxs
    if isinstance(cur, int) and isinstance(maxs, int) and maxs > 0:
        row["remaining"] = maxs - cur
        row["soldOut"] = cur >= maxs
        row["nearSellout"] = (0 < maxs - cur <= 25)
    else:
        row["remaining"] = None; row["soldOut"] = False; row["nearSellout"] = False
    bal = d.get("balanceOf_user")
    old_bal = s.get("balanceOf_user") if "balanceOf_user" in s else s.get("userBalance")
    row["balanceOf_user"] = bal; row["prevBalanceOf_user"] = old_bal
    row["slotChanged"] = (bal is not None and old_bal is not None and bal != old_bal)
    # launch-age status from snapshot for context
    row["status"] = s.get("status", "")
    row["launchNote"] = (s.get("launchNote", "") or "")[:200]
    rows.append(row)

rows.sort(key=lambda r: (r.get("mintedInInterval") is None, -(r.get("mintedInInterval") or 0)))
out = {"block": CUR_BLOCK, "prevBlock": PREV_BLOCK,
       "intervalNote": "baseline = run 0801 reread block 132302277; block-diff x 0.45s",
       "passes": [r for r in rows if r.get("velocityPasses")],
       "soldOut": [r for r in rows if r.get("soldOut")],
       "nearSellout": [r for r in rows if r.get("nearSellout")],
       "slotChanged": [r for r in rows if r.get("slotChanged")],
       "rows": rows}
json.dump(out, open(f"{BASE}/run-2026-11-08-0831-velocity.json", "w"), indent=1)
print(f"VELOCITY passes={len(out['passes'])} soldOut={len(out['soldOut'])} nearSellout={len(out['nearSellout'])} slotChanged={len(out['slotChanged'])} rows={len(rows)}")
for r in out["passes"]:
    print(" PASS", r["name"], r["mintedInInterval"], "rate", r["ratePerMin"], "ratio", r["ratioVsPrev"], "freePct", r["freePct"], "status", r["status"])
for r in out["soldOut"]:
    print(" SOLDOUT", r["name"], r["curSupply"], "/", r["maxSupply"])
for r in out["nearSellout"]:
    print(" NEAR", r["name"], r["curSupply"], "/", r["maxSupply"], "remaining", r["remaining"])
for r in out["slotChanged"]:
    print(" SLOT-CHG", r["name"], "bal", r["prevBalanceOf_user"], "->", r["balanceOf_user"])
for r in rows[:12]:
    print(" TOP", r["name"], "minted", r.get("mintedInInterval"), "rate", r.get("ratePerMin"), "ratio", r.get("ratioVsPrev"), "freePct", r.get("freePct"), r.get("velocityNote", ""))
