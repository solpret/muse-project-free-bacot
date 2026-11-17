#!/usr/bin/env python3
"""Merge run 0831 results into onchain-snapshot.json. Writes snapshot (with .bak)."""
import json, copy, datetime
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
reread=json.load(open(BASE+"run-2026-11-11-0831-reread.json"))
probe=json.load(open(BASE+"run-2026-11-11-0831-probe.json"))
names=json.load(open(BASE+"run-2026-11-11-0831-names.json"))
import shutil
shutil.copy(BASE+"onchain-snapshot.json", BASE+"onchain-snapshot.json.bak-0831-premerge")
C=snap.setdefault("contracts",{})
BLOCK=reread["block"]
def vel(name, new_supply):
    e=C.get(name)
    if not isinstance(e,dict): return
    old=e.get("totalSupply")
    if old is None or new_supply is None: return
    diff=new_supply-old
    prev_rate=e.get("currentRatePerMin")
    rate=round(diff/30.0,4)
    e["previousTotalSupply"]=old; e["totalSupply"]=new_supply
    e["mintedInInterval"]=diff; e["intervalMinutes"]=30.0
    e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
    ratio=None
    if prev_rate and prev_rate>0: ratio=round(rate/prev_rate,2)
    e["velocityRatio"]=ratio
    e["velocityLegPasses"]= bool(ratio is not None and ratio>=1.5 and diff>=20)
    e["lastReadBlock"]=BLOCK; e["lastReadWib"]="2026-11-11 08:31 WIB"
    return diff, rate, ratio
# --- 1. reread updates (priority contracts) ---
for name,d in reread["reread"].items():
    if name in ("SOLDERCATS","REWINDCLUB"): continue  # handled below with mint data
    if name not in C: continue
    e=C[name]
    ns=d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None: ns=d.get("totalMinted")
    if ns is not None:
        diff,rate,ratio=vel(name, ns) or (None,None,None)
        e[f"runNote0831"]=(f"Run 0831 (blok {BLOCK}): totalSupply {e.get('previousTotalSupply')}->{ns} "
            f"(+{diff}, {rate}/mnt vs prev {e.get('previousRatePerMin')} = {ratio}x) -> velocity "
            f"{'LOLOS' if e.get('velocityLegPasses') else 'GAGAL'}; bal_user={d.get('balanceOf_user')}; "
            f"freeMinted={d.get('freeMinted')}; status {e.get('status')}.")
    if d.get("freeClaimed") is not None: e["freeClaimed"]=d["freeClaimed"]
    if d.get("freeMinted") is not None: e["freeMinted"]=d["freeMinted"]
    if d.get("FREE_SUPPLY") is not None: e["FREE_SUPPLY"]=d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None: e["MAX_SUPPLY"]=d["MAX_SUPPLY"]
    if d.get("balanceOf_user") is not None: e["balanceOf_user"]=d["balanceOf_user"]
    e["lastReadBlock"]=BLOCK; e["lastReadWib"]="2026-11-11 08:31 WIB"
# --- 2. wave promotions: 15 watchlist-only -> EARLY (first mints verified) ---
PROMO={
 "Chestnut Common":28,"Coral Strand":19,"Poplar Thwaite":25,"Gorse Hurst":19,
 "Sycamore Stead":27,"Worsted Printworks":25,"Sienna Barbican":24,"Twill Fullery":20,
 "Heather Vale":27,"Hazel Combe":26,"Rowan Holt":27,"Jasper Knoll":25,
 "Alabaster Shipyard":27,"Marble Silo":20,"Obsidian Granary":21}
for name,supply in PROMO.items():
    e=C.get(name)
    if not isinstance(e,dict): continue
    e["previousTotalSupply"]=0; e["totalSupply"]=supply
    e["mintedInInterval"]=supply; e["intervalMinutes"]=30.0
    e["currentRatePerMin"]=round(supply/30.0,4); e["previousRatePerMin"]=None
    e["velocityRatio"]=None; e["velocityLegPasses"]=False
    e["status"]="early-lead-reported-2026-11-11"
    e["lastReadBlock"]=BLOCK; e["lastReadWib"]="2026-11-11 08:31 WIB"
    e["runNote0831"]=(f"Run 0831 (blok {BLOCK}): FIRST MINTS terverifikasi 0->{supply} -> PROMOSI "
        f"watchlist-only -> EARLY LEAD (dilaporkan sekali run ini, konsolidasi gelombang). "
        f"Free% UNVERIFIED (tanpa free views); umur + website UNVERIFIED. TIDAK di-preview/di-mint (tier early).")
