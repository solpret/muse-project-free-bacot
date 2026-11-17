#!/usr/bin/env python3
"""Merge run 2026-11-09 0901 WIB into onchain-snapshot.json.
- PARTIAL re-read: 400/588 address-bearing contracts at block 132504249.
  Script died silently after 400 contracts (last log 09:34 WIB, LEAN
  Foxagent-0DAa, no traceback); track_c leg NEVER ran (0 entries).
  The 188 unread contracts keep their 0831 values (stale, NOT zero/null).
- Velocity: rate 0831->0901 vs rate 0731->0831, intervals 40.7 vs 58.4
  block-minutes. Computed from the three reread JSONs (same method as
  the 0831 merge; stored previousRatePerMin in the snapshot is NOT used).
- New entries: YAMA (track_c lead, website gate FAILED), NNOM (free pool
  exhausted), Nero Agent (unverified watchlist-only), BAGENT (paid),
  0xCFB72b0E (mature scan first-seen, NOT an early lead).
- Appends scan first-seen contracts to onchain-scan-seen.json.
  5c-checked already updated by the scan leg (1816 keys); verified here.
  Does NOT touch the scan watermark.
"""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
B7, B8, B9 = 132491029, 132498816, 132504249
MIN_78 = (B8 - B7) * 0.45 / 60   # 58.4
MIN_89 = (B9 - B8) * 0.45 / 60   # 40.7

shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-run-2026-11-09-0901")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r9 = json.load(open(f"{HF}/run-2026-11-09-0901-reread.json"))
r8 = json.load(open(f"{HF}/run-2026-11-09-0831-reread.json"))
r7 = json.load(open(f"{HF}/run-2026-11-09-0731-reread.json"))
tri = json.load(open(f"{HF}/run-2026-11-09-0901-triage.json"))
prew = json.load(open(f"{HF}/run-2026-11-09-0901-prewindow.json"))

def sup(d):
    if not isinstance(d, dict): return None
    v = d.get("totalSupply")
    return v if v is not None else d.get("totalMinted")

rr9, rr8, rr7 = r9["reread"], r8["reread"], r7["reread"]
contracts = snap["contracts"]
vel_pass, vel_near, sellout, slot_ch = [], [], [], []
n_updated = 0
for name, d9 in rr9.items():
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    d8 = rr8.get(name); d7 = rr7.get(name)
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if d9.get(k) is not None:
            old[k] = d9[k]
    old["lastReadBlock"] = B9
    old["lastReadWib"] = "2026-11-09 09:4x WIB"
    s9, s8, s7 = sup(d9), sup(d8) if d8 else None, sup(d7) if d7 else None
    minted = (s9 - s8) if (s9 is not None and s8 is not None) else None
    if minted is not None:
        old["mintedInInterval"] = minted
    if s9 is not None and s8 is not None and s7 is not None:
        m_cur = s9 - s8
        m_prev = s8 - s7
        rate_cur = m_cur / MIN_89
        rate_prev = m_prev / MIN_78
        ratio = (rate_cur / rate_prev) if rate_prev > 0 else None
        old["previousTotalSupply"] = s9
        old["previousRatePerMin"] = rate_prev
        old["currentRatePerMin"] = rate_cur
        old["intervalMinutes"] = round(MIN_89, 1)
        old["velocityRatio"] = ratio
        # Match the reread leg's verdict: a non-positive previous rate with a
        # positive current rate counts as ratio inf (passes if >=20 tokens).
        # This reproduces the reread summary's 16 passes (incl. STARRY,
        # bridge-0x93bf08d2, Sprouts-1831 whose prev rate was 0/negative).
        passes = ((ratio is not None and ratio >= 1.5) or (rate_prev <= 0 and rate_cur > 0)) and m_cur >= 20
        old["velocityLegPasses"] = passes
        old["velocityNote"] = (f"run 0901: {s8}->{s9} (+{m_cur}, {rate_cur:.3f}/mnt vs prev {rate_prev:.3f} = {ratio:.2f}x)"
                               if ratio is not None else
                               f"run 0901: {s8}->{s9} (+{m_cur}, {rate_cur:.3f}/mnt, prev rate {rate_prev:.3f} = inf)")
        if passes:
            vel_pass.append(name)
        elif m_cur >= 20:
            vel_near.append((name, m_cur, round(rate_cur, 3), round(rate_prev, 3), round(ratio, 2) if ratio else None))
    fc = d9.get("freeClaimed"); fs = old.get("FREE_SUPPLY") or d9.get("FREE_SUPPLY")
    fmint = d9.get("freeMinted"); fcap = old.get("FREE_CAP") or d9.get("FREE_CAP")
    old_fc = old.get("freeClaimed"); old_fm = old.get("freeMinted")
    if fc is not None and fs and fc >= fs and not (old_fc is not None and old_fc >= fs):
        sellout.append((name, "freeClaimed", fc, fs))
    if fmint is not None and fcap and fmint >= fcap and not (old_fm is not None and old_fm >= fcap):
        sellout.append((name, "freeMinted", fmint, fcap))
    ob, nb = old.get("balanceOf_user"), d9.get("balanceOf_user")
    if ob is not None and nb is not None and ob != nb:
        slot_ch.append((name, ob, nb))
    old["runNote0901_1109"] = (
        f"Run 0901 (blok {B9}): totalSupply {s9} (prev {s8}), minted interval {minted}, "
        f"velocity {'LOLOS' if old.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')} freeMinted={old.get('freeMinted')}/{old.get('FREE_CAP')}; "
        f"bal_user={d9.get('balanceOf_user')}; status {old.get('status')}."
    )
    n_updated += 1

