#!/usr/bin/env python3
"""Merge run 2026-11-18 02:31 WIB results into onchain-snapshot.json (run notes + new entries only)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
BLK = 134176419
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
C = snap["contracts"]
def upd(key, **kw):
    e = C.setdefault(key, {})
    e.update(kw)
    return e
# HIVE Agents
e = C["HIVE Agents"]; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM."
# Bubblebruin
e = C["Bubblebruin"]; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM."
# AgentEcho
e = C["AgentEcho"]; e["totalSupply"]=262; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 241->262 (+21, ~0,69/mnt vs prev ~1,07 = 0,64x -> velocity GAGAL); 262/20000 = 1,3% total-supply (BUKAN % kuota gratis); umur UNVERIFIED + website UNVERIFIED -> tetap EARLY lead. Slot TERBUKA (mintedBy 0, balanceOf 0). TIDAK preview/mint."
# STOCK AGENT
e = C["STOCK AGENT"]; e["totalSupply"]=539; e["freeLeft"]=572; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 534->539 (+5, 0,17/mnt vs prev 0,17 = 1,0x -> velocity GAGAL); free 539/1111 = 48,5% (<50% kandidat, <70% strong lead); slot TERBUKA (quote 0, freeMintedByWallet 0, balanceOf 0); umur UNVERIFIED -> tetap EARLY lead. totalMinted/freeMinted/freeClaimed reverted run ini (nilai snapshot dipertahankan). TIDAK preview/mint."
# Agent Bubble
e = C["Agent Bubble"]; e["freeMinted"]=1876; e["totalSupply"]=2021; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): freeMinted 1873->1876, totalSupply 2018->2021 (+3, velocity GAGAL <20); free 1876/2222 = 84,4% TAPI umur UNVERIFIED -> BUKAN strong lead. DIAM."
# Lumenhold
e = C["Lumenhold"]; e["totalSupply"]=1251; e["freeClaimed"]=1246; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 1250->1251, freeClaimed 1245->1246 (free 83,1% TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead). DIAM."
# Stromboat
e = C["Stromboat"]; e["totalMinted"]=155; e["freeMinted"]=155; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): freeMinted 101->155 (+54, ~1,8/mnt vs prev ~1,29 = 1,40x -> velocity GAGAL tipis, butuh >=1,5x); 155/667 = 23,2% (<50% kandidat, <70% strong lead). Slot TERBUKA (freeMintedBy 0, balanceOf 0). Umur UNVERIFIED + gate GAGAL -> tetap watchlist-only. TIDAK preview/mint."
# Kageveil Genesis
e = C["Kageveil Genesis"]; e["totalSupply"]=39; e["normalMinted"]=39; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 39 FLAT, normalMinted 39/3333 = 1,17%, mintOpen 1, mintClosed 0, balanceOf(user)=0. BUKAN kandidat (<50%), BUKAN strong lead. Tetap EARLY lead. TIDAK preview/mint."
# Foundry Faces
e = C["Foundry Faces"]; e["totalMinted"]=2192; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalMinted 2191->2192 (+1). 2192/11111 = 19,7% total-supply (free% UNVERIFIED). Umur TETAP UNVERIFIED + slot UNVERIFIED (quiz-gated) -> tetap watchlist-only-age-unverified. TIDAK preview/mint."
# Compasyn
e = C["Compasyn"]; e["totalSupply"]=1093; e["freeClaimed"]=1088; e["freePctVerified"]=73.0; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 1093 FLAT, freeClaimed 1088/1490 = 73,0% (verified), slot user TERBUKA (mintedBy 0, balanceOf 0). TETAP BLOKIR tiga alasan independen: (1) same-owner discard; (2) age-excluded (first mint 2026-11-03); (3) website gate NOT passed. BUKAN strong lead meski free% >70%. TIDAK dilaporkan ulang."
# PunchCard
e = C["PunchCard"]; e["totalSupply"]=1310; e["totalMinted"]=1310; e["freeMinted"]=1288; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalSupply 1306->1310 (+4), freeMinted 1284->1288; free ~23,2% (<50%, <70%); slot TERBUKA (mintPriceFor user 0, mintedCount 0, balanceOf 0). Velocity GAGAL. Bukan kandidat/strong lead. DIAM."
# AGCLUB
e = C["AGCLUB"]; e["totalMinted"]=525; e["freeMinted"]=525; e["lastReadWib"]="2026-11-18 ~02:31 WIB"; e["lastReadBlock"]=BLK
e["runNote0231_1118"]="Run 0231 (blok 134176419): totalMinted 524->525 (+1), freeMinted 524->525; free ~59,1% (<70%). Velocity GAGAL. Bukan strong lead. DIAM."
# ARKT - NEW early lead reported this run
C["方舟门票 (ARKT)"] = {
 "address": "0xf91b1ebbcb2b038107ed10b4cb163ed51ce39037",
 "status": "early-lead-reported-2026-11-18-0231",
 "name": "方舟门票", "symbol": "ARKT", "kind": "ERC721",
 "totalSupply": 322, "totalMinted": 322, "MAX_SUPPLY": 1000, "MAX_PER_WALLET": 1, "MAX_BATCH_SIZE": 100,
 "agentShaped": "YA (prong registry reference): agentId() live read = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F EXACT registry Agent ID. Registry bytes TIDAK ada di bytecode/ABI (disimpan di storage via setAgentId). Sourcify exact_match verifiedAt 2026-11-17T08:00:25Z; ABI 31 fns: mint(address)/batchMint(address[])/claim() nonpayable + agentId/setAgentId + hasClaimed. TIDAK ADA quote/cost fn, TIDAK ADA free view.",
 "freePctNote": "totalMinted 322/1000 = 32,2% MAX_SUPPLY (BUKAN % kuota gratis terverifikasi - tanpa free view; klaim post '678 free left' belum terverifikasi on-chain; mint() nonpayable = value 0).",
 "owner": "0xc8dead02117464e715a6885866ed8714c462047b",
 "sameOwnerCheck": "Owner TIDAK ada di same-owner-discards.json (61 entri).",
 "launchNote": "Launch ~02:28 WIB (Boltbook post grandtheftauto6.ai: live di blok 134,175,938, 322/1.000). Live read blok 134,176,419: 322/1000 mengonfirmasi minting baru jalan menit sebelum run. getLogs first-mint corroboration GAGAL -32005 rate limit di bsc-dataseed (window 100 dan 2 blok) - batasan yang sama seperti Kageveil/AgentEcho.",
 "slotNote": "Slot user TAMPAK TERBUKA (balanceOf(user)=0, hasClaimed(user)=0) tapi jalur mint vs claim belum diverifikasi.",
 "website": None, "gate": "not-checked-early-lead (gate hanya jalan bila promosi)",
 "discussion": "Boltbook grandtheftauto6.ai ~02:28 WIB: '方舟门票 (ARKT, BSC) live at block 134,175,938: 322 / 1,000 minted (678 free left)'.",
 "firstSeenWib": "2026-11-18 ~02:31 WIB (Boltbook front page EN+ZH, run main job)",
 "lastReadWib": "2026-11-18 ~02:31 WIB", "lastReadBlock": BLK,
 "runNote0231_1118": "Run 0231: EARLY LEAD dilaporkan sekali. totalMinted 322/1000 = 32,2% MAX_SUPPLY. BUKAN kandidat (<50%), BUKAN strong lead (<70% + free% UNVERIFIED). Early lead TIDAK PERNAH di-preview/di-mint."
}
# Track B pending claim (binanceai.fun) - unchanged
pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"]="2026-11-18 ~02:31 WIB"
pc["note"]="Run 0231 (blok 134176419): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM."
# Track C RigForge - unchanged
tc = snap["track_c"]["RigForge"]
tc["lastReadWib"]="2026-11-18 ~02:31 WIB"
tc["runNote0231_1118"]="Run 0231 (blok 134176419): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM."
snap["last_run_wib"]="2026-11-18 ~02:31 WIB"
snap["last_run_note"]="Run 0231: 1 EARLY LEAD BARU (ARKT) dilaporkan sekali; scan leg FAST-FAIL Ankr 401 ke-37; re-read 200 calls blok 134176419, 0 chunk error; tidak ada promosi/kandidat/eksekusi."
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("merged OK; contracts:", len(snap["contracts"]))
