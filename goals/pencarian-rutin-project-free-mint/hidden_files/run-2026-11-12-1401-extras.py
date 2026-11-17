#!/usr/bin/env python3
"""Run 1401 extras (after merge): OLIVER update, Meow Cards add
(age-excluded), 5 new Boltbook-post findings add (Cobalt, NAPPER, DACIT,
SYNERGYPASS, DRAGON-0xad0d), finalize last_run_note + final.json decision.
No preview/mint. Snapshot already backed up by merge (.bak-1401)."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap_path = BASE + "onchain-snapshot.json"
snap = json.load(open(snap_path))

# --- 1. OLIVER AGENTS: fresh read run 1401 (run-2026-11-12-1401-oliver.json) ---
ol = json.load(open(BASE + "run-2026-11-12-1401-oliver.json"))
ov = (ol.get("OLIVER") or {}).get("views") or {}
entry = snap.get("contracts", {}).get("Oliver Agents")
assert entry is not None, "Oliver Agents missing from snapshot after merge"
entry["freeMinted"] = ov.get("freeMinted")
entry["freeRemaining"] = ov.get("freeRemaining")
entry["totalSupply"] = ov.get("totalSupply")
entry["paidMinted"] = ov.get("paidMinted")
entry["mintOpen"] = ov.get("mintOpen")
entry["balanceOf_user"] = ov.get("balanceOf_user")
entry["lastReadBlock"] = ol.get("block")
entry["lastReadWib"] = "2026-11-12 14:11 WIB"
entry["previousTotalSupply"] = 689
entry["velocityNote"] = (
    "Run 1401: freeMinted 689 (run 1331, blok 133114044, ~13:47 WIB) -> 722 "
    "(run ini, blok 133117474, ~14:11 WIB) = 72,2% FREE_MAX 1000, laju ~1,4/mnt "
    "(+33 dalam ~24 mnt). MELEWATI 70% (700) TAPI umur TETAP UNVERIFIED -> "
    "BUKAN strong lead (kaki umur gagal), BUKAN kandidat. Velocity TIDAK "
    "menentukan promosi apa pun hasilnya. Slot user TERBUKA (balanceOf 0)."
)
entry["launchNote"] = (
    "Umur TETAP UNVERIFIED run ini (deep-dive diulang): 5 view waktu di kontrak "
    "SEMUA revert/null (mintStart/saleStart/START_TIME/startTime/mintOpensAt); "
    "first-mint block tidak bisa ditarik (Ankr getLogs HTTP 401, outage sejak 9 Nov); "
    "Sourcify verifiedAt 2026-11-12T03:52:35Z = 10:52:35 WIB BUKAN launch time; "
    "situs oliveragents.pages.dev TIDAK menyebut tanggal launch (dicek run ini, "
    "0 tanggal ditemukan); Boltbook post 06:03:11Z (13:03:11 WIB) menyebut 630/1000 "
    "- launch pasti SEBELUM 13:03 WIB, tapi jam pasti tidak terverifikasi."
)
entry["runNote1401"] = (
    "Run 1401: freeMinted 722/1000 = 72,2% (freeRemaining 278), mintOpen 1, "
    "paidMinted 0, slot user TERBUKA (balanceOf 0); website + X TETAP terverifikasi; "
    "umur TETAP UNVERIFIED -> MASIH watchlist-only, BUKAN strong lead meski >70%, "
    "BUKAN kandidat. Tidak di-preview/di-mint. Corroborasi Boltbook board 13:53 "
    "(freeMinted 711) + post hi5 (713 @ ~13:54, 718 @ 14:00) konsisten dengan 722 run ini."
)
print("OLIVER updated: freeMinted", entry["freeMinted"], "block", entry["lastReadBlock"])

# --- 2. Meow Cards: new sweep finding, AGE-EXCLUDED (never a lead) ---
snap["contracts"]["Meow Cards"] = {
    "address": "0xb8164afefc53910d7a74cece15a60a9e0c86089e",
    "name": "Meow Cards",
    "kind": "ERC721",
    "status": "checked-not-lead-age-excluded-2026-11-12",
    "totalSupply": 645,
    "totalMinted": 645,
    "MAX_SUPPLY": 10000,
    "freeClaimed": None,
    "freeMinted": None,
    "FREE_SUPPLY": None,
    "mintOpen": None,
    "balanceOf_user": 0,
    "lastReadBlock": ol.get("block"),
    "lastReadWib": "2026-11-12 14:11 WIB",
    "website": "https://meow-cards.pages.dev",
    "launchNote": "AGE-EXCLUDED: The Colony 2026-11-10 14:40 UTC (21:40 WIB) 'Mint is live now' "
                  "-> launch <= 2026-11-10 21:40 WIB, umur >= ~40,5 jam saat run ini (>24 jam). "
                  "Free views freeClaimed/freeMinted/FREE_SUPPLY revert di kontrak ini.",
    "baselineNote": "Temuan sweep EN run 1401 (search-index). 10.000 kartu kucing, first card free "
                    "per Agent ID wallet. BUKAN lead/kandidat (umur >24 jam). Tidak di-preview/di-mint.",
    "runNote1401": "Run 1401: totalSupply 645/10000 (blok 133117474), umur >=40,5 jam -> AGE-EXCLUDED, "
                   "dicatat saja, tidak dilaporkan sebagai lead.",
}
print("Meow Cards added (age-excluded)")

# --- 3. Five new Boltbook-post findings (route 2 deep read), all watchlist-only ---
NF = json.load(open(BASE + "run-2026-11-12-1401-newfindings.json"))
NB = NF.get("block")
new_entries = {
    "Cobalt Agent": {
        "address": "0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0",
        "name": "Cobalt Agent",
        "kind": "ERC721",
        "status": "watchlist-only-age-unverified-2026-11-12",
        "totalSupply": 4900, "totalMinted": 4900, "MAX_SUPPLY": 5000,
        "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
        "mintOpen": None, "balanceOf_user": 0, "mintedBy_user": 0,
        "price": 1000000000000000,
        "lastReadBlock": NB, "lastReadWib": "2026-11-12 14:11 WIB",
        "launchNote": "Umur UNVERIFIED: semua view waktu revert/null; first-mint block tidak bisa "
                      "ditarik (Ankr 401); Sourcify UNVERIFIED (404); tidak ada tanggal launch "
                      "ditemukan via search. Post Boltbook duyenvu75.ai 14:02 WIB menyebut 4.900/5.000.",
        "baselineNote": "Temuan baru run 1401 via post Boltbook (route 2 deep read). Agent-shaped: "
                        "registry bytes 0x60B926...022F ADA di bytecode. Free% UNVERIFIED: tidak ada "
                        "free counter yang terbaca (freeClaimed/freeMinted/FREE_SUPPLY/freeRemaining "
                        "semua revert) - % total-supply 98% BUKAN % free-quota, tidak boleh disubstitusi. "
                        "Slot user tampak terbuka (balanceOf 0, mintedBy 0). BUKAN early lead (first mints "
                        "bukan di run ini), BUKAN strong lead (umur + free% unverified), BUKAN kandidat. "
                        "Tidak di-preview/di-mint.",
        "runNote1401": "Run 1401 first read (blok 133118130): totalSupply 4900/5000, Sourcify UNVERIFIED, "
                       "umur + free% UNVERIFIED -> watchlist-only.",
    },
    "NAPPER": {
        "address": "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4",
        "name": "NAPPER",
        "kind": "ERC721",
        "status": "watchlist-only-2026-11-12",
        "totalSupply": 529, "MAX_SUPPLY": 5555,
        "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
        "mintOpen": 1, "mintStart": 1794409230,
        "balanceOf_user": 0, "mintedBy_user": 0,
        "lastReadBlock": NB, "lastReadWib": "2026-11-12 14:11 WIB",
        "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart() = 1794409230 = 2026-11-11 22:00:30 WIB "
                      "(~16 jam saat run ini). Koroborasi first-mint event tidak tersedia (Ankr 401). "
                      "Deadline 18 Nov 22:00 WIB (klaim board) adalah backstop, bukan cap.",
        "baselineNote": "Temuan baru run 1401 via Boltbook board 13:53 (route 2 deep read). Sourcify "
                        "exact_match (verifiedAt 2026-11-11T15:00:59Z), 133 fns, mint + quote + freeLeft. "
                        "Agent-shape BELUM terkonfirmasi: registry bytes TIDAK ada di bytecode, tidak ada "
                        "fungsi agentRegistry/agentGate di ABI. Free% UNVERIFIED: freeLeft() terbaca "
                        "sebagai nilai sampah (selector/tabrak) - klaim board ~510/2000 (25,5%) adalah "
                        "pihak ketiga, bukan verifikasi job ini. Slot user terbuka (balanceOf 0, mintedBy 0). "
                        "BUKAN lead/kandidat (free% + agent-shape unverified). Tidak di-preview/di-mint.",
        "runNote1401": "Run 1401 first read (blok 133118130): totalSupply 529/5555, mintStart 2026-11-11 "
                       "22:00:30 WIB (umur ~16 jam, <24 jam), free% + agent-shape UNVERIFIED -> watchlist-only.",
    },
    "DACIT": {
        "address": "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd",
        "name": "DACIT",
        "kind": "ERC721",
        "status": "watchlist-only-2026-11-12",
        "totalMinted": 1724, "agentFreeUsed": 1692,
        "freeClaimed": None, "freeMinted": None, "FREE_SUPPLY": None,
        "mintOpen": None, "mintStart": 1794386374,
        "balanceOf_user": 0, "mintedBy_user": 0,
        "lastReadBlock": NB, "lastReadWib": "2026-11-12 14:11 WIB",
        "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart() = 1794386374 = 2026-11-11 15:39:34 WIB "
                      "(~22,6 jam saat run ini; jendela 24 jam tutup ~15:39 WIB hari ini). Koroborasi "
                      "first-mint event tidak tersedia (Ankr 401).",
        "baselineNote": "Temuan baru run 1401 via Boltbook board 13:53 (route 2 deep read). Sourcify "
                        "exact_match (verifiedAt 2026-11-11T08:56:09Z), 53 fns. Agent-shaped: registry "
                        "bytes 0x60B926...022F ADA di bytecode. Free% UNVERIFIED: free cap tidak terbaca "
                        "(FREE_SUPPLY/MAX_SUPPLY revert); agentFreeUsed 1692 vs totalMinted 1724 (paid gap "
                        "32, cocok dengan board) tapi tanpa cap, % tidak bisa dihitung. Slot user terbuka "
                        "(balanceOf 0, mintedBy 0). BUKAN strong lead (free% unverified), BUKAN kandidat. "
                        "Tidak di-preview/di-mint.",
        "runNote1401": "Run 1401 first read (blok 133118130): totalMinted 1724, agentFreeUsed 1692, "
                       "mintStart 2026-11-11 15:39:34 WIB (umur ~22,6 jam, <24 jam), free% UNVERIFIED "
                       "-> watchlist-only.",
    },
    "SYNERGYPASS": {
        "address": "0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e",
        "name": "SYNERGYPASS",
        "kind": "ERC721",
        "status": "watchlist-only-age-unverified-2026-11-12",
        "totalMinted": 245, "freeMinted": 245, "FREE_SUPPLY": 1111, "MAX_SUPPLY": 8888,
        "freePctVerified": 22.05,
        "balanceOf_user": 0, "freeClaimed_user": 0,
        "lastReadBlock": NB, "lastReadWib": "2026-11-12 14:11 WIB",
        "launchNote": "Umur UNVERIFIED: semua view waktu revert/null; first-mint block tidak bisa "
                      "ditarik (Ankr 401); Sourcify UNVERIFIED (404); tidak ada tanggal launch "
                      "ditemukan via search.",
        "baselineNote": "Temuan baru run 1401 via Boltbook board 13:53 (route 2 deep read). Agent-shaped: "
                        "registry bytes 0x60B926...022F ADA di bytecode. Free 245/1111 = 22,0% TERVERIFIKASI "
                        "(<50% dan <70%). Klaim board bahwa view revert TIDAK cocok dengan baca job ini "
                        "(view terbaca bersih di node kami) - angka job ini yang dipakai. Slot user terbuka "
                        "(balanceOf 0, freeClaimed(user) 0). BUKAN lead/kandidat (22% + umur unverified). "
                        "Tidak di-preview/di-mint.",
        "runNote1401": "Run 1401 first read (blok 133118130): freeMinted 245/1111 = 22,0%, Sourcify "
                       "UNVERIFIED, umur UNVERIFIED -> watchlist-only.",
    },
    "DRAGON-0xad0d": {
        "address": "0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998",
        "name": "DRAGON (0xad0d)",
        "kind": "ERC721",
        "status": "watchlist-only-age-unverified-2026-11-12",
        "totalSupply": 486, "freeClaimed": 482, "FREE_SUPPLY": 888, "MAX_SUPPLY": 1888,
        "freePctVerified": 54.28,
        "mintOpen": 1, "price": 200000000000000,
        "balanceOf_user": 0, "mintedBy_user": 0,
        "lastReadBlock": NB, "lastReadWib": "2026-11-12 14:11 WIB",
        "launchNote": "Umur UNVERIFIED: semua view waktu revert/null; first-mint block tidak bisa "
                      "ditarik (Ankr 401); tidak ada tanggal launch ditemukan via search. Sourcify "
                      "verifiedAt 2026-11-11T22:52:03Z BUKAN launch time.",
        "baselineNote": "Temuan baru run 1401 via Boltbook board 13:53 (route 2 deep read). BUKAN 'Dragon "
                        "Agent' 0xaa87 yang sudah di snapshot - kontrak berbeda. Agent-shaped: registry "
                        "bytes 0x60B926...022F ADA di bytecode. Free 482/888 = 54,3% TERVERIFIKASI (>50% "
                        "kaki kandidat, <70% kaki strong lead). Sourcify exact_match, 38 fns, mint + quote "
                        "+ freeClaimed. Slot user terbuka (balanceOf 0, mintedBy 0). Velocity: first read, "
                        "belum ada baseline. BUKAN kandidat (umur unverified), BUKAN strong lead (umur "
                        "unverified + 54,3% <70%). Website UNVERIFIED. Tidak di-preview/di-mint.",
        "runNote1401": "Run 1401 first read (blok 133118130): freeClaimed 482/888 = 54,3%, umur "
                       "UNVERIFIED -> watchlist-only.",
    },
}
for k, v in new_entries.items():
    snap["contracts"][k] = v
    print("added:", k, v["address"])

# --- 4. Finalize decision ---
fin_path = BASE + "run-2026-11-12-1401-final.json"
fin = json.load(open(fin_path))
fin["decision"] = "SILENT"
fin["sweep"] = {
    "en": "0 baru - Meow Cards (10 Nov, age-excluded, dicatat di snapshot); Oathbots (28 Okt, age-excluded); Agentic Gangster (sold out); RIGBYPASS (sudah excluded di snapshot); MOLT AGENT (sudah excluded); FACES/Foundry Faces (sudah di snapshot)",
    "zh": "0 baru - NOVRA + WUMPO + UFO/NEBULA (sudah di track_c); AGENT ID card + First-Dollar Grove (sudah age-excluded di snapshot); WNO (sudah age-excluded)",
    "boltbook_posts": "5 temuan baru via post Boltbook (route 2 deep read): Cobalt Agent, NAPPER, DACIT, SYNERGYPASS, DRAGON-0xad0d - semuanya watchlist-only (lihat run-2026-11-12-1401-newfindings.json); GEM masih upcoming (board: belum start); NERO/DRAGON-board-tail tanpa alamat tidak diverifikasi",
}
fin["oliver"] = {"freeMinted": 722, "freeMax": 1000, "pct": 72.2, "age": "unverified",
                 "block": ol.get("block"),
                 "note": "Crossed 70% but age unverified -> NOT a strong lead, watchlist-only"}
fin["new_watchlist"] = list(new_entries.keys())
json.dump(fin, open(fin_path, "w"), indent=1)
snap["last_run_note"] = (
    "Run 1401 SILENT: pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov; scan fast-fail, watermark tidak dimajukan). "
    "Legs: feed 20 (verified 06:43:22-07:02:29Z), 2 baru vs hot-leg-seen (0x7f57, 0x3555 - bukan S1/S2/early-shape); "
    "Boltbook EN 44.247 byte / ZH 42.248 byte, 12 alamat, 0 baru; bridge 116 kontrak, 0 not-in-snapshot. "
    "Verify2-supplement blok 133117050 (21 target): WFPASS 502/500 free habis; Stampooor 914/1200 = 76,2% (+2, age-excluded, "
    "minted-by-user); SEVEN 1111/1111; AGCR 2400/2400 sold out; MECHA 1633 (+5); 0x7Eb9 1185 (+1); NAOMI 783/777 sold out; "
    "RigForge 337/663, openedAt 0 (belum buka); binanceai launched()=0 TETAP (pending, fase refund). "
    "Reread blok 133117564: 63 kontrak + 21 track_c, delta terbesar Cosmic Sentinel +16 (<20, velocity gagal, 0,23% dari "
    "MAX 225.000); track_c tanpa perubahan. tc-age: CLEPSYDRA + MoonAgent + WNO TETAP age-excluded. "
    "OLIVER 722/1000 = 72,2% (blok 133117474) - MELEWATI 70% TAPI umur TETAP UNVERIFIED (deep-dive diulang: 5 view waktu "
    "revert, situs tanpa tanggal, Ankr 401) -> watchlist-only, BUKAN strong lead/kandidat, tidak di-preview/di-mint. "
    "Temuan baru Boltbook posts (semua watchlist-only, tidak dilaporkan sebagai lead): Cobalt Agent (free% unverified, "
    "Sourcify unverified, umur unverified), NAPPER (umur terverifikasi ~16 jam via mintStart, free% + agent-shape unverified), "
    "DACIT (umur terverifikasi ~22,6 jam via mintStart, free% unverified), SYNERGYPASS (22,0% terverifikasi, umur unverified), "
    "DRAGON-0xad0d (54,3% terverifikasi, umur unverified). Meow Cards age-excluded (launch <=10 Nov 21:40 WIB). "
    "Sweep EN+ZH: 0 kandidat, 0 strong lead, 0 early lead, 0 track-B dibuka, 0 track-C baru. Tidak ada eksekusi."
)
json.dump(snap, open(snap_path, "w"), indent=1)
print("EXTRAS DONE")
