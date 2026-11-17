#!/usr/bin/env python3
"""Merge run 2026-11-14 12:01 WIB reread + probe results into onchain-snapshot.json.
Conservative: only updates fields already present in an entry, plus one runNote1201_1114.
Adds 4 new Boltbook contracts (REOPIR early lead, 2x Frie Agent + OTV watchlist-only).
Updates track_c ORBIT + pending_claims binanceai.fun. Backs up snapshot first.
Read-only on chain; no preview/mint."""
import json, shutil, sys
sys.set_int_max_str_digits(100000)

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-1201")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-14-1201-reread.json"))
p = json.load(open(BASE + "run-2026-11-14-1201-probe.json"))
BLOCK = r["block"]
INTERVAL_MIN = 30.0  # nominal cadence 1131 -> 1201 (blocks 133480640 -> 133484778)

def rate(delta):
    return round(delta / INTERVAL_MIN, 4) if delta is not None else None

updated = []
for name, item in r["reads"].items():
    v = item.get("views", {})
    c = s["contracts"].get(name)
    if c is None:
        continue
    # supply key: prefer the key the snapshot entry already tracks
    sup_key = None
    for k in ("totalSupply", "totalMinted", "totalSnippets"):
        if k in v and v[k] is not None and k in c:
            sup_key = k
            break
    if sup_key is None:
        for k in ("totalSupply", "totalMinted", "totalSnippets"):
            if k in v and v[k] is not None:
                sup_key = k
                break
    prev = c.get(sup_key) if sup_key else None
    cur = v.get(sup_key) if sup_key else None
    delta = None if (prev is None or cur is None) else cur - prev
    prev_rate = c.get("currentRatePerMin")
    cur_rate = rate(delta)
    if sup_key and cur is not None:
        c["previousTotalSupply"] = prev
        c[sup_key] = cur
    if delta is not None:
        c["mintedInInterval"] = delta
        c["intervalMinutes"] = INTERVAL_MIN
        c["previousRatePerMin"] = prev_rate
        c["currentRatePerMin"] = cur_rate
        ratio = None
        if prev_rate and prev_rate > 0 and cur_rate is not None:
            ratio = round(cur_rate / prev_rate, 2)
        c["velocityRatio"] = ratio
        c["velocityLegPasses"] = bool(delta >= 20 and ratio is not None and ratio >= 1.5)
    # free counter refresh where the reread has one
    if v.get("freeClaimed") is not None:
        c["freeClaimed"] = v["freeClaimed"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-14 ~12:01 WIB"
    note = (f"Run 1201 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1131): "
            f"{sup_key} {prev}->{cur} (d={delta}, rate {cur_rate}/mnt, ratio {c.get('velocityRatio')}) -> "
            f"velocity {'LOLOS' if c.get('velocityLegPasses') else 'GAGAL'}; "
            f"free={v.get('freeClaimed')}/{c.get('FREE_SUPPLY')}; DIAM.")
    c["runNote1201_1114"] = note
    updated.append(name)

# --- new contracts from Boltbook ---
s["contracts"]["REOPIR"] = {
    "address": "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
    "name": "Reorg Pirates", "symbol": "REOPIR", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-14",
    "totalSupply": 378, "freeClaimed": 378, "FREE_SUPPLY": 7000, "MAX_SUPPLY": 7777,
    "freePctVerified": round(378 / 7000 * 100, 1),
    "mintOpen": 1, "userMintedBy": 0, "userFreeUsed": 0,
    "website": "https://reorg-pirates.668823.xyz",
    "websiteVerified": True,
    "websiteEvidence": "contractURI external_link + tokenURI external_url + ABI externalUrl() all point to https://reorg-pirates.668823.xyz; site prints exact contract (JSON-LD + footer + llms.txt + collection.json); llms.txt: free rule first 3 mints free per wallet while 7,000-token pool lasts, max supply 7777, price 0.00005 BNB.",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "Launch time UNVERIFIED (no project-stated launch time; first-mint log unavailable, Ankr 401). Earliest dated evidence: Boltbook post /p/W92QXxnrJ3Yn 07:06:37 WIB 14 Nov (129 minted) + hot-leg 0704 on-chain 133 totalSupply; run ini 378 totalSupply blok 133484795. Age likely <24h but UNVERIFIED.",
    "baselineNote": "EARLY lead reported once run 1201 (triage deferred by hot-leg 0704 to main job). Agent-mint-shaped: Sourcify verified ABI (39 fns) with mint + freeClaimed/freeFor/freeLeft/freeUsed + FREE_SUPPLY constant; NO Agent ID registry/AgentGate reference in ABI; free rule per-wallet, Boltbook post hints ungated lane. Narrative Agent-ID UNVERIFIED; X account UNVERIFIED (Boltbook post by cst.ai is the discussion evidence). Never auto-minted/previewed. Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety.",
    "firstSeenBlock": 133484795,
    "lastReadBlock": 133484795,
    "lastReadWib": "2026-11-14 ~12:01 WIB",
    "supplyView": "totalSupply",
    "runNote1201_1114": "Run 1201: EARLY LEAD dilaporkan sekali. totalSupply=freeClaimed=378/7000 (5,4% verified), mintOpen 1, mintedBy(user)=0, freeUsed(user)=0 (slot terbuka; priceFor/quote revert). Website TERVERIFIKASI. Umur UNVERIFIED. DIAM sesudah laporan.",
}
s["contracts"]["FrieAgent-B751"] = {
    "address": "0xb7517e3b31107695f2f8837fafc76999b956c871",
    "name": "Frie Agent", "symbol": "FRIEAGENT", "kind": "ERC721",
    "status": "watchlist-only-2026-11-14",
    "totalSupply": 9901, "totalMinted": 9901, "MAX_SUPPLY": 10000,
    "freeClaimed": None, "FREE_SUPPLY": None,
    "mintOpen": None, "userMintedBy": 0, "userBalance": 0,
    "website": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch time UNVERIFIED; only dated evidence: monitor first detection 2026-11-12 01:50 (~58h before run 1204) -> points to age >=24h (age-excluded if confirmed). First-mint log unavailable (Ankr 401; eth_getLogs rate-limited).",
    "baselineNote": "Watchlist-only, BUKAN lead (hot-leg 1204 investigation + probe run 1201): totalSupply 9901/10000 = 99,0% TOTAL matches Boltbook post (tungquan42.ai recheck 12:03, 9.901/10.001 free 99,0%) BUT no free counter on-chain (freeClaimed/freeMinted/FREE_SUPPLY/FREE_SLOTS/freeRemaining all no-return) -> free% UNVERIFIED; Sourcify NOT verified (no ABI); tokenURI ipfs://agent-id/quar-4965/N metadata unreachable; website gate FAILS (no site found via A/G/I). NEVER preview/mint. Same name/tokenURI as FrieAgent-c64d (different contract + owner) - possibly two deployments/batches.",
    "firstSeenBlock": 133484794,
    "lastReadBlock": 133484794,
    "lastReadWib": "2026-11-14 ~12:01 WIB",
    "supplyView": "totalSupply",
    "runNote1201_1114": "Run 1201: baru di snapshot sebagai watchlist-only (BUKAN early lead, BUKAN lead, TIDAK dilaporkan). DIAM.",
}
s["contracts"]["FrieAgent-c64d"] = {
    "address": "0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5",
    "name": "Frie Agent", "symbol": "FRIEAGENT", "kind": "ERC721",
    "status": "watchlist-only-2026-11-14",
    "totalSupply": 4901, "totalMinted": 4901,
    "freeClaimed": None, "FREE_SUPPLY": None,
    "mintOpen": None, "userMintedBy": 0, "userBalance": 0,
    "website": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch time UNVERIFIED (no project-stated launch time; first-mint log unavailable, Ankr 401). Boltbook post tetternice.ai recheck 11:59 claims 4.901/5.001 free (98,0%).",
    "baselineNote": "Watchlist-only, BUKAN lead (probe run 1201): totalSupply 4901 matches post count BUT no free counter on-chain (freeClaimed/freeMinted/FREE_SUPPLY all no-return) -> free% UNVERIFIED; Sourcify NOT verified (per post + ABI fetch); tokenURI ipfs://agent-id/quar-4965/1; website not found. NEVER preview/mint. Same name/tokenURI as FrieAgent-B751 (different contract + owner).",
    "firstSeenBlock": 133484795,
    "lastReadBlock": 133484795,
    "lastReadWib": "2026-11-14 ~12:01 WIB",
    "supplyView": "totalSupply",
    "runNote1201_1114": "Run 1201: baru di snapshot sebagai watchlist-only (BUKAN early lead, BUKAN lead, TIDAK dilaporkan). DIAM.",
}
s["contracts"]["OTV"] = {
    "address": "0xfab9c88d25e111edd68a2cca3e0f650863a5bf25",
    "name": "OTV", "symbol": "OTV", "kind": "ERC721",
    "status": "watchlist-only-free-pool-exhausted-2026-11-14",
    "totalSupply": 577, "MAX_SUPPLY": 1500, "FREE_MINT_CAP": 500,
    "freeClaimed": None, "FREE_SUPPLY": None,
    "freeMintsLeft": 0,
    "mintOpen": None, "userMintedBy": None, "userBalance": 0,
    "website": None, "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch time UNVERIFIED. Boltbook post tale.ai: totalSupply 577/1500, +1 minted in 10790 min (very slow).",
    "baselineNote": "Watchlist-only, BUKAN lead (probe run 1201): Sourcify verified ABI (35 fns) with mint + freeMintsClaimed/freeMintsLeft/freeMintsRemaining/freeMintsUsed + FREE_MINT_CAP 500 + PRICE 0.0012 BNB; NO Agent ID registry/AgentGate ref. freeMintsLeft()=0 -> free pool EXHAUSTED; totalSupply 577/1500 = 38,5% total, minting ~0. Slow. NEVER preview/mint.",
    "firstSeenBlock": 133484794,
    "lastReadBlock": 133484794,
    "lastReadWib": "2026-11-14 ~12:01 WIB",
    "supplyView": "totalSupply",
    "runNote1201_1114": "Run 1201: baru di snapshot sebagai watchlist-only, free pool habis (freeMintsLeft=0). TIDAK dilaporkan. DIAM.",
}

# --- track_c ORBIT ---
orb = s.get("track_c", {}).get("ORBIT")
if orb is not None:
    orb["previousFreeClaimed"] = orb.get("freeClaimed")
    orb["freeClaimed"] = 142
    orb["freeRemaining"] = 888 - 142
    orb["lastReadWib"] = "2026-11-14 ~12:01 WIB"
    orb["runNote1201_1114"] = ("Run 1201 (blok 133484778): freeClaimed 119->142/888 (16,0%), claimOpen 1, "
                                "hasFreeClaimed(user)=0, +23 dalam ~30 mnt; umur UNVERIFIED -> tetap watchlist-only, "
                                "BUKAN lead, TIDAK preview/mint. DIAM.")

# --- pending claim binanceai.fun ---
pc = s.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["lastReadWib"] = "2026-11-14 ~12:01 WIB"
    pc["runNote1201_1114"] = ("Run 1201 (blok 133484778): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). DIAM.")

with open(BASE + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(s, f, indent=1)
shutil.move(BASE + "onchain-snapshot.json.tmp", BASE + "onchain-snapshot.json")
print("updated contracts:", len(updated))
print("contracts total:", len(s["contracts"]))
print("new:", ["REOPIR", "FrieAgent-B751", "FrieAgent-c64d", "OTV"])
