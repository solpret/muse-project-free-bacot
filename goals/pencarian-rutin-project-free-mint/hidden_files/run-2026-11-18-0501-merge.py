#!/usr/bin/env python3
"""Merge run 2026-11-18 05:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
Chunk 0-19 of the main re-read failed JSON decode; catch-up file fills HIVE/Bubblebruin/CAT402/JADE/AgentBubble."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0501-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0501-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~05:01 WIB"
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
    pc_entry["runNote0501"]="Run 0501 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 dipertahankan (null run ini) - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0501"]="Run 0501 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: semua view null run ini (degradasi RPC) - nilai lama dipertahankan
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0501"]="Run 0501: semua view null (degradasi RPC, BUKAN nol); nilai lama dipertahankan (totalSupply 1, totalMinted 1, paused 0, hasClaimed 0). Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 1 Sourcify baru + 1 Boltbook baru (0 agent-shaped).
snap["checkedNotAgentShaped0501_1118"]={
 "0x81E77C3532315ca215800E6CE8A49191e7025899":"Sourcify baru 22:03:12Z, 18 fns (token polos: marketing_1/2/3, dead_wallet, transfer/approve), no mint/quote/free/agent - bukan agent-shaped, bukan sale-shape",
 "0x0e63b9c287e32a05e6b9ab8ee8df88a2760225a9":"Boltbook baru (Pieverse Token, post audit grandtheftauto6.ai 22:03:59Z): LayerZero OFT token, verified 2025-12-12, 91 fns, no free view, no agent ref - bukan agent-shaped, bukan sale-shape",
 "boltbook_new_0501":"Boltbook EN+ZH 8 alamat (vs 11 di 0431): 0x0e63b9c2 Pieverse di atas; sisanya sudah di snapshot (AgentBubble, Matrix, LumenFindings, CPASS, MOONDRILL, AgentEcho, STOCK AGENT) - 0 lead baru"}
snap["last_run"]="free-mint-search 2026-11-18 05:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~05:01 WIB"
snap["runNote0501_1118"]="Run 0501 (blok 134196313, interval ~30 mnt vs 0431): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-42 berturut-turut main job; watermark tetap 134086385; head 134196269, gap ~110rb blok). Re-read 212 calls + catch-up 20 calls (chunk 0-19 gagal JSON decode percobaan pertama, retry sukses; 0 chunk error tersisa). Velocity GAGAL di mana-mana (maks +10/30 mnt: AgentEcho 287->297; STOCK AGENT 546->554; sisanya <=+2 atau flat: HIVE 1263, Bubblebruin 2620, CPASS 1776, PunchCard 1315, AgentNOVA 752, Stromboat 182). AgentBubble 84,5% (freeMinted 1878/2222) + Lumenhold ~83% (freeClaimed 1248 dipertahankan, null run ini) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. STOCK AGENT 50,1% (freeLeft 557/1111). THYRK flat 4314/7777=55,5%, user pegang 1. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 null run ini (nilai lama dipertahankan). RONIN 0x9404e093 TIDAK di-probe ulang run ini (nilai 0401 dipertahankan; status same-owner-discarded -> TIDAK PERNAH dipromosikan/dilaporkan). Sourcify feed top 22:03:12Z: 1 baru 0x81E77C35 (token polos, 18 fns, no mint/quote/free/agent - bukan agent-shaped); Boltbook 1 baru Pieverse 0x0e63b9c2 (LayerZero OFT, 91 fns, no free view/agent - bukan agent-shaped). Sweep EN+ZH + Odaily/PANews: 0 baru (Oathbots, LeadLoop, NEXUS CORE, AgentForge, hackou, Pixel Fox, FACE ID, AGENT ID card, First-Dollar Grove, Agentic Gangster, AGENT COSMOS age-excluded, Bitcoin Frogs age-excluded-2026-11-17). Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0 dipertahankan). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 520 flat; pepe tanpa perubahan."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0501_scan"] = ("Run 2026-11-18 05:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,5 dtk, head 134196269); 401 auth-wide, gagal total ke-42 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~110.000 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
