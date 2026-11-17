#!/usr/bin/env python3
"""Finalize run 1801 — applies reread/velocity to snapshot (reload at write
time), 0 age removals, adds NBC (strong lead, GATE-BLOCKED) + DRACO Coin
(track-C lead, GATE-BLOCKED), BinanceAI re-check note (already reported once
run 1701 — NOT re-reported), scan-partial note in state (watermark NOT
advanced by this run; backfill owns it). Atomic snapshot write. Appends
NBC + xm to onchain-scan-seen.json; adds 3 ERC-20s to
track-c-scan-checked.json."""
import json, os
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REREAD_BLOCK = 132190042
NOW = datetime.now(timezone(timedelta(hours=7)))
TS = NOW.strftime("%Y-%m-%d %H:%M WIB")
RUN = "2026-11-07 run 1801"

re = json.load(open(f"{BASE}/run-2026-11-07-1801-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-07-1801-velocity.json"))
age = json.load(open(f"{BASE}/run-2026-11-07-1801-age-sweep.json"))
fresh = json.load(open(f"{BASE}/run-2026-11-07-1801-fresh-nbc-draco.json"))

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

# --- Age sweep: 0 candidates, no removals ---
assert age.get("candidates") == [], age.get("candidates")
removed = []

# --- Per-contract run notes ---
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1801"] = (f"Run 1801 (blok {REREAD_BLOCK}): totalSupply 1255 flat vs run 1731 (1255) -> velocity "
        "GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.")
nbc_note_free = f"{fresh['nbc_freeUsed']}/{fresh['nbc_freeTotal']} = {round(fresh['nbc_freeUsed']/fresh['nbc_freeTotal']*100,1)}%"
for nm in ("AgentVOLT (round 1)", "Sidecoo"):
    c = snap["contracts"].get(nm)
    if c is not None:
        row = next((r for r in vel.get("rows", []) if r.get("name") == nm), {})
        c[f"velocityNote1801"] = (f"Run 1801 (blok {REREAD_BLOCK}): totalSupply +{row.get('mintedInInterval')} "
            f"(rate {row.get('ratePerMin')}/mnt, ratio {row.get('ratioVsPrev')} vs prev) -> velocity LOLOS, TAPI free% + umur "
            "UNVERIFIED (semua free view revert) -> BUKAN strong lead/kandidat. Tetap watchlist-only.")
neo = snap["contracts"].get("NeoGods")
if neo is not None:
    neo["totalSupply"] = 1736
    neo["runNote1801"] = (f"Run 1801 (blok {REREAD_BLOCK}): totalSupply 1736/3333 (1700 di 1731); first mint 2026-11-07 09:54:06 WIB "
        "(umur ~8,1 jam, <=48 jam); free% UNVERIFIED + website gate GAGAL (1731) -> tetap watchlist-only, bukan strong lead/kandidat.")
nr = snap["contracts"].get("NULLRAID First Breach")
if nr is not None:
    nr["status"] = "minted-by-user-2026-11-07"
    nr["totalSupply"] = 537
    nr["freeMints"] = 537
    nr["freeClaims_user"] = True
    nr["balanceOf_user"] = 1
    nr["mintTx"] = "0xb5b3f5b6a6506bebb46bad9703c93c1bc51247d41da335493e3f45420c13b862"
    nr["mintBlock"] = 132189253
    nr["mintTokenId"] = 503
    nr["runNote1801"] = (f"Run 1801: mint user TERVERIFIKASI (freeClaims(user)=1, balanceOf(user)=1, ownerOf(503)=wallet agent 0xeb23; "
        "totalSupply 537, freeMints 537/1111 = 48,3%, phase 1, price 0, paused 0, remainingInPhase 574). Status snapshot sudah "
        "minted-by-user-2026-11-07.")

