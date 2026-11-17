#!/usr/bin/env python3
"""Merge run 1801 PART 2 (scan legs: watermark/seen/5c-checked + MONOLITH + run note).
Parent merge only. Reads triage + enriched first-seen + scan output."""
import json, os

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
S = HF + "onchain-snapshot.json"

# --- 1. seen: add 60 first-seen (lowercase -> first_block) ---
enriched = json.load(open("/tmp/first_seen_1801_enriched.json"))
seen = json.load(open(HF + "onchain-scan-seen.json"))
before = len(seen.get("contracts", {}))
added = 0
for row in enriched:
    k = row["address"].lower()
    if k not in seen.setdefault("contracts", {}):
        seen["contracts"][k] = row["first_block"]
        added += 1
with open(HF + "onchain-scan-seen.json.tmp1801", "w") as f:
    json.dump(seen, f, indent=1)
os.replace(HF + "onchain-scan-seen.json.tmp1801", HF + "onchain-scan-seen.json")
print("seen contracts:", before, "->", len(seen["contracts"]), "(added", added, ")")

# --- 2. scan state: advance watermark ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["last_scanned_block"] = 132381478
st["last_scan_window_from"] = 132380479
st["last_scan_window_to"] = 132381478
st["last_scan_wib"] = "2026-11-08 17:57-18:05 WIB"
st["last_scan_gap_skipped"] = "132377462-132380478 (3017 blocks; window from watermark to head 4017 blocks > cap 1000; scan covered most recent 1000 only; backfill OFF)"
st["last_scan_ankr_calls"] = 40
st["last_scan_errors"] = 0
st["nft_contracts_last_scan"] = 134
st["erc20_mint_contracts_last_scan"] = 285
st["head_at_scan_start"] = 132381433
st["last_scan_gap_skipped_1801"] = "132377462-132380478 (3017 blocks)"
st["runNote1801_scan"] = (
    "Scan run 1801: pre-flight LULUS 8.2 dtk (50 blok, 248 log, head 132381433); window 132380479-132381478 "
    "(1000 blok, 17:57:22-18:04:51 WIB), 20/20 chunk, 0 error, 40 Ankr calls, partial=false; 134 NFT "
    "(131 ERC721 + 3 ERC1155) / 954 mint / 285 ERC20-mint; HIVE tidak di window; watermark 132377461 -> "
    "132381478; skipped gap 132377462-132380478 (3.017 blok, backfill OFF; gap lama 132373210-132376461 juga "
    "belum ter-cover). First-seen 60: SEMUA HISTORIC (supply >> window mints), 0 fresh, 0 kandidat early lead; "
    "49/60 registry-bytes agent-shaped; 22/60 same-owner-discarded (owner 0x11038f4a x5 wave OBSIDIAN/THE KEY/ALL "
    "ACCESS/GOLDEN TICKET/ORBIT PASS, 0x53043412 x5, 0xd76d5918 x4, 0x190f1f0c x4, 0x75d251ba x3, 0xa0542755, "
    "0x1e1e3f44 x2, 0x310cea29 x2, 0xb35349ee, 0x293fc9e1 x2). MONOLITH re-find (bukan lead baru; launch unverified). "
    "5a Sourcify 20 item: MONOLITH/ORBIT PASS/THE KEY sudah di scan (dedup); SaleV12 0x7047aED5 BUKAN lead track-C "
    "(tanpa registry, saleStart=0). 5c: 47 ERC20 mint_count>=10, 45 sudah dicek, 2 baru dicek, 0 hit S1/S2."
)
with open(HF + "onchain-scan-state.json.tmp1801", "w") as f:
    json.dump(st, f, indent=1)
os.replace(HF + "onchain-scan-state.json.tmp1801", HF + "onchain-scan-state.json")
print("scan-state watermark -> 132381478")

# --- 3. track-c-scan-checked: append 2 newly checked ---
chk = json.load(open(HF + "track-c-scan-checked.json"))
new_addrs = ["0xb50dC583cC6F83750c36789F52d51E12dA664444", "0xEBbA172c2Dfdd677873102390bfd54aFe0B40D5f"]
added_c = 0
if isinstance(chk, dict) and "checked" in chk and isinstance(chk["checked"], list):
    low = [str(x).lower() for x in chk["checked"]]
    for a in new_addrs:
        if a.lower() not in low:
            chk["checked"].append(a)
            added_c += 1
elif isinstance(chk, dict):
    for a in new_addrs:
        if a not in chk and a.lower() not in [str(x).lower() for x in chk.keys()]:
            chk[a] = {"checked_wib": "2026-11-08 18:01 WIB", "run": "1801", "shape": "no-shape"}
            added_c += 1
elif isinstance(chk, list):
    for a in new_addrs:
        if a not in chk:
            chk.append(a)
            added_c += 1
with open(HF + "track-c-scan-checked.json.tmp1801", "w") as f:
    json.dump(chk, f, indent=1)
os.replace(HF + "track-c-scan-checked.json.tmp1801", HF + "track-c-scan-checked.json")
print("track-c-scan-checked added:", added_c)

