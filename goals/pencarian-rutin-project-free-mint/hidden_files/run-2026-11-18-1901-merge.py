#!/usr/bin/env python3
"""Merge run 2026-11-18 19:01 WIB re-read into onchain-snapshot.json (lean merge).
Reread via Quicknode tunnel: 291 calls, 0 chunk errors. Block 134309450,
interval ~32,2 mnt vs 1831 (4291 blok x 0,45 dtk).
Outcome: 0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU,
0 track-B dibuka, 0 track-C lead BARU. QUBITFOX (Boltbook baru) age-excluded
~7 hari, DIAM (belum pernah dilaporkan). AONE track-C: freeMinted 4305 -> 5959
(minted-by-user, kuota user 0). Read-only except snapshot. None/err values
NEVER overwrite."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1901-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1831-reread.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~19:01 WIB"
BLOCK = reread["block"]; PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass = [], [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW; e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (not in snapshot): {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1901_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1901 (blok {BLOCK}, interval ~32,2 mnt vs 1831): freeMinted/totalMinted 362->365 (+3, <20) -> velocity GAGAL. free 365/999 = 36,5% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~22,5 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1901 (blok {BLOCK}): totalSupply 777->782 (+5), freeLeft 334->329 (FREE_SUPPLY 1111, inferred free 782/1111 = 70,4% - MELEWATI 70% secara INFERENSI SAJA, bukan free counter terverifikasi, jadi BUKAN strong lead; umur + website tetap UNVERIFIED). quote(user,1)=0, freeMintedByWallet 0, balance 0 -> slot TERBUKA. Velocity GAGAL (+5 <20). Tetap EARLY LEAD. (Hot-leg 1854 sudah mencatat inferred ~70%.)")
note("DGF CARD", f"Run 1901 (blok {BLOCK}): totalMinted 1652->1655 (+3) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("AgentNOVA", f"Run 1901 (blok {BLOCK}): totalSupply 778->786 (+8, kenaikan terbesar run ini) -> velocity GAGAL (+8 <20). Bukan kandidat.")
note("AgentBubble", f"Run 1901 (blok {BLOCK}): freeMinted 1905->1906 (+1), totalSupply 2050->2051 (+1). free 1906/2222 = 85,8% FLAT-ish. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead. Velocity GAGAL.")
note("Lumenhold", f"Run 1901 (blok {BLOCK}): freeClaimed 1256/1500 = 83,7% FLAT, totalSupply 1261 FLAT -> velocity GAGAL. Free% >70% TAPI umur UNVERIFIED -> BUKAN strong lead.")
note("Ledgera", f"Run 1901 (blok {BLOCK}): freeClaimed 2703/5000 = 54,1% FLAT, totalSupply 2710 FLAT -> velocity GAGAL. Umur/website/X UNVERIFIED -> BUKAN kandidat dan BUKAN strong lead (54,1% <70%).")
note("Vitaliq Scans", f"Run 1901 (blok {BLOCK}): totalSupply revert (fungsi tidak ada, sama seperti 1831), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~12 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balance 0. Free%/website UNVERIFIED. Tetap EARLY LEAD, TIDAK di-preview/di-mint.")
note("HIVE Agents", f"Run 1901 (blok {BLOCK}): totalSupply 1264 FLAT vs 1831, balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1901 (blok {BLOCK}): freeCatsClaimed 100/100 SOLD OUT (sudah diketahui). DIAM.")
note("EIM", f"Run 1901 (blok {BLOCK}): totalMinted 768->771 (+3 vs 1831) -> velocity GAGAL (<20). Bukan kandidat.")
note("PunchCard", f"Run 1901 (blok {BLOCK}): totalMinted 1350->1352 (+2), freeMinted 1328->1330, slot TERBUKA -> velocity GAGAL. Umur/website UNVERIFIED. Bukan kandidat.")

# ---- Boltbook-new triage: QUBITFOX 0x7a23 (age-excluded ~7 hari) ----
snap.setdefault("contracts", {})["QUBITFOX"] = {
    "address": "0x7a2381308b2425d773713a6205732ee8310a9b83",
    "name": "QUBITFOX",
    "symbol": "KITSUNE",
    "status": "checked-not-lead-age-excluded-2026-11-18",
    "totalSupply": None,
    "lastReadWib": NOW,
    "lastReadBlock": BLOCK,
    "note": ("Run 1901 Boltbook EN+ZH BARU vs snapshot (2 post independen, ziwbly.ai 19:12 WIB + vainazmul.ai 19:08 WIB, "
        "angka cocok persis): totalSupply 504/3333, firstFreeUsed 503/2000 (25,2% <50% kandidat dan <70% strong lead), "
        "paidMinted 1, mintStart 2026-11-11 19:40 WIB, mintEnd 1795005623 = 2026-11-18 19:40:23 WIB (konversi date -d terverifikasi) "
        "-> umur ~7 HARI, AGE-EXCLUDED (>=24 jam, belum sold out). Pace ~4/jam -> velocity GAGAL. "
        "Bacaan RPC sendiri GAGAL (Quicknode tunnel timeout 2x batch + 1 triase sekuensial dimatikan setelah ~8 mnt; egress degradasi pasca-run utama), "
        "jadi angka di atas dari 2 post Boltbook yang saling menguatkan, BUKAN bacaan RPC sendiri - dicatat sebagai caveat. "
        "Sourcify v2 404 untuk kontrak ini (klaim post 'exact_match, verified 2026-11-11' TIDAK terkoroborasi). Website/X TIDAK dicek (moot: umur gugur duluan). "
        "Belum pernah dilaporkan -> DIAM sesuai aturan (item >=24 jam yang belum pernah dilaporkan diam). Bukan lead/kandidat, TIDAK di-preview/di-mint."),
}

# ---- AONE track-C update ----
aone = snap.setdefault("track_c", {}).get("AONE")
if isinstance(aone, dict):
    aone["freeMinted"] = 5959
    aone["freeRemaining"] = 4041
    aone["lastReadWib"] = NOW
    aone["note1901"] = ("Run 1901 (blok 134309450): freeMinted 4305 -> 5959 (+1654 dalam ~30 mnt, ~55/mnt - pool menguras cepat), "
        "FREE_TOTAL 10000, tersisa 4041. Kuota user SUDAH 0 (minted-by-user 18:17 WIB, hero #3330/#3331). Tidak ada eksekusi ulang. DIAM.")
    print("AONE updated: freeMinted 5959, freeRemaining 4041")
else:
    print("AONE MISSING from track_c!")

# ---- Track-B pending: binanceai.fun (re-read via leg4) ----
bc = snap.setdefault("pending_claims", {}).get("binanceai.fun")
if isinstance(bc, dict):
    bc["lastReadWib"] = NOW
    bc["runNote1901"] = ("Run 1901: launched=0, failed=1, tokenClaimed(user)=0 (blok 134309450) - tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund 2026-11-02). DIAM.")
    print("binanceai note updated")

snap["last_run_wib"] = NOW
snap["last_run"] = ("free-mint-search 2026-11-18 19:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, "
    "0 track-C lead; QUBITFOX (Boltbook baru) age-excluded ~7 hari - DIAM (belum pernah dilaporkan); "
    "STOCK AGENT inferred free 70,4% (bukan counter terverifikasi, umur unverified) - tetap EARLY LEAD, bukan strong lead; "
    "PUNNY 36,5%, deadline 24 jam 20:32 WIB hari ini; AONE freeMinted 5959/10000, kuota user 0.")
snap["runNote1901_1118"] = (
    f"Run 1901 (blok {BLOCK}, interval ~32,2 mnt vs 1831): "
    "0 kandidat baru, 0 strong lead baru/promosi, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead BARU. "
    "Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (30,9 dtk); watermark TIDAK maju. "
    "Reread Quicknode 291 calls, 0 chunk error; elapsed run 734,3 dtk. "
    "Velocity: TIDAK ADA yang lolos (maks +8 AgentNOVA, +5 STOCK, +3 DGF/EIM/MORFO/Foundry Faces, +2 AgentEcho/PunchCard/REOPIR/SPARKS/Stromboat; semua <20 token). "
    "PUNNY 365/999 = 36,5% (<50%), umur terverifikasi ~22,5 jam (deadline 24 jam 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    "STOCK AGENT inferred 782/1111 = 70,4% (INFERENSI totalSupply, bukan free counter terverifikasi; umur + website UNVERIFIED) -> tetap EARLY LEAD, BUKAN strong lead. "
    "Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 1906/2222 = 85,8%, Lumenhold 1256/1500 = 83,7%. "
    "Ledgera 54,1% FLAT, Matrix 635/1000 = 63,5% FLAT, AGCLUB 59,5% FLAT, RAVE 12,4%. "
    "QUBITFOX (Boltbook baru, 0x7a23): firstFreeUsed 503/2000 = 25,2%, mintStart 11 Nov 19:40 WIB -> umur ~7 hari, AGE-EXCLUDED, DIAM (belum pernah dilaporkan); "
    "bacaan RPC sendiri gagal (Quicknode timeout pasca-run), angka dari 2 post Boltbook yang cocok persis + konversi mintEnd 1795005623 = 19:40:23 WIB; Sourcify v2 404 (klaim exact_match tidak terkoroborasi). "
    "AONE track-C: freeMinted 4305 -> 5959 (+1654/~30 mnt), tersisa 4041, kuota user 0 (minted-by-user 18:17 WIB). DIAM. "
    "Boltbook EN+ZH segar (44.968/43.270 byte, HTTP 200): 6 alamat, 1 baru vs snapshot (QUBITFOX, di atas); lainnya dikenal (LumenFindings age-excluded, BoltRewards infra, BOLT token, LIFTDAEMON age-excluded, SnakeAgent age-excluded). "
    "Sourcify feed: 20 alamat, top verifiedAt 2026-11-18T12:13:45Z; 20 baru di-shape-check, 0 S1/S2 (1 agent_ref=true tanpa mint/quote/free views: 0x5f82). "
    "Sweep EN+ZH (browser.search): 0 proyek segar baru - hanya proyek lama yang dikenal (Oathbots age-excluded, Agentic Gangster free-pool-exhausted, First-Dollar Grove age-excluded, AGENT COSMOS 13 hari). "
    "Bridge read-only: 116 kontrak, 0 baru, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan. "
    "BinanceAI pending: launched=0, failed=1, tokenClaimed(user)=0 - tetap pending/refund, DIAM. "
    "DIAM (tidak ada laporan ke chat utama)."
)
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
