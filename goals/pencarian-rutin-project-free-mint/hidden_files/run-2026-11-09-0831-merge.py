#!/usr/bin/env python3
"""Merge run 2026-11-09 0831 WIB into onchain-snapshot.json.
- Re-read values for all snapshot contracts + track_c (block 132498816).
- Velocity: rate 0731->0831 vs rate 0631->0731 computed from the three
  reread JSONs (intervals 58.4 vs 65.3 block-minutes). NOTE: stored
  previousRatePerMin in the snapshot is NOT used -- the 0731 merge's
  previousTotalSupply-based previous rate was 0 for most contracts
  (quirk: previousTotalSupply was set to the new supply each run).
  Using the three reread JSONs reproduces the reread summary verdicts.
- New entries: 10 mature scan contracts (NOT early leads), PokeChain
  (sold out, user holds 1), Sidecoo Season (upcoming, paid ticket).
- Appends scan first-seen contracts to onchain-scan-seen.json.
  5c-checked already updated by the scan leg (1800 keys); verified here.
  Does NOT touch the scan watermark.
"""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
B6, B7, B8 = 132482323, 132491029, 132498816
MIN_67 = (B7 - B6) * 0.45 / 60   # 65.3
MIN_78 = (B8 - B7) * 0.45 / 60   # 58.4

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-run-2026-11-09-0831")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r8 = json.load(open(f"{HF}/run-2026-11-09-0831-reread.json"))
r7 = json.load(open(f"{HF}/run-2026-11-09-0731-reread.json"))
r6 = json.load(open(f"{HF}/run-2026-11-09-0631-reread.json"))
tri = json.load(open(f"{HF}/run-2026-11-09-0831-triage.json"))
prew = json.load(open(f"{HF}/run-2026-11-09-0831-prewindow.json"))

def sup(d):
    if not isinstance(d, dict): return None
    v = d.get("totalSupply")
    return v if v is not None else d.get("totalMinted")

rr8, rr7, rr6 = r8["reread"], r7["reread"], r6["reread"]
contracts = snap["contracts"]
vel_pass, vel_near, sellout, slot_ch = [], [], [], []
n_updated = 0
for name, d8 in rr8.items():
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    d7 = rr7.get(name); d6 = rr6.get(name)
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if d8.get(k) is not None:
            old[k] = d8[k]
    old["lastReadBlock"] = B8
    old["lastReadWib"] = "2026-11-09 09:0x WIB"
    s8, s7, s6 = sup(d8), sup(d7) if d7 else None, sup(d6) if d6 else None
    minted = (s8 - s7) if (s8 is not None and s7 is not None) else None
    if minted is not None:
        old["mintedInInterval"] = minted
    if s8 is not None and s7 is not None and s6 is not None:
        m_cur = s8 - s7
        m_prev = s7 - s6
        rate_cur = m_cur / MIN_78
        rate_prev = m_prev / MIN_67
        ratio = (rate_cur / rate_prev) if rate_prev > 0 else None
        old["previousTotalSupply"] = s8
        old["previousRatePerMin"] = rate_prev
        old["currentRatePerMin"] = rate_cur
        old["intervalMinutes"] = round(MIN_78, 1)
        old["velocityRatio"] = ratio
        passes = ratio is not None and ratio >= 1.5 and m_cur >= 20
        old["velocityLegPasses"] = passes
        old["velocityNote"] = (f"run 0831: {s7}->{s8} (+{m_cur}, {rate_cur:.3f}/mnt vs prev {rate_prev:.3f} = {ratio:.2f}x)"
                               if ratio is not None else
                               f"run 0831: {s7}->{s8} (+{m_cur}, {rate_cur:.3f}/mnt, prev rate 0)")
        if passes:
            vel_pass.append(name)
        elif m_cur >= 20:
            vel_near.append((name, m_cur, round(rate_cur, 3), round(rate_prev, 3), round(ratio, 2) if ratio else None))
    fc = d8.get("freeClaimed"); fs = old.get("FREE_SUPPLY") or d8.get("FREE_SUPPLY")
    fmint = d8.get("freeMinted"); fcap = old.get("FREE_CAP") or d8.get("FREE_CAP")
    old_fc = old.get("freeClaimed"); old_fm = old.get("freeMinted")
    if fc is not None and fs and fc >= fs and not (old_fc is not None and old_fc >= fs):
        sellout.append((name, "freeClaimed", fc, fs))
    if fmint is not None and fcap and fmint >= fcap and not (old_fm is not None and old_fm >= fcap):
        sellout.append((name, "freeMinted", fmint, fcap))
    ob, nb = old.get("balanceOf_user"), d8.get("balanceOf_user")
    if ob is not None and nb is not None and ob != nb:
        slot_ch.append((name, ob, nb))
    old["runNote0831_1109"] = (
        f"Run 0831 (blok {B8}): totalSupply {s8} (prev {s7}), minted interval {minted}, "
        f"velocity {'LOLOS' if old.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')} freeMinted={old.get('freeMinted')}/{old.get('FREE_CAP')}; "
        f"bal_user={d8.get('balanceOf_user')}; status {old.get('status')}."
    )
    n_updated += 1

