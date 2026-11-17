#!/usr/bin/env python3
"""Merge for free-mint-search run 2026-11-12 21:01 WIB.
Reads run-2026-11-12-2101-verify.json + legs, updates onchain-snapshot.json:
- re-read targets: supply/free/lastRead + runNote2101_1112
- age-exclusions (verified launch >=24h, not sold out, reported once as early lead):
  CRTSAINTS, 0x2e50 (INBOXGOBLIN), MOONDRILL -> removed from contracts, recorded
  in age_exclusions_2101
- RigForge track_c refresh; binanceai claim still closed.
Backup first. No preview/mint."""
import json, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 21:01 WIB"
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2101")
snap = json.load(open(BASE + "onchain-snapshot.json"))
ver = json.load(open(BASE + "run-2026-11-12-2101-verify.json"))
block = ver["block"]

# verify name -> snapshot contract key
MAP = {
    "WFPASS": "WFPASS", "SEVEN": "SEVEN", "AGCR": "AGCR", "MECHA": "MECHA",
    "BUCKET": "BUCKET", "SUDOSAINTS": "SUDOSAINTS", "Pickgrid": "Pickgrid",
    "LuckyCatch": "LuckyCatch", "BinanceLife": "BinanceLife",
    "Kongtou-AirdropCnNFT": "Kongtou-AirdropCnNFT", "0x7Eb9": "0x7Eb9",
    "NAOMI": "NAOMI", "AgenticGangster": "AgenticGangster",
    "AIRDROP": "AIRDROP", "Kitebots": "Kitebots", "Dragon Agent": "Dragon Agent",
}
updated = []
for name, key in MAP.items():
    r = ver["reads"].get(name)
    if not r or not r.get("views"):
        continue
    c = snap["contracts"].get(key)
    if c is None:
        continue
    v = r["views"]
    prev = c.get("totalSupply")
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY"):
        if v.get(f) is not None:
            c[f] = v[f]
    if v.get("balanceOf_user") is not None:
        c["balanceOf_user"] = v["balanceOf_user"]
    c["lastReadBlock"] = block
    c["lastReadWib"] = TS
    new = c.get("totalSupply")
    minted = (new - prev) if (isinstance(new, int) and isinstance(prev, int)) else None
    c["runNote2101_1112"] = (
        f"Run 2101 (blok {block}): totalSupply {prev}->{new} "
        f"(+{minted if minted is not None else '?'}), velocity GAGAL (<20 token); "
        f"freeClaimed={v.get('freeClaimed')}, freeMinted={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; bukan kandidat; tanpa perubahan status.")
    updated.append(key)

# velocity notes for the two active early leads with a fresh read
m = snap["contracts"].get("MECHA")
if m:
    m["runNote2101_1112"] = (
        "Run 2101 (blok 133173524): totalMinted 1836->1846 (+10, ~0,33/mnt), "
        "freeClaimed 1835->1845; FREE_SUPPLY null -> % free UNVERIFIED; velocity GAGAL "
        "(<20 token); umur launch UNVERIFIED -> tetap watchlist-only EARLY, bukan kandidat.")
b = snap["contracts"].get("BUCKET")
if b:
    b["runNote2101_1112"] = (
        "Run 2101 (blok 133173524): totalSupply 717->718 (+1), velocity GAGAL; "
        "deadline umur 24 jam 2026-11-12 21:16:46 WIB (mintOpenedAt 11 Nov 21:16:46) "
        "belum lewat saat bacaan run ini (~21:06) -> age-exclusion jatuh ke run 21:31; "
        "tetap EARLY, bukan kandidat.")

