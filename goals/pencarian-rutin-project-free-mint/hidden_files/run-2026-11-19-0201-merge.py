#!/usr/bin/env python3
"""Merge run 2026-11-19 02:01 WIB lean re-read into onchain-snapshot.json.
Driver A run-2026-11-19-0201.py: pre-flight 401 fast-fail + leg-4 re-read
FOKUS 15/15 fresh, 0 chunk errors, block 134364150, 117 calls, 95.8s +
Boltbook EN/ZH. Driver B run-2026-11-19-0201-legs.py: Sourcify feed 20,
5 shape-checked, 0 S1/S2 + bridge + pre-flight 401. Sweep subagent:
0 proyek baru terverifikasi <24 jam; semua hit 'baru' sudah dikenal job ini
(Pocket Ai age-excluded 16 Nov; Agent Vein track_c checked-not-sale-shape;
Xigo sudah excluded; JINCHAN sold-out 8 Nov; DGF CARD umur kini
TERVERIFIKASI TUA via Boltbook post blok 131707996 -> age-excluded run ini).
Nulls NEVER overwrite; lastReadWib updated ONLY for items with >=1 int value.
Interval ~59.2 min from block delta (134364150-134356258 = 7892 x 0.45s).
Prev reread = run 0101 (lesson 0101: prev WAJIB reread run sebelumnya)."""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-0201")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0201-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-19-0101-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-19 ~02:01 WIB"
BLOCK = reread.get("block")
INTERVAL_MIN = 59.2
print(f"block {BLOCK} interval {INTERVAL_MIN} min (delta 7892 x 0.45s)")
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
    snap["contracts"][key]["runNote0201_1119"] = text

