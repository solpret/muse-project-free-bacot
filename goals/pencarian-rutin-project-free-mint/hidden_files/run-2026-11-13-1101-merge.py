#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 11:01 WIB.
Reads run-2026-11-13-1101-verify.json + discovery.json + probe.json,
updates onchain-snapshot.json (backup first).
REPORTABLE CHANGE: NONE - silent run. No new candidate / strong lead /
early lead / track-B change / track-C lead. Royal Rush 246/1000 (24.6%)
rising fast (+240/31 mnt) but still <50% + age unverified; OLIVER 91.2%
still age-unverified; Agentx 61.7% velocity FAIL; KOMA age-excluded at
discovery (never reported -> silent). Ankr pre-flight FAIL 401 (outage
since 9 Nov) - scan leg fast-fail, watermark unchanged.
Velocity convention: same as runs 0931/1001/1031 (previousRatePerMin frozen
as stored; question flagged for parent, NOT changed here).
Pending-claims bookkeeping: snapshot pending_claims was {} although
binanceai.fun is still pending (launched=0) - RESTORED in this merge.
eth_blockNumber read failed transiently this run (empty response); block
recorded as unknown, contract reads all succeeded via dataseed."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1101"
v = json.load(open(BASE + f"run-2026-11-13-{RUN}-verify.json"))
reads = v["reads"]
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + f"onchain-snapshot-2026-11-13-{RUN}.bak")
C = snap["contracts"]; TC = snap["track_c"]
MIN = 31.0
def vel(prev, new, prev_rate):
    minted = (new - prev) if (prev is not None and new is not None) else None
    rate = (minted / MIN) if minted is not None else None
    ratio = (rate / prev_rate) if (rate is not None and prev_rate) else None
    passes = bool(minted is not None and minted >= 20 and ratio is not None and ratio >= 1.5)
    return minted, rate, ratio, passes
def S(n): return reads[n]["summary"]
# --- Agentx (address-keyed) ---
a = C["Agentx"]
new_tm = S("Agentx").get("totalMinted")
minted, rate, ratio, passes = vel(678, new_tm, a.get("previousRatePerMin") or 0.18)
a["previousTotalSupply"] = 678; a["totalMinted"] = new_tm
a["freeMinted"] = S("Agentx").get("freeMinted")
a["mintedInInterval"] = minted; a["intervalMinutes"] = MIN
a["currentRatePerMin"] = round(rate, 3) if rate is not None else None
a["velocityRatio"] = round(ratio, 2) if ratio is not None else None
a["velocityLegPasses"] = passes
a["lastReadBlock"] = None; a["lastReadWib"] = "2026-11-13 ~11:03 WIB"
a["freePct"] = round(100.0 * a["freeMinted"] / 1111, 1)
a["runNote1101"] = ("Run 1101: totalMinted 678->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); umur ~11,9 jam <24 jam; "
    "gate website GAGAL (sudah dilaporkan 08:01 + hot-leg 08:29) - DIAM." % (new_tm, minted, rate, ratio or 0, a["freeMinted"], a["freePct"]))
# --- Zero ---
z = C["Zero"]
new_tm = S("Zero").get("totalMinted")
minted, rate, ratio, passes = vel(231, new_tm, z.get("previousRatePerMin") or 2.42)
z["previousTotalSupply"] = 231; z["totalMinted"] = new_tm
z["freeMinted"] = S("Zero").get("freeMinted")
z["mintedInInterval"] = minted; z["intervalMinutes"] = MIN
z["currentRatePerMin"] = round(rate, 3) if rate is not None else None
z["velocityRatio"] = round(ratio, 2) if ratio is not None else None
z["velocityLegPasses"] = passes
z["lastReadBlock"] = None; z["lastReadWib"] = "2026-11-13 ~11:03 WIB"
z["runNote1101"] = ("Run 1101: totalMinted 231->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
    "free %s/500 = %.1f%% (<50%% kandidat, <70%% strong lead); slot terbuka; umur ~3,2 jam <24 jam; website UNVERIFIED - DIAM."
    % (new_tm, minted, rate, ratio or 0, z["freeMinted"], 100.0 * z["freeMinted"] / 500))
