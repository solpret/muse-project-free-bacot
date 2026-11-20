#!/usr/bin/env python3
"""Merge run 1331 (2026-11-17 13:31 WIB) reads into onchain-snapshot.json.
Baseline: run 1301 reread block 134068636. Head now = 134073286 (leg4 block read OK in run script).
(leg4_reread block read OK in run script).
Interval = (BLOCK-PREV_BLOCK)*0.45/60 min. Read-only on chain;
writes snapshot only. No new leads this run (see runlog)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r_prev = json.load(open(BASE + "run-2026-11-17-1301-reread.json"))["reads"]
r_cur = json.load(open(BASE + "run-2026-11-17-1331-reread.json"))["reads"]
run1331 = json.load(open(BASE + "run-2026-11-17-1331.json"))
BLOCK = 134073286  # leg4 block read OK in run script (1331 reread)
PREV_BLOCK = 134068636  # run 1301 leg4 block
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
# No retry override this run: binanceai-mint + RigForge views read OK in the
# run script itself (no /tmp/retry1331.json needed).
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
    e["lastReadWib"] = "2026-11-17 ~13:31 WIB"
    free = e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap = (e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else
           (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX")))
    pct = (round(100 * free / cap, 1) if isinstance(free, int) and isinstance(cap, int) and cap else None)
    if pct is not None:
        e["freePctVerified"] = pct
    vel_summary[name] = (minted, None if rate is None else round(rate, 3),
                         None if ratio is None else round(ratio, 2), vel, pct)
    if name == "binanceai-mint":
        note = (f"Run 1331: launched={cur_views.get('launched')}, failed={cur_views.get('failed')}, "
                f"isRefundPhase={cur_views.get('isRefundPhase')}, totalShares={cur_views.get('totalShares')}, "
                f"tokenClaimed(user)={cur_views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM.")
    elif name == "RigForge":
        note = (f"Run 1331: freeSharesLeft={cur_views.get('freeSharesLeft')}, openedAt={cur_views.get('openedAt')}, "
                f"freeClaimed={cur_views.get('freeClaimed')}, freeBooked(user)={cur_views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM.")
    elif name == "Zero":
        note = (f"Run 1331 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1231): totalSupply/freeClaimed tetap REVERT "
                f"(batch None, nilai lama dipertahankan); balanceOf(user)={cur_views.get('balanceOf_user')}. DIAM.")
    elif pct is not None:
        note = (f"Run 1331 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1231, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note = (f"Run 1331 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1231, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote1331_1117"] = note

print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k, v in vel_summary.items():
    print(" ", k, v)

# PXIO: no snapshot entry; velocity from reread files only.
# Prev rate = 1231->1301 interval (32.48 min, blocks 134064306->134068636).
r1231 = json.load(open(BASE + "run-2026-11-17-1231-reread.json"))["reads"]
px_prev = supply_of((r_prev.get("PXIO") or {}).get("views") or {})
px_cur = supply_of((r_cur.get("PXIO") or {}).get("views") or {})
px_minted = (px_cur - px_prev) if isinstance(px_cur, int) and isinstance(px_prev, int) else None
px_rate = (px_minted / INTERVAL_MIN) if px_minted is not None else None
px_1231 = supply_of((r1231.get("PXIO") or {}).get("views") or {})
px_prev_rate = ((px_prev - px_1231) / 32.48) if isinstance(px_prev, int) and isinstance(px_1231, int) else None  # (134068636-134064306)*0.45/60 = 32.48 min
px_ratio = (px_rate / px_prev_rate) if (px_rate is not None and px_prev_rate not in (None, 0)) else None
px_vel = bool(px_minted is not None and px_minted >= 20 and px_ratio is not None and px_ratio >= 1.5)
print("PXIO:", px_prev, "->", px_cur, "minted", px_minted, "rate",
      None if px_rate is None else round(px_rate, 2), "ratio",
      None if px_ratio is None else round(px_ratio, 2), "vel", px_vel,
      "(minted-by-user 17 Nov - bukan promosi)")

# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc:
    pc["lastReadWib"] = "2026-11-17 ~13:31 WIB"
    _bv = (r_cur.get("binanceai-mint") or {}).get("views") or {}
    pc["runNote1331"] = (f"Run 1331: launched={_bv.get('launched')}, failed={_bv.get('failed')}, isRefundPhase={_bv.get('isRefundPhase')}, totalShares={_bv.get('totalShares')}, "
                         f"tokenClaimed(user)={_bv.get('tokenClaimed_user')} (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM.")
# track_c RigForge + DogeRageFi + PEPE + bsccat
tc = snap.setdefault("track_c", {})
rf = tc.get("RigForge")
_rfv = (r_cur.get("RigForge") or {}).get("views") or {}
if isinstance(rf, dict):
    rf["freeSharesLeft"] = _rfv.get("freeSharesLeft")
    rf["openedAt"] = _rfv.get("openedAt")
    rf["freeClaimed"] = _rfv.get("freeClaimed")
    rf["lastReadWib"] = "2026-11-17 ~13:31 WIB"
    rf["runNote1331_1117"] = f"Run 1331: freeSharesLeft={_rfv.get('freeSharesLeft')}, openedAt={_rfv.get('openedAt')}, freeClaimed={_rfv.get('freeClaimed')} (blok {BLOCK}). Belum buka. DIAM."
dr = tc.get("DogeRageFi")
_drv = (r_cur.get("DogeRageFi") or {}).get("views") or {}
if isinstance(dr, dict):
    dr["totalMinted"] = _drv.get("totalMinted")
    dr["freeSupply"] = _drv.get("freeSupply")
    dr["maxSupply"] = _drv.get("maxSupply")
    dr["mintOpen"] = _drv.get("mintOpen")
    dr["lastReadWib"] = "2026-11-17 ~13:31 WIB"
    dr["runNote1331_1117"] = f"Run 1331: totalMinted={_drv.get('totalMinted')}, freeSupply={_drv.get('freeSupply')}/{_drv.get('maxSupply')}, mintOpen={_drv.get('mintOpen')}, bal_user={_drv.get('balanceOf_user')} (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
pepe = run1331.get("pepe_reread", {})
if isinstance(pepe, dict) and "freeMinted" in pepe:
    pp = tc.get("PEPE")
    if isinstance(pp, dict):
        pp["freeMinted"] = pepe.get("freeMinted")
        pp["soldShares"] = pepe.get("soldShares")
        pp["opened"] = pepe.get("opened")
        pp["hasMinted_user"] = pepe.get("hasMinted_user")
        pp["lastReadWib"] = "2026-11-17 ~13:31 WIB"
        pp["runNote1331_1117"] = (f"Run 1331: freeMinted={pepe.get('freeMinted')}/500, soldShares={pepe.get('soldShares')}, "
                                  f"opened={pepe.get('opened')}, hasMinted(user)={pepe.get('hasMinted_user')} (blok {BLOCK}). Tidak berubah. DIAM.")
bs = tc.get("bsccat")
if isinstance(bs, dict):
    bs["lastReadWib"] = "2026-11-17 ~13:31 WIB"
    bs["runNote1331_1117"] = f"Run 1331: tidak ada re-read baru (watchlist-only, umur unverified). DIAM."

# PXIO Miners MINTED BY USER 17 Nov ~10:58 WIB (user-confirmed; reread run ini:
# mintedBy_user 0->1, balanceOf_user 0->1, totalSupply 5422->6167).
# Mint tx 0x848f650be2c49704cbbf5d275002ba3e927d86d1ab7a8919c29840b3ee9f48e9,
# blok 134051566, token #5672, tier LABORER (mines 10 $PXIO/jam), batchId 4837.
# Mining DIMULAI 17 Nov ~11:07 WIB (user konfirmasi; start() tx
# 0x83cd69581a53a0831440a55204fd07bbbf3454cdddaf9da0cc899a7792df2161, blok
# 134052735; rate 10 $PXIO/jam, cap 150 $PXIO, storage penuh ~02:07 WIB 18 Nov).
# Listing: user putuskan SIMPAN 17 Nov ~11:05 WIB (market fixed 5 USDT/tier,
# fee ~0,00194 BNB > saldo agent). Status kini minted-by-user, bukan promosi.
px = snap.get("contracts", {}).get("PXIO Miners")
if isinstance(px, dict):
    px["status"] = "minted-by-user-2026-11-17"
    px["totalSupply"] = px_cur
    px["mintedBy_user"] = (r_cur.get("PXIO") or {}).get("views", {}).get("mintedBy_user")
    px["balanceOf_user"] = (r_cur.get("PXIO") or {}).get("views", {}).get("balanceOf_user")
    px["mintTx"] = "0x848f650be2c49704cbbf5d275002ba3e927d86d1ab7a8919c29840b3ee9f48e9"
    px["mintBlock"] = 134051566
    px["mintTokenId"] = 5672
    px["mintNote1331_1117"] = ("Run 1331: totalSupply 9227->9812 (+585, blok %d), mintedBy 2, balanceOf 2. "
        "Velocity %s (+%s, %s/mnt vs prev %s = %sx) TAPI sudah minted-by-user -> bukan promosi. "
        "Mining dimulai 11:07 WIB 17 Nov (10 PXIO/jam, cap 150); listing SIMPAN per keputusan user 11:05 WIB." % (
        BLOCK, "LOLOS" if px_vel else "GAGAL", px_minted,
        None if px_rate is None else round(px_rate, 2),
        None if px_prev_rate is None else round(px_prev_rate, 2),
        None if px_ratio is None else round(px_ratio, 2)))


# MORFO age-exclusion (run 1331): velocity LOLOS interval ini (+47 totalMinted
# 982->1029, ~1,45/mnt vs prev ~0,23/mnt = ~6,3x) TAPI free% UNVERIFIED (ABI
# Sourcify exact_match 2026-11-13T04:16:05Z: tanpa free view/quote/mintStart;
# totalMinted 1033/MAX_SUPPLY 25000 = 4,1% total-supply, BUKAN % kuota gratis)
# + umur TERVERIFIKASI >24 jam (sudah minting di run 2026-11-15 02:01 WIB,
# totalMinted ~717; Medium 15 Nov menyebut MORFO di batch mint 15 Nov) +
# website/X UNVERIFIED -> bukan kandidat/strong lead; umur >24 jam + belum sold
# out -> AGE-EXCLUDED, dihapus dari pantauan aktif (PLAN re-read run berikut).
# Tidak pernah dilaporkan sebagai lead -> DIAM (aturan age-excluded).
if snap.get("contracts", {}).get("MORFO", {}).get("status") != "age-excluded-2026-11-17":
        snap.setdefault("contracts", {})["MORFO"] = {
        "address": "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
        "name": "MORFO", "kind": "ERC721",
        "status": "age-excluded-2026-11-17",
        "totalSupply": None, "totalMinted": 1033, "MAX_SUPPLY": 25000,
        "freeMinted": None, "freeClaimed": None, "freePctVerified": None,
        "mintOpen": 1, "hasMinted_user": 0, "balanceOf_user": 0,
        "xVerified": False, "velocityVerified": True,
        "velocityLegPasses": True,
        "launchNote": "Usia TERVERIFIKASI >24 jam: sudah minting di run 2026-11-15 02:01 WIB (totalMinted ~717); Medium 15 Nov menyebut MORFO di batch free mint 15 Nov. Sourcify verifiedAt 2026-11-13T04:16:05Z bukan launch time.",
        "website": None, "gate": "not-checked-age-excluded",
        "lastReadBlock": BLOCK, "lastReadWib": "2026-11-17 ~13:31 WIB",
        "runNote1331_1117": ("Run 1331: AGE-EXCLUDED. totalMinted 982->1029 (+47, ~1,45/mnt vs prev ~0,23/mnt = ~6,3x), "
                             "velocity LOLOS TAPI free% UNVERIFIED (tanpa free view; 1033/25000 = 4,1% total-supply) + umur >24 jam terverifikasi "
                             "(minting sejak <=15 Nov 02:01 WIB) + website/X unverified -> bukan kandidat/strong lead; dihapus dari pantauan aktif. DIAM."),
    }

# hot-leg-seen: catat 4 kontrak feed baru run ini agar tidak di-shape-check ulang.
try:
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    if isinstance(seen, dict):
        for a in run1331.get("sourcify_feed", {}).get("new_contracts", []):
            seen.setdefault(a, {"first_seen": "free-mint-search-1331", "source": "sourcify-feed"})
        json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
        print("hot-leg-seen updated:", len(seen))
    else:
        print("hot-leg-seen not a dict, skipped")
except Exception as e:
    print("hot-leg-seen update failed:", type(e).__name__, str(e)[:120])

snap["last_run_wib"] = "2026-11-17 ~13:31 WIB"
snap["last_run"] = "2026-11-17 ~13:31 WIB"
snap["runNote1331_1117"] = open(BASE + "run-2026-11-17-1331-summary.txt").read().strip()

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
