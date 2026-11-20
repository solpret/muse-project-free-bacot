#!/usr/bin/env python3
"""Merge run 2026-11-17 20:01 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
CAT402 sellout was already reported by hot-leg 19:44 -> status flip only, no re-report.
PunchCard added to snapshot if absent (early lead reported run 1601, website verified)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134124594
WIB = "2026-11-17 ~20:01 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name)
        return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2001_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2001 (blok 134124594): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("XCOPY", {"totalSupply": 439, "totalMinted": 439, "previousTotalSupply": 439,
              "mintedInInterval": 0, "currentRatePerMin": 0.0, "velocityLegPasses": False},
    "Run 2001 (blok 134124594): totalSupply 439->439 (+0) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1957, "previousTotalSupply": 1955,
              "mintedInInterval": 2, "velocityLegPasses": False},
    "Run 2001 (blok 134124594): totalMinted 1955->1957 (+2 <20) -> velocity GAGAL; free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 961, "totalMinted": 961, "previousTotalSupply": 945,
                  "mintedInInterval": 16, "intervalMinutes": 32.0, "currentRatePerMin": 0.5,
                  "velocityRatio": 1.16, "velocityLegPasses": False},
    "Run 2001 (blok 134124594): totalSupply 945->961 (+16, 0,50/mnt vs prev 0,43 = 1,16x) -> velocity GAGAL (<20 token, <1,5x); free% + umur UNVERIFIED. DIAM.")
c = snap["contracts"].get("CAT402")
if c is not None:
    c.update({"freeCatsClaimed": 100, "freeCatsRemaining": 0, "totalCatsMinted": 100,
              "status": "sold-out-2026-11-17", "lastReadBlock": BLK, "lastReadWib": WIB,
              "runNote2001_1117": "Run 2001 (blok 134124594): freeCatsClaimed 100/100, freeCatsRemaining 0 -> FREE POOL SOLD OUT. Sellout SUDAH dilaporkan sekali oleh hot-leg 19:44 (73->100); run ini hanya konfirmasi + status flip, TIDAK lapor ulang."})
    print("CAT402 status -> sold-out (already reported by hot-leg 19:44)")
else:
    print("CAT402 MISSING in snapshot")

# PunchCard: add if absent
if "PunchCard" not in snap["contracts"] and "Punch Card" not in snap["contracts"]:
    snap["contracts"]["PunchCard"] = {
        "address": "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
        "name": "PunchCard", "kind": "ERC721",
        "status": "early-lead-reported-2026-11-17",
        "totalSupply": 1233, "freeMinted": 1215, "MAX_SUPPLY": 5555,
        "mintOpen": 1, "balanceOf_user": 0,
        "freePctVerified": 21.9,
        "freePctNote": "freeMinted 1215/5555 = 21,9% terverifikasi on-chain run 2001 (di bawah bar strong lead >70%).",
        "websiteVerified": True,
        "ageVerified": False,
        "ageNote": "Usia peluncuran UNVERIFIED (belum ada first-mint corroboration di run ini); early lead dilaporkan run 1601.",
        "velocityLegPasses": False,
        "previousTotalSupply": 1228, "mintedInInterval": 5,
        "lastReadBlock": BLK, "lastReadWib": WIB,
        "runNote2001_1117": "Run 2001 (blok 134124594): totalSupply 1228->1233 (+5), freeMinted 1214->1215; free 21,9% <70%; velocity GAGAL. DIAM.",
    }
    print("PunchCard ADDED to snapshot (was hot-leg focus only)")
else:
    print("PunchCard already in snapshot")

pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change; refund-phase report already done earlier)")

snap["last_run"] = "2026-11-17 ~20:01 WIB"
snap["last_run_wib"] = "2026-11-17 ~20:01 WIB"
snap["timestamp_wib"] = "2026-11-17 ~20:01 WIB"
snap["runNote2001"] = (
    "Run 2001 (jadwal 20:01 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. Reread 20/20 OK (blok 134124594, 16,8 dtk): "
    "HIVE 1263 flat; XCOPY 439 flat; ARKYN 1955->1957 (+2); MineCard 945->961 (+16, velocity GAGAL); "
    "PunchCard 1228->1233, free 1215/5555=21,9% (<70%); Matrix free 585/1000=58,5% (<70%); "
    "CAT402 free 100/100 SOLD OUT - sudah dilaporkan hot-leg 19:44, run ini konfirmasi + status flip saja. "
    "BinanceAI pending tetap launched=0/failed=1/refund=1. Pre-flight Ankr 401 fast-fail, watermark TETAP 132512564; "
    "5c dilewati. Feed 20 kontrak, 0 baru vs hot-leg-seen (newest verifiedAt 13:04:55Z). Boltbook EN 46.594 B / ZH 46.921 B, "
    "0 keyword hit, 0 alamat baru (semua sudah di seen). Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH + Odaily: semua sudah dikenal (Oathbots, Meow Cards, Agentic Gangster free pool habis, Burn Agent, "
    "QILIN/SAFU/PROXY/firebearer, BN Agent Trials, AGENT ID cards). DIAM - tanpa laporan chat."
)
snap["last_run_note"] = snap["runNote2001"]
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
