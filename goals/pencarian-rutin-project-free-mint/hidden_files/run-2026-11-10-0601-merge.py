#!/usr/bin/env python3
"""Merge run 2026-11-10 06:01 WIB (tag 0601). Reloads snapshot fresh, applies
reread. Writes snapshot. Scan FAST-FAIL (preflight Ankr 401 x2, outage since
2026-11-09 ~13:33 WIB) -> watermark NOT advanced. NO execution in this run.
Velocity baseline: snapshot post-merge 0531 (current snapshot before this merge);
interval block-derived 43.6 min (132667204 ts 1794264572 -> 132673016 ts 1794267188).
Skip-if-fresher: a contract whose live lastReadBlock is newer than this run's
block is skipped.
Removals: HUNT PASS (track A age-excluded: first mint 2026-11-07 02:00:40 WIB,
blok 132061011, ~77 jam > 48 jam; totalMinted 1690/3000, not sold out).
Additions: NONE (NOVA AGENT age-excluded discovery, not added; see run note).
"""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 43.6
NEW_BLOCK = 132673016

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0601-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = copy.deepcopy(s)
rr = json.load(open(f"{BASE}/run-2026-11-10-0601-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
BC = base["contracts"]; BTC = base.get("track_c", {})

updated = 0; degraded = 0; skipped_fresher = 0; vel_pass = []
for name, e in list(BC.items()):
    live = C.get(name)
    if live is None:
        continue
    if isinstance(live.get("lastReadBlock"), int) and live["lastReadBlock"] > NEW_BLOCK:
        skipped_fresher += 1
        continue
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0601 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None and isinstance(prev_sup, int) and isinstance(new_sup, int) and prev_sup < 10_000_000:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("previousRatePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            live["previousTotalSupply"] = prev_sup; live["mintedInInterval"] = minted
            live["intervalMinutes"] = INTERVAL; live["currentRatePerMin"] = rate
            live["previousRatePerMin"] = prev_rate; live["velocityRatio"] = ratio
            live["velocityLegPasses"] = vpass
        live["totalSupply"] = new_sup
        note = f"Run 0601 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0601_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
    updated += 1

tc_updated = 0
for name, e in list(BTC.items()):
    if not isinstance(e, dict):
        continue
    live = TC.get(name)
    if not isinstance(live, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining", "totalFreeShares"):
        if r.get(k) is not None:
            live[k] = r[k]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    tc_updated += 1

# --- HUNT PASS age-exclusion (track A) ---
removed = []
if "HUNT PASS" in C:
    hp = C["HUNT PASS"]
    removed.append(("HUNT PASS", hp.get("status"),
                    "first mint 2026-11-07 02:00:40 WIB blok 132061011 (~77 jam); "
                    "totalMinted 1690/3000 FREE_SUPPLY (56,3%, belum sold out) blok 132673016"))
    del C["HUNT PASS"]
else:
    print("HUNT PASS already absent")

# --- Track A age-watch (NOT removed; evidence incomplete) ---
# MONOLITH: first mint 2026-11-08 17:32:27 WIB, deadline umur 2026-11-10 17:32 WIB (belum lewat).
# Night Bandits Club + King's Game: bacaan free-quota gagal (semua view None) -> 'belum sold out'
# tak terverifikasi; tetap age-watch per preseden run 2231/2301/2331.

s["runNote0601_1110"] = (
 f"Run 0601 (blok {NEW_BLOCK}, interval 43,6 mnt vs 0531): re-read 633 kontrak + 74 track_c "
 f"(degraded totalSupply None: {degraded}). "
 f"Velocity LOLOS {len(vel_pass)}: {vel_pass} - promosi 0 (semua gagal kaki lain: free%/umur/website "
 f"UNVERIFIED atau gate-blocked/discarded/minted-by-user/age-excluded). "
 f"THYRK: totalSupply 1184->1352 (+168, rate ~3,85/mnt), freeMinted 1346/7777=17,3% (INFERENSI bila "
 f"semua mint gratis, bukan verified; % leg N/A), slot TERBUKA (freeUsed=0 hot-leg 0619), website "
 f"thyrk.fun TERVERIFIKASI, umur presisi UNVERIFIED - tetap early lead, BELUM strong lead. "
 f"SAKURA: totalSupply 1081->1109 (+28), freeMinted 1099/6000=18,3% (<25%), velocity GAGAL, slot "
 f"UNVERIFIED (freeClaimed user revert), website GATE FAILED (contractURI/baseURI null, tokenURI "
 f"relatif tanpa site, Sourcify unverified) - tetap early lead. "
 f"HUNT PASS AGE-EXCLUDED + dihapus dari snapshot (first mint 2026-11-07 02:00:40 WIB, ~77 jam; "
 f"totalMinted 1690/3000 belum sold out). "
 f"NOVA AGENT (Boltbook 06:31 WIB) AGE-EXCLUDED, TIDAK masuk snapshot: first mint teramati blok "
 f"131197893 = 2026-11-02 14:05:20 WIB (scan-seen + eth_getBlockByNumber run ini), umur >=7 hari; "
 f"totalSupply 962/5555 belum sold out; website gate JUGA FAILED (contractURI/baseURI null, "
 f"tokenURI(1) relatif '1.json', Sourcify unverified, tanpa situs/X di post). "
 f"binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed user 0, "
 f"saldo 0) - tidak dilaporkan ulang. "
 f"Track C: sellout/paid-only baru TIDAK ADA yang terverifikasi (free views mayoritas None). "
 f"Scan FAST-FAIL (preflight Ankr 401 x2, head 132673015/132673807; outage sejak 2026-11-09 ~13:33 WIB); "
 f"watermark tetap 132512564, gap ke head ~160.500 blok. "
 f"Discovery: Boltbook EN+ZH (NOVA age-excluded; THYRK token di post send.ai), Sourcify feed 20 (3 baru: "
 f"0x0D19/0x2F10/0xB3f4 - ketiganya kontrak DeFi zap/position-manager, 0 hit S1/S2), sweep EN+ZH + "
 f"Binance Square (0 proyek baru; MOLT AGENT + PixelFox sudah di snapshot; AgentForge/PocketDragons/"
 f"Hundred/Agent Radar Pass/BLOB Miner semua Okt/awal-Nov, umur >48 jam), Odaily 0, PANews 0, "
 f"bridge 116 kontrak (mtime tak berubah 2026-11-08 18:21 UTC; 8 tidak di snapshot, sama seperti run 0531). "
 f"TIDAK ADA kandidat/strong lead/early lead baru - run DIAM kecuali laporan sekali age-exclusion "
 f"HUNT PASS (+ NOVA sebagai temuan Boltbook yang gugur umur)."
)
s["runNote0601_1110_scan"] = (
 "Run 0601 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok: FAIL 8,1 dtk HTTP 401 Unauthorized "
 "(head 132673015), retry FAIL 6,2 dtk HTTP 401 (head 132673807). Kelanjutan outage Ankr sejak "
 "2026-11-09 ~13:33 WIB (preflight 0531 juga 401). Scan leg TIDAK dijalankan (amendemen 2026-11-06: "
 "credits-exhausted/paid-gate error -> stop leg run ini, lanjut route lain, tanpa bayar). "
 "Watermark tetap 132512564; gap ke head ~160.500 blok dan tumbuh (milik backfill, backfill OFF). "
 "5c dilewati (tanpa output scan)."
)
s["runNote0601_1110_age_exclusions"] = (
 "Age-exclusion run 0601 (launch terverifikasi >48 jam, belum sold out): " +
 "; ".join(f"{n} ({ev}; status lama: {st})" for n, st, ev in removed) +
 ". NOVA AGENT 0x1b6E6F62528DE674C12BC2C04C159336d3DB049e (temuan Boltbook run ini, BUKAN di snapshot): "
 "first mint teramati blok 131197893 = 2026-11-02 14:05:20 WIB (onchain-scan-seen.json + "
 "eth_getBlockByNumber run ini, ts 1793603120); totalSupply 962/5555 (blok 132674465) belum sold out; "
 "TIDAK masuk snapshot, TIDAK dilaporkan sebagai lead. "
 "MONOLITH belum lewat deadline umur (2026-11-10 17:32 WIB). Night Bandits Club + King's Game tetap "
 "age-watch (free-quota tak terbaca)."
)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated}")
print(f"vel_pass={vel_pass}")
print(f"removed={removed}")
print(f"contracts now={len(C)} track_c now={len(TC)}")