# --- Oliver Agents (name-keyed) ---
o = C["Oliver Agents"]
new_ts = S("OLIVER").get("totalSupply"); new_fm = S("OLIVER").get("freeMinted")
o["previousTotalSupply"] = 958; o["totalSupply"] = new_ts; o["freeMinted"] = new_fm
o["freeRemaining"] = S("OLIVER").get("freeRemaining")
o["mintedInInterval"] = new_ts - 958; o["intervalMinutes"] = MIN
o["currentRatePerMin"] = round((new_ts - 958) / MIN, 3)
o["velocityLegPasses"] = False
o["lastReadBlock"] = None; o["lastReadWib"] = "2026-11-13 ~11:03 WIB"
o["runNote1101"] = ("Run 1101: totalSupply 958->%s (+%s), freeMinted 908->%s/1000 = %.1f%%; velocity GAGAL (<20 token); "
    "umur launch TETAP UNVERIFIED -> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka; watchlist-only, DIAM."
    % (new_ts, new_ts - 958, new_fm, 100.0 * new_fm / 1000))
# --- Royal Rush Agents (name-keyed) ---
r = C["Royal Rush Agents"]
new_ts = S("RoyalRush").get("totalSupply"); new_fm = S("RoyalRush").get("freeMinted")
r["previousTotalSupply"] = 6; r["totalSupply"] = new_ts; r["freeMinted"] = new_fm
r["freeRemaining"] = S("RoyalRush").get("freeRemaining")
r["paidMinted"] = S("RoyalRush").get("paidMinted"); r["mintedCount"] = S("RoyalRush").get("mintedCount")
r["mintedInInterval"] = new_fm - 6; r["intervalMinutes"] = MIN
r["currentRatePerMin"] = round((new_fm - 6) / MIN, 2)
r["velocityBaselineNote"] = ("Run 1101: interval pertama sejak snapshot-add (1031: free 6); rate %.2f/mnt dicatat sebagai baseline, "
    "velocity TIDAK lulus sendirian (tanpa previous rate) per aturan body." % r["currentRatePerMin"])
r["velocityLegPasses"] = False
r["lastReadBlock"] = None; r["lastReadWib"] = "2026-11-13 ~11:03 WIB"
r["runNote1101"] = ("Run 1101: freeMinted 6->%s/1000 = %.1f%% (+%s dalam ~31 mnt, ~%.2f/mnt, naik cepat); totalSupply %s, paidMinted %s; "
    "masih <50%% kandidat + <70%% strong lead; umur launch TETAP UNVERIFIED; X UNVERIFIED; slot user TERBUKA (freeClaimedByAgent=0, bal 0); "
    "BUKAN kandidat/strong lead; monitor run berikut." % (new_fm, 100.0 * new_fm / 1000, new_fm - 6, r["currentRatePerMin"], new_ts, r["paidMinted"]))
