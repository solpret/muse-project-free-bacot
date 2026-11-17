#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-14 13:01 WIB into onchain-snapshot.json.
Read-only on-chain (data from run-2026-11-14-1301-reread.json); updates snapshot
entries, velocity fields, run notes, track_c BRAVO entry. No preview/mint."""
import json, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-1301-reread.json"))
BLOCK = reread["block"]  # 133492650
PREV_BLOCK = 133488906
INTERVAL_MIN = round((BLOCK - PREV_BLOCK) / 2.22 / 60, 1)  # ~28.1
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
    entry["lastReadWib"] = "2026-11-14 ~13:01 WIB"
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
        note = (f"Run 1301 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1231): "
                f"{prev_supply}->{sval} (d={d}, rate {cur_rate}/mnt, ratio {ratio}) -> "
                f"velocity {'LOLOS' if passes else 'GAGAL'}")
        if entry.get("free_pct") is not None:
            note += f"; free={fc}/{fs}={entry['free_pct']}%"
        if entry.get("mintOpen") is not None:
            note += f"; mintOpen={entry['mintOpen']}"
        if entry.get("balanceOf_user") is not None:
            note += f"; bal_user={entry['balanceOf_user']}"
        entry["runNote1301_1114"] = note
        if passes:
            velocity_pass.append(name)
    else:
        entry["runNote1301_1114"] = (f"Run 1301 (blok {BLOCK}): baca "
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

# Track C: BRAVO (new discovery, watchlist-only, age unverified)
snap.setdefault("track_c", {})
snap["track_c"]["BRAVO"] = {
    "name": "BRAVO",
    "sale": "0xd57a06f0c37e303704261080Fc884f7BE941331D",
    "token": "0xd5e97D76560cef39a29C3C401Da42749d6F67B94",
    "awardsLedger": "0x13b7b91f02891878A0C0025AEaCf34E14c220275",
    "status": "watchlist-only-age-unverified-2026-11-14",
    "source": "Boltbook post /p/BYK8UA5pp0cU run 1301 + verifikasi on-chain run ini",
    "freeClaimed": 242, "FREE_SHARES": 888, "free_pct": 27.3,
    "seatsTaken": 242, "paidSold": 0, "openedAt": 0,
    "DOORS_OPEN": 1794582000, "doorsOpenWib": "2026-11-15 22:00 WIB",
    "canBook_user": 1, "bookedOf_user": 0, "quote_user_1": None,
    "website": "https://bravo.fcfs.workers.dev/",
    "websiteEvidence": "situs mencetak kontrak persis (Hall + Token + AwardsLedger)",
    "shape": "S1-variant: quote() + freeClaimed/FREE_SHARES + claimFree + agentIdOf/agentIds gate; TANPA fungsi mint(); TANPA registry bytes 0x60B926...22F di bytecode",
    "launchNote": "Umur UNVERIFIED: tidak ada stated launch time; post Boltbook hari ini menyebut 'pagi tadi masih 194' (launch <= 14 Nov pagi); first-mint log terblokir (Ankr 401). BUKAN lead (umur unverified + free 27,3% <50%/<70%).",
    "x_discussion": "unverified",
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~13:01 WIB",
}

snap["runNote1301_1114"] = (
    "Run 1301: reread 33/33 OK blok 133492650 (131,3 dtk). Velocity: 1 LOLOS (REOPIR +44, 1,57/mnt vs prev 0,0667 = 23,5x) "
    "TAPI free 424/7000=6,1% -> BUKAN kandidat/strong lead. RaceAgents 524->533 (+9, <20) free 533/1000=53,3% tapi velocity GAGAL -> bukan kandidat. "
    "CPASS 1405->1453 (+48, 1,71/mnt vs prev 2,13 = 0,80x) GAGAL; B77D 904->929 (+25, 0,89 vs 1,6 = 0,56x) GAGAL. "
    "WANGCAI 128/188=68,1% FLAT (<70%, bukan strong lead; slot terbuka, umur <24j terverifikasi, website NONE -> gate FAILS); YUANBAO 117/188=62,2% FLAT. "
    "DragonAgents 726 FLAT, free 722/888=81,3% tapi umur UNVERIFIED + velocity 0 -> BUKAN strong lead. "
    "Zero totalSupply/freeClaimed gagal baca lagi (nilai lama dipertahankan); PX24 totalSupply gagal baca run ini. "
    "ORBIT freeClaimed 148->152/888 (17,1%), umur UNVERIFIED. "
    "Scan leg FAST-FAIL (Ankr 401 pre-flight 11,7 dtk), watermark tetap 132512564. "
    "Sourcify feed: 1 baru vs hot-leg-seen (0xe33252c8... sellBatch, 8 fns, tanpa mint/free/registry -> BUKAN agent-shaped, BUKAN S1/S2). "
    "Boltbook EN+ZH: Forge Pass 721/20.000 (umur unverified, gate FAILS, flat); Flare Agent 9.901/10.001 (99,0%, FLAT sejak 9 Nov, umur unverified); "
    "TINY AGENTS free pool 0 (sold out, sudah excluded); Pickhash checked-not-agent-shaped (sudah dicatat run 1031); "
    "BRAVO BARU -> track_c watchlist-only (242/888=27,3% free, pool belum buka 15 Nov 22:00 WIB, umur UNVERIFIED, situs mencetak kontrak persis); "
    "CX 854/713 (91,8% free, pace 0) TANPA alamat kontrak di post -> tidak bisa diverifikasi on-chain run ini. "
    "Sweep EN+ZH: 0 baru (Oathbots/Agentic Gangster/Meow Cards/First-Dollar Grove/AGENT COSMOS/Subsonic Tribe dkk sudah dikenal/lewat umur). "
    "Odaily 0 penyebutan Agent ID. Bridge 116 kontrak, 0 baru. binanceai tetap refund phase (launched 0, failed 1). "
    "0 eksekusi/preview. DIAM."
)
snap["runNote1301_1114_scan"] = (
    "Scan leg FAST-FAIL run 1301: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 11,7 dtk "
    "(helper custom.ankr ankr_post, blok 133492600-133492650). Scan TIDAK dijalankan; watermark tetap 132512564; "
    "track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini)."
)
snap["runNote1301_1114_feedshape"] = (
    "Feed Sourcify run 1301 (limit 20, verifiedAt 05:14-06:06 UTC): 1 baru vs hot-leg-seen: "
    "0xe33252c80321e377176ab4612149c611C34291F2 (verified 06:06:09Z) — ABI 8 fns (owner/rescue/sellBatch/sellBatchMerged/sellBatchMergedV3/sellBatchV3/sellFor/sellForV3), "
    "tanpa mint, tanpa free view, tanpa registry/AgentGate -> BUKAN agent-shaped, BUKAN S1/S2, tidak masuk snapshot."
)
snap["runNote1301_1114_boltbook"] = (
    "Boltbook EN+ZH run 1301 (crawl 06:07-06:08 UTC): BRAVO (baru, lihat track_c); ANOVA = AgentNOVA 0x4346...9540 (sudah di snapshot, 446/6.666, pace 0,2/mnt); "
    "CX (854/713, 91,8% free, pace 0) tanpa alamat kontrak di post — tidak terverifikasi on-chain; "
    "Forge Pass 721/20.000; Flare Agent 9.901/10.001 FLAT; TINY AGENTS freeRemaining 0; Pickhash 1.997/10.000 (checked-not-agent-shaped). "
    "0 early lead baru dari Boltbook run ini."
)
snap["last_run"] = "run 1301 2026-11-14"
snap["last_run_wib"] = "2026-11-14 ~13:01 WIB"
snap["last_run_note"] = snap["runNote1301_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("MERGED. velocity_pass:", velocity_pass)
print("reads:", reread["reads_ok"], "/", reread["reads_total"], "block:", BLOCK)