# track_c updates
tc = snap.get("track_c", {})
n_tc = 0
for k, v in r8.get("track_c", {}).items():
    if not isinstance(v, dict):
        continue
    ent = tc.get(k)
    if not isinstance(ent, dict):
        continue
    for kk in ("totalSupply", "freeMinted", "freeClaimed"):
        if v.get(kk) is not None:
            ent[kk] = v[kk]
    ent["runNote0831_1109"] = f"Run 0831 (blok {B8}): totalSupply {v.get('totalSupply')}, freeMinted {v.get('freeMinted')}."
    n_tc += 1

def base_entry(name, addr, status, **kw):
    e = {"address": addr, "status": status, "name": name, "lastReadBlock": B8,
         "lastReadWib": "2026-11-09 09:0x WIB"}
    e.update(kw)
    return e

# 10 mature scan contracts (NOT early leads: pre-window mints prove launches predate the window)
tri_by_addr = {x["address"].lower(): x for x in tri["first_seen_triage"]}
sc = json.load(open(f"{HF}/run-2026-11-09-0831-scan.json"))
raw_by_addr = {c["address"].lower(): c for c in sc.get("contracts_raw", [])}
MAT = {
 "0x5c043926": ("0x5c04392641c81F1b69826E13d8f3F78c58464970", "Sourcify exact_match; FREE_PER_WALLET/FREE_SUPPLY/freeClaimed/freeMinted/freeOpen/freeRemaining + mint/quoteMint; owner 0x75d251ba... (not in discards); 20 pre-window mints, first block 132401588"),
 "0x9fd3e0a3": ("0x9fd3e0a352269820717B373E140D3709Dc279851", "registry-bytes True, Sourcify unverified; no free/mint funcs readable; owner 0x590e271c... (not in discards); 1 pre-window mint (block 132497759) BUT totalSupply 411 >> 4 recent mints -> bulk minted before 132400000; name/symbol unreadable"),
 "0x253a002E": ("0x253a002E4D03F1b49C4739f2165dfA00F17feE25", "registry-bytes True, Sourcify unverified; owner() None (unreadable); 0 pre-window mints BUT 2 mints in earlier window [132300000,132399999], first block 132305540"),
 "0x74830117": ("0x74830117F86af8a8D39e56B2bcD4D34B30D7B027", "registry-bytes True, Sourcify unverified; owner 0x86daea87... (not in discards); 18 pre-window mints, first block 132495131"),
 "0xf4dC5600": ("0xf4dC5600D2546E1e52b8cA81169D3Cec53264b68", "Sourcify exact_match; mint/agentMintCount/mintedByAgent (no free views); owner 0x1a2e1239... (not in discards); 58 pre-window mints, first block 132402538"),
 "0x18042D2E": ("0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5", "S1 (mint+quote+free views+agent), exact_match; FREE_CAP/canFreeMint/claimedFree/freeMint/freeMinted; owner 0x4e9b1d07... (not in discards); 3 pre-window mints, first block 132469340"),
 "0x4AB41152": ("0x4AB41152EdB3E2853b19828e51927db36508cd64", "registry-bytes True, Sourcify unverified; owner 0x36f3d56e... (not in discards); 192 pre-window mints, first block 132424300"),
 "0x99dE10fc": ("0x99dE10fc70EbEEc6C32e108f48793459628b41a5", "Sourcify exact_match; FREE_PER_WALLET/FREE_SUPPLY/freeMinted/freeOpen/freeRemaining + mint; owner 0x75d251ba... (not in discards); 11 pre-window mints, first block 132465407"),
 "0x1B72ceC5": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", "registry-bytes True, Sourcify JSONDecodeError (unverified); owner 0x4e9b1d07... (not in discards); 6 pre-window mints, first block 132426646"),
 "0x02f10432": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", "registry-bytes True, Sourcify JSONDecodeError (unverified); owner 0x4e9b1d07... (not in discards); 4 pre-window mints, first block 132437413"),
}
for short, (addr, note) in MAT.items():
    t = tri_by_addr.get(addr.lower(), {})
    raw = raw_by_addr.get(addr.lower(), {})
    pw = prew.get(addr, {})
    contracts[short] = base_entry(
        short, addr, "watchlist-only-mature-newly-noticed-2026-11-09",
        kind="ERC721",
        totalSupply=pw.get("totalSupply"),
        firstSeenBlock=t.get("first_block") or raw.get("first_block"),
        scanMintCount=raw.get("mint_count"),
        scanMinters=raw.get("distinct_minters"),
        owner=t.get("owner"),
        ownerNote="Owner NOT in same-owner-discards.json (checked run 0831).",
        launchNote="Age UNVERIFIED: first mint predates the scan window (pre-window mints in [132400000, 132497913] or large totalSupply with earlier mints => launched before ~132400000). NOT a window launch; do NOT report as early lead.",
        preWindowMints=pw.get("pre_window_mints"),
        preWindowFirstBlock=pw.get("first_pre_block"),
        baselineNote=f"Scan first-seen run 0831 but MATURE (not a new launch). {note}. First-seen in this window is a seen-file gap artifact, not a launch. Watchlist-only; age/free% still unverified for tiers.",
        xVerified=False, velocityVerified=False,
        runNote0831_1109=f"Run 0831: added as mature newly-noticed (NOT early lead); pre-window mints {pw.get('pre_window_mints')}, first pre-window block {pw.get('first_pre_block')}.",
    )

