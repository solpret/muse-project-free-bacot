#!/usr/bin/env python3
"""Merge run 1931 reread + triage-7bcc + 5a5c + binanceai probe into onchain-snapshot.json.
Preserves old values when fresh reads are None (read artifact, not zero).
INTERVAL 64.97 min from block timestamps 132577311 (18:34:03 WIB) -> 132585967 (19:39:01 WIB).
Phase 1: update readings, add Agentic early lead, write run notes, PRINT age-exclusion
candidates (no deletions in this phase).
Writes run-2026-11-09-1931-merge.json (summary)."""
import json, re, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
INTERVAL = 64.97
BLOCK = 132585967
NOW = datetime.datetime(2026, 11, 9, 19, 39, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-1931-reread.json"))
tri = json.load(open(f"{BASE}/run-2026-11-09-1931-triage-7bcc.json"))
a5 = json.load(open(f"{BASE}/run-2026-11-09-1931-5a5c.json"))
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

n_upd = 0
vel_pass = []
for name, v in contracts.items():
    r = rr.get("reread", {}).get(name)
    if not isinstance(r, dict):
        continue
    prev_ts = v.get("totalSupply")
    new_ts = r.get("totalSupply")
    minted = None
    if isinstance(prev_ts, int) and isinstance(new_ts, int):
        minted = new_ts - prev_ts
        prev_rate = v.get("currentRatePerMin")
        rate = minted / INTERVAL
        ratio = (rate / prev_rate) if (isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
        v["previousTotalSupply"] = prev_ts
        v["mintedInInterval"] = minted
        v["intervalMinutes"] = INTERVAL
        v["currentRatePerMin"] = round(rate, 4)
        v["previousRatePerMin"] = prev_rate
        v["velocityRatio"] = (round(ratio, 2) if ratio is not None else None)
        v["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if v["velocityLegPasses"]:
            vel_pass.append((name, minted, round(ratio, 2)))
    for k in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY",
              "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    fs = v.get("FREE_SUPPLY")
    fc = v.get("freeClaimed")
    if isinstance(fs, int) and fs and isinstance(fc, int):
        v["freePctVerified"] = round(100.0 * fc / fs, 2)
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 19:39 WIB"
    v["runNote1931_1109"] = (
        f"Run 1931 (blok {BLOCK}, interval {INTERVAL} mnt vs run 1831): "
        f"{prev_ts}->{new_ts} (+{minted if minted is not None else 'n/a'}), "
        f"velocity {'LOLOS' if v.get('velocityLegPasses') else 'GAGAL'}; "
        f"free={v.get('freeClaimed')}/{v.get('FREE_SUPPLY')}; bal_user={v.get('balanceOf_user')}; "
        f"status {v.get('status')}."
    )
    n_upd += 1

n_tc = 0
for name, v in track_c.items():
    if not isinstance(v, dict):
        continue
    r = rr.get("track_c", {}).get(name)
    if not isinstance(r, dict):
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "balanceOf_user", "freeClaimed_user"):
        if r.get(k) is not None:
            v[k] = r[k]
    v["lastReadBlock"] = BLOCK
    v["lastReadWib"] = "2026-11-09 19:39 WIB"
    v["runNote1931_1109"] = (f"Run 1931 (blok {BLOCK}): totalSupply={r.get('totalSupply')} "
        f"freeMinted={r.get('freeMinted')} freeSharesRemaining={r.get('freeSharesRemaining')} bal_user={r.get('balanceOf_user')}.")
    n_tc += 1

# --- new early lead: Agentic (AGTC) ---
contracts["Agentic"] = {
    "address": "0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5",
    "status": "early-lead-reported-2026-11-09",
    "name": "Agentic", "symbol": "AGTC", "kind": "ERC721",
    "totalSupply": tri.get("totalMinted"),
    "totalMinted": tri.get("totalMinted"),
    "freeClaimed": tri.get("freeMinted"),
    "freeMinted": tri.get("freeMinted"),
    "FREE_SUPPLY": tri.get("FREE_SUPPLY"),
    "MAX_SUPPLY": tri.get("MAX_SUPPLY"),
    "freePctVerified": round(100.0 * tri["freeMinted"] / tri["FREE_SUPPLY"], 2),
    "paidPrice": tri.get("paidPrice"),
    "DEFAULT_PAID_PRICE": tri.get("DEFAULT_PAID_PRICE"),
    "registry": tri.get("registry"),
    "owner": tri.get("owner"),
    "hasFreeMinted_user": tri.get("hasFreeMinted_user"),
    "balanceOf_user": tri.get("balanceOf_user"),
    "userBalance": 0,
    "xVerified": False,
    "velocityVerified": False,
    "website": None,
    "gate": "FAILED (run 1931, metode A-N): (A) pencarian alamat kontrak tanpa hasil; (C) Sourcify stdJson tanpa URL; (G) pencarian nama 'Agentic' hanya same-name lain (AGC, Believers, AgentForge, AgentID) - bukan linkage; (H) tanpa contractURI (revert); (I) tokenURI(1) = metadata workers.dev tanpa external_url; (J) ABI tanpa fungsi site/URL. TIDAK ada website terverifikasi. Gate gagal = scope block untuk eksekusi, BUKAN kegagalan safety; early lead tetap dilaporkan sekali.",
    "launchNote": "Usia peluncuran TERBATAS TERVERIFIKASI <=48 jam: Sourcify verifiedAt 2026-11-09T12:26:25Z = 19:26:25 WIB; pertama muncul di feed Sourcify hot-leg 19:29 (TIDAK ada di feed 19:24); freeMinted 118 (19:29) -> 189 (~19:41) = minting live di-run. Event first-mint TIDAK bisa dibaca: Ankr getLogs 401 (outage sejak ~13:33 WIB) + dataseed eth_getLogs -32005 limit exceeded (bahkan 200 blok) + publicnode eth_getLogs rate-limit; Blockscout tidak dukung BSC. Batas atas umur <1 jam saat triase.",
    "baselineNote": "EARLY lead dilaporkan sekali run 1931. TIDAK PERNAH auto-mint/preview. Agent-shape terverifikasi: Sourcify exact_match (verifiedAt 2026-11-09T12:26:25Z); ABI mintFree() no-arg nonpayable + mint() payable + hasFreeMinted(address) + freeMinted() + FREE_SUPPLY() + registry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F exact on-chain; owner 0x9e07f754116315298d8aaf3e24181de2907b4623 TIDAK ada di same-owner-discards.json (60 entri). Free pool 189/1000 = 18,9% (<25% kaki strong lead). Slot user TERBUKA (hasFreeMinted(user)=0, balanceOf(user)=0). Metadata: 'Agentic #1 - A Uncommon Standard Bot ... Holding this NFT entitles its owner to a one-time claim of 5.000 AGTR (Agentic Reward Token)' - host metadata vienoaqila.workers.dev, BUKAN situs proyek. Promosi ke strong lead bila: umur terverifikasi + free% >=25% + slot tetap terbuka (saat ini free% 18,9% GAGAL).",
    "firstSeenBlock": 132585967,
    "lastReadBlock": tri.get("block"),
    "lastReadWib": "2026-11-09 19:41 WIB",
    "runNote1931_1109": "Run 1931: baru masuk snapshot sebagai EARLY lead (lihat baselineNote). freeMinted 189/1000 = 18,9%; slot user terbuka; website gate FAILED.",
}

# --- binanceai track-B re-check ---
snap["binanceai_claim"]["verified_run"] = "2026-11-09 run 1931"
snap["binanceai_claim"]["verified_wib"] = "2026-11-09 19:4x WIB"
snap["binanceai_claim"]["block"] = 132587052

# --- age-exclusion candidates (PRINT ONLY, no deletion this phase) ---
ACTIVE = ("early-lead", "early-lead-reported", "early-lead-backfill", "strong-lead",
          "watchlist-only", "watchlist-only-mature-newly-noticed", "candidate")
def launch_dt(v):
    for k in ("startTimeWib", "firstMintWib"):
        s = v.get(k)
        if isinstance(s, str):
            try:
                return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                pass
    ln = v.get("launchNote") or ""
    m = re.search(r"20\d\d-11-0\d[ 0-9:]+", ln)
    if m:
        try:
            return datetime.datetime.fromisoformat(m.group(0).strip().replace(" ", "T")[:19]).replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
        except Exception:
            return None
    return None

cands = []
for name, v in contracts.items():
    st = str(v.get("status") or "")
    if not any(st.startswith(a) for a in ACTIVE):
        continue
    ld = launch_dt(v)
    if ld is None:
        continue
    if ld.tzinfo is None:
        ld = ld.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=7)))
    age_h = (NOW - ld).total_seconds() / 3600.0
    fs = v.get("FREE_SUPPLY"); fc = v.get("freeClaimed")
    pool_open = (isinstance(fs, int) and isinstance(fc, int) and fc < fs)
    ts = v.get("totalSupply"); mx = v.get("MAX_SUPPLY")
    sold_out = (isinstance(ts, int) and isinstance(mx, int) and ts >= mx)
    if age_h > 48 and pool_open and not sold_out:
        cands.append((name, st, ld.isoformat(), round(age_h, 1)))

