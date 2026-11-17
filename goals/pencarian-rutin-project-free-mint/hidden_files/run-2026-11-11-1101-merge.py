#!/usr/bin/env python3
"""Merge run 1101 (scheduled 2026-11-11 11:01 WIB) results into onchain-snapshot.json.
Writes snapshot (with .bak). Inputs: run-2026-11-11-1101-reread.json (block
132901015, 59 contracts + 22 track_c), run-2026-11-11-1101-legs.json (feed +
Boltbook + bridge + binanceai), run-2026-11-11-1101-preflight.log (Ankr 401),
hot-leg 1054 values (Bot Fighters 17, ABYSSCABLE 760, Stampooor freeMinted 572).
"""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1101-reread.json"))
legs = json.load(open(BASE + "run-2026-11-11-1101-legs.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1101-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 11:01 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict):
        return None
    old = e.get("totalSupply")
    if old is None or new_supply is None:
        return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = None
    if prev_rate and prev_rate > 0:
        ratio = round(rate / prev_rate, 2)
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

# --- 1. reread updates (generic) ---
for name, d in reread["reread"].items():
    if name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        e["runNote1101"] = ("Run 1101 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        old = e.get("totalSupply")
        if old is None:
            e["totalSupply"] = ns
            e["lastReadBlock"] = BLOCK
            e["lastReadWib"] = TS
            e["runNote1101"] = ("Run 1101 (blok %s): totalSupply pertama terbaca %s (sebelumnya None) - "
                                "baseline dicatat, velocity belum lulus; freeMinted=%s; bal_user=%s; status %s."
                                % (BLOCK, ns, d.get("freeMinted"), d.get("balanceOf_user"), e.get("status")))
        else:
            r = vel(name, ns)
            diff, rate, ratio = r if r else (None, None, None)
            e["runNote1101"] = ("Run 1101 (blok %s): totalSupply %s->%s (+%s, %s/mnt vs prev %s = %sx) -> velocity %s; "
                                "bal_user=%s; freeMinted=%s; status %s."
                                % (BLOCK, e.get("previousTotalSupply"), ns, diff, rate,
                                   e.get("previousRatePerMin"), ratio,
                                   "LOLOS" if e.get("velocityLegPasses") else "GAGAL",
                                   d.get("balanceOf_user"), d.get("freeMinted"), e.get("status")))
    if d.get("freeClaimed") is not None:
        e["freeClaimed"] = d["freeClaimed"]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None:
        e["MAX_SUPPLY"] = d["MAX_SUPPLY"]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS

# --- 2. Stampooor: 534->577 (+43), velocity GAGAL (1.43/mnt vs prev 1.33 = 1.08x) ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": 577, "totalSupply": 577, "freeMinted": 572,
               "freeAvailable_user": 1, "lastReadBlock": BLOCK, "lastReadWib": TS})
    st["runNote1101"] = ("Run 1101: totalSupply 534->577 (+43, 1,43/mnt vs prev 1,33 = 1,08x) -> velocity GAGAL. "
        "Free 572/1200 = 47,7% (freeMinted 572 per hot leg 1054 blok 132900742; baca LEAN run ini freeClaimed=None) "
        "- di bawah 50% kandidat DAN di bawah 70% strong lead. Slot user TERBUKA (balanceOf 0). Umur "
        "TERVERIFIKASI <24 jam (mintStart 11 Nov ~09:00 WIB). X + website UNVERIFIED. Tetap EARLY. "
        "TIDAK di-preview/di-mint.")

# --- 3. Jade Vault 0x7Eb9: 374->398 (+24) velocity GAGAL (0.80/mnt vs prev 1.30 = 0.62x) ---
jv = C.get("0x7Eb9")
if isinstance(jv, dict):
    jv.update({"totalMinted": 398, "totalSupply": 398, "lastReadBlock": BLOCK, "lastReadWib": TS})
    jv["runNote1101"] = ("Run 1101: totalMinted 374->398 (+24, 0,80/mnt vs prev 1,30 = 0,62x) -> velocity GAGAL. "
        "Tetap EARLY: free% UNVERIFIED (template tanpa free counter - % total supply 398/8888 TIDAK "
        "disubstitusi), umur + website + X UNVERIFIED. TIDAK di-preview/di-mint.")

# --- 4. NIGHTFORGE: 740 flat, velocity GAGAL; ~36,9% ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    nf.update({"totalSupply": 740, "freePctVerified": 36.9,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    nf["runNote1101"] = ("Run 1101: totalSupply 740 flat vs run 1031 (740, +0) -> velocity GAGAL; "
        "agentFreeUsed ~737/2000 = 36,9% (jauh di bawah ambang strong lead >70% per amandemen 11 Nov 09:18 WIB). "
        "Slot terbuka (balanceOf 0). Deadline umur 14:37 WIB 11 Nov belum lewat - TAPI per amandemen >70%, "
        "NIGHTFORGE BUKAN strong lead jadi deadline recheck gate moot untuk jalur strong lead. Tetap "
        "watchlist-only. TIDAK di-preview/di-mint.")

