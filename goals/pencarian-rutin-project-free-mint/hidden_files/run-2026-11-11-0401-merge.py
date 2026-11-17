#!/usr/bin/env python3
"""Merge run 0401 readings + 2 strong-lead direct mints into onchain-snapshot.json."""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
reread=json.load(open(f"{BASE}/run-2026-11-11-0401-reread.json"))
probe=json.load(open(f"{BASE}/run-2026-11-11-0401-probe.json"))
C=snap.setdefault("contracts",{})
TC=snap.setdefault("track_c",{})
BLK=reread.get("block")  # 132845183
def upd(name, **kw):
    e=C.setdefault(name,{})
    e.update(kw)
    e["lastReadBlock"]=BLK
    e["lastReadWib"]="2026-11-11 04:01 WIB"
    return e
# --- route 1 re-reads (supply deltas vs 0331 baseline) ---
for name,d in reread.get("reread",{}).items():
    if name=="CosmicSentinel": continue  # dup of Cosmic Sentinel
    e=C.get(name)
    if e is None: continue
    old=e.get("totalSupply")
    if d.get("totalSupply") is not None: e["totalSupply"]=d["totalSupply"]
    if d.get("freeMinted") is not None: e["freeMinted"]=d["freeMinted"]
    if d.get("balanceOf_user") is not None: e["balanceOf_user"]=d["balanceOf_user"]
    if d.get("mintOpen") is not None: e["mintOpen"]=d["mintOpen"]
    e["lastReadBlock"]=BLK; e["lastReadWib"]="2026-11-11 04:01 WIB"
    delta=(d.get("totalSupply") or old or 0)-(old or 0) if d.get("totalSupply") is not None else 0
    e["runNote0401_1111"]=f"Run 0401 (blok {BLK}): totalSupply {old}->{d.get('totalSupply')} ({delta:+d}), velocity GAGAL (<20 token); bal_user={d.get('balanceOf_user')}."
# --- probe fresh values for the two minted + NIGHTFORGE ---
p=probe.get("probe",{})
rv=p.get("RIMEVAULT",{}); mx=p.get("MYCELIX",{}); nf=p.get("NIGHTFORGE",{})
# RIMEVAULT minted
e=C["RIMEVAULT"]
e.update({"totalSupply":504,"agentFreeUsed":504,"agentFreeByWallet_user":1,"balanceOf_user":1,
 "status":"minted-by-user-2026-11-11","mintTx":"0xb3ae5ed6020e10a2032771ed0ef434adf145802c529720f512682bdfbcc04c7f",
 "mintBlock":132846359,"mintGas":250029,"mintGasFeeBnb":0.000016642,"mintTokenId":504,
 "mintOrderId":"26111000002032335361","mintRewardClaimable":"10000 RIME (TOKEN 0xe9ba5711dc1e3d8e71729a3cbd89f501a0247199, pair PCS V2 0x0 - tidak di-claim)",
 "lastReadBlock":132846429,"lastReadWib":"2026-11-11 04:01 WIB",
 "runNote0401_1111":"Run 0401: STRONG LEAD -> DIRECT MINT BERHASIL. agentFreeUsed 503/2000 = 25,15% (probe blok 132846050), mintStart 21:27:59 WIB 10 Nov (umur ~6,6 jam <24 jam), slot terbuka, website TERVERIFIKASI rimevault.pages.dev (H), audit Binance hasResult=false (tanpa hasil), preview bersih 000000000 (+1 ERC721 #504). tx 0xb3ae5ed6020e10a2032771ed0ef434adf145802c529720f512682bdfbcc04c7f, blok 132846359, receipt 1, gas 250029 (~0,0000166 BNB). ownerOf(504)=wallet agent, agentFreeByWallet 0->1, agentFreeUsed 503->504. Rarity: UNREVEALED (Sealed Ice Cube). Market: Ice Market ada (fee 3%, hanya revealed) tapi listing live unverified + #504 unrevealed -> TIDAK di-list. Reward 10.000 RIME claimable, pair 0x0 -> tidak di-claim."})
