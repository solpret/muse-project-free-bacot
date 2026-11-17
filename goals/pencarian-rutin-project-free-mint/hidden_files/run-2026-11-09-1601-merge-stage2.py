#!/usr/bin/env python3
"""Merge STAGE 2 run 2026-11-09 1601 WIB — discovery incorporation (Agentite +
Motor Agent early leads, 0x3314 checked-not-lead), velocity-promotion rulings,
NIBULL/NUSA/ORDIagent track_c notes, final run notes. Read-only w.r.t. chain.
Writes: onchain-snapshot.json (atomic), run-2026-11-09-1601-merge-stage2.json."""
import json, shutil
from datetime import datetime, timezone, timedelta
HF="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW=datetime.now(timezone(timedelta(hours=7)))
snap=json.load(open(f"{HF}/onchain-snapshot.json"))
m1=json.load(open(f"{HF}/run-2026-11-09-1601-merge-stage1.json"))
r1601=json.load(open(f"{HF}/run-2026-11-09-1601-reread.json"))
tri=json.load(open(f"{HF}/run-2026-11-09-1601-triage-new.json"))
tri2=json.load(open(f"{HF}/run-2026-11-09-1601-triage-new2.json"))
BLOCK=r1601["block"]
contracts=snap.setdefault("contracts",{})
tc=snap.setdefault("track_c",{})
report={"run":"2026-11-09-1601","stage":2,"block":BLOCK,
        "early_leads_new":["Agentite","Motor Agent"],"checked_not_lead":["0x331426d06CA0F9616D121888e3Fe60E2C3E42354"],
        "promotions":[],"velocity_rulings":{},"track_c_notes":{}}
# ---- 1. Agentite (early lead) ----
contracts["Agentite"]={
 "address":"0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2",
 "market":"0x0910182F40D3B60f2577De79aBdecf7915178cEF",
 "status":"early-lead-reported-2026-11-09",
 "name":"Agentite","symbol":"AGT","kind":"ERC721",
 "source":"Boltbook front page EN+ZH + recheck posts, run 1601 discovery",
 "website":"https://agentite.pages.dev",
 "websiteEvidence":"agent.json (site doc) prints exact contracts: nft 0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2 + marketplace 0x0910182F40D3B60f2577De79aBdecf7915178cEF + registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; site front page: free mint 1,000, agents only, 1/wallet, gas only; mintFree(expiry, signature) backend-signed",
 "xHandle":"@agentite_gems (per Boltbook launch post; first handle @agentite_nft suspended hours after launch; profile belum diverifikasi langsung)",
 "xVerified":False,
 "sourcify":"UNVERIFIED (404)",
 "bscscanVerified":False,
 "deployer":"0xa7E7d090E32b46933ad11DDa68085625Dfb36c8B",
 "deployerInDiscards":False,
 "registryBytesHit":True,
 "registryBytesSource":"eth_getCode mengandung 0x60b9262456de011f7d15a54cdd8c48baaa8b022f (triage run 1601)",
 "freeMinted":18,"totalMinted":18,"publicMinted":0,"FREE_SUPPLY":1000,"MAX_SUPPLY":3333,
 "freePctVerified":1.8,
 "mintStart":1794177963,"mintStartWib":"2026-11-09 05:46:03 WIB",
 "ageHoursAtTriage":11.1,
 "ageVerified":True,
 "ageNote":"mintStart on-chain 05:46:03 WIB 2026-11-09 + agent.json 'contracts deployed 9 Nov 2026' + first mints observed on-chain (freeMinted 18 blok 132562000); blok first-mint persis UNVERIFIED (getLogs gagal semua endpoint: dataseed limit-exceeded, publicnode rate-limited, Ankr 401)",
 "freeSlotUserOpen":True,
 "hasFreeMinted_user":0,"balanceOf_user":0,
 "freeMechanics":"mintFree(expiry, signature) — signature backend (keccak256(nftAddress, minter, phase=0, expiry)); request signed pass from backend, no captcha; free phase grades Common (780) + Uncommon (220) only; public mint 0.0008 BNB opens when freeMinted=1000",
 "marketplace":"own market 0x0910182F40D3B60f2577De79aBdecf7915178cEF (minPrice 0.0001 BNB, listingFee 0.000107 BNB, royalty 5%, trading opens at 1500 minted, listings open from launch)",
 "totalSupply":None,"supplyView":"totalMinted (totalSupply() reverts)",
 "lastReadBlock":132562466,"lastReadWib":"2026-11-09 16:5x WIB",
 "velocityLegPasses":False,
 "reportedOnceWib":"2026-11-09 ~17:0x WIB (EARLY LEAD, run 1601)",
 "note":"EARLY LEAD run 1601. Agent-shaped: bytecode registry bytes + FREE_SUPPLY/freeMinted views + agent.json Agent ID gate. First mints verified on-chain (18 free, blok 132562000). Free 1.8% (<25% -> bukan strong lead). TIDAK pernah preview/mint. Deployer bukan discards; owner() tidak ada di kontrak (revert)."}
