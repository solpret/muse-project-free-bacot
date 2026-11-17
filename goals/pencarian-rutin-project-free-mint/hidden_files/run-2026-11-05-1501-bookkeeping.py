"""Run 1501 bookkeeping (single stage): re-read + early-probe + track-C updates,
batch age-exclusion (53), 2 new early leads (Agent Coffee, Driftnauts).
Scan state + seen already updated by subagent A (watermark 131782180).
"""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN="2026-11-05 run 1501"
RBLK=131782166   # re-read / track-C block
PBLK=131782665   # early-probe block
VBLK=131785472   # verification block for new early leads
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1501.bak.json")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]

def upd(name, field, newval, blk, note, rate_interval=50.0, prev_rate_key="currentRatePerMin"):
    if name not in C:
        print("MISS", name); return
    e=C[name]
    prev=e.get(field)
    e[field]=newval
    if isinstance(prev,int) and isinstance(newval,int):
        minted=newval-prev
        e["previousTotalSupply"]=prev
        e["mintedInInterval"]=minted
        e["intervalMinutes"]=rate_interval
        e["currentRatePerMin"]=round(minted/rate_interval,3)
        e["previousRatePerMin"]=e.get(prev_rate_key) if isinstance(e.get(prev_rate_key),(int,float)) else None
        e["velocityLegPasses"]=False
    e["lastReadBlock"]=blk
    e["lastReadWib"]=RUN
    e["runNote1501"]=note

# --- Track A re-read (blok 131782166; interval ~50 mnt vs run 1431) ---
upd("HIVE Agents","totalSupply",1242,RBLK,
 "Run 1501 (blok 131782166): 1242 flat vs 1431 (1242) -> velocity GAGAL; balance 1; minted-by-user, bukan kandidat.")
upd("Tigora-E8c4","totalMinted",603,RBLK,
 "Run 1501: totalMinted 601->603 (+2, <20) -> velocity GAGAL.")
upd("BNBRunnerz-2674","totalSupply",3207,RBLK,
 "Run 1501: 3191->3207 (+16, <20) -> velocity GAGAL.")
upd("Blobbies-a7fB","totalSupply",1417,RBLK,
 "Run 1501: 1416->1417 (+1, <20) -> velocity GAGAL.")
upd("Jolly","totalMinted",3382,RBLK,
 "Run 1501: totalMinted 3361->3382 (+21, ~0,42/mnt vs 0,333 tersimpan = 1,26x <1,5x) -> velocity GAGAL; umur ~40 jam (first mint 2026-11-03 23:27:33 WIB) <=48 jam -> tetap strong-lead-gate-blocked, tanpa laporan perubahan.")
upd("HACKED","totalSupply",3340,RBLK,
 "Run 1501: 3312->3340 (+28, ~0,56/mnt vs 1,0 tersimpan = 0,56x) -> velocity GAGAL; minted-by-user (balance 2), bukan kandidat.")
upd("SoulAgent","totalSupply",672,RBLK,
 "Run 1501: 670->672 (+2, <20) -> velocity GAGAL; tetap EARLY.")
upd("PERSONA-A930","totalSupply",1120,RBLK,
 "Run 1501: 1120 flat -> velocity GAGAL; tetap EARLY.")
upd("AFROG","totalSupply",329,RBLK,
 "Run 1501: 323->329 (+6, <20) -> velocity GAGAL; free 329/1111 = 29,6% (>=25%) TAPI umur peluncuran tetap UNVERIFIED -> watchlist-only, BUKAN promosi strong lead.")
C["AFROG"]["freeClaimed"]=329; C["AFROG"]["freePctVerified"]=29.61
upd("Saturnode","totalSupply",1746,RBLK,
 "Run 1501: 1729->1746 (+17, <20) -> velocity GAGAL; free 1723/4000 = 43,1%; umur tetap UNVERIFIED -> tetap EARLY.")
