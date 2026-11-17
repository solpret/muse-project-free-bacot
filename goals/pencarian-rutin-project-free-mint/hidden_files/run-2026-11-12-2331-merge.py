#!/usr/bin/env python3
"""Merge run 2026-11-12 2331 into onchain-snapshot.json.
Reads: run-2026-11-12-2331-fastbatch.json + run-2026-11-12-2331-verify.stdout.log
       + fresh targeted re-reads done this run (CAP7, PESI, BC1B slot/registry).
Applies: value updates, Home promotion, BC1B add, 3 age-exclusions (removals),
         fa22 excluded-entry confirmation, run notes.
"""
import json, re, shutil, ast, os

H = os.path.expanduser("~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
SNAP = os.path.join(H, "onchain-snapshot.json")
shutil.copy2(SNAP, SNAP + ".bak-2331")
snap = json.load(open(SNAP))
fb = json.load(open(os.path.join(H, "run-2026-11-12-2331-fastbatch.json")))
BLOCK = fb["block"]  # 133196011
NOW = "2026-11-13 ~00:15 WIB"

def find_by_addr(addr):
    a = addr.lower()
    for sec in ("contracts", "track_c", "excluded"):
        for k, v in snap.get(sec, {}).items():
            if isinstance(v, dict):
                for f in ("address", "sale", "token"):
                    if isinstance(v.get(f), str) and v[f].lower() == a:
                        return sec, k
    return None, None

def upd(sec, key, vals, note=None):
    e = snap.get(sec, {}).get(key)
    if e is None:
        print("SKIP missing", sec, key)
        return False
    for k, v in vals.items():
        if v is not None:
            e[k] = v
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-12 ~23:57 WIB"
    if note:
        e["runNote2331"] = note
    return True

# ---- fastbatch updates (block 133196011) ----
r = fb["reads"]
upd("contracts", "SolNFT", {"totalMinted": r["SolNFT"]["totalMinted"], "freeMinted": r["SolNFT"]["freeMinted"],
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": 0, "freePctVerified": round(272/333*100, 1)},
    "Run 2331: 272/333 = 81,7% (>70%), slot terbuka, umur <24 jam (mintOpensAt 21:31:58 WIB). Tetap strong-lead-gate-blocked (dilaporkan 23:01) - DIAM.")
upd("contracts", "AgcNFT", {"totalMinted": r["AgcNFT"]["totalMinted"], "freeMinted": r["AgcNFT"]["freeMinted"],
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": 0, "freePctVerified": round(314/333*100, 1)},
    "Run 2331: 314/333 = 94,3% (>70%), slot terbuka, umur <24 jam (mintOpensAt 21:33:32 WIB). Tetap strong-lead-gate-blocked (dilaporkan 22:31) - DIAM.")
upd("contracts", "Home", {"totalMinted": r["NEW-fd55"]["totalMinted"], "freeMinted": r["NEW-fd55"]["freeMinted"],
    "mintOpen": 1, "balanceOf_user": 0, "freeClaimed_user": 0, "freePctVerified": round(97/111*100, 1),
    "status": "strong-lead-gate-blocked-2026-11-12"},
    "Run 2331 PROMOSI early->STRONG LEAD: 97/111 = 87,4% (>70%), mintOpen 1, slot terbuka, mintOpensAt 1794498886 = 22:54:46 WIB (umur ~1 jam, TERVERIFIKASI). Gate website GAGAL metode A/B/C/G/H/I/J (K search-index 0; M tanpa hit; L tidak dicoba - preseden SolNFT 2301). DILAPORKAN SEKALI run ini sebagai strong lead gate-blocked; TIDAK preview/mint. Velocity: +35 interval pertama (62->97).")
upd("contracts", "Steady", {"totalSupply": r["0x4919-S1"]["totalSupply"], "freeClaimed": r["0x4919-S1"]["freeClaimed"],
    "freePctVerified": round(347/555*100, 1)},
    "Run 2331: 347/555 = 62,5% (<70%), umur MASIH UNVERIFIED. Tetap early-lead - DIAM. Velocity +68 (279->347).")
# MECHA via verify log (block pre-fastbatch)
upd("contracts", "MECHA", {"totalMinted": 1869, "freeClaimed": 1868, "freePctVerified": round(1868/4444*100, 1)},
    "Run 2331 (verify log): 1868/4444 = 42,0%, umur UNVERIFIED. Tetap early-lead - DIAM.")
# OBFG via address lookup
sec, key = find_by_addr("0x5314071bba19943f58347ba5dec423e5032a6818")
print("OBFG found:", sec, key)
if sec:
    upd(sec, key, {"totalMinted": 469, "freeMinted": 469, "freePctVerified": round(469/1230*100, 1)},
        "Run 2331: 469/1230 = 38,1% (verify log), saleStart 1794488476 = 20:01:16 WIB, freeAvailable(user)=1. Tetap track-C lead gate-blocked (dilaporkan 20:18) - DIAM.")

# ---- verify-log updates (values from run-2026-11-12-2331-verify.stdout.log) ----
log = open(os.path.join(H, "run-2026-11-12-2331-verify.stdout.log")).read()
parsed = {}
for line in log.splitlines():
    m = re.match(r"^(\S.*?)\s+(\{.*\})\s+contractURI:", line)
    if m:
        try:
            parsed[m.group(1).strip()] = ast.literal_eval(m.group(2))
        except Exception as ex:
            print("parse fail:", m.group(1), ex)
print("verify parsed keys:", sorted(parsed.keys()))
KEYMAP = {"BinanceLife": "Binance Life Cards", "Kongtou-AirdropCnNFT": None, "Dragon Agent": "Dragon Agent",
          "WFPASS": "WFPASS", "SEVEN": "SEVEN", "AGCR": "AGCR", "SUDOSAINTS": "SUDOSAINTS",
          "Pickgrid": "Pickgrid", "LuckyCatch": "LuckyCatch", "AgenticGangster": "AgenticGangster",
          "AIRDROP": "AIRDROP", "Kitebots": "Kitebots"}
for lk, vals in parsed.items():
    if lk in ("BinanceLife", "OBFG", "MECHA", "Stampooor"):
        continue
    sk = KEYMAP.get(lk, lk)
    if sk is None:
        print("verify key unmapped (logged only):", lk, vals)
        continue
    sec2, key2 = ("contracts", sk)
    if sk not in snap.get("contracts", {}):
        sec2, key2 = find_by_addr("")  # placeholder
        # try track_c
        if sk in snap.get("track_c", {}):
            sec2, key2 = "track_c", sk
        else:
            print("verify key not in snapshot (logged only):", lk, "->", sk)
            continue
    e = snap[sec2][key2]
    for f in ("totalSupply", "totalMinted", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen",
              "balanceOf_user", "freeClaimed_user", "mintedBy_user", "freeAvailable_user", "mintStart"):
        if vals.get(f) is not None:
            e[f] = vals[f]
    e["lastReadWib"] = "2026-11-12 ~23:40 WIB (verify-2331)"
    e["runNote2331"] = "Run 2331 (verify log): " + json.dumps({k: v for k, v in vals.items() if v is not None})[:400]
# RigForge + binanceai-mint (track_c / pending)
if "RigForge" in snap.get("track_c", {}):
    e = snap["track_c"]["RigForge"]
    e.update({"freeClaimed": 338, "freeSharesLeft": 662, "openedAt": 0, "FREE_SHARES": 1000,
              "lastReadWib": "2026-11-12 ~23:40 WIB (verify-2331)",
              "runNote2331": "Run 2331: freeClaimed 338, freeSharesLeft 662, openedAt 0 - belum dibuka. DIAM."})
sec3, key3 = find_by_addr("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E")
print("binanceai-mint found:", sec3, key3)
if sec3 and key3:
    e = snap[sec3][key3]
    e.update({"launched": 0, "freeSharesRemaining": 0, "FREE_SHARES": 2888,
              "lastReadWib": "2026-11-12 ~23:40 WIB (verify-2331)",
              "runNote2331": "Run 2331: launched 0, freeSharesRemaining 0, FREE_SHARES 2888 - tetap refund phase. DIAM."})
# NOTV-0415 + LOWB + BHTB + AgentGrid-sale (fastbatch, generic views mostly null)
sec4, key4 = find_by_addr("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01")
if sec4:
    e = snap[sec4][key4]
    e.update({"totalMinted": 0, "totalSupply": 0, "lastReadBlock": BLOCK,
              "lastReadWib": "2026-11-12 ~23:57 WIB",
              "runNote2331": "Run 2331: totalMinted 0 - belum dibuka (freeStart 1794567600 = 13 Nov 18:00 WIB). DIAM."})
for addr, note in [("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", "Run 2331: totalMinted 1013, FREE_SHARES 1000, opened 0 - free pool habis. DIAM."),
                   ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", "Run 2331: hanya totalSupply 1e26 terbaca; pool/launch unverified. DIAM."),
                   ("0x651302C0043040D48EaAF85605E12F0549aD6D89", "Run 2331: hanya FREE_SHARES 500 terbaca. DIAM.")]:
    s5, k5 = find_by_addr(addr)
    if s5:
        snap[s5][k5].update({"lastReadBlock": BLOCK, "lastReadWib": "2026-11-12 ~23:57 WIB", "runNote2331": note})
    else:
        print("not found by addr:", addr)

# ---- fa22 excluded-entry confirmation ----
fe = snap.get("excluded", {}).get("AgentGenesis-fa22")
if fe:
    fe["freeMinted"] = 111
    fe["freePct"] = 100.0
    fe["runNote2331"] = "Run 2331: dikonfirmasi sold out 111/111 FREE_CAP (blok 133196011). Sellout SUDAH dilaporkan run 2231 + sudah excluded - DIAM run ini."

# ---- BC1B / RESUME -> track_c (track-C lead baru, gate-blocked) ----
snap.setdefault("track_c", {})["RESUME-BC1B"] = {
    "sale": "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    "token": "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
    "name": "RESUME", "symbol": "RESUME", "kind": "track-c-sale-S2",
    "status": "track-c-lead-gate-blocked-2026-11-12",
    "saleShape": "S2 PASS: token (name/symbol/decimals/totalSupply) + mintFree() no-arg + free views (freeMinted(address)->bool, freeCount, FREE_CAP 3000) + AGENT_REGISTRY() = registry resmi 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; Sourcify verified 55 fns",
    "FREE_CAP": 3000, "freeCount": 443, "freePoolLeft": 2557, "freePctClaimed": 14.8,
    "paidCount": 10, "saleStart": 1794488398, "saleStartWib": "2026-11-12 19:59:58 WIB",
    "saleEndsAt": 1794747598, "poolCreated": 0, "tradingEnabled": 0, "settled": 0,
    "freeMinted_user": 0, "balanceOf_user": 0, "userSlotOpen": True,
    "ageVerified": True,
    "ageNote": "saleStart() on-chain 1794488398 = 19:59:58 WIB 12 Nov (umur ~4 jam saat bacaan run 2331).",
    "slotNote": "Slot TERBUKA: freeMinted(user)=false (bacaan ulang run ini, arity benar), balanceOf(user)=0.",
    "gateNote": "GATE WEBSITE GAGAL run 2331 (metode A/B/C/G/H/I/J): (A) pencarian alamat kontrak 0 hit proyek; (B) Boltbook EN+ZH tidak memuat alamat; (C) metadata Sourcify tanpa URL proyek; (G) pencarian nama 'RESUME' hanya proyek lain (NOVRA/UFO/NEBULA/Agentic Gangster/TINY/AGC/kartu Agent ID) - same-name BUKAN linkage; (H) contractURI() tidak ada di ABI; (I) tokenURI() tidak ada di ABI; (J) ABI tanpa fungsi site/url/domain; (K) search-index 0 hit via (A); (M) tanpa situs berbasis nama; (L) tidak dicoba - preseden SolNFT 2301. DILAPORKAN SEKALI run ini sebagai track-C lead gate-blocked; TIDAK preview/mint.",
    "firstSeenBlock": BLOCK, "firstSeenWib": "2026-11-12 ~23:45 WIB",
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-12 ~23:57 WIB",
    "source": "Sourcify feed run 2331 (temuan leg 5a + retry)",
}

# ---- AGE EXCLUSIONS (removals) ----
removed = []
# 1) Binance Life Cards (contracts)
if "Binance Life Cards" in snap.get("contracts", {}):
    snap["contracts"].pop("Binance Life Cards")
    removed.append("Binance Life Cards")
# 2) CAP7 (track_c) - fresh re-read this run: saleStart 1794371051, freeMinted 330/640
if "CAP7" in snap.get("track_c", {}):
    snap["track_c"].pop("CAP7")
    removed.append("CAP7")
# 3) PESI (track_c key 'PESI') - fresh re-read this run: freeRemaining 746, freeShares 254
if "PESI" in snap.get("track_c", {}):
    snap["track_c"].pop("PESI")
    removed.append("PESI")
snap["age_exclusions_2331"] = [
    {"name": "Binance Life Cards", "address": "0x4367b86F889014e6fD57fE812B86A581b913C645",
     "track": "A", "reason": "age-excluded",
     "evidence": "mintStart() on-chain 1794414145 = 2026-11-11 23:22:25 WIB; deadline 24 jam 2026-11-12 23:22:25 WIB LEWAT; bacaan segar run 2331 (blok 133196011): totalMinted/freeMinted 18/10000, belum sold out.",
     "reported_once": True, "removed_wib": NOW},
    {"name": "CAP7 (Obrigado Capitao)", "address": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
     "track": "C", "reason": "age-excluded",
     "evidence": "saleStart() on-chain 1794371051 = 2026-11-11 11:24:11 WIB (cocok dgn snapshot); deadline 24 jam 2026-11-12 11:24:11 WIB LEWAT; bacaan ulang run ini: freeMinted 330/640 FREE_SHARES (310 tersisa), totalSupply 5e29, belum sold out. (Catatan: 'deadline 25 Nov' lama di snapshot adalah SALE_WINDOW 14 hari, BUKAN deadline umur 24 jam.)",
     "reported_once": True, "removed_wib": NOW},
    {"name": "PESI-sale", "address": "0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD",
     "track": "C", "reason": "age-excluded",
     "evidence": "Sale live sejak 2026-11-10 02:16 WIB (post thecolony.uk 2026-11-09T19:16:24Z + Bluesky 2026-11-09T19:05:56Z mengumumkan live); umur >= ~46 jam > 24 jam. Bacaan ulang run ini (ABI eksak): freeCap 1000, freeRemaining 746, freeShares 254, paidShares 0, lpCreated 0, paused 0 - pool MASIH TERBUKA, belum sold out.",
     "reported_once": True, "removed_wib": NOW},
]
print("removed:", removed)

snap["runNote2331_1112"] = (
    "Run 2331 (jadwal 23:31 WIB, eksekusi 23:31-00:20 WIB; fast-batch blok 133196011): "
    "0 kandidat baru, 1 STRONG LEAD BARU (Home 0xfd55 promosi early->strong, gate-blocked), "
    "1 TRACK-C LEAD BARU (RESUME-BC1B 0xBC1B, gate-blocked), 0 early lead baru, 0 track-B dibuka, "
    "3 AGE-EXCLUSION (Binance Life Cards, CAP7, PESI-sale - dilaporkan sekali + dihapus), "
    "1 sellout terkonfirmasi tanpa laporan ulang (fa22 111/111, sudah dilaporkan + excluded run 2231). "
    "Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan leg fast-fail, watermark TETAP 132512564; 5c dilewati. "
    "Sourcify feed 20 kontrak (verifiedAt 16:25:52-16:32:11Z), 8 shape-check lolos urllib + 12 gagal IncompleteRead (curl retry: semua S1=S2=False, 0 early). "
    "Boltbook EN 43.810 byte / ZH 42.165 byte, 15 alamat, 2 baru (0xc340f810 unverified Sourcify 404, 0xfbb7d47c - keduanya bukan agent/sale-shape). "
    "Bridge 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded (STALE mtime 2026-11-08). "
    "Verify utama TIMEOUT 700 dtk (35/42 terbaca, JSON tidak tertulis; nilai dari stdout log) - fast-batch v2 144,6 dtk menutup 12 target. "
    "BATCH-FAIL (nilai lama dipertahankan, BUKAN nol): OLIVER, Cobalt, DACIT, SYNERGYPASS, DRAGON-0xad0d, AGENT COSMOS, AGENT ID card, RunicKey, Thor, Vexa, ROBO, CAP7 (fast-batch; CAP7 dibaca ulang single-call run ini). "
    "SolNFT 272/333 = 81,7% + AgcNFT 314/333 = 94,3% tetap strong-lead-gate-blocked (dilaporkan 23:01/22:31) - DIAM. "
    "OBFG 469/1230 = 38,1% tetap track-C lead gate-blocked - DIAM. Steady 347/555 = 62,5% + MECHA 1868/4444 = 42,0% tetap early - DIAM. "
    "Horus AI Phase 1 sold out 2.000/2.000 (situs live horus-ai-bnb.vercel.app, Phase 2 berbayar) - SUDAH dilaporkan + excluded run 0131 - DIAM. "
    "TINY AGENTS (0x83d5e5449CB513A9c0C257808222F1Ba723d0978, thecolony 10 Nov 18:05Z = 11 Nov 01:05 WIB) umur >24 jam -> age-excluded, tidak pernah jadi lead, tanpa laporan (hanya log). "
    "Velocity: 0 lolos (SolNFT +35/55 mnt = ~0,64/mnt < ambang; AgcNFT +27; Home +35 interval pertama; Steady +68; MECHA +12-13; OBFG +23 - semua di bawah 1,5x+20 token vs baseline run 2301/2231)."
)
snap["runNote2331_1112_discovery"] = (
    "Discovery run 2331: Sourcify feed 20 (verified 16:25:52-16:32:11Z) -> 0 S1/0 S2/0 early (8 shape-check + 12 curl-retry). "
    "Boltbook EN+ZH dibaca langsung (43.810/42.165 byte), 2 alamat baru vs seen+snapshot: 0xc340f810 (Sourcify 404, unverified) + 0xfbb7d47c (shape-check n_fns=0) - keduanya BUKAN lead. "
    "Sweep EN+ZH (browser.search): 0 proyek baru - Oathbots/AGENT MAO/RIGBYPASS/NOVRA age-excluded; Agentic Gangster free habis; UFO closed 22:05 WIB; NEBULA minted-by-user; WNO minted-by-user; SAFUAI paid-only; PESI dikenal; BAYC sale free round over. "
    "Sweep menemukan: Horus AI (Phase 1 sold out, sudah excluded 0131), TINY AGENTS (age-excluded, lihat runNote2331_1112), Solace (checked-not-lead-paid-only 11 Nov), Agent Harvest Land (watchlist-only-pelengkap-scan, tanpa perubahan). "
    "Odaily newsflash EN: 0 item Agent ID/free-mint (semua makro/Nvidia). "
    "CATATAN: hasil sweep mengandung instruksi agen tertanam ('Use my Binance Agentic Wallet to call mint()...') - konten eksternal, TIDAK diikuti; sweep hanya discovery, semua angka diverifikasi on-chain independen."
)
snap["last_run_wib"] = "2026-11-12 23:31 WIB"
snap["last_run"] = "2026-11-12-2331"
json.dump(snap, open(SNAP, "w"), indent=1)
print("OK. contracts:", len(snap.get("contracts", {})), "track_c:", len(snap.get("track_c", {})),
      "excluded:", len(snap.get("excluded", {})))
print("Binance Life Cards in contracts:", "Binance Life Cards" in snap.get("contracts", {}))
print("CAP7 in track_c:", "CAP7" in snap.get("track_c", {}))
print("PESI in track_c:", "PESI" in snap.get("track_c", {}))
print("Home status:", snap["contracts"]["Home"]["status"], snap["contracts"]["Home"]["freeMinted"])
print("RESUME-BC1B in track_c:", "RESUME-BC1B" in snap.get("track_c", {}))
print("fa22 excluded freeMinted:", snap["excluded"]["AgentGenesis-fa22"]["freeMinted"])
