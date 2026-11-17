#!/usr/bin/env python3
"""Merge run 0031 (2026-11-17 00:31 WIB) reads into onchain-snapshot.json.
Baseline: run 0001 reread block 133964440. Head now 133968621.
Interval = (133968621-133964440)*0.45/60 = 31.36 min. Read-only on chain;
writes snapshot only. Single-call verified (3 endpoints) values override:
Zephyra totalMinted 961, Pengu totalMinted/freeMinted 138/138, Kryntar
totalMinted 1318 + standardRemaining 793 + legendaryRemaining 111 + mintOpen 1;
Zero totalSupply/freeClaimed still REVERT on all 3 (old values kept)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r0001 = json.load(open(BASE + "run-2026-11-17-0001-reread.json"))["reads"]
r0031 = json.load(open(BASE + "run-2026-11-17-0031-reread.json"))["reads"]
BLOCK = 133968621
PREV_BLOCK = 133964440
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

VERIFIED = {
    "Zephyra": {"totalMinted": 961},
    "Pengu": {"totalMinted": 138, "freeMinted": 138},
    "Kryntar": {"totalMinted": 1318, "standardRemaining": 793,
                "legendaryRemaining": 111, "mintOpen": 1},
    "Zero": {"totalSupply": "REVERT", "freeClaimed": "REVERT"},
    "AgentNOVA": {"totalSupply": 684},
}
FIELDS = ["totalSupply", "totalMinted", "freeMinted", "freeClaimed", "FREE_SUPPLY",
          "FREE_CAP", "FREE_MAX", "MAX_SUPPLY", "mintOpen", "freeRemaining",
          "remainingSupply", "totalShares", "launched", "failed", "isRefundPhase",
          "claimOpen", "totalSpecimens", "currentExperiment", "genesisStart",
          "genesisOpen", "freeSharesLeft", "openedAt", "freeSupply", "maxSupply",
          "saleStart", "saleOpen", "saleEnd", "standardRemaining",
          "legendaryRemaining", "isFreePhase", "freeLeft", "mintsLeft", "PRICE",
          "FREE_MINT_CAP", "freeMintsLeft"]
UFIELDS = ["balanceOf_user", "freeUsed_user", "freeClaimed_user", "mintedBy_user",
           "hasFreeClaimed_user", "tokenClaimed_user", "freeBooked_user",
           "freeDone_user", "cost_user_1", "holdsAgentId_user"]
vel_summary = {}
for name, cur in r0031.items():
    addr = cur["address"].lower()
    ent = byaddr.get(addr)
    if ent is None:
        print(name, "no snapshot entry, skipped")
        continue
    key, e = ent
    cur_views = dict(cur.get("views") or {})
    prev_views = (r0001.get(name) or {}).get("views") or {}
    vrf = VERIFIED.get(name, {})
    for f, val in vrf.items():
        if val != "REVERT":
            cur_views[f] = val
    ps, ns = supply_of(prev_views), supply_of(cur_views)
    # Zephyra/Pengu: 00:01 read was None (revert verdict then); fall back to last
    # stored snapshot supply as the previous baseline and flag it.
    baseline_note = "reread 0001"
    if ps is None and name in ("Zephyra", "Pengu"):
        ps = supply_of(e)
        baseline_note = "snapshot stored (00:01 read None/revert)"
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
    e["lastReadWib"] = "2026-11-17 ~00:31 WIB"
    free = e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap = (e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else
           (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX")))
    pct = (round(100 * free / cap, 1) if isinstance(free, int) and isinstance(cap, int) and cap else None)
    if pct is not None:
        e["freePctVerified"] = pct
    vel_summary[name] = (minted, None if rate is None else round(rate, 3),
                         None if ratio is None else round(ratio, 2), vel, pct)
    if name == "binanceai-mint":
        note = (f"Run 0031: launched={cur_views.get('launched')}, failed={cur_views.get('failed')}, "
                f"isRefundPhase={cur_views.get('isRefundPhase')}, totalShares={cur_views.get('totalShares')}, "
                f"tokenClaimed(user)={cur_views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM.")
    elif name == "RigForge":
        note = (f"Run 0031: freeSharesLeft={cur_views.get('freeSharesLeft')}, openedAt={cur_views.get('openedAt')}, "
                f"freeClaimed={cur_views.get('freeClaimed')}, freeBooked(user)={cur_views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM.")
    elif name in VERIFIED:
        note = (f"Run 0031 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0001, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; "
                f"verifikasi single-call 3 endpoint: {vrf} (REVERT = view revert di 3 endpoint, nilai lama dipertahankan). DIAM.")
    elif pct is not None:
        note = (f"Run 0031 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0001): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note = (f"Run 0031 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0001): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote0031_1117"] = note

print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k, v in vel_summary.items():
    print(" ", k, v)

# PXIO: no snapshot entry; velocity from reread files only.
px_prev = supply_of((r0001.get("PXIO") or {}).get("views") or {})
px_cur = supply_of((r0031.get("PXIO") or {}).get("views") or {})
px_minted = (px_cur - px_prev) if isinstance(px_cur, int) and isinstance(px_prev, int) else None
px_rate = (px_minted / INTERVAL_MIN) if px_minted is not None else None
px_prev_rate = 796 / 26.82  # run 0001 corrected rate (fix script)
px_ratio = (px_rate / px_prev_rate) if px_rate is not None else None
px_vel = bool(px_minted is not None and px_minted >= 20 and px_ratio is not None and px_ratio >= 1.5)
print("PXIO:", px_prev, "->", px_cur, "minted", px_minted, "rate",
      None if px_rate is None else round(px_rate, 2), "ratio",
      None if px_ratio is None else round(px_ratio, 2), "vel", px_vel)

# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc:
    pc["lastReadWib"] = "2026-11-17 ~00:31 WIB"
    pc["runNote0031"] = (f"Run 0031: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                         f"tokenClaimed(user)=0 (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM.")
# track_c RigForge + DogeRageFi
tc = snap.setdefault("track_c", {})
rf = tc.get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = 636
    rf["openedAt"] = 0
    rf["freeClaimed"] = 364
    rf["lastReadWib"] = "2026-11-17 ~00:31 WIB"
    rf["runNote0031_1117"] = f"Run 0031: freeSharesLeft=636, openedAt=0, freeClaimed=364 (blok {BLOCK}). Belum buka. DIAM."
dr = tc.get("DogeRageFi")
if isinstance(dr, dict):
    dr["totalMinted"] = 229
    dr["freeSupply"] = 432
    dr["maxSupply"] = 666
    dr["mintOpen"] = 1
    dr["lastReadWib"] = "2026-11-17 ~00:31 WIB"
    dr["runNote0031_1117"] = f"Run 0031: totalMinted=229, freeSupply=432/666, mintOpen=1, bal_user=0 (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."

snap["last_run_wib"] = "2026-11-17 ~00:31 WIB"
snap["last_run"] = "2026-11-17 ~00:31 WIB"
snap["runNote0031_1117"] = (
    f"Run 0031 (00:31 WIB): re-read 47/47 OK (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0001). "
    f"Velocity LOLOS: tidak ada. PXIO +{px_minted} ({None if px_rate is None else round(px_rate, 1)}/mnt, "
    f"{None if px_ratio is None else round(px_ratio, 2)}x vs prev 29,7) - velocity GAGAL, tetap EARLY lead (free% + umur UNVERIFIED). "
    "Gerakan lain maks Punch Card +5, RAVE +3, SPARKS/BoldLeonidas/MORFO +2 - semua velocity GAGAL. "
    "Threshold >70%: tidak ada yang tembus (AGCLUB 57,9%, Matrix 56,6%, Ledgera 53,8%, RaceAgents 63,0%; AgentBubble 74,3% dari MAX tapi free-cap + umur unverified). "
    "Zephyra/Pengu/Kryntar kini TERBACA di 3 endpoint (00:01 'REVERT' terbantahkan: Zephyra totalMinted 961, Pengu 138/138, Kryntar 1318 + 793/111 + mintOpen 1); "
    "Zero tetap REVERT di 3 endpoint. Vezlune/Poffzi tetap sold-out-free. binanceai tetap refund. RigForge belum buka; PEPE tidak berubah. "
    "Ankr pre-flight GAGAL HTTP 401 (lagi) -> scan FAST-FAIL, watermark TETAP 132512564. Sourcify 2 baru, 0 sale-shape "
    "(0x3B88 vault-mint tanpa agent/free, 0xCC3E vault tanpa mint). Boltbook 0 baru. Sweep EN+ZH + Odaily: hanya proyek lama "
    "(Agentic Gangster 9 Nov, Dragon Agents free habis, JINCHAN window tutup 10 Nov, Saturnagent sold out) - 0 baru. Bridge 116 kontrak, 0 di luar snapshot. DIAM (tanpa laporan chat)."
)
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
