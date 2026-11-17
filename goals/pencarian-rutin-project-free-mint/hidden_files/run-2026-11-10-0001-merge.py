#!/usr/bin/env python3
"""Merge run 0001 (2026-11-10 00:01 WIB) reread + triage into onchain-snapshot.json.
INTERVAL 16.8 min (blocks 132618916 -> 132621152, ~0.45s/block). Read-only except snapshot."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 16.8
BLOCK = 132621152
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-10-0001-reread.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []; soldout_new = []; free25 = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]:
            vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    if isinstance(fs, int) and fs and isinstance(fcl, int) and fcl >= fs and "sold-out" not in str(v.get("status")):
        soldout_new.append((name, fcl, fs))
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0001_1110"] = (f"Run 0001 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2331): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
    st = str(v.get("status") or "")
    if (isinstance(v.get("freePctVerified"), (int, float)) and v["freePctVerified"] >= 25
        and not any(x in st for x in ("sold-out", "excluded", "minted-by-user", "age-excluded", "discarded"))):
        free25.append((name, v.get("freePctVerified"), v.get("freeClaimed_user"), v.get("balanceOf_user"), st,
                       v.get("startTimeWib"), v.get("launchTime"), v.get("xVerified"), v.get("website")))
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict):
        continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote0001_1110"] = f"Run 0001 track_c re-read (blok {BLOCK}): {r}."
    n_tc += 1
# --- PIXEL MONSTERS note ---
px = contracts.get("PIXEL MONSTERS")
px_note = ""
if isinstance(px, dict):
    fm = px.get("freeMinted")
    px["freePctVerified"] = round(100.0 * fm / 2000, 2) if isinstance(fm, int) else px.get("freePctVerified")
    px_note = (f"PIXEL MONSTERS: total {px.get('totalSupply')} (prev {px.get('previousTotalSupply')}, +{px.get('mintedInInterval')}, "
               f"ratio {px.get('velocityRatio')} -> velocity {'LOLOS' if px.get('velocityLegPasses') else 'GAGAL'}); "
               f"freeMinted {fm}/2000 = {px.get('freePctVerified')}% (strong lead butuh >=25%); slot user terbuka; tetap early lead.")
    px["runNote0001_1110"] = "Run 0001: " + px_note + " TIDAK preview/mint."
# --- STAR CARDS note ---
sc = contracts.get("STAR CARDS")
sc_note = ""
if isinstance(sc, dict):
    sc_note = (f"STAR CARDS: totalSupply {sc.get('totalSupply')}, freeMinted {sc.get('freeMinted')}/5000 "
               f"= {sc.get('freePctVerified')}%; tetap early lead, TIDAK preview/mint.")
# --- 0x4Bc1A172 sale note ---
sale = track_c.get("0x4Bc1A172-sale")
sale_note = ""
if isinstance(sale, dict):
    sale_note = (f"0x4Bc1A172 sale: freeMinted {sale.get('freeMinted')} (reread run 0001); "
                 "SALE_START 2026-11-10 12:00 WIB - MASIH BELUM BUKA; tetap watchlist-only-not-open.")
    sale["runNote0001_1110"] = "Run 0001: " + sale_note
# --- STAMP PASS early lead (new, run 0001) ---
stamp = {
    "address": "0x202dcfbC011fF5697D13022e7Bc57Ede7237a37e",
    "name": "STAMP PASS", "symbol": "STAMPPASS", "kind": "ERC721",
    "status": "early-lead-2026-11-10",
    "totalSupply": 13, "totalMinted": 13, "freeMinted": 13, "paidMinted": 0,
    "freeAllocation": 111, "freeRemaining": 98, "maxSupply": 5555,
    "mintPrice": 1000000000000000, "mintOpen": 1, "maxFreePerWallet": 1,
    "canClaimFree_user": True, "hasAgentId_user": True, "freeMintedBy_user": 0,
    "balanceOf_user": 0, "owner": "0x2193d6e0468ac747823e7e876f1acd34ffe43a67",
    "agentId_registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "stampToken": "0xA5c198ab79E54738C8A3b528Ab572579bE189320",
    "rewardPerMint": 10000000000000000000000,
    "website": "https://stamppass.pages.dev",
    "website_verified": True,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur peluncuran UNVERIFIED (first-mint timestamp belum terverifikasi; Ankr getLogs mati 401. Indikasi segar: Sourcify verifiedAt 2026-11-09T17:03:37Z / 2026-11-10 00:03:37 WIB; situs menyatakan deployed 2026-11-10).",
    "firstSeenBlock": 132622128, "lastReadBlock": 132622128,
    "lastReadWib": NOW_WIB,
    "baselineNote": ("Run 0001 route 5a retry: Sourcify feed verifiedAt 17:03:37Z; S1 shape (mint+mintPrice+freeMinted+agentId). "
        "Baca segar blok 132622128: totalMinted 13, freeMinted 13/111 (11,7%), paid 0, mintOpen 1, canClaimFree(user)=true, "
        "hasAgentId(user)=true, freeMintedBy(user)=0. agentId()=registry 0x60B9... terverifikasi on-chain. Sourcify exact source "
        "StampPass.sol (IAgentId balanceOf gate). Website TERVERIFIKASI stamppass.pages.dev (mencetak NFT_ADDRESS + TOKEN_ADDRESS persis). "
        "X discussion UNVERIFIED (pencarian kontrak/nama nihil). Owner 0x2193... tidak di same-owner-discards (owner sama dengan NEURA, checked-not-lead). "
        "EARLY LEAD dilaporkan sekali run 0001; TIDAK preview/mint (early tidak pernah auto-mint)."),
}
contracts["STAMP PASS"] = stamp
# --- WNO watchlist-only (hot-leg 2339 follow-up, run 0001) ---
wno = {
    "address": "0x8C969a4CD49E4774908e667702C3d7C3ece164D0",
    "name": "War Need Over", "symbol": "WNO", "kind": "ERC20",
    "status": "watchlist-only-age-unverified-2026-11-10",
    "totalSupply": 6000000000000000000000000000,
    "FREE_SHARES": 3000, "totalFreeShares": 19, "freeRemaining": 2981,
    "totalPaidShares": 0, "totalShares": 19, "totalRaised": 0,
    "PRICE": 1000000000000000, "TOKENS_PER_SHARE": 1000000000000000000000000,
    "MAX_SHARES": 6000, "quote_user_1_cost": 0, "freeUsed_user": False,
    "isAgent_user": True, "balanceOf_user": 0, "sharesOf_user": 0,
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "website": None, "xVerified": False,
    "launchNote": "Umur UNVERIFIED (first-mint time belum terverifikasi; BscScan read didelegasikan ke live browser task browser-task:d68625bb-8523-5719-800a-e5b2381bf4a4, menunggu hasil).",
    "lastReadBlock": 132621661, "lastReadWib": NOW_WIB,
    "baselineNote": ("Hot-leg 2339 S1 sale-shape (verified 23:40:24 WIB): pool 12/3000 free. Run 0001 baca ulang blok 132621661: "
        "totalFreeShares 19 (+7), freeRemaining 2981, quote(user,1) cost 0/free 1, freeUsed(user)=false, isAgent=true, slot terbuka. "
        "Website TIDAK ditemukan (metode A-D,G,H,I,M + pencarian nama/kontrak run 0001 nihil; L BscScan menunggu browser task). "
        "WATCHLIST-ONLY (umur unverified + website belum terverifikasi) - bukan lead, TIDAK preview/mint."),
}
track_c["War Need Over"] = wno
snap["last_run"] = 1
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = (f"Run 0001 (2026-11-10 00:01 WIB): 620 kontrak + 87 track_c re-read (blok {BLOCK}, interval {INTERVAL} mnt vs run 2331); "
    "1 EARLY LEAD BARU: STAMP PASS (dilaporkan sekali); 0 kandidat/strong lead/track-C lead baru; 0 sold-out baru; 0 age-exclusion baru; "
    "WNO ditambahkan sebagai watchlist-only (umur unverified, website belum ditemukan; BscScan browser task menunggu); "
    "scan fast-fail Ankr 401 (preflight 8,1 dtk, head 132621069; watermark 132512564, gap ~108.505 blok); binanceai tetap refund; Grove freeOpen=0.")
snap["runNote0001_1110"] = snap["last_run_note"]
snap["runNote0001_1110_scan"] = ("Run 0001 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 Unauthorized (8,1 dtk, head 132621069); "
    "outage sejak ~13:33 WIB 2026-11-09 (~10,5 jam); watermark TETAP 132512564, gap ~108.505 blok ke head saat preflight. "
    "Backfill bukan tugas job ini; reconnect Ankr belum terverifikasi pulih.")
snap["runNote0001_1110_binanceai"] = ("Run 0001 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132622703). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote0001_1110_5a"] = ("Run 0001 route 5a: feed Sourcify 20 alamat (verifiedAt 16:33:16-17:03:37Z). 10 pertama timeout pada percobaan pertama, "
    "retry berhasil: 2 S1 hit - 0x8C969a4C (War Need Over WNO, sudah hot-leg 2339, watchlist-only) dan 0x202dcfbc (STAMP PASS, EARLY LEAD baru run ini). "
    "8 sisanya 0 S1/S2. 5c: tidak ada output scan baru (scan fast-fail); tidak ada ERC-20 baru dicek run ini.")
snap["runNote0001_1110_velocity"] = ("Run 0001 velocity LOLOS: " + ("; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) if vel_pass else "TIDAK ADA") +
    ". " + px_note + " " + sc_note)
snap["runNote0001_1110_discovery"] = ("Run 0001 rute 2: Boltbook EN 44.907 byte + ZH 45.111 byte, rc 200. Baru vs run 2331: AGENT 888 SEASON 2 0x1c963acf "
    "(supply 52/888, mintOpen true tapi SEMUA sim mint value-0 revert incl. mint() 'not eligible' - bukan free path terverifikasi, bukan lead); "
    "XAGENT sale 0xdb17930b (token 0xE9B4C0a6, totalMinted 4 share, tier 1 = 10.000 share @ 1,00 USDT - PAID-only, bukan lead); "
    "PAXP 0x08b1a979 (totalSupply 5.090/6.666, freeMinted 4.845, mintStart 2026-11-05 06:49:58 WIB -> umur ~4,7 hari >48 jam - AGE-EXCLUDED, bukan lead); "
    "NEURA distributor/token 0x77da87aE (sudah checked-not-lead); Lenx Agent Pass 0x6e252e3a (sudah di snapshot, strong-lead-gate-unverified); "
    "Night Shift 0x427aed3f (age-excluded, flat 9.490); Pacture 0x95AF9fe1 (10.164 shares, stall). "
    "Rute 3: sweep EN+ZH - 0 lead gratis baru; WOJAGENT (ai.wojagent.workers.dev) sudah age-excluded 2026-11-08 di snapshot, bukan baru; "
    "sisa item lama/dikenal (MALTA, YAMA, AGC, AGENT MAO paused). "
    "Rute 6: Odaily 247.695 byte + PANews 118.940 byte, rc 200, 0 mention Agent ID/free-mint/free-share/WNO/XAGENT. DappBay dilewati (tidak ada kandidat baru yang butuh cek website-evidence; STAMP PASS sudah terverifikasi via pages.dev). "
    "Bridge: tidak berubah (mtime 2026-11-09 01:21:53 WIB); 8 kontrak belum di snapshot menurut hitungan run ini (7 menurut run 2331 - selisih hitung alamat AGC token), semuanya temuan lama - bukan lead baru.")
snap["runNote0001_1110_grove"] = ("Run 0001 Grove: freeOpen=0 (blok 132620836, grove-watch-state.json, cek 2026-11-10 00:01 WIB) - belum buka; per body rule freeOpen==0: diam, tidak dilaporkan.")
snap["runNote0001_1110_stamp"] = ("Run 0001 STAMP PASS EARLY LEAD (kontrak 0x202dcfbC011fF5697D13022e7Bc57Ede7237a37e): "
    "Sourcify verifiedAt 2026-11-09T17:03:37Z (2026-11-10 00:03:37 WIB); baca segar blok 132622128: totalMinted 13, freeMinted 13/111 (11,7%), paid 0, "
    "mintOpen 1, canClaimFree(user)=true, hasAgentId(user)=true, freeMintedBy(user)=0, maxFreePerWallet 1, mintPrice 0,001 BNB (paid lane), "
    "rewardPerMint 10.000 STAMP; agentId()=registry 0x60B9... terverifikasi on-chain; Sourcify exact source StampPass.sol; "
    "website TERVERIFIKASI https://stamppass.pages.dev (mencetak NFT_ADDRESS + TOKEN_ADDRESS persis; stamppass.vercel.app adalah situs lain tanpa kontrak - bukan situs proyek); "
    "tokenURI #1: 5.555 pass, 111 free, 0,001 BNB paid, tiap mint 10.000 STAMP; contractURI revert (tanpa pointer); "
    "X discussion UNVERIFIED; umur UNVERIFIED (first-mint timestamp belum ada; indikasi segar: verified hari ini + situs 'deployed 2026-11-10'); "
    "owner 0x2193d6e0468ac747823e7e876f1acd34ffe43a67 tidak di same-owner-discards (owner sama dengan NEURA checked-not-lead). "
    "Tier EARLY (bukan kandidat/strong: free% 11,7% <25%, velocity belum ada baseline); TIDAK preview/mint. Dilaporkan sekali run ini.")
snap["runNote0001_1110_wno"] = ("Run 0001 WNO follow-up (hot-leg 2339): baca ulang blok 132621661 - totalFreeShares 12->19 (+7), freeRemaining 2981, "
    "quote(user,1) cost 0/free 1, freeUsed(user)=false, isAgent=true, slot terbuka. Website tetap TIDAK ditemukan (A/G contract+name search nihil; "
    "D same-family 404; H no contractURI; I ERC-20 no tokenURI; M site filters nihil; L BscScan menunggu live-browser task "
    "browser-task:d68625bb-8523-5719-800a-e5b2381bf4a4). Umur tetap UNVERIFIED. Ditambahkan ke snapshot track_c sebagai watchlist-only-age-unverified; "
    "bukan lead, TIDAK preview/mint.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass}")
print("soldout_new:", soldout_new)
print("free>=25% screen:", json.dumps(free25, indent=1)[:3000])
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
print("PX:", px_note)
print("SC:", sc_note)
print("SALE:", sale_note)
