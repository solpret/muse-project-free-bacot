#!/usr/bin/env python3
"""Merge run 2026-11-10 05:31 WIB (tag 0531). Reloads snapshot fresh, applies
reread + discovery findings. Writes snapshot. Scan FAST-FAIL (preflight Ankr 401,
head 132666907) -> watermark NOT advanced. NO execution in this run.
Velocity baseline: snapshot post-merge 0431 (current snapshot before this merge);
interval block-derived 56.68 min (132659645 -> 132667204). Skip-if-fresher:
a contract whose live lastReadBlock is newer than this run's block is skipped.
Additions: THYRK (early lead hot-leg 0524, snapshot-ready entry), JINCHAN + FCAT
(watchlist-only, discovery 0531). Removals: 17 track_c age-excluded (>48h,
launch evidence stored in snapshot).
"""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 56.68
NEW_BLOCK = 132667204

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0531-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = copy.deepcopy(s)
rr = json.load(open(f"{BASE}/run-2026-11-10-0531-reread.json"))
vel = json.load(open(f"{BASE}/run-2026-11-10-0531-velocity.json"))
thyrk = json.load(open(f"{BASE}/run-2026-11-10-0531-thyrk.json"))
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
        note = f"Run 0531 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0531 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0531_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
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

# --- Age-excluded track_c removals (launch evidence stored in snapshot) ---
AGE_OUT = {
 "DeY": "first FreeClaimed 2026-11-04 16:46:29 WIB (~133 jam)",
 "Predictagent-PRDICT": "firstMint 2026-11-05 21:49:35 WIB (~104 jam)",
 "FANBEIMAO-824d": "startAt 2026-11-04 20:00 WIB (~130 jam)",
 "ShibAgent-R2": "startedAt 2026-11-05 05:22:14 WIB (~125 jam; deadline +72 jam 2026-11-08 05:22 lewat)",
 "LuckyBox-LUCK": "first mint 2026-11-05 15:59:44 WIB (~134 jam)",
 "ChimpAgent": "first mint ~2026-11-06 22:06 WIB (~80 jam)",
 "MizzlewickAgent": "first mint 2026-11-07 10:41:45 WIB (~67 jam)",
 "JupiterAgent-JAGT": "first mint 2026-11-07 12:30:30 WIB (~66 jam)",
 "PLNK": "first mint 2026-11-07 09:00:31 WIB (~69 jam)",
 "QuonkersAgent": "first mint 2026-11-07 15:01:11 WIB (~63 jam)",
 "HobnorbAgent": "first mint 2026-11-07 14:56:55 WIB (~63 jam)",
 "WibblezapAgent": "first mint 2026-11-07 15:02:06 WIB (~63 jam)",
 "DribblonAgent": "first mint 2026-11-07 14:56:46 WIB (~63 jam)",
 "YammerjackAgent": "first mint 2026-11-07 14:57:56 WIB (~63 jam)",
 "Draco Coin": "first mint 2026-11-07 18:02:30 WIB (~60 jam)",
 "PHNX": "first mint 2026-11-07 18:43:47 WIB (~59 jam)",
 "OSK": "saleStart 2026-11-03 23:32:53 WIB (~150 jam; saleEnd 2026-11-06 23:32:53 lewat)",
}
removed_tc = []
for name, ev in AGE_OUT.items():
    if name in TC:
        removed_tc.append((name, TC[name].get("status"), ev))
        del TC[name]
    else:
        print("AGE-OUT MISSING:", name)