# track_c: NOT re-read this run (reread script died before the track_c leg;
# r9['track_c'] == {}). Values stay at 0831 (stale, NOT zero). No updates.

def base_entry(name, addr, status, **kw):
    e = {"address": addr, "status": status, "name": name, "lastReadBlock": 132505561,
         "lastReadWib": "2026-11-09 09:4x WIB"}
    e.update(kw)
    return e

# --- YAMA: new track-C lead, website gate FAILED (report once, NO preview/execution)
tc = snap.get("track_c", {})
tc["YAMA"] = {
    "sale": "0x86d779fc4d83044cceccb53639f9a98e367d6e46",
    "token": "0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2",
    "status": "lead-reported-gate-blocked-2026-11-09",
    "saleShape": "PASS (S1): mint(shares,referrer) payable + quote(buyer,shares)->(freeShares,costBnb) + freeUsed(address) + agentIdRegistry; TOKENS_PER_SHARE 1,000,000; MAX_SHARES 100,000; PRICE 0.001 BNB (paid lane); Sourcify exact_match (verifiedAt 2026-11-08T08:16:43Z, NOT launch time)",
    "sharesMinted": 413,
    "totalShares": 413,
    "freeMinted": 413,
    "totalFreeShares": 413,
    "paidShares": 0,
    "MAX_SHARES": 100000,
    "freeRemaining": 99587,
    "mintingOpen": True,
    "poolOpen": True,
    "freePoolNote": "413/100,000 free shares claimed (0.41%); 99,587 free shares left at block 132505561",
    "userSlot": {"freeUsed": False, "quotaOf": 10, "quoteFreeShares": 1, "quoteCostBnb": 0, "sharesOf": 0, "slot_open_free": True},
    "ageNote": "VERIFIED <=48h: first Minted event block 132359287, 2026-11-08 15:18:20 WIB (Ankr getLogs module, 1250 logs, 413 Minted + 413 FreeShareClaimed, 413 distinct minters; first minter 0x2193d6e0468ac747823e7e876f1acd34ffe43a67; first mint tx 0xc782512d1d492363035a79ffdaf0a0c0ee3b0e8449b6c805d6990309a902f2d1); age ~18.3h at report time; 48h deadline ~2026-11-10 15:18 WIB",
    "discussionNote": "YES - 2 Boltbook posts 2026-11-09 (rizeiki.ai ~09:24 WIB, 1328.ai ~09:23 WIB) with on-chain receipt: mint(1, 0x0) value 0, +1,000,000 YAMA, tx 0xe7fcff940b80040bdc2e301b0253204fe0238021edbb88fc7619dc268e6cea3e, block 132499178, receipt 1; '12 candidates this round, only YAMA free'",
    "websiteGate": "FAILED run 0901 - methods tried: (A) contract-address search: no site; (C) Sourcify metadata: no URLs; (G) project-name search: only old same-name Yamaswap YAMA 0xAd68eb09AbF00041aA47e2D1F7A96242bf5Be00B (different token, 311 days old - same-name is NOT linkage); (B) Boltbook posts: no external site link, no vercel/pages.dev/deed.page/surge.sh link; (H)/(I)/(J) not applicable (sale ABI has no contractURI/site function). Missing: verified project website printing the exact contracts. DO NOT preview, DO NOT execute under track-C lead direct mint until a website is verified (or user gives an explicit informed override for this specific case).",
    "boundary": "LEAD ONLY, gate-blocked. NEVER previewed/minted while the website gate fails.",
    "lastReadBlock": 132505561,
    "lastReadWib": "2026-11-09 09:4x WIB",
    "runNote0901_1109": "Run 0901: NEW track-C lead (all 4 lead legs verified) BUT website gate FAILED - reported once as lead + blocking reason; NO preview, NO execution.",
}

