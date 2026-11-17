#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 22:01 WIB. Read-only inputs:
run-2026-11-12-2201-verify.json, run-2026-11-12-2201-legs.json,
run-2026-11-12-2201-fastbatch.json. Writes snapshot (with .bak-2201 backup)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE+"onchain-snapshot.json", BASE+"onchain-snapshot.json.bak-2201")
s = json.load(open(BASE+"onchain-snapshot.json"))
fb = json.load(open(BASE+"run-2026-11-12-2201-fastbatch.json"))

# --- NAPPER age-exclusion (deadline 2026-11-12 22:00:30 WIB passed during this run) ---
nap = s["contracts"].pop("NAPPER", None)
s["age_exclusions_2201"] = (
 "Run 2201: NAPPER 0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4 - mintStart() 1794409230 = "
 "2026-11-11 22:00:30 WIB (terverifikasi on-chain), deadline 2026-11-12 22:00:30 WIB lewat saat run "
 "(bacaan segar 22:22 WIB blok ~133182592: totalSupply 628/5555 = 11,3%, mintOpen 1; bacaan hot-leg 21:44 WIB "
 "blok 133179433: totalSupply 626/5555). Belum sold out. Website terverifikasi ADA "
 "(dreamcompile.pages.dev via llms.txt) tapi free% UNVERIFIED + bukan agent-shaped; TIDAK PERNAH dilaporkan "
 "sebagai lead/kandidat (watchlist-only) -> dihapus dari contracts TANPA laporan chat (aturan: hapus + catat "
 "bukti; lapor sekali hanya bila pernah dilaporkan). Tidak dilaporkan ulang kecuali ada fase/batch mint baru terverifikasi.")
assert nap is not None, "NAPPER missing from snapshot!"

# --- SolNFT / AgcNFT velocity second read (baseline run 2131 block 133177364) ---
sol = s["contracts"]["SolNFT"]
sol.update({"totalMinted": 71, "freeMinted": 71, "freePctVerified": 21.3,
            "lastReadBlock": 133182592, "lastReadWib": "2026-11-12 22:25 WIB",
            "previousRatePerMin": 1.48,
            "runNote2201": "Run 2201: totalMinted/freeMinted 67 (22:22) -> 71 (22:25) /333 FREE_CAP = 21,3%; "
            "interval vs baseline run 2131 (9, blok 133177364): +58 token / 39,2 mnt = 1,48/mnt = rate baseline pertama "
            "(velocity TIDAK lulus run ini: belum ada previous rate). Umur terverifikasi via mintOpensAt 1794493918 "
            "(21:31:58 WIB). Jauh di bawah 50% kandidat & >70% strong lead; X unverified; gate website GAGAL -> tetap early-lead watchlist, TIDAK preview/mint."})
agc = s["contracts"]["AgcNFT"]
agc.update({"totalMinted": 199, "freeMinted": 199, "freePctVerified": 59.8,
            "lastReadBlock": 133182592, "lastReadWib": "2026-11-12 22:25 WIB",
            "previousRatePerMin": 3.72,
            "runNote2201": "Run 2201: totalMinted/freeMinted 189 (22:22) -> 199 (22:25) /333 FREE_CAP = 59,8% "
            "(>50% kaki kandidat TAPI velocity TIDAK lulus: interval vs baseline run 2131 (43, blok 133177364): +146 token / "
            "39,2 mnt = 3,72/mnt = rate baseline pertama, belum ada previous rate untuk banding 1,5x; X unverified; gate "
            "website GAGAL). Masih <70% strong lead. Tetap early-lead watchlist, TIDAK preview/mint. Waspada run berikut: "
            "bila tembus >70% + gate tetap gagal -> strong lead gate-blocked, lapor sekali."})

# --- MECHA ---
m = s["contracts"]["MECHA"]
m.update({"totalMinted": 1852, "freeClaimed": 1851, "freePctVerified": 41.6,
          "lastReadBlock": 133181032, "lastReadWib": "2026-11-12 22:01 WIB",
          "runNote2201": "Run 2201 (blok 133181032): totalMinted 1850->1852 (+2), freeClaimed 1851/4444 = 41,6%; "
          "velocity GAGAL (<20 token); umur UNVERIFIED; gate website GAGAL -> tetap watchlist-only EARLY."})

