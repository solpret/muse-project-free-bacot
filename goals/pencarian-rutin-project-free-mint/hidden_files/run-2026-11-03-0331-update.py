import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
read=json.load(open(BASE+"run-2026-11-03-0331-read.json"))
extra=json.load(open(BASE+"run-2026-11-03-0331-extra.json"))
# backup
json.dump(snap, open(BASE+"onchain-snapshot-2026-11-03-0331.bak.json","w"), indent=1)
# GEN updates: interval from block timestamps 131301776 (03:04:40) -> 131306378 (03:39:11) = 34.52 min
interval_gen=34.52
for name,e in snap["contracts"].items():
    if name not in read: continue
    v=read[name]
    old_ts=e.get("totalSupply"); new_ts=v.get("totalSupply()")
    e["totalSupply"]=new_ts
    if v.get("freeClaimed()") is not None: e["freeClaimed"]=v["freeClaimed()"]
    if v.get("FREE_SUPPLY()") is not None: e["FREE_SUPPLY"]=v["FREE_SUPPLY()"]
    if v.get("mintedBy(address)") is not None: e["userMintedBy"]=v["mintedBy(address)"]
    if v.get("freeUsed(address)") is not None: e["userFreeUsed"]=v["freeUsed(address)"]
    if v.get("balanceOf(address)") is not None: e["userBalance"]=v["balanceOf(address)"]
    if old_ts is not None and new_ts is not None:
        delta=new_ts-old_ts; rate=round(delta/interval_gen,3) if interval_gen else None
        prev_rate=e.get("currentRatePerMin")
        e["previousTotalSupply"]=old_ts; e["mintedInInterval"]=delta; e["intervalMinutes"]=interval_gen
        e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
        e["velocityLegPasses"]=bool(prev_rate and prev_rate>0 and rate>=1.5*prev_rate and delta>=20)
        e["velocityNote"]=f"Run 03:31 WIB (read block 131306378): +{delta} in ~{interval_gen} min = {rate}/min, ratio vs prior {prev_rate} = {(round(rate/prev_rate,2) if prev_rate else None)} -> velocity leg {'PASSES' if e['velocityLegPasses'] else 'FAILS'}."
    e["lastReadBlock"]=131306378; e["lastReadWib"]="2026-11-03T03:51:00+07:00"