# --- New: NBC (strong lead, GATE-BLOCKED — NO preview/mint) ---
snap["contracts"]["Night Bandits Club"] = {
    "address": "0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf",
    "status": "strong-lead-2026-11-07-gate-blocked",
    "name": "Night Bandits Club", "symbol": "NBC", "kind": "ERC721",
    "firstSeenBlock": 132189223, "firstSeenWib": "2026-11-07 18:02:28 WIB",
    "firstMintWib": "2026-11-07 18:02:28 WIB",
    "firstMintBlock": 132189223,
    "scanWindow": "132189133-132190132",
    "scanMints": 45, "scanMinters": 45,
    "totalSupply": None, "mintedTotal": fresh["nbc_mintedTotal"],
    "freeTotal": fresh["nbc_freeTotal"], "freeUsed": fresh["nbc_freeUsed"],
    "freePctVerified": round(fresh["nbc_freeUsed"]/fresh["nbc_freeTotal"]*100, 1),
    "paidTotal": 667, "paidUsed": fresh["nbc_paidUsed"],
    "supplyCap": 1111, "priceWei": 720000000000000,
    "opensAtWib": "2026-11-07 18:02:03 WIB", "closesAtWib": "2026-11-14 18:02:03 WIB",
    "mintOpen": True,
    "freeTakenBy_user": fresh["nbc_freeTakenBy_user"], "balanceOf_user": fresh["nbc_balanceOf_user"],
    "userSlotNote": "Slot TERBUKA menurut bacaan (freeTakenBy(user)=0, balanceOf(user)=0, mintFree() tanpa argumen) — BUKAN preview-verified (early/strong lead tidak pernah di-preview sebelum gate lolos; gate GAGAL run ini).",
    "lastReadBlock": fresh["head"], "lastReadWib": RUN,
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Umur TERVERIFIKASI: first mint blok 132189223, 2026-11-07 18:02:28 WIB (timestamp blok via fast_rpc eth_getBlockByNumber, "
        "BUKAN Ankr); opensAt() kontrak 18:02:03 WIB; Sourcify verifiedAt 2026-11-07T11:03:05Z (= 18:03:05 WIB). Umur ~29 menit saat baca segar 18:31 WIB, <=48 jam."),
    "gateNote": ("WEBSITE GATE GAGAL run 1801 — TIDAK ADA preview/mint: (A) pencarian alamat mentah: tanpa hasil relevan; (B) Boltbook en+zh "
        "0 sebutan NBC; (C) Sourcify metadata tanpa URL (metadata 404); (G) pencarian nama 'Night Bandits Club' hanya hasil tak terkait; "
        "(H) contractURI ipfs://bafybeif5dnuhu5iastpx3t4exiet4dmkmtqmemu4egehatehwamxqammwm/collection.json — gateway IPFS diblokir sandbox "
        "(ipfs.io/Pinata/Cloudflare/dweb.link 'Your request was blocked'), isi collection.json TIDAK terbaca; (I) tokenURI(1) juga IPFS, sama-sama "
        "tak terbaca; (K) GitHub pencarian alamat/nama: tanpa hasil; (L) BscScan halaman token via browser (18:24-18:31 WIB): TIDAK ADA kolom "
        "Website/Social terisi (Overview + tab Info hanya 'Click here to update the token information'), holder 165, transfer 170, peringatan "
        "'Reputation UNKNOWN'; (M) site:vercel.app/pages.dev/deed.page 'Night Bandits Club': tanpa hasil; (N) tidak berlaku (tidak ada Agent ID "
        "token proyek yang diketahui). X UNVERIFIED (tidak ada akun X proyek ditemukan; X opsional, bukan penghambat)."),
    "baselineNote": ("STRONG LEAD run 1801 (first-seen scan + langsung memenuhi 3 kaki strong lead pada bacaan pertama): umur terverifikasi ~29 menit "
        "(<=48 jam); free 175/444 = 39,4% TERVERIFIKASI (>=25%); slot user terbuka menurut bacaan (freeTakenBy=0, balance=0). Agent-shaped: Sourcify "
        "exact_match (61 fungsi: mintFree() tanpa argumen nonpayable, mintPaid(uint256) payable, freeTakenBy/freeTotal/freeUsed, mintedTotal, "
        "supplyCap, opensAt/closesAt, priceWei 0,00072 BNB); gate() mengembalikan alamat registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; "
        "registry-bytes hit. BUKAN kandidat: free% 39,4% < 50% + velocity belum terhitung (tanpa prev rate) + X unverified. TIDAK DIEKSEKUSI run ini: "
        "website gate GAGAL (di atas) — strong-lead direct mint butuh gate lolos dulu. Dilaporkan SEKALI run 1801 sebagai strong lead + alasan gate. "
        "LOOT_PER_MINT 15e18 per mint. Sumber: onchain-scan-2026-11-07-1801.json + run-2026-11-07-1801-nbc-verify.json + "
        "run-2026-11-07-1801-nbc-2e19-verify.json + abi-nbc-1801.json + browser BscScan (task 6ca0ded1)."),
}

