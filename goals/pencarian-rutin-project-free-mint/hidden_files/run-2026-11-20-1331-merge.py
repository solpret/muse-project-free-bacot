#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 13:31 WIB into onchain-snapshot.json.
Main re-read ~13:33 WIB (50 kontrak, 418 eth_call, 249 errors - degradasi
RPC bsc-dataseed, nilai lama dipertahankan; eth_blockNumber OK, blok merge 134648052).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru.
Tambahan run ini: Coffee Agents (upcoming, Sourcify baru), PXPC (age-excluded),
NEXUS CORE (sold out) - ketiganya dari sweep/feed run ini, dicatat checked, DIAM."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~13:35 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1331-reread.json"))
BLOCK = 134648052  # eth_blockNumber run ini OK (pre-flight Ankr head 134647869)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1331")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1331-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is not None:
        sv["previousTotalSupply"] = old_sup
        sv["totalSupply"] = new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"] = v["delta"]
        sv["intervalMinutes"] = v["minutes"]
        sv["currentRatePerMin"] = v["rate_per_min"]
    sv["velocityLegPasses"] = bool(v["velocity_pass"])
    if v["free_pct"] is not None:
        sv["freePctInference"] = v["free_pct"]
    sv["lastReadBlock"] = BLOCK
    sv["lastReadWib"] = NOW_WIB
    sv["runNote1331_1120"] = (
        f"Run 1331 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# ONI: totalMinted tetap 208 (tidak berubah vs 1301), balanceOf(user)=0.
oni = snap.get("contracts", {}).get("ONI", {})
if oni:
    oni["totalMinted"] = 208
    oni["freeMinted"] = 208
    oni["balanceOf_user"] = 0
    oni["lastReadBlock"] = BLOCK
    oni["lastReadWib"] = NOW_WIB
    oni["runNote1331_1120"] = (
        f"Run 1331 (blok ~{BLOCK}): totalMinted 208 FLAT vs 1301 (208); free views revert "
        f"(FREE_SUPPLY/freeSupply/freeLeft/quote/freeMintedByWallet) - free% tetap inferensi 20,8%; "
        f"balanceOf(user)=0; slot user UNVERIFIED; website/X belum dicek. Bukan strong lead/kandidat - baseline tracking saja. DIAM.")
# binanceai pending claim: launched/failed/isRefundPhase TERBACA run ini
# (launched=0, failed=1, isRefundPhase=1, totalShares 3110) - tanpa perubahan,
# tetap fase refund (sudah dilaporkan sekali 2026-11-02).
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1331"] = (
    f"Run 1331 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            old_fm = tc[key].get("freeMinted")
            tc[key]["freeMinted"] = fm
            tc[key]["runNote1331_1120"] = (
                f"Run 1331 (blok ~{BLOCK}): freeMinted {old_fm}->{fm}. DIAM.")
        else:
            tc[key]["runNote1331_1120"] = (
                f"Run 1331 (blok ~{BLOCK}): freeMinted GAGAL baca (transport error), nilai lama dipertahankan. DIAM.")
# --- Entri baru run ini (dicatat, DIAM, tanpa laporan chat) ---
contracts = snap.setdefault("contracts", {})
contracts["Coffee Agents"] = {
    "address": "0xc1fAd916153d1b91d6ba9a2253450A6eB2f48245",
    "name": "Coffee Agents", "symbol": "TBEANS",
    "status": "watchlist-only-upcoming-2026-11-20",
    "totalMinted": 0, "totalSupply": None,
    "FREE_QUOTA": 1500, "MAX_SUPPLY": 5555, "MAX_PER_WALLET": 20,
    "MINT_DURATION": 1209600,
    "mintActive": False, "mintStartTime": 0, "currentPrice": 0,
    "agentId": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0x1bd0ce03ddc4c90e840513861860fa1ea481fdb0",
    "freeClaimed_user": False, "balanceOf_user": 0,
    "verifiedAt": "2026-11-20T06:31:33Z",
    "source": "Sourcify recently-verified feed run 1331 (baru)",
    "note": "Agent-shaped TERKONFIRMASI (agentId()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; ABI: mintFree() no-arg, FREE_QUOTA, mintStartTime, mintActive; totalMinted 0, mintActive=false, mintStartTime=0 -> BELUM LAUNCH. Bukan early lead (first mint belum ada), bukan kandidat. Watchlist-only upcoming; pantau startMint. Website/X belum dicari (belum launch).",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-PXPC-2026-11-20"] = {
    "address": "0x6a6601f2d1b8b4cca97ce8800df5e8f4fe1910c8",
    "name": "Pixel Agent PC", "symbol": "PXPC",
    "status": "checked-age-excluded-2026-11-20",
    "totalSupply": 847, "MAX_SUPPLY": 5000, "balanceOf_user": 0,
    "launchNote": "Launch ~2026-10-25T05:31Z (post Binance Square 380989830379207 kontemporer: 'deployed just minutes ago' saat mint) -> umur ~26 hari, >24 jam, belum sold out (847/5000) -> AGE-EXCLUDED.",
    "source": "Sweep rute 3 run 1331 (search-index, Binance Square)",
    "note": "Baru ditemukan run ini dari arsip Square 25 Okt; umur terverifikasi >24 jam -> tidak masuk watchlist aktif, tidak dilaporkan.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
contracts["checked-NEXUSCORE-2026-11-20"] = {
    "address": "0xa477a70223a684e0fe7d31ba1949ee96a4f1995d",
    "name": "NEXUS CORE", "symbol": "NEXUS",
    "status": "checked-sold-out-2026-11-20",
    "totalMinted": 3333, "MAX_SUPPLY": 3333, "mintOpen": 1,
    "quote_user_1": 0, "balanceOf_user": 0,
    "launchNote": "Launch ~2026-10-25 (post Binance Square 381028638509600 kontemporer) -> SOLD OUT 3333/3333.",
    "source": "Sweep rute 3 run 1331 (search-index, Binance Square)",
    "note": "Baru ditemukan run ini dari arsip Square 25 Okt; sudah sold out -> excluded, tidak masuk watchlist, tidak dilaporkan.",
    "lastReadBlock": BLOCK, "lastReadWib": NOW_WIB,
}
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 13:31 WIB"
snap["runNote1331"] = (
    "Run 1331: re-read 50 kontrak (418 call, 249 error RPC, blok merge 134648052); "
    "velocity LOLOS 0 (delta terbesar +9 Everything Is Mine, <20 token; bsccat-sale delta 9e24 = 9 unit sale, bukan NFT); "
    "free>70%: Lumenhold 85,3% (1280/1500, bal_user 0) + STOCK AGENT 83,8% (freeLeft 180/1111, bal_user 0) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; TURTLE 48,9% (43/88) + LION 46,6% (41/88), delta 0, di bawah 50% track-A. "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail. "
    "Sourcify 1 baru: Coffee Agents 0xc1fAd916153d1b91d6ba9a2253450A6eB2f48245 (TBEANS, FREE_QUOTA 1500, MAX_SUPPLY 5555, "
    "agentId()=registry, mintFree() no-arg) - totalMinted 0, mintActive=false, mintStartTime=0 -> BELUM LAUNCH, "
    "watchlist-only upcoming, BUKAN early lead/kandidat, DIAM. "
    "Boltbook EN 45.214 byte + ZH 43.317 byte, 11 alamat full, 0 baru, 0 shape hit. Bridge 0 baru (116/116 in snapshot). "
    "Sweep rute 3: 2 temuan arsip Square 25 Okt - PXPC 0x6a6601f2d1b8b4cca97ce8800df5e8f4fe1910c8 (847/5000, launch ~25 Okt -> umur ~26 hari, AGE-EXCLUDED, dicatat checked) "
    "dan NEXUS CORE 0xa477a70223a684e0fe7d31ba1949ee96a4f1995d (3333/3333 SOLD OUT, dicatat checked); keduanya tidak dilaporkan. "
    "Oathbots/AGENTID/LeadLoop/AGENT COSMOS/JINCHAN sudah di snapshot; GETAGENT tetap watchlist-only (shape FAIL Sourcify unverified, tidak berubah). "
    "ONI totalMinted 208 FLAT, bal_user 0, free% tetap inferensi 20,8%. "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1, totalShares 3110). "
    "bsccat freeMinted 565->574 (+9); AONE freeMinted 10000 (tidak berubah). "
    "TIDAK ada lead/kandidat/eksekusi baru - DIAM.")
snap["runNote1331_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134647869) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~561.667 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
