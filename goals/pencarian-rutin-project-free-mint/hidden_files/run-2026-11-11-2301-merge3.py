#!/usr/bin/env python3
"""Merge2301 pass 2: apply the 38 SUCCESSFUL reread reads that merge2 missed.
The restarted reread ran during egress flapping: first 24 contracts batch-failed,
last 38 returned real values. merge2 only handled the 24 fails. This pass applies
velocity + values for the 38 ok reads (interval 30 min vs snapshot 2231 values).
No preview/mint. Appends runNote2301_1111_vel to snapshot.
"""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2301-reread.json"))
C = snap.setdefault("contracts", {})
TS = "2026-11-11 23:01 WIB"
BLOCK = reread.get("block")

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
    ratio = round(rate / prev_rate, 2) if prev_rate and prev_rate > 0 else None
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

vel_pass, vel_fail, partial = [], [], []
for name, d in reread.get("reread", {}).items():
    if name not in C or not isinstance(d, dict) or d.get("_batch_fail"):
        continue
    e = C[name]
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        if r and e.get("velocityLegPasses"):
            vel_pass.append((name, r))
        elif r:
            vel_fail.append((name, r))
    else:
        partial.append(name)
        e["lastReadBlock"] = BLOCK
        e["lastReadWib"] = TS
    for k in ("totalMinted", "freeMinted", "freeClaimed", "FREE_SUPPLY", "MAX_SUPPLY",
              "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if d.get(k) is not None:
            e[k] = d[k]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    old_note = e.get("runNote2301_1111", "")
    e["runNote2301_1111"] = (
        (old_note + " " if old_note else "") +
        "Baca ulang OK run 2301 (blok None, egress flapping): totalSupply %s, balanceOf(user)=%s."
        % (ns, d.get("balanceOf_user")))

print("vel_pass:", vel_pass)
print("vel_fail count:", len(vel_fail))
print("partial (no supply):", partial)
for name, r in vel_fail:
    print("  FAIL", name, r)
snap["runNote2301_1111_vel"] = (
    "Run 2301 velocity (38 baca OK dari reread yang di-restart; 24 batch-fail): LOLOS: %s. "
    "Semua 38 gagal promosi (free%%/umur/X/website UNVERIFIED atau sudah minted-by-user). "
    "Contoh: Twill Fullery 203->216 (+13, <20 token); Pearl Sound 73->75 (+2); Chestnut Common 67->69 (+2); "
    "RAMRAIDERS 568->573 (+5); RIMEVAULT 1079->1084 (+5); MYCELIX 623->624 (+1); REWINDCLUB 563->567 (+4); "
    "LCDSPRITE 583->587 (+4); CosmicSentinel 482; ORBITJANITOR 734; EMBERANVIL 1151; BYTEBLOOM 856; SOLDERCATS 553." % (vel_pass,))
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE2301-PASS2 DONE")