# --- age exclusions (verified launch >= 24h at run time, not sold out) ---
def age_rec(name, addr, mint_start, supply, cap):
    dt = datetime.datetime.fromtimestamp(mint_start, datetime.timezone(datetime.timedelta(hours=7)))
    return {
        "name": name, "address": addr,
        "mintStartWib": dt.strftime("%Y-%m-%d %H:%M:%S WIB"),
        "deadline24hWib": (dt + datetime.timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S WIB"),
        "readWib": TS, "readBlock": block,
        "totalSupply_at_removal": supply, "freeCap": cap,
        "freePct_approx": round(100.0 * supply / cap, 2) if cap else None,
        "status_before": "early-lead-reported-2026-11-11",
        "reported_as": "age-excluded-once-2026-11-12-2101",
        "evidence": "mintStart on-chain (baca segar run 2101) + totalSupply segar; bukan sold out; "
                    "website + X + diskusi tidak pernah terverifikasi; tidak pernah jadi kandidat.",
    }

removed = []
for name, key, addr, ms, cap in [
    ("CRTSAINTS", "CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F", 1794405023, 2000),
    ("0x2e50 (INBOXGOBLIN)", "0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3", 1794405623, 2000),
    ("MOONDRILL", "MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0", 1794406225, 2000),
]:
    c = snap["contracts"].pop(key, None)
    supply = ver["reads"][key]["views"].get("totalSupply") if ver["reads"].get(key) else None
    if supply is None and c is not None:
        supply = c.get("totalSupply")
    removed.append(age_rec(name, addr, ms, supply, cap))
snap["age_exclusions_2101"] = removed
snap["runNote2101_1112_age_exclusions"] = (
    "Run 2101: CRTSAINTS (launch 11 Nov 20:50:23 WIB, deadline 12 Nov 20:50:23), "
    "0x2e50/INBOXGOBLIN (launch 11 Nov 21:00:23, deadline 21:00:23), MOONDRILL "
    "(launch 11 Nov 21:10:25, deadline 21:10:25) semuanya >=24 jam saat run, belum sold out "
    "(supply 149/137/123 vs cap 2000), dilaporkan sekali sebagai age-excluded (ketiganya "
    "pernah dilaporkan sekali sebagai EARLY lead 11 Nov). Dihapus dari contracts. "
    "BUCKET deadline 21:16:46 belum lewat saat bacaan run ini -> run 21:31. "
    "MECHA umur tetap UNVERIFIED -> tetap watchlist-only.")

# --- RigForge track_c refresh (unchanged) ---
rf = snap.get("track_c", {}).get("RigForge")
if rf:
    rf["freeSharesLeft"] = 662
    rf["openedAt"] = 0
    rf["freeClaimed"] = 338
    rf["lastReadBlock"] = block
    rf["lastReadWib"] = TS

# --- binanceai pending claim: still closed ---
snap["runNote2101_1112_binanceai"] = (
    "Run 2101 (blok 133173524): binanceai-mint launched()=0, freeSharesRemaining=0, "
    "FREE_SHARES=2888 — klaim BELUM dibuka (fase refund); pending_claims tetap kosong; "
    "tidak ada klaim/preview.")

# --- OBFG read (tracked by hot-leg in hot-leg-seen.json; NOT added to main snapshot) ---
snap["runNote2101_1112_obfg"] = (
    "Run 2101 (blok 133173524): OBFG 0x5314071bba19943f58347ba5dec423e5032a6818 "
    "freeMinted 312->329/1230 (26,8%), totalSupply 329, saleStart 1794488476 "
    "(20:01:16 WIB, umur ~70 mnt), freeAvailable(user)=1, quote(user,1) gratis; "
    "gate website tetap GAGAL (dilaporkan sekali 20:18 WIB) -> TIDAK preview/mint, "
    "tidak dilaporkan ulang; tracking di hot-leg-seen.json, bukan snapshot utama.")

snap["last_run"] = "2026-11-12-2101"
snap["last_run_wib"] = TS
snap["last_run_block"] = block
snap["last_run_note"] = (
    "Run 2101: pre-flight Ankr 401 FAIL (scan fast-fail, watermark tetap 132512564); "
    "feed 20 kontrak 0 baru; Boltbook EN+ZH 7 alamat 0 baru; bridge 116 kontrak "
    "0 not-in-snapshot, 7 same-owner-discarded; verify 35 target (22 terbaca, "
    "13 BATCH-FAIL, nilai lama dipertahankan); 3 age-exclusions (CRTSAINTS, 0x2e50, "
    "MOONDRILL) dilaporkan sekali; 0 kandidat/strong lead/early lead/track-B/track-C baru; "
    "tidak ada preview/mint/eksekusi.")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("updated:", updated)
print("removed:", [r["name"] for r in removed])
print("block:", block)
