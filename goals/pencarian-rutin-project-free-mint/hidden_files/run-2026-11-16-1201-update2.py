#!/usr/bin/env python3
"""Snapshot update #2 for run 2026-11-16 12:01 WIB (PEPE / DRAGON / AGENTX).
XOR is handled separately after its getLogs walk finishes.
Read-only on-chain except the snapshot write. No preview/mint."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))

# PEPE BSC share sale 0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980 - USER ALREADY MINTED
# Verified on-chain run 1201 (dataseed): hasMinted(user)=1, freeMinted 204/500, opened=0.
# Sale-shape S1 PASS (mint/claimFree + costOf + freeMinted/freeClaimed + registrar 0x60B9...022F).
# mintStartTime 1794743044 = 2026-11-15 18:44 WIB (age ~17,8 jam <24 jam) but slot user SUDAH dipakai.
s.setdefault("track_c", {})["PEPE"] = {
    "address": "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980",
    "token": "0x66af3218a336ccdb675dba37f6632cfca3f5fe46",
    "pair": "0xc29d69672863fbbf4daaecee78ac678c9703a9a8",
    "registrar": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "status": "minted-by-user-2026-11-16",
    "name": "PEPE",
    "site": "https://pepebnb.pages.dev",
    "saleShape": "S1 PASS (claimFree + costOf + freeMinted/freeClaimed + registrar Agent ID)",
    "freeMinted": 204, "FREE_SHARES": 500, "totalMinted": 204, "totalPaid": 0,
    "TOTAL_SHARES": 10000, "FREE_TOKENS": 10000000, "PRICE": 5000000000000000,
    "opened": 0, "OPEN_AT": 10000, "MINT_WINDOW": 1296000,
    "mintStartTime": 1794743044, "mintStartTimeWib": "2026-11-15 18:44 WIB",
    "costOf_1": 0, "hasMinted_user": 1, "paused": 0, "soldShares": 204,
    "source": "Boltbook b/alpha: ziwbly.ai /p/fz76f5v9kp-P + nicodart.ai /p/bUEi-_pQqY2y + engralif.ai recheck; hot-leg 11:54 sudah mencatat user sudah mint",
    "lastReadWib": "2026-11-16 ~12:01 WIB",
    "runNote1201": "Run 1201: PEPE track-C, freeMinted 204/500 (40,8%), opened=0 (pool belum buka, token belum bisa dijual - pola CAP7/BRAVO), costOf(1)=0, hasMinted(user)=1 -> SLOT USER SUDAH DIPAKAI, bukan lead. Dicatat minted-by-user agar tidak dilaporkan ulang. Umur terverifikasi dari mintStartTime 15 Nov 18:44 WIB (~17,8 jam, <24 jam) tapi tidak relevan karena slot sudah dipakai.",
}
# DRAGON 0xad0d... - free pool CONFIRMED exhausted on-chain run 1201; status stays age-excluded (14 Nov)
d = s["contracts"].get("DRAGON-0xad0d")
if d is not None:
    d["totalSupply"] = 894
    d["freeClaimed"] = 888
    d["FREE_SUPPLY"] = 888
    d["mintOpen"] = 1
    d["balanceOf_user"] = 0
    d["lastReadWib"] = "2026-11-16 ~12:01 WIB"
    d["runNote1201_1116"] = "Run 1201: totalSupply 894, freeClaimed 888/888 = 100% HABIS (terverifikasi on-chain run ini; cocok dengan board super44.ai 11:56 WIB + Alphapedia: free lane tutup 16 Nov ~08:41 WIB, blok ~133841360). Status TETAP age-excluded-2026-11-14 (sudah dikeluarkan dari pantauan aktif 14 Nov) -> TIDAK dilaporkan ulang, hanya dicatat."
# AGENTX 0x64a5... - NEW discovery from board post, AGE-EXCLUDED (mintOpensAt 12 Nov 23:11 WIB, ~85 jam)
s["contracts"]["AGENTX"] = {
    "address": "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    "name": "Agentx", "symbol": "AGENTX",
    "status": "checked-age-excluded-2026-11-16",
    "FREE_CAP": 1111, "freeMinted": 947, "MAX_SUPPLY": 2222, "MAX_PER_WALLET": 2,
    "mintOpen": 1, "mintOpensAt": 1794499865, "mintOpensAtWib": "2026-11-12 23:11 WIB",
    "price": 5000000000000000, "totalMinted": 947, "nextTokenId": 948,
    "freeClaimed_user": 0, "holdsAgentId_user": 1, "mintsBy_user": 0, "balanceOf_user": 0,
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "owner": "0xd314d0b0d204cd6dd7a5b8c9cda1cadc59984344",
    "source": "Boltbook board super44.ai /p/zLoveddNtrpr 11:56 WIB (freeMinted 946/1111); diverifikasi on-chain run 1201 (freeMinted 947/1111 = 85,2%)",
    "lastReadWib": "2026-11-16 ~12:01 WIB",
    "runNote1201": "Run 1201: BARU ditemukan via board post. freeMinted 947/1111 = 85,2% (>70% ambang strong lead), slot user TERBUKA (freeClaimed(user)=0, holdsAgentId=1), mintOpen=1, Sourcify exact_match, agentIdRegistry resmi. TAPI mintOpensAt 12 Nov 23:11 WIB -> umur ~85 jam > 24 jam -> AGE-EXCLUDED. Tidak pernah dilaporkan sebelumnya -> DIAM (tidak dilaporkan sebagai age-excluded). Dicatat agar tidak di-triage ulang.",
}
s["runNote1201_1116_pepe"] = "Run 1201 PEPE (track-C, 0x7E920e...D980): freeMinted 204/500, opened=0, costOf(1)=0, hasMinted(user)=1 -> user SUDAH klaim 1 share gratis (10.000.000 PEPE); slot dipakai, bukan lead. mintStartTime 15 Nov 18:44 WIB. Dicatat minted-by-user di track_c."
s["runNote1201_1116_dragon"] = "Run 1201 DRAGON: freeClaimed 888/888 HABIS (totalSupply 894) terverifikasi on-chain; status tetap age-excluded-2026-11-14, tidak dilaporkan ulang."
s["runNote1201_1116_agentx"] = "Run 1201 AGENTX (baru, board super44.ai): freeMinted 947/1111 = 85,2%, slot user terbuka, tapi mintOpensAt 12 Nov 23:11 WIB (~85 jam) -> AGE-EXCLUDED, diam (belum pernah dilaporkan)."
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("UPDATE2 DONE")
