#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-14 13:31 WIB into onchain-snapshot.json.
Read-only on-chain (data from run-2026-11-14-1331-reread.json); updates snapshot
entries, velocity fields, run notes, Dawn Agent entry + ORBIT track_c update. No preview/mint."""
import json, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-1331-reread.json"))
BLOCK = reread["block"]  # 133492650
PREV_BLOCK = 133492650
INTERVAL_MIN = round((BLOCK - PREV_BLOCK) / 2.22 / 60, 1)  # ~30.5
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

# supply-view key per contract (which field counts as total minted)
def supply_of(views):
    for k in ("totalSupply", "totalMinted", "totalSpecimens", "totalRemnants"):
        if views.get(k) is not None:
            return k, views[k]
    return None, None

velocity_pass = []
notes = {}
for name, rd in reread["reads"].items():
    views = rd.get("views") or {}
    entry = snap["contracts"].get(name)
    if entry is None:
        # key may differ (e.g. 'BinanceAI-mint'); find by address
        addr = (rd.get("address") or "").lower()
        for k, v in snap["contracts"].items():
            if isinstance(v, dict) and str(v.get("address") or "").lower() == addr:
                entry = v; name = k; break
    if entry is None or not isinstance(entry, dict):
        notes[name] = "NO SNAPSHOT ENTRY (read-only, skipped)"
        continue
    skey, sval = supply_of(views)
    prev_supply = entry.get("totalSupply", entry.get("totalMinted"))
    prev_rate = entry.get("currentRatePerMin")
    # update raw fields present in views
    for f in ("totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "FREE_MAX", "FREE_CAP", "mintOpen",
              "mintedBy", "freeUsed", "balanceOf", "price", "AGENT_ID"):
        pass
    if views.get("totalSupply") is not None:
        entry["totalSupply"] = views["totalSupply"]
    if views.get("totalMinted") is not None:
        entry["totalMinted"] = views["totalMinted"]
    if views.get("freeClaimed") is not None:
        entry["freeClaimed"] = views["freeClaimed"]
    if views.get("freeMinted") is not None:
        entry["freeMinted"] = views["freeMinted"]
    if views.get("FREE_SUPPLY") is not None:
        entry["FREE_SUPPLY"] = views["FREE_SUPPLY"]
    if views.get("FREE_MAX") is not None:
        entry["FREE_MAX"] = views["FREE_MAX"]
    if views.get("MAX_SUPPLY") is not None:
        entry["MAX_SUPPLY"] = views["MAX_SUPPLY"]
    if views.get("mintOpen") is not None:
        entry["mintOpen"] = views["mintOpen"]
    if views.get("balanceOf_user") is not None:
        entry["balanceOf_user"] = views["balanceOf_user"]
    if views.get("mintedBy_user") is not None:
        entry["mintedBy_user"] = views["mintedBy_user"]
    if views.get("freeUsed_user") is not None:
        entry["freeUsed_user"] = views["freeUsed_user"]
    if views.get("freeClaimed_user") is not None:
        entry["freeClaimed_user"] = views["freeClaimed_user"]
    if views.get("price") is not None:
        entry["price"] = views["price"]
    entry["lastReadBlock"] = BLOCK
    entry["lastReadWib"] = "2026-11-14 ~13:31 WIB"
    # velocity
    if sval is not None and prev_supply is not None:
        d = sval - prev_supply
        entry["previousTotalSupply"] = prev_supply
        entry["mintedInInterval"] = d
        entry["intervalMinutes"] = INTERVAL_MIN
        cur_rate = round(d / INTERVAL_MIN, 4) if INTERVAL_MIN else 0.0
        entry["previousRatePerMin"] = prev_rate
        entry["currentRatePerMin"] = cur_rate
        ratio = round(cur_rate / prev_rate, 2) if prev_rate else None
        entry["velocityRatio"] = ratio
        passes = bool(prev_rate is not None and ratio is not None and ratio >= 1.5 and d >= 20)
        entry["velocityLegPasses"] = passes
        # free pct where computable
        fc = entry.get("freeClaimed", entry.get("freeMinted"))
        fs = entry.get("FREE_SUPPLY", entry.get("FREE_MAX", entry.get("FREE_CAP")))
        if fc is not None and fs:
            entry["free_pct"] = round(100.0 * fc / fs, 1)
        note = (f"Run 1331 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1301): "
                f"{prev_supply}->{sval} (d={d}, rate {cur_rate}/mnt, ratio {ratio}) -> "
                f"velocity {'LOLOS' if passes else 'GAGAL'}")
        if entry.get("free_pct") is not None:
            note += f"; free={fc}/{fs}={entry['free_pct']}%"
        if entry.get("mintOpen") is not None:
            note += f"; mintOpen={entry['mintOpen']}"
        if entry.get("balanceOf_user") is not None:
            note += f"; bal_user={entry['balanceOf_user']}"
        entry["runNote1331_1114"] = note
        if passes:
            velocity_pass.append(name)
    else:
        entry["runNote1331_1114"] = (f"Run 1331 (blok {BLOCK}): baca "
            f"{'GAGAL/null untuk ' + str(skey) if sval is None else 'OK ' + str(skey) + '=' + str(sval)}"
            f"; nilai lama dipertahankan" if sval is None else f"; total {skey}={sval}")
        if sval is not None:
            entry["previousTotalSupply"] = prev_supply
            entry["mintedInInterval"] = None
            entry["intervalMinutes"] = INTERVAL_MIN
            entry["previousRatePerMin"] = prev_rate
            entry["currentRatePerMin"] = None
            entry["velocityRatio"] = None
            entry["velocityLegPasses"] = False

# Dawn Agent (new Boltbook find, checked this run - watchlist-only, NOT an early lead)
snap.setdefault("contracts", {})
snap["contracts"]["Dawn Agent"] = {
    "address": "0xe32cb801c5fd38b44cd3eaa796963307724418c1",
    "status": "watchlist-only-checked-not-lead-2026-11-14",
    "name": "Dawn Agent",
    "symbol": "DAWNAGENT",
    "kind": "ERC721",
    "totalSupply": 4901,
    "MAX_SUPPLY": 5000,
    "balanceOf_user": 0,
    "mintedBy_user": 0,
    "xVerified": False,
    "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: tidak ada stated launch time; post Boltbook 13:27 WIB (dieuxuan50.ai) klaim 4.901/5.001 free (98%) + FREE 1/.ai; Sourcify UNVERIFIED. Angka 4.901/5.001 yang sama juga muncul di post Aero Agent halaman yang sama (kemungkinan copy-paste).",
    "baselineNote": "Dicek on-chain run 1331: name/symbol Dawn Agent/DAWNAGENT; registry bytes 0x60B926... exact di bytecode; selector mint(uint256)+totalSupply ada; TAPI semua free view REVERT (FREE_SUPPLY/freeMinted/freeClaimed/mintOpen/priceFor/costOf/hasAgentId/agentRegistry) -> bentuk free TIDAK terverifikasi. 0 Transfer events dalam 2000 blok terakhir (publicnode topic0-only, kontrol USDT/ORBIT membuktikan query bekerja) -> minting stalled, pace 0. BUKAN early lead (first mint tak terverifikasi on-chain run ini + tanpa bukti free-mint). Watchlist-only.",
    "firstSeenWib": "2026-11-14 ~13:24 WIB (hot-leg-seen, source boltbook)",
    "lastReadBlock": 133497052,
    "lastReadWib": "2026-11-14 ~13:35 WIB",
}

# Track C: ORBIT update (age verification attempts this run)
snap.setdefault("track_c", {})
_orbit = snap["track_c"].get("ORBIT", {})
_orbit["freeClaimed"] = 232
_orbit["previousFreeClaimed"] = 152
_orbit["free_pct"] = 26.1
_orbit["lastReadBlock"] = BLOCK
_orbit["lastReadWib"] = "2026-11-14 ~13:31 WIB"
_orbit["runNote1331_1114"] = (
    "Run 1331 (blok 133496709): freeClaimed 152->228/888 (25,7%; live 232 di blok 133499135), claimOpen 1, "
    "hasFreeClaimed(user)=0, +76 dalam ~30 mnt (burst: +3/20mnt sebelumnya, +4/18mnt sesudahnya); totalSupply FLAT 47.252.000. "
    "Umur TETAP UNVERIFIED: first-claim TIDAK terverifikasi — Ankr 401; dataseed eth_getLogs TERBUKTI kosong untuk SEMUA kontrak "
    "(kontrol USDT 0 log/200 blok, padahal publicnode 11.506); publicnode getLogs kontradiktif antar-query pada rentang tumpang tindih "
    "(68 mint 10k di 133492650-133494650 vs 0 log di chunk tumpang tindih 133493634-133494633; filter topic-2 tidak andal, pakai topic0-only + filter klien) "
    "-> bukti log tidak dapat diandalkan; publicnode archive eth_call cutoff ~blok 133485000-133490000 (archive butuh personal token), "
    "freeClaimed sudah 149 di 133490000 -> first claim mendahului jendela archive. Tetap watchlist-only, BUKAN lead, TIDAK preview/mint. DIAM."
)
snap["track_c"]["ORBIT"] = _orbit

# Track B: binanceai.fun pending claim re-check (refund phase unchanged)
_pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
_pc["launched"] = 0
_pc["failed"] = 1
_pc["isRefundPhase"] = 1
_pc["totalShares"] = 3110
_pc["tokenClaimed_user"] = 0
_pc["lastReadWib"] = "2026-11-14 ~13:31 WIB"
_pc["runNote1331"] = (
    "Run 1331: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
    f"(blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
)

snap["runNote1331_1114"] = (
    "Run 1331: reread 33/33 OK blok 133496709 (158,8 dtk, interval ~30,5 mnt vs run 1301). Velocity: 1 LOLOS (AgentNOVA +21, 0,69/mnt vs prev 0,21 = 3,22x) "
    "TAPI free% UNVERIFIED (tidak ada free view) -> BUKAN kandidat/strong lead. B77D +38 (1,25/mnt vs prev 0,89 = 1,40x) GAGAL tipis (<1,5x). "
    "RaceAgents 533->538 (+5) free 53,8% tapi velocity 0,51x GAGAL. CPASS 1453->1468 (+15, 0,29x) GAGAL. REOPIR +8 (0,17x) GAGAL; free 6,2%. "
    "WANGCAI 128/188=68,1% FLAT (<70%, bukan strong lead; slot terbuka, umur <24j terverifikasi, website NONE -> gate FAILS); YUANBAO 117/188=62,2% FLAT. "
    "DragonAgents 728, free 724/888=81,5% tapi age-excluded-2026-11-14 + umur UNVERIFIED -> BUKAN strong lead. HIVE 1263 FLAT, minted-by-user. "
    "Zero totalSupply/freeClaimed gagal baca lagi (nilai lama dipertahankan); PX24 totalSupply gagal baca run ini. "
    "ORBIT freeClaimed 152->228/888 (25,7%), umur TETAP UNVERIFIED (first-claim tak terverifikasi; bukti log tidak andal — lihat track_c). "
    "Dawn Agent BARU dicek -> watchlist-only (bukan early lead; lihat runNote boltbook). "
    "Scan leg FAST-FAIL (Ankr 401 pre-flight 3,6 dtk), watermark tetap 132512564. "
    "Sourcify feed: 0 baru vs hot-leg-seen (20 kontrak, verifiedAt 05:48-06:30 UTC, semua sudah diproses hot-leg). "
    "Boltbook EN+ZH: Dawn Agent baru (lihat atas); Nero Agent 9.900/10.000 FLAT (free views revert, Sourcify unverified, watchlist-only); "
    "Lion's Share 1.116/1.450 age-excluded-2026-11-08; DragonAgents (lihat atas); Pickhash checked-not-agent-shaped; BOLT footer links bukan proyek. "
    "Sweep EN+ZH: 0 baru (Agentic Gangster free pool habis; STAMP PASS sold-out; AGENT COSMOS + TINY AGENTS lewat umur; AgentForge 27 Okt, lewat umur). "
    "Odaily 0 penyebutan Agent ID. Bridge 116 kontrak, 0 baru (mtime 2026-11-08 18:21). binanceai tetap refund phase (launched 0, failed 1). "
    "0 eksekusi/preview. DIAM."
)
snap["runNote1331_1114_scan"] = (
    "Scan leg FAST-FAIL run 1331: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam ~3,6 dtk "
    "(helper custom.ankr ankr.py logs, blok 133496659-133496709). Scan TIDAK dijalankan; watermark tetap 132512564; "
    "track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini)."
)
snap["runNote1331_1114_feedshape"] = (
    "Feed Sourcify run 1331 (limit 20, verifiedAt 05:48-06:30 UTC): 0 baru vs hot-leg-seen "
    "(20/20 sudah diproses hot-leg run 1324/1329; 2 teratas 0xE100Ba95 + 0xA27e3102 sudah shape-check hot-leg: S1/S2 False). "
    "Tidak ada kontrak baru untuk shape-check run ini."
)
snap["runNote1331_1114_boltbook"] = (
    "Boltbook EN+ZH run 1331 (fetch ~13:32 WIB, EN 44.121 byte, ZH 42.497 byte, 9 alamat, 7 proyek): "
    "Dawn Agent 0xe32c... (BARU, dieuxuan50.ai 13:27 WIB, klaim 4.901/5.001 free 98% + FREE 1/.ai) -> dicek on-chain run ini: "
    "name/symbol Dawn Agent/DAWNAGENT, totalSupply 4901, MAX_SUPPLY 5000, registry bytes exact di bytecode, TAPI semua free view revert + Sourcify UNVERIFIED + "
    "0 Transfer events dalam 2000 blok terakhir (publicnode topic0-only, kontrol USDT/ORBIT membuktikan query bekerja) -> BUKAN early lead "
    "(first mint tak terverifikasi + tanpa bukti free-mint); masuk snapshot watchlist-only. "
    "Catatan: angka 4.901/5.001 yang sama juga muncul di post Aero Agent halaman yang sama (kemungkinan copy-paste). "
    "Nero Agent 9.900/10.000 FLAT (watchlist-only-unverified, free views revert). Lion's Share 1.116/1.450 age-excluded-2026-11-08. "
    "DragonAgents 727->728 (lihat run note utama). Pickhash checked-not-agent-shaped. BOLT + BoltRewards = footer platform, bukan proyek. "
    "0 early lead baru dari Boltbook run ini."
)
snap["last_run"] = "run 1331 2026-11-14"
snap["last_run_wib"] = "2026-11-14 ~13:31 WIB"
snap["last_run_note"] = snap["runNote1331_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("MERGED. velocity_pass:", velocity_pass)
print("reads:", reread["reads_ok"], "/", reread["reads_total"], "block:", BLOCK)
