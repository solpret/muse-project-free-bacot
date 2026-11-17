import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap=json.load(open(BASE+"onchain-snapshot.json"))
read=json.load(open(BASE+"run-2026-11-03-0401-read.json"))
extra2=json.load(open(BASE+"run-2026-11-03-0401-extra2.json"))
fresh=json.load(open(BASE+"run-2026-11-03-0401-fresh.json"))
json.dump(snap, open(BASE+"onchain-snapshot-2026-11-03-0401.bak.json","w"), indent=1)
interval_gen=25.67  # 0331 GEN read 20:39:54 UTC -> 0401 GEN read 21:05:34 UTC
for name,e in snap["contracts"].items():
    if name not in read: continue
    v=read[name]
    old_ts=e.get("totalSupply"); new_ts=v.get("totalSupply()")
    e["totalSupply"]=new_ts
    if v.get("freeClaimed()") is not None: e["freeClaimed"]=v["freeClaimed()"]
    if v.get("FREE_SUPPLY()") is not None: e["FREE_SUPPLY"]=v["FREE_SUPPLY()"]
    if v.get("freeMinted()") is not None: e["freeMinted"]=v["freeMinted()"]
    if v.get("freeLeft()") is not None: e["freeLeft"]=v["freeLeft()"]
    if v.get("mintedBy(address)") is not None: e["userMintedBy"]=v["mintedBy(address)"]
    if v.get("freeUsed(address)") is not None: e["userFreeUsed"]=v["freeUsed(address)"]
    if v.get("balanceOf(address)") is not None: e["userBalance"]=v["balanceOf(address)"]
    if old_ts is not None and new_ts is not None:
        delta=new_ts-old_ts; rate=round(delta/interval_gen,3)
        prev_rate=e.get("currentRatePerMin")
        e["previousTotalSupply"]=old_ts; e["mintedInInterval"]=delta; e["intervalMinutes"]=interval_gen
        e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
        e["velocityLegPasses"]=bool(prev_rate and prev_rate>0 and rate>=1.5*prev_rate and delta>=20)
        e["velocityNote"]=f"Run 04:01 WIB (read block 131309808): +{delta} in ~{interval_gen} min = {rate}/min, ratio vs prior {prev_rate} = {(round(rate/prev_rate,2) if prev_rate else None)} -> velocity leg {'PASSES' if e['velocityLegPasses'] else 'FAILS'}."
    e["lastReadBlock"]=131309808; e["lastReadWib"]="2026-11-03T04:26:00+07:00"
interval_ex=26.22  # 0331 extra block 131306576 (03:40:41 WIB) -> 0401 extra2 block 131310011
extra_map={"Caravan Agent":"totalMinted()","Kelp Agent":"totalMinted()","Peony Agent":"totalMinted()","Yunjin Agent":"totalMinted()","Deco Agent":"totalMinted()","Opera Agent":"totalMinted()","Silk Agent":"totalMinted()","Jelly Agent":"totalMinted()","Flora Agent":"totalMinted()"}
pct_notes={
 "Kelp Agent":"INFERENSI totalMinted 262/438 = 59,82% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - tetap >50%, strong-lead-gate-blocked, tidak di-mint",
 "Jelly Agent":"INFERENSI totalMinted 111/471 = 23,57% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY",
 "Flora Agent":"INFERENSI totalMinted 171/598 = 28,60% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY",
 "Caravan Agent":"INFERENSI totalMinted 154/422 = 36,49% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY",
 "Silk Agent":"INFERENSI totalMinted 386/387 = 99,74% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis) - mendekati sold out free supply, BELUM sold out, slot terbuka",
 "Peony Agent":"INFERENSI totalMinted 350/425 = 82,35% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)",
 "Yunjin Agent":"INFERENSI totalMinted 411/479 = 85,80% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)",
 "Deco Agent":"INFERENSI totalMinted 459/512 = 89,65% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)",
 "Opera Agent":"INFERENSI totalMinted 406/460 = 88,26% (bukan verified free counter; costFor(1)=0 mendukung jalur gratis)",
}
for name,fn in extra_map.items():
    e=snap["contracts"][name]; r=extra2[name]; old=e.get("totalMinted"); new=r.get(fn)
    if new is not None and old is not None:
        delta=new-old; rate=round(delta/interval_ex,3); prev_rate=e.get("currentRatePerMin")
        e["previousTotalMinted"]=old; e["mintedInInterval"]=delta; e["intervalMinutes"]=interval_ex
        e["previousRatePerMin"]=prev_rate; e["currentRatePerMin"]=rate
        e["velocityLegPasses"]=bool(prev_rate and prev_rate>0 and rate>=1.5*prev_rate and delta>=20)
        e["velocityNote"]=f"Run 04:01 WIB (extra2 block 131310011): +{delta} in ~{interval_ex} min = {rate}/min, ratio vs prior {prev_rate} = {(round(rate/prev_rate,2) if prev_rate else None)} -> velocity leg {'PASSES' if e['velocityLegPasses'] else 'FAILS'} (strong lead tidak menunggu velocity; early lead belum promosi)."
    e["totalMinted"]=new
    e["userMintedBy"]=r.get("mintedBy(address)"); e["lastReadBlock"]=131310011; e["lastReadWib"]="2026-11-03T04:26:00+07:00"
    if name in pct_notes: e["freePctNote"]=pct_notes[name]
