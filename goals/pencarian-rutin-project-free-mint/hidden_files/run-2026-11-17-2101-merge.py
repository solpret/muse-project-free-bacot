#!/usr/bin/env python3
"""Merge run 2026-11-17 21:01 (free-mint-search) into the main snapshot.
Updates scalar readings + last_run fields only; does NOT delete history keys.
No tier changes this run; CAT402 sellout already reported (hot-leg 19:44)."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
BLK = 134132653
WIB = "2026-11-17 ~21:01 WIB"

def upd(name, fields, note):
    e = snap["contracts"].get(name)
    if e is None:
        print("MISSING in snapshot:", name); return False
    e.update(fields)
    e["lastReadBlock"] = BLK
    e["lastReadWib"] = WIB
    e["runNote2101_1117"] = note
    return True

upd("HIVE Agents", {"totalSupply": 1263, "balanceOf_user": 1},
    "Run 2101 (blok 134132653): totalSupply 1263 FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
upd("XCOPY", {"totalSupply": 443, "totalMinted": 443, "previousTotalSupply": 442,
              "mintedInInterval": 1, "currentRatePerMin": 0.03, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): totalSupply 442->443 (+1 <20) -> velocity GAGAL. DIAM.")
upd("ARKYN", {"totalMinted": 1962, "previousTotalSupply": 1960,
              "mintedInInterval": 2, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): totalMinted 1960->1962 (+2 <20) -> velocity GAGAL; free% UNVERIFIED. DIAM.")
upd("Mine Card", {"totalSupply": 986, "totalMinted": 986, "previousTotalSupply": 974,
                  "mintedInInterval": 12, "intervalMinutes": 30.0, "currentRatePerMin": 0.40,
                  "velocityRatio": 0.93, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): totalSupply 974->986 (+12 <20, 0,40/mnt vs prev 0,43 = 0,93x) -> velocity GAGAL; free% + umur UNVERIFIED. DIAM.")
upd("PunchCard", {"totalSupply": 1242, "freeMinted": 1224, "previousTotalSupply": 1237,
                  "mintedInInterval": 5, "velocityLegPasses": False, "freePctVerified": 22.0},
    "Run 2101 (blok 134132653): totalSupply 1237->1242 (+5), freeMinted 1219->1224; free 1224/5555=22,0% (<70% bar strong lead); velocity GAGAL. DIAM.")
upd("Bold Leonidas", {"totalSupply": 896, "previousTotalSupply": 895,
                      "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): totalSupply 895->896 (+1) -> velocity GAGAL. DIAM.")
upd("ALIEN", {"totalSupply": 451, "previousTotalSupply": 450,
              "mintedInInterval": 1, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): totalSupply 450->451 (+1) -> velocity GAGAL. DIAM.")
upd("AGCLUB", {"freeMinted": 522, "mintedInInterval": 0, "velocityLegPasses": False},
    "Run 2101 (blok 134132653): freeMinted 522 FLAT; free 522/8888=5,9% (<70%). DIAM.")
c = snap["contracts"].get("CAT402")
if c is not None:
    c.update({"freeCatsClaimed": 100, "freeCatsRemaining": 0, "totalCatsMinted": 100,
              "status": "sold-out-2026-11-17", "lastReadBlock": BLK, "lastReadWib": WIB,
              "runNote2101_1117": "Run 2101 (blok 134132653): freeCatsClaimed 100/100, freeCatsRemaining 0 -> tetap SOLD OUT (sudah dilaporkan hot-leg 19:44). DIAM."})
    print("CAT402 still sold-out (already reported)")
else:
    print("CAT402 MISSING in snapshot")

pc = snap.get("pending_claims", {}).get("binanceai.fun")
if pc is not None:
    pc.update({"launched": 0, "failed": 1, "isRefundPhase": 1,
               "tokenClaimed_user": 0, "lastReadWib": WIB})
    pc["runNote2101_1117"] = "Run 2101 (blok 134132653): launched=0, failed=1, isRefundPhase=1, tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM."
    print("binanceai pending: still launched=0, failed=1, refund=1 (no change)")

snap["last_run"] = "2026-11-17 ~21:01 WIB"
snap["last_run_wib"] = "2026-11-17 ~21:01 WIB"
snap["timestamp_wib"] = "2026-11-17 ~21:01 WIB"
snap["runNote2101"] = (
    "Run 2101 (jadwal 21:01 WIB): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru. Reread 20/20 OK (blok 134132653, 74,3 dtk): "
    "HIVE 1263 flat; XCOPY 442->443 (+1); ARKYN 1960->1962 (+2); MineCard 974->986 (+12, velocity GAGAL); "
    "PunchCard 1237->1242, free 1224/5555=22,0% (<70%); Matrix free 585/1000=58,5% flat (<70%); "
    "CAT402 free 100/100 tetap SOLD OUT (sudah dilaporkan hot-leg 19:44); DRAGON freeRemaining 0 (sudah diketahui); "
    "PXIO-Miners totalSupply 14471->14706 (+235/30 mnt, hot-leg focus, BUKAN di snapshot; tindak lanjut run 2031: "
    "free view tetap None semua (tanpa jalur gratis terverifikasi), first-seen 16 Nov 19:19 WIB (>24 jam), "
    "checked-not-sale-shape - dicatat saja, bukan tier); BoldLeonidas 895->896; ALIEN 450->451; "
    "FrieAgent-B751 9901/c64d 4901/Flare-bd6f 4900 flat; AGCLUB free 522 flat; Abyssora 62->63; HANAMI-BLOOM 132 flat; "
    "RigForge openedAt 0, freeSharesLeft 627 flat. BinanceAI pending tetap launched=0/failed=1/refund=1. "
    "Pre-flight Ankr 401 fast-fail (ke-27 berturut-turut main job, 22,3 dtk, head 134132430), watermark TETAP 134086385; 5c dilewati. "
    "Feed Sourcify 20 kontrak (verifiedAt 13:31:47-14:05:37Z), 1 baru vs hot-leg-seen (15925 entri): "
    "0x9A86 - S1/S2 false (tanpa mint/quote/free view/agent), bukan lead. "
    "Boltbook EN 45.206 B / ZH 45.400 B, 0 keyword hit, 2 alamat baru (0x539F, 0xa580) - keduanya S1/S2 false, bukan lead. "
    "Bridge 116 kontrak, 0 outside snapshot, 7 same_owner_discarded. "
    "Sweep EN+ZH + Odaily: semua sudah dikenal (Oathbots, Meow Cards, Agentic Gangster free pool habis, Burn Agent, "
    "QILIN/SAFU/PROXY/firebearer, BN Agent Trials season berakhir 8 Nov, AGENT ID cards, LeadLoop/NEXUS CORE, Xuanwu Seed); "
    "Odaily hanya berita makro, 0 pengumuman free-mint Agent ID. "
    "DIAM - tanpa laporan chat."
)
snap["last_run_note"] = snap["runNote2101"]
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("snapshot saved")
