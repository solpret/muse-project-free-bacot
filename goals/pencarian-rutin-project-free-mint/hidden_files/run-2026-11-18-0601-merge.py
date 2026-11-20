#!/usr/bin/env python3
"""Merge run 2026-11-18 06:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0601-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0601-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~06:01 WIB"
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
    pc_entry["runNote0601"]="Run 0601 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0601"]="Run 0601 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0601"]="Run 0601: totalSupply 2 flat, totalMinted 2, paused 0, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 1 Sourcify baru + 1 Boltbook baru (0 agent-shaped).
snap["checkedNotAgentShaped0601_1118"]={
 "0x942455e00C01d0014c268309a71D3AfF3c827777":"Sourcify baru 22:52:44Z 17 Nov; hot-leg 0554 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "0x508CD7C962F20d8fB03A9a54cb179c628Cb1c2f3":"Sourcify baru 22:52:06Z 17 Nov; hot-leg 0554 shape-check: mint+quote+freeClaimed TAPI tanpa agent-ref - bukan agent-shaped, bukan sale-shape",
 "0xa30e1482A98A5AcDDF8E352e2eB45Fd2fE54B7D5":"Sourcify baru 22:52:06Z 17 Nov; hot-leg 0554 shape-check: mint+quote+freeClaimed TAPI tanpa agent-ref - bukan agent-shaped, bukan sale-shape",
 "0xC0430c75A99920b3D2491B3bC1Cd6DDC6deD3091":"Sourcify baru (di feed 0601 posisi 4); hot-leg 0549 shape-check: S1/S2 false, no mint/quote/free-view/agent-ref - bukan agent-shaped, bukan sale-shape",
 "boltbook_new_0601":"Boltbook EN+ZH 5 alamat, 0 baru vs 0531 (0x85e657ec sudah di-shape-check hot-leg 0524, 0 agent-shaped; sisanya sudah di snapshot: 0x4158B701, 0x8269Ea16, 0xBbDd8C77, STOCK AGENT) - 0 lead baru"}
snap["last_run"]="free-mint-search 2026-11-18 06:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~06:01 WIB"
snap["runNote0601_1118"]="Run 0601 (blok 134204229, interval ~30 mnt vs 0531): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-44 berturut-turut main job; watermark tetap 134086385; head 134204188, gap ~117.800 blok). Re-read 212 calls, 0 chunk error, 0 null pada view kunci; view err (selector revert) sama seperti 0531, bukan degradasi RPC. Velocity GAGAL di mana-mana (maks +12/30 mnt: MORFO 1092->1104; sisanya <=+5 atau flat: HIVE 1263, Bubblebruin 2620, CPASS 1777, AgentEcho 302->307, Kageveil 39->41, STOCK AGENT 566->567, AgentNOVA 754). STOCK AGENT freeLeft 544/1111 = 51,0% free terpakai TAPI umur UNVERIFIED + X unverified + velocity gagal -> BUKAN kandidat/strong lead; dicatat saja. AgentBubble 84,6% (freeMinted 1880/2222, flat) + Lumenhold 83,3% (freeClaimed 1250/1500, flat) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. THYRK totalSupply 4415, freeMinted 4314 flat, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 totalSupply 2 flat, hasClaimed 0. Sourcify feed top tetap 22:52:44Z 17 Nov: 3 baru vs 0531 (0x942455e0, 0x508CD7C9, 0xa30e1482) + 0xC0430c75 - semuanya sudah di-shape-check hot-leg (0549/0554), 0 agent-shaped/sale-shape. Boltbook 0 alamat baru vs 0531. Sweep EN+ZH: 0 baru (Bitcoin Frogs muncul lagi di ZH - SUDAH age-excluded run 1431 17 Nov, sale 31 Okt, JANGAN laporkan ulang; First-Dollar Grove 8 Nov, Agentic Gangster 9 Nov, AGENT COSMOS 5 Nov, Oathbots/LeadLoop/AGENT ID card 25-28 Okt semua lama). Odaily newsflash 17 Nov 18:04-22:22 + PANews front page: 0 hit Agent ID free-mint. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 520 flat; pepe free pool habis 500/500 + user sudah mint."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0601_scan"] = ("Run 2026-11-18 06:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,1 dtk, head 134200166); 401 auth-wide, gagal total ke-43 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~113.800 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
