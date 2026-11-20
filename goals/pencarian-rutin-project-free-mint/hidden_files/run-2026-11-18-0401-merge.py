#!/usr/bin/env python3
"""Merge run 2026-11-18 03:01 WIB re-read into onchain-snapshot.json (read-only legs only).
Never writes scan-bridge.json. No preview/mint/claim."""
import json
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
reread=json.load(open(f"{HF}/run-2026-11-18-0401-reread.json"))
reads=reread["reads"]
NOW="2026-11-18 ~04:01 WIB"
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
    pc_entry["runNote0401"]="Run 0401 (blok %s): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM." % BLOCK

# Track C: RigForge re-read
rg=reads.get("RigForge",{}).get("views",{})
tc=snap.get("track_c",{})
rf=tc.get("RigForge")
if isinstance(rf,dict):
    for f in ("freeSharesLeft","openedAt","freeClaimed"):
        if isinstance(rg.get(f),int): rf[f]=rg[f]
    rf["runNote0401"]="Run 0401 (blok %s): openedAt 0, freeSharesLeft 625, freeClaimed 375 - belum dibuka. DIAM." % BLOCK

# ARKT-claim-62a7 (run 0401): UNCHANGED since run 0331 - totalSupply 1,
# totalMinted 1, paused 0, hasClaimed(user)=0. Early lead already reported
# once in run 0331; no re-report. Claim still needs server EIP-712 signature
# (claimSigner 0x73ce048c71005e681851e5649b4711853526ffba); website gate still
# UNVERIFIED (aiarkdao.com does not print exact contract).
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
snap["checkedNotAgentShaped0401_1118"]={
 "0x6c8A5eA02D761aAb2Cc3091854BFA9FB189c894E":"Sourcify new 21:06:47Z, 26 fns, no mint/quote/free/agent - not agent-shaped",
 "0x3CF44FDc31B8758165b5854a1E33eE0447391E84":"Sourcify new 21:05:41Z, 31 fns, token, no mint/quote/free/agent - not agent-shaped",
 "0x1d6f1b0637A928b253096FB51296eE054976F288":"Sourcify new 21:04:05Z, 1 fn, no mint/quote/free/agent - not agent-shaped",
 "0x88fbc458D812a5315f2706644B711459958ED3C5":"Sourcify new 21:03:31Z, 1 fn, no mint/quote/free/agent - not agent-shaped",
 "0x9c4bBbF52FB9e35F04A69E453EB251FEE84348f2":"Sourcify new 21:03:15Z, 20 fns, token + mint fn, no quote/free/agent - not sale-shape",
 "0xb18D2E1dFC20b129bdF5cd126b748e00AdeEBd1c":"Sourcify new 21:03:01Z, 31 fns, token, no mint/quote/free/agent - not agent-shaped",
 "0x580CDa3690067dD00e1e186f5BAe9a8fEd3CF8C2":"Sourcify new 21:02:16Z, 20 fns, token + mint fn, no quote/free/agent - not sale-shape",
 "0x17196826850F0A4F52E39af1a5DcBf0AE515754d":"Sourcify new 21:01:32Z, 20 fns, token + mint fn, no quote/free/agent - not sale-shape",
 "0xd501080591e66a4b9db62cf38271437cc87e1c72":"Nova (NOVA) ERC-20, Boltbook post (8,000,000,000 minted, counter flat), 45 fns, freeClaimed view but no mint fn, no quote, no agent ref - not sale-shape"}
