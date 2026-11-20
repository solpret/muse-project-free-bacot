#!/usr/bin/env python3
"""Merge run 2026-11-17 20:31 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
No tier changes this run; CAT402 sellout already reported (hot-leg 19:44)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134128243
WIB = "2026-11-17 ~20:31 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2031_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2031 (blok 134128243): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("XCOPY", {"totalSupply": 442, "totalMinted": 442, "previousTotalSupply": 439,
              "mintedInInterval": 3, "currentRatePerMin": 0.1, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): totalSupply 439->442 (+3 <20) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1960, "previousTotalSupply": 1957,
              "mintedInInterval": 3, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): totalMinted 1957->1960 (+3 <20) -> velocity GAGAL; free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 974, "totalMinted": 974, "previousTotalSupply": 961,
                  "mintedInInterval": 13, "intervalMinutes": 30.0, "currentRatePerMin": 0.43,
                  "velocityRatio": 0.86, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): totalSupply 961->974 (+13 <20, 0,43/mnt vs prev 0,50 = 0,86x) -> velocity GAGAL; free% + umur UNVERIFIED. DIAM.")
upd("PunchCard", {"totalSupply": 1237, "freeMinted": 1219, "previousTotalSupply": 1233,
                  "mintedInInterval": 4, "velocityLegPasses": False, "freePctVerified": 21.9},
    "Run 2031 (blok 134128243): totalSupply 1233->1237 (+4), freeMinted 1215->1219; free 1219/5555=21,9% (<70% bar strong lead); velocity GAGAL. DIAM.")
upd("Bold Leonidas", {"totalSupply": 895, "previousTotalSupply": 894,
                      "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): totalSupply 894->895 (+1) -> velocity GAGAL. DIAM.")
upd("ALIEN", {"totalSupply": 450, "previousTotalSupply": 446,
              "mintedInInterval": 4, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): totalSupply 446->450 (+4) -> velocity GAGAL. DIAM.")
upd("AGCLUB", {"freeMinted": 522, "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2031 (blok 134128243): freeMinted 522 FLAT; free 522/8888=5,9% (<70%). DIAM.")
c = snap["contracts"].get("CAT402")
if c is not None:
    c.update({"freeCatsClaimed": 100, "freeCatsRemaining": 0, "totalCatsMinted": 100,
              "status": "sold-out-2026-11-17", "lastReadBlock": BLK, "lastReadWib": WIB,
              "runNote2031_1117": "Run 2031 (blok 134128243): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44). DIAM."})
    print("CAT402 still sold-out (already reported)")
else:
    print("CAT402 MISSING in snapshot")

pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote2031_1117"] = "Run 2031 (blok 134128243): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM."
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-17 ~20:31 WIB"
snap["last_run_wib"] = "2026-11-17 ~20:31 WIB"
snap["timestamp_wib"] = "2026-11-17 ~20:31 WIB"
snap["runNote2031"] = (
    "Run 2031 (jadwal 20:31 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. Reread 20/20 OK (blok 134128243, 23,6 dtk): "
    "HIVE 1263 flat; XCOPY 439->442 (+3); ARKYN 1957->1960 (+3); MineCard 961->974 (+13, velocity GAGAL); "
    "PunchCard 1233->1237, free 1219/5555=21,9% (<70%); Matrix free 585/1000=58,5% (<70%); "
    "CAT402 free 100/100 tetap SOLD OUT (sudah dilaporkan hot-leg 19:44); DRAGON freeRemaining 0 (sudah diketahui); "
    "PXIO-Miners totalSupply 13894->14471 (+577/30 mnt, hot-leg focus, BUKAN di snapshot; free% + umur UNVERIFIED, "
    "semantika view belum terverifikasi - dicatat saja, bukan tier); BoldLeonidas 894->895; ALIEN 446->450; "
    "FrieAgent-B751 9901/c64d 4901/Flare-bd6f 4900 flat; AGCLUB free 522 flat; Abyssora 62 flat; HANAMI-BLOOM 132 flat; "
    "RigForge openedAt 0, freeSharesLeft 627 flat. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (1,6 dtk), watermark TETAP 132512564; 5c dilewati. "
    "Feed Sourcify 20 kontrak (verifiedAt 13:01:12-13:32:50Z), 3 baru vs hot-leg-seen (15906 entri): "
    "0x5741 (quote+agent, tanpa mint/free view), 0x3c97, 0x8c67 - ketiganya S1/S2 false, bukan lead. "
    "Boltbook EN 45.112 B / ZH 45.255 B, 0 keyword hit, 0 alamat baru. Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH + Odaily: semua sudah dikenal (Oathbots, Meow Cards, Agentic Gangster free pool habis, Burn Agent, "
    "QILIN/SAFU/PROXY/firebearer, BN Agent Trials season berakhir 8 Nov, AGENT ID cards, LeadLoop/NEXUS CORE). "
    "DIAM - tanpa laporan chat."
)
snap["last_run_note"] = snap["runNote2031"]
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
