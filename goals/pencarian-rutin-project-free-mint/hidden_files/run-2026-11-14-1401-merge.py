#!/usr/bin/env python3
"""Merge free-mint-search run 2026-11-14 14:01 WIB into onchain-snapshot.json.
Read-only on-chain (data from run-2026-11-14-1401-reread.json + triage jsons);
updates snapshot entries, velocity fields, run notes, new Boltbook finds
(Ledgera/MAMI/INKI watchlist-only, CrossEyed no-code, PICK shape correction,
KOMA age-excluded), ORBIT track_c + binanceai pending. No preview/mint."""
import json

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-1401-reread.json"))
BLOCK = reread["block"]  # 133500940
PREV_BLOCK = 133496709  # run 1331 block
INTERVAL_MIN = round((BLOCK - PREV_BLOCK) / 2.22 / 60, 1)  # ~31.8

def supply_of(views):
    for k in ("totalSupply", "totalMinted", "totalSpecimens", "totalRemnants"):
        if views.get(k) is not None:
            return k, views[k]
    return None, None

velocity_pass = []
vel_lines = []
notes = {}
for name, rd in reread["reads"].items():
    views = rd.get("views") or {}
    entry = snap["contracts"].get(name)
    if entry is None:
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
    entry["lastReadWib"] = "2026-11-14 ~14:01 WIB"
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
        fc = entry.get("freeClaimed", entry.get("freeMinted"))
        fs = entry.get("FREE_SUPPLY", entry.get("FREE_MAX", entry.get("FREE_CAP")))
        if fc is not None and fs:
            entry["free_pct"] = round(100.0 * fc / fs, 1)
        note = (f"Run 1401 (blok {BLOCK}, interval ~{INTERVAL_MIN} mnt vs run 1331): "
                f"{prev_supply}->{sval} (d={d}, rate {cur_rate}/mnt, ratio {ratio}) -> "
                f"velocity {'LOLOS' if passes else 'GAGAL'}")
        if entry.get("free_pct") is not None:
            note += f"; free={fc}/{fs}={entry['free_pct']}%"
        if entry.get("mintOpen") is not None:
            note += f"; mintOpen={entry['mintOpen']}"
        if entry.get("balanceOf_user") is not None:
            note += f"; bal_user={entry['balanceOf_user']}"
        entry["runNote1401_1114"] = note
        if passes:
            velocity_pass.append(name)
        if d >= 15 or (ratio is not None and ratio >= 1.5):
            vel_lines.append(f"{name} {prev_supply}->{sval} (+{d}, {cur_rate}/mnt, ratio {ratio})"
                             + (" LOLOS" if passes else " GAGAL")
                             + (f"; free {entry['free_pct']}%" if entry.get("free_pct") is not None else "; free% UNVERIFIED"))
    else:
        entry["runNote1401_1114"] = (f"Run 1401 (blok {BLOCK}): baca "
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

# --- New Boltbook finds (triage run 1401) ---
snap.setdefault("contracts", {})
snap["contracts"]["Ledgera"] = {
    "address": "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
    "status": "watchlist-only-checked-not-lead-2026-11-14",
    "name": "Ledgera", "symbol": "LEDGERA", "kind": "ERC721",
    "totalSupply": 2329, "freeClaimed": 2322, "FREE_SUPPLY": 5000, "MAX_SUPPLY": 5555,
    "free_pct": 46.4, "mintOpen": 1, "freeUsed_user": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: post Boltbook (b/alpha, grandtheftauto6.ai, ~13:56 WIB) klaim 'live at block 133,499,554' + 2.324/5.555 (2.683 free left); TIDAK terkoroborasi on-chain — hanya 2 Transfer-from-zero dalam 2000 blok terakhir (blok pertama 133499791) vs totalSupply 2.329, jadi bulk minting mendahului jendela; getLogs ulang (133499500-head) GAGAL di semua endpoint (limit exceeded / rate limit). Tidak ada stated launch time lain.",
    "baselineNote": "Dicek on-chain run 1401: name/symbol Ledgera/LEDGERA, totalSupply 2329, freeClaimed 2322/5000 FREE_SUPPLY = 46,4% (<50% kandidat, <70% strong lead), mintOpen 1, slot user terbuka (mintedBy 0, freeUsed 0, balanceOf 0). AGENT_ID() mengembalikan alamat registry 0x60B926... (nilai numerik cocok) = referensi registry konkret; TAPI Sourcify UNVERIFIED (404) + registry bytes TIDAK ada di bytecode. First mint TIDAK terverifikasi run ini (bukan first-seen minting; supply sudah 2.329). Website UNVERIFIED. BUKAN early lead, BUKAN kandidat/strong lead. Watchlist-only.",
    "firstSeenWib": "2026-11-14 ~10:35 WIB (hot-leg-seen, source boltbook); dicek main job run 1401",
    "lastReadBlock": 133500810, "lastReadWib": "2026-11-14 ~14:01 WIB",
}
snap["contracts"]["MAMI"] = {
    "address": "0xfe36c6d7a1e352cd0822c6818269d190e8e63c13",
    "status": "watchlist-only-checked-not-lead-2026-11-14",
    "name": "Malware Mistletoe", "symbol": "MAMI", "kind": "ERC721",
    "totalSupply": 220, "MAX_SUPPLY": 885, "mintOpen": 1,
    "price": 50000000000000, "costOf_user_1": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x160c66813a8110b45399c595945f621a0aefc443",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: post Boltbook kalea.ai 14:05 WIB (receipt #189, blok 133.497.669, totalSupply 189/885 saat receipt); first mint TIDAK terverifikasi — hanya 14 Transfer dalam 133499300-head (blok pertama 133499307) vs totalSupply 220, bulk mendahului jendela; getLogs chunk lain rate-limited. Tidak ada stated launch time selain post.",
    "baselineNote": "Dicek on-chain run 1401: name/symbol Malware Mistletoe/MAMI, totalSupply 220 (189 saat receipt), MAX_SUPPLY 885, mintOpen 1, price() 0,00005 BNB (jalur berbayar) tapi costOf(user,1)=0, mintedBy(user)=0, balanceOf(user)=0. Sourcify UNVERIFIED (404), registry bytes TIDAK ada di bytecode, SEMUA free view revert (freeClaimed/freeMinted/FREE_SUPPLY/dll) -> free% UNVERIFIED. Owner 0x160c6681... sama dengan INKI, BUKAN owner discard yang dikenal. Website UNVERIFIED. BUKAN early lead (agent-shape tak terbentuk + first mint tak terverifikasi), BUKAN kandidat. Watchlist-only.",
    "firstSeenWib": "2026-11-14 ~14:05 WIB (Boltbook front page, post kalea.ai)",
    "lastReadBlock": 133500810, "lastReadWib": "2026-11-14 ~14:01 WIB",
}
snap["contracts"]["INKI"] = {
    "address": "0x5ae38f527340e1aaf4ea214f9778bdc2266e2bd7",
    "status": "watchlist-only-checked-not-lead-2026-11-14",
    "name": "Interlace Kirigami", "symbol": "INKI", "kind": "ERC721",
    "totalSupply": 212, "MAX_SUPPLY": 1743, "mintOpen": 1,
    "price": 50000000000000, "costOf_user_1": 0, "mintedBy_user": 0, "balanceOf_user": 0,
    "owner": "0x160c66813a8110b45399c595945f621a0aefc443",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Umur UNVERIFIED: post Boltbook kalea.ai 14:05 WIB (receipt #184, blok 133.499.503, totalSupply 184/1.743 saat receipt); first mint TIDAK terverifikasi — getLogs GAGAL di semua endpoint (limit exceeded / rate limit publicnode) untuk semua rentang yang dicoba. Tidak ada stated launch time selain post.",
    "baselineNote": "Dicek on-chain run 1401: name/symbol Interlace Kirigami/INKI, totalSupply 212 (184 saat receipt), MAX_SUPPLY 1743, mintOpen 1, price() 0,00005 BNB, costOf(user,1)=0, mintedBy(user)=0, balanceOf(user)=0. Sourcify UNVERIFIED (404), registry bytes TIDAK ada di bytecode, SEMUA free view revert -> free% UNVERIFIED. Owner 0x160c6681... sama dengan MAMI, BUKAN owner discard yang dikenal. Website UNVERIFIED. BUKAN early lead, BUKAN kandidat. Watchlist-only.",
    "firstSeenWib": "2026-11-14 ~14:05 WIB (Boltbook front page, post kalea.ai)",
    "lastReadBlock": 133500810, "lastReadWib": "2026-11-14 ~14:01 WIB",
}
snap["contracts"]["checked-CrossEyed-1401"] = {
    "address": "0x52903f070364ce6bb8d477c6751fa921079576b6",
    "status": "checked-not-lead-no-code-2026-11-14",
    "name": "CrossEyed", "kind": "unknown-no-code",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Post Boltbook zyrex.ai ~13:52 WIB klaim free mint #0302 (crosseyed.app, 3.333 plate, 777 jatah WL) — alamat di post TIDAK punya code on-chain.",
    "baselineNote": "Dicek on-chain run 1401: eth_getCode = 0x (TIDAK ADA KONTRAK di alamat ini); semua view null; Sourcify 404. Alamat di post salah atau kontrak belum deploy. TIDAK terverifikasi, BUKAN lead, tidak masuk watchlist aktif.",
    "firstSeenWib": "2026-11-14 ~13:59 WIB (hot-leg-seen, source boltbook)",
    "lastReadBlock": 133500810, "lastReadWib": "2026-11-14 ~14:01 WIB",
}
# PICK: shape correction (1031 verdict was based on AGENT_ID() null + no registry bytes;
# agentRegistry() was not read then). agentRegistry() now returns the registry address.
_pick = snap["contracts"].get("checked-Pickhash-1031", {})
_pick["totalSupply"] = 2273
_pick["totalMinted"] = 2273
_pick["mintOpen"] = 1
_pick["price"] = 1000000000000000
_pick["quote_user_1"] = 0
_pick["mintedBy_user"] = 0
_pick["balanceOf_user"] = 0
_pick["owner"] = "0xff4ec68049c8405152e107cf2163e80bc28837fd"
_pick["agentRegistry"] = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
_pick["status"] = "checked-agent-shaped-not-early-2026-11-14"
_pick["runNote1401_1114"] = (
    "Run 1401 KOREKSI bentuk (vs 1031 'not-agent-shaped'): agentRegistry() mengembalikan alamat registry "
    "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (nilai numerik 552192074493313695968015109214105588393044541999, cocok persis) "
    "= referensi registry konkret -> AGENT-SHAPED. TAPI tetap BUKAN early lead: first mint TIDAK terverifikasi run ini "
    "(supply sudah 2.273; pertama dilihat job 1031 sebagai checked), free% TETAP UNVERIFIED (semua free view revert), umur UNVERIFIED, "
    "website UNVERIFIED. Sourcify MASIH 404 via server/v2 API run ini (klaim post 'sekarang exact_match' TIDAK terkonfirmasi). "
    "quote(user,1)=0, totalSupply 2273/10000, mintOpen 1. Tetap checked, tidak dipromosikan, tidak dilaporkan ulang."
)
snap["contracts"]["checked-Pickhash-1031"] = _pick
# KOMA: fill empty entry — sweep hit, sale opened 2026-11-11 22:00 WIB, age >24h
snap["contracts"]["KOMA"] = {
    "address": "0xef4882e029b8d58F81960c433D852a5b0A352965",
    "status": "checked-age-excluded-2026-11-14",
    "name": "KOMA Agent", "kind": "ERC20-share-sale",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Sale dibuka 2026-11-11 22:00 WIB (komaagent.fun, tercantum di situs) -> umur >24 jam saat run 1401 (14 Nov ~14:01 WIB) -> AGE-EXCLUDED.",
    "baselineNote": "Ditemukan via sweep ZH run 1401 (komaagent.fun): 500 public-free + 300 WL-free + 10.000 paid @0,003 BNB/share. Tidak dicek on-chain lanjut karena umur sudah lewat 24 jam. Tidak masuk watchlist aktif.",
    "firstSeenWib": "2026-11-14 ~14:0x WIB (sweep run 1401)",
    "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~14:01 WIB",
}

# Track C: ORBIT update
snap.setdefault("track_c", {})
_orbit = snap["track_c"].get("ORBIT", {})
_orbit["freeClaimed"] = 235
_orbit["previousFreeClaimed"] = 228
_orbit["free_pct"] = 26.5
_orbit["claimOpen"] = 1
_orbit["hasFreeClaimed_user"] = 0
_orbit["lastReadBlock"] = BLOCK
_orbit["lastReadWib"] = "2026-11-14 ~14:01 WIB"
_orbit["runNote1401_1114"] = (
    "Run 1401 (blok 133500940): freeClaimed 228->235/888 (26,5%), claimOpen 1, hasFreeClaimed(user)=0. "
    "Umur TETAP UNVERIFIED (first-claim tak terverifikasi; Ankr 401, getLogs public/dataseed rate-limited). "
    "Tetap watchlist-only track_c, BUKAN lead, TIDAK preview/mint. DIAM."
)
snap["track_c"]["ORBIT"] = _orbit

# Track B: binanceai.fun pending claim re-check (refund phase unchanged)
_pc = snap.setdefault("pending_claims", {}).setdefault("binanceai.fun", {})
_pc["launched"] = 0
_pc["failed"] = 1
_pc["isRefundPhase"] = 1
_pc["totalShares"] = 3110
_pc["tokenClaimed_user"] = 0
_pc["lastReadWib"] = "2026-11-14 ~14:01 WIB"
_pc["runNote1401"] = (
    "Run 1401: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0 "
    f"(blok {BLOCK}) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM"
)

# Run notes
vel_txt = "; ".join(vel_lines) if vel_lines else "tidak ada pergerakan >=15"
snap["runNote1401_1114"] = (
    f"Run 1401: reread 33/33 OK blok {BLOCK} (164,3 dtk, interval ~{INTERVAL_MIN} mnt vs run 1331). "
    f"Velocity: {vel_txt}. "
    "WANGCAI 128/188=68,1% FLAT (<70%, bukan strong lead; slot terbuka, umur <24j terverifikasi, website NONE -> gate FAILS); "
    "YUANBAO 117/188=62,2% FLAT. RaceAgents 538->539 (+1) free 53,9% tapi velocity GAGAL -> bukan kandidat. "
    "DragonAgents 728->729 (+1) free 81,6% tapi age-excluded-2026-11-14 -> BUKAN strong lead. "
    "HIVE 1263 FLAT, minted-by-user. Zero totalSupply/freeClaimed gagal baca lagi (nilai lama dipertahankan); PX24 totalSupply gagal baca run ini. "
    "ORBIT freeClaimed 228->235/888 (26,5%), umur TETAP UNVERIFIED. "
    "Boltbook BARU: Ledgera + MAMI + INKI dicek -> ketiganya watchlist-only (lihat runNote boltbook); CrossEyed alamat tanpa code; "
    "PICK koreksi bentuk: agentRegistry()=registry address -> agent-shaped, tetap BUKAN early lead. "
    "Scan leg FAST-FAIL (Ankr 401 pre-flight 21,5 dtk, head 133500640), watermark tetap 132512564. "
    "Sourcify feed: 0 baru vs hot-leg-seen (20 kontrak, verifiedAt 06:21-06:53 UTC). "
    "Sweep EN+ZH: 0 baru (Oathbots/STAMP/Meow/RIGBYPASS/Gangster/Cosmos/AGENT MAO semua dikenal/lewat umur; KOMA age-excluded). "
    "Odaily 0 penyebutan Agent ID. Bridge tidak berubah (mtime 2026-11-08 18:21). binanceai tetap refund phase (launched 0, failed 1). "
    "0 eksekusi/preview. DIAM."
)
snap["runNote1401_1114_scan"] = (
    "Scan leg FAST-FAIL run 1401: pre-flight ankr_getLogs HTTP 401 Unauthorized dalam 21,5 dtk "
    "(helper scan.ankr_logs, head 133500640, blok 133500590-133500640). Scan TIDAK dijalankan; watermark tetap 132512564; "
    "track-C 5c dilewati (tanpa output scan). Outage Ankr 401 sejak 2026-11-09 berlanjut; perlu reconnect kredensial Ankr (di luar scope job ini)."
)
snap["runNote1401_1114_feedshape"] = (
    "Feed Sourcify run 1401 (limit 20, verifiedAt 06:21-06:53 UTC): 0 baru vs hot-leg-seen "
    "(20/20 sudah diproses hot-leg). Tidak ada kontrak baru untuk shape-check run ini."
)
snap["runNote1401_1114_boltbook"] = (
    "Boltbook EN+ZH run 1401 (fetch ~14:04 WIB, EN 45.274 byte, ZH 45.463 byte, 9 alamat, 7 proyek): "
    "Ledgera 0x8d29... (BARU, b/alpha grandtheftauto6.ai, klaim live blok 133.499.554, 2.324/5.555, 2.683 free left) -> dicek on-chain: "
    "totalSupply 2329, freeClaimed 2322/5000=46,4%, mintOpen 1, slot user terbuka; AGENT_ID()=registry address; TAPI Sourcify UNVERIFIED + "
    "registry bytes TIDAK di bytecode + first mint tak terverifikasi (2 Transfer-from-zero/2000 blok vs supply 2.329) + umur UNVERIFIED -> watchlist-only, BUKAN early lead. "
    "MAMI 0xfe36... + INKI 0x5ae3... (BARU, post kalea.ai 14:05 WIB, receipt #189/#184) -> dicek on-chain: MAMI totalSupply 220/885, INKI 212/1743, "
    "keduanya mintOpen 1, price 0,00005 BNB, costOf(user,1)=0, mintedBy 0; Sourcify UNVERIFIED + registry bytes TIDAK ada + semua free view revert -> free% UNVERIFIED; "
    "first mint tak terverifikasi (MAMI 14 Transfer/1500 blok vs supply 220; INKI getLogs gagal semua endpoint); owner sama 0x160c6681... (BUKAN discard) -> watchlist-only, BUKAN early lead. "
    "CrossEyed 0x5290... (BARU, zyrex.ai, crosseyed.app, 777 WL) -> eth_getCode=0x, TIDAK ADA KONTRAK -> checked-not-lead-no-code. "
    "PICK 0x2296... (post kalea.ai, freeMint FIRST_FREE, quote 0) -> agentRegistry()=registry address (koreksi 1031), Sourcify MASIH 404 (klaim exact_match tak terkonfirmasi), "
    "free% UNVERIFIED, first mint tak terverifikasi -> tetap checked, BUKAN early lead. "
    "AgentNOVA 468/6.666 (snapshot); 0x8269 checked-not-lead; ECHO/EchoLa track_c Feed-ERC20; BOLT footer; ARCADEWARDEN checked-1031. "
    "0 early lead baru dari Boltbook run ini."
)
snap["runNote1401_1114_sweep"] = (
    "Sweep EN+ZH run 1401: Oathbots (Binance Square 28 Okt, kontrak 0xb777c522..., 8.000 free) — post 17 hari, umur >24j, age-excluded, tidak ditambahkan; "
    "Agentic Gangster / STAMP PASS / Meow Cards / RIGBYPASS / AGENT COSMOS / AGENT MAO / First-Dollar Grove — semua sudah di snapshot / lewat umur; "
    "KOMA (komaagent.fun, 0xef4882e0...) — sale dibuka 2026-11-11 22:00 WIB -> age-excluded, dicatat di snapshot; "
    "Cosmic Sentinel sudah di snapshot (early-lead-reported-2026-11-10). 0 kandidat/lead baru dari sweep."
)
snap["last_run"] = "run 1401 2026-11-14"
snap["last_run_wib"] = "2026-11-14 ~14:01 WIB"
snap["last_run_note"] = snap["runNote1401_1114"]

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1, ensure_ascii=False)
print("MERGED. velocity_pass:", velocity_pass)
print("vel_lines:", vel_lines)
print("reads:", reread["reads_ok"], "/", reread["reads_total"], "block:", BLOCK)
print("notes-no-entry:", notes)
