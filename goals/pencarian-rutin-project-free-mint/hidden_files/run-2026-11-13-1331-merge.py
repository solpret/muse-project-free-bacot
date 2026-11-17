#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 13:31 WIB.
Reads run-2026-11-13-1331-verify.json + discovery.json + verify-new.json
+ run-2026-11-13-1331-e589.json, updates onchain-snapshot.json (backup first).
REPORTABLE CHANGE: 1 SELLOUT - JNTM (track-C lead, dilaporkan 0801)
free pool 1000/1000 = 100% (freeLeft 0), laporkan sekali + hapus dari track_c.
NEW: Mossbound Key 0xe589 (Sourcify feed, S1 PASS, agent-shaped NFT) -
sale BELUM buka (saleStart 13:51:55 WIB hari ini, totalSupply 0) ->
watchlist-only-upcoming, TIDAK dilaporkan sebagai lead/kandidat, TIDAK
di-preview/di-mint. Xeno Agent 0xc972 (Boltbook baru) + 0x40089b (feed baru)
checked, BUKAN agent-shaped, dicatat saja.
Lainnya DIAM: 0 kandidat baru, 0 strong lead baru, 0 early lead baru,
0 track-C lead baru, 0 perubahan track-B, 0 age-exclusion baru.
Pre-flight FAIL (HTTP 401) - scan leg fast-fail, watermark tetap 132512564.
Velocity convention: previousRatePerMin frozen as stored (runs 0931-1301).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1331"
MIN = 30.0
v = json.load(open(BASE + f"run-2026-11-13-{RUN}-verify.json"))
reads = v["reads"]
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + f"onchain-snapshot-2026-11-13-{RUN}.bak")
C = snap["contracts"]; TC = snap["track_c"]
def S(n): return reads[n]["summary"]
def vel(prev, new, prev_rate):
    minted = (new - prev) if (prev is not None and new is not None) else None
    rate = (minted / MIN) if minted is not None else None
    ratio = (rate / prev_rate) if (rate is not None and prev_rate) else None
    passes = bool(minted is not None and minted >= 20 and ratio is not None and ratio >= 1.5)
    return minted, rate, ratio, passes
WIB = "2026-11-13 ~13:40 WIB"
BLK = 133304615
# --- Agentx ---
a = C["Agentx"]; prev_tm = a["totalMinted"]
new_tm = S("Agentx").get("totalMinted")
minted, rate, ratio, passes = vel(prev_tm, new_tm, a.get("previousRatePerMin") or 0.18)
a["previousTotalSupply"] = prev_tm; a["totalMinted"] = new_tm
a["freeMinted"] = S("Agentx").get("freeMinted")
a["mintedInInterval"] = minted; a["intervalMinutes"] = MIN
a["currentRatePerMin"] = round(rate, 3) if rate is not None else None
a["velocityRatio"] = round(ratio, 2) if ratio is not None else None
a["velocityLegPasses"] = passes
a["lastReadBlock"] = BLK; a["lastReadWib"] = WIB
a["freePct"] = round(100.0 * a["freeMinted"] / 1111, 1)
a["ageHours"] = round((1794552715 - 1794499865) / 3600, 1)  # placeholder overwritten below
a["ageHours"] = 14.3
a[f"runNote{RUN}"] = ("Run 1331: totalMinted %s->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); umur ~14,3 jam (mintOpensAt 23:11 WIB 12 Nov) <24 jam; "
    "gate website GAGAL (sudah dilaporkan 08:01 + hot-leg 08:29) - DIAM."
    % (prev_tm, new_tm, minted, rate, ratio or 0, a["freeMinted"], a["freePct"]))
