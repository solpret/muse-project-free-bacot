#!/usr/bin/env python3
"""Merge run 2301 reread + triage into onchain-snapshot.json. Read-only except snapshot.
INTERVAL 23.32 min (blocks 132611007 -> 132614113, timestamps 1794239278 -> 1794240677)."""
import json, datetime, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 23.32
BLOCK = 132614113
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2301-reread.json"))
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
    # sold-out detection: free counter reached free supply (was not before)
    if isinstance(fs, int) and fs and isinstance(fcl, int) and fcl >= fs and "sold-out" not in str(v.get("status")):
        soldout_new.append((name, fcl, fs))
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = NOW_WIB
    v["runNote2301_1109"] = (f"Run 2301 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2231): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
    # strong-lead screen: free% >=25, slot open, not excluded/sold-out/minted
    st = str(v.get("status") or "")
    if (isinstance(v.get("freePctVerified"), (int, float)) and v["freePctVerified"] >= 25
        and not any(x in st for x in ("sold-out","excluded","minted-by-user","age-excluded","discarded"))):
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
    n_tc += 1
# --- STAR CARDS early lead (new, run 2301) ---
contracts["STAR CARDS"] = {
    "address": "0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1",
    "name": "STAR CARDS",
    "symbol": "STAR",
    "status": "early-lead-2026-11-09",
    "kind": "nft-erc721",
    "totalSupply": 5,
    "freeMinted": 5,
    "FREE_SUPPLY": 5000,
    "freeRemaining": 4995,
    "FREE_PER_WALLET": 5,
    "freeClaimedBy_user": 0,
    "priceFor_user": 1000000000000000,
    "balanceOf_user": 0,
    "freeStartEpoch": 1794239944,
    "freeStartWib": "2026-11-09 23:15:44 WIB",
    "dripStartEpoch": 1794499200,
    "creator": "0xb07b263ffb129575142537fa307f24e6a435f78a",
    "creator_in_discards": False,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "agentGating": "AGENT_ID() returns EXACT registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; ABI claimFree()/freeMinted()/FREE_SUPPLY()/FREE_PER_WALLET()/priceFor(address); Sourcify verified (verifiedAt 2026-11-09T16:02:13Z)",
    "freePctVerified": 0.1,
    "xVerified": False,
    "website": None,
    "velocityVerified": False,
    "velocityLegPasses": False,
    "lastReadBlock": 132614694,
    "lastReadWib": NOW_WIB,
    "baselineNote": ("EARLY LEAD run 2301 (dilaporkan sekali run ini). Ditemukan via route 5a feed Sourcify (verifiedAt 2026-11-09T16:02:13Z, "
      "belum di hot-leg-seen/reported saat triase). Triase segar blok 132614694: ERC-721 STAR CARDS (STAR), totalSupply 5, freeMinted 5/5000 = 0,1% "
      "(<25% strong lead, <50% kandidat), freeRemaining 4995, FREE_PER_WALLET 5, freeClaimedBy(user)=0 (slot TERBUKA), priceFor(user)=0,001 BNB "
      "(jalur berbayar; jalur gratis claimFree()), freeStart on-chain 1794239944 = 23:15:44 WIB 2026-11-09 (umur ~5 mnt saat triase, TERVERIFIKASI <=48 jam), "
      "dripStart 1794499200 (~2026-11-12). AGENT_ID() = registry persis. Creator 0xb07b263ffb129575142537fa307f24e6a435f78a TIDAK ada di same-owner-discards.json. "
      "Website + X UNVERIFIED (belum dicari mendalam - early lead tidak butuh gate; deep-dive menyusul bila promosi). TIDAK preview/mint (early lead)."),
    "runNote2301_1109": "Run 2301: EARLY LEAD baru (lihat baselineNote). Masuk snapshot watchlist untuk tracking velocity/free%.",
}
# --- PIXEL MONSTERS note ---
px = contracts.get("PIXEL MONSTERS")
px_note = ""
if isinstance(px, dict):
    fm = px.get("freeMinted")
    px["freePctVerified"] = round(100.0 * fm / 2000, 2) if isinstance(fm, int) else px.get("freePctVerified")
    px_note = (f"PIXEL MONSTERS: total {px.get('totalSupply')} (prev {px.get('previousTotalSupply')}, +{px.get('mintedInInterval')}, "
               f"ratio {px.get('velocityRatio')} -> velocity {'LOLOS' if px.get('velocityLegPasses') else 'GAGAL'}); "
               f"freeMinted {fm}/2000 = {px.get('freePctVerified')}% (strong lead butuh >=25%); slot user terbuka; tetap early lead.")
    px["runNote2301_1109"] = "Run 2301: " + px_note + " TIDAK preview/mint."
# --- 0x4Bc1A172 sale note ---
sale = track_c.get("0x4Bc1A172-sale")
if isinstance(sale, dict):
    sale["runNote2301_1109"] = ("Run 2301: sale MASIH BELUM BUKA (SALE_START 2026-11-10 12:00 WIB); freeMinted 0. "
        "Status tetap watchlist-only-not-open; dicek ulang saat buka; TIDAK dilaporkan.")
snap["last_run"] = 2301
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2301: 620 kontrak + 87 track_c re-read (blok 132614113, 724,0 dtk, interval 23,32 mnt vs run 2231); "
    "EARLY LEAD BARU 1: STAR CARDS 0x8b059e61 (5/5000 free, AGENT_ID registry persis, freeStart 23:15 WIB, slot terbuka) - dilaporkan sekali; "
    "0 kandidat/strong lead/track-C baru; 0 sold-out baru; PIXEL MONSTERS tetap early lead; "
    "5a: 22 alamat baru feed Sourcify, 1 S1 hit 0x5a52fe87 (SAMO) TAPI free pool 0/9000 (publicFreeRemaining 0, totalShares 9000, launched 0) - bukan lead, log saja; "
    "scan fast-fail Ankr 401 (preflight 5,5 dtk, head 132614189; watermark 132512564, gap ~101.625 blok); binanceai tetap refund; Grove freeOpen=0.")
