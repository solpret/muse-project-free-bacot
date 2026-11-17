#!/usr/bin/env python3
"""Merge run 2026-11-09 0731 WIB into onchain-snapshot.json.
- Re-read values for all 561 snapshot contracts + 75 track_c (block 132491029).
- Velocity: rate 0631->0731 vs rate 0531->0631 (blocks 132475627/132482323/132491029).
- New entries: MONEY + ShadowSquad (0631 carry-over), 7 mature scan contracts,
  Ringgent, Glitchpilotfox, MiraAgent, FOUNT (track_c), SakuraNFT (paid-only),
  BAO-NFT (age-excluded), AgenticGangsterNFT (age-unverified).
- Status updates: LIFTCAT sold-out free, GLOOP sold-out.
- Appends scan first-seen contracts to onchain-scan-seen.json and 5c-checked
  addresses to track-c-scan-checked.json. Does NOT touch the scan watermark.
"""
import json, copy
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
B5, B6, B7 = 132475627, 132482323, 132491029
MIN_56 = (B6 - B5) * 0.45 / 60
MIN_67 = (B7 - B6) * 0.45 / 60

snap = json.load(open(f"{HF}/onchain-snapshot.json"))
r7 = json.load(open(f"{HF}/run-2026-11-09-0731-reread.json"))
r6 = json.load(open(f"{HF}/run-2026-11-09-0631-reread.json"))
gate = json.load(open(f"{HF}/run-2026-11-09-0731-gate.json"))
early = json.load(open(f"{HF}/run-2026-11-09-0731-early-verify.json"))
prew = json.load(open(f"{HF}/run-2026-11-09-0731-prewindow.json"))
tri = json.load(open(f"{HF}/run-2026-11-09-0731-triage.json"))
try:
    fm = json.load(open(f"{HF}/run-2026-11-09-0731-firstmint.json"))
except Exception:
    fm = {}

def sup(d):
    if not isinstance(d, dict): return None
    v = d.get("totalSupply")
    return v if v is not None else d.get("totalMinted")

rr7, rr6 = r7["reread"], r6["reread"]
contracts = snap["contracts"]
vel_pass, vel_near, sellout, slot_ch = [], [], [], []
n_updated = 0
for name, d7 in rr7.items():
    old = contracts.get(name)
    if not isinstance(old, dict):
        continue
    d6 = rr6.get(name)
    # update reads (only when not None, to preserve last-known on RPC degradation)
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if d7.get(k) is not None:
            old[k] = d7[k]
    old["lastReadBlock"] = B7
    old["lastReadWib"] = "2026-11-09 08:2x WIB"
    s7, s6, s5 = sup(d7), sup(d6), sup(old)
    # NOTE: sup(old) reads the just-updated totalSupply; use stored previous instead
    prev_sup = old.get("previousTotalSupply")
    if s7 is not None and prev_sup is not None:
        minted = s7 - prev_sup
        old["mintedInInterval"] = minted
    else:
        minted = None
    if s7 is not None and s6 is not None and prev_sup is not None:
        m_cur = s7 - s6
        m_prev = s6 - prev_sup
        rate_cur = m_cur / MIN_67
        rate_prev = m_prev / MIN_56 if MIN_56 > 0 else 0
        ratio = (rate_cur / rate_prev) if rate_prev > 0 else None
        old["previousTotalSupply"] = s7
        old["previousRatePerMin"] = rate_prev
        old["currentRatePerMin"] = rate_cur
        old["intervalMinutes"] = round(MIN_67, 1)
        old["velocityRatio"] = ratio
        passes = ratio is not None and ratio >= 1.5 and m_cur >= 20
        old["velocityLegPasses"] = passes
        old["velocityNote"] = f"run 0731: {s6}->{s7} (+{m_cur}, {rate_cur:.3f}/mnt vs prev {rate_prev:.3f} = {ratio:.2f}x)" if ratio is not None else f"run 0731: {s6}->{s7} (+{m_cur}, {rate_cur:.3f}/mnt, prev rate 0)"
        if passes:
            vel_pass.append(name)
        elif m_cur >= 20:
            vel_near.append((name, m_cur, round(rate_cur, 3), round(rate_prev, 3), round(ratio, 2) if ratio else None))
    # free-pool sellout (new)
    fc = d7.get("freeClaimed"); fs = old.get("FREE_SUPPLY") or d7.get("FREE_SUPPLY")
    fmint = d7.get("freeMinted"); fcap = old.get("FREE_CAP") or d7.get("FREE_CAP")
    old_fc = old.get("freeClaimed"); old_fm = old.get("freeMinted")
    if fc is not None and fs and fc >= fs and not (old_fc is not None and old_fc >= fs):
        sellout.append((name, "freeClaimed", fc, fs))
    if fmint is not None and fcap and fmint >= fcap and not (old_fm is not None and old_fm >= fcap):
        sellout.append((name, "freeMinted", fmint, fcap))
    # slot change
    ob, nb = old.get("balanceOf_user"), d7.get("balanceOf_user")
    if ob is not None and nb is not None and ob != nb:
        slot_ch.append((name, ob, nb))
    old["runNote0731_1109"] = (
        f"Run 0731 (blok {B7}): totalSupply {s7} (prev {s6}), minted interval {minted}, "
        f"velocity {'LOLOS' if old.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={old.get('freeClaimed')}/{old.get('FREE_SUPPLY')} freeMinted={old.get('freeMinted')}/{old.get('FREE_CAP')}; "
        f"bal_user={d7.get('balanceOf_user')}; status {old.get('status')}."
    )
    n_updated += 1

