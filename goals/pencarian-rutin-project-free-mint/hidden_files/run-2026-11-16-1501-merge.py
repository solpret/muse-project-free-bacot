#!/usr/bin/env python3
"""Merge run 2026-11-16 15:01 WIB into onchain-snapshot.json. Read-only on chain; writes snapshot only."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s=json.load(open(BASE+"onchain-snapshot.json"))
r15=json.load(open(BASE+"run-2026-11-16-1501-reread.json"))
r14=json.load(open(BASE+"run-2026-11-16-1401-reread.json"))
feed=json.load(open(BASE+"run-2026-11-16-1501-feedshape.json"))
BLK=r15["block"]; WIB="2026-11-16 ~15:01 WIB"
def find_entry(addr):
    for coll in ("contracts","track_c"):
        for k,v in s.get(coll,{}).items():
            if isinstance(v,dict) and (v.get("address") or "").lower()==addr.lower():
                return coll,k,v
    return None,None,None
def cur(v):
    return v.get("totalSupply") if v.get("totalSupply") is not None else v.get("totalMinted")
# previous rates per min from run 1401 note (deltas over ~30 mnt vs 1331)
prev_rate={"RAVE":18/30,"AGCLUB":17/30,"Zephyra":16/30,"AgentNOVA":16/30,"Bold Leonidas":15/30,"SPARKS":11/30,"Matrix Agents":4/30}
updated=[]
for name,rd in r15["reads"].items():
    v=rd["views"] or {}
    coll,k,ent=find_entry(rd["address"])
    if ent is None:
        print("NO SNAPSHOT ENTRY for",name,rd["address"]); continue
    v14=r14["reads"].get(name,{}).get("views") or {}
    c15,c14=cur(v),cur(v14)
    delta=(c15-c14) if (c15 is not None and c14 is not None) else None
    rate=(delta/60.0) if delta is not None else None
    pr=prev_rate.get(name)
    ratio=(rate/pr) if (rate is not None and pr) else None
    vel = bool(delta is not None and delta>=20 and ratio is not None and ratio>=1.5)
    # write fresh views
    for f in ("totalSupply","totalMinted","freeMinted","freeClaimed","freeLeft","FREE_SUPPLY","FREE_CAP","MAX_SUPPLY","mintOpen","paused","priceFor_user","freeUsed_user","balanceOf_user","mintedBy_user","freeClaimed_user","freeMintedBy_user","hasAgentId_user","mintedPerWallet_user","freeMintedPerWallet_user","holdsAgentId_user","mintsBy_user","mintCountOf_user","freeSharesLeft","openedAt","freeBooked_user","freeRemaining","FREE_MAX","paidMinted","mintPrice","totalSpecimens","currentExperiment","genesisStart","genesisOpen","priceFor_user_1","mintPriceFor_user_1","cost_user_1","mintsLeft","FREE_MINT_CAP","freeMintsLeft","PRICE","remainingSupply","isFreePhase","TOKEN_PRICE","AGENT_ID","owner","launched","failed","isRefundPhase","totalShares","tokenClaimed_user","claimOpen","hasFreeClaimed_user","freeSupply","maxSupply"):
        if f in v and v[f] is not None:
            ent[f]=v[f]
    ent["lastReadBlock"]=BLK
    ent["lastReadWib"]=WIB
    if delta is not None:
        ent["previousTotalSupply"]=c14
        ent["totalSupply"]=c15 if v.get("totalSupply") is not None else ent.get("totalSupply")
        if v.get("totalMinted") is not None: ent["totalMinted"]=v["totalMinted"]
        ent["mintedInInterval"]=delta
        ent["intervalMinutes"]=60
        ent["currentRatePerMin"]=round(rate,4)
        ent["previousRatePerMin"]=round(pr,4) if pr is not None else None
        ent["velocityRatio"]=round(ratio,2) if ratio is not None else None
        ent["velocityLegPasses"]=vel
    ent["runNote1501_1116"]=f"Run 1501 (blok {BLK}, interval ~60 mnt vs run 1401; run 1431 pakai set baca berbeda + tidak persist reread JSON 37-set): {c14}->{c15} (+{delta}, {rate:.3f}/mnt vs prev {pr if pr is not None else 'n/a'}/mnt = {ratio if ratio is not None else 'n/a'}x) -> velocity {'LOLOS' if vel else 'GAGAL'} (butuh >=1.5x DAN >=20 token). DIAM." if delta is not None else f"Run 1501 (blok {BLK}): views tidak lengkap (totalSupply/totalMinted None), velocity TIDAK dihitung. DIAM."
    updated.append(name)
print("updated:",len(updated),updated)
# BinanceAI pending claim
pc=s.get("pending_claims",{})
print("pending_claims keys:",list(pc.keys())[:10])
for k,v in pc.items():
    if isinstance(v,dict) and "binanceai" in k.lower():
        v["launched"]=0; v["failed"]=1; v["isRefundPhase"]=1; v["totalShares"]=3110; v["tokenClaimed"]=0
        v["lastCheckWib"]=WIB; v["lastReadBlock"]=BLK
        v["runNote1501_1116"]="Run 1501: launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0 - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM."
        print("binanceai updated:",k)
# Xeno Agent entry
s["contracts"]["Xeno Agent"]={
 "address":"0xc6a533146b7de96f9c805c19777bafd93a41b594",
 "status":"checked-not-lead-paid-only-2026-11-16",
 "totalSupply":4900,"totalMinted":4900,"MAX_SUPPLY":5000,
 "priceWei":1000000000000000,
 "balanceOf_user":0,"mintedBy_user":0,
 "lastReadBlock":133892541,"lastReadWib":WIB,
 "source":"Boltbook front page EN+ZH run 1501 (post g24xlY3XI76_, grandtheftauto6.ai, 2026-11-16T07:51:04Z) + verifikasi on-chain run ini",
 "note":"Xeno Agent (XENOAGENT): totalSupply=totalMinted=4900/5000 (98%, 100 tersisa). price()=0.001 BNB; static eth_call mint(1) value 0 dari wallet user REVERT 0x3c6b4b28 (sama dgn laporan Boltbook + komentar bedebah.ai/blobcrypto.ai) - jalur gratis TERTUTUP, 100 sisa BERBAYAR. Tanpa free view (freeMinted/freeClaimed/freeLeft/freeSupply revert - fungsi tidak ada); Sourcify 404 (unverified); umur UNVERIFIED (first-mint tak terverifikasi, Ankr 401) tapi MOOT karena paid-only. BUKAN lead/kandidat, TIDAK dilaporkan, TIDAK preview/mint.",
}
print("Xeno added")
# Feedshape checked entries in track_c
n_new=0
for o in feed:
    addr=o["address"]
    exists=any(isinstance(v,dict) and (v.get("address") or "").lower()==addr.lower() for v in s.get("track_c",{}).values())
    if exists: continue
    key="Feed-ERC20-0x"+addr[2:6]
    s["track_c"][key]={"address":addr,"status":"checked-not-sale-shape-2026-11-16",
      "note":f"Run 1501 Sourcify feed (verified {o.get('verifiedAt','?')}): S1={o.get('S1')} S2={o.get('S2')}; mint={o.get('has_mint')} quote={o.get('has_quote')} free_views={o.get('free_views')} agent_ref={o.get('agent_ref')} fns={o.get('n_fns')}. Bukan lead track-C; first-mint tidak terverifikasi."}
    n_new+=1
print("feedshape new track_c entries:",n_new)
# run notes
s["runNote1501_1116"]="Run 1501 (15:01 WIB): re-read 37/37 OK blok 133892405 (88,5 dtk, interval ~60 mnt vs run 1401; run 1431 pakai set baca berbeda dan tidak persist reread JSON 37-set). 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. Velocity: TIDAK ADA yang lolos; maks SPARKS +9 (0,150/mnt, <20); AgentNOVA +3; Bold Leonidas +3; MORFO/NOISE/Matrix +2; Zephyra/Pengu/SKRR +1; sisanya 0/flat. BARU dicek run ini: Xeno Agent 0xc6a533... (Boltbook, klaim 4900/5000) - totalSupply 4900/5000 terverifikasi on-chain, price()=0,001 BNB, static mint(1) value 0 REVERT 0x3c6b4b28, tanpa free view, Sourcify 404 -> PAID-ONLY, bukan lead, TIDAK dilaporkan. Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund). ALIEN masih BELUM DIBUKA (totalSupply 0, mintOpen=0); RigForge openedAt masih 0. Boltbook EN 200 (46.765 byte) / ZH 200 (46.866 byte): 7 alamat, 1 baru (Xeno Agent)."
s["runNote1501_1116_scan"]="Run 1501 SCAN FAST-FAIL (Ankr 401): pre-flight via run-2026-11-16-1501-scanpreflight.py (ankr_getLogs 50 blok 133892573-133892622) gagal deterministik HTTP 401 Unauthorized dalam 1,22 dtk, sama dengan run 2026-11-12, 2026-11-14 00:16, 2026-11-15 07:16 & 12:31, 2026-11-16 03:01, 09:01 & 14:01. Driver TIDAK diluncurkan. Watermark TETAP 132512564. Head 133892623, gap 1.380.059 blok dan membesar (~8.000/jam). Triase + 5c dilewati (tidak ada output scan)."
s["runNote1501_1116_feedshape"]="Run 1501 Sourcify feed: 20 kontrak terbaru (verifiedAt s.d. 08:02:32Z), 0 S1 / 0 S2; 1 kontrak dgn mint+freeMinted (0x1d4E...) tanpa quote + tanpa agent_ref -> bukan sale-shape. 20/20 dicatat checked-not-sale-shape di track_c (baru semua)."
s["runNote1501_1116_boltbook"]="Run 1501 Boltbook EN+ZH (curl langsung, HTTP 200): 7 alamat unik, 6 sudah di snapshot (Agent Bubble watchlist; LumenFindings age-excluded; PEPE track_c minted-by-user; 0x8269 checked-not-lead; NEUPEN checked-not-lead-not-agent-shaped; BOLT platform token), 1 baru = Xeno Agent 0xc6a533... (paid-only, lihat runNote1501_1116)."
s["runNote1501_1116_sweep"]="Run 1501 sweep EN+ZH: hanya proyek lama (Agentic Gangster 9 Nov free sold out; Meow Cards age-excluded 12 Nov; RIGBYPASS excluded; Saturnagent sold-out 14 Nov; Dragon Agents free lane CLOSED 888/888; UFO/NEBULA 10 Nov) - 0 proyek baru. Komplemen 6a/6b/6c: Odaily newsflash dicek langsung (tidak ada item free-mint Agent ID); Square/PANews/DappBay tidak menambah di luar sweep+Boltbook+Sourcify."
s["runNote1501_1116_binanceai"]="Run 1501 track-B binanceai.fun: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 (blok 133892405) - tetap pending/refund, sudah dilaporkan sekali (fase refund 2 Nov), DIAM."
s["runNote1501_1116_bridge"]="Run 1501 bridge (read-only): 116 kontrak bridge, 116/116 sudah di snapshot, 0 baru, 7 same_owner_discarded. Tidak ada temuan pelengkap baru / promosi run ini. Job ini tidak menulis bridge."
s["last_run_wib"]="2026-11-16 ~15:01 WIB"
s["last_run"]="free-mint-search 2026-11-16 15:01 WIB — DIAM (0 kandidat/strong/early/track-B/track-C baru, 0 eksekusi)"
s["last_run_note"]="Run 1501: DIAM - 0 kandidat/strong/early/track-B/track-C baru. Velocity tidak ada yang lolos (maks SPARKS +9). Xeno Agent baru dicek: paid-only (mint value 0 revert), bukan lead. Ankr 401 berlanjut; watermark scan tertahan di 132512564."
json.dump(s,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("SNAPSHOT WRITTEN")
