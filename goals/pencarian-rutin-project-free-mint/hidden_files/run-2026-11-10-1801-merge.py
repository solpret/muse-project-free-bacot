#!/usr/bin/env python3
"""Merge run 1801 reread+vel into snapshot. FRESH for run 1801 only.
Run 1801 (jadwal 18:01 WIB, dieksekusi 18:02-~18:55 WIB). Block re-read: 132765203.
Reread 665 kontrak + 81 track_c (598,7 dtk).
- Velocity LOLOS 7, TANPA promosi: BEWORK +470 (bukan agent-shaped, free%/umur/X unverified);
  THYRK +185 (minted-by-user); Glitchpilotfox +129 (age-excluded); Wuyuhive +122
  (temuan pelengkap scan, umur UNVERIFIED — pencarian web tanpa bukti launch);
  Lion's Share +55 (age-excluded); bridge-0x6eee + Zhenzhu (unit token fungible, bukan NFT).
- EARLY LEAD BARU 3 (dilaporkan sekali): NIGHTFORGE (SMITH, 601/9.999, mintStart
  2026-11-10 14:37 WIB terverifikasi), EMBERANVIL (SMITH, 842/9.999, mintStart
  2026-11-10 14:59 WIB terverifikasi), Cosmic Sentinel (CSNT, 276 total, 271 freeMinted,
  quote(user,1)=0, website TERVERIFIKASI cosmic-sentinel.pages.dev/mint, umur UNVERIFIED).
  Ketiganya: registry bytes True (agent-shaped), first mints terverifikasi on-chain,
  TIDAK pernah di-preview/di-mint (early lead). Website NIGHTFORGE/EMBERANVIL TIDAK
  terverifikasi (contractURI -> halaman infografik tak terkait; site root tidak mencetak
  kontrak; pencarian kontrak/nama tanpa hasil) — dicatat, bukan penghalang laporan early.
- KOREKSI PENTING — gelombang costOf owner 0x11038f4a... (11 entri discard, 2026-11-06/08):
  ACORE + 5 InsertCoin (POTION SHOP, insert.coin, Tiny Worlds, Mixtape & Co., DICE.EXE)
  + ONI-new SEMUA owner 0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd = owner group yang
  SUDAH di-discard. Run 1731 salah menilai POTION/ONI "paid-only" (hanya baca price()):
  costOf(user,1)=0 membuktikan mint pertama GRATIS — TAPI status discard TIDAK berubah:
  TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, TIDAK dieksekusi (log saja).
  ACORE (70% minted, slot terbuka) TETAP promotion-discarded-same-owner-2026-11-09.
- Scan leg FAST-FAIL (preflight Ankr 401, 5,5 dtk; outage berlanjut sejak 2026-11-09
  ~13:33 WIB; watermark tetap 132512564). Sourcify v2 contract endpoint DEGRADASI run ini
  (hanya metadata 209B, tanpa ABI — berlaku untuk semua kontrak incl. POTION yang
  17:47 WIB masih mengembalikan ABI penuh); shape-check feed dialihkan ke probing
  selector on-chain (feedprobe): 19 kontrak baru, 0 sale-shape (token polos / kosong).
- Boltbook: ACORE hype (4 post) = discarded; NIGHTFORGE/EMBERANVIL early; InsertCoin wave
  = discarded; SAKURA free 20,7% (<25%, tetap early); Lambdwyn 31,1% (umur >>48h);
  Riddle Run 10,4%; $GWEH/$SGARDEN/$UNSOLVED/$TLDR = meme coin launchpad Boltbook
  (7 hari lalu, bukan share sale, bukan lead); Horus AI Phase 1 sold out; Agentic
  Gangster excluded; AgentGoldMiner (25 Okt) age-excluded; Cosmic Sentinel early.
- binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110).
- Bridge scan-bridge.json TIDAK berubah (mtime 2026-11-08 18:21 UTC): 0 temuan baru.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1801"
BLOCK = 132765203
NOW = "2026-11-10 18:01 WIB"
INTERVAL = 30.0
NOW_DT = datetime.datetime(2026, 11, 10, 18, 55, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
WIN_START = datetime.datetime(2026, 11, 10, 17, 31, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1801-premerge")

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
        e["runNote1801_1110"] = text

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
    return (f"Run 1801 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("BEWORK", (dyn_note("BEWORK") or "") +
     " Velocity LOLOS run ini (+470, 2,04x) TAPI TANPA promosi: bukan agent-shaped "
     "(shape-unverified sejak 2026-11-05: tanpa registry bytes, Sourcify 404, fungsi mint tak teridentifikasi), "
     "free% UNVERIFIED, umur UNVERIFIED, X unverified. Bukan early lead, bukan kandidat, TIDAK preview/mint.")
note("Wuyuhive", (dyn_note("Wuyuhive") or "") +
     " Velocity LOLOS run ini (+122, 20,33x) TAPI TANPA promosi: temuan pelengkap scan "
     "(bridge), umur peluncuran UNVERIFIED — pencarian web run ini tanpa bukti launch time — "
     "free ~55% + slot terbuka tidak cukup tanpa umur terverifikasi. Tetap watchlist-only. "
     "Dilaporkan hanya bila promosi tier, berlabel 'temuan pelengkap scan'.")
note("Glitchpilotfox", (dyn_note("Glitchpilotfox") or "") +
     " Velocity LOLOS run ini (+129, 16,1x) TAPI TANPA promosi: age-excluded-2026-11-09 "
     "(first mint terverifikasi 2026-11-03 18:21 WIB).")
note("Lion's Share", (dyn_note("Lion's Share") or "") +
     " Velocity LOLOS run ini (+55, 3,23x) TAPI TANPA promosi: age-excluded-2026-11-08 "
     "(first mint terverifikasi 2026-11-05 22:28 WIB).")
note("THYRK", (dyn_note("THYRK") or "") +
     " Velocity LOLOS run ini (+185, 2,94x) TAPI TANPA promosi: sudah minted-by-user (#6849).")
note("Claf Eye", (dyn_note("Claf Eye") or "") + " Velocity GAGAL (0,23x). Tetap early lead, tanpa promosi.")
note("BAGENT", (dyn_note("BAGENT") or "") + " Velocity GAGAL (0,93x).")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") + " Velocity GAGAL (0,43x). Sudah minted-by-user (#581).")
note("POTION SHOP", (dyn_note("POTION SHOP") or "") +
     " KOREKSI run 1801 vs run 1731: BUKAN paid-only — costOf(user,1)=0 (mint pertama GRATIS, "
     "template costOf). NAMUN owner 0x11038f4a... = owner group costOf/mintsLeft yang SUDAH di-discard "
     "(11 entri same-owner-discards.json, 2026-11-06/08) -> status promotion-discarded-same-owner-2026-11-10. "
     "TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, TIDAK dieksekusi.")
note("Sakura", (dyn_note("Sakura") or "") +
     " Triage run ini: freeMinted 1.378/6.666 = 20,7% (<25% strong leg), totalSupply 1.388, "
     "Sourcify 404 (unverified, sesuai post Nico). Tetap early lead, tanpa promosi.")
note("AGENT CORE", (dyn_note("AGENT CORE") or "") +
     " Ditemukan lagi run ini via hype Boltbook (4 post: ACORE 1.407/2.000, freeLeft 598, costOf(user,1)=0, "
     "slot terbuka) — TETAP promotion-discarded-same-owner-2026-11-09: owner 0x11038f4a... = owner group "
     "costOf/mintsLeft yang sudah di-discard. TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, "
     "TIDAK dieksekusi. Dicatat di run log saja.")
note("Forge Pass", (dyn_note("Forge Pass") or "") +
     " Catatan degennft.ai 18:05 WIB: freeMinted() kini REVERT (getter makin gelap: kemarin PRICE/freeLeft/mintOpen "
     "revert, kini freeMinted ikut). Reread run ini: freeMinted None (revert) — nilai lama dipertahankan.")
note("Golden Agents", (dyn_note("Golden Agents") or "") + " Tetap early lead; tanpa promosi.")

# ---- generic NEW-sellout detection ----
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
            entry["runNote1801_1110"] = (f"Run 1801 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS:", new_sellouts if new_sellouts else "none")

# ---- age-exclusion scan: deadlines falling inside run 1731 -> 1801 window ----
def parse_wib(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S WIB", "%Y-%m-%dT%H:%M:%S+07:00", "%Y-%m-%d %H:%M WIB"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
        except Exception:
            continue
    return None
new_age_excl = []
for name, entry in snap.get("contracts", {}).items():
    if not isinstance(entry, dict):
        continue
    st = str(entry.get("status", ""))
    if any(t in st for t in TERMINAL):
        continue
    launch = None
    for k in ("firstMintWib", "startTimeWib", "launchWib"):
        launch = parse_wib(entry.get(k))
        if launch:
            break
    if not launch:
        continue
    deadline = launch + datetime.timedelta(hours=48)
    if WIN_START < deadline <= NOW_DT:
        sold = False
        f = rr.get("reread", {}).get(name, {})
        cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP")
        fm = f.get("freeMinted"); fc = f.get("freeClaimed")
        if cap and ((fm is not None and fm >= cap) or (fc is not None and fc >= cap)):
            sold = True
        entry["status"] = "age-excluded-2026-11-10"
        entry["runNote1801_1110"] = (f"Run 1801 (blok {BLOCK}): AGE-EXCLUDED - launch terverifikasi {launch}, "
            f"deadline 48 jam {deadline} lewat; soldOut={sold}. Status -> age-excluded-2026-11-10. Dilaporkan sekali oleh parent.")
        new_age_excl.append((name, str(launch), str(deadline), sold))
print("NEW AGE EXCLUSIONS:", new_age_excl if new_age_excl else "none")

# ---- track_c generic lastRead updates + free values ----
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

# ---- new early leads run 1801 ----
snap["contracts"]["NIGHTFORGE"] = {
    "address": "0x22f43ba09fd4beb9417d4484c60370354b220186",
    "name": "NIGHTFORGE", "symbol": "SMITH", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 601, "MAX_SUPPLY": 9999, "mintOpen": 1,
    "mintStart": 1794296194, "mintStartWib": "2026-11-10 14:37 WIB",
    "balanceOf_user": 0,
    "firstSeenBlock": 132763884, "firstSeenWib": "2026-11-10 ~17:54 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True,
    "contractURI": "https://nightforge.pages.dev/meta/collection.json",
    "gate": "website_unverified",
    "launchNote": "mintStart() on-chain = 1794296194 = 2026-11-10 14:37 WIB -> umur ~3,5 jam, TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1801 (Boltbook cskh.ai 17:54 WIB: 595/9.999). "
        "Agent-shaped: registry bytes 0x60B926...022F di bytecode + mint(1) value 0 lolos static eth_call "
        "(verifikasi cskh.ai + sim ulang run ini). First mints terverifikasi on-chain (601 saat triase). "
        "Free% 601/9.999 = 6,0% (<25% strong leg). Website TIDAK terverifikasi: contractURI menunjuk halaman "
        "infografik tak terkait (tanpa NIGHTFORGE/SMITH/kontrak), site root nightforge.pages.dev tidak mencetak "
        "kontrak, pencarian kontrak/nama tanpa hasil (metode A/G/H/I dicoba). X discussion: post Boltbook cskh.ai. "
        "Tidak pernah di-preview/di-mint (early lead). Promosi ke strong lead bila 3 kaki terpenuhi + gate website lolos."}
snap["contracts"]["EMBERANVIL"] = {
    "address": "0x7673c596a6702d32f844266dc2ca7b1fd6d7df21",
    "name": "EMBERANVIL", "symbol": "SMITH", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 842, "MAX_SUPPLY": 9999, "mintOpen": 1,
    "mintStart": 1794297602, "mintStartWib": "2026-11-10 14:59 WIB",
    "balanceOf_user": 0,
    "firstSeenBlock": 132752838, "firstSeenWib": "2026-11-10 ~17:xx WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True,
    "contractURI": "https://emberanvil.pages.dev/meta/collection.json",
    "gate": "website_unverified",
    "launchNote": "mintStart() on-chain = 1794297602 = 2026-11-10 14:59 WIB -> umur ~3 jam, TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1801 (dieksekusi gratis #618 oleh nicodart.ai, tx 0xbf7bea6e...; "
        "template bytecode IDENTIK dengan NIGHTFORGE, 17.776 byte). Agent-shaped: registry bytes 0x60B926...022F "
        "di bytecode + mint(1) value 0 lolos static eth_call (sim ulang run ini). First mints terverifikasi on-chain "
        "(842 saat triase). Free% 842/9.999 = 8,4% (<25% strong leg). Website TIDAK terverifikasi: contractURI "
        "menunjuk pola sama seperti NIGHTFORGE, site root emberanvil.pages.dev tidak mencetak kontrak, pencarian "
        "kontrak/nama tanpa hasil (metode A/G/H/I dicoba). Tidak pernah di-preview/di-mint (early lead)."}
snap["contracts"]["Cosmic Sentinel"] = {
    "address": "0x88731d1eb41c36f3d705fdb58b658244c06afc36",
    "name": "Cosmic Sentinel", "symbol": "CSNT", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 276, "freeMinted": 271, "MAX_SUPPLY": 225000, "mintOpen": 1,
    "quote_user_1": 0, "balanceOf_user": 0, "freeClaimed_user": 0,
    "owner": "0x38d2bbdf9b1c15f5fdbf6f7c10023edf17a59bd4",
    "firstSeenWib": "2026-11-10 ~18:30 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True,
    "website": "https://cosmic-sentinel.pages.dev/mint",
    "gate": "website_verified",
    "launchNote": "Umur peluncuran UNVERIFIED (mintStart/START_TIME revert; tidak ada tanggal launch di situs).",
    "baselineNote": "EARLY lead dilaporkan sekali run 1801 (temuan sweep web rute 3/5b). Agent-shaped: registry bytes "
        "0x60B926...022F di bytecode. First mints terverifikasi on-chain (totalSupply 276, freeMinted 271). "
        "Slot user TERBUKA: quote(user,1)=0, balanceOf(user)=0, freeClaimed(user)=0. Website TERVERIFIKASI: "
        "cosmic-sentinel.pages.dev/mint mencetak kontrak persis + syarat free-mint Agent ID. Sourcify UNVERIFIED "
        "(404). Owner 0x38d2bbdf... TIDAK ada di same-owner-discards.json. Free% 271/225.000 = 0,12% "
        "(<25% strong leg). Umur UNVERIFIED -> bukan strong lead/kandidat sampai launch terverifikasi <=48 jam. "
        "Tidak pernah di-preview/di-mint (early lead)."}

# ---- InsertCoin wave: discarded owner (log-only entries, never leads) ----
DISC_OWNER = "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd"
for nm, addr, ts, mx in [
    ("insert.coin", "0x0d03cb2149094910fc7a46f05529c561090ddaaf", 225, None),
    ("Tiny Worlds", "0x04c310b283030c056110abef004fc784a4cb6568", 229, None),
    ("Mixtape & Co.", "0xbb164c4e54cdcc6fa0a262e22f1452a67b44674b", 234, None),
    ("DICE.EXE", "0x9af8ebbc01556421bd4ff603f989fd109b9407d0", 110, None),
]:
    snap["contracts"][nm] = {
        "address": addr, "name": nm, "kind": "ERC721",
        "status": "promotion-discarded-same-owner-2026-11-10",
        "owner": DISC_OWNER,
        "totalSupply": ts, "costOf_user_1": 0,
        "balanceOf_user": 0,
        "firstSeenWib": "2026-11-10 ~18:00 WIB",
        "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "note": f"Gelombang InsertCoin (Boltbook nicodart.ai rekap 18:00 WIB): mint pertama gratis per wallet "
            f"(costOf(user,1)=0, template costOf), Sourcify exact_match. NAMUN owner {DISC_OWNER} = owner group "
            f"costOf/mintsLeft yang SUDAH di-discard (11 entri same-owner-discards.json, 2026-11-06/08). "
            f"TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, TIDAK dieksekusi — dicatat di run log saja."}
# POTION SHOP + ONI-new: correct run-1731 verdict, apply discard status
for nm in ("POTION SHOP", "ONI-new"):
    e = snap["contracts"].get(nm)
    if isinstance(e, dict):
        e["status"] = "promotion-discarded-same-owner-2026-11-10"
        e["owner"] = DISC_OWNER
        e["costOf_user_1"] = 0
        e["runNote1801_1110"] = (e.get("runNote1801_1110", "") +
            " KOREKSI: owner 0x11038f4a... = owner group costOf/mintsLeft yang sudah di-discard "
            "(same-owner-discards.json) -> status promotion-discarded-same-owner-2026-11-10. "
            "Mint pertama gratis (costOf 0) TETAP TIDAK mengubah discard: tidak dilaporkan sebagai lead, "
            "tidak dipromosikan, tidak dieksekusi.")

# ---- binanceai.fun: unchanged ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 1801"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~18:4x WIB"
    snap["binanceai_claim"]["block"] = BLOCK
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-read run 1801: launched 0, failed 1, isRefundPhase 1, "
        "totalShares 3110, tokenClaimed user 0, saldo TOKEN user 0 - TIDAK BERUBAH vs run 1731. Status tetap closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run note ----
snap["runNote1801_1110"] = (
    "Run 1801 (2026-11-10 18:01-~18:55 WIB, blok re-read 132765203): re-read 665 kontrak + 81 track_c (598,7 dtk). "
    "Velocity LOLOS 7, TANPA promosi (BEWORK +470 bukan agent-shaped; THYRK +185 minted-by-user; Glitchpilotfox +129 "
    "age-excluded; Wuyuhive +122 umur unverified; Lion's Share +55 age-excluded; bridge-0x6eee + Zhenzhu unit token). "
    "EARLY LEAD BARU 3 (dilaporkan sekali): NIGHTFORGE (601/9.999, mintStart 14:37 WIB), EMBERANVIL (842/9.999, "
    "mintStart 14:59 WIB), Cosmic Sentinel (276 total/271 free, quote 0, website terverifikasi, umur unverified). "
    "KOREKSI DISCARDED: ACORE + gelombang InsertCoin (POTION SHOP, insert.coin, Tiny Worlds, Mixtape & Co., DICE.EXE) "
    "+ ONI-new = owner 0x11038f4a... yang SUDAH di-discard — costOf(user,1)=0 membuktikan mint pertama gratis, tapi "
    "discard TIDAK berubah: tidak dilaporkan sebagai lead, tidak dipromosikan, tidak dieksekusi. "
    "Scan leg FAST-FAIL (preflight Ankr 401, 5,5 dtk; watermark tetap 132512564). Sourcify v2 ABI endpoint degradasi "
    "(metadata 209B tanpa ABI); feed shape-check dialihkan ke probing selector on-chain: 19 kontrak baru, 0 sale-shape. "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah. 0 kandidat baru, 0 strong lead baru, "
    "0 track-C lead/kandidat baru, 0 track-B claim.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote1801_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
