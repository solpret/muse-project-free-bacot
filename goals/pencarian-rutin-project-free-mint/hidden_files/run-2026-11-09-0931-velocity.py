#!/usr/bin/env python3
"""Velocity + material-change analysis for re-read run 2026-11-09 09:31 WIB.
Reads run-2026-11-09-0931-reread.json (r10), 0901 (r9, PARTIAL 400),
0831 (r8), 0731 (r7) + onchain-snapshot.json. READ-ONLY; writes
run-2026-11-09-0931-velocity.json. Does NOT write the snapshot.

Method (same as 0901 merge):
- sup(d) = totalSupply else totalMinted.
- B7=132491029, B8=132498816, B9=132504249, B10=132510544 (final JSON block;
  batch-1 contract reads were at ~block 132508961, batch-2 ~132509827).
- MIN_89 = 40.7, MIN_910 = 47.2, MIN_78 = 58.4, MIN_810 = 88.0.
- Contracts read in 0901: rate_cur=(s10-s9)/47.2, rate_prev=(s9-s8)/40.7.
- Contracts NOT read in 0901 (188): baseline = snapshot stored supply
  (0831 value, lastReadBlock 132498816); rate_cur=(s10-s_snap)/88.0,
  rate_prev=(s8-s7)/58.4. Flagged as long-baseline.
- Pass: ratio>=1.5 AND minted_cur>=20; or prev rate<=0 and cur>0 with >=20.
- None is NEVER treated as 0/a change (read artefact).
"""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
B7, B8, B9, B10 = 132491029, 132498816, 132504249, 132510544
MIN_78 = (B8 - B7) * 0.45 / 60    # 58.4
MIN_89 = (B9 - B8) * 0.45 / 60    # 40.7
MIN_910 = (B10 - B9) * 0.45 / 60  # 47.2
MIN_810 = (B10 - B8) * 0.45 / 60  # 88.0

r10 = json.load(open(f"{HF}/run-2026-11-09-0931-reread.json"))
r9 = json.load(open(f"{HF}/run-2026-11-09-0901-reread.json"))
r8 = json.load(open(f"{HF}/run-2026-11-09-0831-reread.json"))
r7 = json.load(open(f"{HF}/run-2026-11-09-0731-reread.json"))
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
special = json.load(open(f"{HF}/run-2026-11-09-0931-special.json"))

def sup(d):
    if not isinstance(d, dict): return None
    v = d.get("totalSupply")
    return v if v is not None else d.get("totalMinted")

def view_of(d):
    """View used for THIS read: totalSupply if present, else totalMinted."""
    if not isinstance(d, dict): return None
    return "totalSupply" if d.get("totalSupply") is not None else "totalMinted"

rr10, rr9, rr8, rr7 = r10["reread"], r9["reread"], r8["reread"], r7["reread"]
contracts = snap["contracts"]

vel_pass, vel_near, vel_fail_prev_pass = [], [], []
sellout_new, slot_ch, bal_ch = [], [], []
free_pct = {}
total_nft_mints = 0
no_supply = []

for name, d10 in rr10.items():
    old = contracts.get(name, {})
    # LIKE-FOR-LIKE views only: never compare totalMinted now vs a
    # totalSupply baseline (or vice versa) — that fabricates mints.
    view = view_of(d10)
    s10 = d10.get(view) if view else None
    if s10 is None:
        no_supply.append(name)
        continue
    d9, d8, d7 = rr9.get(name), rr8.get(name), rr7.get(name)
    if d9 is not None and d9.get(view) is not None:
        s9, base_block, interval = d9.get(view), B9, MIN_910
        baseline_src = "0901-reread"
        s8 = d8.get(view) if d8 else None
        rate_prev = ((s9 - s8) / MIN_89) if (s9 is not None and s8 is not None) else None
    elif d9 is not None and d9.get(view) is None and old.get(view) is not None:
        # Current view differs from 0901 read; fall back to snapshot same-view.
        s9, base_block, interval = old.get(view), B8, MIN_810
        baseline_src = "snapshot/0831-same-view"
        s8 = d8.get(view) if d8 else None
        s7 = d7.get(view) if d7 else None
        rate_prev = ((s8 - s7) / MIN_78) if (s8 is not None and s7 is not None) else None
    else:
        # Not read in 0901: baseline = snapshot stored supply (0831 value).
        s_base = old.get(view)
        s9, base_block, interval = s_base, B8, MIN_810
        baseline_src = "snapshot/0831"
        s8 = d8.get(view) if d8 else None
        s7 = d7.get(view) if d7 else None
        rate_prev = ((s8 - s7) / MIN_78) if (s8 is not None and s7 is not None) else None
    if s9 is None:
        continue
    m_cur = s10 - s9
    if s10 < 10**12 and m_cur > 0:
        total_nft_mints += m_cur
    rate_cur = m_cur / interval if interval else None
    ratio = (rate_cur / rate_prev) if (rate_cur is not None and rate_prev and rate_prev > 0) else None
    passes = False
    if rate_cur is not None:
        if ratio is not None and ratio >= 1.5 and m_cur >= 20:
            passes = True
        elif rate_prev is not None and rate_prev <= 0 and rate_cur > 0 and m_cur >= 20:
            passes = True
            ratio = None  # inf convention
    rec = {"name": name, "minted": m_cur, "rate_cur": round(rate_cur, 4) if rate_cur is not None else None,
           "rate_prev": round(rate_prev, 4) if rate_prev is not None else None,
           "ratio": round(ratio, 2) if ratio is not None else None,
           "baseline": baseline_src, "interval_min": round(interval, 1),
           "supply_now": s10, "status_snapshot": old.get("status")}
    if passes:
        vel_pass.append(rec)
    elif m_cur >= 20:
        vel_near.append(rec)
    # free % (verified only)
    fc = d10.get("freeClaimed"); fs = d10.get("FREE_SUPPLY") or old.get("FREE_SUPPLY")
    fm = d10.get("freeMinted"); fcap = old.get("FREE_CAP") or d10.get("FREE_CAP")
    pct = None
    if fc is not None and fs:
        pct = fc / fs
    elif fm is not None and fcap:
        pct = fm / fcap
    if pct is not None:
        free_pct[name] = round(pct, 4)
    # NEW sellout vs 0901/snapshot baseline
    old_fc = (d9.get("freeClaimed") if d9 else old.get("freeClaimed"))
    old_fm = (d9.get("freeMinted") if d9 else old.get("freeMinted"))
    if fc is not None and fs and fc >= fs and not (old_fc is not None and old_fc >= fs):
        sellout_new.append((name, "freeClaimed", fc, fs))
    if fm is not None and fcap and fm >= fcap and not (old_fm is not None and old_fm >= fcap):
        sellout_new.append((name, "freeMinted", fm, fcap))
    # slot / balance changes vs 0901 (or snapshot for unread)
    ob = (d9.get("balanceOf_user") if d9 else old.get("balanceOf_user"))
    nb = d10.get("balanceOf_user")
    if ob is not None and nb is not None and ob != nb:
        bal_ch.append((name, ob, nb))
    ofc_u = (d9.get("freeClaimed_user") if d9 else old.get("freeClaimed_user"))
    nfc_u = d10.get("freeClaimed_user")
    if ofc_u is not None and nfc_u is not None and ofc_u != nfc_u:
        slot_ch.append((name, ofc_u, nfc_u))