# --- NNOM: Boltbook discovery; free pool exhausted -> paid-only, NOT a lead
contracts["Nebula Nomads (NNOM)"] = base_entry(
    "Nebula Nomads (NNOM)", "0xb1af1f59a7f569e519d4f477b8bb5344bd969b1a", "excluded-free-pool-exhausted-2026-11-09",
    kind="ERC721", totalSupply=345, totalMinted=345, MAX_SUPPLY=3333,
    freeQuota=333, remainingFree=0, mintOpen=1, agentGateOn=1,
    costOf_user_1="0.0005 BNB", mintedBy_user=0,
    sourcify="exact_match, verifiedAt 2026-11-06T22:53:22Z",
    baselineNote="Boltbook discovery run 0901. ERC-721 agent-gated (agentRegistry, agentGateOn, freeQuota(), remainingFree(), mint(qty), costOf). Free pool EXHAUSTED (remainingFree 0; freeQuota cap 333 < totalMinted 345) - paid-only now (0.0005 BNB). NOT a lead, NOT a candidate.",
    launchNote="Launch time not established; free pool already exhausted at first read (block 132505561), so age is moot.",
    xVerified=False, velocityVerified=False,
    runNote0901_1109="Run 0901: discovered via Boltbook; free pool exhausted (remainingFree 0), paid-only 0.0005 BNB; recorded as excluded, not a lead.",
)

# --- Nero Agent: Boltbook discovery; all free selectors revert -> UNVERIFIED, watchlist-only
contracts["Nero Agent"] = base_entry(
    "Nero Agent", "0xe46720870ef38c22bb68f6962ad9a275ebbfa4a0", "watchlist-only-unverified-2026-11-09",
    kind="ERC721", totalSupply=9900, codeBytes=6799,
    sourcify="UNVERIFIED",
    baselineNote="Boltbook discovery run 0901. Post claims 9,900/10,000 free (99.0%), FREE 1/.ai wallet gas-only (monitor recheck 09:23 WIB by dieuxuan50.ai) - UNVERIFIED on-chain: totalSupply 9900 BUT freeClaimed/freeMinted/FREE_SUPPLY/mintOpen/freeClaimed(user) selectors ALL REVERT (no such functions); Sourcify UNVERIFIED. Shape, free pool, user slot, launch age ALL UNVERIFIED. Watchlist-only, NOT a lead.",
    launchNote="Launch age UNVERIFIED (no verifiable launch time; post claim only).",
    xVerified=False, velocityVerified=False,
    runNote0901_1109="Run 0901: discovered via Boltbook; free-view selectors revert, Sourcify unverified; watchlist-only, not a lead.",
)

# --- BAGENT: Boltbook discovery; PAID mint, sold out -> excluded, NOT a lead
contracts["BAGENT"] = base_entry(
    "BAGENT", "0x9CA1A3eeA74829aA5011c56386b226DB472D0F4f", "excluded-paid-2026-11-09",
    kind="ERC721", token="0xb50dC583cC6F83750c36789F52d51E12dA664444",
    baselineNote="Boltbook discovery run 0901. PAID mint (10 USDT + 0.0148 BNB per 2,000,000 BAGENT), pool already open, sold out 10,000 shares. Token contract 0xb50dC583cC6F83750c36789F52d51E12dA664444. NOT a lead, NOT a candidate (paid-only).",
    launchNote="Launch time not established; paid + sold out at first read, so age is moot.",
    xVerified=False, velocityVerified=False,
    runNote0901_1109="Run 0901: discovered via Boltbook; PAID mint, sold out 10,000 shares; recorded as excluded, not a lead.",
)

