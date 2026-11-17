#!/usr/bin/env python3
"""Merge run 1601 reread+vel+verifications into snapshot. FRESH for run 1601 only.
Main events run 1601:
- Velocity LOLOS 1: Sidecoo (+82, 3.73x) -> TANPA promosi (free% + slot + umur
  UNVERIFIED; note run 1231 sama). SEVENFOLD velocity GAGAL (15 token, 0.68x);
  free 1738/3000 = 57,9%; audit-block dipertahankan (token MORROW riskLevel 4 HIGH + RISK).
  THYRK velocity GAGAL (53 token, 1.34x); sudah minted-by-user.
- Cheems Agent CHEEMSA 0x00b4bdA5... (Sourcify feed): S1 PASS terverifikasi,
  free pool 1000/1000, slot user terbuka, audit riskLevel 3 MID 0 RISK hit,
  TAPI PRE-LAUNCH (mintStart 2026-11-10 17:00 WIB) + website gate BELUM ditemukan
  -> masuk track_c watchlist-only-upcoming (BUKAN lead, TIDAK preview/mint).
  Kontradiksi hot-leg 1604 ('ALL new not sale shape' vs S1_PASS) terselesaikan:
  bug label string di hot-leg-run-2026-11-10-1604.py (~baris 291); S1_PASS benar.
- PESI 0xe82BAc76... (thecolony.uk post 2026-11-09 19:16 UTC): S1 PASS terverifikasi,
  free pool 955/1000 (45 claimed), slot user TERBUKA (freeClaimed[labelhash masgayut]=false),
  umur ~14 jam (post time; first-mint on-chain tidak terkoroborasi, Ankr 401),
  owner TIDAK di discards; audit token riskLevel 2 LOW + 1 RISK hit
  ('Contract Not Renounced'); sale hasResult=false. Gate website: GAGAL (metode A-N, termasuk BscScan live browser: tanpa tautan Website/Social).
- Exit Gang 0xc014C167... (Boltbook): agent-shaped terverifikasi (AGENT_REGISTRY exact,
  freeMinted 288/333 = 86,5%) TAPI owner 0x67230d... ADA di same-owner-discards
  (grup Cz Agent/MAMESUKE/Whale Agent/Jager) -> DIBUANG per same-owner rule:
  TIDAK dilaporkan sebagai lead, TIDAK masuk snapshot. Log saja.
- Scan fast-fail Ankr 401 (preflight 6,3 dtk, head 132749752); watermark TETAP 132512564.
  Feed Sourcify 20/20 (hot-leg 1604): 1 S1 (0x00b4, pre-launch). Sweep web/sosial: 0 baru.
  binanceai.fun tetap refund/failed (sudah dilaporkan sekali). Bridge: 116 kontrak, tidak berubah.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1601"
BLOCK = 132749741
NOW = "2026-11-10 16:01 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1601-premerge")

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
        entry["intervalMinutes"] = 33.0
        entry["currentRatePerMin"] = row.get("rate")
        entry["velocityRatio"] = row.get("ratio")
        entry["velocityLegPasses"] = row.get("passes")
    updated += 1

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1601_1110"] = text

def dyn_note(name, extra=""):
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
    return (f"Run 1601 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra}")

# ---- key watchlist notes ----
note("Sidecoo", (dyn_note("Sidecoo") or "") +
     " Velocity LOLOS run ini (+82, 3,73x) TAPI TANPA promosi: free views tetap None "
     "(freeMinted/freeClaimed null, MAX_SUPPLY 2^256-1) -> free% UNVERIFIED; umur/website/X "
     "UNVERIFIED -> bukan strong lead, bukan kandidat, TIDAK preview/mint. Tetap watchlist-only.")
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " KANDIDAT tetap AUDIT-BLOCKED (dilaporkan 12:03 + 13:30; tidak dilaporkan ulang). "
     "free 1738/3000 = 57,9% >=50% tapi velocity GAGAL run ini (15 token, 0,68x). "
     "Audit-block dari run 1431 dipertahankan (token MORROW riskLevel 4 HIGH + RISK); tidak di-audit ulang run ini. TIDAK preview/mint.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user (#6849 run 1231 + 20 THYRK pending swap) -> velocity GAGAL run ini, tanpa relevansi.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> velocity tidak relevan, TANPA promosi.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user; tanpa perubahan.")
note("Zapcourier", (dyn_note("Zapcourier") or "") + " Minted-by-user; free pool 712/712 habis; tanpa perubahan.")
note("ELSY AGENT", (dyn_note("ELSY AGENT") or "") + " Pasca-mint terverifikasi: bal_user=2 (#880/#881). TIDAK di-auto-list (own market tidak live).")
note("Sakura", (dyn_note("Sakura") or "") + " Tetap early lead; first mint terverifikasi 2026-11-10 01:47 WIB -> deadline 48 jam 2026-11-12 01:47 WIB.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; first mint terverifikasi 2026-11-09 ~02:00 WIB -> deadline 48 jam 2026-11-11 ~02:00 WIB.")

# ---- Cheems Agent CHEEMSA: S1 PASS tapi PRE-LAUNCH -> track_c watchlist-only-upcoming ----
snap.setdefault("track_c", {})["Cheems Agent"] = {
    "sale": "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
    "token": "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2",
    "name": "Cheems Agent", "symbol": "CHEEMSA", "kind": "ERC20-sale-S1-single-contract",
    "status": "watchlist-only-upcoming-2026-11-10",
    "saleShape": "S1 PASS: mint/mintForSelf/claimFree + quote(uint256) + free views (freeClaimed, freeClaimedByWallet, FREE_SHARES, totalFreeMinted, FREE_PER_ID) + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify exact_match, verifiedAt 2026-11-10T09:03:00Z. S2 FAIL (tanpa mintFree no-arg / FREE_SLOTS).",
    "freePoolNote": "Free pool PENUH 1000/1000 (totalFreeMinted 0, blok 132749969 ~16:10 WIB); FREE_PER_ID 1; freeClaimedByWallet(user)=false -> slot gratis TERBUKA via claimFree(). quote(1) = 0,003 BNB adalah harga PAID mint via mint(), bukan bukti paid-only.",
    "launchNote": "PRE-LAUNCH: mintStart 1794304800 = 2026-11-10 17:00:00 WIB (~50 menit sesudah run 1601); totalMinted 0, currentState 0, tradingOpen false, pair 0x0. Deadline mint 2026-11-13 17:00 WIB; HARD_CAP 10.000 share, SOFT_CAP 2.000. Umur 48 jam dihitung sejak 17:00 WIB 10 Nov; deadline umur 17:00 WIB 12 Nov.",
    "gate": "BELUM DITEMUKAN (run 1601, metode A-N): pencarian alamat kontrak 0 hit; nama proyek EN+ZH 0 hit (hanya CHEEMS meme 2024, bukan linkage); Boltbook EN+ZH 16:04 0 mention; Sourcify tanpa URL; tanpa fungsi website/contractURI di ABI. GitHub code search butuh auth (limitasi dicatat). Metode L (BscScan token-info) belum dicoba run ini.",
    "audit": "Binance audit: hasResult=true, riskLevel 3 MID, riskAlert null, 0 hit RISK; 2 CAUTION isHit=true ('Contract Code Not Verified' — bertentangan dengan Sourcify exact_match, kemungkinan lag vendor — dan 'Newly Created Token').",
    "baselineNote": ("BARU run 1601 (Sourcify recently-verified feed, hot-leg 16:04 mencatat S1_PASS "
        "SEKALIGUS frasa 'ALL new not sale shape' — kontradiksi terselesaikan: bug label string di "
        "hot-leg-run-2026-11-10-1604.py ~baris 291; S1_PASS benar, dibuktikan fetch Sourcify segar + ABI. "
        "Verifikasi run-2026-11-10-1601-verify-00b4.json. Owner/factory 0xca14... BUKAN di same-owner-discards. "
        "BUKAN lead (belum launching + gate belum ditemukan); TIDAK preview/mint. Cek ulang pada/sesudah 17:00 WIB: "
        "konfirmasi launch (totalFreeMinted > 0) + cari ulang website; bila website terverifikasi + pool/slot terbuka "
        "+ audit tetap tanpa RISK hit -> TRACK-C LEAD."),
    "lastReadBlock": 132749969, "lastReadWib": "2026-11-10 16:10 WIB",
}

# ---- PESI: track-c-lead-gate-blocked (S1 PASS + pool/slot/umur lolos, gate GAGAL + audit RISK) ----
snap.setdefault("track_c", {})["PESI"] = {
    "sale": "0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD",
    "token": "0x9AEFce1FC6aEb5A5E4051f5fA9fd9D54C4dA6EF5",
    "name": "PESI", "symbol": "PESI", "kind": "ERC20-sale-S1",
    "status": "track-c-lead-gate-blocked-2026-11-10",
    "saleShape": "S1 PASS: mintPaid + priceOf(uint256) + free views (freeCap/freeClaimed/freeRemaining/freeShares) + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify exact_match (sale + token), verifiedAt 2026-11-09T19:00:56Z/58Z. Sumber PesiLaunch.sol dibaca penuh: claimFree(agentTokenId) 1 per Agent ID, escrow paid, LP otomatis di 2000 paid shares, refund penuh bila deadline lewat tanpa LP; owner HANYA pause/unpause + renounce.",
    "freePoolNote": "Free pool 955/1000 tersisa (freeShares 45, blok 132751601 ~16:25 WIB); FREE_PER_ID 1 per Agent ID; slot user TERBUKA (freeClaimed[labelhash 'masgayut']=false; registry ownerOf(labelhash)=wallet agent 0xeb23...). priceOf(1)=sharePrice=0,001 BNB (paid). paidShares 0/5000, pair 0x0, lpCreated false.",
    "launchNote": "Umur ~14 jam: post thecolony.uk 'PESI is live on BNB Chain' terbit 2026-11-09T19:16:24Z (02:16 WIB 10 Nov); tidak ada jam launch eksplisit di post. First-mint on-chain TIDAK terkoroborasi (Ankr getLogs 401); freeShares=45>0 membuktikan minting sudah berjalan. Deadline kontrak 1796841843 (~30 hari).",
    "gate": "GAGAL (run 1601, metode A-N): (A) pencarian alamat kontrak sale/token 0 hit (hanya hasil PESI tak terkait: saham Perma-Fix, proyek EU, token PEPSI); (B) Boltbook EN+ZH 0 mention; (C) metadata Sourcify tanpa URL (hanya import OpenZeppelin); (D) tidak ada pola situs same-family ditemukan; (E) owner sale 0x077984a60a39a24e8f5b04466d52a2bbbb227e9d TIDAK di discards, tanpa grup/link; (F) tidak ada handle X yang ditemukan di tempat lain untuk dikonfirmasi; (G) pencarian nama proyek hanya menemukan post thecolony.uk itu sendiri (tanpa link situs); (H) contractURI() tidak ada di ABI; (I) tokenURI n/a (bukan NFT); (J) tidak ada fungsi website/siteURL di ABI; (K) GitHub code search butuh auth (limitasi dicatat, tidak dicoba); (L) BscScan token-info via live browser (16:23-16:27 WIB, lolos Cloudflare): Overview TANPA tautan Website/Social, tab Info hanya 'Click here to update the token information', tanpa URL proyek (iklan bc.game bukan tautan proyek); (M) site: filters + pencarian deployer tanpa hit; (N) hop author-bio: penulis post 'Meow Cards' di thecolony.uk, post tidak menautkan situs proyek. Post thecolony.uk sendiri BUKAN website proyek (platform publikasi bersama; preseden WNO: gate lolos via situs sendiri warneedover.netlify.app, bukan via post thecolony). Gate TIDAK LOLOS -> TIDAK di-preview/TIDAK di-mint. Blokir kedua: audit token 1 RISK hit ('Contract Not Renounced').",
    "audit": "Binance audit: SALE hasResult=false (tidak ada hasil, bukan lolos); TOKEN hasResult=true, riskLevel 2 LOW, riskAlert null, 1 RISK hit ('Contract Not Renounced' isHit=true) + 2 CAUTION ('Mintable Detected', 'Newly Created Token'); buyTax/sellTax 0. RISK hit = STOP per aturan (blokir mint walau gate lolos).",
    "baselineNote": ("BARU run 1601 (sapuan web/sosial; post thecolony.uk oleh Meow Cards, koloni Build In Public). "
        "Verifikasi run-2026-11-10-1601-verify-pesi.json/log + audit /tmp/audit-pesi-e82BAc.json + /tmp/audit-pesi-9AEFce.json. "
        "Owner sale 0x077984a60a39a24e8f5b04466d52a2bbbb227e9d TIDAK di same-owner-discards. "
        "Token: PESI, 18 desimal, totalSupply 450.000.000 (45 share x 10M), maxSupply 70.000.000.000; feeBps 2000 (20% dev fee dari paid shares saja, sesuai post)."),
    "lastReadBlock": 132751601, "lastReadWib": "2026-11-10 16:25 WIB",
}

# ---- track_c lastRead updates ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    if name in rr.get("track_c", {}):
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = NOW
tc = snap.get("track_c", {})
if isinstance(tc.get("NUSA"), dict):
    tc["NUSA"]["runNote1601_1110"] = ("Run 1601: freeMinted 370 (tetap), freeClaimed(user)=0, gate FAILED (website tidak terverifikasi); "
        "deadline umur 48 jam 2026-11-10 17:05 WIB (~25 menit lagi dari run ini). TIDAK preview/mint, TIDAK dilaporkan ulang.")
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote1601_1110"] = "Run 1601: freeMinted 1000 (tetap), totalSupply 1e27, bal_user=0. Tetap watchlist-only-boltbook; umur UNVERIFIED. TIDAK ada perubahan."
if isinstance(tc.get("WNO"), dict):
    tc["WNO"]["runNote1601_1110"] = ("Run 1601: pasca-mint terverifikasi — balanceOf(user) 1.000.000 WNO (1e24) tetap; totalSupply 6e27; "
        "pair PCS V2 tetap 0x0 (belum ada) -> tetap di pending-swaps.json (no_pair).")

snap["last_run"] = 1
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
snap["last_run_note"] = ("Run 1601: re-read 659 kontrak + 76 track_c (blok 132749741; 659,3 dtk). "
    "Velocity LOLOS 1 (Sidecoo +82, 3,73x) — TANPA promosi (free% + slot + umur UNVERIFIED). "
    "SEVENFOLD velocity GAGAL, free 57,9%, audit-block dipertahankan. "
    "BARU track_c watchlist-only: Cheems Agent 0x00b4 (S1 PASS, pre-launch 17:00 WIB, gate belum ditemukan) + PESI (S1 PASS, pool 955/1000, slot terbuka, umur ~14 jam) GATE-BLOCKED + AUDIT-BLOCKED (token RISK 'Contract Not Renounced') -> dilaporkan sekali run ini, TIDAK preview/mint. "
    "Exit Gang 0xc014 (Boltbook, agent-shaped, free 288/333) DIBUANG same-owner (owner 0x67230d... grup Cz Agent/MAMESUKE/Whale Agent/Jager) — tidak dilaporkan, tidak masuk snapshot. "
    "Scan fast-fail Ankr 401 (preflight 6,3 dtk, head 132749752); watermark TIDAK dimajukan, gap ~237 ribu blok. "
    "Feed Sourcify 20/20 (hot-leg 1604): 1 S1 (0x00b4). Sweep web/sosial: 0 proyek baru. "
    "binanceai.fun tetap refund/failed (sudah dilaporkan sekali). Bridge: 116 kontrak, tidak berubah sejak 2026-11-08.")
snap["runNote1601_1110"] = snap["last_run_note"]

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE 1601 DONE: contracts updated={updated}, block={BLOCK}")
print("track_c count now:", len(snap.get("track_c", {})))
print("contracts count now:", len(snap.get("contracts", {})))