# MYCELIX minted
e=C["MYCELIX"]
e.update({"totalSupply":508,"agentFreeUsed":508,"agentFreeByWallet_user":1,"balanceOf_user":1,
 "status":"minted-by-user-2026-11-11","mintTx":"0x7f3a84186785ac1ec9b414ddfff06a2a7a4029bf6bdfa8dcc4c0fab5517ecc2e",
 "mintBlock":132846673,"mintGas":349681,"mintGasFeeBnb":0.0000218485,"mintTokenId":508,
 "mintOrderId":"26111000002032336808","mintRewardClaimable":"10000 token MYCELIX (TOKEN 0xbe5ca40e4bc8b561615390eefd5f1d4911ff3ea0, pair PCS V2 0x0 - tidak di-claim)",
 "lastReadBlock":132846698,"lastReadWib":"2026-11-11 04:01 WIB",
 "runNote0401_1111":"Run 0401: STRONG LEAD -> DIRECT MINT BERHASIL. agentFreeUsed 506/2000 = 25,3% (probe blok 132846050), mintStart 21:47:32 WIB 10 Nov (umur ~6,3 jam <24 jam), slot terbuka, website TERVERIFIKASI mycelix.pages.dev (H), audit Binance hasResult=false (tanpa hasil), preview bersih 000000000 (+1 ERC721 #508). tx 0x7f3a84186785ac1ec9b414ddfff06a2a7a4029bf6bdfa8dcc4c0fab5517ecc2e, blok 132846673, receipt 1, gas 349681 (~0,0000218 BNB). ownerOf(508)=wallet agent, agentFreeByWallet 0->1, agentFreeUsed 506->508. Rarity: UNREVEALED (metadata rate.json 404). Market: Rot Market BELUM live -> TIDAK di-list. Reward 10.000 token claimable, pair 0x0 -> tidak di-claim."})
# NIGHTFORGE gate-blocked, still no mint
e=C["NIGHTFORGE"]
e.update({"totalSupply":708,"agentFreeUsed":705,"paidMinted":3,"agentFreeByWallet_user":0,"balanceOf_user":0,
 "lastReadBlock":BLK,"lastReadWib":"2026-11-11 04:01 WIB",
 "runNote0401_1111":"Run 0401: totalSupply 702->708 (+6), agentFreeUsed 699->705 (35,25% dari 2000); slot terbuka; gate website TETAP BLOCKED (recheck via cron gate-blocked-recheck; deadline umur 14:37 WIB 11 Nov). TIDAK di-mint."})
# WORKER / Skywe notes (reread values)
e=C["WORKER"]; e.update({"totalSupply":358,"lastReadBlock":BLK,"lastReadWib":"2026-11-11 04:01 WIB",
 "runNote0401_1111":"Run 0401: totalSupply 353->358 (+5); umur + free% TETAP UNVERIFIED; website PASSED; slot terbuka. Watchlist-only, TIDAK di-preview/TIDAK di-mint."})
e=C["Skywe Legion"]; e.update({"lastReadBlock":BLK,"lastReadWib":"2026-11-11 04:01 WIB",
 "runNote0401_1111":"Run 0401: batch baca gagal semua view (None) - degradasi baca, BUKAN nol; nilai lama dipertahankan (totalMinted 339); umur + free% + website TETAP UNVERIFIED. Watchlist-only, TIDAK di-preview/TIDAK di-mint."})
# --- track_c re-reads ---
for name,d in reread.get("track_c",{}).items():
    e=TC.get(name)
    if e is None or not isinstance(e,dict): continue
    if d.get("freeMinted") is not None: e["freeMinted"]=d["freeMinted"]
    if d.get("totalSupply") is not None: e["totalSupply"]=d["totalSupply"]
    e["lastReadBlock"]=BLK; e["lastReadWib"]="2026-11-11 04:01 WIB"
