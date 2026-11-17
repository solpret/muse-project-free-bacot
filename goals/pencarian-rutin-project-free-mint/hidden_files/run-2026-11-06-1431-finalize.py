#!/usr/bin/env python3
"""Finalize run 2026-11-06 1431 WIB (parent).
Merges leg-1 re-read, 3 early leads, SYMBOL age-exclusion, BNB Chick gate-fail,
scan-state note, seen-file additions, 5c merge. Does NOT touch the shared
watermark (backfill owns it). Backs up snapshot first.
"""
import json, shutil, copy, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1431"
NOW_WIB = "2026-11-06 run 1431"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-1431")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-1431")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-1431")
shutil.copy(f"{BASE}/track-c-scan-checked.json", f"{BASE}/track-c-scan-checked.json.bak-20261106-1431")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-2026-11-06-1431-reread-lean.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1431.json"))
checked5c = json.load(open(f"{BASE}/run-2026-11-06-1431-5c-checked.json"))
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
tcchecked = json.load(open(f"{BASE}/track-c-scan-checked.json"))

BLOCK = reread["block"]  # 131969896
merged_nft = 0
merged_tc = 0

# --- 1. Leg-1 NFT re-read merge (non-None values only, match by address) ---
addr2name = {}
for name, e in snap.get("contracts", {}).items():
    if not isinstance(e, dict):
        continue
    a = (e.get("address") or "").lower()
    if a:
        addr2name[a] = name
for name, vals in reread.get("reread", {}).items():
    if not isinstance(vals, dict):
        continue
    a = (vals.get("address") or "").lower()
    key = addr2name.get(a) or (name if name in snap.get("contracts", {}) and isinstance(snap["contracts"].get(name), dict) else None)
    if not key:
        continue
    e = snap["contracts"][key]
    for k, v in vals.items():
        if k in ("address",):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1

# --- 2. Leg-1 track_c re-read merge (match by sale address) ---
sale2name = {}
for name, e in snap.get("track_c", {}).items():
    if not isinstance(e, dict):
        continue
    s = (e.get("sale") or "").lower()
    if s:
        sale2name[s] = name
for name, vals in reread.get("track_c", {}).items():
    if not isinstance(vals, dict):
        continue
    s = (vals.get("sale") or vals.get("address") or "").lower()
    key = sale2name.get(s) or (name if name in snap.get("track_c", {}) and isinstance(snap["track_c"].get(name), dict) else None)
    if not key:
        continue
    e = snap["track_c"][key]
    for k, v in vals.items():
        if k in ("sale", "address"):
            continue
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- 3. HIVE run note (all views failed this run -> old values kept) ---
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote1431_1106"] = ("Run 1431 (blok 131969896): SEMUA view gagal baca (None) - degradasi RPC, "
        "BUKAN nol; nilai lama (1253) dipertahankan, velocity TIDAK dihitung; "
        "balanceOf(user) lama 1 dipertahankan; minted-by-user, bukan kandidat.")