C["Saturnode"]["freeClaimed"]=1723; C["Saturnode"]["freePctVerified"]=43.08
for k,sup,free,pool in [("Swarmcentaur",777,772,5),("Agentyyds",600,595,5),("Pilotneon",500,495,5),("Mummyhive",600,582,18)]:
    if k in C:
        C[k].update({"totalSupply":sup,"freeClaimed":free,"lastReadBlock":RBLK,"lastReadWib":RUN,
                     "runNote1501":f"Run 1501: totalSupply {sup}, freeClaimed {free} flat — free pool tersisa {pool}, BUKAN sold out; tanpa perubahan tier."})
upd("StarAgent-7d39","totalSupply",985,RBLK,
 "Run 1501: totalSupply 975->985 (+10); claimedFree(user)=0; tetap EARLY.")
# Shroomies + RigOrb: NOT in snapshot (reread-only); notes live in run log only.

# --- Early-probe (blok 131782665; interval ~53 mnt vs run 1431) ---
def upd_early(name, supply, free, cap, note):
    if name not in C:
        print("MISS", name); return
    e=C[name]
    prev=e.get("totalSupply")
    e["totalSupply"]=supply
    if free is not None: e["freeClaimed"]=free
    if cap is not None:
        e["FREE_CAP"]=cap
        e["freePctVerified"]=round(100.0*free/cap,2) if isinstance(free,int) else None
    if isinstance(prev,int) and isinstance(supply,int):
        e["previousTotalSupply"]=prev
        e["mintedInInterval"]=supply-prev
        e["intervalMinutes"]=53.0
        e["currentRatePerMin"]=round((supply-prev)/53.0,3)
        e["velocityLegPasses"]=False
    e["lastReadBlock"]=PBLK
    e["lastReadWib"]=RUN
    e["runNote1501"]=note
upd_early("Thronemind",461,461,2000,
 "Run 1501: 431->461 (+30); free 461/2000 = 23,05% <25% -> tetap EARLY; slot terbuka.")
upd_early("Hashseers",465,465,2000,
 "Run 1501: 436->465 (+29); free 465/2000 = 23,25% <25% -> tetap EARLY; slot terbuka.")
upd_early("Layerloom",477,477,2000,
 "Run 1501: 414->477 (+63); free 477/2000 = 23,85% <25% -> tetap EARLY; slot terbuka.")
upd_early("Cachejack",344,344,2000,
 "Run 1501: 290->344 (+54); free 344/2000 = 17,2% <25% -> tetap EARLY; slot terbuka.")
upd_early("AgentMiner",558,None,None,
 "Run 1501: totalSupply 499->558 (+59). Free % tetap UNVERIFIED (free views revert; ABI: freeFor/freeLeft/freeUsed, tanpa counter free-cap). Tetap EARLY.")
upd_early("Smeltbots",460,460,2000,
 "Run 1501: 405->460 (+55); free 460/2000 = 23,0% <25% -> tetap EARLY; slot terbuka.")
upd_early("Tumblebots",465,465,2000,
 "Run 1501: 393->465 (+72); free 465/2000 = 23,25% <25% -> tetap EARLY; slot terbuka.")
upd_early("Neurolucha",347,347,800,
 "Run 1501: 335->347 (+12); free 347/800 = 43,38% — strong lead gate-blocked, tanpa perubahan; TIDAK di-preview/di-mint.")
upd_early("Roguefall",196,196,2000,
 "Run 1501: 190->196 (+6); free 196/2000 = 9,8% -> tetap EARLY; slot terbuka.")
upd_early("Agent Goats",111,111,1111,
 "Run 1501: 109->111 (+2); free 111/1111 = 9,99% -> tetap EARLY; slot terbuka (mintedBy(user)=0).")
upd_early("Agent Owls",107,107,1111,
 "Run 1501: 105->107 (+2); free 107/1111 = 9,63% -> tetap EARLY; slot terbuka (mintedBy(user)=0).")
