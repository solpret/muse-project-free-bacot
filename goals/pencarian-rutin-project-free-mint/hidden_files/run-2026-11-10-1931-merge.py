#!/usr/bin/env python3
"""Merge run 1931 reread+vel+discovery into snapshot. FRESH for run 1931 only.
Run 1931 (jadwal 19:31 WIB, dieksekusi ~19:31-20:0x WIB). Block re-read: 132777614.
Reread 671 kontrak + 84 track_c (690,6 dtk, bsc-dataseed; Ankr tidak dipakai).

ATURAN UMUR BARU (AGENTS.md, diadopsi 2026-11-10 ~19:36 WIB, di tengah run ini):
ambang FREE BACOT berubah <=48 jam -> KURANG DARI 24 jam, berlaku semua tier.
Run ini menerapkan aturan baru: band 24-48 jam dengan launch TERVERIFIKASI +
free pool tersisa TERVERIFIKASI -> age-excluded (dilaporkan sekali bila pernah
dilaporkan); pool UNVERIFIED -> DITAHAN (preseden Gloop/Dafeiyu run 1831/1901);
launch hanya dari teks/firstSeen -> DITAHAN (bukan launch terverifikasi).

- EARLY LEAD BARU 2 (dilaporkan sekali run ini, via feed Sourcify recently-verified):
  BYTEBLOOM 0x74bbDAD7 (BLOOM; mintStart 2026-11-10 19:30:55 WIB; status minted 154,
  paid 0, agentFree 154, xFree 0; freeLeft 1846/2000 = 7,7% agent lane; website
  bytebloom.pages.dev TERVERIFIKASI via contractURI -> config.js mencetak kontrak
  persis + registry; slot user TERBUKA walletInfo hasAgentId=1 agentFreeNext=1
  freeUsed=0; X UNVERIFIED; velocity belum ada baseline) dan KERNELMONK 0x016b9CE7
  (MONK; mintStart 2026-11-10 19:24:46 WIB; status minted 251, paid 0, agentFree 251;
  freeLeft 1749/2000 = 12,6%; website kernelmonk.pages.dev TERVERIFIKASI sama;
  slot user TERBUKA). Keduanya: agent-shaped (REGISTRY()=registry persis,
  freeLeft() tuple, mintOpen 1, MAX_SUPPLY 5555, PRICE 0,0009 BNB), Sourcify
  exact_match, fee_recipient SAMA 0x442F0C6F811AbF2c1970E00d0Fb6903000283030
  (gelombang 2 kontrak 1 kreator; TIDAK ada di same-owner-discards.json; owner()
  tidak ada di ABI). TIDAK di-preview/di-mint (early lead). Market sendiri:
  0x8c1c800f (BYTEBLOOM) + 0xb8599513 (KERNELMONK), keduanya juga di feed hari ini.
  Catatan: freeMint() no-arg TIDAK ADA di ABI template ini; jalur gratis Agent ID
  adalah mint(1) value 0 bila walletInfo.agentFreeNext=1 (verifikasi on-chain
  untuk wallet user: agentFreeNext=1 di kedua kontrak); jalur X butuh signature
  backend (freeMintXWithRef) - BUKAN jalur eksekusi langsung. Koroborasi first-mint
  via status()/freeLeft() yang bergerak + mintStart; getLogs first-Transfer
  mustahil (Ankr 401).
- SELLOUT BARU 3 (free pool 100%, dilaporkan sekali): FrankensteinFriends
  (freeClaimed 696/696), VampireVibes (675/675), 0xCFB72b0E (freeMinted 1111/1111).
- AGE-EXCLUDED BARU 2 (aturan <24 jam, launch terverifikasi, pool tersisa
  terverifikasi, pernah dilaporkan -> dilaporkan sekali): ShadowSquad
  (firstMint 2026-11-09 06:40 WIB, 36,8 jam; free 412/819) + Agentite
  (mintStart 2026-11-09 05:46 WIB, 37,7 jam; freeMinted 134/1000).
  DITAHAN (pool UNVERIFIED, preseden Gloop): HELIX, Beast16, Pressure, NUMBI,
  Lucky Cat, Meow Cards, BAHUANG3, Reel, Riddle Run, Gloop, Pixel Laptop.
  DITAHAN (launch UNVERIFIED - hanya teks/firstSeen): KIJIN, Dragon Agent,
  Iron Bloom, Agentic, 0x13A1Ebc9-new, Shard Id, Sidecoo Season, STAR CARDS, JOLT.
  >48 jam lainnya (45 item) tetap ditahan preseden yang sama - TIDAK dibersihkan
  massal run ini.
- Velocity LOLOS 2 TANPA promosi: Pixel Laptop +95 (7,31x; free% UNVERIFIED +
  umur 52,6 jam) + Orbit Atlas +21 (4,19x; free% + umur UNVERIFIED, agent-shape
  tidak menentukan). STALL +107 (ratio None, belum ada baseline rate).
- Scan leg FAST-FAIL (preflight Ankr 401 dalam 5,6 dtk, head 132777643; outage
  berlanjut sejak 2026-11-09 ~13:33 WIB; kuota Ankr 0% s.d. 1 Des 2026).
  Watermark tetap 132512564; gap ke head ~265.079 blok.
- binanceai.fun TIDAK BERUBAH (launched 0, failed 1, refund 1, shares 3110,
  tokenClaimed user 0, blok 132778642).
- Bridge scan-bridge.json TIDAK berubah (116 kontrak; 6 belum di snapshot, semua
  temuan lama Nov 3-4: Ore/ETHBack/Ikigai/AGC/PANBA ERC20 + Krillfarm
  same-owner-discarded; bukan lead NFT, tanpa promosi).
- Feed Sourcify 20 terbaru (verified 19:22-19:38 WIB): 2 hit agent-shape NFT
  (BYTEBLOOM + KERNELMONK di atas); 0 hit sale-shape. 0x572872D3 hanya
  agentRegistry (tanpa mint/free views) + 0xd60c3a76 hanya registry - bukan lead.
- Boltbook EN+ZH (curl langsung, 45.630/45.429 byte): 4 alamat baru, semuanya
  BUKAN lead (FATCOIN meme Robinhood Chain; DigiWarriors mintOpen 0 + paid
  0,0009 BNB; DYOR vesting token; 0x8269ea = link BOLT di header situs).
  10 alamat lain sudah di snapshot.
- Sweep: Agentic Gangster sold out (sudah excluded), Horus Phase 1 sold out,
  MOLT/Subsonic/Grove/PixelFox sudah di snapshot - tanpa lead baru.
- Rute 6: Square (AirdropBuzz MALTA/YAMA, Ptah lewat - sudah dikenal),
  Odaily + PANews tanpa item Agent ID/free-mint; DappBay tidak dibutuhkan
  (website BYTEBLOOM/KERNELMONK terverifikasi langsung).
- 0 kandidat baru, 0 strong lead baru, 2 early lead baru, 0 track-C lead/
  kandidat baru, 0 track-B claim, 0 eksekusi.
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-1931"
BLOCK = 132777614
NOW = "2026-11-10 19:31 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-1931-premerge")

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
        e["runNote1931_1110"] = text

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
    return (f"Run 1931 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("Pixel Laptop", (dyn_note("Pixel Laptop") or "") +
     " Velocity LOLOS run ini (+95, 7,31x) TAPI TANPA promosi: free% UNVERIFIED "
     "(free views null) + umur 52,6 jam (first mint 2026-11-08 14:56 WIB, di atas "
     "ambang baru <24 jam) + free pool UNVERIFIED -> DITAHAN age-exclusion "
     "(preseden Gloop/Dafeiyu), tetap early lead.")
note("Orbit Atlas", (dyn_note("Orbit Atlas") or "") +
     " Velocity LOLOS run ini (+21, 4,19x) TAPI TANPA promosi: free% UNVERIFIED + "
     "umur UNVERIFIED + agent-shape tidak menentukan (ABI tanpa registry_ref, "
     "tanpa free views). Tetap watchlist-only.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead run 1901: 542->649 (+107, ratio None - belum ada baseline rate, "
     "velocity GAGAL). Free% + umur UNVERIFIED. Tetap early lead.")
note("ACOS-3aed", (dyn_note("ACOS-3aed") or "") +
     " +100 (3,33/mnt, 0,83x) velocity GAGAL. Umur/pct/website UNVERIFIED. "
     "Bukan early lead, bukan kandidat.")
note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " Minted-by-user run 1909/1901 (#539); +89 interval ini. Tanpa aksi.")
note("Fossil Drawer", (dyn_note("Fossil Drawer") or "") +
     " Minted-by-user: totalSupply 1121. Tanpa aksi.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") +
     " Minted-by-user: freeClaimed 2426/7777 = 31,2%. Tanpa aksi.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Early lead: 5456->5522 (+66, 0,45x) velocity GAGAL. Free% + umur UNVERIFIED. Tetap early lead.")
note("Agentite", (dyn_note("Agentite") or "") +
     " AGE-EXCLUDED run ini (aturan baru <24 jam): mintStart 2026-11-09 05:46 WIB "
     "(37,7 jam), freeMinted 134/1000 = 13,4% (pool tersisa terverifikasi). "
     "Status -> age-excluded-2026-11-10. Dilaporkan sekali run ini.")
note("ShadowSquad", (dyn_note("ShadowSquad") or "") +
     " AGE-EXCLUDED run ini (aturan baru <24 jam): first mint 2026-11-09 06:40 WIB "
     "(36,8 jam), freeClaimed 412/819 = 50,3% (pool tersisa terverifikasi). "
     "Status -> age-excluded-2026-11-10. Dilaporkan sekali run ini.")
note("FrankensteinFriends", (dyn_note("FrankensteinFriends") or "") +
     " SELLOUT BARU run ini: freeClaimed 696/696 = 100% (free pool habis). "
     "Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali run ini.")
note("VampireVibes", (dyn_note("VampireVibes") or "") +
     " SELLOUT BARU run ini: freeClaimed 675/675 = 100% (free pool habis). "
     "Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali run ini.")
note("0xCFB72b0E", (dyn_note("0xCFB72b0E") or "") +
     " SELLOUT BARU run ini: freeMinted 1111/1111 = 100% (free pool habis). "
     "Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali run ini.")
note("Gloop", (dyn_note("Gloop") or "") +
     " DITAHAN age-exclusion (aturan baru <24 jam): launch 8 Nov 19:00 WIB "
     "terverifikasi (48,5 jam) TAPI free pool state UNVERIFIED (totalMinted 87, "
     "FREE_SUPPLY/free views null, mintOpen 1) - preseden run 1831/1901. Tetap "
     "early-lead-reported-2026-11-08.")

# ---- generic NEW-sellout detection (prev < cap <= fresh) ----
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
            entry["runNote1931_1110"] = (f"Run 1931 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS (generic):", new_sellouts if new_sellouts else "none")

# ---- specific sellouts: free pool already at cap in snapshot, confirmed fresh ----
for name, key, cap in [("FrankensteinFriends", "freeClaimed", 696),
                       ("VampireVibes", "freeClaimed", 675),
                       ("0xCFB72b0E", "freeMinted", 1111)]:
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["status"] = "sold-out-free-pool-exhausted-2026-11-10"

# ---- age-exclusions (aturan baru <24 jam): ShadowSquad + Agentite ----
for name in ("ShadowSquad", "Agentite"):
    e = snap["contracts"].get(name)
    if isinstance(e, dict):
        e["status"] = "age-excluded-2026-11-10"

# ---- BYTEBLOOM + KERNELMONK: new early leads ----
snap["contracts"]["BYTEBLOOM"] = {
    "address": "0x74bbDAD7c027C56bE30A7fEaC6F7371B95f1c32B",
    "name": "BYTEBLOOM", "symbol": "BLOOM", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 154, "totalMinted": 154, "paid": 0, "agentFree": 154, "xFree": 0,
    "revealed": 153, "mintOpen": 1,
    "MAX_SUPPLY": 5555, "PRICE": 900000000000000,
    "agentFreeCap": 2000, "xFreeCap": 1000,
    "agentFreeLeft": 1846, "xFreeLeft": 1000,
    "freePctAgentVerified": 7.7,
    "mintStart": 1794313855, "mintStartWib": "2026-11-10 19:30:55 WIB",
    "mintEnd": 1794918655, "mintEndWib": "2026-11-17 19:30:55 WIB",
    "market": "0x8c1c800Fc3079E9dEa13a9c5F4c20d0e5e2f2675",
    "feeRecipient": "0x442F0C6F811AbF2c1970E00d0Fb6903000283030",
    "xSignerAddress": "0x200C0f78B08C3C8E80cE5f5EeECdb1259Cf0fFF4",
    "balanceOf_user": 0, "mintedBy_user": 0,
    "walletInfo_user": {"minted": 0, "canMint": 20, "freeUsed": 0, "hasAgentId": 1,
                        "agentFreeNext": 1, "nextReward": 10000000000000000000000, "claimable": 0},
    "agentFreeByWallet_user": 0,
    "firstSeenBlock": 132779566, "firstSeenWib": "2026-11-10 ~19:5x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sourcify": "exact_match (feed recently-verified 2026-11-10T12:36:21Z)",
    "website": "https://bytebloom.pages.dev/",
    "gate": "website_verified",
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart() on-chain 1794313855 = 2026-11-10 "
        "19:30:55 WIB; status().start sama; totalSupply 154 + agentFree 154 (paid 0).",
    "baselineNote": "EARLY lead dilaporkan sekali run 1931 (temuan feed Sourcify "
        "recently-verified + shape-check probe selector). Agent-shaped: REGISTRY() = "
        "registry Agent ID persis; freeLeft() -> (agentLeft, xLeft); mintOpen 1; "
        "MAX_SUPPLY 5555; PRICE 0,0009 BNB; Sourcify exact_match. First mints "
        "terverifikasi on-chain run ini (status minted 154, agentFree 154, freeLeft "
        "agent 1906->1846 bergerak; koroborasi first-Transfer via getLogs mustahil - "
        "Ankr 401). Website TERVERIFIKASI (method H: contractURI -> "
        "bytebloom.pages.dev/meta/collection.json, external_link ke situs; config.js "
        "situs mencetak kontrak persis nft 0x74bb... + registry + market). Slot user "
        "TERBUKA + GRATIS: walletInfo(user) hasAgentId=1, agentFreeNext=1, "
        "freeUsed=0, mintedBy(user)=0, balanceOf(user)=0; jalur gratis Agent ID "
        "adalah mint(1) value 0 (freeMint() no-arg TIDAK ADA di ABI; jalur X butuh "
        "signature backend freeMintXWithRef - bukan jalur eksekusi langsung). "
        "Free% agent lane 154/2000 = 7,7% (<25% strong lead). X discussion UNVERIFIED. "
        "Velocity: run pertama, belum ada baseline rate. Fee_recipient SAMA dengan "
        "KERNELMONK 0x442F0C6F811AbF2c1970E00d0Fb6903000283030 (gelombang 2 kontrak, "
        "1 kreator); TIDAK ada di same-owner-discards.json; owner() tidak ada di ABI. "
        "Market sendiri ada (0x8c1c800f, juga di feed hari ini). TIDAK pernah "
        "di-preview/di-mint (early lead). Promosi ke strong lead bila free% agent "
        ">=25% + umur <24 jam + slot terbuka."}
snap["contracts"]["KERNELMONK"] = {
    "address": "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7",
    "name": "KERNELMONK", "symbol": "MONK", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 251, "totalMinted": 251, "paid": 0, "agentFree": 251, "xFree": 0,
    "revealed": 250, "mintOpen": 1,
    "MAX_SUPPLY": 5555, "PRICE": 900000000000000,
    "agentFreeCap": 2000, "xFreeCap": 1000,
    "agentFreeLeft": 1749, "xFreeLeft": 1000,
    "freePctAgentVerified": 12.55,
    "mintStart": 1794313486, "mintStartWib": "2026-11-10 19:24:46 WIB",
    "mintEnd": 1794918286, "mintEndWib": "2026-11-17 19:24:46 WIB",
    "market": "0xb8599513fb217c9a2A51BAe997E29ba516FE6268",
    "feeRecipient": "0x442F0C6F811AbF2c1970E00d0Fb6903000283030",
    "xSignerAddress": "0xB5a3a38a554148453898692b9dB7a88d5F4645Ef",
    "balanceOf_user": 0, "mintedBy_user": 0,
    "walletInfo_user": {"minted": 0, "canMint": 20, "freeUsed": 0, "hasAgentId": 1,
                        "agentFreeNext": 1, "nextReward": 10000000000000000000000, "claimable": 0},
    "agentFreeByWallet_user": 0,
    "firstSeenBlock": 132779578, "firstSeenWib": "2026-11-10 ~19:5x WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sourcify": "exact_match (feed recently-verified 2026-11-10T12:25:24Z)",
    "website": "https://kernelmonk.pages.dev/",
    "gate": "website_verified",
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart() on-chain 1794313486 = 2026-11-10 "
        "19:24:46 WIB; status().start sama; totalSupply 251 + agentFree 251 (paid 0).",
    "baselineNote": "EARLY lead dilaporkan sekali run 1931 (temuan feed Sourcify "
        "recently-verified + shape-check probe selector). Agent-shaped: REGISTRY() = "
        "registry Agent ID persis; freeLeft() -> (agentLeft, xLeft); mintOpen 1; "
        "MAX_SUPPLY 5555; PRICE 0,0009 BNB; Sourcify exact_match. First mints "
        "terverifikasi on-chain run ini (status minted 251, agentFree 251, freeLeft "
        "agent 1826->1749 bergerak; koroborasi first-Transfer via getLogs mustahil - "
        "Ankr 401). Website TERVERIFIKASI (method H: contractURI -> "
        "kernelmonk.pages.dev/meta/collection.json, external_link ke situs; config.js "
        "situs mencetak kontrak persis nft 0x016b... + registry + market). Slot user "
        "TERBUKA + GRATIS: walletInfo(user) hasAgentId=1, agentFreeNext=1, "
        "freeUsed=0, mintedBy(user)=0, balanceOf(user)=0; jalur gratis Agent ID "
        "adalah mint(1) value 0 (freeMint() no-arg TIDAK ADA di ABI; jalur X butuh "
        "signature backend freeMintXWithRef - bukan jalur eksekusi langsung). "
        "Free% agent lane 251/2000 = 12,6% (<25% strong lead). X discussion UNVERIFIED. "
        "Velocity: run pertama, belum ada baseline rate. Fee_recipient SAMA dengan "
        "BYTEBLOOM 0x442F0C6F811AbF2c1970E00d0Fb6903000283030 (gelombang 2 kontrak, "
        "1 kreator); TIDAK ada di same-owner-discards.json; owner() tidak ada di ABI. "
        "Market sendiri ada (0xb8599513, juga di feed hari ini). TIDAK pernah "
        "di-preview/di-mint (early lead). Promosi ke strong lead bila free% agent "
        ">=25% + umur <24 jam + slot terbuka."}

# ---- track_c generic lastRead updates + 11-11 values ----
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
tc1111 = snap.get("track_c", {}).get("11-11")
if isinstance(tc1111, dict):
    tc1111["freeMinted"] = 401
    tc1111["runNote1931_1110"] = ("Run 1931: freeMinted 385->401/1000 (+16). Umur + website tetap "
        "UNVERIFIED -> tetap watchlist-only, bukan lead.")

# ---- age-exclusion notes (aturan baru <24 jam) ----
snap["runNote1931_1110_age_exclusions"] = (
    "Run 1931 age-exclusions (aturan BARU <24 jam, diadopsi 19:36 WIB): 2 BARU - "
    "ShadowSquad (firstMint 2026-11-09 06:40 WIB, 36,8 jam; free 412/819) + Agentite "
    "(mintStart 2026-11-09 05:46 WIB, 37,7 jam; freeMinted 134/1000); keduanya launch "
    "terverifikasi + pool tersisa terverifikasi + pernah dilaporkan -> dilaporkan sekali "
    "sebagai age-excluded. SELLOUT (bukan age): FrankensteinFriends 696/696, "
    "VampireVibes 675/675, 0xCFB72b0E 1111/1111 (free pool 100%). DITAHAN "
    "(pool UNVERIFIED, preseden Gloop/Dafeiyu): HELIX, Beast16, Pressure, NUMBI, "
    "Lucky Cat, Meow Cards, BAHUANG3, Reel, Riddle Run, Gloop, Pixel Laptop. DITAHAN "
    "(launch UNVERIFIED - hanya teks/firstSeen): KIJIN, Dragon Agent, Iron Bloom, "
    "Agentic, 0x13A1Ebc9-new, Shard Id, Sidecoo Season, STAR CARDS, JOLT. "
    "Catch-up 24-48 jam: 23 item teridentifikasi, 2 diexclude + 3 sellout di atas; "
    "45 item >48 jam tetap ditahan preseden yang sama (TIDAK dibersihkan massal run ini).")

# ---- binanceai.fun: unchanged ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 1931"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~19:5x WIB"
    snap["binanceai_claim"]["block"] = 132778642
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 1931 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 1901. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote1931_1110"] = (
    "Run 1931 (2026-11-10 19:31-~20:0x WIB, blok re-read 132777614): re-read 671 kontrak + 84 track_c (690,6 dtk). "
    "ATURAN UMUR BARU <24 jam diterapkan run ini (diadopsi 19:36 WIB). EARLY LEAD BARU 2 (dilaporkan sekali run ini): "
    "BYTEBLOOM 0x74bbDAD7 (BLOOM; mintStart 19:30:55 WIB; status minted 154, agentFree 154/2000 = 7,7%; website "
    "bytebloom.pages.dev TERVERIFIKASI; slot user terbuka) + KERNELMONK 0x016b9CE7 (MONK; mintStart 19:24:46 WIB; "
    "status minted 251, agentFree 251/2000 = 12,6%; website kernelmonk.pages.dev TERVERIFIKASI; slot user terbuka). "
    "Keduanya agent-shaped + Sourcify exact_match + fee_recipient sama 0x442F (gelombang 2 kontrak, TIDAK ada di "
    "same-owner-discards.json); TIDAK di-preview/di-mint (early lead). SELLOUT BARU 3: FrankensteinFriends 696/696, "
    "VampireVibes 675/675, 0xCFB72b0E 1111/1111. AGE-EXCLUDED BARU 2: ShadowSquad (36,8 jam) + Agentite (37,7 jam). "
    "Velocity LOLOS 2 TANPA promosi (Pixel Laptop +95 free% UNVERIFIED + umur 52,6 jam; Orbit Atlas +21 free%/umur "
    "UNVERIFIED). Scan leg FAST-FAIL (preflight Ankr 401, 5,6 dtk; watermark tetap 132512564; gap ~265.079 blok). "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah. "
    "0 kandidat baru, 0 strong lead baru, 0 track-C lead/kandidat baru, 0 track-B claim, 0 eksekusi.")
snap["runNote1931_1110_scan"] = (
    "Run 1931 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132777643), HTTP 401 Unauthorized "
    "dalam 5,6 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564; gap ke head ~265.079 blok dan tumbuh - milik backfill, ikut gagal 401). "
    "Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote1931_1110_discovery"] = (
    "Run 1931 discovery: Sourcify feed 20 terbaru (verified 19:22-19:38 WIB), shape-check via probe selector: "
    "2 hit agent-shape NFT (BYTEBLOOM + KERNELMONK, keduanya EARLY lead run ini); 0 hit sale-shape; 0x572872D3 "
    "hanya agentRegistry + 0xd60c3a76 hanya registry (bukan lead). Boltbook EN+ZH via curl langsung (45.630/45.429 "
    "byte): 4 alamat baru, semuanya BUKAN lead (FATCOIN meme Robinhood Chain; DigiWarriors mintOpen 0 + paid "
    "0,0009 BNB; DYOR vesting token; 0x8269ea = link BOLT di header situs). Sweep: Agentic Gangster sold out "
    "(sudah excluded), Horus Phase 1 sold out, MOLT/Subsonic/Grove/PixelFox sudah di snapshot - tanpa lead baru. "
    "Komplemen rute 6: Square (AirdropBuzz MALTA/YAMA, Ptah lewat - sudah dikenal), Odaily + PANews tanpa item "
    "Agent ID/free-mint; DappBay tidak dibutuhkan (website BYTEBLOOM/KERNELMONK terverifikasi langsung).")
snap["runNote1931_1110_binanceai"] = (
    "Run 1931 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132778642). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote1931_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