# --- 4. Add 3 early leads to contracts ---
snap["contracts"]["WeZards"] = {
    "address": "0xe4d7Ec33Fcf7D93cBE7F4D46d0ef35F437956aab",
    "status": "early-lead-2026-11-06-1431",
    "name": "WeZards",
    "symbol": "WEZARDS",
    "kind": "ERC721",
    "agentShape": "Sourcify verified ABI (46 fns): agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact; mintAgenticFree() nonpayable no-arg",
    "FREE_ALLOCATION": 2500,
    "freeMinted": 27,
    "remainingFreeAllocation": 2473,
    "freePctVerified": 1.08,
    "MINT_PRICE": "0.001 BNB (paid leg only)",
    "mintOpen": True,
    "userSlot": {"hasClaimedFree": 0, "slotOpen": True},
    "firstSeenBlock": 131968955,
    "firstMintWib": "2026-11-06 14:29:47",
    "firstMintTx": "0xf658979ee0d6df8bdfc4b86e31a62717a7323fac0c19209cc133894c614c2753",
    "scanWindow": "131968930-131969929",
    "scanMints": 16,
    "scanMinters": 16,
    "totalMinted": 27,
    "lastReadWib": "2026-11-06 ~15:06 WIB (re-read: totalMinted 27, freeMinted 27, remainingFreeAllocation 2473, mintOpen 1)",
    "launchNote": "VERIFIED <=48h: first mint block 131968955, 2026-11-06 14:29:47 WIB; zero mint logs back to block 131940000 (~11:00 WIB); age ~35 min at triage",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "UNVERIFIED run ini: contractURI() reverts (method H nihil); name search no site (generic Agent ID articles only). Gate methods A-N belum lengkap — website/X dicek ulang run berikut bila promosi.",
    "baselineNote": "EARLY lead reported once run 1431. Never auto-minted/previewed. Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety.",
}
snap["contracts"]["AgentB-c047"] = {
    "address": "0xc047F826E9E53D853c5683290EE50B6F02496529",
    "status": "early-lead-2026-11-06-1431",
    "name": "AgentB",
    "symbol": "AGENTB",
    "kind": "ERC721",
    "agentShape": "Sourcify verified ABI (17 fns): registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact; mint() nonpayable no-arg; NO price/quote/paid-mint fn in ABI (free by construction)",
    "MAX_SUPPLY": 10000,
    "totalMinted": 382,
    "lastReadWib": "2026-11-06 ~15:06 WIB (totalMinted 382, still minting fast)",
    "userSlot": {"hasMinted": 0, "slotOpen": True},
    "firstSeenBlock": 131965391,
    "firstMintWib": "2026-11-06 14:03:03",
    "scanWindow": "131968930-131969929",
    "scanMints": 63,
    "scanMinters": 63,
    "freePctNote": "UNVERIFIED: no free-allocation/free view on-chain; total % 382/10000 is total %, NOT free % — never substituted",
    "launchNote": "VERIFIED <=48h: first mint block ~131965391 (binary search, Ankr), 2026-11-06 14:03:03 WIB; age ~1h at triage",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "UNVERIFIED run ini (not checked in scan sub-task).",
    "baselineNote": "EARLY lead reported once run 1431. Same-name pair with AgentB-06ec (14:03 vs 14:24); per OG rule this earlier one is the pair OG — with the user's caveat that one dev can run two same-name contracts. No owner() fn in ABI, common-owner check not possible. Never auto-minted/previewed.",
}
snap["contracts"]["AgentB-06ec"] = {
    "address": "0x06ecAE09523DA3698640728cc205305df5C33988",
    "status": "early-lead-2026-11-06-1431",
    "name": "AgentB",
    "symbol": "AGENTB",
    "kind": "ERC721",
    "agentShape": "Sourcify verified ABI (19 fns incl contractURI, variantOf): registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact; mint() nonpayable no-arg; no price/quote/paid fn (free by construction)",
    "MAX_SUPPLY": 10000,
    "totalMinted": 186,
    "lastReadWib": "2026-11-06 ~15:06 WIB (totalMinted 186, still minting)",
    "userSlot": {"hasMinted": 0, "slotOpen": True},
    "firstSeenBlock": 131968198,
    "firstMintWib": "2026-11-06 14:24:06",
    "scanWindow": "131968930-131969929",
    "scanMints": 19,
    "scanMinters": 19,
    "freePctNote": "UNVERIFIED: no free view; total % 186/10000 is not free %",
    "launchNote": "VERIFIED <=48h: first mint block ~131968198 (binary search, Ankr), 2026-11-06 14:24:06 WIB; age ~40 min at triage",
    "xVerified": False,
    "velocityVerified": False,
    "websiteNote": "UNVERIFIED run ini (not checked in scan sub-task).",
    "baselineNote": "EARLY lead reported once run 1431. Later twin of AgentB-c047 (same-name pair 14:03 vs 14:24). Never auto-minted/previewed.",
}

