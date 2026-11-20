#!/usr/bin/env python3
"""Merge run 2026-11-19 01:01 WIB lean re-read into onchain-snapshot.json.
Main script run-2026-11-19-0101.py completed leg-4 (15/15 focus items fresh,
0 chunk errors, block 134352903, 117 calls, 181.3s) + Boltbook EN/ZH files,
then was killed by the 420s timeout during Sourcify/shape legs; salvage
run-2026-11-19-0101-salvage.py (98.3s) completed Sourcify + shape-check +
bridge + pre-flight. Nulls NEVER overwrite; lastReadWib updated ONLY for
items with >=1 int value. Interval ~24.9 min from block delta (134356258-134352903
= 3355 blocks x 0.45s). Prev reread = run 0031. Read-only except snapshot."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0101-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-19-0001-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-19 ~01:01 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 25.2
print(f"block {BLOCK} interval {INTERVAL_MIN} min (delta 3355 x 0.45s)")
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
    has_int = any(isinstance(val, int) for val in v.values())
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
    if has_int:
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
    snap["contracts"][key]["runNote0101_1119"] = text

note_by_name("STOCK AGENT", "Run 0101 (blok 134356258, interval ~25,2 mnt vs 0031): totalSupply 818 FLAT, freeLeft 293 FLAT (FREE_SUPPLY 1111, inferred free 818/1111 = 73,6% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. mintOpen 1, quote_user_1 0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (0 <20).")
note_by_name("Lumenhold", "Run 0101: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 0101: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("THYRK", "Run 0101: freeMinted 4318/7777 = 55,5% FLAT, totalSupply 4419 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("Vitaliq Scans", "Run 0101: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~18 jam, TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov - kurang dari 6 jam lagi), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 0101: totalSupply 1264 FLAT vs 0031, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("Bubblebruin", "Run 0101: totalSupply 2627 FLAT (was 2627 at 0031; freeClaimed 2621/7777 = 33,7% FLAT) -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("ARKYN", "Run 0101: totalMinted 2324->2326 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 0101: totalSupply 827->828 (+1) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("Matrix", "Run 0101: freeMinted 642 FLAT, totalSupply 636 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("AGCLUB", "Run 0101: totalMinted/freeMinted 530 FLAT (FREE_CAP 888 = 59,7%) -> velocity GAGAL. Bukan kandidat.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["note0101"] = ("Run 0101 (blok 134356258): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang.")
    print("AONE note updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- RigForge track-C: still not open ----
rf = snap.setdefault("track_c", {}).get("RigForge")
if isinstance(rf, dict):
    rf["note0101"] = ("Run 0101 (blok 134356258): freeSharesLeft 621 FLAT vs 0031, "
        "openedAt tetap 0 (belum buka), freeClaimed 379 FLAT. Tetap belum buka; bukan lead/kandidat.")
    print("RigForge note updated: freeSharesLeft 621 FLAT, openedAt 0")

# ---- bsccat / PEPE (track_c): fresh reads this run ----
bs = snap.setdefault("track_c", {}).get("bsccat")
bv = reread.get("bsccat", {}).get("views", {})
if isinstance(bs, dict):
    if isinstance(bv.get("freeMinted"), int):
        bs["freeMinted"] = bv["freeMinted"]
    bs["lastReadWib"] = NOW
    bs["note0101"] = ("Run 0101 (blok 134356258): bacaan segar - freeMinted 546 FLAT vs 0031, "
        "totalSupply 546e27, view lain revert. BUKAN perubahan reportable. Tetap watchlist-only-age-unverified.")
    print("bsccat note updated: freeMinted", bv.get("freeMinted"))
pe = snap.setdefault("track_c", {}).get("PEPE")
pv = reread.get("pepe", {})
if isinstance(pe, dict):
    pe["lastReadWib"] = NOW
    pe["note0101"] = ("Run 0101 (blok 134356258): bacaan segar - freeMinted 500 FLAT, soldShares 501, "
        "FREE_SHARES 500, opened 0, hasMinted(user)=1. BUKAN perubahan. Minted-by-user.")
    print("PEPE note updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote0101"] = ("Run 0101 (blok 134356258): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-19 01:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status reportable; velocity 0 LOLOS (maks +2 ARKYN, interval ~25,2 mnt). STOCK AGENT 73,6% inferred FLAT - tetap EARLY LEAD; "
    "Lumenhold 83,9% FLAT tapi umur UNVERIFIED; Vitaliq umur ~18 jam terverifikasi <24 jam (deadline ~07:00 WIB 19 Nov). "
    "Boltbook EN+ZH OK 200 (44.819/43.213 byte, 4/3 alamat, free_kw 6/1) - 1 alamat baru 0x0b0b... (shape S1/S2 false, verifiedAt 5 Nov, bukan lead). "
    "Sourcify feed 20 baru, 14 shape-checked, 0 shape hit S1/S2. Sweep: 0 proyek baru terverifikasi <24 jam; semua hit item lama/terminal. "
    "Scan leg FAST-FAIL (pre-flight Ankr HTTP 401 Unauthorized - auth/paid-gate, BUKAN timeout egress); watermark TETAP 134086385; gap ~269.873 blok.")
snap["runNote0101_1119"] = (
    "Run 0101 (interval ~25,2 mnt vs 0031 dari delta blok 3355 x 0,45 dtk; blok 134356258): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status reportable. "
    "Split-driver pattern BEKERJA: driver A run-2026-11-19-0101.py (pre-flight + leg-4 re-read FOKUS 15/15 item bernilai segar, 117 calls, 0 chunk error, 82,3 dtk + Boltbook EN/ZH tersimpan) selesai 90,6 dtk TANPA kill 420 dtk; driver B run-2026-11-19-0101-legs.py (48,7 dtk) menyelesaikan Sourcify + shape-check + bridge + pre-flight. "
    "Velocity: 0 LOLOS - maks +2 ARKYN (totalMinted 2324->2326) dan +1 AgentNOVA (totalSupply 827->828); sisanya 0/FLAT - semua <20 token. "
    "STOCK AGENT totalSupply 818 FLAT, freeLeft 293 FLAT, inferred free 73,6% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Lumenhold freeClaimed 1259/1500 = 83,9% FLAT (umur UNVERIFIED -> BUKAN strong lead). Ledgera 54,1% FLAT, THYRK 55,5% FLAT, Matrix 642 FLAT, AGCLUB 59,7% FLAT, HIVE 1264 FLAT, Bubblebruin 33,7% FLAT. "
    "Vitaliq Scans: genesisStart 07:00 WIB 18 Nov (umur ~18 jam TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov - kurang dari 6 jam lagi), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY: totalMinted/freeMinted 379 FLAT, mintClosed=1, mintStart 2026-11-17 20:32 WIB (umur ~28 jam) - age-exclusion SUDAH dilaporkan 20:34 WIB 18 Nov dan entri sudah dihapus dari snapshot; tidak ada aksi. "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). RigForge freeSharesLeft 621 FLAT, openedAt tetap 0 (belum buka). "
    "bsccat: bacaan segar freeMinted 546 FLAT. PEPE: freeMinted 500 FLAT, opened 0, hasMinted(user)=1. "
    "Boltbook EN+ZH HTTP 200 (44.819/43.213 byte, 4/3 alamat, free_kw 6/1) - 1 alamat BARU 0x0b0b8df4d7df0b2cdd00877b476a447a8a1824ee (mint true, TANPA quote/free view/agent ref, verifiedAt 2026-11-05T08:01:27Z -> BUKAN S1/S2, BUKAN early-shape; dicatat, tidak dilaporkan, tidak masuk snapshot). 0x26ad... (0031) sudah rotasi keluar dari front page. "
    "Sourcify feed 5a: HTTP 200, 20 kontrak baru (verifiedAt 17:44-18:06 UTC), 14 shape-checked (12 feed baru + Boltbook 0x0b0b + YAMA re-check): 0 S1, 0 S2. YAMA re-check: S1/S2 FALSE (agent_ref FALSE) - tetap bukan lead track C. "
    "Bridge read-only: 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Scan leg FAST-FAIL: pre-flight ankr_getLogs HTTP 401 Unauthorized (KEDUA driver; Ankr auth/paid-gate - BUKAN timeout egress); watermark TETAP 134086385; gap ~269.873 blok (head 134356258) dan terus membesar; scan chain-wide TIDAK diluncurkan; gap ditangani backfill driver. "
    "Sweep rute 3/5b/6 (subagent read-only): 0 proyek baru terverifikasi <24 jam; semua hit item lama/terminal (Agentic Gangster sold out, RIGBYPASS/MOLT/AGENT COSMOS/ONLYAI umur >24 jam, Bold Leonidas/Saturnagent/Gryphlume sold out, TriEight/Dragon Agents/Rulz Share terminal, Likhin/JINMA/YAMA/NOTV/UFO/NEBULA/VISION/NOVRA/WNO/QILIN/SAFU/PROXY di track_c/snapshot). Square: posting relevan terbaru 25 Okt-10 Nov, tanpa link/kontrak baru. Odaily newsflash 19 Nov 01:49 WIB + PANews: tanpa item Agent ID/free-mint. DappBay kategori AI: kurasi umum, tanpa free-mint baru. Catatan sweep: jendela waitlist NOTV berakhir 19 Nov 15:00 UTC (~22:00 WIB) - item sudah age-excluded-2026-11-14 di track_c, bookkeeping saja, tanpa aksi. "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan reportable baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
