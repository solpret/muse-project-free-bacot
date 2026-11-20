#!/usr/bin/env python3
"""Merge run 2026-11-18 03:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0431-reread.json"))
reads=reread["reads"]
NOW="2026-11-18 ~04:31 WIB"
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
    pc_entry["runNote0431"]="Run 0431 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0431"]="Run 0431 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7 (run 0431): UNCHANGED since run 0331 - totalSupply 1,
# totalMinted 1, paused 0, hasClaimed(user)=0. Early lead already reported
# once in run 0331; no re-report. Claim still needs server EIP-712 signature
# (claimSigner 0x73ce048c71005e681851e5649b4711853526ffba); website gate still
# UNVERIFIED (aiarkdao.com does not print exact contract).
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
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
# Shape-checked this run: 1 Sourcify baru + 5 hot-leg 0424 (0 agent-shaped).
# Boltbook 'baru' vs 0401 semuanya sudah di snapshot / bukan kontrak.
snap["checkedNotAgentShaped0431_1118"]={
 "0xbAE02683a30D9D07cf00566c53cEF48d5546Da34":"Sourcify baru 21:32:56Z, 17 fns (PASS_DOVE/NOAH_REWARD, redeemPass/redeemTicket, tDOVE/tNOAH), no mint/quote/free/agent - pass/ticket redemption, not agent-shaped, not sale-shape",
 "hotleg0424_5":"Hot-leg 0424 shape-checked 5 Sourcify baru (0xbc9D1840 8 fns mint/no quote; 0x0e4D042F 10 fns token; 0xEd4E7516 8 fns mint/no quote; 0xc579A233 32 fns; 0x1243B23E 22 fns token) - 0 agent-shaped, 0 sale-shape",
 "boltbook_new_0431":"Boltbook EN+ZH 11 alamat (vs 9 di 0401): 0x08e3e408 Rulz Share (sudah di snapshot), 0x1c759C4e Claf Eye (sudah di snapshot), 0x0d729700 AgentBubble (di PLAN), 0xff2dac23 AgentEcho (di PLAN), 0x269299d3 = HASH TX mint Mine Card (bukan kontrak), 0x4158B701 LumenFindings (sudah di snapshot), 0x87b354e2 MOONDRILL = Boltbook-87b3 (sudah di snapshot) - 0 lead baru"}
snap["last_run"]="free-mint-search 2026-11-18 04:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT (RONIN same-owner-discarded hanya dicatat, bukan lead)"
snap["last_run_wib"]="2026-11-18 ~04:31 WIB"
snap["runNote0431_1118"]="Run 0431 (blok 134192636, interval ~30 mnt vs 0401): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-41 berturut-turut main job; watermark tetap 134086385; head 134192588, gap ~106rb blok). Re-read 212 calls, 0 chunk error. Velocity GAGAL di mana-mana (maks +6/30 mnt: AgentEcho 281->287; STOCK AGENT 543->546; AgentNOVA 750->751; Lumenhold freeClaimed 1246->1248; sisanya flat: HIVE 1263, Bubblebruin 2620, XCOPY 455, Mine Card 1109, EIM 436, Stromboat 180, ADRAW freeMinted 302, AGCLUB 527, PunchCard 1314, Matrix freeMinted 592, Ledgera totalSupply 2709). HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). AgentBubble 84,4% (freeMinted 1876/2222, flat) + Lumenhold ~83% (freeClaimed 1248) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. STOCK AGENT 49,1% (freeLeft 565/1111), slot user terbuka (quote 0) - di bawah 70%. THYRK SEMUA view null run ini (degradasi RPC, BUKAN nol; nilai lama 4314/7777=55,5% dipertahankan). CAT402 sold out (freeCatsClaimed 100/100). PIXELFROGS mintOpen 0. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 flat 1/1, paused 0 - keduanya sudah early-lead-reported, tanpa perubahan. RONIN 0x9404e093 TIDAK di-probe ulang run ini (nilai 0401: freeClaimed 1137/2222=51,2% dipertahankan; status same-owner-discarded -> TIDAK PERNAH dipromosikan/dilaporkan). Sourcify feed top 21:34:54Z: 1 baru 0xbAE02683 (pass/ticket redemption, 17 fns, no mint/quote/free/agent - bukan agent-shaped); 5 baru hot-leg 0424 sudah shape-checked hot-leg (0 hit). Boltbook EN+ZH 11 alamat: 0 lead baru (Rulz Share, Claf Eye, AgentBubble, AgentEcho, LumenFindings, MOONDRILL sudah di snapshot; 0x269299d3 = hash tx, bukan kontrak). Sweep EN+ZH + Odaily/PANews: 0 baru (semua sudah di snapshot: Oathbots, Meow Cards, Agentic Gangster, LeadLoop, AGENT ID card, First-Dollar Grove, Bitcoin Frogs, AGENT COSMOS age-excluded, Agent Zet free phase complete). Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0, totalShares 3110). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 520 flat; pepe tanpa perubahan."
# Roninagent (0x9404e093): TIDAK di-probe ulang run ini. Nilai 0401
# (freeClaimed 1137/2222, totalSupply 1147, mintOpen 1) dipertahankan apa
# adanya; status TETAP same-owner-discarded - NEVER promoted/reported as
# lead (bridge amendment 2026-11-03); log only. Blok stempel lama TIDAK
# ditulis ulang sebagai bacaan 0431.
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0431_scan"] = ("Run 2026-11-18 04:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,4 dtk, head 134192588); 401 auth-wide, gagal total ke-41 "
    "berturut-turut main job (sama dgn 2026-11-12, 11-14, 11-15, 11-16, 11-17). Watermark TETAP 134086385; "
    "gap ~106.000 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