# --- New: DRACO Coin (track-C lead, GATE-BLOCKED — NO preview/mint) ---
snap.setdefault("track_c", {})["Draco Coin"] = {
    "address": "0x2e1927798462397a88e3c1015Dc8168e798DF6D3",
    "status": "track-c-lead-2026-11-07-gate-blocked",
    "name": "Draco Coin", "symbol": "DRACO", "kind": "ERC20-sale-S1",
    "firstSeenBlock": 132189228, "firstSeenWib": "2026-11-07 18:02:30 WIB",
    "firstMintWib": "2026-11-07 18:02:30 WIB",
    "scanWindow": "132189133-132190132",
    "scanMints": 15, "scanMinters": 15,
    "totalSupply": fresh["draco_totalSupply"], "totalMints": fresh["draco_totalMints"],
    "MAX_CAP": 1000000000000000000000000000,
    "currentStage": 1, "currentTokensPerMint": 25000000000000000000000,
    "priceWei": 111000000000000, "maxPerWallet": 5, "mintOpen": True,
    "STAGE1_TOKENS": 25000000000000000000000, "STAGE2_START": 500,
    "STAGE3_START": 1500, "STAGE4_START": 4000, "STAGE5_START": 8000,
    "isFreeMintAvailable_user": fresh["draco_isFreeMintAvailable_user"],
    "currentPriceFor_user": fresh["draco_currentPriceFor_user"],
    "mintsOf_user": fresh["draco_mintsOf_user"], "balanceOf_user": fresh["draco_balanceOf_user"],
    "owner": "0x2e01c4a4dcfa811288b123f050b5009b14b0c048",
    "lastReadBlock": fresh["head"], "lastReadWib": RUN,
    "gateNote": ("WEBSITE GATE GAGAL run 1801 — TIDAK ADA preview/mint: (A) pencarian alamat mentah: tanpa hasil relevan (hanya Decred/DRX/Draco Inu "
        "tak terkait); (G) pencarian nama 'Draco Coin' DRACO: hanya Draco Inu / Draco.Finance / DRACMA tak terkait; (K) GitHub pencarian alamat/nama: "
        "tanpa hasil; (L) BscScan halaman token via browser (18:31-18:43 WIB): TIDAK ADA kolom Website/Social terisi (Overview + tab Info hanya "
        "'Click here to update the token information'), holder 101, transfer 105, peringatan 'Reputation UNKNOWN', MAX TOTAL SUPPLY tampil "
        "'2,625,000 DRACO' (= 105 mint x 25.000 saat halaman dimuat); (M) site:vercel.app/pages.dev/deed.page 'Draco Coin': tanpa hasil. "
        "X UNVERIFIED (tidak ada akun X proyek ditemukan; X opsional)."),
    "note": ("TRACK-C LEAD run 1801 (first-seen via 5c dari scan 1801): bentuk SALE S1 LOLOS — ABI Sourcify exact_match (61 fungsi): mint() payable + "
        "currentPriceFor(address)/price() (quote/cost) + isFreeMintAvailable(address) (free-share view) + agentRegistry() yang mengembalikan alamat "
        "registry Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F. Free pool: isFreeMintAvailable(user)=1, currentPriceFor(user)=0, mintsOf(user)=0, "
        "balanceOf(user)=0 (slot user terbuka); totalMints 63 (18:31 WIB), stage 1 (25.000 DRACO/mint, stage 2 mulai mint ke-500). Umur TERVERIFIKASI "
        "first mint 2026-11-07 18:02:30 WIB (blok 132189228, ~29 menit, <=48 jam). TIDAK DIEKSEKUSI run ini: website gate GAGAL (di atas) — track-C lead "
        "direct mint butuh gate lolos dulu. Dilaporkan SEKALI run 1801 sebagai track-C lead + alasan gate. Sumber: run-2026-11-07-1801-triage-scan.json "
        "+ run-2026-11-07-1801-nbc-2e19-verify.json + abi-erc20-2e19-1801.json + browser BscScan (task 6ca0ded1)."),
}

