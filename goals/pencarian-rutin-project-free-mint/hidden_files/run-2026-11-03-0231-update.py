import json, copy
base="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(base+"/onchain-snapshot.json"))
read=json.load(open(base+"/run-2026-11-03-0231-read.json"))
extra=json.load(open(base+"/run-2026-11-03-0231-extra.json"))
WIB="2026-11-03T02:45:00+07:00"
# generic updates for non-minted contracts
for name,v in snap["contracts"].items():
    if "minted-by-user" in str(v.get("status")): continue
    cur=read.get(name)
    if not cur: continue
    if cur.get("totalSupply()") is not None: v["totalSupply"]=cur["totalSupply()"]
    if cur.get("freeClaimed()") is not None: v["freeClaimed"]=cur["freeClaimed()"]
    if cur.get("FREE_SUPPLY()") is not None: v["FREE_SUPPLY"]=cur["FREE_SUPPLY()"]
    if cur.get("freeMinted()") is not None: v["freeMinted"]=cur["freeMinted()"]
    if cur.get("balanceOf(address)") is not None: v["userBalance"]=cur["balanceOf(address)"]
    v["lastReadBlock"]=read["block"]; v["lastReadWib"]=WIB
# extra updates
for name, fields in [
 ("River Agent", extra["River Agent"]), ("Deco Agent", extra["Deco Agent"]),
 ("Opera Agent", extra["Opera Agent"]), ("Silk Agent", extra["Silk Agent"]),
 ("Peony Agent", extra["Peony Agent"]), ("QAFUAI", extra["QAFUAI"])]:
    v=snap["contracts"][name]
    if fields.get("totalMinted()") is not None: v["totalMinted"]=fields["totalMinted()"]
    if fields.get("FREE_SUPPLY()") is not None: v["FREE_SUPPLY"]=fields["FREE_SUPPLY()"]
    if fields.get("MAX_SUPPLY()") is not None: v["MAX_SUPPLY"]=fields["MAX_SUPPLY()"]
    if fields.get("freeMinted()") is not None: v["freeMinted"]=fields["freeMinted()"]
    if fields.get("freeRemaining()") is not None: v["freeRemaining"]=fields["freeRemaining()"]
    if fields.get("mintedBy(address)") is not None: v["userMintedBy"]=fields["mintedBy(address)"]
    v["lastReadBlock"]=extra["block"]; v["lastReadWib"]=WIB
# River sold out -> remove
river=snap["contracts"].pop("River Agent", None)
print("River removed:", river["totalMinted"] if river else None, "/", river["FREE_SUPPLY"] if river else None)
# Opera promotion
op=snap["contracts"]["Opera Agent"]
op.update({"status":"strong-lead-gate-blocked-2026-11-03",
 "freePctNote":"INFERENSI totalMinted 287/460 = 62,39% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis)",
 "strongLeadNote":"PROMOSI run 02:31 WIB: (a) umur TERVERIFIKASI first mint 2026-11-03 01:19:34 WIB (~1,4 jam); (b) totalMinted 287/460 = 62,39% INFERENSI (melewati 50% dari 219/460 pada 02:10); (c) slot user terbuka mintedBy=0, costFor(1)=0. Blok 131297718.",
 "gateNote":"Gate website-only GAGAL run 02:31 WIB, metode (A)-(G): (A) pencarian alamat mentah hanya hasil tak terkait (Opera browser/Browser Operator); (B) Boltbook front page 02:31 WIB (en+zh) tidak memuat post Opera/0x32ddd7; (C) Sourcify terverifikasi template pabrik yang sama, tidak ada URL proyek; (D) tidak ada pola situs same-family yang muncul; (E) owner() 0xccd7af9c2e209fb41e24952afdd7945c327974bc, agentIdRegistry() = registry; (F) twitterapi.io tidak dipakai (tidak ada kandidat handle; X opsional); (G) pencarian nama 'Opera Agent' hanya proyek tak terkait; DappBay kategori AI tidak memuat 'Opera Agent' (absence bukan bukti). X opsional, bukan penghambat. TIDAK di-preview, TIDAK di-mint.",
 "velocityNote":"Interval run 02:31: 219 -> 287 (+68) dalam ~37 menit = 1,84/menit vs 1,541 sebelumnya = 1,19x -> velocity leg GAGAL (tidak dipakai untuk promosi strong lead).",
 "currentRatePerMin":1.84, "previousRatePerMin":1.541, "velocityLegPasses":False})