# --- 5. AgentPals: 76->77 (+1), 77/300 = 25,7% ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap.update({"totalSupply": 77, "freeMinted": 77, "totalMinted": 77,
               "status": "watchlist-only-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    ap["runNote1101"] = ("Run 1101: totalSupply 76->77 (+1). Free phase LIVE sejak 11 Nov 06:33:57 WIB; "
        "77/300 = 25,7% (<50% kandidat, <70% strong lead). Slot user terbuka (balanceOf 0). Website UNVERIFIED. "
        "Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 6. Bot Fighters: update dari hot-leg 1054 (17/500) - job ini tidak re-read BOTF run ini ---
bf = C.get("Bot Fighters")
if isinstance(bf, dict):
    bf.update({"totalSupply": 17, "totalMinted": 17, "freeMinted": 17,
               "lastReadBlock": 132900742, "lastReadWib": "2026-11-11 10:54 WIB (hot leg)"})
    bf["runNote1101"] = ("Run 1101: Bot Fighters 12->17/500 (3,4%) per hot-leg 1054 (blok 132900742) - job utama "
        "tidak re-read BOTF run ini (di luar daftar PRIO; hot leg melacak tiap 5 mnt). Slot user TERBUKA, umur "
        "MASIH UNVERIFIED (first-mint milik scan leg job utama; Ankr 401). Tetap watchlist-only-age-unverified. "
        "TIDAK di-preview/di-mint.")

