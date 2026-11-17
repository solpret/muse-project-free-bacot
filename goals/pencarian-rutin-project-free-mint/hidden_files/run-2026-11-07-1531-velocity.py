#!/usr/bin/env python3
"""Velocity + sellout/slot scan for run 1531 — computed from reread vs snapshot.
Read-only on inputs; writes run-2026-11-07-1531-velocity.json.
Interval from block diff x 0.45 s/block. Velocity only where the snapshot
baseline is recent (lastReadBlock >= 132032735, run 2201); older baselines
are stale and marked not-computable.
"""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
re = json.load(open(f"{BASE}/run-2026-11-07-1531-reread.json"))
CUR_BLOCK = re["block"]
if CUR_BLOCK is None:
    import sys; sys.path.insert(0, "/home/hatch/workspace/fast_exec")
    from fast_rpc import race as _race
    CUR_BLOCK = int(_race("eth_blockNumber", []), 16)
    print("CUR_BLOCK fallback via race:", CUR_BLOCK)
PREV_BLOCK_FLOOR = 132171021
SEC_PER_BLOCK = 0.45

def _num(x):
    if isinstance(x, bool): return None
    if isinstance(x, int): return x
    if isinstance(x, str):
        try: return int(x, 16) if x.startswith("0x") else int(x)
        except Exception: return None
    return None

def freepct(d, s):
    # prefer verified free counter over FREE_SUPPLY/MAX_SUPPLY
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
    prev = _num(s.get("totalSupply"))
    prev_block = s.get("lastReadBlock")
    prev_rate = s.get("currentRatePerMin")
    row = {"name": name, "address": d.get("address"),
           "prevSupply": prev, "curSupply": cur, "prevBlock": prev_block,
           "prevRatePerMin": prev_rate}
    fp, fc, cap, how = freepct(d, s)
    row["freePct"] = fp; row["freeCounter"] = fc; row["freeCap"] = cap; row["freePctHow"] = how
    if isinstance(prev, int) and isinstance(cur, int) and isinstance(prev_block, int) and prev_block >= PREV_BLOCK_FLOOR:
        interval_min = (CUR_BLOCK - prev_block) * SEC_PER_BLOCK / 60.0
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
    # sellout / near-sellout / slot
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
    rows.append(row)

rows.sort(key=lambda r: (r.get("mintedInInterval") is None, -(r.get("mintedInInterval") or 0)))
out = {"block": CUR_BLOCK, "prevBlockFloor": PREV_BLOCK_FLOOR,
       "intervalNote": "block-diff x 0.45s; velocity only for baselines >= run 1501 reread block",
       "passes": [r for r in rows if r.get("velocityPasses")],
       "soldOut": [r for r in rows if r.get("soldOut")],
       "nearSellout": [r for r in rows if r.get("nearSellout")],
       "slotChanged": [r for r in rows if r.get("slotChanged")],
       "rows": rows}
json.dump(out, open(f"{BASE}/run-2026-11-07-1531-velocity.json", "w"), indent=1)
print(f"VELOCITY passes={len(out['passes'])} soldOut={len(out['soldOut'])} nearSellout={len(out['nearSellout'])} slotChanged={len(out['slotChanged'])} rows={len(rows)}")
for r in out["passes"]:
    print(" PASS", r["name"], r["mintedInInterval"], "rate", r["ratePerMin"], "ratio", r["ratioVsPrev"], "freePct", r["freePct"])
for r in out["soldOut"]:
    print(" SOLDOUT", r["name"], r["curSupply"], "/", r["maxSupply"])
for r in out["nearSellout"]:
    print(" NEAR", r["name"], r["curSupply"], "/", r["maxSupply"], "remaining", r["remaining"])
for r in out["slotChanged"]:
    print(" SLOT-CHG", r["name"], "bal", r["prevBalanceOf_user"], "->", r["balanceOf_user"])
for r in rows[:12]:
    print(" TOP", r["name"], "minted", r.get("mintedInInterval"), "rate", r.get("ratePerMin"), "ratio", r.get("ratioVsPrev"), "freePct", r.get("freePct"), r.get("velocityNote", ""))