# Silk promotion
si=snap["contracts"]["Silk Agent"]
si.update({"status":"strong-lead-gate-blocked-2026-11-03",
 "freePctNote":"INFERENSI totalMinted 311/387 = 80,36% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis)",
 "strongLeadNote":"PROMOSI run 02:31 WIB: (a) umur TERVERIFIKASI first mint 2026-11-03 01:25:13 WIB (~1,3 jam); (b) totalMinted 311/387 = 80,36% INFERENSI (melewati 50% dari 144/387 pada 02:10); (c) slot user terbuka mintedBy=0, costFor(1)=0. Blok 131297718.",
 "gateNote":"Gate website-only GAGAL run 02:31 WIB, metode (A)-(G): (A) pencarian alamat mentah hanya hasil tak terkait; (B) Boltbook front page 02:31 WIB (en+zh) tidak memuat post Silk/0xF88878; (C) Sourcify terverifikasi template pabrik yang sama, tidak ada URL proyek; (D) tidak ada pola situs same-family yang muncul; (E) owner() 0x1dd3f105d7aeafd1487ce73cf231d4f3f7d7e94d = owner Deco Agent (grup deployer pabrik); (F) twitterapi.io tidak dipakai (tidak ada kandidat handle; X opsional); (G) pencarian nama 'Silk Agent' hanya proyek tak terkait; DappBay kategori AI tidak memuat 'Silk Agent' (absence bukan bukti). X opsional, bukan penghambat. TIDAK di-preview, TIDAK di-mint.",
 "velocityNote":"Interval run 02:31: 144 -> 311 (+167) dalam ~37 menit = 4,51/menit vs 1,459 sebelumnya = 3,09x dan >=20 token -> velocity leg LULUS interval ini (informatif; strong lead tidak menunggu velocity, dan gate tetap memblokir eksekusi).",
 "currentRatePerMin":4.51, "previousRatePerMin":1.459, "velocityLegPasses":True})
# Peony update
pe=snap["contracts"]["Peony Agent"]
pe.update({"freePctNote":"totalMinted 204/425 = 48,00% (totalMinted-based, BUKAN verified free counter) - masih di bawah 50%, tetap EARLY",
 "velocityNote":"Interval run 02:31: 43 -> 204 (+161) dalam ~20 menit (blok 131295546 -> 131297718) = ~8,05/menit; rate pertama tersimpan sebagai baseline.",
 "currentRatePerMin":8.05, "previousTotalSupply":43})
