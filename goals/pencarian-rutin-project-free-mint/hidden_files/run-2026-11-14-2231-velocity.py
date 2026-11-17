#!/usr/bin/env python3
"""Velocity analysis run 2231 vs hot-leg 2229 reread (read-only; no snapshot edit).
Interval from block timestamps fetched live (blocks 133555636 -> 133556613).
Focus: velocity PASS (>=1.5x prev rate AND >=20 tokens), free% >=70 / >=50, slot changes."""
import json, subprocess
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

def block_ts(n):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(n), False]})
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

r_prev_j = json.load(open(BASE + "run-2026-11-14-2229-reread.json"))
r_prev = r_prev_j["reads"]
BLOCK_PREV = r_prev_j.get("block")
r_cur_j = json.load(open(BASE + "run-2026-11-14-2231-reread.json"))
r_cur = r_cur_j["reads"]
BLOCK_CUR = r_cur_j.get("block")
snap = json.load(open(BASE + "onchain-snapshot.json"))["contracts"]
SUPPLY_KEYS = ["totalSupply", "totalMinted", "totalSpecimens", "totalRemnants"]

ts_prev = block_ts(BLOCK_PREV)
ts_cur = block_ts(BLOCK_CUR)
interval_min = (ts_cur - ts_prev) / 60 if (ts_prev and ts_cur) else None
print(f"block ts prev={ts_prev} cur={ts_cur} interval_min={interval_min}")

def supply(views):
    if not views:
        return None, None
    for k in SUPPLY_KEYS:
        if views.get(k) is not None:
            return k, views[k]
    return None, None

def free_pct(views):
    if not views:
        return None, "no views"
    fc = views.get("freeClaimed"); fm = views.get("freeMinted")
    for cap_key in ("FREE_SUPPLY", "FREE_MAX", "FREE_CAP", "FREE_POOL", "FREE_SHARES"):
        cap = views.get(cap_key)
        if cap:
            n = fc if fc is not None else fm
            if n is not None:
                return round(100 * n / cap, 1), f"{n}/{cap} {cap_key}"
    return None, "no free cap view"

rows = []
for name, rc in r_cur.items():
    vc = rc.get("views"); vp = r_prev.get(name, {}).get("views")
    skc, cur = supply(vc); skp, prev = supply(vp)
    minted = (cur - prev) if (cur is not None and prev is not None and skc == skp) else None
    rate = round(minted / interval_min, 3) if (minted is not None and interval_min) else None
    s = snap.get(name, {})
    prev_rate = s.get("currentRatePerMin", s.get("previousRatePerMin"))
    if prev_rate is None:
        addr = (rc.get("address") or "").lower()
        for k, v in snap.items():
            if (v.get("address") or "").lower() == addr and k != name:
                prev_rate = v.get("currentRatePerMin", v.get("previousRatePerMin"))
                break
    ratio = round(rate / prev_rate, 2) if (rate is not None and prev_rate) else None
    vel_pass = bool(ratio is not None and ratio >= 1.5 and minted is not None and minted >= 20)
    fpct, fbasis = free_pct(vc)
    slot = []
    for k in ("mintedBy_user", "freeUsed_user", "freeClaimed_user", "balanceOf_user",
              "mintedByWallet_user", "freeMintedPerWallet_user", "freeBooked_user",
              "hasFreeClaimed_user", "priceFor_user", "holdsAgentId_user"):
        a = vp.get(k) if vp else None; b = vc.get(k) if vc else None
        if a is not None and b is not None and a != b:
            slot.append(f"{k}: {a}->{b}")
    rows.append({"name": name, "supply_key": skc, "prev": prev, "cur": cur,
                 "minted": minted, "rate": rate, "prev_rate": prev_rate,
                 "ratio": ratio, "vel_pass": vel_pass, "free_pct": fpct,
                 "free_basis": fbasis, "slot_change": slot,
                 "views_none_2231": [k for k, x in (vc or {}).items() if x is None]})
json.dump({"interval_min": interval_min, "block_prev": BLOCK_PREV,
           "block_cur": BLOCK_CUR, "rows": rows},
          open(BASE + "run-2026-11-14-2231-velocity.json", "w"), indent=1)
print(f"{'name':<18} {'prev':>6} {'cur':>6} {'mint':>5} {'rate':>6} {'prevRate':>8} {'ratio':>6} {'free%':>6}  vel  slot")
for r in rows:
    print(f"{r['name']:<18} {str(r['prev']):>6} {str(r['cur']):>6} {str(r['minted']):>5} {str(r['rate']):>6} {str(r['prev_rate']):>8} {str(r['ratio']):>6} {str(r['free_pct']):>6}  {'PASS' if r['vel_pass'] else 'fail'}  {';'.join(r['slot_change'])}")
print("\nVELOCITY PASS:", [r["name"] for r in rows if r["vel_pass"]] or "NONE")
print("free% >=70:", [(r["name"], r["free_pct"], r["free_basis"]) for r in rows if r["free_pct"] is not None and r["free_pct"] >= 70])
print("free% >=50:", [(r["name"], r["free_pct"], r["free_basis"]) for r in rows if r["free_pct"] is not None and r["free_pct"] >= 50])
print("free pool 0 (sellout check):", [(r["name"], r["free_basis"]) for r in rows if r["free_pct"] == 100.0])
print("views None in 2231:", {r["name"]: r["views_none_2231"] for r in rows if r["views_none_2231"]})
