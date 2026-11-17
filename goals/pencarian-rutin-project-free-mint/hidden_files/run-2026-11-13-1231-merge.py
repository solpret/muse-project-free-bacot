#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 12:31 WIB.
Reads run-2026-11-13-1231-verify.json + discovery.json, updates
onchain-snapshot.json (backup first). REPORTABLE CHANGE: NONE - silent run.
No new candidate / strong lead / early lead / track-B change / track-C lead.
Royal Rush 463/1000 (46.3%, +50/30 mnt = 1.67/mnt vs baseline 7.74 = 0.22x)
velocity FAIL, age unverified; Zero 259/500 = 51.8% (+8, <20 token) velocity
FAIL, X/website unverified; Agentx 707/1111 = 63.6% velocity FAIL, gate-blocked
already reported; OLIVER 927/1000 = 92.7% age TETAP UNVERIFIED (no promotion);
JNTM free 491/1000 opened=0 quote NULL; OBFG 667/1230 = 54.2% gate-blocked;
binanceai launched=0 (pending). Ankr pre-flight FAIL 401 (outage since 9 Nov)
- scan leg fast-fail, watermark unchanged (132512564). Discovery: Sourcify
feed 20, 0 new vs hot-leg-seen; Boltbook EN retry 46,417 B (16 addrs) / ZH
42,244 B (15 addrs), 0 new vs hot-leg-seen. Web sweep: no new <24h item
(Agentic Gangster / STAMP PASS / RIGBYPASS / MOLT / AGENT COSMOS all known
and/or >24h). Bridge: 116 contracts / 7 same-owner-discarded - unchanged vs
run 1201, no promotion. Velocity convention: previousRatePerMin frozen as
stored (same as runs 0931/1001/1031/1101/1201; question flagged for parent,
NOT changed).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1231"
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
WIB = "2026-11-13 ~12:35 WIB"
BLK = v.get("block")
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
a["runNote1231"] = ("Run 1231: totalMinted %s->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); umur ~13,4 jam <24 jam; "
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
z["runNote1231"] = ("Run 1231: totalMinted %s->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/500 = %.1f%% - TETAP di atas 50%% (259/500), TAPI velocity GAGAL + X/website UNVERIFIED -> BUKAN kandidat; <70%% -> BUKAN strong lead; slot terbuka; umur ~4,7 jam <24 jam - DIAM."
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
o["runNote1231"] = ("Run 1231: totalSupply %s->%s (+%s), freeMinted %s->%s/1000 = %.1f%%; velocity GAGAL (<20 token); "
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
r["runNote1231"] = ("Run 1231: freeMinted %s->%s/1000 = %.1f%% (+%s dalam ~30 mnt, ~%.2f/mnt vs baseline 7,74 = %.2fx -> velocity GAGAL, melambat); "
    "totalSupply %s, paidMinted %s; masih <50%% kandidat + <70%% strong lead; umur launch TETAP UNVERIFIED; X UNVERIFIED; slot user TERBUKA "
    "(freeClaimedByAgent=0, bal 0); BUKAN kandidat/strong lead; monitor run berikut."
    % (prev_fm, new_fm, 100.0 * new_fm / 1000, minted, rate, ratio or 0, new_ts, r["paidMinted"]))
# --- AgentLabs ---
al = C["AgentLabs"]; prev = al.get("totalSpecimens")
al["previousTotalSpecimens"] = prev; al["totalSpecimens"] = S("AgentLabs").get("totalSpecimens")
al["lastReadBlock"] = BLK; al["lastReadWib"] = WIB
al["runNote1231"] = "Run 1231: totalSpecimens %s->%s (experiment 2 berjalan); DIAM." % (prev, al["totalSpecimens"])
# --- OUTY ---
ou = C["OUTY"]; ou["freeSold"] = S("OUTY").get("freeSold"); ou["minted"] = S("OUTY").get("minted")
ou["lastReadBlock"] = BLK; ou["lastReadWib"] = WIB
ou["runNote1231"] = "Run 1231: freeSold 20->21/1500; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; DIAM."
# --- MECHA ---
m = C["MECHA"]; prev = m.get("freeClaimed")
m["previousTotalMinted"] = m.get("totalMinted"); m["totalMinted"] = S("MECHA").get("totalMinted")
m["freeClaimed"] = S("MECHA").get("freeClaimed")
m["lastReadBlock"] = BLK; m["lastReadWib"] = WIB
m["runNote1231"] = "Run 1231: freeClaimed %s->%s/4444 = %.1f%% (<50%%); DIAM." % (prev, m["freeClaimed"], 100.0 * m["freeClaimed"] / 4444)
# --- Pickgrid ---
p = C["Pickgrid"]; p["freeMinted"] = S("Pickgrid").get("freeMinted")
p["lastReadBlock"] = BLK; p["lastReadWib"] = WIB
p["runNote1231"] = "Run 1231: freeMinted 216/300 FLAT, umur UNVERIFIED; DIAM."
# --- PX24 group ---
for key, name in [("PX24","PX24"),("SKRR","SKRR"),("ME30","ME30"),("CY24","CY24")]:
    e = C[key]; prev = e.get("totalSupply"); new = S(name).get("totalSupply")
    e["previousTotalSupply"] = prev; e["totalSupply"] = new
    e["lastReadBlock"] = BLK; e["lastReadWib"] = WIB
    e["runNote1231"] = "Run 1231: totalSupply %s->%s (%+d), umur TETAP UNVERIFIED; DIAM." % (prev, new, new - prev)
# --- HIVE Agents ---
h = C["HIVE Agents"]; h["totalSupply"] = S("HIVE").get("totalSupply")
h["lastReadBlock"] = BLK; h["lastReadWib"] = WIB
h["runNote1231"] = "Run 1231: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user; DIAM."
# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]; prev_fc = j["freeClaimed"]
j["freeClaimed"] = S("JNTM").get("freeClaimed"); j["freeLeft"] = S("JNTM").get("freeLeft")
j["totalMinted"] = S("JNTM").get("totalMinted"); j["paidMinted"] = S("JNTM").get("paidMinted")
j["opened"] = S("JNTM").get("opened")
j["lastReadBlock"] = BLK; j["lastReadWib"] = WIB
j["runNote1231"] = ("Run 1231: free %s->%s/1000 = %.1f%% (+%s); paidMinted 68 FLAT (totalMinted %s); quote(address,uint256) TETAP NULL; "
    "opened=0; slot terbuka; umur ~6,4 jam (mintStart 06:13 WIB). Gate PENDING (L) + quote NULL - tanpa perubahan tier; DIAM."
    % (prev_fc, j["freeClaimed"], 100.0 * j["freeClaimed"] / 1000, j["freeClaimed"] - prev_fc, j["totalMinted"]))
ob = TC["OBFG"]; prev_fm = ob["freeMinted"]
ob["previousTotalMinted"] = ob.get("totalMinted"); ob["totalMinted"] = S("OBFG").get("totalMinted")
ob["freeMinted"] = S("OBFG").get("freeMinted")
ob["freePct"] = round(100.0 * ob["freeMinted"] / 1230, 1)
ob["lastReadBlock"] = BLK; ob["lastReadWib"] = WIB
ob["runNote1231"] = ("Run 1231: %s->%s/1230 = %.1f%% (+%s), umur ~16,6 jam (saleStart 20:01 WIB 12 Nov) <24 jam, slot terbuka (freeAvailable=1); "
    "gate-blocked SUDAH dilaporkan 12 Nov; DIAM." % (prev_fm, ob["freeMinted"], ob["freePct"], ob["freeMinted"] - prev_fm))
nv = TC["NOTV"]; nv["totalMinted"] = S("NOTV").get("totalMinted")
nv["lastReadBlock"] = BLK; nv["lastReadWib"] = WIB
nv["runNote1231"] = "Run 1231: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka; DIAM."
am = TC["AgentMuse"]; prev_fc = am["freeClaimed"]
am["freeClaimed"] = S("AgentMuse").get("freeClaimed")
am["bookedOf_user"] = S("AgentMuse").get("bookedOf_user")
am["lastReadBlock"] = BLK; am["lastReadWib"] = WIB
am["runNote1231"] = "Run 1231: freeClaimed %s->%s/888 = %.1f%%, bookedOf(user)=FREE_OSK utuh; minted-by-user; DIAM." % (prev_fc, am["freeClaimed"], 100.0 * am["freeClaimed"] / 888)
# --- DragonAgent + BC1B ---
da = C["Dragon Agent"]; prev = da.get("totalSupply"); da["totalSupply"] = S("DragonAgent").get("totalSupply")
da["runNote1231"] = "Run 1231: totalSupply %s->%s (+%s); free views NULL -> free %% UNVERIFIED; DIAM." % (prev, da["totalSupply"], da["totalSupply"] - prev if prev is not None else "?")
da["lastReadBlock"] = BLK; da["lastReadWib"] = WIB
bc = TC.get("RESUME-BC1B")
if bc is not None:
    prev = bc.get("freeCount"); bc["freeCount"] = S("BC1B").get("freeCount")
    bc["runNote1231"] = "Run 1231: freeCount %s->%s; DIAM." % (prev, bc["freeCount"])
    bc["lastReadBlock"] = BLK; bc["lastReadWib"] = WIB
# --- pending_claims: keep binanceai.fun pending (launched=0 read fresh) ---
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
pc["launched"] = S("BinanceAI-mint").get("launched")
pc["tokenClaimed_user"] = S("BinanceAI-mint").get("tokenClaimed_user")
pc["lastReadWib"] = WIB
snap["pending_claims"] = {"binanceai.fun": pc}
snap["runNote1231"] = ("Run 1231 (12:31-12:35 WIB, blok 133296524, baca kontrak 21 target sukses via dataseed): "
    "SILENT - 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead baru, 0 perubahan track-B, 0 age-exclusion baru. "
    "Zero 259/500=51,8% (+8, 0,27/mnt vs prev 2,42 = 0,11x, <20 token -> velocity GAGAL, X/website unverified) -> BUKAN kandidat/strong lead; "
    "Royal Rush 463/1000=46,3% (+50/30 mnt, 1,67/mnt vs baseline 7,74 = 0,22x -> velocity GAGAL, melambat; umur+X unverified); "
    "Agentx 707/1111=63,6% (+8, <20 token -> velocity GAGAL), gate-blocked; OLIVER 927/1000=92,7% umur TETAP UNVERIFIED (tidak bisa promosi); "
    "JNTM free 491/1000 opened=0 quote NULL; OBFG 667/1230=54,2% gate-blocked; binanceai launched=0 (pending).")
snap["runNote1231_scan"] = ("Run 1231 scan leg FAST-FAIL: Ankr pre-flight 1 chunk 50 blok HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09, ~4,7 hari). Watermark TETAP 132512564; gap ke head terus tumbuh. 5c dilewati (tanpa output scan).")
snap["runNote1231_discovery"] = ("Run 1231 discovery: Sourcify feed 20, 0 baru vs hot-leg-seen (hot-leg 1224 sudah mencatat 7 baru, semua probe-not-sale-shape); "
    "Boltbook EN retry 46.417 B (16 alamat) / ZH 42.244 B (15 alamat), 0 baru vs hot-leg-seen (fetch EN pertama 0 byte, retry berhasil); "
    "sweep web EN: 0 baru <24 jam (Agentic Gangster/STAMP PASS/RIGBYPASS/MOLT/AGENT COSMOS semua sudah dikenal dan/atau >24 jam; UFO/NEBULA/MALTA/YAMA lama); "
    "bridge 116 kontrak, 7 same-owner-discarded, tanpa promosi/perubahan.")
snap["last_run_wib"] = "2026-11-13 ~12:35 WIB"
snap["timestamp_wib"] = "2026-11-13 ~12:35 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; backup onchain-snapshot-2026-11-13-1231.bak")
