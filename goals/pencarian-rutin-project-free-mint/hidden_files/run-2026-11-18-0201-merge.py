#!/usr/bin/env python3
"""Merge run 2026-11-18 02:01 WIB results into onchain-snapshot.json (run notes + new entries only)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
C = snap["contracts"]
def upd(key, **kw):
    e = C.setdefault(key, {})
    e.update(kw)
    return e
# HIVE Agents
e = C["HIVE Agents"]; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM."
# Bubblebruin
e = C["Bubblebruin"]; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 2620 FLAT, freeClaimed 2614/7777 = 33,6%, balanceOf(user)=1, minted-by-user. DIAM."
# AgentEcho
e = C["AgentEcho"]; e["totalSupply"]=241; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 209->241 (+32, ~1,07/mnt vs prev ~4/mnt -> velocity GAGAL); 241/20000 = 1,2% total-supply (BUKAN % kuota gratis - tanpa free view/quote); umur UNVERIFIED + website UNVERIFIED -> tetap EARLY lead, BUKAN strong lead/kandidat. Slot TERBUKA (mintedBy 0, balanceOf 0). TIDAK preview/mint."
# STOCK AGENT
e = C["STOCK AGENT"]; e["totalSupply"]=534; e["freeLeft"]=577; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 529->534 (+5, 0,17/mnt vs prev 0,33 = 0,5x -> velocity GAGAL); free 534/1111 = 48,1% (<50% kandidat, <70% strong lead); slot TERBUKA (quote 0, freeMintedByWallet 0, balanceOf 0); umur UNVERIFIED -> tetap EARLY lead. TIDAK preview/mint."
# Agent Bubble (key with space)
e = C["Agent Bubble"]; e["freeMinted"]=1873; e["totalSupply"]=2018; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): freeMinted 1873, totalSupply 2018 (hot-leg 0159 baca 1874/2019 di blok 134172493 - selisih 1 = variansi node RPC, bukan penurunan); free 84,3% TAPI umur UNVERIFIED -> BUKAN strong lead. DIAM."
# Lumenhold
e = C["Lumenhold"]; e["totalSupply"]=1250; e["freeClaimed"]=1245; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 1250 FLAT, freeClaimed 1245 (free 83,0% TAPI umur UNVERIFIED + velocity GAGAL -> BUKAN strong lead). DIAM."
# Stromboat (new - first read by main job; found by hot-leg 0149/0154)
C["Stromboat"] = {
 "address": "0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",
 "status": "watchlist-only-age-unverified-2026-11-18",
 "totalMinted": 101, "freeMinted": 101, "paidMinted": 0, "mintOpen": 1,
 "freeSupplyNote": "freeMinted 101/667 = 15,1% (<50% kandidat, <70% strong lead)",
 "freeMintedBy_user": 0, "balanceOf_user": 0, "slotOpen": True,
 "firstSeenWib": "2026-11-18 ~01:49 WIB (hot-leg)", "firstReadMainJob": "2026-11-18 ~02:01 WIB",
 "lastReadWib": "2026-11-18 ~02:01 WIB", "lastReadBlock": 134172350,
 "launchNote": "Umur peluncuran UNVERIFIED (tidak ada stated launch time / first-mint corroboration).",
 "gateNote": "Website gate GAGAL (hot-leg run 01:49, metode A: pencarian alamat kontrak tanpa situs proyek).",
 "velocityNote": "01:49 +67/5mnt -> 01:54 +8/5mnt -> 02:01 +9/~7mnt (melambat); velocity TIDAK lolos.",
 "runNote0201_1118": "Run 0201: freeMinted 92->101 (+9), totalMinted 101, paidMinted 0, mintOpen 1, slot user TERBUKA (freeMintedBy 0, balanceOf 0). 101/667 = 15,1%. Umur UNVERIFIED + gate GAGAL -> watchlist-only, BUKAN lead. TIDAK preview/mint."
}
# Foundry Faces - UPDATE existing entry (do not replace history)
e = C["Foundry Faces"]; e["totalMinted"]=2191; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalMinted 1631 (11-12) -> 2191 (+560; burst +539/2jam per Boltbook belski.ai 02:02 WIB, lalu flat). 2191/11111 = 19,7% total-supply (free% UNVERIFIED - tanpa free view). KOREKSI: cek Sourcify script run ini sempat salah baca 'NOT verified' (parser endpoint) - yang benar Sourcify exact_match verifiedAt 2026-11-11T04:31:40Z (sesuai snapshot + diverifikasi ulang live); ABI mintFree + holdsAgentId + AGENT_ID; klaim 'tidak ada selector mint di bytecode' DITARIK (scan selector tidak lengkap). Umur TETAP UNVERIFIED (first-mint tidak terkoroborasi; archive eth_call gagal) + slot UNVERIFIED (quiz-gated) -> tetap watchlist-only-age-unverified, BUKAN early lead (first mint bukan di run ini) / kandidat / strong lead. TIDAK preview/mint."
# Compasyn - UPDATE existing entry (do not replace history)
e = C["Compasyn"]; e["totalSupply"]=1093; e["freeClaimed"]=1088; e["freePctVerified"]=73.0; e["lastReadWib"]="2026-11-18 ~02:01 WIB"; e["lastReadBlock"]=134172350
e["runNote0201_1118"]="Run 0201 (blok 134172350): totalSupply 1093 FLAT, freeClaimed 1088/1490 = 73,0% (verified), slot user TERBUKA (mintedBy 0, balanceOf 0). TETAP BLOKIR tiga alasan independen (tidak berubah sejak 0531 11-09): (1) same-owner discard (owner Neuroveil/Homunqul cluster); (2) age-excluded - first mint TERVERIFIKASI 2026-11-03 14:49:54 WIB (~15 hari); (3) website gate NOT passed. BUKAN strong lead meski free% >70%. Jangan promosikan, jangan preview/eksekusi. TIDAK dilaporkan ulang (sudah dilaporkan sekali sebagai blocked 0531 11-09)."
# Kageveil Genesis - NEW early lead reported this run
C["Kageveil Genesis"] = {
 "address": "0xf79860f419be7b604d909e254785400d9edbd9d0",
 "status": "early-lead-reported-2026-11-18-0201",
 "name": "Kageveil Genesis", "symbol": "KAGE", "kind": "ERC721",
 "totalSupply": 39, "MAX_SUPPLY": 9999, "NORMAL_SUPPLY": 3333, "ELITE_SUPPLY": 6666, "PACK_SUPPLY": 666,
 "normalMinted": 39, "eliteMinted": 0, "packsMinted": 0, "mintOpen": 1, "mintClosed": 0, "balanceOf_user": 0,
 "agentShaped": "YA (prong free-mint function): Sourcify exact_match verifiedAt 2026-11-17T15:43:36Z; ABI 69 fns: mintNormal(bytes32 agentIdHash, bytes sig) nonpayable + agentSigner 0xac261122620f895cfde7a0779ac938d9aff6f2dc + agentUsed + NORMAL_SUPPLY 3333. TIDAK ADA referensi registry Agent ID di ABI/bytecode (AGENT_ID()/agentRegistry() absen) - dinyatakan jelas.",
 "freePctNote": "normalMinted 39/3333 = 1,17% alokasi normal (free% sebagai % kuota gratis: tanpa free view, 39/3333 adalah hitungan alokasi normal; totalSupply 39/9999 = 0,39%).",
 "owner": "0x61f2c58602f9bf432d085203e3317bd477d49da2",
 "sameOwnerCheck": "Owner TIDAK ada di same-owner-discards.json (61 entri).",
 "launchNote": "Umur UNVERIFIED: klaim Boltbook grandtheftauto6.ai ~02:00 WIB (blok 134171724: 38/9.999) saja; first-mint getLogs GAGAL -32005 limit exceeded di bsc-dataseed + dataseed1 (bahkan window 100 blok) - batasan yang sama seperti AgentEcho 0131.",
 "slotNote": "Slot user UNVERIFIED: mintNormal butuh signature off-chain dari agentSigner (jalur signature belum diverifikasi); balanceOf(user)=0; agentUsed(user-hash) belum dicek.",
 "website": None, "gate": "not-checked-early-lead (gate hanya jalan bila promosi)",
 "discussion": "Boltbook grandtheftauto6.ai 2026-11-17T19:00:01Z: 'Kageveil Genesis (KAGE, BSC) live at block 134,171,724: 38 / 9,999 minted (9,961 free left)'.",
 "firstSeenWib": "2026-11-18 ~02:01 WIB (Boltbook front page EN+ZH, run main job)",
 "lastReadWib": "2026-11-18 ~02:01 WIB", "lastReadBlock": 134172350,
 "runNote0201_1118": "Run 0201: EARLY LEAD dilaporkan sekali. totalSupply 38->39 (live read), normalMinted 39/3333 = 1,17%. BUKAN kandidat (<50%), BUKAN strong lead (<70% + umur UNVERIFIED). Early lead TIDAK PERNAH di-preview/di-mint."
}
# Track B pending claim (binanceai.fun) - unchanged
pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"]="2026-11-18 ~02:01 WIB"
pc["note"]="Run 0201 (blok 134172350): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM."
# Track C RigForge - unchanged
tc = snap["track_c"]["RigForge"]
tc["lastReadWib"]="2026-11-18 ~02:01 WIB"
tc["runNote0201_1118"]="Run 0201 (blok 134172350): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM."
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("merged OK; contracts:", len(snap["contracts"]))
