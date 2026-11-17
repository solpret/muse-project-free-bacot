#!/usr/bin/env python3
"""Merge run 2026-11-10 07:01 WIB (tag 0701). Reloads snapshot fresh, applies
reread. Writes snapshot. Scan FAST-FAIL (preflight Ankr 401 x2, outage since
2026-11-09 ~13:33 WIB) -> watermark NOT advanced. NO execution in this run.
Velocity baseline: snapshot post-merge 0601 (current snapshot before this merge);
interval block-derived 32.48 min (132673016 ts 1794267188 -> 132677349 ts 1794269137).
Skip-if-fresher: a contract whose live lastReadBlock is newer than this run's
block is skipped.
Removals: NONE. Additions: NONE.
FCAT/JINCHAN Agents: free% now verified on-chain (282/888, 150/888); see run note.
"""
import json, shutil, copy
from datetime import datetime, timezone, timedelta

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 32.48
NEW_BLOCK = 132677349

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0701-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
base = copy.deepcopy(s)
rr = json.load(open(f"{BASE}/run-2026-11-10-0701-reread.json"))
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
        note = f"Run 0701 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
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
        note = f"Run 0701 (blok {NEW_BLOCK}, {NOW_STR}): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            live[k] = r[k]
    if r.get("balanceOf_user") is not None:
        live["balanceOf_user"] = r["balanceOf_user"]
    if r.get("freeClaimed_user") is not None:
        live["freeClaimed_user"] = r["freeClaimed_user"]
    live["lastReadBlock"] = NEW_BLOCK; live["lastReadWib"] = NOW_STR
    live["runNote0701_1110"] = note + f"free={live.get('freeClaimed')}/{live.get('FREE_SUPPLY')}; bal_user={live.get('balanceOf_user')}; status {live.get('status')}."
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

# --- NO age-exclusion this run ---
# MONOLITH: first mint 2026-11-08 17:32:27 WIB, deadline umur 2026-11-10 17:32 WIB (belum lewat).
# Night Bandits Club: launch TERVERIFIKASI 2026-11-07 18:02:28 WIB (~61,5 jam > 48 jam) TAPI semua
# view free-quota None run ini -> 'belum sold out' tak terverifikasi; tetap age-watch per preseden
# run 2231/2301/2331/0601. King's Game: launch UNVERIFIED (first-seen 2026-11-07 21:06 hanya lower
# bound) -> tetap age-watch, bukan exclusion.
removed = []

# --- FCAT / JINCHAN Agents special updates (run 0701 deep-dive) ---
fcat = C.get("FCAT Agents")
if isinstance(fcat, dict):
    fcat["freePctVerified"] = round(282 / 888 * 100, 2)
    fcat["freePctNote0701"] = (
        "Run 0701: freeClaimed 282/888 = 31,8% TERVERIFIKASI (run 0531: free% UNVERIFIED/inferensi "
        "14,8%; run 0601: 130/888 inferensi). AGENT_ID() = registry persis "
        "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; mintedBy(user)=0 (slot TERBUKA); price()=0,0002 BNB "
        "(paid lane; cost(1) revert); balanceOf(user)=0; blok 132678219. Diskusi publik ADA: 3 post "
        "Boltbook independen hari ini (1328.ai ~06:47 WIB blok 132671871, grandtheftauto6.ai ~06:48 WIB "
        "blok 132672277, vibibiy.ai 07:05:08 WIB blok 132676893). Website GATE FAILED metode (A) address "
        "search (hanya same-name kontrak lain: FAMECAT 0xdfcb..., Fortune Cat 0xeda2...), (G) name search, "
        "(H) contractURI tanpa URL, (I) tokenURI data-URI tanpa URL; tanpa situs/X di post. Umur "
        "UNVERIFIED (first-mint blok belum terbaca; getLogs mati; Sourcify verifiedAt 22:36:36Z bukan "
        "launch time). Owner 0x23f5cdd233925ea83369a495b95f825ed710fbaa TIDAK ada di "
        "same-owner-discards.json (grep 0). Tetap watchlist-only - BELUM strong lead (umur + website "
        "belum terverifikasi). TIDAK preview/mint."
    )
jin = C.get("JINCHAN Agents")
if isinstance(jin, dict):
    jin["freePctVerified"] = round(150 / 888 * 100, 2)
    jin["freePctNote0701"] = (
        "Run 0701: totalSupply 130->150 (+20), freeClaimed 150/888 = 16,9% TERVERIFIKASI (run 0531: "
        "inferensi 9,3%). <25% strong-lead leg. Slot terbuka (mintedBy(user)=0, 0531). Umur/website "
        "UNVERIFIED. Tetap watchlist-only."
    )

# --- Track A age-watch (NOT removed; evidence incomplete) ---
# MONOLITH: first mint 2026-11-08 17:32:27 WIB, deadline umur 2026-11-10 17:32 WIB (belum lewat).
# Night Bandits Club + King's Game: bacaan free-quota gagal (semua view None) -> 'belum sold out'
# tak terverifikasi; tetap age-watch per preseden run 2231/2301/2331.

