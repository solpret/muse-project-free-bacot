#!/usr/bin/env python3
"""Merge run 2026-11-16 12:31 WIB reread into onchain-snapshot.json + Lunar Atlas triage.
Interval 40.83 min (block timestamps: 133868584 ts 1794805539 -> 133874029 ts 1794807989 = 2450s).
36/36 reads OK. Velocity: Matrix PASSES (+39, 0.955/mnt vs prev 0.567 = 1.69x, >=20) but free% 53.8% <70%,
age UNVERIFIED, X unverified -> tetap early lead, TIDAK preview/mint. SPARKS +11 (<20) GAGAL.
Lunar Atlas (Boltbook tungquan42.ai /p/rXx-ioOMaTsX): AGE-EXCLUDED - first detected 2026-11-12 03:02 WIB
(monitor) -> umur ~4,4 hari > 24 jam. Belum pernah dilaporkan -> DIAM. On-chain: totalSupply 744,
MAX_SUPPLY 1115, costOf(user,1)=0, mintedBy(user)=0, mintsLeft(user)=10, mintOpen=1, price 0.00005 BNB.
tokenURI(1)=https://agent-cosmic-043-lunar-atlas.pages.dev/meta/1.json (metadata host, bukan bukti website
per putusan AgentPals); contractURI() kosong; registry bytes TIDAK ada di bytecode (agentIds/
agentTokenIdOf/mintedByAgent ada di ABI; gating Agent ID dikonfirmasi komentar mintitbaby.ai tapi
umur sudah menggugurkan - tidak dikejar lebih jauh). Sourcify exact_match, verifiedAt 2026-11-10T02:51:45Z.
SAMO 0xf62c... (Boltbook audit post, token ERC-20, counter flat) BUKAN lead - log only, tanpa entri snapshot.
Read-only except the snapshot write + backup. No preview/mint."""
import json, shutil, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1231")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1231-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 40.83
PRIMARY = {"AGCLUB":"totalMinted","MORFO":"totalMinted","NOISE":"totalMinted","RaceAgents":"totalSupply",
 "Zero":"totalMinted","HIVE":"totalSupply",
 "AgentNOVA":"totalSupply","SPARKS":"totalSupply","WANGCAI":"totalSupply",
 "YUANBAO":"totalSupply","PX24":"totalSupply","Zephyra":"totalMinted","LumenFindings":"totalSpecimens",
 "Pengu":"totalMinted","CPASS":"totalMinted","ORBIT":"totalSupply","TrashBandits":"totalMinted",
 "SKRR":"totalSupply","REOPIR":"totalSupply","FrieAgent-B751":"totalSupply","FrieAgent-c64d":"totalSupply",
 "Ledgera":"totalSupply","MAMI":"totalSupply","INKI":"totalSupply","HashcatDepot":"totalSupply",
 "OTV":"totalSupply","RAVE":"totalMinted","HANAMI":"totalSupply","CosmicSentinel":"totalSupply",
 "Matrix Agents":"totalSupply","Bold Leonidas":"totalSupply","ALIEN":"totalSupply","JADE":"totalSupply"}
COPY = ["totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","FREE_CAP","FREE_MAX",
 "MAX_SUPPLY","mintOpen","mintStart","isFreePhase","balanceOf_user","freeRemaining",
 "freeClaimed_user","freeUsed_user","mintedBy_user","hasAgentId_user","holdsAgentId_user",
 "priceFor_user","priceFor_user_1","mintedByWallet_user","paused","TOKEN_PRICE","remainingSupply",
 "mintPriceFor_user_1","cost_user_1","freeMintedPerWallet_user","mintedPerWallet_user",
 "totalSpecimens","currentExperiment","genesisStart","genesisOpen","mintsBy_user","mintCountOf_user",
 "freeSharesLeft","openedAt","freeBooked_user","claimOpen","hasFreeClaimed_user","mintsLeft",
 "FREE_MINT_CAP","freeMintsLeft","PRICE","paidMinted","mintPrice","freeClaimedByAgent_masgayut",
 "freeClaimedByAgent_masgayut_ai","freeSupply","maxSupply","hasClaimedFree_user","mintEnd","mintEnded",
 "PAID_PRICE","PAID_SUPPLY"]