# --- AgentLabs ---
al = C["AgentLabs"]
al["previousTotalSpecimens"] = 1822; al["totalSpecimens"] = S("AgentLabs").get("totalSpecimens")
al["lastReadBlock"] = None; al["lastReadWib"] = "2026-11-13 ~11:03 WIB"
al["runNote1101"] = "Run 1101: totalSpecimens 1822->%s (experiment 2 berjalan); DIAM." % al["totalSpecimens"]
# --- OUTY ---
ou = C["OUTY"]
ou["freeSold"] = S("OUTY").get("freeSold"); ou["minted"] = S("OUTY").get("minted")
ou["lastReadBlock"] = None; ou["lastReadWib"] = "2026-11-13 ~11:03 WIB"
ou["runNote1101"] = "Run 1101: freeSold 20 FLAT/1500; FREE_FEE 0,0001 BNB TETAP - BUKAN gas-only; DIAM."
# --- MECHA ---
m = C["MECHA"]
m["previousTotalMinted"] = 1914; m["totalMinted"] = S("MECHA").get("totalMinted")
m["freeClaimed"] = S("MECHA").get("freeClaimed")
m["lastReadBlock"] = None; m["lastReadWib"] = "2026-11-13 ~11:03 WIB"
m["runNote1101"] = "Run 1101: freeClaimed 1914/4444 = 43,1%% FLAT (<50%%); DIAM."
# --- Pickgrid ---
p = C["Pickgrid"]
p["freeMinted"] = S("Pickgrid").get("freeMinted")
p["lastReadBlock"] = None; p["lastReadWib"] = "2026-11-13 ~11:03 WIB"
p["runNote1101"] = "Run 1101: freeMinted 216/300 FLAT, umur UNVERIFIED; DIAM."
# --- PX24 group ---
for key, name in [("PX24","PX24"),("SKRR","SKRR"),("ME30","ME30"),("CY24","CY24")]:
    e = C[key]; prev = {"PX24":520,"SKRR":509,"ME30":270,"CY24":456}[key]
    new = S(name).get("totalSupply")
    e["previousTotalSupply"] = prev; e["totalSupply"] = new
    e["lastReadBlock"] = None; e["lastReadWib"] = "2026-11-13 ~11:03 WIB"
    e["runNote1101"] = "Run 1101: totalSupply %s->%s (%+d), umur TETAP UNVERIFIED; DIAM." % (prev, new, new - prev)
# --- HIVE Agents (name-keyed) ---
h = C["HIVE Agents"]
h["totalSupply"] = S("HIVE").get("totalSupply")
h["lastReadBlock"] = None; h["lastReadWib"] = "2026-11-13 ~11:03 WIB"
h["runNote1101"] = "Run 1101: totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user; DIAM."
# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]
j["freeClaimed"] = S("JNTM").get("freeClaimed"); j["freeLeft"] = S("JNTM").get("freeLeft")
j["totalMinted"] = S("JNTM").get("totalMinted"); j["paidMinted"] = S("JNTM").get("paidMinted")
j["opened"] = S("JNTM").get("opened")
j["lastReadBlock"] = None; j["lastReadWib"] = "2026-11-13 ~11:03 WIB"
j["runNote1101"] = ("Run 1101: free 430->%s/1000 = %.1f%% (+36); paidMinted 68 FLAT (totalMinted %s); quote(address,uint256) TETAP NULL; "
    "opened=0; slot terbuka; umur ~4,9 jam (mintStart 06:13 WIB). Gate PENDING (L) + quote NULL - tanpa perubahan tier; DIAM."
    % (j["freeClaimed"], 100.0 * j["freeClaimed"] / 1000, j["totalMinted"]))
ob = TC["OBFG"]
ob["previousTotalMinted"] = 646; ob["totalMinted"] = S("OBFG").get("totalMinted")
ob["freeMinted"] = S("OBFG").get("freeMinted")
ob["freePct"] = round(100.0 * ob["freeMinted"] / 1230, 1)
ob["lastReadBlock"] = None; ob["lastReadWib"] = "2026-11-13 ~11:03 WIB"
ob["runNote1101"] = ("Run 1101: %s->%s/1230 = %.1f%% (+4), umur ~15,2 jam (saleStart 20:01 WIB 12 Nov) <24 jam, slot terbuka (freeAvailable=1); "
    "gate-blocked SUDAH dilaporkan 12 Nov; DIAM." % (646, ob["freeMinted"], ob["freePct"]))
