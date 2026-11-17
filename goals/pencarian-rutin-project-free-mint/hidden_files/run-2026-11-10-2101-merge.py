#!/usr/bin/env python3
"""Merge run 2101 reread+vel+target+probe+discovery into snapshot. FRESH for run 2101 only.
Run 2101 (jadwal 21:01 WIB, dieksekusi ~21:01-21:3x WIB). Block re-read: 132789581.
Reread 675 kontrak + 85 track_c (930.5 dtk, bsc-dataseed; Ankr tidak dipakai).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2101"
BLOCK = 132789581
NOW = "2026-11-10 21:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
tgt = json.load(open(f"{BASE}/run-{TS}-target.json"))
probe = json.load(open(f"{BASE}/run-{TS}-probe.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2101-premerge")

updated = 0
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name)
    if not f:
        continue
    row = vel.get("rows", {}).get(name, {})
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    if row.get("minted") is not None:
        entry["previousTotalSupply"] = row.get("prev")
        entry["mintedInInterval"] = row.get("minted")
        entry["intervalMinutes"] = INTERVAL
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1
print(f"contracts updated: {updated}")

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote2101_1110"] = text

def dyn_note(name, extra_txt=""):
    row = vel.get("rows", {}).get(name, {})
    f = rr.get("reread", {}).get(name, {})
    e = snap["contracts"].get(name, {})
    if not row:
        return None
    minted = row.get("minted"); rate = row.get("rate"); ratio = row.get("ratio")
    passes = row.get("passes")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    cap = e.get("FREE_SUPPLY") or e.get("FREE_CAP") or e.get("agentFreeCap") or e.get("MAX_SUPPLY")
    freetxt = ""
    if fm is not None and cap and cap < 10**12:
        freetxt = f"; freeMinted {fm}/{cap} = {fm/cap*100:.1f}%"
    elif fc is not None and cap and cap < 10**12:
        freetxt = f"; freeClaimed {fc}/{cap} = {fc/cap*100:.1f}%"
    vtxt = "velocity LOLOS" if passes else "velocity GAGAL"
    return (f"Run 2101 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- KERNELMONK: minted by hot-leg run 20:59 WIB (reported 21:05 WIB) - reconcile, do NOT re-report ----
km = snap["contracts"].get("KERNELMONK")
if isinstance(km, dict):
    km["status"] = "minted-by-user-2026-11-10"
    km["mintTx"] = "0x15fbc506506d94ed9ef003056844d9f04b07dd2aef81ed6d61e59497af76a949"
    km["mintBlock"] = 132790036
    km["mintGas"] = 250029
    km["mintGasBnb"] = 0.0000238078
    km["mintTokenId"] = 509
    km["mintOrderId"] = 26111000002031777671
    km["agentFree"] = 517
    km["balanceOf_user"] = 1
    km["userBalance"] = 1
    km["runNote2101_1110"] = (
        "Run 2101: REKONSILIASI - KERNELMONK sudah di-mint HOT-LEG run 20:59 WIB "
        "(dilaporkan 21:05 WIB, TIDAK dilaporkan ulang run ini, TIDAK dieksekusi ulang). "
        "Tx 0x15fbc506506d94ed9ef003056844d9f04b07dd2aef81ed6d61e59497af76a949, blok 132790036, "
        "tokenId 509, gas 250029 (0,0000238078 BNB). Pasca-mint terverifikasi run ini: "
        "balanceOf(user)=1 (baca ulang 2x + kontrol alamat lain 0), totalSupply 518, "
        "agentFree 517/2000 = 25,85% (targeted read blok 132791737: status 517, freeLeft agent 1483). "
        "Rarity: #3444 Tier Scroll Carrier, Model Mist Courier, Rank 5. Marketplace: own market "
        "0xb8599513fb217c9a2A51BAe997E29ba516FE6268 fee 3%, listedCount 0 -> TIDAK ada listing live / "
        "TIDAK ada floor -> TIDAK di-list (aturan auto-list; Element fallback manual saja). "
        "Velocity run ini +44 (1,467/mnt, 0,47x) GAGAL - tidak relevan, slot sudah terpakai.")
    print("KERNELMONK reconciled as minted-by-user (hot-leg 2059)")

# ---- Lanternfield: PROMOTED early -> strong lead (free 31.4%), GATE FAILED -> no execution ----
lf = snap["contracts"].get("Lanternfield")
lp = probe.get("Lanternfield", {})
if isinstance(lf, dict):
    lf["status"] = "strong-lead-gate-failed-2026-11-10"
    lf["totalSupply"] = lp.get("totalSupply()") or lf.get("totalSupply")
    lf["totalMinted"] = lp.get("totalMinted()") or lf.get("totalMinted")
    lf["freeMinted"] = lp.get("freeMinted()") or lf.get("freeMinted")
    lf["freeRemaining"] = lp.get("freeRemaining()")
    lf["freePctVerified"] = 31.4
    lf["balanceOf_user"] = lp.get("balanceOf(address)")
    lf["freeMintedBy_user"] = lp.get("freeMintedBy(address)")
    lf["canFreeMint_user"] = lp.get("canFreeMint(address)")
    lf["freeAvailable_user"] = lp.get("freeAvailable(address)")
    lf["hasAgentId_user"] = lp.get("hasAgentId(address)")
    lf["freeRemainingFor_user"] = lp.get("freeRemainingFor(address)")
    lf["runNote2101_1110"] = (
        "Run 2101: PROMOSI early -> STRONG LEAD (dilaporkan sekali run ini sebagai strong lead + "
        "alasan gate, TIDAK di-preview/TIDAK di-mint). Probe segar: freeMinted 471/1500 = 31,4% "
        "(>=25%; run 2031 masih 251/1500 = 16,7%), totalSupply 470, freeRemaining 1027, "
        "saleStart 1794315653 = 2026-11-10 20:00:53 WIB (umur ~1,5 jam, <24 jam TERVERIFIKASI), "
        "slot user TERBUKA (balanceOf 0, freeMintedBy 0, canFreeMint 1, freeAvailable 1, "
        "hasAgentId 1, freeRemainingFor 1), owner 0x0. Velocity run ini +183 (6,1/mnt, 0,95x) GAGAL. "
        "MANDATORY WEBSITE GATE GAGAL: lanternfield.surge.sh placeholder Surge 404, TIDAK mencetak "
        "kontrak (dicek ulang run ini via run 2001/2031 - tetap unverified). X discussion UNVERIFIED. "
        "Tidak ada eksekusi selama gate gagal; promosi tercatat, pantauan lanjut.")
    print("Lanternfield promoted to strong lead (gate failed)")

note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") +
     " Early lead run 1931. Targeted read blok 132791735: status (463 minted, 0 paid, "
     "463 agentFree, 0 xFree); freeLeft agent 1537/2000 -> agentFree 463/2000 = 23,15% "
     "(<25% strong lead). Velocity GAGAL run ini (+46, 0,44x). Hot-leg 2119: pace 0 dalam 5 mnt. "
     "Website TERVERIFIKASI; slot user terbuka (bal 0). Tetap early lead; re-read prioritas run berikut.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") +
     " Minted-by-user: freeClaimed 2429/7777 = 31,2%. Tanpa aksi.")
note("Zapcourier", (dyn_note("Zapcourier") or "") +
     " Minted-by-user: freeClaimed 712/712 = 100% (free pool habis). Tanpa aksi.")
note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " Minted-by-user 2026-11-10 (#539); freeMinted 879/1111 = 79,1%. Tanpa aksi.")
note("Agentic", (dyn_note("Agentic") or "") +
     " Velocity GAGAL run ini. Gate FAILED (website) tetap berlaku; freeMinted segar 947/1000 "
     "vs freePctVerified lama 18,9% (189/1000) - INKONSISTENSI counter tetap ditandai, bukan kandidat.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Velocity GAGAL run ini (+76, 1,23x). Umur + free% UNVERIFIED. Tetap early lead.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead run 1901: +187 interval ini, velocity LOLOS (1,89x) TAPI TANPA promosi: "
     "free% + umur UNVERIFIED. Tetap early lead.")
note("ACOS-3aed", (dyn_note("ACOS-3aed") or "") +
     " +330 interval ini (11,0/mnt, 1,84x), velocity LOLOS TAPI TANPA promosi: umur/pct/"
     "website UNVERIFIED. Bukan early lead, bukan kandidat.")
note("Golden Agents", (dyn_note("Golden Agents") or "") +
     " Velocity GAGAL run ini (+6). Probe segar: totalSupply 1432, MAX_SUPPLY 100000, "
     "owner 0x931b0b8c6dafaef8719cbbb00815ce939a946a07, free views null, tanpa fungsi agent. "
     "Free% + umur + website UNVERIFIED. Tetap early lead, tanpa promosi.")

# ---- generic NEW-sellout detection (prev < cap <= fresh, per key, terminal skipped) ----
TERMINAL = ("sold-out", "soldout", "age-excluded", "excluded-", "minted-by-user")
new_sellouts = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("reread", {}).get(name, {})
    cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP") or entry.get("agentFreeCap")
    if not cap or cap >= 10**12:
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    for key in ("freeMinted", "freeClaimed"):
        prev = entry.get(key)
        fresh = f.get(key)
        if prev is not None and fresh is not None and prev < cap <= fresh:
            new_sellouts.append((name, key, prev, fresh, cap))
            entry["status"] = "sold-out-free-pool-exhausted-2026-11-10"
            entry["runNote2101_1110"] = (f"Run 2101 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS (generic):", new_sellouts if new_sellouts else "none")

# ---- MSTRACK 0xa37b: checked-not-lead (temuan Boltbook run ini, diverifikasi mendalam) ----
if "MacroSwap Tracker" not in snap.get("contracts", {}):
    snap["contracts"]["MacroSwap Tracker"] = {
        "address": "0xa37b3ff7a1cabf77256a4b246eba1652011e4569",
        "name": "MacroSwap Tracker", "symbol": "MSTRACK", "kind": "ERC721",
        "status": "checked-not-lead-2026-11-10",
        "totalSupply": 490, "owner": "0xb9d326a805c2b2ec5d129afef1990e71b213b938",
        "balanceOf_user": 0, "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "xVerified": False, "velocityVerified": False,
        "website": "https://macroswap.finance",
        "gate": "FAILED: no site prints the exact contract (contractURI external_link "
            "macroswap.finance + nft.macroswap.dev collection JSON do not print 0xa37b; "
            "macroswap.dev home also does not print it)",
        "launchNote": "Umur TIDAK diverifikasi (first-mint walkback mustahil: eth_getLogs -32005 "
            "di semua RPC publik; totalSupply 479 (run 2031 probe) -> 490 (run ini, +11/30 mnt, mint aktif). "
            "Bukan patokan umur.",
        "baselineNote": "Checked-not-lead run 2101 (temuan post Boltbook nicodart.ai 21:05 WIB: tx free mint "
            "0x63bfd15037c3c79583a55b720f19e95bb45e00f00123df13b9de4fd4a1e9618c, blok 132789137, "
            "receipt 1, mint() no-arg value 0 ke 0xa37b, tokenId = alamat minter). Verifikasi run ini: "
            "mint() no-arg nonpayable, eth_call dari wallet user SUKSES (return tokenId = alamat user) - "
            "slot user TERBUKA dan gratis (gas only). NAMUN BUKAN Free Bacot: (1) narasi BUKAN Agent ID - "
            "ini utility tracker MacroSwap (metadata: 'Non-transferable record of this wallet's buys and "
            "sells on MacroSwap... Does not represent any asset, right or promise of returns'); ABI tanpa "
            "fungsi agent/registry; (2) free-quota % TIDAK BISA diverifikasi (tanpa FREE_SUPPLY/cap); "
            "(3) website gate GAGAL (lihat gate). BUKAN early lead (bukan agent-mint-shaped: tanpa referensi "
            "agent apa pun di ABI; kaitan ke sale DogeKing hanya infrastruktur MacroSwap, dan token() sale "
            "0xd73a = 0xab36c1c92a3de7462b91306c63c63a4bd5317972, BUKAN 0xa37b - koreksi klasifikasi lama). "
            "Owner 0xb9d326a8... TIDAK ada di same-owner-discards.json (dicek run ini). TIDAK pernah "
            "di-preview/di-mint. Dicatat agar tidak ditemukan ulang.",
    }
    print("MSTRACK added as checked-not-lead")

# ---- DogeKing track_c: correct token address + fresh sale reads ----
dk = snap.get("track_c", {}).get("DogeKing")
if isinstance(dk, dict):
    dk["token"] = "0xab36c1c92a3de7462b91306c63c63a4bd5317972"
    dk["tokenCorrection2101"] = ("KOREKSI run 2101: token() sale 0xd73a dibaca langsung = "
        "0xab36c1c92a3de7462b91306c63c63a4bd5317972, BUKAN MSTRACK 0xa37b (0xa37b adalah NFT tracker "
        "MacroSwap terpisah, lihat entri MacroSwap Tracker).")
    dk["website"] = "https://dogeking.club"
    dk["x"] = "https://x.com/DogeKing_Agent"
    dk["saleStart"] = 1794308400
    dk["freeClaimed"] = 1000
    dk["isOpen"] = 0
    dk["runNote2101_1110"] = ("Run 2101: DogeKing sale tetap SOLD OUT (freeClaimed 1000/1000, isOpen 0, "
        "saleStart 1794308400 = 2026-11-10 18:00 WIB; website dogeking.club + x.com/DogeKing_Agent "
        "dibaca langsung run ini). BUKAN lead/kandidat. Koreksi token: lihat tokenCorrection2101.")
    print("DogeKing track_c corrected")

# ---- track_c generic lastRead updates ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("track_c", {}).get(name, {})
    if not f:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
tc1111 = snap.get("track_c", {}).get("11-11")
if isinstance(tc1111, dict):
    f1111 = rr.get("track_c", {}).get("11-11", {})
    if f1111.get("freeMinted") is not None:
        tc1111["freeMinted"] = f1111["freeMinted"]
        tc1111["runNote2101_1110"] = (f"Run 2101: freeMinted {f1111['freeMinted']}/1000. Umur + website "
            "tetap UNVERIFIED -> tetap watchlist-only, bukan lead.")

# ---- age-exclusion notes (aturan <24 jam): none new this run ----
snap["runNote2101_1110_age_exclusions"] = (
    "Run 2101 age-exclusions (aturan <24 jam): 0 BARU. Tidak ada entri non-terminal "
    "dengan launch/first-mint terverifikasi di jendela 2026-11-09 20:31-21:01 WIB yang "
    "melewati 24 jam run ini (dicek via launchNote/first-mint di snapshot). DITAHAN "
    "preseden run 1931 tetap berlaku (pool UNVERIFIED: HELIX, Beast16, Pressure, NUMBI, "
    "Lucky Cat, Meow Cards, BAHUANG3, Reel, Riddle Run, Gloop, Pixel Laptop; launch "
    "UNVERIFIED: KIJIN, Dragon Agent, Iron Bloom, Agentic, 0x13A1Ebc9-new, Shard Id, "
    "Sidecoo Season, STAR CARDS, JOLT).")

# ---- binanceai.fun: unchanged (refund phase) ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 2101"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~21:2x WIB"
    snap["binanceai_claim"]["block"] = tgt.get("block")
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 2101 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 2031. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote2101_1110"] = (
    "Run 2101 (2026-11-10 21:01-~21:3x WIB, blok re-read 132789581): re-read 675 kontrak + 85 track_c (930,5 dtk). "
    "KERNELMONK: SUDAH di-mint HOT-LEG run 20:59 WIB (tx 0x15fbc506506d94ed9ef003056844d9f04b07dd2aef81ed6d61e59497af76a949, "
    "blok 132790036, tokenId 509; dilaporkan hot-leg 21:05 WIB) - rekonsiliasi run ini (balanceOf user 1 terverifikasi 2x), "
    "TIDAK dilaporkan ulang, TIDAK dieksekusi ulang. STRONG LEAD BARU 1 (dilaporkan sekali run ini, GATE-BLOCKED, tanpa eksekusi): "
    "Lanternfield 0x9aab6e84 - freeMinted 471/1500 = 31,4% (>=25%), umur terverifikasi saleStart 20:00:53 WIB (~1,5 jam), "
    "slot user terbuka; MANDATORY WEBSITE GATE GAGAL (lanternfield.surge.sh placeholder 404, tidak mencetak kontrak). "
    "BYTEBLOOM 463/2000 = 23,15% (masih <25%, pace 0 - hot-leg 2119). MSTRACK 0xa37b checked-not-lead (utility tracker "
    "MacroSwap non-transferable, bukan narasi Agent ID, gate gagal, token sale DogeKing dikoreksi ke 0xab36c1...). "
    "EARLY LEAD BARU 0; SELLOUT BARU 0; AGE-EXCLUDED BARU 0. Velocity LOLOS 8 TANPA promosi (bridge-Wise Owl +24, Scarabswarm +43 "
    "discarded, ACOS-3aed +330, BNBRunnerz-2674 +49, SlimySlug +50, HackouCoinPass +128 minted-by-user, STALL +187, Dropnix +34 "
    "discarded). Scan leg FAST-FAIL (preflight Ankr 401, 2,9 dtk, head 132789535; watermark tetap 132512564; gap ~276.971 blok). "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah (116 kontrak; 6 alamat non-snapshot ditinjau: temuan 3-4 Nov, "
    "bukan lead, umur >24 jam, 1 same_owner_discarded - tidak ditambahkan/dilaporkan). 0 kandidat baru, 0 track-C lead/kandidat baru, "
    "0 track-B claim, 0 eksekusi oleh run ini.")
snap["runNote2101_1110_scan"] = (
    "Run 2101 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132789535), HTTP 401 Unauthorized "
    "dalam 2,9 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564; gap ke head ~276.971 blok dan tumbuh - milik backfill, ikut gagal 401). "
    "Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote2101_1110_discovery"] = (
    "Run 2101 discovery: Sourcify feed 20 terbaru (verified 13:45-14:04Z), 1 kontrak baru di-shape-check run ini "
    "(0x357d64f8: mint + agentId tanpa quote/free -> S1/S2 False), 19 lain sudah di hot-leg-seen. Boltbook EN+ZH via curl "
    "langsung (45.426/45.638 byte): 7 alamat, 1 'baru' 0x63bf... ternyata fragmen TX HASH post nicodart.ai (MSTRACK free mint, "
    "blok 132789137) - bukan kontrak; sisanya sudah di snapshot/hot-leg-seen. MSTRACK 0xa37b diverifikasi mendalam run ini "
    "(lihat entri MacroSwap Tracker): mint gratis terbuka tapi BUKAN Free Bacot (utility tracker, gate gagal). "
    "Sweep: Oathbots, Agentic Gangster, Hundred, AgentForge, Pixel Fox, PocketDragons, WNO, NOVRA, First-Dollar Grove - "
    "semua sudah di snapshot atau berumur >24 jam. Komplemen rute 6: Odaily newsflash 0 mention agent/free-mint; PANews/Square "
    "tanpa item baru; DappBay tidak dibutuhkan (tidak ada gate baru yang perlu dicek).")
snap["runNote2101_1110_binanceai"] = (
    "Run 2101 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132791746). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote2101_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
