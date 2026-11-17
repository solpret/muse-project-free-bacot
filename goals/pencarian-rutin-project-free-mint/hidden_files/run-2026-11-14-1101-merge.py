#!/usr/bin/env python3
"""Merge run 1101 (2026-11-14 ~11:01 WIB) into onchain-snapshot.json. Read-only on-chain; writes snapshot + this log."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
old=json.load(open(BASE+"run-2026-11-14-1031-reread.json"))["reads"]
new=json.load(open(BASE+"run-2026-11-14-1101-reread.json"))["reads"]
INTERVAL=27.8  # minutes, blocks 133472775 -> 133476480 @0.45s/blk
TOTKEYS=("totalMinted","totalSupply","totalSnippets","totalRemnants","totalSpecimens")
def tot(views):
    for k in TOTKEYS:
        if k in views and views[k] is not None: return k, views[k]
    return None, None
notes=[]
for name, item in new.items():
    nv=item["views"]; nk, nval = tot(nv)
    if nk is None: 
        notes.append(f"{name}: no total view (reads null again)" if name=="Zero" else f"{name}: no total view")
        continue
    ov = old.get(name,{}).get("views",{})
    ok, oval = tot(ov)
    entry = snap["contracts"].setdefault(name, {})
    prev_rate = entry.get("currentRatePerMin")
    if oval is not None and nval is not None:
        d = nval - oval
        rate = round(d/INTERVAL, 3)
        ratio = round(rate/prev_rate, 2) if prev_rate else None
        vel = bool(prev_rate and rate >= 1.5*prev_rate and d >= 20)
        entry["previousTotalSupply"]=oval; entry["mintedInInterval"]=d
        entry["intervalMinutes"]=INTERVAL; entry["currentRatePerMin"]=rate
        entry["previousRatePerMin"]=prev_rate; entry["velocityRatio"]=ratio
        entry["velocityLegPasses"]=vel
    entry[nk]=nval; entry["lastReadBlock"]=133476480; entry["lastReadWib"]="2026-11-14 ~11:04 WIB"
    # keep the per-view fresh values too
    for k,v in nv.items():
        if v is not None: entry[k]=v
    entry["runNote1101_1114"]=f"Run 1101 (blok 133476480): {nk} {oval}->{nval} (+{nval-oval if oval is not None else '?'}, {round((nval-oval)/INTERVAL,3) if oval is not None else '?'}/mnt, prev rate {prev_rate}, ratio {round(((nval-oval)/INTERVAL)/prev_rate,2) if prev_rate and oval is not None else 'n/a'}) -> velocity {'LOLOS' if entry.get('velocityLegPasses') else 'GAGAL'}."
    notes.append(entry["runNote1101_1114"])
# --- new entries ---
snap["contracts"]["CPASS"]={
 "address":"0x5877d2bb9f226cc3e438f4d656caeb27deafc576","name":"CoinFin Pass","symbol":"CPASS","kind":"ERC721",
 "status":"early-lead-reported-2026-11-14",
 "source":"Boltbook board (muhlis020201 10:50 recheck + mamun21k) + Sourcify feed cross-check, run 1101",
 "totalMinted":1070,"MAX_SUPPLY":10000,"MAX_PER_WALLET":20,"mintOpen":1,
 "priceFor_user":0,"holdsAgentId_user":1,"balanceOf_user":0,"mintCountOf_user":0,
 "firstSeenWib":"2026-11-14 ~11:10 WIB (run 1101)","firstSeenSource":"Boltbook post 2BA_J3aDHmqo (CPASS 977 @10:50) + own on-chain read 1070 @~11:15",
 "freePctNote":"UNVERIFIED: no freeMinted/freeClaimed/free-pool view in ABI; totalMinted 1070/10000=10.7% is TOTAL, not free quota (paid tiers 0.0002/0.0004/0.0008 BNB exist). Never substitute total % for free %.",
 "launchNote":"UNVERIFIED: llms.txt says contracts deployed 2026-11-13; mint-open time not stated; first Boltbook mention ~10:19 WIB 14 Nov with 867 already minted. First-mint log unverifiable this run (Ankr 401; dataseed eth_getLogs -32005 limit-exceeded incl. control; publicnode rate-limited).",
 "website":"https://coinfin.fun/","gate":"PASSED-2026-11-14 (llms.txt prints exact Pass contract 0x5877D2bb9F226cC3E438F4d656cAeb27DEAFC576; baseTokenURI https://coinfin.fun/metadata/pass/; homepage loads 20.722 byte; skill.md/launch.json return GitHub 404 page, no contract there)",
 "xStatus":"not checked","velocityNote":"First baseline this run: 977 @10:50 (Boltbook) -> 1070 @~11:15 own read (+93, ~3,7/mnt). No previous rate yet; do NOT pass on velocity alone.",
 "slotNote":"Slot OPEN: priceFor(user)=0, mintCountOf(user)=0, holdsAgentId(user)=1, balanceOf(user)=0, mintOpen=1. Free mint needs contract knowledge question (salt COINFIN-Q, per llms.txt).",
 "note":"EARLY lead reported once run 1101. NEVER auto-mint/preview as early lead. Site also promises 250.000 FIN claim per Pass + BNB season dividends (site description, UNVERIFIED value).",
 "lastReadBlock":133476480,"lastReadWib":"2026-11-14 ~11:15 WIB"}
snap["contracts"]["Trash Bandits"]={
 "address":"0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D","name":"Trash Bandits","symbol":"BANDIT","kind":"ERC721",
 "status":"watchlist-only-2026-11-14",
 "source":"Boltbook post 61DKbMV2gZDB (bangwi.ai recheck) + hot-leg-seen 2026-11-13 02:12 WIB",
 "totalMinted":236,"MAX_SUPPLY":1000,"balanceOf_user":0,
 "freePctNote":"UNVERIFIED: no freeMinted/freeClaimed/free-pool view in ABI (totalSupply/freeMinted/freeClaimed/mintOpen/owner ALL revert per author); totalMinted 236/1000=23.6% is TOTAL, not free quota.",
 "launchNote":"UNVERIFIED: first seen by hot leg 2026-11-13 02:12 WIB; Boltbook post 325 refresh ~03:28 WIB 14 Nov had 230. First-mint log not verified.",
 "gate":"NOT CHECKED","xStatus":"not checked",
 "velocityNote":"Pace ~0,01/mnt per author (230 @~03:28 -> 234 refresh, +4 in ~451 mnt); own read 236 @~11:20. Stalled.",
 "note":"Agent-shaped (claimAgentFree() + Agent-ID gate proven by author sims; ABI free views agentFreeCap/agentFreeUsed/claimAgentFree). Watchlist-only: below 50%/70% legs, free% + age unverified. Never reported as lead.",
 "lastReadBlock":133476480,"lastReadWib":"2026-11-14 ~11:20 WIB"}
snap["contracts"]["SPEC"]={
 "address":"0x639329f5dc4317c44D9Fed961a1217ba845012F7","name":"AgentLabs Specimen","symbol":"SPEC","kind":"ERC721",
 "status":"watchlist-only-2026-11-14",
 "source":"Boltbook post 2BA_J3aDHmqo + hot-leg-seen 2026-11-12 17:24 WIB",
 "totalSpecimens":3118,"currentExperiment":3,"genesisOpen":1,"genesisStart":1794492248,
 "priceFor_user":0,"holdsAgentId_user":1,"balanceOf_user":0,
 "freePctNote":"UNVERIFIED: no free counter in ABI (mintFree exists, paid tiers exist).",
 "launchNote":"genesisStart 1794492248 = 12 Nov ~21:00 WIB (site agentlabs.fun: one experiment/day). Current exp3 ends 07:00 WIB 15 Nov. Launch-age per experiment unverified; treated watchlist-only like LumenFindings.",
 "website":"https://agentlabs.fun/ (per hot-leg note 12 Nov: site loads, 'A daily experiment lab for agents')",
 "gate":"NOT CHECKED (free% unverified blocks candidacy anyway)",
 "lastReadBlock":133476480,"lastReadWib":"2026-11-14 ~11:16 WIB"}
snap.setdefault("track_c",{})["ORBIT"]={
 "sale":"0x7d5F7f323db3050AF92E9aa1584E883B3b24d680","token":"0x7d5F7f323db3050AF92E9aa1584E883B3b24d680 (same contract)",
 "status":"watchlist-only-age-unverified-2026-11-14",
 "name":"ORBIT","symbol":"ORBIT","kind":"ERC20-claim-single-contract",
 "saleShape":"PASS (S2-variant with equivalents): contract IS token (name/symbol/decimals/totalSupply) + no-arg claimFree() (mintFree equivalent) + free views freeClaimed/freeRemaining + FREE_MAX 888 (FREE_SLOTS equivalent) + AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Sourcify verified (37 fns).",
 "freeClaimed":60,"FREE_MAX":888,"freeRemaining":828,"FREE_AMOUNT":10000000000000000000000,"claimOpen":1,"PAID_PRICE":1000000000000000,
 "totalSupply":45572000000000000000000000,"MAX_SUPPLY":100000000000000000000000000,
 "userSlot":{"hasFreeClaimed":0,"balanceOf":0,"note":"Slot open: hasFreeClaimed(user)=0, claimOpen=1, freeRemaining 828."},
 "ageNote":"UNVERIFIED: Sourcify verifiedAt 2026-11-14T03:55:52Z (10:55:52 WIB) is verification time, NOT launch time. First-mint log unverifiable this run (Ankr 401; dataseed eth_getLogs -32005 incl. 500-blk chunks + control address; publicnode rate-limited; BscScan API returns HTML without key).",
 "xNote":"No project X found this run","website":"NOT CHECKED (no site found yet)",
 "boundary":"WATCHLIST ONLY. Never reported as a lead, never previewed/minted. Promotes only on verified age <24h + website gate + safety.",
 "lastReadBlock":133476480,"lastReadWib":"2026-11-14 ~11:10 WIB"}
snap.setdefault("track_c",{})["NIUBI-2c8E"]={
 "sale":"0x2c8EDa46dd4E5228375912f3efFf3781D25a54B7","token":None,
 "status":"watchlist-only-refund-phase-2026-11-14",
 "name":"NIUBI","site":"https://niubi.bid","kind":"ERC20-share-sale-proxy",
 "saleShape":"UNVERIFIED: proxy + implementation 0x6cd78d1eaadab0be51fa724675c77ecb173f8c82 BOTH unverified on Sourcify (ABI 404). Shape from Boltbook post + selector probes.",
 "totalMinted":1625,"MAX_SHARES":5999,"freeLotsClaimed":1625,"FREE_POOL":2000,"freeLeft":375,
 "mintOpen":1,"opened":0,"refunding":1,"refundDeadline":1794589624,
 "pair":"0x0eadCD47BaB8667488c98Fdf99FfA96BF3461196 (WBNB pair, reserves 0/0 per Boltbook rechecks)",
 "userSlot":{"balanceOf":0,"note":"User holds NO NIUBI share (balanceOf 0); never claimed. Author ai1288 claimed 1 free share 12 Nov."},
 "ageNote":"Age >24h: author claimed 12 Nov; 1.385 minted 12 Nov 20:01 -> 1.625 now. AGE-EXCLUDED regardless.",
 "note":"REFUND PHASE: refunding()=1, refundDeadline 2026-11-14 00:07 WIB passed, opened()=0, pair 0/0 (no market, no price). NOT a lead, never reported as one, never previewed/minted. Recorded so later runs do not re-triage it. Distinct from tracked NIUBI sale 0x094D... (track_c NIUBI).",
 "lastReadBlock":133476480,"lastReadWib":"2026-11-14 ~11:21 WIB"}
snap.setdefault("excluded",{})["Oathbots"]={
 "address":"0xb777c52296f0d7d3c5cab7ae0c1aaac6b014b256","symbol":"OATH","track":"A","status":"excluded-age-over-24h-2026-11-14",
 "note":"Binance Square post 2026-10-28 (17 days ago): 10.000 robots, first 8.000 Agent-ID wallets free, ~375 minted. Age >>24h, free ~4,7% of free allocation. Age-excluded; never reported, never previewed/minted."}
snap["runNote1101_1114"]="Run 1101 (jadwal 11:01, ~11:01-11:45 WIB): REREAD 25/25 OK blok 133476480 (107,3 dtk). Velocity: semua GAGAL (B77D 1,907 vs prev 3,46 = 0,55x; AgentBubble 0,540 vs 0,522 = 1,03x + free 1376/2222=61,9% <70%; MORFO/AgentZENITH/SPARKS flat; LumenFindings +32 free% UNVERIFIED; Pengu 66/999=6,6%). EARLY LEAD BARU: CPASS (CoinFin Pass) 0x5877d2bb9f226cc3e438f4d656caeb27deafc576 - totalMinted 1070/10000, ~3,7/mnt, slot terbuka (priceFor 0), website TERVERIFIKASI coinfin.fun/llms.txt (mencetak kontrak persis), free% + umur UNVERIFIED, X unverified - dilaporkan sekali sebagai EARLY, TIDAK PERNAH preview/mint. Track-C watchlist-only baru: ORBIT 0x7d5F... (S2-variant, free 828/888, slot terbuka, umur UNVERIFIED - getLogs mati di semua jalur). NIUBI-2c8E refund-phase (refunding 1, deadline 00:07 WIB lewat, opened 0, pair 0/0, user balance 0) - watchlist-only, bukan lead. Trash Bandits 236/1000 watchlist-only. SPEC watchlist-only (Lumen-family). SCAN: FAST-FAIL Ankr 401 (4,6 dtk), watermark TETAP 132512564. FEED: 18 baru vs 1031, 0 S1/S2 (ABI-only, 27,4 dtk). BOLTBOOK EN+ZH segar, 14 alamat; LUCKY LIFE same-owner-discarded (diam), Wraith not-agent-shaped (diam), GOAT paid 0,0004 BNB (bukan free), Runesmith vesting-claim (bukan free mint), Cube Apes chain 4663 (bukan BSC). SWEEP EN+ZH: 0 baru (Oathbots age-excluded, Golden Agents/STAMP/AGENT COSMOS sudah di snapshot, Agent Operators mint belum buka 15 Nov). ODAILY: 0 Agent ID/free-mint. BRIDGE: mtime 8 Nov 18:21 UTC, tidak berubah, 0 baru. PENDING CLAIM binanceai.fun: launched 0, failed 1, refund 1, tokenClaimed(user) 0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). DIAM. KANDIDAT 0, STRONG LEAD 0, TRACK-B 0, TRACK-C LEAD 0. EKSEKUSI/PREVIEW 0."
snap["last_run"]="run 1101 2026-11-14"
snap["last_run_wib"]="2026-11-14 ~11:45 WIB"
snap["last_run_note"]=snap["runNote1101_1114"]
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("merge OK; contracts:", len(snap["contracts"]), "track_c:", len(snap.get("track_c",{})))
for n in notes: print(n)
