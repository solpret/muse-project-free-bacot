#!/usr/bin/env python3
"""Merge run 0001 (scheduled 2026-11-12 00:01 WIB) into onchain-snapshot.json.
Inputs: reread.json (block 133007257), verify-new.json (block 133009171),
verify-lean.json (block 133010737), shape-feed-retry.json, feed.json,
feed-new.json, check-67b9-rig.json. Legs script was timeout-killed during
RigForge (legs.json absent) - legs facts taken from legs.log + curl fallback
feed + ZH retry2. Writes snapshot (with .bak) + updates hot-leg-seen.json.
No preview/mint."""
import json, shutil, datetime, os
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-12 00:01 WIB"
def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-12-0001-reread.json"))
verify = json.load(open(BASE + "run-2026-11-12-0001-verify-new.json"))["verify"]
lean = json.load(open(BASE + "run-2026-11-12-0001-verify-lean.json"))["verify"]
shape = json.load(open(BASE + "run-2026-11-12-0001-shape-feed-retry.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0001-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block", 133007257)

# --- 1. reread contracts: values + velocity ---
vel_pass, vel_fail, batch_fail = [], [], []
for name, d in reread.get("reread", {}).items():
    e = C.get(name)
    if not isinstance(e, dict):
        continue
    ts_new = d.get("totalSupply")
    fm_new = d.get("freeMinted")
    note_parts = []
    if ts_new is None and fm_new is None:
        batch_fail.append(name)
        e["runNote0001_1112"] = ("Run 0001 (blok %s): baca batch GAGAL (transport, degradasi RPC) - nilai lama dipertahankan, "
            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    prev_ts = e.get("totalSupply")
    prev_block = e.get("lastReadBlock") or 0
    interval = max(1.0, (BLOCK - prev_block) * 0.45 / 60.0) if prev_block else 30.0
    if ts_new is not None:
        e["totalSupply"] = ts_new
        if prev_ts is not None and ts_new >= prev_ts:
            minted = ts_new - prev_ts
            rate = minted / interval
            prev_rate = e.get("currentRatePerMin")
            ratio = (rate / prev_rate) if (prev_rate and prev_rate > 0) else None
            e["previousTotalSupply"] = prev_ts
            e["mintedInInterval"] = minted
            e["intervalMinutes"] = round(interval, 1)
            e["previousRatePerMin"] = prev_rate
            e["currentRatePerMin"] = round(rate, 4)
            e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
            passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
            e["velocityLegPasses"] = passes
            (vel_pass if passes else vel_fail).append((name, minted, round(rate, 3), e["velocityRatio"]))
            note_parts.append("velocity %s (+%d token, %.3f/mnt vs prev %.3f = %sx; butuh >=1.5x DAN >=20)" % (
                "LOLOS" if passes else "GAGAL", minted, rate, prev_rate or 0, ("%.2f" % ratio) if ratio is not None else "None"))
        else:
            e["velocityLegPasses"] = False
            note_parts.append("velocity tidak dihitung (totalSupply lama None/turun)")
    if fm_new is not None:
        e["freeMinted"] = fm_new
        note_parts.append("freeMinted=%s" % fm_new)
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    e["runNote0001_1112"] = "Run 0001 (blok %s): %s; bal_user=%s; status %s." % (
        BLOCK, "; ".join(note_parts) if note_parts else "tanpa perubahan", d.get("balanceOf_user"), e.get("status"))
print("velocity PASS:", vel_pass)
print("velocity FAIL n:", len(vel_fail), "batch_fail n:", len(batch_fail), batch_fail)

# --- 2. track_c reread values ---
tc_changes = []
for name, d in reread.get("track_c", {}).items():
    e = TC.get(name)
    if not isinstance(e, dict):
        continue
    ch = []
    for k in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if d.get(k) is not None and e.get(k) != d.get(k):
            ch.append("%s %s->%s" % (k, e.get(k), d.get(k)))
            e[k] = d.get(k)
    if ch:
        tc_changes.append((name, ch))
        e["runNote0001_1112"] = "Run 0001 (blok %s): %s; tanpa perubahan tier." % (BLOCK, "; ".join(ch))
print("track_c changes:", tc_changes)

# --- 3. verify-new fresh values ---
def setv(name, kv, note, store="contracts"):
    e = (C if store == "contracts" else TC).get(name)
    if not isinstance(e, dict):
        print("MISS", store, name); return
    for k, v in kv.items():
        if v is not None:
            e[k] = v
    e["runNote0001_1112"] = note
    e["lastReadBlock"] = verify.get("block", 133009171) if "block" in verify else e.get("lastReadBlock")
    e["lastReadWib"] = TS

v = verify
setv("MECHA", {"totalMinted": v["MECHA"].get("totalMinted"), "freeClaimed": v["MECHA"].get("freeClaimed"),
               "freePoolSize": v["MECHA"].get("freePoolSize")},
     "Run 0001 verify-new (blok 133009171): totalMinted/freeClaimed 786/4444 = 17,69%% (was 605). "
     "Masih jauh <50%%/70%%; freeAvailable(user)=2, bal 0. Tetap EARLY, tanpa promosi.")
setv("BUCKET", {"totalSupply": v["BUCKET"].get("totalSupply"), "totalFreeCount": v["BUCKET"].get("totalFreeCount"),
                "MAX_SUPPLY": v["BUCKET"].get("MAX_SUPPLY")},
     "Run 0001 verify-new: totalSupply/totalFreeCount 511 (was 451), MAX_SUPPLY 3333; mintOpenedAt 1794406606 = "
     "%s (umur TERVERIFIKASI <24 jam). free%%%% ~15,3%%%% bila cap=MAX; isAgent(user)=1, bal 0. Tetap EARLY, tanpa promosi." % wib(1794406606))
setv("MOONDRILL", {"totalSupply": v["MOONDRILL"].get("totalSupply"), "MAX_SUPPLY": v["MOONDRILL"].get("MAX_SUPPLY")},
     "Run 0001 verify-new: totalSupply 67 (was 64), MAX_SUPPLY 4444; mintStart 1794406225 = %s "
     "(umur TERVERIFIKASI <24 jam); paidMinted 0, firstFreeUsed 67. free%%%% ~1,5%%%% bila cap=MAX. Tetap EARLY, tanpa promosi." % wib(1794406225))
setv("0x2e50", {"totalSupply": v["0x2e50"].get("totalSupply"), "MAX_SUPPLY": v["0x2e50"].get("MAX_SUPPLY")},
     "Run 0001 verify-new: totalSupply 66 (was 65), MAX_SUPPLY 5555; mintStart 1794405623 = %s "
     "(umur TERVERIFIKASI <24 jam); paidMinted 0, firstFreeUsed 66. free%%%% ~1,2%%%% bila cap=MAX. Tetap EARLY, tanpa promosi." % wib(1794405623))
setv("CRTSAINTS", {"totalSupply": v["CRTSAINTS"].get("totalSupply"), "MAX_SUPPLY": v["CRTSAINTS"].get("MAX_SUPPLY")},
     "Run 0001 verify-new: totalSupply 56 (was 49), MAX_SUPPLY 3333; mintStart 1794405023 = %s "
     "(umur TERVERIFIKASI <24 jam); paidMinted 0, firstFreeUsed 56. free%%%% ~1,7%%%% bila cap=MAX. Tetap EARLY, tanpa promosi." % wib(1794405023))
setv("AGCR", {"totalSupply": v["AGCR"].get("totalSupply"), "totalMinted": v["AGCR"].get("totalMinted"),
              "freeMinted": v["AGCR"].get("freeMinted"), "FREE_SUPPLY": v["AGCR"].get("FREE_SUPPLY"),
              "MAX_SUPPLY": v["AGCR"].get("MAX_SUPPLY")},
     "Run 0001 verify-new: totalSupply 2397, totalMinted 2431, freeMinted 2377/2400 = 99,04%%%% (was 2373, +4), "
     "paidMinted 54, mintOpen 1, bal 0. Umur TETAP UNVERIFIED (tidak ada mintStart/saleStart terbaca). "
     "Tetap watchlist-only-age-unverified, BUKAN strong lead, TIDAK di-preview/di-mint.")
setv("WFPASS", {"totalSupply": v["WFPASS"].get("totalSupply"), "totalMinted": v["WFPASS"].get("totalMinted"),
                "freeMinted": v["WFPASS"].get("freeMinted"), "FREE_SUPPLY": v["WFPASS"].get("FREE_SUPPLY")},
     "Run 0001 verify-new: totalSupply/totalMinted/freeMinted 0, mintOpen 0, FREE_SUPPLY 500, MAX 1500; saleStart 1794438000 = "
     "%s, saleEnd 1794697200 = %s. BELUM LAUNCH (prelaunch). Tanpa aksi." % (wib(1794438000), wib(1794697200)))
setv("S1-6C50", {"totalMinted": v["S1-6C50"].get("totalMinted"), "freeMinted": v["S1-6C50"].get("freeMinted")},
     "Run 0001 verify-new: totalMinted/freeMinted 100/100 FREE_CAP - SELLOUT dipertahankan. TIDAK dilaporkan ulang.", store="track_c")
setv("S1-0895", {"totalMinted": 111, "freeMinted": 111, "MAX_SUPPLY": 3333},
     "Run 0001: verify-new batch GAGAL (degradasi RPC), lean retry BERHASIL: totalMinted/freeMinted 111 (was 100, +11), "
     "MAX_SUPPLY 3333, mintOpen 1, price 0,0014 BNB, freeClaimed(user)=0. Free CAP TETAP UNVERIFIED (FREE_SUPPLY revert), "
     "quote user + umur TETAP UNVERIFIED. Tetap track_c watchlist-only-pending-verification, BUKAN lead, TIDAK di-preview/di-mint.",
     store="track_c")
setv("BB-7c71", {},
     "Run 0001 verify-new: batch GAGAL (degradasi RPC, 75,1 dtk) - nilai lama dipertahankan, BUKAN nol. Tanpa promosi.", store="track_c")
# NAOMI checked entry
naomi = C.get("checked-0xC7Ad-2001", {})
naomi["totalMinted"] = 782; naomi["freeMinted"] = 777
naomi["runNote0001_1112"] = ("Run 0001 verify-new: totalMinted 782, freeMinted 777/777, paidMinted 5 - "
    "FREE POOL SOLD OUT dipertahankan (terverifikasi ulang).")

# --- 4. lean retry values: SEVEN / BALIFE / Stampooor / AgentPals ---
lv = lean
sev = C.get("SEVEN", {})
sev["totalSupply"] = lv["SEVEN"].get("totalSupply")
sev["totalMinted"] = lv["SEVEN"].get("totalMinted")
sev["freeMinted"] = lv["SEVEN"].get("freeMinted")
sev["FREE_CAP"] = lv["SEVEN"].get("FREE_CAP")
sev["MAX_SUPPLY"] = lv["SEVEN"].get("MAX_SUPPLY")
sev["mintOpen"] = lv["SEVEN"].get("mintOpen")
sev["balanceOf_user"] = lv["SEVEN"].get("balanceOf_user")
sev["lastReadBlock"] = lean.get("block", 133010737); sev["lastReadWib"] = TS
sev["runNote0001_1112"] = ("Run 0001 lean retry (blok 133010737): totalMinted/freeMinted 420/1111 = 37,8%%%% (was 77 run 2331, +343 dalam ~1 jam), "
    "MAX_SUPPLY 7777, mintOpen 1, mintOpensAt %s (umur TERVERIFIKASI <24 jam), bal 0. Lonjakan besar tapi masih <50%%%%/70%%%%; "
    "velocity belum terhitung (baca totalSupply pertama run ini). Tetap EARLY, tanpa promosi; X + website UNVERIFIED." % wib(1794415297))
bal = C.get("Binance Life Cards", {})
bal["totalMinted"] = v["Binance Life Cards"].get("totalMinted")
bal["freeMinted"] = v["Binance Life Cards"].get("freeMinted")
bal["MAX_SUPPLY"] = v["Binance Life Cards"].get("MAX_SUPPLY")
bal["balanceOf_user"] = v["Binance Life Cards"].get("balanceOf_user")
bal["lastReadBlock"] = verify.get("block", 133009171); bal["lastReadWib"] = TS
bal["runNote0001_1112"] = ("Run 0001 verify-new (blok 133009171): totalMinted/freeMinted 11 (was 5), freeRemaining inferensi ~1989/2000 = 0,55%%%%, "
    "MAX_SUPPLY 10000, mintStart %s (umur TERVERIFIKASI <24 jam), paidMinted 0, bal 0. Tetap EARLY, tanpa promosi; "
    "slot user + X + website UNVERIFIED." % wib(1794414145))
st = C.get("Stampooor Stamp Packs", {})
st["totalMinted"] = v["Stampooor"].get("totalMinted")
st["freeMinted"] = v["Stampooor"].get("freeMinted")
st["FREE_SUPPLY"] = v["Stampooor"].get("FREE_SUPPLY")
st["MAX_SUPPLY"] = v["Stampooor"].get("MAX_SUPPLY")
st["balanceOf_user"] = v["Stampooor"].get("balanceOf_user")
st["lastReadBlock"] = verify.get("block", 133009171); st["lastReadWib"] = TS
st["runNote0001_1112"] = ("Run 0001 verify-new (blok 133009171): totalMinted/freeMinted 879/1200 = 73,25%%%% (>70%%%%), mintOpen 1, "
    "mintStart %s (umur TERVERIFIKASI <24 jam, deadline ~09:00 WIB 12 Nov), slot TERBUKA (freeAvailable(user)=1, bal 0). "
    "Tetap STRONG LEAD GATE-BLOCKED (situs tidak load; gate-blocked-recheck menangani cek ulang). "
    "TIDAK di-preview, TIDAK di-mint, TIDAK dilaporkan ulang (tanpa perubahan tier)." % wib(1794362419))
ap = C.get("AgentPals", {})
ap["totalMinted"] = lv["AgentPals"].get("totalMinted")
ap["freeMinted"] = lv["AgentPals"].get("freeMinted")
ap["FREE_SUPPLY"] = lv["AgentPals"].get("FREE_SUPPLY")
ap["MAX_SUPPLY"] = lv["AgentPals"].get("MAX_SUPPLY")
ap["balanceOf_user"] = lv["AgentPals"].get("balanceOf_user")
ap["lastReadBlock"] = lean.get("block", 133010737); ap["lastReadWib"] = TS
ap["runNote0001_1112"] = ("Run 0001 lean retry (blok 133010737): totalMinted 301, freeMinted 300/300 = FREE POOL SOLD OUT "
    "TERKONFIRMASI ulang; bal_user=1 (sudah dimiliki user). Status minted-by-user-2026-11-11 dipertahankan; TIDAK dilaporkan ulang.")

# --- 5. NEW: 0x79b0 prelaunch (S1-shaped, agent_ref, but 0 mints, mintOpen 0) ---
C["0x79b0"] = {
    "address": "0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
    "name": None, "symbol": None, "kind": "ERC721",
    "status": "watchlist-only-prelaunch-2026-11-12",
    "totalSupply": 0, "totalMinted": None, "freeMinted": 0, "FREE_CAP": 200, "maxSupply": 888,
    "mintOpen": 0, "balanceOf_user": 0,
    "owner": "0x%040x" % lv["0x79b0"].get("owner") if lv["0x79b0"].get("owner") else None,
    "firstSeenBlock": 133010737, "firstSeenWib": "2026-11-12 00:01 WIB",
    "lastReadBlock": 133010737, "lastReadWib": TS,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "BELUM LAUNCH: totalSupply 0 + mintOpen 0 (lean retry run 0001, blok 133010737). S1-shape lolos (mint + price/quote + freeMinted + agent_ref via REGISTRY/agentGate di ABI). FREE_CAP 200, maxSupply 888.",
    "baselineNote": ("S1-shaped, agent-shaped (REGISTRY + agentGate + FREE_CAP + FREE_TOKENS + BONUS), TAPI BELUM LAUNCH (0 mint, mintOpen 0). "
        "BUKAN early lead (tidak ada first mint). Dilacak sebagai prelaunch; bila mintOpen=1 + first mints terverifikasi, evaluasi ulang sebagai early lead. "
        "Run berikut: tambahkan 0x79b0 ke verify-new TARGETS."),
    "runNote0001_1112": "Run 0001: S1 BARU dari feed Sourcify (shape-feed-retry), diverifikasi lean: BELUM LAUNCH. Masuk watchlist prelaunch, BUKAN early lead, TIDAK dilaporkan.",
}

# --- 6. hot-leg-seen: shape verdicts for 9 feed-new + 3 retries + 0x79b0/0xE1a4 ---
try:
    seen_j = json.load(open(BASE + "hot-leg-seen.json"))
    for s in shape.get("shapes", []):
        a = s.get("address")
        if not a:
            continue
        verdict = "sale-shape" if (s.get("S1") or s.get("S2")) else ("shape-unverified" if s.get("verified") is None else "checked-not-sale-shape")
        note = ("S1=%s S2=%s early=%s mint=%s quote=%s free=%s agent=%s token=%s nft=%s (shape-feed-retry 0001)" % (
            s.get("S1"), s.get("S2"), s.get("early_shape"), s.get("has_mint"), s.get("has_quote"),
            s.get("free_views"), s.get("agent_ref"), s.get("is_token"), s.get("is_nft")))
        if s.get("error"):
            note += " ERR: " + str(s.get("error"))[:100]
        if a in seen_j and isinstance(seen_j[a], dict):
            seen_j[a]["note"] = note; seen_j[a]["status"] = verdict
        else:
            seen_j[a] = {"first_seen_wib": "2026-11-12T00:01:00+07:00", "note": note,
                         "source": "sourcify-feed-0001-shape", "status": verdict}
    if "0x79b0CE8b39c3Ed230487172751612b4F631398Bc" in seen_j:
        seen_j["0x79b0CE8b39c3Ed230487172751612b4F631398Bc"]["status"] = "watchlist-only-prelaunch"
        seen_j["0x79b0CE8b39c3Ed230487172751612b4F631398Bc"]["note"] += " | run 0001 lean: totalSupply 0, mintOpen 0 = BELUM LAUNCH (FREE_CAP 200, maxSupply 888)."
    if "0xE1a4fFb104e5BF2b7aA5aD77969D43B56FCEE91A" in seen_j:
        seen_j["0xE1a4fFb104e5BF2b7aA5aD77969D43B56FCEE91A"]["status"] = "checked-not-agent-shaped"
        seen_j["0xE1a4fFb104e5BF2b7aA5aD77969D43B56FCEE91A"]["note"] += (" | run 0001 deep-check: totalSupply/freeMinted 111 (first mints ada) TAPI tanpa registry/AgentGate "
            "(agentIdRegistry/agentRegistry/registry revert), tanpa name/symbol, tanpa mintStart/saleStart, tanpa FREE_SUPPLY/FREE_CAP - "
            "bukti agent-shape TIDAK cukup -> BUKAN early lead, tidak dilaporkan.")
    json.dump(seen_j, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    print("seen updated, total", len(seen_j))
except Exception as e:
    print("SEEN update FAIL", e)

# --- 7. legs summary file (legs script was timeout-killed; reconstruct from logs) ---
legs_out = {
    "started_wib": TS,
    "feed": {"error": "URLError: urlopen timed out (legs urllib); recovered via curl",
             "n": 20, "newest_verifiedAt": "2026-11-11T17:27:26Z", "oldest_verifiedAt": "2026-11-11T16:48:18Z",
             "via": "curl run-2026-11-12-0001-feed.json"},
    "feed_new": json.load(open(BASE + "run-2026-11-12-0001-feed-new.json")),
    "feed_shape": {"s1_pass": shape.get("s1_pass", []), "s2_pass": shape.get("s2_pass", []),
                   "early_shape": shape.get("early_shape", []), "via": "shape-feed-retry (75s timeout, 3 workers)"},
    "boltbook_en": {"bytes": 44044, "n": 17, "via": "curl fallback (urllib IncompleteRead)"},
    "boltbook_zh": {"bytes": 45332, "n": 9, "via": "curl retry2 (legs urllib+curl FAIL)"},
    "boltbook_new": ["0x67b955d6155ac3957dfa61c3855590dcbf2b64f8"],
    "boltbook_new_note": "0x67b955d6 BUKAN kontrak: fragmen 40-hex pertama dari TX HASH di postingan Boltbook AGX402 waitlist (sudah dicatat hot-leg 00:09); eth_getCode len 0 = EOA/tx-hash, bukan lead.",
    "bridge": {"total": 116, "not_in_snapshot": [], "same_owner_discarded": 7, "note": "0 temuan pelengkap baru"},
    "binanceai": {"launched": False, "note": "launched()=false, tetap refund phase"},
    "rigforge": {"freeBooked_user": 10000000000000000000000, "openedAt": None, "freeSharesLeft": None,
                 "note": "openedAt/freeSharesLeft/freeClaimed GAGAL baca (degradasi RPC, 20s timeout); freeBooked(user) 10000 RIG utuh; pool belum terverifikasi buka (was openedAt 0 run 2331)"},
    "legs_timeout_note": "legs.py TERBUNUH timeout 400 dtk di fase RigForge (eth_call lambat); legs.json ini direkonstruksi dari legs.log + file curl + check-67b9-rig.json.",
}
json.dump(legs_out, open(BASE + "run-2026-11-12-0001-legs.json", "w"), indent=1)

# --- 8. top-level run note ---
snap["runNote0001_1112"] = (
    "Run 0001 (2026-11-12 00:01 WIB, eksekusi ~00:15-00:55 WIB): 0 kandidat baru, 0 strong lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 0 EARLY LEAD BARU. Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - "
    "scan leg fast-fail, watermark TIDAK dimajukan (tetap 132512564); 5c dilewati (tanpa output scan). Reread 62 kontrak (blok 133007257, 674,9 dtk) + "
    "23 track_c: velocity 0 LOLOS (terbesar SUDOSAINTS +6; semua <20 token; 28 batch-fail transport, nilai lama dipertahankan). "
    "Stampooor tetap strong-lead gate-blocked (freeMinted 879/1200 = 73,25%%, slot terbuka, umur <24 jam, deadline ~09:00 WIB 12 Nov). "
    "AgentPals free pool SOLD OUT terkonfirmasi ulang (300/300; sudah dimiliki user). SEVEN melonjak 77->420/1111 = 37,8%% (+343/jam) tapi tetap EARLY "
    "(<50%%/70%%; velocity belum terhitung). BALIFE 11/2000 = 0,55%%, tetap EARLY. AGCR 2377/2400 = 99,04%% tapi umur TETAP UNVERIFIED -> watchlist-only. "
    "MECHA 786/4444 = 17,69%%, BUCKET 511, MOONDRILL 67, 0x2e50 66, CRTSAINTS 56 - semua tetap EARLY. NAOMI sold out terkonfirmasi ulang (777/777). "
    "S1-0895 111 (was 100), free cap/quote/umur TETAP UNVERIFIED - tetap pending-verification. WFPASS BELUM LAUNCH (saleStart 06:00 WIB 12 Nov). "
    "Sourcify feed 20 kontrak (verified 16:48-17:27 UTC; urllib timeout, diambil via curl), shape-check retry: S1 = 0x79b0 (NFT, agent-shaped, TAPI BELUM "
    "LAUNCH: totalSupply 0, mintOpen 0, FREE_CAP 200 - masuk watchlist prelaunch, BUKAN early lead); early-shape 0xE1a4 (111 first mints TAPI tanpa "
    "registry/AgentGate/nama/launch-time/free-cap - bukti agent-shape tidak cukup, BUKAN early lead, tidak dilaporkan); 3 alamat retry 2331 "
    "(0xC7E70B80, 0xebB62dFA, 0x107778f6) terkonfirmasi bukan agent-shaped. Boltbook EN OK (44.044 byte, 17 alamat), ZH retry2 OK (45.332 byte, 9 alamat), "
    "0 baru - 'baru' 0x67b955d6 adalah fragmen tx-hash postingan AGX402 waitlist (bukan kontrak). Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). "
    "Binanceai launched()=false (tetap refund phase). RigForge: freeBooked(user) 10000 RIG utuh; openedAt/freeSharesLeft gagal baca (degradasi RPC). "
    "Sweep EN+ZH: 0 proyek baru (Oathbots dikenal, Agentic Gangster pool habis, Horus Phase-1 sold out, AgentForge lama, TINY AGENTS/Burn Agent/Agentite/NOVRA excluded). "
    "Route 6: Odaily + PANews 0 item Agent ID/free-mint. Degradasi egress berat run ini: legs timeout-kill 400 dtk, verify-early2 mati kena restart service, "
    "banyak batch 75 dtk/timeout - semua nilai gagal baca dicatat sebagai gagal baca, BUKAN nol. Age-exclusion: tidak ada item baru (Stampooor deadline ~09:00 WIB). "
    "DIAM sesuai aturan (tidak ada yang baru memenuhi tier).")
snap["last_run"] = "2026-11-12 00:01 WIB"
snap["last_run_wib"] = "2026-11-12 00:01 WIB"
tmp = BASE + "onchain-snapshot.json.tmp"
with open(tmp, "w") as f: json.dump(snap, f, indent=1)
os.replace(tmp, BASE + "onchain-snapshot.json")
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