# --- top-level run notes ---
snap["runNote1931_1109"] = (
    f"Run 1931: re-read {n_upd} kontrak + {n_tc} track_c (blok {BLOCK}, interval {INTERVAL} mnt vs run 1831 - block timestamp 132577311 18:34:03 WIB -> 132585967 19:39:01 WIB). "
    f"Velocity LOLOS: {vel_pass} - Mechfarm (same-owner-discarded 2026-11-03, owner d76d, TIDAK promosi), Skyagent (age-excluded 2026-11-06, TIDAK promosi). TIDAK ADA promosi. "
    "Sellout baru: 0 (kontrak di ts>=MAX sudah max sejak sebelum run ini). Free-pool-exhausted baru: 0. "
    "EKSEKUSI: 0. Early lead BARU: Agentic (AGTC) 0x7BcC29c5 - dilaporkan sekali run ini. "
    "Scan leg FAST-FAIL (Ankr pre-flight HTTP 401, outage sejak ~13:33 WIB; watermark tetap 132512564; gap ke head ~73.800 blok). "
    "Track-B binanceai: TIDAK BERUBAH (launched 0, failed 1, refund 1, totalShares 3110, tokenClaimed(user) 0, blok 132587052). "
    "Bridge: tidak berubah (mtime 2026-11-08 18:21); 8 kontrak bridge tidak di snapshot (7 non-discarded ERC-20 mint-pattern + 1 same-owner-discarded Krillfarm) - TIDAK ditambahkan, sesuai run 1831 (lama Nov 3-8, bukan NFT free-mint). "
    "Route 5a: 10 kontrak Sourcify baru (verifiedAt 19:33-19:38 WIB) - semuanya S1=S2=False, bukan sale-shape. Route 5c: 0 kandidat ERC-20 belum dicek >=10 mint di output scan 12:31 (semua sudah dicek / di bawah ambang). "
    "Boltbook EN+ZH: 10 alamat front page, 5 tidak di snapshot utama tapi semuanya sudah di hot-leg-seen + shape-check false (bukan agent-shaped). Sweep web: MALTA/YAMA sudah di track_c gate-blocked (tidak dilaporkan ulang); MOLT AGENT pool habis 25/25 (artikel Colony '18 free left' basi); tidak ada kandidat baru dari sweep."
)
snap["runNote1931_1109_scan"] = (
    "Run 1931 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132586100-132586149), 1 attempt ~13,5 dtk: HTTP 401 Unauthorized "
    "(kredensial custom.ankr ditolak rpc.ankr.com; outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; "
    "gap ke head ~73.796 blok dan tumbuh). Route 5c memakai output scan terakhir 12:31 (0 kandidat baru). "
    "Konfirmasi independen 19:50 WIB (evaluasi gate job lain): Ankr kuota 0% s.d. 1 Des 2026; semua RPC publik BSC jawab eth_getLogs -32005."
)
snap["runNote1931_1109_binanceai"] = (
    "Run 1931 track-B: binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (probe dataseed, blok 132587052). Status closed-refund-phase-2026-11-07; sudah dilaporkan sekali; tidak dilaporkan ulang."
)
snap["runNote1931_1109_age_exclusions"] = (
    f"Run 1931 age-exclusions baru: 0 (kandidat terverifikasi >48h dari daftar aktif: {cands if cands else 'tidak ada'})."
)
snap["runNote1931_1109_early_leads"] = (
    "Run 1931 early lead BARU: Agentic (AGTC) 0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5 - ERC-721 agent-shaped (mintFree no-arg + FREE_SUPPLY 1000 + registry exact), "
    "Sourcify exact_match verifiedAt 19:26:25 WIB, pertama di feed 19:29, freeMinted 118->189 di-run (minting live), free% 18,9% (<25% kaki strong lead), slot user TERBUKA, "
    "owner TIDAK di same-owner-discards, website gate FAILED (metode A-N, tanpa situs terverifikasi). Dilaporkan sekali run ini sebagai EARLY; TIDAK pernah preview/mint. "
    "Sourcify feed 20 terbaru: 10 kontrak baru (19:33-19:38 WIB) semuanya S1=S2=False. Boltbook: 5 alamat baru-vs-snapshot sudah di hot-leg-seen, shape false."
)
snap["runNote1931_1109_discovery"] = (
    "Run 1931 discovery: Agentic (AGTC) 0x7BcC29c5 via Sourcify feed (hot-leg 19:29) - triase penuh run ini (lihat baselineNote Agentic). "
    "MALTA 0x728095Ab... + YAMA 0x86d779fc... muncul lagi di sweep web (AirdropBuzz, dicek 9 Nov) - keduanya SUDAH di track_c gate-blocked, tidak dilaporkan ulang. "
    "MOLT AGENT 0x4B8150f1... disebut thecolony.ai '18 free left' - BASI: on-chain freeMinted 25/25 habis, status excluded. "
    "Tidak ada kandidat/strong-lead/track-C-lead baru dari discovery run ini."
)
snap["runNote1931_1109_velocity"] = (
    f"Run 1931 velocity (interval {INTERVAL} mnt): LOLOS {vel_pass} - keduanya terminal (Mechfarm same-owner-discarded, Skyagent age-excluded), TIDAK promosi. "
    "getpuffr +112 (rate 1,724 vs prev 0,0 - rasio tak terhitung, bukan pass). Rose Genesis +66 (rate 1,016 vs prev 2,648 - melambat). "
    "Bubblebruin +7 (free% 29,19->29,28). HIVE Agents 1256 flat. 13 bacaan all-null = artefak baca, nilai lama dipertahankan."
)
snap["last_run_wib"] = "2026-11-09 19:31 WIB"
snap["last_run"] = "1931"

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
summary = {"updated_contracts": n_upd, "updated_track_c": n_tc, "velocity_pass": vel_pass,
           "age_candidates": cands, "block": BLOCK, "interval_min": INTERVAL}
json.dump(summary, open(f"{BASE}/run-2026-11-09-1931-merge.json", "w"), indent=1)
print("MERGE DONE", json.dumps(summary, indent=1))