# --- 3. SOLDERCATS minted ---
sc=C["SOLDERCATS"]; sc.update({
 "status":"minted-by-user-2026-11-11","totalSupply":504,"agentFreeUsed":504,
 "agentFreeByWallet":1,"balanceOf_user":1,"userBalance":1,"freePctVerified":25.2,
 "mintTx":"0x94f1f51a13bcf6fec68eb79b42941daab049568de728530332640234c03bed70",
 "mintBlock":132882485,"mintGas":250029,"mintTokenId":504,"supplyView":"totalSupply",
 "lastReadBlock":132882574,"lastReadWib":"2026-11-11 08:31 WIB"})
sc["runNote0831"]=("Run 0831: STRONG-LEAD DIRECT MINT BERHASIL. Kaki segar: umur TERVERIFIKASI <24 jam "
 "(mintStart 1794321310 = 10 Nov 21:35 WIB, ~11 jam); free 500/2000 = 25,00% (agentFreeUsed probe blok 132881827); "
 "slot user TERBUKA (agentFreeByWallet 0, balanceOf 0, mintOpen 1); gate PASSED (soldercats.pages.dev, metode H); "
 "discards bersih (kontrak + owner). Audit Binance hasResult=false (tanpa hasil, bukan lolos), tanpa RISK hit. "
 "Sim eth_call mint(1) value 0 SUKSES. Preview bersih 000000000 (+1 ERC721 #504, tokenId 0x1f8). "
 "Tx 0x94f1f51a13bcf6fec68eb79b42941daab049568de728530332640234c03bed70 blok 132882485 gas 250029 (~0,0000196 BNB) status 1; "
 "ownerOf(504)=agent, balanceOf 0->1, agentFreeUsed 500->504, agentFreeByWallet 0->1. "
 "UNREVEALED Sealed Cardboard Box (tokenURI meta/box.json, tier tidak terverifikasi). "
 "Own market Alley Swap 0xd35592aeccb54a9e528bf4b1a6fcfd4de9367bc9 fee 3%, listedCount 0, volume 0, sales 0 -> tanpa floor, TIDAK di-list. "
 "Element floor 0,00289 BNB (2 listing, volume 0 — hot-leg 0834) -> listing manual pun percuma saat ini. "
 "Claimable 10.000 PURR (TOKEN 0x2e61933a2d835526f5c5e8b836abb5373d831913, terverifikasi hot-leg 0834 via 2 RPC), getPair 0 — belum diklaim. "
 "PELAJARAN: token 0x174afa... adalah DOT milik LCDSPRITE (audit riskLevel 4 HIGH) — BUKAN token SOLDERCATS; jangan klaim DOT.")
# --- 4. REWINDCLUB minted + auto-list blocked (NotRevealed) ---
rc=C["REWINDCLUB"]; rc.update({
 "status":"minted-by-user-2026-11-11","totalSupply":502,"agentFreeUsed":502,
 "agentFreeByWallet":1,"balanceOf_user":1,"userBalance":1,"freePctVerified":25.1,
 "mintTx":"0xee5d66abe548f0959909dddbd0816d146ae975cf053e0fb6bb35abd531a46071",
 "mintBlock":132883329,"mintGas":256939,"mintTokenId":502,"supplyView":"totalSupply",
 "lastReadBlock":132883401,"lastReadWib":"2026-11-11 08:31 WIB"})