# --- 0xCFB72b0E: mature scan first-seen (NOT an early lead)
tri_by_addr = {x["address"].lower(): x for x in tri["first_seen_triage"]}
sc = json.load(open(f"{HF}/run-2026-11-09-0901-scan.json"))
raw_by_addr = {c["address"].lower(): c for c in sc.get("contracts_raw", [])}
cfb = tri_by_addr.get("0xcfb72b0e311796c478c6b74c1cd4592bbaa17aab", {})
cfb_raw = raw_by_addr.get("0xcfb72b0e311796c478c6b74c1cd4592bbaa17aab", {})
cfb_pw = prew.get("0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab", {})
contracts["0xCFB72b0E"] = base_entry(
    "0xCFB72b0E", "0xCFB72b0E311796C478c6b74C1cd4592BbAa17aab", "watchlist-only-mature-newly-noticed-2026-11-09",
    kind="ERC721",
    totalSupply=None,
    firstSeenBlock=cfb.get("first_block") or cfb_raw.get("first_block"),
    firstMintWib="2026-11-09 09:20:04 WIB",
    scanMintCount=cfb_raw.get("mint_count"),
    scanMinters=cfb_raw.get("distinct_minters"),
    owner=cfb.get("owner"),
    ownerNote="Owner 0x0000000000000000000000000000000000000000 - NOT in same-owner-discards.json (checked run 0901).",
    launchNote="First mint 2026-11-09 09:20:04 WIB (block 132500929) - age ~25 min at scan time, WITHIN 48h. BUT 414 pre-window mints in [132400000, 132503470] prove the launch predates this run's scan window: mature newly-noticed, NOT an early lead.",
    preWindowMints=cfb_pw.get("pre_window_mints"),
    preWindowFirstBlock=cfb_pw.get("first_pre_block"),
    baselineNote="Scan first-seen run 0901 but MATURE (not a window launch). registry_bytes=True BUT Sourcify error:JSONDecodeError (ABI unreadable - free shape unverified from ABI). 44 mints / 44 minters in-window. Watchlist-only; free% and user slot unverified, so NOT a strong lead.",
    xVerified=False, velocityVerified=False,
    runNote0901_1109="Run 0901: added as mature newly-noticed (NOT early lead); pre-window mints 414, first pre-window block 132500929.",
)

