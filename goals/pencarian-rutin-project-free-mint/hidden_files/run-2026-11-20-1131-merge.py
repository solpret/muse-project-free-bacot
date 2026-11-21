#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 11:31 WIB into onchain-snapshot.json.
Main re-read ~11:33 WIB (49 kontrak, 324 eth_call, 258 errors - degradasi RPC
bsc-dataseed, nilai lama dipertahankan; eth_blockNumber gagal JSONDecodeError,
blok merge memakai head pre-flight 134631911).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Read-only kecuali snapshot. Tanpa perubahan status/lead baru."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~11:35 WIB"
reread = json.load(open(BASE + "run-2026-11-20-1131-reread.json"))
BLOCK = 134631911  # head pre-flight Ankr (eth_blockNumber run ini gagal)
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-1131")
snap = json.load(open(BASE + "onchain-snapshot.json"))
interim = json.load(open(BASE + "run-2026-11-20-1131-interim.json"))
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
    sv["runNote1131_1120"] = (
        f"Run 1131 (blok ~{BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd += 1
# binanceai pending claim: launched/failed/isRefundPhase GAGAL baca run ini
# (transport JSONDecodeError, degradasi RPC) -> nilai lama dipertahankan;
# hot-leg 11:29 WIB (blok 134631659) baca launched=0, failed=1, isRefundPhase=1.
pc = snap.get("pending_claims", {}).get("binanceai.fun", {})
bv = reread["reads"]["binanceai-mint"]["views"]
for k in ("totalShares", "tokenClaimed_user", "refundClaimed_user"):
    if num(bv, k) is not None:
        pc[k if k != "tokenClaimed_user" else "tokenClaimed_user"] = num(bv, k)
pc["lastReadWib"] = NOW_WIB
pc["runNote1131"] = (
    f"Run 1131 (blok ~{BLOCK}): launched/failed/isRefundPhase GAGAL baca (transport JSONDecodeError, RPC degradasi) - "
    f"nilai lama dipertahankan (hot-leg 1129: launched=0, failed=1, isRefundPhase=1); "
    f"totalShares {bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')}, "
    f"refundClaimed(user)={bv.get('refundClaimed_user')} - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc = snap.get("track_c", {})
for key, rkey in (("bsccat", "bsccat-sale"), ("AONE", "AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm = num(reread["reads"][rkey]["views"], "freeMinted")
        if fm is not None:
            tc[key]["freeMinted"] = fm
        tc[key]["runNote1131_1120"] = (
            f"Run 1131 (blok ~{BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
snap["timestamp_wib"] = NOW_WIB
snap["last_run_wib"] = "free-mint-search 2026-11-20 11:31 WIB"
snap["runNote1131"] = (
    "Run 1131: re-read 49 kontrak (324 call, 258 error RPC, blok merge = head pre-flight 134631911); "
    "velocity LOLOS 0; free>70%: Lumenhold 85,3% (delta 0) + STOCK AGENT 83,8% (+2, 0,067/mnt, ratio 0,26) - "
    "keduanya tetap age/website UNVERIFIED, bukan strong lead, DIAM. Pre-flight Ankr 401 (sejak 9 Nov) - scan leg fast-fail. "
    "Sourcify 2 baru, 0 shape hit. Boltbook 1 'baru' 0xEdFE74D7... = EOA owner AgentBadge (tanpa code), bukan kontrak, bukan lead. "
    "Bridge 0 baru. Route-3 sweep: 0 kandidat baru (Mintu Bots berbayar; BNB ORBIT/RIGBYPASS/AGENT COSMOS/AGENT ID cards/Agentic Gangster umur >24 jam dan/atau free% <50%). "
    "binanceai tetap pending/refund. TIDAK ada lead/kandidat/eksekusi - DIAM.")
snap["runNote1131_scan"] = (
    "Scan leg route 4: pre-flight Ankr getLogs HTTP 401 Unauthorized (exit 1, head 134631911) - fast-fail, "
    "watermark TETAP 134086385, gap ke head ~545.000 blok dan membesar; blocker kredensial Ankr (custom.ankr) di luar scope job ini. "
    "Track-C 5c: tanpa output scan baru (Ankr 401), tidak ada shape-check backlog run ini.")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merged contracts:", n_upd, "| block:", BLOCK, "| no new leads")
