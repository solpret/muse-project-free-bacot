#!/usr/bin/env python3
"""Merge run 2026-11-19 00:31 WIB lean re-read into onchain-snapshot.json.
Main script run-2026-11-19-0031.py completed leg-4 (15/15 focus items fresh,
0 chunk errors, block 134352903, 117 calls, 181.3s) + Boltbook EN/ZH files,
then was killed by the 420s timeout during Sourcify/shape legs; salvage
run-2026-11-19-0031-salvage.py (98.3s) completed Sourcify + shape-check +
bridge + pre-flight. Nulls NEVER overwrite; lastReadWib updated ONLY for
items with >=1 int value. Interval ~24.9 min from block delta (134352903-134349577
= 3326 blocks x 0.45s). Prev reread = run 0001. Read-only except snapshot."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0031-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-19-0001-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-19 ~00:31 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 24.9
print(f"block {BLOCK} interval {INTERVAL_MIN} min (delta 3326 x 0.45s)")
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
    snap["contracts"][key]["runNote0031_1119"] = text

note_by_name("STOCK AGENT", "Run 0031 (blok 134352903, interval ~24,9 mnt vs 0001): totalSupply 818 FLAT, freeLeft 293 FLAT (FREE_SUPPLY 1111, inferred free 818/1111 = 73,6% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. mintOpen 1, quote_user_1 0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (0 <20).")
note_by_name("Lumenhold", "Run 0031: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 0031: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("THYRK", "Run 0031: freeMinted 4318/7777 = 55,5% FLAT, totalSupply 4419 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("Vitaliq Scans", "Run 0031: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~17,5 jam, TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 0031: totalSupply 1264 FLAT vs 0001, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("Bubblebruin", "Run 0031: totalSupply 2627 FLAT (was 2627 at 0001; freeClaimed 2621/7777 = 33,7% FLAT) -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("ARKYN", "Run 0031: totalMinted 2315->2324 (+9) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 0031: totalSupply 818->827 (+9) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("Matrix", "Run 0031: freeMinted 642 FLAT, totalSupply 636 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("AGCLUB", "Run 0031: totalMinted/freeMinted 530 FLAT (FREE_CAP 888 = 59,7%) -> velocity GAGAL. Bukan kandidat.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["note0031"] = ("Run 0031 (blok 134352903): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang.")
    print("AONE note updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- RigForge track-C: still not open ----
rf = snap.setdefault("track_c", {}).get("RigForge")
if isinstance(rf, dict):
    rf["note0031"] = ("Run 0031 (blok 134352903): freeSharesLeft 621 FLAT vs 0001, "
        "openedAt tetap 0 (belum buka), freeClaimed 379 FLAT. Tetap belum buka; bukan lead/kandidat.")
    print("RigForge note updated: freeSharesLeft 621 FLAT, openedAt 0")

# ---- bsccat / PEPE (track_c): fresh reads this run ----
bs = snap.setdefault("track_c", {}).get("bsccat")
bv = reread.get("bsccat", {}).get("views", {})
if isinstance(bs, dict):
    if isinstance(bv.get("freeMinted"), int):
        bs["freeMinted"] = bv["freeMinted"]
    bs["lastReadWib"] = NOW
    bs["note0031"] = ("Run 0031 (blok 134352903): bacaan segar - freeMinted 545->546 (+1), "
        "totalSupply 546e27, view lain revert. BUKAN perubahan reportable. Tetap watchlist-only-age-unverified.")
    print("bsccat note updated: freeMinted", bv.get("freeMinted"))
pe = snap.setdefault("track_c", {}).get("PEPE")
pv = reread.get("pepe", {})
if isinstance(pe, dict):
    pe["lastReadWib"] = NOW
    pe["note0031"] = ("Run 0031 (blok 134352903): bacaan segar - freeMinted 500 FLAT, soldShares 501, "
        "FREE_SHARES 500, opened 0, hasMinted(user)=1. BUKAN perubahan. Minted-by-user.")
    print("PEPE note updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote0031"] = ("Run 0031 (blok 134352903): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-19 00:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status reportable; velocity 0 LOLOS (maks +9 ARKYN/AgentNOVA, interval ~24,9 mnt). STOCK AGENT 73,6% inferred FLAT - tetap EARLY LEAD; "
    "Lumenhold 83,9% FLAT tapi umur UNVERIFIED; Vitaliq umur ~17,5 jam terverifikasi <24 jam (deadline ~07:00 WIB 19 Nov). "
    "Boltbook EN+ZH OK 200 (43.824/42.210 byte, 4 alamat, free_kw 2/2) - 1 alamat baru 0x26ad... (shape S1/S2 false, bukan lead). "
    "Sourcify feed 20 baru, 0 shape hit S1/S2. Sweep: 0 proyek baru terverifikasi <24 jam; YAMA sale (0x86D7...) bukan S1/S2 (tanpa agent ref, verifiedAt 8 Nov) + umur UNVERIFIED - dicatat saja. "
    "Scan leg FAST-FAIL (pre-flight Ankr HTTP 401 Unauthorized - auth/paid-gate, BUKAN timeout egress); watermark TETAP 134086385; gap ~266.518 blok.")
snap["runNote0031_1119"] = (
    "Run 0031 (interval ~24,9 mnt vs 0001 dari delta blok 3326 x 0,45 dtk; blok 134352903): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status reportable. "
    "Main script run-2026-11-19-0031.py: leg-4 re-read FOKUS 15/15 item bernilai segar (117 calls, 0 chunk error, 181,3 dtk) + Boltbook EN/ZH tersimpan, "
    "lalu killed timeout 420 dtk saat legs Sourcify/shape; salvage run-2026-11-19-0031-salvage.py (98,3 dtk) menyelesaikan Sourcify + shape + bridge + pre-flight. "
    "Velocity: 0 LOLOS - maks +9 ARKYN (totalMinted 2315->2324) dan +9 AgentNOVA (totalSupply 818->827); sisanya 0/FLAT - semua <20 token. "
    "STOCK AGENT totalSupply 818 FLAT, freeLeft 293 FLAT, inferred free 73,6% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Lumenhold freeClaimed 1259/1500 = 83,9% FLAT (umur UNVERIFIED -> BUKAN strong lead). Ledgera 54,1% FLAT, THYRK 55,5% FLAT, Matrix 642 FLAT, AGCLUB 59,7% FLAT, HIVE 1264 FLAT, Bubblebruin 33,7% FLAT. "
    "Vitaliq Scans: genesisStart 07:00 WIB 18 Nov (umur ~17,5 jam TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY: totalMinted/freeMinted 379 FLAT, mintClosed=1, mintStart 2026-11-17 20:32 WIB (umur ~28 jam) - age-exclusion SUDAH dilaporkan 20:34 WIB 18 Nov dan entri sudah dihapus dari snapshot (catatan 0001); tidak ada aksi. "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). RigForge freeSharesLeft 621 FLAT, openedAt tetap 0 (belum buka). "
    "bsccat: bacaan segar freeMinted 545->546 (+1). PEPE: freeMinted 500 FLAT, opened 0, hasMinted(user)=1. "
    "Boltbook EN+ZH HTTP 200 (43.824/42.210 byte, 4 alamat, free_kw 2/2) - 1 alamat BARU 0x26ad277193ff31bd086a47bf7b1d25a93573c989 (31 fns, agent_ref True, is_token True, TANPA mint/quote/free view -> BUKAN S1/S2, BUKAN early-shape; verifiedAt 2026-11-18T13:56:48Z; dicatat, tidak dilaporkan, tidak masuk snapshot). "
    "Sourcify feed 5a: HTTP 200, 20 kontrak baru (verifiedAt 17:25-17:46 UTC), SEMUA shape-checked: 0 S1, 0 S2 (terdekat 0xC463... mint+agent_ref+is_token TANPA quote/free view; 0xAF43.../0x3ABE... mint TANPA quote/agent). "
    "YAMA PROJECT (temuan sweep, sale 0x86D779fc4d83044cCECCb53639f9a98E367D6E46, token 0xa84EA20a667B3b1859aB9a9984FF5F03D8688aE2, yamaproject.pages.dev, first share free, 3.042/100.000 shares): shape-check S1/S2 FALSE (mint+quote+freeUsed ADA tapi agent_ref FALSE, is_token FALSE; verifiedAt 2026-11-08 - kontrak 11 hari) + umur launch UNVERIFIED -> BUKAN lead/kandidat track C; dicatat runlog saja, tidak masuk snapshot. "
    "DGF CARD (temuan sweep, dgnft.pages.dev, 1.394/5.100 minted) - sudah di snapshot sebagai EARLY LEAD; tanpa tanggal launch di hasil search -> umur tetap UNVERIFIED, tidak ada perubahan. "
    "Bridge read-only: 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Scan leg FAST-FAIL: pre-flight ankr_getLogs HTTP 401 Unauthorized (salvage; Ankr auth/paid-gate kembali - BUKAN timeout egress seperti 0001); watermark TETAP 134086385; gap ~266.518 blok (head 134352903) dan terus membesar; scan chain-wide TIDAK diluncurkan run ini (run sudah di batas 420 dtk; gap ditangani backfill driver). "
    "Sweep rute 3/5b/6 (subagent): 0 proyek baru terverifikasi <24 jam. Square: post relevan terbaru 31 Okt; Odaily flash 18 Nov 23:10-00:58 WIB tanpa item Agent ID; PANews tanpa item; DappBay kurasi lama tanpa free-mint baru. "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan reportable baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