# PokeChain (Boltbook discovery; sold out, user already holds 1)
contracts["PokeChain"] = base_entry(
    "PokeChain", "0x4EF929aF00cB93993c3D01834C4DA79200d31e32", "sold-out-free-2026-11-09",
    kind="ERC721", totalSupply=None, totalMinted=15555, MAX_SUPPLY=15555,
    userBalance=1,
    firstSeenBlock=132500178,
    launchNote="Sold out at discovery (15,555/15,555 totalMinted, block 132500178). Launch time not established; sold-out status makes age moot.",
    website="https://pokechain.trade",
    websiteEvidence="Method I: contractURI() decoded run 0831 names Website https://pokechain.trade + X https://x.com/PokeChainTrade; moot (sold out).",
    xVerified=False, velocityVerified=False,
    baselineNote="Boltbook discovery run 0831. SOLD OUT on first sight (15,555/15,555); user already holds 1 (balanceOf(user)=1). No free pool left; not a lead, not a candidate. Recorded for holdings accuracy only.",
    runNote0831_1109="Run 0831: discovered via Boltbook; totalMinted 15555/15555 SOLD OUT; balanceOf(user)=1; not a lead.",
)

# Sidecoo Season (Boltbook discovery; not launched, PAID ticket)
contracts["Sidecoo Season"] = base_entry(
    "Sidecoo Season", "0xce0242533E92D9AF4fb273049B6ce799da960fcC", "watchlist-only-upcoming-paid-2026-11-09",
    kind="ERC721", totalSupply=0,
    userBalance=0,
    launchNote="Not launched at discovery: totalSupply 0 at 08:42 WIB read run 0831; opens 2026-11-09 13:00 WIB per Boltbook post.",
    baselineNote="Boltbook discovery run 0831. NOT a free-mint lead: ticket 0.0036 BNB for 2 points per NFT (max 10) = PAID. Upcoming watchlist-only; never a free candidate unless a free lane is verified later. Distinct contract from snapshot Sidecoo 0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8.",
    xVerified=False, velocityVerified=False,
    runNote0831_1109="Run 0831: totalSupply 0, opens 2026-11-09 13:00 WIB, PAID ticket 0.0036 BNB; upcoming watchlist-only.",
)

