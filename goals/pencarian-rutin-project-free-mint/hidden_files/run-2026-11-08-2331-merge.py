#!/usr/bin/env python3
"""Parent merge run 2331 part 1 — re-read velocity/supply, age exclusions, Lucky Cat early lead,
DANGEROUS flags, track_c updates. NO FF/VV gate conclusion (awaits browser L + VV sweep).
Writes backup onchain-snapshot.json.bak-2331-premerge first. No execution."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
NOW_WIB = "2026-11-09 00:30 WIB"
HEAD_REREAD = 132428482
LAST_READ_WIB = "2026-11-08 23:57 WIB"
INTERVAL_MIN = 36.95

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-2331-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = s["contracts"]
TC = s.get("track_c", {})
rr = json.load(open(f"{BASE}/run-2026-11-08-2331-reread.json"))
R = rr.get("reread", {})
RTC = rr.get("track_c", {})

def upd(name, note, **kw):
    e = C.get(name)
    if e is None:
        print(f"WARN {name} NOT IN SNAPSHOT, skipped")
        return
    for k, v in kw.items():
        if v is not None:
            e[k] = v
    e["runNote2331_1108"] = note
    e["lastReadBlock"] = HEAD_REREAD
    e["lastReadWib"] = LAST_READ_WIB

def velocity(name):
    """Update velocity fields from fresh totalSupply vs snapshot previousTotalSupply."""
    e = C.get(name)
    r = R.get(name)
    if not e or not r:
        return None
    prev = e.get("totalSupply")
    new = r.get("totalSupply")
    if prev is None or new is None:
        return None
    minted = new - prev
    rate = minted / INTERVAL_MIN
    prev_rate = e.get("currentRatePerMin")
    if prev_rate is None:
        prev_rate = e.get("previousRatePerMin") or 0
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(minted >= 20 and ratio is not None and ratio >= 1.5)
    e["previousTotalSupply"] = prev
    e["totalSupply"] = new
    e["mintedInInterval"] = minted
    e["intervalMinutes"] = INTERVAL_MIN
    e["currentRatePerMin"] = round(rate, 4)
    e["previousRatePerMin"] = prev_rate
    e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
    e["velocityLegPasses"] = passes
    return (minted, round(rate, 4), prev_rate, round(ratio, 2) if ratio is not None else None, passes)

# --- velocity + supply refresh for ALL contracts with fresh totalSupply ---
vel_pass = []
for name in list(C.keys()):
    res = velocity(name)
    if res and res[4]:
        vel_pass.append((name,) + res)
    # refresh free views where fresh (never overwrite with None)
    r = R.get(name)
    if r:
        e = C[name]
        for f in ("freeClaimed", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user"):
            if r.get(f) is not None:
                e[f if f != "balanceOf_user" else "balanceOf_user"] = r[f]
        if r.get("totalMinted") is not None:
            e["totalMinted"] = r["totalMinted"]
print(f"velocity pass (strict): {len(vel_pass)}")
for v in vel_pass:
    print("  VEL-PASS", v)

# --- focus updates ---
upd("HIVE Agents",
    "Run 2331: totalSupply flat 1256, balanceOf(user)=1, status minted-by-user - tanpa perubahan; velocity GAGAL (0 token).",
    totalSupply=1256, balanceOf_user=1)
upd("Bubblebruin",
    "Run 2331: totalSupply 2123->2143 (+20, 0.5413/mnt, 7.00x vs prev - velocity LOLOS) TAPI TIDAK promosi: free 2137/7777=27.5% (<50%), X unverified, status minted-by-user-2026-11-01.",
    totalSupply=2143, freeClaimed=2137)
upd("Zapcourier",
    "Run 2331: totalSupply flat 715, freeClaimed 712/712=100% (free pool habis), balanceOf(user)=1, minted-by-user - tanpa perubahan.",
    totalSupply=715, freeClaimed=712)
upd("Cryonyx",
    "Run 2331: totalSupply 500->501 (+1), freeClaimed 500/809=61.8%, balanceOf(user)=1, minted-by-user - tanpa perubahan.",
    totalSupply=501, freeClaimed=500)
upd("Cathodex",
    "Run 2331: totalSupply flat 765, freeClaimed 763/763=100% (free pool habis), balanceOf(user)=1, minted-by-user - tanpa perubahan.",
    totalSupply=765, freeClaimed=763)
upd("Kirinova",
    "Run 2331: totalSupply flat 716, freeClaimed 711/711=100% (free pool habis), balanceOf(user)=1, minted-by-user - tanpa perubahan.",
    totalSupply=716, freeClaimed=711)
upd("Gourdwick",
    "Run 2331: totalSupply 491->493 (+2), freeClaimed 493/868=56.8%, balanceOf(user)=0, status promotion-discarded-same-owner - tanpa perubahan.",
    totalSupply=493, freeClaimed=493)
upd("Lensorb",
    "Run 2331: totalSupply flat 778, freeClaimed 776/776=100% (free pool habis), balanceOf(user)=1, minted-by-user - tanpa perubahan.",
    totalSupply=778, freeClaimed=776)
upd("Vesperfang",
    "Run 2331: FREE POOL SOLD OUT 752->773/773=100% (totalSupply 766->787, +21, velocity LOLOS 5.25x TAPI TIDAK promosi - status promotion-discarded-same-owner). Mint(1) value-0 sim DIVERIFIKASI run ini REVERT custom error 0x788a686f walau mintOpen()=1 (cocok klaim Boltbook follow-up PIrQtWN6Iw3c) - lane efektif TUTUP. Dicatat saja (sudah discarded, bukan lead) - TIDAK dilaporkan sebagai sellout lead.",
    totalSupply=787, freeClaimed=773)
upd("SHACHO CLUB",
    "Run 2331: totalSupply 187->296 (+109), MAX_SUPPLY 1888, mintOpen 1, balanceOf(user)=0. FLAG DANGEROUS (Boltbook ZH HuXZrBg_8-Hu, blok 132428215): owner 0x11038f4aa771d9d48b8ac7a184e37a8e5324a9dd keluarga 0x1103 (ORBIT PASS, SPACE ROT, ALL ACCESS, THE KEY, GOLDEN TICKET), lane ke-21 keluarga itu; owner-only withdraw/setMintOpen/setRoyalty. Status tetap promotion-discarded-same-owner-2026-11-08; JANGAN mint walau free lane kelihatan buka.",
    totalSupply=296, MAX_SUPPLY=1888)
upd("Saturnode",
    "Run 2331: totalSupply 3751->3787 (+36, velocity LOLOS 10.5x TAPI TIDAK promosi), freeClaimed 3755/4000=93.9%, mintOpen 1, balanceOf(user)=0. FLAG DANGEROUS (Boltbook ZH HuXZrBg_8-Hu, blok 132428215): owner 0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d keluarga 0x6f24 (Mechfarm, Photonode, Saturnagent, Hivebyte, Wuyuhive). Status tetap watchlist-only-pelengkap-scan; X unverified + gate belum terverifikasi + flag ini = TIDAK promosi.",
    totalSupply=3787, freeClaimed=3755)
upd("Pokechain",
    "Run 2331: totalMinted 11359->12478 (+1119), MAX 15555, balanceOf(user)=1. Gate tetap terverifikasi (2301). Bukan kandidat baru.",
    totalMinted=12478, balanceOf_user=1)
upd("GLOOP",
    "Run 2331: totalMinted 2563->2701 (+138), balanceOf(user)=1. Gate tetap terverifikasi. Bukan kandidat baru.",
    totalMinted=2701, balanceOf_user=1)
upd("HELIX",
    "Run 2331: totalSupply/totalMinted 392->404 (+12), balanceOf(user)=0; gate tetap GAGAL.",
    totalSupply=404, totalMinted=404)
upd("BAHUANG2",
    "Run 2331: totalMinted 1086->1108 (+22), freeMinted 1086->1104; slot user OPEN; gate tetap GAGAL. Tetap strong-lead gate-blocked.",
    totalMinted=1108, freeMinted=1104)
upd("Jinchan",
    "Run 2331: totalMinted 838, FREE_SUPPLY 777, balanceOf(user)=1; status sold-out-free-2026-11-08 tetap (Boltbook: free lane CLOSED - konsisten).",
    totalMinted=838, balanceOf_user=1)
upd("Aura Agents",
    "Run 2331: totalSupply 4731 (+21 interval, velocity LOLOS) TAPI TIDAK promosi: free% UNVERIFIED (freeClaimed None), X unverified, status watchlist-only-not-early-2026-11-03.",
    totalSupply=4731)
upd("Hackagent",
    "Run 2331: totalSupply 4479->4515 (+36, velocity LOLOS) TAPI TIDAK promosi: status promotion-discarded-same-owner-2026-11-03.",
    totalSupply=4515)
upd("Lambdwyn",
    "Run 2331: totalSupply 660 (+20 interval, velocity LOLOS) TAPI TIDAK promosi: free 655/1624=40.3% (<50%), X unverified, status watchlist-only-scan-2026-11-03.",
    totalSupply=660, freeClaimed=655)
upd("Hourglas",
    "Run 2331: totalSupply 3013->3039 (+26, velocity LOLOS) TAPI TIDAK promosi: free 3034/7000=43.3% (<50%), X unverified, status early-lead-reported-2026-11-08.",
    totalSupply=3039, freeClaimed=3034)
upd("Alchemister",
    "Run 2331: totalSupply 3076->3130 (+54, velocity LOLOS) TAPI TIDAK promosi: free% UNVERIFIED (freeClaimed None), X unverified, status early-lead.",
    totalSupply=3130)

# --- age exclusions (verified launch >48h, not sold out) ---
AGE = [
    {"name": "AgentBox", "address": "0x08393dad165d90e7258501fE1dfb5F3498644011",
     "firstMintWib": "2026-11-05 12:47:33 WIB", "ageHours": 83.2,
     "evidence": "First open TERVERIFIKASI on-chain: first BoxOpened/FreeBoxOpened blok 131766040 = 2026-11-05 12:47:33 WIB; saleState() 12:47:28 WIB (launchNote). Reads run ini DEGRADED (semua view None) - tidak ada bukti sellout.",
     "status_before": "early-lead-reported-2026-11-05", "removed_run": "2026-11-08 run 2331",
     "reason": "Umur peluncuran terverifikasi 83,2 jam (>48 jam) dan belum sold out (tidak ada bukti sellout); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."},
    {"name": "Data Synth", "address": "0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642",
     "firstMintWib": "2026-11-06 08:11:04 WIB", "ageHours": 63.8,
     "evidence": "First mint VERIFIED on-chain: first Transfer-from-zero blok 131918469 = 2026-11-06 08:11:04 WIB (launchNote). Fresh read run ini: totalMinted()=1, totalSupply()=3333 (MAX 3333) - hanya 1 mint tercatat, TIDAK sold out.",
     "status_before": "early-lead-reported-2026-11-06", "removed_run": "2026-11-08 run 2331",
     "reason": "Umur peluncuran terverifikasi 63,8 jam (>48 jam) dan belum sold out (totalMinted 1/3333); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."},
    {"name": "Zero Genesis", "address": "0x7807202FBE09f4AAC9ac312ed593ba16806F6b34",
     "firstMintWib": "2026-11-06 ~08:16 WIB", "ageHours": 63.7,
     "evidence": "First mint VERIFIED on-chain: first Transfer-from-zero blok 131919173 = ~2026-11-06 08:16 WIB (launchNote). Fresh read run ini: totalMinted()=1 - hanya 1 mint tercatat, TIDAK sold out.",
     "status_before": "early-lead-reported-2026-11-06", "removed_run": "2026-11-08 run 2331",
     "reason": "Umur peluncuran terverifikasi 63,7 jam (>48 jam) dan belum sold out (totalMinted 1/3333); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."},
    {"name": "Cipher Mind", "address": "0x3226B724d9F81c4E09E6E07b75532e01e6f5c7B7",
     "firstMintWib": "2026-11-06 09:14:06 WIB", "ageHours": 62.7,
     "evidence": "First mint VERIFIED on-chain: first Transfer-from-zero blok 131926871 = 2026-11-06 09:14:06 WIB (launchNote). Fresh read run ini: totalMinted()=1 - hanya 1 mint tercatat, TIDAK sold out.",
     "status_before": "early-lead-reported-2026-11-06", "removed_run": "2026-11-08 run 2331",
     "reason": "Umur peluncuran terverifikasi 62,7 jam (>48 jam) dan belum sold out (totalMinted 1/3333); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."},
    {"name": "Cyber Lynx Agent", "address": "0x5189EAEB67d2A799CD9094AEc4Af6eb76C6E073b",
     "firstMintWib": "2026-11-06 09:19:19 WIB", "ageHours": 62.6,
     "evidence": "First mint VERIFIED on-chain: first Transfer-from-zero blok 131927568 = 2026-11-06 09:19:19 WIB (launchNote). Fresh read run ini: totalMinted()=1 - hanya 1 mint tercatat, TIDAK sold out.",
     "status_before": "early-lead-reported-2026-11-06", "removed_run": "2026-11-08 run 2331",
     "reason": "Umur peluncuran terverifikasi 62,6 jam (>48 jam) dan belum sold out (totalMinted 1/3333); dihapus dari watchlist aktif per aturan umur 48 jam; dilaporkan sekali run ini."},
]
for a in AGE:
    if a["name"] in C:
        del C[a["name"]]
        print(f"AGE-EXCLUDED + removed: {a['name']} ({a['ageHours']}h)")
    else:
        print(f"AGE-EXCLUDED already gone: {a['name']}")
s.setdefault("age_exclusions", []).extend(AGE)

# --- new entries ---
C["Lucky Cat"] = {
    "address": "0xB3AC4612E609fce2B98c2f6602D5EFCeeB61C473",
    "status": "early-lead-reported-2026-11-08-2331",
    "name": "Lucky Cat", "symbol": "LUCKY", "kind": "ERC721",
    "totalSupply": 5, "totalMinted": 5, "freeMinted": 5, "FREE_POOL": 2000,
    "freeRemaining": 1995, "FREE_PER_WALLET": 5, "MAX_SUPPLY": 10000,
    "freePctVerified": 0.25, "mintOpen": 1,
    "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
    "userSlotNote": "Slot OPEN: freeMintCount(user)=0 dari FREE_PER_WALLET=5 (baca segar run 2331). quote(user,1)=186336038470553 wei (~0,000186 BNB) adalah harga tier BERBAYAR, bukan harga free - jalur free belum di-preview (early lead TIDAK PERNAH di-preview).",
    "firstSeenBlock": 132428001, "firstMintWib": "2026-11-08 23:53:58 WIB",
    "scanWindow": "132427550-132428549",
    "scanMints": 5, "scanMinters": 1,
    "lastReadBlock": HEAD_REREAD, "lastReadWib": LAST_READ_WIB,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint VERIFIED on-chain: 5 mints, 1 minter (owner 0xb07b263ffb129575142537fa307f24e6a435f78a) di blok 132428001 = 2026-11-08 23:53:58 WIB (scan route-4 window 132427550-132428549 + fast_rpc block timestamp). Umur ~16 menit saat baca - TERVERIFIKASI <=48 jam.",
    "baselineNote": "EARLY lead dilaporkan sekali run 2331. Never auto-minted/previewed. Agent-shape VERIFIED: gate() = registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (baca on-chain segar), Sourcify exact_match, free views (FREE_PER_WALLET/FREE_POOL/freeMintCount/freeMinted/freeOf/freeRemaining) + mint/quote/forge/tierPrice. Free 5/2000=0,25% (<25% strong leg); X UNVERIFIED (tidak ada diskusi ditemukan); velocity belum terhitung (baseline pertama). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety.",
    "gateNote": "Website gate BELUM dicek (early lead - gate hanya relevan saat promosi ke strong lead).",
    "runNote2331_1108": "Run 2331: EARLY lead BARU (first-seen scan, satu-satunya first-seen dari 66 NFT ter-enrich; 31 NFT window tidak ter-enrich - gap cakupan). Dilaporkan sekali run ini.",
}
C["BNBirds"] = {
    "address": "0x5d6967fe8400c4504c5035e1fb834967da7efbde",
    "status": "checked-not-lead-2026-11-08-2331",
    "name": "BNBirds", "symbol": "BIRDS", "kind": "ERC721",
    "totalSupply": 994, "FREE_SUPPLY": 1000, "MAX_SUPPLY": 1111, "mintOpen": None,
    "userBalance": 0,
    "firstSeenNote": "Boltbook follow-up PIrQtWN6Iw3c (~23:47 WIB): totalSupply 994 (+1 sejak #993 radar zhi19 ~23:10 WIB), mint(1) sim passes, Sourcify-UNVERIFIED.",
    "baselineNote": "Dicek run 2331 (triage Boltbook): Sourcify unverified -> agent-shape UNKNOWN; free hampir habis (994/1000 = 99,4% bila totalSupply = free); slot user tidak bisa diverifikasi (free views None). BUKAN lead, tidak dilaporkan sebagai lead, tidak di-preview/di-mint.",
    "lastReadBlock": HEAD_REREAD, "lastReadWib": LAST_READ_WIB,
    "runNote2331_1108": "Run 2331: dicek (Boltbook) - unverified + free hampir habis; bukan lead.",
}
C["MiChan"] = {
    "address": "0x669cb75f51b5d23f4b42fc1522b653d7b88e608d",
    "status": "checked-not-lead-2026-11-08-2331",
    "name": "MiChan", "symbol": "MICHAN", "kind": "ERC721",
    "totalSupply": 298, "totalMinted": 298, "freeMinted": 296, "MAX_SUPPLY": 2222, "mintOpen": 1,
    "userBalance": 0,
    "firstSeenNote": "Boltbook ZH HuXZrBg_8-Hu (blok 132428215).",
    "baselineNote": "Dicek run 2331 (triage Boltbook): Sourcify unverified -> agent-shape UNKNOWN; freeMinted 296 (tanpa FREE cap - % tidak bisa dihitung). FLAG DANGEROUS (Boltbook): owner 0x36f3d56ead5d1d6c2434f94defcef732c5c3cbd2 farm 0x36f3, owner bisa ubah aturan mint kapan saja. BUKAN lead, tidak dilaporkan sebagai lead, tidak di-preview/di-mint; JANGAN mint.",
    "lastReadBlock": HEAD_REREAD, "lastReadWib": LAST_READ_WIB,
    "runNote2331_1108": "Run 2331: dicek (Boltbook) - unverified + flag DANGEROUS; bukan lead.",
}
C["OPEC"] = {
    "address": "0x88311E8fA4ab792CA72acaf6f8AD4B391cc56713",
    "status": "checked-not-agent-shaped-2026-11-08-2331",
    "name": "Open Crossing", "symbol": "OPEC", "kind": "ERC20",
    "totalSupply": 1000000000000000000000000000, "userBalance": 0,
    "firstSeenNote": "Boltbook EN ddTaqUv8XbQs (post 23:5x WIB): 5.000 spots, 200.000 OPEC/spot, mint(20)=4 jt OPEC, 0 BNB; deploy 2026-11-07 22:05:53 UTC; 456/5000 spots (9,12%) di blok 132425154.",
    "baselineNote": "Dicek run 2331 (triage Boltbook): NOT-AGENT-SHAPED - mint terbuka TANPA syarat Agent ID (post sendiri: 'No whitelist, signature, approval, deposit, or Agent ID is required'; AgentDetected hanya event informasional); tanpa free views; tanpa website/X/pair (post sendiri: 'No verifiable official website, X account... No OPEC/WBNB or OPEC/USDT pool'). BUKAN track A (bukan NFT), BUKAN track C (tidak agent-gated, tidak ada free-share view). BUKAN lead, tidak dilaporkan sebagai lead, tidak di-preview/di-mint.",
    "lastReadBlock": HEAD_REREAD, "lastReadWib": LAST_READ_WIB,
    "runNote2331_1108": "Run 2331: dicek (Boltbook) - bukan agent-gated + tanpa website; bukan lead.",
}

# --- track_c updates ---
def tc_upd(name, note, **kw):
    e = TC.get(name)
    if e is None:
        print(f"WARN track_c {name} NOT IN SNAPSHOT, skipped")
        return
    for k, v in kw.items():
        if v is not None:
            e[k] = v
    e["runNote2331_1108"] = note
    e["lastReadBlock"] = HEAD_REREAD
    e["lastReadWib"] = LAST_READ_WIB

tc_upd("NUSA", "Run 2331: freeMinted 236->240; tradingOpen tidak dicek ulang run ini (nilai 0 dari 2301 dipertahankan). Tetap track-c lead gate-blocked.", freeMinted=240)
tc_upd("Crack", "Run 2331: totalSupply 3866->3871; minted-by-user.", totalSupply=3871)
tc_upd("NOVRA", "Run 2331: totalSupply token 73 jt -> 74 jt NOVRA (shares 73->74); status tetap track-c-free-pool-exhausted-2026-11-08 (free pool sudah habis, sudah dilaporkan).", totalSupply=74000000000000000000000000)
if "ORBITA" in TC:
    TC["ORBITA"]["runNote2331_1108"] = ("Run 2331: Boltbook klaim 'ORBITA sold out' (post 23:50 WIB) TIDAK bisa diverifikasi dari baca segar (freeMinted=None, totalSupply token tidak berubah 1e27, balanceOf_user 1e24 = 1 jt token); status tetap minted-by-user-2026-11-07; tanpa perubahan, tanpa laporan.")
    TC["ORBITA"]["lastReadBlock"] = HEAD_REREAD
    TC["ORBITA"]["lastReadWib"] = LAST_READ_WIB

# --- scan-seen append (Lucky Cat only; first-seen correct dedupe) ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
if isinstance(seen.get("contracts"), dict):
    seen["contracts"]["0xB3AC4612E609fce2B98c2f6602D5EFCeeB61C473"] = {
        "first_seen_block": 132428001, "first_seen_wib": "2026-11-08 23:53:58 WIB",
        "source": "run-2331-scan", "note": "Lucky Cat (LUCKY) early lead reported run 2331"}
else:
    seen["0xB3AC4612E609fce2B98c2f6602D5EFCeeB61C473"] = {
        "first_seen_block": 132428001, "first_seen_wib": "2026-11-08 23:53:58 WIB",
        "source": "run-2331-scan", "note": "Lucky Cat (LUCKY) early lead reported run 2331"}
with open(f"{BASE}/onchain-scan-seen.json", "w") as f:
    json.dump(seen, f, indent=1)
print("seen appended: Lucky Cat")

# --- scan-state note (watermark NOT advanced) ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["runNote2331_1108_scan"] = ("Run 2331 scan PARTIAL: pre-flight OK 12,9 dtk (head 132428439, 194 logs/50 blok). "
    "Window 132427550-132428549 (1000 blok, cap), log collection lengkap 20/20 chunk, 40 Ankr calls, 0 error; "
    "enrichment terhenti di 67/97 oleh timeout 700 dtk (SCAN_EXIT=124). Partial JSON terselamatkan: 66 NFT + 273 ERC-20-mint. "
    "First-seen (dedupe benar): 1 - Lucky Cat. 31 NFT window TIDAK ter-enrich - gap cakupan. "
    "Watermark TIDAK dimajukan (tetap 132422005, milik backfill); skipped gap 132422006-132427549.")
st["runNote2331_1108"] = "Run 2331 scan partial (67/97 enriched); watermark NOT advanced."
with open(f"{BASE}/onchain-scan-state.json", "w") as f:
    json.dump(st, f, indent=1)

# --- top-level run notes ---
s["last_run_wib"] = "2026-11-08 23:31 WIB"
s["last_run"] = "2331"
s["runNote2331_1108"] = ("Run 2331 (23:31-00:xx WIB): re-read blok 132428482 (542 kontrak + 72 track_c, 0 batch_fail, 122 degraded - naik dari 40 di 2301, RPC degradasi); "
    "scan window 132427550-132428549 PARTIAL (pre-flight OK 12,9 dtk; 40 Ankr calls, 0 error; enrichment killed 700s timeout di 67/97, partial=true, 66 NFT + 273 ERC-20; 31 NFT window TIDAK ter-enrich - gap cakupan). "
    "Watermark TIDAK dimajukan (milik backfill; skipped gap 132422006-132427549). 5c: 10 baru dicek, 0 hit S1/S2 (semua Sourcify-unverified). "
    "Velocity strict: 22 lolos, 0 promosi. EARLY LEAD BARU: Lucky Cat (gate()=registry, free 5/2000, first mint 23:53:58 WIB) - dilaporkan sekali. "
    "Strong leads FF/VV: gate (L) BscScan masih menunggu hasil browser + VV first-mint sweep berjalan - diputuskan di merge part 2. "
    "Age-exclusion: 5 dihapus (AgentBox 83,2j; Data Synth 63,8j; Zero Genesis 63,7j; Cipher Mind 62,7j; Cyber Lynx 62,6j) - dilaporkan sekali. "
    "Vesperfang free pool SOLD OUT 773/773 + mint revert 0x788a686f terverifikasi (dicatat, bukan lead). "
    "Binanceai tetap refund phase. Bridge: 116 kontrak, 0 baru.")
s["runNote2331_1108_scan"] = ("Scan run 2331 PARTIAL: pre-flight OK 12,9 dtk (head 132428439, 194 logs/50 blok). Window 132427550-132428549 (1000 blok, cap), "
    "log collection lengkap 20/20 chunk, 40 Ankr calls, 0 error; enrichment terhenti di 67/97 oleh timeout 700 dtk (SCAN_EXIT=124). "
    "Partial JSON terselamatkan: 66 NFT + 273 ERC-20-mint. First-seen di antara 66 yang ter-enrich: 1 (Lucky Cat). "
    "31 NFT window tidak ter-enrich (alamat tidak tercatat di log) - gap cakupan. Watermark tidak dimajukan.")
s["runNote2331_1108_binanceai"] = ("Run 2331: binanceai tetap refund phase (launched=0, failed=1, isRefundPhase=1, totalShares 3110, "
    "tokenClaimed(user)=0, saldo TOKEN user 0); tanpa perubahan, sudah dilaporkan sekali.")
s["runNote2331_1108_web"] = ("Run 2331 web: Boltbook EN+ZH 3 temuan baru - (1) OPEC (bukan agent-gated, tanpa website - dicatat, bukan lead); "
    "(2) FrankensteinFriends + VampireVibes (SALE-S1, free ~99%/98%, slot terbuka, umur ~1 jam - strong lead, gate (L) pending); "
    "(3) flag DANGEROUS SHACHO/Saturnode/MiChan (owner keluarga rug lama) - dicatat. Sweep EN+ZH: 0 situs proyek baru yang kandidat "
    "(AgentForge/Pixel Fox umur >48 jam). Route 6: 0 temuan. Sourcify feed 20 item: 5 baru dicek run ini (4 NOT-AGENT-SHAPED, 1 MINT-SHAPE Lucky Cat); "
    "5 lainnya sudah dicek hot-leg 23:44 (not-sale-shape); Wisp Sourcify masih 404 (ke-6).")
s["runNote2331_1108_triage_new"] = ("Triase parent: FrankensteinFriends 0xedfd9e65 (totalSupply 718, free 689/696=99,0%, slot user TERBUKA, AGENT gate=registry via ABI; "
    "first mint blok 132421120 = 2026-11-08 23:02:21 WIB, jendela awal [132411334,132420333] belum terverifikasi - dataseed -32005); "
    "VampireVibes 0xa5fb4e0e (totalSupply 687, free 659/675=97,6%, slot user TERBUKA; first mint sweep berjalan, first so far blok 132422915); "
    "keduanya satu owner 0x90e8b1c93c80758e2bd5032c7acec382501cb84b (factory wave); gate website (A)(C)(G)(H)(I)(J)(K) tanpa hasil; (L) BscScan menunggu browser. "
    "BNBirds (unverified, free ~99,4% habis) + MiChan (unverified, flag DANGEROUS) dicatat bukan lead. OPEC dicatat bukan agent-shaped.")

with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(s, f, indent=1)
print("snapshot saved; contracts now:", len(s["contracts"]))
print("DONE merge part 1")