# --- 5. SYMBOL age-exclusion: remove from contracts -> excluded ---
symbol = snap["contracts"].pop("SYMBOL", None)
snap.setdefault("excluded", {})["SYMBOL"] = {
    "address": "0x993C822E7d9bBC75aa6b5095bD90a011Ff38cF71",
    "symbol": "SYMBOL",
    "track": "A",
    "status": "excluded-age-over-48h-2026-11-06",
    "note": ("Website gate kini LOLOS (symbolai.pages.dev mencetak kontrak persis: NFT 0x993c822e..., token 0x265b2a6b..., sale 0x34e81BfE... — diverifikasi parent via browser.open 2026-11-06 14:43 WIB; gateNote 2026-11-03 'no official site' superseded) — TAPI umur GUGUR: miningStart() on-chain 2026-10-27 21:26:29 WIB (Phase 1 Oct 27–Nov 26 per situs); batas konservatif: totalSupply sudah 4272 pada 2026-11-03 10:05 WIB + Boltbook pagi 2026-11-03 lapor freeMint #4269/#4270 → launch <= 2026-11-03 ~10:05 WIB → umur >= ~76 jam pada bacaan 14:47 WIB (dari miningStart ~233 jam). Belum sold out (totalSupply segar 5345/10000, MAX_SUPPLY 10000, mintOpen 1). Free % tetap UNVERIFIED (tanpa free-counter view). Slot user terbuka (mintedBy 0, quoteCents(user,1)=0, balance 0). Diskrepansi: counter situs '3.333 minted' SALAH/stale vs on-chain 5345 — on-chain otoritas. Dihapus dari watchlist per aturan umur 48 jam; tidak dilaporkan ulang kecuali fase/batch mint baru terverifikasi. TIDAK di-preview/di-mint. Detail: run-2026-11-06-1431-symbol.md."),
    "removedWib": NOW_WIB,
}
symbol_excluded = symbol is not None

# --- 6. BNB Chick track_c: fresh pool + gate FAILED ---
chick = snap["track_c"].get("BNB Chick")
if chick is not None:
    chick["freeSharesRemaining"] = 1109
    chick["freeMinted"] = 891
    chick["totalSupply"] = "9000000 CHICK (9e24 wei; 891 free + 9 paid shares x 10000)"
    chick["paidSharesSold"] = 9
    chick["lastReadWib"] = "2026-11-06 14:53 WIB (head 131972055)"
    chick["status"] = "lead-gate-failed-2026-11-06-1431"
    chick["gateNote"] = ("GATE WEBSITE GAGAL run 1431 (methods A–N, diperiksa parent + 2 worker): "
        "(A) raw contract-address search: 0 hit; (B) Boltbook front page EN+ZH + Lemmy API 50 newest: 0 hit 'Chick/CHICK/BNB Chick'; "
        "(C) Sourcify source/metadata: no URL; (D) same-family patterns bnbchick + vercel/pages.dev/deed.page: 0 hit, no URL guessed; "
        "(E) owner() reverts (no owner fn); devWallet 0x7e1c68c63744f85405f581202d69b5d39a1764ab NOT in same-owner-discards; deployer unresolvable (BscScan Cloudflare-blocked + public RPC eth_getCode null); "
        "(F) twitterapi.io DEAD — never called; no handle found elsewhere to confirm; "
        "(G) project-name search 'BNB Chick/CHICK Agent ID free share': no site (generic Agent ID content + unrelated CG FOOD CHICK token); "
        "(H) contractURI: no such fn in 36-fn ABI; (I) tokenURI/external_url: no tokenURI fn (fungible sale, not NFT); "
        "(J) ABI grep website/siteURL/domain/external: none; (K) GitHub code search exact address + name: 0 hit (search-index absence NOT proof of no repo — true code search needs auth); "
        "(L) BscScan token page via live browser: BLOCKED Cloudflare bot wall ('Just a moment...', never cleared, 4 Ray IDs) — INCONCLUSIVE, NOT absence; "
        "(M) site:vercel.app/pages.dev/surge.sh 'BNB Chick'/'bnbchick': no results; deployer-address search impossible (deployer unknown); "
        "(N) registry profile/author-bio hop: no Agent ID handle/project author identified — hop not traversable. "
        "Lead legs tetap lolos (S1, pool 1109/2000, slot user terbuka, umur ~4,9 jam) TAPI gate gagal → TIDAK di-preview/di-mint. "
        "Dilaporkan sekali run 1431 sebagai lead gate-blocked (bukan kandidat). Tetap di track_c sebagai gate-failed; re-check website run berikut bila bukti baru muncul.")
    chick["reportedOnce"] = "run 1431 gate-failed lead report"