upd_early("Hirelings-A",119,119,2000,
 "Run 1501: 116->119 (+3); free 119/2000 = 5,95% -> tetap EARLY; slot terbuka.")
upd_early("Hirelings-B",90,90,2000,
 "Run 1501: 86->90 (+4); free 90/2000 = 4,5% -> tetap EARLY; slot terbuka.")
upd_early("Forklings",130,130,2000,
 "Run 1501: 126->130 (+4); free 130/2000 = 6,5% -> tetap EARLY; slot terbuka.")
upd_early("Auspibots",134,134,2000,
 "Run 1501: 131->134 (+3); free 134/2000 = 6,7% -> tetap EARLY; slot terbuka.")
for key in ["Pacture"]:
    if key in C:
        C[key].update({"lastReadBlock":PBLK,"lastReadWib":RUN,
            "runNote1501":"Run 1501: sharesMinted 10489->10520 (+31), freeMinted 7700 flat, paidShares 2789->2820; freeClaimed(user)=1."})
    else:
        print("MISS", key, "(PACT re-read hanya di run log)")
for pat in ["MEOW","WAGA"]:
    hits=[k for k in C if pat.lower() in k.lower()]
    print(pat, "snapshot keys:", hits)

# --- Track C notes (blok 131782166) ---
TC=s.get("track_c",{})
def tcn(key, note):
    if key in TC: TC[key]["runNote1501"]=note
    else: print("TC MISS", key)
tcn("OSK","Run 1501: opened 0, totalMinted 2277 flat — tidak berubah (belum dibuka).")
tcn("NIULAI","Run 1501: launched 0, phase 4 — tidak berubah (arti enum phase 4 MASIH belum terverifikasi).")
tcn("KillZero-K0-sale","Run 1501: launched 0 — tidak berubah.")
tcn("DROID","Run 1501: opened 0, freeMinted 557->558 (+1), totalMinted 557 flat — tidak berubah.")
tcn("IMARS","Run 1501: opened 1, freeMinted 300 flat, totalMinted 624 flat — pool gratis tetap habis, bukan lead.")
tcn("ASOC-43cE","Run 1501: freeClaimed(user) 0, saleEnded 0 — masih pre-open, TIDAK di-preview/di-mint.")
tcn("SENBAZURU-b215","Run 1501: opened 1, freeClaimed 222->224 (+2 mint pihak lain), hasFreeShare(user)=1 (slot user terpakai); paidSold tidak dibaca run ini.")
tcn("FABE","Run 1501: launched 0, freeSharesRemaining 2821, freeSharesClaimed(user)=1 — slot user sudah dipakai, tidak berubah.")
tcn("ShibAgent-R2","Run 1501: freeClaimed 125->126 (+1), phase 1, balanceOf(user)=0 — tanpa perubahan tier.")
tcn("QAGENT-2","Run 1501: freeMinted 6666 flat, sharesMinted 6702 flat — free pool habis, tidak berubah.")
bkeys=[k for k in TC if "binanceai" in k.lower()]
print("BINANCEAI track_c keys:", bkeys)
if bkeys:
    TC[bkeys[0]]["runNote1501"]="Run 1501: launched 0, totalShares 3110, isRefundPhase 1, failed 1 — tetap refund/failed, tidak berubah."

# --- Batch age-exclusion (53; false positive Neonnodefox + Pepe420 DIPERTAHANKAN) ---
cands=json.load(open(f"{BASE}/run-2026-11-05-1501-age-candidates.json"))
m1=json.load(open(f"{BASE}/run-2026-11-05-1501-age-reads-merged.json"))
b3=json.load(open(f"{BASE}/run-2026-11-05-1501-age-reads-batch3.json"))
reads={}
for src in (m1,b3):
    for k,v in src.items():
        if k not in ("block","note"): reads[k]=v
FP={"Neonnodefox","Pepe420"}
def rd(d, fn):
    v=d.get(fn)
    return v if isinstance(v,int) else ("revert" if isinstance(v,dict) else v)
