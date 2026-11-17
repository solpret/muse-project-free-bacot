#!/usr/bin/env python3
"""Finalize run 1831 — applies reread/velocity to snapshot (reload at write
time), 0 age removals from watchlist, updates NBC (50% crossed, velocity
fails) + DRACO, adds DinoAgent (strong lead, GATE-BLOCKED) + Tri333 (early
lead, gate PASSED) + PHNX (track-C lead, GATE-BLOCKED), records PIXEL BOYZ
age-exclusion (never in snapshot), BINANCEAI re-check note (unchanged, already
reported once run 1701 — NOT re-reported), scan-partial note in state
(watermark NOT advanced; backfill owns it). Atomic snapshot write. Appends
4 first-seen to onchain-scan-seen.json; adds 9 ERC-20s to
track-c-scan-checked.json."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132197315
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1831"

re = json.load(open(f"{BASE}/run-2026-11-07-1831-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1831-velocity.json"))
age = json.load(open(f"{BASE}/run-2026-11-07-1831-age-sweep.json"))
fresh = json.load(open(f"{BASE}/run-2026-11-07-1831-fresh-nbc-draco.json"))
gate = json.load(open(f"{BASE}/run-2026-11-07-1831-gate-dino-tri333.json"))
phnx = json.load(open(f"{BASE}/run-2026-11-07-1831-trackc-28a4-verify.json"))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
updated = 0; none_free = 0
for name, d in re["reread"].items():
    c = snap["contracts"].get(name)
    if c is None: continue
    old_ts = c.get("totalSupply")
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if d.get(k) is not None: c[k] = d[k]
    if d.get("totalSupply") is not None and old_ts is not None:
        c["previousTotalSupply"] = old_ts
    if d.get("balanceOf_user") is not None: c["balanceOf_user"] = d["balanceOf_user"]
    if d.get("freeClaimed") is None and d.get("freeMinted") is None: none_free += 1
    c["lastReadBlock"] = REREAD_BLOCK
    c["lastReadWib"] = RUN
    updated += 1
for name, d in re.get("track_c", {}).items():
    tc = snap.get("track_c", {}).get(name)
    if isinstance(tc, dict):
        if d.get("totalSupply") is not None: tc["totalSupply"] = d["totalSupply"]
        if d.get("freeMinted") is not None: tc["freeMinted"] = d["freeMinted"]
        if d.get("freeSharesRemaining") is not None: tc["freeSharesRemaining"] = d["freeSharesRemaining"]
        tc["lastReadBlock"] = REREAD_BLOCK
        tc["lastReadWib"] = RUN

vel_updated = 0
for row in vel.get("rows", []):
    name = row.get("name")
    c = snap["contracts"].get(name)
    if c is None: continue
    cur = row.get("curSupply")
    if cur is None or cur > 1000000: continue
    c["mintedInInterval"] = row.get("mintedInInterval")
    c["intervalMinutes"] = row.get("intervalMin")
    c["currentRatePerMin"] = row.get("ratePerMin")
    c["previousRatePerMin"] = row.get("prevRatePerMin")
    c["velocityLegPasses"] = row.get("velocityPasses")
    c["velocityRatio"] = row.get("ratioVsPrev")
    vel_updated += 1

assert age.get("candidates") == [], age.get("candidates")
removed = []

# --- Per-contract run notes ---
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1831"] = (f"Run 1831 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1801 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
horus = snap["contracts"].get("Horus AI")
if horus is not None:
    row = next((r for r in vel.get("rows", []) if r.get("name") == "Horus AI"), {})
    horus["velocityNote1831"] = (f"Run 1831 (blok {REREAD_BLOCK}): totalSupply +{row.get('mintedInInterval')} "
        f"(rate {row.get('ratePerMin')}/mnt, ratio {row.get('ratioVsPrev')} vs prev) -> velocity LOLOS, TAPI freePct None "
        "(semua free view revert / tanpa FREE_SUPPLY) -> BUKAN strong lead/kandidat. Tetap watchlist-only. Status: early-lead-backfill.")
neo = snap["contracts"].get("NeoGods")
if neo is not None:
    neo["totalSupply"] = 1764
    neo["runNote1831"] = (f"Run 1831 (blok {REREAD_BLOCK}): totalSupply 1764/3333 (1736 di 1801, +28); first mint 2026-11-07 09:54:06 WIB "
        "(umur ~9,2 jam, <=48 jam); free% UNVERIFIED + website gate GAGAL (1731) -> tetap watchlist-only, bukan strong lead/kandidat.")
nr = snap["contracts"].get("NULLRAID First Breach")
if nr is not None:
    nr["totalSupply"] = 598
    nr["runNote1831"] = (f"Run 1831 (blok {REREAD_BLOCK}): totalSupply 598 (537 di 1801, +61); balanceOf(user)=1; free views tidak "
        "terbaca via LEAN batch run ini (degradasi, nilai snapshot dipertahankan: freeMints 537/1111 = 48,3% di 1801); minted-by-user-2026-11-07, bukan kandidat.")

# --- NBC update: 50% CROSSED, velocity now computable but FAILS ---
nbc = snap["contracts"].get("Night Bandits Club")
if nbc is not None:
    nbc["mintedTotal"] = fresh["nbc"]["mintedTotal()"]
    nbc["freeUsed"] = fresh["nbc"]["freeUsed()"]
    nbc["freeTotal"] = fresh["nbc"]["freeTotal()"]
    nbc["freePctVerified"] = round(fresh["nbc"]["freeUsed()"] / fresh["nbc"]["freeTotal()"] * 100, 1)
    nbc["paidUsed"] = fresh["nbc"]["paidUsed()"]
    nbc["freeTakenBy_user"] = fresh["nbc"]["freeTakenBy_user"]
    nbc["balanceOf_user"] = fresh["nbc"]["balanceOf_user"]
    nbc["lastReadBlock"] = fresh["head"]
    nbc["lastReadWib"] = RUN
    nbc["velocityVerified"] = False
    nbc["runNote1831"] = (
        f"Run 1831 (bacaan segar blok {fresh['head']}, ~18:47 WIB): freeUsed {fresh['nbc']['freeUsed()']}/{fresh['nbc']['freeTotal()']} = "
        f"{round(fresh['nbc']['freeUsed()']/fresh['nbc']['freeTotal()']*100,1)}% — MELEWATI 50% (222/444) dari 39,4% di 18:31 WIB. "
        "Velocity kini TERHITUNG tapi GAGAL: 136 (18:22) -> 156 (~18:27) -> 175 (18:31) -> 250 (~18:47): +75 dalam ~16 mnt = ~4,7/mnt vs "
        "rate sebelumnya ~4,3/mnt = rasio ~1,09x (< 1,5x yang disyaratkan) — kecepatan STABIL, bukan MENINGKAT. Jadi BUKAN kandidat "
        "(velocity gagal + X unverified). Slot user masih terbuka (freeTakenBy=0, balance=0). Gate website TETAP GAGAL (run 1801; re-search "
        "alamat/nama mentah run ini tanpa hasil baru) — TIDAK ADA preview/mint. Perubahan 50% ini dilaporkan SEKALI run 1831 sebagai update "
        "status strong lead (bukan laporan ulang lead). Catatan: reread leg 1 run ini gagal membaca NBC (semua view None — degradasi RPC, "
        "BUKAN nol); angka di atas dari bacaan segar leg 6 yang berhasil.")
    nbc["velocityNote1831"] = ("Run 1831: rate interval ~4,7/mnt (250-175 dalam ~16 mnt) vs prev ~4,3/mnt (175-136 dalam ~9 mnt) = rasio ~1,09x "
        "< 1,5x DAN >=20 token terpenuhi tapi rasio gagal -> velocity GAGAL. BUKAN kandidat.")

# --- DRACO update ---
dr = snap.get("track_c", {}).get("Draco Coin")
if isinstance(dr, dict):
    dr["totalMints"] = 128
    dr["totalSupply"] = 3200000000000000000000000
    dr["lastReadBlock"] = REREAD_BLOCK
    dr["lastReadWib"] = RUN
    dr["runNote1831"] = (f"Run 1831 (blok {REREAD_BLOCK}): totalMints 128 (63 di 18:31 WIB run 1801, +65), totalSupply 3.200.000 DRACO; "
        "bacaan segar leg 6 (blok 132195458, ~18:47 WIB): totalMints 122, isFreeMintAvailable(user)=1, currentPriceFor(user)=0, mintsOf(user)=0, "
        "balanceOf(user)=0 — slot user masih terbuka, mintOpen=1. Gate website TETAP GAGAL (run 1801) — TIDAK ADA preview/mint. Tidak ada "
        "perubahan status (tetap track-C lead gate-blocked); tidak dilaporkan ulang.")

# --- New: DinoAgent (strong lead, GATE-BLOCKED — NO preview/mint) ---
d = gate["DinoAgent"]
snap["contracts"]["DinoAgent"] = {
    "address": "0xcE19D6A5FF15e088D4bf23614242927139084895",
    "status": "strong-lead-2026-11-07-gate-blocked",
    "name": "DinoAgent", "symbol": "DINOAGENT", "kind": "ERC721",
    "firstSeenBlock": 132194540, "firstSeenWib": "2026-11-07 18:42:22 WIB",
    "firstMintWib": "2026-11-07 18:42:22 WIB",
    "firstMintBlock": 132194540,
    "scanWindow": "132194540-132195539",
    "scanMints": 54, "scanMinters": 54,
    "totalMinted": d["totalMinted()"], "freeMinted": d["freeMinted()"],
    "FREE_SUPPLY": d["FREE_SUPPLY()"], "MAX_SUPPLY": d["MAX_SUPPLY()"],
    "freeLeft": d["freeLeft()"],
    "freePctVerified": round(d["freeMinted()"] / d["FREE_SUPPLY()"] * 100, 1),
    "paidMinted": d["paidMinted()"],
    "mintOpen": None,
    "freeClaimed_user": d["freeClaimed_user"], "balanceOf_user": d["balanceOf_user"],
    "userSlotNote": "Slot TERBUKA menurut bacaan (freeClaimed(user)=0, balanceOf(user)=0, mintFree() tanpa argumen) — BUKAN preview-verified (strong lead tidak pernah di-preview sebelum gate lolos; gate GAGAL run ini).",
    "lastReadBlock": gate["head"], "lastReadWib": RUN,
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Umur TERVERIFIKASI: first mint blok 132194540, 2026-11-07 18:42:22 WIB (timestamp blok via fast_rpc eth_getBlockByNumber, "
        "BUKAN Ankr). Umur ~20 menit saat verifikasi scan, ~24 menit saat bacaan segar 19:06 WIB, <=48 jam."),
    "gateNote": ("WEBSITE GATE GAGAL run 1831 — TIDAK ADA preview/mint. Situs proyek DITEMUKAN via tokenURI (metode I): tokenURI(1) = "
        "https://dinoagent-dinos3.vercel.app/assets/meta/1.json — situs https://dinoagent-dinos3.vercel.app/ cocok identitas proyek (3.333 supply, "
        "777 free, 1/wallet, token $DINO, rarity Common-Rare-Epic-Legendary) TAPI situs TIDAK MENCETAK alamat kontrak: homepage + HTML mentah (37.753 "
        "byte) 0 kemunculan alamat 0xcE19...; situs justru menyatakan 'Wallet connection opens once the official contract is announced' (kontrak belum "
        "diumumkan di situs); file metadata tokenURI 404. Metode lain: (A) pencarian alamat mentah: tanpa hasil relevan (hanya DINO tak terkait); "
        "(C) Sourcify exact_match, metadata tanpa URL; (G) pencarian nama 'DinoAgent': tanpa hasil situs proyek di indeks (situs ditemukan via "
        "tokenURI, bukan via pencarian); (H) contractURI() null/revert; (K) GitHub alamat/nama: tanpa hasil relevan (hanya repo DINO/CQ-DINO tak "
        "terkait); (M) site:vercel.app/pages.dev/netlify.app 'DinoAgent': tanpa hasil. X UNVERIFIED (tidak ada akun X proyek ditemukan; X opsional)."),
    "baselineNote": ("STRONG LEAD run 1831 (first-seen scan + langsung memenuhi 3 kaki strong lead pada bacaan pertama): umur terverifikasi ~20 menit "
        "(<=48 jam); free 226/777 = 29,1% TERVERIFIKASI saat verifikasi scan (>=25%), 234/777 = 30,1% pada bacaan segar 19:06 WIB; slot user terbuka "
        "menurut bacaan (freeClaimed=0, balance=0). Agent-shaped: Sourcify exact_match (33 fungsi: mintFree() tanpa argumen nonpayable, mintPaid, "
        "freeClaimed/freeLeft/freeMinted, FREE_SUPPLY 777, MAX_SUPPLY 3333, rarityOf); AGENT_ID_REGISTRY() = registry Agent ID "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; registry-bytes hit. Kecepatan ~11 free/menit saat verifikasi. BUKAN kandidat: free% 30,1% < 50% + "
        "velocity belum terhitung (tanpa prev rate) + X unverified. TIDAK DIEKSEKUSI run ini: website gate GAGAL (di atas) — strong-lead direct mint "
        "butuh gate lolos dulu. Dilaporkan SEKALI run 1831 sebagai strong lead + alasan gate. Sumber: onchain-scan-2026-11-07-1831.json (partial) + "
        "run-2026-11-07-1831-triage-scan.json + run-2026-11-07-1831-gate-dino-tri333.json + browser fetch dinoagent-dinos3.vercel.app."),
}

# --- New: Tri333 (EARLY lead, gate PASSED — NEVER preview/mint as early lead) ---
t = gate["Tri333"]
snap["contracts"]["Tri333"] = {
    "address": "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f",
    "status": "early-lead-2026-11-07-gate-passed",
    "name": "Tri333", "symbol": "T333", "kind": "ERC721",
    "firstSeenBlock": 132194550, "firstSeenWib": "2026-11-07 18:42:27 WIB",
    "firstMintWib": "2026-11-07 18:42:27 WIB",
    "firstMintBlock": 132194550,
    "scanWindow": "132194540-132195539",
    "scanMints": 42, "scanMinters": 26,
    "totalMinted": t["totalMinted()"], "freeMinted": t["freeMinted()"],
    "FREE_CAP": t["FREE_CAP()"], "MAX_SUPPLY": t["MAX_SUPPLY()"],
    "freePctVerified": round(t["freeMinted()"] / t["FREE_CAP()"] * 100, 1),
    "paidMintedCount": t["paidMintedCount()"],
    "mintOpen": t["mintOpen()"],
    "freeCount_user": t["freeCount_user"], "balanceOf_user": t["balanceOf_user"],
    "userSlotNote": "Slot TERBUKA menurut bacaan (freeCount(user)=0, balanceOf(user)=0, freeMint(uint256) nonpayable, max 2/wallet) — BUKAN preview-verified (early lead TIDAK PERNAH di-preview/di-mint).",
    "lastReadBlock": gate["head"], "lastReadWib": RUN,
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Umur TERVERIFIKASI: first mint blok 132194550, 2026-11-07 18:42:27 WIB (timestamp blok via fast_rpc, BUKAN Ankr). "
        "Umur ~20 menit saat verifikasi scan, ~24 menit saat bacaan segar 19:06 WIB, <=48 jam."),
    "gateNote": ("WEBSITE GATE LOLOS run 1831 (metode I — tokenURI): tokenURI(1) = https://tri333-mint.netlify.app/metadata/metadata.json, "
        "external_url https://tri333-mint.netlify.app; situs https://tri333-mint.netlify.app/ cocok identitas proyek (3.333 supply, 2.222 free max 2/wallet, "
        "1.111 paid 0,00005 BNB, royalty 5%) DAN HTML mentah situs MENCETAK alamat kontrak persis 0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f "
        "(1 kemunculan, beserta alamat registry 0x60B9...). Metode lain: (A) pencarian alamat mentah: tanpa hasil relevan; (C) Sourcify exact_match, "
        "metadata tanpa URL; (G) pencarian nama 'Tri333': tanpa hasil situs di indeks (situs ditemukan via tokenURI). X UNVERIFIED (X opsional)."),
    "baselineNote": ("EARLY LEAD run 1831 (first-seen scan): umur terverifikasi ~20 menit (<=48 jam); free 333/2222 = 15,0% TERVERIFIKASI saat verifikasi "
        "scan, 336/2222 = 15,1% pada bacaan segar 19:06 WIB — DI BAWAH 25% sehingga BUKAN strong lead (baru early lead); slot user terbuka menurut bacaan "
        "(freeCount=0, balance=0). Agent-shaped: Sourcify exact_match (34 fungsi: freeMint(uint256) nonpayable, freeCount/freeMinted, FREE_CAP 2222, "
        "FREE_PER_WALLET 2, MAX_SUPPLY 3333, mintOpen=1, PRICE 0,00005 BNB); agentIdRegistry() = registry Agent ID "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; registry-bytes hit. TIDAK DIEKSEKUSI run ini: early lead TIDAK PERNAH di-preview/di-mint; naik jadi "
        "strong lead bila free% >=25% (dengan gate sudah lolos, strong-lead direct mint baru berlaku sesudah promosi + guard segar). Dilaporkan SEKALI "
        "run 1831 sebagai early lead. Sumber: onchain-scan-2026-11-07-1831.json (partial) + run-2026-11-07-1831-triage-scan.json + "
        "run-2026-11-07-1831-gate-dino-tri333.json + browser fetch tri333-mint.netlify.app."),
}

# --- New: PHNX (track-C lead, GATE-BLOCKED — NO preview/mint) ---
snap.setdefault("track_c", {})["PHNX"] = {
    "address": "0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224",
    "status": "track-c-lead-2026-11-07-gate-blocked",
    "name": "PHNX", "symbol": "PHNX", "kind": "ERC20-sale-S1",
    "firstSeenBlock": 132194728, "firstSeenWib": "2026-11-07 18:43:47 WIB",
    "firstMintWib": "2026-11-07 18:43:47 WIB",
    "scanWindow": "132194540-132195539",
    "scanMints": 11, "scanMinters": 11,
    "totalSupply": phnx["totalSupply()"], "totalMints": phnx["totalMints()"],
    "MAX_CAP": phnx["MAX_CAP()"],
    "currentStage": 1, "currentTokensPerMint": 25000000000000000000000,
    "priceWei": phnx["price()"], "maxPerWallet": phnx["maxPerWallet()"], "mintOpen": phnx["mintOpen()"],
    "STAGE1_TOKENS": 25000000000000000000000, "STAGE2_START": 500,
    "freeMintsLeft": 425, "freeMintsUsed": 75, "freeMintLimit": 500,
    "isFreeMintAvailable_user": phnx["isFreeMintAvailable_user"],
    "currentPriceFor_user": phnx["currentPriceFor_user"],
    "mintsOf_user": phnx["mintsOf_user"], "balanceOf_user": phnx["balanceOf_user"],
    "agentRegistry": phnx["agentRegistry"],
    "lastReadBlock": phnx["head"], "lastReadWib": RUN,
    "gateNote": ("WEBSITE GATE GAGAL run 1831 — TIDAK ADA preview/mint: (A) pencarian alamat mentah: tanpa hasil relevan (hanya saham Phoenix Energy, "
        "PhoenixDAO, PhoenixCoin tak terkait); (C) Sourcify exact_match, metadata tanpa URL; (G) pencarian nama 'PHNX Phoenix free share': tanpa "
        "hasil situs proyek (hanya panduan umum Agent ID, PIXEL BOYZ, Ptah, AGENT MAO tak terkait); (M) site:vercel.app/pages.dev/netlify.app 'PHNX "
        "free mint Agent ID': tanpa hasil. (K) GitHub tidak dijalankan run ini — A/C/G/M sudah cukup untuk menyatakan gate gagal (tidak ada situs "
        "ditemukan di jalur mana pun). X UNVERIFIED (X opsional)."),
    "note": ("TRACK-C LEAD run 1831 (first-seen via 5c-extra dari scan 1831 + Sourcify feed): bentuk SALE S1 LOLOS — ABI Sourcify exact_match "
        "(66 fungsi): mint() payable + currentPriceFor(address)/price() (quote/cost) + isFreeMintAvailable(address) (free-share view, preseden DRACO "
        "run 1801) + agentRegistry() = registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Free pool TERVERIFIKASI: freeMintsLeft 425/500 "
        "(freeMintsUsed 75); slot user terbuka (isFreeMintAvailable(user)=1, currentPriceFor(user)=0, mintsOf(user)=0, balanceOf(user)=0); stage 1 "
        "(25.000 PHNX/mint, stage 2 mulai mint ke-500), harga paid price() 0,000888 BNB, MAX_CAP 1e9, maxPerWallet 5, mintOpen=1. Umur TERVERIFIKASI "
        "first mint 2026-11-07 18:43:47 WIB (blok 132194728, ~25 menit, <=48 jam). TIDAK DIEKSEKUSI run ini: website gate GAGAL (di atas) — track-C lead "
        "direct mint butuh gate lolos dulu. Dilaporkan SEKALI run 1831 sebagai track-C lead + alasan gate. Sumber: run-2026-11-07-1831-triage-scan.json "
        "+ run-2026-11-07-1831-5c-extra-redo.json + run-2026-11-07-1831-trackc-28a4-verify.json."),
}

# --- PIXEL BOYZ age-exclusion (discovered via gate-check sweep; never in snapshot) ---
snap.setdefault("age_exclusions", []).append({
    "name": "PIXEL BOYZ",
    "address": "0xaFB50403C0838D5b45F8748138BA33A70E23b8cf",
    "site": "https://www.pixelboyz.shop/mint",
    "in_snapshot": False,
    "firstSeenBlock": 131256647,
    "firstSeenWib": "2026-11-02 21:26:07 WIB",
    "ageHours": "~117",
    "totalMinted": 4296, "totalFreeMinted": 4290, "freeTotal": 6000,
    "freePct": 71.5,
    "status_before": "seen-only (first-seen scan, tidak pernah masuk snapshot / tidak pernah dilaporkan sebagai lead)",
    "removed_run": RUN,
    "reason": ("Ditemukan run 1831 via pencarian gate PHNX (hasil samping): situs mencetak alamat kontrak persis + registry, free 4.290/6.000 = 71,5% "
        "terverifikasi on-chain, slot user terbuka (walletFreeRemaining=2, hasAgentId=1, balance=0), freeSaleActive=1 — TAPI umur peluncuran "
        "TERVERIFIKASI >48 jam (first-seen blok 131256647 = 2026-11-02 21:26 WIB, ~117 jam sebelum run; first mint terjadi pada/sebelum blok itu) "
        "dan belum sold out (4.296/10.000) -> AGE-EXCLUDED per aturan umur 48 jam; bukan lead/kandidat; tidak dilaporkan ke chat (hanya dicatat, "
        "preseden BAYC sale run 1801). Catatan: tampilan situs 'Total Minted 0' sudah basi/rusak (on-chain 4.296). Tidak ada fase/batch mint baru "
        "yang terverifikasi."),
})

# --- TRACK B — BINANCEAI re-check (already reported once run 1701; NOT re-reported) ---
snap["runNote1831_binanceai"] = (
    "Run 1831: BINANCEAI re-check — launched()=0, failed()=1, isRefundPhase()=1, totalShares()=3110, tokenClaimed(user)=0, tokenBalance(user)=0 — "
    "IDENTIK run 1701/1731/1801 (upaya pertama via race() timeout di semua RPC; retry bersih via dataseed/publicnode batch berhasil 9,2 dtk, head "
    "132195492 — nilai null di pass pertama adalah artefak RPC, bukan perubahan state). Sudah dilaporkan sekali run 1701; TIDAK dilaporkan ulang. "
    "Grove: freeOpen=0, freeClaimed(user)=false — identik run 1801."
)
snap.setdefault("binanceai_claim", {})["verified_run"] = RUN
snap.setdefault("binanceai_claim", {})["verified_wib"] = TS

snap["runNote1831_1107"] = (
    "Run 1831: 1 STRONG LEAD BARU (GATE-BLOCKED) + 1 EARLY LEAD BARU (gate lolos) + 1 TRACK-C LEAD BARU (GATE-BLOCKED) + NBC melewati 50% (update "
    "status sekali) + PIXEL BOYZ age-excluded (dicatat saja). 0 kandidat baru, 0 eksekusi, 0 pending claim baru/dibuka, 0 age-exclusion dari watchlist. "
    "STRONG LEAD: DinoAgent (DINOAGENT) 0xcE19D6A5FF15e088D4bf23614242927139084895 — first-seen scan window 132194540-132195539 (blok 132194540, 54 mint/54 "
    "minter); umur terverifikasi first mint 2026-11-07 18:42:22 WIB (~20 menit); free 226/777 = 29,1% TERVERIFIKASI (>=25%), 234/777 = 30,1% bacaan segar "
    "19:06 WIB; slot user terbuka (freeClaimed=0, balance=0); agent-shaped (Sourcify exact_match, mintFree() no-arg, AGENT_ID_REGISTRY()=registry "
    "0x60B9...). BUKAN kandidat (free% <50%, velocity belum terhitung, X unverified). TIDAK DIEKSEKUSI: website gate GAGAL — situs ditemukan via "
    "tokenURI (dinoagent-dinos3.vercel.app, cocok identitas 3.333/777 free/$DINO) TAPI TIDAK MENCETAK alamat kontrak (0 kemunculan di HTML mentah; situs "
    "menyatakan kontrak belum diumumkan); metode A/C/G/H/I/K/M dicoba. Dilaporkan SEKALI run 1831 sebagai strong lead + alasan gate. "
    "EARLY LEAD: Tri333 (T333) 0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f — first-seen scan (blok 132194550, 42 mint/26 minter); umur terverifikasi first "
    "mint 2026-11-07 18:42:27 WIB (~20 menit); free 333/2222 = 15,0% TERVERIFIKASI (<25% -> early, bukan strong); slot user terbuka (freeCount=0, "
    "balance=0); agent-shaped (Sourcify exact_match, freeMint(uint256), agentIdRegistry()=registry 0x60B9...). Website gate LOLOS (metode I: situs "
    "tri333-mint.netlify.app via tokenURI, HTML mentah MENCETAK alamat kontrak persis). TIDAK DIEKSEKUSI: early lead TIDAK PERNAH di-preview/di-mint; "
    "promosi ke strong lead bila free% >=25%. Dilaporkan SEKALI run 1831 sebagai early lead. "
    "TRACK-C LEAD: PHNX 0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224 — first-seen via 5c-extra scan 1831 + Sourcify feed; bentuk SALE S1 LOLOS (mint + "
    "currentPriceFor/price + isFreeMintAvailable + agentRegistry()=registry 0x60B9...); free pool TERVERIFIKASI freeMintsLeft 425/500; slot user terbuka "
    "(isFreeMintAvailable=1, harga user 0, mintsOf=0); umur terverifikasi first mint 2026-11-07 18:43:47 WIB (~25 menit); stage 1, 25.000 PHNX/mint, "
    "totalMints 75. TIDAK DIEKSEKUSI: website gate GAGAL (metode A/C/G/M — tanpa situs ditemukan). Dilaporkan SEKALI run 1831 sebagai track-C lead + "
    "alasan gate. "
    "NBC UPDATE (perubahan status, dilaporkan sekali): free 250/444 = 56,3% — MELEWATI 50% (dari 39,4% di 18:31 WIB); velocity kini terhitung tapi GAGAL "
    "(~4,7/mnt vs ~4,3/mnt = rasio ~1,09x < 1,5x — kecepatan stabil, bukan meningkat) sehingga BUKAN kandidat; slot user masih terbuka; gate tetap "
    "GAGAL — TIDAK ADA preview/mint. DRACO: totalMints 128 (63 di 18:31 WIB), slot user masih terbuka; gate tetap GAGAL; tidak dilaporkan ulang. "
    "PIXEL BOYZ 0xaFB50403C0838D5b45F8748138BA33A70E23b8cf: free 4.290/6.000 = 71,5% + slot user terbuka + situs mencetak kontrak, TAPI first-seen "
    "2026-11-02 21:26 WIB (~117 jam) -> AGE-EXCLUDED, dicatat saja, tidak dilaporkan ke chat. "
    "Preflight: attempt-1 GAGAL (~48 dtk, dataseed timeout semua endpoint; probe Ankr OK 6,6 dtk — outage dataseed saja, sementara); retry-1 PASS 16,1 "
    "dtk (head 132195492, 345 log/50 blok). Tanpa no_proxy; Ankr lewat proxy env. "
    "Reread 447 kontrak + 68 track_c (blok 132197315, 806,4 dtk; head-block awal gagal dibaca — race timeout semua endpoint, dipatok belakangan ke "
    "132197315 via dataseed1; interval velocity sedikit over-estimasi ~5 mnt, rate konservatif); 342 supply terbaca; 105 supply None / 104 all-None "
    "(degradasi eth_call, dicatat None bukan nol — setara 103 di run 1801); 5 kontrak snapshot ber-address None tidak dibaca (Mummyhive, LuckyBox-d08e, "
    "SnailMail, Jolly, AgentGlyph). Velocity 1 pass: Horus AI +95 ratio 1,84x — freePct None -> BUKAN strong lead/kandidat, hanya dicatat. Sold-out "
    "tercatat 35 (0 baru). Slot berubah: 0. HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. NULLRAID totalSupply 598 (+61), "
    "balanceOf(user)=1, minted-by-user. NeoGods 1764/3333 (+28), watchlist-only. Age sweep: 0 kandidat penghapusan; 44 kept; 378 umur UNVERIFIED. "
    "Boltbook EN+ZH FRESH (HTTP 200, 25 kartu, rotasi penuh vs 1801) + 6 post + 3 author deep-read — 0 lead baru; $BUNNY token + Vorn Agent DITOLAK "
    "(Sourcify unverified, minting macet/0 mint); HOPKIN GENESIS + 3 lane 0x1103-family (Gacha Gang, helm.ai, OMENS) sudah dikenal via hot-leg/scan-seen, "
    "tanpa Agent ID gate (free untuk alamat mana pun) — bukan lead; Paw Gang tetap buka malam ini 20:00 WIB (tanpa kontrak); Pearl reset besok ~18:09 WIB; "
    "$SGARDEN Failed di sidebar. Sweep EN+ZH + Square/Odaily/PANews/DappBay — 0 proyek baru; Agent Periodic Lab sudah dikenal (totalSupply revert, % "
    "unverified). $SWARM tetap bukan track C (semua berbayar). M3M3 tetap refund phase. Razor genesis BELUM dimulai (pair kosong). WHALE NFT kontrak B "
    "gate tetap GAGAL (1.829/5.000 run 1701). WHALE A sold out 5.000/5.000. "
    "Scan leg: window 132194540-132195539 (1000 blok, cap; head 132195539; gap 132188666-132194539 = 4.874 blok untuk backfill — 467 + 4.407; window "
    "132189133-132190132 sudah dicover scan 1801), chunk 20/20 selesai (0 error, 40 panggilan Ankr), 141 ERC721 + 3 ERC1155 + 320 ERC-20-mint; enrichment "
    "STALL di 41/144 -> timeout 700 dtk (SCAN_EXIT=124, pola stall berulang); 40 kontrak ter-enrich (partial JSON terselamatkan, partial=True); 104 kontrak "
    "NFT unenriched (alamat tidak terpulihkan -> backfill). Watermark TIDAK dimajukan run ini (tetap 132188665, milik backfill). Triage scan: 3 first-seen — "
    "DinoAgent (strong lead, di atas) + Tri333 (early lead, di atas) + XiaomiS7 0xfA3a8bA545FebccaE0b88aF8D5f8b7f4D4173333 (4 mint/4 minter, Sourcify "
    "not_verified, tanpa registry/free-shape -> bukan agent-shaped, hanya dicatat). "
    "5a Sourcify feed 20 kontrak: 0 shape hit (feed OK, 0 error); near-miss dicatat: 0xcE19... (DinoAgent — mintFree + free views tapi tanpa registry "
    "menurut feed-check leg 5 — dikoreksi triage scan: registry ADA via AGENT_ID_REGISTRY()), 0x2728.../0x28a4... (registry ada, tanpa free view menurut "
    "feed-check — dikoreksi redo parent: 0x28a4... punya isFreeMintAvailable -> S1 LOLOS, PHNX lead di atas). 5c dari scan 1801: 38 >=10, semua sudah "
    "dicek, 0 baru, 0 hit. 5c-extra dari scan 1831 (redo parent, endpoint Sourcify benar /v2/contract/): 9 dicek — 8 Sourcify-unverified (404), 1 S1 hit "
    "(PHNX, di atas); checked list kini 2539 alamat. Catatan: script gate parent pertama memakai endpoint Sourcify salah (/v2/contracts/) sehingga "
    "mengembalikan 404 untuk semua — hasil itu DIBUANG, diganti redo dengan endpoint benar; verifikasi Sourcify DinoAgent/Tri333/PHNX di redo = exact_match. "
    "Track B: pending_claims kosong; BINANCEAI re-check identik run 1701 (refund/failed, sudah dilaporkan — tidak dilaporkan ulang); Grove freeOpen 0, "
    "freeClaimed_user false. Bridge: tidak berubah (mtime 2026-11-06 02:48); 0 promosi/perubahan; 115 kontrak, 114 tidak di snapshot, 94 same-owner-discarded. "
    "Koreksi atas flag leg 6: NBC + DRACO ADA di snapshot (kontrak 452 termasuk NBC, track_c 84 termasuk DRACO) — flag 'tidak ada' leg 6 adalah salah "
    "baca (kemungkinan salinan snapshot lama); tidak ada celah persistensi finalize run 1801."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")

# seen file: append 4 first-seen (reload at write time)
seen_path = f"{BASE}/onchain-scan-seen.json"
seen = json.load(open(seen_path))
seen.setdefault("contracts", {}).update({
    "0xce19d6a5ff15e088d4bf23614242927139084895": 132194540,
    "0x157d860e30b6c6d4dC0abe3bD6e66e659A9d524f": 132194550,
    "0xfa3a8ba545febccae0b88af8d5f8b7f4d4173333": 132194709,
    "0x28a4f0bbdc1be886f9e5a290e6598a83f248b224": 132194728,
})
seen["_meta"]["contracts_count"] = len(seen["contracts"])
with open(seen_path, "w") as f:
    json.dump(seen, f, indent=1)

# track-c checked: add the 9 ERC-20s from scan 1831 (case-insensitive dedupe)
chk_path = f"{BASE}/track-c-scan-checked.json"
chk = json.load(open(chk_path))
lst = chk.setdefault("checked", [])
low = {a.lower() for a in lst}
for a in ["0x5D28C44bAd17d75D2207C4A042b73AF5297971C2",
          "0x62926C83729fB7d54b211C2dd9D5A9116be38a87",
          "0x68Cf8Eb34F99d8c86F9E5518B9b5Cea45b1Bb889",
          "0x2760e5D359EB84512207A91C02E2eC29fd30a1b2",
          "0x71E8639b242FFaf9e2a5ab0247FaacD17E25eE4E",
          "0x54Ff11c7a6850a442E0029Bd454ef000e5131191",
          "0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224",
          "0xD89651A8B8B79C7F65543Dd428837b98D63ba60E",
          "0x597bE001b48891620Da1440CdfA82D08297dfB45"]:
    if a.lower() not in low:
        lst.append(a); low.add(a.lower())
chk["0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224"] = {
    "source": "run-1831-5c-extra-redo", "status": "track-c-lead-gate-blocked",
    "mint_count": 11, "note": "S1 shape passes (mint + currentPriceFor/price + isFreeMintAvailable + agentRegistry()=registry); free pool freeMintsLeft 425/500, price user 0, age verified first mint 18:43:47 WIB; website gate FAILED run 1831 — NOT minted."}
for a, mc in [("0x5D28C44bAd17d75D2207C4A042b73AF5297971C2", 122),
              ("0x62926C83729fB7d54b211C2dd9D5A9116be38a87", 43),
              ("0x68Cf8Eb34F99d8c86F9E5518B9b5Cea45b1Bb889", 39),
              ("0x2760e5D359EB84512207A91C02E2eC29fd30a1b2", 19),
              ("0x71E8639b242FFaf9e2a5ab0247FaacD17E25eE4E", 15),
              ("0x54Ff11c7a6850a442E0029Bd454ef000e5131191", 15),
              ("0xD89651A8B8B79C7F65543Dd428837b98D63ba60E", 10),
              ("0x597bE001b48891620Da1440CdfA82D08297dfB45", 10)]:
    chk[a] = {"source": "run-1831-5c-extra-redo", "status": "checked-not-verified",
              "mint_count": mc, "note": "Sourcify not_verified (404, endpoint benar /v2/contract/) — shape unknown, recorded checked, never re-checked."}
with open(chk_path, "w") as f:
    json.dump(chk, f, indent=1)

# state note (scan partial; watermark untouched by this run)
st_path = f"{BASE}/onchain-scan-state.json"
st = json.load(open(st_path))
st["note_1831_scan_partial"] = (
    "Run 1831 scan (route 4): preflight attempt-1 GAGAL ~48 dtk (dataseed timeout semua endpoint; probe Ankr OK 6,6 dtk — outage dataseed "
    "sementara); retry-1 PASS 16,1 dtk (head 132195492, 345 log/50 blok). Window 132194540-132195539 (1000 blok, cap dari head 132195539; gap "
    "132188666-132194539 = 4.874 blok untuk backfill; window 132189133-132190132 sudah dicover scan 1801), chunk 20/20 selesai (0 error, 40 "
    "panggilan Ankr), 141 ERC721 + 3 ERC1155 + 320 ERC-20-mint; enrichment STALL di 41/144 -> timeout 700 dtk (SCAN_EXIT=124, pola stall berulang "
    "seperti run 1601/1631/1701/1731/1801); 40 kontrak ter-enrich (partial JSON terselamatkan, partial=True); 104 kontrak NFT unenriched (alamat "
    "tidak terpulihkan -> backfill). Watermark TIDAK dimajukan run ini (tetap 132188665, milik backfill). Triage scan 3 first-seen (DinoAgent strong "
    "lead gate-blocked + Tri333 early lead gate-passed + XiaomiS7 bukan agent-shaped); 5c-extra 9 dicek (PHNX track-C lead gate-blocked)."
)
with open(st_path, "w") as f:
    json.dump(st, f, indent=1)
print(f"FINALIZE-1831 updated={updated} none_free={none_free} vel_updated={vel_updated} removed_age={len(removed)} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} age_excl={len(snap.get('age_exclusions', []))} ts={TS}", flush=True)
