#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 10:01 WIB.
Reads run-2026-11-13-1001-verify.json + discovery.json, updates
onchain-snapshot.json (backup first). NO reportable change this run:
no new candidate / strong lead / early lead / track-B change / track-C
lead; no sellout; no age-exclusion. Read-only otherwise; no preview/mint.
Velocity convention: same as run 0931 (previousRatePerMin frozen as stored;
lag question flagged for parent in run 0931 runlog, NOT changed here).
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "1001"
v = json.load(open(BASE + f"run-2026-11-13-{RUN}-verify.json"))
d = json.load(open(BASE + f"run-2026-11-13-{RUN}-discovery.json"))
reads = v["reads"]
block = v.get("block")
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + f"onchain-snapshot-2026-11-13-{RUN}.bak")
C = snap["contracts"]
TC = snap["track_c"]
NOTE = "Run 1001 (blok %s): " % block

def vel(prev_ts, new_ts, prev_rate, minutes=30.0):
    minted = (new_ts - prev_ts) if (prev_ts is not None and new_ts is not None) else None
    rate = (minted / minutes) if minted is not None else None
    if rate is None or prev_rate is None or prev_rate == 0:
        ratio = None
    else:
        ratio = rate / prev_rate
    passes = bool(minted is not None and minted >= 20 and ratio is not None and ratio >= 1.5)
    return minted, rate, ratio, passes

# --- Agentx (contracts) ---
a = C["Agentx"]
new_tm = reads["Agentx"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(661, new_tm, a.get("previousRatePerMin") or 0.18)
a["previousTotalSupply"] = 661
a["totalSupply"] = new_tm
a["freeClaimed"] = reads["Agentx"]["summary"].get("freeMinted")
a["mintedInInterval"] = minted
a["intervalMinutes"] = 30.0
a["currentRatePerMin"] = round(rate, 3) if rate is not None else None
a["velocityRatio"] = round(ratio, 2) if ratio is not None else None
a["velocityLegPasses"] = passes
a["lastReadBlock"] = block
a["lastReadWib"] = "2026-11-13 ~10:03 WIB"
a["runNote1001"] = (NOTE + "totalMinted 661->%s (+%s, %.2f/mnt vs prev 0.18 = %.2fx, <20 token) -> velocity GAGAL; "
                    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); "
                    "umur ~10,8 jam (mintOpensAt 2026-11-12 23:11 WIB) <24 jam; gate-blocked SUDAH dilaporkan 13 Nov 08:01 - DIAM." %
                    (new_tm, minted, rate, ratio if ratio else 0, a["freeClaimed"],
                     100.0 * a["freeClaimed"] / 1111))

