#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 13:01 WIB.
Reads run-2026-11-13-1301-verify.json + discovery.json + triage/probe/koma
files, updates onchain-snapshot.json (backup first).
REPORTABLE CHANGE: 1 SELLOUT - Steady free pool 555/555 habis (early lead
dilaporkan 12 Nov; umur+website+X tetap UNVERIFIED; slot user hilang).
Lapor sekali + hapus dari snapshot.
Lainnya DIAM: 0 kandidat baru, 0 strong lead baru, 0 early lead baru,
0 track-C lead baru, 0 perubahan track-B, 0 age-exclusion baru selain
KOMA (koreksi vonis 1831 + age-excluded diam, tidak pernah jadi lead).
Royal Rush 506/1000 = 50,6% (lewat 50%) TAPI velocity GAGAL + umur
UNVERIFIED -> BUKAN kandidat/strong lead; TIDAK dilaporkan (preseden
Zero run 1231: crossing 50% saja bukan perubahan yang dilaporkan).
Pre-flight FAIL (timeout, bukan 401 biasa) - scan leg fast-fail, watermark
tetap 132512564. Discovery: Sourcify feed fetch pertama 0 byte (gagal),
retry berhasil 20 kontrak (verifiedAt 05:34:22-06:03:26Z), 3 baru vs
hot-leg-seen, semua probe-not-sale-shape (0xbFe7 12 fns S1 false; 0x3cD0
token pajak 62 fns S1 false; 0xf597 code 86 byte, no hit). Boltbook EN
44.318 B / ZH 42.709 B, 1 baru: Zephyr Agent 0x14d8 (Sourcify unverified,
probe mint+price saja, tanpa free/agent; totalSupply 9901/10000) -> BUKAN
agent-shaped, dicatat saja. Sweep EN+ZH: 0 baru <24 jam; KOMA ditemukan
lagi via sweep ZH - triase ulang membatalkan vonis 1831 (ternyata
agent-shaped + free views ada) TAPI MINT_START 11 Nov 21:00 WIB (umur
~40 jam > 24 jam) + free publik 500/500 HABIS -> age-excluded, diam.
Odaily newsflash EN: 0 item Agent ID/free-mint.
Velocity convention: previousRatePerMin frozen as stored (runs 0931-1231).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1301"
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
WIB = "2026-11-13 ~13:10 WIB"
BLK = 133304499
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
a["runNote1301"] = ("Run 1301: totalMinted %s->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); umur ~14,0 jam (mintOpensAt 23:11 WIB 12 Nov) <24 jam; "
    "gate website GAGAL (sudah dilaporkan 08:01 + hot-leg 08:29) - DIAM." % (prev_tm, new_tm, minted, rate, ratio or 0, a["freeMinted"], a["freePct"]))
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
z["runNote1301"] = ("Run 1301: totalMinted %s->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/500 = %.1f%%, TAPI velocity GAGAL + X/website UNVERIFIED -> BUKAN kandidat; <70%% -> BUKAN strong lead; slot terbuka; umur ~5,1 jam (mintOpensAt 07:55 WIB) <24 jam - DIAM."
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
o["runNote1301"] = ("Run 1301: totalSupply %s->%s (+%s), freeMinted %s->%s/1000 = %.1f%%; velocity GAGAL (<20 token); "
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
r["runNote1301"] = ("Run 1301: freeMinted %s->%s/1000 = %.1f%% (+%s dalam ~30 mnt, ~%.2f/mnt vs baseline 7,74 = %.2fx -> velocity GAGAL, melambat); "
    "totalSupply %s, paidMinted %s; LEWAT 50%% TAPI velocity GAGAL + umur launch TETAP UNVERIFIED + X UNVERIFIED -> BUKAN kandidat (<70%% juga, bukan strong lead); "
    "crossing 50%% saja TIDAK dilaporkan (preseden Zero run 1231); slot user TERBUKA (freeClaimedByAgent=0, bal 0); monitor run berikut."
    % (prev_fm, new_fm, 100.0 * new_fm / 1000, minted, rate, ratio or 0, new_ts, r["paidMinted"]))
# --- Steady: SELLOUT free pool -> remove ---
st = C.pop("Steady", None)
steady_note = None
if st is not None:
    prev_fc = st.get("freeClaimed")
    steady_note = ("Run 1301 SELLOUT: Steady 0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf freeClaimed %s->555/555 = 100%% (totalSupply 557, "
        "FREE_SUPPLY 555, MAX_SUPPLY 1111); free pool HABIS, slot user hilang (freeUsed_user=0 tapi pool 0). Early lead dilaporkan sekali run 2231 (12 Nov); "
        "umur launch TETAP UNVERIFIED + website/X UNVERIFIED sampai akhir (tidak pernah promosi). Dilaporkan sekali run ini + dihapus dari snapshot."
        % (prev_fc,))
    snap.setdefault("sellouts", []).append({"name": "Steady", "address": "0x4919afF275a3cf126A8F9fD280Ae8Cd24D734cCf",
        "track": "A", "reason": "sellout-free-pool", "evidence": steady_note, "reported_once": True, "removed_wib": WIB})
# --- AgentLabs ---
al = C["AgentLabs"]; prev = al.get("totalSpecimens")
al["previousTotalSpecimens"] = prev; al["totalSpecimens"] = S("AgentLabs").get("totalSpecimens")
al["lastReadBlock"] = BLK; al["lastReadWib"] = WIB
al["runNote1301"] = "Run 1301: totalSpecimens %s->%s (experiment 2 berjalan; genesisStart 21:04 WIB 12 Nov, deadline umur 21:04 WIB 13 Nov belum lewat); DIAM." % (prev, al["totalSpecimens"])
# --- OUTY ---
ou = C["OUTY"]; ou["freeSold"] = S("OUTY").get("freeSold"); ou["minted"] = S("OUTY").get("minted")
ou["lastReadBlock"] = BLK; ou["lastReadWib"] = WIB
ou["runNote1301"] = "Run 1301: freeSold 21/1500 FLAT; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; DIAM."
# --- MECHA ---
m = C["MECHA"]; prev = m.get("freeClaimed")
m["previousTotalMinted"] = m.get("totalMinted"); m["totalMinted"] = S("MECHA").get("totalMinted")
m["freeClaimed"] = S("MECHA").get("freeClaimed")
m["lastReadBlock"] = BLK; m["lastReadWib"] = WIB
m["runNote1301"] = "Run 1301: freeClaimed %s->%s/4444 = %.1f%% (<50%%); DIAM." % (prev, m["freeClaimed"], 100.0 * m["freeClaimed"] / 4444)
# --- Pickgrid ---
p = C["Pickgrid"]; p["freeMinted"] = S("Pickgrid").get("freeMinted")
p["lastReadBlock"] = BLK; p["lastReadWib"] = WIB
p["runNote1301"] = "Run 1301: freeMinted 216/300 FLAT, umur UNVERIFIED; DIAM."
# --- PX24 group (PX24 read FAILED this run -> keep old value) ---
for key, name in [("PX24","PX24"),("SKRR","SKRR"),("ME30","ME30"),("CY24","CY24")]:
    e = C[key]; prev = e.get("totalSupply"); new = S(name).get("totalSupply")
    if new is None:
        e["runNote1301"] = "Run 1301: BACA GAGAL (batch-fail, nilai lama dipertahankan, BUKAN nol); umur TETAP UNVERIFIED; DIAM."
    else:
        e["previousTotalSupply"] = prev; e["totalSupply"] = new
        e["runNote1301"] = "Run 1301: totalSupply %s->%s (%+d), umur TETAP UNVERIFIED; DIAM." % (prev, new, new - prev)
    e["lastReadBlock"] = BLK; e["lastReadWib"] = WIB
# --- HIVE Agents ---
h = C["HIVE Agents"]; h["totalSupply"] = S("HIVE").get("totalSupply")
h["lastReadBlock"] = BLK; h["lastReadWib"] = WIB
h["runNote1301"] = "Run 1301: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user; DIAM."
# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]; prev_fc = j["freeClaimed"]
j["freeClaimed"] = S("JNTM").get("freeClaimed"); j["freeLeft"] = S("JNTM").get("freeLeft")
j["totalMinted"] = S("JNTM").get("totalMinted"); j["paidMinted"] = S("JNTM").get("paidMinted")
j["opened"] = S("JNTM").get("opened")
j["lastReadBlock"] = BLK; j["lastReadWib"] = WIB
j["runNote1301"] = ("Run 1301: free %s->%s/1000 = %.1f%% (+%s); paidMinted 68 FLAT (totalMinted %s); quote(address,uint256) TETAP NULL; "
    "opened=0; slot terbuka; umur ~6,8 jam (mintStart 06:13 WIB). Gate PENDING (L) + quote NULL - tanpa perubahan tier; DIAM."
    % (prev_fc, j["freeClaimed"], 100.0 * j["freeClaimed"] / 1000, j["freeClaimed"] - prev_fc, j["totalMinted"]))
ob = TC["OBFG"]; prev_fm = ob["freeMinted"]
ob["previousTotalMinted"] = ob.get("totalMinted"); ob["totalMinted"] = S("OBFG").get("totalMinted")
ob["freeMinted"] = S("OBFG").get("freeMinted")
ob["freePct"] = round(100.0 * ob["freeMinted"] / 1230, 1)
ob["lastReadBlock"] = BLK; ob["lastReadWib"] = WIB
ob["runNote1301"] = ("Run 1301: %s->%s/1230 = %.1f%% (+%s), umur ~17,1 jam (saleStart 20:01 WIB 12 Nov) <24 jam, slot terbuka (freeAvailable=1); "
    "gate-blocked SUDAH dilaporkan 12 Nov; DIAM." % (prev_fm, ob["freeMinted"], ob["freePct"], ob["freeMinted"] - prev_fm))
nv = TC["NOTV"]; nv["totalMinted"] = S("NOTV").get("totalMinted")
nv["lastReadBlock"] = BLK; nv["lastReadWib"] = WIB
nv["runNote1301"] = "Run 1301: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka; DIAM."
am = TC["AgentMuse"]; prev_fc = am["freeClaimed"]
am["freeClaimed"] = S("AgentMuse").get("freeClaimed")
am["bookedOf_user"] = S("AgentMuse").get("bookedOf_user")
am["lastReadBlock"] = BLK; am["lastReadWib"] = WIB
am["runNote1301"] = "Run 1301: freeClaimed %s->%s/888 = %.1f%%, bookedOf(user)=FREE_OSK utuh; minted-by-user; DIAM." % (prev_fc, am["freeClaimed"], 100.0 * am["freeClaimed"] / 888)
# --- DragonAgent + BC1B ---
da = C["Dragon Agent"]; prev = da.get("totalSupply"); da["totalSupply"] = S("DragonAgent").get("totalSupply")
da["runNote1301"] = "Run 1301: totalSupply %s->%s (+%s); free views NULL -> free %% UNVERIFIED; DIAM." % (prev, da["totalSupply"], da["totalSupply"] - prev if prev is not None else "?")
da["lastReadBlock"] = BLK; da["lastReadWib"] = WIB
bc = TC.get("RESUME-BC1B")
if bc is not None:
    prev = bc.get("freeCount"); bc["freeCount"] = S("BC1B").get("freeCount")
    bc["runNote1301"] = "Run 1301: freeCount %s->%s; DIAM." % (prev, bc["freeCount"])
    bc["lastReadBlock"] = BLK; bc["lastReadWib"] = WIB
# --- KOMA: correct 1831 verdict + age-exclusion (silent, never a lead) ---
koma_note = ("KOREKSI run 1301: vonis run 1831 '0xef48 (64 fns, mint tanpa free/agent)' SALAH - baca ulang ABI segar: free views ADA "
    "(FREE_PUBLIC_SHARES 500, FREE_WHITELIST_SHARES 300, freePublicMinted, freeWhitelistMinted, freeClaimedByWallet), quote quoteFor, "
    "agent link via idCollection()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (sebagai uint). Bentuk sale S1 TERPENUHI + website komaagent.fun "
    "mencetak kontrak. TAPI MINT_START on-chain 1794405600 = 2026-11-11 21:00 WIB -> umur ~40 jam > 24 jam, DAN free publik 500/500 HABIS "
    "(freePublicMinted 500; WL 6/300; paidMinted 11; totalMinted 517; saleDeadline 16 Nov 21:00 WIB; user freeClaimedByWallet=0). "
    "AGE-EXCLUDED + free pool habis; tidak pernah dilaporkan sebagai lead -> DIAM (tanpa laporan chat), dicatat di sini + age_exclusions.")
fw = TC.get("Feed-wave-1831-2026-11-11")
if fw is not None:
    fw["note"] = (fw.get("note", "") + " " + koma_note)
    fw["lastReadWib"] = WIB
snap.setdefault("age_exclusions", []).append({"name": "KOMA Agent", "address": "0xef4882e029b8d58F81960c433D852a5b0A352965",
    "track": "C", "reason": "age-excluded", "evidence": koma_note, "reported_once": False, "removed_wib": WIB})
# --- pending_claims: binanceai.fun still pending (launched=0) ---
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
pc["launched"] = S("BinanceAI-mint").get("launched")
pc["tokenClaimed_user"] = S("BinanceAI-mint").get("tokenClaimed_user")
pc["lastReadWib"] = WIB
snap["pending_claims"] = {"binanceai.fun": pc}
snap["runNote1301"] = ("Run 1301 (13:01-13:10 WIB, blok ~133304499, baca kontrak 22 target sukses, PX24 batch-fail nilai lama dipertahankan): "
    "1 SELLOUT DILAPORKAN SEKALI (Steady free 555/555 = 100%%, early lead 12 Nov, dihapus dari snapshot); 0 kandidat baru, 0 strong lead baru, "
    "0 early lead baru, 0 track-C lead baru, 0 perubahan track-B, 0 age-exclusion baru yang dilaporkan (KOMA age-excluded diam - tidak pernah jadi lead). "
    "Royal Rush 506/1000=50,6% (lewat 50%, +43/30 mnt, 1,43/mnt vs baseline 7,74 = 0,18x -> velocity GAGAL, umur+X unverified) -> BUKAN kandidat/strong lead, TIDAK dilaporkan; "
    "Agentx 712/1111=64,1% (+5, velocity GAGAL), gate-blocked; Zero 263/500=52,6% (+4, velocity GAGAL); OLIVER 929/1000=92,9% umur TETAP UNVERIFIED; "
    "JNTM free 539/1000 opened=0 quote NULL; OBFG 669/1230=54,4% gate-blocked; AgentLabs 2125 spesimen; binanceai launched=0 (pending).")
snap["runNote1301_steady"] = steady_note
snap["runNote1301_scan"] = ("Run 1301 scan leg FAST-FAIL: Ankr pre-flight 1 chunk 50 blok TIMEOUT (bukan 401 biasa - error 'timed out'; outage Ankr sejak 2026-11-09 berlanjut). "
    "Watermark TIDAK dimajukan (tetap 132512564); gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1301_discovery"] = ("Run 1301 discovery: Sourcify feed fetch pertama 0 byte (gagal), retry berhasil 20 kontrak (verifiedAt 05:34:22-06:03:26Z), "
    "3 baru vs hot-leg-seen, semua probe-not-sale-shape (0xbFe7 12 fns S1 false; 0x3cD0 token pajak 62 fns S1 false; 0xf597 code 86 byte, no hit); "
    "Boltbook EN 44.318 B / ZH 42.709 B, 1 baru: Zephyr Agent 0x14d8 (Sourcify unverified, probe mint+price saja tanpa free/agent, totalSupply 9901/10000) -> BUKAN agent-shaped, dicatat saja; "
    "sweep EN+ZH: 0 baru <24 jam (Agentic Gangster/STAMP/RIGBYPASS/MOLT/AGENT COSMOS/WNO/UFO/NEBULA/NOVRA/Grove semua dikenal dan/atau >24 jam; BN Agent Trials musim 25 Okt-8 Nov, >24 jam); "
    "KOMA ditemukan lagi via sweep ZH -> triase ulang (lihat runNote1301_koma); Odaily newsflash EN: 0 item Agent ID/free-mint (semua makro/Nvidia/BTC); "
    "bridge 116 kontrak, 1 not-in-snapshot menurut hitung alamat (PIXEL BOYZ 0xafb5 - sudah ada di snapshot, selisih cara hitung saja), 7 same-owner-discarded, tanpa promosi/perubahan.")
snap["runNote1301_koma"] = koma_note
snap["last_run_wib"] = WIB
snap["timestamp_wib"] = WIB
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; backup onchain-snapshot-2026-11-13-1301.bak; Steady removed:", steady_note is not None)
