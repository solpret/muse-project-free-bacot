#!/usr/bin/env python3
"""Parent merge run 2026-11-08 0801. Backs up snapshot/seen/state/checked before writing."""
import json, shutil, time, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "20261108-0801"
def load(p): return json.load(open(p))
def save(p, d):
    tmp = p + ".tmp"
    json.dump(d, open(tmp, "w"), indent=1)
    os.replace(tmp, p)
for f in ["onchain-snapshot.json", "onchain-scan-seen.json", "onchain-scan-state.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-{TS}")
snap = load(f"{BASE}/onchain-snapshot.json")
reread = load(f"{BASE}/run-2026-11-08-0801-reread.json")
vel = load(f"{BASE}/run-2026-11-08-0801-velocity.json")
seen = load(f"{BASE}/onchain-scan-seen.json")
state = load(f"{BASE}/onchain-scan-state.json")
checked = load(f"{BASE}/track-c-scan-checked.json")
scan = load(f"{BASE}/onchain-scan-2026-11-08-0801.json")
five_c = load(f"{BASE}/run-2026-11-08-0801-5c.json")
BLOCK = reread["block"]  # 132302277
updated, skipped_none = 0, 0
for name, rd in reread.get("reread", {}).items():
    c = snap["contracts"].get(name)
    if c is None: continue
    prev_ts = c.get("totalSupply")
    ts = rd.get("totalSupply")
    tm = rd.get("totalMinted")
    new_ts = ts if ts is not None else (tm if tm is not None and c.get("totalSupply") is None else prev_ts)
    if ts is None and tm is None:
        skipped_none += 1
    else:
        c["previousTotalSupply"] = prev_ts
        c["totalSupply"] = new_ts
        updated += 1
    for k, sk in [("freeClaimed","freeClaimed"),("freeMinted","freeMinted"),("FREE_SUPPLY","FREE_SUPPLY"),("MAX_SUPPLY","MAX_SUPPLY"),("mintOpen","mintOpen")]:
        if rd.get(k) is not None: c[sk] = rd[k]
    if rd.get("balanceOf_user") is not None: c["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None: c["freeClaimed_user"] = rd["freeClaimed_user"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-08 run 0801"
    c["runNote0801"] = f"Run 0801 (blok {BLOCK}): totalSupply {new_ts} (prev {prev_ts}), minted interval vs 0731 tercatat di velocity; balanceOf(user)={c.get('balanceOf_user')}."
# velocity: Lambdwyn pass
lw = snap["contracts"].get("Lambdwyn")
if lw is not None:
    lw["previousTotalSupply"] = 494; lw["totalSupply"] = 519
    lw["mintedInInterval"] = 25; lw["intervalMinutes"] = 29.84
    lw["currentRatePerMin"] = 0.8377; lw["previousRatePerMin"] = 0.5333
    lw["velocityRatio"] = 1.57; lw["velocityLegPasses"] = True
    lw["velocityNote"] = "run 0801: +25 token, 0.8377/mnt, rasio 1.57x vs run 0731 - VELOCITY LOLOS tapi BUKAN promosi (free% UNVERIFIED, umur launch UNVERIFIED)."
# Dafeiyu: first velocity baseline + final read
df = snap["contracts"].get("Dafeiyu")
if df is not None:
    df["totalSupply"] = 388
    df["previousTotalSupply"] = 178
    df["velocityNote"] = "run 0801: baseline PERTAMA tercatat (178 -> 388, +210); belum ada rate/rasio (tanpa baseline run 0731) -> velocity TIDAK lulus run ini. Bacaan akhir parent blok 132305490: totalSupply 448."
    df["runNote0801"] = "Run 0801 (blok 132302277): totalSupply 388 (was 178); free% tetap UNVERIFIED (freeClaimed() revert); slot open by read (balanceOf(user)=0). Bacaan akhir parent blok 132305490: totalSupply 448."
    df["lastReadBlock"] = BLOCK; df["lastReadWib"] = "2026-11-08 run 0801"
# HokiKoi: promoted + MINTED #64 by parallel process after baw re-login (not by this run)
hk = snap["contracts"].get("HokiKoi")
if hk is not None:
    hk["totalMinted"] = 67; hk["freeMinted"] = 67; hk["FREE_CAP"] = 111
    hk["freePctVerified"] = 60.36
    hk["freePctNote"] = "VERIFIED: freeMinted 67 / FREE_CAP 111 = 60,36% (blok 132305490). Sempat 49/111 = 44,14% saat verifikasi parent blok 132305032 -> promosi early->strong lead (hot-leg 0814 sudah melaporkan promosi + gate PASSED + mint BLOCKED baw logout)."
    hk["mintOpen"] = True
    hk["status"] = "minted-by-user-2026-11-08"
    hk["userSlotNote"] = "Slot TERPAKAI: freeCount(user)=1, balanceOf(user)=1 (blok 132305490). Mint #64 dieksekusi proses paralel sesudah baw login ulang (bukan run ini): tx 0x862279c5368209e4f369ae37bb722aae3ed6378ab890021b6fa67fae2b0611a2, blok 132305321, 2026-11-08 08:33:26 WIB, receipt status 1, gas 113.390."
    hk["mintTx"] = "0x862279c5368209e4f369ae37bb722aae3ed6378ab890021b6fa67fae2b0611a2"
    hk["mintBlock"] = 132305321; hk["mintGas"] = 113390; hk["mintTokenId"] = 64
    hk["balanceOf_user"] = 1
    hk["runNote0801"] = "Run 0801: promosi ke strong lead terverifikasi parent (free 49/111=44,14% blok 132305032; gate website PASSED via tokenURI->hokikoi-mint.netlify.app; audit Binance hasResult=false). Mint #64 sudah dieksekusi proses paralel sesudah baw login ulang (bukan run ini) - TIDAK dilaporkan ulang sebagai promosi."
    hk["lastReadBlock"] = 132305490; hk["lastReadWib"] = "2026-11-08 run 0801"
    hk["velocityNote"] = "run 0801: baseline velocity tercatat (totalMinted 21 -> 67); promosi strong lead sudah dilaporkan hot-leg 0814."
# HokiPanda: NEW strong lead, gate PASSED, audit no-result, FREE POOL SOLD OUT before execution
snap["contracts"]["HokiPanda"] = {
    "address": "0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517",
    "status": "strong-lead-reported-2026-11-08-0801-sold-out",
    "name": "HokiPanda", "symbol": "HPANDA", "kind": "ERC721",
    "totalMinted": 111, "freeMinted": 111, "FREE_CAP": 111, "FREE_PER_WALLET": 1,
    "MAX_SUPPLY": 3333, "PAID_CAP": 3222, "PRICE": 0.00005,
    "paidMintedCount": 0, "mintOpen": True,
    "freePctVerified": 100.0,
    "freePctNote": "VERIFIED: freeMinted 111 / FREE_CAP 111 = 100% (blok 132305490) - free pool HABIS. Progres: 83/111=74,77% saat triase scan (~08:25) -> 106/111=95,5% verifikasi parent blok 132305032 -> 111/111 sold out blok 132305490.",
    "userSlotNote": "Slot TIDAK PERNAH terpakai: freeCount(user)=0, balanceOf(user)=0 (blok 132305490). Slot terbuka saat deteksi, tapi free pool habis sebelum eksekusi sempat jalan (baw logout ~08:15-08:19, login ulang sesudahnya; pool habis ~08:33-08:35). TIDAK di-preview/di-mint run ini.",
    "firstSeenBlock": 132301321,
    "firstMintWib": "2026-11-08 08:03:25 WIB",
    "firstMintNote": "First mint TERVERIFIKASI parent run 0801 (triage scan): blok 132301321 = 2026-11-08 08:03:25 WIB (timestamp via dataseed eth_getBlockByNumber, bukan Ankr), tokenId 1, tx 0x1dd860c7dc38810b50fcd41b7ea29a056447158010e6b5ed26864b8f99a552b1; 43 mints / 43 minters dalam window scan.",
    "agentShapedNote": "agentIdRegistry()=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (registry persis); Sourcify exact_match (60 fns) dengan free views FREE_CAP/FREE_PER_WALLET/freeMinted/freeCount/freeMint + mintOpen. Ditemukan scan route 4 + feed Sourcify (cross-check) - dilaporkan SEKALI run ini.",
    "owner": "0x13333df46ab3e95f4166370d571e7b73aad06370",
    "ownerNote": "Owner SAMA dengan HokiKoi (0x13333df46ab3e95f4166370d571e7b73aad06370) - bukan di bridge same_owner_discarded, bukan grup factory 0xa05427...; dicatat, bukan discard.",
    "gateNote": "Website gate PASSED run ini (metode I): tokenURI(1)=https://hokipanda-mint.netlify.app/metadata/metadata.json, external_url https://hokipanda-mint.netlify.app - situs mencetak kontrak persis 0x4b61A776... dalam CFG mint (NFT + REGISTRY persis + MAX 3333 / FREE_CAP 111 / PRICE 0,00005 cocok on-chain). Metode A (raw address search) tanpa hit proyek - tidak dibutuhkan karena (I) lolos.",
    "auditNote": "Binance audit run ini: code 000000, hasResult=false, isSupported=true, riskLevel -1, riskItems [], riskAlert null - TIDAK ADA HASIL (disclosed, bukan pass).",
    "lastReadBlock": 132305490, "lastReadWib": "2026-11-08 run 0801",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint terverifikasi 2026-11-08 08:03:25 WIB (umur ~22 mnt saat triase, <=48 jam).",
    "baselineNote": "STRONG LEAD dilaporkan sekali run 0801: umur terverifikasi ~0,4 jam + free 74,77% (>=25%) + slot user terbuka. TIDAK sempat di-mint: free pool habis (111/111) sebelum eksekusi; baw logout saat deteksi, login ulang sesudah pool menipis. Dilaporkan sekali sebagai strong lead + sold out.",
    "runNote0801": "Run 0801: strong lead baru (scan+feed). Gate PASSED, audit no-result, free 106/111 saat verifikasi parent - SOLD OUT 111/111 sebelum eksekusi (blok 132305490). TIDAK di-mint."
}
# seen: HokiPanda + ERC20s from scan output
contracts_seen = seen.get("contracts", {})
added_nft = 0
hp_key = "0x4b61a7767da68f18266907b2eb7c9a1ee3d24517"
if hp_key not in contracts_seen:
    contracts_seen[hp_key] = {"first_seen_block": 132301321, "first_seen_run": "2026-11-08-0801", "source": "onchain-scan-2026-11-08-0801"}
    added_nft = 1
added_erc20 = 0
for e in scan.get("erc20_mint_contracts_list", []):
    k = e["address"].lower()
    if k not in contracts_seen:
        contracts_seen[k] = {"first_seen_block": e.get("first_block"), "first_seen_run": "2026-11-08-0801", "source": "onchain-scan-2026-11-08-0801", "mint_count_window": e.get("mint_count")}
        added_erc20 += 1
seen["contracts"] = contracts_seen
# track-c-scan-checked: 6 newly checked (top-level keys, mirror existing pattern)
existing_top = [k for k in checked.keys() if k != "checked"]
sample_val = checked.get(existing_top[0]) if existing_top else None
added_5c = 0
for c in five_c.get("checked", []):
    a = c.get("address")
    if not a: continue
    if a in checked or a.lower() in [k.lower() for k in checked.keys()]:
        continue
    checked[a] = {"run": "2026-11-08-0801", "shape": "no-shape", "source": "scan-2026-11-08-0801", "sourcify": "not_verified"}
    added_5c += 1
# snapshot meta notes
snap["runNote0801"] = ("Run 0801 (2026-11-08 ~08:01-08:40 WIB): 1 STRONG LEAD BARU HokiPanda (dilaporkan sekali; gate PASSED, audit no-result, free pool SOLD OUT 111/111 sebelum eksekusi - tidak di-mint). "
    "HokiKoi promosi early->strong lead (free 44,14% parent) SUDAH dilaporkan hot-leg 0814 (gate PASSED, mint BLOCKED baw logout); #64 DI-MINT proses paralel sesudah baw login ulang (tx 0x862279c5..., blok 132305321, 08:33:26 WIB, gas 113.390) - bukan run ini, tidak dilaporkan ulang. "
    "Velocity pass 1: Lambdwyn (+25, 1,57x) bukan promosi (free%+umur UNVERIFIED). Dafeiyu baseline pertama (178->388->448), free% tetap UNVERIFIED. Sellout baru 0 (total 35). Slot berubah 0 (kecuali HokiKoi terpakai). Age REMOVE 0. "
    "Scan PARSIAL (enrichment stall 70/124, SCAN_EXIT=124; window 132301401-132302400; gap 132293853-132301400 belum ter-cover; watermark TIDAK maju). "
    "Sourcify 0 sale-shape; sweep 0 proyek baru; komplemen 0; binanceai tetap refund phase; bridge tidak berubah. baw LOGOUT ~08:15-08:19 lalu LOGIN ULANG (status CONNECTED saat cek parent ~08:36 WIB). PER ATURAN DIAM + dedupe: laporan chat hanya HokiPanda (strong lead + sold out).")
snap["runNote0801_scan"] = ("Run 0801 scan: pre-flight PASS 7,6 dtk (head 132302330, 248 log/50 blok). Window 132301401-132302400 (1000 blok, cap); skipped gap 132293853-132301400 (7.548 blok; backfill nonaktif). "
    "Chunk 20/20 OK; enrichment stall 70/124 -> watchdog kill 780 dtk, SCAN_EXIT=124, partial=true (122 ERC721 + 2 ERC1155 + 269 ERC20-mint, 40 Ankr calls, 0 error). 54 kontrak tidak ter-enrich (alamat hilang run ini). "
    "Triage: 1 true first-seen = HokiPanda (STRONG LEAD, lalu sold out). Watermark TIDAK dimajukan (tetap 132293852). 5c: 54 ERC20 >=10, 48 sudah dicek, 6 baru dicek, 0 hit S1/S2.")
snap["last_run"] = "free-mint-search 2026-11-08 0801 WIB"
snap["last_run_wib"] = "2026-11-08 0801 WIB"
snap["last_run_note"] = snap["runNote0801"]
# scan state note
state["note_0801_scan"] = snap["runNote0801_scan"]
save(f"{BASE}/onchain-snapshot.json", snap)
save(f"{BASE}/onchain-scan-seen.json", seen)
save(f"{BASE}/onchain-scan-state.json", state)
save(f"{BASE}/track-c-scan-checked.json", checked)
print(json.dumps({"reread_updated": updated, "reread_none": skipped_none, "seen_added_nft": added_nft, "seen_added_erc20": added_erc20, "checked_added_5c": added_5c, "seen_total": len(contracts_seen)}, indent=1))
