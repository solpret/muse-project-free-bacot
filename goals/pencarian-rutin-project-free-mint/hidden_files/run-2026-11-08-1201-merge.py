#!/usr/bin/env python3
"""Merge run 1201 results into onchain-snapshot.json. No executions. Values None = keep old."""
import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-08-1201-reread.json"))
ana=json.load(open(f"{BASE}/run-2026-11-08-1201-analysis.json"))
blk=r["block"]; interval=ana["interval_min"]
vel={v[0]:v for v in ana["vel_pass"]}
n_upd=0; n_none=0
for name,d in r.get("reread",{}).items():
    s=snap.get("contracts",{}).get(name)
    if not s: continue
    ts=d.get("totalSupply")
    if ts is None:
        n_none+=1
    else:
        prev=s.get("totalSupply")
        if prev is not None and ts!=prev:
            minted=ts-prev
            rate=minted/interval if interval>0 else 0
            s["previousTotalSupply"]=prev
            s["mintedInInterval"]=minted
            s["intervalMinutes"]=round(interval,1)
            s["previousRatePerMin"]=s.get("currentRatePerMin") or 0
            s["currentRatePerMin"]=round(rate,4)
            pr=s["previousRatePerMin"]
            ratio=(rate/pr) if pr and pr>0 else None
            s["velocityRatio"]=round(ratio,2) if ratio is not None else None
            s["velocityLegPasses"]=bool(ratio is not None and ratio>=1.5 and minted>=20)
            rtxt=f"{ratio:.2f}x" if ratio is not None else "None (rate sebelumnya 0)"
            s["runNote1201"]=f"Run 1201 (blok {blk}, interval {interval:.1f} mnt): {prev}->{ts} (+{minted}, {rate:.3f}/mnt vs prev {pr} = {rtxt}) -> velocity {'LOLOS' if s['velocityLegPasses'] else 'GAGAL'}."
        s["totalSupply"]=ts
        n_upd+=1
    bal=d.get("balanceOf_user")
    if bal is not None: s["balanceOf_user"]=bal; s["userBalance"]=bal
    fc=d.get("freeClaimed")
    if fc is not None:
        s["freeClaimed"]=fc
        fs=s.get("FREE_SUPPLY")
        if fs: s["freePctVerified"]=round(fc/fs*100,2)
    s["lastReadBlock"]=blk
    s["lastReadWib"]="2026-11-08 run 1201"
# velocity notes for the 3 passers (status-aware, no promotion)
for v in ana["vel_pass"]:
    name=v[0]
    s=snap.get("contracts",{}).get(name)
    if not s: continue
    s["velocityNote1201"]=(f"Run 1201: velocity LOLOS (+{v[3]}, {v[4]}/mnt vs prev {v[5]} = {v[4]/v[5]:.2f}x) TAPI TIDAK promosi: "
        f"status {v[6]} (Mechfarm lama = same-owner-discarded; Skyagent = age-excluded; Mechfarm-baru 0x1fab92b9 = strong-lead gate-failed run 0831, gate tetap gagal -> tidak ada eksekusi).")
# track_c fresh values
n_tc=0
for name,d in r.get("track_c",{}).items():
    s=snap.get("track_c",{}).get(name)
    if not s or not isinstance(s,dict): continue
    for k in ("totalSupply","totalMinted","sharesMinted","totalShares","freeClaimed","freeMinted"):
        if d.get(k) is not None:
            s[k]=d[k]; n_tc+=1
    s["lastReadBlock"]=blk; s["lastReadWib"]="2026-11-08 run 1201"
# discovery exclusions (sold out + age-excluded, verified on-chain run 1201)
disc=json.load(open(f"{BASE}/run-2026-11-08-1201-discovery.json"))
ex=snap.setdefault("excluded",{})
ex["Pixel Fox"]={"address":"0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c","track":"A","status":"excluded-sold-out-age-over-48h-2026-11-08","note":"Discovery run 1201 (route 3): totalMinted 3333/3333 SOLD OUT; umur ~14 hari -> age-excluded. Tidak dilaporkan sebagai lead."}
ex["PocketDragons"]={"address":"0x2cff830264343f29d4924160096f1271a8a14ace","track":"A","status":"excluded-sold-out-age-over-48h-2026-11-08","note":"Discovery run 1201 (route 3): totalSupply 7000/7000 SOLD OUT; umur ~15 hari -> age-excluded. Tidak dilaporkan sebagai lead."}
ex["AgentForge"]={"address":"0xf11ea7f1a9768bce1622c9a04f00d5f7da1e8c16","track":"A","status":"excluded-sold-out-age-over-48h-2026-11-08","note":"Discovery run 1201 (route 3): totalSupply 3333/3333 SOLD OUT; umur ~12 hari -> age-excluded. Tidak dilaporkan sebagai lead."}
ex["NEKO"]={"address":"0x321c88321e9c20464184228529a58ba48ef24635","track":"A","status":"excluded-out-of-scope-2026-11-08","note":"Discovery run 1201 (route 2 Boltbook): NEKO di Robinhood Chain (bukan BSC), free mint buka 2026-11-08 17:00 WIB, bukan narasi Agent ID -> di luar scope Free Bacot. Log only."}
# top-level run notes
snap["runNote1201"]=("Run 1201 (2026-11-08, blok reread 132337484, interval 57,4 mnt vs run 1101): reread 477 kontrak + 67 track_c; "
 "velocity LOLOS 3, 0 promotable (Mechfarm lama +20 same-owner-discarded; Skyagent +28 age-excluded; Mechfarm-baru 0x1fab92b9 +51 strong-lead gate-failed run 0831 - gate tetap gagal, tidak ada eksekusi/promosi). "
 "Sellout BARU 0 (4 yang di-flag subagent - SeanceSociety/Cryptlichor/bridge-0xf11c5f7a/Whale Agent - ternyata free pool SUDAH habis di snapshot sejak sebelum run 1101, freeClaimed==FREE_SUPPLY; 23 flag parent juga sudah di MAX_SUPPLY di snapshot; AnonymousAgent-Token = artefak satuan raw-vs-whole; bridge-0x6eee003e = artefak ERC-20 wei). "
 "Slot berubah 0. Age-remove 0 (kept-verified-launch + unverified-launch tetap). Track C: 3 hanya berubah totalSupply (Crack 3732->3745, ORBITA, PLNK); 0 lead/kandidat baru; NIULAI/OSK/KillZero/DROID/IMARS tidak berubah (tetap not-open/pool-habis). "
 "Bridge: file tidak berubah sejak 2026-11-06 02:48, 115 kontrak, 0 entri baru (33 seeded finding tidak di snapshot sudah dilaporkan sebagai finding, bukan lead baru). "
 "RPC terdegradasi run ini: 113 kontrak bacaan totalSupply None (nilai lama dipertahankan, BUKAN nol); free views None di banyak kontrak; single-call lambat + rate-limit -32005 sesekali. "
 "baw LOGOUT PREMATUR KE-2 ~12:39 WIB (sesi baru mati mendadak, UNCONNECTED) - tidak ada eksekusi run ini sehingga tidak berdampak; eksekusi mendatang butuh login ulang QR user.")
