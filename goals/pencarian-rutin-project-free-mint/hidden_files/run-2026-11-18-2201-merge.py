#!/usr/bin/env python3
"""Merge run 2026-11-18 22:01 WIB re-read into onchain-snapshot.json (lean merge).
Driver run-2026-11-18-2201.py completed exit 0 in 83.7s (no SIGTERM).
Reread via Quicknode tunnel: 285 calls, 4 chunk errors 429 (calls 135-139,
155-159, 180-184, 275-279 - rate limit 15/s) - nulls are read failures, never
overwrites. Block 134332751 (prev 2131: 134328778). Interval 30.0 min wall-clock.
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. 0 perubahan status.
Boltbook EN+ZH OK (44.940 / 43.241 byte, 9 alamat unik, 0 baru - semua dikenal;
0x7106... non-kontrak 2131 sudah tidak ada di front page). Sourcify feed OK
(20 alamat, semua sudah di hot-leg-seen -> 0 shape-check baru; 7 target retry
dari hot-leg 2154 ternyata SUDAH tercatat di hot-leg-seen sebagai attempted,
jadi filter seen melewatinya - retry terpisah di luar filter, lihat runlog).
Scan leg FAST-FAIL pre-flight HTTP 401 (Ankr outage sejak 2026-11-09 berlanjut);
watermark TETAP 134086385. Read-only except snapshot. None/err values NEVER overwrite.
Notes resolved by contract ADDRESS (PLAN names differ from snapshot keys for
EIM/PIXEL FROGS/Flare-bd6f/Kryntar)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2201-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2131-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~22:01 WIB"
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
    snap["contracts"][key]["runNote2201_1118"] = text

note_by_name("STOCK AGENT", "Run 2201 (blok 134332751, interval ~30 mnt vs 2131): totalSupply 800->801 (+1), freeLeft 311->310 (FREE_SUPPLY 1111, inferred free 801/1111 = 72,1% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. quote_user_1 = 0; user views null (chunk 429) - slot per baca terakhir baik (hot-leg 2154: freeMintedByWallet 0) tetap terbuka. Velocity GAGAL (+1 <20). 70% crossing sudah dilaporkan 18:44 - tidak dilaporkan ulang.")
note_by_name("Lumenhold", "Run 2201: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 2201: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note_by_name("Vitaliq Scans", "Run 2201: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~15 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 2201: totalSupply 1264 FLAT vs 2131, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("CAT402", "Run 2201: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note_by_name("Bubblebruin", "Run 2201: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("DGF CARD", "Run 2201: totalMinted 1673->1676 (+3) -> velocity GAGAL (<20). freeMinted/mintOpen revert. Tetap EARLY LEAD.")
note_by_name("THE WALL", "Run 2201: totalSupply 5518 FLAT -> velocity GAGAL; free views revert. Bukan kandidat.")
note_by_name("Mine Card", "Run 2201: totalSupply 1385 FLAT (2131: +15) -> velocity GAGAL. Bukan kandidat.")
note_by_name("EIM", "Run 2201: totalMinted 795->796 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 2201: totalSupply 798->804 (+6, maks run ini) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("ARKYN", "Run 2201: totalMinted 2298->2300 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("REOPIR", "Run 2201: totalSupply 594 FLAT, freeClaimed 594 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("SPARKS", "Run 2201: totalSupply 1215 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("PunchCard", "Run 2201: totalSupply 1360->1361 (+1), totalMinted 1361 -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("MORFO", "Run 2201: totalMinted 1133->1134 (+1), mintOpen 1 -> velocity GAGAL. Bukan kandidat.")
note_by_name("PIXELFROGS", "Run 2201: totalSupply 456 FLAT, freeMinted 454, freeLeft 2546, mintOpen 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Flare-bd6f", "Run 2201: totalSupply 4900 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Stromboat", "Run 2201: totalMinted 333->334 (+1), freeMinted 334, paidMinted 0 -> velocity GAGAL. Bukan kandidat.")
note_by_name("Compasyn", "Run 2201: totalSupply 1097 FLAT, freeClaimed 1092 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kitebots", "Run 2201: totalSupply 1481 FLAT, freeMinted 1481 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Kryntar", "Run 2201: totalMinted 1378 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Pengu", "Run 2201: totalMinted 139 FLAT, freeMinted 139 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("XCOPY", "Run 2201: totalSupply 464 FLAT, totalMinted 464 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("ADRAW", "Run 2201: SEMUA view null (chunk 135-139 429) -> BACA GAGAL, nilai lama dipertahankan; freeMinted lama 326. Bukan kandidat.")
note_by_name("AgentEcho", "Run 2201: totalSupply 415 terbaca lagi (null di 2131), mintOpen 1, AGENT_ID 552192074493313695968015109214105588393044541999, mintedBy 0, balance 0. Bukan kandidat.")
note_by_name("Abyssora", "Run 2201: SEMUA view null lagi (chunk 429) -> BACA GAGAL, nilai lama dipertahankan. Bukan kandidat.")
note_by_name("Kageveil Genesis", "Run 2201: totalSupply/normalMinted/mintOpen/mintClosed null (chunk 275-279 429) -> BACA GAGAL parsial, nilai lama dipertahankan (totalSupply 49); balanceOf 0 terbaca. Bukan kandidat.")
note_by_name("Foundry Faces", "Run 2201: totalMinted 2208->2209 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("ALIEN", "Run 2201: totalSupply 504->505 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("PUNNY", "Run 2201: freeMinted 379/999 = 37,94% FLAT, totalMinted 379 FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). Tetap EARLY LEAD / bukan kandidat.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 10000
    aone["FREE_TOTAL"] = 10000
    aone["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        aone["lastReadBlock"] = BLOCK
    aone["note2201"] = ("Run 2201 (blok 134332751): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang. Entry dipertahankan dengan status minted-by-user.")
    print("AONE updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- bsccat / PEPE track-C re-reads ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    bs["freeMinted"] = reread["bsccat"]["views"].get("freeMinted")
    bs["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        bs["lastReadBlock"] = BLOCK
    bs["note2201"] = ("Run 2201: freeMinted 536 FLAT (2131: 536), totalMinted err (revert). "
        "Status tetap watchlist-only-age-unverified. Bukan lead/kandidat.")
    print("bsccat updated: freeMinted 536 FLAT")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    fm = reread["pepe"].get("freeMinted")
    if isinstance(fm, int):
        pe["freeMinted"] = fm
    pe["lastReadWib"] = NOW
    if isinstance(BLOCK, int):
        pe["lastReadBlock"] = BLOCK
    pe["note2201"] = ("Run 2201: freeMinted null (chunk 429) -> BACA GAGAL, nilai lama 500 dipertahankan; "
        "soldShares 501, FREE_SHARES 500, hasMinted_user 1, minted-by-user-2026-11-16. DIAM.")
    print("PEPE updated: freeMinted read FAILED, old 500 retained")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote2201"] = ("Run 2201 (blok 134332751): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 22:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status; STOCK AGENT inferred 72,1% (bukan counter terverifikasi) - tetap EARLY LEAD; Lumenhold 83,9% FLAT tapi umur UNVERIFIED; "
    "Boltbook 0 alamat baru; Sourcify feed 0 shape-check baru (semua sudah di hot-leg-seen). Sweep: PENDING (subagent belum kembali saat merge).")
snap["runNote2201_1118"] = (
    "Run 2201 (interval ~30 mnt vs 2131; blok 134332751): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status. "
    "Driver selesai exit 0 dalam 83,7 dtk (tanpa SIGTERM). "
    "Scan leg FAST-FAIL: Ankr pre-flight GAGAL HTTP 401 Unauthorized dalam 1,1 dtk (outage Ankr sejak 2026-11-09 berlanjut); watermark TETAP 134086385; gap ~246.366 blok (head 134332751) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Reread Quicknode 285 calls, 4 chunk error 429 (calls 135-139, 155-159, 180-184, 275-279 - rate limit 15/dtk; ADRAW semua null, Abyssora semua null, Kageveil totalSupply null, PEPE freeMinted null - nilai lama dipertahankan, BUKAN perubahan). "
    "Velocity: 0 LOLOS - maks +6 AgentNOVA, +3 DGF CARD, +2 ARKYN, +1 Foundry Faces/PunchCard/MORFO/STOCK AGENT/EIM/ALIEN/Stromboat - semua <20 token. "
    "STOCK AGENT totalSupply 800->801 (+1), freeLeft 310, inferred free 801/1111 = 72,1% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THE WALL 5518 FLAT, DGF CARD 1676 (+3). "
    "Vitaliq Scans: genesisStart 07:00 WIB (umur ~15 jam TERVERIFIKASI <24 jam), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY freeMinted 379/999 = 37,94% FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34). "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). "
    "bsccat freeMinted 536 FLAT (tetap watchlist-only-age-unverified); PEPE freeMinted null (baca gagal, nilai lama 500 dipertahankan). "
    "Boltbook EN OK (44.940 byte, 9 alamat) + ZH OK (43.241 byte, 9 alamat); 0 alamat baru - semua dikenal (0x7106... non-kontrak 2131 sudah tidak ada di front page). "
    "Sourcify feed OK via tunnel (20 alamat, semua sudah di hot-leg-seen -> 0 shape-check baru, 0 sale-shape). "
    "CATATAN: 7 target retry shape-check dari hot-leg 2154 ternyata SUDAH tercatat di hot-leg-seen.json sebagai attempted (hot-leg menulis semua hasil shape-check ke seen, termasuk yang gagal) - jadi filter seen di driver utama melewatinya dan retry di driver ini no-op; ketujuh alamat tetap BELUM ter-shape-check (ABI endpoint Sourcify timeout rc=28). Retry langsung di luar filter dilakukan terpisah run ini, hasilnya di runlog. "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Sweep rute 3/5b/6: lihat runlog (subagent). "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
