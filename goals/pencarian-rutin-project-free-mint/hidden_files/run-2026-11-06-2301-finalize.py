#!/usr/bin/env python3
"""Finalize run 2026-11-06 2301 WIB (parent).
Merges leg-1 re-read, velocity rows, scan partial + 5c, Sourcify/Boltbook
findings, targeted reads (Luna verify failed RPC, Hivefacai/WHALE-A sold-out
verified, BINANCEAI refund/failed, Grove freeOpen=0, bridge 0 baru).
No preview/mint/claim/approve/sign/transaksi in this run."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2301"
NOW_WIB = "2026-11-06 run 2301"

for f in ["onchain-snapshot.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-2301")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
vel = json.load(open(f"{BASE}/run-{TS}-velocity.json"))
fivec = json.load(open(f"{BASE}/run-{TS}-5c-checked.json"))
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-2301.json"))

BLOCK = reread.get("block")
merged_nft = 0
merged_tc = 0

NUM_FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "maxSupply", "mintOpen", "paused",
              "freeQuota", "remainingFree", "freeCap", "FREE_CAP", "PAID_CAP",
              "paidMinted", "totalPodsMinted", "freePodsClaimed", "freePodsRemaining",
              "phase", "opened", "launched", "saleEnded", "price", "PRICE"]
USER_FIELDS = {"balanceOf_user": "balanceOf_user", "mintedBy_user": "mintedBy_user",
               "freeUsed_user": "freeUsed_user", "quote_user_1": "quote_user_1",
               "costOf_user_1": "costOf_user_1", "canFreeMint_user": "canFreeMint_user",
               "claimedFree_user": "claimedFree_user", "freeClaimed_user": "freeClaimed_user",
               "freeSharesRemaining": "freeSharesRemaining",
               "freeSharesClaimed_user": "freeSharesClaimed_user",
               "hasFreeShare_user": "hasFreeShare_user",
               "sharesMinted": "sharesMinted", "mintsLeft_user": "mintsLeft_user",
               "mintedPerWallet_user": "mintedPerWallet_user",
               "freeClaimedBy_user": "freeClaimedBy_user",
               "freeWindowClosesAt": "freeWindowClosesAt",
               "quoteFor_user_1": "quoteFor_user_1", "agentGateOn": "agentGateOn",
               "spotsLeft": "spotsLeft", "totalMints": "totalMints"}
for name, d in reread.get("reread", {}).items():
    e = snap["contracts"].get(name)
    if e is None:
        continue
    for f in NUM_FIELDS:
        if d.get(f) is not None:
            e[f] = d[f]
    for src, dst in USER_FIELDS.items():
        if d.get(src) is not None:
            e[dst] = d[src]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1
for name, d in reread.get("track_c", {}).items():
    e = snap["track_c"].get(name)
    if e is None:
        continue
    for f in NUM_FIELDS + list(USER_FIELDS.keys()):
        if isinstance(d, dict) and d.get(f) is not None:
            e[f] = d[f]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- velocity merge (guard: never overwrite with None) ---
vel_rows = {r[0]: r for r in vel.get("rows", [])}
for name, r in vel_rows.items():
    e = snap["contracts"].get(name)
    if e is None or r[3] is None:
        continue
    e["previousTotalSupply"] = r[2]
    e["mintedInInterval"] = r[4]
    e["currentRatePerMin"] = r[5]
    e["previousRatePerMin"] = r[6]
    e["velocityLegPasses"] = bool(r[8])
    e["velocityNote2301"] = (
        f"Run 2301 (blok {vel.get('block_now')}, interval {vel.get('interval_min'):.2f} mnt "
        f"vs run 2201): {r[2]}->{r[3]} (+{r[4]}, {r[5]}/mnt vs prev {r[6]} = "
        f"{r[7] if r[7] is not None else 'None'}x) -> velocity "
        f"{'LOLOS' if r[8] else 'GAGAL'}."
    )
ls = snap["contracts"].get("Lion's Share")
if ls is not None:
    ls["velocityVerified"] = True
    ls["velocityNote2301"] += (" Lion's Share velocity LOLOS run ini, TAPI free% vs free cap tetap "
        "UNVERIFIED (free views None run ini) + umur UNVERIFIED -> tetap watchlist-only, TIDAK promosi, "
        "TIDAK dilaporkan (preseden PassAgentX run 2201 / Sprouts-1831 run 2131). Slot user terbuka "
        "(costOf(user,1)=0, mintedBy 0, balance 0, mintOpen 1).")
pa = snap["contracts"].get("PassAgentX")
if pa is not None:
    pa["velocityNote2301"] = ("Run 2301: freeMinted/totalSupply gagal baca (degradasi RPC); "
        "nilai 2201 dipertahankan; velocity tidak dihitung run ini.")

# --- targeted notes ---
snap["contracts"]["Pulsekeep"]["runNote2301"] = (
    "Run 2301: totalSupply 1977 (1931: 1627; post Boltbook vibibiy 1.916), MAX_SUPPLY 4000, "
    "slot user terbuka (canFreeMint 1, claimedFree 0, balance 0). freeMinted/freeClaimed gagal baca run ini; "
    "free% terakhir terverifikasi 81,25% (1625/2000 FREE_CAP, run 1931). Umur TETAP UNVERIFIED: deep-dive Ankr "
    "getLogs gagal (proxy tunnel stall, 3x retry) + eth_call semua endpoint timeout; Sourcify verifiedAt "
    "2026-11-02T16:18:45Z BUKAN launch time. BUKAN strong lead (butuh umur terverifikasi), BUKAN kandidat.")
snap["contracts"]["RigOrb-539e"]["runNote2301"] = (
    "Run 2301: totalSupply 1424 (0131: 1298), mintOpen 1, priceFor(user,1)=0, mintedCount(user)=0 "
    "(slot terbuka, first mint gratis). Free% tetap UNVERIFIED (free views revert); 1424/10000 = 14,2% < 25% "
    "-> BUKAN strong lead. Umur terverifikasi <=48 jam (first mint 2026-11-05 04:43:23 WIB) tapi akan "
    "age-exclude ~2026-11-07 04:43 WIB bila belum sold out. Website tetap terverifikasi (orb.rigforge.xyz).")
snap["contracts"]["HIVE Agents"]["runNote2301"] = (
    "Run 2301: semua view gagal baca (degradasi RPC); nilai 2201 dipertahankan (totalSupply 1255, balance 1); "
    "minted-by-user, bukan kandidat.")
snap["contracts"]["KING Agent"]["runNote2301"] = (
    "Run 2301: totalSupply/freeQuota/remainingFree gagal baca; costOf(user,1)=0, agentGateOn=1, mintOpen=1, "
    "balance 0; gate-blocked strong lead, tanpa bukti gate baru, tanpa sellout -> tidak dilaporkan.")
snap["contracts"]["Forklings"]["runNote2301"] = (
    "Run 2301: semua view gagal baca; nilai 2201 dipertahankan (freeMinted 1021/2000 = 51,05%, velocity GAGAL); "
    "tetap strong-lead-gate-blocked, tidak dilaporkan ulang.")
snap["contracts"]["Soul Agent"]["runNote2301"] = (
    "Run 2301: supply views gagal baca; quoteFor(user,1)=0, mintedPerWallet(user)=0, balance 0. Deadline 48 jam "
    "2026-11-06 23:53:44 WIB BELUM lewat saat finalisasi (~23:39 WIB) -> belum age-exclude; run 00:01 yang "
    "menangani bila belum sold out.")
if "MoonCat" in snap["contracts"]:
    snap["contracts"]["MoonCat"]["runNote2301"] = (
        "Run 2301: totalSupply 1091/1111 (2201: 1079), 20 tersisa; velocity +12 <20 GAGAL; belum sold out; "
        "watchlist-only, tidak dilaporkan.")
if "Goblins-1831" in snap["contracts"]:
    snap["contracts"]["Goblins-1831"]["runNote2301"] = (
        "Run 2301: totalSupply 457 (baseline lama 200, run 1901; loncatan +257 BUKAN dalam interval 52 mnt ini "
        "— prev 2201 None, baseline SNAP_BASE 200); velocity tidak lolos (rate sebelumnya None); 457/1745, "
        "belum sold out; watchlist-only.")

# --- sold-out removals (verified fresh this run; delete from contracts, archive in excluded) ---
removed = []
for key, addr, max_supply, evidence in [
    ("Hivefacai-d337", "0xd337F2cb906CD5c571eDF4a28DbE66a2447A6281", 700,
     "totalSupply 700 = MAX_SUPPLY 700 = FREE_SUPPLY 700, freeClaimed 699, blok 132041527 (~23:36 WIB, direct eth_call setelah leg-1 gagal baca); dikuatkan post Boltbook vibibiy 16:10 UTC (700/700 sold out) + bacaan 700 di run 2131 dan 2201."),
    ("WHALE-A", "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0", 5000,
     "totalSupply 5000 = MAX_SUPPLY 5000, blok 132039757 (leg-1 run 2301); 2201: 4980; post Boltbook 4.994-4.995/5.000."),
]:
    e = snap["contracts"].pop(key, None)
    if e is None:
        continue
    e["status"] = "sold-out-2026-11-06"
    e["selloutNote2301"] = evidence + " Dilaporkan sekali run 2301; dihapus dari watchlist aktif (contracts) ke excluded."
    snap.setdefault("excluded", {})[key] = e
    removed.append(key)

# --- 5c merge into track-c-scan-checked.json ---
store = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked = store.get("checked", {}) if isinstance(store, dict) else {}
added5c = 0
for r in fivec.get("checked", []):
    a = r["address"]
    if a.lower() not in {k.lower() for k in checked}:
        checked[a] = {
            "run": TS, "mint_count": r.get("mint_count"),
            "S1": r.get("S1"), "S2": r.get("S2"),
            "note": "checked-not-sale-shape (Sourcify not_verified; registry_bytes=True, tanpa ABI)",
            "sourcify": r.get("sourcify"), "registry_bytes": r.get("registry_bytes"),
        }
        added5c += 1
if isinstance(store, dict):
    store["checked"] = checked
json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- run notes ---
snap["runNote2301_1106"] = (
    "Run 2301 (23:01-~23:40 WIB): 0 kandidat, 0 auto-mint/claim, 0 strong-lead baru. 1 EARLY lead BARU DIBATALKAN "
    "oleh koreksi seen-file: Luna Phase Agents (57 mint/43 minter di jendela scan, registry+free views lengkap) "
    "ternyata SUDAH tercatat di onchain-scan-seen.json sejak run 2331 2026-11-02 23:31 WIB (first_seen_block "
    "131271425, 118 mint, status first-seen-recorded-not-early-lead) -> umur >48 jam, BUKAN lead baru, TIDAK "
    "ditambahkan ke snapshot. 2 SELLOUT dilaporkan sekali + dihapus dari watchlist aktif: Hivefacai 700/700 "
    "(verifikasi segar blok 132041527) dan WHALE-A 5000/5000 (leg-1 blok 132039757). Lion's Share velocity LOLOS "
    "(+27, 4,38x) tapi free% + umur UNVERIFIED -> tetap watchlist, tidak promosi. ChimpAgent: semua view None "
    "(degradasi RPC); nilai 2201 dipertahankan; tetap track-c-lead-gate-blocked. BINANCEAI tetap refund/failed "
    "(launched 0, failed 1, isRefundPhase 1, blok 132041726). Agent Grove fase 2 tetap belum dibuka (freeOpen 0, "
    "blok 132041747). Crack VAULT (Boltbook vibibiy): Sourcify 404 (2 rute) -> bukan agent-shaped -> bukan lead, "
    "tidak ditambahkan. Oni/EOND/CELIUZ: bukan lead (tanpa free-shape / ABI tak terbaca / berbayar). Soul Agent "
    "deadline 23:53:44 WIB belum lewat saat finalisasi -> belum age-exclude. Scan parsial (chunk 1000 blok "
    "132037071-132038070 OK, 40 panggilan Ankr, 0 error; enrichment stall 39/168, SCAN_EXIT=124; 0 true first-seen "
    "dari 39 ter-enrich setelah koreksi seen-file; 129 kontrak jendela tak ter-enrich = gap). 5c: 50 ERC-20 "
    "mint>=10, 47 sudah dicek, 3 baru dicek, 0 sale shape. Sourcify feed: 20 kontrak, 10 NEW, 0 S1/S2 "
    "(2 gagal fetch ABI). Boltbook en+zh: 0 baru (vibibiy post: semua nama sudah dikenal snapshot/excluded; "
    "Tacotron + Agent Creatures sudah excluded-umur). Sweep route 3/6: nihil (SWARM berbayar 1 USDT/share; "
    "AGENT MAO + Burn Agent sudah dikenal). Bridge: 115/7/0 baru. Tidak ada preview/mint/claim/approve/sign/transaksi."
)
snap["runNote2301_scan_1106"] = (
    "Scan run 2301: pre-flight v1 GAGAL (dataseed eth_blockNumber timeout 4/4) tapi pre-flight v2 Ankr getLogs OK "
    "8,3 dtk (264 log/50 blok, head proxy 132038070) -> scan jalan. Jendela 132037071-132038070 (1000 blok terbaru "
    "dari watermark 132033557; gap 132033558-132037070 = 3513 blok dilewati cap, milik backfill). 40 panggilan Ankr, "
    "0 error, partial=true. Enrichment stall 39/168 (Sourcify URLError + dataseed eth_getCode/eth_call timeout), "
    "SCAN_EXIT=124 (timeout 780 dtk). Triage awal salah label 'FIRST-SEEN' (membandingkan seen.keys() top-level, "
    "bukan seen['contracts']) — dikoreksi: 0 true first-seen dari 39 ter-enrich; Luna Phase Agents sudah di seen "
    "sejak 2026-11-02. 129 kontrak NFT jendela tidak ter-enrich -> gap cakupan; watermark TIDAK dimajukan "
    "(milik backfill); seen file TIDAK ditulis run ini (semua 39 sudah ada di seen)."
)
snap["last_run"] = NOW_WIB
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = "2026-11-06T23:40:00+07:00"
snap["note"] = snap.get("note", "") + " | Run 2301: 0 kandidat; Hivefacai + WHALE-A sold out (dilaporkan sekali, dihapus dari watchlist); Luna Phase Agents BUKAN lead baru (sudah seen 2026-11-02); Lion's Share velocity lolos tapi free%/umur unverified; scan parsial 39/168."

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

# --- scan state note (append, do not advance watermark) ---
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["note_2301_scan"] = (
    "Run 2301: pre-flight v1 GAGAL (dataseed timeout), pre-flight v2 Ankr getLogs OK 8,3 dtk. Jendela main-scan "
    "132037071-132038070 (1000 blok, cap 1000; gap 132033558-132037070 = 3513 blok dilewati cap, milik backfill). "
    "40 panggilan Ankr, 0 error, partial=true. Enrichment stall 39/168, SCAN_EXIT=124. 0 true first-seen "
    "(koreksi seen-file). 129 kontrak NFT jendela tidak ter-enrich -> gap; watermark TIDAK dimajukan (milik "
    "backfill); seen file TIDAK ditulis run ini."
)
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)

print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added5c={added5c} "
      f"removed={removed} contracts={len(snap['contracts'])} "
      f"track_c={len(snap['track_c'])} excluded={len(snap['excluded'])}")