snap["runNote2301_1109"] = snap["last_run_note"]
snap["runNote2301_1109_scan"] = ("Run 2301 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 Unauthorized (5,5 dtk, head 132614189); "
    "outage sejak ~13:33 WIB 2026-11-09 (~9,7 jam); watermark TETAP 132512564, gap ~101.625 blok ke head saat preflight. "
    "Backfill bukan tugas job ini; reconnect Ankr belum terverifikasi pulih.")
snap["runNote2301_1109_binanceai"] = ("Run 2301 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132614189). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2301_1109_5a"] = ("Run 2301 route 5a: 22 alamat BARU feed Sourcify (verifiedAt 15:49-16:13Z; 3 sisanya sudah hot-leg-seen/snapshot), "
    "1 S1 hit: 0x5a52fe87 (sale SAMO, token 0xf62ca1fe; mint+quote+freeSharesRemaining/freeSharesClaimed+AGENT_ID_REGISTRY persis) TAPI free pool HABIS "
    "(freeSharesRemaining 0, publicFreeRemaining 0, totalShares 9000/9000 FREE_SHARES, totalPaidShares 0, launched 0, saleClockStart 1794240385) - BUKAN lead, "
    "tidak masuk snapshot, log saja. 0x8b059e61 (STAR CARDS) S1 False/S2 False tapi agent-shaped NFT -> EARLY LEAD (lihat baselineNote). "
    "Sisanya 20 alamat: 0 S1/S2 hit. 5c: tidak ada output scan baru (scan fast-fail sejak 13:33); tidak ada ERC-20 baru dicek run ini.")
snap["runNote2301_1109_velocity"] = ("Run 2301 velocity LOLOS: " + ("; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) if vel_pass else "TIDAK ADA") +
    ". " + px_note)
snap["runNote2301_1109_discovery"] = ("Run 2301 rute 2: Boltbook EN 46.519 byte + ZH 46.710 byte, rc 200; baru vs run 2231: AGENT 888 SEASON 2 0x1c963acf (33/888, first mint 21:15 WIB) - "
    "BUKAN agent-shaped (ABI ERC-721 polos: mint/mintOpen/mintedByWallet/season1, tanpa registry/free view) -> bukan early lead, log saja; "
    "DogePunk 0xea404392 (5.000/5.000, 0 free left, 10 hari) - sold out + umur lewat -> log saja; NEURA recheck (claimFree sim lolos, 198 klaim, claimOpen 1) - "
    "tetap checked-not-lead (tanpa pair + bukan agent-shaped, sesuai triase 1831; post sendiri mengakui tanpa pair/pasar); NEON District CY01 755/778 (tinggal 23). "
    "Rute 3: sweep EN+ZH - tidak ada proyek baru (hanya recheck/ulang: MOLT, Horus, AGC/AGENT MAO/MALTA/YAMA sudah dikenal). "
    "Rute 6: Odaily 250.447 byte + PANews 119.190 byte, rc 200, 0 mention Agent ID/free-mint. DappBay tidak dikonsultasikan (tidak ada kandidat yang memerlukannya). "
    "Bridge: tidak berubah (mtime ~01:38 WIB 2026-11-09); 8 kontrak bridge belum di snapshot sama seperti run 2231 (ERC-20 finding tracked-wallet / 1 same-owner-discarded) - tidak ada penambahan ke snapshot run ini.")
snap["runNote2301_1109_grove"] = ("Run 2301 Grove: freeOpen=0 (blok 132612967, file run-2026-11-09-2301-grove-check.json, grove-check job 23:02 WIB) - belum buka.")
snap["runNote2301_1109_starcards"] = ("Run 2301 STAR CARDS early lead (lihat contracts['STAR CARDS'].baselineNote): ERC-721 0x8b059e611E5f16b4659f81698CDbcB3dcfcDFDF1, "
    "Sourcify verifiedAt 2026-11-09T16:02:13Z; AGENT_ID() = registry persis 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; claimFree() + FREE_SUPPLY 5000; "
    "totalSupply 5, freeMinted 5 (0,1%), freeRemaining 4995, FREE_PER_WALLET 5, freeClaimedBy(user)=0 (slot TERBUKA), priceFor(user)=0,001 BNB (jalur berbayar); "
    "freeStart on-chain 1794239944 = 23:15:44 WIB (umur ~5 mnt, TERVERIFIKASI <=48 jam); dripStart 1794499200. Creator 0xb07b263ffb129575142537fa307f24e6a435f78a "
    "TIDAK di discards. Website + X UNVERIFIED. Dilaporkan sekali sebagai EARLY LEAD; TIDAK preview/mint; masuk snapshot watchlist.")
snap["runNote2301_1109_age_exclusions"] = ("Run 2301 age-exclusions baru: 0. Item >48h yang sama seperti run 2231 (Night Bandits Club, Pocket Ai, King's Game) "
    "dipertahankan sebagai age-watch dengan alasan yang sama (free-quota gagal baca / launchNote tidak tegas / status non-aktif) - tidak ada informasi baru run ini "
    "yang mengubah keputusan; tidak dihapus.")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass}")
print("soldout_new:", soldout_new)
print("free>=25% screen:", json.dumps(free25, indent=1)[:3000])
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
print("PX:", px_note)