# --- Zero ---
z = C["Zero"]; prev_tm = z["totalMinted"]
new_tm = S("Zero").get("totalMinted")
minted, rate, ratio, passes = vel(prev_tm, new_tm, z.get("previousRatePerMin") or 2.42)
z["previousTotalSupply"] = prev_tm; z["totalMinted"] = new_tm
z["freeMinted"] = S("Zero").get("freeMinted")
z["mintedInInterval"] = minted; z["intervalMinutes"] = MIN
z["currentRatePerMin"] = round(rate, 3) if rate is not None else None
z["velocityRatio"] = round(ratio, 2) if ratio is not None else None
z["velocityLegPasses"] = passes
z["lastReadBlock"] = BLK; z["lastReadWib"] = WIB
z["freePct"] = round(100.0 * z["freeMinted"] / 500, 1)
z[f"runNote{RUN}"] = ("Run 1331: totalMinted %s->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/500 = %.1f%%, TAPI velocity GAGAL + X/website UNVERIFIED -> BUKAN kandidat; <70%% -> BUKAN strong lead; slot terbuka; umur ~5,6 jam (mintOpensAt 07:55 WIB) <24 jam - DIAM."
    % (prev_tm, new_tm, minted, rate, ratio or 0, z["freeMinted"], z["freePct"]))
# --- Oliver Agents ---
o = C["Oliver Agents"]; prev_ts = o["totalSupply"]; prev_fm = o["freeMinted"]
new_ts = S("OLIVER").get("totalSupply"); new_fm = S("OLIVER").get("freeMinted")
o["previousTotalSupply"] = prev_ts; o["totalSupply"] = new_ts; o["freeMinted"] = new_fm
o["freeRemaining"] = S("OLIVER").get("freeRemaining")
o["mintedInInterval"] = new_ts - prev_ts; o["intervalMinutes"] = MIN
o["currentRatePerMin"] = round((new_ts - prev_ts) / MIN, 3)
o["velocityLegPasses"] = False
o["lastReadBlock"] = BLK; o["lastReadWib"] = WIB
o[f"runNote{RUN}"] = ("Run 1331: totalSupply %s->%s (+%s), freeMinted %s->%s/1000 = %.1f%%; velocity GAGAL (<20 token); "
    "umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka; watchlist-only, DIAM."
    % (prev_ts, new_ts, new_ts - prev_ts, prev_fm, new_fm, 100.0 * new_fm / 1000))
# --- Royal Rush Agents ---
r = C["Royal Rush Agents"]; prev_fm = r["freeMinted"]
new_ts = S("RoyalRush").get("totalSupply"); new_fm = S("RoyalRush").get("freeMinted")
r["previousTotalSupply"] = r["totalSupply"]; r["totalSupply"] = new_ts; r["freeMinted"] = new_fm
r["freeRemaining"] = S("RoyalRush").get("freeRemaining")
r["paidMinted"] = S("RoyalRush").get("paidMinted"); r["mintedCount"] = S("RoyalRush").get("mintedCount")
minted = new_fm - prev_fm; rate = minted / MIN
ratio = rate / 7.74 if rate else None
r["mintedInInterval"] = minted; r["intervalMinutes"] = MIN
r["currentRatePerMin"] = round(rate, 2)
r["velocityRatio"] = round(ratio, 2) if ratio else None
r["velocityLegPasses"] = False
r["lastReadBlock"] = BLK; r["lastReadWib"] = WIB
r["freePct"] = round(100.0 * new_fm / 1000, 1)
r[f"runNote{RUN}"] = ("Run 1331: freeMinted %s->%s/1000 = %.1f%% (+%s dalam ~30 mnt, ~%.2f/mnt vs baseline 7,74 = %.2fx -> velocity GAGAL, melambat); "
    "totalSupply %s, paidMinted %s; velocity GAGAL + umur launch TETAP UNVERIFIED + X UNVERIFIED -> BUKAN kandidat (<70%% juga, bukan strong lead); "
    "slot user TERBUKA (freeClaimedByAgent=0, bal 0); monitor run berikut."
    % (prev_fm, new_fm, 100.0 * new_fm / 1000, minted, rate, ratio or 0, new_ts, r["paidMinted"]))