# Extra factory contracts: interval 131301969 (03:06:07) -> 131306576 (03:40:41) = 34.57 min
interval_ex=34.57
extra_map={"Caravan Agent":"totalMinted()","Kelp Agent":"totalMinted()","Peony Agent":"totalMinted()","Yunjin Agent":"totalMinted()","Deco Agent":"totalMinted()","Opera Agent":"totalMinted()","Silk Agent":"totalMinted()"}
for name,fn in extra_map.items():
    e=snap["contracts"][name]; r=extra[name]; old=e.get("totalMinted"); new=r.get(fn)
    if new is not None and old is not None:
        delta=new-old; rate=round(delta/interval_ex,3); prev_rate=e.get("currentRatePerMin")
        e["previousTotalMinted"]=old; e["mintedInInterval"]=delta; e["intervalMinutes"]=interval_ex
        e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
        e["velocityLegPasses"]=bool(prev_rate and prev_rate>0 and rate>=1.5*prev_rate and delta>=20)
        e["velocityNote"]=f"Run 03:31 WIB (extra block 131306576): +{delta} in ~{interval_ex} min = {rate}/min, ratio vs prior {prev_rate} = {(round(rate/prev_rate,2) if prev_rate else None)} -> velocity leg {'PASSES' if e['velocityLegPasses'] else 'FAILS'} (first rate if prior None; strong lead does not wait for velocity)."
    e["totalMinted"]=new; e["FREE_SUPPLY"]=r.get("FREE_SUPPLY()"); e["MAX_SUPPLY"]=r.get("MAX_SUPPLY()")
    e["userMintedBy"]=r.get("mintedBy(address)"); e["lastReadBlock"]=131306576; e["lastReadWib"]="2026-11-03T03:51:00+07:00"
    if name=="Kelp Agent":
        e["freePctNote"]="INFERENSI totalMinted 220/438 = 50,23% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis)"
        e["status"]="strong-lead-gate-blocked-2026-11-03"
        e["gateNote"]="Gate website-only GAGAL run 03:31 WIB setelah metode (A)-(G): (A) pencarian alamat mentah hanya hasil tak terkait; (B) Boltbook front page en+zh 03:31 tidak menyebut Kelp/0xf76F0B; (C) metadata Sourcify hanya URL EIP (OpenZeppelin), tidak ada situs proyek; contractURI() None; (D) tidak ada pola situs same-family; (E) owner() 0xccd7af9c2e209fb41e24952afdd7945c327974bc = owner Peony/Opera (grup deployer pabrik, BUKAN pengecualian); (F) twitterapi.io tidak dipakai (tidak ada kandidat handle; X opsional); (G) pencarian nama 'Kelp Agent' hanya proyek tak terkait; DappBay kategori AI tidak memuat 'Kelp Agent' (absence bukan bukti). X opsional, bukan penghambat. TIDAK di-preview/di-mint."
        e["baselineNote"]="EARLY lead reported run 03:01 WIB. PROMOSI ke strong lead run 03:31 WIB (umur terverifikasi + totalMinted 220/438=50,23% inferensi + slot terbuka), GATE-BLOCKED, tidak di-mint."
    if name=="Caravan Agent":
        e["freePctNote"]="INFERENSI totalMinted 135/422 = 31,99% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY"
    if name=="Peony Agent":
        e["freePctNote"]="INFERENSI totalMinted 296/425 = 69,65% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)"
    if name=="Yunjin Agent":
        e["freePctNote"]="INFERENSI totalMinted 395/479 = 82,46% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)"
    if name=="Deco Agent":
        e["freePctNote"]="INFERENSI totalMinted 457/512 = 89,26% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)"
    if name=="Opera Agent":
        e["freePctNote"]="INFERENSI totalMinted 404/460 = 87,83% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)"
    if name=="Silk Agent":
        e["freePctNote"]="INFERENSI totalMinted 379/387 = 97,93% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - mendekati sold out free supply, belum sold out, slot terbuka"
# QAFUAI
q=snap["contracts"]["QAFUAI"]; q["freeMinted"]=extra["QAFUAI"]["freeMinted()"]; q["freeRemaining"]=extra["QAFUAI"]["freeRemaining()"]
q["freePctNote"]="freeMinted 38/2000 = 1,90% (verified free views FREE_POOL/freeMinted/freeRemaining) - tetap EARLY"
q["lastReadBlock"]=131306576; q["lastReadWib"]="2026-11-03T03:51:00+07:00"
# New early leads
snap["contracts"]["Mechfarm"]={
 "address":"0xde536232c09ea778b6cb8409328362F7e9182bc9","name":"Mechfarm","symbol":"MCHFRM","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalSupply":35,"freeClaimed":35,"FREE_SUPPLY":5555,"MAX_SUPPLY":5555,
 "freePctVerified":0.63,"mintOpen":True,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, blok 131306576 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131305346,"scanMints":33,"scanMinters":24,
 "lastReadBlock":131306576,"lastReadWib":"2026-11-03T03:51:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: pre-window walk 131280000-131304363 = 0 from-zero log; window first Transfer-from-zero blok 131305346, 2026-11-03 03:31:27 WIB, tx 0x819c7c335a1a366a4fb274c4e64eef972b45a9a5d76500a875d63c1a6d03bb8f; 35 from-zero log di walk (26+9) = totalSupply 35; 35 mint/25 minter di hitung ulang jendela 131304000-131306576 (scan: 33 mint/24 minter sampai blok 131306233, selisih karena bacaan segar lebih baru). Umur ~20 menit pada laporan.",
 "baselineNote":"EARLY lead reported once run 03:31 WIB. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI (mint + quote + freeClaimed/freeFor/freeLeft/freeUsed + AGENT_ID) dan AGENT_ID() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F on-chain; contractURI on-chain: 'Mechfarm is 5,555 mech farmer robots... Mint is gated to .ai Agent ID holders' - TANPA URL situs (bukan bukti website). Sourcify feed saat scan IncompleteRead, dicatat jelas. Owner 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (= owner Dronegent)."}