# --- 7. Run notes ---
snap["runNote1431_1106"] = (
    "Run 1431 SILENT kecuali 3 EARLY lead baru + 1 gate-failed track-C lead + 1 age-exclusion (lihat laporan run): "
    "0 kandidat baru, 0 promosi strong lead, 0 pending claim baru/dibuka, 0 sellout, 0 slot user hilang. "
    "Leg 1 blok 131969896, interval ~32,2 mnt (estimasi) vs run 1401. Velocity: hanya CantonTron LOLOS matematika (+141, 4,38/mnt, 2,15x) TAPI non-actionable (track-C gate-failed); "
    "Crack nyaris lolos (+229, 7,11/mnt, 1,48x < 1,5x) → GAGAL; SEAT-f11e GAGAL (1,17x, +49); StarAgent-7d39 GAGAL (0,91x, +18), umur ~41,3 jam tetap <=48 jam, tetap EARLY; "
    "KING Agent drift (883->890, remainingFree 2450->2443, free 26,7%) tetap strong-lead-gate-blocked; Thronemind/Hashseers/Smeltbots/Tumblebots GAGAL, tetap strong-lead-gate-blocked; "
    "PassAgentX +6 (3838->3844); Forklings freeMinted 980 (tanpa baseline 1401). Read-fail NULL (bukan nol): HIVE/Mossminds/MILLION/LuckyBox/AgentGlyph/BNB CACHE semua view gagal — degradasi RPC berlanjut. "
    "Koreksi proses: analyze script run ini sempat pakai row[6] file velocity 1401 (rate pra-1401) sebagai prev-rate; dikoreksi ke row[5] (rate run 1401 sendiri) — SEAT 1,42x->1,17x, Crack 1,18x->1,48x; outcome tidak berubah (keduanya GAGAL). File velocity 1401 sendiri konsisten (bug hanya pada cara baca file itu di versi pertama script run ini). "
    "Boltbook front-page urllib gagal (IncompleteRead 0 byte); curl -L berhasil — run berikut pakai curl untuk front page. "
    "Leg 2 Boltbook 0 hit; Lemmy newest tetap 2026-11-05T09:20:52Z. Leg 5a Sourcify 0 baru vs hot-leg-seen, 0 sale shape. "
    "Track B binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0). Bridge 115 kontrak, 7 discarded, 0 not in snapshot. "
    "Sweep 0 proyek baru (SYMBOL website baru → age-excluded, lihat bawah; $SWARM paid-only). Sourcify feed 0 sale shape. 5c: 20 baru dicek, 0 sale shape. "
    "SYMBOL AGE-EXCLUDED + dihapus dari watchlist (miningStart 2026-10-27 21:26 WIB, umur ~233 jam; totalSupply segar 5345/10000; website kini terverifikasi tapi umur gugur). "
    "BNB Chick track-C lead GATE GAGAL (A–N) → dilaporkan sekali, TIDAK di-preview/di-mint; pool segar 1109/2000 (14:53 WIB)."
)
snap["runNote1431_scan_1106"] = (
    "Run 1431: SCAN SUKSES (pertama penuh sejak stall 1301/1331/1401; fix partial-write 14:25 terverifikasi bekerja — partial JSON di disk sejak enrich 1). "
    "Pre-flight OK 8,2 dtk (head 131969891). Window 131968930-131969929 (1000 blok terbaru), 20/20 chunk + 194/194 enrich, 40 panggilan Ankr, 0 error, ~18 mnt, partial=false. "
    "194 NFT (ERC721 188, ERC1155 6) + 460 ERC-20 mint. 7 true first-seen: 3 EARLY lead (WeZards, AgentB 0xc047, AgentB 0x06ec) + RigOrb PAID-ONLY + 3 bukan agent-shaped (SANRAT Racers, bBroker, EDUMARK). "
    "Watermark bersama TIDAK dimajukan (tetap 131939548, posisi backfill); gap 131939549-131968929 (~29.381 blok) ditutup backfill. "
    "5c: 77 ERC-20 mint_count>=10, 44 sudah dicek, 20 baru dicek (cap 20), 0 sale shape (semua Sourcify no-abi); 13 dibuang sampling limit. "
    "Koreksi akuntansi 5c: script sempat tulis '57 sudah dicek' — angka benar 44 (13 cap-dropped ikut terhitung); verdict tidak berubah. 5c eth_getCode sempat None semua (transien; re-test OK) — skrip 5c butuh retry eth_getCode."
)
snap["last_run"] = "2026-11-06 run 1431"
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 1431: 3 EARLY lead baru (WeZards, AgentB 0xc047, AgentB 0x06ec) + BNB Chick track-C lead GATE GAGAL (dilaporkan sekali, tidak di-mint) + "
    "SYMBOL age-excluded (dihapus dari watchlist). 0 kandidat, 0 promosi strong lead, 0 track-B/track-C baru lain. Scan route 4 SUKSES penuh pertama sejak stall 1301/1331/1401.")
