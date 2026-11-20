#!/usr/bin/env python3
"""Merge run 2026-11-19 00:01 WIB partial re-read into onchain-snapshot.json (lean merge).
Driver 0001 killed at 420s (EXIT 124, RPC degraded); retry killed at 360s (39/63 chunks);
resume killed at 300s during shape-check. Reread JSON has 51/63 items with fresh values
at block 134349577; 12 items all-null (Abyssora, APGB V1, Velko Rig, Crown, Longge,
DGF CARD, THE WALL, AgentPepe, Hivebyte, E5F8, ARKT-8334, TRIAGE-df6b) + bsccat/pepe
all-null - nulls NEVER overwrite; lastReadWib updated ONLY for items with >=1 int value.
Interval ~38.1 min derived from block delta (134349577-134344503 = 5074 blocks x 0.45s).
Prev reread = run 2331. No triage file this run (Boltbook 0 new). Sourcify feed leg
timed out in this run; cross-check via hot-leg 2354 (seen stayed 16753 -> 0 new, 0 shape hits).
Read-only except snapshot."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-2331-reread.json")) if False else None
reread = json.load(open(f"{HF}/run-2026-11-19-0001-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-2331-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-19 ~00:01 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 38.1
print(f"block {BLOCK} interval {INTERVAL_MIN} min (from block delta 5074 x 0.45s)")
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
    snap["contracts"][key]["runNote0001_1119"] = text

note_by_name("STOCK AGENT", "Run 0001 (blok 134349577, interval ~38,1 mnt vs 2331): totalSupply 815->818 (+3), freeLeft 296->293 (FREE_SUPPLY 1111, inferred free 818/1111 = 73,6% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. mintOpen 1, quote_user_1 0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (+3 <20).")
note_by_name("Lumenhold", "Run 0001: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 0001: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note_by_name("THYRK", "Run 0001: freeMinted 4318/7777 = 55,5% FLAT (<70%), totalSupply FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("Vitaliq Scans", "Run 0001: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~17 jam, TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 0001: totalSupply 1264 FLAT vs 2331, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("CAT402", "Run 0001: freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note_by_name("Bubblebruin", "Run 0001: totalSupply 2627 FLAT, freeClaimed 2621/7777 = 33,7% -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("ARKYN", "Run 0001: totalMinted 2303->2306->2315 (+9 vs 2331) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 0001: totalSupply 804->809->818 (+9 vs 2331) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("ALIEN", "Run 0001: totalSupply 508->511 (+3) -> velocity GAGAL. Bukan kandidat.")
note_by_name("SPARKS", "Run 0001: totalSupply 1217->1219 (+2) -> velocity GAGAL. Bukan kandidat.")
note_by_name("CPASS", "Run 0001: totalMinted 1788->1789 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("MORFO", "Run 0001: totalMinted 1135->1136 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("EIM", "Run 0001: totalMinted 807->808 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("Zephyra", "Run 0001: totalMinted 1023->1024 (+1) -> velocity GAGAL. Bukan kandidat.")
note_by_name("Compasyn", "Run 0001: totalSupply 1103 FLAT, freeClaimed 1098 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("PunchCard", "Run 0001: totalSupply 1362 FLAT (freeMinted/paidMinted baca OK run ini: nilai dipertahankan dari snapshot bila null). Velocity GAGAL. Bukan kandidat.")
note_by_name("Matrix", "Run 0001: totalSupply/freeMinted FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("AGCLUB", "Run 0001: totalMinted/freeMinted FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("REOPIR", "Run 0001: totalSupply/freeClaimed 598 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("Mine Card", "Run 0001: totalSupply/totalMinted 1390 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("PUNNY", "Run 0001: freeMinted 379/999 = 37,94% FLAT, mintClosed=1 (age-exclusion sudah dilaporkan 20:34 18 Nov; entri sudah dihapus dari snapshot - note ini miss bila key tidak ada).")
note_by_name("AgentPepe", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - nilai lama dipertahankan, BUKAN perubahan. Tetap watchlist-only-age-unverified.")
note_by_name("Hivebyte", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - nilai lama dipertahankan, BUKAN perubahan. Tetap watchlist-only-age-unverified.")
note_by_name("DGF CARD", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - nilai lama dipertahankan, BUKAN perubahan. Tetap EARLY LEAD.")
note_by_name("THE WALL", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - nilai lama dipertahankan, BUKAN perubahan.")
note_by_name("E5F8", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - status watchlist-only-mint-open-no-public-mint-2026-11-18 dari 2331 dipertahankan.")
note_by_name("ARKT-8334", "Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - status watchlist-only-first-mints-2026-11-18 dari 2331 dipertahankan.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["note0001"] = ("Run 0001 (blok 134349577): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang. Entry dipertahankan dengan status minted-by-user.")
    print("AONE note updated: still SOLD OUT 10000/10000 (no fresh read values changed)")
else:
    print("AONE MISSING from track_c!")

# ---- RigForge track-C: still not open ----
rf = snap.setdefault("track_c", {}).get("RigForge")
if isinstance(rf, dict):
    rf["note0001"] = ("Run 0001 (blok 134349577): freeSharesLeft 621 FLAT vs 2331, "
        "openedAt tetap 0 (belum buka), freeClaimed 379 FLAT. Tetap belum buka; bukan lead/kandidat.")
    print("RigForge note updated: freeSharesLeft 621 FLAT, openedAt 0")

# ---- bsccat / PEPE: NO fresh read this run (RPC degraded) - values kept, notes only ----
bs = snap.setdefault("track_c", {}).get("bsccat")
if isinstance(bs, dict):
    bs["note0001"] = ("Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - "
        "freeMinted terakhir 545 (run 2331) dipertahankan, BUKAN perubahan. Tetap watchlist-only-age-unverified.")
    print("bsccat note updated: no fresh read")
pe = snap.setdefault("track_c", {}).get("PEPE")
if isinstance(pe, dict):
    pe["note0001"] = ("Run 0001: TIDAK ADA BACAAN SEGAR (RPC degraded, 3x timeout; semua view null) - "
        "freeMinted terakhir 500 FLAT (run 2331) dipertahankan, BUKAN perubahan. Minted-by-user.")
    print("PEPE note updated: no fresh read")

# ---- Track-B pending: binanceai.fun ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote0001"] = ("Run 0001 (blok 134349577): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-19 00:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "0 perubahan status reportable; velocity 0 LOLOS (maks +9 ARKYN/AgentNOVA, interval ~38,1 mnt). STOCK AGENT +3 (inferred 73,6%) - tetap EARLY LEAD; "
    "Lumenhold 83,9% FLAT tapi umur UNVERIFIED; Vitaliq umur ~17 jam terverifikasi <24 jam (deadline ~07:00 WIB 19 Nov). "
    "Boltbook EN+ZH OK 200 (44.897/43.199 byte, 7 alamat, free_kw 6/4) - 0 alamat baru (semua di hot-leg-seen/snapshot). "
    "Sweep: 0 proyek baru terverifikasi <24 jam; AGENT MUSE age-excluded (buka 13 Nov); GANG AGENT sinyal lemah (tanpa kontrak/situs/launch); Square/Odaily/PANews/DappBay 0 item baru. "
    "Driver + retry + resume SEMUA kena timeout (RPC/egress degraded parah malam ini); re-read parsial 51/63 item; 12 item + bsccat/pepe tanpa bacaan segar (nilai lama dipertahankan). "
    "Sourcify feed leg timeout di run ini; cross-check hot-leg 2354: seen tetap 16753 -> 0 baru, 0 shape hit. "
    "Scan leg FAST-FAIL (pre-flight egress timeout, BUKAN 401); watermark TETAP 134086385.")
snap["runNote0001_1119"] = (
    "Run 0001 (interval ~38,1 mnt vs 2331 dari delta blok 5074 x 0,45 dtk; blok 134349577): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "0 perubahan status reportable. "
    "DEGRADASI RPC/EGRESS PARAH: driver 0001 killed 420 dtk (EXIT 124, pre-flight egress timeout + chunk 1-20 TimeoutError); "
    "retry killed 360 dtk (39/63 chunk, hasil parsial terselamatkan via incremental persist); resume killed 300 dtk saat shape-check; "
    "legs-script 5a+bridge killed 180 dtk (Sourcify via tunnel ikut timeout). Re-read akhir: 51/63 item bernilai segar; "
    "12 item all-null (Abyssora, APGB V1, Velko Rig, Crown, Longge, DGF CARD, THE WALL, AgentPepe, Hivebyte, E5F8, ARKT-8334, TRIAGE-df6b) "
    "dan bsccat/pepe all-null - nilai lama dipertahankan, BUKAN perubahan; lastReadWib hanya di-update untuk item bernilai segar. "
    "Scan leg FAST-FAIL: pre-flight ankr_getLogs GAGAL setup OSError 'batch failed on all healthy endpoints: timed out' (egress-wide, BUKAN 401); "
    "watermark TETAP 134086385; gap ~263.192 blok (head 134349577) dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan). "
    "Velocity: 0 LOLOS - maks +9 ARKYN (totalMinted 2306->2315) dan +9 AgentNOVA (totalSupply 809->818), +3 ALIEN, +3 STOCK AGENT, +2 SPARKS, +1 CPASS/MORFO/EIM/Zephyra - semua <20 token. "
    "STOCK AGENT totalSupply 815->818 (+3), freeLeft 296->293, inferred free 818/1111 = 73,6% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: Lumenhold freeClaimed 1259/1500 = 83,9% FLAT. "
    "Ledgera 54,1% FLAT, Bubblebruin 33,7% FLAT, CAT402 sold out 100/100, HIVE 1264 FLAT (minted-by-user), THYRK freeMinted 4318/7777 = 55,5% FLAT (<70%). "
    "Vitaliq Scans: genesisStart 07:00 WIB 18 Nov (umur ~17 jam TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). RigForge freeSharesLeft 621 FLAT, openedAt tetap 0 (belum buka). "
    "bsccat/pepe: TIDAK ADA BACAAN SEGAR run ini (nilai 545/500 dari 2331 dipertahankan). "
    "Boltbook EN+ZH HTTP 200 (44.897/43.199 byte, 7 alamat, free_kw 6/4) - 0 alamat BARU (semua sudah di hot-leg-seen dan/atau snapshot). "
    "Sourcify feed 5a: TIMEOUT di run ini (legs-script killed 180 dtk); cross-check hot-leg 2354: hot-leg-seen tetap 16753 sesudah seen-write -> 0 kontrak feed/Boltbook baru, 0 shape hit S1/S2. "
    "Bridge read-only: 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Sweep rute 3/5b/6 (subagent): 0 proyek baru terverifikasi <24 jam. Nama segar: AGENT MUSE ($MUSE, agentmuse.fcfs.workers.dev) - dibuka 13 Nov 06:00 WIB, umur ~6 hari -> AGE-EXCLUDED (tidak dilaporkan, tidak masuk snapshot: tanpa alamat kontrak di post/situs, host workers.dev bukan bukti situs proyek); "
    "GANG AGENT (IG @hanirami2022, 3.822/10.000 unit) - tanpa URL situs, tanpa alamat kontrak, tanpa tanggal launch -> umur UNVERIFIED, sinyal lemah, dicatat runlog saja (tanpa kontrak tak bisa masuk snapshot); "
    "Agentic Gangster sold out 10 Nov; RIGBYPASS age-excluded; PUNCH IN / DREADNOUGHT sinyal lemah tanpa kontrak; 42 Agentic Pass COMING SOON; GLOOP sold out. "
    "Square: post terbaru 2-5 Nov, tanpa post segar 18-19 Nov. Odaily-PANews: 0 item Agent ID/free-mint. DappBay: 122 entri AI, tanpa kecocokan nama segar (absen bukan bukti). "
    "Binance Agent ID Hackathon diumumkan 18 Nov (pendaftaran s.d. 9 Des, hadiah 60.000 USDC) - bukan mint, dicatat sebagai konteks. "
    "LAPORAN: DIAM (tidak ada kandidat/lead/perubahan reportable baru)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