# ---- 2. Motor Agent (early lead) ----
contracts["Motor Agent"]={
 "address":"0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5",
 "market":"0x1C2743449C177D608d3B19C88160fc1B402f7BAC",
 "status":"early-lead-reported-2026-11-09",
 "name":"Motor Agent","symbol":"MOTOR","kind":"ERC721",
 "source":"Sourcify recently-verified feed (verifiedAt 2026-11-09T09:09:07Z), run 1601 discovery",
 "website":"https://motor-agent.xyz",
 "websiteEvidence":"contractURI https://motor-agent.xyz/meta/collection.json external_link -> motor-agent.xyz; site served HTML/JS config prints exact contract 0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5 + market 0x1C2743449C177D608d3B19C88160fc1B402f7BAC + 'deployed 2026-11-09 16:08 +07'; visible page text does NOT show the address (SPA) — evidence via site-published config",
 "xHandle":None,"xVerified":False,
 "sourcify":"verified exact_match (ABI 131 entries; REGISTRY, AgentFreeMint, freeMintX, freeLeft, AGENT_FREE_CAP, X_FREE_CAP)",
 "bscscanVerified":True,
 "deployer":"0xb4DaE00dD17BE9C881F40a9b6A30236c41eecB6B",
 "deployerInDiscards":False,
 "registryBytesHit":True,
 "REGISTRY":"0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
 "AGENT_FREE_CAP":2000,"X_FREE_CAP":200,
 "freeLeft":[1680,200],
 "freeAgentClaimed":320,"freeAgentPct":16.0,"freeXClaimed":0,
 "totalSupply":317,"MAX_SUPPLY":5555,"paidMinted":0,"PRICE":1500000000000000,
 "mintStart":1794215298,"mintStartWib":"2026-11-09 16:08:18 WIB",
 "mintEnd":1794820098,
 "mintOpen":1,
 "ageHoursAtTriage":0.8,
 "ageVerified":True,
 "ageNote":"mintStart on-chain 16:08:18 WIB 2026-11-09 (= site 'deployed 2026-11-09 16:08 +07' = Sourcify verifiedAt 16:09 WIB); first mints verified on-chain (totalSupply 317 blok 132562000)",
 "freeSlotUserOpen":True,
 "freeUsedByWallet_user":0,"balanceOf_user":0,"claimable_user":0,
 "TOKEN":"0xFDd44C29Af794249318930CeBBf9CC3DfFF9E4b1",
 "contractURI":"https://motor-agent.xyz/meta/collection.json",
 "freeMechanics":"freeMintX(signature, xUserIdHash, deadline) X-gated (backend signature); fungsi lane AGENT-free belum dipetakan (tidak ada mintFree polos di ABI; AGENT_FREE_CAP 2000, 320 terpakai) — klarifikasi sebelum promosi",
 "ownerNote":"owner()/admin() revert — kontrak tanpa owner; deployer via BscScan creator",
 "lastReadBlock":132562000,"lastReadWib":"2026-11-09 16:5x WIB",
 "velocityLegPasses":False,
 "reportedOnceWib":"2026-11-09 ~17:0x WIB (EARLY LEAD, run 1601)",
 "note":"EARLY LEAD run 1601. Agent-shaped VERIFIED (Sourcify exact_match + REGISTRY exact + free views + mintOpen). First mints verified on-chain (317 total, 320 agent-free claimed). Free agent 16% (<25% -> bukan strong lead). TIDAK pernah preview/mint. Deployer bukan discards."}
