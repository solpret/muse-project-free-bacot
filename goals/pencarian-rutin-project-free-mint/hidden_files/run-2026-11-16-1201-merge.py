#!/usr/bin/env python3
"""Merge run 2026-11-16 12:01 WIB reread into onchain-snapshot.json.
Fresh merge: values from run-2026-11-16-1201-reread.json + snapshot.
Interval 30.0 min vs run 1131 (blok 133864749 -> 133868584). 36/36 reads OK.
WOMEN NOT in ITEMS (sold out run 1131, removed from snapshot then).
XOR (Glyphs of Xor) is NOT merged here - its age walk is still running;
added by a separate update step after the walk finishes.
Read-only except the snapshot write + backup. No preview/mint."""
import json, shutil, re
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261116-1201")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-16-1201-reread.json"))
reads = r["reads"]; BLK = r["block"]; INTERVAL = 30.0
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
    entry["lastReadWib"] = "2026-11-16 ~12:01 WIB"
    if old_prim is not None and new_prim is not None:
        prev_rate = entry.get("currentRatePerMin")
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
        entry["runNote1201_1116"] = text
    else:
        log.append(f"NOTE-SKIP {name}: no entry")

vel = {}
for line in log:
    m = re.match(r"(\S+): (\d+)->(\d+) \(\+(-?\d+), ([\d.]+)/mnt vs prev (\S+) = (\S+)x\) vel=(\w+)", line)
    if m:
        vel[m.group(1)] = (int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5), m.group(6), m.group(7), m.group(8))
for n, (o, nw, d, rate, prev, ratio, v) in vel.items():
    log.append(f"VEL {n}: {o}->{nw} +{d} {rate}/mnt prev={prev} ratio={ratio}x vel={v}")

