#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-13 09:31 WIB.
Reads run-2026-11-13-0931-verify.json + discovery.json, updates
onchain-snapshot.json (backup first). SolNFT 333/333 -> sold out: reportable
change once; move contracts -> excluded. Read-only otherwise; no preview/mint.
"""
import json, shutil, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "0931"
v = json.load(open(BASE + f"run-2026-11-13-{RUN}-verify.json"))
d = json.load(open(BASE + f"run-2026-11-13-{RUN}-discovery.json"))
reads = v["reads"]
block = v.get("block")
snap = json.load(open(BASE + "onchain-snapshot.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + f"onchain-snapshot-2026-11-13-{RUN}.bak")
C = snap["contracts"]
TC = snap["track_c"]
NOTE = "Run 0931 (blok %s): " % block

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
prev_ts = a.get("previousTotalSupply") if a.get("previousTotalSupply") is not None else 645
new_tm = reads["Agentx"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(645, new_tm, a.get("previousRatePerMin") or 0.18)
a["previousTotalSupply"] = 645
a["totalSupply"] = new_tm
a["freeClaimed"] = reads["Agentx"]["summary"].get("freeMinted")
a["mintedInInterval"] = minted
a["intervalMinutes"] = 30.0
a["currentRatePerMin"] = round(rate, 3) if rate is not None else None
a["previousRatePerMin"] = 0.18
a["velocityRatio"] = round(ratio, 2) if ratio is not None else None
a["velocityLegPasses"] = passes
a["lastReadBlock"] = block
a["lastReadWib"] = "2026-11-13 ~09:33 WIB"
a["runNote0931"] = (NOTE + "totalMinted 645->%s (+%s, %.2f/mnt vs prev 0.18 = %sx, <20 token) -> velocity GAGAL; "
                    "free %s/1111 = %.1f%% (<70%% strong lead); slot terbuka (freeClaimed_user=0); "
                    "gate-blocked SUDAH dilaporkan 13 Nov 08:01 - DIAM." %
                    (new_tm, minted, rate, ratio if ratio else 0, a["freeClaimed"],
                     100.0 * a["freeClaimed"] / 1111))

# --- Zero (contracts) ---
z = C["Zero"]
new_tm = reads["Zero"]["summary"].get("totalMinted")
minted, rate, ratio, passes = vel(183, new_tm, z.get("previousRatePerMin") or 2.42)
z["previousTotalSupply"] = 183
z["totalSupply"] = new_tm
z["freeClaimed"] = reads["Zero"]["summary"].get("freeMinted")
z["mintedInInterval"] = minted
z["intervalMinutes"] = 30.0
z["currentRatePerMin"] = round(rate, 3) if rate is not None else None
z["previousRatePerMin"] = 2.42
z["velocityRatio"] = round(ratio, 2) if ratio is not None else None
z["velocityLegPasses"] = passes
z["lastReadBlock"] = block
z["lastReadWib"] = "2026-11-13 ~09:33 WIB"
z["runNote0931"] = (NOTE + "totalMinted 183->%s (+%s, %.2f/mnt vs prev 2.42 = %.2fx) -> velocity GAGAL; "
                    "free %s/500 = %.1f%% (<50%% kandidat, <70%% strong lead); slot TERBUKA; "
                    "website tetap UNVERIFIED. BUKAN kandidat, BUKAN strong lead. DIAM." %
                    (new_tm, minted, rate, ratio or 0, z["freeClaimed"],
                     100.0 * z["freeClaimed"] / 500))

# --- Oliver Agents (contracts) ---
o = C["Oliver Agents"]
new_ts = reads["OLIVER"]["summary"].get("totalSupply")
new_free = reads["OLIVER"]["summary"].get("freeMinted")
minted, rate, ratio, passes = vel(920, new_ts, o.get("previousRatePerMin") or 0.0)
o["previousTotalSupply"] = 920
o["totalSupply"] = new_ts
o["freeClaimed"] = new_free
o["mintedInInterval"] = minted
o["intervalMinutes"] = 30.0
o["currentRatePerMin"] = round(rate, 3) if rate is not None else None
o["velocityRatio"] = ratio
o["velocityLegPasses"] = False
o["lastReadBlock"] = block
o["lastReadWib"] = "2026-11-13 ~09:33 WIB"
o["runNote0931"] = (NOTE + "totalSupply 920->%s (+%s), freeMinted %s/1000 = %.1f%%, freeRemaining 100, paid beku 50; "
                    "velocity TIDAK lulus (rate sebelumnya 0 -> rasio tidak terhitung); umur launch TETAP UNVERIFIED "
                    "-> TIDAK BISA promosi ke strong lead walau >70%% + website lolos + slot terbuka. Watchlist-only, DIAM." %
                    (new_ts, minted, new_free, 100.0 * new_free / 1000))

# --- SolNFT: SOLD OUT 333/333 -> move contracts -> excluded ---
sol = C.pop("SolNFT")
sol["status"] = "sold-out-2026-11-13"
sol["totalSupply"] = reads["SolNFT"]["summary"].get("totalMinted")
sol["freeClaimed"] = reads["SolNFT"]["summary"].get("freeMinted")
sol["lastReadBlock"] = block
sol["lastReadWib"] = "2026-11-13 ~09:33 WIB"
sol["runNote0931"] = (NOTE + "totalMinted 332->333 = FREE_CAP 333 -> SOLD OUT (free pool 0). "
                      "Gate-blocked SUDAH dilaporkan 23:30 12 Nov; TIDAK PERNAH di-mint user (balanceOf 0). "
                      "PERUBAHAN dilaporkan sekali ke chat utama run ini; entry dipindah contracts -> excluded.")
snap.setdefault("excluded", {})["SolNFT"] = sol

# --- track_c: JNTM / OBFG / NOTV / AgentMuse ---
j = TC["JNTM"]
jr = reads["JNTM"]["summary"]
j["freeClaimed"] = jr.get("freeClaimed")
j["totalMinted"] = jr.get("totalMinted")
j["paidMinted"] = jr.get("paidMinted")
j["lastReadBlock"] = block
j["lastReadWib"] = "2026-11-13 ~09:33 WIB"
j["runNote0931"] = (NOTE + "free 316->322/1000 = 32,2%%; paidMinted 59 FLAT (totalMinted 381); quote NULL TETAP; "
                    "slot terbuka; umur ~4 jam. Gate PENDING (L) + quote NULL - tanpa perubahan tier. DIAM.")
ob = TC["OBFG"]
obr = reads["OBFG"]["summary"]
ob["totalSupply"] = obr.get("totalSupply")
ob["freeClaimed"] = obr.get("freeMinted")
ob["lastReadBlock"] = block
ob["lastReadWib"] = "2026-11-13 ~09:33 WIB"
ob["runNote0931"] = (NOTE + "totalSupply 628->633/1230 = 51,5%%; slot terbuka (freeAvailable=1); umur ~14,5 jam <24 jam. "
                    "Gate-blocked SUDAH dilaporkan 12 Nov. DIAM.")
nt = TC["NOTV"]
nt["totalSupply"] = reads["NOTV"]["summary"].get("totalSupply")
nt["lastReadBlock"] = block
nt["lastReadWib"] = "2026-11-13 ~09:33 WIB"
nt["runNote0931"] = (NOTE + "totalSupply 0, freeStart 1794567600 = 18:00 WIB 13 Nov - BELUM BUKA. DIAM.")
am = TC["AgentMuse"]
amr = reads["AgentMuse"]["summary"]
am["freeClaimed"] = amr.get("freeClaimed")
am["bookedOf_user"] = amr.get("bookedOf_user")
am["lastReadBlock"] = block
am["lastReadWib"] = "2026-11-13 ~09:33 WIB"
am["runNote0931"] = (NOTE + "freeClaimed 201->226/888; bookedOf(user)=FREE_OSK utuh; minted-by-user. DIAM.")

# --- contracts: light touch notes for other re-read targets ---
for key, note in [
    ("HIVE Agents", NOTE + "totalSupply 1263 flat, balanceOf(user)=1; minted-by-user. DIAM."),
    ("AgentLabs", None),
]:
    pass
# AgentLabs / OUTY / MECHA / Pickgrid / PX24-group / DragonAgent / binanceai: record in runNote0931 on snapshot top level
snap["runNote0931"] = (
    NOTE + "AgentLabs totalSpecimens 1545->1580 (exp 2); OUTY freeSold 11->20/1500, FREE_FEE 0,0001 BNB TETAP bukan gas-only; "
    "MECHA totalMinted 1899->1908, free 1907/4444=42,9%% (<50%%); Pickgrid freeMinted 216/300=72%% TAPI umur UNVERIFIED; "
    "PX24/SKRR/ME30/CY24 totalSupply 520/507/269/455, umur TETAP UNVERIFIED; HIVE 1263 flat; "
    "DragonAgent 967 flat; binanceai.fun launched()=0, tokenClaimed(user)=0 - tetap pending. "
    "Sourcify feed 20, 1 baru 0x86b752DA79674D2AbE87bfB1a9F151B411f8fCF9 (3 fns, tanpa mint/quote/free/agent -> BUKAN agent-shaped, BUKAN sale-shape). "
    "Boltbook EN 43584 byte / ZH 42041 byte, 12/11 alamat, 0 baru vs seen. "
    "Bridge: 116 kontrak, 1 not-in-snapshot = PIXEL BOYZ 0xafb50403... (SUDAH ada di excluded sebagai 'PIXEL BOYZ', ruled out 57/10000=0,57%%; "
    "re-read rutin pertama: totalMinted 6008/10000, first-seen scan 3 Nov -> umur >>24 jam, age-excluded, SILENT, tanpa promosi). "
    "Scan leg FAST-FAIL: Ankr pre-flight HTTP 401 (outage sejak 9 Nov, ~4,5 hari); watermark TETAP 132512564; gap ke head ~760.000 blok; 5c dilewati. "
    "Sweep EN+ZH: 0 baru <24 jam (Agentic Gangster/STAMP/RIGBYPASS/MOLT/Oathbots sudah dikenal; WNO+NEBULA sudah minted-by-user; NOVRA age-excluded; UFO tutup 12 Nov 22:05 WIB). "
    "SolNFT SOLD OUT 333/333 -> LAPOR SEKALI (lihat runlog)."
)
snap["timestamp_wib"] = "2026-11-13 ~09:33 WIB"
snap["last_run_wib"] = "2026-11-13 ~09:33 WIB"
snap["last_run_note"] = "Run 0931: 1 perubahan reportable (SolNFT sold out); selebihnya DIAM. Scan Ankr 401 fast-fail."
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge OK; block", block, "; SolNFT moved to excluded; snapshot ts 09:33 WIB")
print("Agentx free", C["Agentx"]["freeClaimed"], "Zero free", C["Zero"]["freeClaimed"],
      "Oliver free", C["Oliver Agents"]["freeClaimed"], "JNTM free", TC["JNTM"]["freeClaimed"],
      "OBFG", TC["OBFG"]["totalSupply"])
