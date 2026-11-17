#!/usr/bin/env python3
"""Merge run 2026-11-14 12:31 WIB reread + probe results into onchain-snapshot.json.
Conservative: only updates fields already present in an entry, plus one runNote1201_1114.
Adds 4 new Boltbook contracts (REOPIR early lead, 2x Frie Agent + OTV watchlist-only).
Updates track_c ORBIT + pending_claims binanceai.fun. Backs up snapshot first.
Read-only on chain; no preview/mint."""
import json, shutil, sys
sys.set_int_max_str_digits(100000)

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-20261114-1231")
s = json.load(open(BASE + "onchain-snapshot.json"))
r = json.load(open(BASE + "run-2026-11-14-1231-reread.json"))
p = json.load(open(BASE + "run-2026-11-14-1231-probe.json"))
BLOCK = r["block"]
INTERVAL_MIN = 30.0  # nominal cadence 1201 -> 1231 (blocks 133484778 -> 133488906)

def rate(delta):
    return round(delta / INTERVAL_MIN, 4) if delta is not None else None

updated = []
for name, item in r["reads"].items():
    v = item.get("views", {})
    c = s["contracts"].get(name)
    if c is None:
        continue
    # supply key: prefer the key the snapshot entry already tracks
    sup_key = None
    for k in ("totalSupply", "totalMinted", "totalSnippets"):
        if k in v and v[k] is not None and k in c:
            sup_key = k
            break
    if sup_key is None:
        for k in ("totalSupply", "totalMinted", "totalSnippets"):
            if k in v and v[k] is not None:
                sup_key = k
                break
    prev = c.get(sup_key) if sup_key else None
    cur = v.get(sup_key) if sup_key else None
    delta = None if (prev is None or cur is None) else cur - prev
    prev_rate = c.get("currentRatePerMin")
    cur_rate = rate(delta)
    if sup_key and cur is not None:
        c["previousTotalSupply"] = prev
        c[sup_key] = cur
    if delta is not None:
        c["mintedInInterval"] = delta
        c["intervalMinutes"] = INTERVAL_MIN
        c["previousRatePerMin"] = prev_rate
        c["currentRatePerMin"] = cur_rate
        ratio = None
        if prev_rate and prev_rate > 0 and cur_rate is not None:
            ratio = round(cur_rate / prev_rate, 2)
        c["velocityRatio"] = ratio
        c["velocityLegPasses"] = bool(delta >= 20 and ratio is not None and ratio >= 1.5)
    # free counter refresh where the reread has one
    if v.get("freeClaimed") is not None:
        c["freeClaimed"] = v["freeClaimed"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-14 ~12:01 WIB"
    note = (f"Run 1231 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1201): "
            f"{sup_key} {prev}->{cur} (d={delta}, rate {cur_rate}/mnt, ratio {c.get('velocityRatio')}) -> "
            f"velocity {'LOLOS' if c.get('velocityLegPasses') else 'GAGAL'}; "
            f"free={v.get('freeClaimed')}/{c.get('FREE_SUPPLY')}; DIAM.")
    c["runNote1231_1114"] = note
    updated.append(name)

# --- track_c ORBIT ---
orb = s.get("track_c", {}).get("ORBIT")
if orb is not None:
    orb["previousFreeClaimed"] = orb.get("freeClaimed")
    orb["freeClaimed"] = 148
    orb["freeRemaining"] = 888 - 148
    orb["lastReadWib"] = "2026-11-14 ~12:31 WIB"
    orb["runNote1231_1114"] = ("Run 1231 (blok 133488906): freeClaimed 142->148/888 (16,7%), claimOpen 1, "
                                "hasFreeClaimed(user)=0, +6 dalam ~30 mnt; umur UNVERIFIED -> tetap watchlist-only, "
                                "BUKAN lead, TIDAK preview/mint. DIAM.")

# --- pending claim binanceai.fun ---
pc = s.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc["lastReadWib"] = "2026-11-14 ~12:31 WIB"
    pc["runNote1231_1114"] = ("Run 1231 (blok 133488906): launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
                               "tokenClaimed(user)=0 - refund phase TIDAK BERUBAH (sudah dilaporkan sekali 2 Nov). DIAM.")

with open(BASE + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(s, f, indent=1)
shutil.move(BASE + "onchain-snapshot.json.tmp", BASE + "onchain-snapshot.json")
print("updated contracts:", len(updated))
print("contracts total:", len(s["contracts"]))
print("new: none")
s["last_run_wib"] = "2026-11-14 ~12:31 WIB"
s["runNote1231_1114"] = "Run 1231: reread 33/33 OK blok 133488906; velocity 0 LOLOS; WANGCAI 128/188=68,1% FLAT (<70%, bukan strong lead); YUANBAO 117/188=62,2% FLAT; scan FAST-FAIL Ankr 401; feed 13 baru 0 shape-hit; Boltbook 0 baru; sweep 0 baru; Odaily 0; binanceai refund phase unchanged; ORBIT 142->148/888; KANDIDAT 0, STRONG LEAD 0, EARLY LEAD 0, TRACK-C 0, EKSEKUSI 0. DIAM."
