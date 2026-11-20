#!/usr/bin/env python3
"""Merge run 2026-11-18 03:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0331-reread.json"))
reads=reread["reads"]
NOW="2026-11-18 ~03:31 WIB"
BLOCK=reread["block"]

addr2key={}
for _k,_v in snap.get("contracts",{}).items():
    if isinstance(_v,dict) and _v.get("address"):
        addr2key[_v["address"].lower()]=_k
def upd(name, fields):
    e=snap["contracts"].get(name)
    if e is None:
        _a=reads.get(name,{}).get("address","").lower()
        _k=addr2key.get(_a)
        if _k: e=snap["contracts"][_k]
    if e is None:
        print("MISS", name); return
    v=reads.get(name,{}).get("views",{})
    for f in fields:
        val=v.get(f)
        if isinstance(val,int):
            e[f]=val
    e["lastReadWib"]=NOW
    e["lastReadBlock"]=BLOCK

upd("HIVE Agents", ["totalSupply","balanceOf_user"])
upd("Bubblebruin", ["totalSupply","freeClaimed","balanceOf_user"])
upd("CAT402", ["freeCatsClaimed"])
upd("JADE", ["freeClaimed","totalSupply","mintOpen","mintedBy_user","balanceOf_user"])
upd("AgentBubble", ["freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user"])
upd("DRAGON", ["freeMinted","totalMinted","balanceOf_user"])
upd("Matrix", ["freeMinted","freeRemaining","totalSupply","mintOpen"])
upd("AGCLUB", ["totalMinted","freeMinted","FREE_CAP","mintOpen","balanceOf_user"])
upd("BNBG", ["totalMinted"])
upd("SPARKS", ["totalSupply"])
upd("Ledgera", ["freeClaimed","totalSupply","mintOpen","freeUsed_user","balanceOf_user"])
upd("BoldLeonidas", ["totalSupply","mintOpen","balanceOf_user"])
upd("RaceAgents", ["totalSupply","freeMinted","mintOpen"])
upd("CPASS", ["totalMinted","mintOpen","balanceOf_user"])
upd("REOPIR", ["freeClaimed","totalSupply","mintOpen"])
upd("RAVE", ["totalMinted","freeMinted","mintOpen"])
upd("MORFO", ["totalMinted","mintOpen"])
upd("PIXELFROGS", ["totalSupply","freeMinted","freeLeft","mintOpen","freeClaimed_user"])
upd("Flare-bd6f", ["totalSupply"])
upd("PunchCard", ["totalSupply","totalMinted","freeMinted","paidMinted","MAX_SUPPLY","mintOpen","mintedCount_user","balanceOf_user"])
upd("XCOPY", ["totalSupply","totalMinted"])
upd("ARKYN", ["totalMinted"])
upd("Mine Card", ["totalSupply","totalMinted"])
upd("ALIEN", ["totalSupply"])
upd("Kitebots", ["totalSupply","freeMinted"])
upd("EIM", ["totalMinted","mintOpen"])
upd("Lumenhold", ["totalSupply","freeClaimed"])
upd("PXIO Miners", ["totalSupply"])
upd("FrieAgent-B751", ["totalSupply"])
upd("FrieAgent-c64d", ["totalSupply"])
upd("Abyssora", ["totalSupply"])
upd("HANAMI", ["totalSupply","freeMinted"])
upd("Zephyra", ["totalMinted"])
upd("AgentNOVA", ["totalSupply"])
upd("ONI", ["totalMinted","totalSupply"])
upd("HAPPE", ["totalMinted","freeMinted"])
upd("Kryntar", ["totalMinted"])
upd("Pengu", ["totalMinted","freeMinted"])
upd("STOCK AGENT", ["totalSupply","freeLeft","FREE_SUPPLY","MAX_SUPPLY","mintOpen","freeMintedByWallet_user","balanceOf_user"])
upd("THYRK", ["totalSupply","freeMinted","MAX_SUPPLY","freeUsed_user","balanceOf_user"])
upd("ADRAW", ["freeMinted","balanceOf_user","hasClaimedFree_user"])
upd("AgentEcho", ["totalSupply","mintOpen","MAX_SUPPLY","mintedBy_user","balanceOf_user"])
upd("ARKT", ["totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"])
upd("Stromboat", ["totalMinted","freeMinted","paidMinted","mintOpen","freeMintedBy_user","balanceOf_user"])
upd("Kageveil Genesis", ["totalSupply","normalMinted","mintOpen","mintClosed","balanceOf_user"])
upd("Foundry Faces", ["totalMinted"])
upd("Compasyn", ["totalSupply","freeClaimed","mintedBy_user","balanceOf_user"])
# JADE cost is wei, keep separately
jv=reads.get("JADE",{}).get("views",{})
if isinstance(jv.get("cost_user_1"),int): snap["contracts"]["JADE"]["cost_user_1"]=jv["cost_user_1"]
pc=reads.get("PunchCard",{}).get("views",{})
if isinstance(pc.get("mintPriceFor_user_1"),int): snap["contracts"]["PunchCard"]["mintPriceFor_user_1"]=pc["mintPriceFor_user_1"]

# Track B pending claim re-read
bna=reads.get("binanceai-mint",{}).get("views",{})
pc_entry=snap.get("pending_claims",{}).get("binanceai.fun")
if pc_entry is not None:
    for f in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user"):
        if isinstance(bna.get(f),int): pc_entry[f]=bna[f]
    pc_entry["lastReadWib"]=NOW
    pc_entry["runNote0331"]="Run 0331 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0331"]="Run 0331 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7 LAUNCHED between 03:01-03:33 WIB (run 0331): paused 1->0,
# totalSupply 0->1, totalMinted 0->1, hasClaimed(user)=0; first mint verified
# on-chain (token #1 owner 0xe5564f2404a26eb0ab9f085d2d51f01dd94ad999, via
# ownerOf(1)); exact first-mint block unpinned (public RPC eth_getLogs
# rate-limited: bsc-dataseed "limit exceeded", publicnode 429 on 6/8 chunks).
# Age <24h VERIFIED by bracket (supply 0 at 03:01, 1 at ~03:33). agentId() =
# registry exact. claim(deadline,signature) nonpayable BUT needs EIP-712
# signature from claimSigner 0x73ce048c71005e681851e5649b4711853526ffba
# (server-issued, 15-min window) - NOT directly mintable. Site aiarkdao.com
# (via tokenURI image) does NOT print the exact contract in fetched HTML;
# no /skill.md, no /launch.json -> website gate UNVERIFIED. User eligibility
# UNVERIFIED (holds 0 ARKT NFT; signature eligibility unknown).
# Reported ONCE as EARLY lead in run 0331 (first mint verified this run).
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    ac["totalSupply"]=1; ac["totalMinted"]=1; ac["paused"]=0; ac["hasClaimed_user"]=0
    ac["status"]="early-lead-reported-2026-11-18"
    ac["launchBracketWib"]="2026-11-18 03:01-03:33 WIB (supply 0->1, paused 1->0)"
    ac["firstMint"]={"tokenId":1,"owner":"0xe5564f2404a26eb0ab9f085d2d51f01dd94ad999","block":"unpinned (public RPC getLogs rate-limited)","ageVerified":"<24h by bracket"}
    ac["gate"]="website UNVERIFIED (aiarkdao.com via tokenURI image, does not print exact contract; no /skill.md, no /launch.json)"
    ac["eligibility"]="UNVERIFIED (user holds 0 ARKT NFT; claim needs server EIP-712 signature, claimSigner 0x73ce048c71005e681851e5649b4711853526ffba)"
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 9 addresses, 0 agent-shaped (registry bytes false + ABI)
snap["checkedNotAgentShaped0331_1118"]={
 "0x336abda83b385e1b9c75855810cb6769561f5533":"HOG ERC-20 token (Boltbook post: live read-only verification, not a free mint)",
 "0xB647686b425653A229f5b0d91855e3bB92D45492":"RuneCoinMining staking contract (Boltbook Runestone post, not a free mint)",
 "0xC4b03274969eF7D449b3aC3ED5d1A9C723ba447F":"TOSA Lion plain ERC-20",
 "0x93eBA7E74c8f75841931e9037830605EFEc17EaD":"WebAuthn/ERC-4337 validator module (14 fns, no mint/agent)",
 "0x670b1f3D926195214EfE3447fB550eb960af0E8d":"Pyramid Hunts generic ERC-721 mint (mint+MINT_PRICE, totalSupply 0, no agent gate/free views)",
 "0x997b29763201fe2C833A19d60b42114B3084baa6":"DeFi pool/position contract (36 fns, no mint/agent)",
 "0xBaf11A3B6721e61A75F4092E83cB6673CAad849f":"DeFi pool implementation (71 fns, no mint/agent)",
 "0x3b0697Da968AFAE90032C23A371374695eDcE763":"USDT plain ERC-20 (6 fns)",
 "0x986E4c99BCB756cBB41ADDe36C17b40272748740":"Koma Fox plain ERC-20"}
snap["last_run"]="free-mint-search 2026-11-18 03:31 WIB - 0 kandidat, 0 strong lead, 1 early lead baru (ARKT-claim-62a7, first mint verified), 0 track-B dibuka, 0 track-C lead; LAPOR EARLY SEKALI"
snap["last_run_wib"]="2026-11-18 ~03:31 WIB"
snap["runNote0331_1118"]="Run 0331 (blok 134184483, interval ~30 mnt vs 0301): 1 EARLY LEAD BARU: ARKT-claim-62a7 (Ark Ticket 0x62a7AC33) LAUNCHED - paused 1->0, totalSupply 0->1 antara 03:01-03:33 WIB, first mint terverifikasi (token #1 owner 0xe5564f2404a26eb0ab9f085d2d51f01dd94ad999); umur <24h VERIFIED by bracket (blok/tx first-mint exact tidak terpin - public RPC eth_getLogs rate-limited); agentId()=registry exact; claim() nonpayable TAPI butuh signature EIP-712 dari claimSigner server (15 mnt window) - TIDAK langsung mintable; website aiarkdao.com (via tokenURI image) TIDAK mencetak kontrak exact (HTML fetch, no /skill.md, no /launch.json) -> gate UNVERIFIED; eligibility user UNVERIFIED (holds 0 ARKT NFT); hasClaimed(user)=0. Dilaporkan SEKALI sebagai EARLY, TIDAK di-preview/di-mint. 0 kandidat, 0 strong lead, 0 track-B dibuka, 0 track-C lead. Scan FAST-FAIL (Ankr 401 ke-39 berturut-turut main job; watermark tetap 134086385). Re-read 212 calls, 0 chunk error. AgentEcho 270->276 (+6, velocity GAGAL), ARKT 322->323 (+1), STOCK AGENT 539->540 (+1, 48,6%), AgentNOVA 748->749 (+1); HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). AgentBubble 84,4% + Lumenhold ~83% di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. THYRK freeMinted 4314/7777=55,5%. CAT402 sold out (freeCatsClaimed 100/100). PIXELFROGS mintOpen 0 (tutup). binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1). RigForge belum dibuka (openedAt 0, freeSharesLeft 625). Sourcify feed baru 7 + Boltbook baru 2: semua 9 shape-checked, 0 agent-shaped (registry bytes false + ABI: modul WebAuthn, kontrak DeFi pool, ERC-20 polos, generic NFT, RuneCoinMining, HOG). Boltbook 0 lead baru. Sweep EN+ZH + Odaily/PANews: 0 baru (semua sudah di snapshot, age-excluded: Bitcoin Frogs, Meow Cards, Oathbots; AgenticGangster, Subsonic Tribe, AGENT ID card sudah dikenal). Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded."
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