TC["MOODENG"]["runNote0401_1111"]="Run 0401: freeMinted 398->451 (90,2% dari 500 FREE_SHARES); agent-shape TETAP UNVERIFIED + website UNVERIFIED + settle butuh 28,5 BNB paid -> watchlist-only, TIDAK di-preview/TIDAK di-mint. Deadline umur 02:00 WIB 12 Nov."
TC["ORYN-sale"]["runNote0401_1111"]="Run 0401: paused=1 (tetap), claim TIDAK terbuka; umur + website TETAP UNVERIFIED. Watchlist-only-paused, TIDAK di-preview/TIDAK di-mint."
TC["UFO"]["runNote0401_1111"]="Run 0401: totalSupply 9e30 (tetap); sale-shape TETAP GAGAL + permit gate manusia (EIP-712 off-chain) -> watchlist-only, TIDAK di-preview/TIDAK di-mint. Deadline umur 22:05 WIB 12 Nov."
TC["11-11"]["runNote0401_1111"]="Run 0401: freeMinted 586 (tetap); umur + website TETAP UNVERIFIED. Watchlist-only, tanpa perubahan."
# --- top-level run notes ---
snap["last_run_wib"]="2026-11-11 04:01 WIB"
snap["timestamp_wib"]="2026-11-11 04:01 WIB"
snap["last_run_note"]="Run 0401: 2 STRONG-LEAD DIRECT MINT BERHASIL — RIMEVAULT #504 (tx 0xb3ae5ed6020e10a2032771ed0ef434adf145802c529720f512682bdfbcc04c7f, blok 132846359) + MYCELIX #508 (tx 0x7f3a84186785ac1ec9b414ddfff06a2a7a4029bf6bdfa8dcc4c0fab5517ecc2e, blok 132846673); keduanya free, preview bersih, audit hasResult=false (tanpa hasil), rarity UNREVEALED, tidak di-list (market belum live/unrevealed), reward 10.000 token claimable tapi pair 0x0 (tidak di-claim). Saldo BNB agent 0,000062 -> ~0,000024 BNB. NIGHTFORGE tetap gate-blocked (705/2000). Scan Ankr FAST-FAIL (401). Binanceai launched=0 (tetap). Boltbook 0 baru; Sourcify feed 0 baru; sweep 0 baru (Agentic Gangster free sold out, MOLT free habis — sudah excluded). MOODENG 451/500 (90,2%) tapi agent-shape + website unverified + settle paid -> watchlist-only."
snap["runNote0401_1111"]="Run 0401 (blok 132845183): 2 strong-lead direct mint berhasil (RIMEVAULT #504 + MYCELIX #508). NIGHTFORGE gate-blocked. RIMEVAULT/MYCELIX status -> minted-by-user-2026-11-11."
snap["runNote0401_1111_scan"]="Run 0401 scan FAST-FAIL: preflight Ankr 401 Unauthorized dalam 25,8 dtk (head 132846894; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09, kini ~38,5 jam). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~334.330 blok dan tumbuh)."
snap["runNote0401_1111_binanceai"]="Run 0401 binanceai.fun: launched()=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132846850) — TIDAK BERUBAH (refund phase, sudah dilaporkan sekali)."
snap["runNote0401_1111_discovery"]="Run 0401 discovery: Boltbook EN 200 45.884B + ZH 200 45.960B, 11 alamat unik, 0 baru vs snapshot+hot-leg-seen. Sourcify feed 20 terbaru (verified 20:15:37-21:01:45Z), 0 baru vs hot-leg-seen (10.815). Sweep EN+ZH: 0 proyek baru (Agentic Gangster free sold out 111/111; MOLT free habis; Horus Phase 1 sold out; Subsonic/BNBmeme/Pixel Pets/Skynet lama Okt). Odaily 200 264.145B + PANews 200 119.482B, 0 keyword. Bridge: scan-bridge.json mtime 2026-11-09 01:21 WIB (STALE), 116 kontrak, 0 temuan pelengkap baru."
snap["runNote0401_1111_age_exclusions"]="Run 0401 age-exclusions (aturan <24 jam): 0 BARU (window 03:31->04:01 WIB). Deadline umur yang masih berjalan: NIGHTFORGE 2026-11-11 14:37 WIB; RIMEVAULT ~21:28 WIB, SOLDERCATS ~21:35 WIB, MYCELIX ~21:47 WIB, REWINDCLUB ~21:49 WIB, LCDSPRITE ~21:52 WIB (11 Nov); MOODENG ~02:00 WIB 12 Nov; UFO ~22:05 WIB 12 Nov. RIMEVAULT/MYCELIX sudah minted-by-user (bukan age-excluded). WORKER/Skywe Legion launch UNVERIFIED (watchlist-only, bukan age-excluded). Tidak ada item yang dihapus dari snapshot."
snap["runNote0401_1111_mints"]="Run 0401 mints: RIMEVAULT #504 tx 0xb3ae5ed6020e10a2032771ed0ef434adf145802c529720f512682bdfbcc04c7f blok 132846359 gas 250029 fee 0,000016642 BNB orderId 26111000002032335361; MYCELIX #508 tx 0x7f3a84186785ac1ec9b414ddfff06a2a7a4029bf6bdfa8dcc4c0fab5517ecc2e blok 132846673 gas 349681 fee 0,0000218485 BNB orderId 26111000002032336808. Sesi baw logged-in; DevMode enabled s.d. 2026-11-17; sessionExpire 2026-11-12T21:12:41Z. Saldo BNB agent 0,000062 -> 0,000046 (pasca-RIMEVAULT) -> ~0,000024 BNB (pasca-MYCELIX, verifikasi on-chain)."
json.dump(snap,open(f"{BASE}/onchain-snapshot.json","w"),indent=1)
print("MERGE OK; contracts:",len(C),"track_c:",len(TC))
