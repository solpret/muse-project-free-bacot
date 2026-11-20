#!/usr/bin/env python3
"""Merge run 2026-11-18 07:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0701-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0701-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~07:01 WIB"
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
    pc_entry["runNote0701"]="Run 0701 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0701"]="Run 0701 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0701"]="Run 0701: totalSupply 2 flat, totalMinted 2, paused 0, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 16 Sourcify baru vs 0601 (0 agent-shaped/sale-shape).
snap["checkedNotAgentShaped0701_1118"]={
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
 "boltbook_new_0701":"Boltbook EN+ZH 7 alamat, 2 'baru' vs 0601 (0x23ebbd63 + 0x5dbd2eb4) ternyata TX HASH di post PXIO Miner #3326 (crimicul.ai), bukan kontrak - 0 lead baru; sisanya sudah dikenal (CPASS, AgentEcho, 0x4158B701, 0x8269Ea16, 0xBbDd8C77)"}
snap["last_run"]="free-mint-search 2026-11-18 07:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~07:01 WIB"
snap["runNote0701_1118"]="Run 0701 (blok 134212440, interval ~30 mnt vs 0631): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-46 berturut-turut main job, elapsed 2,1 dtk; watermark tetap 134086385; head 134212295, gap ~125.910 blok). Re-read 212 calls, 0 chunk error; view err (selector revert) sama seperti 0631, bukan degradasi RPC. Velocity: EIM +39 (456->495, prev +19 = 2,05x, >=20) LOLOS tapi free%/umur/X unverified -> bukan kandidat/strong; ARKYN +33 (1980->2013, prev 0) lolos aritmetik tapi free%/umur unverified -> bukan kandidat/strong; STOCK AGENT +12 (572->584) gagal >=20; sisanya <=+6 atau flat. STOCK AGENT freeLeft 527/1111 = 52,6% free terpakai TAPI umur UNVERIFIED + X unverified + velocity gagal -> BUKAN kandidat/strong lead. AgentBubble 84,8% (freeMinted 1883/2222, +1) + Lumenhold 83,5% (freeClaimed 1252/1500, +2) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. Matrix 59,5% (595/1000), AGCLUB 59,3% (527/888) di bawah 70%. THYRK flat, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 totalSupply 2 flat, hasClaimed 0. ONI totalMinted 6 (0,6%) - tanpa gerak. Sourcify feed top 23:59:15Z 17 Nov: 4 baru vs 0631 - semuanya sudah di-shape-check hot-leg (0639/0654/0659), 0 agent-shaped/sale-shape. Boltbook 0 lead baru (BNBG sudah early-lead; RONIN same-owner-discarded; Hivebyte dikenal 8 Nov; 0xc4bFf245 = owner STOCK AGENT). Sweep EN+ZH: 0 baru (Oathbots 28 Okt, Laser Agents/AGENTID/hackou 25 Okt, AGENT COSMOS 5 Nov, Agentic Gangster 9 Nov, First-Dollar Grove 8 Nov, Bitcoin Frogs age-excluded + free pool habis 2000/2000). Odaily newsflash + PANews front page (keduanya HTTP 200): 0 hit Agent ID free-mint. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 521->522; pepe free pool habis 500/500 + user sudah mint. Early lead 17 Nov masih <24 jam (Agent Panda ~22 jam, Pocket Ai ~20,3 jam, ONI ~19 jam) - belum age-excluded; batas 24 jam jatuh 09:02-12:01 WIB hari ini, ditangani run berikutnya."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0701_scan"] = ("Run 2026-11-18 07:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 2,1 dtk, head 134212295); 401 auth-wide, gagal total ke-46 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~125.910 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