snap["contracts"]["Dronegent"]={
 "address":"0xF6Ab7131b01F0a94e8860C284fC904D09ED0373b","name":"Dronegent","symbol":"DRNGNT","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalSupply":99,"freeClaimed":92,"FREE_SUPPLY":5555,"MAX_SUPPLY":5555,
 "freePctVerified":1.66,"mintOpen":None,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131304570,"scanMints":64,"scanMinters":46,
 "lastReadBlock":131306576,"lastReadWib":"2026-11-03T03:51:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: pre-window walk 131280000-131304363 menemukan 15 from-zero log, earliest blok 131303467, 2026-11-03 03:17:21 WIB, tx 0xad637c30c7ead6f40ab7846a240846b7ab897f936ec928a08991691c3b4f61db; Sourcify verifiedAt 2026-11-02T20:17:30Z (=03:17:30 WIB) menguatkan peluncuran ~03:17. Hitungan log (15 pre + 64 window = 79) tertinggal dari totalSupply 99 / freeClaimed 92 pada bacaan segar yang lebih baru - selisih dicatat, bukan disembunyikan.",
 "baselineNote":"EARLY lead reported once run 03:31 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: AGENT_ID() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + freeClaimed view + quote 0; Sourcify saat scan RemoteDisconnected (bukan verified, dicatat jelas). Owner 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (= owner Mechfarm)."}
snap["contracts"]["Jelly Agent"]={
 "address":"0xE20638C26Fd7EAC342a4164b4F026754375AEbfE","name":"Jelly Agent","symbol":"JELLY","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalMinted":76,"FREE_SUPPLY":471,"MAX_SUPPLY":1967,
 "freePctNote":"INFERENSI totalMinted 76/471 = 16,13% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis)",
 "mintOpen":True,"userMintedBy":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, costFor(1)=0 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131304408,"scanMints":45,"scanMinters":21,
 "lastReadBlock":131306576,"lastReadWib":"2026-11-03T03:51:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: pre-window walk 131280000-131304363 menemukan 15 from-zero log, earliest blok 131304030, 2026-11-03 03:21:35 WIB, tx 0x6d2292e89255a94b9b5d34c34cd7f78ce69debdfec85caa1e637ec094adea96b; hitungan log (15 pre + 45 window = 60) tertinggal dari totalMinted 76 pada bacaan segar yang lebih baru - selisih dicatat.",
 "baselineNote":"EARLY lead reported once run 03:31 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: agentIdRegistry() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + costFor 0 + FREE_SUPPLY; Sourcify saat scan IncompleteRead (bukan verified, dicatat jelas). Owner 0xccd7af9c2e209fb41e24952afdd7945c327974bc (grup deployer pabrik Peony/Opera/Kelp)."}
snap["contracts"]["Flora Agent"]={
 "address":"0x1C89AcaB7A497F537f988b5f20055fd11B062f50","name":"Flora Agent","symbol":"FLORA","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalMinted":60,"FREE_SUPPLY":598,"MAX_SUPPLY":2137,
 "freePctNote":"INFERENSI totalMinted 60/598 = 10,03% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis)",
 "mintOpen":True,"userMintedBy":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, costFor(1)=0 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131306152,"scanMints":22,"scanMinters":6,
 "lastReadBlock":131306576,"lastReadWib":"2026-11-03T03:51:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: pre-window walk 131280000-131304363 = 0 from-zero log; window first Transfer-from-zero blok 131306152, 2026-11-03 03:37:30 WIB. Hitungan log scan (22) tertinggal dari totalMinted 60 pada bacaan segar blok 131306576 (burst minting di ~424 blok berikutnya) - selisih dicatat.",
 "baselineNote":"EARLY lead reported once run 03:31 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: agentIdRegistry() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F + costFor 0 + FREE_SUPPLY; Sourcify saat scan IncompleteRead (bukan verified, dicatat jelas). Owner 0x1dd3f105d7aeafd1487ce73cf231d4f3f7d7e94d (grup deployer pabrik Silk/Deco/Yunjin)."}
