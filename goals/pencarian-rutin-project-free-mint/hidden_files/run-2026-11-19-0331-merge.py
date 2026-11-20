#!/usr/bin/env python3
"""Run 2026-11-19 03:31 WIB, merge: velocity vs run 0301 snapshot values,
snapshot update (focus items + 3 new early leads + binanceai + track_c
AONE/RigForge), backup first. No preview/mint/claim."""
import json, shutil, time
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-0331")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0331-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]          # 134376096
BLK_PREV = 134372259               # run 0301
INTERVAL_MIN = (BLK_NEW - BLK_PREV) * 0.45 / 60.0   # ~28.8
out = {"run": "free-mint-search 2026-11-19 03:31 WIB (merge)",
       "interval_min": round(INTERVAL_MIN, 1), "block_prev": BLK_PREV, "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

# supply metric per contract (totalSupply preferred, else totalMinted/freeMinted)
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
    # snapshot stores totalSupply as the supply field for most; for metric!=totalSupply use stored field
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
    # update snapshot entry
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
    e["lastReadWib"] = "2026-11-19 ~03:31 WIB"
    e["runNote0331_1119"] = (
        f"Run 0331 (blok {BLK_NEW}, interval ~{INTERVAL_MIN:.1f} mnt vs run 0301): "
        f"{metric} {vel[name].get('prev')}->{vel[name].get('cur')} "
        f"(+{vel[name].get('minted')}, {vel[name].get('rate')}/mnt vs prev "
        f"{vel[name].get('prev_rate')} = {vel[name].get('ratio')}x) -> velocity "
        f"{'LOLOS' if vel[name]['pass'] else 'GAGAL'}; " +
        {"HIVE Agents": "totalSupply 1265 FLAT (+0); balanceOf(user)=1; minted-by-user. DIAM.",
         "PUNNY": "totalMinted/freeMinted 379 FLAT, mintClosed=1; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
         "Vitaliq Scans": "genesisStart 2026-11-18 07:00 WIB (umur ~20,5 jam <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov, ~3,5 jam lagi); holdsAgentId(user)=1, balance 0; free%/website UNVERIFIED -> tetap EARLY LEAD.",
         "Bubblebruin": "totalSupply 2629 (+1), freeClaimed 2623/7777 = 33,7%; balanceOf(user)=1; minted-by-user. DIAM.",
         "Matrix": "freeMinted 643 (+1), freeRemaining 357, mintOpen 1. DIAM.",
         "AGCLUB": "totalMinted/freeMinted 530/888 = 59,7% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "Ledgera": "freeClaimed 2707/5000 = 54,1% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "ARKYN": "totalMinted 2328 FLAT. DIAM.",
         "Lumenhold": "freeClaimed 1259/1500 = 83,9% FLAT; umur UNVERIFIED -> BUKAN strong lead. DIAM.",
         "AgentNOVA": "totalSupply 837 (+1). DIAM.",
         "STOCK AGENT": "totalSupply 828 (+1), freeLeft 283, inferred free 828/1111 = 74,5% (INFERENSI totalSupply; freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); quote_user_1=0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0; umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
         "THYRK": "totalSupply 4419, freeMinted 4318/7777 = 55,5% FLAT; freeUsed(user)=1, balanceOf(user)=1. DIAM.",
         "AgentMintPass": "totalMinted 283 (+9), balanceOf(user)=0, mintedCount(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         "AGATE-Pass": "totalMinted 255 (+6), balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         "AgentDrop": "totalMinted 221 FLAT (+0), balanceOf(user)=0, hasMinted(user)=0; umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
         }.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]

# RigForge / AONE (track_c) + bsccat/pepe notes
tc = snap.setdefault("track_c", {})
aone = tc.get("AONE", {}) if isinstance(tc.get("AONE"), dict) else {}
if "AONE" in tc and isinstance(tc["AONE"], dict):
    tc["AONE"]["runNote0331_1119"] = ("Run 0331: freeMinted tetap 10000/10000 SOLD OUT "
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~03:31 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    rig["runNote0331_1119"] = ("Run 0331: freeSharesLeft 621 FLAT, openedAt tetap 0 "
        "(belum buka). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~03:31 WIB"
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~03:31 WIB"
    pc["binanceai.fun"]["runNote0331"] = ("Run 0331 (blok 134376096): launched=0, failed=1, "
        "isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

# ---- update 3 EARLY leads (already in snapshot since run 0301) ----
for k, tm in (("AgentMintPass", 283), ("AGATE-Pass", 255), ("AgentDrop", 221)):
    e = snap["contracts"].get(k, {})
    _prev_tm = e.get("totalMinted")
    e["previousTotalSupply"] = _prev_tm
    e["totalMinted"] = tm
    e["lastReadBlock"] = BLK_NEW
    e["lastReadWib"] = "2026-11-19 ~03:31 WIB"
    e["runNote0331_1119"] = (f"Run 0331 (blok {BLK_NEW}, interval ~{INTERVAL_MIN:.1f} mnt vs run 0301): "
        f"totalMinted {_prev_tm}->{tm} (+{tm - (_prev_tm or tm)}), "
        f"velocity GAGAL (<20 token); balanceOf(user)=0, slot belum dipakai; umur/website UNVERIFIED, "
        f"gate GAGAL -> tetap EARLY LEAD. DIAM.")
    snap["contracts"][k] = e
out["early_leads_updated"] = ["AgentMintPass", "AGATE-Pass", "AgentDrop"]
snap["last_run"] = {"run": "free-mint-search 2026-11-19 03:31 WIB",
                    "verdict": "DIAM: 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; scan FAST-FAIL (Ankr 401); watermark tetap 134086385; gap ~289.711 blok",
                    "block": BLK_NEW}
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-0331-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