snap["runNote1201_scan"]=("Run 1201: SCAN PARSIAL (pre-flight OK 2,2 dtk, head 132335148). Window 132334203-132335202 (1000 blok terbaru; cap 1000). 20/20 chunk selesai (ERC721 150, ERC1155 4, ERC20-mint 268) TAPI 1 chunk Transfer error (132335103-132335152, Remote end closed connection - 50 blok Transfer logs hilang). "
 "Enrichment STALL: hanya 4/150 kontrak dalam ~9 mnt (~2 mnt/kontrak, Sourcify IncompleteRead/timeout) -> scan DI-KILL manual (SIGTERM), JSON parsial tersimpan. 4 enriched: NeoTrade Soulbound, Uniswap V4 Positions, Pancake V3 Positions (infrastruktur, bukan lead), Paw Gang (sudah di snapshot) - 0 EARLY lead. "
 "Watermark TIDAK dimajukan (tetap 132328744); skipped gap 132328745-132334202 (5458 blok; backfill dinonaktifkan user). 5c dari JSON parsial: 4 baru dicek (0x3d1f4165 not_verified; 0x7cB3B9F0 Sourcify RemoteDisconnected; 0x8f249065 registry-bytes saja tanpa ABI; 0x7d4a6614 URLError), 0 sale-shape; track-c-scan-checked.json 1463 -> 1467.")
snap["runNote1201_binanceai"]=("Run 1201: binanceai tetap fase refund/failed (failed=1, isRefundPhase=1, totalShares 3110, tokenClaimed_user=0, balance 0; launched() None run ini = artefak baca, bukan perubahan - bacaan sebelumnya 0). SUDAH dilaporkan run 1701 2026-11-07 - TIDAK dilaporkan ulang.")
snap["runNote1201_discovery"]=("Run 1201 discovery (routes 2/3/5a/6): 0 early/strong lead/kandidat baru, TIDAK ADA laporan chat. Boltbook EN 44.635 B / ZH 43.176 B, 0 keyword hit; 1 baru NEKO Robinhood (out-of-scope, dicatat excluded). Sourcify feed 20 -> 0 S1/0 S2 (1 baru 0x3352Fdc1 ABI kosong, retry run berikut). Sweep: SYMBOL sale PAID-ONLY (bukan track C); Pixel Fox/PocketDragons/AgentForge SOLD OUT + umur 12-15 hari (dicatat excluded). Razor Agent upcoming, belum deploy. Square/Odaily/PANews 0 baru; DappBay: Razor/SYMBOL/Cedar Kiln/Pixel Fox/PocketDragons tidak terdaftar (ketiadaan bukan bukti). Author pages Boltbook tidak dibaca ulang run ini (hanya front page EN+ZH). twitterapi.io tidak pernah dipanggil.")
snap["runNote1201_5c"]="Run 1201 5c: 4 ERC20 baru (mint_count>=10) dari scan parsial dicek, 0 sale-shape (detail di run-2026-11-08-1201-5c.json); 2 dari 4 gagal baca Sourcify (RemoteDisconnected/URLError) - dicatat checked dengan status error, bukan shape-fail terverifikasi."
snap["last_run"]="free-mint-search 2026-11-08 1201 WIB"
snap["last_run_wib"]="2026-11-08 12:57 WIB"
snap["timestamp_wib"]="2026-11-08 run 1201"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print(f"MERGE DONE: contracts updated={n_upd}, none-reads={n_none}, track_c fields={n_tc}")
# seen file: append the 4 scan-enriched contracts
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
scan=json.load(open(f"{BASE}/onchain-scan-2026-11-08-1201.json"))
added=[]
for c in scan.get("contracts",[]):
    a=c["address"]
    if a not in seen and a.lower() not in {k.lower() for k in seen}:
        seen[a]=c.get("first_block")
        added.append(a)
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json","w"), indent=1)
print("seen appended:", added, "| seen total now:", len(seen))
