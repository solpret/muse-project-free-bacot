#!/usr/bin/env python3
"""Merge run 2231 reread + triage + 5a + binanceai + grove into onchain-snapshot.json.
INTERVAL 32.4 min (block 132602589 ~21:45 WIB -> 132606907 ~22:18 WIB).
Reports due this run: NONE (no new candidate/strong lead/early lead/track-C lead/track-B change/sold-out).
No execution. Read-only except snapshot."""
import json, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 32.4; BLOCK = 132606907
NOW_WIB = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2231-reread.json"))
contracts = snap.setdefault("contracts", {}); track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict): continue
    prev_ts = v.get("totalSupply"); new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts; v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4); v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]: vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None: v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    elif isinstance(fs, int) and fs and isinstance(v.get("freeMinted"), int):
        v["freePctVerified"] = round(100.0 * v["freeMinted"] / fs, 2)
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = NOW_WIB
    v["runNote2231_1109"] = (f"Run 2231 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2131): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict): continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = NOW_WIB
    n_tc += 1
# --- PIXEL MONSTERS: keep reread values (61->196, freeMinted 194); only annotate ---
px = contracts.get("PIXEL MONSTERS")
if isinstance(px, dict):
    px["freePctVerified"] = round(100.0 * px["freeMinted"] / 2000, 2) if isinstance(px.get("freeMinted"), int) else px.get("freePctVerified")
    px["runNote2231_1109"] = ("Run 2231: early lead tetap (dilaporkan run 2131). totalSupply 61->196 (+135, 4,17/mnt, "
        "interval pertama -> baseline rate, velocity TIDAK lolos run ini); freeMinted 194/2000 = 9,7% (masih <25% strong lead); "
        "slot user terbuka (freeClaimed user 0, bal 0); mintOpen 1. Tetap early lead; TIDAK preview/mint.")
# --- NEW: AGENT CORE same-owner-discarded (owner 0x1103) ---
contracts["AGENT CORE"] = {
    "address": "0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
    "name": "AGENT CORE", "symbol": "ACORE", "kind": "ERC721",
    "status": "promotion-discarded-same-owner-2026-11-09",
    "totalSupply": 498, "freeLeft": 1505, "MAX_SUPPLY": 2000, "mintOpen": 1,
    "price": 200000000000000, "MAX_PER_WALLET": 10,
    "freeOf_user_1": 1, "costOf_user_1": 0, "mintsLeft_user": 10, "mintedBy_user": 0,
    "freeClaimed_user": None, "balanceOf_user": 0,
    "owner": "0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd",
    "registry_bytes": True, "code_len": 15606,
    "firstSeenWib": "2026-11-09 22:12 WIB",
    "firstSeenSource": "Boltbook post /p/xLZA60UqHHrS by hi5.ai",
    "lastReadBlock": 132609248, "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: baru via Boltbook. totalSupply 498/2000, freeLeft 1505 (free ~24,75%, di bawah 25% strong lead); "
        "freeOf(user,1)=1, costOf=0, mintsLeft(user)=10, slot user TERBUKA; mintOpen 1, price 0,0002 BNB. "
        "owner() = 0x11038f4a... = gelombang costOf/mintsLeft yang SUDAH ada di same-owner-discards.json (Toucan Play/jelly.exe/Los Flamingos/dll, 11 kontrak) "
        "-> promotion-discarded-same-owner; TIDAK dipromosikan/dilaporkan sebagai lead, TIDAK preview/mint. Umur unverified (tanpa mintStart/startTime). "
        "Website + X unverified. Pace post: 422 (16:33 WIB) -> 497 (~13/jam)."),
}
# --- NEW: Agent Miner watchlist-only (age + free% unverified) ---
contracts["Agent Miner"] = {
    "address": "0x8670e99062ead2ce5402754aede769602fdf38b8",
    "name": "Agent Miner", "symbol": "AGMIN", "kind": "ERC721",
    "status": "watchlist-only-age-free%-unverified-2026-11-09",
    "totalSupply": 1311, "MAX_SUPPLY": 4444, "mintOpen": 1,
    "MAX_PER_WALLET": 5, "soldOut": 0,
    "freeLeft_user": 1, "freeUsed_user": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0xcb529c67b87ceb8f5485ec43e5681ceabaeba275",
    "registry_bytes": True, "code_len": 21884,
    "firstSeenWib": "2026-11-09 22:12 WIB",
    "firstSeenSource": "Boltbook post /p/xLZA60UqHHrS by hi5.ai (bersama AGENT CORE)",
    "lastReadBlock": 132609248, "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: baru via Boltbook (post yang sama dengan AGENT CORE). totalSupply 1311/4444 (29,5% cap), mintOpen 1, PRICE 0,001 BNB (post), "
        "MAX_PER_WALLET 5, soldOut 0; gate Agent ID nyata (mint value 0 revert AgentIdRequired dari plain wallet, per post); freeLeft(user)=1, freeUsed(user)=0 -> slot user TERBUKA. "
        "Owner 0xcb52... TIDAK ada di same-owner-discards.json. free% UNVERIFIED (tanpa view freeClaimed/freeMinted/freeSupply) + umur UNVERIFIED (tanpa mintStart/startTime; "
        "post hanya memberi first-read 16:33 WIB 1092 minted) -> BUKAN early/strong lead (first mint bukan run ini, 1311 sudah termint); watchlist-only; TIDAK dilaporkan; TIDAK preview/mint. "
        "Website + X discussion unverified. RIGS_PER_MINT 15.000 (per post), RIGS tanpa pool/harga terverifikasi."),
}
# --- NEW: Eon Agent watchlist-only age-unverified ---
contracts["Eon Agent"] = {
    "address": "0x9d619eb8d97a746c962ff8defbe3a85d6804b0cf",
    "name": "Eon Agent", "symbol": "EONAGENT", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-09",
    "totalSupply": 9900, "totalMinted": 9900, "MAX_SUPPLY": 10000,
    "price": 1000000000000000, "MAX_PER_WALLET": 10, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x69a130b5c5433e55091433bf2e622fede819a1ad",
    "registry_bytes": True, "code_len": 13598,
    "sourcify": "UNVERIFIED (per post)",
    "firstSeenWib": "2026-11-09 22:16 WIB",
    "firstSeenSource": "Boltbook post /p/hO6pJVIxGB9g by dieuduong369.ai",
    "lastReadBlock": 132609248, "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: baru via Boltbook. 9.900/10.000 (99,0%) per post, terkonfirmasi on-chain totalSupply 9900/10000. UMUR UNVERIFIED: post tanpa waktu launch; "
        "tidak ada view mintStart/startTime/SALE_START/launchTime; Sourcify UNVERIFIED. Template sama dengan Nova/Flare (code_len 13598, registry bytes TRUE) "
        "tapi umur tidak boleh diasumsikan. free% UNVERIFIED (tanpa free views). BUKAN lead; TIDAK dilaporkan; watchlist-only."),
}
# --- NEW: Riddle Run watchlist-only riddle-gated ---
contracts["Riddle Run"] = {
    "address": "0x92473d34f017a342ccbc4119b6ef0ef00daa4ee8",
    "name": "Riddle Run", "symbol": "RRUN", "kind": "ERC721",
    "status": "watchlist-only-riddle-gated-2026-11-09",
    "totalSupply": 67, "totalMinted": 67, "MAX_SUPPLY": 2222,
    "mintStart": 1794225254, "mintStartWib": "2026-11-09 18:54:14 WIB",
    "owner": "0xc137b2e17dc751026473c51bc625a57a233dd399",
    "registry_bytes": True, "code_len": 25682,
    "website": "https://riddlerun.xyz",
    "websiteNote": "Situs ada (riddlerun.xyz, 31.087 byte, fetch run 2231) tapi TIDAK mencetak alamat kontrak exact -> BUKAN website evidence per standar print; gate website UNVERIFIED.",
    "firstSeenWib": "2026-11-09 22:20 WIB",
    "firstSeenSource": "Boltbook ZH post /p/Gy85G0pOjazh by riery.ai",
    "lastReadBlock": 132609248, "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: baru via Boltbook ZH. totalSupply 67/2222, mintStart 2026-11-09 18:54:14 WIB (umur TERVERIFIKASI ~3,7 jam, <=48 jam). "
        "Riddle mint value 0, 2/wallet, TAPI butuh solve clue + sign EIP-712 + server check (bukan click-and-mint; instant mint berbayar 0,002 BNB). "
        "free% UNVERIFIED (tanpa free views); owner 0xc137... TIDAK ada di discards. BUKAN lead (free lane bukan plain free mint agent + tidak bisa auto-mint); "
        "watchlist-only; TIDAK dilaporkan; TIDAK preview/mint."),
}
# --- NEW: Gryphlume excluded free-exhausted (+ same-owner) ---
contracts["Gryphlume"] = {
    "address": "0x8ea465abd41aec8b6f1bd80a7c6c37d3ae85529c",
    "name": "Gryphlume", "symbol": "GRYPLM", "kind": "ERC721",
    "status": "excluded-free-exhausted-2026-11-09",
    "totalSupply": 815, "freeClaimed": 796, "FREE_SUPPLY": 796, "MAX_SUPPLY": 996, "mintOpen": 1,
    "MAX_PER_WALLET": 50, "freeLeft_user": 0, "balanceOf_user": 0,
    "owner": "0xd76d5918fb337667b22fe37ae2055b5542cf8dc9",
    "registry_bytes": True, "code_len": 38136,
    "firstSeenWib": "2026-11-09 22:12 WIB",
    "firstSeenSource": "Boltbook post by vainazmul.ai (EN) + quyennuong.ai (ZH)",
    "lastReadBlock": 132609248, "lastReadWib": NOW_WIB,
    "runNote2231_1109": ("Run 2231: baru via Boltbook. totalSupply 815/996, freeClaimed 796/796 -> FREE LANE TUTUP GLOBAL (habis ~12:09 Dhaka per post; +10 mint terakhir berbayar). "
        "freeLeft(user)=0. Owner 0xd76d... JUGA owner gelombang yang sudah di same-owner-discards.json (Terragent/Mechfarm/Dronegent). "
        "-> EXCLUDED free-exhausted; TIDAK dilaporkan sebagai lead."),
}
# --- 0x4Bc1A172 sale: still not open (light touch; reread already updated freeMinted) ---
sale = track_c.get("0x4Bc1A172-sale")
if isinstance(sale, dict):
    sale["runNote2231_1109"] = ("Run 2231: sale MASIH BELUM BUKA (SALE_START 2026-11-10 12:00 WIB); freeMinted 0, totalSupply null (revert saat baca, sale belum buka). "
        "Status tetap watchlist-only-not-open-2026-11-09; dicek ulang saat buka; TIDAK dilaporkan.")
