#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-13 23:31 WIB.
Merges run-2026-11-13-2331-verify.json + -retry.json + -probe-race-relic.json
+ -probe-s1trio.json into onchain-snapshot.json (fresh read, then write).
No preview/mint. Backup saved as onchain-snapshot.json.bak-2331 first."""
import json, shutil, subprocess, os
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
_env=dict(os.environ); _env["TZ"]="Asia/Jakarta"
NOW=subprocess.check_output(["date","+%Y-%m-%d ~%H:%M WIB"],env=_env).decode().strip()
LAST_RUN=subprocess.check_output(["date","+%Y-%m-%dT%H:%M+07:00"],env=_env).decode().strip()
shutil.copy(BASE+"onchain-snapshot.json", BASE+"onchain-snapshot.json.bak-2331")
print("NOW:", NOW)
snap=json.load(open(BASE+"onchain-snapshot.json"))
verify=json.load(open(BASE+"run-2026-11-13-2331-verify.json"))
retry=json.load(open(BASE+"run-2026-11-13-2331-retry.json"))
probeRR=json.load(open(BASE+"run-2026-11-13-2331-probe-race-relic.json"))
probeS1=json.load(open(BASE+"run-2026-11-13-2331-probe-s1trio.json"))
READS={}
for src in (verify,retry,probeRR,probeS1):
    for k,v in src["reads"].items():
        if v.get("views") is not None: READS[k]=v
VB=verify.get("block")  # 133388727
RB=retry.get("block")   # 133389464
def norm(a): return (a or "").lower()
updated=[]
for key,ent in snap.get("contracts",{}).items():
    a=norm(ent.get("address"))
    hit=None
    for rk,rv in READS.items():
        if norm(rv.get("address"))==a and a:
            hit=(rk,rv); break
    if not hit: continue
    rk,rv=hit
    views=rv["views"]
    for fk,fv in views.items():
        if fv is not None: ent[fk]=fv
    # lastReadBlock: probe/retry blocks are fresher than VB
    ent["lastReadBlock"]=retry.get("block") if rk in retry.get("reads",{}) else VB
    ent["lastReadWib"]=NOW
    updated.append(key)
print("generic-merged:",len(updated))
def note(key,text):
    ent=snap["contracts"].get(key)
    if ent is not None: ent["runNote2331"]=text
# --- velocity + status notes (interval 2231->2331 ~49 mnt chain-time, blok 133382185->133388727) ---
note("OBFG","Run 2331: totalSupply 707->717 (+10), rate 0,089/mnt vs prev 0,1061 = 0,84x — velocity GAGAL; free 717/1230 = 58,3%. Sudah AGE-EXCLUDED (run 2002). DIAM.")
note("JNTM","Run 2331: totalMinted 1202->1212 (+10 paid), freeClaimed 1000/1000, freeLeft 0 — free pool TETAP habis. DIAM.")
note("AgentMuse","Run 2331: freeClaimed 446->453/888 = 51,0% (+7), DOORS_OPEN 1794524400 = 2026-11-13 05:53:20 WIB (deadline umur 05:53 WIB 14 Nov). Minted-by-user (track_c). DIAM.")
note("OUTY","Run 2331: minted 41 FLAT, freeSold 41/1500 = 2,7%, phase 1, freeOpen 1, freeQuotaOf_user 1; FREE_FEE 0,0001 BNB (free lane TIDAK cost-0). Status watchlist-only-opened-fee-not-free. DIAM.")
note("PX24","Run 2331: totalSupply 527 FLAT. DIAM.")
note("SKRR","Run 2331: totalSupply 517->518 (+1). DIAM.")
note("ME30","Run 2331: totalSupply 298->299 (+1), rate 0,020/mnt vs prev 0,0401 = 0,51x — velocity GAGAL. DIAM.")
note("CY24","Run 2331: totalSupply 464 FLAT. DIAM.")
note("MECHA","Run 2331: totalMinted 1969->1972 (+3), rate 0,061/mnt vs prev 0,06 = 1,02x — velocity GAGAL. DIAM.")
note("Pickgrid Pickaxe","Run 2331: totalSupply 218 FLAT, freeMinted 216/300 = 72,0% FLAT; umur TETAP UNVERIFIED. Bukan strong lead. DIAM.")
note("HIVE Agents","Run 2331: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Zero","Run 2331: totalMinted 307->314 (+7), rate 0,143/mnt vs prev 2,6886 = 0,05x — velocity GAGAL; freeMinted 314/500 = 62,8% (FREE_CAP 500), slot terbuka, mintOpen 1. Umur <24 jam s.d. 07:55 WIB 14 Nov. Bukan strong lead (<70%). DIAM.")
note("Oliver Agents","Run 2331: totalSupply 1028->1031 (+3), freeMinted 981/1000 = 98,1%; AGE-EXCLUDED (sudah dilaporkan hot leg 21:00 WIB). DIAM.")
note("Royal Rush Agents","Run 2331: totalSupply 910->914 (+4), rate 0,082/mnt vs prev 0,1202 = 0,68x — velocity GAGAL; freeMinted 917/1000 = 91,7%, freeRemaining 83, slot terbuka; umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM.")
note("Mossbound Key","Run 2331: totalSupply 327 FLAT, freeMinted 325/325 = 100%, freeRemaining 0 — sold out terkonfirmasi (sudah dilaporkan hot leg 14:44 WIB). DIAM.")
note("Slate Insignia","Run 2331: totalSupply 89->90 (+1), freeMinted 89/480 = 18,5%. DIAM.")
note("Dragon Agent","Run 2331: totalSupply 991->992 (+1), rate 0,020/mnt vs prev 0,0112 = 1,82x TAPI <20 token dalam interval — velocity GAGAL. DIAM.")
note("Violet Waybill","Run 2331: totalSupply 133 FLAT, freeMinted 132/1230 = 10,7%. DIAM.")
note("Cinder Crucible","Run 2331 (blok 133388727): totalSupply 112->221 (+109), rate 2,22/mnt, prev rate 0,0 — rasio tak terhitung, velocity TIDAK dihitung lolos; freeMinted 221/325 = 68,0% pada bacaan ini. Hot-leg 23:51 WIB membaca 231/325 = 71,1% (lebih segar) dan SUDAH melaporkan sebagai track-C lead gate-blocked — run ini DIAM, tidak lapor ulang.")
note("Agent Bubble","Run 2331: totalSupply 1353->1389 (+36), rate 0,734/mnt vs prev 1,0259 = 0,72x — velocity GAGAL; free% TETAP UNVERIFIED (FREE_SUPPLY null). Bukan kandidat. DIAM.")
note("Moss Signal","Run 2331: totalSupply 805 FLAT. DIAM.")
note("AGENT COSMOS","Run 2331: totalSupply 5389->5393 (+4), rate 0,082/mnt vs prev 0,1116 = 0,73x — velocity GAGAL. DIAM.")
note("HANAMI BLOOM","Run 2331: totalSupply 132 FLAT. DIAM.")
note("BUILD","Run 2331: totalSupply 204->206 (+2), freeMinted 200/200 = 100% (freeLeft 0) — free pool habis; user sudah mint. DIAM.")
note("Moon","Run 2331: totalSupply 452->486 (+34; totalMinted 460->486 = +26 vs 2231), rate ~0,69/mnt, TANPA prev rate tersimpan — velocity TIDAK dihitung lolos; free% UNVERIFIED. Bukan kandidat. DIAM.")
note("Zora Agent","Run 2331: totalSupply 4900 FLAT. DIAM.")
note("Cinder Agents","Run 2331: totalSupply 297 FLAT, freeMinted 166/500 = 33,2%. DIAM.")
note("AlphaPulse Genesis Badge","Run 2331: totalSupply 220->221 (+1), rate 0,020/mnt vs prev 0,0354 = 0,58x — velocity GAGAL. DIAM.")
note("PROMPTPIRATES","Run 2331: totalSupply 602 FLAT. DIAM.")
note("RAMRAIDERS","Run 2331: totalSupply 681 FLAT. DIAM.")
note("Lucky Catch","Run 2331: totalSupply 22 FLAT. DIAM.")
note("Cobalt Agent","Run 2331: totalSupply 4900 FLAT. DIAM.")
note("Thor","Run 2331: totalSupply 4901 FLAT. DIAM.")
note("Vexa","Run 2331: totalSupply 4900 FLAT. DIAM.")
note("SYNERGYPASS","Run 2331: totalSupply 302 FLAT, freeMinted 302/1111 = 27,2%. DIAM.")
note("SUDOSAINTS","Run 2331: totalSupply 778->780 (+2), rate 0,041/mnt vs prev 0,0372 = 1,10x — velocity GAGAL. DIAM.")
note("AgentRune","Run 2331: totalSupply 205 FLAT. DIAM.")
note("0x7Eb9","Run 2331: totalSupply 1257->1259 (+2), rate 0,041/mnt vs prev 0,2072 = 0,20x — velocity GAGAL. DIAM.")
note("MORFO","Run 2331: totalMinted 434->455 (+21), rate ~0,43/mnt, TANPA prev rate tersimpan — velocity TIDAK dihitung lolos; MAX_SUPPLY 25000, mintOpen 1; free% UNVERIFIED. Tetap early lead. DIAM. (Boltbook EN 23:25 WIB: 435/25.000.)")
note("FERO","Run 2331: totalMinted 8->13 (+5), window buka 23:00 WIB; free% ~13/3333 = 0,4%. Bukan kandidat/strong lead/early. Tetap watchlist-only. DIAM.")
note("0xd8dA6BF2","Run 2331: SEMUA view null (totalSupply/MAX_SUPPLY/mintOpen/freeMinted/FREE_SUPPLY/balanceOf) — view tidak terbaca (revert/ABI tidak cocok); nilai snapshot dipertahankan. DIAM.")
note("Ochre","Run 2331 (retry, blok 133389464): totalSupply 211, freeMinted 210/210 = 100%, freeRemaining 0, isFreeOpen 0, saleStart 1794556267 = 2026-11-13 14:51:07 WIB — SOLD OUT terkonfirmasi (sudah dilaporkan hot leg 15:19 WIB). Alamat kontrak dilengkapi di entri ini (sebelumnya null). DIAM.")
note("Mihao","Run 2331 (retry): totalSupply 503->508 (+5), MAX_SUPPLY 2999, mintOpen 1, balanceOf(user) 0. DIAM.")
note("Kitebots","Run 2331 (retry): totalSupply 1264 FLAT, freeMinted 1264, FREE_CAP 3280, MAX_SUPPLY 4000. DIAM.")
note("PIXELPHARAOH","Run 2331 (retry, blok 133389464): totalSupply 899->908 (+9), MAX_SUPPLY 5555, mintOpen 1, balanceOf(user) 0; free% UNVERIFIED. DIAM.")
# Ochre: fix missing address (generic merge could not match it)
och=snap["contracts"].get("Ochre")
if och and not och.get("address"):
    och["address"]="0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
    for fk,fv in retry["reads"]["Ochre"]["views"].items():
        if fv is not None: och[fk]=fv
    och["lastReadBlock"]=RB; och["lastReadWib"]=NOW
# LNFT: not in snapshot contracts — check alternate key 'Laptop NFT'
lnft_key = "Laptop NFT" if "Laptop NFT" in snap["contracts"] else None
if lnft_key:
    ent=snap["contracts"][lnft_key]
    ent["runNote2331"]=("Run 2331: retry GAGAL lagi (transport null, ke-2 kalinya berturut-turut); nilai snapshot dipertahankan "
      "(totalSupply 338 dari 2231). Hot-leg sudah melaporkan sebagai early lead 21:35 WIB. DIAM.")
    print("LNFT found under key:", lnft_key)
else:
    snap["contracts"]["LNFT"]={
     "address":"0xb2ac84b0d2c9684436f2cf2dc7dfc8e80be78657",
     "name":"Laptop NFT","symbol":None,"kind":"ERC721",
     "status":"watchlist-only-hot-leg-early-lead-2026-11-13",
     "totalSupply":338,
     "note":"Hot-leg melaporkan sebagai early lead 21:35 WIB 13 Nov. Main job: bacaan run 2231 totalSupply 327->338 (+11); run 2331 verify + retry KEDUANYA gagal transport (null) — nilai dipertahankan, bukan nol. TIDAK dilaporkan ulang oleh main job.",
     "lastReadBlock":133382185,"lastReadWib":NOW,
     "runNote2331":"Run 2331: verify + retry GAGAL transport (null). Nilai snapshot dipertahankan. DIAM.",
    }
    print("LNFT added to snapshot (was absent)")
# CDD8: all views null, no snapshot entry — record as checked in run log only (not added)
# --- new early lead: Race Agents ---
snap["contracts"]["Race Agents"]={
 "address":"0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
 "name":"Race Agents","symbol":"RACEAGENTS",
 "kind":"ERC721 (AGENT_ID_REGISTRY + FREE_MAX + freeMinted + mintOpen)",
 "status":"early-lead-reported-2026-11-13",
 "totalSupply":323,"freeMinted":323,"FREE_MAX":1000,"MAX_SUPPLY":5000,"mintOpen":1,
 "balanceOf_user":0,
 "firstSeenWib":"2026-11-13 ~20:25 WIB (probe hot-leg: freeMinted 3)",
 "discovery":"Boltbook front page EN run 2331 (2 post: Race Agents 319/5.000 + Race Pass 20/5.000) + Sourcify feed hot-leg 2024",
 "ageNote":"Umur launch: first-mint bound ~20:25 WIB 13 Nov (probe hot-leg freeMinted 3 -> 323 run ini), <24 jam; waktu launch resmi proyek UNVERIFIED.",
 "freePctVerified":32.3,
 "freeNote":"Free% TERVERIFIKASI 323/1000 = 32,3% (freeMinted/FREE_MAX). Slot user: freeClaimed view ABSEN (tidak terbaca); pool terbuka + balanceOf(user) 0 — slot kemungkinan terbuka, TIDAK terverifikasi via view langsung.",
 "website":None,"websiteNote":"Website UNVERIFIED (contract-address + project-name search run 2331: tidak ada situs proyek ditemukan).",
 "xNote":"X UNVERIFIED.",
 "note":"EARLY LEAD dilaporkan sekali run 2331: agent-shaped (registry + FREE_MAX + freeMinted), mint pertama terverifikasi on-chain run ini (323, minting live +316 sejak 20:28 WIB), belum ada entri snapshot. Bukan strong lead (<70%) / kandidat (velocity belum ada baseline; X + website unverified). TIDAK pernah preview/mint.",
 "lastReadBlock":133385943,"lastReadWib":NOW,
}
# --- new early lead: Crown Racer Cards (0x7B1ca439) ---
snap["contracts"]["Crown Racer Cards"]={
 "address":"0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
 "name":"Crown Racer Cards","symbol":"CRACE",
 "kind":"ERC721 (agentId()=registry + FREE_QUOTA + freeMinted + freeClaimed + mintFree)",
 "status":"early-lead-reported-2026-11-13",
 "totalSupply":299,"totalMinted":299,"freeMinted":297,"FREE_QUOTA":500,"mintOpen":1,
 "freeClaimed_user":0,"nextFreeId":298,
 "owner":"0xe0d90c1e7cb4e7c36b096bde4ff618e91118c8e1",
 "firstSeenWib":"2026-11-13 ~23:19 WIB (hot-leg feed poll; Sourcify verifiedAt 16:03:07Z = 23:03:07 WIB)",
 "discovery":"Sourcify recently-verified feed run 2331 (49 fns) + probe run ini",
 "ageNote":"Umur launch: first-mint bound ~23:19 WIB 13 Nov (pertama terlihat hot-leg), <24 jam; waktu launch resmi proyek UNVERIFIED.",
 "freePctVerified":59.4,
 "freeNote":"Free% TERVERIFIKASI 297/500 = 59,4% (freeMinted/FREE_QUOTA). Slot user TERBUKA (freeClaimed(user)=0).",
 "website":None,"websiteNote":"Website UNVERIFIED (belum dicari — early lead, bukan kandidat).",
 "xNote":"X UNVERIFIED.",
 "note":"EARLY LEAD dilaporkan sekali run 2331: agent-shaped (agentId() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis + FREE_QUOTA + freeMinted), mint pertama terverifikasi on-chain run ini (299 total, 297 free), belum ada entri snapshot, hot-leg TIDAK melaporkan. Bukan strong lead (59,4% < 70%) / kandidat (velocity belum ada baseline; X + website unverified). TIDAK pernah preview/mint.",
 "lastReadBlock":133389512,"lastReadWib":NOW,
}
# --- RELIC: free lane exhausted, checked only ---
snap["contracts"]["Relics of the First Agents"]={
 "address":"0x3A82dd3c9Df165D89259a8ec1eCC6CF91D7AEC4E",
 "name":"Relics of the First Agents","symbol":"RELIC",
 "kind":"ERC721 (agentFreeCap/agentFreeUsed + xFreeCap/xFreeUsed)",
 "status":"checked-free-pool-exhausted-2026-11-13",
 "totalMinted":502,"agentFreeCap":500,"agentFreeUsed":500,"xFreeCap":250,"xFreeUsed":1,
 "balanceOf_user":0,
 "discovery":"Sourcify recently-verified feed run 2331 (hot-leg first seen 02:12:41 WIB 13 Nov)",
 "note":"Checked run 2331: free lane AGENT HABIS (agentFreeUsed 500/500), xFreeUsed 1/250. BUKAN lead — TIDAK dilaporkan.",
 "lastReadBlock":133385943,"lastReadWib":NOW,
}
# --- Ponke: first-read watchlist ---
snap["contracts"]["Ponke"]={
 "address":"0x0c222b11a380df4f68cee7cacb162357e60c7215",
 "name":"Ponke","symbol":None,
 "kind":"token-mint (totalSupply satuan wei + totalMinted/freeMinted)",
 "status":"watchlist-only-first-read-2026-11-13",
 "totalSupply":450000000000000000000000000000,"totalMinted":63,"freeMinted":63,
 "balanceOf_user":0,
 "discovery":"Boltbook front page run 2331 (carried over dari run 2231: unreadable)",
 "freePctVerified":None,
 "freeNote":"Free% UNVERIFIED (tanpa FREE_SLOTS/FREE_SUPPLY view).",
 "ageNote":"Umur launch UNVERIFIED.",
 "website":None,"websiteNote":"Website UNVERIFIED.",
 "lastReadBlock":RB,"lastReadWib":NOW,
}
# --- Feed-5877 (CPASS): quiz-gated + totalMinted 257 ---
f5877=snap["contracts"].get("Feed-5877")
if f5877:
    f5877["totalMinted"]=257
    f5877["lastReadBlock"]=RB; f5877["lastReadWib"]=NOW
    f5877["runNote2331"]=("Run 2331 (retry, blok 133389464): totalMinted 257/10000 (Boltbook ZH ~23:40 WIB menyebut 82 — "
      "angka Boltbook tertinggal/di bawah bacaan on-chain; bacaan on-chain yang dipakai), MAX_SUPPLY 10000, mintOpen 1, balanceOf(user) 0. "
      "QUIZ-GATED: mintFree(uint256) butuh jawaban kuis via answerFor(wallet) — mekanisme sama seperti SPEC/FIND. Sudah dilaporkan sekali sebagai early lead run 2231. DIAM.")
# --- S1 trio -> track_c checked (sale-shaped, free pool 0, paid-only) ---
trio={
 "S1-5106":("0x5106640f80D13e8E796b021FFb6F9735ad00a416","黃金終局金庫 GoldenVault","GVAULT","https://goldvault-bnb.surge.sh",5000000000000000,1794715472,1794593078),
 "S1-Bedf":("0xBedf504A6e383c2a46827b7151b3732D7d791a08","DualKey Genesis AI Vault","DUALKEY","https://dualkey-ai.surge.sh",6000000000000000,1794715501,1794593790),
 "S1-FA0A":("0xFA0A8297E746cf3662E1065CB4D07bD7BC230484","BlitzEV Quant Jackpot Vault","BLITZEV","https://blitzev-bnb.surge.sh",4000000000000000,1794715487,1794593094),
}
for key,(addr,name,sym,site,quote,mend,rend) in trio.items():
    snap.setdefault("track_c",{})[key]={
     "address":addr,"name":name,"symbol":sym,
     "kind":"S1 factory sale (mint + quote + free views + registry)",
     "status":"checked-paid-only-free-pool-0-2026-11-13",
     "saleShape":"PASS (S1): mint + quote + free views + AI_AGENT_REGISTRY = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
     "AI_AGENT_REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
     "FREE_SUPPLY":0,"freeMinted":0,"totalSupply":4,"totalMinted":4,"mintOpen":1,
     "quote_user_1":quote,"quote_user_1_bnb":quote/1e18,
     "MINT_END":mend,"roundEndTime":rend,
     "mintedPerWallet_user":0,"userShares_user":0,"checkAiAgent_user":1,
     "owner":"0x0000000000000000000000000000000000000000",
     "WEBSITE":site,
     "note":("Checked run 2331 (probe blok 133389512): bentuk sale S1 LENGKAP, TAPI FREE_SUPPLY = 0 dan freeMinted = 0 "
       "-> free pool NOL, dan quote(user,1) = %.4f BNB (BERBAYAR) -> BUKAN track-C lead. WEBSITE() = %s (dicatat sebagai bukti situs potensial; "
       "tidak dievaluasi lebih lanjut karena bukan lead). MINT_END ~2026-11-15 11:04 WIB; roundEndTime ~2026-11-14 01:04 WIB." % (quote/1e18, site)),
     "lastReadBlock":133389512,"lastReadWib":NOW,
    }
# --- CA76 Book 4.0 -> track_c checked (sale, mint closed, no free path) ---
snap.setdefault("track_c",{})["Feed-0xca76"]={
 "address":"0xca76405325A172803aC5682E286cE1ebCEBAcA71",
 "name":"Book 4.0","symbol":"BOOK",
 "kind":"sale (AGENT_ID_REGISTRY + LOT_PRICE + SALE_WINDOW)",
 "status":"checked-mint-closed-no-free-path-2026-11-13",
 "saleShape":"S1/S2 GAGAL: ada registry + LOT_PRICE, TAPI tanpa free view/fn; mintOpen 0",
 "AGENT_ID_REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "LOT_PRICE":1000000000000000,"SALE_WINDOW":900,"mintOpen":0,
 "totalSupply":866399999999999999999999994,
 "note":"Checked run 2331 (probe blok 133389512): agent-shaped sale, TAPI mintOpen = 0 (tutup) dan tanpa jalur gratis -> BUKAN track-C lead. TIDAK dilaporkan.",
 "lastReadBlock":133389512,"lastReadWib":NOW,
}
# --- NOTV (track_c): freeStart passed, still 0 minted ---
notv=snap.get("track_c",{}).get("NOTV")
if notv:
    notv["totalSupply"]=0; notv["totalMinted"]=0
    notv["lastReadBlock"]=VB; notv["lastReadWib"]=NOW
    notv["runNote2331"]=("Run 2331: totalSupply/totalMinted TETAP 0/2000 padahal freeStart 18:00 WIB 13 Nov SUDAH LEWAT — "
      "belum ada mint sama sekali. Tetap watchlist-only-not-open. DIAM.")
# --- pending claim binanceai.fun ---
pc=snap.get("pending_claims",{}).get("binanceai.fun")
if pc:
    pc["lastReadWib"]=NOW
    pc["runNote2331"]=("Run 2331: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 — "
      "TIDAK BERUBAH (refund phase sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")
snap["last_run"]=LAST_RUN
json.dump(snap,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("snapshot written; contracts:",len(snap["contracts"]),"track_c:",len(snap.get("track_c",{})))