# --- BAYC sale age-exclusion (never in snapshot; recorded for dedupe) ---
snap.setdefault("age_exclusions", []).append({
    "name": "BAYC sale (ApeYachtSale)",
    "token": "0xEA2390207d2e36779b47bf9839d37746e805C4ed",
    "sale": "0xA178Dd21FD274b25e92c4Ab4A58A8d0B6bdfAE6b",
    "in_snapshot": False,
    "saleStartWib": "2026-11-04 21:00 WIB",
    "ageHours": 69.1,
    "FREE_SHARES": 2000,
    "status_before": "watchlist-only-pelengkap-scan (token)",
    "removed_run": RUN,
    "reason": "Umur sale terverifikasi ~69,1 jam (>48 jam) — age-excluded; bukan lead/kandidat; tidak dilaporkan ke chat (hanya dicatat). Diverifikasi on-chain run 1801 leg 3 (blok 132190145): token() cocok, FREE_SHARES=2.000, saleStart 2026-11-04 21:00 WIB.",
})

# --- TRACK B — BINANCEAI light re-check (already reported once run 1701; NOT re-reported) ---
snap["binanceai_claim"] = {
    "status": "closed-refund-phase-2026-11-07",
    "mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    "token": "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
    "userShares": 1, "tokenClaimed_user": 0, "tokenBalance_user": 0,
    "launched": 0, "failed": 1, "isRefundPhase": 1, "totalShares": 3110,
    "verified_run": RUN, "verified_wib": TS, "block": None,
    "verify_method": "binanceai-grove.py run 1801 — nilai IDENTIK run 1701/1731 (pembacaan kontrak berhasil; satu baca balanceOf awal null karena timeout RPC, retry mengonfirmasi 0 — artefak baca, bukan perubahan state)",
    "note": "Re-check ringan run 1801: tetap fase refund/failed (failed=1, isRefundPhase=1, launched=0). SUDAH dilaporkan sekali run 1701 — TIDAK dilaporkan ulang run ini. Share user gratis — tidak ada dana yang perlu di-refund. Grove: freeOpen 0, freeClaimed_user false.",
}
snap["runNote1801_binanceai"] = (
    "Run 1801: BINANCEAI re-check ringan — nilai IDENTIK run 1701/1731 (failed()=1, isRefundPhase()=1, launched()=0, totalShares()=3110, "
    "tokenClaimed(user)=0, tokenBalance(user)=0). Sudah dilaporkan sekali run 1701; tracking pending claim tetap DITUTUP; TIDAK dilaporkan ulang. "
    "Grove: freeOpen 0, freeClaimed_user false."
)