# GLOOP re-confirmation (Boltbook: CLOSED 3333/3333 this morning) - already sold-out in snapshot; note only
if "GLOOP" in contracts:
    contracts["GLOOP"]["runNote0831_1109"] = "Run 0831: Boltbook confirms CLOSED 3333/3333 this morning; status already sold-out."

# top-level run notes
snap["timestamp_wib"] = "2026-11-09 09:0x WIB"
snap["last_run_wib"] = "2026-11-09 09:0x WIB"
snap["runNote0831"] = (
    f"Run 0831: re-read {n_updated}/576 contracts + {n_tc}/76 track_c at block {B8} (reread 624.8s, exit 0). "
    f"Velocity LOLOS (0731->0831 vs 0631->0731): {vel_pass}. Near (>=20, fail): {vel_near}. "
    f"New free-pool sellouts: {sellout}. Slot changes: {slot_ch}. "
    "Scan window 132497914-132498913 (1000 blocks, 40 Ankr calls, 0 chunk errors); "
    "111 NFT + 308 ERC20-mint; 22 first-seen triaged, 0 new early leads (all 10 non-discarded agent-shaped first-seen proved mature via pre-window mints; 6 same-owner-discarded never promoted); "
    "track-C 5c: 65 candidates, 12 new checked, 0 S1/S2. "
    "Discovery: 0 new candidates/leads; PokeChain sold out (user holds 1); Sidecoo Season upcoming + paid; PPL/Fountain/GLOOP/Gugu closed. "
    "Binanceai claim: still refund/failed phase, no change."
)
snap["runNote0831_scan"] = (
    "Scan run 0831: pre-flight OK 5.6s (1000 logs/50 blocks). Window 132497914-132498913 (latest 1000, cap 1000). "
    "Gap to backfill watermark not scanned by this job (backfill owns watermark; backfill DISABLED by user). "
    "No chunk errors this run. Enrich still running at merge time (partial=true, ~17/111); contracts_raw + ERC20 list complete, triage unaffected."
)
snap["runNote0831_velocity"] = f"Velocity passes run 0831: {vel_pass} (all blocked: ETHBack x2 + Zhenzhu token-scale, not NFT mints; Glitchronin same-owner-discarded; MONOLITH free% unverified + gate unverified)."
snap["runNote0831_binanceai"] = (
    "Run 0831: binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance=0. "
    "IDENTICAL to snapshot (verified 2026-11-08 14:05 WIB). Still closed-refund-phase; no change, no re-report."
)
snap["runNote0831_discovery"] = (
    "Run 0831 discovery: Boltbook EN+ZH fetched 08:44-08:47 WIB. New vs snapshot: Sidecoo Season 0xce024253... (unlaunched, opens 13:00 WIB, PAID 0.0036 BNB ticket) + "
    "PokeChain 0x4EF929aF... (sold out 15555/15555, user holds 1; website pointer via contractURI). Sourcify feed 20 entries (verifiedAt 00:47:18Z-01:42:27Z): 0 new agent-shaped. "
    "Sweep + complements (Square/Odaily/PANews/DappBay): no new leads. Bridge unchanged since 2026-11-08 18:21 UTC; same 8 not-in-snapshot. 0 candidates/leads; silence rule applies."
)

# append newly seen scan contracts to seen file
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
seen_lows = {k.lower() for k in seen}
added = 0
for c in sc.get("contracts_raw", []):
    if c["address"].lower() not in seen_lows:
        seen[c["address"]] = c.get("first_block")
        added += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)

# verify 5c-checked (already updated by scan leg)
checked = json.load(open(f"{HF}/track-c-scan-checked.json"))
missing5c = [x["address"] for x in tri.get("track_c_5c", []) if x["address"].lower() not in {k.lower() for k in checked}]
print(f"5c already in checked file: {len(tri.get('track_c_5c', [])) - len(missing5c)}/{len(tri.get('track_c_5c', []))}; missing={missing5c}")

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: updated={n_updated} track_c={n_tc} vel_pass={vel_pass}")
print(f"vel_near={vel_near}")
print(f"sellout={sellout} slot_changes={slot_ch}")
print(f"seen added={added} (total {len(seen)}); contracts now={len(snap['contracts'])} track_c now={len(snap.get('track_c', {}))}")