snap["last_run"] = 2231
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2231: 615 kontrak + 86 track_c re-read (blok 132606907, 746,9 dtk, interval 32,4 mnt vs run 2131); "
    "0 kandidat/strong lead/early lead/track-C baru; 0 sold-out baru; PIXEL MONSTERS tetap early lead (196 total, free 194/2000=9,7%, baseline velocity); "
    "baru via Boltbook: AGENT CORE -> same-owner-discarded (owner 0x1103); Agent Miner watchlist-only (umur+free% unverified, slot user terbuka); "
    "Eon Agent watchlist-only umur unverified (9900/10000); Riddle Run watchlist-only riddle-gated (mintStart 18:54 WIB, situs tidak mencetak kontrak); "
    "Gryphlume excluded free-exhausted (796/796, owner 0xd76d discarded); 5a: 14 alamat baru feed Sourcify, 0 S1/S2 hit; "
    "scan fast-fail Ankr 401 (preflight3 5,0 dtk, head 132608785; watermark 132512564, gap ~96 rb blok); binanceai tetap refund; Grove freeOpen=0.")
snap["runNote2231_1109"] = snap["last_run_note"]
snap["runNote2231_1109_scan"] = ("Run 2231 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 Unauthorized (preflight3, 5,0 dtk, head 132608785; "
    "2 percobaan preflight awal gagal di head() urllib timeout, bukan Ankr); outage sejak ~13:33 WIB 2026-11-09; watermark TETAP 132512564, "
    "gap ~96.221 blok ke head saat preflight3. Backfill bukan tugas job ini; reconnect Ankr belum terverifikasi pulih.")
