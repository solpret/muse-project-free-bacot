#!/usr/bin/env python3
"""Merge run 1401 results into onchain-snapshot.json. No executions. Values None = keep old."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-08-1401-reread.json"))
ana=json.load(open(f"{BASE}/run-2026-11-08-1401-analysis.json"))
blk=r["block"]; interval=ana["interval_min"]
n_upd=0; n_none=0; n_changed=0
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
            s["runNote1401"]=f"Run 1401 (blok {blk}, interval {interval:.1f} mnt): {prev}->{ts} (+{minted}, {rate:.3f}/mnt vs prev {pr} = {rtxt}) -> velocity {'LOLOS' if s['velocityLegPasses'] else 'GAGAL'}."
            n_changed+=1
        elif prev is not None:
            s["previousTotalSupply"]=prev
            s["mintedInInterval"]=0
            s["intervalMinutes"]=round(interval,1)
            s["previousRatePerMin"]=s.get("currentRatePerMin") or 0
            s["currentRatePerMin"]=0.0
            s["velocityRatio"]=None
            s["velocityLegPasses"]=False
            s["runNote1401"]=f"Run 1401 (blok {blk}, interval {interval:.1f} mnt): {prev} flat -> velocity GAGAL."
        s["totalSupply"]=ts
        n_upd+=1
    bal=d.get("balanceOf_user")
    if bal is not None: s["balanceOf_user"]=bal; s["userBalance"]=bal
    fc=d.get("freeClaimed")
    if fc is not None:
        s["freeClaimed"]=fc
        fs=s.get("FREE_SUPPLY")
        if fs: s["freePctVerified"]=round(fc/fs*100,2)
    tm=d.get("totalMinted")
    if tm is not None: s["totalMinted"]=tm
    fm=d.get("freeMinted")
    if fm is not None: s["freeMinted"]=fm
    s["lastReadBlock"]=blk
    s["lastReadWib"]="2026-11-08 14:24 WIB"
# PANDORA velocity note (watchlist-only, +41, ratio ~1.06x -> gagal)
p=snap["contracts"].get("0xdb8a4102c49a41cfaed7673a3f155f19853af5e8")
if p:
    p["runNote1401_velocity"]="Run 1401 (blok 132351271, interval 35.8 mnt vs run 1331): 315->356 (+41, 1.145/mnt vs prev 1.0833 = 1.06x) -> velocity GAGAL; free% + gate tetap unverified/lemah, bukan promosi."
# Sidecoo velocity note (pass but not promotable)
sc=snap["contracts"].get("Sidecoo")
if sc:
    sc["velocityNote1401"]="Run 1401: velocity LOLOS (+37, 1.0338/mnt vs prev 0.6042 = 1.71x) TAPI TIDAK promosi: free% UNVERIFIED (semua free view None), umur UNVERIFIED, slot user UNVERIFIED; status watchlist-only-2026-11-06; MAX_SUPPLY 2^256-1."
# HokiBunny free-pool sellout -> remove from snapshot (report once by parent)
HBK="0xb0C14C75E747DD9cf94D907ff5191425059540aD"
hb_removed=None
if HBK in snap["contracts"]:
    hb_removed=snap["contracts"].pop(HBK)
    snap["removed1401_hokibunny"]={
        "address":HBK,"name":"HokiBunny","symbol":"HBUNNY",
        "status":"removed-sold-out-free-pool-2026-11-08-run1401",
        "note":("Run 1401: free pool HABIS — totalMinted 222/222 = FREE_CAP 222, freeMinted 222 (was 207 at run 1231); "
                "verified twice: reread batch blok 132351271 + single-call confirm (totalMinted 222, freeMinted 222, mintOpen 1). "
                "Was strong-lead-2026-11-08-gate-failed (63.5% free, gate website gagal). Paid lane may remain (mintOpen 1) but free lane closed. "
                "Removed from snapshot per body rule; report once."),
        "prior_status":hb_removed.get("status"),"firstMintWib":hb_removed.get("firstMintWib"),
    }
# discovery exclusions (age-excluded, verified on-chain / dated posts)
ex=snap.setdefault("excluded",{})
ex["Cosmofawn"]={"address":"0x9831577F7Ee2257e9B0b5C9809eD53B00e6975b8","track":"A","status":"excluded-age-over-48h-2026-11-08","note":"Scan run 1401 first-seen + walk-back: first mint TERVERIFIKASI 2026-11-02 18:45:25 WIB (~5,9 hari, >48h); free 265/1280 = 20,7%; Sourcify verified, registry-bytes hit, owner 0x6f244724... (bukan same-owner-discards). Age-excluded, tidak dilaporkan sebagai lead."}
ex["Agentgeili"]={"address":"0xf89CEdb1Bbc3C11a4941e543Ecf9f890788567f0","track":"A","status":"excluded-age-over-48h-2026-11-08","note":"Scan run 1401 first-seen + walk-back: first mint TERVERIFIKASI 2026-11-04 21:16:28 WIB (~3,7 hari, >48h); free 630/999 = 63,1%, slot user open (freeUsed 0, mintedBy 0) TAPI umur gagal -> bukan strong lead/kandidat. Sourcify verified, registry-bytes hit, owner sama dengan Cosmofawn 0x6f244724... Age-excluded, tidak dilaporkan sebagai lead."}
ex["Subsonic Tribe"]={"address":"0x65DDB3E337c12E5964ead6Cb9b6469203EF4caf1","track":"A","status":"excluded-age-over-48h-2026-11-08","note":"Discovery run 1401 (route 3, post X 26 Okt): launch >48 jam -> age-excluded. Tidak ditambahkan ke snapshot."}
ex["BNBmeme"]={"address":"0xdfe8c254b8cb1cdb2ecf755cbd519e9a23760723","track":"A","status":"excluded-age-over-48h-2026-11-08","note":"Discovery run 1401 (route 3, post 26 Okt, window s.d. 30 Okt): launch >48 jam -> age-excluded. Tidak ditambahkan ke snapshot."}
# top-level run notes
snap["runNote1401"]=("Run 1401 (2026-11-08, blok reread 132351271, interval 35,8 mnt vs run 1331): reread 487 kontrak + 71 track_c; "
 "velocity LOLOS 1 (Sidecoo +37, 1,71x) TAPI TIDAK promotable (free% + umur + slot UNVERIFIED). "
 "Sellout BARU 1: HokiBunny free pool HABIS (totalMinted/freeMinted 222/222 = FREE_CAP; dulu strong-lead gate-failed) — dihapus dari snapshot, laporkan sekali. "
 "Sellout-flag lain (Zapcourier/Cathodex/Kirinova/Lensorb/dll, freeClaimed==FREE_SUPPLY) SUDAH 100% di snapshot sejak sebelum run ini, bukan baru. "
 "Slot berubah 0. Age-remove 0 dari watchlist (Cosmofawn + Agentgeili age-excluded sebelum masuk snapshot). "
 "HIVE 1256 flat/balance 1, Bubblebruin +8 (2067, free 26,5%), PANDORA +41 (velocity gagal). "
 "RPC terdegradasi: 114 kontrak totalSupply None (nilai lama dipertahankan, BUKAN nol); track_c 71/71 totalSupply None (batch gagal total); free views None di banyak kontrak. "
 "Bridge: tidak berubah (sha b3f349f1…, 115 kontrak, mtime 2026-11-06 02:48 UTC). Track-B binanceai tetap refund phase (launched 0/failed 1/refund 1, shares 3110) — sudah dilaporkan, tidak dilaporkan ulang.")
snap["runNote1401_scan"]=("Run 1401: SCAN OK (pre-flight gagal percobaan 1 — Ankr RemoteDisconnected + 3x dataseed timeout — lalu OK percobaan 2, 42 dtk, 1000 log, head 132351223). "
 "Window 132350655-132351654 (1000 blok terbaru; cap 1000), 20/20 chunk + 131/131 enrich, 40 Ankr calls, 0 error, partial=false. 131 NFT (mints) + 362 ERC-20-mint. "
 "4 first-seen registry-bytes: Cosmofawn + Agentgeili (walk-back first mint 2026-11-02 18:45 WIB / 2026-11-04 21:16 WIB -> AGE-EXCLUDED, bukan lead), Niulai NFT + ZAPLO (bukan agent-shaped: no registry/free view, Sourcify unverified; ZAPLO FREE_SUPPLY 0). "
 "27 first-seen lain: infrastruktur (Uniswap/Pancake positions, BABT, badges) + non-agent (CloudBank, Mosfik, Swarm Agent, BNX Free, Twin3, RAXF, dll) — bukan lead. "
 "Watermark 132347311 -> 132351654; skipped gap 132347312-132350654 (3343 blok, backfill off). HIVE Agents tidak ada di window.")
snap["runNote1401_binanceai"]=("Run 1401: binanceai tetap fase refund/failed (launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed_user 0, balance 0; blok 132351409). SUDAH dilaporkan — TIDAK dilaporkan ulang.")
snap["runNote1401_discovery"]=("Run 1401 discovery (routes 2/3/5a/6): 0 early/strong lead/kandidat baru. Boltbook EN fresh 07:21 UTC, ZH stale 18 jam; Nova Agent 0x232816a2 (99%, Sourcify unverified, free views revert -> free% UNVERIFIED, umur UNVERIFIED, sudah di hot-leg-seen) bukan lead; Spuds tanpa Agent ID gate; POH sold out; BNAF tanpa alamat kontrak (tidak terverifikasi). "
 "Sourcify feed 20 -> 3 baru, ketiganya proxy ERC1967 yang implementasinya sudah di hot-leg-seen (bukan lead). Sweep: hanya proyek lama 24 Okt-2 Nov (AGC, AgentForge, AGENT MAO paused, Pixel Fox, Laser, PocketDragons, Black Hole, Nidavellir, Subsonic, BNBmeme, BN Agent File, PIXEL PETS, Skynet). "
 "Square/Odaily/PANews 0 baru; DappBay: tidak ada kandidat live yang butuh website-evidence check. twitterapi.io tidak pernah dipanggil; boltbook.com tidak pernah dipakai.")
snap["runNote1401_5c"]="Run 1401 5c: 52 ERC-20 mint_count>=10, 7 baru dicek (cap 20), 0 sale-shape S1/S2 (6 no-abi Sourcify, 1 proxy 0 fungsi); track-c-scan-checked.json 1476 -> 1483 top-level keys."
snap["last_run"]="free-mint-search 2026-11-08 1401 WIB"
snap["last_run_wib"]="2026-11-08 14:40 WIB"
snap["timestamp_wib"]="2026-11-08 run 1401"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print(f"MERGE DONE: contracts updated={n_upd}, none-reads={n_none}, changed={n_changed}, hokibunny_removed={hb_removed is not None}, snapshot contracts now={len(snap['contracts'])}")