removed=[]
for name, meta in cands.items():
    if name in FP:
        print("FP retained (not excluded):", name); continue
    if name not in C:
        print("AGE MISS (not in contracts):", name); continue
    old=C.pop(name)
    d=reads.get(name, {})
    sup=rd(d,"totalSupply()"); tm=rd(d,"totalMinted()")
    if sup=="revert" or sup is None: sup=tm
    free=rd(d,"freeClaimed()")
    if free=="revert" or free is None: free=rd(d,"freeMinted()")
    cap=rd(d,"FREE_SUPPLY()")
    if cap=="revert" or cap is None: cap=rd(d,"FREE_CAP()")
    mx=rd(d,"MAX_SUPPLY()")
    blk = b3.get("block") if name in b3 else m1.get("block")
    pool_note=""
    if isinstance(free,int) and isinstance(cap,int) and free>=cap and isinstance(sup,int) and isinstance(mx,int) and sup<mx:
        pool_note=" (free pool habis, totalSupply < MAX — preseden Praxion run 1431)"
    s.setdefault("excluded",{})[name]={
        "address": old.get("address"), "symbol": old.get("symbol"), "track": "A",
        "status": "excluded-age-over-48h-2026-11-05",
        "note": f"Age-excluded run 1501 (batch): first mint TERVERIFIKASI {meta['firstMintWib']} (sumber: {meta['src']}, launchNote snapshot). Umur {meta['age_h']} jam >48 jam pada run 1501 (~15:30 WIB) dan BELUM sold out (bacaan segar run 1501 blok {blk}: totalSupply/totalMinted {sup}, free {free}/{cap}, MAX_SUPPLY {mx}){pool_note}. Dihapus dari watchlist aktif per aturan 48 jam; status lama {meta['status']}. Dilaporkan sekali sebagai perubahan (batch age-exclusion) ke parent run 1501; tidak di-preview/di-mint.",
        "previous_status": meta["status"],
        "firstMintWib": meta["firstMintWib"],
        "lastReading": f"totalSupply/totalMinted {sup}, free {free}/{cap}, MAX_SUPPLY {mx} (run 1501 blok {blk})",
    }
    removed.append(name)
print("Batch age-excluded:", len(removed))
print("Removed:", ", ".join(removed))

