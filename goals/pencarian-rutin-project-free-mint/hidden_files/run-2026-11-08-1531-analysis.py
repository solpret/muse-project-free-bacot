"""Analysis run 1531: velocity/sellout/slot/promotion/track-C from reread JSON.
Read-only vs snapshot; writes run-2026-11-08-1531-analysis.json only."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-08-1531-reread.json"))
block = rr["block"]
PREV_BLOCK = 132355740  # snapshot lastReadBlock (14:49 WIB)
INTERVAL_MIN = (block - PREV_BLOCK) * 0.45 / 60  # 6170 blocks -> ~46.3 min; wall 14:49->15:31 = 42 min
print(f"block {block} prev {PREV_BLOCK} interval_block_based {INTERVAL_MIN:.1f} min (wall 42 min)")
out = {"block": block, "interval_min_block_based": round(INTERVAL_MIN, 1),
       "interval_min_wall": 42, "started_wib": rr.get("started_wib"),
       "velocity_pass": [], "sellout_new": [], "slot_changes": [],
       "changes": [], "degraded": [], "not_in_reread": [],
       "early_lead_promotion_check": {}, "gate_failed_strong": {},
       "paw_gang": {}, "track_c": {}}

def supply_now(r):
    if r.get("totalSupply") is not None:
        return r["totalSupply"], "totalSupply"
    if r.get("totalMinted") is not None:
        return r["totalMinted"], "totalMinted"
    return None, None

for name, e in snap["contracts"].items():
    r = rr["reread"].get(name)
    if r is None:
        out["not_in_reread"].append(name)
        continue
    now, view = supply_now(r)
    if now is None:
        out["degraded"].append(name)
        continue
    prev = e.get("totalSupply") if view == "totalSupply" else e.get("totalMinted")
    if not isinstance(prev, int):
        prev = e.get("totalSupply")
    minted = now - prev if isinstance(prev, int) else None
    rate = (minted / INTERVAL_MIN) if isinstance(minted, int) else None
    prev_rate = e.get("currentRatePerMin")
    ratio = (rate / prev_rate) if (rate is not None and isinstance(prev_rate, (int, float)) and prev_rate) else None
    vel = bool(ratio is not None and ratio >= 1.5 and isinstance(minted, int) and minted >= 20)
    # free %
    fc = r.get("freeClaimed")
    fm = r.get("freeMinted")
    fs = e.get("FREE_SUPPLY") or e.get("freeSupply") or r.get("FREE_SUPPLY")
    freepct = None
    if isinstance(fc, int) and isinstance(fs, int) and fs:
        freepct = fc / fs * 100
    elif isinstance(fm, int) and isinstance(fs, int) and fs:
        freepct = fm / fs * 100
    # sellout
    sold = False
    if isinstance(fc, int) and isinstance(fs, int) and fs and fc >= fs:
        sold = True
    ms = r.get("MAX_SUPPLY") or e.get("MAX_SUPPLY")
    if isinstance(now, int) and isinstance(ms, int) and ms and view == "totalSupply" and now >= ms:
        sold = True
    if vel:
        out["velocity_pass"].append({"name": name, "address": e.get("address"), "minted": minted,
            "rate": round(rate, 4), "prev_rate": prev_rate,
            "ratio": round(ratio, 2) if ratio else None,
            "freePct": round(freepct, 1) if freepct is not None else None,
            "status": e.get("status")})
    if sold and "sold-out" not in str(e.get("status")) and "soldout" not in str(e.get("status")):
        out["sellout_new"].append({"name": name, "address": e.get("address"),
                "freeClaimed": fc, "freeMinted": fm, "FREE_SUPPLY": fs,
                "totalSupply_now": r.get("totalSupply"), "MAX_SUPPLY": ms,
                "status": e.get("status")})
    # user slot change
    bal = r.get("balanceOf_user")
    fcu = r.get("freeClaimed_user")
    old_bal = e.get("userBalance", e.get("balanceOf_user"))
    old_fcu = e.get("freeClaimed_user")
    slot_note = None
    if isinstance(bal, int) and isinstance(old_bal, int) and bal != old_bal:
        slot_note = f"balanceOf {old_bal}->{bal}"
    if isinstance(fcu, int) and isinstance(old_fcu, int) and fcu != old_fcu:
        slot_note = (slot_note + "; " if slot_note else "") + f"freeClaimed(user) {old_fcu}->{fcu}"
    if slot_note:
        out["slot_changes"].append({"name": name, "address": e.get("address"),
                "note": slot_note, "status": e.get("status")})
    if minted != 0 or freepct is not None:
        out["changes"].append({"name": name, "address": e.get("address"), "view": view,
                "prev": prev, "now": now, "minted": minted,
                "rate": round(rate, 4) if rate is not None else None,
                "prev_rate": prev_rate, "ratio": round(ratio, 2) if ratio else None,
                "velocity": vel, "freeClaimed": fc, "freeMinted": fm,
                "freePct": round(freepct, 2) if freepct is not None else None,
                "bal": bal, "freeClaimed_user": fcu, "status": e.get("status")})

# --- named checks ---
NAMED_EARLY = ["Undead NFTs", "CAISHEN", "Pixel Laptop", "NEKART", "Alchemister",
               "Alchemister-0xCafEEDDF", "0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B", "Agent Goats"]
for name in NAMED_EARLY:
    e = snap["contracts"].get(name)
    r = rr["reread"].get(name)
    if not e:
        out["early_lead_promotion_check"][name] = "NOT IN SNAPSHOT"
        continue
    now, view = supply_now(r) if r else (None, None)
    fc = r.get("freeClaimed") if r else None
    fm = r.get("freeMinted") if r else None
    fs = e.get("FREE_SUPPLY") or e.get("freeSupply") or (r.get("FREE_SUPPLY") if r else None)
    freepct = None
    if isinstance(fc, int) and isinstance(fs, int) and fs:
        freepct = fc / fs * 100
    elif isinstance(fm, int) and isinstance(fs, int) and fs:
        freepct = fm / fs * 100
    elif isinstance(e.get("freeClaimed"), int) and isinstance(fs, int) and fs:
        freepct = e["freeClaimed"] / fs * 100
    ch = next((c for c in out["changes"] if c["name"] == name), None)
    out["early_lead_promotion_check"][name] = {
        "address": e.get("address"), "status": e.get("status"),
        "totalSupply_snap": e.get("totalSupply"), "now": now, "view": view,
        "minted_interval": ch["minted"] if ch else None,
        "velocity": ch["velocity"] if ch else None,
        "freePct": round(freepct, 2) if freepct is not None else None,
        "freeClaimed_now": fc, "freeMinted_now": fm, "FREE_SUPPLY": fs,
        "bal_user_now": r.get("balanceOf_user") if r else None,
        "freeClaimed_user_now": r.get("freeClaimed_user") if r else None,
        "bal_user_snap": e.get("userBalance", e.get("balanceOf_user")),
        "firstMintWib": e.get("firstMintWib"), "launchNote": (e.get("launchNote") or "")[:300],
        "startTimeWib": e.get("startTimeWib"),
        "ageNote": (e.get("ageNote") or "")[:300],
        "freePctInference_snap": e.get("freePctInference"),
    }

for name in ["Jinli Agents", "Dafeiyu", "Chiphiveowl", "Farmbuxiang"]:
    e = snap["contracts"].get(name)
    r = rr["reread"].get(name)
    ch = next((c for c in out["changes"] if c["name"] == name), None)
    out["gate_failed_strong"][name] = {
        "address": e.get("address") if e else None, "status": e.get("status") if e else None,
        "totalSupply_snap": e.get("totalSupply") if e else None,
        "now": ch["now"] if ch else (r.get("totalSupply") if r else None),
        "minted_interval": ch["minted"] if ch else None,
        "freePct": ch["freePct"] if ch else None,
        "bal_user_now": r.get("balanceOf_user") if r else None,
        "freeClaimed_user_now": r.get("freeClaimed_user") if r else None,
        "bal_user_snap": e.get("userBalance", e.get("balanceOf_user")) if e else None,
        "slot_change": next((s for s in out["slot_changes"] if s["name"] == name), None),
    }

# Paw Gang read-only
pg = snap["contracts"].get("Paw Gang")
rp = rr["reread"].get("Paw Gang")
out["paw_gang"] = {
    "address": pg.get("address") if pg else None, "status": pg.get("status") if pg else None,
    "totalSupply_snap": pg.get("totalSupply") if pg else None,
    "totalMinted_snap": pg.get("totalMinted") if pg else None,
    "totalSupply_now": rp.get("totalSupply") if rp else None,
    "totalMinted_now": rp.get("totalMinted") if rp else None,
    "FREE_SUPPLY": pg.get("FREE_SUPPLY") if pg else None,
    "mintOpen_now": rp.get("mintOpen") if rp else None,
    "balanceOf_user_now": rp.get("balanceOf_user") if rp else None,
    "difficultyBits": "NOT READ by reread script (not in LEAN views); no PoW computation attempted",
    "firstMintWib": pg.get("firstMintWib") if pg else None,
}

# Track-C
for name, e in snap["track_c"].items():
    if not isinstance(e, dict):
        continue
    st = str(e.get("status") or "")
    if "lead" not in st or "not-a-lead" in st or "not-lead" in st:
        continue
    r = rr["track_c"].get(name)
    if r is None:
        out["track_c"][name] = {"status": st, "note": "NOT IN REREAD track_c output"}
        continue
    out["track_c"][name] = {
        "status": st, "sale": e.get("sale"),
        "totalSupply_now": r.get("totalSupply"), "freeMinted_now": r.get("freeMinted"),
        "freeSharesRemaining_now": r.get("freeSharesRemaining"),
        "balanceOf_user_now": r.get("balanceOf_user"),
        "freeClaimed_user_now": r.get("freeClaimed_user"),
        "snap_freeMinted": e.get("freeMinted"), "snap_freePoolRemaining": e.get("freePoolRemaining"),
        "snap_free_pool_note": e.get("free_pool"), "snap_userSlot": e.get("userSlot") or e.get("user_slot"),
        "snap_giftsClaimed": e.get("giftsClaimed"), "snap_giftsLeft": e.get("giftsLeft"),
        "fillDeadlineWib": e.get("fillDeadlineWib"), "saleStartWib": e.get("saleStartWib"),
        "snap_totalMints": e.get("totalMints"), "snap_MAX_MINTS": e.get("MAX_MINTS"),
        "snap_freeLeft_user": e.get("freeLeft_user"),
    }

print(json.dumps(out, indent=1)[:9000])
json.dump(out, open(f"{BASE}/run-2026-11-08-1531-analysis.json", "w"), indent=1)
print("WROTE analysis; velocity:", len(out["velocity_pass"]), "sellout_new:", len(out["sellout_new"]),
      "slot_changes:", len(out["slot_changes"]), "changes:", len(out["changes"]),
      "degraded:", len(out["degraded"]), "not_in_reread:", len(out["not_in_reread"]))
