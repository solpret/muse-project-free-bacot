"""Analysis run 1731: velocity/sellout/slot/promotion/track-C + named flags.
Read-only vs snapshot; writes run-2026-11-08-1731-analysis.json only.
NEVER edits onchain-snapshot.json / state / seen files."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-1731"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
block = rr["block"]
PREV_BLOCK = 132373045  # 1631 reread block
INTERVAL_MIN = (block - PREV_BLOCK) * 0.45 / 60
NOW = datetime.datetime(2026, 11, 8, 17, 35)  # WIB approx at analysis time
CUTOFF = NOW - datetime.timedelta(hours=48)
print(f"block {block} prev {PREV_BLOCK} interval_block_based {INTERVAL_MIN:.1f} min (wall ~30 min 17:02->17:32)")
out = {"block": block, "interval_min_block_based": round(INTERVAL_MIN, 1),
       "interval_min_wall": 30, "started_wib": rr.get("started_wib"),
       "velocity_pass": [], "sellout_new": [], "sellout_genuinely_new_vs_1631": [],
       "slot_changes": [], "changes": [], "degraded": [], "not_in_reread": [],
       "early_lead_promotion_check": {}, "gate_failed_strong": {},
       "paw_gang": {}, "track_c": {}, "track_c_changes": [],
       "voltlings": {}, "hive": {}, "ink_koi": {}, "age_exclusion_candidates": [],
       "binanceai": {}}
try:
    a1601 = json.load(open(f"{BASE}/run-2026-11-08-1631-analysis.json"))
    sellout_1601 = set(s["name"] for s in a1601.get("sellout_new", []))
except Exception:
    sellout_1601 = set()

def supply_now(r):
    if r.get("totalSupply") is not None:
        return r["totalSupply"], "totalSupply"
    if r.get("totalMinted") is not None:
        return r["totalMinted"], "totalMinted"
    return None, None

TERMINAL = ("sold-out", "age-excluded", "minted-by-user", "excluded",
            "promotion-discarded", "same-owner-discarded", "paid-only")

def parse_wib(s):
    if not isinstance(s, str):
        return None
    s = s.replace(" WIB", "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def launch_time(e):
    for k in ("firstMintWib", "startTimeWib", "launchTimeWib", "saleStartWib"):
        t = parse_wib(e.get(k))
        if t:
            return t, k
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
    fc = r.get("freeClaimed")
    fm = r.get("freeMinted")
    fs = e.get("FREE_SUPPLY") or e.get("freeSupply") or r.get("FREE_SUPPLY")
    freepct = None
    if isinstance(fc, int) and isinstance(fs, int) and fs:
        freepct = fc / fs * 100
    elif isinstance(fm, int) and isinstance(fs, int) and fs:
        freepct = fm / fs * 100
    sold = False
    if isinstance(fc, int) and isinstance(fs, int) and fs and fc >= fs:
        sold = True
    if isinstance(fm, int) and isinstance(fs, int) and fs and fm >= fs:
        sold = True
    ms = r.get("MAX_SUPPLY") or e.get("MAX_SUPPLY")
    if isinstance(now, int) and isinstance(ms, int) and ms and view == "totalSupply" and now >= ms:
        sold = True
    if vel:
        out["velocity_pass"].append({"name": name, "address": e.get("address"), "minted": minted,
            "rate": round(rate, 4), "prev_rate": prev_rate,
            "ratio": round(ratio, 2) if ratio else None,
            "freePct": round(freepct, 1) if freepct is not None else None,
            "freePct_verified": freepct is not None,
            "status": e.get("status")})
    if sold and "sold-out" not in str(e.get("status")) and "soldout" not in str(e.get("status")):
        rec = {"name": name, "address": e.get("address"),
                "freeClaimed": fc, "freeMinted": fm, "FREE_SUPPLY": fs,
                "totalSupply_now": r.get("totalSupply"), "MAX_SUPPLY": ms,
                "status": e.get("status")}
        out["sellout_new"].append(rec)
        if name not in sellout_1601:
            out["sellout_genuinely_new_vs_1631"].append(rec)
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
    # age-exclusion candidate: verified launch >48h, not sold out, status not terminal
    if not sold and not any(x in str(e.get("status")) for x in TERMINAL):
        lt, lsrc = launch_time(e)
        if lt and lt < CUTOFF:
            out["age_exclusion_candidates"].append({
                "name": name, "address": e.get("address"), "status": e.get("status"),
                "launch_source": lsrc, "launch_wib": lt.strftime("%Y-%m-%d %H:%M:%S WIB"),
                "age_hours": round((NOW - lt).total_seconds() / 3600, 1),
                "totalSupply_now": now, "freeClaimed_now": fc, "freeMinted_now": fm,
                "FREE_SUPPLY": fs, "freePct": round(freepct, 2) if freepct is not None else None,
                "firstMintBlock": e.get("firstMintBlock")})

# --- named checks: Voltlings / HIVE / Ink Koi ---
def named(name):
    e = snap["contracts"].get(name)
    r = rr["reread"].get(name)
    if not e:
        return {"note": "NOT IN SNAPSHOT"}
    now, view = supply_now(r) if r else (None, None)
    fc = r.get("freeClaimed") if r else None
    fm = r.get("freeMinted") if r else None
    fs = e.get("FREE_SUPPLY") or e.get("freeSupply") or (r.get("FREE_SUPPLY") if r else None)
    freepct = None
    if isinstance(fc, int) and isinstance(fs, int) and fs:
        freepct = fc / fs * 100
    elif isinstance(fm, int) and isinstance(fs, int) and fs:
        freepct = fm / fs * 100
    ch = next((c for c in out["changes"] if c["name"] == name), None)
    lt, lsrc = launch_time(e)
    return {"address": e.get("address"), "status": e.get("status"),
            "totalSupply_snap": e.get("totalSupply"), "totalMinted_snap": e.get("totalMinted"),
            "now": now, "view": view, "minted_interval": ch["minted"] if ch else None,
            "rate": ch["rate"] if ch else None, "prev_rate": e.get("currentRatePerMin"),
            "ratio": ch["ratio"] if ch else None, "velocity": ch["velocity"] if ch else None,
            "freeClaimed_now": fc, "freeMinted_now": fm, "FREE_SUPPLY": fs,
            "freePct": round(freepct, 2) if freepct is not None else None,
            "free_remaining": (fs - fm) if (isinstance(fs, int) and isinstance(fm, int)) else None,
            "sold_out": bool(isinstance(fm, int) and isinstance(fs, int) and fs and fm >= fs),
            "mintOpen_now": r.get("mintOpen") if r else None,
            "balanceOf_user_now": r.get("balanceOf_user") if r else None,
            "freeClaimed_user_now": r.get("freeClaimed_user") if r else None,
            "balanceOf_user_snap": e.get("userBalance", e.get("balanceOf_user")),
            "freeClaimed_user_snap": e.get("freeClaimed_user"),
            "claimedFree_user_snap": e.get("claimedFree_user"),
            "launch_source": lsrc, "launch_wib": lt.strftime("%Y-%m-%d %H:%M:%S WIB") if lt else None,
            "firstMintBlock": e.get("firstMintBlock"),
            "slot_change": next((s for s in out["slot_changes"] if s["name"] == name), None)}

out["voltlings"] = named("Voltlings")
out["hive"] = named("HIVE Agents")
out["ink_koi"] = named("0xbd4B4e7189ae9356514664146b0eD683601200A9")

# --- named early-lead promotion checks (continuity from 1631) ---
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
        "firstMintWib": e.get("firstMintWib"), "startTimeWib": e.get("startTimeWib")}

# --- gate-failed strong leads ---
for name in ["Jinli Agents", "Dafeiyu", "Chiphiveowl", "Farmbuxiang",
             "0x1fab92b937572c79550aeee51cee77d3add20367",
             "0xa8543350e5accacc780c9613bfa2fb9b52d3858e"]:
    e = snap["contracts"].get(name)
    r = rr["reread"].get(name)
    ch = next((c for c in out["changes"] if c["name"] == name), None)
    out["gate_failed_strong"][name] = {
        "address": e.get("address") if e else None, "status": e.get("status") if e else None,
        "totalSupply_snap": e.get("totalSupply") if e else None,
        "now": ch["now"] if ch else (r.get("totalSupply") if r else None),
        "minted_interval": ch["minted"] if ch else None,
        "rate": ch["rate"] if ch else None, "prev_rate": e.get("currentRatePerMin") if e else None,
        "ratio": ch["ratio"] if ch else None, "velocity": ch["velocity"] if ch else None,
        "freePct": ch["freePct"] if ch else None,
        "freeClaimed_now": r.get("freeClaimed") if r else None,
        "freeMinted_now": r.get("freeMinted") if r else None,
        "FREE_SUPPLY": e.get("FREE_SUPPLY") if e else None,
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

# Track-C: lead-status detail + changes vs snapshot for all read entries
for name, e in snap["track_c"].items():
    if not isinstance(e, dict):
        continue
    st = str(e.get("status") or "")
    r = rr["track_c"].get(name)
    if "lead" in st and "not-a-lead" not in st and "not-lead" not in st:
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
    if r is not None:
        diffs = {}
        for snap_k, rr_k in (("freeMinted", "freeMinted"),
                             ("freePoolRemaining", "freeSharesRemaining"),
                             ("balanceOf_user", "balanceOf_user"),
                             ("freeClaimed_user", "freeClaimed_user"),
                             ("totalSupply", "totalSupply")):
            sv, rv = e.get(snap_k), r.get(rr_k)
            if isinstance(sv, int) and isinstance(rv, int) and sv != rv:
                diffs[snap_k] = f"{sv}->{rv}"
        if diffs:
            out["track_c_changes"].append({"name": name, "status": st, "diffs": diffs,
                    "sale": e.get("sale")})

# binanceai comparison
try:
    b1631 = json.load(open(f"{BASE}/run-{TS}-binanceai.json"))
    b1601 = json.load(open(f"{BASE}/run-2026-11-08-1631-binanceai.json"))
    out["binanceai"] = {"run_1731": b1631, "run_1631": b1601,
                        "changed": {k: (b1601.get(k), b1631.get(k))
                                    for k in set(b1601) | set(b1631)
                                    if b1601.get(k) != b1631.get(k)},
                        "snapshot_state": snap.get("binanceai_claim", {}).get("status")}
except Exception as ex:
    out["binanceai"] = {"error": str(ex)}

# MarsAgent one-off (hot-leg 17:19 mintOpen 1->0; NOT in snapshot)
try:
    m = json.load(open(f"{BASE}/run-{TS}-marsagent.json"))
    out["marsagent"] = m
except Exception as ex:
    out["marsagent"] = {"error": str(ex)}

json.dump(out, open(f"{BASE}/run-{TS}-analysis.json", "w"), indent=1)
print("WROTE analysis; velocity:", len(out["velocity_pass"]), "sellout_new:", len(out["sellout_new"]),
      "genuinely_new_sellout:", len(out["sellout_genuinely_new_vs_1631"]),
      "slot_changes:", len(out["slot_changes"]), "changes:", len(out["changes"]),
      "degraded:", len(out["degraded"]), "not_in_reread:", len(out["not_in_reread"]),
      "age_excl_candidates:", len(out["age_exclusion_candidates"]),
      "track_c_changes:", len(out["track_c_changes"]))