# track_c updates
tc = snap.get("track_c", {})
n_tc = 0
for k, v in r7.get("track_c", {}).items():
    if not isinstance(v, dict):
        continue
    ent = tc.get(k)
    if not isinstance(ent, dict):
        continue
    for kk in ("totalSupply", "freeMinted", "freeClaimed"):
        if v.get(kk) is not None:
            ent[kk] = v[kk]
    ent["runNote0731_1109"] = f"Run 0731 (blok {B7}): totalSupply {v.get('totalSupply')}, freeMinted {v.get('freeMinted')}."
    n_tc += 1

# ---- new entries ----
def base_entry(name, addr, status, **kw):
    e = {"address": addr, "status": status, "name": name, "lastReadBlock": B7,
         "lastReadWib": "2026-11-09 08:2x WIB"}
    e.update(kw)
    return e

# MONEY (0631 carry-over, early lead reported 0631; website verified this run)
contracts["MONEY"] = base_entry(
    "MONEY", "0x085a493ac880188a69ad38449f505dA9E730C50B", "early-lead-2026-11-09",
    symbol="MONEY", kind="ERC721", totalSupply=None, totalMinted=207, freeMinted=207,
    FREE_CAP=222, MAX_SUPPLY=333, freePctVerified=93.2, mintOpen=1,
    userBalance=0, firstSeenBlock=132482094,
    firstMintWib="2026-11-09 06:39:42 WIB",
    launchNote="First mint verified on-chain: block 132482094, 2026-11-09 06:39:42 WIB (run 0631). Age ~1.7h at run 0731, within 48h.",
    website="https://money-nft-mint.netlify.app/",
    websiteEvidence="Method I: tokenURI(1) = https://money-nft-mint.netlify.app/metadata/metadata.json; site fetched 200 (12,674 bytes) run 0731 and PRINTS the exact contract 0x085a493ac880188a69ad38449f505dA9E730C50B.",
    gate="website_verified",
    xVerified=False, velocityVerified=False, velocityLegPasses=False,
    velocityNote="Run 0731: freeMinted 154 (0631) -> 192 (gate) -> 207 (verify), rate ~1/min vs prev ~1.9/min -> velocity GAGAL (<1.5x).",
    userSlotNote="Slot user UNVERIFIED: contract has no freeClaimed(address)/freeFor view; balanceOf(user)=0 only.",
    owner="0x13333df46ab3e95f4166370d571e7b73aad06370",
    ownerNote="Owner same as LIFTCAT (0x13333df46ab3e95f4166370d571e7b73aad06370); NOT in same-owner-discards.json.",
    baselineNote="EARLY lead reported once run 0631. Never auto-minted/previewed. Free 207/222 = 93.2% (pool nearly exhausted, ~15 left). Stays early lead: velocity fails, X unverified, user slot unverified.",
    runNote0731_1109="Run 0731: freeMinted 207/222 (93.2%), website VERIFIED via tokenURI->netlify site printing exact contract; velocity GAGAL; X unverified; slot unverified; early lead only, no execution.",
)