note("SPARKS", "Run 1201 (blok 133868584, interval 30,0 mnt vs run 1131): totalSupply 922->949 (+27, 0,900/mnt vs prev 0,333 = 2,70x, >=20 token) -> velocity LOLOS; free%/umur/website MASIH UNVERIFIED -> tetap early lead, TIDAK preview/mint.")
note("MORFO", "Run 1201 (blok 133868584): totalMinted 860->877 (+17, 0,567/mnt vs prev 0,533 = 1,06x, <20 token) -> velocity GAGAL.")
note("AgentNOVA", "Run 1201 (blok 133868584): totalSupply 652 FLAT -> velocity GAGAL.")
note("Bold Leonidas", "Run 1201 (blok 133868584): totalSupply 781->785 (+4, <20 token) -> velocity GAGAL; mintPriceFor(user,1)=0 (slot gratis TERBUKA), balanceOf(user)=0, mintOpen=1; free%/umur/website MASIH UNVERIFIED -> tetap early lead.")
note("Matrix Agents", "Run 1201 (blok 133868584): totalSupply 479->496 (+17, 0,567/mnt, <20 token) -> velocity GAGAL; anomali freeMinted (499) > totalSupply (496) BERLANJUT; freeClaimedByAgent(user)=0.")
note("Ledgera", "Run 1201 (blok 133868584): totalSupply 2692 FLAT, freeClaimed 2685/5000 = 53,7% - BUKAN kandidat/strong lead (velocity 0).")
note("CPASS", "Run 1201 (blok 133868584): totalMinted 1737 FLAT -> velocity GAGAL.")
note("HIVE", "Run 1201 (blok 133868584): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Zero", "Run 1201 (blok 133868584): totalSupply/freeClaimed GAGAL baca run ini (degradasi RPC, BUKAN nol); nilai lama dipertahankan, velocity TIDAK dihitung. balanceOf(user)=0.")
note("ALIEN", "Run 1201 (blok 133868584): totalSupply 0 TETAP, mintOpen=0 (BELUM DIBUKA), FREE_SUPPLY 1000/MAX_SUPPLY 1300, isFreePhase=1 -> tetap UPCOMING watchlist-only.")
note("WANGCAI", "Run 1201 (blok 133868584): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("YUANBAO", "Run 1201 (blok 133868584): totalSupply 189 FLAT (free pool habis tercatat sold-out-2026-11-14). DIAM.")
note("LumenFindings", "Run 1201 (blok 133868584): totalSpecimens 6222->6227 - counter spesimen eksperimen, BUKAN velocity mint (item age-excluded). DIAM.")
note("DogeRageFi", "Run 1201 (blok 133868584): totalMinted 226 FLAT, freeSupply 432 TETAP, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Umur presisi MASIH UNVERIFIED; gate website MASIH GAGAL -> watchlist-only, DIAM.")
note("ORBIT", "Run 1201 (blok 133868584): freeClaimed 292/888 TETAP, claimOpen 1, hasFreeClaimed(user)=0, umur UNVERIFIED -> watchlist-only, DIAM.")
note("RigForge", "Run 1201 (blok 133868584): freeSharesLeft 639, openedAt 0, freeClaimed 361 - DIAM.")
note("JADE", "Run 1201 (blok 133868584): totalSupply 191 FLAT (free pool tetap 0). DIAM.")
note("RAVE", "Run 1201 (blok 133868584): totalMinted 334 FLAT, freeMinted 334/3000 = 11,1% (free% kuota UNVERIFIED - tanpa FREE_SUPPLY view). DIAM.")
note("AGCLUB", "Run 1201 (blok 133868584): totalMinted 486 FLAT, freeMinted 486/888 = 54,7% (FREE_CAP 888), mintOpen 1, balanceOf(user)=0 -> velocity GAGAL (0).")
# Track-B binanceai.fun pending claim
ba = reads.get("BinanceAI-mint", {}).get("views") or {}
pc = s.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
for k in ("launched","failed","isRefundPhase","totalShares"):
    if ba.get(k) is not None: pc[k] = ba[k]
if ba.get("tokenClaimed_user") is not None: pc["tokenClaimed_user"] = ba["tokenClaimed_user"]
pc["lastReadWib"] = "2026-11-16 ~12:01 WIB"
pc["runNote1201"] = "Run 1201: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133868584) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
bmentry, _ = find_entry("BinanceAI-mint")
if bmentry is not None:
    for k in ("launched","failed","isRefundPhase","totalShares"):
        if ba.get(k) is not None: bmentry[k] = ba[k]
    bmentry["lastReadBlock"] = BLK; bmentry["lastReadWib"] = "2026-11-16 ~12:01 WIB"
# Agent Grove grove-check
gr = json.load(open(BASE + "run-2026-11-16-1201-grove-check.json"))
ge, _ = find_entry("Agent Grove")
if ge is not None:
    ge["runNote1201_1116"] = "Run 1201: grove-check (blok 133870861): freeOpen=0/false, freeClaimed(user)=0 -> MASIH BELUM DIBUKA, tetap upcoming watchlist-only. DIAM."
    ge["freeOpen"] = gr.get("freeOpen")
    ge["lastReadBlock"] = gr.get("block")
    ge["lastReadWib"] = "2026-11-16 ~12:01 WIB"
# Bridge comparison (read-only)
_br = json.load(open(BASE + "scan-bridge.json")).get("contracts", {})
_snap_addrs = { (v.get("address") or "").lower() for v in list(s.get("contracts", {}).values()) + list(s.get("track_c", {}).values()) if isinstance(v, dict) }
_br_addrs = { k.lower() for k in _br.keys() }
_missing = sorted(_br_addrs - _snap_addrs)
_disc = sum(1 for v in _br.values() if isinstance(v, dict) and v.get("same_owner_discarded"))
s["runNote1201_1116_bridge"] = f"Run 1201 bridge (read-only): {len(_br)} kontrak bridge, {len(_br_addrs & _snap_addrs)}/{len(_br)} sudah di snapshot, {len(_missing)} baru: {_missing if _missing else 'tidak ada'}, {_disc} same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["last_run_wib"] = "2026-11-16 ~12:01 WIB"
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("\n".join(log))
print("MERGE DONE")