rc["runNote0831"]=("Run 0831: STRONG-LEAD DIRECT MINT BERHASIL (melewati 25% DI TENGAH run: reread 495/2000, "
 "probe ulang 501/2000 = 25,05%). Kaki segar: umur TERVERIFIKASI <24 jam (mintStart 1794322145 = 10 Nov 21:49 WIB, ~11 jam); "
 "free 501/2000 = 25,05% (agentFreeUsed probe blok 132883280); slot user TERBUKA (agentFreeByWallet 0, balanceOf 0, mintOpen 1); "
 "gate PASSED (rewindclub.pages.dev, metode H); kontrak tidak ada di discards (owner() tidak ada di ABI template ini). "
 "Audit Binance hasResult=false (tanpa hasil, bukan lolos), tanpa RISK hit. Sim eth_call mint(1) value 0 SUKSES. "
 "Preview bersih 000000000 (+1 ERC721 #502, tokenId 0x1f6). "
 "Tx 0xee5d66abe548f0959909dddbd0816d146ae975cf053e0fb6bb35abd531a46071 blok 132883329 gas 256939 (~0,0000212 BNB) status 1; "
 "ownerOf(502)=agent, balanceOf 0->1, agentFreeUsed 501->502, agentFreeByWallet 0->1. "
 "UNREVEALED Sealed Cassette Case (tokenURI meta/case.json, tier tidak terverifikasi). Claimable 10.000 DECK. "
 "AUTO-LIST GAGAL: own market 0xfb414d2288536f35eea77ba996effddb85e07574 fee 3%, listedCount 2, FLOOR LIVE 0,005 BNB (#435 + #171, valid); "
 "approve(502) ke market BERHASIL (tx 0x4687139e265cb0abfd512242cc6d438a0923334a5036c0067d4aa5e10f5a2bc6 blok 132883661 gas 48413 status 1, preview bersih); "
 "list(502, 0,005 BNB) GAGAL preview 351805 — static call revert custom error 0xb2c9bc88 = NotRevealed() (token #502 UNREVEALED, market menolak list token belum reveal). "
 "STOP sesuai guard (gagal satu langkah -> stop, jangan paksa); approval single-token #502 ke market tetap aktif. Listing menunggu reveal.")
# --- 5. NIGHTFORGE fresh free% (still gate-blocked) ---
nf=C.get("NIGHTFORGE")
if isinstance(nf,dict):
    nf.update({"totalSupply":731,"agentFreeUsed":728,"paidMinted":3,"lastReadBlock":132883280,"lastReadWib":"2026-11-11 08:31 WIB"})
    nf["runNote0831"]=("Run 0831: agentFreeUsed 728/2000 = 36,40% (totalSupply 731, paidMinted 3), slot terbuka; "
        "tetap STRONG LEAD GATE-BLOCKED (website UNVERIFIED) — TIDAK di-preview/di-mint. Recheck gate ~12:37 WIB (cron gate-blocked-recheck). Deadline umur 14:37 WIB 11 Nov.")
# --- 6. three new feed contracts -> watchlist-only-upcoming ---
C["Stampooor Stamp Packs"]={"address":"0x467696af8c2206B977B24081445104632dc1D459","status":"watchlist-only-upcoming-2026-11-11",
 "name":"Stampooor Stamp Packs","symbol":"STPACK","kind":"ERC721","totalMinted":0,"totalSupply":0,
 "freeMinted":0,"FREE_SUPPLY":1200,"MAX_SUPPLY":3000,"mintStart":0,"mintEnd":0,"mintOpen":0,
 "REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f","balanceOf_user":0,
 "baselineNote":"UPCOMING run 0831 (temuan feed Sourcify recently-verified, verifiedAt 2026-11-11T01:28:20Z): REGISTRY()=registry resmi, FREE_SUPPLY 1200, MAX 3000, freeMinted 0, totalMinted 0, mintStart 0, mintOpen 0 — BELUM launching (0 mint) -> BUKAN early lead (belum ada first mint). Umur + website UNVERIFIED. TIDAK di-preview/di-mint.",
 "lastReadBlock":132881827,"lastReadWib":"2026-11-11 08:31 WIB"}
C["Rulz Share"]={"address":"0x08E3e40829718913fb627c818Cb334B1E3d5B699","status":"watchlist-only-upcoming-2026-11-11",
 "name":"Rulz Share","symbol":"RSHARE","kind":"ERC721","totalMinted":0,"totalSupply":0,
 "MAX_SHARES":10000,"agentIdRequired":1,"mintStart":1794528000,"mintEnd":1795132800,
 "registry":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f","hasClaimed_user":0,"balanceOf_user":0,
 "baselineNote":"UPCOMING run 0831 (feed Sourcify verifiedAt 2026-11-11T01:17:53Z): template 23-fn claimFreeShare + registry() resmi + agentIdRequired=1, MAX_SHARES 10000, totalMinted 0, mintStart 1794528000 = 2026-11-13 ~07:00 WIB (MASA DEPAN) -> BUKAN early lead (belum launching). Umur + website UNVERIFIED. TIDAK di-preview/di-mint.",
 "lastReadBlock":132881827,"lastReadWib":"2026-11-11 08:31 WIB"}