# QAFUAI unchanged values already set; note
qa=snap["contracts"]["QAFUAI"]
qa["freePctNote"]="freeMinted 24/2000 = 1,20% (verified free views FREE_POOL/freeMinted/freeRemaining) - tidak berubah run 02:31, tetap EARLY"
# Yunjin early lead
snap["contracts"]["Yunjin Agent"]={
 "address":"0x6F726D4cF7263f1F7562d5868EC09806d7ef70f8",
 "status":"early-lead-reported-2026-11-03",
 "name":"Yunjin Agent","symbol":"YUNJIN","kind":"ERC721",
 "totalMinted":234,"FREE_SUPPLY":479,"MAX_SUPPLY":1917,
 "freePctNote":"totalMinted 234/479 = 48,85% (totalMinted-based, BUKAN verified free counter)",
 "mintOpen":True,"userMintedBy":0,"userBalance":0,
 "firstSeenBlock":131295702,"scanMints":69,"scanMinters":26,
 "lastReadBlock":131298967,"lastReadWib":WIB,"xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: pre-window Ankr walk 131280000-131295677 menemukan 29 from-zero log, earliest blok 131294060, 2026-11-03 02:06:47 WIB, tx 0x2c94cbe563f07f18b0d7ca71165abf156e4c02f2360978bb405bb3a3b0d53634; window first block 131295702 (02:19:06 WIB). Umur ~40 menit pada run 02:31 (<=48 jam).",
 "baselineNote":"EARLY lead run 02:31 WIB (never previewed/minted). Agent-shape verified: Sourcify verified ABI (mint + costFor + FREE_SUPPLY + agentIdRegistry) dan agentIdRegistry() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain. Slot terbuka (mintedBy=0, costFor(1)=0). X unverified, website unverified, velocity baseline pertama tersimpan.",
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, costFor(1)=0, blok 131298967 - TIDAK di-preview/di-mint (early lead)."}
# pending claims: pollen unchanged, binanceai unchanged
snap["pending_claims"]["hive-pollen"]["lastReadBlock"]=read["block"]
snap["pending_claims"]["hive-pollen"]["lastReadWib0231"]="blok 131297508: launched 0, phase 1, pollenAgents 7827 (sama dengan 02:01), paidSold 1060 (dari 1050) - tetap pending, tidak dilaporkan ulang"
snap["timestamp_wib"]=WIB
snap["note"]=(snap.get("note","")+" | Run 02:31 WIB: River sold out 271/271 lalu dihapus; Opera + Silk promosi ke strong-lead-gate-blocked (gate website-only gagal, tidak di-preview/di-mint); Peony 204/425 = 48,00% tetap early; QAFUAI tetap 24/2000; Yunjin early lead baru (first mint 02:06:47 WIB, 234/479 = 48,85%); scan 131295678-131297677, 80 calls, 0 error, 207 NFT, 706 ERC20, first-seen baru 9 (hanya Yunjin agent-shaped terverifikasi); 5c 0 lolos dari 20, 45 sisanya sampling limit; Sourcify feed 20/20 sudah hot-seen.")
json.dump(snap, open(base+"/onchain-snapshot.json","w"), indent=1)
print("contracts now:", len(snap["contracts"]))
# seen file
seen=json.load(open(base+"/onchain-scan-seen.json"))
firstseen=json.load(open(base+"/run-2026-11-03-0231-scan-firstseen.json"))
for c in firstseen:
    seen["contracts"][c["address"].lower()]=c["first_block"]
json.dump(seen, open(base+"/onchain-scan-seen.json","w"), indent=1)
print("seen contracts:", len(seen["contracts"]))
# scan state
st=json.load(open(base+"/onchain-scan-state.json"))
st["skipped_gap"]=st.get("skipped_gap","")+" ; 131293873-131295677 (1805 blocks, window capped at 2000; scan covered only most recent 2000 blocks 131295678-131297677)"
st.update({"last_scanned_block":131297677,"last_scan_window_from":131295678,"last_scan_window_to":131297677,"last_scan_wib":"2026-11-03T02:45:00+07:00","ankr_calls":80,"errors":[],"nft_contracts":207,"erc20_mint_contracts":706,"last_scan_window":"131295678-131297677","ankr_calls_last_scan":80,"errors_last_scan":0,"from_block":131295678,"to_block":131297677,"last_scan_run":"2026-11-03-0231"})
st["note"]="Scan 0231 run: window 131295678-131297677 (2000 blocks, cap; head-last=3805), 80 Ankr calls, 0 errors, 207 NFT contracts, 706 ERC-20 mint contracts. First-seen new: 9 (agent-shaped verified: Yunjin early lead only; rest 1-7 mints, mostly Sourcify-unverified, seen-only)."
json.dump(st, open(base+"/onchain-scan-state.json","w"), indent=1)
# track-c checked
tc=json.load(open(base+"/track-c-scan-checked.json"))
cands5c=json.load(open(base+"/run-2026-11-03-0231-trackc-5c-cands.json"))
res5c=json.load(open(base+"/run-2026-11-03-0231-trackc-5c.json"))
for c in cands5c:
    tc["checked"][c["address"].lower()]={}
json.dump(tc, open(base+"/track-c-scan-checked.json","w"), indent=1)
print("trackc checked:", len(tc["checked"]))