# Prev-interval (run 1201) rates from run-1201 runlog, for items whose snapshot rate field is stale (0.0)
PREV_RATE_OVERRIDE = {"SPARKS": 0.900, "MORFO": 0.567, "Bold Leonidas": 0.133}
def find_entry(name):
    if name in s.get("contracts", {}): return s["contracts"][name], "contracts"
    if name in s.get("track_c", {}): return s["track_c"][name], "track_c"
    return None, None
log=[]
for name, prim in PRIMARY.items():
    rd = reads.get(name)
    entry, where = find_entry(name)
    if rd is None or entry is None:
        log.append(f"{name}: SKIP (read={rd is not None}, entry={where})"); continue
    views = rd.get("views") or {}
    old_prim = entry.get(prim)
    new_prim = views.get(prim)
    for k in COPY:
        if k in views and views[k] is not None:
            entry[k] = views[k]
    entry["lastReadBlock"] = BLK
    entry["lastReadWib"] = "2026-11-16 ~12:31 WIB"
    if old_prim is not None and new_prim is not None:
        prev_rate = entry.get("currentRatePerMin")
        if not prev_rate:
            prev_rate = PREV_RATE_OVERRIDE.get(name)
        d = new_prim - old_prim
        rate = d / INTERVAL
        ratio = (rate / prev_rate) if prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and d >= 20)
        entry["previousTotalSupply"] = old_prim
        entry["mintedInInterval"] = d
        entry["intervalMinutes"] = INTERVAL
        entry["previousRatePerMin"] = prev_rate
        entry["currentRatePerMin"] = rate
        entry["velocityRatio"] = ratio
        entry["velocityLegPasses"] = vel
        log.append(f"{name}: {old_prim}->{new_prim} (+{d}, {rate:.3f}/mnt vs prev {prev_rate} = {ratio if ratio is None else round(ratio,2)}x) vel={vel}")
    else:
        log.append(f"{name}: {prim} new={new_prim} old={old_prim} (uncomparable; old values kept)")

def note(name, text):
    entry, where = find_entry(name)
    if entry is not None:
        entry["runNote1231_1116"] = text
    else:
        log.append(f"NOTE-SKIP {name}: no entry")

