#!/usr/bin/env python3
"""Merge run 2026-11-18 05:31 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0531-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0531-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~05:31 WIB"
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
    pc_entry["runNote0531"]="Run 0531 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0531"]="Run 0531 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0531"]="Run 0531: totalSupply 1->2 (+1), totalMinted 2, paused 0, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 1 Sourcify baru + 1 Boltbook baru (0 agent-shaped).
snap["checkedNotAgentShaped0531_1118"]={
 "0xba2F07A8b1276E9B0836D2cBda862A15e0447777":"Sourcify baru 22:32:35Z 17 Nov; hot-leg 0529 shape-check: token, 22 fns, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0x592a63373d6885fCabc63092ec520A3B2abcf8b8":"Sourcify baru 22:24:21Z 17 Nov; hot-leg 0524 shape-check: token, 15 fns, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0x8b921449fa76932b7263D5Ec396B5f56820A737B":"Sourcify baru 22:12:21Z 17 Nov; hot-leg 0516 shape-check: token, 8 fns, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0xdf882159051425E7e285c0E278d9eD4cF5387777":"Sourcify baru 22:12:17Z 17 Nov; hot-leg 0516 shape-check: token, 40 fns, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0x85e657ec1d678f12e2980eb08b9eee232400b5cd":"Boltbook baru; hot-leg 0524 shape-check: n_fns 0, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0x94bd501F3D2bB5eF205a63c74D7995916830bc96":"Boltbook baru; hot-leg 0214 shape-check: n_fns 0, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "boltbook_new_0531":"Boltbook EN+ZH 7 alamat: 0x85e657ec + 0x94bd501F di atas (0 agent-shaped); sisanya sudah di snapshot (CPASS, AgentEcho, STOCK AGENT, 0x4158B701, 0x8269Ea16, 0xBbDd8C77) - 0 lead baru"}
snap["last_run"]="free-mint-search 2026-11-18 05:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~05:31 WIB"
snap["runNote0531_1118"]="Run 0531 (blok 134200218, interval ~30 mnt vs 0501): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-43 berturut-turut main job; watermark tetap 134086385; head 134200166, gap ~113.800 blok). Re-read 212 calls, 0 chunk error. Velocity GAGAL di mana-mana (maks +12/30 mnt: STOCK AGENT 554->566, 0,4/mnt, <20 token; sisanya <=+2 atau flat: HIVE 1263, Bubblebruin 2620, CPASS 1776->1777, AgentEcho 302 flat, AgentNOVA 752->754, ONI 6 flat). STOCK AGENT lewati 50% (freeLeft 545/1111 = 50,9%) TAPI umur UNVERIFIED + X unverified + velocity gagal -> BUKAN kandidat/strong lead; dicatat saja. AgentBubble 84,6% (freeMinted 1880/2222) + Lumenhold ~83% (freeClaimed 1250) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. THYRK flat 4314/7777=55,5%, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. DRAGON baca pulih (freeMinted 1000/totalMinted 1005/bal 1; null di 0524/0529 = kegagalan RPC, BUKAN perubahan state). ARKT (f91b) flat 323/1000; ARKT-claim-62a7 totalSupply 1->2, hasClaimed 0. RONIN 0x9404e093 TIDAK di-probe ulang run ini (nilai 0401 dipertahankan; status same-owner-discarded -> TIDAK PERNAH dipromosikan/dilaporkan). Sourcify feed top 22:32:35Z 17 Nov: 4 baru vs 0501 (0xba2F07A8, 0x592a6337, 0x8b921449, 0xdf882159) - semuanya sudah di-shape-check hot-leg, 0 agent-shaped/sale-shape. Boltbook 2 baru vs 0501 (0x85e657ec, 0x94bd501F) - sudah di-shape-check hot-leg, 0 agent-shaped. Sweep EN+ZH: 0 baru (Oathbots, LeadLoop, NEXUS CORE, AgentForge, AGENT ID card, Xuanwu Seed, Agentic Gangster, BN Agent Trials semua lama/age-excluded; Burn Agent sudah excluded 9 Nov). Odaily/PANews newsflash: 0 hit Agent ID free-mint. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 520 flat; pepe free pool habis 500/500 + user sudah mint."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0531_scan"] = ("Run 2026-11-18 05:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,1 dtk, head 134200166); 401 auth-wide, gagal total ke-43 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~113.800 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