snap["timestamp_wib"] = NOW_WIB

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)

# --- 8. Scan-state note (watermark untouched) ---
state["note_1431_scan"] = snap["runNote1431_scan_1106"]
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1, ensure_ascii=False)

# --- 9. Seen file: add 7 first-seen (lowercase addr -> first-seen block) ---
first_seen = {}
for c in scan.get("contracts", []):
    a = (c.get("address") or c.get("contract") or "").lower()
    if a:
        first_seen[a] = c.get("first_block") or c.get("first_seen_block") or scan.get("from_block")
targets = {
    "0xe4d7ec33fcf7d93cbe7f4d46d0ef35f437956aab": 131968955,
    "0xc047f826e9e53d853c5683290ee50b6f02496529": 131965391,
    "0x06ecae09523da3698640728cc205305df5c33988": 131968198,
    "0x72d977237f7b3931a08434ceb d0d3814fe13539e".replace(" ", ""): None,
    "0x8ebd4589f2d5ba4e50bf69b40ad10722de461ac": None,
    "0x94bfa3aa4d95683385fc9a345548179539cb1822": None,
    "0x3a1320343ca0b1a58b2ebd973feb079e6a7ad00": None,
}
added = 0
for addr, fb in targets.items():
    if addr not in seen.get("contracts", {}):
        seen["contracts"][addr] = fb or first_seen.get(addr) or scan.get("from_block")
        added += 1
seen.setdefault("_meta", {})["last_scan_wib"] = NOW_WIB
seen["_meta"]["last_scan_window"] = "131968930-131969929"
seen["_meta"]["last_scan_added"] = added
seen["_meta"]["contracts_count"] = len(seen["contracts"])
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1, ensure_ascii=False)

# --- 10. Merge 5c checked into track-c-scan-checked.json ---
new_addrs = list(checked5c.get("checked", {}).keys())
if isinstance(tcchecked, dict) and isinstance(tcchecked.get("checked"), dict):
    store = tcchecked["checked"]
    before = len(store)
    for a in new_addrs:
        if a not in store:
            store[a] = checked5c["checked"][a]
    after = len(store)
else:
    before = len(tcchecked) if isinstance(tcchecked, dict) else 0
    for a in new_addrs:
        if a not in tcchecked:
            tcchecked[a] = checked5c["checked"][a]
    after = len(tcchecked)
json.dump(tcchecked, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1, ensure_ascii=False)

print(f"merged_nft={merged_nft} merged_trackc={merged_tc}")
print(f"symbol_excluded={symbol_excluded}")
print(f"contracts_now={len(snap['contracts'])} track_c_now={len(snap['track_c'])} excluded_now={len(snap.get('excluded',{}))}")
print(f"seen_added={added} seen_total={len(seen['contracts'])}")
print(f"5c before={before} after={after} new={len(new_addrs)}")
print("snapshot backup: onchain-snapshot.json.bak-20261106-1431")
