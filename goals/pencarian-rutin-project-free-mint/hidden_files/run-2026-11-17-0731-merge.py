#!/usr/bin/env python3
"""Merge run 0731 (2026-11-17 07:31 WIB) reads into onchain-snapshot.json.
Baseline: run 0701 reread block 134020958. Head now = leg4_reread block 134024585.
Interval = (BLOCK-134016330)*0.45/60 min. Read-only on chain;
writes snapshot only. No new leads this run (see runlog)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r_prev = json.load(open(BASE + "run-2026-11-17-0701-reread.json"))["reads"]
r_cur = json.load(open(BASE + "run-2026-11-17-0731-reread.json"))["reads"]
run0731 = json.load(open(BASE + "run-2026-11-17-0731.json"))
BLOCK = 134024585  # leg4_reread block from run script (eth_blockNumber OK)
PREV_BLOCK = 134020958
INTERVAL_MIN = round((BLOCK - PREV_BLOCK) * 0.45 / 60, 2)
byaddr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and v.get("address"):
        byaddr[v["address"].lower()] = (k, v)

def supply_of(views):
    if views is None:
        return None
    if views.get("totalMinted") is not None:
        return views.get("totalMinted")
    return views.get("totalSupply")

FIELDS = ["totalSupply", "totalMinted", "freeMinted", "freeClaimed", "FREE_SUPPLY",
          "FREE_CAP", "FREE_MAX", "MAX_SUPPLY", "mintOpen", "freeRemaining",
          "remainingSupply", "remaining", "totalShares", "launched", "failed", "isRefundPhase",
          "claimOpen", "totalSpecimens", "currentExperiment", "genesisStart",
          "genesisOpen", "freeSharesLeft", "openedAt", "freeSupply", "maxSupply",
          "saleStart", "saleOpen", "saleEnd", "standardRemaining",
          "legendaryRemaining", "isFreePhase", "freeLeft", "mintsLeft", "PRICE",
          "FREE_MINT_CAP", "freeMintsLeft", "mintStart", "mintEnd", "mintEnded",
          "paidMinted"]
UFIELDS = ["balanceOf_user", "freeUsed_user", "freeClaimed_user", "mintedBy_user",
           "hasFreeClaimed_user", "tokenClaimed_user", "freeBooked_user",
           "freeDone_user", "cost_user_1", "holdsAgentId_user"]
# DRAGON/XCOPY were first read in verify-reads (not reread) at 0401; baseline = snapshot stored.
SNAP_BASELINE = {"DRAGON": 227, "XCOPY": 308}
vel_summary = {}
for name, cur in r_cur.items():
    addr = cur["address"].lower()
    ent = byaddr.get(addr)
    if ent is None:
        print(name, "no snapshot entry, skipped")
        continue
    key, e = ent
    cur_views = dict(cur.get("views") or {})
    prev_views = (r_prev.get(name) or {}).get("views") or {}
    ps, ns = supply_of(prev_views), supply_of(cur_views)
    baseline_note = "reread 0601"
    if ps is None and name in SNAP_BASELINE:
        ps = SNAP_BASELINE[name]
        baseline_note = "snapshot stored (first reread; 0401 read via verify-reads)"
    minted = (ns - ps) if isinstance(ns, int) and isinstance(ps, int) else None
    prev_rate = e.get("currentRatePerMin")
    rate = (minted / INTERVAL_MIN) if minted is not None else None
    ratio = (rate / prev_rate) if (rate is not None and prev_rate not in (None, 0)) else None
    vel = bool(minted is not None and minted >= 20 and ratio is not None and ratio >= 1.5)
    for f in FIELDS + UFIELDS:
        if f in cur_views and cur_views[f] is not None:
            e[f] = cur_views[f]
    e["previousTotalSupply"] = ps
    e["mintedInInterval"] = minted
    e["intervalMinutes"] = INTERVAL_MIN
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = vel
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-17 ~07:01 WIB"
    free = e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap = (e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else
           (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX")))
    pct = (round(100 * free / cap, 1) if isinstance(free, int) and isinstance(cap, int) and cap else None)
    if pct is not None:
        e["freePctVerified"] = pct
    vel_summary[name] = (minted, None if rate is None else round(rate, 3),
                         None if ratio is None else round(ratio, 2), vel, pct)
    if name == "binanceai-mint":
        note = (f"Run 0731: launched={cur_views.get('launched')}, failed={cur_views.get('failed')}, "
                f"isRefundPhase={cur_views.get('isRefundPhase')}, totalShares={cur_views.get('totalShares')}, "
                f"tokenClaimed(user)={cur_views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM.")
    elif name == "RigForge":
        note = (f"Run 0731: freeSharesLeft={cur_views.get('freeSharesLeft')}, openedAt={cur_views.get('openedAt')}, "
                f"freeClaimed={cur_views.get('freeClaimed')}, freeBooked(user)={cur_views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM.")
    elif name == "Zero":
        note = (f"Run 0731 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0701): totalSupply/freeClaimed tetap REVERT "
                f"(batch None, nilai lama dipertahankan); balanceOf(user)={cur_views.get('balanceOf_user')}. DIAM.")
    elif pct is not None:
        note = (f"Run 0731 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0701, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note = (f"Run 0731 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0701, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote0731_1117"] = note

print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k, v in vel_summary.items():
    print(" ", k, v)

# PXIO: no snapshot entry; velocity from reread files only.
# Prev rate = 0601->0701 interval (29.62 min, blocks 134012380->134016330).
r0601 = json.load(open(BASE + "run-2026-11-17-0601-reread.json"))["reads"]
px_prev = supply_of((r_prev.get("PXIO") or {}).get("views") or {})
px_cur = supply_of((r_cur.get("PXIO") or {}).get("views") or {})
px_minted = (px_cur - px_prev) if isinstance(px_cur, int) and isinstance(px_prev, int) else None
px_rate = (px_minted / INTERVAL_MIN) if px_minted is not None else None
px_0601 = supply_of((r0601.get("PXIO") or {}).get("views") or {})
px_prev_rate = ((px_prev - px_0601) / 29.62) if isinstance(px_prev, int) and isinstance(px_0601, int) else None
px_ratio = (px_rate / px_prev_rate) if (px_rate is not None and px_prev_rate not in (None, 0)) else None
px_vel = bool(px_minted is not None and px_minted >= 20 and px_ratio is not None and px_ratio >= 1.5)
print("PXIO:", px_prev, "->", px_cur, "minted", px_minted, "rate",
      None if px_rate is None else round(px_rate, 2), "ratio",
      None if px_ratio is None else round(px_ratio, 2), "vel", px_vel)

# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc:
    pc["lastReadWib"] = "2026-11-17 ~07:01 WIB"
    _bv = (r_cur.get("binanceai-mint") or {}).get("views") or {}
    pc["runNote0731"] = (f"Run 0731: launched={_bv.get('launched')}, failed={_bv.get('failed')}, isRefundPhase={_bv.get('isRefundPhase')}, totalShares={_bv.get('totalShares')}, "
                         f"tokenClaimed(user)={_bv.get('tokenClaimed_user')} (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM.")
# track_c RigForge + DogeRageFi + PEPE + bsccat
tc = snap.setdefault("track_c", {})
rf = tc.get("RigForge")
_rfv = (r_cur.get("RigForge") or {}).get("views") or {}
if isinstance(rf, dict):
    rf["freeSharesLeft"] = _rfv.get("freeSharesLeft")
    rf["openedAt"] = _rfv.get("openedAt")
    rf["freeClaimed"] = _rfv.get("freeClaimed")
    rf["lastReadWib"] = "2026-11-17 ~07:01 WIB"
    rf["runNote0731_1117"] = f"Run 0731: freeSharesLeft={_rfv.get('freeSharesLeft')}, openedAt={_rfv.get('openedAt')}, freeClaimed={_rfv.get('freeClaimed')} (blok {BLOCK}). Belum buka. DIAM."
dr = tc.get("DogeRageFi")
_drv = (r_cur.get("DogeRageFi") or {}).get("views") or {}
if isinstance(dr, dict):
    dr["totalMinted"] = _drv.get("totalMinted")
    dr["freeSupply"] = _drv.get("freeSupply")
    dr["maxSupply"] = _drv.get("maxSupply")
    dr["mintOpen"] = _drv.get("mintOpen")
    dr["lastReadWib"] = "2026-11-17 ~07:01 WIB"
    dr["runNote0731_1117"] = f"Run 0731: totalMinted={_drv.get('totalMinted')}, freeSupply={_drv.get('freeSupply')}/{_drv.get('maxSupply')}, mintOpen={_drv.get('mintOpen')}, bal_user={_drv.get('balanceOf_user')} (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
pepe = run0731.get("pepe_reread", {})
if isinstance(pepe, dict) and "freeMinted" in pepe:
    pp = tc.get("PEPE")
    if isinstance(pp, dict):
        pp["freeMinted"] = pepe.get("freeMinted")
        pp["soldShares"] = pepe.get("soldShares")
        pp["opened"] = pepe.get("opened")
        pp["hasMinted_user"] = pepe.get("hasMinted_user")
        pp["lastReadWib"] = "2026-11-17 ~07:01 WIB"
        pp["runNote0731_1117"] = (f"Run 0731: freeMinted={pepe.get('freeMinted')}/500, soldShares={pepe.get('soldShares')}, "
                                  f"opened={pepe.get('opened')}, hasMinted(user)={pepe.get('hasMinted_user')} (blok {BLOCK}). Tidak berubah. DIAM.")
bs = tc.get("bsccat")
if isinstance(bs, dict):
    bs["lastReadWib"] = "2026-11-17 ~07:01 WIB"
    bs["runNote0731_1117"] = f"Run 0731: tidak ada re-read baru (watchlist-only, umur unverified). DIAM."

snap["last_run_wib"] = "2026-11-17 ~07:01 WIB"
snap["last_run"] = "2026-11-17 ~07:01 WIB"
snap["runNote0731_1117"] = open(BASE + "run-2026-11-17-0731-summary.txt").read().strip()

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
