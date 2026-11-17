#!/usr/bin/env python3
"""Merge run 0231 (2026-11-17 02:31 WIB) reads into onchain-snapshot.json.
Baseline: run 0201 reread block 133980222. Head now 133984444.
Interval = (133984444-133980222)*0.45/60 = 31.67 min. Read-only on chain;
writes snapshot only. Also adds DRAGON (0xfc19) + XCOPY (0x3fbe) as EARLY
leads (verified Sourcify ABI + exact registry + fresh reads, 3 endpoints)
and bsccat (0x9dd4) to track_c as watchlist-only (hot-leg 0214)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
r0201 = json.load(open(BASE + "run-2026-11-17-0201-reread.json"))["reads"]
r0231 = json.load(open(BASE + "run-2026-11-17-0231-reread.json"))["reads"]
BLOCK = 133984444
PREV_BLOCK = 133980222
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
    "Kryntar": {"totalMinted": 1350, "standardRemaining": 761,
                "legendaryRemaining": 111, "mintOpen": 1},
    "Zero": {"totalSupply": "REVERT", "freeClaimed": "REVERT"},
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
for name, cur in r0231.items():
    addr = cur["address"].lower()
    ent = byaddr.get(addr)
    if ent is None:
        print(name, "no snapshot entry, skipped")
        continue
    key, e = ent
    cur_views = dict(cur.get("views") or {})
    prev_views = (r0201.get(name) or {}).get("views") or {}
    vrf = VERIFIED.get(name, {})
    for f, val in vrf.items():
        if val != "REVERT":
            cur_views[f] = val
    ps, ns = supply_of(prev_views), supply_of(cur_views)
    baseline_note = "reread 0201"
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
    e["lastReadWib"] = "2026-11-17 ~02:31 WIB"
    free = e.get("freeMinted") if e.get("freeMinted") is not None else e.get("freeClaimed")
    cap = (e.get("FREE_SUPPLY") if e.get("FREE_SUPPLY") is not None else
           (e.get("FREE_CAP") if e.get("FREE_CAP") is not None else e.get("FREE_MAX")))
    pct = (round(100 * free / cap, 1) if isinstance(free, int) and isinstance(cap, int) and cap else None)
    if pct is not None:
        e["freePctVerified"] = pct
    vel_summary[name] = (minted, None if rate is None else round(rate, 3),
                         None if ratio is None else round(ratio, 2), vel, pct)
    if name == "binanceai-mint":
        note = (f"Run 0231: launched={cur_views.get('launched')}, failed={cur_views.get('failed')}, "
                f"isRefundPhase={cur_views.get('isRefundPhase')}, totalShares={cur_views.get('totalShares')}, "
                f"tokenClaimed(user)={cur_views.get('tokenClaimed_user')} (blok {BLOCK}) - tetap fase refund, klaim BELUM terbuka. DIAM.")
    elif name == "RigForge":
        note = (f"Run 0231: freeSharesLeft={cur_views.get('freeSharesLeft')}, openedAt={cur_views.get('openedAt')}, "
                f"freeClaimed={cur_views.get('freeClaimed')}, freeBooked(user)={cur_views.get('freeBooked_user')} (blok {BLOCK}). Belum buka. DIAM.")
    elif name in VERIFIED:
        note = (f"Run 0231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0201, baseline {baseline_note}): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; "
                f"verifikasi single-call 3 endpoint: {vrf} (REVERT = view revert di 3 endpoint, nilai lama dipertahankan). DIAM.")
    elif pct is not None:
        note = (f"Run 0231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0201): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free={free}/{cap} ({pct}%)")
    else:
        note = (f"Run 0231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0201): supply {ps}->{ns} (+{minted}), "
                f"rate {None if rate is None else round(rate, 3)}/mnt vs prev {prev_rate} = {None if ratio is None else round(ratio, 2)}x, velocity {'LOLOS' if vel else 'GAGAL'}; free% UNVERIFIED")
    e["runNote0231_1117"] = note

print("interval_min:", INTERVAL_MIN)
print("velocity summary:")
for k, v in vel_summary.items():
    print(" ", k, v)

# PXIO: no snapshot entry; velocity from reread files only.
px_prev = supply_of((r0201.get("PXIO") or {}).get("views") or {})
px_cur = supply_of((r0231.get("PXIO") or {}).get("views") or {})
px_minted = (px_cur - px_prev) if isinstance(px_cur, int) and isinstance(px_prev, int) else None
px_rate = (px_minted / INTERVAL_MIN) if px_minted is not None else None
px_prev_rate = 176 / 29.55  # run 0201 rate (+176 in 29.55 min = 5.96/mnt)
px_ratio = (px_rate / px_prev_rate) if px_rate is not None else None
px_vel = bool(px_minted is not None and px_minted >= 20 and px_ratio is not None and px_ratio >= 1.5)
print("PXIO:", px_prev, "->", px_cur, "minted", px_minted, "rate",
      None if px_rate is None else round(px_rate, 2), "ratio",
      None if px_ratio is None else round(px_ratio, 2), "vel", px_vel)

# ---- New EARLY leads (verified this run, 3 endpoints) ----
verify = json.load(open(BASE + "run-2026-11-17-0231-verify-new.json"))
vreads = json.load(open(BASE + "run-2026-11-17-0231-verify-reads.json"))
snap["contracts"]["DRAGON"] = {
    "address": "0xfc191b76041498b14dcae3c802af3389c74263e6",
    "name": "DRAGON", "symbol": "DRAGON", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-17-0231",
    "totalMinted": 227, "freeMinted": 227, "FREE_SUPPLY": 1000, "MAX_SUPPLY": 4000,
    "freeRemaining": 773, "paidMinted": 0, "mintEnded": 0,
    "mintStart": 1794833890, "mintEnd": 1794963490,
    "launchTimeWib": "2026-11-16 19:58:10 WIB (mintStart on-chain)",
    "ageVerified": True, "ageHoursAtReport": 6.9,
    "freePctVerified": 22.7,
    "userSlotOpen": True,
    "hasClaimedFree_user": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x9cbbb6f70bb1bea76234690f1226be022d9182a4",
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (AGENT_ID_REGISTRY exact, 3 endpoint)",
    "sourcifyVerifiedAt": "2026-11-16T12:58:48Z",
    "xVerified": True,
    "xEvidence": "Boltbook FIND-31 (thecellyouknow.ai) + lloyd.ai 'Two Dragons, two contracts' + ferrr.ai recheck 02:35 WIB (222/1000)",
    "websiteVerified": False,
    "websiteNote": "No site found this run; gate methods not yet run (early lead needs no gate). Two Dragons exist per Boltbook; live one is 0xfc19.",
    "velocityVerified": False,
    "previousTotalSupply": 227, "mintedInInterval": None, "intervalMinutes": None,
    "previousRatePerMin": None, "currentRatePerMin": None, "velocityRatio": None,
    "velocityLegPasses": False,
    "firstSeenBlock": 133985423, "lastReadBlock": 133985423,
    "lastReadWib": "2026-11-17 ~02:31 WIB",
    "baselineNote": ("EARLY lead reported once run 0231: agent-shaped (Sourcify exact_match, AGENT_ID_REGISTRY exact, "
                     "freeMint()+freeMinted+FREE_SUPPLY), first mints verified on-chain 3 endpoint (227/1000 free, 22.7%), "
                     "age VERIFIED <24h (mintStart 2026-11-16 19:58:10 WIB), slot user open, X discussion verified, website UNVERIFIED. "
                     "Bukan kandidat (free% 22.7% <50%), bukan strong lead (<70%). Velocity baseline: first read run ini."),
    "runNote0231_1117": ("Run 0231: EARLY lead (baru). totalMinted/freeMinted 227/1000 (22.7%), freeRemaining 773, "
                         "mintStart 2026-11-16 19:58:10 WIB (umur ~6.9 jam, VERIFIED), slot user open, velocity baseline (belum ada rate sebelumnya)."),
}
snap["contracts"]["XCOPY"] = {
    "address": "0x3fbec44c7c845374267b06033940abe45c63edfa",
    "name": "XCOPY", "symbol": "XCOPY", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-17-0231",
    "totalSupply": 308, "totalMinted": 308, "MAX_SUPPLY": 1100,
    "mintOpen": 1, "remaining": 792, "balanceOf_user": 0,
    "freePctVerified": None,
    "freePctNote": "No free counter in ABI (no freeMinted/freeClaimed view); total 308/1100 = 28% is NOT free%. mintPriceFor(user) null (signature unclear) - user free slot UNVERIFIED.",
    "userSlotOpen": None,
    "owner": "0xcf26eb7895dc9b2cc0eeac76aa748d80b485799",
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (AGENT_REGISTRY exact, 3 endpoint)",
    "sourcifyVerifiedAt": "2026-11-16T16:25:15Z",
    "xVerified": True,
    "xEvidence": "Boltbook FIND-31 (thecellyouknow.ai) + degennft.ai recheck (304/1100, +1/30 mnt)",
    "websiteVerified": False,
    "websiteNote": ("contractURI claims Website https://xcopy.art + X https://x.com/XCOPYART, BUT live xcopy.art (200, 676.833 byte, dicek run ini) "
                    "TIDAK mencetak kontrak 0x3fbe... (0 hit) -> BUKAN website evidence (metode H). Kemungkinan impersonasi nama XCOPY; gate website GAGAL sampai ada situs yang mencetak kontrak."),
    "ageVerified": False,
    "ageNote": "No mintStart in ABI; Sourcify verifiedAt 2026-11-16T16:25:15Z is NOT launch time; first Boltbook mention ~02:28 WIB 17 Nov. Usia peluncuran UNVERIFIED.",
    "velocityVerified": False,
    "previousTotalSupply": 308, "mintedInInterval": None, "intervalMinutes": None,
    "previousRatePerMin": None, "currentRatePerMin": None, "velocityRatio": None,
    "velocityLegPasses": False,
    "firstSeenBlock": 133985423, "lastReadBlock": 133985423,
    "lastReadWib": "2026-11-17 ~02:31 WIB",
    "baselineNote": ("EARLY lead reported once run 0231: agent-shaped (Sourcify exact_match, AGENT_REGISTRY exact), first mints verified "
                     "on-chain 3 endpoint (308/1100 total, pace merayap +1/30 mnt per Boltbook), free% UNVERIFIED, umur UNVERIFIED, "
                     "slot user UNVERIFIED, website UNVERIFIED (xcopy.art tidak mencetak kontrak). Bukan kandidat/strong lead."),
    "runNote0231_1117": ("Run 0231: EARLY lead (baru). totalSupply/totalMinted 308/1100 (28% total, BUKAN free%), mintOpen 1, remaining 792, "
                         "velocity baseline (belum ada rate sebelumnya)."),
}

# ---- bsccat to track_c as watchlist-only (hot-leg 0214 assessment) ----
tc = snap.setdefault("track_c", {})
tc["bsccat"] = {
    "sale": "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
    "name": "bsccat / $BSC",
    "status": "watchlist-only-age-unverified",
    "source": "hot-leg 0214 (bsccat.com), picked up by main run 0231",
    "website": "https://bsccat.com",
    "websiteGate": "PASS per hot-leg 0214 (live read 02:17 WIB prints exact mint contract twice + registry)",
    "site_claims": ("18,000 shares incl 800 free; 1 free/Agent ID; 1 share = 1,000,000 $BSC; paid 0.001 BNB/share; "
                    "pool opens at 7,000 net paid shares or sellout; token non-transferable before pool; 2.5% tax after pool"),
    "freeMinted": 389, "totalSupply": 389,
    "caveats": ("Source UNVERIFIED per site; registry mismatch site 0x60B9...022F vs post 0x31f9...; pool NOT open yet; "
                "free pool number unverified; user slot unverified; age likely <24h but unbounded "
                "(first mint in checked window 23:32 WIB 16 Nov; earlier mints not excluded)"),
    "lastReadWib": "2026-11-17 ~02:31 WIB",
    "runNote0231_1117": ("Run 0231: ditambahkan ke track_c sebagai watchlist-only (bukan lead): website gate PASS tapi shape inferred "
                         "bukan ABI-verified, free pool + slot user unverified, umur unverified. TIDAK di-preview/mint, TIDAK dilaporkan sebagai lead."),
}

# pending claim binanceai.fun
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc:
    pc["lastReadWib"] = "2026-11-17 ~02:31 WIB"
    pc["runNote0231"] = (f"Run 0231: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                         f"tokenClaimed(user)=0 (blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM.")
# track_c RigForge + DogeRageFi
rf = tc.get("RigForge")
if isinstance(rf, dict):
    rf["freeSharesLeft"] = 636
    rf["openedAt"] = 0
    rf["freeClaimed"] = 364
    rf["lastReadWib"] = "2026-11-17 ~02:31 WIB"
    rf["runNote0231_1117"] = f"Run 0231: freeSharesLeft=636, openedAt=0, freeClaimed=364 (blok {BLOCK}). Belum buka. DIAM."
dr = tc.get("DogeRageFi")
if isinstance(dr, dict):
    dr["totalMinted"] = 229
    dr["freeSupply"] = 432
    dr["maxSupply"] = 666
    dr["mintOpen"] = 1
    dr["lastReadWib"] = "2026-11-17 ~02:31 WIB"
    dr["runNote0231_1117"] = f"Run 0231: totalMinted=229, freeSupply=432/666, mintOpen=1, bal_user=0 (blok {BLOCK}). Watchlist-only-age-unverified. DIAM."

snap["last_run_wib"] = "2026-11-17 ~02:31 WIB"
snap["last_run"] = "2026-11-17 ~02:31 WIB"
snap["runNote0231_1117"] = (
    f"Run 0231 (02:31 WIB): re-read 47/47 OK (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 0201). "
    f"Velocity LOLOS: tidak ada. PXIO +{px_minted} ({None if px_rate is None else round(px_rate, 2)}/mnt, "
    f"{None if px_ratio is None else round(px_ratio, 2)}x vs prev 5,96) - velocity GAGAL, tetap EARLY lead (free% + umur UNVERIFIED). "
    "Gerakan lain: ALIEN +3, Punch Card +4, AgentBubble +1 (1653), AGCLUB +1 (515/888 = 58,0%), RAVE +1, MORFO +1, LumenFindings +3 spesimen - semua velocity GAGAL. "
    "Threshold >70%: tidak ada yang tembus (AGCLUB 58,0%, Matrix 569 flat, Ledgera 2691/5000 = 53,8%, RaceAgents 631/1000 = 63,1%; AgentBubble 1653/2222 = 74,4% dari MAX tapi free-cap + umur unverified). "
    "Zephyra/Pengu/Kryntar flat (961, 138/138, 1350 + 761/111 + mintOpen 1); Zero tetap REVERT. Vezlune/Poffzi tetap sold-out-free. binanceai tetap refund. RigForge belum buka; PEPE tidak berubah (freeMinted 500/500). "
    "BARU: 2 EARLY lead dilaporkan sekali - DRAGON 0xfc19 (free 227/1000 = 22,7%, umur VERIFIED ~6,9 jam via mintStart 2026-11-16 19:58:10 WIB, slot user open, X verified, website unverified) "
    "dan XCOPY 0x3fbe (308/1100 total, free% + umur + slot user UNVERIFIED, website unverified - xcopy.art tidak mencetak kontrak). "
    "bsccat 0x9dd4 masuk track_c watchlist-only (bukan lead). ECHO/MIRAGE/WOOF (FIND-31): alamat lengkap tidak ada di post -> tidak bisa diverifikasi, dicatat unverified, TIDAK dilaporkan. "
    "Ankr pre-flight GAGAL HTTP 401 (ke-10 berturut-turut) -> scan FAST-FAIL, watermark TETAP 132512564; 5c dilewati (tanpa output scan). Sourcify 3 baru, 0 sale-shape. "
    "Boltbook 0x9383... = hash transaksi (false positive regex), bukan kontrak. Sweep EN+ZH + Odaily: hanya proyek lama (Agentic Gangster 9 Nov, AGENT COSMOS 5 Nov, Orzo 4 Nov, Saturnagent sold out 2000/2000, RIGBYPASS 10 Nov, First-Dollar Grove 8 Nov) - 0 baru. Bridge 116 kontrak, 0 di luar snapshot. "
    "Hot-leg: tidak ada file run baru sesudah 0214 (0219/0224/0229 hilang) - cron hot-leg kemungkinan macet, dicatat untuk dicek."
)

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
