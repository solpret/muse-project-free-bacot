#!/usr/bin/env python3
"""Merge run 2026-11-10 09:31 WIB into onchain-snapshot.json. Read-only on
state except the snapshot itself. Backup first. View-aware velocity (same as
0901 merge). Interval 39.9 min (blok 132693151 ts 1794276249 -> 132698471 ts
1794278643). SEVENFOLD website VERIFIED this run (methods H/I/G); free 700/3000
= 23.3% (prio6 fresh read) — still <25%, stays watchlist-only. No promotions,
no new leads, no sellouts, no age-exclusions this run."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{snap_path}.bak-0931-premerge")
snap = json.load(open(snap_path))
rr = json.load(open(f"{BASE}/run-2026-11-10-0931-reread.json"))
BLOCK = rr["block"]
INTERVAL = 39.9
TS_WIB = "2026-11-10 09:31 WIB"

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

def note(name, key, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e[key] = text

# --- prio6 fresh reads (supplement; reread values take precedence where present) ---
prio6 = json.load(open(f"{BASE}/run-2026-11-10-0931-prio6.json"))["reads"]
sev = snap["contracts"].get("SEVENFOLD")
if isinstance(sev, dict):
    # Canonical values come from the reread (block-stamped); prio6 only fills gaps.
    p6 = prio6.get("SEVENFOLD", {})
    if sev.get("freeMinted") is None and p6.get("freeMinted") is not None:
        sev["freeMinted"] = p6["freeMinted"]
    if sev.get("agentFreeUsed") is None and p6.get("agentFreeUsed") is not None:
        sev["agentFreeUsed"] = p6["agentFreeUsed"]
    if sev.get("totalSupply") is None and p6.get("totalSupply") is not None:
        sev["totalSupply"] = p6["totalSupply"]
    fm = sev.get("freeMinted")
    sev["freePctVerified"] = round(fm / 3000 * 100, 2) if isinstance(fm, (int, float)) else None
    sev["website"] = "https://sevenfold-genesis.pages.dev/"
    sev["websiteVerified"] = True
    sev["websiteEvidence"] = ("VERIFIED run 0931 methods H/I/G: contractURI() = "
        "https://sevenfold-genesis.pages.dev/meta/collection.json (external_link = site); "
        "tokenURI(1) = same host; /llms.txt prints 'Contract address: "
        "0x4ca724a354db4f743607ecc1a5f117b2e617c8ae' (exact sale contract); /agent.json prints "
        "contract 0x4ca724a354db4f743607ecc1a5f117b2e617c8ae + token "
        "0x1f4e976b899df67cB4F69BB21aFa0Aee274153Fe (MORROW) + canonicalSite. Front page HTML "
        "itself prints no contract address (JS SPA), but /llms.txt + /agent.json on the same "
        "host do — website evidence per strict print standard. X account still UNVERIFIED "
        "(optional, never blocks).")
    sev["lastReadWib"] = TS_WIB
    note("SEVENFOLD", "runNote0931_1110",
         "Run 0931 (reread blok 132698471 + prio6 cross-check): totalSupply 630->706 (+76), "
         "agentFreeUsed/freeMinted 629->705, free 705/3000 = 23,5% TERVERIFIKASI (naik dari 21,0% run 0901; "
         "prio6 ~10:0x WIB membaca 700/3000 = 23,3%) — MASIH <25% "
         "strong-lead leg. Slot TERBUKA (bal 0). Umur terverifikasi <=48 jam (mintStart 07:33:08 WIB). "
         "WEBSITE TERVERIFIKASI run ini (llms.txt + agent.json mencetak kontrak persis) — gate kini LOLOS, "
         "tinggal kaki 25%. BUKAN strong lead, BUKAN kandidat. TIDAK preview/mint.")
note("FCAT Agents", "runNote0931_1110",
     "Run 0931 (prio6 fresh read ~10:0x WIB): totalSupply 358->385 (+27), freeClaimed 385/888 = 43,4% "
     "TERVERIFIKASI (naik dari 40,3% run 0901). Velocity: rate ~0,6-0,68/mnt vs prev 0,35 = ~1,7-1,9x "
     "dengan >=20 token — velocity LOLOS pada baca prio6 (interval ~40-45 mnt, blok prio6 tidak "
     "tercapture; angka reread kanonik menyusul di merge). Slot TERBUKA (bal 0). Umur UNVERIFIED + "
     "website GATE FAILED (run 0701) — tetap watchlist-only, BUKAN strong lead/kandidat. TIDAK preview/mint.")
note("JINCHAN Agents", "runNote0931_1110",
     "Run 0931: prio6 read GAGAL total (semua view None — degradasi eth_call dataseed); nilai lama "
     "dipertahankan (freeClaimed 214/888 = 24,1% run 0901). Tetap watchlist-only.")
note("Roguefall", "runNote0931_1110",
     "Run 0931 (prio6 fresh read ~10:0x WIB): totalSupply 1022->1052 (+30), freeMinted 1046/2000 = 52,3% "
     "TERVERIFIKASI (naik dari 50,8% run 0901). Velocity GAGAL (~0,67/mnt vs baseline 1,60 = 0,42x). "
     "Slot TERBUKA (bal 0). Umur UNVERIFIED + website GATE FAILED — tetap watchlist-only, BUKAN strong "
     "lead/kandidat. TIDAK preview/mint.")
note("Sakura", "runNote0931_1110",
     "Run 0931 (prio6 fresh read ~10:0x WIB): totalSupply 1263->1288 (+25), freeMinted 1278/6000 = 21,3% "
     "TERVERIFIKASI (naik dari 20,9% run 0901). Velocity GAGAL (~0,55/mnt vs prev 0,54 = ~1,0x). Slot "
     "UNVERIFIED (freeClaimed user revert), website GATE FAILED. Tetap early lead.")
note("THYRK", "runNote0931_1110",
     "Run 0931 (prio6 fresh read ~10:0x WIB): totalSupply 2173->2367 (+194), freeMinted 2319 (tanpa free "
     "cap; % leg N/A). Slot user TERPAKAI (bal 1, mint #6849). Website thyrk.fun TERVERIFIKASI. Umur "
     "presisi UNVERIFIED. Tetap early lead.")
note("MONOLITH", "runNote0931_1110",
     "Run 0931 (blok 132699172, special2): totalSupply 645->651 (+6), velocity GAGAL. Deadline umur "
     "2026-11-10 17:32 WIB belum lewat. Age-watch.")
note("King's Game", "runNote0931_1110",
     "Run 0931 (blok 132699172, special2): totalMinted/freeMinted flat 3, balanceOf(user)=0. Launch "
     "UNVERIFIED — tetap age-watch per preseden. Tanpa perubahan.")
note("Lenx Agent Pass", "runNote0931_1110",
     "Run 0931 (blok 132699172, special2): freeMinted 1000/1000, freeRemaining 0 — tetap sold-out-2026-11-10 "
     "(dilaporkan run 0901).")
note("Night Bandits Club", "runNote0931_1110",
     "Run 0931 (blok 132699172, special2): freeUsed 444/444 — tetap sold-out-2026-11-10 (dilaporkan run 0901).")

tc = snap.get("track_c", {})
if isinstance(tc.get("NUSA"), dict):
    tc["NUSA"]["freeMinted"] = 364
    tc["NUSA"]["runNote0931_1110"] = (
        "Run 0931 (blok 132699172, special2): freeMinted 363->364 (+1); sharesMinted 371; soldOut=0, "
        "closed=0; freeAvailable(user)=1, freeClaimed(user)=0, saldo token user=0. Slot user masih terbuka, "
        "TAPI gate TETAP FAILED -> TIDAK di-preview/TIDAK di-mint. Deadline umur 2026-11-10 17:05 WIB belum lewat.")
if isinstance(tc.get("BOME-50CD"), dict):
    tc["BOME-50CD"]["runNote0931_1110"] = (
        "Run 0931 (blok 132699172, special2): TIDAK BERUBAH — mintOpen=0, opened=0, FREE_CAP=1000, "
        "freeLotsMinted=0 (pool 1000/1000), freeUsed(user)=0. Sale masih belum dibuka.")
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote0931_1110"] = (
        "Run 0931: freeMinted flat 1000, totalSupply 1e27, balance user=0. Tanpa perubahan.")
if isinstance(tc.get("PACTA"), dict):
    tc["PACTA"]["runNote0931_1110"] = (
        "Run 0931: freeMinted flat 55, sharesMinted=57, soldOut=0, freeClaimed(user)=0. Status "
        "excluded-free-pool-exhausted-2026-11-09, tanpa perubahan.")

snap["runNote0931_1110_binanceai"] = (
    "Run 0931 track-B: binanceai.fun TIDAK BERUBAH — launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0 (blok 132699172, special2). Status "
    "closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote0931_1110_grove"] = (
    "Run 0931 Grove: TIDAK BERUBAH — freeOpen=0, freeMinted=2500/2500, FREE_SUPPLY=2500, "
    "MAX_SUPPLY=12500, freeClaimed(user)=0, balance user=0 (blok 132699172, special2).")
snap["runNote0931_1110"] = (
    f"Run 0931 (2026-11-10 09:31 WIB, blok {BLOCK}, interval 39,9 mnt): re-read {len(rr['reread'])} kontrak + "
    f"{len(rr['track_c'])} track_c. Velocity LOLOS (merge): {vel_pass if vel_pass else '0 — FCAT lolos pada baca prio6 '
    'saja (~1,7-1,9x, >=20 token), tapi umur + website unverified sehingga tier tidak berubah'}. "
    "SEVENFOLD: free 705/3000 = 23,5% (masih <25%) + WEBSITE TERVERIFIKASI run ini (llms.txt + agent.json "
    "mencetak kontrak persis; gate kini lolos, tinggal kaki 25%) — tetap watchlist-only, BUKAN strong lead. "
    "FCAT 43,4% verified, Roguefall 52,3% verified, Sakura 21,3% verified — tetap watchlist-only/early lead. "
    "JINCHAN read gagal total (nilai lama dipertahankan). THYRK slot terpakai. NUSA freeMinted 364, gate tetap "
    "FAILED. BOME-50CD masih belum dibuka. Binanceai/Grove tidak berubah. Ankr 401 fast-fail (preflight 16,5 dtk, "
    "head 132698469); watermark tetap 132512564; gap ~185.905 blok. Feed Sourcify 20/20 dicek (5 retry sekuensial), "
    "0 S1/S2. Boltbook 0 baru vs snapshot+seen+hotleg. Bridge 116 kontrak, 0 promosi. Odaily/PANews 0 hit. "
    "Kandidat baru 0; strong lead baru 0; early lead baru 0; track-C lead/kandidat baru 0; sellout baru 0. RUN DIAM.")
snap["runNote0931_1110_scan"] = (
    "Route 4 scan: FAST-FAIL. Pre-flight ankr_getLogs 50 blok (head 132698469): FAIL 16,5 dtk HTTP 401 "
    "Unauthorized. Kelanjutan outage Ankr sejak 2026-11-09 ~13:33 WIB. Scan leg TIDAK dijalankan; watermark "
    "tetap 132512564; gap ke head ~185.905 blok dan tumbuh. 5c dilewati (tanpa output scan).")
snap["last_run_wib"] = TS_WIB
snap["timestamp_wib"] = TS_WIB

tmp_path = snap_path + ".tmp-0931"
with open(tmp_path, "w") as f:
    json.dump(snap, f, indent=1, ensure_ascii=False)
import os
os.replace(tmp_path, snap_path)
print("merged. contracts:", len(snap["contracts"]), "track_c:", len(snap["track_c"]),
      "updated reads:", updated, "tc fields:", tc_updated, "vel_pass:", vel_pass)
