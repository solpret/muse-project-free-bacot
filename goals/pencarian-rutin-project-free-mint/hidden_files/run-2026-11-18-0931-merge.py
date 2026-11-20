#!/usr/bin/env python3
"""Merge run 2026-11-18 09:31 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
Velocity computed vs run 0901 (block 134228447 -> 134232346, ~29.2 min)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-0931-reread.json"))
reads = reread["reads"]
NOW = "2026-11-18 ~09:31 WIB"
BLOCK = reread["block"]
PREV_BLOCK = 134228447
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

def upd(name, fields):
    e = snap["contracts"].get(name)
    if e is None:
        _a = reads.get(name, {}).get("address", "")
        _k = addr2key.get(_a.lower()) if isinstance(_a, str) else None
        if _k: e = snap["contracts"][_k]
    if e is None:
        print("MISS", name); return None
    v = reads.get(name, {}).get("views", {})
    for f in fields:
        val = v.get(f)
        if isinstance(val, int): e[f] = val
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK
    return e

FIELDS = {
 "HIVE Agents": ["totalSupply","balanceOf_user"],
 "Bubblebruin": ["totalSupply","freeClaimed","balanceOf_user"],
 "CAT402": ["freeCatsClaimed"],
 "JADE": ["freeClaimed","totalSupply","mintOpen","mintedBy_user","balanceOf_user"],
 "Agent Bubble": ["freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"],
 "DRAGON": ["freeMinted","totalMinted","balanceOf_user"],
 "Matrix Agents": ["freeMinted","freeRemaining","totalSupply","mintOpen"],
 "AGCLUB": ["totalMinted","freeMinted","FREE_CAP","mintOpen","balanceOf_user"],
 "BNBG": ["totalMinted"],
 "SPARKS": ["totalSupply"],
 "Ledgera": ["freeClaimed","totalSupply","mintOpen","freeUsed_user","balanceOf_user"],
 "BoldLeonidas": ["totalSupply","mintOpen","balanceOf_user"],
 "RaceAgents": ["totalSupply","freeMinted","mintOpen"],
 "CPASS": ["totalMinted","mintOpen","balanceOf_user"],
 "REOPIR": ["freeClaimed","totalSupply","mintOpen"],
 "RAVE": ["totalMinted","freeMinted","mintOpen"],
 "MORFO": ["totalMinted","mintOpen"],
 "PIXELFROGS": ["totalSupply","freeMinted","freeLeft","mintOpen","freeClaimed_user"],
 "Flare-bd6f": ["totalSupply"],
 "PunchCard": ["totalSupply","totalMinted","freeMinted","paidMinted","MAX_SUPPLY","mintOpen","mintPriceFor_user_1","mintedCount_user","balanceOf_user"],
 "XCOPY": ["totalSupply","totalMinted"],
 "ARKYN": ["totalMinted"],
 "Mine Card": ["totalSupply","totalMinted"],
 "ALIEN": ["totalSupply"],
 "Kitebots": ["totalSupply","freeMinted"],
 "Everything Is Mine (EIM)": ["totalMinted","mintOpen"],
 "Lumenhold": ["totalSupply","freeClaimed"],
 "PXIO Miners": ["totalSupply"],
 "FrieAgent-B751": ["totalSupply"],
 "FrieAgent-c64d": ["totalSupply"],
 "Abyssora": ["totalSupply"],
 "HANAMI": ["totalSupply","freeMinted"],
 "Zephyra": ["totalMinted"],
 "AgentNOVA": ["totalSupply"],
 "ONI": ["totalMinted","totalSupply"],
 "HAPPE": ["totalMinted","freeMinted"],
 "Kryntar": ["totalMinted"],
 "Pengu": ["totalMinted","freeMinted"],
 "STOCK AGENT": ["totalSupply","freeLeft","FREE_SUPPLY","MAX_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user"],
 "THYRK": ["totalSupply","freeMinted","MAX_SUPPLY","freeUsed_user","balanceOf_user"],
 "ADRAW": ["freeMinted","balanceOf_user","hasClaimedFree_user"],
 "AgentEcho": ["totalSupply","mintOpen","MAX_SUPPLY","AGENT_ID","mintedBy_user","balanceOf_user"],
 "ARKT": ["totalSupply","totalMinted","MAX_SUPPLY","agentId","hasClaimed_user","balanceOf_user"],
 "Stromboat": ["totalMinted","freeMinted","paidMinted","mintOpen","freeMintedBy_user","balanceOf_user"],
 "Kageveil Genesis": ["totalSupply","normalMinted","mintOpen","mintClosed","balanceOf_user"],
 "Foundry Faces": ["totalMinted"],
 "Compasyn": ["totalSupply","freeClaimed","mintedBy_user","balanceOf_user"],
 "ARKT-claim-62a7": ["totalSupply","totalMinted","paused","hasClaimed_user"],
}
for n, fs in FIELDS.items():
    upd(n, fs)

# velocity notes for the two velocity-passers + key movers
snap["contracts"]["SPARKS"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}, interval ~29,2 mnt vs run 0901): totalSupply 1125->1167 (+42, 1,436/mnt vs prev 0,057 = 25,05x) -> velocity LOLOS (>=1,5x DAN >=20 token). TAPI TIDAK promosi: free% UNVERIFIED (semua free view freeMinted/freeClaimed/freeLeft/FREE_SUPPLY/freeSupply/quote/cost revert; probe segar run ini), umur peluncuran UNVERIFIED (tanpa stated launch time di snapshot), slot user UNVERIFIED (mintedBy/freeMintedByWallet revert, balanceOf(user)=0). Bukan kandidat, bukan strong lead. Tetap watchlist-only.")
snap["contracts"]["Everything Is Mine (EIM)"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}, interval ~29,2 mnt vs run 0901): totalMinted 630->650 (+20, 0,684/mnt vs prev 0,100 = 6,84x) -> velocity LOLOS (>=1,5x DAN >=20 token, tepat di ambang). TAPI TIDAK promosi: free% UNVERIFIED (semua free view revert; total 650/8888 = 7,3% total supply, jauh di bawah 50%), umur UNVERIFIED, X unverified, slot user UNVERIFIED (balanceOf(user)=0, mintedBy(user)=0). Early lead sudah dilaporkan sekali 17 Nov. Bukan kandidat, bukan strong lead. Tetap early-lead-reported.")
snap["contracts"]["STOCK AGENT"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): totalSupply 624->641 (+17, 0,581/mnt vs prev 0,331 = 1,75x) -> velocity GAGAL (<20 token). Free inferred 641/1111 = 57,7%% (freeLeft 470) - di atas 50%% kandidat TAPI di bawah 70%% strong lead; umur UNVERIFIED; website gate BELUM terverifikasi. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat, bukan strong lead. Tetap early-lead-reported-2026-11-18-0031.")
snap["contracts"]["Agent Bubble"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): freeMinted 1888/2222 = 85,0%% (>70%%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 2033, balanceOf(user)=0. Tetap watchlist-only.")
snap["contracts"]["Lumenhold"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): freeClaimed 1252/1500 = 83,5%% (>70%%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply flat 1257. Tetap watchlist-only-age-unverified.")
snap["contracts"]["Matrix Agents"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): freeMinted 611/1000 = 61,1%% (<70%%), totalSupply 607->608 (+1) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap early-lead-reported-2026-11-15.")
snap["contracts"]["AGCLUB"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): freeMinted 527/888 = 59,3%% (<70%%), totalMinted flat 527 -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat. Tetap watchlist-only.")
snap["contracts"]["Mine Card"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): totalSupply 1212->1230 (+18, 0,616/mnt vs prev 1,200 = 0,51x) -> velocity GAGAL (<20 token dan rasio <1,5x). Free% UNVERIFIED (tanpa free view di PLAN). Bukan kandidat. DIAM.")
snap["contracts"]["ADRAW"]["runNote0931_1118"] = (
 f"Run 0931 (blok {BLOCK}): freeMinted 309->313 (+4), totalSupply view revert (bukan 0). Tetap watchlist-only-age-unverified. DIAM.")
# bsccat / pepe into their snapshot keys if present
rr = reread
snap["contracts"].setdefault("bsccat", {})["runNote0931_1118"] = "Run 0931: freeMinted 523->524 (blok %d); pool views lain revert. DIAM." % BLOCK
# pending claim binanceai.fun
pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote0931"] = (f"Run 0931 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c RigForge
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote0931"] = (f"Run 0931 (blok {BLOCK}): openedAt 0, freeSharesLeft 624, freeClaimed 376 - pool BELUM dibuka, tanpa perubahan. DIAM.")
# ARKT-claim
ac = snap["contracts"]["ARKT-claim-62a7"]
ac["runNote0931"] = "Run 0931: totalSupply 3 flat, totalMinted 3, hasClaimed(user) 0 - tanpa perubahan. DIAM."

snap["runNote0931_1118"] = (
 "Run 0931 (blok re-read %d, interval ~29,2 mnt vs 0901): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. "
 "Velocity LOLOS 2 item TAPI tanpa promosi: SPARKS +42 (25,05x) dan EIM +20 (6,84x) - keduanya free%% + umur UNVERIFIED. "
 "STOCK +17 (<20, free inferred 57,7%% <70%%). AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. "
 f"CAT402 sold out (100/100). binanceai.fun tetap refund phase; RigForge belum dibuka; ARKT-claim flat 3. DIAM.")
snap["checkedNotSaleShape0931_1118"] = (
 "Sourcify feed top BERUBAH vs 0901 (verifiedAt 2026-11-18T02:34:38Z): 6 kontrak baru vs hot-leg 0924 (0x55B4/0xF18F/0xf6C0/0xf37d/0x3797/0x49dF), semuanya S1=False S2=False (tanpa free view + tanpa agent ref; 0xF18F punya mint tapi tanpa quote/free/agent) -> checked-not-sale-shape, tidak diulang run ini.")
snap["boltbook_new_0931"] = (
 "Boltbook EN+ZH (43.914/42.200 byte, HTTP 200): 5 alamat distinct, sama EN=ZH. 0 KONTRAK PROYEK BARU vs snapshot: AGENT COSMOS 0x3Aed (age-excluded-2026-11-12, post recheck takoyaki.ai 10:35 HKT totalSupply 5.712/100.000, nextMintPrice 0 - bukan fase baru); LUCKY LIFE 0x6d31 (promotion-discarded-same-owner-2026-11-09, recheck 742/3.144 free 23,6%%); STOCK AGENT 0xba70 (di snapshot); BoltRewards 0x8269 (infra); BOLT token 0xBbDd (non-lead).")
snap["last_run_wib"] = NOW
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

# scan-state note
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0931_scan"] = ("Run 2026-11-18 09:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 1,1 dtk, head 134232346); 401 auth-wide, gagal total ke-51 berturut-turut main job. Watermark TETAP 134086385; gap ~145.961 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
