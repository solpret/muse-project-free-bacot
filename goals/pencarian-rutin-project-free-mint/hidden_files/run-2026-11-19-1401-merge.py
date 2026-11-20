#!/usr/bin/env python3
"""Run 2026-11-19 14:01 WIB, merge: velocity vs per-item lastReadBlock
(per-item interval), snapshot update (focus items + 3 early leads +
binanceai + track_c AONE/RigForge/bsccat/pepe), backup first.
No preview/mint/claim. No new age-exclusion this run.
"""
import json, shutil
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-1401")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-1401-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]
out = {"run": "free-mint-search 2026-11-19 14:01 WIB (merge)", "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

SUPPLY_FN = {
 "HIVE Agents": "totalSupply", "PUNNY": "totalMinted",
 "Bubblebruin": "totalSupply", "Matrix": "freeMinted", "AGCLUB": "totalMinted",
 "Ledgera": "freeClaimed", "ARKYN": "totalMinted", "Lumenhold": "freeClaimed",
 "AgentNOVA": "totalSupply", "STOCK AGENT": "totalSupply", "THYRK": "totalSupply",
 "AgentMintPass": "totalMinted", "AGATE-Pass": "totalMinted", "AgentDrop": "totalMinted",
 "AgentForge Hero": "baseMinted",
}
EXTRA = {
 "HIVE Agents": "balanceOf(user)=1; minted-by-user. DIAM.",
 "PUNNY": "mintClosed=1; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
 "Bubblebruin": "balanceOf(user)=1; minted-by-user. DIAM.",
 "Matrix": "DIAM.",
 "AGCLUB": "DIAM.",
 "Ledgera": "DIAM.",
 "ARKYN": "free% UNVERIFIED + umur UNVERIFIED + X/website UNVERIFIED -> BUKAN kandidat, BUKAN strong lead; tetap watchlist-only. DIAM (tidak dilaporkan ke chat).",
 "Lumenhold": "umur UNVERIFIED -> BUKAN strong lead. DIAM.",
 "AgentNOVA": "DIAM.",
 "STOCK AGENT": "free% INFERENSI totalSupply (freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
 "THYRK": "DIAM.",
 "AgentMintPass": "umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AGATE-Pass": "umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AgentDrop": "umur/website UNVERIFIED, gate GAGAL -> tetap EARLY LEAD.",
 "AgentForge Hero": "EARLY LEAD dilaporkan sekali run 1031; umur + X + website UNVERIFIED, gate GAGAL -> TIDAK PERNAH preview/mint. DIAM.",
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
    e["lastReadWib"] = "2026-11-19 ~14:01 WIB"
    v = vel[name]
    e["runNote1401_1119"] = (
        f"Run 1401 (blok {BLK_NEW}, interval ~{interval_min:.1f} mnt vs blok {prev_blk}): "
        f"{metric} {v.get('prev')}->{v.get('cur')} "
        f"(+{v.get('minted')}, {v.get('rate')}/mnt vs prev "
        f"{v.get('prev_rate')} = {v.get('ratio')}x) -> velocity "
        f"{'LOLOS' if v['pass'] else 'GAGAL'}; " + EXTRA.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]
out["age_excluded"] = []

# AFHERO: baseMinted IS the supply view -> sync totalSupply + freePct
_af = snap["contracts"].get("AgentForge Hero")
if isinstance(_af, dict) and vel.get("AgentForge Hero", {}).get("cur") is not None:
    _af["totalSupply"] = vel["AgentForge Hero"]["cur"]
    _af["freePct"] = round(vel["AgentForge Hero"]["cur"] / 10000 * 100, 2)

# ---- sync "Matrix Agents" (early-lead entry, same contract as "Matrix") ----
ma = snap.get("contracts", {}).get("Matrix Agents")
if isinstance(ma, dict):
    ma["freeMinted"] = vel["Matrix"].get("cur")
    ma["totalSupply"] = num(reads.get("Matrix", {}).get("views", {}).get("totalSupply"))
    ma["lastReadBlock"] = BLK_NEW
    ma["lastReadWib"] = "2026-11-19 ~14:01 WIB"
    ma["runNote1401_1119"] = (f"Run 1401 (blok {BLK_NEW}): freeMinted {vel['Matrix'].get('prev')}->{vel['Matrix'].get('cur')}, "
        f"totalSupply {num(reads.get('Matrix', {}).get('views', {}).get('totalSupply'))}, "
        f"freeRemaining {num(reads.get('Matrix', {}).get('views', {}).get('freeRemaining'))}, mintOpen {num(reads.get('Matrix', {}).get('views', {}).get('mintOpen'))} "
        "(bacaan segar via entri 'Matrix'); velocity GAGAL; umur UNVERIFIED -> tetap EARLY LEAD. DIAM.")

# ---- RigForge / AONE (track_c) ----
tc = snap.setdefault("track_c", {})
if "AONE" in tc and isinstance(tc["AONE"], dict):
    _aone = reread.get("reads", {}).get("AONE-sale", {}).get("views", {})
    _fm = _aone.get("freeMinted"); _ft = _aone.get("FREE_TOTAL")
    tc["AONE"]["runNote1401_1119"] = (f"Run 1401: freeMinted {_fm}/{_ft} " + ("SOLD OUT " if _fm is not None and _ft is not None and _fm>=_ft else "") +
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~14:01 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    _rig = reread.get("reads", {}).get("RigForge", {}).get("views", {})
    rig["runNote1401_1119"] = (f"Run 1401: freeSharesLeft {_rig.get('freeSharesLeft')}, openedAt {_rig.get('openedAt')} "
        "(belum buka bila openedAt 0). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~14:01 WIB"
bsc = tc.get("bsccat") if isinstance(tc, dict) else None
if isinstance(bsc, dict):
    _bfm = reread.get("bsccat", {}).get("views", {}).get("freeMinted")
    bsc["runNote1401_1119"] = (f"Run 1401: freeMinted {_bfm} "
        "(totalMinted/soldShares revert seperti biasa). DIAM.")
    bsc["lastReadWib"] = "2026-11-19 ~14:01 WIB"
pepe = reread.get("pepe", {})
out["pepe_reread"] = pepe

# ---- DGF CARD (bridge 0x01f9ca4f..., first-seen run-22, first mint 2026-11-04 05:40 WIB) ----
_dgf = reread.get("reads", {}).get("DGF CARD", {}).get("views", {})
out["dgf_card"] = {"views": _dgf, "block": BLK_NEW,
    "verdict": "AGE-EXCLUDED: first mint 2026-11-04 05:40 WIB (scan run-22) = ~15 hari lalu, >24 jam; "
               "sudah dilaporkan sekali sebagai scan finding (bukan lead job ini); TIDAK ditambah ke watchlist aktif, "
               "TIDAK dilaporkan ke chat; dicatat di run log + age_exclusions saja."}
snap.setdefault("age_exclusions", []).append({
    "name": "DGF CARD (DGFCARD)", "address": "0x01f9ca4ff95d49594cc8b6591022186dc5c1bc72",
    "track": "A", "reason": "age-excluded",
    "evidence": out["dgf_card"]["verdict"] + f" Bacaan run ini (blok {BLK_NEW}): totalSupply/freeClaimed/FREE_SUPPLY/MAX_SUPPLY semua revert (view tidak tersedia di kontrak); balanceOf(user)=0.",
    "reported_once": False, "removed_wib": "2026-11-19 ~14:01 WIB"})

# ---- binanceai pending claim ----
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~14:01 WIB"
    _bai = reread.get("reads", {}).get("binanceai-mint", {}).get("views", {})
    pc["binanceai.fun"]["runNote1401"] = (f"Run 1401 (blok {BLK_NEW}): launched={_bai.get('launched')}, failed={_bai.get('failed')}, "
        f"isRefundPhase={_bai.get('isRefundPhase')}, totalShares {_bai.get('totalShares')}, tokenClaimed(user)={_bai.get('tokenClaimed_user')} — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

gap_blocks = BLK_NEW - 134086385
snap["last_run"] = {"run": "free-mint-search 2026-11-19 14:01 WIB",
                    "verdict": ("DIAM: 0 kandidat, 0 strong lead, 0 early lead baru, 0 track-B dibuka, 0 track-C lead; "
                                f"velocity {'SEMUA GAGAL' if not out['velocity_passes'] else 'LOLOS: ' + ','.join(out['velocity_passes'])}; "
                                f"scan FAST-FAIL (Ankr 401); watermark tetap 134086385; gap ~{gap_blocks:,} blok"),
                    "block": BLK_NEW}
snap["last_run_wib"] = "2026-11-19 ~14:01 WIB"
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-1401-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
