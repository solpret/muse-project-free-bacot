#!/usr/bin/env python3
"""Merge run 1831 reread+vel+discovery into snapshot. FRESH for run 1831 only.
Run 1831 (jadwal 18:31 WIB, dieksekusi ~18:31-19:0x WIB). Block re-read: 132769068.
Reread 672 kontrak + 81 track_c (659 dtk, bsc-dataseed; Ankr tidak dipakai).
- Velocity LOLOS 4, TANPA promosi: ACOS-3aed +73 (36,32x; age/pct/website unverified);
  Zhenzhu (unit-token artefak, bukan NFT); Claf Eye +220 (2,42x; early lead, free% + umur
  UNVERIFIED); Fossil Drawer +79 (minted-by-user).
- EARLY LEAD BARU 2 (dilaporkan sekali): HackouCoinPass HCPASS 0xA96f20BC (free 259/1111
  = 23,3%, saleStart 18:31 WIB terverifikasi, slot user TERBUKA, website TERVERIFIKASI
  hackou.com/coin-pass) + NIGHTFORGE B 0x051f04ff (SMITH, totalSupply 303, mintStart
  14:51 WIB terverifikasi, registry bytes di bytecode; free%/slot/website UNVERIFIED).
  Keduanya TIDAK pernah di-preview/di-mint (early lead).
- TRACK-C WATCHLIST-ONLY baru 2 (dicatat, BUKAN lead, TIDAK dilaporkan sebagai lead):
  YAMA PROJECT 0x86D779fc (S1 pass, quote 0, slot terbuka; umur + website UNVERIFIED)
  + LOWB 0x00487ED0 (opened=false, belum dibuka; MINT_DEADLINE 14 Nov 19:00 WIB).
- AGE-EXCLUSION (catch-up, bukti bersih): 7 kontrak early/strong lead 2026-11-08 dengan
  first mint terverifikasi + free pool terverifikasi TERBUKA + mintOpen 1, umur 51,6-59,8
  jam > 48 jam: Jinli Agents, 0xa8543350, 0x1fab92b9, Cassetto, Retrocam, Hourglas,
  CAISHEN. Dihapus dari contracts, dicatat di age_exclusions, dilaporkan sekali.
- Scan leg FAST-FAIL (preflight Ankr 401; outage berlanjut sejak 2026-11-09 ~13:33 WIB;
  watermark tetap 132512564; gap ~259.130 blok).
- CHEEMSA sold-out 1000/1000 TERVERIFIKASI run ini (totalFreeMinted, blok 132772378);
  sudah dilaporkan sekali hot-leg 1804 - TIDAK dilaporkan ulang.
- binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110; blok 132772378).
- Agentic Gangster Genesis: free pool HABIS 111/111 (sudah excluded run 1431) - log saja.
- Bridge scan-bridge.json TIDAK berubah (mtime 2026-11-08 18:21).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1831"
BLOCK = 132769068
NOW = "2026-11-10 18:31 WIB"
INTERVAL = 30.0
NOW_DT = datetime.datetime(2026, 11, 10, 18, 31, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
WIN_START = datetime.datetime(2026, 11, 10, 18, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1831-premerge")

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
        e["runNote1831_1110"] = text

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
    return (f"Run 1831 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("ACOS-3aed", (dyn_note("ACOS-3aed") or "") +
     " Velocity LOLOS run ini (+73, 36,32x) TAPI TANPA promosi: status "
     "watchlist-only-age-pct-website-unverified-2026-11-04 — umur, free% dan website "
     "semuanya UNVERIFIED. Bukan early lead, bukan kandidat, TIDAK preview/mint.")
note("Zhenzhu", (dyn_note("Zhenzhu") or "") +
     " Velocity LOLOS run ini TAPI artefak unit-token fungible (bukan hitungan NFT), "
     "seperti run 1801. Bukan promosi.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Velocity LOLOS run ini (+220, 2,42x) TAPI TANPA promosi: early lead, free% "
     "UNVERIFIED (freeClaimed/freeMinted None) + umur UNVERIFIED. Tetap early lead.")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") +
     " Velocity LOLOS run ini (+79, 2,39x) TAPI TANPA promosi: sudah minted-by-user.")
note("NIGHTFORGE", (dyn_note("NIGHTFORGE") or "") +
     " Early lead run 1801: 601->609 (+8). Free% 609/9.999 = 6,1% (<25%). Tetap early lead.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") +
     " Early lead run 1801: 842->864 (+22). Free% 864/9.999 = 8,6% (<25%). Tetap early lead.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead run 1801: 276->280 (+4), freeClaimed_user=0 (slot terbuka). "
     "Umur tetap UNVERIFIED -> bukan strong lead.")
note("Sakura", (dyn_note("Sakura") or "") + " Early lead; tanpa promosi.")
note("Cinder Agents", (dyn_note("Cinder Agents") or "") + " Early lead; 239 flat; tanpa promosi.")
note("THYRK", (dyn_note("THYRK") or "") + " Sudah minted-by-user; tanpa promosi.")

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
            entry["runNote1831_1110"] = (f"Run 1831 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS:", new_sellouts if new_sellouts else "none")

# ---- age-exclusion scan: windowed (deadline in run window) + catch-up list ----
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

def pool_open(entry, f):
    cap = entry.get("FREE_SUPPLY") or entry.get("FREE_CAP")
    fm = f.get("freeMinted"); fc = f.get("freeClaimed")
    if cap and cap < 10**12:
        if fm is not None:
            return fm < cap, (fm, cap, "freeMinted")
        if fc is not None:
            return fc < cap, (fc, cap, "freeClaimed")
    return None, (None, cap, None)

new_age_excl = []
removed_names = []
for name, entry in list(snap.get("contracts", {}).items()):
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
        f = rr.get("reread", {}).get(name, {})
        opened, det = pool_open(entry, f)
        if opened is False:
            continue
        age_h = (NOW_DT - launch).total_seconds() / 3600
        rec = {"name": name, "address": entry.get("address"),
               "firstMintWib": str(launch), "ageHours": round(age_h, 1),
               "free": f"{det[0]}/{det[1]} = {det[0]/det[1]*100:.1f}%" if det[0] is not None and det[1] else "pool state per reread",
               "status_before": st, "removed_run": "2026-11-10 run 1831",
               "removed_wib": "2026-11-10 18:31 WIB",
               "reason": f"Umur peluncuran terverifikasi {age_h:.1f} jam (>48 jam) dan belum sold out "
                         f"(free {det[0]}/{det[1]}); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."}
        snap.setdefault("age_exclusions", []).append(rec)
        del snap["contracts"][name]
        removed_names.append(name)
        new_age_excl.append((name, str(launch), str(deadline), det))
print("WINDOWED AGE EXCLUSIONS:", new_age_excl if new_age_excl else "none")

# catch-up: verified launch >48h + verified open pool + mintOpen 1 (missed by earlier windowed checks)
CATCHUP = [
    ("Jinli Agents", "2026-11-08 06:44:59 WIB", 59.8, 359, 888, "freeClaimed"),
    ("0xa8543350e5accacc780c9613bfa2fb9b52d3858e", "2026-11-08 08:12:40 WIB", 58.3, 2966, 7000, "freeClaimed"),
    ("0x1fab92b937572c79550aeee51cee77d3add20367", "2026-11-08 08:12:39 WIB", 58.3, 2437, 4000, "freeClaimed"),
    ("Cassetto", "2026-11-08 14:56:03 WIB", 51.6, 2735, 7000, "freeClaimed"),
    ("Retrocam", "2026-11-08 14:56:27 WIB", 51.6, 2740, 7000, "freeClaimed"),
    ("Hourglas", "2026-11-08 14:56:12 WIB", 51.6, 3051, 7000, "freeClaimed"),
    ("CAISHEN", "2026-11-08 14:55:43 WIB", 51.6, 281, 888, "freeClaimed"),
]
catchup_removed = []
for name, first_wib, age_h, free_n, cap, key in CATCHUP:
    e = snap["contracts"].get(name)
    if not isinstance(e, dict):
        print(f"CATCHUP SKIP {name}: not in contracts"); continue
    f = rr.get("reread", {}).get(name, {})
    fresh = f.get(key)
    if fresh is None or fresh >= cap:
        print(f"CATCHUP SKIP {name}: fresh {key}={fresh} vs cap {cap} (not verifiably open)"); continue
    if f.get("mintOpen") is not None and f.get("mintOpen") != 1:
        print(f"CATCHUP SKIP {name}: mintOpen={f.get('mintOpen')}"); continue
    rec = {"name": name, "address": e.get("address"), "firstMintWib": first_wib,
           "ageHours": age_h, "free": f"{fresh}/{cap} = {fresh/cap*100:.1f}%",
           "status_before": str(e.get("status", "")), "removed_run": "2026-11-10 run 1831 (catch-up)",
           "removed_wib": "2026-11-10 18:31 WIB",
           "reason": f"Umur peluncuran terverifikasi {age_h} jam (>48 jam) dan belum sold out "
                     f"(free {fresh}/{cap}, mintOpen 1); deadline 48 jam lewat sebelum run-run sebelumnya "
                     f"(windowed check tidak menangkapnya); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."}
    snap.setdefault("age_exclusions", []).append(rec)
    del snap["contracts"][name]
    removed_names.append(name)
    catchup_removed.append(name)
print("CATCHUP AGE EXCLUSIONS:", catchup_removed if catchup_removed else "none")

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

# ---- CHEEMSA: sold-out verified this run (already reported hot-leg 1804) ----
ch = snap.get("track_c", {}).get("Cheems Agent")
if isinstance(ch, dict):
    ch["runNote1831_1110"] = ("Run 1831: totalFreeMinted 1000/1000 TERVERIFIKASI (direct eth_call, blok 132772378) "
        "- free pool SOLD OUT; freeClaimedByWallet(user)=1 (slot user terpakai via mint run 1731). "
        "Sudah dilaporkan sekali hot-leg 1804 - TIDAK dilaporkan ulang.")

# ---- new early leads run 1831 ----
snap["contracts"]["HackouCoinPass"] = {
    "address": "0xA96f20BCeD857d3174Bb40e806b0151daeEaa62e",
    "name": "HackouCoinPass", "symbol": "HCPASS", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 258, "totalMinted": 259, "freeMinted": 259, "freeRemaining": 852,
    "FREE_SUPPLY": 1111, "MAX_SUPPLY": 2222, "mintOpen": 1, "isFreeOpen": 1,
    "saleStart": 1794310281, "saleStartWib": "2026-11-10 18:31 WIB",
    "saleEnd": 1794569481, "saleEndWib": "2026-11-13 18:31 WIB",
    "canFreeMint_user": True, "freeMintedBy_user": 0, "costOf_user_1": 0, "balanceOf_user": 0,
    "owner": "0x0000000000000000000000000000000000000000",
    "firstSeenBlock": 132771694, "firstSeenWib": "2026-11-10 ~18:31 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True, "sourcify": "exact_match",
    "website": "https://hackou.com/coin-pass/",
    "gate": "website_verified",
    "launchNote": "saleStart() on-chain = 1794310281 = 2026-11-10 18:31 WIB -> umur hitungan menit, TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1831 (temuan feed Sourcify recently-verified). "
        "Agent-shaped: Sourcify exact_match, ABI punya AGENT_ID_REGISTRY + agentIdRegistry() = registry persis, "
        "canFreeMint/claimFree/freeMint/mintFree, FREE_SUPPLY/FREE_PER_WALLET. First mints terverifikasi on-chain "
        "(totalMinted 259). Free% 259/1111 = 23,3% (<25% strong leg, <50% kandidat) -> EARLY. Slot user TERBUKA: "
        "canFreeMint(user)=true, freeMintedBy(user)=0, costOf(user,1)=0, balanceOf(user)=0. Website TERVERIFIKASI "
        "(metode H: contractURI external_link https://hackou.com/coin-pass/ mencetak kontrak persis + registry + "
        "supply/pricing cocok on-chain). X/discussion UNVERIFIED. Owner() = 0x0 (renounced), TIDAK ada di "
        "same-owner-discards.json. Tidak pernah di-preview/di-mint (early lead). Promosi ke strong lead bila "
        "free% >=25% + umur tetap <=48 jam + slot terbuka."}
snap["contracts"]["NIGHTFORGE B"] = {
    "address": "0x051f04ff7b095793613b9caac197cc1051c24e2b",
    "name": "NIGHTFORGE B", "symbol": "SMITH", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 303, "MAX_SUPPLY": 9999, "mintOpen": 1,
    "mintStart": 1794297070, "mintStartWib": "2026-11-10 14:51 WIB",
    "mintedBy_user": 0, "balanceOf_user": 0,
    "firstSeenBlock": 132769564, "firstSeenWib": "2026-11-10 ~17:44 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True, "sourcify": "404-not-verified",
    "gate": "website_unverified",
    "launchNote": "mintStart() on-chain = 1794297070 = 2026-11-10 14:51 WIB -> umur ~3h50m, TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1831 (temuan Boltbook ZH trio post). Agent-shaped: bytecode "
        "17.776 byte MENGANDUNG registry address 0x60B926...022F (Sourcify 404). First mints terverifikasi on-chain "
        "(totalSupply 303, cocok persis dengan angka Boltbook). Free% + slot user UNVERIFIED: freeMinted/FREE_SUPPLY/"
        "freeClaimed/agentIdRegistry/costOf/quote semua REVERT (ABI berbeda dari NIGHTFORGE A). Website UNVERIFIED "
        "(trio post tanpa site link; pencarian nama/kontrak tanpa hasil). X UNVERIFIED (diskusi Boltbook saja). "
        "Owner() REVERT (unverifiable); keluarga/PAYEE sama dengan NIGHTFORGE A + EMBERANVIL per Boltbook, keduanya "
        "TIDAK ada di same-owner-discards.json. Boltbook pace: B +96/jam vs A +20, EMBER +66. Tidak pernah "
        "di-preview/di-mint (early lead). Promosi ke strong lead bila free% + slot terverifikasi."}

# ---- new track_c watchlist-only run 1831 (NOT leads) ----
snap["track_c"]["YAMA PROJECT"] = {
    "sale": "0x86D779fc4d83044cCECCb53639f9a98E367D6E46",
    "token": "0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2",
    "name": "YAMA PROJECT", "kind": "track-c-sale-S1",
    "status": "watchlist-only-age-website-unverified-2026-11-10",
    "totalShares": 2657, "totalFreeShares": 2655, "totalPaidShares": 2,
    "MAX_SHARES": 100000, "LIQUIDITY_TARGET_SHARES": 5000,
    "PRICE": "0.001 BNB", "TOKENS_PER_SHARE": 1000000,
    "quote_user_1": 0, "freeUsed_user": 0, "isAgent_user": True, "quotaOf_user": 10,
    "pair": "0x0",
    "firstSeenWib": "2026-11-10 ~18:4x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "baselineNote": "Track-C WATCHLIST-ONLY run 1831 (temuan Boltbook ZH + AirdropBuzz), BUKAN lead/kandidat: umur "
        "UNVERIFIED (Boltbook klaim first mint 10 Nov ~05:15 vs cek AirdropBuzz bertanggal 9 Nov - konflik; "
        "koroborasi first-mint block mustahil tanpa getLogs) + website UNVERIFIED (pencarian nama hanya hasil "
        "tidak terkait). S1 pass (mint + quote + freeUsed/totalFreeShares + registry persis); quote(user,1)=0, "
        "freeUsed(user)=0, isAgent(user)=true; pool terbuka 2657/100000 (2655 free). Peringatan: belum ada pair/LP; "
        "vault owner bisa withdraw BNB untuk likuiditas masa depan. Naik jadi lead hanya bila umur terverifikasi "
        "<=48 jam + website terverifikasi."}
snap["track_c"]["LOWB"] = {
    "sale": "0x00487ED061C77A1dd5085ef3a2D593366f9C6B35",
    "token": "LOWB itself (single-contract token+sale)",
    "name": "LOWB", "kind": "track-c-sale",
    "status": "watchlist-only-not-open-2026-11-10",
    "totalFreeMinted": 205, "FREE_SHARES": 1000, "MAX_SHARES": 10000,
    "totalMinted": 205, "opened": False, "pair": "0x0",
    "PRICE": "0.002 BNB", "MINT_DEADLINE": 1794657600, "MINT_DEADLINE_WIB": "2026-11-14 19:00 WIB",
    "owner": "0x000000000000000000000000000000000000dead",
    "firstSeenWib": "2026-11-10 ~18:28 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "baselineNote": "Track-C WATCHLIST-ONLY run 1831 (temuan feed Sourcify), BUKAN lead: sale BELUM dibuka "
        "(opened=false, pair 0x0). Sale-shape borderline S1: mint + freeMint + freeMinted/totalFreeMinted + "
        "agentRegistry() persis + PRICE view; TANPA fungsi quote/cost di ABI (strict S1 minta quote/cost). "
        "totalFreeMinted 205/1000. Owner 0xdead, TIDAK ada di same-owner-discards.json. Cek ulang flag opened run berikut."}

# ---- binanceai.fun: unchanged (direct verify this run) ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 1831"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~19:0x WIB"
    snap["binanceai_claim"]["block"] = 132772378
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 1831 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 1801. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote1831_1110"] = (
    "Run 1831 (2026-11-10 18:31-~19:0x WIB, blok re-read 132769068): re-read 672 kontrak + 81 track_c (659 dtk). "
    "Velocity LOLOS 4, TANPA promosi (ACOS-3aed +73 umur/pct/website unverified; Zhenzhu artefak unit-token; "
    "Claf Eye +220 free%+umur unverified; Fossil Drawer +79 minted-by-user). "
    "EARLY LEAD BARU 2 (dilaporkan sekali): HackouCoinPass HCPASS 0xA96f20BC (free 259/1111=23,3%, saleStart 18:31 WIB, "
    "slot terbuka, website TERVERIFIKASI hackou.com/coin-pass) + NIGHTFORGE B 0x051f04ff (SMITH, 303/9.999, mintStart "
    "14:51 WIB, registry bytes; free%/slot/website UNVERIFIED). Keduanya TIDAK di-preview/di-mint (early lead). "
    "TRACK-C WATCHLIST-ONLY baru 2 (dicatat, BUKAN lead): YAMA PROJECT (umur+website unverified) + LOWB (belum dibuka). "
    "AGE-EXCLUSION 7 (catch-up): Jinli Agents, 0xa8543350, 0x1fab92b9, Cassetto, Retrocam, Hourglas, CAISHEN "
    "(first mint terverifikasi 8 Nov, free pool terverifikasi terbuka, umur 51,6-59,8 jam) - dihapus + dilaporkan sekali. "
    "CHEEMSA sold-out 1000/1000 TERVERIFIKASI run ini (sudah dilaporkan hot-leg 1804, tidak diulang). "
    "Agentic Gangster free pool HABIS (sudah excluded run 1431, log saja). "
    "Scan leg FAST-FAIL (preflight Ankr 401; watermark tetap 132512564; gap ~259.130 blok). "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah. "
    "0 kandidat baru, 0 strong lead baru, 0 track-C lead/kandidat baru, 0 track-B claim, 0 eksekusi.")
snap["runNote1831_1110_scan"] = (
    "Run 1831 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132769357-132769406), HTTP 401 Unauthorized "
    "(outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan "
    "(tetap 132512564; gap ke head ~259.130 blok dan tumbuh - milik backfill, ikut gagal 401). Route 5c: tanpa output scan baru.")
snap["runNote1831_1110_discovery"] = (
    "Run 1831 discovery: Sourcify feed 20 terbaru (verified 18:09-18:32 WIB), ABI penuh kembali (tidak degradasi); "
    "2 hit: HackouCoinPass (EARLY) + LOWB (track-C watchlist-only, belum dibuka). 18 lain bukan agent-shaped "
    "(proxy/vault infra, card/staking, ERC20 polos, PickMine/PickToken, ImprintCanvasV2). Boltbook EN+ZH: NIGHTFORGE B "
    "(EARLY), YAMA PROJECT (track-C watchlist-only), Agentic Gangster (sold out, sudah excluded run 1431), PONK buka "
    "21:00 WIB tanpa kontrak (upcoming saja). Sweep: AGIO (thesis-gated, tanpa kontrak) + JAGENT (berbayar 1 USDT) "
    "excluded. Komplemen rute 6: Square/Odaily/PANews tanpa lead baru; DappBay tidak dibutuhkan.")
snap["runNote1831_1110_age_exclusions"] = (
    "Run 1831 age-exclusions baru: 7 (catch-up) - Jinli Agents (firstMint 8 Nov 06:44:59, 59,8 jam, freeClaimed 359/888), "
    "0xa8543350 (8 Nov 08:12:40, 58,3 jam, 2966/7000), 0x1fab92b9 (8 Nov 08:12:39, 58,3 jam, 2437/4000), Cassetto "
    "(8 Nov 14:56:03, 51,6 jam, 2735/7000), Retrocam (8 Nov 14:56:27, 51,6 jam, 2740/7000), Hourglas (8 Nov 14:56:12, "
    "51,6 jam, 3051/7000), CAISHEN (8 Nov 14:55:43, 51,6 jam, 281/888) - semuanya mintOpen 1 + free pool terverifikasi "
    "terbuka. Dihapus dari contracts + dicatat di age_exclusions + dilaporkan sekali. "
    "DITAHAN (pool state tidak terverifikasi, bukan bukti bersih): Dafeiyu (totalSupply 666 == FREE_SUPPLY 666, "
    "freeClaimed tak terbaca), Undead NFTs + NEKART (cap free tak diketahui), 0xAAEF5BB8 / 0x5Ba49f09 / Zorrie / "
    "King's Game / Pixel Laptop (free views None), 0xf710ebd2 (mintOpen 0 = mint tertutup), N1007-c900 (firstMint "
    "hanya estimasi, umur UNVERIFIED), PACK-B8Cf (shape unverified). Windowed check (deadline 18:01-18:31 WIB): nihil.")
snap["runNote1831_1110_binanceai"] = (
    "Run 1831 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132772378). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote1831_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})),
      "removed this run:", removed_names)
