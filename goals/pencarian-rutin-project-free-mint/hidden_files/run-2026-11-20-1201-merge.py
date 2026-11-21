#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 12:01 WIB into onchain-snapshot.json.
Main re-read ~12:03 WIB (49 kontrak, 384 eth_call, 245 errors - degradasi RPC
bsc-dataseed, nilai lama dipertahankan; eth_blockNumber gagal JSONDecodeError,
blok merge memakai head pre-flight Ankr 134635869).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~12:05 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1201-reread.json"))
BLOCK = 134635869  # head pre-flight Ankr (eth_blockNumber run ini gagal)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1201")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1201-interim.json"))
vel = interim["velocity"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
by_addr = {}
for k, v in snap.get("contracts", {}).items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
n_upd = 0
for name, v in vel.items():
    addr = v["address"].lower()
    if addr not in by_addr:
        continue
    sk, sv = by_addr[addr]
    old_sup = v["old_supply"]
    new_sup = v["new_supply"]
    if new_sup is not None:
        sv["previousTotalSupply"] = old_sup
        sv["totalSupply"] = new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"] = v["delta"]
        sv["intervalMinutes"] = v["minutes"]
        sv["currentRatePerMin"] = v["rate_per_min"]
    sv["velocityLegPasses"] = bool(v["velocity_pass"])
    if v["free_pct"] is not None:
        sv["freePctInference"] = v["free_pct"]
    sv["lastReadBlock"] = BLOCK
    sv["lastReadWib"] = NOW_WIB
    sv["runNote1201_1120"] = (
        f"Run 1201 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# binanceai pending claim: launched/failed/isRefundPhase TERBACA run ini
# (launched=0, failed=1, isRefundPhase=1, totalShares 3110) - tanpa perubahan,
# tetap fase refund (sudah dilaporkan sekali 2026-11-02).
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("launched", "failed", "isRefundPhase", "totalShares"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
for k in ("tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1201"] = (
    f"Run 1201 (blok ~{BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, "
    f"tokenClaimed(user)={bv.get('tokenClaimed_user')}, refundClaimed(user)={bv.get('refundClaimed_user')} - "
    f"tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            tc[key]["freeMinted"] = fm
        tc[key]["runNote1201_1120"] = (
            f"Run 1201 (blok ~{BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 12:01 WIB"
snap["runNote1201"] = (
    "Run 1201: re-read 49 kontrak (384 call, 245 error RPC, blok merge = head pre-flight 134635869); "
    "velocity LOLOS 0 (delta terbesar +6 ALIEN/ARKYN, <20 token); free>70%: STOCK AGENT 83,8% (delta 0, freeLeft 180) - "
    "umur/website UNVERIFIED, bukan strong lead, DIAM; Lumenhold GAGAL baca run ini (nilai lama dipertahankan). "
    "Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail. "
    "Sourcify 1 baru (0x1b40d88e, token tanpa mint/quote/free views, tanpa agent ref), 0 shape hit. "
    "Boltbook EN 44.985 byte + ZH 43.294 byte, 0 baru, 0 shape hit. Bridge 0 baru. "
    "Route-3 sweep: 0 kandidat baru (Mintu Bots berbayar-excluded; Oathbots 23 hari, AGENT ID cards 26 hari, LeadLoop 26 hari, "
    "NEXUS CORE 26 hari, Meow Cards 10 hari, AGENT COSMOS 15 hari - semua umur >24 jam; Coracle sold out 2026-11-10). "
    "binanceai tetap pending/refund (launched=0, failed=1, isRefundPhase=1). "
    "TIDAK ada lead/kandidat/eksekusi - DIAM.")
snap["runNote1201_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134635869) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~549.000 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
