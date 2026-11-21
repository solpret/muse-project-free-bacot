#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 10:31 WIB into onchain-snapshot.json.
Main re-read ~10:04 WIB (blok 134624040, 49 kontrak, 404 eth_call, 241 errors
- degradasi RPC, nilai lama dipertahankan). Prev baseline direkonstruksi dari
interim 0931 + retry 0901 (reread 0931 terhapus pasca-merge).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~11:05 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1101-reread.json"))
BLOCK = reread["block"] if isinstance(reread.get("block"), int) else 134624040
MINUTES = 31.0
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1101")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-1101-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-1101-interim.json"))
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
    sv["runNote1101_1120"] = (
        f"Run 1101 (blok {BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# binanceai pending claim (baca OK run ini)
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
pc["launched"] = bv.get("launched")
pc["failed"] = bv.get("failed")
pc["isRefundPhase"] = bv.get("isRefundPhase")
pc["totalShares"] = bv.get("totalShares")
pc["tokenClaimed_user"] = bv.get("tokenClaimed_user")
pc["lastReadWib"] = NOW_WIB
pc["runNote1101"] = (
    f"Run 1101 (blok {BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')}, "
    f"refundClaimed(user)={bv.get('refundClaimed_user')} - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            tc[key]["freeMinted"] = fm
        tc[key]["runNote1101_1120"] = (
            f"Run 1101 (blok {BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
snap["timestamp_wib"] = NOW_WIB
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
