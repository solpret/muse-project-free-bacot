#!/usr/bin/env python3
"""Merge run 2331 reread + triage into onchain-snapshot.json. Read-only except snapshot.
INTERVAL 35.8 min (blocks 132614113 -> 132618916, timestamps 1794240677 -> 1794242825)."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 35.8
BLOCK = 132618916
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2331-reread.json"))
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
    v["runNote2331_1109"] = (f"Run 2331 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2301): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
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
# --- PIXEL MONSTERS note ---
px = contracts.get("PIXEL MONSTERS")
px_note = ""
if isinstance(px, dict):
    fm = px.get("freeMinted")
    px["freePctVerified"] = round(100.0 * fm / 2000, 2) if isinstance(fm, int) else px.get("freePctVerified")
    px_note = (f"PIXEL MONSTERS: total {px.get('totalSupply')} (prev {px.get('previousTotalSupply')}, +{px.get('mintedInInterval')}, "
               f"ratio {px.get('velocityRatio')} -> velocity {'LOLOS' if px.get('velocityLegPasses') else 'GAGAL'}); "
               f"freeMinted {fm}/2000 = {px.get('freePctVerified')}% (strong lead butuh >=25%); slot user terbuka; tetap early lead.")
    px["runNote2331_1109"] = "Run 2331: " + px_note + " Free lane baru dibuka 21:35 WIB (Boltbook). TIDAK preview/mint."
# --- 0x4Bc1A172 sale note ---
sale = track_c.get("0x4Bc1A172-sale")
if isinstance(sale, dict):
    sale["runNote2331_1109"] = ("Run 2331: sale MASIH BELUM BUKA (SALE_START 2026-11-10 12:00 WIB); freeMinted 0. "
        "Status tetap watchlist-only-not-open; dicek ulang saat buka; TIDAK dilaporkan.")
# --- POCKET AI AGE-EXCLUSION (body age rule) ---
# Launch terverifikasi on-chain: first mint 2026-11-07 10:41:45 WIB (blok 132130472, backfill)
# -> umur ~61 jam pada run 2331 (>48 jam). Belum sold out: totalMinted 1396 -> 1413/5555
# (baca segar run ini, blok 132618916) + post Boltbook 23:xx WIB totalMinted 1.406,
# mintFree() sim PASS -> mint masih buka. Free-quota reading: TIDAK BISA dibaca
# (Sourcify rc 400, tanpa ABI, free views revert/None). Website BARU terverifikasi
# run ini (pocket.agenticwallet.workers.dev mencetak kontrak persis) - bukan alasan
# menahan: umur yang menggugurkan. Preseden penahanan 2231/2301 ("launchNote kosong")
# tidak lagi berlaku: firstMintWib terverifikasi on-chain di entry; ketidakpastian
# arah hanya membuat umur LEBIH tua. Dihapus dari contracts + dilaporkan sekali.
pocket = contracts.pop("Pocket Ai", None)
pocket_evidence = None
if pocket is not None:
    pocket_evidence = {
        "address": pocket.get("address"),
        "status_before": pocket.get("status"),
        "firstMintWib": pocket.get("firstMintWib"),
        "firstMintBlock": pocket.get("firstMintBlock"),
        "ageHoursAtRemoval": "~61",
        "totalMinted_before": 1396,
        "totalMinted_run2331": 1413,
        "MAX_SUPPLY": 5555,
        "freeQuotaReading": "UNVERIFIED (Sourcify rc 400, no ABI, free views None)",
        "stillMintingEvidence": "totalMinted +17 dalam interval run ini (1396->1413, blok 132618916); post Boltbook zeeke.ai /p/deuKVHCRDbzL totalMinted 1.406, mintFree() sim PASS",
        "website": "https://pocket.agenticwallet.workers.dev (terverifikasi run ini, mencetak kontrak persis; TIDAK membatalkan age-exclusion)",
        "removedWib": NOW_WIB,
        "reportedOnce": True,
    }
snap["last_run"] = 2331
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2331: 621 kontrak + 87 track_c re-read (blok 132618916, interval 35,8 mnt vs run 2301); "
    "0 kandidat/strong lead/track-C baru; 0 sold-out baru; AGE-EXCLUSION 1: Pocket Ai (early lead 2026-11-07) dihapus dari watchlist "
    "(umur terverifikasi ~61 jam >48 jam, totalMinted 1413/5555, mint masih buka) - dilaporkan sekali; "
    "PIXEL MONSTERS tetap early lead (freeMinted 430/2000 = 21,5% <25%); STAR CARDS tanpa perubahan (5/5000); "
    "scan fast-fail Ankr 401 (preflight 8,3 dtk, head 132617367; watermark 132512564, gap ~104.803 blok); binanceai tetap refund; Grove freeOpen=0.")
snap["runNote2331_1109"] = snap["last_run_note"]
snap["runNote2331_1109_scan"] = ("Run 2331 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 Unauthorized (8,3 dtk, head 132617367); "
    "outage sejak ~13:33 WIB 2026-11-09 (~10,3 jam); watermark TETAP 132512564, gap ~104.803 blok ke head saat preflight. "
    "Backfill bukan tugas job ini; reconnect Ankr belum terverifikasi pulih.")
snap["runNote2331_1109_binanceai"] = ("Run 2331 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132617590). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2331_1109_5a"] = ("Run 2331 route 5a: 5 alamat BARU feed Sourcify (verifiedAt 16:13:08-16:33:18Z; sisanya sudah hot-leg-seen/snapshot), "
    "0 S1/S2 hit - tidak ada lead track-C baru. 0xC8113f80 sudah dicek di 2301 (hasil sama). "
    "5c: tidak ada output scan baru (scan fast-fail sejak 13:33); tidak ada ERC-20 baru dicek run ini.")
snap["runNote2331_1109_velocity"] = ("Run 2331 velocity LOLOS: " + ("; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) if vel_pass else "TIDAK ADA") +
    ". " + px_note)
snap["runNote2331_1109_discovery"] = ("Run 2331 rute 2: Boltbook EN 45.303 byte + ZH 45.477 byte, rc 200 (curl pertama rc=302, retry -L ok). "
    "Baru vs run 2301: Pocket Ai 0xf9d00b7a (post zeeke.ai /p/deuKVHCRDbzL, totalMinted 1.406, situs pocket.agenticwallet.workers.dev, X @Agentic_Pocket) - "
    "BUKAN baru: sudah di snapshot sebagai early-lead-backfill (dilaporkan 2026-11-07 ~11:10 WIB); triase run ini: website TERVERIFIKASI (situs mencetak kontrak persis), "
    "Sourcify rc 400 TIDAK terverifikasi (klaim post exact_match SALAH), free path tetap UNVERIFIED, umur ~61 jam -> AGE-EXCLUDED run ini (lihat age_exclusions); "
    "PAXP 0x08b1a979 (5.090/6.666, +13/~3 jam, free lane unverified, bukan klaim free-mint); BASKET 0xa855a032 (solve() proof-of-work, bukan free mint polos). "
    "Update item dikenal: AGTC freeMinted 516->527/1.000 tapi lane stall 0 mint ~45 mnt (gate FAILED run 1931, tetap); PIXEL MONSTERS free lane baru dibuka 21:35 WIB, "
    "1.587/2.000 free left; Marbleworks 940/1.111 free (slot user terpakai); HOPKIN 4.321/10.000; WOJAGENT ~455 gratis tersisa (tetap age-excluded); "
    "Lion's Share 765/1.450 flat (tetap age-excluded); A888S2 41/888 (tetap bukan agent-shaped); BYTE + KZMB tanpa alamat kontrak di post (tidak bisa diverifikasi). "
    "DogePunk/NEURA/MALTA sudah rotasi keluar front page. "
    "Rute 3: sweep EN+ZH - 0 lead gratis baru; SYMBOL share sale (sale 0x34e81BfE, token 0x265b2a6b, symbolai.pages.dev/sale) PAID-only (tier 1,00-1,30 USDT/share, tanpa tier gratis); "
    "sisanya item lama/dikenal. "
    "Rute 6: Odaily 249.653 byte + PANews 119.190 byte, rc 200, 0 mention Agent ID/free-mint/free-share. DappBay dilewati (tidak ada kandidat baru yang butuh cek website-evidence; Pocket Ai sudah membawa link situs di post). "
    "Bridge: tidak berubah (mtime 2026-11-09 01:21:53 WIB); 7 kontrak belum di snapshot (6 non-discarded + 1 discarded 0x0aa11f32), semuanya temuan lama - bukan lead baru.")
snap["runNote2331_1109_grove"] = ("Run 2331 Grove: freeOpen=0 (blok 132617002, grove-watch-state.json, cek 23:31 WIB) - belum buka; per body rule freeOpen==0: diam, tidak dilaporkan.")
snap["runNote2331_1109_age_exclusions"] = ("Run 2331 age-exclusions baru: 1 - POCKET AI dihapus dari watchlist aktif (lihat runNote2331_1109_pocket). "
    "Night Bandits Club + King's Game dipertahankan sebagai age-watch seperti run 2231/2301 (tidak ada info baru run ini yang mengubah keputusan: NBC baca free-quota gagal lagi "
    "(semua view None) sehingga 'belum sold out' tidak bisa diverifikasi + status strong-lead-gate-blocked non-aktif; King's Game launchNote UNVERIFIED + totalMinted 3).")
snap["runNote2331_1109_pocket"] = ("Run 2331 POCKET AI AGE-EXCLUDED (early lead 2026-11-07 ~11:10 WIB, kontrak 0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102): "
    "dihapus dari snapshot contracts. Bukti: launch TERVERIFIKASI on-chain first mint 2026-11-07 10:41:45 WIB (blok 132130472, backfill) -> umur ~61 jam >48 jam pada run ini; "
    "belum sold out: totalMinted 1.396 -> 1.413/5.555 (baca segar blok 132618916, +17 dalam interval) + post Boltbook 23:xx WIB totalMinted 1.406, mintFree() sim PASS; "
    "free-quota reading: UNVERIFIED (Sourcify rc 400, tanpa ABI, free views None) - dicatat apa adanya, bukan sebagai lolos; "
    "website BARU terverifikasi run ini (pocket.agenticwallet.workers.dev mencetak kontrak persis) - tidak membatalkan age-exclusion; "
    "owner 0x9aab2a878f40323af113e5528afe74e4b21a0401 tidak di same-owner-discards. Dilaporkan sekali sebagai age-exclusion; "
    "hanya ditambahkan lagi bila ada mint phase/batch baru yang terverifikasi.")
snap["runNote2331_1109_starcards"] = ("Run 2331 STAR CARDS: tanpa perubahan (totalSupply 5, freeMinted 5/5000 = 0,1%, slot terbuka) - tetap early lead, TIDAK preview/mint, tidak dilaporkan ulang.")
if pocket_evidence is not None:
    snap["age_excluded_2331_pocket_ai"] = pocket_evidence
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass}")
print("soldout_new:", soldout_new)
print("free>=25% screen:", json.dumps(free25, indent=1)[:3000])
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
print("PX:", px_note)
print("POCKET removed:", pocket_evidence is not None)
