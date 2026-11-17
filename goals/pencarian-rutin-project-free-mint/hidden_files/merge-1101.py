import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
re=json.load(open(f"{BASE}/run-2026-11-07-1101-reread.json"))
vel=json.load(open(f"{BASE}/run-2026-11-07-1101-velocity.json"))
BLOCK=re["block"]
vrows={r["name"]:r for r in vel["rows"]}
n_upd=0
for name,d in re["reread"].items():
    s=snap["contracts"].get(name)
    if s is None: continue
    cur=d.get("totalSupply")
    if cur is None: cur=d.get("totalMinted")
    if isinstance(cur,int):
        s["previousTotalSupply"]=s.get("totalSupply")
        s["totalSupply"]=cur
    s["lastReadBlock"]=BLOCK
    s["lastReadWib"]="2026-11-07 run 1101"
    vr=vrows.get(name)
    if vr:
        s["mintedInInterval"]=vr.get("mintedInInterval")
        s["intervalMinutes"]=vr.get("intervalMin")
        s["currentRatePerMin"]=vr.get("ratePerMin")
        s["previousRatePerMin"]=vr.get("prevRatePerMin")
        s["velocityLegPasses"]=vr.get("velocityPasses")
        if vr.get("freePct") is not None:
            s["freePctInference"]=vr["freePct"]
    n_upd+=1
# track_c last-read stamps
for name,d in re.get("track_c",{}).items():
    t=snap.get("track_c",{}).get(name)
    if isinstance(t,dict):
        t["lastReadBlock"]=BLOCK
        t["lastReadWib"]="2026-11-07 run 1101"
# MizzlewickAgent track-C lead, GATE-BLOCKED (no verified website)
snap.setdefault("track_c",{})["MizzlewickAgent"]={
 "sale":"0x892E438425b3A41BC75b25C22Fd878b3fa2e308d",
 "token":"0x892E438425b3A41BC75b25C22Fd878b3fa2e308d",
 "status":"lead-gate-blocked-2026-11-07",
 "saleShape":"PASS (S1): mint(uint256) + quote(address,uint256)->(freeShares,costBnb) + freeUsed view + AGENT_ID_REGISTRY()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact, Sourcify verified (24 fns)",
 "name":"MizzlewickAgent","symbol":"MZWK","decimals":18,
 "MAX_SHARES":1000,"sharesSold":116,"FREE_PER_AGENT":1,
 "TOKENS_PER_SHARE":1000000000000000000000000,
 "PRICE_PER_SHARE":100000000000000,"AGENT_PRICE_PER_SHARE":1000000000000000,
 "quote_user_1":"(freeShares=1, costBnb=0)",
 "freeUsed_user":0,"isAgent_user":True,"mintedBy_user":0,"balanceOf_user":0,
 "firstMintWib":"2026-11-07 10:41:45","firstMintBlock":132130472,"ageHoursAt1101":"~1.0",
 "ageNote":"VERIFIED <=48h: first Minted event on-chain block 132130472, 2026-11-07 10:41:45 WIB (run 1031 firstmint-892e-1031.log); deadline 2026-11-09 10:41 WIB",
 "auditBinance":"hasResult=true, riskLevel 2 LOW, riskAlert None; only hit 'Newly Created Token' (CAUTION, not RISK) - audit-892e-1101.json",
 "gate":"FAILED - no verified project website after methods (A)-(N): (A) contract-address search no hits; (B) Boltbook front pages dead (HTTP 302, 0-byte body) + hot-leg 1109 0 new; (C) Sourcify metadata no URLs; (D) no same-family pattern known; (E) no owner() on contract; (F) no X handle found to confirm; (G) project-name search 'MizzlewickAgent'/'MZWK' no hits; (H) no contractURI fn; (I) tokenURI N/A; (J) ABI has no website/siteURL/domain/external fn; (K) GitHub search-index no hits (true code search needs auth - limitation stated); (L) BscScan token page via live browser: page loaded, Info tab lists NO official links (no website/X/Telegram/Discord); (M) site:vercel/pages/deed filters no hits; (N) registry-profile hop N/A for fungible sale. DO NOT preview, DO NOT execute. Reported once as gate-blocked lead run 1101.",
 "lastCheckBlock":BLOCK,"lastCheckWib":"2026-11-07 run 1101",
 "boundary":"LEAD ONLY, GATE-BLOCKED. NEVER previewed/minted in this run. TRACK-C LEAD DIRECT MINT does NOT trigger: mandatory website gate failed first."
}
snap["runNote1101_1107"]=("Run 1101: 0 kandidat, 0 strong lead baru, 0 early lead baru, 0 track-C lead/kandidat baru yang bisa dieksekusi, 0 pending claim baru/dibuka. "
 "Preflight PASS 4,9 dtk (head 132135793). Reread 463 kontrak + 57 track_c, blok 132135865. Scan SUKSES window 132134866-132135865 (1000 blok, cap), 69 NFT + 143 ERC-20 mint, 9 Ankr calls (tercatat), 2 chunk timeout (TransferSingle 132135066-132135115, Transfer 132135116-132135165 - 100 blok cakupan parsial, ditutup backfill); 0 first-seen sejati. "
 "Velocity 11 pass, semua freePct None/<50% (tertinggi Hackagent 39,64% tapi status promotion-discarded-same-owner; Hotpotsage 52,55% tapi velocity GAGAL ratio None + minted-by-user; Agent Goats 47,9% velocity GAGAL ratio 0,38, gate-blocked, deadline umur 12:55:17 WIB). Sold out 34 (sama dgn 0901, tanpa sellout baru); near-sellout SEAT-f11e 4977/5000, Dumpster Royalty 632/650. "
 "Sourcify feed 20 kontrak, 0 S1/S2 baru. 5c: 2 ERC-20 baru dicek (0x6777..., 0xd84D...), 0 shape hit. Boltbook mati (HTTP 302, body 0-byte). Bridge: tidak berubah, 0 promosi. Pending claims kosong; BINANCEAI tetap refund/failed. "
 "TRACK-C LEAD GATE-BLOCKED (dilaporkan sekali): MizzlewickAgent (MZWK) 0x892E438425b3A41BC75b25C22Fd878b3fa2e308d - S1 lolos, sharesSold 116/1000, quote(user,1)=(freeShares=1,costBnb=0), umur ~1 jam, audit Binance LOW (riskLevel 2, tanpa RISK) - TAPI gate website GAGAL (semua metode A-N, termasuk BscScan Info tanpa tautan resmi) - TIDAK di-preview/dimint.")
snap["last_run"]="2026-11-07-1101"
snap["last_run_wib"]="2026-11-07 11:01 WIB (dieksekusi ~11:20-11:55 WIB)"
snap["last_run_note"]=snap["runNote1101_1107"]
snap["timestamp_wib"]="2026-11-07 11:01 WIB"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("contracts updated:", n_upd)
print("track_c keys:", len(snap["track_c"]))
# scan state
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st["last_scanned_block"]=132135865
st["last_scan_window_from"]=132134866
st["last_scan_window_to"]=132135865
st["last_scan_wib"]="run 2026-11-07-1101"
st["note_1101_scan"]="Run 1101 SUKSES window 132134866-132135865 (1000 blok, cap), 69 NFT + 143 ERC-20 mint, 9 Ankr calls (tercatat), 2 chunk timeout (TransferSingle 132135066-132135115, Transfer 132135116-132135165); 0 first-seen sejati. Gap parsial 132135066-132135165 (100 blok) ditutup backfill."
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
print("scan state updated")
