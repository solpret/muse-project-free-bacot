#!/usr/bin/env python3
"""Velocity + material-change analysis for re-read run 2026-11-09 10:01 WIB.
Reads run-2026-11-09-1001-reread.json (r11), 0931 (r10), 0901 (r9) +
onchain-snapshot.json. READ-ONLY; writes run-2026-11-09-1001-velocity.json.
B11 is ESTIMATED (re-read JSON block=None, dataseed head-read failed):
head 132518180 at ~11:10 WIB (ABC verify) + ~12 min to re-read end 11:22
=> B11 ~132519800. MIN_1011 = (B11-B10)*0.45/60 ~ 69.4 min. Flagged.
Method mirrors 0931-velocity.py. None is NEVER a change (read artefact)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
B9, B10, B11 = 132504249, 132510544, 132519800
MIN_910 = (B10 - B9) * 0.45 / 60    # 47.2
MIN_1011 = (B11 - B10) * 0.45 / 60  # ~69.4 (B11 estimated)
r11 = json.load(open(f"{HF}/run-2026-11-09-1001-reread.json"))
r10 = json.load(open(f"{HF}/run-2026-11-09-0931-reread.json"))
r9 = json.load(open(f"{HF}/run-2026-11-09-0901-reread.json"))
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
def sup(d):
    if not isinstance(d, dict): return None
    v = d.get("totalSupply")
    return v if v is not None else d.get("totalMinted")
def view_of(d):
    if not isinstance(d, dict): return None
    return "totalSupply" if d.get("totalSupply") is not None else "totalMinted"
rr11, rr10, rr9 = r11["reread"], r10["reread"], r9["reread"]
contracts = snap["contracts"]
vel_pass, vel_near, sellout_new, slot_ch, bal_ch = [], [], [], [], []
free_pct, no_supply = {}, []
total_nft_mints = 0
for name, d11 in rr11.items():
    old = contracts.get(name, {})
    view = view_of(d11)
    s11 = d11.get(view) if view else None
    if s11 is None:
        no_supply.append(name); continue
    # token-scale artefact guard: NFT supplies are < 1e7; bigger = token balance
    token_scale = s11 > 10_000_000
    d10, d9 = rr10.get(name), rr9.get(name)
    s10 = d10.get(view) if d10 and d10.get(view) is not None else None
    if s10 is None:
        s10 = old.get(view)
    if s10 is None: continue
    minted = s11 - s10
    if not token_scale and minted > 0: total_nft_mints += minted
    rate_cur = minted / MIN_1011
    s9 = d9.get(view) if d9 and d9.get(view) is not None else None
    rate_prev = ((s10 - s9) / MIN_910) if s9 is not None else None
    ratio = None
    if rate_prev is not None and rate_prev > 0: ratio = rate_cur / rate_prev
    elif rate_prev == 0 and rate_cur > 0: ratio = float("inf")
    passes = (not token_scale) and minted >= 20 and ((ratio is not None and ratio >= 1.5) or (rate_prev == 0 and rate_cur > 0))
    rec = {"name": name, "minted": minted, "rate_cur": round(rate_cur, 4),
           "rate_prev": round(rate_prev, 4) if rate_prev is not None else None,
           "ratio": round(ratio, 2) if ratio not in (None, float("inf")) else ratio,
           "supply_now": s11, "status_snapshot": old.get("status")}
    if passes: vel_pass.append(rec)
    elif (not token_scale) and minted >= 20: vel_near.append(rec)
    # free % (verified views only)
    fc, fm = d11.get("freeClaimed"), d11.get("freeMinted")
    fs = d11.get("FREE_SUPPLY") or old.get("FREE_SUPPLY") or old.get("freeSupply")
    if fc is not None and fs: free_pct[name] = fc / fs
    elif fm is not None and fs: free_pct[name] = fm / fs
    # sellout: free views hit cap
    if fc is not None and fs and fc >= fs: sellout_new.append((name, "freeClaimed", fc, fs))
    elif fm is not None and fs and fm >= fs: sellout_new.append((name, "freeMinted", fm, fs))
    # slot / balance changes vs snapshot
    if d11.get("freeClaimed_user") is not None and old.get("freeClaimed_user") is not None and d11["freeClaimed_user"] != old["freeClaimed_user"]:
        slot_ch.append((name, old["freeClaimed_user"], d11["freeClaimed_user"]))
    if d11.get("balanceOf_user") is not None and old.get("balanceOf_user") is not None and d11["balanceOf_user"] != old["balanceOf_user"]:
        bal_ch.append((name, old["balanceOf_user"], d11["balanceOf_user"]))
# track_c changes vs snapshot
tc_changes = []
for name, d in r11.get("track_c", {}).items():
    old = snap.get("track_c", {}).get(name, {})
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining", "totalShares", "sharesMinted"):
        if d.get(f) is not None and old.get(f) is not None and d[f] != old[f]:
            tc_changes.append([name, f, old[f], d[f]])
out = {"blocks": {"B9": B9, "B10": B10, "B11_estimated": B11,
                  "intervals_min": {"MIN_910": round(MIN_910,1), "MIN_1011": round(MIN_1011,1)}},
       "coverage": {"contracts_read": len(rr11), "track_c_read": len(r11.get("track_c", {})),
                    "supply_none": len(no_supply), "supply_none_list": no_supply},
       "velocity_pass": vel_pass, "velocity_near_ge20": vel_near,
       "free_pct_verified": free_pct,
       "free_pct_ge25": {k: round(v,4) for k, v in free_pct.items() if v >= 0.25},
       "sellout_new": sellout_new, "slot_changes": slot_ch, "balance_changes": bal_ch,
       "total_nft_scale_mints_interval": total_nft_mints,
       "track_c_changes": tc_changes}
json.dump(out, open(f"{HF}/run-2026-11-09-1001-velocity.json", "w"), indent=1)
print(f"contracts={len(rr11)} tc={len(r11.get('track_c',{}))} supply_none={len(no_supply)}")
print(f"VEL PASS: {len(vel_pass)}")
for r in vel_pass: print("  PASS", r["name"], f"+{r['minted']} ratio={r['ratio']} status={r['status_snapshot']}")
print(f"VEL NEAR (>=20, gagal): {len(vel_near)}")
for r in vel_near: print("  NEAR", r["name"], f"+{r['minted']} ratio={r['ratio']} status={r['status_snapshot']}")
print("FREE% >=25%:", {k: round(v,3) for k, v in free_pct.items() if v >= 0.25})
print("SELLOUT NEW:", sellout_new)
print("SLOT CH:", slot_ch)
print("BAL CH:", bal_ch)
print("TOTAL NFT mints interval:", total_nft_mints)
print("TC CHANGES:", tc_changes)