# --- JNTM: SELLOUT free pool -> remove from track_c ---
j = TC.pop("JNTM", None)
jntm_note = None
if j is not None:
    prev_fc = j.get("freeClaimed")
    jntm_note = ("Run 1331 SELLOUT: JNTM 0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b freeClaimed %s->1000/1000 = 100%% (freeLeft 0, "
        "totalMinted 1087, paidMinted 87); free pool HABIS, slot user hilang (freeClaimedByAgent=0 tapi pool 0). Track-C lead dilaporkan sekali run 0801 "
        "(gate PENDING + quote NULL, tidak pernah di-preview/di-mint). Umur ~7,3 jam (mintStart 06:13 WIB) <24 jam. Dilaporkan sekali run ini + dihapus dari track_c."
        % (prev_fc,))
    snap.setdefault("sellouts", []).append({"name": "JNTM", "address": "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
        "track": "C", "reason": "sellout-free-pool", "evidence": jntm_note, "reported_once": True, "removed_wib": WIB})
# --- AgentLabs ---
al = C["AgentLabs"]; prev = al.get("totalSpecimens")
al["previousTotalSpecimens"] = prev; al["totalSpecimens"] = S("AgentLabs").get("totalSpecimens")
al["lastReadBlock"] = BLK; al["lastReadWib"] = WIB
al[f"runNote{RUN}"] = "Run 1331: totalSpecimens %s->%s (experiment 2 berjalan; genesisStart 21:04 WIB 12 Nov, deadline umur 21:04 WIB 13 Nov belum lewat); DIAM." % (prev, al["totalSpecimens"])
# --- OUTY ---
ou = C["OUTY"]; ou["freeSold"] = S("OUTY").get("freeSold"); ou["minted"] = S("OUTY").get("minted")
ou["lastReadBlock"] = BLK; ou["lastReadWib"] = WIB
ou[f"runNote{RUN}"] = "Run 1331: freeSold 21->23/1500 (+2); FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; DIAM."
# --- MECHA ---
m = C["MECHA"]; prev = m.get("freeClaimed")
m["previousTotalMinted"] = m.get("totalMinted"); m["totalMinted"] = S("MECHA").get("totalMinted")
m["freeClaimed"] = S("MECHA").get("freeClaimed")
m["lastReadBlock"] = BLK; m["lastReadWib"] = WIB
m[f"runNote{RUN}"] = "Run 1331: freeClaimed %s->%s/4444 = %.1f%% (<50%%); DIAM." % (prev, m["freeClaimed"], 100.0 * m["freeClaimed"] / 4444)
# --- Pickgrid ---
p = C["Pickgrid"]; p["freeMinted"] = S("Pickgrid").get("freeMinted")
p["lastReadBlock"] = BLK; p["lastReadWib"] = WIB
p[f"runNote{RUN}"] = "Run 1331: freeMinted 216/300 FLAT, umur UNVERIFIED; DIAM."
# --- PX24 group (PX24 read FAILED again -> keep old value) ---
for key, name in [("PX24","PX24"),("SKRR","SKRR"),("ME30","ME30"),("CY24","CY24")]:
    e = C[key]; prev = e.get("totalSupply"); new = S(name).get("totalSupply")
    if new is None:
        e[f"runNote{RUN}"] = "Run 1331: BACA GAGAL (batch-fail, nilai lama dipertahankan, BUKAN nol); umur TETAP UNVERIFIED; DIAM."
    else:
        e["previousTotalSupply"] = prev; e["totalSupply"] = new
        e[f"runNote{RUN}"] = "Run 1331: totalSupply %s->%s (%+d), umur TETAP UNVERIFIED; DIAM." % (prev, new, new - prev)
    e["lastReadBlock"] = BLK; e["lastReadWib"] = WIB
