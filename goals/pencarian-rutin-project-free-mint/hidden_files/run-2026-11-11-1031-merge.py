#!/usr/bin/env python3
"""Merge run 1031 (scheduled 2026-11-11 10:31 WIB) results into onchain-snapshot.json.
Writes snapshot (with .bak). Inputs: run-2026-11-11-1031-reread.json (block
132897068, 59 contracts + 22 track_c), run-2026-11-11-1031-probe.json (Fira /
Baby Neiro / binanceai, block 132897411), run-2026-11-11-1031-probe-58a7.json
(Bot Fighters, block 132897699), run-2026-11-11-1031-probe-58a7-gate.json
(owner/getLogs/discards), run-2026-11-11-1031-probe-abyss-rose.json (block
132898484), run-2026-11-11-1031-feed-shape.json (18 ABIs: S1=1 BOTF)."""
import json, shutil, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1031-reread.json"))
probe = json.load(open(BASE + "run-2026-11-11-1031-probe.json"))
probe58 = json.load(open(BASE + "run-2026-11-11-1031-probe-58a7.json"))
gate58 = json.load(open(BASE + "run-2026-11-11-1031-probe-58a7-gate.json"))
probar = json.load(open(BASE + "run-2026-11-11-1031-probe-abyss-rose.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1031-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 10:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict):
        return None
    old = e.get("totalSupply")
    if old is None or new_supply is None:
        return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = None
    if prev_rate and prev_rate > 0:
        ratio = round(rate / prev_rate, 2)
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

# --- 1. reread updates (generic) ---
for name, d in reread["reread"].items():
    if name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        e["runNote1031"] = ("Run 1031 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        old = e.get("totalSupply")
        if old is None:
            e["totalSupply"] = ns
            e["lastReadBlock"] = BLOCK
            e["lastReadWib"] = TS
            e["runNote1031"] = ("Run 1031 (blok %s): totalSupply pertama terbaca %s (sebelumnya None) - "
                                "baseline dicatat, velocity belum lulus; freeMinted=%s; bal_user=%s; status %s."
                                % (BLOCK, ns, d.get("freeMinted"), d.get("balanceOf_user"), e.get("status")))
        else:
            r = vel(name, ns)
            diff, rate, ratio = r if r else (None, None, None)
            e["runNote1031"] = ("Run 1031 (blok %s): totalSupply %s->%s (+%s, %s/mnt vs prev %s = %sx) -> velocity %s; "
                                "bal_user=%s; freeMinted=%s; status %s."
                                % (BLOCK, e.get("previousTotalSupply"), ns, diff, rate,
                                   e.get("previousRatePerMin"), ratio,
                                   "LOLOS" if e.get("velocityLegPasses") else "GAGAL",
                                   d.get("balanceOf_user"), d.get("freeMinted"), e.get("status")))
    if d.get("freeClaimed") is not None:
        e["freeClaimed"] = d["freeClaimed"]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None:
        e["MAX_SUPPLY"] = d["MAX_SUPPLY"]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS

# --- 2. Stampooor: 494->534 (+40), velocity GAGAL (1.33/mnt vs prev 1.90 = 0.70x) ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": 534, "freeMinted": 534, "totalSupply": 534,
               "freeAvailable_user": 1, "lastReadBlock": BLOCK, "lastReadWib": TS})
    st["runNote1031"] = ("Run 1031: freeMinted 494->534 (+40, 1,33/mnt vs prev 1,90 = 0,70x) -> velocity GAGAL. "
        "Free 534/1200 = 44,5% (<50% kandidat, <70% strong lead). Slot user TERBUKA (balanceOf 0). "
        "Umur TERVERIFIKASI <24 jam (mintStart 11 Nov ~09:00 WIB). X + website UNVERIFIED. Tetap EARLY. "
        "TIDAK di-preview/di-mint.")

# --- 3. Jade Vault 0x7Eb9: 335->374 (+39) velocity LOLOS (1.30/mnt vs prev 0.50 = 2.60x) ---
jv = C.get("0x7Eb9")
if isinstance(jv, dict):
    jv.update({"totalMinted": 374, "totalSupply": 374, "lastReadBlock": BLOCK, "lastReadWib": TS})
    jv["runNote1031"] = ("Run 1031: totalMinted 335->374 (+39, 1,30/mnt vs prev 0,50 = 2,60x) -> velocity LOLOS. "
        "TAPI tetap EARLY: free% UNVERIFIED (template tanpa free counter - % total supply 374/8888 TIDAK "
        "disubstitusi), umur + website + X UNVERIFIED, quote(user,1)=0 dari run 0931. TIDAK di-preview/di-mint. "
        "Perubahan kaki velocity dicatat di run log saja, bukan laporan chat (bukan promosi).")

# --- 4. NIGHTFORGE: 740 flat, velocity GAGAL; ~36,9% ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    nf.update({"totalSupply": 740, "freePctVerified": 36.9,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    nf["runNote1031"] = ("Run 1031: totalSupply 740 flat vs run 1001 (740, +0) -> velocity GAGAL; "
        "agentFreeUsed ~737/2000 = 36,9% (jauh di bawah ambang strong lead >70%). Slot terbuka (balanceOf 0). "
        "Deadline umur 14:37 WIB 11 Nov belum lewat. Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 5. AgentPals: 75->76 (+1), 76/300 = 25,3% ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap.update({"totalSupply": 76, "freeMinted": 76, "totalMinted": 76,
               "status": "watchlist-only-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    ap["runNote1031"] = ("Run 1031: totalSupply 75->76 (+1) - baseline kedua. Free phase LIVE sejak 11 Nov 06:33:57 WIB; "
        "76/300 = 25,3% (<50% kandidat, <70% strong lead). Slot user terbuka (balanceOf 0). Website UNVERIFIED. "
        "Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 6. BYTEBLOOM velocity GAGAL run ini (762, +6) tapi minted-by-user: tanpa promosi ---
bb = C.get("BYTEBLOOM")
if isinstance(bb, dict):
    bb["runNote1031"] = ("Run 1031: totalSupply 756->762 (+6, 0,20/mnt vs prev 1,00 = 0,20x) -> velocity GAGAL; "
        "status minted-by-user-2026-11-10 - TIDAK ada promosi/aksi (sudah dimiliki user).")

# --- 7. Fira Agent: 4900 flat ---
fa = C.get("Fira Agent")
if isinstance(fa, dict):
    fa.update({"totalSupply": 4900, "lastReadBlock": probe.get("block"), "lastReadWib": TS})
    fa["runNote1031"] = ("Run 1031 (blok %s): totalSupply 4900 flat vs run 1001 (4900/5000). Free%% 98,0%% INFERENCE "
        "(tanpa free counter). Umur + website + X UNVERIFIED. Tetap watchlist-only-age-unverified. "
        "TIDAK di-preview/di-mint." % probe.get("block"))

# --- 8. Baby Neiro track-C: 223->225 (+2), masih terkunci ---
bn = TC.get("Baby Neiro")
if isinstance(bn, dict):
    bn.update({"totalMinted": 225, "freeMinted": 225,
               "lastReadBlock": probe.get("block"), "lastReadWib": TS})
    bn["runNote1031"] = ("Run 1031 (blok %s): totalMinted=freeMinted 223->225/500 (45,0%%), opened 0, OPEN_AT 10000 "
        "(token TERKUNCI sampai 10.000 share). Umur + website UNVERIFIED. Tetap watchlist-only-age-unverified. "
        "TIDAK di-preview/di-mint." % probe.get("block"))

# --- 9. Bot Fighters (BOTF) 0x58a7: BARU di snapshot sbg watchlist-only-age-unverified ---
# Hot leg sudah mencatatnya 10:47 WIB di hot-leg-reported.json (watchlist-only-age-unverified) setelah
# verifikasi sendiri (totalSupply 3, freeMinted 3/500, website VERIFIED via app.js). Job ini TIDAK
# melaporkan ulang (dedupe lintas job: satu kontrak dilaporkan sekali). Verifikasi independen run ini:
# totalSupply 2, freeMinted 2/500, FREE_CAP 500, PAID_CAP 1000, MAX_SUPPLY 1500, price 0,002 BNB (paid
# lane), paused 0, agentRegistry() = registry persis 0x60B9...022F, walletFreeUsed(user)=0, balanceOf 0,
# externalBase https://botfighters.pages.dev/bot/?id=, tokenURI(1) external_url =
# https://botfighters.pages.dev/bot/?id=1 (hot leg). Website: situs termuat (browser), identitas +
# angka cocok persis (500 free, 1/Agent ID, maks 5 paid/wallet); alamat kontrak TIDAK tercetak di teks
# halaman (hot leg: app.js mencetak alamat persis). Umur UNVERIFIED: Sourcify verifiedAt 10:26:33 WIB
# BUKAN launch time; first-mint Transfer event tidak terkoroborasi (Ankr getLogs 401; eth_getLogs publik
# -32005; eth_call historis kembalikan null/state pruned); tidak ada stated launch time / post publik.
# Kontrak + owner 0x235e349fa54cf6c47ebcece6e0e645ca3d4ab160 BERSIH dari same-owner-discards.json (61 entri).
C["Bot Fighters"] = {
    "address": "0x58a704d9e02FE11c0A61683AE7F606E4366F13eb",
    "name": "Bot Fighters", "symbol": "BOTF", "kind": "ERC721",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "totalSupply": 2, "totalMinted": 2, "freeMinted": 2,
    "FREE_CAP": 500, "PAID_CAP": 1000, "MAX_SUPPLY": 1500,
    "MAX_PAID_PER_WALLET": 5, "price": 2000000000000000, "paused": 0,
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "walletFreeUsed_user": 0, "balanceOf_user": 0,
    "externalBase": "https://botfighters.pages.dev/bot/?id=",
    "imageBase": "https://botfighters.pages.dev/img/",
    "owner": "0x235e349fa54cf6c47ebcece6e0e645ca3d4ab160",
    "sourcifyVerified": True, "verifiedAt": "2026-11-11T03:26:33Z",
    "website": "https://botfighters.pages.dev/",
    "websiteVerified": True,
    "websiteNote": ("Situs termuat (browser 10:47 WIB): 'Free robot for .ai Agent ID holders - 500 free robots, "
        "1 per Agent ID + 1 per wallet, max 5 paid per wallet' - identitas + angka cocok persis dengan kontrak "
        "(FREE_CAP 500, MAX_PAID_PER_WALLET 5). Kontrak TIDAK tercetak di teks halaman; hot leg 10:34 menemukan "
        "alamat persis di app.js bundle. Linkage kontrak->situs: externalBase() on-chain + tokenURI(1) "
        "external_url botfighters.pages.dev/bot/?id=1."),
    "xVerified": False,
    "launchNote": ("Umur UNVERIFIED: Sourcify verifiedAt 2026-11-11T03:26:33Z (10:26:33 WIB) BUKAN launch time; "
        "first-mint Transfer event tidak terkoroborasi run ini (Ankr getLogs HTTP 401; eth_getLogs publik "
        "-32005 'limit exceeded' blok head-300; eth_call historis kembalikan null/state pruned); tidak ada "
        "stated launch time di situs; tidak ada post Boltbook/X. TotalSupply 2 (probe run ini blok 132897699) "
        "-> 3 (verifikasi hot leg 10:34, blok 132898306)."),
    "baselineNote": ("BARU dicatat run 1031 (temuan feed Sourcify recently-verified run ini: verified 10:26:33 WIB; "
        "shape-check S1 PASS + early-shape PASS, 56 fns: freeMint(agentId,gen) + freeMinted + agentRegistry + "
        "price). Hot leg 10:34 SUDAH mencatatnya di hot-leg-reported.json (10:47:28 WIB) sebagai "
        "watchlist-only-age-unverified - job ini TIDAK melaporkan ulang (dedupe lintas job). BUKAN early lead "
        "versi hot leg (umur unverified); BUKAN strong lead (0,6% <70%); BUKAN kandidat (umur + X unverified). "
        "TIDAK di-preview/di-mint. Promosi hanya bila umur terverifikasi <24 jam + gate website lolos + kaki "
        "strong lead terpenuhi."),
    "firstSeenBlock": probe58.get("block"),
    "firstSeenWib": "2026-11-11 ~10:45 WIB",
    "lastReadBlock": probe58.get("block"), "lastReadWib": TS,
    "runNote1031": ("Run 1031: Bot Fighters BARU dicatat watchlist-only-age-unverified (totalSupply 2, freeMinted 2/500 "
        "= 0,4%, slot user terbuka, agentRegistry persis, website terverifikasi, umur UNVERIFIED). Hot leg sudah "
        "mencatat 10:47 WIB - TIDAK dilaporkan ulang ke chat (dedupe). TIDAK di-preview/di-mint."),
}

# --- 10. ABYSSCABLE (DIVER) 0xd2e9: BARU di snapshot sbg watchlist-only ---
# Ditemukan probe-abyss worker 10:04 (tidak pernah di-merge run 1001); hot leg melacak di prio-reread
# (750 @10:19, 754 @10:29). Probe run ini: totalSupply 755, agentFreeUsed 755, MAX 5555, mintOpen 1,
# mintStart 1794314301 = 10 Nov ~19:38:47 WIB (umur ~15,3 jam <24 jam, TERVERIFIKASI via mintStart),
# free cap 2.000 (post Boltbook) -> 755/2000 = 37,75% (<50% kandidat, <70% strong lead). Slot terbuka
# (balanceOf 0). X discussion: post Boltbook 10:08 + call @crypto19. Website UNVERIFIED. Kontrak BERSIH
# dari same-owner-discards.json. BUKAN early lead (first mints 10 Nov, bukan run ini), BUKAN strong lead,
# BUKAN kandidat. TIDAK di-preview/di-mint. Tidak dilaporkan ke chat (watchlist-only).
C["ABYSSCABLE"] = {
    "address": "0xd2e9242b0d7c0186cc181a5fc8534541dad278a2",
    "name": "ABYSSCABLE", "symbol": "DIVER", "kind": "ERC721",
    "status": "watchlist-only-2026-11-11",
    "totalSupply": 755, "agentFreeUsed": 755, "freeCap": 2000,
    "freePct": 37.75,
    "MAX_SUPPLY": 5555, "mintOpen": 1, "balanceOf_user": 0,
    "mintStart": 1794314301, "mintStartWib": "2026-11-10 ~19:38 WIB",
    "mintEnd": 1794919101,
    "xVerified": True,
    "xNote": "Diskusi: post Boltbook 11 Nov 10:08 WIB (746/5.555, +102 sejak call @crypto19) - discussion evidence ada, akun X proyek belum terverifikasi.",
    "websiteVerified": False,
    "velocityVerified": False,
    "launchNote": "Umur TERVERIFIKASI <24 jam: mintStart() on-chain = 1794314301 = 10 Nov ~19:38:47 WIB; deadline umur ~19:39 WIB 11 Nov.",
    "baselineNote": ("BARU dicatat run 1031 (temuan probe-abyss worker 10:04 yang tidak ter-merge run 1001; hot leg "
        "melacak di prio-reread 750 @10:19, 754 @10:29). Probe run ini (blok 132898484): totalSupply 755, "
        "agentFreeUsed 755/2000 = 37,75%. Kontrak BERSIH dari same-owner-discards.json. BUKAN early lead "
        "(first mints 10 Nov), BUKAN strong lead (37,75% <70%), BUKAN kandidat (37,75% <50%, website "
        "unverified). TIDAK di-preview/di-mint. Tidak dilaporkan ke chat (watchlist-only)."),
    "firstSeenWib": "2026-11-11 ~10:04 WIB (probe-abyss)",
    "lastReadBlock": probar.get("block"), "lastReadWib": TS,
    "runNote1031": ("Run 1031: ABYSSCABLE BARU dicatat watchlist-only (totalSupply 755, agentFreeUsed 755/2000 = 37,75%, "
        "mintStart 10 Nov ~19:38 WIB, umur ~15,3 jam <24 jam, slot terbuka, website unverified). Tidak "
        "dilaporkan ke chat (bukan lead/kandidat). TIDAK di-preview/di-mint."),
}

# --- 11. ROSE / Pixel Relay 0x8f41: BARU di snapshot sbg watchlist-only-age-free%-unverified ---
# Post Boltbook recheck 11 Nov (~10:0x): totalSupply 664, name() Pixel Relay, symbol PX01. Probe run ini:
# totalSupply 668, MAX_SUPPLY 813, mintOpen 1, balanceOf 0; freeClaimed/freeMinted/FREE_SUPPLY semua revert
# (tanpa free counter - free% UNVERIFIED, 668/813 = 82,2% total supply TIDAK disubstitusi); mintStart()
# revert (umur UNVERIFIED). Kontrak BERSIH dari same-owner-discards.json. BUKAN early lead (first mints
# tidak terverifikasi run ini), BUKAN strong lead/kandidat (free% + umur + website unverified).
# TIDAK di-preview/di-mint. Tidak dilaporkan ke chat (watchlist-only).
C["ROSE Pixel Relay"] = {
    "address": "0x8f41960b7a6e6fb2423a426491d8a5ca6386ef47",
    "name": "Pixel Relay", "symbol": "PX01", "kind": "ERC721",
    "status": "watchlist-only-age-free%-unverified-2026-11-11",
    "totalSupply": 668, "MAX_SUPPLY": 813, "mintOpen": 1, "balanceOf_user": 0,
    "freePctNote": ("UNVERIFIED: freeClaimed/freeMinted/FREE_SUPPLY semua revert (kontrak tanpa free counter); "
        "totalSupply 668/813 = 82,2% BUKAN free% terverifikasi dan TIDAK disubstitusi."),
    "xVerified": False, "websiteVerified": False, "velocityVerified": False,
    "launchNote": ("Umur UNVERIFIED: mintStart() revert; pertama terlihat sebagai post recheck Boltbook 11 Nov "
        "~10:0x WIB (totalSupply 664); Sourcify creation/runtime exact_match per post (tidak diverifikasi "
        "ulang run ini)."),
    "baselineNote": ("BARU dicatat run 1031 (temuan Boltbook front page 11 Nov: post recheck 'ROSE totalSupply 664, "
        "name() Pixel Relay, symbol PX01'). Probe run ini (blok 132898484): totalSupply 668, MAX_SUPPLY 813, "
        "balanceOf(user)=0. Kontrak BERSIH dari same-owner-discards.json. BUKAN early lead / strong lead / "
        "kandidat (free% + umur + website UNVERIFIED). TIDAK di-preview/di-mint. Tidak dilaporkan ke chat "
        "(watchlist-only)."),
    "lastReadBlock": probar.get("block"), "lastReadWib": TS,
    "runNote1031": ("Run 1031: ROSE/Pixel Relay BARU dicatat watchlist-only-age-free%-unverified (totalSupply 668/813, "
        "free% UNVERIFIED, umur UNVERIFIED). Tidak dilaporkan (bukan lead/kandidat)."),
}

# --- 12. track_c updates from reread (non-None only) ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict):
        continue
    e = TC[name]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    if name == "11-11":
        e["runNote1031"] = "Run 1031: freeMinted 608->612 (+4 vs run 1001); tetap watchlist-only-age-website-unverified."

# --- 13. Rulz Share + Mimint Share: tidak di-re-read run ini, tetap upcoming ---
for k in ("Rulz Share", "Mimint Share"):
    e = C.get(k)
    if isinstance(e, dict):
        e["runNote1031"] = ("Run 1031: TIDAK di-re-read run ini (di luar daftar PRIO); totalMinted 0 per run 0931, "
            "mintStart 1794528000 = 13 Nov ~07:00 WIB - tetap upcoming, belum launching.")

# --- 14. first-mint probe result for BOTF (if file exists) ---
fm_path = BASE + "run-2026-11-11-1031-probe-58a7-firstmint.json"
fm_note = "Probe first-mint BOTF (eth_call historis): "
if os.path.exists(fm_path):
    try:
        fm = json.load(open(fm_path))
        reads = fm.get("reads", {})
        nz = [b for b, v in reads.items() if isinstance(v, int) and v > 0]
        if fm.get("first_mint_block"):
            fm_note += ("first-mint block ~%s (totalSupply %s) - timestamp blok belum diambil, umur tetap "
                        "UNVERIFIED sampai timestamp terverifikasi." % (fm["first_mint_block"], fm.get("first_mint_block_supply")))
        elif nz:
            fm_note += "totalSupply >0 di bracket tertua (head-12000) - launch lebih tua dari ~2,8 jam atau state pruned; tidak terbracket."
        else:
            fm_note += "semua pembacaan historis null (dataseed tidak melayani eth_call historis / state pruned) - first-mint block tidak dapat ditentukan."
    except Exception as ex:
        fm_note += "file first-mint tidak terbaca (%s)." % ex
else:
    fm_note += "file belum ada saat merge (probe masih berjalan / gagal) - umur tetap UNVERIFIED."
snap["runNote1031_firstmint_botf"] = fm_note

# --- 15. top-level run notes ---
snap["last_run_wib"] = TS
snap["timestamp_wib"] = TS
snap["last_run_note"] = ("Run 1031: 0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead baru / 0 early lead "
    "baru dilapor. BARU dicatat watchlist-only (TIDAK dilaporkan): Bot Fighters 2/500 (0,4%, umur unverified - "
    "sudah dicatat hot leg 10:47 WIB, dedupe), ABYSSCABLE 755/2000 (37,75%, umur <24 jam), ROSE/Pixel Relay "
    "668/813 (free% + umur unverified). Stampooor 494->534 (44,5%, velocity GAGAL, tetap EARLY); Jade Vault "
    "335->374 (velocity LOLOS tapi tetap EARLY - free%/umur/website/X unverified); NIGHTFORGE 740 flat (36,9%, "
    "tetap watchlist-only <70%); AgentPals 76/300 = 25,3%. Feed Sourcify 18 baru di-shape-check: 1 S1 (Bot "
    "Fighters). Scan FAST-FAIL (pre-flight Ankr 401). binanceai launched=0 (refund phase).")
snap["runNote1031"] = snap["last_run_note"]
snap["runNote1031_scan"] = ("Scan run 1031 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized "
    "dalam 14,7 dtk (head 132897130 via RPC publik). Outage Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0% "
    "s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564; gap ke head ~384.600 blok dan tumbuh; "
    "backfill OFF - run backfill terakhir 10:16 WIB juga 401). Track-C 5c dilewati run ini (tidak ada output "
    "scan baru).")
snap["runNote1031_binanceai"] = ("Run 1031: launched=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok %s) - "
    "TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong." % probe.get("block"))
snap["runNote1031_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah sejak run 1001), "
    "116 kontrak, 7 same_owner_discarded; 0 temuan pelengkap baru (tidak ada kontrak di luar snapshot yang belum "
    "tercatat). same-owner-discards.json mtime 2026-11-10 20:22 WIB (61 entri) - tidak ada entri baru; Bot "
    "Fighters (kontrak + owner 0x235e...ab160), ABYSSCABLE, ROSE BERSIH dari discards sebelum dicatat.")
snap["runNote1031_discovery"] = ("Discovery run 1031: Boltbook EN+ZH dibaca via browser text-fetch (crawl 10:11 WIB, ~20 alamat "
    "unik): 0 baru vs snapshot/hot-leg-seen kecuali ABYSSCABLE + ROSE (hot-leg-seen, baru dicatat snapshot utama "
    "run ini) - LOWB 823/1.000, Pathwyrm (excluded), HIPPO/NIGHT age-excluded, ONI/COMPASYN/ACORE discarded, "
    "HELIX/DRAGON/EMBER early-lead-reported, KOAI/Agent Miner watchlist, NEON sold out, BAGENT (sudah diklaim), "
    "Fira + Baby Neiro sudah di snapshot. Sweep EN+ZH: 0 proyek baru (Agentic Gangster/MOLT/NOVRA/AgentForge "
    "semua sudah tercatat exhausted/excluded; Golden Agents age-excluded; Agent Operators upcoming tanpa kontrak). "
    "Sourcify feed 20 kontrak (verified 03:03-03:27Z): 2 sudah ditriase run 1001, 18 di-shape-check run ini - "
    "S1=1 (Bot Fighters 0x58a7), S2=0, EARLY-shape=1 (Bot Fighters). Odaily newsflash: 0 keyword hit. PANews "
    "tidak dibaca run ini (Odaily sudah 0 hit; retry run berikut).")
snap["runNote1031_age_exclusions"] = ("Run 1031: 0 age-exclusion BARU. Deadline berjalan: NIGHTFORGE 14:37 WIB 11 Nov "
    "(mintStart 10 Nov 14:37 WIB; 36,9% - watchlist-only); AgentPals ~06:33 WIB 12 Nov; MOODENG ~02:00 WIB "
    "12 Nov; UFO ~22:05 WIB 12 Nov. Bot Fighters: umur UNVERIFIED (bukan age-excluded) - watchlist-only. "
    "Fira Agent: pertama terlihat 9 Nov 21:26 WIB (diduga >24 jam) tapi launch time tidak terverifikasi ke standar "
    "exclusion - tetap watchlist-only-age-unverified, bukan age-excluded.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE. contracts:", len(C), "track_c:", len(TC))
print("Bot Fighters in contracts:", "Bot Fighters" in C, "| ABYSSCABLE:", "ABYSSCABLE" in C, "| ROSE:", "ROSE Pixel Relay" in C)
