#!/usr/bin/env python3
"""Run 2026-11-19 02:31 WIB, merge: velocity vs run 0201 snapshot values,
snapshot update (focus items + 3 new early leads + binanceai + track_c
AONE/RigForge), backup first. No preview/mint/claim."""
import json, shutil, time
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-0231")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-19-0231-reread.json"))
reads = reread["reads"]
BLK_NEW = reread["block"]          # 134368591
BLK_PREV = 134364150               # run 0201
INTERVAL_MIN = (BLK_NEW - BLK_PREV) * 0.45 / 60.0   # ~33.3
out = {"run": "free-mint-search 2026-11-19 02:31 WIB (merge)",
       "interval_min": round(INTERVAL_MIN, 1), "block_prev": BLK_PREV, "block_new": BLK_NEW}

def num(v):
    return v if isinstance(v, int) else None

# supply metric per contract (totalSupply preferred, else totalMinted/freeMinted)
SUPPLY_FN = {
 "HIVE Agents": "totalSupply", "PUNNY": "totalMinted", "Vitaliq Scans": "totalSupply",
 "Bubblebruin": "totalSupply", "Matrix": "freeMinted", "AGCLUB": "totalMinted",
 "Ledgera": "freeClaimed", "ARKYN": "totalMinted", "Lumenhold": "freeClaimed",
 "AgentNOVA": "totalSupply", "STOCK AGENT": "totalSupply", "THYRK": "totalSupply",
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
    e["lastReadWib"] = "2026-11-19 ~02:31 WIB"
    e["runNote0231_1119"] = (
        f"Run 0231 (blok {BLK_NEW}, interval ~{INTERVAL_MIN:.1f} mnt vs run 0201): "
        f"{metric} {vel[name].get('prev')}->{vel[name].get('cur')} "
        f"(+{vel[name].get('minted')}, {vel[name].get('rate')}/mnt vs prev "
        f"{vel[name].get('prev_rate')} = {vel[name].get('ratio')}x) -> velocity "
        f"{'LOLOS' if vel[name]['pass'] else 'GAGAL'}; " +
        {"HIVE Agents": "balanceOf(user)=1; minted-by-user. DIAM.",
         "PUNNY": "mintClosed=1, mintStart 2026-11-17 20:32 WIB; sudah age-excluded + dihapus 0201 (entri ini bacaan ulang saja). DIAM.",
         "Vitaliq Scans": "genesisStart 2026-11-18 07:00 WIB (umur ~19,5 jam <24 jam; deadline age-exclusion ~07:00 WIB 19 Nov); holdsAgentId(user)=1, balance 0; free%/website UNVERIFIED -> tetap EARLY LEAD.",
         "Bubblebruin": "freeClaimed 2622/7777 = 33,7%; balanceOf(user)=1; minted-by-user. DIAM.",
         "Matrix": "freeMinted 642 FLAT, freeRemaining 358, mintOpen 1. DIAM.",
         "AGCLUB": "freeMinted 530/888 = 59,7% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "Ledgera": "freeClaimed 2707/5000 = 54,1% FLAT, mintOpen 1, balanceOf(user)=0. DIAM.",
         "ARKYN": "totalMinted 2328 FLAT. DIAM.",
         "Lumenhold": "freeClaimed 1259/1500 = 83,9% FLAT; umur UNVERIFIED -> BUKAN strong lead. DIAM.",
         "AgentNOVA": "totalSupply 836. DIAM.",
         "STOCK AGENT": "inferred free 824/1111 = 74,2% (INFERENSI totalSupply; freeMinted/freeClaimed revert = BUKAN free counter terverifikasi); quote_user_1=0, freeMintedByWallet(user)=0 (slot terbuka), balanceOf(user)=0; umur + website UNVERIFIED -> tetap EARLY LEAD, BUKAN strong lead. DIAM.",
         "THYRK": "freeMinted 4318/7777 = 55,5%; freeUsed(user)=1, balanceOf(user)=1. DIAM.",
         }.get(name, ""))
out["velocity"] = vel
out["velocity_passes"] = [k for k, v in vel.items() if v["pass"]]

# RigForge / AONE (track_c) + bsccat/pepe notes
tc = snap.setdefault("track_c", {})
aone = tc.get("AONE", {}) if isinstance(tc.get("AONE"), dict) else {}
if "AONE" in tc and isinstance(tc["AONE"], dict):
    tc["AONE"]["runNote0231_1119"] = ("Run 0231: freeMinted tetap 10000/10000 SOLD OUT "
        "(sudah dilaporkan sekali run 2131 18 Nov — tidak dilaporkan ulang). DIAM.")
    tc["AONE"]["lastReadWib"] = "2026-11-19 ~02:31 WIB"
rig = None
for k, v in tc.items():
    if isinstance(v, dict) and "RigForge" in str(k):
        rig = v
if rig is not None:
    rig["runNote0231_1119"] = ("Run 0231: freeSharesLeft 621 FLAT, openedAt tetap 0 "
        "(belum buka). DIAM.")
    rig["lastReadWib"] = "2026-11-19 ~02:31 WIB"
pc = snap.setdefault("pending_claims", {})
if isinstance(pc, dict) and "binanceai.fun" in pc:
    pc["binanceai.fun"]["lastReadWib"] = "2026-11-19 ~02:31 WIB"
    pc["binanceai.fun"]["runNote0231"] = ("Run 0231 (blok 134368591): launched=0, failed=1, "
        "isRefundPhase=1, totalShares 3110, tokenClaimed(user)=0 — tetap pending/refund, "
        "sudah dilaporkan sekali (fase refund), DIAM.")

# ---- 3 new EARLY leads (first main-job read; agent-shaped; first mints verified) ----
new_leads = {
 "AgentMintPass": {
  "address": "0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
  "status": "early-lead-2026-11-19",
  "name": "Agent Mint Pass", "kind": "ERC721",
  "totalMinted": 272, "MAX_SUPPLY": 10000,
  "firstSeenBlock": 134369886, "lastReadBlock": 134370493,
  "lastReadWib": "2026-11-19 ~02:31 WIB",
  "xVerified": False, "velocityVerified": False,
  "baselineNote": ("EARLY lead dilaporkan sekali run 0231 19 Nov (temuan sweep Boltbook post "
    "https://boltbook.fun/p/z47wuf650ZFf?lang=en). Sourcify exact_match; ABI: agentId + "
    "hasAgentId + mint() no-arg + REWARD + rewardToken + MAX_SUPPLY 10000 + totalMinted; "
    "agent-shaped TRUE (registry reference). totalMinted 271 (driver C, blok 134369886) -> "
    "272 (driver D, blok 134370493); balanceOf(user)=0, mintedCount(user)=0 (slot belum dipakai). "
    "Post pihak ketiga (sim): mint() lolos wallet Agent ID 3/3, gagal wallet biasa 0/3; "
    "rewardToken 0x7007a8c633dc68dc2adf2374fa46a2982afd558a, pool ~48.920.000 AMT; 1/wallet; "
    "+5.000 AMT/mint. Free% UNVERIFIED (tanpa free counter di ABI; 272/10000 = 2,7% dari cap "
    "saja). Umur UNVERIFIED (kontrak terverifikasi Sourcify 2026-11-18T13:22:24Z; waktu launch "
    "tidak dinyatakan di mana pun; BUKAN launch time). Website gate GAGAL: tidak ada situs/sosial "
    "ditemukan (postingan Boltbook sendiri menyatakan 'No site or socials found'; pencarian "
    "alamat kontrak + nama proyek run ini hanya mengembalikan postingan Boltbook itu; metode "
    "A/G dicoba, H/I/J/K/L/M/N belum ada pointer). TIDAK PERNAH di-preview/di-mint (early lead). "
    "Promosi ke strong lead hanya bila 3 kaki lead kuat + gate website lolos."),
  "gateStatus": "FAILED-no-website-2026-11-19",
  "launchNote": "Launch time UNVERIFIED (Sourcify verifiedAt 2026-11-18T13:22:24Z bukan launch time; postingan Boltbook ~18 Nov tanpa tanggal launch).",
  "freePctNote": "UNVERIFIED: tanpa freeMinted/freeClaimed view; totalMinted 272/10000 cap = 2,7% (bukan % free).",
 },
 "AGATE-Pass": {
  "address": "0x5b63bd45e61a2e6540548c3509b598b6384206c5",
  "status": "early-lead-2026-11-19",
  "name": "AGATE Pass", "kind": "ERC721",
  "totalMinted": 247,
  "firstSeenBlock": 134369886, "lastReadBlock": 134370493,
  "lastReadWib": "2026-11-19 ~02:31 WIB",
  "xVerified": False, "velocityVerified": False,
  "baselineNote": ("EARLY lead dilaporkan sekali run 0231 19 Nov (temuan sweep Boltbook post "
    "https://boltbook.fun/p/z47wuf650ZFf?lang=en). Sourcify exact_match; ABI: agentIDRegistry + "
    "holdsAgentID + setAgentIDRegistry + mint() no-arg + canMint + hasMinted + totalMinted; "
    "agent-shaped TRUE (registry reference — CATATAN: varian nama agentIDRegistry/holdsAgentID "
    "TIDAK ditangkap set agent_ref shape-checker S1/S2 (hanya agentId/agentRegistry/registry); "
    "checker perlu ditambah varian ini). totalMinted 195 di postingan -> 247 run ini (+52, masih "
    "minting); balanceOf(user)=0, hasMinted(user)=0 (slot belum dipakai). Post pihak ketiga (sim): "
    "mint() lolos wallet Agent ID 3/3, gagal wallet biasa. Badge saudaranya 0x42c9ed912025df33ca1676aad4651cdded3f09ed "
    "sudah di snapshot (watchlist-only-age-unverified-2026-11-18). Free% UNVERIFIED (tanpa free "
    "counter; cap tidak terbaca). Umur UNVERIFIED (Sourcify verifiedAt 2026-11-18T11:38:26Z bukan "
    "launch time). Website gate GAGAL: tidak ada situs/sosial ditemukan (hanya postingan Boltbook; "
    "pencarian alamat kontrak + nama proyek run ini). TIDAK PERNAH di-preview/di-mint."),
  "gateStatus": "FAILED-no-website-2026-11-19",
  "launchNote": "Launch time UNVERIFIED (Sourcify verifiedAt 2026-11-18T11:38:26Z bukan launch time).",
  "freePctNote": "UNVERIFIED: tanpa freeMinted/freeClaimed view; cap tidak terbaca.",
 },
 "AgentDrop": {
  "address": "0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
  "status": "early-lead-2026-11-19",
  "name": "AgentDrop", "kind": "ERC721",
  "totalMinted": 220,
  "firstSeenBlock": 134369886, "lastReadBlock": 134370493,
  "lastReadWib": "2026-11-19 ~02:31 WIB",
  "xVerified": False, "velocityVerified": False,
  "baselineNote": ("EARLY lead dilaporkan sekali run 0231 19 Nov (temuan sweep Boltbook post "
    "https://boltbook.fun/p/z47wuf650ZFf?lang=en). Sourcify exact_match; ABI: registry() + "
    "hasMinted + mint() no-arg + tip + totalMinted; registry() mengembalikan persis registry "
    "Agent ID 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F -> agent-shaped TRUE. totalMinted 219 "
    "(driver C) -> 220 (driver D); balanceOf(user)=0, hasMinted(user)=0 (slot belum dipakai). "
    "Post pihak ketiga (sim): mint() lolos wallet Agent ID 3/3, gagal wallet biasa. JANGAN "
    "disamakan dengan 'AgentDrop' di agentra.trade (kampanye airdrop BNB Chain, same-name saja, "
    "BUKAN linkage) atau paket PyPI agentdrop (SDK transfer file, bukan proyek ini). Free% "
    "UNVERIFIED (tanpa free counter; cap tidak terbaca). Umur UNVERIFIED (Sourcify verifiedAt "
    "2026-11-18T11:47:44Z bukan launch time). Website gate GAGAL: tidak ada situs/sosial "
    "ditemukan (hanya postingan Boltbook; pencarian alamat kontrak + nama proyek run ini). "
    "TIDAK PERNAH di-preview/di-mint."),
  "gateStatus": "FAILED-no-website-2026-11-19",
  "launchNote": "Launch time UNVERIFIED (Sourcify verifiedAt 2026-11-18T11:47:44Z bukan launch time).",
  "freePctNote": "UNVERIFIED: tanpa freeMinted/freeClaimed view; cap tidak terbaca.",
 },
}
for k, v in new_leads.items():
    snap["contracts"][k] = v
out["new_early_leads"] = list(new_leads.keys())
snap["last_run"] = {"run": "free-mint-search 2026-11-19 02:31 WIB",
                    "verdict": "3 EARLY LEAD BARU (AgentMintPass, AGATE-Pass, AgentDrop); 0 kandidat, 0 strong lead, 0 track-B dibuka, 0 track-C lead; scan FAST-FAIL (Ankr 401/RemoteDisconnected); watermark tetap 134086385",
                    "block": BLK_NEW}
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
json.dump(out, open(f"{HF}/run-2026-11-19-0231-merge.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str)[:4000])