snap["last_run"]="free-mint-search 2026-11-18 04:01 WIB - 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; SILENT (RONIN same-owner-discarded hanya dicatat, bukan lead)"
snap["last_run_wib"]="2026-11-18 ~04:01 WIB"
snap["runNote0401_1118"]="Run 0401 (blok 134188671, interval ~30 mnt vs 0331): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead - SILENT. Scan FAST-FAIL (Ankr 401 ke-40 berturut-turut main job; watermark tetap 134086385; head 134188634, gap ~102rb blok). Re-read 212 calls, 0 chunk error. Velocity GAGAL di mana-mana (maks +5/30 mnt: AgentEcho 276->281, Stromboat 175->180; STOCK AGENT 540->543; XCOPY 453->455; ADRAW freeMinted 300->302; Mine Card 1108->1109; EIM 435->436; AgentNOVA 749->750). HIVE flat 1263, Bubblebruin flat 2620 (freeClaimed 2614/7777=33,6%). AgentBubble 84,4% (freeMinted 1876/2222, flat) + Lumenhold ~83% (1246, flat) di atas 70% TAPI umur UNVERIFIED - BUKAN strong lead. THYRK 55,5% flat (4314/7777). CAT402 sold out (freeCatsClaimed 100/100). PIXELFROGS mintOpen 0. ARKT (f91b) flat 323/1000; ARKT-claim-62a7 flat 1/1, paused 0 - keduanya sudah early-lead-reported, tanpa perubahan. RONIN/RONAG 0x9404e093 (Boltbook recheck): freeClaimed 1137/2222=51,2% + totalSupply 1147 terverifikasi on-chain (blok 134189237), mintOpen 1, mintedBy(user)=0 - TAPI same-owner-discarded (snapshot Roninagent, status 2026-11-03) -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead, hanya dicatat. Nova 0xd5010805 (Boltbook, 8M minted flat): shape-checked, bukan sale-shape (no mint/quote/agent). Sourcify feed 8 baru + Boltbook 3 baru: semua 9 shape-checked, 0 agent-shaped. Hot-leg 0409 menutup 5 Sourcify lebih baru (0 hit). Sweep EN+ZH + Odaily/PANews: 0 baru (semua sudah di snapshot: Oathbots, Meow Cards, Agentic Gangster, Laser Agents, AGENT ID card, hackou, First-Dollar Grove, Bitcoin Frogs age-excluded, AGENT COSMOS age-excluded). Bridge: 116 kontrak, 0 not in snapshot, 7 same-owner discarded. binanceai.fun pending claim tetap refund phase (launched 0, failed 1, isRefundPhase 1, tokenClaimed 0). RigForge belum dibuka (openedAt 0, freeSharesLeft 625, freeClaimed 375). bsccat/pepe tanpa perubahan."
# Roninagent (0x9404e093): Boltbook recheck this run - fresh on-chain probe
# (blok 134189237): freeClaimed 1137/2222 = 51,2%, totalSupply 1147, mintOpen 1,
# mintedBy(user)=0, balanceOf(user)=0. Status TETAP same-owner-discarded -
# NEVER promoted/reported as lead (bridge amendment 2026-11-03); log only.
ron = snap["contracts"].get("Roninagent")
if isinstance(ron, dict):
    ron["freeClaimed"] = 1137
    ron["totalSupply"] = 1147
    ron["FREE_SUPPLY"] = 2222
    ron["mintOpen"] = 1
    ron["runNote0401_1118"] = ("Run 0401 (blok 134189237): Boltbook recheck + probe on-chain: freeClaimed 1137/2222=51,2%, "
        "totalSupply 1147, mintOpen 1, mintedBy(user)=0, balanceOf(user)=0. Slot user TERBUKA dan free% >50% TAPI "
        "status same-owner-discarded (2026-11-03) -> TIDAK PERNAH dipromosikan/dilaporkan sebagai lead; hanya dicatat di run log.")
    ron["lastReadWib"] = NOW
    ron["lastReadBlock"] = 134189237
# Scan state: pre-flight 401 fast-fail, watermark NOT advanced
st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_0401_scan"] = ("Run 2026-11-18 04:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal "
    "deterministik HTTP 401 Unauthorized (elapsed 1,2 dtk, head 134188634); 401 auth-wide, gagal total ke-40 "
    "berturut-turut main job (sama dgn 2026-11-12, 11-14, 11-15, 11-16, 11-17). Watermark TETAP 134086385; "
    "gap ~102.000 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)

json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]))
