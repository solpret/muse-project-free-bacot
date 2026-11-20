#!/usr/bin/env python3
"""Merge run 2026-11-18 08:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim.
No chunk errors this run; catch-up file empty ({})."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0801-reread.json"))
catch=json.load(open(f"{HF}/run-2026-11-18-0801-catchup.json"))
reads=reread["reads"]
for n,v in catch.items():
    reads.setdefault(n,{"address":"","views":{}})["views"].update(v)
NOW="2026-11-18 ~08:01 WIB"
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
    pc_entry["runNote0801"]="Run 0801 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0801"]="Run 0801 (blok %s): openedAt 0, freeSharesLeft 624, freeClaimed 376 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7: views terbaca normal run ini (totalSupply 1->2)
ac=snap["contracts"].get("ARKT-claim-62a7")
if isinstance(ac,dict):
    acv=reads.get("ARKT-claim-62a7",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","paused","hasClaimed_user"):
        if isinstance(acv.get(_f),int): ac[_f]=acv[_f]
    ac["lastReadWib"]=NOW; ac["lastReadBlock"]=BLOCK
    ac["runNote0801"]="Run 0801: totalSupply 3 flat (was 3), totalMinted 3, hasClaimed(user) 0 - terbaca normal run ini. Early lead sudah dilaporkan sekali run 0331; tanpa perubahan."
# ARKT NFT (key "方舟门票 (ARKT)") re-read values
arktn=snap["contracts"].get("方舟门票 (ARKT)")
if isinstance(arktn,dict):
    arv=reads.get("ARKT",{}).get("views",{})
    for _f in ("totalSupply","totalMinted","MAX_SUPPLY","hasClaimed_user","balanceOf_user"):
        if isinstance(arv.get(_f),int): arktn[_f]=arv[_f]
    arktn["lastReadWib"]=NOW; arktn["lastReadBlock"]=BLOCK
# Shape-checked this run: 16 Sourcify baru vs 0601 (0 agent-shaped/sale-shape).
snap["checkedNotAgentShaped0801_1118"]={
 "sourcify_0801":"Feed top BERUBAH vs hot-leg 0759 (0x190eE5bC6DF8581b2CEBDE3DF99014F80d28f0e4, verifiedAt 2026-11-18T01:03:26Z): 1 kontrak baru vs 0759, di-shape-check run ini: S1 FALSE (ada freeClaimed + agentIdOf/registry, TANPA fungsi quote/cost) + S2 FALSE (tanpa mintFree, tanpa FREE_SLOTS/FREE_SUPPLY) -> checked-not-sale-shape. Probe on-chain: freeRemaining 500/500, FREE_SHARES 500, sharesSold 0, soldOut 0, startTime 1795000680 (~18:18 WIB 18 Nov, BELUM dibuka), canFreeMint(user) 0. Near-miss bentuk sale (freeMint + FREE_SHARES + registry) tapi gagal S1/S2 sesuai definisi -> BUKAN lead track C, TIDAK di-preview/di-mint. 0x8cC62Bf4d165D686633a5E8dd764CA2b81ca7777 sudah di-shape-check hot-leg 0759 (S1/S2 false, is_token, tanpa mint/quote/free views/agent ref).",
 "boltbook_new_0801":"Boltbook EN+ZH 9+9 alamat; 0 lead baru. Satu alamat tampak-baru 0xcff1f74540e04e0cc3b6793562374f6862847151 = PREFIX TX HASH (tx PXIO claim 0xcff1f74540e04e0cc3b6793562374f68628471518f6d483961e511f02aab1001, post msb.ai 01:02 UTC), BUKAN kontrak - false positive regex. 0x4158b701... muncul 2x (checksum vs lowercase) = alamat sama."}
snap["last_run"]="free-mint-search 2026-11-18 08:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; 2 REMOVAL (Panda-2820 sold out + ONI age-excluded) - dilaporkan sekali"
snap["last_run_wib"]="2026-11-18 ~08:01 WIB"
snap["runNote0801_1118"]="Run 0801 (blok 134220261, interval ~30 mnt vs 0731): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. REMOVAL: Agent Panda-2820 SOLD OUT (totalMinted 10000/10000 MAX_SUPPLY, verifikasi live run ini; first mint 7 Nov 09:02 WIB) + ONI AGE-EXCLUDED (window startTime 15 Nov 12:00 WIB -> umur ~68 jam terverifikasi, totalMinted 6/3000 belum sold out) - keduanya dihapus dari snapshot, dilaporkan sekali. Scan FAST-FAIL (Ankr 401 ke-48 berturut-turut main job, elapsed 2,6 dtk, head 134220200; watermark tetap 134086385; gap ~133.815 blok). Re-read 212 calls, 0 chunk error; view err (selector revert) identik 0731, bukan degradasi RPC. Velocity: EIM +44 (523->567, prev +28 = 1,57x, >=20) LOLOS aritmetik TAPI EIM TIDAK ADA di snapshot (belum pernah ditambahkan; free%/umur/X unverified) -> bukan kandidat/strong; ditambahkan ke snapshot sbg watchlist-only-age-unverified run ini. Mine Card +36 (1128->1164, prev +12 = 3,0x, >=20) LOLOS aritmetik TAPI free% UNVERIFIED + umur UNVERIFIED + narasi UNVERIFIED (tanpa agent/registry) -> bukan kandidat/strong. Stromboat +27 (199->226, rasio vs rate 30-mnt sebelumnya TIDAK bisa diverifikasi) + free 226/667=33,9% + umur UNVERIFIED -> bukan kandidat/strong. ARKYN +29 (2124->2153, prev +111 = 0,26x) velocity GAGAL + free%/umur unverified. STOCK AGENT +12 (593->605, <20) velocity GAGAL; freeLeft 506 -> 605/1111=54,5% TAPI umur UNVERIFIED + X unverified -> BUKAN kandidat/strong; slot user tetap terbuka (quote 0, freeMintedByWallet 0, balance 0). AgentBubble 84,9% (freeMinted 1887/2222) + Lumenhold 83,5% (freeClaimed 1252/1500) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. Matrix 59,8% (598/1000), AGCLUB 59,3% (527/888) di bawah 70%. PunchCard 23,4%. HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). THYRK freeMinted 4314, slot user sudah terpakai. JADE cost user 0,0005 BNB (bukan gratis). CAT402 sold out (freeCatsClaimed 100/100). PIXELFROGS mintOpen 0. DRAGON free pool habis 1000/1000, bal 1. ARKT-claim-62a7 totalSupply 3 flat, hasClaimed 0. ONI totalMinted 6 flat (dihapus: age-excluded). Sourcify feed top BERUBAH (0x190eE5bC..., verifiedAt 01:03:26Z): 1 baru, shape-check S1/S2 FALSE -> checked-not-sale-shape (near-miss: freeMint + FREE_SHARES + registry, tanpa quote fn; probe: freeRemaining 500/500, startTime ~18:18 WIB 18 Nov belum dibuka, canFreeMint(user) 0). Boltbook EN+ZH (44.854/43.167 byte, HTTP 200): 9+9 alamat, 0 lead baru (0xcff1... = prefix tx hash PXIO, false positive). Sweep EN+ZH: 0 baru (Oathbots 28 Okt, AGENTID/LeadLoop 25 Okt, NEXUS 25 Okt, AgentForge 27 Okt, hackou 25 Okt, Bitcoin Frogs age-excluded + free pool habis 2000/2000, First-Dollar Grove 8 Nov, Agentic Gangster 9 Nov, @congge918 26 Okt). Odaily newsflash (265.933 byte) + PANews (114.242 byte), keduanya HTTP 200: 0 hit Agent ID/free-mint/free-share. Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 624, freeClaimed 376). bsccat freeMinted 522 flat; pepe free pool habis 500/500 + user sudah mint."
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0801_scan"] = ("Run 2026-11-18 08:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 2,6 dtk, head 134220200); 401 auth-wide, gagal total ke-48 "
    "berturut-turut main job. Watermark TETAP 134086385; "
    "gap ~133.815 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
