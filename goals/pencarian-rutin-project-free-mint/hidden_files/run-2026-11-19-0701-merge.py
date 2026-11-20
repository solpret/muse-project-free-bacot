#!/usr/bin/env python3
"""Run 2026-11-19 07:01 WIB, merge: velocity vs per-item lastReadBlock
(per-item interval, not a single interval: items were last read at 0601,
0631, or 0201), snapshot update (focus items + 3 early leads + binanceai +
track_c AONE/RigForge), backup first. No preview/mint/claim.
Vitaliq Scans genesisStart 2026-11-18 07:00 WIB -> age 24h02m at this run,
mintOpen=1, totalSupply revert (no sold-out evidence) -> AGE-EXCLUDE:
removed from snapshot.contracts, reported once.
"""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-0701")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0701-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]          # 134404263
out = {"run": "free-mint-search 2026-11-19 07:01 WIB (merge)", "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

SUPPLY_FN = {
 "HIVE Agents": "totalSupply", "PUNNY": "totalMinted", "Vitaliq Scans": "totalSupply",
 "Bubblebruin": "totalSupply", "Matrix": "freeMinted", "AGCLUB": "totalMinted",
 "Ledgera": "freeClaimed", "ARKYN": "totalMinted", "Lumenhold": "freeClaimed",
 "AgentNOVA": "totalSupply", "STOCK AGENT": "totalSupply", "THYRK": "totalSupply",
 "AgentMintPass": "totalMinted", "AGATE-Pass": "totalMinted", "AgentDrop": "totalMinted",
}
NOTES = {
 "HIVE Agents": "totalSupply 1265 FLAT (+0); balanceOf(user)=1; minted-by-user. DIAM.",
 "PUNNY": "totalMinted/freeMinted 379 FLAT, mintClosed=1; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
 "Bubblebruin": "totalSupply 2630 FLAT (+0), freeClaimed 2624/7777 = 33,7%; balanceOf(user)=1; minted-by-user. DIAM.",
 "Matrix": "freeMinted 643->644 (+1), freeRemaining 356, mintOpen 1. DIAM.",
 "AGCLUB": "totalMinted/freeMinted 530/888 = 59,7% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
 "Ledgera": "freeClaimed 2708 FLAT (+0), totalSupply 2715, 2708/5000 = 54,2%, mintOpen 1, balanceOf(user)=0. DIAM.",
 "ARKYN": "totalMinted 2335->2367 (+32) -> velocity LOLOS (>=1.5x DAN >=20 token). TAPI free% UNVERIFIED + umur UNVERIFIED + X/website UNVERIFIED -> BUKAN kandidat, BUKAN strong lead; tetap watchlist-only. DIAM (tidak dilaporkan ke chat).",
 "Lumenhold": "freeClaimed 1259/1500 = 83,9% FLAT; umur UNVERIFIED -> BUKAN strong lead. DIAM.",
 "AgentNOVA": "totalSupply 845 FLAT (+0). DIAM.",
 "STOCK AGENT": "totalSupply 835 FLAT (+0), freeLeft 276, inferred free 835/1111 = 75,2% (INFERENSI totalSupply; freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); quote_user_1=0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0; umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
 "THYRK": "totalSupply 4419->4422 (+3), freeMinted 4318->4321 (+3, 4321/7777 = 55,6%); freeUsed(user)=1, balanceOf(user)=1. DIAM.",
 "AgentMintPass": "totalMinted 320->347 (+27) -> velocity GAGAL (rasio <1.5x); balanceOf(user)=0, mintedCount(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AGATE-Pass": "totalMinted 273->294 (+21) -> velocity LOLOS (>=1.5x DAN >=20 token). TAPI umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD, BUKAN strong lead/kandidat. DIAM (tidak dilaporkan ke chat).",
 "AgentDrop": "totalMinted 230->232 (+2) -> velocity GAGAL; balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
}
vel = {}
for name, metric in SUPPLY_FN.items():
    if name == "Vitaliq Scans":
        continue  # handled by age-exclusion below
    cur = num(reads.get(name, {}).get("views", {}).get(metric))
    prev_entry = snap.get("contracts", {}).get(name, {})
    prev = prev_entry.get(metric)
    if prev is None:
        prev = prev_entry.get("totalSupply")
    prev_rate = prev_entry.get("currentRatePerMin")
    prev_blk = prev_entry.get("lastReadBlock") or 134396048
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
    e["lastReadWib"] = "2026-11-19 ~07:01 WIB"
    v = vel[name]
    e["runNote0701_1119"] = (
        f"Run 0701 (blok {BLK_NEW}, interval ~{interval_min:.1f} mnt vs blok {prev_blk}): "
        f"{metric} {v.get('prev')}->{v.get('cur')} "
        f"(+{v.get('minted')}, {v.get('rate')}/mnt vs prev "
        f"{v.get('prev_rate')} = {v.get('ratio')}x) -> velocity "
        f"{'LOLOS' if v['pass'] else 'GAGAL'}; " + NOTES.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]

# ---- Vitaliq Scans: AGE-EXCLUSION (genesisStart verified on-chain) ----
vit = snap.get("contracts", {}).get("Vitaliq Scans", {})
vit_views = reads.get("Vitaliq Scans", {}).get("views", {})
snap["runNote0701_age_exclusions"] = (
    "Run 0701 (blok 134404263, ~07:02 WIB): Vitaliq Scans 0xad0d78689d047bb9a32f5bf93438373a73da68ec "
    "AGE-EXCLUDED + dihapus dari snapshot.contracts. Bukti: genesisStart on-chain 1794960000 = "
    "2026-11-18 07:00 WIB (terverifikasi); umur 24 jam 02 mnt >= 24 jam; mintOpen=1 (masih terbuka); "
    "totalSupply REVERT (tidak terbaca, tidak ada bukti sold out); holdsAgentId(user)=1, balanceOf(user)=0; "
    "free%/website UNVERIFIED. Status sebelumnya early-lead-2026-11-18 (dilaporkan sekali run 1331 18 Nov). "
    "Dilaporkan sekali sebagai age-excluded run ini."
)
out["age_excluded"] = ["Vitaliq Scans"]
if "Vitaliq Scans" in snap.get("contracts", {}):
    del snap["contracts"]["Vitaliq Scans"]

# ---- sync "Matrix Agents" (early-lead entry, same contract as "Matrix") ----
ma = snap.get("contracts", {}).get("Matrix Agents")
if isinstance(ma, dict):
    ma["freeMinted"] = vel["Matrix"].get("cur")
    ma["totalSupply"] = num(reads.get("Matrix", {}).get("views", {}).get("totalSupply"))
    ma["lastReadBlock"] = BLK_NEW
    ma["lastReadWib"] = "2026-11-19 ~07:01 WIB"
    ma["runNote0701_1119"] = ("Run 0701 (blok 134404263): freeMinted 643->644 (+1), totalSupply 638, "
        "freeRemaining 356, mintOpen 1 (bacaan segar via entri 'Matrix'); velocity GAGAL; umur UNVERIFIED -> tetap EARLY LEAD. DIAM.")

# ---- RigForge / AONE (track_c) ----
tc = snap.setdefault("track_c", {})
if "AONE" in tc and isinstance(tc["AONE"], dict):
    tc["AONE"]["runNote0701_1119"] = ("Run 0701: freeMinted tetap 10000/10000 SOLD OUT "
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~07:01 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    rig["runNote0701_1119"] = ("Run 0701: freeSharesLeft 621 FLAT, openedAt tetap 0 "
        "(belum buka). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~07:01 WIB"

# ---- binanceai pending claim ----
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~07:01 WIB"
    pc["binanceai.fun"]["runNote0701"] = ("Run 0701 (blok 134404263): launched=0, failed=1, "
        "isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

snap["last_run"] = {"run": "free-mint-search 2026-11-19 07:01 WIB",
                    "verdict": "DIAM + 1 AGE-EXCLUDED (Vitaliq Scans): 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; velocity LOLOS ARKYN + AGATE-Pass (tanpa promosi); scan FAST-FAIL (Ankr 401); watermark tetap 134086385; gap ~317.878 blok",
                    "block": BLK_NEW}
snap["last_run_wib"] = "2026-11-19 ~07:01 WIB"
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-0701-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