# ShadowSquad (0631 carry-over, strong lead pending gate; gate methods A-N tried, L pending browser)
contracts["ShadowSquad"] = base_entry(
    "ShadowSquad", "0x0bc496BC51D14ae6C4A7003B05061323d4De9206", "strong-lead-2026-11-09-gate-pending",
    symbol="SHASQU", kind="ERC721", totalSupply=433, freeClaimed=411, FREE_SUPPLY=819,
    MAX_SUPPLY=1170, freePctVerified=50.2, mintOpen=1, FREE_PER_WALLET=1,
    userBalance=0, firstSeenBlock=132482138,
    firstMintWib="2026-11-09 06:40:02 WIB",
    launchNote="First mint verified on-chain: block 132482138, 2026-11-09 06:40:02 WIB (run 0631). Age ~1.7h at run 0731, within 48h.",
    xVerified=False, velocityVerified=False, velocityLegPasses=False,
    velocityNote="Run 0731: totalSupply flat 433, freeClaimed flat 411 vs run 0631 -> velocity GAGAL (0 token).",
    userSlotNote="Slot OPEN: quote(user,1)=0, freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0 (verified 0631 + 0731 gate).",
    owner="0x90e8b1c93c80758e2bd5032c7acec382501cb84b",
    ownerNote="Owner NOT in same-owner-discards.json (checked 0631 + 0731).",
    gate="pending_method_L_bscscan",
    gateNote="Website gate methods tried run 0631+0731: (A) raw contract search - no hit; (B) Boltbook front page EN+ZH - absent; (C) Sourcify metadata - no URLs; (G) project-name search - no hit; (H) contractURI - base64 JSON, no external_link; (I) tokenURI - metadata only, no external_url; (J) ABI grep - no site functions; (M) site: filters - no results; (D) no same-family pattern; (N) no Boltbook author hop (no post). (L) BscScan token page via live browser - PENDING at merge time; gate concludes after L.",
    baselineNote="STRONG LEAD (age verified <=48h + free 411/819=50.2% + slot open) reported run 0631 as gate-pending. NOT executed, NOT previewed. Direct mint ONLY if website gate passes + audit + clean preview + free quota fresh.",
    runNote0731_1109="Run 0731: freeClaimed 411/819 (50.2%) flat, slot OPEN, velocity GAGAL; gate still pending method L (BscScan browser read); no execution.",
)

# 7 mature scan contracts (NOT early leads: pre-window mints prove launches predate the window)
MAT = {
 "0xaE9d85E7": ("0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8", 285, 281, 2000, "registry-bytes True, Sourcify unverified; owner 0x6f244724... = Glitchpilotfox/Chipbotcore/Ringgent cluster operator (not in discards)"),
 "0xa7046Fc6": ("0xa7046Fc653556b8d50370Ab8dB189b2E447eacDb", 475, None, 100, "Sourcify exact_match, FREE_SUPPLY constant + mint; totalSupply 475 > FREE_SUPPLY 100"),
 "0xB03A85D2": ("0xB03A85D2bdF7d2C5aeb0cE5e69Af6b94BE78f672", 746, 746, 4000, "S1 (mint+quote+free views+agent), exact_match; owner 0x190f1f0c... shared with 0x02669Fe0"),
 "0xb7ae3eF5": ("0xb7ae3eF58f4507a29115DEc6Eb8De7fEEcc3b6C4", 90, None, 6000, "registry-bytes True, Sourcify unverified; freeMinted 88/6000 = 1.5%"),
 "0x02669Fe0": ("0x02669Fe012373EE95882Bc02bba207a7De55ccdB", 433, 433, 3800, "S1 (mint+quote+free views+agent), exact_match; owner 0x190f1f0c... shared with 0xB03A85D2"),
 "0x8852505F": ("0x8852505F66F153124879b46Be364627572175d4D", None, None, None, "registry-bytes True, exact_match, claimFree + mint; totalMinted 945"),
 "0xB6407991": ("0xB6407991b76E712d15EdEF06e125abcC730364F7", None, None, None, "registry-bytes True, Sourcify match, mint fns; totalMinted 8054; mintedBy(user)=1 - user already minted"),
}
for short, (addr, ts, fc, fs, note) in MAT.items():
    ev = early.get(short, {})
    pw = prew.get(short, {})
    contracts[short] = base_entry(
        short, addr, "watchlist-only-mature-newly-noticed-2026-11-09",
        kind="ERC721", totalSupply=ts, freeClaimed=fc, FREE_SUPPLY=fs,
        userBalance=ev.get("balanceOf_user"),
        firstSeenBlock=next((x["first_block"] for x in tri["first_seen_triage"] if x["address"].lower() == addr.lower()), None),
        launchNote="Age UNVERIFIED: first mint predates the scan window (pre-window mints in [132400000, 132490028] or large totalSupply with 0 pre-window mints => launched before ~132400000). NOT a window launch; do NOT report as early lead.",
        preWindowMints=pw.get("pre_window_mints"),
        baselineNote=f"Scan first-seen run 0731 but MATURE (not a new launch). {note}. First-seen in this window is a seen-file gap artifact, not a launch. Watchlist-only; age/free% still unverified for tiers.",
        xVerified=False, velocityVerified=False,
        runNote0731_1109=f"Run 0731: added as mature newly-noticed (NOT early lead); totalSupply {ts}, freeClaimed {fc}/{fs}, pre-window mints {pw.get('pre_window_mints')}.",
    )