# Mechfarm + Dronegent GEN updates already applied above (totalSupply/freeClaimed); add fresh note
for nm, ts, fc in [("Mechfarm",67,63),("Dronegent",163,156)]:
    e=snap["contracts"][nm]
    e["freePctVerified"]=round(100*fc/5555,2)
    e["freePctNote"]=f"freeClaimed terverifikasi {fc}/5555 = {round(100*fc/5555,2)}% run 04:01 WIB (blok 131309808) - masih <50%, tetap EARLY"
    e["lastReadBlock"]=131309808
q=snap["contracts"]["QAFUAI"]; q["freeMinted"]=38
q["freePctNote"]="freeMinted 38/2000 = 1,90% (verified free views) - tetap EARLY, tidak berubah run 04:01 WIB"
q["lastReadBlock"]=131309808
# New early leads
snap["contracts"]["Hexagent"]={
 "address":"0x7BA27f90c7b509af1dFBDa2a788Fe4488ff3aab4","name":"Hexagent","symbol":"HEXAGT","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalSupply":40,"freeClaimed":40,"FREE_SUPPLY":3333,"MAX_SUPPLY":3333,
 "freePctVerified":1.20,"mintOpen":True,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0, blok 131311318 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131309590,"scanMints":16,"scanMinters":9,
 "lastReadBlock":131311318,"lastReadWib":"2026-11-03T04:26:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: walk 131290000-head menemukan 36 from-zero log, earliest blok 131309590, 2026-11-03 04:03:17 WIB, tx 0x0597c5d0d9bde49454a892827999e6564ad5acd884027b567150691255b72055; Sourcify verifiedAt 2026-11-02T21:03:24Z (=04:03:24 WIB) menguatkan peluncuran ~04:03. Hitungan log (36) tertinggal dari freeClaimed 40 pada bacaan segar yang lebih baru (burst) - selisih dicatat.",
 "baselineNote":"EARLY lead reported once run 04:01 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: AGENT_ID() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis + freeClaimed view + quote 0; Sourcify saat verifikasi RemoteDisconnected/IncompleteRead (bukan verified, dicatat jelas). contractURI on-chain (base64 JSON): 'Hexagent is 3,333 server-farm guardian androids... Mint is gated to .ai Agent ID holders' - TANPA URL situs (bukan bukti website). Owner 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (= owner Mechfarm/Dronegent)."}
snap["contracts"]["Halo Agent"]={
 "address":"0x56503C6540411ABa95824A047c50651dcE625Fb3","name":"Halo Agent","symbol":"HALO","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalMinted":22,"FREE_SUPPLY":397,"MAX_SUPPLY":1588,
 "freePctNote":"INFERENSI totalMinted 22/397 = 5,54% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY",
 "mintOpen":True,"userMintedBy":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, costFor(1)=0, blok 131311318 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131310192,"scanMints":2,"scanMinters":2,
 "lastReadBlock":131311318,"lastReadWib":"2026-11-03T04:26:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: walk 131290000-head menemukan 21 from-zero log, earliest blok 131310192, 2026-11-03 04:07:48 WIB, tx 0x0d585c60f307b367cfc0d6a55ccee6b53a6b8925b41276360b430503241d75e9; Sourcify verifiedAt 2026-11-02T21:00:35Z (=04:00:35 WIB) adalah verifikasi SEBELUM mint pertama (verifiedAt bukan launch time). Hitungan log (21) vs totalMinted 22 segar - selisih 1 (burst) dicatat.",
 "baselineNote":"EARLY lead reported once run 04:01 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: agentIdRegistry() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis + costFor 0 + FREE_SUPPLY; Sourcify saat verifikasi RemoteDisconnected/IncompleteRead (bukan verified, dicatat jelas). contractURI() None (bukan bukti website). Owner 0xccd7af9c2e209fb41e24952afdd7945c327974bc (grup deployer pabrik Peony/Opera/Kelp). Catatan nama: deployment Halo Agent lain yang sempat ditolak sebelumnya bersimbol HALOAGENT dan tanpa free shape - deployment ini (HALO) BERBEDA dan MEMILIKI free shape, jadi dinilai sendiri."}
