#!/usr/bin/env python3
"""Merge run 2026-11-18 11:31 WIB re-read into onchain-snapshot.json (lean merge).
Read-only legs only. Never writes scan-bridge.json. No preview/mint/claim.
Adds PUNNY as EARLY LEAD (first-seen this run). Corrects the 1101 registry-bytes
reason for Mechfarm (typo'd literal in newleads script) - outcome unchanged:
Mechfarm stays age-excluded since 2026-11-05 (firstMint 2026-11-03 17:11 WIB)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1131-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1101-reread.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~11:31 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

updated, missed = [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name)
        continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply")
    pval = pv.get("totalSupply")
    view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted")
        pval = pv.get("totalMinted")
        view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        e["previousTotalSupply"] = pval
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4)
        e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel
        e["supplyView"] = view
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (no snapshot key): {missed}")

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1131_1118"] = text
    else:
        print("NOTE MISS", key)

note("HIVE Agents", f"Run 1131 (blok {BLOCK}): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1131 (blok {BLOCK}): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1131 (blok {BLOCK}): freeMinted 1889/2222 = 85,0% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2034 FLAT, balanceOf(user)=0. Tetap watchlist-only.")
note("Lumenhold", f"Run 1131 (blok {BLOCK}): freeClaimed 1252/1500 = 83,5% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1257 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1131 (blok {BLOCK}): freeMinted 616/1000 = 61,6% (<70%), totalSupply 612->613 (+1) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1131 (blok {BLOCK}): freeMinted 527/888 = 59,3% (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1131 (blok {BLOCK}): totalSupply 1169->1181 (+12, 0,491/mnt, 7,68x) -> velocity GAGAL (<20 token). Free% UNVERIFIED. Bukan kandidat.")
note("STOCK AGENT", f"Run 1131 (blok {BLOCK}): totalSupply 661->673 (+12, 0,491/mnt, 4,34x) -> velocity GAGAL (<20 token). Free inferred (1111-438)/1111 = 60,6% (<70%). Umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0). Bukan kandidat/strong lead.")
note("AgentEcho", f"Run 1131 (blok {BLOCK}): totalSupply 362->374 (+12, 0,491/mnt, 5,78x) -> velocity GAGAL (<20 token). Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1131 (blok {BLOCK}): totalMinted 688 FLAT -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1131 (blok {BLOCK}): totalSupply 1267->1268 (+1) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("PunchCard", f"Run 1131 (blok {BLOCK}): totalSupply 1332->1334 (+2) -> velocity GAGAL. freeMinted 1312/5555 = 23,6%. Bukan kandidat. DIAM.")
note("CAT402", f"Run 1131 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1131 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")

# ---- PUNNY: EARLY LEAD (first-seen this run) ----
snap["contracts"]["PUNNY"] = {
    "address": "0xaFAE0Bf373ad87E88555afe1605111F66C99062C",
    "name": "PUNNY",
    "symbol": "PUNNY",
    "kind": "ERC721",
    "status": "early-lead-reported-2026-11-18-1131",
    "totalMinted": 286,
    "freeMinted": 286,
    "FREE_SUPPLY": 999,
    "MAX_SUPPLY": 10000,
    "freeRemaining": 713,
    "mintStart": 1794922323,
    "mintStartWib": "2026-11-17T20:32:03+07:00",
    "mintClosed": 0,
    "MINT_DURATION": 86400,
    "mintClosesWib": "2026-11-18T20:32:03+07:00",
    "PAID_PRICE": 2000000000000000,
    "hasClaimedFree_user": 0,
    "mintedBy_user": 0,
    "balanceOf_user": 0,
    "agentRegistryBytes": True,
    "agentRegistryBytesCount": 2,
    "sourcifyVerifiedAt": "2026-11-17T13:34:26Z",
    "tokenURI1": "https://punny-nft.surge.sh/metadata/1.json",
    "websiteGate": "UNVERIFIED - tokenURI host punny-nft.surge.sh root 404, metadata tanpa external_url; pencarian nama proyek 0 hit situs proyek",
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "Launch VERIFIED <24h: mintStart() 2026-11-17 20:32:03 WIB, umur 15 jam 09 mnt saat baca 11:41 WIB; jendela mint 24 jam tutup 2026-11-18 20:32:03 WIB.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1131 WIB 2026-11-18. Agent-shaped: registry bytes 0x60B9...022F x2 di bytecode + agentIdRegistry() + freeMint()/FREE_SUPPLY. freeMinted 286/999 = 28,6% (<50% kandidat, <70% strong lead). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0). Website gate BELUM terverifikasi -> TIDAK PERNAH di-preview/di-mint sebagai early lead. Promosi ke strong lead butuh >70% + gate website; ke kandidat butuh semua kaki + safety.",
    "firstSeenBlock": 134247720,
    "firstSeenWib": "2026-11-18 ~11:28 WIB (Boltbook drzein.ai)",
    "lastReadBlock": BLOCK,
    "lastReadWib": NOW,
    "supplyView": "totalMinted",
    "currentRatePerMin": None,
    "velocityLegPasses": False,
}
snap["contracts"].setdefault("bsccat", {})["runNote1131_1118"] = (
    f"Run 1131: freeMinted 526 (flat vs 1101), totalSupply mentah 5,26e26; pool views lain revert. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1131_1118"] = (
    "Run 1131: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1131_1118"] = (f"Run 1131 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1131_1118"] = (f"Run 1131 (blok {BLOCK}): openedAt 0, freeSharesLeft 622 (1101: 622), "
    "freeClaimed 378 (1101: 378) - pool BELUM dibuka, tanpa perubahan status. DIAM.")
bb = snap["track_c"]["BNBbaby"]
bb["lastReadBlock"] = BLOCK
bb["runNote1131_1118"] = (f"Run 1131 (blok {BLOCK}): minter 0xbb7e...2637 mintingOpen=0 (TERKONFIRMASI tutup, konsisten dengan post takoyaki.ai), "
    "freeMinted 12456, mintedBy(user)=1 - user sudah klaim gratis 2026-11-02, tanpa perubahan. DIAM.")

snap["runNote1131_1118"] = (
    "Run 1131 (blok re-read %d, interval ~24,4 mnt vs 1101): 1 EARLY LEAD BARU (PUNNY, dilaporkan sekali), 0 kandidat, 0 strong lead, 0 track-B dibuka, 0 track-C lead. "
    "Velocity: TIDAK ADA yang lolos (terbanyak SPARKS/STOCK/AgentEcho +12, semua <20 token). "
    "AgentBubble 85,0%% + Lumenhold 83,5%% di atas 70%% TAPI umur UNVERIFIED -> BUKAN strong lead. STOCK free inferred 60,6%% (<70%%); Matrix 61,6%%; AGCLUB 59,3%%. "
    "PUNNY 0xaFAE0Bf373ad87E88555afe1605111F66C99062C: ERC-721, freeMinted 286/999 = 28,6%%, mintStart 2026-11-17 20:32:03 WIB (umur 15 jam 09 mnt, tutup 20:32 WIB), slot user TERBUKA, registry bytes x2 + agentIdRegistry + freeMint/FREE_SUPPLY -> EARLY LEAD. Website gate UNVERIFIED (punny-nft.surge.sh root 404, metadata tanpa external_url; search nama 0 hit) -> tidak pernah di-preview/di-mint. "
    "KOREKSI LITERAL REGISTRY: skrip newleads 1101/1131 memakai literal salah ketik 39-karakter '...48baa8b022f' (kurang satu 'a') sehingga registry_bytes selalu False; literal benar 40-karakter '...48baaa8b022f' sudah dipakai onchain_nft_scan.py. Dampak: Mechfarm 0x1fab SEBENARNYA agent-shaped (registry bytes x2) TAPI tetap DIAM karena SUDAH EXCLUDED age-over-48h sejak 2026-11-05 (firstMint 2026-11-03 17:11:49 WIB, tercatat di excluded Mechfarm-1FAb) - alasan 1101 'tanpa registry bytes' SALAH, hasil 'bukan lead' TETAP BENAR. Literal di run-2026-11-18-1131-newleads.py sudah diperbaiki. "
    "DragonAgent 0x82db14ac (token DAGENT, feeRecipient = owner 0x87a2...b099, paid shares ke owner, tanpa LP reserve): agentRegistry() = registry persis + registry bytes x2 -> agent-shaped TAPI fungible, ABI unverified, semua free view revert -> sale-shape UNVERIFIED -> BUKAN lead track-C, log only. "
    "Agent Pioneers 0xe2C11B21: Sourcify 404, freeMinted 321/10000 = 3,2%%, tanpa registry bytes -> BUKAN agent-shaped, log only. "
    "BNBbaby: minter 0xbb7e...2637 mintingOpen=0 terkonfirmasi (post takoyaki.ai benar: CA 0xD007... adalah token, bukan mint contract); user sudah klaim (mintedBy 1). DIAM. "
    "Sourcify feed top BARU (verifiedAt 2026-11-18T04:31:51Z): 4 kontrak baru (0x2586, 0x9288, 0x9d7b, 0x0d54) -> S1=False S2=False semua (hot-leg 1129 sudah shape-check, 0 hit) -> checked-not-sale-shape. "
    "Boltbook: SUDOSAINTS age-excluded 2026-11-16 (klaim 'Lead READY' author diabaikan - umur gugur); Sigmora 1.110/2.286 (free 48,3%%) watchlist-only; 0x37fe... adalah tx hash (bukan kontrak). "
    "binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 622). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    "Scan leg: pre-flight Ankr 401 gagal ke-50 berturut-turut main job (elapsed 2,8 dtk); watermark TETAP 134086385, gap ~162.626 blok. DIAM." % BLOCK)
snap["checkedNotSaleShape1131_1118"] = (
    "Sourcify feed top BARU vs 1101 (verifiedAt 2026-11-18T04:31:51Z, top 0x25866fe0809A5D6DC61027ccF854eBFD73EC2451): 4 kontrak baru - "
    "0x2586 (79 fns, tanpa mint/quote/free view/agent ref), 0x9288 (token, 22 fns), 0x9d7b (token, 9 fns), 0x0d54 (6 fns) -> S1=False S2=False semua (shape-check hot-leg 1129) -> checked-not-sale-shape.")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1131: 1 EARLY LEAD BARU (PUNNY) dilaporkan sekali; scan leg FAST-FAIL Ankr 401 ke-50; "
    "re-read 265 calls blok 134248219, 0 chunk error; tidak ada promosi/kandidat/eksekusi; koreksi literal registry (Mechfarm tetap age-excluded).")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1131_scan"] = ("Run 2026-11-18 11:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized (elapsed 2,8 dtk, head 134248219); "
    "401 auth-wide, gagal total ke-50 berturut-turut main job. Watermark TETAP 134086385; gap ~162.626 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