# --- track_c additions ---
tc = s.setdefault("track_c", {})
tc["AgentGenesis-fa22"] = {
 "sale": "0xfa22065BEc8aebfA2789CFb7F6F1799c1ecf395e", "token": "0xfa22065BEc8aebfA2789CFb7F6F1799c1ecf395e",
 "name": "Agent Genesis", "symbol": "AGEN", "kind": "ERC721-sale-S1",
 "status": "lead-gate-blocked-2026-11-12",
 "saleShape": "PASS (S1): mint + quote(price) + freeClaimed/freeMinted + agentIdRegistry() = registry resmi 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, Sourcify verified 64 fns",
 "freeMinted": 91, "FREE_CAP": 111, "MAX_SUPPLY": 1111, "freePct": 82.0, "mintOpen": 1,
 "mintOpensAt": 1794494731, "priceWei": 10000000000000000000,
 "freeClaimed_user": 0,
 "launchNote": "Umur TERVERIFIKASI <24 jam: mintOpensAt on-chain 1794494731 = 2026-11-12 21:45:31 WIB "
 "(umur ~40 mnt saat bacaan 22:25 WIB); dikoroborasi live minting (freeMinted 8 hot-leg 21:44 -> 83 run 22:22 -> 91 run 22:25). "
 "First-mint log timestamp TIDAK tersedia (Ankr 401).",
 "slotNote": "Slot user TERBUKA: freeClaimed(user)=0, balanceOf(user)=0 (hot-leg 21:44 + fast-batch run ini).",
 "gateNote": "GATE WEBSITE GAGAL run 2201 (metode A-K/M/N): (A) pencarian alamat kontrak 0 hit proyek; "
 "(B) Boltbook EN+ZH tidak memuat alamat; (C) metadata Sourcify tanpa URL proyek; (G) pencarian nama 'Agent Genesis' "
 "hanya proyek lain (framework/PyPI agent-genesis, OS-Genesis) - same-name BUKAN linkage; (I) contractURI() revert, "
 "tokenURI(1)='1', tokenURI(83)='83' tanpa URL/external_url; (J) ABI tanpa fungsi site/url/domain; (K) GitHub code search "
 "butuh auth - keterbatasan dicatat, search-index 0 hit; (M) site:vercel/pages/deed tanpa hit proyek; (N) tidak ada post "
 "Boltbook/author hop. DILAPORKAN SEKALI run 2201 sebagai track-C lead gate-blocked; TIDAK preview/mint.",
 "lastReadWib": "2026-11-12 22:25 WIB"}
tc["NOTV-0415"] = {
 "sale": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", "token": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
 "name": "Not Verified", "symbol": "NOTV", "kind": "ERC20-sale-S1",
 "status": "watchlist-only-age-unverified-2026-11-12",
 "saleShape": "PASS (S1) per hot-leg 2144: mint+quote+free views+agent registry",
 "totalSupply": 0, "totalMinted": 0, "FREE_SHARES": 2000,
 "note": "BELUM ADA mint sama sekali (totalMinted 0, hot-leg 21:44 + fast-batch run ini) - pre-launch/belum dibuka; "
 "mintOpensAt/mintStart/saleStart revert (tidak ada view) -> umur UNVERIFIED. Watchlist-only, BUKAN lead, TIDAK preview/mint.",
 "lastReadWib": "2026-11-12 22:25 WIB"}
