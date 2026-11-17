#!/usr/bin/env python3
"""Merge run 2026-11-10 10:01 WIB into onchain-snapshot.json. CLEAN merge:
data-driven only — no hardcoded per-contract values from earlier runs.
- Generic reread merge (same view-aware velocity logic as 0901/0931 merges).
- INTERVAL computed from block timestamps (prev block 132698471 ts 1794278643
  -> reread block ts via eth_getBlockByNumber, retries; fallback 51.0 noted).
- Adds new discoveries verified this run: Iron Bloom, Orbit Lantern (watchlist-only,
  website VERIFIED, age/free% UNVERIFIED), HELM (sold out), hotleg1024-A/B
  (watchlist-only, all views None — retry next run).
- Run notes written ONLY from this run's actual evidence (preflight, feed-shape,
  special2, newdisc, discovery). No prio6 this run.
Backup first; writes snapshot atomically."""
import json, shutil, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{snap_path}.bak-1001-premerge")
snap = json.load(open(snap_path))
rr = json.load(open(f"{BASE}/run-2026-11-10-1001-reread.json"))
BLOCK = rr["block"]
TS_WIB = "2026-11-10 10:01 WIB"
PREV_TS = 1794278643  # block 132698471 (run 0931 read)

def block_ts(num):
    for ep in ["https://bsc-dataseed1.bnbchain.org/",
               "https://bsc-dataseed2.bnbchain.org/",
               "https://bsc-dataseed.binance.org/"]:
        try:
            out = subprocess.run(
                ["curl", "-sL", "--max-time", "20", "-X", "POST", ep,
                 "-H", "Content-Type: application/json",
                 "-d", json.dumps({"jsonrpc": "2.0", "id": 1,
                                   "method": "eth_getBlockByNumber",
                                   "params": [hex(num), False]})],
                capture_output=True, text=True, timeout=25).stdout
            r = json.loads(out).get("result", {})
            if r.get("timestamp"):
                return int(r["timestamp"], 16)
        except Exception:
            continue
    return None

ts_new = block_ts(BLOCK)
if ts_new:
    INTERVAL = round((ts_new - PREV_TS) / 60, 1)
else:
    INTERVAL = 51.0
print("BLOCK", BLOCK, "ts_new", ts_new, "INTERVAL", INTERVAL, flush=True)

FREE_FIELDS = ["freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY",
               "mintOpen", "balanceOf_user", "freeClaimed_user"]
updated = 0
vel_pass = []
for name, entry in snap["contracts"].items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["reread"].get(name)
    if not fresh:
        continue
    view = "totalMinted" if str(entry.get("supplyView", "")).startswith("totalMinted") else "totalSupply"
    new = fresh.get(view)
    if new is None:
        pass
    else:
        prev = entry.get(view)
        if prev is None:
            entry[view] = new
        else:
            if new <= 10**7 and prev <= 10**7:
                minted = new - prev
                prev_rate = entry.get("currentRatePerMin")
                rate = minted / INTERVAL if INTERVAL > 0 else 0.0
                ratio = (rate / prev_rate) if prev_rate else None
                passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
                if prev > 10_000_000:
                    passes = False
                entry["previousTotalSupply"] = prev
                entry["mintedInInterval"] = minted
                entry["intervalMinutes"] = INTERVAL
                entry["previousRatePerMin"] = prev_rate
                entry["currentRatePerMin"] = rate
                entry["velocityRatio"] = ratio
                entry["velocityLegPasses"] = passes
                if passes:
                    vel_pass.append(name)
            entry[view] = new
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = TS_WIB
        updated += 1
    for f in FREE_FIELDS:
        if fresh.get(f) is not None:
            entry[f] = fresh[f]
    if fresh.get("balanceOf_user") is not None:
        entry["balanceOf_user"] = fresh["balanceOf_user"]
        entry["userBalance"] = fresh["balanceOf_user"]

