#!/usr/bin/env python3
"""Merge run 2131 reread+vel+target+probe+ember-probe into snapshot. FRESH for run 2131 only.
Run 2131 (jadwal 21:31 WIB, dieksekusi ~21:31-22:3x WIB). Block re-read: 132795774.
Reread 676 kontrak + 85 track_c (403.1 dtk, resume; bsc-dataseed; Ankr tidak dipakai).
Does NOT re-report anything (reporting is the parent run's final message).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-10-2131"
BLOCK = 132795774
NOW = "2026-11-10 21:31 WIB"
INTERVAL = 30.0
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-{TS}-reread.json"))
vel = json.load(open(f"{BASE}/run-{TS}-vel.json"))
tgt = json.load(open(f"{BASE}/run-{TS}-target.json"))
probe = json.load(open(f"{BASE}/run-{TS}-probe.json"))
ember = json.load(open(f"{BASE}/run-{TS}-ember-probe.json"))
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2131-premerge")

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
        e["runNote2131_1110"] = text

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
    return (f"Run 2131 (blok {BLOCK}): totalSupply {row.get('prev')}->{row.get('new')} "
            f"(+{minted}, {rate}/mnt vs prev {row.get('prev_rate')} = {ratio}x) {vtxt}{freetxt}; "
            f"bal_user={f.get('balanceOf_user')}; status {e.get('status')}.{extra_txt}")

# ---- Lanternfield: MINTED by this run (strong-lead direct mint) ----
lf = snap["contracts"].get("Lanternfield")
lp = probe.get("Lanternfield", {})
if isinstance(lf, dict):
    lf["status"] = "minted-by-user-2026-11-10"
    lf["mintTx"] = "0xf5438e5bc1c6fe4c91868b8364043522fb3f460c252c8167a02a90acd0c08f20"
    lf["mintOrderId"] = 26111000002031884369
    lf["mintBlock"] = 132796746
    lf["mintGas"] = 112158
    lf["mintGasBnb"] = 0.000008476
    lf["mintTokenId"] = 516
    lf["balanceOf_user"] = 1
    lf["userBalance"] = 1
    lf["freeMinted"] = 518
    lf["runNote2131_1110"] = (
        "Run 2131: DI-MINT run ini (strong-lead direct mint). Gate BERUBAH sejak run 2101 "
        "(dulu placeholder 404): lanternfield.surge.sh kini LIVE, mencetak kontrak persis 4x di home "
        "(13.041 byte), 2x di llms.txt, 4x di skill.md. Kaki strong lead saat probe: freeMinted 501/1500 = "
        "33,4% (>=25%), umur ~1,9 jam TERVERIFIKASI (saleStart 1794315653 = 2026-11-10 20:00:53 WIB), slot "
        "terbuka (balanceOf 0, freeMintedBy 0, canFreeMint 1, freeAvailable 1, hasAgentId 1). Quote(user,1) = "
        "(freeUnits 1, paidUnits 0, valueWei 0, ok). Audit Binance: hasResult=false (tanpa hasil, bukan lolos), "
        "isSupported true, riskLevel -1, tanpa RISK hit. Preview bersih 000000000 (freeMint() 0x5b70ea9f, value 0, "
        "+1 ERC721 prediksi #513). Tx 0xf5438e5bc1c6fe4c91868b8364043522fb3f460c252c8167a02a90acd0c08f20, blok "
        "132796746, gas 112158 (~0,000008476 BNB), tokenId 516. Pasca-mint: ownerOf(516) = wallet agent, "
        "balanceOf 0->1, freeMintedBy 0->1, freeAvailable 1->0, freeMinted 518/1500. Rarity: tokenURI(516) base64 "
        "JSON, traits Edition Free, Lanterns 6, Sky Plum; TANPA trait Rarity/Tier -> tier NOT verified "
        "(dicatat di nft-rarity-inventory.md). Marketplace: TIDAK ada own market live (situs mint-only; "
        "pencarian web nihil) -> TIDAK di-list (aturan auto-list; Element fallback manual saja).")
    print("Lanternfield reconciled as minted-by-user (run 2131)")

# ---- EMBERANVIL: MINTED by this run (promoted early -> strong lead -> direct mint) ----
em = snap["contracts"].get("EMBERANVIL")
ep = ember.get("EMBERANVIL", {})
if isinstance(em, dict):
    em["status"] = "minted-by-user-2026-11-10"
    em["mintTx"] = "0x50820ce7e5df33d5e7b223e9155fa795b99ea4b9554d54706f843da211ff5d1b"
    em["mintOrderId"] = 26111000002031900481
    em["mintBlock"] = 132797992
    em["mintGas"] = 256939
    em["mintGasBnb"] = 0.00002064
    em["mintTokenId"] = 946
    em["balanceOf_user"] = 1
    em["userBalance"] = 1
    em["totalSupply"] = 946
    em["agentFree"] = 943
    em["runNote2131_1110"] = (
        "Run 2131: PROMOSI early -> STRONG LEAD -> DI-MINT run ini (strong-lead direct mint). Velocity LOLOS "
        "(+29, 0,967/mnt vs 0,367 = 2,63x). Kaki strong lead saat probe segar blok 132797942: agentFreeUsed "
        "942/2000 = 47,1% (>=25%), mintStart 1794297602 = 2026-11-10 14:59 WIB (umur ~7,3 jam TERVERIFIKASI), "
        "slot terbuka (walletInfo [0, 20, 0, 1, 1, 1e22, 0], agentFreeByWallet 0, balance 0). Gate LULUS "
        "metode H via contractURI -> emberanvil.pages.dev: llms.txt + agent.json mencetak kontrak persis 1x "
        "(identitas cocok: 9.999 smith, 3.000 slot gratis, harga 0,0002 BNB). Audit Binance: hasResult=false "
        "(tanpa hasil, bukan lolos), isSupported true, riskLevel -1, tanpa RISK hit. Preview bersih 000000000 "
        "(mint(1) 0xa0712d68...0001, value 0, +1 ERC721 prediksi #946; fungsi sama dengan mint KERNELMONK "
        "terbukti). Tx 0x50820ce7e5df33d5e7b223e9155fa795b99ea4b9554d54706f843da211ff5d1b, blok 132797992, gas "
        "256939 (~0,00002064 BNB), tokenId 946. Pasca-mint: ownerOf(946) = wallet agent, balanceOf 0->1, "
        "agentFreeByWallet 0->1, agentFreeUsed 943/2000, totalSupply 946. tokenURI(946) = sealed crate "
        "(Sealed Ingot Crate, tanpa trait smith; tier NOT verified, dicatat di nft-rarity-inventory.md). "
        "claimable(user) = 10.000 EMBER via claimRewards() - TIDAK di-claim run ini (di luar otorisasi; "
        "dilaporkan sebagai peluang). Marketplace: own market Slag Market "
        "0xb8aa1d77778a107f59906bae4a0b1443e0cd53af (NFT() cocok, fee 3%) listedCount 1, floor live "
        "0,000002839711249073 BNB (#771, satu-satunya listing) -> TIDAK di-list: floor debu di bawah biaya gas "
        "approve+list (~0,00002-0,00004 BNB); listing akan merugi - dilaporkan sekali, Element manual saja.")
    print("EMBERANVIL reconciled as minted-by-user (run 2131)")

# ---- NIGHTFORGE: strong lead, GATE FAILED (site mati) - no execution ----
nf = snap["contracts"].get("NIGHTFORGE")
np = ember.get("NIGHTFORGE", {})
if isinstance(nf, dict):
    nf["status"] = "strong-lead-gate-blocked-2026-11-10"
    nf["runNote2131_1110"] = (
        "Run 2131: STRONG LEAD, GATE GAGAL - dilaporkan sekali run ini sebagai strong-lead-gate-blocked, "
        "TIDAK di-preview/TIDAK di-mint. Probe segar: status [659, 3, 656, 0, 648...], freeLeft [1344, 1000] -> "
        "agentFree 656/2000 = 32,8% (>=25%), mintStart 1794296194 = 2026-11-10 14:37 WIB (umur TERVERIFIKASI "
        "<24 jam), slot terbuka (balanceOf 0, walletInfo [0, 20, 0, 1, 1, 1e22, 0]), PRICE 0,0002 BNB. "
        "MANDATORY WEBSITE GATE GAGAL - nightforge.pages.dev MATI: home/llms.txt/skill.md/agent.json SEMUA "
        "mengembalikan HTML infografis medis yang sama (23.857 byte, 'Following Up Results & Incidental "
        "Findings'), 0 kecocokan kontrak; contractURI -> meta/collection.json juga mengembalikan HTML yang "
        "sama; tokenURI(1) -> meta/3680.json juga HTML yang sama. Pencarian alamat mentah (metode A) nihil. "
        "Sourcify 404 (unverified). Pola keluarga sama (.pages.dev, fee recipient 0x442F...) TIDAK cukup "
        "tanpa situs yang mencetak kontrak. Pantauan lanjut; mint hanya bila gate terverifikasi + guard segar.")
    print("NIGHTFORGE recorded as strong-lead-gate-blocked")

# ---- SOLDERCATS: NEW EARLY LEAD (Sourcify feed, verified 21:39 WIB) ----
if "SOLDERCATS" not in snap.get("contracts", {}):
    snap["contracts"]["SOLDERCATS"] = {
        "address": "0x3D972EBbF7488f21b95250B867e2406c723C9DDC",
        "name": "SOLDERCATS", "symbol": "CAT", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-10",
        "totalSupply": 78, "MAX_SUPPLY": 6666, "PRICE": 900000000000000,
        "agentFreeCap": 2000, "agentFreeUsed": 78, "agentFree": 78,
        "mintStart": 1794321310, "mintOpen": 1, "balanceOf_user": 0,
        "agentFreeByWallet_user": 0,
        "contractURI": "https://soldercats.pages.dev/meta/collection.json",
        "website": "https://soldercats.pages.dev",
        "market": "0xd35592aeccb54a9e528bf4b1a6fcfd4de9367bc9",
        "firstSeenBlock": 132798861, "firstSeenWib": "2026-11-10 ~22:1x WIB",
        "lastReadBlock": 132798861, "lastReadWib": "2026-11-10 ~22:1x WIB",
        "gate": "PASSED (metode H via contractURI): llms.txt + agent.json soldercats.pages.dev mencetak "
            "kontrak persis (lowercase 0x3d972e...); identitas cocok (6.666 supply, harga 0,0009 BNB, token "
            "PURR, Alley Swap 3%, mint reward 10.000 PURR).",
        "runNote2131_1110": (
            "Run 2131 EARLY LEAD BARU (dilaporkan sekali run ini; TIDAK di-preview/TIDAK di-mint - tier early). "
            "Ditemukan via Sourcify feed (verifiedAt 2026-11-10 14:39:02Z = 21:39:02 WIB), shape-check: template "
            "SMITH (freeMintX, freeLeft, AGENT_FREE_CAP, agentFreeByWallet, agentFreeUsed, mintStart, mintOpen). "
            "Probe segar blok 132798861: totalSupply 78, agentFreeUsed 78/2000 = 3,9% (<25% strong lead), "
            "mintStart 1794321310 = 2026-11-10 21:35 WIB (umur ~35 mnt TERVERIFIKASI), mintOpen 1, freeLeft "
            "[1922, 1000], slot user TERBUKA (agentFreeByWallet 0, walletInfo [0, 20, 0, 1, 1, 1e22, 0]). "
            "Website TERVERIFIKASI (lihat gate). Market: Alley Swap 0xd35592aeccb54a9e528bf4b1a6fcfd4de9367bc9 "
            "(juga muncul di feed Sourcify run ini, 17 fns, bukan mint - market, bukan lead). BUKAN dari "
            "Boltbook (tidak disebut di front page EN/ZH run ini) dan BUKAN dari bridge (tidak ada di "
            "scan-bridge.json). Pantauan lanjut untuk promosi ke strong lead bila free% >=25%."),
    }
    print("SOLDERCATS added as early lead")

note("BYTEBLOOM", (dyn_note("BYTEBLOOM") or "") +
     " Early lead run 1931. Targeted read blok 132794859: agentFree 478/2000 = 23,9% (reread 486/2000 = "
     "24,3%), mintOpen 1, saleStart 1794313855 = 2026-11-10 19:30:55 WIB. Velocity GAGAL (+30, 0,65x). "
     "Website TERVERIFIKASI; slot user terbuka. Masih <25% strong lead - re-read prioritas run berikut "
     "(pace ~1/mnt, butuh ~20 mint lagi).")
note("KERNELMONK", (dyn_note("KERNELMONK") or "") +
     " Minted-by-user (hot-leg 20:59 WIB, tx 0x15fbc506...). Targeted read: totalSupply 536. Tanpa aksi.")
note("GoldenAgents", (dyn_note("GoldenAgents") or "") +
     " Probe segar: totalSupply 1442, MAX 100000, owner 0x931b0b8c6dafaef8719cbbb00815ce939a946a07, "
     "free views null, tanpa fungsi agent. Free% + umur + website UNVERIFIED. Tetap early lead.")
note("HIVE Agents", (dyn_note("HIVE Agents") or "") + " Minted-by-user; tanpa perubahan.")
note("HackouCoinPass", (dyn_note("HackouCoinPass") or "") +
     " Minted-by-user 2026-11-10 (#539). Tanpa aksi.")
note("Agentic", (dyn_note("Agentic") or "") +
     " Velocity GAGAL run ini. Gate FAILED (website) tetap berlaku; freeMinted segar vs freePctVerified "
     "lama INKONSISTENSI counter tetap ditandai, bukan kandidat.")
note("STALL", (dyn_note("STALL") or "") +
     " Early lead run 1901. Free% + umur UNVERIFIED. Tetap early lead.")
note("Claf Eye", (dyn_note("Claf Eye") or "") +
     " Velocity GAGAL run ini. Umur + free% UNVERIFIED. Tetap early lead.")

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
            entry["runNote2131_1110"] = (f"Run 2131 (blok {BLOCK}): SELLOUT BARU - {key} {prev}->{fresh}/{cap} "
                f"(cap tercapai interval ini). Status -> sold-out-free-pool-exhausted-2026-11-10. Dilaporkan sekali oleh parent.")
            break
print("NEW SELLOUTS (generic):", new_sellouts if new_sellouts else "none")

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

# ---- age-exclusion notes (aturan <24 jam): none new this run ----
snap["runNote2131_1110_age_exclusions"] = (
    "Run 2131 age-exclusions (aturan <24 jam): 0 BARU. Dicek 6 item yang sudah melewati 24 jam "
    "(Agentic, Reel, Sidecoo Season, Iron Bloom, STAR CARDS, Shard Id) - semuanya DITAHAN per preseden "
    "run 1931/2101 (timestamp mereka adalah Sourcify verifiedAt, bukan launch time, atau jalur gratis "
    "unverified); TIDAK dikeluarkan sepihak. Tidak ada item yang melewati 24 jam di jendela "
    "21:01->21:31 WIB.")

# ---- binanceai.fun: unchanged (refund phase) ----
if isinstance(snap.get("binanceai_claim"), dict):
    snap["binanceai_claim"]["verified_run"] = "2026-11-10 run 2131"
    snap["binanceai_claim"]["verified_wib"] = "2026-11-10 ~21:5x WIB"
    snap["binanceai_claim"]["block"] = tgt.get("block")
    snap["binanceai_claim"]["verify_method"] = ("binanceai re-check run 2131 (direct eth_call): launched 0, failed 1, "
        "isRefundPhase 1, totalShares 3110, tokenClaimed user 0 - TIDAK BERUBAH vs run 2101. Status tetap "
        "closed-refund-phase-2026-11-07, TIDAK dilaporkan ulang.")

# ---- top-level run notes ----
snap["runNote2131_1110"] = (
    "Run 2131 (2026-11-10 21:31-~22:3x WIB, blok re-read 132795774): re-read 676 kontrak + 85 track_c (403,1 dtk, "
    "resume setelah percobaan pertama mati di 300 kontrak). DUA MINT BERHASIL run ini (strong-lead direct mint): "
    "(1) Lanternfield #516 - gate BERUBAH sejak run 2101 (situs kini live, mencetak kontrak 4x), free 501/1500 = "
    "33,4%, tx 0xf5438e5bc1c6fe4c91868b8364043522fb3f460c252c8167a02a90acd0c08f20, blok 132796746, gas 112158 "
    "(~0,000008476 BNB); rarity: Edition Free/Lanterns 6/Sky Plum, tier NOT verified; TIDAK ada own market live "
    "-> TIDAK di-list. (2) EMBERANVIL #946 - promosi early->strong (velocity +29, 2,63x LOLOS; agentFree 942/2000 "
    "= 47,1%), gate lulus metode H (emberanvil.pages.dev), tx "
    "0x50820ce7e5df33d5e7b223e9155fa795b99ea4b9554d54706f843da211ff5d1b, blok 132797992, gas 256939 "
    "(~0,00002064 BNB); sealed crate (tier NOT verified); claimable 10.000 EMBER TIDAK di-claim run ini; own "
    "market Slag Market live (fee 3%) tapi floor debu 0,00000284 BNB (#771) -> TIDAK di-list (di bawah biaya gas). "
    "STRONG LEAD GATE-BLOCKED 1 (dilaporkan sekali, tanpa eksekusi): NIGHTFORGE 656/2000 = 32,8% - "
    "nightforge.pages.dev MATI (semua path mengembalikan HTML infografis medis 23.857 byte, 0 kecocokan kontrak). "
    "EARLY LEAD BARU 1: SOLDERCATS 0x3d972e... (Sourcify 21:39 WIB) - free 78/2000 = 3,9%, mintStart 21:35 WIB, "
    "website TERVERIFIKASI (llms.txt + agent.json mencetak kontrak), slot terbuka. BYTEBLOOM 478-486/2000 ~24% "
    "(masih <25%). KERNELMONK totalSupply 536 (sudah di-mint hot-leg). binanceai.fun TIDAK BERUBAH (refund phase). "
    "Scan leg FAST-FAIL (preflight Ankr 401, 1,2 dtk, head 132794621; watermark tetap 132512564; gap ~282.057 blok). "
    "Discovery: subagent discovery TER-INTERUPSI (compaction) sebelum menulis discovery.json - direkonsiliasi dari "
    "artefaknya (feed 20 kontrak verified 14:14-14:45Z, 6 di-shape-check; Boltbook EN/ZH 45.383/45.616 byte, 11 alamat "
    "semua dikenal/lama; sweep + route 6 TIDAK selesai - ulangi run berikut). 0 kandidat baru, 0 track-C lead/kandidat "
    "baru, 0 track-B claim, 0 age-excluded baru.")
snap["runNote2131_1110_scan"] = (
    "Run 2131 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132794621), HTTP 401 Unauthorized "
    "dalam 1,2 dtk (outage sejak ~13:33 WIB 2026-11-09 berlanjut; kuota Ankr 0% s.d. 1 Des 2026). Watermark TIDAK "
    "dimajukan (tetap 132512564; gap ke head ~282.057 blok dan tumbuh). "
    "Route 5c: tanpa output scan baru (tidak ada ERC-20 backlog baru untuk di-shape-check run ini).")
snap["runNote2131_1110_discovery"] = (
    "Run 2131 discovery: subagent discovery TER-INTERUPSI (compaction) sebelum menulis discovery.json; parent "
    "merekonsiliasi dari artefak yang sudah ditulis. Sourcify feed 20 terbaru (verified 14:14-14:45Z), 6 "
    "di-shape-check: 1 agent-shaped BARU = SOLDERCATS 0x3d972e (SMITH template, freeMintX + AGENT_FREE_CAP; "
    "S1/S2 False sebagai sale - ini NFT, bukan sale), 1 market = 0xd35592ae (Alley Swap SOLDERCATS, 17 fns, "
    "bukan mint), 1 mint+agent tanpa free (0x7dc6b5...), 3 tanpa bentuk agent. Boltbook EN+ZH via curl langsung "
    "(45.383/45.616 byte): 11 alamat, semuanya dikenal/lama (Lanternfield, THYRK, FOSSIL + 8 alamat Sourcify "
    "verified 29 Okt/3 Nov atau unverified - bukan lead baru). SOLDERCATS BUKAN dari Boltbook (tidak disebut) dan "
    "BUKAN dari bridge (scan-bridge.json tidak berubah sejak 2026-11-08 18:21, 116 kontrak; tidak ada "
    "SOLDERCATS/EMBERANVIL di dalamnya). Sweep web/sosial + komplemen rute 6 (Odaily/PANews/Square/DappBay) TIDAK "
    "selesai karena interupsi - ulangi run berikut.")
snap["runNote2131_1110_binanceai"] = (
    "Run 2131 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (direct eth_call, blok 132794859). Status closed-refund-phase-2026-11-07; sudah dilaporkan "
    "sekali; tidak dilaporkan ulang. pending_claims kosong.")
snap["last_run_block"] = BLOCK
snap["last_run_wib"] = NOW
snap["last_run_note"] = snap["runNote2131_1110"]

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print("MERGE DONE. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})))
