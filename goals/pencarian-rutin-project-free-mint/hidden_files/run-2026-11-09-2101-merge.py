#!/usr/bin/env python3
"""Merge run 2101 reread + triage + 5a + binanceai + grove into onchain-snapshot.json.
INTERVAL 32.6 min (block 132593641 ~20:37 WIB -> 132597982 ~21:10 WIB).
Read-only except snapshot. No promotions: 4 strong leads still gate-blocked;
FMA new watchlist-only (age unverified + gate failed); 0x5f76 S1-hit views unverified."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 32.6; BLOCK = 132597982; NOW_WIB = "2026-11-09 21:10 WIB"
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-2101-reread.json"))
contracts = snap.setdefault("contracts", {}); track_c = snap.setdefault("track_c", {})
n_upd = 0; vel_pass = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict): continue
    prev_ts = v.get("totalSupply"); new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts; v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4); v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]: vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None: v[k] = r[k]
    fs = v.get("FREE_SUPPLY"); fcl = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fcl, int):
        v["freePctVerified"] = round(100.0 * fcl / fs, 2)
    v["lastReadBlock"] = BLOCK; v["lastReadWib"] = NOW_WIB
    v["runNote2101_1109"] = (f"Run 2101 (blok {BLOCK}, interval {INTERVAL} mnt vs run 2031): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')} fm={v.get('freeMinted')}; "
        f"bal_user={v.get('balanceOf_user')}; status {v.get('status')}.")
    n_upd += 1
n_tc = 0
for name, v in track_c.items():
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict) or not isinstance(v, dict): continue
    if r.get("totalSupply") is not None: v["totalSupply"] = r["totalSupply"]
    if r.get("freeMinted") is not None: v["freeMinted"] = r["freeMinted"]
    if r.get("freeSharesRemaining") is not None: v["freeSharesRemaining"] = r["freeSharesRemaining"]
    if r.get("balanceOf_user") is not None: v["balanceOf_user"] = r["balanceOf_user"]
    n_tc += 1

# --- strong-lead free% from operative freeMinted counter (freeClaimed() reverts) ---
tc = contracts["TIME CARDS Genesis"]
tc["freePctVerified"] = round(100.0 * 1552 / 2000, 2)
tc["freeMinted"] = 1552
ag = contracts["Agentic"]; ag["freePctVerified"] = round(100.0 * 415 / 1000, 2); ag["freeMinted"] = 415
bh = contracts["BAHUANG3"]; bh["freePctVerified"] = round(100.0 * 2337 / 6000, 2)
lx = contracts["Lenx Agent Pass"]; lx["freePctVerified"] = round(100.0 * 794 / 1000, 2); lx["freeMinted"] = 794
# Dragon Agent: velocity pass but free%/age unverified -> stays early lead
dr = contracts["Dragon Agent"]
dr["runNote2101_velocity"] = ("Run 2101: velocity LOLOS (+41, 1.258/mnt, 21.1x prev 0.0595) "
    "tapi free% UNVERIFIED (FREE_SUPPLY None, freeClaimed/freeMinted None) + umur UNVERIFIED "
    "-> TETAP early lead, bukan promosi strong lead.")
# NEURA: freeClaimCount 137 -> 189 (Boltbook 'cap never existed' terkonfirmasi on-chain),
# legs tetap gagal (tanpa pair + bukan agent-shaped) -> tetap checked-not-lead
nr = contracts["NEURA"]
nr["freeClaimCount"] = 189
nr["runNote2101_1109"] = ("Run 2101: freeClaimCount 137->189 (klaim 'cap 137 tidak ada' di Boltbook "
    "terkonfirmasi on-chain); claimOpen=1, freeClaimed(user)=0; TAPI tetap checked-not-lead: "
    "tanpa pair NEU (LP hook gagal) + bukan agent-shaped (tanpa registry/AgentGate).")
# Osiris Guardians: free pool exhausted on-chain (fm 2222/2222) but already age-excluded; no change
og = contracts["Osiris Guardians"]
og["runNote2101_1109"] = ("Run 2101: freeMinted 1920->2222/2222 (pool gratis habis on-chain); "
    "status TETAP age-excluded-2026-11-09, tidak dilaporkan ulang.")

# --- new track_c entries ---
track_c["FairMint Agent (FMA)"] = {
    "address": "0xA45CA208d015C81Bf2f5e606437e4f9d1D8C2FE8",
    "status": "watchlist-only-age-website-unverified-2026-11-09",
    "totalSupply": 482000000000000000000000,
    "freeMinted": 482,
    "FREE_SUPPLY": 10000,
    "note": ("Ditemukan via Boltbook front page run 2101 (post 21:00-21:07 WIB: FMA 462-472/10.000, "
      "mint() value 0 sim lolos, gate Agent ID). Triase on-chain run 2101 (blok 132599210-132600450): "
      "Sourcify exact_match (verifiedAt 2026-11-09T06:37:46Z); sumber FairMintAgent.sol: mint() no-arg nonpayable, "
      "require REGISTRY.handleOf()>0 (NEED_AGENT_ID) + !hasMinted + mintCount<MAX_MINTS; REGISTRY()=registry "
      "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (terverifikasi on-chain); mintCount 482/10.000, "
      "TOKENS_PER_MINT 1000 FMA, totalSupply 482.000; hasMinted(user)=0, balanceOf(user)=0 (slot TERBUKA). "
      "Bentuk S2-equivalent (token+sale satu kontrak, mint() no-arg = mintFree-equivalent, mintCount/MAX_MINTS = "
      "free-view equivalent). GUGUR 2 kaki: (i) UMUR UNVERIFIED - first-mint tidak terverifikasi (Ankr 401; "
      "dataseed eth_getLogs -32005 + historical eth_call tanpa archive state; publicnode archive butuh token + "
      "getLogs rate-limited; verifiedAt BUKAN launch time); (ii) WEBSITE GATE GAGAL - metode A/C/G/J/M dicoba, "
      "tidak ada situs proyek (hanya fairmint.com yang tidak terkait + Boltbook tanpa link situs). "
      "BUKAN lead/kandidat; TIDAK pernah preview/mint. Diskusi: Boltbook 3 post 21:00-21:07 WIB."),
}
track_c["0x5f76cAb7-5a-hit"] = {
    "address": "0x5f76cAb7B054e088563D5098E17bD0dc430e61aE",
    "status": "watchlist-only-shape-verified-views-unverified-2026-11-09",
    "note": ("Route 5a run 2101: SATU-SATUNYA S1 hit dari 25 alamat feed Sourcify baru (mint+quote+freeUsed+agent+token). "
      "Verifikasi on-chain GAGAL 2x (transport berbeda): semua view null (free pool, user slot, quote, launch) - "
      "quote(user,1) mengembalikan 2^256-1 (garbage, bukan quote valid); registry bytes TRUE di bytecode (code 9956 byte); "
      "totalSupply 235.800.000, decimals 18, freeUsed(user)=0, balanceOf(user)=0. BUKAN lead (free pool/slot/umur "
      "unverified); TIDAK pernah preview/mint. Cek ulang views run berikut."),
}
snap["last_run_wib"] = NOW_WIB
snap["last_run_note"] = ("Run 2101: 612 kontrak + 83 track_c re-read (blok 132597982); 0 kandidat/early/lead baru; "
    "FMA baru watchlist-only (S2-equivalent, umur+website unverified); 0x5f76 S1-hit views unverified; "
    "TIME CARDS 77,6% / Agentic 41,5% / BAHUANG3 38,95% / Lenx 79,4% (semua tetap gate-blocked, sudah dilaporkan); "
    "Dragon Agent velocity LOLOS tapi tetap early lead (free%/umur unverified); NEURA freeClaimCount 189, tetap not-lead; "
    "scan fast-fail Ankr 401 (watermark 132512564, gap ~87 rb blok); binanceai tetap refund; Grove belum buka.")
snap["timestamp_wib"] = NOW_WIB
snap["runNote2101_1109"] = snap["last_run_note"]
snap["runNote2101_1109_scan"] = ("Run 2101 route 4: SCAN FAST-FAIL - Ankr pre-flight HTTP 401 (4,1 dtk, head 132598018), "
    "outage sejak ~13:33 WIB 2026-11-09; watermark TETAP 132512564, gap ~85.454 blok ke head saat preflight "
    "(~87 rb saat merge). Backfill tidak dijalankan run ini (bukan tugas job ini).")
snap["runNote2101_1109_binanceai"] = ("Run 2101 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, "
    "isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132598124). "
    "Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote2101_1109_fma"] = ("Run 2101 FMA: lihat track_c FairMint Agent (FMA) - S2-equivalent terverifikasi on-chain, "
    "pool 482/10.000, slot user terbuka; umur UNVERIFIED + website gate GAGAL -> watchlist-only, bukan lead, tidak dilaporkan.")
snap["runNote2101_1109_grove"] = ("Run 2101 Grove: freeOpen=0 (blok 132597103, grove-check 21:01 WIB) - belum buka.")
with open(f"{BASE}/onchain-snapshot.json", "w") as f:
    json.dump(snap, f, indent=1)
print(f"MERGE DONE contracts={n_upd} track_c={n_tc} velocity_pass={vel_pass}")