note_by_name("STOCK AGENT", "Run 0201 (blok 134364150, interval ~59,2 mnt vs 0101): totalSupply 818->820 (+2), freeLeft 293->291 (FREE_SUPPLY 1111, inferred free 820/1111 = 73,8% - INFERENSI totalSupply saja; freeMinted/freeClaimed revert = BUKAN counter terverifikasi, umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. mintOpen 1, quote_user_1 0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0. Velocity GAGAL (+2 <20).")
note_by_name("Lumenhold", "Run 0201: freeClaimed 1259/1500 = 83,9% FLAT, totalSupply 1264 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note_by_name("Ledgera", "Run 0201: freeClaimed 2707/5000 = 54,1% FLAT, totalSupply 2714 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("THYRK", "Run 0201: freeMinted 4318/7777 = 55,5% FLAT, totalSupply 4419 FLAT -> velocity GAGAL. Bukan kandidat/strong lead.")
note_by_name("Vitaliq Scans", "Run 0201: totalSupply err (revert - fungsi tidak ada), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~19 jam, TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov - kurang dari 5 jam lagi), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note_by_name("HIVE Agents", "Run 0201: totalSupply 1264 FLAT vs 0101, balanceOf(user)=1, minted-by-user. DIAM.")
note_by_name("Bubblebruin", "Run 0201: totalSupply 2627->2628 (+1), freeClaimed 2622/7777 = 33,7% FLAT -> velocity GAGAL. Minted-by-user, bukan kandidat. DIAM.")
note_by_name("ARKYN", "Run 0201: totalMinted 2326->2328 (+2) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("AgentNOVA", "Run 0201: totalSupply 828->835 (+7) -> velocity GAGAL (<20). Bukan kandidat.")
note_by_name("Matrix", "Run 0201: freeMinted 642 FLAT, totalSupply 636 FLAT -> velocity GAGAL. Bukan kandidat.")
note_by_name("AGCLUB", "Run 0201: totalMinted/freeMinted 530 FLAT (FREE_CAP 888 = 59,7%) -> velocity GAGAL. Bukan kandidat.")

# ---- AONE track-C: still SOLD OUT (already reported at 2131) ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["note0201"] = ("Run 0201 (blok 134364150): freeMinted tetap 10000/10000 = FREE POOL SOLD OUT "
        "(sudah dilaporkan sekali di run 2131; kuota user sudah 0 - minted-by-user 18:17 WIB). "
        "Tidak dilaporkan ulang.")
    print("AONE note updated: still SOLD OUT 10000/10000")
else:
    print("AONE MISSING from track_c!")

# ---- RigForge track-C: still not open ----
rf = snap.setdefault("track_c", {}).get("RigForge")
if isinstance(rf, dict):
    rf["note0201"] = ("Run 0201 (blok 134364150): freeSharesLeft 621 FLAT vs 0101, "
        "openedAt tetap 0 (belum buka), freeClaimed 379 FLAT. Tetap belum buka; bukan lead/kandidat.")
    print("RigForge note updated: freeSharesLeft 621 FLAT, openedAt 0")

# ---- Agent Vein track-C: sweep site reading, status UNCHANGED ----
av = snap.setdefault("track_c", {}).get("Agent Vein")
if isinstance(av, dict):
    av["note0201"] = ("Run 0201 (blok 134364150): sweep rute 3/5b membaca situs agent-miner-vein.vercel.app: "
        "counter situs 177/1000 free share (naik +5 dalam ~3 hari menurut crawl lama) - counter SITUS, bukan on-chain; "
        "semua view sale on-chain tetap revert (run 2331) -> S1 tetap FALSE, umur tetap UNVERIFIED. "
        "Status tetap checked-not-sale-shape-2026-11-18; bukan lead/kandidat; tanpa promosi.")
    print("Agent Vein note updated (sweep site reading, status unchanged)")

# ---- bsccat / PEPE (track_c): fresh reads this run ----
bs = snap.setdefault("track_c", {}).get("bsccat")
bv = reread.get("bsccat", {}).get("views", {})
if isinstance(bs, dict):
    if isinstance(bv.get("freeMinted"), int):
        bs["freeMinted"] = bv["freeMinted"]
    bs["lastReadWib"] = NOW
    bs["note0201"] = ("Run 0201 (blok 134364150): bacaan segar - freeMinted 546 FLAT vs 0101, "
        "totalSupply 546e27, view lain revert. BUKAN perubahan reportable. Tetap watchlist-only-age-unverified.")
    print("bsccat note updated: freeMinted", bv.get("freeMinted"))
pe = snap.setdefault("track_c", {}).get("PEPE")
pv = reread.get("pepe", {})
if isinstance(pe, dict):
    pe["lastReadWib"] = NOW
    pe["note0201"] = ("Run 0201 (blok 134364150): bacaan segar - freeMinted 500 FLAT, soldShares 501, "
        "FREE_SHARES 500, opened 0, hasMinted(user)=1. BUKAN perubahan. Minted-by-user.")
    print("PEPE note updated: freeMinted 500 FLAT")

# ---- Track-B pending: binanceai.fun ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote0201"] = ("Run 0201 (blok 134364150): launched=0, failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

# ---- Pocket Ai: sweep re-found it; already age-excluded 2026-11-16 -> silent ----
pk = snap.get("contracts", {}).get("PocketAi")
if isinstance(pk, dict):
    pk["runNote0201_1119"] = ("Run 0201: sweep rute 3/5b menemukan lagi Pocket Ai (situs + kontrak sama). "
        "SUDAH age-excluded 2026-11-16 (merkle root 12 Nov mencakup paid mint -> umur >=4 hari) - DIAM, tanpa aksi, tanpa laporan ulang. "
        "Entri duplikat 'POCKET' (watchlist-only-age-unverified-2026-11-12, kontrak sama) dibiarkan apa adanya run ini.")
    print("PocketAi note updated (already age-excluded, silent)")

# ---- DGF CARD: AGE-EXCLUDED run ini (early lead reported 18 Nov 12:31 -> ditutup) ----
dgf_key = "DGF CARD"
dgf = snap.get("contracts", {}).pop(dgf_key, None)
if isinstance(dgf, dict):
    excl = snap.setdefault("excluded", {})
    excl["DGF CARD"] = {
        "address": dgf.get("address"),
        "name": "DGF CARD",
        "status": "excluded-age-2026-11-19",
        "website": dgf.get("website"),
        "ageEvidence": ("Boltbook post https://boltbook.fun/p/j0LD38izwuvR?lang=en (dibaca ulang parent run 0201): "
            "totalMinted 376 pada blok 131707996; blok itu ~5 Nov 2026 menurut dating blok dari head 134364150 @ 19 Nov 02:05 WIB "
            "(delta 2.656.154 blok x 0,45 dtk ~= 13,8 hari; toleransi +-1 hari tetap >>24 jam) -> minting sudah berjalan selambatnya ~5 Nov, "
            "umur >=13 hari pada 19 Nov -> AGE-EXCLUDED. Early lead dilaporkan sekali 18 Nov 12:31; penutupan ini dilaporkan sekali run 0201."),
        "previousStatus": dgf.get("status"),
        "totalMintedAtRemoval": dgf.get("totalMinted"),
        "removedWib": NOW,
    }
    print("DGF CARD AGE-EXCLUDED: removed from contracts, added to excluded")
else:
    print("DGF CARD not in contracts (already removed?)")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-19 02:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
    "1 PERUBAHAN REPORTABLE: DGF CARD age-excluded (early lead 18 Nov 12:31 ditutup; umur >=13 hari via totalMinted 376 @ blok 131707996 ~5 Nov). "
    "Velocity 0 LOLOS (maks +7 AgentNOVA, interval ~59,2 mnt). STOCK AGENT inferred 73,8% FLAT - tetap EARLY LEAD; "
    "Lumenhold 83,9% FLAT tapi umur UNVERIFIED; Vitaliq umur ~19 jam terverifikasi <24 jam (deadline ~07:00 WIB 19 Nov). "
    "Boltbook EN+ZH OK 200 (44.715/43.036 byte, 7/7 alamat mentah, 6 unik) - 0 alamat baru vs hot-leg-seen/snapshot/track_c. "
    "Sourcify feed 20 baru, 5 shape-checked, 0 shape hit S1/S2. Sweep: 0 proyek baru terverifikasi <24 jam; semua hit sudah dikenal "
    "(Pocket Ai age-excluded 16 Nov; Agent Vein checked-not-sale-shape; Xigo sudah excluded; JINCHAN sold-out 8 Nov; AGIO bukan free-mint langsung). "
    "Scan leg FAST-FAIL (pre-flight Ankr HTTP 401 Unauthorized - auth/paid-gate, BUKAN timeout egress); watermark TETAP 134086385; gap ~277.765 blok.")
snap["runNote0201_1119"] = (
    "Run 0201 (interval ~59,2 mnt vs 0101 dari delta blok 7892 x 0,45 dtk; blok 134364150): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "1 PERUBAHAN REPORTABLE: DGF CARD AGE-EXCLUDED - early lead (dilaporkan sekali 18 Nov 12:31) DITUTUP run ini: "
    "bukti umur = Boltbook post https://boltbook.fun/p/j0LD38izwuvR?lang=en (dibaca ulang parent run 0201): totalMinted 376 pada blok 131707996; "
    "blok itu ~5 Nov 2026 menurut dating blok dari head 134364150 @ 19 Nov 02:05 WIB (delta 2.656.154 blok x 0,45 dtk ~= 13,8 hari; toleransi +-1 hari tetap >>24 jam) "
    "-> minting sudah berjalan selambatnya ~5 Nov, umur >=13 hari -> AGE-EXCLUDED; entri dihapus dari snapshot contracts, dipindah ke excluded. "
    "Split-driver pattern BEKERJA: driver A run-2026-11-19-0201.py (pre-flight + leg-4 re-read FOKUS 15/15 item bernilai segar, 117 calls, 0 chunk error, 95,8 dtk + Boltbook EN/ZH tersimpan) "
    "selesai TANPA kill 420 dtk; driver B run-2026-11-19-0201-legs.py (88,5 dtk) menyelesaikan Sourcify + shape-check + bridge + pre-flight. "
    "Velocity: 0 LOLOS - maks +7 AgentNOVA (totalSupply 828->835), +2 ARKYN (totalMinted 2326->2328), +2 STOCK AGENT (818->820), +1 Bubblebruin (2627->2628); sisanya 0/FLAT - semua <20 token. "
    "STOCK AGENT totalSupply 820, freeLeft 291, inferred free 73,8% (INFERENSI totalSupply, freeMinted/freeClaimed revert; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Lumenhold freeClaimed 1259/1500 = 83,9% FLAT (umur UNVERIFIED -> BUKAN strong lead). Ledgera 54,1% FLAT, THYRK 55,5% FLAT, Matrix 642 FLAT, AGCLUB 59,7% FLAT, HIVE 1264 FLAT, Bubblebruin 33,7% FLAT. "
    "Vitaliq Scans: genesisStart 07:00 WIB 18 Nov (umur ~19 jam TERVERIFIKASI <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov - kurang dari 5 jam lagi), free%/website UNVERIFIED -> tetap EARLY LEAD. "
    "PUNNY: totalMinted/freeMinted 379 FLAT, mintClosed=1 - age-exclusion SUDAH dilaporkan 20:34 WIB 18 Nov dan entri sudah dihapus dari snapshot; tidak ada aksi. "
    "AONE freeMinted tetap 10000/10000 SOLD OUT (sudah dilaporkan 2131 - tidak dilaporkan ulang). RigForge freeSharesLeft 621 FLAT, openedAt tetap 0 (belum buka). "
    "bsccat: bacaan segar freeMinted 546 FLAT. PEPE: freeMinted 500 FLAT, opened 0, hasMinted(user)=1. "
    "Boltbook EN+ZH HTTP 200 (44.715/43.036 byte, 7/7 alamat mentah termasuk duplikat case, 6 unik, free_kw 2/0) - 0 alamat BARU vs hot-leg-seen/snapshot/track_c "
    "(0x1FE0.../0x4158.../0x5b63... sudah di hot-leg-seen; 0x9b0c... = hero AONE; 0x0b0b... 0101 sudah rotasi keluar). "
    "Sourcify feed 5a: HTTP 200, 20 kontrak baru (verifiedAt s.d. 19:04:17Z), 5 shape-checked (4 feed baru + YAMA re-check): 0 S1, 0 S2. YAMA re-check: S1/S2 FALSE (agent_ref FALSE) - tetap bukan lead track C. "
    "Bridge read-only: 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "Scan leg FAST-FAIL: pre-flight ankr_getLogs HTTP 401 Unauthorized (KEDUA driver; Ankr auth/paid-gate - BUKAN timeout egress); watermark TETAP 134086385; gap ~277.765 blok (head 134364150) dan terus membesar; scan chain-wide TIDAK diluncurkan; gap ditangani backfill driver. "
    "Sweep rute 3/5b/6 (subagent read-only): 0 proyek baru terverifikasi <24 jam. Hit 'baru' subagent SEMUA sudah dikenal job ini: Pocket Ai (age-excluded 16 Nov, DIAM), "
    "Agent Vein (track_c checked-not-sale-shape; counter situs 177/1000 free share dicatat, on-chain tetap revert -> tanpa promosi), Xigo (sudah di excluded), "
    "JINCHAN (sold-out-free 8 Nov, terminal), AGIO (free share berkondisi tesis, tanpa kontrak di homepage, bukan free-mint langsung). "
    "Square: post relevan terbaru 1-5 Nov, tanpa post baru <24 jam; pengumuman Agent ID Hackathon 18 Nov-9 Des (ekosistem, bukan free-mint). "
    "Odaily newsflash 19 Nov ~02:05 WIB + PANews: tanpa item Agent ID/free-mint. DappBay kategori AI: kurasi umum, tanpa free-mint baru. "
    "LAPORAN: 1 perubahan reportable (DGF CARD age-excluded); selain itu DIAM."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT SAVED")
