#!/usr/bin/env python3
"""Snapshot update for free-mint-search run 2026-11-13 22:31 WIB.
Merges run-2026-11-13-2231-verify.json + -retry.json + -probe2.json into
onchain-snapshot.json (fresh read, then write). No preview/mint."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
verify=json.load(open(BASE+"run-2026-11-13-2231-verify.json"))
retry=json.load(open(BASE+"run-2026-11-13-2231-retry.json"))
probe2=json.load(open(BASE+"run-2026-11-13-2231-probe2.json"))
READS={}
for src in (verify,retry):
    for k,v in src["reads"].items():
        if v.get("views") is not None: READS[k]=v
for k,v in probe2["reads"].items():
    if v.get("views") is not None: READS[k]=v
VB=verify.get("block")  # 133382185
NOW="2026-11-13 ~23:20 WIB"
# map snapshot contract key -> address (lower)
def norm(a): return (a or "").lower()
updated=[]
# generic merge by address
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
    ent["lastReadBlock"]=VB
    ent["lastReadWib"]=NOW
    updated.append(key)
print("generic-merged:",len(updated))
def note(key,text):
    ent=snap["contracts"].get(key)
    if ent is not None: ent["runNote2231"]=text
# --- velocity + status notes (interval 2201->2231 ~73 min wall clock; block diff 8491 ~64 min chain time) ---
note("Agent Bubble","Run 2231 (retry, blok ~133382xxx): totalSupply 1240->1353 (+113), freeMinted 1126->1221 (+95); rate ~1,43-1,55/mnt vs prev 1,0259 = ~1,4-1,5x — BORDERLINE, dalam galat ukur interval (64-77 mnt), TIDAK dihitung lolos bersih; free% TETAP UNVERIFIED (FREE_SUPPLY null; cap 1.111 terbukti salah — free terus tercetak). Bukan kandidat/strong lead. DIAM.")
note("Zero","Run 2231 (retry): totalMinted 307->314 (+7), freeMinted 314/500 = 62,8% (FREE_CAP 500), slot terbuka (balanceOf 0), mintOpen 1; velocity GAGAL (+7/73 mnt = 0,09/mnt vs prev 2,69 = 0,03x). Umur <24 jam s.d. 07:55 WIB 14 Nov. Bukan strong lead (<70%). DIAM.")
note("Pickgrid Pickaxe","Run 2231: freeMinted 216/300 = 72,0% FLAT (totalSupply 218 flat), umur TETAP UNVERIFIED (tanpa mintStart; first-mint terblokir Ankr 401). Bukan strong lead (umur unverified). DIAM.")
note("Royal Rush Agents","Run 2231: totalSupply 899->910 (+11), freeMinted 902->913/1000 = 91,3%, freeRemaining 87, slot terbuka; velocity GAGAL (+11/73 mnt = 0,15/mnt vs prev 0,12 = 1,19x <1,5x); umur TETAP UNVERIFIED. Bukan strong lead/kandidat. DIAM.")
note("MORFO","Run 2231: totalMinted 415->434 (+19), MAX_SUPPLY 25000, mintOpen 1; free% UNVERIFIED (tanpa free view). Tetap early lead. DIAM. (Boltbook recheck independen: 435/25.000.)")
note("Cinder Crucible","Run 2231: totalSupply 109->112 (+3), freeMinted 112/325 = 34,5%, slot terbuka; lead gate-blocked, tidak berubah. DIAM.")
note("Slate Insignia","Run 2231: totalSupply 89 FLAT, freeMinted 88/480 = 18,3%. DIAM.")
note("Violet Waybill","Run 2231: totalSupply 132->133 (+1), freeMinted 132/1230 = 10,7%. DIAM.")
note("HIVE Agents","Run 2231: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Oliver Agents","Run 2231: totalSupply 1028, freeMinted 978/1000 = 97,8%, freeRemaining 22; AGE-EXCLUDED (sudah dilaporkan hot leg 21:00 WIB). DIAM.")
note("Mossbound Key","Run 2231: freeRemaining 0 — sold out terkonfirmasi (sudah dilaporkan hot leg 14:44 WIB). DIAM.")
note("Ochre Medallion","Run 2231: freeRemaining 0 — sold out terkonfirmasi (sudah dilaporkan hot leg 15:19 WIB). DIAM.")
note("GoldVein","Run 2231: freeSold 500/500 — sold out terkonfirmasi (sudah dilaporkan run 2201). Catatan: post Boltbook 23:09 menyebut '12 tersisa' — DITOLAK oleh bacaan on-chain segar ini (freeSold 500 = FREE_SHARES 500). DIAM.")
note("BUILD","Run 2231: freeMinted 200/200 (freeLeft 0) — free pool habis; user sudah mint (freeClaimed_user 1, balanceOf 1). DIAM.")
note("Moon","Run 2231: totalMinted 452->460 (+8), agentIdRegistry cocok. DIAM.")
note("Zora Agent","Run 2231: totalSupply 4900 FLAT. DIAM.")
note("MECHA","Run 2231: totalMinted 1970, freeClaimed 1969. DIAM.")
note("SudoSaints","Run 2231: totalSupply 778 FLAT. DIAM.")
note("AgentRune","Run 2231: totalSupply 205 FLAT. DIAM.")
note("JNTM","Run 2231 (retry): freeClaimed 1000/1000, freeLeft 0 (TIDAK BERUBAH vs 2201), totalMinted 1212 (+10 paid), opened 0 — free pool habis, tidak ada perubahan status. DIAM.")
note("AgentMuse","Run 2231 (retry): freeClaimed 440->446/888 = 50,2%, bookedOf_user membaca 1e26 (nilai mentah, TIDAK diartikan sebagai booking user); velocity GAGAL (+6/85 mnt = 0,07/mnt). Bukan kandidat. DIAM.")
note("OUTY","Run 2231 (retry): minted 41, freeSold 41/1500 = 2,7%, slot terbuka (freeQuotaOf 1), phase 1. DIAM.")
note("PX24","Run 2231 (retry): totalSupply 527 FLAT. DIAM.")
note("SKRR","Run 2231 (retry): totalSupply 516->517 (+1). DIAM.")
note("Thor","Run 2231 (retry): totalSupply 4901 FLAT. DIAM.")
note("Cinder Agents","Run 2231: totalSupply 297 FLAT, freeMinted 166/500 = 33,2%. DIAM.")
note("Kitebots","Run 2231: totalSupply 1264 FLAT, freeMinted 1264. DIAM.")
note("Lucky Catch","Run 2231: totalSupply 22 FLAT. DIAM.")
note("Cobalt Agent","Run 2231: totalSupply 4900 FLAT. DIAM.")
note("Vexa","Run 2231: totalSupply 4900 FLAT. DIAM.")
note("SynergyPass","Run 2231: totalMinted 302 FLAT. DIAM.")
note("Mihao","Run 2231: totalSupply 495->503 (+8). DIAM.")
note("Laptop NFT","Run 2231: totalSupply 327->338 (+11). DIAM.")
# --- Agentx: AGE-EXCLUDED (deadline 23:11:05 WIB 13 Nov passed) ---
ax=snap["contracts"].get("Agentx")
if ax:
    ax["status"]="age-excluded-2026-11-13"
    ax["totalMinted"]=786; ax["freeMinted"]=786; ax["totalSupply"]=786
    ax["freePctVerified"]=70.7
    ax["lastReadBlock"]=VB; ax["lastReadWib"]=NOW
    ax["runNote2231"]=("Run 2231 (retry): freeMinted 786/1111 = 70,7% (+8 vs 2201), slot TERBUKA, mintOpen 1, "
      "TAPI deadline umur 23:11:05 WIB 13 Nov (mintOpensAt 1794499865 + 24 jam) SUDAH LEWAT dan belum sold out "
      "-> AGE-EXCLUDED per aturan umur <24 jam; dihapus dari pantauan aktif. Dilaporkan sekali sebagai penutupan status "
      "(BUKAN penawaran ulang — override sudah ditolak user 'biarkan saja').")
# --- FERO: launched 23:00 WIB ---
fe=snap["contracts"].get("FERO")
if fe:
    fe["status"]="watchlist-only-launched-2026-11-13"
    fe["totalMinted"]=8
    fe["lastReadBlock"]=VB; fe["lastReadWib"]=NOW
    fe["runNote2231"]=("Run 2231: window BUKA 23:00 WIB terkonfirmasi — totalMinted 0->8 (semua via free Agent ID lane, per Boltbook 23:2x WIB). "
      "Free% ~8/3333 = 0,2% (jauh <50%); free lane social-gated (posting X + permit EIP-712). Bukan kandidat/strong lead/early "
      "(sudah dilaporkan sebagai upcoming run 2201; peluncuran saja bukan promosi tier). Tetap watchlist-only. DIAM.")
# --- new early lead: 0x5877D2bb ---
snap["contracts"]["Feed-5877"]={
 "address":"0x5877D2bb9F226cC3E438F4d656cAeb27DEAFC576",
 "name":None,"symbol":None,
 "kind":"ERC721 (mintFree + AGENT_ID gate)",
 "status":"early-lead-reported-2026-11-13",
 "totalMinted":24,"MAX_SUPPLY":10000,"mintOpen":1,"balanceOf_user":0,
 "firstSeenWib":"2026-11-13 ~22:40 WIB (Sourcify verifiedAt 2026-11-13T15:40:42Z)",
 "discovery":"Sourcify recently-verified feed run 2231 (20 kontrak, 19 checked-not-sale-shape, 1 agent-mint-shaped)",
 "ageNote":"Umur launch UNVERIFIED (verifiedAt BUKAN launch time; tanpa mintStart view; first-mint on-chain terblokir Ankr 401).",
 "freePctVerified":None,
 "freeNote":"Free% UNVERIFIED (tanpa freeMinted/FREE_SUPPLY view; mintFree() ada di ABI).",
 "website":None,"websiteNote":"Website UNVERIFIED (belum dicari — early lead, bukan kandidat).",
 "xNote":"X UNVERIFIED.",
 "note":"EARLY LEAD dilaporkan sekali run 2231: ABI Sourcify exact_match (36 fns: mintFree, mintPaid, mintOpen, AGENT_ID, holdsAgentId, MAX_SUPPLY, TIER prices); totalMinted 24/10000 saat bacaan pertama; nama/simbol gagal dibaca (egress flapping). Bukan strong lead/kandidat (umur + free% + website unverified). TIDAK pernah preview/mint.",
 "lastReadBlock":VB,"lastReadWib":NOW,
}
# --- new watchlist first-read: PIXELPHARAOH ---
snap["contracts"]["PIXELPHARAOH"]={
 "address":"0xBb90Cc15F7302Bbb7e114a5329d41dBb104F5350",
 "name":"PIXELPHARAOH","symbol":"KA",
 "kind":"ERC721",
 "status":"watchlist-only-first-read-2026-11-13",
 "totalSupply":899,"MAX_SUPPLY":5555,"mintOpen":1,"balanceOf_user":0,
 "discovery":"Boltbook front page EN run 2231 (~23:25 WIB): totalSupply 897/5555, mint(1) verified at 0 BNB",
 "freePctVerified":None,
 "freeNote":"Free% UNVERIFIED (tanpa freeMinted/FREE_SUPPLY view; post Boltbook menyebut mint(1) value 0 lolos).",
 "ageNote":"Umur launch UNVERIFIED.",
 "website":None,"websiteNote":"Website UNVERIFIED.",
 "lastReadBlock":VB,"lastReadWib":NOW,
}
# --- pending claim binanceai.fun ---
pc=snap.get("pending_claims",{}).get("binanceai.fun")
if pc:
    pc["lastReadWib"]=NOW
    pc["runNote2231"]=("Run 2231: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, refundClaimed(user)=0 — "
      "TIDAK BERUBAH (refund phase sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")
snap["last_run"]="2026-11-13T23:31+07:00"
json.dump(snap,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("snapshot written; contracts:",len(snap["contracts"]))
