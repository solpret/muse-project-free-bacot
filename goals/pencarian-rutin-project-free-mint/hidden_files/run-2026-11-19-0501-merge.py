#!/usr/bin/env python3
"""Run 2026-11-19 05:01 WIB, merge: velocity vs run 0401 snapshot values,
snapshot update (focus items + 3 early leads + binanceai + track_c
AONE/RigForge/bsccat/pepe), backup first. No preview/mint/claim.
Note: run 0401 merge hardcoded early-lead totalMinted (283/255/221) while its
own run log recorded reads 286/257/221 — snapshot baselines for the 3 early
leads are therefore 283/255/221 (stale by 3/2/0). This merge uses the 0401
LOG reads (286/257/221) as the true prev baseline for deltas."""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-0501")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0501-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]          # 134384064
BLK_PREV = 134384064              # run 0431
INTERVAL_MIN = (BLK_NEW - BLK_PREV) * 0.45 / 60.0   # ~29.8
out = {"run": "free-mint-search 2026-11-19 05:01 WIB (merge)",
       "interval_min": round(INTERVAL_MIN, 1), "block_prev": BLK_PREV, "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

SUPPLY_FN = {
 "HIVE Agents": "totalSupply", "PUNNY": "totalMinted", "Vitaliq Scans": "totalSupply",
 "Bubblebruin": "totalSupply", "Matrix": "freeMinted", "AGCLUB": "totalMinted",
 "Ledgera": "freeClaimed", "ARKYN": "totalMinted", "Lumenhold": "freeClaimed",
 "AgentNOVA": "totalSupply", "STOCK AGENT": "totalSupply", "THYRK": "totalSupply",
 "AgentMintPass": "totalMinted", "AGATE-Pass": "totalMinted", "AgentDrop": "totalMinted",
}
vel = {}
for name, metric in SUPPLY_FN.items():
    cur = num(reads.get(name, {}).get("views", {}).get(metric))
    prev_entry = snap.get("contracts", {}).get(name, {})
    prev = prev_entry.get("totalSupply") if metric == "totalSupply" else None
    if metric != "totalSupply":
        prev = prev_entry.get(metric)
        if prev is None:
            prev = prev_entry.get("totalSupply")
    prev_rate = prev_entry.get("currentRatePerMin")
    if cur is None or prev is None:
        vel[name] = {"metric": metric, "cur": cur, "prev": prev, "pass": False,
                     "note": "unreadable metric or no baseline"}
    else:
        minted = cur - prev
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        ratio = (rate / prev_rate) if prev_rate else None
        passed = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        vel[name] = {"metric": metric, "cur": cur, "prev": prev, "minted": minted,
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
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = vel[name].get("rate")
        e["previousRatePerMin"] = prev_rate
        e["velocityLegPasses"] = vel[name]["pass"]
    e["lastReadBlock"] = BLK_NEW
    e["lastReadWib"] = "2026-11-19 ~05:01 WIB"
    e["runNote0501_1119"] = (
        f"Run 0501 (blok {BLK_NEW}, interval ~{INTERVAL_MIN:.1f} mnt vs run 0401): "
        f"{metric} {vel[name].get('prev')}->{vel[name].get('cur')} "
        f"(+{vel[name].get('minted')}, {vel[name].get('rate')}/mnt vs prev "
        f"{vel[name].get('prev_rate')} = {vel[name].get('ratio')}x) -> velocity "
        f"{'LOLOS' if vel[name]['pass'] else 'GAGAL'}; " +
        {"HIVE Agents": "totalSupply 1265 FLAT (+0); balanceOf(user)=1; minted-by-user. DIAM.",
         "PUNNY": "totalMinted/freeMinted 379 FLAT, mintClosed=1; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
         "Vitaliq Scans": "totalSupply REVERT lagi run ini (tidak terbaca), mintOpen 1, genesisStart 2026-11-18 07:00 WIB (umur ~21,5 jam <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov, ~2,5 jam lagi); holdsAgentId(user)=1, balance 0; free%/website UNVERIFIED -> tetap EARLY LEAD.",
         "Bubblebruin": "totalSupply 2629 FLAT (+0), freeClaimed 2623/7777 = 33,7%; balanceOf(user)=1; minted-by-user. DIAM.",
         "Matrix": "freeMinted 643 FLAT (+0), freeRemaining 357, mintOpen 1. DIAM.",
         "AGCLUB": "totalMinted/freeMinted 530/888 = 59,7% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "Ledgera": "freeClaimed 2707->2708 (+1), totalSupply 2715, 2708/5000 = 54,2% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "ARKYN": "totalMinted 2329->2330 (+1). DIAM.",
         "Lumenhold": "freeClaimed 1259/1500 = 83,9% FLAT; umur UNVERIFIED -> BUKAN strong lead. DIAM.",
         "AgentNOVA": "totalSupply 842 FLAT (+0). DIAM.",
         "STOCK AGENT": "totalSupply 830 FLAT (+0), freeLeft 281, inferred free 830/1111 = 74,7% (INFERENSI totalSupply; freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); quote_user_1=0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0; umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
         "THYRK": "totalSupply 4419, freeMinted 4318/7777 = 55,5% FLAT; freeUsed(user)=1, balanceOf(user)=1. DIAM.",
         "AgentMintPass": "totalMinted 292 (+6 vs bacaan 0401 = 286; baseline snapshot 283 stale -3 dari bug hardcode merge 0401); balanceOf(user)=0, mintedCount(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         "AGATE-Pass": "totalMinted 263 (+6 vs bacaan 0401 = 257; baseline snapshot 255 stale -2 dari bug hardcode merge 0401); balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         "AgentDrop": "totalMinted 223 (+2 vs bacaan 0401 = 221); balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         }.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]

# RigForge / AONE (track_c) + bsccat/pepe notes
tc = snap.setdefault("track_c", {})
if "AONE" in tc and isinstance(tc["AONE"], dict):
    tc["AONE"]["runNote0501_1119"] = ("Run 0501: freeMinted tetap 10000/10000 SOLD OUT "
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~05:01 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    rig["runNote0501_1119"] = ("Run 0501: freeSharesLeft 621 FLAT, openedAt tetap 0 "
        "(belum buka). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~05:01 WIB"
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~05:01 WIB"
    pc["binanceai.fun"]["runNote0501"] = ("Run 0501 (blok 134384064): launched=0, failed=1, "
        "isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

# ---- update 3 EARLY leads with 0431-log baselines (292/263/223) ----
for k in ("AgentMintPass", "AGATE-Pass", "AgentDrop"):
    tm = vel[k].get("cur")
    prev_true = vel[k].get("prev")
    if tm is None or prev_true is None:
        continue
    e = snap["contracts"].get(k, {})
    e["previousTotalSupply"] = prev_true
    e["totalMinted"] = tm
    e["lastReadBlock"] = BLK_NEW
    e["lastReadWib"] = "2026-11-19 ~05:01 WIB"
    e["runNote0501_1119"] = (f"Run 0501 (blok {BLK_NEW}, interval ~{INTERVAL_MIN:.1f} mnt vs run 0431): "
        f"totalMinted {prev_true}->{tm} (+{tm - prev_true}), "
        f"velocity {'LOLOS' if vel[k]['pass'] else 'GAGAL'} (<20 token); balanceOf(user)=0, slot belum dipakai; umur/website UNVERIFIED, "
        f"gate GAGAL -> tetap EARLY LEAD. DIAM.")
    snap["contracts"][k] = e
out["early_leads_updated"] = ["AgentMintPass", "AGATE-Pass", "AgentDrop"]
snap["last_run"] = {"run": "free-mint-search 2026-11-19 05:01 WIB",
                    "verdict": "DIAM: 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; scan FAST-FAIL (Ankr 401); watermark tetap 134086385; gap ~301.926 blok",
                    "block": BLK_NEW}
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-0501-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
