#!/usr/bin/env python3
"""Merge run 1001 (scheduled 2026-11-11 10:01 WIB) results into onchain-snapshot.json.
Writes snapshot (with .bak). Reuses the interrupted 10:04 worker's reread JSON
(run-2026-11-11-1004-reread.json, block 132893298, 59 contracts + 22 track_c)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-1004-reread.json"))
probe = json.load(open(BASE + "run-2026-11-11-1001-probe.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1001-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 10:01 WIB"

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

# --- 1. reread updates ---
for name, d in reread["reread"].items():
    if name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        e["runNote1001"] = ("Run 1001 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
            e["runNote1001"] = ("Run 1001 (blok %s): totalSupply pertama terbaca %s (sebelumnya None) - "
                                "baseline dicatat, velocity belum lulus; freeMinted=%s; bal_user=%s; status %s."
                                % (BLOCK, ns, d.get("freeMinted"), d.get("balanceOf_user"), e.get("status")))
        else:
            r = vel(name, ns)
            diff, rate, ratio = r if r else (None, None, None)
            e["runNote1001"] = ("Run 1001 (blok %s): totalSupply %s->%s (+%s, %s/mnt vs prev %s = %sx) -> velocity %s; "
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

# --- 2. Stampooor: 437->494 (+57), velocity GAGAL (1.9/mnt vs prev 5.13 = 0.37x) ---
st = C.get("Stampooor Stamp Packs")
if isinstance(st, dict):
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": 494, "freeMinted": 494, "totalSupply": 494,
               "freeAvailable_user": 1, "lastReadBlock": BLOCK, "lastReadWib": TS})
    st["runNote1001"] = ("Run 1001: freeMinted 437->494 (+57, 1,90/mnt vs prev 5,13 = 0,37x) -> velocity GAGAL. "
        "Free 494/1200 = 41,17% (<50% kandidat, <70% strong lead). Slot user TERBUKA (balanceOf 0). "
        "Umur TERVERIFIKASI <24 jam (mintStart 11 Nov ~09:00 WIB). X + website UNVERIFIED. Tetap EARLY. "
        "TIDAK di-preview/di-mint.")

# --- 3. Jade Vault 0x7Eb9: 320->335 (+15 <20) velocity GAGAL ---
jv = C.get("0x7Eb9")
if isinstance(jv, dict):
    jv.update({"totalMinted": 335, "totalSupply": 335, "lastReadBlock": BLOCK, "lastReadWib": TS})
    jv["runNote1001"] = ("Run 1001: totalMinted 320->335 (+15, <20 token) -> velocity GAGAL. quote(user,1)=0 "
        "(GRATIS, dari run 0931), slot terbuka. Free% tetap UNVERIFIED (template tanpa free counter - % total "
        "supply 335/8888 TIDAK disubstitusi). Umur + website + X UNVERIFIED. Tetap EARLY. TIDAK di-preview/di-mint.")

# --- 4. NIGHTFORGE: 737->740 (+3) velocity GAGAL; ~737/2000 = 36,9% ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    nf.update({"totalSupply": 740, "freePctVerified": 36.9,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    nf["runNote1001"] = ("Run 1001: totalSupply 737->740 (+3) -> velocity GAGAL; agentFreeUsed ~737/2000 = 36,9% "
        "(estimasi dari totalSupply, probe agentFreeUsed tidak diulang run ini - tidak mengubah tier: jauh di bawah "
        "ambang strong lead >70%). Slot terbuka (balanceOf 0). Deadline umur 14:37 WIB 11 Nov belum lewat. "
        "Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 5. AgentPals: baseline pertama 75/300 = 25% (free phase live sejak 06:33 WIB) ---
ap = C.get("AgentPals")
if isinstance(ap, dict):
    ap.update({"totalSupply": 75, "freeMinted": 75, "totalMinted": 75,
               "status": "watchlist-only-2026-11-11",
               "lastReadBlock": BLOCK, "lastReadWib": TS})
    ap["runNote1001"] = ("Run 1001: totalSupply pertama terbaca 75 (sebelumnya None) - baseline dicatat. "
        "Free phase LIVE sejak 11 Nov 06:33:57 WIB; 75/300 = 25,0% (<50% kandidat, <70% strong lead). "
        "Slot user terbuka (balanceOf 0). Website UNVERIFIED. Tetap watchlist-only. TIDAK di-preview/di-mint.")

# --- 6. BYTEBLOOM velocity LOLOS tapi minted-by-user: tanpa promosi ---
bb = C.get("BYTEBLOOM")
if isinstance(bb, dict):
    bb["runNote1001"] = ("Run 1001: totalSupply 726->756 (+30, 1,00/mnt vs prev 0,2667 = 3,75x) -> velocity LOLOS, "
        "TAPI status minted-by-user-2026-11-10 - TIDAK ada promosi/aksi (sudah dimiliki user).")

# --- 7. Fira Agent: BARU di snapshot sbg watchlist-only-age-unverified ---
C["Fira Agent"] = {
    "address": "0x7d46023bf2c3732f5fd30321cfce1ca91684408d",
    "name": "Fira Agent", "kind": "ERC721", "status": "watchlist-only-age-unverified-2026-11-11",
    "totalSupply": 4900, "MAX_SUPPLY": 5000,
    "freePctInference": 98.0,
    "freePctNote": ("INFERENCE ONLY: totalSupply 4900/MAX_SUPPLY 5000 = 98,0%; freeClaimed/freeMinted/FREE_SUPPLY "
                    "semua revert (kontrak tanpa free counter) - BUKAN free% terverifikasi."),
    "sourcifyVerified": False,
    "codeHasRegistry": True,
    "codeLen": 13598,
    "owner": "0xe0808a338d96171fa9bde4d4d1897692392a0cbb",
    "balanceOf_user": 0,
    "xVerified": False, "websiteVerified": False, "velocityVerified": False,
    "launchNote": ("Umur UNVERIFIED: pertama terlihat hot-leg 2026-11-09 21:26 WIB via Boltbook (new_vs_seen) - "
                   "launch <= 9 Nov 21:26 WIB (diduga >24 jam, TAPI launch time sendiri tidak terverifikasi ke standar "
                   "exclusion, jadi watchlist-only, bukan age-excluded). Sourcify UNVERIFIED (404 saat triase hot-leg "
                   "9 Nov + post Boltbook 11 Nov)."),
    "baselineNote": ("BARU dicatat run 1001 (temuan Boltbook front page 11 Nov ~10:05 WIB: '4.900/5.000 free (98,0%)'). "
        "Probe run ini (blok 132894993): totalSupply 4900, MAX_SUPPLY 5000, balanceOf(user)=0, bytecode mengandung "
        "registry hex 0x60B926... (agent-shaped by bytecode). Kontrak + owner BERSIH dari same-owner-discards.json "
        "(61 entri, 12 owner). BUKAN early lead (first mints TIDAK terverifikasi run ini - sudah 4900), BUKAN strong "
        "lead (free% inference + umur unverified + website unverified), BUKAN kandidat. TIDAK di-preview/di-mint. "
        "Tidak dilaporkan ke chat (watchlist-only)."),
    "lastReadBlock": probe.get("block"), "lastReadWib": TS,
    "runNote1001": ("Run 1001: Fira Agent BARU dicatat watchlist-only-age-unverified (totalSupply 4900/5000, free% "
        "98,0% INFERENCE, umur + website + X UNVERIFIED). Tidak dilaporkan (bukan lead/kandidat)."),
}

# --- 8. Baby Neiro: BARU di track_c sbg watchlist-only-age-unverified ---
TC["Baby Neiro"] = {
    "sale": "0x10f84859562B0FCbB7464b17dfC84C809CfbD674",
    "address": "0x10f84859562B0FCbB7464b17dfC84C809CfbD674",
    "token": "0x10f84859562B0FCbB7464b17dfC84C809CfbD674",
    "name": "Baby Neiro", "symbol": "BNEIRO", "kind": "track-c-sale-S1",
    "status": "watchlist-only-age-unverified-2026-11-11",
    "totalMinted": 223, "freeMinted": 223, "FREE_SHARES": 500,
    "freePct": 44.6,
    "opened": 0, "OPEN_AT": 10000,
    "maxShares": 4440000, "tokensPerShare": 75000000,
    "priceAt": "0.003 BNB/share (paid lane)",
    "codeHasRegistry": True,
    "owner": "0x1a8a6ebd81c5c704d8951d6280d66237ef449fd3",
    "balanceOf_user": 0,
    "sourcifyVerified": True, "verifiedAt": "2026-11-10T10:37:42Z",
    "xVerified": False, "websiteVerified": False,
    "launchNote": ("Umur UNVERIFIED: Sourcify verifiedAt 2026-11-10T10:37:42Z BUKAN launch time; first-mint on-chain "
                   "belum terverifikasi (Ankr getLogs mati 401); pace Boltbook hanya dari 11 Nov 09:19 WIB (193) "
                   "-> 09:58 WIB (208)."),
    "baselineNote": ("BARU dicatat run 1001 (temuan Boltbook front page 11 Nov ~09:58 WIB, post recheck: freeMinted "
        "208/500, quoteFor(identity,1,true) cost 0, token 75.000.000/share, slot agen terbuka). Probe run ini "
        "(blok 132894993): totalMinted=freeMinted=223/500 (44,6%), opened=0, OPEN_AT=10000 (token TERKUNCI sampai "
        "10.000 share; paid masih 0), bytecode mengandung registry hex (template RIMEVAULT/GANG/FENGHUO/WNO/MOODENG/"
        "UFO/LOWB). Slot user: freeClaimed/quotaOf/mintedById revert di probe run ini (UNVERIFIED oleh bacaanku; post "
        "Boltbook klaim freeClaimed 0, quotaOf 10, mintedById 0). Kontrak + owner BERSIH dari same-owner-discards.json "
        "(61 entri, 12 owner). BUKAN track-C lead (umur UNVERIFIED + website UNVERIFIED + token terkunci). "
        "TIDAK di-preview/di-mint. Tidak dilaporkan ke chat (watchlist-only)."),
    "lastReadBlock": probe.get("block"), "lastReadWib": TS,
    "runNote1001": ("Run 1001: Baby Neiro BARU dicatat track_c watchlist-only-age-unverified (freeMinted 223/500 = "
        "44,6%, opened 0, token terkunci s.d. 10.000 share). Tidak dilaporkan (bukan lead)."),
}

# --- 9. track_c updates from reread (non-None only) ---
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
        e["runNote1001"] = "Run 1001: freeMinted 608 (flat vs run 0931/0959); tetap watchlist-only-age-website-unverified."

# --- 10. LOWB: free lane 823/1000 per post Boltbook 10:08 WIB (bukan probe sendiri) ---
lb = TC.get("LOWB")
if isinstance(lb, dict):
    lb.update({"totalFreeMinted": 823, "lastReadBlock": BLOCK, "lastReadWib": TS})
    lb["runNote1001"] = ("Run 1001: free lane 823/1000 per post Boltbook front page ~10:08 WIB (blok 132893531/536, "
        "baca pihak ketiga - BUKAN probe run ini; hot-leg 0959 membaca 816). opened 0 (hot-leg 0959, tidak "
        "di-probe ulang run ini). Tetap watchlist-only-not-open (lead track-C butuh sale opening).")

# --- 11. Rulz Share + Mimint Share: tidak di-re-read run ini, tetap upcoming ---
for k in ("Rulz Share", "Mimint Share"):
    e = C.get(k)
    if isinstance(e, dict):
        e["runNote1001"] = ("Run 1001: TIDAK di-re-read run ini (di luar daftar PRIO); totalMinted 0 per run 0931, "
            "mintStart 1794528000 = 13 Nov ~07:00 WIB - tetap upcoming, belum launching.")

# --- 12. top-level run notes ---
snap["last_run_wib"] = TS
snap["timestamp_wib"] = TS
snap["last_run_note"] = ("Run 1001: 0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead baru. Stampooor "
    "437->494 (41,17%, velocity GAGAL, tetap EARLY); Jade Vault 320->335 (tetap EARLY); NIGHTFORGE 737->740 "
    "(~36,9%, tetap watchlist-only <70%); AgentPals baseline 75/300 = 25% (free phase live). BYTEBLOOM velocity "
    "LOLOS (+30, 3,75x) tapi minted-by-user - tanpa promosi. 2 BARU dicatat watchlist-only (TIDAK dilaporkan): "
    "Fira Agent 4900/5000 (free% 98% INFERENCE, umur unverified) + Baby Neiro track-C 223/500 (umur unverified, "
    "token terkunci). Feed Sourcify 2 baru: POPO buyback + plain ERC20 - bukan agent-shaped, bukan lead. "
    "Scan FAST-FAIL (pre-flight Ankr 401). binanceai launched=0 (refund phase).")
snap["runNote1001"] = snap["last_run_note"]
snap["runNote1001_scan"] = ("Scan run 1001 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) HTTP 401 Unauthorized "
    "dalam 42,1 dtk (head 132894670 via RPC publik); percobaan ke-2 timeout 60 dtk (rc=124, tanpa output). Outage "
    "Ankr berlanjut sejak ~13:33 WIB 2026-11-09 (kuota 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap "
    "132512564; gap ke head ~382.000 blok dan tumbuh; backfill OFF). Track-C 5c dilewati run ini (tidak ada output "
    "scan baru).")
snap["runNote1001_binanceai"] = ("Run 1001: launched=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok %s) - "
    "TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong." % probe.get("block"))
snap["runNote1001_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah), 116 kontrak, "
    "7 same_owner_discarded; 6 kontrak 'di luar snapshot' versi cek awal ternyata ada di snapshot bagian excluded "
    "(ORE, ETHBack, Ikigai, AGC, Krillfarm + 1) - 0 temuan pelengkap baru. same-owner-discards.json mtime "
    "2026-11-10 20:22 WIB (61 entri, 12 owner) - tidak ada entri baru; Fira + Baby Neiro (kontrak + owner) BERSIH "
    "dari discards sebelum dicatat.")
snap["runNote1001_discovery"] = ("Discovery run 1001: Boltbook EN+ZH dibaca via browser text-fetch (curl egress 000 run "
    "ini; EN 0-byte via curl sudah 9 run berturut-turut di hot leg - flag infra berlanjut, ZH normal via browser). "
    "~20 alamat unik di front page, 0 baru vs hot-leg-seen (semua sudah di snapshot atau sudah ditriase hot leg). "
    "Sweep EN: 0 proyek baru (Agentic Gangster, AgentForge, Gloomies, Pixel Fox, CHIPS - semua lama/sudah di snapshot "
    "atau tanpa Agent ID). Sweep ZH: 0 proyek baru (UFO + Agentic Gangster sudah di snapshot; First-Dollar Grove sudah "
    "di snapshot sbg age-excluded; AgentID ETH bukan BSC). Sourcify feed 20 kontrak (verified 02:54-03:05Z): 2 baru "
    "vs hot-leg-seen - 0x2892 POPO buyback/fission (bukan mint/sale) + 0x9d86 plain ERC20 (bukan sale-shape); 0 S1/S2/"
    "early. Odaily newsflash: 0 keyword hit. PANews tidak dibaca run ini (Odaily sudah 0 hit; retry run berikut). "
    "Fira Agent + Baby Neiro dicatat watchlist-only (bukan lead, tidak dilaporkan).")
snap["runNote1001_age_exclusions"] = ("Run 1001: 0 age-exclusion BARU. Deadline berjalan: NIGHTFORGE 14:37 WIB 11 Nov "
    "(mintStart 10 Nov 14:37 WIB; ~36,9% - watchlist-only); AgentPals ~06:33 WIB 12 Nov; MOODENG ~02:00 WIB 12 Nov; "
    "UFO ~22:05 WIB 12 Nov. Gelombang early lead umur UNVERIFIED (watchlist-only untuk umur, bukan age-exclusion). "
    "Fira Agent: pertama terlihat 9 Nov 21:26 WIB (diduga >24 jam) tapi launch time tidak terverifikasi ke standar "
    "exclusion - tetap watchlist-only-age-unverified, bukan age-excluded.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE. contracts:", len(C), "track_c:", len(TC))
print("Fira in contracts:", "Fira Agent" in C, "| Baby Neiro in track_c:", "Baby Neiro" in TC)