# --- HIVE Agents ---
h = C["HIVE Agents"]; h["totalSupply"] = S("HIVE").get("totalSupply")
h["lastReadBlock"] = BLK; h["lastReadWib"] = WIB
h[f"runNote{RUN}"] = "Run 1331: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user; DIAM."
# --- track_c: OBFG / NOTV / AgentMuse ---
ob = TC["OBFG"]; prev_fm = ob["freeMinted"]
ob["previousTotalMinted"] = ob.get("totalMinted"); ob["totalMinted"] = S("OBFG").get("totalMinted")
ob["freeMinted"] = S("OBFG").get("freeMinted")
ob["freePct"] = round(100.0 * ob["freeMinted"] / 1230, 1)
ob["lastReadBlock"] = BLK; ob["lastReadWib"] = WIB
ob[f"runNote{RUN}"] = ("Run 1331: %s->%s/1230 = %.1f%% (+%s), umur ~17,5 jam (saleStart 20:01 WIB 12 Nov) <24 jam, slot terbuka (freeAvailable=1); "
    "gate-blocked SUDAH dilaporkan 12 Nov; DIAM." % (prev_fm, ob["freeMinted"], ob["freePct"], ob["freeMinted"] - prev_fm))
nv = TC["NOTV"]; nv["totalMinted"] = S("NOTV").get("totalMinted")
nv["lastReadBlock"] = BLK; nv["lastReadWib"] = WIB
nv[f"runNote{RUN}"] = "Run 1331: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka; DIAM."
am = TC["AgentMuse"]; prev_fc = am["freeClaimed"]
am["freeClaimed"] = S("AgentMuse").get("freeClaimed")
am["bookedOf_user"] = S("AgentMuse").get("bookedOf_user")
am["lastReadBlock"] = BLK; am["lastReadWib"] = WIB
am[f"runNote{RUN}"] = "Run 1331: freeClaimed %s->%s/888 = %.1f%%, bookedOf(user)=FREE_OSK utuh; minted-by-user; DIAM." % (prev_fc, am["freeClaimed"], 100.0 * am["freeClaimed"] / 888)
# --- DragonAgent + BC1B ---
da = C["Dragon Agent"]; prev = da.get("totalSupply"); da["totalSupply"] = S("DragonAgent").get("totalSupply")
da[f"runNote{RUN}"] = "Run 1331: totalSupply %s->%s (+%s); free views NULL -> free %% UNVERIFIED; DIAM." % (prev, da["totalSupply"], da["totalSupply"] - prev if prev is not None else "?")
da["lastReadBlock"] = BLK; da["lastReadWib"] = WIB
bc = TC.get("RESUME-BC1B")
if bc is not None:
    prev = bc.get("freeCount"); bc["freeCount"] = S("BC1B").get("freeCount")
    bc[f"runNote{RUN}"] = "Run 1331: freeCount %s->%s; DIAM." % (prev, bc["freeCount"])
    bc["lastReadBlock"] = BLK; bc["lastReadWib"] = WIB