# ---- 3. 0x3314 checked-not-lead ----
contracts["0x331426d06CA0F9616D121888e3Fe60E2C3E42354"]={
 "address":"0x331426d06CA0F9616D121888e3Fe60E2C3E42354",
 "status":"checked-not-lead-2026-11-09",
 "source":"Sourcify feed run 1601 discovery",
 "sourcify":"verified exact_match (71 fns)",
 "note":"Token mint pool (mint + getMarketPrice + mintPoolRemaining + totalMintedUSDT + TOKENS_PER_USDT + officialWebsite); TIDAK ada free-share view, TIDAK ada registry/AgentGate -> BUKAN track C, BUKAN track A. Tidak masuk watchlist aktif.",
 "lastReadWib":"2026-11-09 16:5x WIB"}
# ---- 4. velocity rulings ----
report["velocity_rulings"]={
 "0xbd4B4e7189ae9356514664146b0eD683601200A9":"velocity LOLOS (+31, 25.14x) TAPI TIDAK promosi: slot user SUDAH terpakai (freeClaimed(user)=1, balanceOf(user)=1, sudah dimiliki); freeMinted 2320/2777 = 83.5% (koreksi dari freeClaimed lama 993); umur first-mint 2026-11-07 17:13 WIB (~47.6 jam, nyaris 48 jam); website None, x unverified. Tetap early-lead-reported-2026-11-07, tanpa laporan baru.",
 "Lucky Agents":"velocity LOLOS (+76, 30.87x) TAPI TIDAK promosi: umur UNVERIFIED (watchlist-only-age-unverified-2026-11-08), free% unverified. Tetap watchlist-only.",
 "Hackagent":"velocity LOLOS (+34, 9.2x) TAPI same-owner-discarded — TIDAK promosi/eksekusi/laporan.",
 "Weldagent":"velocity LOLOS (+63, 51.1x) TAPI same-owner-discarded — TIDAK promosi/eksekusi/laporan.",
 "Pandadroid":"velocity LOLOS (+41, 16.65x) TAPI same-owner-discarded — TIDAK promosi/eksekusi/laporan.",
 "Rookling":"velocity LOLOS (+89, 18.08x) TAPI status age-excluded-2026-11-06 — TIDAK promosi (catatan 'PROMOTION CHECK NEEDED' dari merge stage 1 DIBATALKAN oleh status age-excluded; free% 69.23 tidak relevan setelah exclusion)."}
# ---- 5. track_c notes ----
if "NIBULL" in tc and isinstance(tc["NIBULL"],dict):
    tc["NIBULL"]["note1601_1109"]="Run 1601 (blok 132560865): opened=0, openedAt=0 — sale MASIH BELUM BUKA menurut flag kontrak, TAPI soldShares 1018->1257 (+239 sejak run 1531); freeSharesRemaining() view TIDAK ADA (None) -> free pool tidak bisa diverifikasi. Tetap watchlist-only-upcoming; BUKAN lead. Klarifikasi soldShares vs opened masih terbuka."
    report["track_c_notes"]["NIBULL"]="opened=0, soldShares 1018->1257, free view None — tetap upcoming, bukan lead."
if "NUSA" in tc and isinstance(tc["NUSA"],dict):
    tc["NUSA"]["note1601_1109"]="Run 1601: freeMinted 347->348 (+1 biasa). Tetap track-c-lead-reported; tanpa perubahan."
    report["track_c_notes"]["NUSA"]="freeMinted 347->348, tanpa perubahan."
if "ORDIagent" in tc and isinstance(tc["ORDIagent"],dict):
    tc["ORDIagent"]["note1601_1109"]="Run 1601: semua view None (baca gagal/transport); sale buka 17:00 WIB hari ini (belum tiba saat run). Pantau run berikut."
    report["track_c_notes"]["ORDIagent"]="buka 17:00 WIB; belum ada data run ini."