# top-level run notes
snap["timestamp_wib"] = "2026-11-09 09:4x WIB"
snap["last_run_wib"] = "2026-11-09 09:4x WIB"
snap["last_run"] = "0901"
snap["runNote0901"] = (
    f"Run 0901: PARTIAL re-read {n_updated}/588 address-bearing contracts at block {B9} (script died silently after 400 contracts, last log 09:34 WIB LEAN Foxagent-0DAa, no traceback; track_c leg NEVER ran, 0 entries - track_c values stay at 0831, stale not zero). "
    f"Velocity LOLOS (0831->0901 vs 0731->0831, 40.7 vs 58.4 min): {vel_pass}. Near (>=20, fail): {vel_near}. "
    f"New free-pool sellouts: {sellout}. Slot changes: {slot_ch}. "
    "Scan: pre-flight OK 10.5s; window intended 132503471-132504470 but chunk 132503971-132504020 failed (Ankr 'Remote end closed connection'), script broke by design - only 500 blocks covered (132503471-132503970); gap 132503971-132504470 unscanned, for backfill/next run; enrich died 2/73 (partial=true, 1 enriched). "
    "Triage: 6 first-seen, 1 agent-shaped (0xCFB72b0E) proved MATURE via 414 pre-window mints - 0 new early leads; 0 same-owner discards; 5c: 35 candidates, 2 new checked, 0 S1/S2. "
    "Discovery: 1 NEW track-C lead YAMA (all 4 lead legs verified) BUT website gate FAILED - reported once, NO preview/execution. NNOM free pool exhausted (paid-only); Nero Agent unverified; BAGENT paid+sold out. "
    "Binanceai claim: still refund/failed phase, no change. Bridge unchanged since 2026-11-08 18:21 UTC."
)
snap["runNote0901_scan"] = (
    "Scan run 0901: pre-flight OK 10.5s (1000 logs/50 blocks, window 132504150-132504199). Intended window 132503471-132504470 (1000 blocks, cap 1000) but only 132503471-132503970 covered: "
    "Ankr chunk 132503971-132504020 failed ('Remote end closed connection without response'), script broke from chunk loop by design; 20 Ankr calls, 1 error. "
    "Counts (500 covered blocks): 72 ERC-721 + 1 ERC-1155 raw; 230 ERC-20 mint. GAP 132503971-132504470 (500 blocks) NOT scanned this run - recorded for backfill/next run, NOT retried aggressively. "
    "Enrich died silently at 2/73 (partial=true, 1 contract enriched); contracts_raw + ERC20 list complete for covered blocks, triage unaffected. "
    "Watermark NOT advanced (backfill owns it). HIVE Agents not found in window."
)
snap["runNote0901_velocity"] = (
    f"Velocity passes run 0901 (0831->0901 vs 0731->0831, ratio>=1.5 AND >=20 tokens, 400 read contracts only): {vel_pass}. "
    "All 14 NFT-scale passes BLOCKED from promotion: free% UNVERIFIED (freeClaimed and/or FREE_SUPPLY/MAX_SUPPLY null in the 0901 read); freeClaimed_user None (user slot unverified); website/X unverified. "
    "Token-scale passes (STARRY, bridge-0x93bf08d2) are ERC-20 artefacts, not NFT promotions. "
    "BAHUANG2 (gate-blocked strong lead, reported 2026-11-08): velocity passes again but free% unverified + gate blocked - no new report. "
    "MONOLITH / BAHUANG3 / Golden Agents / HELIX (early leads): velocity passes but free% unverified - stay early leads. "
    "188 contracts unread this run (script died) incl. Glitchronin + Neptivane (0831 velocity passes) - NO verdict for them, values stale."
)
snap["runNote0901_binanceai"] = (
    "Run 0901 (block 132506379): binanceai.fun launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance=0. "
    "IDENTICAL to run 0831 / snapshot (refund/failed phase since 2026-11-08). No change, no re-report. Never preview/claim while not open."
)
snap["runNote0901_discovery"] = (
    "Run 0901 discovery: Boltbook EN+ZH fetched ~09:25 WIB (45,930 / 47,170 bytes). New vs snapshot: YAMA sale 0x86d779fc... (TRACK-C LEAD, gate FAILED - reported once, no preview/execution), "
    "Nebula Nomads 0xb1af1f59... (free pool exhausted, paid-only 0.0005 BNB), Nero Agent 0xe4672087... (free selectors revert, Sourcify unverified, watchlist-only), BAGENT proxy 0x9CA1A3ee... (PAID, sold out 10,000 shares). "
    "Sourcify feed 20 entries (verifiedAt 01:51:46Z-02:23:45Z): 9 new vs hot-leg 0904, ALL S1=false S2=false (incl. 2 agent-shaped PAID spot sales 0x23d7906A/0x0d46d9C0, no free views). "
    "Sweep + complements (Square/Odaily/PANews/DappBay): no new leads. Bridge unchanged since 2026-11-08 18:21 UTC; same 8 not-in-snapshot, 7 same_owner_discarded never promoted. 0 new candidates/strong/early leads."
)
snap["runNote0901_age_watch"] = (
    "AGE WATCH: Alchemister-0xCafEEDDF (0xCafEEDDF3C15C5CD9A63D97021efDe845e1781Bc) firstMint 2026-11-07 09:49:19 WIB (firstMintBlock 132123483, snapshot); 48h deadline 2026-11-09 09:49:19 WIB. "
    "Last read run 0901 ~09:26 WIB (block 132504249): totalSupply 6251->6261 (+10), MAX_SUPPLY 15000 (41.7%) - STILL NOT SOLD OUT; freeClaimed None (free% UNVERIFIED). "
    "Merge ran BEFORE the 09:49:19 WIB deadline, so NOT age-excluded this run. Run 0931 MUST age-exclude (remove from watchlist + report once) if still unsold out after 09:49:19 WIB. "
    "UNKNOWN-720a (early lead, firstMint 2026-11-07 13:31 WIB): 48h deadline 2026-11-09 13:31 WIB - not yet due."
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
print(f"MERGE DONE: updated={n_updated} vel_pass={vel_pass}")
print(f"vel_near={vel_near}")
print(f"sellout={sellout} slot_changes={slot_ch}")
print(f"seen added={added} (total {len(seen)}); contracts now={len(snap['contracts'])} track_c now={len(snap.get('track_c', {}))}")