# --- pending_claims: binanceai.fun still pending (launched=0) ---
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
pc["launched"] = S("BinanceAI-mint").get("launched")
pc["tokenClaimed_user"] = S("BinanceAI-mint").get("tokenClaimed_user")
pc["lastReadWib"] = WIB
snap["pending_claims"] = {"binanceai.fun": pc}
# --- NEW: Mossbound Key (upcoming, sale opens 13:51:55 WIB today) ---
e589 = json.load(open(BASE + "run-2026-11-13-1331-e589.json"))
C["Mossbound Key"] = {
    "address": "0xe589A94316C68d4A4f008f841Deb7e9612445244",
    "name": "Mossbound Key", "symbol": "MSKY", "kind": "ERC721",
    "status": "watchlist-only-upcoming-2026-11-13",
    "totalSupply": e589.get("totalSupply"), "totalMinted": e589.get("totalMinted"),
    "FREE_SUPPLY": e589.get("FREE_SUPPLY"), "FREE_PER_WALLET": e589.get("FREE_PER_WALLET"),
    "FREE_MODE": e589.get("FREE_MODE"), "freeMinted": e589.get("freeMinted"),
    "freeRemaining": e589.get("freeRemaining"), "isFreeOpen": e589.get("isFreeOpen"),
    "saleStart": e589.get("saleStart"), "saleStartWib": "2026-11-13 13:51:55 WIB",
    "saleEnd": e589.get("saleEnd"), "saleEndWib": "2026-11-15 13:51:55 WIB",
    "saleOpen": e589.get("saleOpen"), "mintOpen": e589.get("mintOpen"),
    "MAX_SUPPLY": e589.get("MAX_SUPPLY"), "paidSupply": e589.get("paidSupply"),
    "PRICE": e589.get("PRICE"), "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "freeAvailable_user": e589.get("freeAvailable_user"), "balanceOf_user": e589.get("balanceOf_user"),
    "sourcifyVerifiedAt": "2026-11-13T06:32:07Z", "sourcifyMatch": "exact_match",
    "firstSeenWib": "2026-11-13 ~13:32 WIB",
    "ageVerified": True,
    "ageNote": "saleStart on-chain 1794552715 = 13:51:55 WIB 13 Nov; saleEnd 15 Nov 13:51:55 WIB (durasi 48 jam). Belum buka saat ditemukan (totalSupply 0, isFreeOpen 0, saleOpen 0).",
    "agentShapeNote": "S1 PASS: Sourcify exact_match, 84 fns (mint/mintFree/claimFree/freeMint + quote/costOf + free views FREE_SUPPLY/freeMinted/freeRemaining/freeAvailable/isFreeOpen + agentIdRegistry()=registry Binance 0x60B926...22F). contractURI data: JSON: 500 edisi, 325 free (1/wallet, FCFS) + 175 paid @ 0,0005 BNB, fully on-chain; kontrak tercetak di deskripsi contractURI.",
    "website": None, "websiteVerified": False,
    "websiteNote": "Website/X BELUM ditemukan run ini: pencarian nama 'Mossbound Key' + alamat kontrak (search index) hanya hasil tak terkait (color-picker/game); metadata Sourcify tanpa URL; contractURI data: JSON tanpa external link. Gate website UNVERIFIED - TIDAK boleh preview/mint sampai website terverifikasi (cek ulang saat sale buka).",
    "xVerified": False,
    "freePct": 0.0,
    "lastReadBlock": BLK, "lastReadWib": WIB,
    f"runNote{RUN}": "Run 1331: BARU ditemukan via Sourcify feed (verifiedAt 06:32:07Z). Agent-shaped S1 PASS, 325 free/500, saleStart 13:51:55 WIB hari ini (~12 mnt lagi saat run) - BELUM BUKA (totalSupply 0, isFreeOpen 0, saleOpen 0, freeAvailable_user 0) -> watchlist-only-UPCOMING, BUKAN early lead (0 mint pertama), BUKAN kandidat/strong lead, TIDAK di-preview/di-mint. Website/X UNVERIFIED. Pantau hot-leg + run 1401 saat sale buka.",
}
# --- Feed-checked non-leads this run ---
TC["Feed-0x4008"] = {"address": "0x40089b364a93F8d71208B77b2293255C72791878",
    "status": "checked-not-sale-shape-2026-11-13",
    "note": "Run 1331 Sourcify feed (verifiedAt 2026-11-13T06:31:03Z): ABI 21 fns, TANPA mint/quote/free view/agent ref. GAGAL S1/S2 dan BUKAN early lead. Dicatat checked saja.",
    "lastReadWib": WIB}
TC["Boltbook-0xc972"] = {"address": "0xc972e47d067664effb42ea9f1a2ca667065e4c17",
    "status": "checked-not-agent-shaped-2026-11-13",
    "note": "Run 1331 Boltbook-new (EN+ZH, 11 alamat): Xeno Agent (XENOAGENT), Sourcify unverified, totalSupply 9901/10000, price 0,001 BNB, TANPA free view/agent ref. BUKAN agent-shaped, BUKAN lead. Dicatat checked saja.",
    "lastReadWib": WIB}