# Ringgent (Boltbook discovery; age pending first-mint search)
rg_fm = fm.get("Ringgent", {})
contracts["Ringgent"] = base_entry(
    "Ringgent", "0xf1d1650dbfeb0fa8082481c8213accd59af3cf4a", "watchlist-only-boltbook-2026-11-09",
    symbol="RINGGENT", kind="ERC721", totalSupply=941, freeClaimed=940, FREE_SUPPLY=1000,
    MAX_SUPPLY=1000, freePctVerified=94.0, mintOpen=1, FREE_PER_WALLET=2,
    userBalance=0,
    launchNote="Age UNVERIFIED at merge: first mint before block 132400000 (184 mints in [132400000,132490028] + ~753 earlier); full first-mint search running run 0731. Boltbook recheck 935/1000 at block 132490254 (msbrew.ai).",
    firstMintBlock=rg_fm.get("first_mint_block"), firstMintWib=rg_fm.get("wib"),
    owner="0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
    ownerNote="Owner = Glitchpilotfox/Chipbotcore cluster operator (not in same-owner-discards.json).",
    userSlotNote="Slot OPEN: quote(user,1)=0, freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0.",
    xVerified=False, velocityVerified=False,
    baselineNote="Boltbook discovery run 0731 (msbrew.ai recheck 6: 935/1000, pace ~0.23/min). Free 94.0% + slot open, but AGE UNVERIFIED -> watchlist-only, NOT a strong lead until first mint verifies <=48h. No preview/mint.",
    runNote0731_1109="Run 0731: freeClaimed 940/1000 (94.0%), slot OPEN, age UNVERIFIED (first-mint search running); watchlist-only.",
)

# Glitchpilotfox (bridge contract; Boltbook mention run 0731)
gf_fm = fm.get("Glitchpilotfox", {})
contracts["Glitchpilotfox"] = base_entry(
    "Glitchpilotfox", "0xda552a0b709d09a2532689c6e39d981f527817b6", "watchlist-only-pelengkap-scan-2026-11-09",
    kind="ERC721", totalSupply=1541, freeClaimed=1536, FREE_SUPPLY=4000,
    MAX_SUPPLY=4000, freePctVerified=38.4, mintOpen=1,
    userBalance=0,
    launchNote="Age UNVERIFIED: 79 mints in [132400000,132490028], first pre-window block 132413037; full first-mint search running run 0731. Boltbook: 1536/4000, +4 in ~11m (drhmwt.ai).",
    firstMintBlock=gf_fm.get("first_mint_block"), firstMintWib=gf_fm.get("wib"),
    owner="0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
    ownerNote="Owner = Chipbotcore/Ringgent cluster operator (not in same-owner-discards.json).",
    userSlotNote="Slot OPEN: quote(user,1)=0, freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0.",
    source="scan-bridge (temuan pelengkap scan)",
    xVerified=False, velocityVerified=False,
    baselineNote="Bridge contract (temuan pelengkap scan), added to snapshot on first routine re-read run 0731. Free 38.4% + slot open, but AGE UNVERIFIED -> watchlist-only, NOT a strong lead until first mint verifies <=48h. Report only on promotion/change, labeled 'temuan pelengkap scan'.",
    runNote0731_1109="Run 0731: freeClaimed 1536/4000 (38.4%), slot OPEN, age UNVERIFIED; watchlist-only (pelengkap scan).",
)