# --- Zero (contracts) ---
z = C["Zero"]
new_tm = reads["Zero"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(203, new_tm, z.get("previousRatePerMin") or 2.42)
z["previousTotalSupply"] = 203
z["totalSupply"] = new_tm
z["freeClaimed"] = reads["Zero"]["summary"].get("freeMinted")
z["mintedInInterval"] = minted
z["intervalMinutes"] = 30.0
z["currentRatePerMin"] = round(rate, 3) if rate is not None else None
z["velocityRatio"] = round(ratio, 2) if ratio is not None else None
z["velocityLegPasses"] = passes
z["lastReadBlock"] = block
z["lastReadWib"] = "2026-11-13 ~10:03 WIB"
z["runNote1001"] = (NOTE + "totalMinted 203->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx, <20 token) -> velocity GAGAL; "
                    "free %s/500 = %.1f%% (<50%% kandidat, <70%% strong lead); slot TERBUKA; "
                    "umur ~2,1 jam (mintOpensAt 2026-11-13 07:55 WIB = verifiedAt Sourcify 00:55:26Z) <24 jam; "
                    "website tetap UNVERIFIED. BUKAN kandidat, BUKAN strong lead. DIAM." %
                    (new_tm, minted, rate, ratio or 0, z["freeClaimed"],
                     100.0 * z["freeClaimed"] / 500))

# --- Oliver Agents (contracts) ---
o = C["Oliver Agents"]
new_ts = reads["OLIVER"]["summary"].get("totalSupply")
new_free = reads["OLIVER"]["summary"].get("freeMinted")
minted, rate, ratio, passes = vel(950, new_ts, o.get("previousRatePerMin") or 0.0)
o["previousTotalSupply"] = 950
o["totalSupply"] = new_ts
o["freeClaimed"] = new_free
o["mintedInInterval"] = minted
o["intervalMinutes"] = 30.0
o["currentRatePerMin"] = round(rate, 3) if rate is not None else None
o["velocityRatio"] = ratio
o["velocityLegPasses"] = False
o["lastReadBlock"] = block
o["lastReadWib"] = "2026-11-13 ~10:03 WIB"
o["runNote1001"] = (NOTE + "totalSupply 950->%s (+%s), freeMinted %s/1000 = %.1f%%, freeRemaining %s, paid beku 50; "
                    "velocity TIDAK lulus (<20 token); umur launch TETAP UNVERIFIED "
                    "-> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka. Watchlist-only, DIAM." %
                    (new_ts, minted, new_free, 100.0 * new_free / 1000,
                     reads["OLIVER"]["summary"].get("freeRemaining")))

# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]
jr = reads["JNTM"]["summary"]
j["freeClaimed"] = jr.get("freeClaimed")
j["totalMinted"] = jr.get("totalMinted")
j["paidMinted"] = jr.get("paidMinted")
j["lastReadBlock"] = block
j["lastReadWib"] = "2026-11-13 ~10:03 WIB"
j["runNote1001"] = (NOTE + "free 322->370/1000 = 37,0%%; paidMinted 59->68 (totalMinted 438); quote NULL TETAP; "
                    "slot terbuka; umur ~3,8 jam (mintStart 2026-11-13 06:13 WIB) <24 jam. Gate PENDING (L) + quote NULL - tanpa perubahan tier. DIAM.")
ob = TC["OBFG"]
obr = reads["OBFG"]["summary"]
ob["totalSupply"] = obr.get("totalSupply")
ob["freeClaimed"] = obr.get("freeMinted")
ob["lastReadBlock"] = block
ob["lastReadWib"] = "2026-11-13 ~10:03 WIB"
ob["runNote1001"] = (NOTE + "totalSupply 633->643/1230 = 52,3%%; slot terbuka (freeAvailable=1); umur ~14 jam (saleStart 2026-11-12 20:01 WIB) <24 jam. "
                    "Gate-blocked SUDAH dilaporkan 12 Nov. DIAM.")
nt = TC["NOTV"]
nt["totalSupply"] = reads["NOTV"]["summary"].get("totalSupply")
nt["lastReadBlock"] = block
nt["lastReadWib"] = "2026-11-13 ~10:03 WIB"
nt["runNote1001"] = (NOTE + "totalSupply 0, freeStart 1794567600 = 18:00 WIB 13 Nov - BELUM BUKA. DIAM.")
am = TC["AgentMuse"]
amr = reads["AgentMuse"]["summary"]
am["freeClaimed"] = amr.get("freeClaimed")
am["bookedOf_user"] = amr.get("bookedOf_user")
am["lastReadBlock"] = block
am["lastReadWib"] = "2026-11-13 ~10:03 WIB"
am["runNote1001"] = (NOTE + "freeClaimed 226->244/888; bookedOf(user)=FREE_OSK utuh; minted-by-user. DIAM.")

# --- top-level run note (other re-read targets + discovery summary) ---
snap["runNote1001"] = (
    NOTE + "AgentLabs totalSpecimens 1580->1732 (exp 2 berjalan); OUTY freeSold 20 FLAT/1500, FREE_FEE 0,0001 BNB TETAP bukan gas-only; "
    "MECHA totalMinted 1908->1910, free 1909/4444=43,0%% (<50%%); Pickgrid freeMinted 216/300=72%% TAPI umur UNVERIFIED; "
    "PX24/SKRR/ME30/CY24 totalSupply 520/509/270/455, umur TETAP UNVERIFIED; HIVE 1263 flat, bal_user=1; "
    "DragonAgent 967->968, free views NULL; binanceai.fun launched()=0, tokenClaimed(user)=0 - tetap pending. "
    "Sourcify feed 20, 3 baru vs hot-leg-seen (0x7535: 54 fns tanpa mint/quote/free/agent; 0xf96c: mint+quote tapi tanpa free view/agent; 0xb31D: quote saja, 11 fns) -> 0 agent-shaped, 0 sale-shape. "
    "Boltbook EN 45097 byte / ZH 43356 byte, 11/11 alamat, 2 'baru' vs hot-leg-seen TAPI false positive: 0x0B2b... = sUSDai Arbitrum (post on-chain data, BUKAN BSC free mint), "
    "0x9329... = hash tx claim RUNE (BUKAN alamat kontrak). 0 lead baru. "
    "Bridge (cek manual, script bridgecheck.py crash di track_c string values + collect() 0 entri karena entry bridge tanpa field 'address'): 116 kontrak, 0 not-in-snapshot, 7 same-owner-discarded - tanpa promosi. "
    "Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (outage sejak 9 Nov, ~4,5 hari); watermark TETAP 132512564; gap ke head 764.059 blok (head 133276623); 5c dilewati. "
    "Sweep EN+ZH: 0 baru <24 jam (Oathbots 28 Okt tua; Agentic Gangster/RIGBYPASS/STAMP PASS sudah dikenal; NOVRA age-excluded; First-Dollar Grove 8 Nov >24 jam; free/FREE NFT 25 Okt tua). "
    "Odaily newsflash: tanpa item Agent ID free-mint (hanya berita Nvidia di fetch teks). "
    "TIDAK ADA perubahan reportable run ini - DIAM."
)
snap["timestamp_wib"] = "2026-11-13 ~10:03 WIB"
snap["last_run_wib"] = "2026-11-13 ~10:03 WIB"
snap["last_run_note"] = "Run 1001: 0 perubahan reportable - DIAM. Scan Ankr 401 fast-fail (watermark 132512564, gap 764.059 blok)."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; block", block, "; snapshot ts 10:03 WIB; no reportable change")
print("Agentx free", C["Agentx"]["freeClaimed"], "Zero free", C["Zero"]["freeClaimed"],
      "Oliver free", C["Oliver Agents"]["freeClaimed"], "JNTM free", TC["JNTM"]["freeClaimed"],
      "OBFG", TC["OBFG"]["totalSupply"])