# --- Additions ---
thyrk_entry = thyrk["snapshot_entry"]
C["THYRK"] = thyrk_entry
C["JINCHAN Agents"] = {
 "address": "0xfc9269a515E56A174AD32923a45868d6e97e7EE2",
 "name": "JINCHAN Agents", "symbol": "JINCHAN", "kind": "ERC721",
 "status": "watchlist-only-2026-11-10-discovery-0531",
 "totalSupply": 83, "MAX_SUPPLY": 1888, "FREE_SUPPLY": 888,
 "mintOpen": 1, "mintedBy_user": 0, "balanceOf_user": 0,
 "registryBytes": True, "free_pct_verified": False,
 "free_pct_inference": "9.3% (83/888, bila semua mint gratis - INFERENSI, bukan verified)",
 "age": "UNVERIFIED (first-mint persis unverified; verifiedAt Sourcify 2026-11-10 05:36 WIB bukan launch)",
 "website": None, "xVerified": False,
 "firstSeenWib": "2026-11-10 05:31 WIB (run 0531, Sourcify feed)",
 "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
 "note": "Discovery run 0531: agent-shaped (registry bytes ADA), aktif minting 53->83, slot user terbuka; free%/umur/website/X/ABI UNVERIFIED - BUKAN early lead terverifikasi penuh (first-mint unverified). Butuh deep-dive (ABI saat Sourcify pulih, first-mint, website A-N). Kemungkinan factory wave (template identik FCAT, verifiedAt berselang 5 detik).",
}
C["FCAT Agents"] = {
 "address": "0x349d8FBed5DE52A4e5065E143797d7B92846Be0e",
 "name": "FCAT Agents", "symbol": "FCAT", "kind": "ERC721",
 "status": "watchlist-only-2026-11-10-discovery-0531",
 "totalSupply": 131, "MAX_SUPPLY": 1888, "FREE_SUPPLY": 888,
 "mintOpen": 1, "mintedBy_user": 0, "balanceOf_user": 0,
 "registryBytes": True, "free_pct_verified": False,
 "free_pct_inference": "14.8% (131/888, bila semua mint gratis - INFERENSI, bukan verified)",
 "age": "UNVERIFIED (first-mint persis unverified; verifiedAt Sourcify 2026-11-10 05:36 WIB bukan launch)",
 "website": None, "xVerified": False,
 "firstSeenWib": "2026-11-10 05:31 WIB (run 0531, Sourcify feed)",
 "lastReadBlock": NEW_BLOCK, "lastReadWib": NOW_STR,
 "note": "Discovery run 0531: agent-shaped (registry bytes ADA), aktif minting 69->131, slot user terbuka; free%/umur/website/X/ABI UNVERIFIED - BUKAN early lead terverifikasi penuh. Butuh deep-dive. Kemungkinan factory wave (template identik JINCHAN).",
}

s["runNote0531_1110"] = (
 f"Run 0531 (blok {NEW_BLOCK}, interval 56.68 mnt vs 0431): re-read 630 kontrak + 91 track_c. "
 f"Velocity LOLOS {len(vel_pass)}: {vel_pass} - promosi 0 (semua gagal kaki lain: free%/umur/website UNVERIFIED atau gate-blocked/discarded/minted-by-user/age-excluded). "
 f"SAKURA: totalSupply 1033->1044, free 1028/6000=17.13%, velocity 1.48x GAGAL, slot UNVERIFIED, umur terverifikasi <=48 jam, website GATE FAILED (contractURI/tokenURI null, Sourcify unverified, pencarian nama nihil) - tetap early lead. "
 f"Golden Agents: velocity LOLOS +212 (24.61x) tapi free%/slot/umur/website UNVERIFIED - tetap early lead. "
 f"THYRK ditambahkan ke snapshot (early lead hot-leg 0524; freeMinted 1179, slot TERBUKA verifikasi segar, website thyrk.fun terverifikasi, umur presisi UNVERIFIED - tetap early lead, BELUM strong lead). "
 f"JINCHAN + FCAT ditambahkan watchlist-only (discovery 0531, agent-shaped, first-mint/umur/website UNVERIFIED - bukan early lead terverifikasi). "
 f"REAPER bukan agent-shaped + free quota habis; AGENT ID Card sold out 3000/3000 - tidak masuk snapshot. "
 f"binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1) - tidak dilaporkan ulang. "
 f"Track C: sellout/paid-only baru TIDAK ADA (NUSA freeMinted 358->359). Age-exclusion track_c 17 item dihapus: {[n for n,_,_ in removed_tc]}. "
 f"Scan FAST-FAIL (preflight Ankr 401, head 132666907); watermark tetap 132512564, gap ~154.343 blok. "
 f"Discovery: Boltbook EN+ZH, Sourcify feed 20, sweep EN+ZH, route 6 (0 item Agent ID), bridge 116 kontrak (8 tidak di snapshot, semua era 3 Nov, bukan baru). "
 f"TIDAK ADA kandidat/strong lead/early lead baru terverifikasi - run DIAM (tidak ada laporan chat)."
)
s["runNote0531_1110_scan"] = (
 "Run 0531 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (head 132666907): FAIL 2.7 dtk HTTP 401 Unauthorized "
 "(kelanjutan outage sejak 2026-11-09 ~13:33 WIB). Scan leg TIDAK dijalankan (amendemen 2026-11-06). "
 "Watermark tetap 132512564; gap ke head ~154.343 blok dan tumbuh (milik backfill). Reconnect Ankr (parent ~13:49 WIB 9 Nov) belum terverifikasi pulih."
)
s["runNote0531_1110_age_exclusions_tc"] = (
 "Track C age-exclusions run 0531 (launch terverifikasi >48 jam, masih di track_c, dihapus dari snapshot): " +
 "; ".join(f"{n} ({ev}; status lama: {st})" for n, st, ev in removed_tc) +
 ". NUSA (~37 jam) dan FOUNT (~27 jam) masih <=48 jam - dipertahankan."
)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated}")
print(f"vel_pass={vel_pass}")
print(f"removed_tc={len(removed_tc)}: {[n for n,_,_ in removed_tc]}")
print(f"contracts now={len(C)} track_c now={len(TC)}")