# MiraAgent (Boltbook; free path unverified, Sourcify unverified)
contracts["MiraAgent"] = base_entry(
    "MiraAgent", "0xa545c7aa04885bbd9cf7ae450ae52c40dcb9e449", "watchlist-only-boltbook-2026-11-09",
    kind="ERC721", totalSupply=9900, totalMinted=9900, MAX_SUPPLY=10000,
    userBalance=0,
    launchNote="Age UNVERIFIED. Boltbook (hannn.ai): 9,900/10,000 (99%), frozen 35 min, contract UNVERIFIED on Sourcify.",
    xVerified=False, velocityVerified=False,
    baselineNote="Boltbook discovery run 0731. No free views on contract (freeClaimed/freeMinted all None) -> free% UNVERIFIED; Sourcify UNVERIFIED -> agent-shape unknown. Watchlist-only; not a lead.",
    runNote0731_1109="Run 0731: totalSupply 9900/10000, free views None, Sourcify unverified; watchlist-only.",
)

# SakuraNFT (paid-only) + BAO-NFT (age-excluded) + AgenticGangsterNFT (age-unverified)
contracts["SakuraNFT"] = base_entry(
    "SakuraNFT", "0xE56fD19a19E684b94db1Dd3c81896736E3631D47", "watchlist-only-paid-only-2026-11-09",
    kind="ERC721", totalMinted=335, mintOpen=1, userBalance=0,
    launchNote="First mint 2026-11-09 07:01:49 WIB (block 132485042, run 0631).",
    baselineNote="Sourcify agent-shaped (S1) but PAID-ONLY: remainingFree=0, costOf(user,1)=0.0005 BNB (run 0631 verify3). Never a free-mint candidate.",
    owner="0xe8f8a788f962d7e272de9d9980481f574844004b",
    runNote0731_1109="Run 0731: carried from 0631 as paid-only (costOf 0.0005 BNB, remainingFree 0); no execution.",
)
contracts["BAO-NFT"] = base_entry(
    "BAO-NFT", "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354", "age-excluded-2026-11-09",
    kind="ERC721",
    launchNote="First mint 2026-11-06 06:00:48 WIB (block 131901105, run 0631) -> >48h at run 0731. AGE-EXCLUDED.",
    baselineNote="Boltbook radar post (run 0631) but age-excluded: first mint 2026-11-06, over 48h old and not sold out. Removed from active watchlist per age rule; re-add only on a genuinely new mint phase/batch.",
    runNote0731_1109="Run 0731: age-excluded (>48h, first mint 2026-11-06 06:00:48 WIB).",
)
contracts["AgenticGangsterNFT"] = base_entry(
    "AgenticGangsterNFT", "0x0A2a07eF09DD7D83E2312476F0588aBaA3E34Ce3", "watchlist-only-age-unverified-2026-11-09",
    kind="ERC721", totalMinted=None, freeMinted=1, FREE_SUPPLY=111, MAX_SUPPLY=1111,
    userBalance=0,
    launchNote="Age UNVERIFIED: no mints found in [132440000, 132487777] (run 0631); first mint not yet located.",
    baselineNote="Sourcify agent-shaped (freeMint EIP-712 + FREE_SUPPLY + coinContract), exact_match (run 0631). freeMinted 1/111. Age unverified -> watchlist-only.",
    runNote0731_1109="Run 0731: carried from 0631 as age-unverified watchlist-only; freeMinted 1/111.",
)

# FOUNT -> track_c watchlist-only
tc["FOUNT"] = {
    "address": "0x4d146a58cB2D38ce91961358Dc090282e6ec7396",
    "status": "watchlist-only-boltbook-2026-11-09",
    "name": "FOUNT", "kind": "ERC20",
    "totalSupply": 1000000000000000000000000000, "freeMinted": 1000,
    "userBalance": 0, "lastReadBlock": B7, "lastReadWib": "2026-11-09 08:2x WIB",
    "launchNote": "Age UNVERIFIED. Boltbook (crypto19.ai): 'FOUNT free lane - 50,000 FOUNT, ~364 left, burst took 500 in ~30 min'. Sourcify verified 2026-11-09T00:24:36Z.",
    "agentId": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "baselineNote": "Boltbook + Sourcify discovery run 0731. ERC-20 with freeMinted 1000; free cap (FREE_SUPPLY/FREE_SLOTS) not yet read -> free pool status UNVERIFIED. Track-C sale-shape check pending (slow verify). Watchlist-only; not a lead.",
    "runNote0731_1109": "Run 0731: freeMinted 1000, totalSupply 1e27, agentId=registry; free cap unverified; watchlist-only.",
}

