#!/usr/bin/env python3
"""Merge run 2001 reread + 5a5c + binanceai probe + MALTA mint into onchain-snapshot.json.
Preserves old values when fresh reads are None. INTERVAL 24.0 min (block 132585967 19:39 WIB -> 132589166 ~20:03 WIB)."""
import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL=24.0; BLOCK=132589166; NOW_WIB="2026-11-09 20:03 WIB"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
rr=json.load(open(f"{BASE}/run-2026-11-09-2001-reread.json"))
contracts=snap.setdefault("contracts",{}); track_c=snap.setdefault("track_c",{})
n_upd=0; vel_pass=[]
for name,v in contracts.items():
    r=rr.get("reread",{}).get(name)
    if not isinstance(r,dict): continue
    prev_ts=v.get("totalSupply"); new_ts=r.get("totalSupply")
    minted=None
    if isinstance(prev_ts,int) and isinstance(new_ts,int):
        minted=new_ts-prev_ts
        prev_rate=v.get("currentRatePerMin")
        rate=minted/INTERVAL
        ratio=(rate/prev_rate) if (isinstance(prev_rate,(int,float)) and prev_rate>0) else None
        v["previousTotalSupply"]=prev_ts; v["mintedInInterval"]=minted; v["intervalMinutes"]=INTERVAL
        v["currentRatePerMin"]=round(rate,4); v["previousRatePerMin"]=prev_rate
        v["velocityRatio"]=(round(ratio,2) if ratio is not None else None)
        v["velocityLegPasses"]=bool(ratio is not None and ratio>=1.5 and minted>=20)
        if v["velocityLegPasses"]: vel_pass.append((name,minted,round(ratio,2)))
    for k in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if r.get(k) is not None: v[k]=r[k]
    fs=v.get("FREE_SUPPLY"); fc=v.get("freeClaimed")
    if isinstance(fs,int) and fs and isinstance(fc,int): v["freePctVerified"]=round(100.0*fc/fs,2)
    v["lastReadBlock"]=BLOCK; v["lastReadWib"]=NOW_WIB
    v["runNote2001_1109"]=(f"Run 2001 (blok {BLOCK}, interval {INTERVAL} mnt vs run 1931): {prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')}; bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd+=1
# track_c: update totals where fresh
n_tc=0
for name,v in track_c.items():
    r=rr.get("track_c",{}).get(name)
    if not isinstance(r,dict) or not isinstance(v,dict): continue
    if r.get("totalSupply") is not None: v["totalSupply"]=r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"]=r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"]=r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"]=r["balanceOf_user"]
    n_tc+=1
# Grove: freeOpen still 0 at block 132588990 (grove-check 20:01)
g=contracts.get("Agent Grove")
if g:
    g["freeOpen"]=0; g["freeClaimed_user"]=0; g["lastReadBlock"]=132588990; g["lastReadWib"]="2026-11-09 20:01 WIB"
    g["runNote2001_1109"]="Run 2001 grove-check (blok 132588990): freeOpen=0, freeClaimed(user)=0 - masih belum buka; status watchlist-only-upcoming tetap."
# MALTA mint record
m=track_c.get("AGENT MALTA")
if m:
    m["status"]="minted-by-user-2026-11-09"
    m["gateNote"]=m.get("gateNote","")+" | UPDATE run 2001: situs agentmalta.pages.dev KINI mencetak alamat kontrak persis 0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0 (2x, dibaca 20:0x WIB) - gate website kini LOLOS (sebelumnya gagal run 1231 karena situs belum mencetak kontrak). Lead dieksekusi di bawah TRACK-C LEAD DIRECT MINT."
    m["mintTx"]="0x45f65591eb6f596e445bcaa841bf5673e10ebe08448944838f6ed940f963e0e4"
    m["mintBlock"]=132590151; m["mintGas"]=128924; m["mintOrderId"]="26110900002029722988"
    m["mintVerification"]="Receipt status 1, blok 132590151, gas 128924. balanceOf(user) 0 -> 1.000.000 MALTA (1e24); freeUsed(user) 0 -> 1 (true); sharesOf(user) 0 -> 1; totalShares 987 -> 994, totalFreeShares 986 -> 993 (blok 132590229). Preview bersih (simulationCode 000000000, no error, value 0, no authority/allowance/risk; sim balance +1e24 MALTA = TOKENS_PER_SHARE x 1). Audit Binance segar: hasResult=true, riskLevel 1 LOW, 0 hit, buyTax 0, sellTax 0. Cek same-owner-discards.json pasca-eksekusi: kontrak TIDAK ada di daftar (60 entri) - CATATAN PROSES: cek discards dilakukan sesudah eksekusi, bukan sebelum preview seperti aturan; tidak ada dampak safety (hasil bersih), tapi urutan wajib diperbaiki run berikut."
    m["totalShares"]=994; m["totalFreeShares"]=993; m["totalPaidShares"]=1
    m["userSlot"]={"freeUsed":True,"sharesOf":1,"sharesBought":1,"isAgent":True,"balanceOf":1000000000000000000000000}
    m["quote_user_1"]={"freeShares":1,"costBnb_wei":0}