# --- 2 new early leads ---
C["Agent Coffee"]={
 "address":"0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010","name":"Agent Coffee","symbol":"AGF","kind":"ERC721",
 "status":"early-lead-reported-2026-11-05",
 "totalSupply":326,"freeMinted":None,"FREE_CAP":None,"freePctVerified":None,"paidMinted":None,
 "MAX_SUPPLY":4444,"mintOpen":1,"PRICE_BNB":0.02,"MAX_PER_WALLET":5,"CF_PER_MINT":15000,
 "token":"0x2e7B277357DE2E9C465A1B9216D2e220Db0eEC8d",
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot TERBUKA (blok 131785472): quote(user,1)=0, freeLeft(user)=1, freeUsed(user)=0, mintedBy(user)=0, balanceOf(user)=0. NOT preview-verified (early leads are never previewed).",
 "firstMintBlock":131779892,"firstMintWib":"2026-11-05T14:51:30+07:00",
 "firstSeenBlock":131780187,"scanMints":121,"scanMinters":121,
 "scanNote":"Scan run 1501 window 131780181-131782180: first-seen sejati, first_block scan 131780187; 121 mint / 121 minter berbeda dalam jendela. Sourcify verified (exact_match); ABI memuat freeFor/freeLeft/freeUsed + AGENT_REGISTRY = registry persis (0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F).",
 "launchNote":"First mint TERVERIFIKASI on-chain run 1501: binary-search Ankr getLogs (Transfer-from-zero) -> blok 131779892 = 2026-11-05 14:51:30 WIB; umur ~45 menit pada 15:30 WIB, <=48 jam.",
 "baselineNote":"Baseline run 1501 (blok 131785472): totalSupply 326/4444, mintOpen 1, PRICE 0,02 BNB (jalur berbayar), MAX_PER_WALLET 5. Setiap mint menghasilkan 15.000 CF (token COFFE 0x2e7B277357DE2E9C465A1B9216D2e220Db0eEC8d — di-shape-check 5c run 1501: ERC-20 biasa, bukan S1/S2). Free % UNVERIFIED: freeMinted()/freeClaimed()/FREE_CAP()/FREE_SUPPLY() semuanya revert — tidak ada counter free total; % total supply TIDAK BOLEH dipakai sebagai pengganti.",
 "gateNote":"Website UNVERIFIED run 1501: (H) contractURI() = base64 JSON {name, description} TANPA external_link; (A)/(G) pencarian nama + alamat kontrak tidak menemukan situs/proyek (hanya materi generik Agent ID); X/discussion UNVERIFIED. -> EARLY only, NOT strong lead (free % unverified), NOT candidate, NOT previewed/minted.",
 "lastReadBlock":VBLK,"lastReadWib":RUN,
}
C["Driftnauts"]={
 "address":"0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b","name":"Driftnauts","symbol":"DRFT","kind":"ERC721",
 "status":"early-lead-reported-2026-11-05",
 "totalSupply":312,"freeMinted":312,"FREE_CAP":2640,"freePctVerified":11.82,"paidMinted":0,
 "MAX_SUPPLY":4000,"PAID_CAP":1360,"FREE_PCT":66,"PRICE_BNB":0.0005,
 "userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot TERBUKA (blok 131785472): canFreeMint(user)=1, claimedFree(user)=0, balanceOf(user)=0; quote(user,1) revert (selector quote berbeda — slot dibuktikan canFreeMint+claimedFree). NOT preview-verified (early leads are never previewed).",
 "firstMintBlock":131779452,"firstMintWib":"2026-11-05T14:48:12+07:00",
 "firstSeenBlock":131780182,"scanMints":108,"scanMinters":108,
 "scanNote":"Scan run 1501 window 131780181-131782180: first-seen sejati, first_block scan 131780182; 108 mint / 108 minter berbeda dalam jendela. Sourcify verified (exact_match); ABI memuat FREE_CAP/FREE_PCT/canFreeMint/claimedFree/freeMint/freeMinted + REGISTRY() = registry persis.",
 "launchNote":"First mint TERVERIFIKASI on-chain run 1501: binary-search Ankr getLogs (Transfer-from-zero) -> blok 131779452 = 2026-11-05 14:48:12 WIB; umur ~48 menit pada 15:30 WIB, <=48 jam.",
 "baselineNote":"Baseline run 1501 (blok 131785472): totalSupply 312, freeMinted 312/2640 = 11,82% (<25% -> BUKAN strong lead), MAX_SUPPLY 4000, PAID_CAP 1360, paidMinted 0, PRICE 0,0005 BNB, FREE_PCT 66.",
 "gateNote":"Website UNVERIFIED run 1501: (H) contractURI() revert (tidak ada di ABI); (A)/(G) pencarian nama + alamat kontrak tidak menemukan situs/proyek (hanya materi generik + 'Drifters' yang tidak terkait); X/discussion UNVERIFIED. -> EARLY only, NOT strong lead, NOT candidate, NOT previewed/minted.",
 "lastReadBlock":VBLK,"lastReadWib":RUN,
}
print("Added early leads: Agent Coffee, Driftnauts")