# LIFTCAT + GLOOP sold-out updates (0631 findings)
if "LIFTCAT" in contracts:
    contracts["LIFTCAT"]["status"] = "sold-out-free-2026-11-09"
    contracts["LIFTCAT"]["runNote0731_1109"] = "Run 0731: carried from 0631 - free pool EXHAUSTED (freeMinted 222/222 FREE_CAP). Status -> sold-out-free."
if "GLOOP" in contracts:
    contracts["GLOOP"]["status"] = "sold-out-2026-11-09"
    contracts["GLOOP"]["runNote0731_1109"] = "Run 0731: carried from 0631 - SOLD OUT totalMinted 3,333/3,333 (Boltbook + on-chain). Status -> sold-out."

# top-level run notes
snap["timestamp_wib"] = "2026-11-09 08:2x WIB"
snap["runNote0731"] = (
    f"Run 0731: re-read {n_updated}/561 contracts + {n_tc}/75 track_c at block {B7} (reread 702.6s, exit 0). "
    f"Velocity LOLOS (0631->0731 vs 0531->0631): {vel_pass}. Near (>=20, fail): {vel_near}. "
    f"New free-pool sellouts: {sellout}. Slot changes: {slot_ch}. "
    "Scan window 132490029-132491028 (1000 blocks, 38 Ankr calls, 1 chunk error 132490979-132491028); "
    "87 NFT + 272 ERC20-mint; 23 first-seen triaged, 0 new early leads (all 7 agent-shaped first-seen proved mature via pre-window mints); "
    "track-C 5c: 57 candidates, 9 new checked, 0 S1/S2. "
    "MONEY website VERIFIED (money-nft-mint.netlify.app prints exact contract); ShadowSquad gate pending method L (BscScan browser)."
)
snap["runNote0731_scan"] = (
    "Scan run 0731: pre-flight OK 3.0s (1000 logs/50 blocks). Window 132490029-132491028 (latest 1000, cap 1000). "
    "Gap to backfill watermark not scanned by this job (backfill owns watermark). "
    "Chunk error: Transfer 132490979-132491028 remote-end-closed (50 blocks at head end; contracts first-minted only there may be missed this run; backfill covers). "
    "Enrich still running at merge time (partial=true); contracts_raw + ERC20 list complete, triage unaffected."
)
snap["runNote0731_velocity"] = f"Velocity passes run 0731: {vel_pass} (all blocked: free% unverified except Neptivane discarded; VOLT/Zhenzhu token-scale, not NFT mints)."

# append newly seen scan contracts to seen file
seen = json.load(open(f"{HF}/onchain-scan-seen.json"))
sc = json.load(open(f"{HF}/run-2026-11-09-0731-scan.json"))
seen_lows = {k.lower() for k in seen}
added = 0
for c in sc.get("contracts_raw", []):
    if c["address"].lower() not in seen_lows:
        seen[c["address"]] = c.get("first_block")
        added += 1
json.dump(seen, open(f"{HF}/onchain-scan-seen.json", "w"), indent=1)

# append 5c-checked addresses
checked = json.load(open(f"{HF}/track-c-scan-checked.json"))
checked_lows = {k.lower() for k in checked}
added5c = 0
for x in tri.get("track_c_5c", []):
    if x["address"].lower() not in checked_lows:
        checked[x["address"]] = {"run": "2026-11-09-0731", "S1": x.get("S1"), "S2": x.get("S2"),
                                 "sourcify": x.get("sourcify"), "mint_count": x.get("mint_count")}
        added5c += 1
json.dump(checked, open(f"{HF}/track-c-scan-checked.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE: updated={n_updated} track_c={n_tc} vel_pass={vel_pass}")
print(f"vel_near={vel_near}")
print(f"sellout={sellout} slot_changes={slot_ch}")
print(f"seen added={added} (total {len(seen)}); 5c added={added5c} (total {len(checked)})")
print(f"contracts now={len(snap['contracts'])} track_c now={len(snap.get('track_c', {}))}")