snap[f"runNote{RUN}"] = ("Run 1331 (13:31-13:40 WIB, blok 133304615, baca kontrak 21 target sukses, PX24 batch-fail nilai lama dipertahankan): "
    "1 SELLOUT DILAPORKAN SEKALI (JNTM track-C lead free 1000/1000 = 100%%, freeLeft 0, totalMinted 1087; dihapus dari track_c); "
    "1 BARU UPCOMING (Mossbound Key 0xe589, S1 PASS agent-shaped, 325 free/500, sale buka 13:51:55 WIB hari ini, totalSupply 0 - watchlist-only, TIDAK dilaporkan sebagai lead/kandidat); "
    "0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead baru, 0 perubahan track-B, 0 age-exclusion baru. "
    "Royal Rush 530/1000=53,0% (+24/30 mnt, 0,80/mnt vs baseline 7,74 = 0,10x -> velocity GAGAL, umur+X unverified) -> BUKAN kandidat/strong lead; "
    "Agentx 716/1111=64,5% (+4, velocity GAGAL), gate-blocked; Zero 269/500=53,8% (+6, velocity GAGAL); OLIVER 931/1000=93,1% umur TETAP UNVERIFIED; "
    "OBFG 672/1230=54,6% gate-blocked; AgentLabs 2160 spesimen; binanceai launched=0 (pending).")
snap[f"runNote{RUN}_jntm"] = jntm_note
snap[f"runNote{RUN}_scan"] = ("Run 1331 scan leg FAST-FAIL: Ankr pre-flight HTTP 401 Unauthorized (outage Ankr sejak 2026-11-09 berlanjut; run 1301 timeout, run ini kembali 401). "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap[f"runNote{RUN}_discovery"] = ("Run 1331 discovery: Sourcify feed 20 kontrak (verifiedAt 05:45:01-06:32:07Z), 2 baru vs hot-leg-seen: "
    "0xe589 Mossbound Key (84 fns, S1 TRUE -> verifikasi penuh, upcoming, lihat runNote1331_mossbound) dan 0x40089b (21 fns, S1 false, checked saja); "
    "Boltbook EN 44.941 B / ZH 43.079 B, 1 baru: Xeno Agent 0xc972 (Sourcify unverified, 9901/10000, price 0,001 BNB, tanpa free/agent) -> BUKAN agent-shaped, dicatat saja; "
    "sweep: pencarian 'Mossbound Key' + alamat kontrak (search index) 0 hasil relevan; proyek lain yang dikenal semua >24 jam / sudah dicek; "
    "Odaily newsflash EN: 0 item Agent ID/free-mint (semua makro/pasar); bridge 116 kontrak, 7 same-owner-discarded - sama seperti run 1301, tanpa promosi/perubahan.")
snap[f"runNote{RUN}_mossbound"] = ("Mossbound Key 0xe589A94316C68d4A4f008f841Deb7e9612445244 (MSKY): Sourcify exact_match verifiedAt 2026-11-13T06:32:07Z, 84 fns, S1 PASS "
    "(mint/mintFree/claimFree/freeMint + quote/costOf + FREE_SUPPLY/freeMinted/freeRemaining/freeAvailable/isFreeOpen + agentIdRegistry()=registry Binance). "
    "Baca ulang on-chain chunked (batch 40-call GAGAL total - semua view null; baca ulang per 8 call berhasil): name Mossbound Key, totalSupply 0, totalMinted 0, "
    "FREE_SUPPLY 325, FREE_PER_WALLET 1, FREE_MODE 2, freeMinted 0, freeRemaining 0, isFreeOpen 0, saleOpen 0, mintOpen 0, saleStart 1794552715 = 13:51:55 WIB 13 Nov, "
    "saleEnd 1794725515 = 15 Nov 13:51:55 WIB, MAX_SUPPLY 500, paidSupply 175 @ 0,0005 BNB, freeAvailable_user 0, quote(user,1) = (0,0,0). "
    "contractURI: 500 edisi, 325 free (1/wallet FCFS) + 175 paid, fully on-chain. Website/X: TIDAK ditemukan (nama + alamat kontrak di search index nihil; metadata Sourcify tanpa URL; "
    "contractURI tanpa external link) -> gate UNVERIFIED. Status: watchlist-only-UPCOMING; pantau hot-leg + run 1401 saat sale buka 13:51 WIB.")
snap["last_run_wib"] = WIB
snap["timestamp_wib"] = WIB
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; backup onchain-snapshot-2026-11-13-1331.bak; JNTM removed:", jntm_note is not None)
