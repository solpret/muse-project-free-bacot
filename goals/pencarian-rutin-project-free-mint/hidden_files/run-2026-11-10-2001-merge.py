#!/usr/bin/env python3
"""Merge run 2001 reread+vel+discovery into snapshot. FRESH for run 2001 only.
Run 2001 (jadwal 20:01 WIB, dieksekusi ~20:01-20:4x WIB). Block re-read: 132781366.
Reread 673 kontrak + 84 track_c (881,0 dtk, bsc-dataseed; Ankr tidak dipakai).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2001"
BLOCK = 132781366
NOW = "2026-11-10 20:01 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
tgt = json.load(open(f"{BASE}/run-{TS}-target.json"))
probe = json.load(open(f"{BASE}/run-{TS}-probe.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2001-premerge")

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
        e["runNote2001_1110"] = text

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
    return (f"Run 2001 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

note("Agentic", (dyn_note("Agentic") or "") +
     " Velocity LOLOS run ini (+20, 20,20x) TAPI TANPA promosi: status "
     "strong-lead-gate-failed-2026-11-09 (website gate GAGAL, tidak ada website "
     "terverifikasi) + free 18,9% (189/1000, <25% strong lead dan <50% kandidat) + "
     "X UNVERIFIED. Tetap gate-failed, bukan kandidat.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Velocity LOLOS run ini (+105, 1,59x) TAPI TANPA promosi: umur UNVERIFIED "
     "(post Boltbook menyebut launched 06:45 UTC hari ini, belum koroborasi on-chain) "
     "+ free% UNVERIFIED (free views null) + X UNVERIFIED. Tetap early lead.")
note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") +
     " Early lead run 1931. Targeted read blok 132783695: status (361 minted, 0 paid, "
     "361 agentFree, 0 xFree); freeLeft agent 1639/2000 -> agentFree 361/2000 = 18,1% "
     "(<25% strong lead). Velocity: baseline pertama run ini (ratio None), TIDAK lolos. "
     "Website TERVERIFIKASI; slot user terbuka. Tetap early lead.")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") +
     " Early lead run 1931. Targeted read blok 132783702: status (421 minted, 0 paid, "
     "421 agentFree, 0 xFree); freeLeft agent 1579/2000 -> agentFree 421/2000 = 21,1% "
     "(<25% strong lead, mendekati ambang). Velocity: baseline pertama run ini "
     "(ratio None), TIDAK lolos. Website TERVERIFIKASI; slot user terbuka. Tetap early lead.")
note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " Minted-by-user 2026-11-10 (#539); freeMinted 697/1111 = 62,7%. Tanpa aksi.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("Bubblebruin", (dyn_note("Bubblebruin") or "") +
     " Minted-by-user: freeClaimed 2426/7777 = 31,2%. Tanpa aksi.")
note("Zapcourier", (dyn_note("Zapcourier") or "") +
     " Minted-by-user: freeClaimed 712/712 = 100% (free pool habis). Tanpa aksi.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead run 1901: +81 interval ini, velocity GAGAL (0,76x). Free% + umur "
     "UNVERIFIED. Tetap early lead.")
note("ACOS-3aed", (dyn_note("ACOS-3aed") or "") +
     " +145 interval ini (4,83/mnt, 1,45x - di bawah 1,5x), velocity GAGAL. Umur/pct/"
     "website UNVERIFIED. Bukan early lead, bukan kandidat.")

# ---- generic NEW-sellout detection (prev < cap <= fresh, per key, terminal skipped) ----
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
            entry["runNote2001_1110"] = (f"Run 2001 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS (generic):", new_sellouts if new_sellouts else "none")

# ---- Lanternfield: new EARLY lead (feed Sourcify recently-verified) ----
lp = probe["Lanternfield"]
snap["contracts"]["Lanternfield"] = {
    "address": "0x9aab6e84096A780F9400CdD4E230FaA41B4545f2",
    "name": "Lanternfield", "symbol": "LANTF", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-10",
    "totalSupply": 58, "totalMinted": 58, "freeMinted": 59,
    "FREE_SUPPLY": 1500, "FREE_PER_WALLET": 1, "MAX_SUPPLY": 7500,
    "freeRemaining": 1436, "freePctVerified": 3.9,
    "PRICE": 300000000000000, "mintPrice": 300000000000000, "paidMinted": 0,
    "mintOpen": 1, "saleOpen": 1, "isFreeOpen": 1, "saleClosed": 0,
    "saleStart": 1794315653, "saleStartWib": "2026-11-10 20:00:53 WIB",
    "saleEnd": 1794574853, "saleEndWib": "2026-11-13 20:00:53 WIB",
    "freeEnd": 1794574853,
    "balanceOf_user": 0, "freeMintedBy_user": 0,
    "canFreeMint_user": 1, "freeAvailable_user": 1, "hasAgentId_user": 1,
    "freeRemainingFor_user": 1,
    "owner": "0x0000000000000000000000000000000000000000",
    "firstSeenBlock": 132781099, "firstSeenWib": "2026-11-10 ~20:04 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": NOW,
    "xVerified": False, "velocityVerified": False,
    "REGISTRY": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "sourcify": "exact_match (feed recently-verified 2026-11-10T13:01:06Z)",
    "website": "https://lanternfield.surge.sh/",
    "gate": "website_unverified",
    "launchNote": "Umur TERVERIFIKASI <24 jam: saleStart() on-chain 1794315653 = "
        "2026-11-10 20:00:53 WIB; totalMinted 9 (blok 132781099, ~20:04 WIB) -> 58 "
        "(probe run ini).",
    "baselineNote": "EARLY lead dilaporkan sekali run 2001 (temuan feed Sourcify "
        "recently-verified + shape-check S1+S2 PASS). Agent-shaped: AGENT_ID_REGISTRY() "
        "= agentIdRegistry() = 0x60B926...22F persis; hasAgentId(user)=1; freeMint/mintFree/"
        "mintPaid/quote/cost; Sourcify exact_match (98 fns). First mints terverifikasi "
        "on-chain run ini (totalMinted 9 -> 58, freeMinted 59 - bacaan probe lintas blok, "
        "selisih 1; koroborasi first-Transfer via "
        "getLogs mustahil - Ankr 401 + public RPC -32005). Free 59/1500 = 3,9% (<25% "
        "strong lead, <50% kandidat). Website BELUM TERVERIFIKASI (method H: contractURI "
        "external_link lanternfield.surge.sh ADA tapi situs mengembalikan placeholder "
        "Surge 404 dan TIDAK mencetak kontrak - dicek 2x: hot-leg 1959 + run ini). "
        "Slot user TERBUKA + GRATIS: canFreeMint=1, freeMintedBy=0, freeAvailable=1, "
        "hasAgentId=1, freeRemainingFor=1, costOf(user,1)=0 (hot-leg 1959), balanceOf=0. "
        "X discussion UNVERIFIED (tidak ada diskusi publik ditemukan). Velocity: run "
        "pertama, belum ada baseline rate. owner() = 0x0 (ownerless). TIDAK ada di "
        "same-owner-discards.json. TIDAK pernah di-preview/di-mint (early lead). "
        "Promosi ke strong lead bila free% >=25% + umur <24 jam + slot terbuka + website "
        "terverifikasi (gate wajib sebelum eksekusi)."}
snap["contracts"]["Lanternfield"]["runNote2001_1110"] = (
    "Run 2001: EARLY lead BARU (dilaporkan sekali). saleStart 20:00:53 WIB, umur ~20 mnt; "
    "freeMinted 59/1500 = 3,9%; slot user terbuka; website UNVERIFIED; X UNVERIFIED; "
    "velocity belum ada baseline. Bukan strong lead, bukan kandidat. TIDAK di-preview/di-mint.")

# ---- DogeKing sale: checked sale-shape, free pool SOLD OUT (temuan hot-leg 1959) ----
if "DogeKing" not in snap.get("track_c", {}):
    snap.setdefault("track_c", {})["DogeKing"] = {
        "address": "0xd73a0cdce58e07d8e2a38ee771cc3abc45b6fa45",
        "sale": "0xd73a0cdce58e07d8e2a38ee771cc3abc45b6fa45",
        "token": "0xa37b3ff7a1cabf77256a4b246eba1652011e4569",
        "tokenName": "MacroSwap Tracker (MSTRACK)",
        "status": "checked-sale-shape-sold-out-2026-11-10",
        "shape": "S1 PASS (mintShares + quote + freeClaimed + agentIds()=registry persis)",
        "FREE_SHARES": 1000, "freeClaimed": 1000, "isOpen": 0,
        "saleStartWib": "2026-11-10 18:00:00 WIB",
        "lastReadBlock": 132781826, "lastReadWib": NOW,
        "runNote2001_1110": ("Run 2001: DogeKing (RoyalSale) S1 PASS tapi free pool HABIS "
            "1000/1000, isOpen 0 (blok 132781826, hot-leg 1959). BUKAN lead/kandidat, tidak "
            "pernah dilaporkan sebagai lead. Token MSTRACK 0xa37b... (totalSupply 468, "
            "owner 0xb9d326a805c2b2ec5d129afef1990e71b213b938) adalah token sale ini, bukan "
            "NFT mint. Dicatat agar tidak ditemukan ulang."),
    }

# ---- BNB ORBIT: checked, free pool exhausted + age-excluded (temuan sweep) ----
if "BNB ORBIT" not in snap.get("contracts", {}):
    snap["contracts"]["BNB ORBIT"] = {
        "address": "0x6971D5DF35aF236F26068f62e1A8cE71453FA239",
        "name": "BNB Orbit", "symbol": "ORBIT", "kind": "ERC721",
        "status": "checked-not-lead-age-excluded-2026-11-10",
        "totalSupply": 448, "freeMinted": 444, "FREE_SUPPLY": 444, "MAX_SUPPLY": 4444,
        "freePctVerified": 100.0, "mintOpen": 1, "balanceOf_user": 0,
        "lastReadBlock": BLOCK, "lastReadWib": NOW,
        "xVerified": False, "velocityVerified": False,
        "website": "https://bnborbit.fun",
        "launchNote": "Post resmi tim 2026-11-05 09:03 UTC (thecolony.ai) - umur ~5 hari, "
            "di atas ambang <24 jam. Free pool HABIS 444/444.",
        "baselineNote": "Checked-not-lead run 2001 (temuan sweep, BUKAN lead): free pool "
            "habis 444/444 + umur ~5 hari (>24 jam). Tidak pernah dilaporkan sebagai lead. "
            "Dicatat agar tidak ditemukan ulang.",
    }

# ---- track_c generic lastRead updates ----
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
    f1111 = rr.get("track_c", {}).get("11-11", {})
    if f1111.get("freeMinted") is not None:
        tc1111["freeMinted"] = f1111["freeMinted"]
        tc1111["runNote2001_1110"] = (f"Run 2001: freeMinted {f1111['freeMinted']}/1000. Umur + website "
            "tetap UNVERIFIED -> tetap watchlist-only, bukan lead.")

# ---- age-exclusion notes (aturan <24 jam): none new this run ----
snap["runNote2001_1110_age_exclusions"] = (
    "Run 2001 age-exclusions (aturan <24 jam): 0 BARU. Tidak ada entri non-terminal "
    "dengan launch/first-mint terverifikasi di jendela 2026-11-09 19:31-20:01 WIB yang "
    "melewati 24 jam run ini (dicek via launchNote/first-mint di snapshot). DITAHAN "
    "preseden run 1931 tetap berlaku (pool UNVERIFIED: HELIX, Beast16, Pressure, NUMBI, "
    "Lucky Cat, Meow Cards, BAHUANG3, Reel, Riddle Run, Gloop, Pixel Laptop; launch "
    "UNVERIFIED: KIJIN, Dragon Agent, Iron Bloom, Agentic, 0x13A1Ebc9-new, Shard Id, "
    "Sidecoo Season, STAR CARDS, JOLT).")

# ---- binanceai.fun: unchanged (refund phase) ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 2001"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~20:3x WIB"
    snap["binanceai_claim"]["block"] = tgt.get("block")
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 2001 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 1931. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote2001_1110"] = (
    "Run 2001 (2026-11-10 20:01-~20:4x WIB, blok re-read 132781366): re-read 673 kontrak + 84 track_c (881,0 dtk). "
    "EARLY LEAD BARU 1 (dilaporkan sekali run ini): Lanternfield 0x9aab6e84 (LANTF; saleStart 20:00:53 WIB, umur ~20 mnt; "
    "freeMinted 59/1500 = 3,9%; slot user terbuka; website UNVERIFIED - lanternfield.surge.sh placeholder 404; X UNVERIFIED; "
    "velocity belum ada baseline). Bukan strong lead, bukan kandidat; TIDAK di-preview/di-mint. "
    "SELLOUT BARU 0; AGE-EXCLUDED BARU 0. Velocity LOLOS 2 TANPA promosi (Agentic +20, 20,20x - gate-failed + free 18,9%; "
    "Claf Eye +105, 1,59x - umur + free% UNVERIFIED). BYTEBLOOM agentFree 361/2000 = 18,1% + KERNELMONK 421/2000 = 21,1% "
    "(keduanya <25% strong lead; velocity baseline pertama). DogeKing sale S1 PASS tapi free pool HABIS 1000/1000 (dicatat, "
    "bukan lead). BNB ORBIT free pool habis 444/444 + umur ~5 hari (dicatat, bukan lead). "
    "Scan leg FAST-FAIL (preflight Ankr 401, 5,8 dtk; watermark tetap 132512564; gap ~269.420 blok). "
    "binanceai.fun TIDAK BERUBAH (refund phase). Bridge tidak berubah (116 kontrak; 6 temuan lama Nov 3-4, bukan lead). "
    "0 kandidat baru, 0 strong lead baru, 0 track-C lead/kandidat baru, 0 track-B claim, 0 eksekusi.")
snap["runNote2001_1110_scan"] = (
    "Run 2001 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132781984), HTTP 401 Unauthorized "
    "dalam 5,8 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564; gap ke head ~269.420 blok dan tumbuh - milik backfill, ikut gagal 401). "
    "Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote2001_1110_discovery"] = (
    "Run 2001 discovery: Sourcify feed 20 terbaru (verified 13:05-13:25Z) + 6 dari feed 13:01Z: "
    "1 hit agent-shape NFT (Lanternfield, EARLY lead run ini, dari feed 13:01Z); 14 kontrak baru "
    "(verified 13:05-13:25Z) di-shape-check run ini, 0 hit S1/S2 (near-miss: 0xEe778277 mint tanpa "
    "quote/free/agent; 0x12c69A06 quoteBuy + agentIdRegistry tanpa mint/free; 0x2FC1BE66 freeClaimed "
    "tanpa mint/quote/agent); 5 lain dari feed 13:01Z bukan sale-shape (0x48B397e3, 0x51723b9d, "
    "0x61E82Fa1, 0x698f13ba, 0xA8E36b60 LayerZero OFT). Boltbook EN+ZH via curl langsung (46.462/46.173 byte): "
    "alamat baru 0x727e68d5 = TX HASH DogeKing (bukan kontrak; sale-nya 0xd73a..., sold out), 0x8269ea = link BOLT di "
    "footer, MSTRACK 0xa37b... = token DogeKing (sale sold out); Iron Bloom/Orivia/EMBER/4Agent/AGENT CORE/Pokechain/"
    "Minority/JoltClaim sudah di snapshot. Sweep: Agentic Gangster, AGENT COSMOS, MOLT AGENT, Golden Agents, Agent "
    "Harvest, Agent Zet, Agent Grove, Cosmic Sentinel sudah di snapshot; BNB ORBIT dicatat (free habis + umur ~5 hari); "
    "Agent Operators hanya registrasi (mint buka 15 Nov, belum ada kontrak). Komplemen rute 6: Odaily newsflash 0 mention "
    "'agent'; Square/PANews tanpa item baru; DappBay tidak dibutuhkan (tidak ada gate baru yang perlu dicek).")
snap["runNote2001_1110_binanceai"] = (
    "Run 2001 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132783715). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote2001_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