tc_updated = 0
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    fresh = rr["track_c"].get(name)
    if not fresh:
        continue
    for f in ("freeMinted", "totalSupply", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if fresh.get(f) is not None:
            entry[f] = fresh[f]
            tc_updated += 1
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = TS_WIB

# --- new discoveries verified this run (run-2026-11-10-1001-newdisc.json) ---
nd = json.load(open(f"{BASE}/run-2026-11-10-1001-newdisc.json"))
BLK_ND = nd["block"]
IB = nd["reads"]["Iron Bloom"]
# Orbit Lantern was read by a focused eth_call batch (same run, ~10:55 WIB, between
# newdisc block 132706216 and special2 block 132707816); values below are that read's
# verbatim output — it was not part of newdisc.json's TARGETS.
OL = {"totalSupply": 625, "MAX_SUPPLY": 794, "mintOpen": 1, "balanceOf_user": 0}
snap["contracts"]["Iron Bloom"] = {
    "address": "0xb8c7658f6fc4d0d91da2dd6faeaf0328ff57ccaf",
    "name": "Iron Bloom", "symbol": "ME01", "kind": "ERC721",
    "status": "watchlist-only-2026-11-10",
    "totalSupply": IB.get("totalSupply"), "MAX_SUPPLY": IB.get("MAX_SUPPLY"),
    "mintOpen": IB.get("mintOpen"), "balanceOf_user": IB.get("balanceOf_user"),
    "freeClaimed": IB.get("freeClaimed"), "freeMinted": IB.get("freeMinted"),
    "FREE_SUPPLY": IB.get("FREE_SUPPLY"),
    "costOf_user_1": 0, "price": 200000000000000, "mintedBy_user": 0,
    "mintsLeft_user": 10, "MAX_PER_WALLET": 10,
    "agentIds": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "agentShaped": True,
    "website": "https://agent-mecha-002-iron-bloom.pages.dev/",
    "websiteVerified": True,
    "websiteEvidence": ("VERIFIED run 1001 methods I/H/G: tokenURI(1) = "
        "https://agent-mecha-002-iron-bloom.pages.dev/meta/1.json (external_url = site root); "
        "/llms.txt prints 'Contract: 0xB8C7658f6Fc4D0d91dA2Dd6FAEAF0328FF57CCaf' + 'first mint is free'; "
        "/agent.json prints contract + supply 786 + price 0.0002 BNB + freeRule first-mint. "
        "Method A (raw contract-address search): 0 relevant hits. Method C (Sourcify metadata): no URLs. "
        "Method H contractURI(): None. Site root itself is a JS SPA (no contract in fetched text) — "
        "evidence rests on /llms.txt + /agent.json per strict print standard (SEVENFOLD precedent)."),
    "xVerified": False,
    "launchNote": ("Age UNVERIFIED: no stated launch time in /llms.txt or /agent.json; first-mint time "
        "unknown — Ankr getLogs 401 (outage since 2026-11-09 ~13:33 WIB), public RPC eth_getLogs -32005. "
        "Boltbook post 2026-11-09 ~18:05 WIB already read 345/786 (launch before then, upper bound only). "
        "Sourcify verifiedAt 2026-11-09T06:49:20Z is verification time, NOT launch time."),
    "freePctNote": ("Free% UNVERIFIED: no free counter on contract (no freeClaimed/freeMinted views); "
        "free rule is per-wallet first-mint (devdoc + llms.txt + agent.json: requiresGlobalFreePool=false); "
        "totalSupply 715/786 = 91.0% mixes free + paid mints and must NOT substitute for free-quota %."),
    "freeSlotUserOpen": True,
    "velocityVerified": False,
    "velocityNote": "No baseline yet (first read run 1001, blok %s)." % BLK_ND,
    "lastReadBlock": BLK_ND, "lastReadWib": TS_WIB,
    "supplyView": "totalSupply",
    "discardsChecked": True,
    "baselineNote": ("Discovery run 1001 via Boltbook EN front page (post ~18:05 WIB 2026-11-09) + hot-leg-seen "
        "(Sourcify feed 2026-11-09 14:01 WIB, checked-not-sale-shape). Agent-shaped + free slot open + "
        "website VERIFIED, but age UNVERIFIED + free% UNVERIFIED + no velocity baseline -> watchlist-only, "
        "BUKAN early lead (first mints not verified on-chain this run), BUKAN strong lead, BUKAN kandidat. "
        "Not in same-owner-discards. Next run: verify first-mint time when Ankr recovers; likely sells out soon (71 left)."),
    "runNote1001_1110": ("Run 1001: totalSupply 715/786 (91,0%), mintOpen=1, costOf(user,1)=0, price 0,0002 BNB, "
        "mintedBy(user)=0, balanceOf(user)=0, agentIds()=registry resmi. Website TERVERIFIKASI (llms.txt + "
        "agent.json). Umur UNVERIFIED + free% UNVERIFIED -> watchlist-only. TIDAK preview/mint."),
}
snap["contracts"]["Orbit Lantern"] = {
    "address": "0x83B653aab5cAEa240DAcf722f8fa90E479849b5E",
    "name": "Orbit Lantern", "symbol": "CO01", "kind": "ERC721",
    "status": "watchlist-only-2026-11-10",
    "totalSupply": 625, "MAX_SUPPLY": 794,
    "mintOpen": 1, "balanceOf_user": 0,
    "costOf_user_1": 0, "price": 150000000000000, "mintedBy_user": 0,
    "agentIds": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "agentShaped": True,
    "website": "https://agent-cosmic-003-orbit-lantern.pages.dev/",
    "websiteVerified": True,
    "websiteEvidence": ("VERIFIED run 1001 method G: linked from Iron Bloom /llms.txt as next in Agent Mint Network "
        "(position 3 of 10); own /llms.txt prints 'Contract: 0x83B653aab5cAEa240DAcf722f8fa90E479849b5E' + "
        "'first mint is free'. Same template as Iron Bloom (first-mint free, no global free pool)."),
    "xVerified": False,
    "launchNote": ("Age UNVERIFIED: no stated launch time found; no Boltbook post found; first-mint time unknown "
        "(Ankr getLogs 401; public RPC eth_getLogs -32005)."),
    "freePctNote": ("Free% UNVERIFIED: no free counter; per-wallet first-mint rule, no global free pool; "
        "totalSupply 625/794 = 78,7% mixes free + paid mints, must NOT substitute for free-quota %."),
    "freeSlotUserOpen": True,
    "velocityVerified": False,
    "velocityNote": "No baseline yet (first read run 1001).",
    "lastReadBlock": BLK_ND, "lastReadWib": TS_WIB,
    "supplyView": "totalSupply",
    "discardsChecked": True,
    "baselineNote": ("Discovery run 1001 via Agent Mint Network hop (Iron Bloom llms.txt -> next collection). "
        "Agent-shaped + free slot open + website VERIFIED, but age UNVERIFIED + free% UNVERIFIED + no velocity "
        "baseline -> watchlist-only, BUKAN early lead, BUKAN strong lead, BUKAN kandidat. Not in "
        "same-owner-discards. Next run: verify first-mint time when Ankr recovers."),
    "runNote1001_1110": ("Run 1001: totalSupply 625/794 (78,7%), mintOpen=1, costOf(user,1)=0, price 0,00015 BNB, "
        "mintedBy(user)=0, balanceOf(user)=0, agentIds()=registry resmi. Website TERVERIFIKASI (llms.txt). "
        "Umur UNVERIFIED + free% UNVERIFIED -> watchlist-only. TIDAK preview/mint."),
}
snap["contracts"]["HELM"] = {
    "address": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
    "name": "helm.ai", "symbol": "HELM", "kind": "ERC721",
    "status": "sold-out-free-2026-11-10",
    "totalSupply": 555, "MAX_SUPPLY": 555,
    "mintOpen": 1, "balanceOf_user": 0,
    "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
    "lastReadBlock": BLK_ND, "lastReadWib": TS_WIB,
    "supplyView": "totalSupply",
    "baselineNote": ("Discovery run 1001 via Boltbook ZH front page (post ~22:07 WIB 2026-11-09: 542/555). "
        "Fresh read run 1001: totalSupply 555/555 = sold out before first snapshot entry. Excluded as "
        "sold out; never reported as lead. Not in same-owner-discards."),
    "runNote1001_1110": "Run 1001: totalSupply 555/555 — SOLD OUT. Tidak masuk watchlist aktif.",
}
for key, addr in [("hotleg1024-A", "0x60f7212010600bcbebbfe2a558237004c7f401fd"),
                  ("hotleg1024-B", "0xbf87e6fe445e235699103df56ef8d40a88b9e8ba")]:
    snap["contracts"][key] = {
        "address": addr, "kind": "unknown", "status": "watchlist-only-2026-11-10",
        "totalSupply": None, "freeClaimed": None, "freeMinted": None,
        "lastReadBlock": BLK_ND, "lastReadWib": TS_WIB,
        "baselineNote": ("Discovery run 1001 via hot-leg 1024 leg2 (Boltbook EN+ZH live reads, new addrs). "
            "All on-chain views None this run (not ERC-721 LEAN views or read failed); Sourcify ABI "
            "unavailable (A: timeout; B: 404 unverified). Unverified — retry next run. Not in "
            "same-owner-discards."),
        "runNote1001_1110": "Run 1001: semua view None; ABI Sourcify tidak tersedia. Watchlist-only, unverified.",
    }

# --- age-exclusion run 1001: OinkHash Pigs (early lead, first mint verified) ---
# First mint verified on-chain: block 132311872 = 2026-11-08 09:22:34 WIB (Ankr getLogs,
# recorded in launchNote). 48h deadline 2026-11-10 09:22:34 WIB; read run ini blok 132705990
# ts 1794281984 = 10:39:44 WIB -> umur ~49,3 jam. maxSupply 20000 (deep-dive run 1431);
# totalSupply segar 1737 -> BELUM sold out. Dihapus dari watchlist aktif per aturan umur 48 jam.
OINK_KEY = "0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B"
oink = snap["contracts"].pop(OINK_KEY, None)
if oink is not None:
    snap.setdefault("age_exclusions", []).append({
        "name": "OinkHash Pigs",
        "address": "0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B",
        "firstMintWib": "2026-11-08 09:22:34 WIB (blok 132311872, first Transfer-from-zero, Ankr getLogs)",
        "ageHours": 49.3,
        "supply": 1737,
        "maxSupply": 20000,
        "free": "UNVERIFIED (no global free counter; freeClaimed(user)=0, balanceOf(user)=0)",
        "status_before": "early-lead-reported-2026-11-08",
        "removed_run": "2026-11-10 run 1001",
        "removed_wib": "2026-11-10 10:01 WIB",
        "reason": ("Umur peluncuran terverifikasi 49,3 jam (>48 jam; deadline 2026-11-10 09:22:34 WIB) dan "
            "belum sold out (1737/20000); dihapus dari watchlist aktif per aturan umur 48 jam; "
            "dilaporkan sekali run ini. Velocity run ini LOLOS (103 mint, 14,56x) tapi tidak mengubah "
            "keputusan — aturan umur mengalahkan velocity."),
    })
    snap["runNote1001_1110_age_exclusions"] = (
        "Age-exclusion run 1001: OinkHash Pigs 0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B "
        "(early-lead-reported-2026-11-08). First mint terverifikasi 2026-11-08 09:22:34 WIB (blok 132311872); "
        "deadline 48 jam lewat 2026-11-10 09:22:34 WIB; umur saat baca ~49,3 jam; totalSupply segar 1737/20000 "
        "belum sold out. Dihapus dari watchlist aktif; tercatat di age_exclusions; dilaporkan sekali run ini. "
        "Sweep umur run ini (regex first-mint di launchNote/baselineNote): King's Game tetap age-watch "
        "(launch UNVERIFIED — 2026-11-07 21:06 hanya first-seen/lower bound); Compasyn sudah "
        "promotion-discarded. Sweep regex bisa melewatkan timestamp yang terkubur dalam teks — sweep penuh "
        "menjadi tugas run berikut.")

snap["runNote1001_1110_binanceai"] = (
    "Run 1001 track-B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0 (blok 132707816, special2). Status "
    "closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1001_1110_grove"] = (
    "Run 1001 Grove: TIDAK BERUBAH — freeOpen=0, freeMinted=2500/2500, FREE_SUPPLY=2500, "
    "MAX_SUPPLY=12500, freeClaimed(user)=0, balance user=0 (blok 132707816, special2).")
snap["runNote1001_1110_scan"] = (
    "Route 4 scan: FAST-FAIL. Pre-flight ankr_getLogs 50 blok (head 132705988): FAIL 14,1 dtk HTTP 401 "
    "Unauthorized. Kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. Scan leg TIDAK dijalankan; watermark "
    "tetap 132512564; gap ke head ~193.400 blok dan tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1001_1110"] = (
    f"Run 1001 (2026-11-10 10:01 WIB, blok {BLOCK}, interval {INTERVAL} mnt): re-read "
    f"{len(rr['reread'])} kontrak + {len(rr['track_c'])} track_c. Velocity LOLOS (merge): "
    f"{vel_pass if vel_pass else '0'} — tanpa promosi: Rookling sudah age-excluded; OinkHash Pigs "
    "age-excluded run ini (lihat age_exclusions); Rose Genesis umur+free% unverified; BN Agent File "
    "umur+free% unverified + soulbound. "
    "BARU watchlist-only: Iron Bloom 715/786 (website VERIFIED, slot gratis terbuka, umur+free% UNVERIFIED) + "
    "Orbit Lantern 625/794 (website VERIFIED, slot gratis terbuka, umur+free% UNVERIFIED) — keduanya BUKAN "
    "early/strong lead/kandidat, TIDAK preview/mint. HELM sold out 555/555 (tidak masuk watchlist). "
    "hotleg1024-A/B watchlist-only unverified. MWORKS free pool habis (freeMinted 1111/1111, tak berubah — pola "
    "artefak, user sudah pegang 1; tidak dilaporkan). AGE-EXCLUSION BARU 1: OinkHash Pigs (49,3 jam, 1737/20000). "
    "Feed Sourcify 20/20 dicek, 0 S1/S2. Boltbook EN+ZH: Iron "
    "Bloom + HELM + Hivebyte (sudah di snapshot, tanpa perubahan) + MWORKS (sudah di snapshot); EMBER tanpa gate "
    "Agent ID + 7,8% (log saja); Orin Agent tanpa alamat kontrak (log saja). Bridge 116 kontrak, tidak berubah "
    "sejak 2026-11-09 01:21 WIB, 0 promosi. Odaily/PANews 0 hit. Sweep route 3: 0 baru (semua item lama Okt). "
    "Binanceai/Grove tidak berubah. Kandidat baru 0; strong lead baru 0; early lead baru 0; track-C lead/kandidat "
    "baru 0; sellout baru 0. RUN DIAM kecuali laporan age-exclusion OinkHash Pigs (sekali).")
snap["last_run_wib"] = TS_WIB
snap["timestamp_wib"] = TS_WIB

tmp_path = snap_path + ".tmp-1001"
with open(tmp_path, "w") as f:
    json.dump(snap, f, indent=1, ensure_ascii=False)
import os
os.replace(tmp_path, snap_path)
print("merged. contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]),
      "updated reads:", updated, "tc fields:", tc_updated, "vel_pass:", vel_pass)