snap["runNote2231_1109_binanceai"] = ("Run 2231 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, "
    "totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132608135). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2231_1109_5a"] = ("Run 2231 route 5a: 14 alamat BARU feed Sourcify (verifiedAt 14:48-15:14Z), 0 S1/S2 hit "
    "(10 fetch awal timeout urllib, retry via curl semua False; 4 sisanya langsung False; 1 parsial: 0x31B74e69 mint+agent+freeMinted tapi tanpa quote). "
    "5c: tidak ada output scan baru (scan fast-fail sejak 13:33); tidak ada ERC-20 baru dicek run ini.")
snap["runNote2231_1109_velocity"] = ("Run 2231 velocity LOLOS: " + "; ".join(f"{n} +{m} ({r}x)" for n, m, r in vel_pass) +
    ". Tidak ada yang promotable: hanya artefak ERC-20 bridge-0x6eee (totalSupply wei, bukan hitung NFT) - bukan kandidat; "
    "PIXEL MONSTERS +135 tapi interval pertama (baseline, ratio None) + free% 9,7% <25% (tetap early lead); Dragon Agent +43 ratio 0,41 GAGAL; "
    "Undead NFTs +15 <20 GAGAL; Marbleworks +28 ratio 1,36 GAGAL; Agentic free 468/1000=46,8% tetap gate-failed (sudah dilaporkan); "
    "Lenx Agent Pass freeMinted 805 (gate-unverified, tanpa perubahan); FMA (track_c) 505.000->519.000 token (+14).")