note("SPARKS", "Run 1231 (blok 133874029, interval 40,83 mnt vs run 1201): totalSupply 949->960 (+11, 0,269/mnt vs prev 0,900 = 0,30x, <20 token) -> velocity GAGAL (run 1201 sempat LOLOS +27); free%/umur/website MASIH UNVERIFIED -> tetap early lead, TIDAK preview/mint.")
note("MORFO", "Run 1231 (blok 133874029): totalMinted 877->880 (+3, 0,073/mnt vs prev 0,567 = 0,13x, <20 token) -> velocity GAGAL.")
note("AgentNOVA", "Run 1231 (blok 133874029): totalSupply 652 FLAT -> velocity GAGAL.")
note("Bold Leonidas", "Run 1231 (blok 133874029): totalSupply 785->791 (+6, 0,147/mnt vs prev 0,133 = 1,10x, <20 token) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.")
note("Matrix Agents", "Run 1231 (blok 133874029): totalSupply 496->535 (+39, 0,955/mnt vs prev 0,567 = 1,69x, >=20 token) -> velocity LOLOS pertama kalinya; TAPI freeMinted 538/1000 = 53,8% (<70% ambang strong lead), umur MASIH UNVERIFIED, X unverified -> tetap early lead, BUKAN kandidat/strong lead, TIDAK preview/mint. Anomali freeMinted (538) > totalSupply (535) BERLANJUT; freeClaimedByAgent(user)=0.")
note("Ledgera", "Run 1231 (blok 133874029): totalSupply 2692 FLAT, freeClaimed 2685/5000 = 53,7% - BUKAN kandidat/strong lead (velocity 0).")
note("CPASS", "Run 1231 (blok 133874029): totalMinted 1737 FLAT -> velocity GAGAL.")
note("HIVE", "Run 1231 (blok 133874029): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Zero", "Run 1231 (blok 133874029): totalSupply/freeClaimed GAGAL baca run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.")
note("ALIEN", "Run 1231 (blok 133874029): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.")
note("WANGCAI", "Run 1231 (blok 133874029): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("YUANBAO", "Run 1231 (blok 133874029): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("LumenFindings", "Run 1231 (blok 133874029): totalSpecimens 6227->6229 - counter spesimen eksperimen, BUKAN velocity mint (item age-excluded). DIAM.")
note("DogeRageFi", "Run 1231 (blok 133874029): totalMinted (wei-scaled) +1.500 token, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL -> watchlist-only, DIAM.")
note("ORBIT", "Run 1231 (blok 133874029): freeClaimed 292->293/888, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
note("RigForge", "Run 1231 (blok 133874029): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.")
note("JADE", "Run 1231 (blok 133874029): totalSupply 191 FLAT (free pool tetap 0). DIAM.")
note("RAVE", "Run 1231 (blok 133874029): totalMinted 334 FLAT, freeMinted 334/3000 = 11,1% (free% kuota UNVERIFIED - tanpa FREE_SUPPLY view). DIAM.")
note("AGCLUB", "Run 1231 (blok 133874029): totalMinted 486 FLAT, freeMinted 486/888 = 54,7% (FREE_CAP 888), mintOpen 1, balanceOf(user)=0 -> velocity GAGAL (0).")
# RigForge / DogeRageFi field copy (track_c, not in PRIMARY)
for nm, fields in (("RigForge", ["freeSharesLeft","openedAt","freeClaimed","freeBooked_user"]),
                   ("DogeRageFi", ["totalMinted","freeSupply","maxSupply","mintOpen","mintedBy_user","balanceOf_user"])):
    rd = reads.get(nm); entry, where = find_entry(nm)
    if rd is not None and entry is not None:
        views = rd.get("views") or {}
        for k in fields:
            if views.get(k) is not None: entry[k] = views[k]
        entry["lastReadBlock"] = BLK
        entry["lastReadWib"] = "2026-11-16 ~12:31 WIB"
    else:
        log.append(f"TRACKC-SKIP {nm}: read={rd is not None} entry={where}")
# Track-B binanceai.fun pending claim
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~12:31 WIB"
pc["runNote1231"] = "Run 1231: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133874029) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~12:31 WIB"
# Agent Grove grove-check
gr = json.load(open(BASE + "run-2026-11-16-1231-grove-check.json"))
ge, _ = find_entry("Agent Grove")
if ge is not None:
    ge["runNote1231_1116"] = "Run 1231: grove-check (blok 133874964): freeOpen=0/false, freeClaimed(user)=0 -> MASIH BELUM DIBUKA, tetap upcoming watchlist-only. DIAM."
    ge["freeOpen"] = gr.get("freeOpen")
    ge["lastReadBlock"] = gr.get("block")
    ge["lastReadWib"] = "2026-11-16 ~12:31 WIB"
# Lunar Atlas - new age-excluded entry
s["contracts"]["Lunar Atlas"] = {
    "address": "0x6b2bc86427697c850ee661bb480560f068e3ac8d",
    "name": "Lunar Atlas", "symbol": "",
    "status": "checked-age-excluded-2026-11-16",
    "totalSupply": 744, "MAX_SUPPLY": 1115, "MAX_PER_WALLET": 10,
    "mintOpen": 1, "price": 50000000000000,
    "costOf_user_1": 0, "mintedBy_user": 0, "mintsLeft_user": 10, "balanceOf_user": 0,
    "freePct": None,
    "freePctNote": "UNVERIFIED: tanpa view freeSupply/freeClaimed/freeMinted; totalSupply 744 mencampur free-first-mint + paid (price 0,00005 BNB); klaim post 744/1139 (65,3%) tidak cocok dengan MAX_SUPPLY on-chain 1115 (koreksi komentar mintitbaby.ai: 371 slot tersisa, bukan 395).",
    "firstDetectedWib": "2026-11-12 03:02 WIB",
    "firstDetectedSource": "Boltbook b/alpha: tungquan42.ai /p/rXx-ioOMaTsX (recheck 12:39 WIB 16 Nov; 'Phat hien lan dau: 2026-11-12 03:02 (monitor)')",
    "ageHoursAtRun": "~105",
    "tokenURI_1": "https://agent-cosmic-043-lunar-atlas.pages.dev/meta/1.json",
    "contractURI": None,
    "registryBytesInCode": False,
    "agentShapeNote": "ABI: agentIds/agentTokenIdOf/mintedByAgent + mint/mintWithAgentTokenId/costOf; registry 0x60B9...022F TIDAK ada di bytecode (eth_getCode); gating Agent ID dikonfirmasi komentar mintitbaby.ai (mint(1) value 0 sims PASS dari wallet Agent ID, revert dari plain wallet) - tidak dikejar lebih jauh karena umur sudah menggugurkan.",
    "website": None,
    "gate": "age-excluded (website tidak dicek - umur menggugurkan)",
    "xVerified": False,
    "source": "Boltbook b/alpha: tungquan42.ai /p/rXx-ioOMaTsX",
    "lastReadWib": "2026-11-16 ~12:31 WIB",
    "lastReadBlock": 133874029,
    "runNote1231_1116": "Run 1231: BARU dari Boltbook. totalSupply 744, MAX_SUPPLY 1115, costOf(user,1)=0, mintedBy(user)=0, mintsLeft(user)=10, mintOpen=1, Sourcify exact_match (verifiedAt 2026-11-10T02:51:45Z). TAPI umur >24 jam: first detected monitor 2026-11-12 03:02 WIB (~105 jam) -> AGE-EXCLUDED, diam (belum pernah dilaporkan).",
}
# Bridge comparison (read-only)
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1231_1116_bridge"] = f"Run 1231 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["runNote1231_1116"] = ("Run 1231 (12:31 WIB): re-read 36/36 OK blok 133874029 (76,8 dtk, interval 40,83 mnt vs run 1201 dari timestamp blok). "
 "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
 "Velocity: Matrix LOLOS (+39, 0,955/mnt vs prev 0,567 = 1,69x, >=20) TAPI free% 53,8% <70% + umur UNVERIFIED + X unverified -> tetap early lead, TIDAK preview/mint; "
 "SPARKS +11 (0,30x, <20) GAGAL (run 1201 sempat lolos); MORFO +3 GAGAL; Bold Leonidas +6 GAGAL; sisanya 0/flat. "
 "BARU dicek run ini: Lunar Atlas (totalSupply 744, MAX_SUPPLY 1115, costOf(user,1)=0, TAPI first detected 12 Nov 03:02 WIB ~105 jam -> AGE-EXCLUDED, diam); "
 "SAMO 0xf62c... (post audit token ERC-20, bukan free mint -> bukan lead, log only). "
 "Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund). ALIEN + Agent Grove masih BELUM DIBUKA. "
 "Boltbook EN 200 (45.762 byte) / ZH 200 (46.019 byte): 6/6 alamat, 3 'baru' (1 kontrak riil = Lunar Atlas; 1 audit token SAMO; 1 tx hash Agent Muse). "
 "Sweep EN+ZH: hanya proyek lama (Meow Cards, Agentic Gangster, RIGBYPASS, AGENT COSMOS, First-Dollar Grove, Agent Zet free habis, LeadLoop/NEXUS CORE 25 Okt, Subsonic/BNBmeme 26 Okt). "
 "Odaily newsflash 12:52 WIB: 0 kata 'agent'. Scan leg FAST-FAIL (Ankr 401, 1,76 dtk); watermark TETAP 132512564 (head 133874069, gap 1.361.505). "
 "Sourcify 10 terbaru: 0 S1/S2 (6 IncompleteRead, semua retry via curl OK). Bridge 116/116 sudah di snapshot, 0 baru. Verdict akhir: DIAM (tidak ada laporan chat).")
s["last_run_note"] = ("Run 1231: DIAM - 0 kandidat/strong/early/track-B/track-C baru. Matrix velocity lolos tapi free%/umur/X belum lolos. "
 "Lunar Atlas age-excluded (first detected 12 Nov). Ankr 401 berlanjut; watermark scan tertahan di 132512564.")
s["last_run_wib"] = "2026-11-16 ~12:31 WIB"
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