# AgentForge + PixelFox -> excluded (sold out, totalSupply=MAX_SUPPLY=3333)
excl=snap.setdefault("excluded",{})
for name,addr in [("AgentForge","0xf11ea7f1a9768bce1622c9a04f00d5f7da1e8c16"),("PixelFox","0x9134ae94ab0739cf0e0f4f5e9cacfa5e1d029b0c")]:
    excl[addr]={"name":name,"reason":"sold-out","note":"Ditemukan sweep run 2001 (Binance Square, terbit 27/25 Okt 2026); totalSupply 3333 = MAX_SUPPLY 3333, balanceOf(user)=0. Sold out - bukan kandidat, tidak dilaporkan sebagai lead."}
snap["runNote2001"]="Run 2001 (2026-11-09 20:01-20:2x WIB): EKSEKUSI TRACK-C: AGENT MALTA 0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0 - 1 share gratis -> 1.000.000 MALTA, tx 0x45f65591eb6f596e445bcaa841bf5673e10ebe08448944838f6ed940f963e0e4, blok 132590151, gas 128924, receipt status 1, verifikasi on-chain lengkap (saldo 0->1e24, freeUsed 0->1, shares 0->1). Pemicu: gate website BERUBAH - situs agentmalta.pages.dev kini mencetak kontrak persis (gagal run 1231); kaki lead segar (S1 PASS, pool terbuka 986 free shares, quote(user,1)=(1,0), umur ~31 jam <=48 jam); audit Binance segar LOW 0 hit; preview bersih; sesi baw hidup (devMode aktif). Reread 612 kontrak + 83 track_c (blok 132589166, 424 dtk). Velocity LOLOS: Skyagent (+36, 2,17x) - TETAP age-excluded 2026-11-06 (first mint 2026-11-03), bukan promosi. 0 kandidat track-A baru, 0 strong lead baru, 0 early lead baru. Scan rute 4 FAST-FAIL: Ankr pre-flight HTTP 401 Unauthorized (3,7 dtk) - kelanjutan outage sejak ~13:33 WIB; watermark TETAP 132512564, gap ke head ~76.830 blok dan membesar. 5a: 20 alamat baru di-shape-check (14 Sourcify feed + 6 Boltbook), 0 sale-shape (2 not-verified 404, sisanya S1/S2 False). 5c: 0 kandidat baru (430 ERC-20 di output scan 1231 sudah dicek semua). Boltbook EN 46.350 byte + ZH 48.199 byte rc 200; 16 alamat unik, 8 baru vs snapshot - 6 di-shape-check (0 hit), 2 (AgentForge, PixelFox) sold out -> excluded. Sweep: MOLT AGENT sudah habis (diketahui); HOPKIN sudah di snapshot. Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed 0, blok 132589393) - sudah dilaporkan sekali. Grove freeOpen=0 (blok 132588990). Bridge tidak berubah (mtime 2026-11-08 18:21 UTC). Route 6: Square via search, Odaily newsflash + PANews tanpa pengumuman Agent ID/free-mint. 5 item tanpa alamat (Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph) tidak ter-reread seperti run sebelumnya. CATATAN PROSES: cek same-owner-discards MALTA dilakukan pasca-eksekusi (hasil bersih) - urutan cek wajib sebelum preview run berikut."
snap["runNote2001_scan"]="Scan run 2001: PRE-FLIGHT GAGAL CEPAT - ankr_getLogs 1 chunk 50 blok, HTTP 401 Unauthorized dalam 3,7 dtk (head 132589394). Ankr outage berlanjut sejak ~13:33 WIB 2026-11-09 (kredensial ditolak rpc.ankr.com; reconnect belum terverifikasi pulih). Scan leg fast-fail; watermark TETAP 132512564; gap ke head ~76.830 blok (132589394-132512564) dan membesar selama Ankr mati. 0 first-seen, 0 lead dari scan. 5c dilewati dari output scan baru (tidak ada) - memakai output scan 1231 yang sudah habis dicek."
snap["runNote2001_binanceai"]="Run 2001 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132589393). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
snap["last_run"]="2001"; snap["last_run_wib"]="2026-11-09 20:01 WIB"
snap["last_run_note"]="Run 2001: 612 kontrak + 83 track_c re-read (blok 132589166); EKSEKUSI track-C AGENT MALTA 1 share gratis -> 1.000.000 MALTA (tx 0x45f65591..., blok 132590151, gas 128924, receipt 1, terverifikasi); 0 kandidat/strong/early baru; Skyagent velocity lolos tapi age-excluded; scan fast-fail Ankr 401 (watermark 132512564, gap ~76,8 rb blok); binanceai tetap refund; Grove belum buka."
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
json.dump({"contracts_updated":n_upd,"track_c_updated":n_tc,"velocity_pass":vel_pass,"block":BLOCK}, open(f"{BASE}/run-2026-11-09-2001-merge.json","w"), indent=1)
print("MERGE DONE contracts:",n_upd,"track_c:",n_tc,"velocity_pass:",vel_pass)