# ---- 6. final run notes (overwrite stale stage-1 discovery sentence) ----
snap["runNote1601_1109"]=(
 f"Run 1601 STAGE 2: re-read {len(r1601.get('reread', {}))} kontrak + {len(r1601.get('track_c', {}))} track_c "
 f"(blok {BLOCK}, interval {m1.get('interval_minutes')} mnt vs run 1531); "
 f"velocity LOLOS {len(m1.get('velocity_pass', []))}: {', '.join(v['name'] for v in m1.get('velocity_pass', []))} — promosi 0 (Ink Koi slot user terpakai; Lucky Agents umur unverified; Hackagent/Weldagent/Pandadroid same-owner-discarded; Rookling age-excluded). "
 f"Age-exclusions baru: 0. "
 f"Scan GAGAL CEPAT: Ankr pre-flight 401 x2 (7,9 dtk + 8,0 dtk) — watermark TIDAK dimajukan (tetap 132512564, gap ~{BLOCK - 132512564:,} blok ke head {BLOCK}). "
 f"Binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1, blok 132560689). Grove freeOpen=0 (blok 132560807), belum buka. Bridge tidak berubah (mtime 2026-11-08 18:21 UTC; 116 kontrak; 8 tidak ada di snapshot — semuanya temuan ERC-20 yang sudah ditriase bukan lead). "
 f"Discovery: 2 EARLY LEAD BARU — Agentite (free 18/1000, umur ~11 jam, website terverifikasi via agent.json) + Motor Agent (free agent 320/2000, umur ~0,8 jam, Sourcify exact_match); 1 checked-not-lead (0x3314 token mint pool). "
 f"Backdoor Pass TIDAK diangkat (sudah ditriase run lalu: bukan agent-shaped + rug warning, exclude). "
 f"NIBULL tetap upcoming (opened=0, soldShares 1257). ORDIagent buka 17:00 WIB. Eksekusi 0.")
snap["runNote1601_1109_scan"]=(
 f"Run 1601 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (blok 132560580-132560629): "
 f"ATTEMPT 1 FAIL 7,9 dtk HTTP 401, ATTEMPT 2 FAIL 8,0 dtk HTTP 401 (credential custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB). "
 f"Scan leg TIDAK dijalankan (amendment 2026-11-06: pre-flight gagal = fast-fail, lanjut route lain). Watermark tetap 132512564; "
 f"gap ke head {BLOCK} ~{BLOCK - 132512564:,} blok dan tumbuh (milik backfill, ikut gagal 401). Tidak ada first-seen baru dari scan; triage tidak dijalankan; route 5c tanpa output scan baru (0 sale-shape). "
 f"Konteks dari job lain: flash BlockBeats 16:19 WIB mengutip SlowMist — Ankr diduga diserang, kerugian ~$1 juta (belum diverifikasi run ini; dicatat sebagai kemungkinan penyebab outage).")
snap["runNote1601_1109_binanceai"]=(
 "Run 1601 (blok 132560689): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
 "totalShares=3110, tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote1601_1109_early_leads"]=(
 "Run 1601 EARLY LEADS (dilaporkan sekali ke main chat): (1) Agentite 0xA587F3Ef2BEc919255fCfFF36A6BdD82cf4D87e2 — free 18/1000 (1,8%), mintStart 05:46:03 WIB 2026-11-09 (umur ~11 jam), slot user TERBUKA (hasFreeMinted=0), website agentite.pages.dev terverifikasi (agent.json mencetak kontrak persis), X @agentite_gems (per Boltbook), deployer 0xa7E7d090E32b46933ad11DDa68085625Dfb36c8B bukan discards, Sourcify/BscScan UNVERIFIED, mintFree butuh signature backend. "
 "(2) Motor Agent 0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5 — totalSupply 317, free agent 320/2000 (16%), mintStart 16:08:18 WIB 2026-11-09 (umur ~0,8 jam), slot user TERBUKA (freeUsedByWallet=0), Sourcify exact_match + REGISTRY persis, website motor-agent.xyz (kontrak tercetak di config situs), deployer 0xb4DaE00dD17BE9C881F40a9b6A30236c41eecB6B bukan discards, freeMintX butuh signature X. "
 "Keduanya BUKAN strong lead (free% <25%), TIDAK pernah preview/mint.")
snap["last_run"]="1601"
snap["last_run_wib"]="2026-11-09 ~16:5x WIB"
snap["last_run_note"]=("Run 1601: 2 early lead baru (Agentite + Motor Agent) — dilaporkan sekali; velocity lolos 6 tapi promosi 0; "
                       "scan fast-fail Ankr 401 (watermark tetap 132512564); binanceai tetap refund; NIBULL tetap upcoming.")
snap["timestamp_wib"]="2026-11-09 16:5x WIB"
def save_atomic(path,obj):
    tmp=path+".tmp"
    with open(tmp,"w") as f: json.dump(obj,f,indent=1)
    import os; os.replace(tmp,path)
save_atomic(f"{HF}/onchain-snapshot.json",snap)
json.dump(report,open(f"{HF}/run-2026-11-09-1601-merge-stage2.json","w"),indent=1)
print("MERGE STAGE 2 DONE. contracts now:",len(snap["contracts"]))
print("early leads:",report["early_leads_new"])
print("velocity rulings:",json.dumps(report["velocity_rulings"],indent=1)[:800])
