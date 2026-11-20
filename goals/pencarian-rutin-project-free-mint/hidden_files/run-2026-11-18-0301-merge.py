#!/usr/bin/env python3
"""Merge run 2026-11-18 03:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0301-reread.json"))
reads=reread["reads"]
NOW="2026-11-18 ~03:01 WIB"
BLOCK=reread["block"]

def upd(name, fields):
    e=snap["contracts"].get(name)
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
    pc_entry["runNote0301"]="Run 0301 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0301"]="Run 0301 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# New upcoming item: ARKT sibling claim contract 0x62a7AC33 (Sourcify feed top, verifiedAt 2026-11-17T20:03:48Z)
snap["contracts"]["ARKT-claim-62a7"]={
 "address":"0x62a7AC33ca463331858693b8Aa05B16688bA29E0",
 "name":"ARKT-claim","kind":"ERC721","status":"watchlist-only-upcoming-2026-11-18",
 "totalSupply":0,"totalMinted":0,"MAX_PER_WALLET":1,"paused":1,
 "userBalance":0,"hasClaimed_user":0,
 "note":"Sourcify feed top run 0301 (verifiedAt 2026-11-17T20:03:48Z, exact_match, 36 fns). S1/S2 FALSE (no quote, no free views) - bukan lead track C. Agent-shaped: agentId()=registry EXACT 0x60B926...22F, claim()+hasClaimed+claimSigner+redeemer. Name/symbol on-chain = ARKT / ARKT (sama dgn ARKT NFT 0xf91b...); owner 0xc8dead02117464e715a6885866ed8714c462047b SAMA dgn ARKT, TIDAK ada di same-owner-discards (61 entri) - sibling contract proyek ARKT, kemungkinan claim/redeem contract. BELUM LAUNCH: totalSupply 0, totalMinted 0, paused=1 (blok 134180688). Watchlist-only upcoming, BUKAN kandidat/lead; TIDAK di-preview/di-mint.",
 "launch_time":None,"gate":None,"lastReadWib":NOW,"lastReadBlock":BLOCK}

snap["last_run"]="free-mint-search 2026-11-18 03:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B/C baru; DIAM"
snap["last_run_wib"]="2026-11-18 ~03:01 WIB"
snap["runNote0301_1118"]="Run 0301 (blok 134180268, interval ~30 mnt vs 0231): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead. Scan FAST-FAIL (Ankr 401 ke-38 berturut-turut main job). Re-read 208 calls, 0 chunk error. AgentEcho 262->270 (+8, velocity GAGAL 0,39x), slot terbuka, tetap EARLY. ARKT FLAT 322/1000, tetap EARLY. STOCK AGENT FLAT 539/1111=48,5%, slot terbuka, tetap EARLY. Stromboat 155->168 (+13, velocity GAGAL 0,24x), 25,2%. AgentBubble 84,4% + Lumenhold 83,1% di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. Compasyn 73,0% TAPI triple-blokir (same-owner discard + age-excluded + gate gagal). PIXELFROGS mintOpen 1->0 (mint ditutup; freeMinted 454, freeLeft 2546) - dicatat, bukan lead. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1). RigForge belum dibuka (openedAt 0, freeSharesLeft 625). Sourcify feed baru 1: 0x62a7AC33 (ARKT-claim sibling, S1/S2 false, totalSupply 0, paused 1) - masuk snapshot watchlist-only-upcoming. Boltbook 0 alamat baru (Neiro 0xb5ef sudah hot-leg-seen 9 Nov, free 100/100 habis; 0xf46d = tx hash AgentEcho, bukan kontrak). Sweep EN+ZH + Odaily/PANews: 0 baru (semua sudah di snapshot dgn status terminal)."
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