snap["contracts"]["Dronagent"]={
 "address":"0x307157fb80A63bD4C845f44f5a55Dd90127D8C50","name":"Dronagent","symbol":"DRNAGT","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalSupply":66,"freeClaimed":62,"FREE_SUPPLY":2222,
 "freePctVerified":2.79,"mintOpen":True,"userMintedBy":0,"userFreeUsed":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, freeUsed(user)=0, quote(user,1)=0 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131307647,"scanMints":25,"scanMinters":16,
 "lastReadBlock":131310011,"lastReadWib":"2026-11-03T04:26:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: walk 131290000-head menemukan 67 from-zero log, earliest blok 131307647, 2026-11-03 03:48:43 WIB, tx 0x21dabdadfdb5cc2d802c7370baea8f1cb7b01b26fd2f092fbc04d64ea7d96724; Sourcify verifiedAt 2026-11-02T20:48:54Z (=03:48:54 WIB) menguatkan peluncuran ~03:48. Hitungan log (67) vs totalSupply 66 - selisih 1 dicatat (kemungkinan burn/log noise).",
 "baselineNote":"EARLY lead reported once run 04:01 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: AGENT_ID() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis + freeClaimed view + quote 0; Sourcify saat scan IncompleteRead (bukan verified, dicatat jelas); hot-leg mencatatnya sebagai S1-literal NFT (bukan track-C). Owner 0xd76d5918fb337667b22fe37ae2055b5542cf8dc9 (= owner Mechfarm/Dronegent). BERBEDA dari Dronegent (DRNGNT) - nama/simbol/kontrak berbeda."}
snap["contracts"]["Zephyr Agent"]={
 "address":"0xE41b54504aa171D92E01384aE3aB3007E170Aa70","name":"Zephyr Agent","symbol":"ZEPHYR","kind":"ERC721",
 "status":"early-lead-reported-2026-11-03","totalMinted":22,"FREE_SUPPLY":333,
 "freePctNote":"INFERENSI totalMinted 22/333 = 6,61% (bukan verified free counter: tidak ada freeClaimed view; costFor(1)=0 mendukung jalur gratis) - masih <50%, tetap EARLY",
 "mintOpen":True,"userMintedBy":0,"userBalance":0,
 "userSlotNote":"Slot terbuka: mintedBy(user)=0, costFor(1)=0 - TIDAK di-preview/di-mint (early lead).",
 "firstSeenBlock":131310201,"scanMints":2,"scanMinters":2,
 "lastReadBlock":131310011,"lastReadWib":"2026-11-03T04:26:00+07:00","xVerified":False,"velocityVerified":False,
 "launchNote":"First mint TERVERIFIKASI on-chain: walk 131290000-head menemukan 22 from-zero log, earliest blok 131310201, 2026-11-03 04:07:52 WIB, tx 0xc19dcbe1453d83ef1575281bb2f7307f4402e25906e9702f0587deda2ede9fe9; Sourcify verifiedAt 2026-11-02T20:48:23Z (=03:48:23 WIB) adalah verifikasi SEBELUM mint pertama (verifiedAt bukan launch time). Hitungan log (22) = totalMinted 22 persis.",
 "baselineNote":"EARLY lead reported once run 04:01 WIB. Never auto-minted/previewed. Agent-shape verified on-chain: agentIdRegistry() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis + costFor 0 + FREE_SUPPLY; Sourcify saat scan IncompleteRead (bukan verified, dicatat jelas). Catatan koreksi: hot-leg sempat mencatatnya checked-not-sale-shape berdasar ABI Sourcify yang gagal dibaca - verifikasi view on-chain langsung run ini MEMBUKTIKAN agent-shape, jadi tetap early lead NFT (bukan track-C)."}