snap["runNote2231_1109_discovery"] = ("Run 2231 rute 2: Boltbook EN 45.004 byte + ZH 45.021 byte, rc 200; baru: AGENT CORE 0xf4bacf30 (same-owner-discarded), "
    "Agent Miner 0x8670e990 (watchlist-only), Eon Agent 0x9d619eb8 (watchlist-only), Riddle Run 0x92473d34 (watchlist-only riddle-gated), "
    "Gryphlume 0x8ea465ab (excluded free-exhausted); 0x8269... = BoltRewards (footer, bukan proyek); 0x93e96b... = tx hash klaim AGC (bukan kontrak); "
    "0x92473d34/0xd76d5918 hanya di ZH (Riddle Run + owner Gryphlume). Eon Agent post kedua (dieuduong369.ai 22:16). "
    "Rute 3: sweep EN - MOLT AGENT sudah di snapshot; HOPKIN tidak ditemukan di snapshot run ini (bukan baru); tidak ada proyek baru lain. "
    "Rute 6: Odaily 256.016 byte + PANews 118.659 byte, rc 200, 0 mention Agent ID/free-mint. DappBay tidak dikonsultasikan (tidak ada kandidat yang memerlukannya). "
    "Bridge: tidak berubah (mtime 2026-11-08 18:21 UTC); sama seperti run 2131, tidak ada penambahan ke snapshot.")
snap["runNote2231_1109_grove"] = ("Run 2231 Grove: freeOpen=0 (blok 132604960, grove-check job 22:01 WIB, file run-2026-11-09-2231-grove-check.json) - belum buka.")
snap["runNote2231_1109_triage"] = ("Run 2231 triase: skrip sekuensial awal dihentikan setelah 9 mnt tanpa output (1/5 item selesai: AGENT CORE) lalu diganti versi batch chunk-9 "
    "(4 kontrak tersisa selesai ~51 dtk). AGENT CORE: owner 0x1103 terverifikasi via owner() -> same-owner-discarded. "
    "Agent Miner/Eon/Riddle/Gryphlume terverifikasi via triage2 batch (blok 132609248).")
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE {NOW_WIB} updated={n_upd} track_c={n_tc} vel_pass={vel_pass}")
print("contracts now:", len(snap["contracts"]), "track_c now:", len(snap["track_c"]))