# --- Run notes ---
s["runNote1501"]="Run 1501 (2026-11-05 15:01 WIB): 2 EARLY LEAD BARU (Agent Coffee AGF 0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010, first mint 14:51:30 WIB, slot terbuka quote 0, free % UNVERIFIED; Driftnauts DRFT 0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b, first mint 14:48:12 WIB, free 312/2640 = 11,82%, slot terbuka) — keduanya agent-shaped + first mint terverifikasi, website/X UNVERIFIED -> EARLY only, TIDAK di-preview/di-mint. AGE-EXCLUDED batch 53 item gelombang 2026-11-02/03 (first mint terverifikasi >48 jam, belum sold out, bacaan segar run 1501) -> dipindah ke excluded; Neonnodefox + Pepe420 DIPERTAHANKAN (false positive: timestamp cocok adalah Sourcify verifiedAt, bukan first mint); item minted-by-user + promotion-discarded dipertahankan. RACKRUSH dievaluasi ulang -> tetap BUKAN lead (bukan agent-shaped: tanpa registry/AgentGate; website UNVERIFIED; free 314/400 = 78,5%, umur ~8 jam). 0xUN_minter bukan lead (klaim belum dibuka, umur ~87 jam). Scan: 378 NFT + 701 ERC-20, 80 panggilan Ankr, 0 error, gap 131778154-131780180 dilewati (cap 2000). 5c: 7 ERC-20 baru di-shape-check, 0 lolos S1/S2; 75 dgn mint_count>=10 semuanya sudah terperiksa (68 lama + 7 baru), 0 dibuang sampling limit. Track-B: tidak ada pending claim; BINANCEAI tetap refund/failed. Track-C: tidak ada lead/kandidat baru."
s["runNote1501_scan"]="Scan run 1501: jendela 131780181-131782180 (2000 blok, cap), head 131782180, watermark lama 131778153; gap 131778154-131780180 (2027 blok) dilewati. 80 panggilan Ankr, 0 error, ~17 menit. 378 NFT + 701 ERC-20. First-seen sejati 6: 2 agent-shaped (Agent Coffee AGF, Driftnauts DRFT) + 4 bukan agent-shaped (Staking TMX, DAC Arena, TPR World Slot Pass, Overtime Slave Memorial — masing-masing 1 mint)."
s["runNote1501_age_exclusions"]="Run 1501 AGE-EXCLUSIONS (53 item, dilaporkan sekali sebagai perubahan): AI Gremlins, Abyss Agent, Agent Finance, Agent Raccoons, AgentMirage, Anubis Agents, Arachnoire, Bot Cats, Byte Punks, Caravan Agent, Chain Rascals, Cilok Cats, Cosmofawn, DropMiners, Fenara, Flora Agent, Gearpixel, Glasscore, Glitchronin, Gloamwick, Griffinko, Gryphora, Gungunglow, Halo Agent, Jelly Agent, Kelp Agent, Kigae, Lyra Agent, Neural Frogs, NeuralAtlas, Onyx Agent, Opera Agent, Orbitessa, Plaguelume, Plutoko, Prompt Dogs, Pumpkarrow, Qilinara, Sentrix, Silicomonk, Silk Agent, Skelebop, Strawgrim, Syntaxia, Tangpinku, Venuspi, Wailumbra, Witchlet, Wraithmoth, Yunjin Agent, Yydsgent, Zephyr Agent, Zephyrix — semuanya first mint terverifikasi 49,7-84,9 jam (>48 jam) dan belum sold out per bacaan segar run 1501 -> DIHAPUS dari kontrak aktif, dipindah ke excluded (status excluded-age-over-48h-2026-11-05). DIPERTAHANKAN: Neonnodefox + Pepe420 (false positive seleksi: timestamp yang cocok adalah Sourcify verifiedAt, bukan first mint), semua item minted-by-user, dan promotion-discarded-same-owner (Gearpixel, Skelebop, Witchlet, Venuspi, Griffinko, Tangpinku — aturan umur tetap berlaku karena status mereka early-lead-reported, bukan promotion-discarded)."
s["last_run"]="2026-11-05 run 1501"
s["last_run_wib"]="2026-11-05 run 1501"
s["last_run_note"]=s["runNote1501"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("bookkeeping done; contracts now:", len(s["contracts"]), "excluded now:", len(s.get("excluded",{})))