# --- 4. snapshot: MONOLITH fresh supply + run note ---
snap = json.load(open(S))
mono = snap["contracts"].get("MONOLITH")
if mono is not None:
    mono["totalSupply"] = 42
    mono["totalMinted"] = 42
    mono["lastReadBlock"] = 132381478
    mono["lastReadWib"] = "2026-11-08 18:01 WIB"
    mono["runNote1801_1108"] = ("Run 1801: re-find scan (4 mint window 132380479-132381478) + fresh read totalSupply 42 / "
        "totalMinted 42 (naik dari 15 saat re-read blok 132381403; mint cepat). Launch TETAP UNVERIFIED "
        "(walk-back: 11 mint >= blok 132370000, earliest 132377160 17:32:27 WIB; 24 dari 39 totalMinted tak "
        "terlacak >= blok 132340000 - sebelum ~08:00 WIB atau dev/reserve mint non-Transfer). free% UNVERIFIED, "
        "slot UNVERIFIED. BUKAN early/strong lead baru (sudah dilaporkan sebagai early lead run 1731). "
        "Owner 0xcbcad... BUKAN same-owner-discarded (EXCEPTION BNB Faucet di discards). Tidak di-preview/di-mint.")
    print("MONOLITH updated to 42/42")

snap["runNote1801_1108"] = (
    "Run 1801 (18:01 WIB, selesai ~18:25 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 pending claim baru, 0 lead track-C baru - DIAM per aturan (tidak ada laporan chat baru kecuali perubahan "
    "sellout Oddlode di bawah). "
    "ROUTE 1 re-read blok 132381403: 507/512 kontrak + 71 track_c; velocity pass 2 (Zhenzhu ARTEFAK ERC-20; "
    "Ink Koi 0xbd4B +27, 3.04x, free% 70.4% TAPI slot user terpakai) - tanpa promosi; sellout genuinely baru 1: "
    "Oddlode Drills 0xce18... freeMinted 1000/1000 (totalSupply 1001->1002) - user sudah mint, status -> sold-out; "
    "slot user berubah 0; age-exclusion baru 0; degraded 24 (None = artefak baca, bukan nol); 5 kontrak tidak "
    "masuk re-read (Mummyhive, LuckyBox-d08e, SnailMail, Jolly, AgentGlyph - tanpa alamat di snapshot). "
    "Gelombang 8 kontrak 14:56 WIB (Cassetto dkk.): slot TERBUKA (quote(user,1)=0) + free 37-42% + umur <=48h "
    "terverifikasi, TAPI promosi ke strong lead TETAP DIBATALKAN same-owner (owner 0x5304..., discards sejak run "
    "1431, preseden Gourdwick); contractURI base64 JSON tanpa external_link/URL. "
    "Bridge: 32 kontrak dibaca ulang; 26 bentuk NFT ditambahkan ke snapshot sebagai watchlist-only-pelengkap-scan "
    "(umur unverified; 23 di antaranya first-observed mint 2026-11-03 s.d. 2026-11-04 - dicatat, BUKAN walk-back-verified "
    "launch time, jadi tidak di-age-exclude run ini); 6 ERC20 dilewati (ORE, Ikigai, AGC user, ETHBack, PANBA, "
    "unnamed ERC20). Glitchpilotfox 0xda55... terkoroborasi Boltbook (1.445/4.003 = 36,1%, pace +4/136 mnt sangat "
    "lambat) - tetap watchlist-only-pelengkap-scan, bukan lead (umur unverified, velocity gagal, tanpa website/X). "
    "Track C: NUSA freeMinted 14->40, gate website GAGAL (hot-leg 17:04) - tidak di-mint; AGENT MALTA totalSupply naik, "
    "gate GAGAL - tidak di-mint; Crack totalSupply 3797->3811 (minted-by-user). Track B: binanceai tetap refund/failed "
    "(launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed 0, balance 0). Paw Gang totalMinted "
    "3110->3197, tetap PoW-blocked. "
    "ROUTE 2 Boltbook EN+ZH (25 post) + author pages tak terjangkau (tanpa link di fetch); ROUTE 3 sweep EN+ZH; "
    "ROUTE 6 Square/Odaily/PANews/DappBay - tanpa proyek baru selain Glitchpilotfox; CHIPS kontrak terpotong di post. "
    "ROUTE 4 scan PENUH (window 132380479-132381478, 134 NFT/954 mint/285 ERC20, 40 Ankr calls, 0 error, "
    "pre-flight 8,2 dtk); first-seen 60 SEMUA HISTORIC, 0 fresh, 0 early lead; 22 same-owner-discarded; watermark "
    "132377461 -> 132381478; skipped gap 132377462-132380478 (3.017 blok, backfill OFF). 5a Sourcify: SaleV12 bukan "
    "lead track-C (tanpa registry, saleStart=0); 5c: 2 baru dicek, 0 hit. Ankr total run ~40 (scan) + re-read."
)
snap["runNote1801_1108_scan"] = st["runNote1801_scan"]
snap["last_run"] = "free-mint-search 2026-11-08 1801 WIB"
snap["last_run_wib"] = "2026-11-08 18:25 WIB"
with open(S + ".tmp1801", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(S + ".tmp1801", S)
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]), "excluded now:", len(snap.get("excluded", {})))
print("DONE PART 2")
