#!/usr/bin/env python3
"""Run 2026-11-19 10:01 WIB, merge: velocity vs per-item lastReadBlock
(per-item interval), snapshot update (focus items + 3 early leads +
binanceai + track_c AONE/RigForge/bsccat/pepe), backup first.
No preview/mint/claim. No new age-exclusion this run.
"""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-1001")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-1001-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]
out = {"run": "free-mint-search 2026-11-19 10:01 WIB (merge)", "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

SUPPLY_FN = {
 "HIVE Agents": "totalSupply", "PUNNY": "totalMinted",
 "Bubblebruin": "totalSupply", "Matrix": "freeMinted", "AGCLUB": "totalMinted",
 "Ledgera": "freeClaimed", "ARKYN": "totalMinted", "Lumenhold": "freeClaimed",
 "AgentNOVA": "totalSupply", "STOCK AGENT": "totalSupply", "THYRK": "totalSupply",
 "AgentMintPass": "totalMinted", "AGATE-Pass": "totalMinted", "AgentDrop": "totalMinted",
}
EXTRA = {
 "HIVE Agents": "balanceOf(user)=1; minted-by-user. DIAM.",
 "PUNNY": "mintClosed=1; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
 "Bubblebruin": "freeClaimed 2626/7777 = 33,8%; balanceOf(user)=1; minted-by-user. DIAM.",
 "Matrix": "freeRemaining 354, totalSupply 640, mintOpen 1. DIAM.",
 "AGCLUB": "530/888 = 59,7% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
 "Ledgera": "2708/5000 = 54,2%, mintOpen 1, balanceOf(user)=0. DIAM.",
 "ARKYN": "free% UNVERIFIED + umur UNVERIFIED + X/website UNVERIFIED -> BUKAN kandidat, BUKAN strong lead; tetap watchlist-only. DIAM (tidak dilaporkan ke chat).",
 "Lumenhold": "1263/1500 = 84,2%; umur UNVERIFIED -> BUKAN strong lead. DIAM.",
 "AgentNOVA": "DIAM.",
 "STOCK AGENT": "freeLeft 263, inferred free 848/1111 = 76,3% (INFERENSI totalSupply; freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); quote_user_1=0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0; umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
 "THYRK": "freeMinted 4322 (+1, 4322/7777 = 55,6%); freeUsed(user)=1, balanceOf(user)=1. DIAM.",
 "AgentMintPass": "balanceOf(user)=0, mintedCount(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AGATE-Pass": "balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AgentDrop": "balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
}
vel = {}
for name, metric in SUPPLY_FN.items():
    cur = num(reads.get(name, {}).get("views", {}).get(metric))
    prev_entry = snap.get("contracts", {}).get(name, {})
    prev = prev_entry.get(metric)
    if prev is None:
        prev = prev_entry.get("totalSupply")
    prev_rate = prev_entry.get("currentRatePerMin")
    prev_blk = prev_entry.get("lastReadBlock") or 134412328
    interval_min = (BLK_NEW - prev_blk) * 0.45 / 60.0
    if cur is None or prev is None:
        vel[name] = {"metric": metric, "cur": cur, "prev": prev, "pass": False,
                     "note": "unreadable metric or no baseline"}
    else:
        minted = cur - prev
        rate = minted / interval_min if interval_min > 0 else 0.0
        ratio = (rate / prev_rate) if prev_rate else None
        passed = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        vel[name] = {"metric": metric, "cur": cur, "prev": prev, "minted": minted,
                     "interval_min": round(interval_min, 1),
                     "rate": round(rate, 4), "prev_rate": prev_rate,
                     "ratio": round(ratio, 2) if ratio is not None else None,
                     "pass": passed}
    e = snap["contracts"].setdefault(name, {"address": reads[name]["address"]})
    if cur is not None:
        e["previousTotalSupply"] = prev
        e["totalSupply"] = cur if metric == "totalSupply" else e.get("totalSupply")
        if metric != "totalSupply":
            e[metric] = cur
        e["mintedInInterval"] = vel[name].get("minted")
        e["intervalMinutes"] = round(interval_min, 1)
        e["currentRatePerMin"] = vel[name].get("rate")
        e["previousRatePerMin"] = prev_rate
        e["velocityLegPasses"] = vel[name]["pass"]
    e["lastReadBlock"] = BLK_NEW
    e["lastReadWib"] = "2026-11-19 ~10:01 WIB"
    v = vel[name]
    e["runNote1001_1119"] = (
        f"Run 1001 (blok {BLK_NEW}, interval ~{interval_min:.1f} mnt vs blok {prev_blk}): "
        f"{metric} {v.get('prev')}->{v.get('cur')} "
        f"(+{v.get('minted')}, {v.get('rate')}/mnt vs prev "
        f"{v.get('prev_rate')} = {v.get('ratio')}x) -> velocity "
        f"{'LOLOS' if v['pass'] else 'GAGAL'}; " + EXTRA.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]
out["age_excluded"] = []

# ---- sync "Matrix Agents" (early-lead entry, same contract as "Matrix") ----
ma = snap.get("contracts", {}).get("Matrix Agents")
if isinstance(ma, dict):
    ma["freeMinted"] = vel["Matrix"].get("cur")
    ma["totalSupply"] = num(reads.get("Matrix", {}).get("views", {}).get("totalSupply"))
    ma["lastReadBlock"] = BLK_NEW
    ma["lastReadWib"] = "2026-11-19 ~10:01 WIB"
    ma["runNote1001_1119"] = (f"Run 1001 (blok {BLK_NEW}): freeMinted {vel['Matrix'].get('prev')}->{vel['Matrix'].get('cur')}, "
        f"totalSupply {num(reads.get('Matrix', {}).get('views', {}).get('totalSupply'))}, "
        f"freeRemaining {num(reads.get('Matrix', {}).get('views', {}).get('freeRemaining'))}, mintOpen {num(reads.get('Matrix', {}).get('views', {}).get('mintOpen'))} "
        "(bacaan segar via entri 'Matrix'); velocity GAGAL; umur UNVERIFIED -> tetap EARLY LEAD. DIAM.")

# ---- RigForge / AONE (track_c) ----
tc = snap.setdefault("track_c", {})
if "AONE" in tc and isinstance(tc["AONE"], dict):
    tc["AONE"]["runNote1001_1119"] = ("Run 1001: freeMinted tetap 10000/10000 SOLD OUT "
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~10:01 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    rig["runNote1001_1119"] = ("Run 1001: freeSharesLeft 621 FLAT, openedAt tetap 0 "
        "(belum buka). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~10:01 WIB"
bsc = tc.get("bsccat") if isinstance(tc, dict) else None
if isinstance(bsc, dict):
    bsc["runNote1001_1119"] = ("Run 1001: freeMinted 550 FLAT (sama seperti run 0901) "
        "(totalMinted/soldShares revert seperti biasa). DIAM.")
    bsc["lastReadWib"] = "2026-11-19 ~10:01 WIB"
pepe = reread.get("pepe", {})
out["pepe_reread"] = pepe

# ---- binanceai pending claim ----
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~10:01 WIB"
    pc["binanceai.fun"]["runNote1001"] = ("Run 1001 (blok 134428102): launched=0, failed=1, "
        "isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

snap["last_run"] = {"run": "free-mint-search 2026-11-19 10:01 WIB",
                    "verdict": "DIAM: 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; velocity SEMUA GAGAL (terbesar ARKYN +10, AgentMintPass +6, semua <20 token); scan FAST-FAIL (Ankr 401); watermark tetap 134086385; gap ~341.717 blok",
                    "block": BLK_NEW}
snap["last_run_wib"] = "2026-11-19 ~10:01 WIB"
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-1001-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
