#!/usr/bin/env python3
"""Merge run 0301 (2026-11-17 03:01 WIB) reads into onchain-snapshot.json.
Baseline: run 0231 reread block 133984444. Head now 133988370.
Interval = (133988370-133984444)*0.45/60 = 29.45 min. Read-only on chain;
writes snapshot only. No new leads this run (see runlog)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r_prev = json.load(open(BASE + "run-2026-11-17-0231-reread.json"))["reads"]
r_cur = json.load(open(BASE + "run-2026-11-17-0301-reread.json"))["reads"]
run0301 = json.load(open(BASE + "run-2026-11-17-0301.json"))
BLOCK = run0301["leg4_reread"]["block"]
PREV_BLOCK = 133984444
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
# DRAGON/XCOPY were first read in verify-reads (not reread) at 0231; baseline = snapshot stored.
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
    baseline_note = "reread 0231"
    if ps is None and name in SNAP_BASELINE:
        ps = SNAP_BASELINE[name]
        baseline_note = "snapshot stored (first reread; 0231 read via verify-reads)"
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
    e["lastReadWib"] = "2026-11-17 ~03:01 WIB"
    free = e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap = (e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else
           (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX")))
    pct = (round(100 * free / cap, 1) if isinstance(free, int) and isinstance(cap, int) and cap else None)
    if pct is not None:
        e["freePctVerified"] = pct
    vel_summary[name] = (minted, None if rate is None else round(rate, 3),
                         None if ratio is None else round(ratio, 2), vel, pct)
    if name == "binanceai-mint":
        note = (f"Run 0301: launched={cur_views.get('launched')}, failed={cur_views.get('failed')}, "
                f"isRefundPhase={cur_views.get('isRefundPhase')}, totalShares={cur_views.get('totalShares')}, "
                f"tokenClaimed(user)={cur_views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM.")
    elif name == "RigForge":
        note = (f"Run 0301: freeSharesLeft={cur_views.get('freeSharesLeft')}, openedAt={cur_views.get('openedAt')}, "
                f"freeClaimed={cur_views.get('freeClaimed')}, freeBooked(user)={cur_views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM.")
    elif name == "Zero":
        note = (f"Run 0301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0231): totalSupply/freeClaimed tetap REVERT "
                f"(batch None, nilai lama dipertahankan); balanceOf(user)={cur_views.get('balanceOf_user')}. DIAM.")
    elif pct is not None:
        note = (f"Run 0301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0231, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note = (f"Run 0301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0231, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote0301_1117"] = note

print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k, v in vel_summary.items():
    print(" ", k, v)

# PXIO: no snapshot entry; velocity from reread files only.
r0201 = json.load(open(BASE + "run-2026-11-17-0201-reread.json"))["reads"]
px_prev = supply_of((r_prev.get("PXIO") or {}).get("views") or {})
px_cur = supply_of((r_cur.get("PXIO") or {}).get("views") or {})
px_minted = (px_cur - px_prev) if isinstance(px_cur, int) and isinstance(px_prev, int) else None
px_rate = (px_minted / INTERVAL_MIN) if px_minted is not None else None
px_0201 = supply_of((r0201.get("PXIO") or {}).get("views") or {})
px_prev_rate = ((px_prev - px_0201) / 31.67) if isinstance(px_prev, int) and isinstance(px_0201, int) else None
px_ratio = (px_rate / px_prev_rate) if (px_rate is not None and px_prev_rate not in (None, 0)) else None
px_vel = bool(px_minted is not None and px_minted >= 20 and px_ratio is not None and px_ratio >= 1.5)
print("PXIO:", px_prev, "->", px_cur, "minted", px_minted, "rate",
      None if px_rate is None else round(px_rate, 2), "ratio",
      None if px_ratio is None else round(px_ratio, 2), "vel", px_vel)

# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc:
    pc["lastReadWib"] = "2026-11-17 ~03:01 WIB"
    pc["runNote0301"] = (f"Run 0301: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                         f"tokenClaimed(user)=0 (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM.")
# track_c RigForge + DogeRageFi + PEPE + bsccat
tc = snap.setdefault("track_c", {})
rf = tc.get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = 636
    rf["openedAt"] = 0
    rf["freeClaimed"] = 364
    rf["lastReadWib"] = "2026-11-17 ~03:01 WIB"
    rf["runNote0301_1117"] = f"Run 0301: freeSharesLeft=636, openedAt=0, freeClaimed=364 (blok {BLOCK}). Belum buka. DIAM."
dr = tc.get("DogeRageFi")
if isinstance(dr, dict):
    dr["totalMinted"] = 229
    dr["freeSupply"] = 432
    dr["maxSupply"] = 666
    dr["mintOpen"] = 1
    dr["lastReadWib"] = "2026-11-17 ~03:01 WIB"
    dr["runNote0301_1117"] = f"Run 0301: totalMinted=229, freeSupply=432/666, mintOpen=1, bal_user=0 (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."
pepe = run0301.get("pepe_reread", {})
if isinstance(pepe, dict) and "freeMinted" in pepe:
    pp = tc.get("PEPE")
    if isinstance(pp, dict):
        pp["freeMinted"] = pepe.get("freeMinted")
        pp["soldShares"] = pepe.get("soldShares")
        pp["opened"] = pepe.get("opened")
        pp["hasMinted_user"] = pepe.get("hasMinted_user")
        pp["lastReadWib"] = "2026-11-17 ~03:01 WIB"
        pp["runNote0301_1117"] = (f"Run 0301: freeMinted={pepe.get('freeMinted')}/500, soldShares={pepe.get('soldShares')}, "
                                  f"opened={pepe.get('opened')}, hasMinted(user)={pepe.get('hasMinted_user')} (blok {BLOCK}). Tidak berubah. DIAM.")
bs = tc.get("bsccat")
if isinstance(bs, dict):
    bs["lastReadWib"] = "2026-11-17 ~03:01 WIB"
    bs["runNote0301_1117"] = f"Run 0301: tidak ada re-read baru (watchlist-only, umur unverified). DIAM."

snap["last_run_wib"] = "2026-11-17 ~03:01 WIB"
snap["last_run"] = "2026-11-17 ~03:01 WIB"
snap["runNote0301_1117"] = (
    f"Run 0301 (03:01 WIB): re-read 49/49 OK (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0231). "
    f"Velocity LOLOS: tidak ada. DRAGON +94 (227->321, 3,19/mnt, baseline pertama - belum ada rate sebelumnya, velocity TIDAK lulus run ini; "
    f"free 321/1000 = 32,1% <50%, umur VERIFIED ~7,2 jam, slot user open) - tetap EARLY lead, bukan kandidat/strong lead. "
    f"XCOPY +16 (308->324, 0,54/mnt, baseline pertama; free% + umur + slot UNVERIFIED) - tetap EARLY lead. "
    f"PXIO +100 (3,40/mnt, 0,87x vs prev 3,88) - velocity GAGAL; free% + umur UNVERIFIED. "
    f"Gerakan lain: Matrix +1 (570/1000 = 57,0%), AGCLUB flat (515/888 = 58,0%), Ledgera flat (2691/5000 = 53,8%), RaceAgents flat (631/1000 = 63,1%), "
    f"ALIEN +10, Punch Card +6, Kryntar +12, LumenFindings +7 spesimen, SPARKS +2, BoldLeonidas +1, MORFO +1 - semua velocity GAGAL. "
    f"Threshold >70%: tidak ada yang tembus (AgentBubble 1653/2222 = 74,4% dari MAX tapi free-cap + umur unverified). "
    f"Zephyra/Pengu flat (961, 138/138); Zero tetap REVERT. Vezlune/Poffzi tetap sold-out-free. binanceai tetap refund. RigForge belum buka; PEPE tidak berubah (freeMinted 500/500). "
    f"BARU: tidak ada - Sourcify 0 baru; Boltbook 1 'baru' 0x57e2... (ABI kosong, n_fns=0, bukan sale shape, bukan lead); "
    f"Ankr pre-flight GAGAL HTTP 401 (ke-11 berturut-turut) -> scan FAST-FAIL, watermark TETAP 132512564; 5c dilewati (tanpa output scan). "
    f"Sweep EN+ZH + Odaily: hanya proyek lama (Agentic Gangster 9 Nov, RIGBYPASS 10 Nov, MOLT AGENT 6 Nov, AGENT COSMOS 5 Nov - semua sudah di snapshot) - 0 baru. "
    f"Bridge 116 kontrak, 0 di luar snapshot. Hot-leg terakhir 0259 (Matrix +1). Eksekusi: tidak ada."
)

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