snap["runNote1801_1107"] = (
    "Run 1801: 1 STRONG LEAD BARU (GATE-BLOCKED) + 1 TRACK-C LEAD BARU (GATE-BLOCKED). 0 kandidat baru, 0 eksekusi, 0 pending claim baru/dibuka, "
    "0 age-exclusion dari watchlist (BAYC sale dicatat age-excluded, bukan dari snapshot). "
    "STRONG LEAD: Night Bandits Club (NBC) 0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf — first-seen scan window 132189133-132190132 (blok 132189223, "
    "45 mint/45 minter); umur terverifikasi first mint 2026-11-07 18:02:28 WIB (~29 menit); free 175/444 = 39,4% TERVERIFIKASI (>=25%); slot user "
    "terbuka menurut bacaan (freeTakenBy=0, balance=0); agent-shaped (Sourcify exact_match, mintFree() no-arg, gate()=registry 0x60B9...). BUKAN "
    "kandidat (free% <50%, velocity belum terhitung, X unverified). TIDAK DIEKSEKUSI: website gate GAGAL (metode A/B/C/G/H/I/K/L/M dicoba — tanpa "
    "website terverifikasi; BscScan: tanpa Website/Social; IPFS collection.json tak terbaca karena gateway diblokir sandbox). Dilaporkan SEKALI run "
    "1801 sebagai strong lead + alasan gate. "
    "TRACK-C LEAD: Draco Coin (DRACO) 0x2e1927798462397a88e3c1015Dc8168e798DF6D3 — first-seen via 5c dari scan 1801; bentuk SALE S1 LOLOS (mint + "
    "currentPriceFor/price + isFreeMintAvailable + agentRegistry()=registry 0x60B9...); free user tersedia (isFreeMintAvailable=1, harga user 0, "
    "mintsOf=0); umur terverifikasi first mint 2026-11-07 18:02:30 WIB (~29 menit); stage 1, 25.000 DRACO/mint, totalMints 63 (18:31 WIB). TIDAK "
    "DIEKSEKUSI: website gate GAGAL (metode A/G/K/L/M dicoba — tanpa website terverifikasi; BscScan: tanpa Website/Social). Dilaporkan SEKALI run "
    "1801 sebagai track-C lead + alasan gate. "
    "Preflight PASS 17,7 dtk: head 132190071, 259 log/50 blok. "
    "Reread 446 kontrak + 67 track_c (blok 132190042, 683,5 dtk); 342 supply terbaca; 103 all-None (degradasi, dicatat None bukan nol — setara 102 di "
    "run 1731); 5 kontrak snapshot ber-address None tidak dibaca (Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph). "
    "Velocity 2 pass: AgentVOLT (round 1) +30 ratio 2,01 dan Sidecoo +25 ratio 1,90 — keduanya free% + umur UNVERIFIED -> BUKAN strong "
    "lead/kandidat, hanya dicatat. Sold-out tercatat 35 (sebagian besar sudah berstatus sold-out). Slot berubah: hanya NULLRAID (balanceOf 0->1, "
    "sesuai mint). HIVE Agents totalSupply 1255 flat, balanceOf(user)=1, minted-by-user. NULLRAID mint TERVERIFIKASI (freeClaims=1, balance=1, "
    "ownerOf(503)=wallet agent; totalSupply 537, freeMints 537/1111 = 48,3%). NeoGods 1736/3333, umur ~8,1 jam, free% UNVERIFIED + gate GAGAL -> "
    "tetap watchlist-only. "
    "Age sweep: 0 kandidat penghapusan; 44 kept (minted-by-user/same-owner-discarded); 378 umur UNVERIFIED. "
    "Boltbook EN+ZH FRESH (curl, HTTP 200, 25 kartu, rotasi penuh vs 1731) + 6 post + 3 author deep-read — 0 lead baru; Orin Agent ditolak "
    "(Sourcify unverified, 0 mint/100.000 blok, umur >48 jam); BYTE share sale hanya watch nama (tanpa alamat kontrak, belum terverifikasi "
    "Sourcify, tanpa LP); PassAgentX sudah age-excluded run 0701 (tidak dilaporkan ulang); Paw Gang buka malam ini 20:00 WIB (tanpa kontrak). "
    "Sweep EN+ZH + Square/Odaily/PANews/DappBay — 0 proyek baru. $SWARM (swarmbnb.fun) bukan track C (semua share berbayar, 0/444.000). M3M3: "
    "census gate lewat, refund phase, mint masih LIVE. Razor genesis BELUM dimulai (pair kosong). WHALE NFT kontrak B gate tetap GAGAL. "
    "Scan leg: window 132189133-132190132 (1000 blok, cap; head 132190132; gap 132184220-132189071 tercatat, backfill sudah menutup s.d. 132188665), "
    "chunk 20/20 selesai (0 error, 40 panggilan Ankr), 118 ERC721 + 5 ERC1155 + 318 ERC-20-mint; enrichment STALL di 71/123 -> timeout 700 dtk "
    "(SCAN_EXIT=124, pola stall berulang); 71 kontrak ter-enrich (partial JSON terselamatkan, partial=True). Watermark TIDAK dimajukan run ini "
    "(tetap 132188665, milik backfill). Gap tersisa 132188666-132189132 (467 blok) untuk backfill. Triage scan: 2 first-seen — NBC (di atas) + xm "
    "0xd5D284C72A16969b7fb313dEbd3B64015BF74199 (14 mint/2 minter, Sourcify not_verified, tanpa registry/free-shape -> bukan agent-shaped, hanya dicatat). "
    "TPET 0x31975837D5C68Eea0B66b5Fd27De3506c2f109ba (73 mint/73 minter) first-seen oleh backfill (blok 132188200), sudah di seen file — bukan temuan job ini. "
    "5a Sourcify feed 20 kontrak: 0 shape hit (sourcify.dev terjangkau run ini, 0 error — berbeda dari run 1731). 5c dari scan 1731: 51 >=10, semua "
    "sudah dicek, 0 baru, 0 hit. 5c-extra dari scan 1801: 3 baru dicek — 0x86fe... (not_verified), 0x2e19... DRACO (LEAD, di atas), 0xA010... "
    "(not_verified); checked list kini 2510 alamat. "
    "Track B: pending_claims kosong; BINANCEAI re-check identik run 1701 (refund/failed, sudah dilaporkan — tidak dilaporkan ulang); Grove freeOpen 0, "
    "freeClaimed_user false. "
    "Bridge: tidak berubah (mtime 2026-11-06 02:48); 0 promosi/perubahan."
)
snap["last_run"] = RUN
snap["last_run_wib"] = TS
tmp = f"{BASE}/onchain-snapshot.json.tmp"
with open(tmp, "w") as f:
    json.dump(snap, f, indent=1)
