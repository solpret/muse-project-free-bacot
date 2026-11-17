#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 19:01 WIB.
Reads run-2026-11-13-1901-verify.json + verify-boltbook.json + discovery.json,
updates onchain-snapshot.json (backup first). Apex STRONG-LEAD DIRECT MINT
executed this run (tx 0x206e2a70538f8705c3ebb2b26edb997f592cb4a5792912ccb0515e989c2018fa,
block 133349552, gas 181643, token #175, tier Epic). Read-only except snapshot.
"""
import json, shutil, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1901.bak")
ver = json.load(open(BASE + "run-2026-11-13-1901-verify.json"))
new = json.load(open(BASE + "run-2026-11-13-1901-verify-boltbook.json"))
dis = json.load(open(BASE + "run-2026-11-13-1901-discovery.json"))
BLOCK = ver.get("block")  # 133348427
BLOCK_NEW = new.get("block")  # 133349020
C = snap["contracts"]
TC = snap.setdefault("track_c", {})

def vws(reads, name):
    r = reads.get(name) or {}
    return (r.get("views") or {})

def note1901(c, text):
    c["runNote1901"] = text

# --- main verify targets ---
r = vws(ver["reads"], "OBFG")
if r.get("freeMinted") is not None:
    c = C["Obsidian Forge"] if "Obsidian Forge" in C else None
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["totalMinted"] = r.get("totalMinted")
        c["freeMinted"] = r.get("freeMinted"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): freeMinted 692->693/1230 = 56,3%% (+1, <20) velocity GAGAL; slot terbuka (freeAvailable=1); umur ~23 jam <24 jam, deadline 20:01 WIB 13 Nov; gate website tetap GAGAL (sudah dilaporkan 12 Nov). DIAM." % BLOCK)
    t = TC.get("OBFG")
    if t:
        t["totalSupply"] = r.get("totalSupply"); t["totalMinted"] = r.get("totalMinted")
        t["freeMinted"] = r.get("freeMinted"); t["freePct"] = round(693/1230*100, 1)
        t["lastReadBlock"] = BLOCK; t["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        t["runNote1901"] = "Run 1901: 692->693/1230 = 56,3% (+1), velocity GAGAL; umur ~23 jam <24 jam (deadline 20:01 WIB); gate tetap GAGAL; sudah dilaporkan. DIAM."

r = vws(ver["reads"], "Agentx")
if r.get("freeMinted") is not None:
    c = C.get("Agentx")
    if c:
        c["totalMinted"] = r.get("totalMinted"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalMinted 757 FLAT (+0) velocity GAGAL; free 757/1111 = 68,1%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); umur ~19,9 jam <24 jam, deadline 23:11 WIB 13 Nov; gate website tetap GAGAL (sudah dilaporkan 08:01 + hot-leg 08:29). DIAM." % BLOCK)

r = vws(ver["reads"], "AgentMuse")
if r.get("freeClaimed") is not None:
    t = TC.get("AgentMuse")
    if t:
        t["freeClaimed"] = r.get("freeClaimed"); t["lastReadBlock"] = BLOCK
        t["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        t["runNote1901"] = "Run 1901: freeClaimed 395->400/888 = 45,0% (+5, <20). <50% -> BUKAN kandidat. DIAM."

r = vws(ver["reads"], "AgentLabs")
if r.get("totalSpecimens") is not None:
    c = C.get("AgentLabs")
    if c:
        c["totalSpecimens"] = r.get("totalSpecimens"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSpecimens 2337->2348 (+11, 0,37/mnt vs prev 0,88 = 0,42x) velocity GAGAL; free%% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM." % BLOCK)

r = vws(ver["reads"], "Zero")
if r.get("freeMinted") is not None:
    c = C.get("Zero")
    if c:
        c["totalMinted"] = r.get("totalMinted"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalMinted 296 FLAT velocity GAGAL; free 296/500 = 59,2%%; slot TERBUKA (freeClaimed_user=0); umur ~11,2 jam <24 jam; website/X UNVERIFIED -> BUKAN kandidat, <70%% bukan strong lead. DIAM." % BLOCK)

r = vws(ver["reads"], "OLIVER")
if r.get("freeMinted") is not None:
    c = C.get("Oliver Agents")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSupply 1010->1012, freeMinted 960->962/1000 = 96,2%% (+2) velocity GAGAL; umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka. DIAM." % BLOCK)

r = vws(ver["reads"], "RoyalRush")
if r.get("freeMinted") is not None:
    c = C.get("Royal Rush Agents")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSupply 877->879, freeMinted 870->872/1000 = 87,2%% (+2) velocity GAGAL; umur TETAP UNVERIFIED + X UNVERIFIED walau free >70%% + slot terbuka. BUKAN strong lead/kandidat. DIAM." % BLOCK)

r = vws(ver["reads"], "Slate")
if r.get("freeMinted") is not None:
    c = C.get("Slate Insignia")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSupply 84->85, freeMinted 83->84/480 = 17,5%% (+1, <20) velocity GAGAL; umur ~3,4 jam; website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%%), BUKAN strong lead (<70%%). DIAM." % BLOCK)

r = vws(ver["reads"], "VioletWaybill")
if r.get("freeMinted") is not None:
    c = C.get("Violet Waybill")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSupply 110->113, freeMinted 109->112/1230 = 9,1%% (+3, <20) velocity GAGAL; umur ~2,3 jam; website/X UNVERIFIED, slot terbuka (costOf=0). BUKAN kandidat, BUKAN strong lead. DIAM." % BLOCK)

r = vws(ver["reads"], "MECHA")
if r.get("freeClaimed") is not None:
    c = C.get("MECHA")
    if c:
        c["freeClaimed"] = r.get("freeClaimed"); c["totalMinted"] = r.get("totalMinted")
        c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: freeClaimed 1933 FLAT (43,5%%). DIAM.")

r = vws(ver["reads"], "Pickgrid")
if r.get("freeMinted") is not None:
    c = C.get("Pickgrid")
    if c:
        c["freeMinted"] = r.get("freeMinted"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")

r = vws(ver["reads"], "BC1B")
if r.get("freeCount") is not None:
    c = C.get("BC1B/RESUME") or C.get("BC1B")
    if c:
        c["freeCount"] = r.get("freeCount"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: freeCount 469 FLAT (15,6%%). DIAM.")

r = vws(ver["reads"], "OUTY")
if r.get("freeSold") is not None:
    c = C.get("OUTY")
    if c:
        c["freeSold"] = r.get("freeSold"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: freeSold 35->37/1500 (+2); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")

for nm in ("PX24", "SKRR", "ME30", "CY24"):
    r = vws(ver["reads"], nm)
    if r.get("totalSupply") is not None:
        c = C.get(nm)
        if c:
            c["totalSupply"] = r.get("totalSupply"); c["lastReadBlock"] = BLOCK
            c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
            note1901(c, "Run 1901: totalSupply %s (PX24 524 FLAT, SKRR 516 FLAT, ME30 289 FLAT, CY24 462 FLAT); umur TETAP UNVERIFIED. DIAM." % r.get("totalSupply"))

r = vws(ver["reads"], "DragonAgent")
if r.get("totalSupply") is not None:
    c = C.get("DragonAgent") or C.get("DRAGON-0xad0d")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: totalSupply 981->983 (+2); umur TETAP UNVERIFIED. DIAM.")

r = vws(ver["reads"], "HIVE")
if r.get("totalSupply") is not None:
    c = C.get("HIVE Agents")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901 (blok %s): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM." % BLOCK)

r = vws(ver["reads"], "NOTV")
if r.get("totalMinted") is not None:
    c = C.get("NOTV")
    if c:
        c["totalMinted"] = r.get("totalMinted"); c["lastReadBlock"] = BLOCK
        c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
        note1901(c, "Run 1901: totalMinted MASIH 0 (FREE_SHARES 2000) - belum ada mint pertama walau freeStart 18:00 WIB sudah lewat. Umur launch TETAP UNVERIFIED. Bukan lead. DIAM.")

for nm in ("Mossbound", "Ochre", "JNTM"):
    r = vws(ver["reads"], nm)
    if r:
        key = {"Mossbound": "Mossbound Key", "Ochre": "Ochre Medallion", "JNTM": "JNTM"}.get(nm, nm)
        c = C.get(key)
        if c:
            c["lastReadBlock"] = BLOCK; c["lastReadWib"] = "2026-11-13 ~19:05 WIB"
            note1901(c, "Run 1901: SELLOUT terkonfirmasi ulang (Mossbound 325/325, Ochre 210/210, JNTM 1000/1000); sudah dilaporkan sekali sebelumnya -> TIDAK lapor ulang. DIAM.")

r = vws(ver["reads"], "BinanceAI-mint")
pc = snap.get("pending_claims", {}).get("binanceai.fun")
if r.get("launched") is not None and pc:
    pc["launched"] = r.get("launched"); pc["tokenClaimed_user"] = r.get("tokenClaimed_user")
    pc["isRefundPhase"] = r.get("isRefundPhase"); pc["failed"] = r.get("failed")
    pc["refundClaimed_user"] = r.get("refundClaimed_user")
    pc["lastReadWib"] = "2026-11-13 ~19:05 WIB"
    pc["runNote1901"] = "Run 1901: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM."

# --- verify-new targets (block 133349020) ---
r = new.get("CinderCrucible", {}).get("views", {}) if isinstance(new.get("CinderCrucible"), dict) else {}
if r.get("freeMinted") is not None:
    c = C.get("Cinder Crucible")
    if c:
        c["totalMinted"] = r.get("totalMinted"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK_NEW; c["lastReadWib"] = "2026-11-13 ~19:06 WIB"
        note1901(c, "Run 1901 (blok %s): totalMinted 66->81, freeMinted 81/325 = 24,9%% (+15, <20) velocity GAGAL; slot TERBUKA (freeAvailable=1, costOf=0); umur ~2,4 jam <24 jam. GATE WEBSITE TETAP GAGAL (sudah dilaporkan run 1801). TIDAK di-preview/TIDAK di-mint. saleEnd 1794739861 (konsisten dgn 1831). DIAM." % BLOCK_NEW)
    t = TC.get("Cinder Crucible") or TC.get("CinderCrucible")
    if t:
        t["totalMinted"] = r.get("totalMinted"); t["freeMinted"] = r.get("freeMinted")
        t["lastReadBlock"] = BLOCK_NEW; t["lastReadWib"] = "2026-11-13 ~19:06 WIB"

r = new.get("MossSignal", {}).get("views", {}) if isinstance(new.get("MossSignal"), dict) else {}
if r.get("totalSupply") is not None:
    c = C.get("Moss Signal")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["lastReadBlock"] = BLOCK_NEW
        c["lastReadWib"] = "2026-11-13 ~19:06 WIB"
        note1901(c, "Run 1901: totalSupply 771->780 (+9); 95,0%%+ INFERENSI total-supply, TANPA free counter; slot user TERBUKA (costOf=0); website TERVERIFIKASI; umur launch TETAP UNVERIFIED. BUKAN strong lead/kandidat. DIAM.")

r = new.get("AgentBubble", {}).get("views", {}) if isinstance(new.get("AgentBubble"), dict) else {}
if r.get("freeMinted") is not None:
    c = C.get("Agent Bubble")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["freeMinted"] = r.get("freeMinted")
        c["lastReadBlock"] = BLOCK_NEW; c["lastReadWib"] = "2026-11-13 ~19:06 WIB"
        note1901(c, "Run 1901: totalSupply 581->637, freeMinted 480->536/2222 = 24,1%% (+56, 1,87/mnt vs prev 1,96 = 0,95x) velocity GAGAL (<1,5x). Website TERVERIFIKASI. Umur TETAP UNVERIFIED. BUKAN kandidat (<50%%), BUKAN strong lead (<70%%). DIAM.")

r = new.get("Mihao", {}).get("views", {}) if isinstance(new.get("Mihao"), dict) else {}
if r.get("totalSupply") is not None:
    c = C.get("Mihao")
    if c:
        c["totalSupply"] = r.get("totalSupply"); c["lastReadBlock"] = BLOCK_NEW
        c["lastReadWib"] = "2026-11-13 ~19:06 WIB"
        note1901(c, "Run 1901: totalSupply 456->462 (+6, <20) velocity GAGAL; mintStart 14:15:55 WIB -> umur ~4,9 jam <24 jam TERVERIFIKASI; website TERVERIFIKASI; free%% UNVERIFIED (PRICE 0,0003 BNB berbayar); slot UNVERIFIED. BUKAN kandidat/strong lead. DIAM.")

# --- APEX: STRONG-LEAD DIRECT MINT EXECUTED ---
r = new.get("Apex", {}).get("views", {}) if isinstance(new.get("Apex"), dict) else {}
c = C.get("Apex")
if c:
    c["totalMinted"] = 177; c["freeMinted"] = 173; c["freePct"] = 86.5
    c["freeClaimed_user"] = 1; c["balanceOf_user"] = 1
    c["status"] = "minted-by-user-2026-11-13"
    c["mintTx"] = "0x206e2a70538f8705c3ebb2b26edb997f592cb4a5792912ccb0515e989c2018fa"
    c["mintBlock"] = 133349552; c["mintGas"] = 181643; c["mintTokenId"] = 175
    c["mintOrderId"] = "26111300002038154794"
    c["lastReadBlock"] = 133349552; c["lastReadWib"] = "2026-11-13 ~19:13 WIB"
    c["velocityLegPasses"] = False
    c["currentRatePerMin"] = 1.84; c["previousRatePerMin"] = 3.33
    c["rarity"] = {"tokenId": 175, "tier": "Epic", "background": "Magenta", "outfit": "Royal", "weapon": "Trident", "head": "Hood", "accessory": "Lantern", "power": 82, "source": "https://apex-nft.pages.dev/metadata/175"}
    c["marketplace"] = {"ownMarket": "0x5D4365534e7E87C93B891f53A63b82B5EfaE99bE", "fee": "2.5%", "minPrice": "0.001 BNB", "listedNow": 0, "escrowed": 0, "note": "Own market ADA (escrow, contract-matched) tapi 0 listing live / tanpa floor terbaca -> TIDAK auto-list (aturan post-mint: tanpa floor live = tidak listing). Element fallback manual saja (butuh connect wallet user + API key)."}
    c["audit"] = {"binance": "hasResult=false (TIDAK ADA HASIL, bukan pass)", "requestFile": "audit-1901-apex.json"}
    note1901(c, "Run 1901: STRONG LEAD -> DIRECT MINT BERHASIL. Kaki: umur TERVERIFIKASI (first-mint bound 1801, ~1,3 jam), free 167/200 = 83,5%% (>70%%) saat verify-new blok 133349020, slot TERBUKA (freeClaimed_user=0, balanceOf=0); website TERVERIFIKASI (apex-nft.pages.dev mencetak kontrak persis, dicek ulang run ini); X UNVERIFIED (opsional, tidak meng-gate). Gate + audit (Binance hasResult=false = tidak ada hasil, bukan pass) + quote segar (freeMinted 170/200, freeLeft 30, blok 133349496) + preview BERSIH (000000000, +1 ERC721 #175, tanpa authority/allowance/risk, requestId 5053b52fb9cc4e06868f5409cdb0d495) -> execute BROADCASTED tx 0x206e2a70538f8705c3ebb2b26edb997f592cb4a5792912ccb0515e989c2018fa, receipt status 1 blok 133349552 gas 181643, ownerOf(175)=user, balanceOf=1, freeClaimed=1, freeMinted 173/200. Rarity: Tier Epic (Power 82). Market: own market 0 listing -> TIDAK auto-list.")

# --- KOMA AGENT: age-excluded (sweep ZH baru) ---
TC["KOMA"] = {
    "sale": "0xef4882e029b8d58F81960c433D852a5b0A352965",
    "token": "0xef4882e029b8d58F81960c433D852a5b0A352965",
    "name": "Koma Agent",
    "status": "checked-age-excluded-2026-11-13",
    "website": "https://www.komaagent.fun/",
    "xHandle": "@KomaAgentID",
    "saleShapeNote": "S1/S2 BELUM terverifikasi penuh (view names non-standar: freeClaimed/freeSharesRemaining/freeLeft/freeAvailable/quote/agentIdRegistry semua None; totalMinted 517, totalSupply token 3,35e27) - TIDAK dilanjutkan karena umur gugur duluan.",
    "ageNote": "AGE-EXCLUDED: situs proyek menyatakan mint dibuka 2026-11-11 22:00 WIB (Beijing, UTC+8) + refund deadline 5 hari sesudahnya 2026-11-16 22:00 Beijing; umur saat run ~46,5 jam > 24 jam. TIDAK PERNAH dilaporkan sebelumnya (24-48 jam, belum pernah dilapor) -> DIAM per aturan.",
    "lastReadWib": "2026-11-13 ~19:20 WIB",
}

snap["runNote1901"] = "Run 1901: APEX STRONG-LEAD DIRECT MINT BERHASIL (tx 0x206e2a70538f8705c3ebb2b26edb997f592cb4a5792912ccb0515e989c2018fa, blok 133349552, gas 181643, token #175 Epic). 0 kandidat baru lain, 0 strong lead baru lain, 0 early lead baru, 0 track-C lead/kandidat baru. KOMA AGENT (sweep ZH baru) age-excluded ~46,5 jam, DIAM (belum pernah dilapor). OBFG deadline 20:01 WIB, AgentLabs 21:04 WIB, Agentx 23:11 WIB - belum lewat."
snap["runNote1901_scan"] = "Run 1901 scan leg FAST-FAIL: Ankr pre-flight TIMEOUT (bukan 401 kali ini - 'The read operation timed out'); outage Ankr sejak 2026-11-09 berlanjut. Watermark TETAP 132512564; gap ke head ~837.000 blok (head 133349496). Sudah dilaporkan 9 Nov, TIDAK lapor ulang. 5c dilewati (tanpa output scan). Sourcify feed GAGAL run ini (raw_len=0, fetch kosong) + hot-leg 1904 juga feed n=0; Boltbook EN 0 byte (fetch gagal) / ZH 43.211 B, 0 alamat baru. Bridge read-only: 116 kontrak, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan."
snap["last_run_wib"] = "2026-11-13 ~19:20 WIB"
snap["last_run"] = "2026-11-13T19:20+07:00"
snap["timestamp_wib"] = "2026-11-13 ~19:20 WIB"

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE OK: backup onchain-snapshot-2026-11-13-1901.bak; snapshot updated, Apex minted-by-user, KOMA age-excluded recorded.")