pc=snap["pending_claims"]["hive-pollen"]; pc["lastReadBlock"]=131309808; pc["lastReadWib"]="2026-11-03T04:26:00+07:00"
pc["lastReadNote0401"]="blok 131309808: launched 0, phase 1, pollenAgents 7827 (sama), paidSold 1061 (+1 dari 1060) - tetap PENDING, bukan pembukaan klaim, tidak dilaporkan ulang"
snap["timestamp_wib"]="2026-11-03T04:26:00+07:00"
snap["note"]="Main run 04:01 WIB: route-1 read block 131309808 + extra2 block 131310011 + fresh block 131311318; Hexagent + Halo Agent + Dronagent + Zephyr Agent early lead baru (tidak di-preview/di-mint); Fanerswan + Bakunap first-seen tapi free pool SUDAH habis (seen-only, tidak dilaporkan); Kelp tetap strong-lead-gate-blocked; scan 131308240-131310239 sukses (cap 2000, gap 131306364-131308239 terlewat); 5c 20/20 gagal bentuk S1/S2."
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("contracts now:", len(snap["contracts"]))
seen=json.load(open(BASE+"onchain-scan-seen.json"))
new12={
 "0x307157fb80A63bD4C845f44f5a55Dd90127D8C50":131307647,
 "0x7BA27f90c7b509af1dFBDa2a788Fe4488ff3aab4":131309590,
 "0x73288b54F881af643Aea2B742875906E410705B4":131308240,
 "0x07A67233c92f69dE838F43A5803BBedC2bcDCFeF":131308240,
 "0x0F02DE011F293CfBF49977C21E212f39b4485D27":131308240,
 "0xE41b54504aa171D92E01384aE3aB3007E170Aa70":131310201,
 "0x56503C6540411ABa95824A047c50651dcE625Fb3":131310192,
 "0xe489b2e46A4B21Ac769aA20cE703F0d47AD227Cf":131308240,
 "0x738304412FD058C912cAD05FBAc7c89ab9495732":131308240,
 "0x6fd05699cA5A9d325298CFB9F95B19ed9D02a880":131308240,
 "0x3A808A23dC299C5c6BcEEEa900ba5FE9B1cD43B6":131308240,
 "0x2Bdf3cB9138F3Ef71DD6A83aB24eA25DD540B974":131308240,
}
for a,b in new12.items(): seen["contracts"][a]=b
print("seen contracts now:", len(seen["contracts"]))
json.dump(seen, open(BASE+"onchain-scan-seen.json","w"), indent=1)
state=json.load(open(BASE+"onchain-scan-state.json"))
state["last_scanned_block"]=131310239; state["last_scan_window_from"]=131308240; state["last_scan_window_to"]=131310239
state["last_scan_wib"]="2026-11-03T04:26:00+07:00"; state["last_scan_run"]="2026-11-03-0401"; state["from_block"]=131308240; state["to_block"]=131310239
state["contracts_in_window"]=226; state["erc20_mint_contracts_in_window"]=654; state["ankr_calls"]=80; state["errors"]=[]
state["skipped_gap"]=state.get("skipped_gap","")+"; 131306364-131308239 (1876 blocks, window capped at 2000; scan covered only most recent 2000 blocks 131308240-131310239)"
state["note"]="Scan 0401 run: window 131308240-131310239 (2000 blocks, cap; head-last=3876), 0 errors, 80 Ankr calls, 226 NFT contracts, 654 ERC-20 mint contracts. First-seen new: 12 (agent-shaped verified on-chain: Hexagent + Halo Agent + Dronagent + Zephyr Agent early leads; Fanerswan + Bakunap free pool already sold out at first sight, seen-only; Catties, PSYKO Licence, Blunt Signal, Drift Alloy, Ember Lattice, Flint Vector seen-only, no agent evidence)."
json.dump(state, open(BASE+"onchain-scan-state.json","w"), indent=1)
tc=json.load(open(BASE+"track-c-scan-checked.json"))
cands=json.load(open(BASE+"run-2026-11-03-0401-trackc-5c-cands.json"))
for c in cands: tc["checked"][c["address"]]={}
tc["note"]=tc.get("note","")+" | Run 04:01 WIB: +20 (906 -> 926), 0 S1/S2 pass (19 ABI-empty inconclusive, 1 fail shape)."
json.dump(tc, open(BASE+"track-c-scan-checked.json","w"), indent=1)
print("track-c checked now:", len(tc["checked"]))
