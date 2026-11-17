#!/usr/bin/env python3
"""Merge run 2201 reread+vel+probes into snapshot. FRESH for run 2201 only.
Run 2201 (jadwal 22:01 WIB, dieksekusi ~22:23-23:0x WIB). Block re-read: 132799932.
Reread 677 kontrak + 85 track_c (676.4 dtk, bsc-dataseed; Ankr tidak dipakai).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2201"
BLOCK = 132799932
NOW = "2026-11-10 22:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
probe = json.load(open(f"{BASE}/run-{TS}-probe.json"))
newprobe = json.load(open(f"{BASE}/run-{TS}-newprobe.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2201-premerge")

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

tc_updated = 0
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    f = rr.get("track_c", {}).get(name)
    if not f:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if f.get(k) is not None:
            entry[k] = f[k]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = NOW
    tc_updated += 1
print(f"track_c updated: {tc_updated}")

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote2201_1110"] = text

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
    return (f"Run 2201 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- BYTEBLOOM: MINTED by this run (strong-lead direct mint) ----
bb = snap["contracts"].get("BYTEBLOOM")
if isinstance(bb, dict):
    bb["status"] = "minted-by-user-2026-11-10"
    bb["mintTx"] = "0x4ad8c90a91a0704fc08c2fd20cf13ca3a38f850e41a9651a617cd024097c5007"
    bb["mintOrderId"] = 26111000002031943545
    bb["mintBlock"] = 132801228
    bb["mintGas"] = 315168
    bb["mintGasBnb"] = 0.00002497
    bb["mintTokenId"] = 508
    bb["balanceOf_user"] = 1
    bb["userBalance"] = 1
    bb["totalSupply"] = 509
    bb["agentFreeUsed"] = 509
    bb["agentFreeByWallet_user"] = 1
    bb["claimable_user"] = 10000
    bb["runNote2201_1110"] = (
        "Run 2201: DI-MINT run ini (strong-lead direct mint, promosi early -> strong). Kaki strong lead "
        "saat probe segar: agentFreeUsed 505/2000 = 25,25% (>=25%), mintStart 1794313855 = 2026-11-10 19:30:55 WIB "
        "(umur ~2,7 jam TERVERIFIKASI <24 jam), slot terbuka (agentFreeByWallet 0, balanceOf 0, walletInfo "
        "[0, 20, 0, 1, 1, 1e22, 0]), mintOpen 1, freeLeft [1494, 1000]. Gate LULUS (website TERVERIFIKASI sejak "
        "run 1931, re-verifikasi run ini: bytebloom.pages.dev/llms.txt 760 byte mencetak kontrak persis 1x, "
        "identitas cocok: 5.555 supply, harga 0,0009 BNB, token PETAL, Seed Bazaar fee 3%). Audit Binance: "
        "hasResult=false (tanpa hasil, bukan lolos), isSupported true, riskLevel -1, tanpa RISK hit, riskAlert "
        "null. Same-owner-discards dicek: kontrak + payee 0x442F0C6F811AbF2c1970E00d0Fb6903000283030 bersih. "
        "Preview bersih 000000000 (mint(1) 0xa0712d68...0001, value 0, +1 ERC721 prediksi #508). Tx "
        "0x4ad8c90a91a0704fc08c2fd20cf13ca3a38f850e41a9651a617cd024097c5007, blok 132801228, gas 315168 "
        "(~0,00002497 BNB), tokenId 508. Pasca-mint: ownerOf(508) = wallet agent, balanceOf 0->1, "
        "agentFreeByWallet 0->1, agentFreeUsed 505->509, totalSupply 509. Rarity: tokenURI(508) on-chain = "
        "https://bytebloom.pages.dev/meta/2009.json, name 'BYTEBLOOM #2010', Tier 'Moss Tender' (verbatim proyek), "
        "Model Moss Lantern, Rank 5 (dicatat di nft-rarity-inventory.md — sudah tercatat hot-leg 22:09, tanpa "
        "duplikat). claimable(user) = 10.000 PETAL via claimRewards() - TIDAK di-claim run ini (di luar otorisasi; "
        "dilaporkan sebagai peluang). Marketplace: own market Seed Bazaar 0x8c1c800fc3079e9dea13a9c5f4c20d0e5e2f2675 "
        "(NFT() cocok, fee 3%) listedCount 0, sales 0, volume 0 -> TIDAK ada listing/floor live -> TIDAK di-list "
        "(aturan auto-list; Element fallback manual saja).")
    print("BYTEBLOOM reconciled as minted-by-user (run 2201)")

# ---- ORBITJANITOR: NEW EARLY LEAD (Boltbook ZH, verified on-chain by parent) ----
if "ORBITJANITOR" not in snap.get("contracts", {}):
    snap["contracts"]["ORBITJANITOR"] = {
        "address": "0x8d5a0555446d37afaba75e36da318646a4b32420",
        "name": "ORBITJANITOR", "symbol": "SWEEP", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-10",
        "totalSupply": 324, "MAX_SUPPLY": 4444, "PRICE": 1130000000000000,
        "agentFreeCap": 2000, "agentFreeUsed": 325, "agentFree": 325,
        "mintStart": 1794320692, "mintOpen": 1, "balanceOf_user": 0,
        "agentFreeByWallet_user": 0,
        "contractURI": "https://orbitjanitor.pages.dev/meta/collection.json",
        "website": "https://orbitjanitor.pages.dev",
        "firstSeenBlock": 132801228, "firstSeenWib": "2026-11-10 ~22:3x WIB",
        "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "gate": "website TERVERIFIKASI (metode H via contractURI): orbitjanitor.pages.dev/llms.txt 700 byte "
            "mencetak kontrak persis 1x; identitas cocok (4.444 supply, harga 0,00113 BNB, token DEBRIS, "
            "Salvage Bay fee 3%). X account: UNVERIFIED (tidak dicari run ini; X opsional, bukan gate).",
        "runNote2201_1110": (
            "Run 2201 EARLY LEAD BARU (dilaporkan sekali run ini; TIDAK di-preview/TIDAK di-mint - tier early). "
            "Ditemukan via Boltbook ZH (post 1328.ai, ~22:2x WIB, SWEEP #161 gas-only). Verifikasi on-chain parent: "
            "template SMITH (AGENT_FREE_CAP, agentFreeUsed, freeLeft, mintStart, mintOpen), REGISTRY() = "
            "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry Binance, cocok), totalSupply 324, agentFreeUsed "
            "325/2000 = 16,25% (<25% strong lead, <50% kandidat), mintStart 1794320692 = 2026-11-10 21:24:52 WIB "
            "(umur ~1,1 jam TERVERIFIKASI <24 jam), mintOpen 1, freeLeft [1675, 1000], slot user TERBUKA "
            "(agentFreeByWallet 0, balanceOf 0). Website TERVERIFIKASI (lihat gate). Pantauan lanjut untuk promosi "
            "ke strong lead bila free% >=25%."),
    }
    print("ORBITJANITOR added as early lead")

# ---- GEM: UPCOMING only (Boltbook ZH, opens tomorrow) ----
if "GEM" not in snap.get("contracts", {}):
    snap["contracts"]["GEM"] = {
        "address": "0xbeb8833c5a5290678e67af65a4c12f9402ba404f",
        "name": "GEM", "symbol": "GEM", "kind": "ERC20-mining",
        "status": "upcoming-2026-11-10",
        "website": None,
        "firstSeenWib": "2026-11-10 ~22:2x WIB",
        "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "runNote2201_1110": (
            "Run 2201 UPCOMING-ONLY (dilaporkan sebagai watchlist, BUKAN kandidat, TIDAK di-preview/TIDAK di-mint). "
            "Ditemukan via Boltbook ZH (post mamana.ai ~22:18 WIB): GEM PoW mining, round 1 baru buka BESOK "
            "2026-11-11 19:30 WIB, 200.000 GEM per epoch 30 menit, max 99 tickets. On-chain discovery: token "
            "Sourcify exact_match, started=0, epoch=0, seed=0 (belum mulai). Pantau saat launch; tidak ada eksekusi "
            "sampai benar-benar launch + kontrak + kuota gratis terverifikasi on-chain."),
    }
    print("GEM added as upcoming-only")

# ---- SALE-6B39: track-C checked, NOT a lead (sold out + paid-only) ----
tc = snap.setdefault("track_c", {})
if "0x6B39c561b187F8Bc2aA05323A5E74Fd60BE64d7b" not in tc:
    tc["0x6B39c561b187F8Bc2aA05323A5E74Fd60BE64d7b"] = {
        "address": "0x6B39c561b187F8Bc2aA05323A5E74Fd60BE64d7b",
        "name": "sale-6B39", "kind": "track-c-sale",
        "status": "checked-not-lead-2026-11-10",
        "token": "0x885ea3bc8a89c6500c75f9d3e0e4a7ec943eb1c0",
        "pair": "0xc96325efc39141e91bc13b78496cbfefbcc02c51",
        "opened": 1, "totalMinted": 4000, "MAX_SHARES": 4000,
        "PRICE": 3000000000000000, "TOKENS_PER_SHARE": 75000000000000000000000,
        "BASE_QUOTA": 10, "remainingFor_user": 0,
        "firstSeenWib": "2026-11-10 ~22:2x WIB",
        "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "runNote2201_1110": (
            "Run 2201 CHECKED-NOT-LEAD (tidak dilaporkan sebagai lead/kandidat, tidak di-preview/di-mint). "
            "Ditemukan via Sourcify feed (verifiedAt 2026-11-10 15:25:07Z = 22:25 WIB). Shape-check: sale-shape "
            "S1 parsial (mint + previewMint + registry Binance cocok + opened 1), TAPI totalMinted 4000 = MAX_SHARES "
            "4000 (SOLD OUT), previewMint(user,1) = (0, 0,003 BNB, 75.000 token) -> TIDAK ada jalur gratis untuk "
            "user (cost 0,003 BNB, remainingFor(user) 0), totalRaised 12 BNB. Paid-only + sold out -> bukan lead "
            "track-C. Dicatat agar tidak dicek ulang."),
    }
    print("SALE-6B39 recorded as checked-not-lead")

# ---- SOLDERCATS: still early, progress update ----
sc = snap["contracts"].get("SOLDERCATS")
if isinstance(sc, dict):
    sc["totalSupply"] = 125
    sc["agentFreeUsed"] = 126
    sc["agentFree"] = 126
    sc["runNote2201_1110"] = (
        "Run 2201: totalSupply 78->125 (+47), agentFreeUsed 126/2000 = 6,3% (masih <25% strong lead). "
        "Probe segar: mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~1 jam TERVERIFIKASI), mintOpen 1, "
        "freeLeft [1871, 1000], slot user TERBUKA (agentFreeByWallet 0, balanceOf 0). Tetap early lead; "
        "pantauan lanjut untuk promosi ke strong lead bila free% >=25%.")
    print("SOLDERCATS updated (still early)")

# ---- NIGHTFORGE: gate rechecked, still failed ----
nf = snap["contracts"].get("NIGHTFORGE")
if isinstance(nf, dict):
    nf["runNote2201_1110"] = (
        "Run 2201: totalSupply 659 (0 mint interval ini), agentFreeUsed 656/2000 = 32,8% (tetap >=25% strong "
        "lead). Gate DICEK ULANG run ini: nightforge.pages.dev home/llms.txt/skill.md MASIH mengembalikan HTML "
        "infografis medis yang sama (23.857 byte, 0 kecocokan kontrak) -> gate TETAP GAGAL, TIDAK di-preview/TIDAK "
        "di-mint. Status tetap strong-lead-gate-blocked-2026-11-10 (sudah dilaporkan sekali run 2131; tidak "
        "dilaporkan ulang).")
    print("NIGHTFORGE gate rechecked (still failed)")

note("KERNELMONK", (dyn_note("KERNELMONK") or "") +
     " Minted-by-user (hot-leg 20:59 WIB). Targeted read run 2131: totalSupply 536. Tanpa aksi.")
note("Lanternfield", (dyn_note("Lanternfield") or "") +
     " Minted-by-user run 2131 (#516). Velocity LOLOS run ini (+52, 1,58x) tapi sudah minted - tanpa aksi.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") +
     " Minted-by-user run 2131 (#946). claimable 10.000 EMBER belum di-claim (di luar otorisasi). Tanpa aksi.")
note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " Minted-by-user 2026-11-10 (#539). Tanpa aksi.")
note("Golden Agents", (dyn_note("Golden Agents") or "") +
     " Velocity LOLOS run ini (+24, 2,0x) TAPI free% UNVERIFIED (free views null, FREE_SUPPLY null) + umur "
     "UNVERIFIED -> BUKAN promosi. Tetap early lead; tanpa aksi.")
note("Glitchpilotfox", (dyn_note("Glitchpilotfox") or "") +
     " Velocity LOLOS (+22, 1,57x) TAPI status age-excluded-2026-11-09 -> tanpa aksi.")
note("Agentite", (dyn_note("Agentite") or "") +
     " Velocity LOLOS (+24, 3,0x) TAPI status age-excluded-2026-11-10 -> tanpa aksi.")

# ---- Age exclusions: window 21:31 -> 22:01 WIB (launch epoch 1794234655..1794236455) ----
WIN_LO, WIN_HI = 1794234655, 1794236455
TERMINAL = ("sold-out", "age-excluded", "minted-by-user", "excluded", "promotion-discarded",
            "same-owner-discarded", "paid-only", "upcoming")
newly_excluded = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status") or "")
    if any(x in st for x in TERMINAL):
        continue
    launch = entry.get("mintStart") or entry.get("saleStart") or entry.get("launchTime")
    if isinstance(launch, (int, float)) and WIN_LO <= launch <= WIN_HI:
        newly_excluded.append((name, launch))
print(f"age-exclusion window check: {newly_excluded if newly_excluded else '0 baru'}")

# ---- Top-level run notes ----
snap["last_run_wib"] = NOW
snap["last_run"] = 2201
snap["runNote2201_1110"] = (
    "Run 2201 (2026-11-10 22:01-~23:0x WIB, blok re-read 132799932): re-read 677 kontrak + 85 track_c "
    "(676,4 dtk, bsc-dataseed). SATU MINT BERHASIL run ini (strong-lead direct mint): BYTEBLOOM #508 - promosi "
    "early->strong (agentFreeUsed 505/2000 = 25,25%), gate lulus (bytebloom.pages.dev/llms.txt mencetak kontrak), "
    "audit Binance hasResult=false (tanpa hasil), preview bersih 000000000, tx "
    "0x4ad8c90a91a0704fc08c2fd20cf13ca3a38f850e41a9651a617cd024097c5007, blok 132801228, gas 315168 "
    "(~0,00002497 BNB); rarity Tier 'Moss Tender' (verbatim), Model Moss Lantern, Rank 5; claimable 10.000 PETAL "
    "TIDAK di-claim; own market Seed Bazaar listedCount 0 -> TIDAK di-list. EARLY LEAD BARU 1: ORBITJANITOR "
    "0x8d5a0555446d37afaba75e36da318646a4b32420 (Boltbook ZH; agentFreeUsed 325/2000 = 16,25%, mintStart 21:24:52 WIB, "
    "website terverifikasi, slot terbuka). UPCOMING 1: GEM 0xbeb8833c (buka besok 2026-11-11 19:30 WIB, watchlist-only). "
    "SOLDERCATS 125 totalSupply, agentFreeUsed 126/2000 = 6,3% (tetap early). NIGHTFORGE gate dicek ulang, tetap gagal "
    "(situs mati). Sale 0x6B39 dicek: sold out + paid-only, bukan lead. Scan leg FAST-FAIL (preflight Ankr 401, 3,4 dtk, "
    "head 132800009; watermark tetap 132512564; gap ~287.477 blok). binanceai.fun TIDAK BERUBAH (refund phase). Bridge "
    "tidak berubah (116 kontrak, md5 d1857315e09b237484c8ef2568f14f16). 0 kandidat baru, 0 track-C lead/kandidat baru, "
    "0 track-B claim.")
snap["runNote2201_1110_scan"] = (
    "Run 2201 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132800009), HTTP 401 Unauthorized dalam "
    "3,4 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan "
    "(tetap 132512564; gap ke head ~287.477 blok dan tumbuh). Route 5c: tanpa output scan baru (tidak ada ERC-20 "
    "backlog baru untuk di-shape-check run ini).")
snap["runNote2201_1110_binanceai"] = (
    "Run 2201 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok ~132800009). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["runNote2201_1110_age_exclusions"] = (
    "Run 2201 age-exclusions (aturan <24 jam): 0 BARU. Tidak ada entri non-terminal dengan launch/first-mint "
    "terverifikasi di jendela 2026-11-09 21:31-22:01 WIB yang melewati 24 jam run ini. Preseden DITAHAN run "
    "1931/2101/2131 tetap berlaku (pool/launch UNVERIFIED: HELIX, Beast16, Pressure, NUMBI, Lucky Cat, Meow Cards, "
    "BAHUANG3, Reel, Riddle Run, Gloop, Pixel Laptop, KIJIN, Dragon Agent, Iron Bloom, Agentic, 0x13A1Ebc9-new, "
    "Shard Id, Sidecoo Season, STAR CARDS, JOLT).")
snap["runNote2201_1110_discovery"] = (
    "Run 2201 discovery (subagent, read-only): Sourcify feed 20 terbaru, 0 full agent-mint NFT shape, 1 sale "
    "agent-shaped butuh cek on-chain (0x6B39 -> dicek parent: sold out + paid-only, bukan lead), 1 sale-shaped tanpa "
    "free lane (0x1253f484). Boltbook EN GAGAL fetch (0 byte, 2 percobaan); ZH 45.773 byte, 17 alamat: 1 early lead baru "
    "ORBITJANITOR, 1 upcoming GEM, 2 age-excluded dikenal (POCKET Ai, Alchemister twin), 1 infrastruktur (BoltRewards), "
    "sisanya dikenal. Sweep: semua hit dikenal/dikeluarkan/di-mint (Agentic Gangster excluded, Golden Agents, NOVRA, WNO, "
    "First-Dollar Grove). Rute 6: Square/DappBay/Odaily/PANews nihil baru. Bridge tidak berubah (116 kontrak, 0 non-snapshot).")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT MERGED run 2201")
