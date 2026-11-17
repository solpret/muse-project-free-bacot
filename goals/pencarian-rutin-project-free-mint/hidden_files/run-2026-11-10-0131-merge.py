#!/usr/bin/env python3
"""Merge run 0131 (2026-11-10 01:31 WIB) reread into onchain-snapshot.json.
Generic merge (no run-0031-specific promotion blocks): velocity, free%,
sold-out detection with artifact guard, free>=25% screen for NEW crossings only.
BLOCK and INTERVAL are read from the reread JSON (prev block 132629190, run 0101).
Read-only except snapshot (backup first)."""
import json, datetime, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
PREV_BLOCK = 132629190
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0131")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
bak = json.load(open(f"{BASE}/onchain-snapshot.json.bak-0131"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0131-reread.json"))
BLOCK = rr.get("block") or PREV_BLOCK
INTERVAL = round((BLOCK - PREV_BLOCK) * 0.45 / 60.0, 1) if BLOCK > PREV_BLOCK else 30.0
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []; soldout_new = []; soldout_artifact = []; free25_new = []; free25_all = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL if INTERVAL else 0
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]:
            vel_pass.append((name, minted, round(ratio, 2)))
    old_free_pct = v.get("freePctVerified")
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    if isinstance(fs, int) and fs and isinstance(fcl, int) and fcl >= fs and "sold-out" not in str(v.get("status")):
        old = bak.get("contracts", {}).get(name, {})
        if old.get("freeClaimed") != fcl:
            soldout_new.append((name, fcl, fs))
        else:
            soldout_artifact.append(name)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0131_1110"] = (f"Run 0131 (blok {BLOCK}, interval {INTERVAL} mnt vs run 0101): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
    st = str(v.get("status") or "")
    if isinstance(v.get("freePctVerified"), (int, float)) and v["freePctVerified"] >= 25:
        free25_all.append((name, v["freePctVerified"], st))
        # NEW crossing only: prev free% < 25 and not already strong-lead/gate-failed/reported/sold-out
        if (isinstance(old_free_pct, (int, float)) and old_free_pct < 25
            and not any(x in st for x in ("sold-out", "excluded", "minted-by-user", "age-excluded", "discarded",
                                          "strong-lead", "gate-failed", "early-lead-reported"))):
            free25_new.append((name, old_free_pct, v["freePctVerified"], v.get("freeClaimed_user"),
                               v.get("balanceOf_user"), st, v.get("mintStartWib"), v.get("firstSeenWib")))
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict):
        continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0131_1110"] = f"Run 0131 track_c re-read (blok {BLOCK}): {r}."
    n_tc += 1
snap["last_run_wib"] = NOW_WIB
snap["runNote0131_1110"] = (f"Run 0131 (2026-11-10 01:31 WIB): reread {n_upd} kontrak + {n_tc} track_c (blok {BLOCK}, interval {INTERVAL} mnt). "
    f"Velocity LOLOS: {vel_pass}. Sold-out baru: {soldout_new}. Artefak freeClaimed==FREE_SUPPLY tak berubah: {len(soldout_artifact)} item. "
    f"Free>=25% baru crossing: {free25_new}. Free>=25% total: {len(free25_all)}.")
with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print(f"MERGED n_upd={n_upd} n_tc={n_tc} block={BLOCK} interval={INTERVAL} vel_pass={vel_pass}")
print(f"soldout_new={soldout_new} artifact_n={len(soldout_artifact)}")
print(f"free25_new={free25_new}")
print(f"free25_all_n={len(free25_all)}")
