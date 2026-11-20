#!/usr/bin/env python3
"""Merge run 2026-11-18 22:31 WIB re-read into onchain-snapshot.json (lean merge).
Driver run-2026-11-18-2231.py completed exit 0 in 132.6s (no SIGTERM).
Reread via Quicknode tunnel: 285 calls, 5 chunk errors 429 (calls 130-134,
155-159, 195-199, 210-214, 230-234 - rate limit 15/s) - nulls are read failures, never
overwrites. Block 134336331 (prev 2201: 134332751). Interval 30.0 min wall-clock.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status.
Boltbook EN+ZH OK (45.248 / 43.620 byte, 11 alamat, 0 baru - semua dikenal;
0xbcdd... sudah di-shape-check run ini: S1/S2 false). Sourcify feed OK
(20 alamat, top verifiedAt 2026-11-18T15:35:15Z; shape-check 11 alamat incl.
6 retry dari hot-leg 2229 - semua S1=false, S2=false, 0 sale-shape).
Scan leg FAST-FAIL pre-flight HTTP 401 (Ankr outage sejak 2026-11-09 berlanjut);
watermark TETAP 134086385. Read-only except snapshot. None/err values NEVER overwrite.
Notes resolved by contract ADDRESS."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2231-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2201-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~22:31 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 30.0
print(f"block {BLOCK} interval {INTERVAL_MIN} min (wall-clock)")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass, deltas = [], [], [], {}
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        deltas[name] = minted
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)
print("deltas:", dict(sorted(deltas.items(), key=lambda kv: -kv[1])[:12]))

def note_by_name(plan_name, text):
    d = reads.get(plan_name)
    if not d:
        print("NOTE MISS (no read)", plan_name); return
    key = addr2key.get(d.get("address", "").lower())
    if key is None:
        print("NOTE MISS (no snapshot key)", plan_name); return
    snap["contracts"][key]["runNote2231_1118"] = text

note_by_name("STOCK AGENT", "Run 2231 (blok 134336331, interval ~30 mnt vs 2201): totalSupply 801->810 (+9, MAKS run ini), freeLeft 310->301 (FREE_SUPPLY 1111, inferred free 810/1111 = 72,9% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. freeMintedByWallet(user)=0 terbaca lagi (slot terbuka), balanceOf(user)=0. Velocity GAGAL (+9 <20). 70% crossing sudah dilaporkan 18:44 - tidak dilaporkan ulang.")
note_by_name("Lumenhold", "Run 2231: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 2231: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note_by_name("Vitaliq Scans", "Run 2231: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~15,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 2231: totalSupply 1264 FLAT vs 2201, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("CAT402", "Run 2231: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note_by_name("Bubblebruin", "Run 2231: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("DGF CARD", "Run 2231: totalMinted 1676 FLAT -> velocity GAGAL. freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note_by_name("THE WALL", "Run 2231: totalSupply 5518->5520 (+2) -> velocity GAGAL; free views revert. Bukan kandidat.")
note_by_name("Mine Card", "Run 2231: totalSupply 1385->1387 (+2) -> velocity GAGAL. Bukan kandidat.")
note_by_name("EIM", "Run 2231: totalMinted 796->800 (+4) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 2231: totalSupply 804 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ARKYN", "Run 2231: totalMinted 2300 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("REOPIR", "Run 2231: totalSupply 594 FLAT, freeClaimed 594 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("SPARKS", "Run 2231: totalSupply 1215->1216 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PunchCard", "Run 2231: totalSupply 1361 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("MORFO", "Run 2231: totalMinted 1134 FLAT, mintOpen 1 -> velocity GAGAL. Bukan kandidat.")
note_by_name("PIXELFROGS", "Run 2231: totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Flare-bd6f", "Run 2231: totalSupply 4900 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Stromboat", "Run 2231: totalMinted 334->335 (+1), freeMinted 335, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Compasyn", "Run 2231: totalSupply 1097 FLAT, freeClaimed 1092 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kitebots", "Run 2231: totalSupply 1481 FLAT, freeMinted 1481 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kryntar", "Run 2231: totalMinted 1378 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Pengu", "Run 2231: totalMinted 139 FLAT, freeMinted 139 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("XCOPY", "Run 2231: totalSupply 464 FLAT, totalMinted 464 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ADRAW", "Run 2231: SEMUA view null (chunk 130-134 429) -> BACA GAGAL, nilai lama dipertahankan; freeMinted lama 326. Bukan kandidat.")
note_by_name("AgentEcho", "Run 2231: totalSupply 415 FLAT, mintOpen 1, AGENT_ID 552192074493313695968015109214105588393044541999, mintedBy 0, balance 0. Bukan kandidat.")
note_by_name("Abyssora", "Run 2231: SEMUA view null lagi (chunk 429) -> BACA GAGAL, nilai lama dipertahankan. Bukan kandidat.")
note_by_name("Kageveil Genesis", "Run 2231: totalSupply 49 terbaca lagi (null di 2201), normalMinted 49, mintOpen 1, mintClosed 0; balanceOf 0. Bukan kandidat.")
note_by_name("Foundry Faces", "Run 2231: totalMinted 2209 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ALIEN", "Run 2231: totalSupply 505->506 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PUNNY", "Run 2231: freeMinted 379/999 = 37,94% FLAT, totalMinted 379 FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). Tetap EARLY LEAD / bukan kandidat.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 10000
    aone["FREE_TOTAL"] = 10000
    aone["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        aone["lastReadBlock"] = BLOCK
    aone["note2231"] = ("Run 2231 (blok 134336331): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang. Entry dipertahankan dengan status minted-by-user.")
    print("AONE updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- bsccat / PEPE track-C re-reads ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    fm = reread["bsccat"]["views"].get("freeMinted")
    if isinstance(fm, int):
        bs["freeMinted"] = fm
    bs["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        bs["lastReadBlock"] = BLOCK
    bs["note2231"] = ("Run 2231: freeMinted 536->539 (+3), totalSupply 539000000000000000000000000. "
        "Status tetap watchlist-only-age-unverified. Bukan lead/kandidat.")
    print("bsccat updated: freeMinted 539 (+3)")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    fm = reread["pepe"].get("freeMinted")
    if isinstance(fm, int):
        pe["freeMinted"] = fm
    pe["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        pe["lastReadBlock"] = BLOCK
    pe["note2231"] = ("Run 2231: freeMinted 500 terbaca lagi (null di 2201, nilai lama 500 cocok); "
        "soldShares 501, FREE_SHARES 500, hasMinted_user 1, minted-by-user-2026-11-16. DIAM.")
    print("PEPE updated: freeMinted 500 re-read OK")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2231"] = ("Run 2231 (blok 134336331): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 22:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status; STOCK AGENT +9 (maks run, inferred 72,9%) - tetap EARLY LEAD; Lumenhold 83,9% FLAT tapi umur UNVERIFIED; "
    "Boltbook 0 alamat baru; Sourcify feed 11 shape-check (incl. 6 retry hot-leg 2229) 0 sale-shape. Sweep: PENDING (subagent).")
snap["runNote2231_1118"] = (
    "Run 2231 (interval ~30 mnt vs 2201; blok 134336331): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status. "
    "Driver selesai exit 0 dalam 132,6 dtk (tanpa SIGTERM). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL HTTP 401 Unauthorized dalam 1,9 dtk (outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385; gap ~249.946 blok (head 134336331) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Reread Quicknode 285 calls, 5 chunk error 429 (calls 130-134, 155-159, 195-199, 210-214, 230-234 - rate limit 15/dtk; ADRAW semua null, Abyssora semua null, APGB V1 + Longge null, STOCK FREE_SUPPLY/MAX_SUPPLY/mintOpen/quote null - nilai lama dipertahankan, BUKAN perubahan; Kageveil terbaca lagi 49). "
    "Velocity: 0 LOLOS - maks +9 STOCK AGENT, +4 EIM, +2 Mine Card/THE WALL, +1 ALIEN/SPARKS/Stromboat - semua <20 token. "
    "STOCK AGENT totalSupply 801->810 (+9), freeLeft 301, inferred free 810/1111 = 72,9% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. freeMintedByWallet(user)=0 terbaca lagi (slot terbuka). "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THE WALL 5520 (+2), DGF CARD 1676 FLAT. "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~15,5 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY freeMinted 379/999 = 37,94% FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). "
    "bsccat freeMinted 536->539 (+3, tetap watchlist-only-age-unverified); PEPE freeMinted 500 terbaca lagi (null di 2201). "
    "Boltbook EN OK (45.248 byte, 11 alamat) + ZH OK (43.620 byte, 11 alamat); 0 alamat baru - semua dikenal; 0xbcdd... (baru di hot-leg 2229) di-shape-check run ini: S1/S2 false (mint ada, agent ref ada, tapi tanpa quote + tanpa free view) - bukan sale-shape, bukan early lead (tanpa bukti free-mint/first-mint on-chain run ini). "
    "Sourcify feed OK via tunnel (20 alamat, top verifiedAt 2026-11-18T15:35:15Z; shape-check 11 alamat incl. 6 retry dari hot-leg 2229 - semua S1=false, S2=false, 0 sale-shape; 4 alamat duplikat feed+carry-forward). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Sweep rute 3/5b/6: lihat runlog (subagent). "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