os.replace(tmp, f"{BASE}/onchain-snapshot.json")

# seen file: append NBC + xm (reload at write time; TPET already present)
seen_path = f"{BASE}/onchain-scan-seen.json"
seen = json.load(open(seen_path))
seen.setdefault("contracts", {})["0xa849aed9dc19fba823ccef1fa01bda72fbb8fcdf"] = 132189223
seen["contracts"]["0xd5d284c72a16969b7fb313debd3b64015bf74199"] = 132190123
seen["_meta"]["contracts_count"] = len(seen["contracts"])
with open(seen_path, "w") as f:
    json.dump(seen, f, indent=1)

# track-c checked: add the 3 ERC-20s from scan 1801 (case-insensitive dedupe)
chk_path = f"{BASE}/track-c-scan-checked.json"
chk = json.load(open(chk_path))
lst = chk.setdefault("checked", [])
low = {a.lower() for a in lst}
for a in ["0x86fe61F62CD7999049C2c33523bBf86FDE1ED6F5",
          "0x2e1927798462397a88e3c1015Dc8168e798DF6D3",
          "0xA01012318D8A1DEF6Fac5ff1A9193140a77B9BA3"]:
    if a.lower() not in low:
        lst.append(a); low.add(a.lower())
chk["0x2e1927798462397a88e3c1015Dc8168e798DF6D3"] = {
    "source": "run-1801-5c-extra", "status": "track-c-lead-gate-blocked",
    "mint_count": 15, "note": "S1 shape passes (mint + currentPriceFor/price + isFreeMintAvailable + agentRegistry()=registry); free user available, price 0; age verified 18:02:30 WIB; website gate FAILED run 1801 — NOT minted."}
chk["0x86fe61F62CD7999049C2c33523bBf86FDE1ED6F5"] = {
    "source": "run-1801-5c-extra", "status": "checked-not-verified",
    "mint_count": 20, "note": "Sourcify not_verified (404) — shape unknown, recorded checked, never re-checked."}
chk["0xA01012318D8A1DEF6Fac5ff1A9193140a77B9BA3"] = {
    "source": "run-1801-5c-extra", "status": "checked-not-verified",
    "mint_count": 11, "note": "Sourcify not_verified (404) — shape unknown, recorded checked, never re-checked."}
with open(chk_path, "w") as f:
    json.dump(chk, f, indent=1)

# state note (scan partial; watermark untouched by this run)
st_path = f"{BASE}/onchain-scan-state.json"
st = json.load(open(st_path))
st["note_1801_scan_partial"] = (
    "Run 1801 scan (route 4): window 132189133-132190132 (1000 blok, cap dari head 132190132; watermark 132184219 -> head 132190071 = 5852 blok, "
    "hanya 1000 blok terbaru di-scan; gap 132184220-132189071 tercatat; backfill sudah menutup s.d. 132188665 saat run ini), chunk 20/20 selesai "
    "(0 error, 40 panggilan Ankr), 118 ERC721 + 5 ERC1155 + 318 ERC-20-mint; enrichment STALL di 71/123 -> timeout 700 dtk (SCAN_EXIT=124, pola "
    "stall berulang seperti run 1601/1631/1701/1731); 71 kontrak ter-enrich (partial JSON terselamatkan, partial=True). Watermark TIDAK dimajukan "
    "run ini (tetap 132188665, milik backfill). Gap tersisa 132188666-132189132 (467 blok) untuk backfill. Triage scan 2 first-seen (NBC strong lead "
    "gate-blocked + xm bukan agent-shaped); 5c-extra 3 dicek (DRACO track-C lead gate-blocked)."
)
with open(st_path, "w") as f:
    json.dump(st, f, indent=1)
print(f"FINALIZE-1801 updated={updated} none_free={none_free} vel_updated={vel_updated} removed_age={len(removed)} contracts={len(snap['contracts'])} track_c={len(snap.get('track_c', {}))} ts={TS}", flush=True)