C["Mimint Share"]={"address":"0x0BF38aFe23070C79f693DBDA4ce1866Ff11C4bF7","status":"watchlist-only-upcoming-2026-11-11",
 "name":"Mimint Share","symbol":"MSHARE","kind":"ERC721","totalMinted":0,"totalSupply":0,
 "MAX_SHARES":10000,"agentIdRequired":0,"mintStart":1794528000,"mintEnd":1795132800,
 "registry":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f","hasClaimed_user":0,"balanceOf_user":0,
 "baselineNote":"UPCOMING run 0831 (feed Sourcify verifiedAt 2026-11-11T01:17:41Z): template 23-fn claimFreeShare + registry() resmi, agentIdRequired=0, MAX_SHARES 10000, totalMinted 0, mintStart 1794528000 = 2026-11-13 ~07:00 WIB (MASA DEPAN) -> BUKAN early lead (belum launching). Umur + website UNVERIFIED. TIDAK di-preview/di-mint.",
 "lastReadBlock":132881827,"lastReadWib":"2026-11-11 08:31 WIB"}
# --- 7. track_c updates ---
TC=snap.setdefault("track_c",{})
for name,d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name],dict): continue
    e=TC[name]
    if d.get("freeMinted") is not None: e["freeMinted"]=d["freeMinted"]
    if d.get("totalSupply") is not None: e["totalSupply"]=d["totalSupply"]
    e["lastReadBlock"]=BLOCK; e["lastReadWib"]="2026-11-11 08:31 WIB"
    if name=="DROID": e["runNote0831"]="Run 0831: freeMinted 739->740 (+1); tanpa perubahan status."
    if name=="VISION": e["runNote0831"]="Run 0831: totalSupply 3,1842e27 -> 3,2094e27 (minting berjalan) tapi free views tetap None -> tetap watchlist-only-age-unverified, BUKAN promosi."
# --- 8. top-level run notes ---
snap["last_run_wib"]="2026-11-11 08:31 WIB"
snap["timestamp_wib"]="2026-11-11 08:31 WIB"
snap["last_run_note"]=("Run 0831: 2 MINT BERHASIL (strong-lead direct mint): SOLDERCATS #504 (500/2000 = 25,00%) + "
 "REWINDCLUB #502 (501/2000 = 25,05%, melewati 25% di tengah run). Auto-list REWINDCLUB GAGAL (preview 351805 NotRevealed — token unrevealed); "
 "SOLDERCATS tanpa floor own market (listedCount 0) -> tidak di-list. 15 PROMOSI watchlist-only -> EARLY (gelombang 1+2, first mints terverifikasi). "
 "3 UPCOMING baru dari feed (Stampooor Stamp Packs, Rulz Share, Mimint Share — belum launching). NIGHTFORGE tetap gate-blocked (36,40%). "
 "Scan FAST-FAIL (Ankr 401). binanceai launched=0 (refund phase). 0 age-exclusion baru.")
snap["runNote0831"]=snap["last_run_note"]
snap["runNote0831_scan"]=("Scan run 0831 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized dalam 37,8 dtk "
 "(head 132881140; kuota Ankr 0% s.d. 1 Des 2026; outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~368.000 blok dan tumbuh; backfill OFF).")
snap["runNote0831_binanceai"]="Run 0831: launched=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132882165) — TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong."
snap["runNote0831_bridge"]=("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE), 116 kontrak, 7 same_owner_discarded. "
 "6 kontrak bridge tidak ada di snapshot — sama seperti run 0801 (temuan scan 3-4 Nov, sudah ditriase scan sebagai BUKAN lead); tidak dipromosikan, tidak ditambahkan. Tidak ada temuan pelengkap baru. same-owner-discards.json mtime 2026-11-10 20:22 WIB — tidak ada entri baru.")
json.dump(snap,open(BASE+"onchain-snapshot.json","w"),indent=1)
print("MERGE DONE contracts:",len(C),"track_c:",len(TC))
print("SOLDERCATS:",C["SOLDERCATS"]["status"],C["SOLDERCATS"]["totalSupply"])
print("REWINDCLUB:",C["REWINDCLUB"]["status"],C["REWINDCLUB"]["totalSupply"])
print("PROMO count:",len(PROMO))