# pending claims last-read update
pc=snap["pending_claims"]["hive-pollen"]; pc["lastReadBlock"]=131306378; pc["lastReadWib"]="2026-11-03T03:51:00+07:00"
pc["lastReadWib0331"]="blok 131306378: launched 0, phase 1, pollenAgents 7827 (sama), paidSold 1060 (sama) - tetap pending, tidak dilaporkan ulang"
snap["timestamp_wib"]="2026-11-03T03:51:00+07:00"
snap["note"]="Main run 03:31 WIB: route-1 read block 131306378 + extra block 131306576; Kelp promosi strong lead, GATE website-only GAGAL (A)-(G), tidak di-mint; Mechfarm + Dronegent + Jelly + Flora early lead baru; scan 131304364-131306363 sukses (cap 2000, gap 131301720-131304363 terlewat); 5c 20/20 gagal bentuk S1/S2."
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("contracts now:", len(snap["contracts"]))
# seen file: append 8 first-seen
seen=json.load(open(BASE+"onchain-scan-seen.json"))
print("seen structure:", {k: (len(v) if hasattr(v,'__len__') else type(v)) for k,v in seen.items()})
new8={
 "0xF6Ab7131b01F0a94e8860C284fC904D09ED0373b":131304570,
 "0xE20638C26Fd7EAC342a4164b4F026754375AEbfE":131304408,
 "0xde536232c09ea778b6cb8409328362F7e9182bc9":131305346,
 "0x1C89AcaB7A497F537f988b5f20055fd11B062f50":131306152,
 "0x20Ef1DCf7152ac921CF98A475cB5262E9De56260":131304404,
 "0x2535E83109909c7B9eA22D5b2f7c8621E595e3Dd":131304392,
 "0x28D6BDB41B6A968E1b7b711859aE8793EA203e2E":131305530,
 "0x387Ea21134142d989007AD6391b8104e6B940582":131305945,
}
if "contracts" in seen and isinstance(seen["contracts"], dict):
    for a,b in new8.items(): seen["contracts"][a]=b
    print("seen contracts now:", len(seen["contracts"]))
json.dump(seen, open(BASE+"onchain-scan-seen.json","w"), indent=1)
# scan state
state=json.load(open(BASE+"onchain-scan-state.json"))
state["last_scanned_block"]=131306363; state["last_scan_window_from"]=131304364; state["last_scan_window_to"]=131306363
state["last_scan_wib"]="2026-11-03T03:51:00+07:00"; state["last_scan_run"]="2026-11-03-0331"; state["from_block"]=131304364; state["to_block"]=131306363
state["contracts_in_window"]=243; state["erc20_mint_contracts_in_window"]=690
state["skipped_gap"]=state.get("skipped_gap","")+" ; 131301720-131304363 (2644 blocks, window capped at 2000; scan covered only most recent 2000 blocks 131304364-131306363)"
state["note"]="Scan 0331 run: window 131304364-131306363 (2000 blocks, cap; head-last=4644), 0 errors, 243 NFT contracts, 690 ERC-20 mint contracts. First-seen new: 8 (agent-shaped verified on-chain: Mechfarm + Dronegent + Jelly + Flora early leads; Velvet Purr, BlockHound, Voucher, BlockAir seen-only, no agent evidence). Ankr call count not printed by script output for this run - not recorded as a number."
json.dump(state, open(BASE+"onchain-scan-state.json","w"), indent=1)
# track-c checked: add 20
tc=json.load(open(BASE+"track-c-scan-checked.json"))
cands=json.load(open(BASE+"run-2026-11-03-0331-trackc-5c-cands.json"))
for c in cands: tc["checked"][c["address"]]={}
tc["note"]=tc.get("note","")+" | Run 03:31 WIB: +20 (888 -> 908), 0 S1/S2 pass (13 fail shape, 7 ABI-empty inconclusive)."
json.dump(tc, open(BASE+"track-c-scan-checked.json","w"), indent=1)
print("track-c checked now:", len(tc["checked"]))