nv = TC["NOTV"]
nv["totalMinted"] = S("NOTV").get("totalMinted")
nv["lastReadBlock"] = None; nv["lastReadWib"] = "2026-11-13 ~11:03 WIB"
nv["runNote1101"] = "Run 1101: masih 0/2000, freeStart 18:00 WIB 13 Nov - BELUM buka; DIAM."
am = TC["AgentMuse"]
am["freeClaimed"] = S("AgentMuse").get("freeClaimed")
am["bookedOf_user"] = S("AgentMuse").get("bookedOf_user")
am["lastReadBlock"] = None; am["lastReadWib"] = "2026-11-13 ~11:03 WIB"
am["runNote1101"] = "Run 1101: freeClaimed 261->%s/888 = %.1f%%, bookedOf(user)=FREE_OSK utuh; minted-by-user; DIAM." % (am["freeClaimed"], 100.0 * am["freeClaimed"] / 888)
# --- DragonAgent + BC1B (address-keyed in contracts? check keys) ---
da = C["Dragon Agent"]
prev = da.get("totalSupply"); da["totalSupply"] = S("DragonAgent").get("totalSupply")
da["runNote1101"] = "Run 1101: totalSupply %s->%s (+%s); free views NULL -> free %% UNVERIFIED; DIAM." % (prev, da["totalSupply"], da["totalSupply"] - prev if prev is not None else "?")
da["lastReadBlock"] = None; da["lastReadWib"] = "2026-11-13 ~11:03 WIB"
bc = TC.get("RESUME-BC1B")
if bc is not None:
    bc["freeCount"] = S("BC1B").get("freeCount")
    bc["runNote1101"] = "Run 1101: freeCount 462 FLAT; DIAM."
    bc["lastReadBlock"] = None; bc["lastReadWib"] = "2026-11-13 ~11:03 WIB"
# --- pending_claims: restore binanceai.fun (was {} despite still pending) ---
snap["pending_claims"] = {"binanceai.fun": {
    "mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    "token": "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c",
    "shares": 1, "tokenClaimed_user": 0, "claimable": 1000000,
    "launched": 0, "pair": "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698",
    "status": "pending-not-open-2026-11-01",
    "lastReadWib": "2026-11-13 ~11:03 WIB",
    "note": ("Dipulihkan run 1101: pending_claims snapshot kosong padahal klaim masih pending "
             "(launched()=0, tokenClaimed(user)=0, dibaca segar run ini). Sudah dilaporkan sekali sebagai "
             "PENDING CLAIM; tidak dilaporkan ulang. Tetap dipantau tiap run; auto-klaim saat launched + guard lolos.")}}
snap["runNote1101"] = ("Run 1101 (11:01-11:13 WIB, blok unknown - eth_blockNumber transient gagal, baca kontrak 21 target sukses via dataseed): "
    "SILENT - 0 kandidat baru, 0 strong lead baru, 0 early lead baru, 0 track-C lead baru, 0 perubahan track-B. "
    "Agentx 686/1111=61,7% velocity GAGAL; Zero 235/500=47,0% velocity GAGAL; OLIVER 912/1000=91,2% umur TETAP UNVERIFIED (tidak bisa promosi); "
    "Royal Rush 246/1000=24,6% (+240/31 mnt, baseline velocity dicatat, umur+X unverified); JNTM free 466/1000 opened=0 quote NULL; "
    "OBFG 650/1230=52,8% gate-blocked; binanceai launched=0 (pending, pending_claims dipulihkan).")
snap["runNote1101_scan"] = ("Run 1101 scan leg FAST-FAIL: Ankr pre-flight 1 chunk 50 blok HTTP 401 Unauthorized "
    "(outage sejak 2026-11-09, ~4,5 hari). Watermark TETAP 132512564; gap ke head ~768rb+ blok. 5c dilewati (tanpa output scan).")
snap["last_run_wib"] = "2026-11-13 ~11:13 WIB"
snap["timestamp_wib"] = "2026-11-13 ~11:13 WIB"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; backup onchain-snapshot-2026-11-13-1101.bak")
print("runNote1101:", snap["runNote1101"][:200])