# 0901 velocity passers: did they pass again?
prev_pass_0901 = ["STARRY", "bridge-0x93bf08d2", "Sprouts-1831",
                  "0x2728c134d79d34a977d6d35d8a3014abb5c97ed4", "M3MO", "AGENT PASS",
                  "UNKNOWN-720a", "BAHUANG2", "AGENT BOTS", "Golden Agents", "HELIX",
                  "MONOLITH", "0xCf8d6492", "STRAWBS", "ALL ACCESS", "BAHUANG3"]
pass_names = {r["name"] for r in vel_pass}
for n in prev_pass_0901:
    if n in rr10 and n not in pass_names:
        rec = next((r for r in vel_near if r["name"] == n), None)
        vel_fail_prev_pass.append((n, rec))

# track_c changes: 0931 vs 0831 (0901 had no track_c reads)
tc10, tc8 = r10["track_c"], r8["track_c"]
tc_changes = []
for name, d in tc10.items():
    o = tc8.get(name)
    if not o:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        a, b = o.get(k), d.get(k)
        if a is not None and b is not None and a != b:
            tc_changes.append((name, k, a, b))
snap_tc = snap.get("track_c", {})

out = {
    "blocks": {"B7": B7, "B8": B8, "B9": B9, "B10": B10,
               "intervals_min": {"MIN_78": round(MIN_78, 1), "MIN_89": round(MIN_89, 1),
                                 "MIN_910": round(MIN_910, 1), "MIN_810": round(MIN_810, 1)}},
    "coverage": {"contracts_read": len(rr10), "track_c_read": len(tc10),
                 "supply_none": len(no_supply), "supply_none_list": no_supply,
                 "batch_fail_contracts": sum(1 for v in rr10.values() if v.get("_batch_fail")),
                 "batch_fail_tc": sum(1 for v in tc10.values() if v.get("_batch_fail"))},
    "velocity_pass": vel_pass,
    "velocity_near_ge20": vel_near,
    "velocity_prev_pass_now_fail": vel_fail_prev_pass,
    "free_pct_verified": free_pct,
    "sellout_new": sellout_new,
    "slot_changes": slot_ch,
    "balance_changes": bal_ch,
    "total_nft_scale_mints_interval": total_nft_mints,
    "track_c_changes_vs_0831": tc_changes,
    "yama_special": special.get("yama"),
    "binanceai_special": special.get("binanceai"),
    "alchemister_cafeeddf_special": special.get("alchemister_cafeeddf"),
    "alchemister_69037_reread": rr10.get("Alchemister"),
    "alchemister_69037_snapshot": {k: contracts.get("Alchemister", {}).get(k) for k in
        ("status", "firstSeenWib", "firstBlock", "firstMint", "firstMintWib", "totalSupplyAtTriage")},
}
with open(f"{HF}/run-2026-11-09-0931-velocity.json", "w") as f:
    json.dump(out, f, indent=1)

print(f"contracts={len(rr10)} tc={len(tc10)} supply_none={len(no_supply)}")
print(f"VEL PASS: {len(vel_pass)}")
for r in vel_pass:
    print("  PASS", r["name"], f"+{r['minted']} ratio={r['ratio']} base={r['baseline']}")
print(f"VEL NEAR (>=20, gagal): {len(vel_near)}")
for r in vel_near:
    print("  NEAR", r["name"], f"+{r['minted']} ratio={r['ratio']} base={r['baseline']}")
print("PREV-PASS NOW FAIL:", vel_fail_prev_pass)
print("SELLOUT NEW:", sellout_new)
print("SLOT CH:", slot_ch)
print("BAL CH:", bal_ch)
print("FREE% verified count:", len(free_pct), ">=25%:", [k for k, v in free_pct.items() if v >= 0.25],
      ">=50%:", [k for k, v in free_pct.items() if v >= 0.5])
print("TOTAL NFT mints interval:", total_nft_mints)
print("TC CHANGES vs 0831:", tc_changes)
