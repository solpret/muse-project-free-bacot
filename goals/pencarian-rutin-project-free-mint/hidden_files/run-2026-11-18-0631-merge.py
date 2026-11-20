#!/usr/bin/env python3
"""Merge run 2026-11-18 06:31 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0631-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0631-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~06:31 WIB"
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
    pc_entry["runNote0631"]="Run 0631 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0631"]="Run 0631 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0631"]="Run 0631: totalSupply 2 flat, totalMinted 2, paused 0, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 16 Sourcify baru vs 0601 (0 agent-shaped/sale-shape).
snap["checkedNotAgentShaped0631_1118"]={
 "0x7322C076948F7825d8A7E623E6005432bC271A51":"Sourcify baru top 23:22:42Z 17 Nov; hot-leg 0624 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (9 fns) - token biasa, bukan sale-shape",
 "0xB50bEfD419646598d70da3621b5238755b4A01c0":"Sourcify baru; hot-leg 0619 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0xAfC629ec74880ea1456fA164305abeed68a84cB3":"Sourcify baru; hot-leg 0619 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0x8D2AfCc1774c00bcE133c15bd8C724C815AF7777":"Sourcify baru; hot-leg 0614 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0xefCd1f25576F7578E36d7045A380Ced2F1Ee7034":"Sourcify baru; hot-leg 0614 shape-check: S1/S2 false, has_mint true TAPI no quote/free-view/agent-ref - bukan sale-shape",
 "0x3F245b7cB7b278D50a134135b25eA005F90d0698":"Sourcify baru; hot-leg 0614 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0xF556f71cfA9a907Ce04d2D2a91E9353E6CA5CD7c":"Sourcify baru; hot-leg 0609 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0xba2F07A8b1276E9B0836D2cBda862A15e0447777":"Sourcify baru; hot-leg 0529 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0x592a63373d6885fCabc63092ec520A3B2abcf8b8":"Sourcify baru; hot-leg 0524 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan sale-shape",
 "0x8b921449fa76932b7263D5Ec396B5f56820A737B":"Sourcify baru; hot-leg 0516 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (8 fns) - bukan sale-shape",
 "0xdf882159051425E7e285c0E278d9eD4cF5387777":"Sourcify baru; hot-leg 0516 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (40 fns) - bukan sale-shape",
 "0x81E77C3532315ca215800E6CE8A49191e7025899":"Sourcify baru; hot-leg 0507 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (18 fns) - bukan sale-shape",
 "0x14D9b5778BcD84914C31a9Ad13fa4C14E206D3Aa":"Sourcify baru; hot-leg 0500 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (8 fns) - bukan sale-shape",
 "0x1545C91f35317f7Fdd268ee65dfEa3b849266924":"Sourcify baru; hot-leg 0455 shape-check: S1/S2 false, has_quote true TAPI no mint/free-view/agent-ref - bukan sale-shape",
 "0x2538AdD82670648E372FBc6603C44B18cBDaF92E":"Sourcify baru; hot-leg 0455 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (44 fns) - bukan sale-shape",
 "0xAf93d221D3dA6C9fEF48736b52eDec15ef22002a":"Sourcify baru; hot-leg 0448 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref, is_token (20 fns) - bukan sale-shape",
 "boltbook_new_0631":"Boltbook EN+ZH 7 alamat, 2 'baru' vs 0601 (0x23ebbd63 + 0x5dbd2eb4) ternyata TX HASH di post PXIO Miner #3326 (crimicul.ai), bukan kontrak - 0 lead baru; sisanya sudah dikenal (CPASS, AgentEcho, 0x4158B701, 0x8269Ea16, 0xBbDd8C77)"}
snap["last_run"]="free-mint-search 2026-11-18 06:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~06:31 WIB"
snap["runNote0631_1118"]="Run 0631 (blok 134208437, interval ~30 mnt vs 0601): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-45 berturut-turut main job; watermark tetap 134086385; head 134208387, gap ~122.000 blok). Re-read 212 calls, 0 chunk error; view err (selector revert) sama seperti 0601, bukan degradasi RPC. Velocity GAGAL di mana-mana (maks +19/30 mnt: EIM 437->456; sisanya <=+8 atau flat: AgentEcho 307->315, STOCK AGENT 567->572, AgentBubble 2025->2027, Matrix 589->591, Mine Card 1113->1115, CPASS 1777->1778, PunchCard 1315->1316). STOCK AGENT freeLeft 539/1111 = 51,5% free terpakai TAPI umur UNVERIFIED + X unverified + velocity gagal -> BUKAN kandidat/strong lead; dicatat saja. AgentBubble 84,7% (freeMinted 1882/2222) + Lumenhold 83,3% (freeClaimed 1250/1500, flat) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. Matrix 59,4% (594/1000), AGCLUB 59,3% (527/888) di bawah 70%. THYRK flat, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 totalSupply 2 flat, hasClaimed 0. ONI totalMinted 6 (0,6%) - tanpa gerak. Sourcify feed top 23:22:42Z 17 Nov: 16 baru vs 0601 - semuanya sudah di-shape-check hot-leg (0448-0624), 0 agent-shaped/sale-shape; 2 hit S1/S2 lama di hot-leg-seen (CantonTron 0x92115081 gate-FAILED 6 Nov; Crack 0xAeA1433d minted-by-user 6 Nov) - sudah ditangani, bukan baru. Boltbook 0 lead baru (2 alamat baru ternyata tx hash post PXIO). Sweep EN+ZH: 0 baru (Oathbots 28 Okt, hackou/LeadLoop/Pixel Fox 25 Okt, AgentForge 27 Okt, Subsonic/BNBmeme/BN Agent File/PIXEL PETS/Skynet 26 Okt, Agentic Gangster 9 Nov, QILIN/SAFU/PROXY/传火人 1 Nov, Periodic Lab 2 Nov, AgentIdETH Ethereum - semua lama/dikenal). Odaily newsflash 17 Nov 18:25-23:10 UTC + PANews front page: 0 hit Agent ID free-mint. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 520->521; pepe free pool habis 500/500 + user sudah mint. Early lead 17 Nov masih <24 jam (Agent Panda ~21,5 jam, Pocket Ai ~19,8 jam, ONI ~18,5 jam) - belum age-excluded; batas 24 jam jatuh 09:02-12:01 WIB hari ini, ditangani run berikutnya."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0631_scan"] = ("Run 2026-11-18 06:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,3 dtk, head 134208387); 401 auth-wide, gagal total ke-45 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~122.000 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