s["runNote0701_1110"] = (
 f"Run 0701 (blok {NEW_BLOCK}, interval 32,48 mnt vs 0601): re-read 632 kontrak + 74 track_c "
 f"(degraded totalSupply None: {degraded}). "
 f"Velocity LOLOS {len(vel_pass)}: {vel_pass} - promosi 0 (semua gagal kaki lain: free%/umur/website "
 f"UNVERIFIED atau gate-blocked/discarded/minted-by-user/age-excluded). "
 f"FCAT Agents: totalSupply 214->282 (+68, rate 2,09/mnt vs prev 1,904 = 1,10x, velocity GAGAL (prev rate tersimpan 1,904/mnt, bukan 1,078 - angka 1,078 adalah prev rate JINCHAN)), "
 f"freeClaimed 282/888 = 31,8% TERVERIFIKASI (baru: run 0531/0601 hanya inferensi), slot TERBUKA "
 f"(mintedBy(user)=0, AGENT_ID()=registry persis), diskusi publik ADA (3 post Boltbook independen "
 f"hari ini), TAPI umur UNVERIFIED + website GATE FAILED (metode A/G/H/I) -> tetap watchlist-only, "
 f"BELUM strong lead, TIDAK preview/mint. JINCHAN Agents (twin): 130->150 (+20), freeClaimed 150/888 "
 f"= 16,9% TERVERIFIKASI (<25%), umur/website UNVERIFIED -> tetap watchlist-only. "
 f"THYRK: totalSupply 1352->1505 (+153, rate 4,71/mnt vs prev 3,85 = 1,22x, velocity GAGAL), "
 f"freeMinted 1499/7777=19,3% (INFERENSI bila semua mint gratis, bukan verified; % leg N/A), slot "
 f"TERBUKA, website thyrk.fun TERVERIFIKASI, umur presisi UNVERIFIED - tetap early lead, BELUM strong lead. "
 f"SAKURA: totalSupply 1109->1142 (+33), freeMinted 1132/6000=18,9% (<25%), slot UNVERIFIED "
 f"(freeClaimed user revert), website GATE FAILED - tetap early lead. "
 f"Age-exclusion baru: TIDAK ADA. MONOLITH deadline umur 2026-11-10 17:32 WIB (belum lewat). Night "
 f"Bandits Club (launch terverifikasi 2026-11-07 18:02, ~61,5 jam) + King's Game (launch UNVERIFIED) "
 f"tetap age-watch (semua view free-quota None run ini -> 'belum sold out' tak terverifikasi; preseden "
 f"run 2231/2301/2331/0601). "
 f"binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund=1, totalShares 3110, tokenClaimed user 0, "
 f"saldo 0) - tidak dilaporkan ulang. "
 f"Track C: sellout/paid-only baru TIDAK ADA yang terverifikasi (21 item dgn free data segar; BI NIU "
 f"freeSharesRemaining 0 sudah excluded; NUSA freeMinted 361->362 masih terbuka ~38 jam; FOUNT 1000 "
 f"tetap). "
 f"Scan FAST-FAIL (preflight Ankr 401 x2, 3,2 dtk + 2,3 dtk; outage sejak 2026-11-09 ~13:33 WIB); "
 f"watermark tetap 132512564, gap ke head ~165.000 blok. "
 f"Discovery: Boltbook EN 200 48.019B + ZH 200 48.050B (FCAT post vibibiy.ai 07:05 WIB + THYRK; alamat "
 f"lain di footer: BoltRewards/BOLT infrastruktur), Sourcify feed 20 (4 baru vs 0601: 0x622a/0x9BD7/"
 f"0xe47b/0xf500 - token sync/ERC-20 polos/staking-farm, 0 hit S1/S2), sweep ZH + Binance Square (0 "
 f"proyek baru; AgentID AGI = Ethereum, di luar scope), Odaily 0, PANews 0, "
 f"bridge 116 kontrak (mtime tak berubah 2026-11-08 18:21 UTC; 8 tidak di snapshot, sama seperti run 0601). "
 f"TIDAK ADA kandidat/strong lead/early lead baru - run DIAM."
)
s["runNote0701_1110_scan"] = (
 "Run 0701 scan: FAST-FAIL. Pre-flight Ankr ankr_getLogs 50 blok (132677300-132677349): FAIL 3,2 dtk "
 "HTTP 401 Unauthorized, retry FAIL 2,3 dtk HTTP 401. Kelanjutan outage Ankr sejak 2026-11-09 ~13:33 "
 "WIB (preflight 0601 juga 401). Scan leg TIDAK dijalankan (amendemen 2026-11-06: "
 "credits-exhausted/paid-gate error -> stop leg run ini, lanjut route lain, tanpa bayar). "
 "Watermark tetap 132512564; gap ke head ~165.000 blok dan tumbuh (milik backfill, backfill OFF). "
 "5c dilewati (tanpa output scan)."
)
s["runNote0701_1110_age_exclusions"] = (
 "Age-exclusion run 0701: TIDAK ADA. MONOLITH belum lewat deadline umur (2026-11-10 17:32 WIB). "
 "Night Bandits Club (launch terverifikasi 2026-11-07 18:02:28 WIB, ~61,5 jam > 48 jam) tetap age-watch: "
 "semua view free-quota None run ini sehingga 'belum sold out' tak terverifikasi (preseden run "
 "2231/2301/2331/0601). King's Game tetap age-watch (launch UNVERIFIED; first-seen 2026-11-07 21:06 "
 "hanya lower bound)."
)

json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"updated={updated} degraded={degraded} skipped_fresher={skipped_fresher} tc_updated={tc_updated}")
print(f"vel_pass={vel_pass}")
print(f"removed={removed}")
print(f"contracts now={len(C)} track_c now={len(TC)}")
