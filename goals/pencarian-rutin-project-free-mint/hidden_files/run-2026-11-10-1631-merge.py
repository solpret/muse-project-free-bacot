#!/usr/bin/env python3
"""Merge run 1631 reread+vel+trackc-extra+binanceai into snapshot. FRESH for run 1631 only.
Main events run 1631 (blok 132753436, 16:31 WIB, interval 30 mnt vs run 1601 blok 132749741):
- Velocity LOLOS 3: bridge-0xe5ba3856 (+25, 6,89x), Hootfarm (+28, 10,26x),
  DRIFTWIRE (+71, 2,17x) -> SEMUA TANPA promosi:
  * bridge-0xe5ba3856: freeClaimed 1236/3333 = 37,1% < 50% -> bukan kandidat;
    umur/website UNVERIFIED -> bukan strong lead; tetap watchlist-only-scan-bridge.
  * Hootfarm: freeClaimed 441/999 = 44,1% < 50% -> bukan kandidat; status
    watchlist-only-same-owner-discarded -> TIDAK PERNAH dipromosikan/dilaporkan.
  * DRIFTWIRE: sudah minted-by-user (#745 run 1231) -> velocity tidak relevan.
- SEVENFOLD velocity GAGAL (+14, 1,03x); free 1752/3000 = 58,4% >=50% tapi
  audit-block dipertahankan (token MORROW riskLevel 4 HIGH + RISK, run 1431).
  Sidecoo velocity GAGAL (+11, 0,15x); free views tetap None. THYRK GAGAL (+38, 0,79x),
  sudah minted-by-user.
- Sellout scan: daftar 45 baris IDENTIK dengan run 1601 (comm diff kosong) ->
  TIDAK ADA sellout baru.
- Cheems Agent: MASIH PRE-LAUNCH (mintStart 1794304800 = 17:00 WIB, totalMinted 0,
  totalFreeMinted 0, currentState 0, tradingOpen false; freeClaimedByWallet(user)=0
  -> slot terbuka). Launch ~29 menit lagi. Tetap watchlist-only-upcoming.
- PESI: freeShares 45->46, freeRemaining 954 (1 share ter-klaim); gate GAGAL +
  audit RISK TIDAK BERUBAH -> TIDAK dilaporkan ulang (perubahan 1 share, bukan
  perubahan status material).
- NUSA: freeMinted 370->371, sharesMinted 378; gate FAILED; deadline umur 48 jam
  2026-11-10 17:05 WIB (~34 menit sesudah run ini) -> run berikut age-excluded
  bila belum sold out. TIDAK dilaporkan ulang.
- WNO: KOREKSI ALAMAT — brief run ini menyebut token WNO 0xc6D4ec8C...; itu SALAH,
  0xc6D4... adalah token LUCKY777 (terbukti: LUCKY777 sale token()==0xc6D4...,
  balanceOf(user)=5e25=50.000.000 LUCKY777). Token WNO yang benar = sale =
  0x8C969a4CD49E4774908e667702C3d7C3ece164D0 (single-contract, snapshot benar).
  Pair PCS V2 WNO/WBNB = 0x0 DAN WNO/USDT = 0x0 -> pending-swaps no_pair TIDAK BERUBAH.
  Pair 0x81afde... adalah LUCKY777/WBNB, cadangan 0/0, tidak berubah sejak run 1201.
- binanceai.fun: TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110,
  tokenClaimed(user) 0, balance 0). Sudah dilaporkan sekali; tidak dilaporkan ulang.
- Track_c lain: Crack +2, AGENT MALTA +1,8e25, FMA +2e21, VISION/0x5f76cAb7 +4,32e25
  totalSupply — tanpa perubahan status. CLEPSYDRA/MoonAgent: free views tetap None.
  Tidak ada balanceOf_user baru yang nonzero -> tidak ada mint user yang tak terlapor.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1631"
BLOCK = 132753436
NOW = "2026-11-10 16:31 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
extra = json.load(open(f"{BASE}/run-{TS}-trackc-extra.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1631-premerge")

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

def note(name, text):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["runNote1631_1110"] = text

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
    return (f"Run 1631 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra}")

# ---- key watchlist notes ----
note("bridge-0xe5ba3856", (dyn_note("bridge-0xe5ba3856") or "") +
     " Velocity LOLOS run ini (+25, 6,89x) TAPI TANPA promosi: freeClaimed 1236/3333 = 37,1% < 50% "
     "-> bukan kandidat; umur/website UNVERIFIED -> bukan strong lead; slot user UNVERIFIED "
     "(freeClaimed_user null). Tetap watchlist-only-scan-bridge. TIDAK preview/mint.")
note("Hootfarm", (dyn_note("Hootfarm") or "") +
     " Velocity LOLOS run ini (+28, 10,26x) TAPI TANPA promosi: freeClaimed 441/999 = 44,1% < 50% "
     "-> bukan kandidat; status same-owner-discarded -> TIDAK PERNAH dipromosikan/dilaporkan. Log saja.")
note("DRIFTWIRE", (dyn_note("DRIFTWIRE") or "") + " Sudah minted-by-user (#745 run 1231) -> velocity tidak relevan, TANPA promosi.")
note("Sidecoo", (dyn_note("Sidecoo") or "") +
     " Velocity GAGAL run ini (+11, 0,15x; run 1601 LOLOS +82, 3,73x). Free views tetap None "
     "(freeMinted/freeClaimed null, MAX_SUPPLY 2^256-1) -> free% UNVERIFIED; umur/website/X "
     "UNVERIFIED -> bukan strong lead, bukan kandidat, TIDAK preview/mint. Tetap watchlist-only.")
note("SEVENFOLD", (dyn_note("SEVENFOLD") or "") +
     " KANDIDAT tetap AUDIT-BLOCKED (dilaporkan 12:03 + 13:30; tidak dilaporkan ulang). "
     "free 1752/3000 = 58,4% >=50% tapi velocity GAGAL run ini (+14, 1,03x). "
     "Audit-block dari run 1431 dipertahankan (token MORROW riskLevel 4 HIGH + RISK); tidak di-audit ulang run ini. TIDAK preview/mint.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user (#6849 run 1231 + 20 THYRK pending swap) -> velocity GAGAL run ini, tanpa relevansi.")
note("ELSY AGENT", (dyn_note("ELSY AGENT") or "") + " Pasca-mint terverifikasi: bal_user=2 (#880/#881). TIDAK di-auto-list (own market tidak live).")
note("Sakura", (dyn_note("Sakura") or "") + " Tetap early lead; first mint terverifikasi 2026-11-10 01:47 WIB -> deadline 48 jam 2026-11-12 01:47 WIB.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; first mint terverifikasi 2026-11-09 ~02:00 WIB -> deadline 48 jam 2026-11-11 ~02:00 WIB.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") + " Minted-by-user; tanpa perubahan.")
note("Zapcourier", (dyn_note("Zapcourier") or "") + " Minted-by-user; free pool 712/712 habis; tanpa perubahan.")

# ---- track_c generic lastRead updates (specific notes below override) ----
for name, entry in snap.get("track_c", {}).items():
    if not isinstance(entry, dict):
        continue
    if name in rr.get("track_c", {}):
        entry["lastReadBlock"] = BLOCK
        entry["lastReadWib"] = NOW

# ---- Cheems Agent: still pre-launch ----
tc = snap.get("track_c", {})
if isinstance(tc.get("Cheems Agent"), dict):
    ch = extra["checks"]["Cheems Agent"]["views"]
    tc["Cheems Agent"]["runNote1631_1110"] = (
        f"Run 1631 (blok {BLOCK}): MASIH PRE-LAUNCH — mintStart {ch.get('mintStart')} (= 2026-11-10 17:00 WIB), "
        f"totalMinted {ch.get('totalMinted')}, totalFreeMinted {ch.get('totalFreeMinted')}, currentState {ch.get('currentState')}, "
        f"tradingOpen {ch.get('tradingOpen')}; freeClaimedByWallet(user)={ch.get('freeClaimedByWallet_user')} -> slot terbuka. "
        f"Launch ~29 menit lagi (17:00 WIB). TotalSupply token kini terbaca 1e30 (run 1601 None). "
        f"Tetap watchlist-only-upcoming; BUKAN lead; TIDAK preview/mint. Cek ulang pada/sesudah 17:00 WIB.")
    tc["Cheems Agent"]["lastReadBlock"] = BLOCK
    tc["Cheems Agent"]["lastReadWib"] = NOW
if isinstance(tc.get("PESI"), dict):
    pe = extra["checks"]["PESI"]["views"]
    tc["PESI"]["runNote1631_1110"] = (
        f"Run 1631 (blok {BLOCK}): freeShares {pe.get('freeShares')} (run 1601: 45), freeRemaining {pe.get('freeRemaining')} "
        f"(run 1601: 955), freeCap {pe.get('freeCap')}, paidShares {pe.get('paidShares')}, lpCreated {pe.get('lpCreated')}. "
        f"1 share gratis ter-klaim sejak run 1601 — perubahan 1 share, BUKAN perubahan status material. "
        f"Gate GAGAL + audit token RISK ('Contract Not Renounced') TIDAK BERUBAH -> TIDAK dilaporkan ulang, TIDAK preview/mint.")
    tc["PESI"]["lastReadBlock"] = BLOCK
    tc["PESI"]["lastReadWib"] = NOW
if isinstance(tc.get("NUSA"), dict):
    nu = extra["checks"]["NUSA"]["views"]
    tc["NUSA"]["runNote1631_1110"] = (
        f"Run 1631 (blok {BLOCK}): freeMinted {nu.get('freeMinted')} (run 1601: 370), sharesMinted {nu.get('sharesMinted')}, "
        f"soldOut {nu.get('soldOut')}, closed {nu.get('closed')}. Gate FAILED TIDAK BERUBAH. "
        f"Deadline umur 48 jam 2026-11-10 17:05 WIB (~34 menit sesudah run ini) -> run berikut age-excluded bila belum sold out. "
        f"TIDAK preview/mint, TIDAK dilaporkan ulang.")
    tc["NUSA"]["lastReadBlock"] = BLOCK
    tc["NUSA"]["lastReadWib"] = NOW
if isinstance(tc.get("WNO"), dict):
    tc["WNO"]["runNote1631_1110"] = (
        f"Run 1631 (blok {BLOCK}): KOREKSI ALAMAT — brief run ini menyebut token WNO 0xc6D4ec8C...; itu token LUCKY777 "
        f"(terbukti: LUCKY777 sale token()==0xc6D4..., balanceOf(user)=5e25=50.000.000 LUCKY777). Token WNO yang benar = sale = "
        f"0x8C969a4CD49E4774908e667702C3d7C3ece164D0. Pair PCS V2 WNO/WBNB = 0x0 DAN WNO/USDT = 0x0 "
        f"-> pending-swaps no_pair TIDAK BERUBAH. Pair 0x81afde... adalah LUCKY777/WBNB, cadangan 0/0, tidak berubah sejak run 1201. "
        f"Balance WNO user tetap 1.000.000 (1e24).")
    tc["WNO"]["lastReadBlock"] = BLOCK
    tc["WNO"]["lastReadWib"] = NOW
if isinstance(tc.get("FOUNT"), dict):
    tc["FOUNT"]["runNote1631_1110"] = "Run 1631: freeMinted 1000 (tetap), totalSupply 1e27, bal_user=0. Tetap watchlist-only-boltbook; umur UNVERIFIED. TIDAK ada perubahan."
if isinstance(tc.get("CLEPSYDRA"), dict):
    tc["CLEPSYDRA"]["runNote1631_1110"] = "Run 1631: free views tetap None (freeMinted/freeSharesRemaining null), totalSupply 1e27, bal_user=0. Gate-blocked, TIDAK ada perubahan."
if isinstance(tc.get("MoonAgent-MOAGT"), dict):
    tc["MoonAgent-MOAGT"]["runNote1631_1110"] = "Run 1631: free views tetap None, totalSupply 1e27, bal_user=0. Lead-gate-blocked, TIDAK ada perubahan."

snap["last_run"] = 1
snap["last_run_wib"] = NOW
snap["last_run_block"] = BLOCK
snap["last_run_note"] = ("Run 1631: re-read 659 kontrak + 78 track_c (blok 132753436; 740,6 dtk). "
    "Velocity LOLOS 3 (bridge-0xe5ba3856 +25, 6,89x; Hootfarm +28, 10,26x; DRIFTWIRE +71, 2,17x) — SEMUA TANPA promosi "
    "(bridge free 37,1% <50% + umur/website unverified; Hootfarm free 44,1% <50% + same-owner-discarded; DRIFTWIRE minted-by-user). "
    "SEVENFOLD velocity GAGAL, free 58,4%, audit-block dipertahankan. Sidecoo velocity GAGAL (+11, 0,15x). "
    "Sellout scan IDENTIK dengan run 1601 (45 baris) -> TIDAK ADA sellout baru. "
    "Cheems Agent MASIH PRE-LAUNCH (mintStart 17:00 WIB, totalMinted 0) -> watchlist-only-upcoming. "
    "PESI freeShares 45->46 (gate-blocked + audit RISK, tidak dilaporkan ulang). "
    "NUSA freeMinted 370->371; deadline umur 48 jam 17:05 WIB hari ini. "
    "WNO: pair PCS V2 tetap 0x0 (WBNB+USDT) -> pending-swaps no_pair tidak berubah; KOREKSI: token 0xc6D4... di brief adalah LUCKY777, bukan WNO. "
    "binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110). "
    "TIDAK ADA lead/kandidat baru.")
snap["runNote1631_1110"] = snap["last_run_note"]

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE 1631 DONE: contracts updated={updated}, block={BLOCK}")
print("track_c count now:", len(snap.get("track_c", {})))
print("contracts count now:", len(snap.get("contracts", {})))