for key, addr, note in [
 ("Feed-0x0FE6e584", "0x0FE6e5840EA22604810408e38b008cA8d6114734", "Run 2201 Sourcify feed: 8 fns, TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
 ("Feed-0x11f07E74", "0x11f07E749Af9440c9Cb4bd455e7Dd992bE58cc7F", "Run 2201 Sourcify feed: TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
 ("Feed-0x5686dC00", "0x5686dC00cA6A1992cCE03f5b68103Ed25088B901", "Run 2201 Sourcify feed: TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
 ("Feed-0xE23fA840", "0xE23fA84096Af4EaE175B9fBCc0563057f224Cb4a", "Run 2201 Sourcify feed: TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
 ("Feed-0x88b30F83", "0x88b30F831c40579736C8554DeA242C280D511e48", "Run 2201 Sourcify feed: TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja."),
 ("Feed-0xcfD4a425", "0xcfD4a425b0Fd404a83A798209011439395Cc83A2", "Run 2201 Sourcify feed + Boltbook: 63 fns, quote+freeClaimed+agent ref TAPI TANPA mint -> GAGAL S1 (mint wajib). Token, bukan NFT -> BUKAN early lead. Dicatat checked saja."),
 ("Boltbook-0x15819ebb", "0x15819ebb5067d1bf38e64298813032654647390F", "Run 2201 Boltbook-new: Sourcify 404 (not verified) -> shape UNKNOWN, BUKAN agent-shaped. Dicatat checked saja, retry run berikut.")]:
    tc[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-12" if "0xcfD4" in addr or "Feed-0x" in key else "checked-unverified-2026-11-12",
               "note": note, "lastReadWib": "2026-11-12 22:01 WIB"}

# --- top-level run notes ---
s["last_run"] = "2026-11-12-2201"
s["last_run_wib"] = "2026-11-12 22:01 WIB"
s["last_run_note"] = ("Run 2201: pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564); feed 20 kontrak, "
 "6 baru, 0 agent-shaped (1 nyaris: 0xcfD4 quote+freeClaimed+agent ref TANPA mint); Boltbook EN+ZH 0 alamat proyek baru "
 "(1 Sourcify-404); bridge 116 kontrak 0 not-in-snapshot, 7 same-owner-discarded; verify 35 target (19 terbaca, 16 BATCH-FAIL); "
 "TRACK-C LEAD BARU Agent Genesis 0xfa22 (free 91/111=82%, umur terverifikasi via mintOpensAt 21:45:31 WIB, slot terbuka) "
 "TAPI GATE WEBSITE GAGAL (A-K/M/N) -> dilapor sekali sebagai lead gate-blocked, TIDAK preview/mint; NAPPER age-excluded "
 "(deadline 22:00:30 lewat, 628/5555) dihapus TANPA laporan chat (tidak pernah jadi lead); AgcNFT 199/333 (59,8%, velocity "
 "baseline pertama 3,72/mnt) + SolNFT 71/333 (21,3%) tetap early-lead watchlist; OBFG 405/1230 (32,9%) tetap gate-blocked; "
 "binanceai masih tutup; 0 kandidat/strong lead/track-B baru; 1 eksekusi: TIDAK ADA (tidak ada preview/mint).")
s["runNote2201_1112"] = ("Run 2201 (blok verify 133181032, elapsed 377,8 dtk; fast-batch blok ~133182592): verify 35 target, "
 "19 terbaca, 16 BATCH-FAIL (OLIVER, Cobalt, NAPPER, DACIT, SYNERGYPASS, DRAGON-0xad0d, AGENT COSMOS, AGENT ID card, RunicKey, "
 "Thor, Vexa, ROBO, SolNFT, AgcNFT, AgentGenesis-fa22, NOTV-0415 - nilai lama dipertahankan, BUKAN nol; retry single-call 27-view "
 "x 5 kontrak TERBUNUH setelah ~7 mnt tanpa output (RPC degradasi), diganti fast-batch 19-call (4 dtk, BERHASIL). "
 "WFPASS free 500/500 sold out; Stampooor 928/1200 (77,3%, slot user terpakai); SEVEN 1111/1111 sold out; AGCR free 2400/2400 sold out; "
 "MECHA 1852 (+2, 41,6%, velocity GAGAL); SUDOSAINTS 716 (+2); Pickgrid 218/216; LuckyCatch 21 (+1); BinanceLife 18 (deadline 23:29:05 WIB "
 "belum lewat); Kongtou 112/111; 0x7Eb9 1195 (+1); NAOMI 783/777 free pool habis; AgenticGangster 124/111 free pool habis; "
 "RigForge freeClaimed 338, openedAt 0 (belum buka); AIRDROP 77/77; Kitebots 1258; Dragon Agent 959 (+1).")
s["runNote2201_1112_binanceai"] = ("Run 2201 (blok 133181032): binanceai-mint launched()=0, freeSharesRemaining=0, FREE_SHARES=2888 - "
 "klaim BELUM dibuka (fase refund); pending_claims tetap kosong; tidak ada klaim/preview.")
s["runNote2201_1112_obfg"] = ("Run 2201: OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 freeMinted 397 (verify) -> 405/1230 (32,9%, fast-batch 22:22 WIB), "
 "totalSupply 397, saleStart 1794488476 (20:01:16 WIB, umur ~2 jam 21 mnt), saleEnd 1794661276, freeAvailable(user)=1, quote(user,1) gratis; "
 "gate website tetap GAGAL (dilaporkan sekali 20:18 WIB), masih <70% strong-lead -> TIDAK preview/mint, tidak dilaporkan ulang; "
 "tracking di hot-leg-seen.json, bukan snapshot utama.")
s["runNote2201_1112_age_exclusions"] = s["age_exclusions_2201"]
s["runNote2201_1112_fa22_gate"] = tc["AgentGenesis-fa22"]["gateNote"] + " Lead legs: sale-shape PASS + free pool 20/111 tersisa (91/111=82,0% per 22:25 WIB) + slot user terbuka + umur terverifikasi <24 jam."

json.dump(s, open(BASE+"onchain-snapshot.json","w"), indent=1)
print("MERGE OK: contracts now", len(s["contracts"]), "| track_c now", len(s["track_c"]))
print("NAPPER in contracts:", "NAPPER" in s["contracts"])
print("SolNFT:", s["contracts"]["SolNFT"]["freeMinted"], s["contracts"]["SolNFT"]["freePctVerified"])
print("AgcNFT:", s["contracts"]["AgcNFT"]["freeMinted"], s["contracts"]["AgcNFT"]["freePctVerified"])
print("FA22 in track_c:", "AgentGenesis-fa22" in s["track_c"])