# --- 7. ABYSSCABLE: update dari hot-leg 1054 (760) ---
ab = C.get("ABYSSCABLE")
if isinstance(ab, dict):
    ab.update({"totalSupply": 760, "agentFreeUsed": 760, "freePct": 38.0,
               "lastReadBlock": 132900742, "lastReadWib": "2026-11-11 10:54 WIB (hot leg)"})
    ab["runNote1101"] = ("Run 1101: ABYSSCABLE 758->760/2000 (38,0%) per hot-leg 1054 (blok 132900742). Umur "
        "TERVERIFIKASI <24 jam (mintStart 10 Nov ~19:38 WIB; deadline ~19:39 WIB 11 Nov). Website UNVERIFIED. "
        "Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 8. track_c updates from reread (non-None only) ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict):
        continue
    e = TC[name]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    if name == "11-11":
        e["runNote1101"] = "Run 1101: freeMinted 612->614 (+2 vs run 1031); tetap watchlist-only-age-website-unverified."

# --- 9. Bridge: 6 kontrak baru di snapshot (temuan pelengkap scan, BUKAN lead baru job ini) ---
bridge = json.load(open(BASE + "scan-bridge.json"))["contracts"]
NAMES = {
    "0x7b48474d25431dfad4337735a0a2e57b63573abb": "Ore (ORE)",
    "0x53ba295180ae4b730f9b2a031f77c1bcdb009509": "ETHBack Dividend Tracker",
    "0x76437a85b768bb5612e8a466e492d89d8ef634b1": "Ikigai (IKIGAI)",
    "0x63dea5acdbe1f27c968907d08610a5f0a0284ba6": "Agentic Coin (AGC)",
    "0x0aa11f327313682cdf072affff26d0dffc804483": "Krillfarm (KRILL)",
    "0x493d51ca30c99ab3f40e3d713290ef70a6582486": "Panda Emoji Pack (PANBA)",
}
SHAPE = {
    "0x76437a85b768bb5612e8a466e492d89d8ef634b1": "Sourcify ABI 14 fns: mint ada, quote TIDAK, free views TIDAK, agent ref TIDAK -> BUKAN sale-shape S1/S2.",
    "0x493d51ca30c99ab3f40e3d713290ef70a6582486": "Sourcify ABI 34 fns: mint ada, quote TIDAK, free views TIDAK, agent ref TIDAK -> BUKAN sale-shape S1/S2.",
    "0x63dea5acdbe1f27c968907d08610a5f0a0284ba6": "Sourcify ABI 37 fns: mint ada, quote TIDAK, free views TIDAK, agent ref TIDAK -> BUKAN sale-shape S1/S2. Token AGC yang sudah dikenal (Modal Bacot), BUKAN lead Free Bacot.",
}
for addr in legs["bridge"]["not_in_snapshot"]:
    key = "bridge-" + addr.lower()[:10]
    b = bridge.get(addr, {})
    disc = bool(b.get("same_owner_discarded"))
    C[key] = {
        "address": addr,
        "name": NAMES.get(addr.lower()),
        "kind": "bridge-scan-finding",
        "status": "same-owner-discarded-never-promote-2026-11-11" if disc else "watchlist-only-scan-bridge-2026-11-11",
        "source": "scan-bridge (temuan pelengkap scan, sudah dilaporkan job scan; BUKAN lead baru job ini)",
        "totalSupply": None, "freeClaimed": None, "FREE_SUPPLY": None, "freeMinted": None,
        "userMintedBy": None, "userFreeUsed": None, "userBalance": 0,
        "sameOwnerDiscarded": disc,
        "note": (b.get("note", "")[:300] + " | " + SHAPE.get(addr.lower(), ""))[:600],
        "lastReadBlock": BLOCK, "lastReadWib": TS,
        "velocityVerified": False, "mintedInInterval": None, "intervalMinutes": None,
        "currentRatePerMin": None, "previousRatePerMin": None, "velocityLegPasses": False,
        "velocityRatio": None,
        "runNote1101": ("Run 1101: BARU dicatat dari scan-bridge.json (temuan pelengkap scan; bridge mtime "
            "2026-11-08 18:21 WIB, STALE - 6 kontrak ini terlewat perbandingan run-run sebelumnya). "
            + ("PAID mint (bukan gratis) -> BUKAN Free Bacot. " if addr.lower() in (
                "0x7b48474d25431dfad4337735a0a2e57b63573abb", "0x53ba295180ae4b730f9b2a031f77c1bcdb009509") else "")
            + ("SAME-OWNER-DISCARDED -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. " if disc else "")
            + SHAPE.get(addr.lower(), "")
            + " TIDAK dilaporkan ke chat (bukan lead/kandidat)."),
    }
    print("ADDED bridge entry:", key, addr, "discarded" if disc else "")

# --- 10. top-level run notes ---
snap["last_run_wib"] = TS
snap["timestamp_wib"] = TS
snap["last_run_note"] = ("Run 1101: 0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead baru / 0 early lead "
    "baru dilapor. BARU dicatat watchlist-only (TIDAK dilaporkan): 6 temuan pelengkap scan dari bridge "
    "(Ore + ETHBack PAID, Ikigai + PANBA + AGC bukan sale-shape, Krillfarm same-owner-discarded). Stampooor "
    "534->577 (47,7%, velocity GAGAL, tetap EARLY); Jade Vault 374->398 (velocity GAGAL, tetap EARLY); "
    "NIGHTFORGE 740 flat (36,9%, tetap watchlist-only <70%); AgentPals 77/300 = 25,7%; Bot Fighters 17/500 "
    "(umur unverified); ABYSSCABLE 760/2000 (38,0%). Feed Sourcify 20 kontrak: 0 baru (2 abi-timeout lama "
    "tetap tanpa ABI). Boltbook EN+ZH via curl OK, 0 alamat baru. Scan FAST-FAIL (pre-flight Ankr 401). "
    "binanceai launched=0 (refund phase).")
snap["runNote1101"] = snap["last_run_note"]
snap["runNote1101_scan"] = ("Scan run 1101 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized "
    "(head ~132901015 via RPC publik, blok reread). Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0% "
    "s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~388.450 blok dan tumbuh; "
    "backfill OFF - run backfill terakhir 10:16 WIB juga 401). Track-C 5c dilewati run ini (tidak ada output "
    "scan baru).")
snap["runNote1101_binanceai"] = ("Run 1101: launched()=0 (blok %s) - TIDAK BERUBAH (refund phase, sudah dilaporkan "
    "sekali). pending_claims: binanceai.fun tetap pending, TIDAK di-preview/diklaim." % BLOCK)
snap["runNote1101_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah sejak run 1001), "
    "116 kontrak, 7 same_owner_discarded; 6 kontrak di luar snapshot yang terlewat perbandingan run-run "
    "sebelumnya, BARU dicatat run ini sebagai bridge-scan-finding (watchlist-only, BUKAN lead): Ore 0x7b48 "
    "(PAID 0,03 BNB), ETHBack 0x53ba (PAID 0,01 BNB), Ikigai 0x7643 (ERC20, bukan sale-shape), AGC 0x63de "
    "(token AGC dikenal, bukan sale-shape), Krillfarm 0x0aa1 (same-owner-discarded, TIDAK PERNAH promosi), "
    "PANBA 0x493d (ERC20 via pack sale, bukan sale-shape). Koreksi: klaim run 1031 '0 temuan pelengkap baru' "
    "tidak tepat - 6 ini memang belum ada di snapshot.")
snap["runNote1101_discovery"] = ("Discovery run 1101: Sourcify feed 20 kontrak (verified 03:05-03:57Z): 0 baru vs "
    "hot-leg-seen + feed 1031; shape-check 2 abi-timeout lama (0xddf252ad, 0x5273f49b) tetap no-abi-in-response "
    "-> retry run berikut; S1=0 S2=0 EARLY=0. Boltbook EN 45.175 byte + ZH 45.083 byte via curl (urllib gagal "
    "IncompleteRead; hot leg EN 0-byte 2x berturut-turut): 9 + 8 alamat, 0 baru (semua sudah di snapshot / "
    "hot-leg-seen: Onyx Agent, Hippo Social Club, ROSE Pixel Relay, BOLT, Stampooor). Sweep EN+ZH: 0 proyek "
    "baru - Agentic Gangster (free-pool-exhausted, sudah tercatat), First-Dollar Grove (age-excluded, sudah "
    "tercatat), WNO (track_c, minted-by-user), Golden Agents (age-excluded, sudah tercatat), Laser Agents / "
    "Pixel Fox / AGENT MAO (lama/dikenal), Agent Operators (upcoming 15 Nov, tanpa kontrak). Leg 6: Odaily "
    "newsflash + PANews front page dibaca run ini - 0 item Agent ID/free-mint.")
snap["runNote1101_age_exclusions"] = ("Run 1101: 0 age-exclusion BARU. Deadline berjalan: NIGHTFORGE 14:37 WIB 11 Nov "
    "(mintStart 10 Nov 14:37 WIB; 36,9% - watchlist-only; per amandemen >70% deadline recheck gate moot untuk "
    "jalur strong lead); AgentPals ~06:33 WIB 12 Nov; MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. "
    "Bot Fighters: umur UNVERIFIED (bukan age-excluded) - watchlist-only. Fira Agent: pertama terlihat 9 Nov "
    "21:26 WIB (diduga >24 jam) tapi launch time tidak terverifikasi ke standar exclusion - tetap "
    "watchlist-only-age-unverified, bukan age-excluded. STALL / Cosmic Sentinel / Dragon Agent: umur "
    "UNVERIFIED - watchlist-only, bukan age-exclusion.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE. contracts:", len(C), "track_c:", len(TC))
