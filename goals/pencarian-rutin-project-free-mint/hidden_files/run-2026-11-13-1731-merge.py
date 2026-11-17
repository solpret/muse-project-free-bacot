#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 17:31 WIB.
Updates re-read targets from run-2026-11-13-1731-verify.json (block 133336349),
adds 5 new watchlist entries (Moss Signal, Agent Bubble, Mihao, Cinder Crucible,
Apex), records feed checked-not-sale-shape in track_c, updates binanceai pending.
Read-only on chain; writes snapshot + backup. No preview/mint."""
import json, shutil, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 133336349
READ_WIB = "2026-11-13 ~17:35 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot-2026-11-13-1731.bak")
s = json.load(open(BASE + "onchain-snapshot.json"))
v = json.load(open(BASE + "run-2026-11-13-1731-verify.json"))
vb = json.load(open(BASE + "run-2026-11-13-1731-verify-boltbook.json"))
vn = json.load(open(BASE + "run-2026-11-13-1731-verify-new.json"))
contracts = s.setdefault("contracts", {})
by_addr = {}
for k, e in contracts.items():
    a = (e.get("address") or "").lower() if isinstance(e, dict) else ""
    if a:
        by_addr[a] = k

def upd(addr, fields, note):
    k = by_addr.get(addr.lower())
    if k is None:
        print("WARN no snapshot key for", addr)
        return
    e = contracts[k]
    e.update(fields)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = READ_WIB
    e["runNote1731"] = note

def summ(key):
    r = v["reads"].get(key, {})
    return r.get("summary", {}) or {}

# --- re-read targets (1701 -> 1731, interval ~29.5 mnt, blok 133332412 -> 133336349) ---
upd("0x5314071bba19943f58347ba5dec423e5032a6818",
    {"totalSupply": 688, "totalMinted": 688, "freeMinted": 688,
     "freeAvailable_user": 1, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): freeMinted 687->688/1230 = 55,9% (+1, 0,034/mnt, velocity GAGAL <20 token); umur ~21,6 jam (saleStart 12 Nov 20:01 WIB) <24 jam, deadline 20:01 WIB 13 Nov; slot terbuka (freeAvailable=1). Gate website tetap GAGAL (sudah dilaporkan 12 Nov). DIAM.")
upd("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
    {"freeClaimed": 1000, "freeLeft": 0, "totalMinted": 1197},
    "Run 1731: SELLOUT terkonfirmasi ulang (freeClaimed 1000/1000, freeLeft 0); sudah dilaporkan sekali sebelumnya. DIAM.")
upd("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
    {"totalMinted": 746, "freeMinted": 746, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalMinted 744->746 (+2, 0,068/mnt vs prev 0,10 = 0,68x, <20 token) -> velocity GAGAL; free 746/1111 = 67,1% (<70% strong lead); slot terbuka. Umur ~18,4 jam (mintOpensAt 12 Nov 23:11 WIB) <24 jam, deadline 23:11 WIB 13 Nov. Gate website tetap GAGAL (sudah dilaporkan 08:01 + hot-leg 08:29). DIAM.")
upd("0x779fa133848d23052B7345F63B3b2E5309cd13ed",
    {"freeClaimed": 379},
    "Run 1731: freeClaimed 371->379/888 = 42,7% (+8). <50% -> BUKAN kandidat. DIAM.")
upd("0x639329f5dc4317c44D9Fed961a1217ba845012F7",
    {"totalSpecimens": 2291, "balanceOf_user": 0, "currentExperiment": 2},
    "Run 1731 (blok 133336349): totalSpecimens 2270->2291 (+21, 0,71/mnt vs prev 0,30 = 2,37x, >=20 token) -> velocity LOLOS. TETAP BUKAN kandidat/promosi: free% UNVERIFIED + X UNVERIFIED + website UNVERIFIED; experiment 2 berjalan; deadline umur 21:04 WIB 13 Nov belum lewat. DIAM (tanpa promosi).")
upd("0xDBE8C42d7fB7108bEd4484fC4400F70f526F1412",
    {"freeSold": 34, "minted": 34, "balanceOf_user": 0},
    "Run 1731: freeSold 29->34/1500 (+5); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only. DIAM.")
upd("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
    {"totalMinted": 1934, "freeClaimed": 1933},
    "Run 1731: freeClaimed 1933 FLAT (1933/4444 = 43,5%). DIAM.")
upd("0x7f541bcc33abed0e64455565da723e949c6f76f0",
    {"freeMinted": 216},
    "Run 1731: freeMinted 216 FLAT, umur UNVERIFIED. DIAM.")
upd("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
    {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 1731: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
    {"totalMinted": 294, "freeMinted": 294, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalMinted 292->294 (+2, 0,068/mnt vs prev 0,10 = 0,68x) -> velocity GAGAL; free 294/500 = 58,8%; slot TERBUKA. Umur ~10 jam (mintOpensAt 07:55 WIB) <24 jam. Website/X UNVERIFIED -> BUKAN kandidat, <70% bukan strong lead. DIAM.")
upd("0xad86e4d52e55709d1bda08f922853d4b109e0810",
    {"totalSupply": 1008, "freeMinted": 958, "freeRemaining": 42, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalSupply 999->1008, freeMinted 949->958/1000 = 95,8% (+9, 0,31/mnt vs prev 0,13 = 2,4x, <20 token) -> velocity GAGAL. Umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70% + website lolos + slot terbuka. DIAM.")
upd("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    {"freeCount": 469, "balanceOf_user": 0},
    "Run 1731: freeCount 469 FLAT (15,6%). DIAM.")
upd("0x2e34d33256C920C33b2a03FEC132A2c74061d5D3",
    {"totalSupply": 865, "freeMinted": 845, "freeRemaining": 155, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalSupply 852->865, freeMinted 832->845/1000 = 84,5% (+13, 0,44/mnt vs prev 0,77 = 0,57x) -> velocity GAGAL. Umur TETAP UNVERIFIED + X UNVERIFIED -> BUKAN strong lead walau >70% + slot terbuka. DIAM.")
upd("0xe589A94316C68d4A4f008f841Deb7e9612445244",
    {"totalSupply": 326, "totalMinted": 326, "freeMinted": 325, "freeRemaining": 0, "freeAvailable_user": 0},
    "Run 1731: SELLOUT terkonfirmasi ulang (325/325); sudah dilaporkan sekali sebelumnya. DIAM.")
upd("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D",
    {"totalSupply": 211, "totalMinted": 211, "freeMinted": 210, "freeRemaining": 0, "freeAvailable_user": 0, "balanceOf_user": 0},
    "Run 1731: SELLOUT terkonfirmasi ulang (210/210); sudah dilaporkan sekali sebelumnya. DIAM.")
upd("0x5893199322A5300775912ebD236d8f1fEFC700Db",
    {"totalSupply": 64, "totalMinted": 64, "freeMinted": 63, "freeRemaining": 417, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalSupply 45->64, freeMinted 44->63/480 = 13,1% (+19, 0,64/mnt vs prev 0,13 = 4,9x TAPI <20 token) -> velocity GAGAL. Umur ~2 jam (buka 15:50:57 WIB). Website/X UNVERIFIED, slot user UNVERIFIED. BUKAN kandidat (<50%), BUKAN strong lead (<70%). TIDAK di-preview / TIDAK di-mint. DIAM.")
upd("0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6",
    {"totalSupply": 981, "balanceOf_user": 0},
    "Run 1731: totalSupply 981 FLAT; umur UNVERIFIED. DIAM.")
upd("0x36D9A4392E3d9ff05B6929C82D536367E9c1bc8d",
    {"totalSupply": 62, "totalMinted": 62, "freeMinted": 61, "freeRemaining": 1169,
     "freeAvailable_user": 1, "balanceOf_user": 0},
    "Run 1731 (blok 133336349): totalSupply 27->62, freeMinted 27->61/1230 = 5,0% (+34, 1,15/mnt; tanpa prev rate -> baseline, velocity TIDAK lolos sendirian). Umur ~45 mnt (saleStart 16:51 WIB). Early lead sudah dilaporkan run 1701; website/X UNVERIFIED; slot terbuka. BUKAN kandidat (<50%), BUKAN strong lead (<70%). TIDAK di-preview / TIDAK di-mint. DIAM.")
upd("0xe712510fcb27935e657e41ebb97982d6b123136c",
    {"totalSupply": 524, "balanceOf_user": 0},
    "Run 1731: totalSupply 524 FLAT; umur UNVERIFIED. DIAM.")
upd("0x9081f02876c173d0c69f042959cfd0d61c668b17",
    {"totalSupply": 515, "balanceOf_user": 0},
    "Run 1731: totalSupply 513->515 (+2); umur UNVERIFIED. DIAM.")
upd("0xa545c8726bcf4acf840dac521b369911fe2abc8d",
    {"totalSupply": 289, "balanceOf_user": 0},
    "Run 1731: totalSupply 289 FLAT; umur UNVERIFIED. DIAM.")
upd("0x731d879ee2cd4bbf32efef9178d51d5c1441d052",
    {"totalSupply": 461, "balanceOf_user": 0},
    "Run 1731: totalSupply 460->461 (+1); umur UNVERIFIED. DIAM.")
upd("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
    {"totalSupply": 0, "totalMinted": 0, "FREE_SHARES": 2000, "freeStart": 1794567600},
    "Run 1731: totalSupply 0, freeStart 1794567600 = 18:00 WIB 13 Nov - belum buka saat baca (~17:35 WIB). Cek run berikut sesudah 18:00 WIB. DIAM.")

# --- pending claim binanceai.fun ---
pc = s.get("pending_claims", {})
for k, e in pc.items():
    if isinstance(e, dict) and (e.get("mint") or "").lower() == "0x46cb1d3efd4307506cda7ebba5a51be64746739e":
        e["runNote1731"] = ("Run 1731: launched()=0, tokenClaimed(user)=0, isRefundPhase()=1, failed()=1, "
            "refundClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). Tetap pending, TIDAK dilaporkan ulang. DIAM.")
        e["lastReadWib"] = READ_WIB
        print("binanceai pending updated:", k)

# --- new watchlist entries (all watchlist-only, NOT reported as leads) ---
contracts["Moss Signal"] = {
    "address": "0xb2e5d82900b854d3cb8c6bb917426abadb687f68",
    "name": "Moss Signal", "symbol": "BO01", "status": "watchlist-only-2026-11-13",
    "totalSupply": 765, "MAX_SUPPLY": 805, "mintOpen": 1,
    "price_BNB": 0.0001, "MAX_PER_WALLET": 10,
    "costOf_user_1": 0, "mintedBy_user": 0, "mintedByAgent_user": 0, "balanceOf_user": 0,
    "owner": "0x3fbe2b54baf80d33e2ef6e46cb972959536eca17",
    "website": "https://agent-botanical-004-moss-signal.pages.dev/",
    "lastReadBlock": 133337640, "lastReadWib": "2026-11-13 ~17:45 WIB",
    "note": ("Run 1731 Boltbook baru (post 17:3x WIB, tx hash 0x97f3... BUKAN kontrak - itu hash tx klaim #757; "
        "kontrak sebenarnya 0xb2e5...): totalSupply 765/805 = 95,0% (INFERENSI total-supply saja - TIDAK ADA free counter di kontrak: "
        "ABI Sourcify 37 fns tanpa freeMinted/freeClaimed/freeRemaining/FREE_SUPPLY; price()=0,0001 BNB; costOf(user,1)=0, mintedBy(user)=0, "
        "mintedByAgent(user)=0 -> slot user TERBUKA, free lane 1 mint pertama terverifikasi via costOf). Umur launch TETAP UNVERIFIED: "
        "tanpa saleStart/mintOpensAt view; first-mint via eth_getLogs GAGAL TOTAL (24 chunk x 5000 blok, semua endpoint dataseed gagal; Ankr 401) - "
        "BUKAN bukti tidak ada mint. Website TERVERIFIKASI (site root agent-botanical-004-moss-signal.pages.dev mencetak kontrak persis; "
        "tokenURI -> meta host yang sama + llms.txt). X UNVERIFIED. BUKAN strong lead: kaki free% hanya inferensi + umur unverified. "
        "BUKAN kandidat. TIDAK di-preview/di-mint. Watchlist-only; promosi hanya bila umur terverifikasi <24 jam DAN free% terverifikasi >70%."),
}
contracts["Agent Bubble"] = {
    "address": "0x0d72970046c056db90888351b739246f468bff0b",
    "name": "Agent Bubble", "symbol": "BUBB", "status": "watchlist-only-2026-11-13",
    "totalSupply": 475, "totalMinted": 475, "freeMinted": 374, "MAX_SUPPLY": 2222, "mintOpen": 1,
    "balanceOf_user": 0, "website": "https://agentbubbles.pages.dev",
    "xHandleNote": "contractURI menyebut X https://x.com/Agent_Bubblez; post Boltbook menyebut @Agent_Bubbl - SELISIH, X tetap opsional",
    "lastReadBlock": 133337640, "lastReadWib": "2026-11-13 ~17:45 WIB",
    "note": ("Run 1731 Boltbook baru (post 17:3x WIB): freeMinted 374/2222 = 16,8% TERVERIFIKASI; first mint free lalu 0,00016 BNB "
        "(contractURI). Website TERVERIFIKASI via contractURI external_link https://agentbubbles.pages.dev (site root mencetak kontrak persis). "
        "Umur launch UNVERIFIED (tanpa saleStart/mintOpensAt view). First mint BUKAN run ini (475 sudah minted) -> BUKAN early lead. "
        "BUKAN kandidat (<50%), BUKAN strong lead (<70%). Slot user UNVERIFIED. TIDAK di-preview/di-mint. Watchlist-only."),
}
contracts["Mihao"] = {
    "address": "0xea4ef9da567f59ea7b5f5b7e08305f4e613bab73",
    "name": "Mihao", "symbol": "MIHAO", "status": "watchlist-only-2026-11-13",
    "totalSupply": 438, "MAX_SUPPLY": 2999, "PRICE": 300000000000000, "mintStart": 1794554155,
    "mintOpen": 1, "balanceOf_user": 0, "website": "https://mihao-6zg.pages.dev/",
    "lastReadBlock": 133337640, "lastReadWib": "2026-11-13 ~17:45 WIB",
    "note": ("Run 1731 Boltbook baru (post 17:3x WIB, blok 133336556): totalSupply 438/2999 = 14,6%; mintStart on-chain 1794554155 = "
        "14:15:52 WIB 13 Nov -> umur ~3,6 jam <24 jam TERVERIFIKASI. Website TERVERIFIKASI (mihao-6zg.pages.dev mencetak kontrak persis; "
        "tokenURI host sama). Free% UNVERIFIED (tanpa free view; PRICE 0,0003 BNB = harga berbayar; free lane mintFree hanya klaim post, "
        "belum diverifikasi on-chain). Slot user UNVERIFIED. First mint BUKAN run ini -> BUKAN early lead. BUKAN kandidat (<50%), "
        "BUKAN strong lead. TIDAK di-preview/di-mint. Watchlist-only."),
}
contracts["Cinder Crucible"] = {
    "address": "0x73f1A09e49cA70F8ac6a2F8673Bf7f0f69219b23",
    "name": "Cinder Crucible", "symbol": "CDCR", "status": "upcoming-prelaunch-2026-11-13",
    "totalSupply": 0, "totalMinted": 0, "freeMinted": 0, "freeRemaining": 0,
    "FREE_SUPPLY": 325, "MAX_SUPPLY": 500, "PRICE": 2000000000000000,
    "saleStart": 1794567061, "saleEnd": 1794739861, "mintOpen": 0, "saleOpen": 0, "isFreeOpen": 0,
    "freeAvailable_user": 0, "freeMintedBy_user": 0, "balanceOf_user": 0, "hasAgentId_user": 1,
    "lastReadBlock": 133336984, "lastReadWib": "2026-11-13 ~17:40 WIB",
    "note": ("Run 1731 feed Sourcify baru (verifiedAt 2026-11-13T10:31:14Z): S1-shape LOLOS via ABI 84 fns "
        "(mint/claimFree/mintFree + quote + free views + agentIdRegistry = registry resmi 0x60B926...22F). Sale BELUM BUKA saat baca: "
        "saleStart on-chain 1794567061 = 17:51 WIB 13 Nov, totalMinted 0, saleOpen=0, isFreeOpen=0, freeRemaining 0 (belum buka). "
        "FREE_SUPPLY 325 / MAX 500, PRICE 0,002 BNB (paid). Website UNVERIFIED (contractURI base64 tanpa external_link). X UNVERIFIED. "
        "Status upcoming-prelaunch (bukan kandidat, bukan lead) - TIDAK di-preview/di-mint sebelum buka + verifikasi on-chain. Cek run berikut sesudah 17:51 WIB."),
}
contracts["Apex"] = {
    "address": "0x6DdE73D48Ed92c9C60B77711d37fEc0B03ACBE18",
    "name": "Apex", "symbol": "APEX", "status": "watchlist-only-age-unverified-2026-11-13",
    "totalMinted": 0, "freeMinted": 0, "FREE_CAP": 200, "MAX_SUPPLY": 2000, "mintOpen": 0,
    "freeClaimed_user": 0, "balanceOf_user": 0,
    "lastReadBlock": 133336984, "lastReadWib": "2026-11-13 ~17:40 WIB",
    "note": ("Run 1731 feed Sourcify baru (verifiedAt 2026-11-13T10:32:17Z): ABI 42 fns, mint + free views "
        "(FREE_CAP/freeClaimed/freeLeft/freeMinted) + agent ref, TANPA quote -> S1 GAGAL (quote wajib), S2 belum terbukti "
        "(belum dicek apakah kontrak ini tokennya sendiri + mintFree tanpa argumen). Agent-shaped parsial. BELUM LAUNCH: totalMinted 0, "
        "mintOpen 0, tanpa saleStart view -> umur UNVERIFIED. Website/X UNVERIFIED. BUKAN early lead (0 mint), BUKAN kandidat/strong lead. "
        "Watchlist-only; cek bentuk S2 + launch saat mint pertama muncul."),
}

# --- track_c: feed checked-not-sale-shape ---
tc = s.setdefault("track_c", {})
for key, addr, va, fns, note in [
    ("Feed-0x7758", "0x7758773373E3b07C5e286e7A8c922046a3f0EFfe", "2026-11-13T10:33:34Z", 20,
     "TANPA mint/quote/free view/agent ref"),
    ("Feed-0x9305", "0x93051d18A37A8c9e64655328ea1609ee3B2aa14C", "2026-11-13T10:32:21Z", 34,
     "quote+agent ADA tapi TANPA mint dan TANPA free view"),
    ("Feed-0x5D43", "0x5D4365534e7E87C93B891f53A63b82B5EfaE99bE", "2026-11-13T10:32:19Z", 20,
     "TANPA mint/quote/free view/agent ref"),
    ("Feed-0x01A2", "0x01A2d740Bf09d0F998d049223C2171bF526A81d2", "2026-11-13T10:30:48Z", 21,
     "TANPA mint/quote/free view/agent ref"),
]:
    tc[key] = {"address": addr, "name": key, "status": "checked-not-sale-shape-2026-11-13",
               "note": (f"Run 1731 discovery: Sourcify feed baru (verifiedAt {va}), ABI {fns} fns, S1 false ({note}) - "
                        "BUKAN lead track-C / early lead. Dicatat saja."),
               "lastReadWib": "2026-11-13 ~17:40 WIB"}

s["runNote1731"] = (
    "Run 1731 (17:31-17:55 WIB): DIAM - tidak ada kandidat baru, strong lead baru/promosi, early lead baru, "
    "pending claim baru/dibuka, atau lead track-C baru. 25 target re-read blok 133336349; AgentLabs velocity LOLOS (+21, 2,37x) tanpa promosi "
    "(free%/X/website unverified). 5 watchlist-only baru (Moss Signal, Agent Bubble, Mihao, Cinder Crucible upcoming-prelaunch, Apex) - "
    "TIDAK dilaporkan sebagai lead. Dawn/Mira/Drift Agent: probe bytecode mint+price saja, tanpa free view/agent selector, Sourcify unverified, "
    "umur/free/slot unverified -> BUKAN agent-shaped, tidak masuk snapshot, tidak dilaporkan. BOLT-0x97f3... = hash tx (bukan kontrak; "
    "eth_getCode 0x) - false positive discovery, kontrak sebenarnya Moss Signal. Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (outage sejak "
    "2026-11-09); watermark TETAP 132512564; 5c dilewati. Bridge: 116 kontrak, 7 same-owner-discarded - tidak berubah, tanpa promosi/perubahan.")
s["runNote1731_checked"] = (
    "Run 1731 checked-not-agent-shaped (tidak masuk snapshot, tidak dilaporkan): Dawn Agent 0x4fda436d1370eb612bcb48fd90aefbce5656870e "
    "(9.900/10.000 total, Sourcify unverified, eth_getCode gagal semua endpoint - probe tidak lengkap); Mira Agent "
    "0xa545c7aa04885bbd9cf7ae450ae52c40dcb9e449 (9.900/10.000 total, Sourcify unverified, probe: mint(uint256)+price() saja, tanpa free/agent); "
    "Drift Agent 0x7af5a52a9c00ff2143f2bac4eabf03e1e41950ad (4.901/5.000 total, Sourcify unverified, probe sama: mint+price saja, tanpa free/agent). "
    "Ketiganya: total-supply % tinggi BUKAN free% terverifikasi (tanpa free view), umur UNVERIFIED (tanpa saleStart), slot UNVERIFIED, "
    "owner Dawn/Mira sama 0x69a130b5c5433e55091433bf2e622fede819a1ad (bukan di same-owner-discards). "
    "BOLT-0x97f353205056608341f758841bfa6464c5481b02 = hash transaksi klaim Moss Signal #757 (blok 133326871), BUKAN alamat kontrak.")
s["last_run_wib"] = "2026-11-13 ~17:55 WIB"
s["timestamp_wib"] = "2026-11-13 ~17:55 WIB"
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; contracts:", len(s["contracts"]), "track_c:", len(s["track_c"]))
print("new entries:", [k for k in ("Moss Signal", "Agent Bubble", "Mihao", "Cinder Crucible", "Apex") if k in s["contracts"]])
