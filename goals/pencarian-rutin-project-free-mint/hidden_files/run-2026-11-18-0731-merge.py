#!/usr/bin/env python3
"""Merge run 2026-11-18 07:31 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0731-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0731-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~07:31 WIB"
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
    pc_entry["runNote0731"]="Run 0731 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0731"]="Run 0731 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0731"]="Run 0731: totalSupply 2->3, totalMinted 3, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 16 Sourcify baru vs 0601 (0 agent-shaped/sale-shape).
snap["checkedNotAgentShaped0731_1118"]={
 "sourcify_0731":"Feed top TIDAK BERUBAH vs hot-leg 0724 (0x4fF4E53f9BC8Ffdc86F4bd1160106e5D03277777, verifiedAt 2026-11-18T00:19:56Z): 0 kontrak baru vs 0701, 0 shape-check baru run ini; 4 baru vs 0631 sudah di-shape-check hot-leg (0639/0654/0659), 0 agent-shaped/sale-shape",
 "boltbook_new_0731":"Boltbook EN+ZH 6+6 alamat; rotasi front-page vs 0701 (0x1577cbaa Lion's Share + 0x6ac03204 masuk, keduanya sudah di-seen; ZH 0x5fe03829 Roguefall age-excluded, sudah di snapshot) - 0 lead baru"}
snap["last_run"]="free-mint-search 2026-11-18 07:31 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT"
snap["last_run_wib"]="2026-11-18 ~07:31 WIB"
snap["runNote0731_1118"]="Run 0731 (blok 134216239, interval ~30 mnt vs 0701): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-47 berturut-turut main job, elapsed 1,7 dtk; watermark tetap 134086385; head 134216165, gap ~129.780 blok). Re-read 212 calls, 0 chunk error; view err (selector revert) sama seperti 0701, bukan degradasi RPC. Velocity: ARKYN +111 (2013->2124, prev +33 = 3,36x, >=20) LOLOS aritmetik tapi free% UNVERIFIED + umur UNVERIFIED -> bukan kandidat/strong; EIM +28 (495->523, prev +39 = 0,72x) velocity GAGAL + free%/umur/X unverified -> bukan kandidat/strong; Mine Card +12, AgentEcho +9, STOCK AGENT +9 (584->593) gagal >=20; sisanya <=+6 atau flat. STOCK AGENT freeLeft 518/1111 = 53,4% free terpakai TAPI umur UNVERIFIED + X unverified + velocity gagal -> BUKAN kandidat/strong lead. AgentBubble 84,8% (freeMinted 1885/2222, +2) + Lumenhold 83,5% (freeClaimed 1252/1500, +0) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. Matrix 59,6% (596/1000), AGCLUB 59,3% (527/888) di bawah 70%. PunchCard 23,4%. THYRK flat, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis) - bukan kandidat. CAT402 sold out (freeCatsClaimed 100/100, sudah dilaporkan 17 Nov). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 totalSupply 2->3, hasClaimed 0. ONI totalMinted 6 (0,6%) - tanpa gerak. Sourcify feed top 00:19:56Z 18 Nov TIDAK BERUBAH vs hot-leg 0724: 0 baru vs 0701, 0 agent-shaped/sale-shape. Boltbook EN+ZH (44.534/43.335 byte, HTTP 200): 6+6 alamat, rotasi front-page saja (Lion's Share 0x1577cbaa + 0x6ac03204 masuk, keduanya sudah di-seen; ZH 0x5fe03829 = Roguefall age-excluded) - 0 lead baru. Sweep EN+ZH: 0 baru (Oathbots 28 Okt, AGENTID/LeadLoop 25 Okt, @congge918 26 Okt, Agentic Gangster 9 Nov, First-Dollar Grove 8 Nov, Bitcoin Frogs age-excluded + free pool habis 2000/2000). Odaily newsflash (260.082 byte) + PANews (116.018 byte), keduanya HTTP 200: 0 hit Agent ID/free-mint/free-share. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat freeMinted 522 flat; pepe free pool habis 500/500 + user sudah mint. Early lead 17 Nov: Agent Panda-2820 masih <24 jam (batas ~09:02 WIB hari ini); PocketAi SUDAH age-excluded 16 Nov (status snapshot); ONI 6 flat - belum age-excluded; ditangani run berikutnya."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0731_scan"] = ("Run 2026-11-18 07:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,7 dtk, head 134216165); 401 auth-wide, gagal total ke-47 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~129.780 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
