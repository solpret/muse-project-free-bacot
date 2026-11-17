#!/usr/bin/env python3
"""Merge run 1901 reread+vel+discovery into snapshot. FRESH for run 1901 only.
Run 1901 (jadwal 19:01 WIB, dieksekusi ~19:01-19:5x WIB). Block re-read: 132773577.
Reread 667 kontrak + 83 track_c (707.7 dtk, bsc-dataseed; Ankr tidak dipakai).
- HCPASS PROMOTED early -> strong lead + MINTED: freeMinted 259->467 (42.0%),
  saleStart 18:31 WIB verified, slot open (canFreeMint=1, costOf=0). Website gate
  PASSED (hackou.com/coin-pass). Strong-lead direct mint executed by HOT-LEG run
  1909 (tx 0x2fdac3c967099ad6b58d8f004de64ab5c15870f1bf45f8d56672090b360f36e5,
  blok 132775869, token #539, gas 144567, receipt 1, ownerOf(539)=wallet agent);
  run 1901 independently previewed clean (000000000, +1 ERC721 prediksi #538)
  + executed -> baw deduplicated to the SAME tx hash (no second mint, balanceOf
  tetap 1). Hot leg reported the mint 19:40 WIB -> run 1901 does NOT re-report.
- EARLY LEAD BARU 1 (dilaporkan sekali run ini): STALL 0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308
  (Agent Market Stall; registry bytes; first mint receipt tx 0x866c88... blok 132772880
  status 1 token #393; totalSupply 542/12000; costFor(user,1)=0 slot TERBUKA;
  website TERVERIFIKASI agentmarket.exchange mencetak kontrak persis; umur + free%
  UNVERIFIED). TIDAK di-preview/di-mint (early lead).
- SAME-OWNER-DISCARDED (dicatat, TIDAK dilaporkan sebagai lead, TIDAK dipromosikan):
  Dropnix 0xb95531eb (owner 0xa054275580c6d1c9077543907ac5798f2494ecce = grup factory
  Cryonyx/Gourdwick) + Rayglide 0xc4035e85 (owner 0x53043412c4f2436f68e56bb9638ebebb099fb3c1
  = factory wave 8 kontrak FREE_SUPPLY 7000/MAX_SUPPLY 7777, discard 2026-11-08).
  Keduanya dicek discards SEBELUM preview/mint (tidak ada preview/mint).
- TRACK-C WATCHLIST-ONLY baru 1 (dicatat, BUKAN lead): 11-11 sale 0x64767b1a
  (freeMint 160.000 1111, freeMinted 385/1000, slot terbuka freeClaimed(user)=0,
  endTime 2026-11-17 15:50 WIB; umur + website UNVERIFIED; Alphapedia slug saja).
- UPCOMING WATCHLIST-ONLY baru 1 (dicatat, BUKAN lead): HikariPass 0x66B893bB
  (HPASS, agentRegistry()=registry persis, totalMinted 0, mintOpen 0, MAX 1000).
- HashKitty 0xa0abff12: BUKAN agent-shaped (registry bytes False, agentRegistry()=0),
  kontrak lama totalMinted 2855/10000 -> log saja, TIDAK masuk snapshot.
- Velocity LOLOS 3, TANPA promosi: ACOS-3aed +121 (1,66x; umur/pct/website unverified);
  Agentite +37 (4,11x; free 114/1000=11,4% <25%); NIGHTFORGE +20 (2,50x; free% UNVERIFIED).
  HCPASS +209 (ratio None, prev rate null) -> promosi strong lead (di atas).
- AGE-EXCLUSION windowed (deadline 18:31-19:01 WIB): Gloop (launch 8 Nov 19:00 WIB,
  deadline 19:00 WIB) DITAHAN - free pool state UNVERIFIED (FREE_SUPPLY/free views
  null, totalMinted 87, mintOpen 1); bukan bukti bersih -> TIDAK dihapus.
- Scan leg FAST-FAIL (preflight Ankr 401; outage berlanjut sejak 2026-11-09 ~13:33 WIB;
  watermark tetap 132512564; gap ke head ~261.090 blok).
- binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110, blok 132775141).
- Fossil Drawer freeMinted 1085/1111 (97,7%, 26 tersisa) - minted-by-user, tanpa aksi.
- Bridge scan-bridge.json TIDAK berubah (mtime 2026-11-08 18:21:53 UTC).
- Sourcify feed 20 terbaru (verified 18:48-19:12 WIB): 0 hit agent-shape NFT, 0 hit
  sale-shape; HikariPass upcoming (di atas). Boltbook EN+ZH: STALL (EARLY),
  Dropnix + Rayglide (same-owner-discarded), 11-11 (track-C watchlist-only),
  HashKitty (bukan agent-shaped), Wise Owl/Fossil/NIGHTFORGE trio sudah di snapshot.
- 0 kandidat baru, 0 strong lead baru selain HCPASS (sudah dieksekusi + dilaporkan
  hot-leg), 1 early lead baru (STALL), 0 track-C lead/kandidat baru, 0 track-B claim.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1901"
BLOCK = 132773577
NOW = "2026-11-10 19:01 WIB"
INTERVAL = 30.0
NOW_DT = datetime.datetime(2026, 11, 10, 19, 1, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
WIN_START = datetime.datetime(2026, 11, 10, 18, 31, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1901-premerge")

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
        e["runNote1901_1110"] = text

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
    return (f"Run 1901 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " PROMOSI early -> STRONG LEAD run ini (free 467/1111=42,0% >=25%, umur terverifikasi "
     "saleStart 18:31 WIB, slot terbuka canFreeMint=1 costOf=0) + MINTED: tx "
     "0x2fdac3c967099ad6b58d8f004de64ab5c15870f1bf45f8d56672090b360f36e5, blok 132775869, "
     "token #539, gas 144567, receipt 1, ownerOf(539)=wallet agent. Eksekusi oleh HOT-LEG run 1909; "
     "run 1901 preview bersih (000000000, +1 ERC721 prediksi #538) + execute -> baw dedup ke tx hash "
     "YANG SAMA (tidak ada mint kedua, balanceOf tetap 1). Hot leg melaporkan mint 19:40 WIB -> "
     "run 1901 TIDAK melaporkan ulang. Status -> minted-by-user-2026-11-10.")
note("Agentite", (dyn_note("Agentite") or "") +
     " Velocity LOLOS run ini (+37, 4,11x) TAPI TANPA promosi: free 114/1000=11,4% (<25% strong leg). "
     "Tetap early lead.")
note("NIGHTFORGE", (dyn_note("NIGHTFORGE") or "") +
     " Velocity LOLOS run ini (+20, 2,50x) TAPI TANPA promosi: free% UNVERIFIED (free views null). "
     "Tetap early lead; umur terverifikasi (mintStart 14:37 WIB).")
note("NIGHTFORGE B", (dyn_note("NIGHTFORGE B") or "") +
     " Early lead run 1831: 303->307 (+4). Free% + slot UNVERIFIED. Tetap early lead.")
note("EMBERANVIL", (dyn_note("EMBERANVIL") or "") +
     " Early lead run 1801: 864->880 (+16). Free% UNVERIFIED. Tetap early lead; free lane tutup malam ini per Boltbook.")
note("Cosmic Sentinel", (dyn_note("Cosmic Sentinel") or "") +
     " Early lead run 1801: 280->291 (+11, <20) velocity GAGAL. Umur UNVERIFIED. Tetap early lead.")
note("ACOS-3aed", (dyn_note("ACOS-3aed") or "") +
     " Velocity LOLOS run ini (+121, 1,66x) TAPI TANPA promosi: status watchlist-only-age-pct-website-"
     "unverified-2026-11-04 - umur, free% dan website semuanya UNVERIFIED. Bukan early lead, bukan kandidat.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Early lead: 5309->5456 (+147, 0,67x) velocity GAGAL. Free% + umur UNVERIFIED. Tetap early lead.")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") +
     " Minted-by-user: freeMinted 1085/1111 = 97,7% (26 free tersisa), totalSupply 1095. Tanpa aksi.")
note("bridge-Wise Owl Society-2", (dyn_note("bridge-Wise Owl Society-2") or "") +
     " Bridge watchlist-only: 3436->3478 (+42). Free% + umur UNVERIFIED. Tanpa promosi.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") +
     " Minted-by-user: freeClaimed 2426/7777 = 31,2%. Tanpa aksi.")

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
            entry["runNote1901_1110"] = (f"Run 1901 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS:", new_sellouts if new_sellouts else "none")

# ---- HCPASS -> minted-by-user ----
hcp = snap["contracts"].get("HackouCoinPass")
if isinstance(hcp, dict):
    hcp["status"] = "minted-by-user-2026-11-10"
    hcp["totalSupply"] = 541
    hcp["totalMinted"] = 541
    hcp["freeMinted"] = 541
    hcp["freeRemaining"] = 570
    hcp["mintTx"] = "0x2fdac3c967099ad6b58d8f004de64ab5c15870f1bf45f8d56672090b360f36e5"
    hcp["mintBlock"] = 132775869
    hcp["mintGas"] = 144567
    hcp["mintTokenId"] = 539
    hcp["mintOrderId"] = "26111000002031553756"
    hcp["mintWib"] = "2026-11-10 19:24:48 WIB"
    hcp["userBalance"] = 1
    hcp["freeMintedBy_user"] = 1
    hcp["canFreeMint_user"] = 0
    hcp["mintFeeBnb"] = 0.0000111446
    hcp["mintNote"] = ("Strong-lead direct mint (track A): preview bersih 000000000 (+1 ERC721, prediksi #538, "
        "aktual #539 karena pool bergerak cepat), audit Binance hasResult=false (tanpa hasil, bukan lolos), "
        "riskLevel -1 LOW, tanpa RISK hit; gate website LOLOS (hackou.com/coin-pass/); discards dicek "
        "(owner()=0x0, tidak ada di 60 entri). Dieksekusi hot-leg run 1909; run 1901 execute ter-dedup ke "
        "tx hash yang sama (tidak ada mint kedua). Dilaporkan sekali hot-leg 19:40 WIB. Post-mint: TIDAK ada "
        "own market live (situs hanya halaman mint, tanpa market/trade/listing) -> TIDAK di-list. Rarity: "
        "tier NOT verified (tokenURI #539: Edition Free, Metal Silver, Backdrop Teal; sudah dicatat hot-leg "
        "di nft-rarity-inventory.md, tidak diduplikasi).")

# ---- STALL: new early lead ----
snap["contracts"]["STALL"] = {
    "address": "0xe3de7fd0d12cff4a46d8bf702ab593b6f921b308",
    "name": "STALL", "symbol": "STALL", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 542, "MAX_SUPPLY": 12000, "mintOpen": 1,
    "costFor_user_1": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x3d018a51905e3bc6ea01e5d731e6a0ce89929fd7",
    "firstSeenBlock": 132772880, "firstSeenWib": "2026-11-10 ~19:10 WIB",
    "firstMintTx": "0x866c880b693f0e3736886d676e5fb7fc05a5c7c37feae6639806390f9be31be9",
    "firstMintTokenId": 393,
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "registryBytes": True, "sourcify": "exact_match-2026-11-10 (per Boltbook; direct endpoint 404 run ini)",
    "website": "https://agentmarket.exchange/",
    "gate": "website_verified",
    "launchNote": "Umur peluncuran UNVERIFIED: tidak ada mintStart/START_TIME view; Sourcify verifiedAt 2026-11-10 "
        "per Boltbook (waktu verifikasi, BUKAN launch); first public mention Boltbook 19:10 WIB hari ini; "
        "koroborasi first-mint block mustahil (Ankr 401, public RPC tolak eth_getLogs).",
    "baselineNote": "EARLY lead dilaporkan sekali run 1901 (temuan Boltbook EN+ZH, post nicodart.ai 19:10 WIB + "
        "verifikasi komentar crypto19.ai). Agent-shaped: bytecode 14.806 byte MENGANDUNG registry address "
        "0x60B926...022F; template agentmarket.exchange; Sourcify exact_match per Boltbook. First mints "
        "terverifikasi on-chain run ini (receipt tx 0x866c88... blok 132772880 status 1, token #393; "
        "totalSupply 363->447->542). Slot user TERBUKA + GRATIS terverifikasi: costFor(user,1)=0, "
        "mintedBy(user)=0, balanceOf(user)=0 (site: 1st mint free untuk Agent ID, lalu tier 0,0003 BNB). "
        "Website TERVERIFIKASI (agentmarket.exchange mencetak kontrak persis + harga/costFor). Diskusi: "
        "Boltbook (post + komentar verifikasi). X account UNVERIFIED. Free% UNVERIFIED (free views null). "
        "Owner 0x3d01... TIDAK ada di same-owner-discards.json. Catatan: tiap Stall klaim 25.000 $AMKT "
        "(klaim holder dibuka; kontrak $AMKT tidak disebut di halaman ini - belum diverifikasi). "
        "Tidak pernah di-preview/di-mint (early lead). Promosi ke strong lead bila umur terverifikasi <=48 jam "
        "+ free% >=25% terverifikasi."}

# ---- Dropnix + Rayglide: same-owner-discarded records ----
snap["contracts"]["Dropnix"] = {
    "address": "0xb95531eb859c556b7c9521a99b7b67ba12519564",
    "name": "Dropnix", "symbol": "DROPNIX", "kind": "ERC721",
    "status": "same-owner-discarded-2026-11-10",
    "totalSupply": 2634, "freeClaimed": 2623, "FREE_SUPPLY": 4000,
    "FREE_PER_WALLET": 3, "MAX_SUPPLY": 4444, "mintOpen": 1,
    "balanceOf_user": 0,
    "owner": "0xa054275580c6d1c9077543907ac5798f2494ecce",
    "firstSeenWib": "2026-11-10 ~19:10 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "registryBytes": True, "sourcify": "exact_match-2026-10-30 (per Boltbook)",
    "gate": "website_unverified",
    "baselineNote": "DITEMUKAN run 1901 (Boltbook post nicodart.ai 19:10 WIB) TAPI DIBUANG di triase: owner "
        "0xa054275580c6d1c9077543907ac5798f2494ecce = grup factory Cryonyx/Gourdwick di "
        "same-owner-discards.json (entri Gourdwick + Gourdreaper). TIDAK dilaporkan sebagai lead, TIDAK "
        "dipromosikan, TIDAK pernah di-preview/di-mint (cek discards SEBELUM preview/mint per aturan "
        "2026-11-07). Fakta lain (dicatat saja): freeClaimed 2623/4000=65,6%, FREE_PER_WALLET 3, mint(3) "
        "gratis, mint ke-4+ 0,00005 BNB; contractURI base64 JSON tanpa external_link; situs resmi tidak "
        "ditemukan (flag Boltbook); umur UNVERIFIED (Sourcify verified 2026-10-30 = waktu verifikasi, "
        "BUKAN launch)."}
snap["contracts"]["Rayglide"] = {
    "address": "0xc4035e850f64d61adce8ecd774f1200d655e5f00",
    "name": "Rayglide", "symbol": "RAYGLIDE", "kind": "ERC721",
    "status": "same-owner-discarded-2026-11-10",
    "totalSupply": 2558, "freeClaimed": 2558, "FREE_SUPPLY": 7000,
    "FREE_PER_WALLET": 3, "MAX_SUPPLY": 7777, "mintOpen": 1,
    "balanceOf_user": 0,
    "owner": "0x53043412c4f2436f68e56bb9638ebebb099fb3c1",
    "firstSeenWib": "2026-11-10 ~19:1x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "registryBytes": True,
    "gate": "website_unverified",
    "baselineNote": "DITEMUKAN run 1901 (Boltbook ZH post hooya.ai, Rayglide #2511 claimed free) TAPI DIBUANG di "
        "triase: owner 0x53043412c4f2436f68e56bb9638ebebb099fb3c1 = factory wave 8 kontrak template sama "
        "(FREE_SUPPLY 7000/MAX_SUPPLY 7777) di same-owner-discards.json (Cassetto, Candlewick, Coralume, "
        "Retrocam, Pixpad, Keyforge, Hourglas, Compasso; discard 2026-11-08, promosi strong lead DIBATALKAN "
        "run 1431 preseden Gourdwick). Rayglide sendiri FREE_SUPPLY 7000/MAX_SUPPLY 7777 = template wave "
        "yang sama. TIDAK dilaporkan sebagai lead, TIDAK dipromosikan, TIDAK pernah di-preview/di-mint. "
        "Fakta lain (dicatat saja): freeClaimed 2558/7000=36,5%, FREE_PER_WALLET 3; contractURI base64 JSON "
        "tanpa external_link; umur + website UNVERIFIED."}

# ---- HikariPass: upcoming watchlist-only ----
snap["contracts"]["HikariPass"] = {
    "address": "0x66B893bB2c3CdCc53340A27F7d2735F7a38639a2",
    "name": "HikariPass", "symbol": "HPASS", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-10",
    "totalSupply": None, "totalMinted": 0, "MAX_SUPPLY": 1000, "mintOpen": 0,
    "balanceOf_user": 0,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0x756e33f6bc97f0a12168e08c8b308331f3d4bea7",
    "firstSeenWib": "2026-11-10 ~19:1x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "sourcify": "verified 2026-11-10T12:06:34Z (feed recently-verified)",
    "gate": "website_unverified",
    "baselineNote": "UPCOMING watchlist-only run 1901 (temuan feed Sourcify recently-verified): agentRegistry() = "
        "registry persis 0x60B9...022F, mintOpen 0, totalMinted 0, MAX_SUPPLY 1000, name HikariPass / HPASS. "
        "BELUM launching (0 mint) -> BUKAN lead/kandidat, TIDAK di-preview/di-mint; dilaporkan HANYA sebagai "
        "upcoming watchlist item. Cek ulang flag mintOpen run berikut."}

# ---- 11-11: track-C watchlist-only ----
snap["track_c"]["11-11"] = {
    "sale": "0x64767b1a39441e72046c2162065a2896e154b341",
    "token": "0x398Fa8a4d9e6FE658E3ECD2F4B5CDC8F3562C522",
    "name": "11-11", "kind": "track-c-sale",
    "status": "watchlist-only-age-website-unverified-2026-11-10",
    "freeMinted": 385, "FREE_MINTS": 1000,
    "pricePerShare": 2000000000000000,
    "endTime": 1794905430, "endTimeWib": "2026-11-17 15:50 WIB",
    "freeClaimed_user": 0, "balanceOf_user": 0,
    "owner": "0x0000000000000000000000000000000000000000",
    "firstSeenWib": "2026-11-10 ~19:1x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "registryBytes": True, "sourcify": "exact_match (per Boltbook)",
    "gate": "website_unverified",
    "baselineNote": "Track-C WATCHLIST-ONLY run 1901 (temuan Boltbook post rizeiki.ai), BUKAN lead/kandidat: umur "
        "UNVERIFIED (tidak ada startTime view; window berakhir 2026-11-17 15:50 WIB; first public mention "
        "Boltbook hari ini) + website UNVERIFIED (hanya slug Alphapedia Boltbook, BUKAN situs proyek; pencarian "
        "nama tanpa situs). Sale-shape borderline S1: freeMint() tanpa argumen + freeMinted view + pricePerShare "
        "0,002 BNB + registry bytes di code; TANPA fungsi quote/cost di ABI. 1 free share = 160.000 1111, "
        "freeMinted 385/1000 (naik 358->384->385 run ini), freeClaimed(user)=0 (slot terbuka), owner 0x0 "
        "renounced, TIDAK ada di same-owner-discards.json. Peringatan: belum ada pair/LP, belum ada harga. "
        "Naik jadi lead hanya bila umur terverifikasi <=48 jam + website terverifikasi."}

# ---- track_c generic lastRead updates + fresh YAMA/LOWB values ----
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
yama = snap.get("track_c", {}).get("YAMA PROJECT")
if isinstance(yama, dict):
    yama["totalShares"] = 2669
    yama["totalFreeShares"] = 2667
    yama["totalPaidShares"] = 2
    yama["freeUsed_user"] = 0
    yama["isAgent_user"] = True
    yama["runNote1901_1110"] = ("Run 1901: re-check langsung totalShares 2657->2669, totalFreeShares 2667, paid 2, "
        "freeUsed(user)=0, isAgent(user)=1, quota 10, target likuiditas 2669/5000. Umur + website tetap "
        "UNVERIFIED -> tetap watchlist-only, bukan lead.")
lowb = snap.get("track_c", {}).get("LOWB")
if isinstance(lowb, dict):
    lowb["totalFreeMinted"] = 391
    lowb["totalMinted"] = 400
    lowb["opened"] = False
    lowb["runNote1901_1110"] = ("Run 1901: re-check langsung opened=false (masih BELUM dibuka), totalFreeMinted "
        "205->391/1000, totalMinted 400, sharesOf(user)=0. Tetap watchlist-only-not-open; MINT_DEADLINE "
        "14 Nov 19:00 WIB.")

# ---- age-exclusion windowed check (deadline 18:31-19:01 WIB): Gloop HELD ----
snap["runNote1901_1110_age_exclusions"] = (
    "Run 1901 age-exclusions baru: 0. Windowed check (deadline 18:31-19:01 WIB): Gloop (launch 8 Nov 19:00 WIB "
    "terverifikasi via MINT_START on-chain, deadline 19:00 WIB) DITAHAN - free pool state UNVERIFIED "
    "(FREE_SUPPLY/freeMinted/freeClaimed null, totalMinted 87, mintOpen 1); bukan bukti bersih seperti "
    "preseden run 1831 (Dafeiyu dkk) -> TIDAK dihapus, tetap early-lead-reported-2026-11-08. Catch-up: nihil.")

# ---- binanceai.fun: unchanged ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 1901"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~19:3x WIB"
    snap["binanceai_claim"]["block"] = 132775141
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 1901 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 1831. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote1901_1110"] = (
    "Run 1901 (2026-11-10 19:01-~19:5x WIB, blok re-read 132773577): re-read 667 kontrak + 83 track_c (707,7 dtk). "
    "HCPASS PROMOSI early -> strong lead (free 467/1111=42,0%, saleStart 18:31 WIB, slot terbuka) + MINTED #539 "
    "(tx 0x2fdac3c967099ad6b58d8f004de64ab5c15870f1bf45f8d56672090b360f36e5, blok 132775869, gas 144567; eksekusi "
    "hot-leg run 1909, run 1901 execute ter-dedup ke tx yang sama; dilaporkan sekali hot-leg 19:40 WIB, run 1901 "
    "TIDAK melaporkan ulang). EARLY LEAD BARU 1 (dilaporkan sekali run ini): STALL 0xe3de7fd0 (Agent Market Stall; "
    "costFor(user,1)=0 slot terbuka; website agentmarket.exchange TERVERIFIKASI; umur + free% UNVERIFIED). "
    "SAME-OWNER-DISCARDED 2 (dicatat, TIDAK dilaporkan sebagai lead): Dropnix (owner 0xa054 Cryonyx) + Rayglide "
    "(owner 0x5304 factory wave 7000/7777). TRACK-C WATCHLIST-ONLY baru 1: 11-11 (umur + website unverified). "
    "UPCOMING baru 1: HikariPass (mintOpen 0, 0 mint). HashKitty bukan agent-shaped (log saja). "
    "Velocity LOLOS 3 TANPA promosi (ACOS-3aed +121 umur/pct/website unverified; Agentite +37 free 11,4%; "
    "NIGHTFORGE +20 free% unverified). Age-exclusion: 0 (Gloop DITAHAN, pool unverified). "
    "Scan leg FAST-FAIL (preflight Ankr 401; watermark tetap 132512564; gap ~261.090 blok). "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah. "
    "0 kandidat baru, 0 track-C lead/kandidat baru, 0 track-B claim, 1 eksekusi (HCPASS, ter-dedup hot-leg).")
snap["runNote1901_1110_scan"] = (
    "Run 1901 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132773654), HTTP 401 Unauthorized "
    "dalam 10,0 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564; gap ke head ~261.090 blok dan tumbuh - milik backfill, ikut gagal 401). "
    "Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote1901_1110_discovery"] = (
    "Run 1901 discovery: Sourcify feed 20 terbaru (verified 18:48-19:12 WIB), shape-check via probe selector: "
    "0 hit agent-shape NFT, 0 hit sale-shape; HikariPass upcoming (agentRegistry persis, mintOpen 0). "
    "Boltbook EN+ZH (19:0x WIB): STALL (EARLY), Dropnix + Rayglide (same-owner-discarded), 11-11 (track-C "
    "watchlist-only), HashKitty (bukan agent-shaped), Wise Owl/Fossil/NIGHTFORGE trio sudah di snapshot. "
    "Sweep: AGENT COSMOS (ACOS-3aed, sudah watchlist) + MOLT AGENT (sudah excluded free habis) + Agentite "
    "(sudah early lead) - tanpa lead baru. Komplemen rute 6: Square (AirdropBuzz MALTA/YAMA, Ptah lewat), "
    "Odaily + PANews tanpa item Agent ID/free-mint; DappBay tidak dibutuhkan (STALL website terverifikasi langsung).")
snap["runNote1901_1110_binanceai"] = (
    "Run 1901 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132775141). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote1901_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
