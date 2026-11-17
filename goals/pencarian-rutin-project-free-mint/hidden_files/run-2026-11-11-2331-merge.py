#!/usr/bin/env python3
"""Merge run 2331 (scheduled 2026-11-11 23:31 WIB) into onchain-snapshot.json.
Inputs: reread.json (62+23, block 133001424), verify-new.json (block 133002517),
verify-naomi.json, verify-s1new.json, verify-ff65b.json, shape-feed.json,
legs.json, feed.json. Writes snapshot (with .bak) + updates hot-leg-seen.json
for the 20 feed addresses. No preview/mint."""
import json, shutil, datetime
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11 23:31 WIB"
def wib(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-2331-reread.json"))
verify = json.load(open(BASE + "run-2026-11-11-2331-verify-new.json"))["verify"]
shape = json.load(open(BASE + "run-2026-11-11-2331-shape-feed.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-2331-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread.get("block", 133001424)

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
        e["runNote2331_1111"] = ("Run 2331 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
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
    e["runNote2331_1111"] = "Run 2331 (blok %s): %s; bal_user=%s; status %s." % (
        BLOCK, "; ".join(note_parts) if note_parts else "tanpa perubahan", d.get("balanceOf_user"), e.get("status"))
print("velocity PASS:", vel_pass)
print("velocity FAIL n:", len(vel_fail), "batch_fail n:", len(batch_fail), batch_fail)

# --- 1b. Stampooor / AgentPals freeMinted-only updates ---
st = C.get("Stampooor Stamp Packs", {})
st["freeMinted"] = 873
st["lastReadBlock"] = BLOCK; st["lastReadWib"] = TS
st["runNote2331_1111"] = ("Run 2331 (blok %s): totalSupply GAGAL baca (nilai lama 868 dipertahankan, BUKAN 0); "
    "freeMinted 873/1200 = 72,75%% (>70%%), slot TERBUKA (bal 0), umur TERVERIFIKASI <24 jam (mintStart 09:00:19 WIB). "
    "Tetap STRONG LEAD GATE-BLOCKED (situs tidak load; gate-blocked-recheck menangani cek ulang). "
    "TIDAK di-preview, TIDAK di-mint, TIDAK dilaporkan ulang (tanpa perubahan tier)." % BLOCK)
ap = C.get("AgentPals", {})
ap["freeMinted"] = 300
ap["lastReadBlock"] = BLOCK; ap["lastReadWib"] = TS
ap["runNote2331_1111"] = ("Run 2331 (blok %s): totalSupply GAGAL baca; freeMinted 300/300 = FREE POOL SOLD OUT "
    "(totalMinted sebelumnya 301). Status tetap minted-by-user-2026-11-11 (sudah dimiliki user); "
    "sold out pool gratis dicatat, TIDAK dilaporkan ulang sebagai perubahan lead." % BLOCK)

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
        e["runNote2331_1111"] = "Run 2331 (blok %s): %s; tanpa perubahan tier." % (BLOCK, "; ".join(ch))
print("track_c changes:", tc_changes)

# --- 3. verify-new fresh values ---
def setv(name, kv, note, store="contracts"):
    e = (C if store == "contracts" else TC).get(name)
    if not isinstance(e, dict):
        print("MISS", store, name); return
    for k, v in kv.items():
        if v is not None:
            e[k] = v
    e["runNote2331_1111"] = note
    e["lastReadBlock"] = verify.get("block", 133002517) if "block" in verify else e.get("lastReadBlock")
    e["lastReadWib"] = TS

v = verify
setv("MECHA", {"totalMinted": v["MECHA"].get("totalMinted"), "freeClaimed": v["MECHA"].get("freeClaimed"),
               "freePoolSize": v["MECHA"].get("freePoolSize")},
     "Run 2331 verify-new (blok 133002517): totalMinted/freeClaimed 605/4444 = 13,62%% (was 403). "
     "Lonjakan +202 sejak hot-leg 2244 tapi free%% jauh di bawah 50%%/70%%; freeAvailable(user)=2, bal 0. "
     "Tetap EARLY, tanpa promosi.")
setv("BUCKET", {"totalSupply": v["BUCKET"].get("totalSupply"), "totalFreeCount": v["BUCKET"].get("totalFreeCount"),
                "MAX_SUPPLY": v["BUCKET"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalSupply/totalFreeCount 451 (was 405), MAX_SUPPLY 3333; mintOpenedAt 1794406606 = "
     "%s (umur TERVERIFIKASI <24 jam). free%%%% ~13,5%%%% bila cap=MAX; isAgent(user)=1, bal 0. Tetap EARLY, tanpa promosi." % wib(1794406606))
setv("MOONDRILL", {"totalSupply": v["MOONDRILL"].get("totalSupply"), "MAX_SUPPLY": v["MOONDRILL"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalSupply 64 (was 53), MAX_SUPPLY 4444; mintStart 1794406225 = %s "
     "(umur TERVERIFIKASI <24 jam); paidMinted 0, firstFreeUsed 64. free%%%% ~1,4%%%% bila cap=MAX. Tetap EARLY, tanpa promosi." % wib(1794406225))
setv("0x2e50", {"totalSupply": v["0x2e50"].get("totalSupply"), "MAX_SUPPLY": v["0x2e50"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalSupply 65 (was 53), MAX_SUPPLY 5555; mintStart 1794405623 = %s "
     "(umur TERVERIFIKASI <24 jam); paidMinted 0, firstFreeUsed 65. free%%%% ~1,2%%%% bila cap=MAX. Tetap EARLY, tanpa promosi." % wib(1794405623))
setv("AGCR", {"totalSupply": v["AGCR"].get("totalSupply"), "totalMinted": v["AGCR"].get("totalMinted"),
              "freeMinted": v["AGCR"].get("freeMinted"), "FREE_SUPPLY": v["AGCR"].get("FREE_SUPPLY"),
              "MAX_SUPPLY": v["AGCR"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalSupply 2393, totalMinted 2427, freeMinted 2373/2400 = 98,88%%%% (tidak berubah vs 2244), "
     "paidMinted 54, mintOpen 1, bal 0. Umur TETAP UNVERIFIED (tidak ada mintStart/saleStart terbaca). "
     "Tetap watchlist-only-age-unverified, BUKAN strong lead, TIDAK di-preview/di-mint.")
setv("WFPASS", {"totalSupply": v["WFPASS"].get("totalSupply"), "totalMinted": v["WFPASS"].get("totalMinted"),
                "freeMinted": v["WFPASS"].get("freeMinted"), "FREE_SUPPLY": v["WFPASS"].get("FREE_SUPPLY")},
     "Run 2331 verify-new: totalSupply/totalMinted/freeMinted 0, mintOpen 0, FREE_SUPPLY 500, MAX 1500; saleStart 1794438000 = "
     "%s, saleEnd 1794697200 = %s. BELUM LAUNCH (prelaunch). Tanpa aksi." % (wib(1794438000), wib(1794697200)))
setv("S1-6C50", {"totalMinted": v["S1-6C50"].get("totalMinted"), "freeMinted": v["S1-6C50"].get("freeMinted")},
     "Run 2331 verify-new: totalMinted/freeMinted 100/100 FREE_CAP - SELLOUT TERKONFIRMASI (sudah dilaporkan hot-leg 2244). "
     "Status sold-out dipertahankan, TIDAK dilaporkan ulang.", store="track_c")
setv("S1-0895", {"totalMinted": v["S1-0895"].get("totalMinted"), "freeMinted": v["S1-0895"].get("freeMinted"),
                 "MAX_SUPPLY": v["S1-0895"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalMinted/freeMinted 100 (was 59 ~23:44 WIB, +41 dalam ~10 mnt - cepat), MAX_SUPPLY 3333, "
     "mintOpen 1, freeClaimed(user)=0, price 0,0014 BNB, agentIdRegistry set. Free CAP TETAP UNVERIFIED (FREE_SUPPLY revert), "
     "quote user + umur TETAP UNVERIFIED. Tetap track_c watchlist-only-pending-verification, BUKAN lead, TIDAK di-preview/di-mint.",
     store="track_c")
setv("BB-7c71", {"totalSupply": v["BB-7c71"].get("totalSupply"), "freeMinted": v["BB-7c71"].get("freeMinted"),
                 "MAX_SUPPLY": v["BB-7c71"].get("MAX_SUPPLY")},
     "Run 2331 verify-new: totalSupply/freeMinted 496, MAX_SUPPLY 7777 (~6,4%%%% bila cap=MAX). Tanpa promosi.", store="track_c")
# NAOMI checked entry
naomi = C.get("checked-0xC7Ad-2001", {})
naomi["totalMinted"] = 782; naomi["freeMinted"] = 777
naomi["runNote2331_1111"] = ("Run 2331 verify-new + targeted check: totalMinted 782, freeMinted 777/777, paidMinted 5 - "
    "FREE POOL SOLD OUT TERKONFIRMASI on-chain (2x baca independen). Klaim Colony '338 dari 777 slot tersisa' SALAH/basi. "
    "Status checked-free-pool-sold-out dipertahankan.")

# --- 4. NEW early leads: SEVEN + Binance Life Cards ---
C["SEVEN"] = {
    "address": "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
    "name": "SEVEN", "symbol": "SEVEN", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-11",
    "totalMinted": 77, "freeMinted": 77, "FREE_CAP": 1111, "MAX_SUPPLY": 7777,
    "freePctVerified": 6.93, "mintOpen": 1, "price": 1400000000000000,
    "FREE_PER_WALLET": 3, "MAX_PER_WALLET": 10,
    "mintOpensAt": 1794415297, "mintOpensAtWib": wib(1794415297),
    "freeCountBy_user": 0, "mintsBy_user": 0, "holdsAgentId_user": 1, "balanceOf_user": 0,
    "owner": "0x7f13f050e6fb278d01537b12379b01e8dbadf5f2",
    "firstSeenBlock": 133002517, "firstSeenWib": "2026-11-11 23:31 WIB",
    "lastReadBlock": 133002517, "lastReadWib": TS,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch TERVERIFIKASI <24 jam via kontrak mintOpensAt() = 2026-11-11 23:41:37 WIB; Sourcify verifiedAt 2026-11-11T16:36:18Z; first-seen job ini run 2331 (feed Sourcify + shape-check S1).",
    "baselineNote": ("EARLY lead dilaporkan sekali run 2331: agent-shaped (agentIdRegistry + holdsAgentId + FREE_CAP + freeMinted), "
        "first mints terverifikasi on-chain (77 total, semua free). Kaki: umur TERVERIFIKASI <24 jam; free 77/1111 = 6,93%% "
        "(jauh <50%%/70%%); slot user TERBUKA (freeCountBy 0, holdsAgentId 1); X UNVERIFIED; website UNVERIFIED; velocity UNVERIFIED "
        "(baca pertama). Owner 0x7f13... TIDAK ada di same-owner-discards. TIDAK PERNAH auto-mint/preview; promosi hanya bila 3 kaki strong lead terpenuhi."),
    "runNote2331_1111": "Run 2331: EARLY LEAD BARU (lihat baselineNote).",
}
C["Binance Life Cards"] = {
    "address": "0x4367b86F889014e6fD57fE812B86A581b913C645",
    "name": "Binance Life Cards", "symbol": "BALIFE", "kind": "ERC721",
    "status": "early-lead-reported-2026-11-11",
    "totalMinted": 5, "freeMinted": 5, "freeRemaining": 1995, "FREE_POOL": 2000,
    "FREE_POOL_note": "Inferensi: freeRemaining 1995 + freeMinted 5 = 2000",
    "MAX_SUPPLY": 10000, "mintStart": 1794414145, "mintStartWib": wib(1794414145),
    "paidMinted": 0, "balanceOf_user": 0,
    "owner": "0xb07b263ffb129575142537fa307f24e6a435f78a",
    "firstSeenBlock": 133002517, "firstSeenWib": "2026-11-11 23:31 WIB",
    "lastReadBlock": 133002517, "lastReadWib": TS,
    "xVerified": False, "velocityVerified": False,
    "launchNote": "Launch TERVERIFIKASI <24 jam via kontrak mintStart() = 2026-11-11 23:22:25 WIB; Sourcify verifiedAt 2026-11-11T16:23:12Z; first-seen job ini run 2331 (feed Sourcify + shape-check S1). Registry 0x60B926...22F terkonfirmasi di source BinanceLifeCards.sol; gate() ada.",
    "baselineNote": ("EARLY lead dilaporkan sekali run 2331: agent-shaped (registry di source + gate() + freeMinted/freeRemaining), "
        "first mints terverifikasi on-chain (5 total, semua free). Kaki: umur TERVERIFIKASI <24 jam; free 5/2000 = 0,25%% "
        "(FREE_POOL inferensi 1995+5); slot user UNVERIFIED (quote butuh agentId, belum dibaca); X UNVERIFIED; website UNVERIFIED; "
        "velocity UNVERIFIED (baca pertama). Owner 0xb07b... TIDAK ada di same-owner-discards. TIDAK PERNAH auto-mint/preview; "
        "promosi hanya bila 3 kaki strong lead terpenuhi."),
    "runNote2331_1111": "Run 2331: EARLY LEAD BARU (lihat baselineNote).",
}
# S1-0895: keep pending-verification note (already set above via setv)
# --- 5. hot-leg-seen: record the 20 feed addresses with shape verdicts ---
try:
    seen_j = json.load(open(BASE + "hot-leg-seen.json"))
    for s in shape.get("shapes", []):
        a = s.get("address")
        if not a:
            continue
        verdict = "sale-shape" if (s.get("S1") or s.get("S2")) else ("shape-unverified" if s.get("verified") is None else "checked-not-sale-shape")
        note = ("S1=%s S2=%s early=%s mint=%s quote=%s free=%s agent=%s token=%s nft=%s (shape-feed 2331)" % (
            s.get("S1"), s.get("S2"), s.get("early_shape"), s.get("has_mint"), s.get("has_quote"),
            s.get("free_views"), s.get("agent_ref"), s.get("is_token"), s.get("is_nft")))
        if s.get("error"):
            note += " ERR: " + str(s.get("error"))[:100]
        if a in seen_j and isinstance(seen_j[a], dict):
            seen_j[a]["note"] = note; seen_j[a]["status"] = verdict
        else:
            seen_j[a] = {"first_seen_wib": "2026-11-11T23:31:00+07:00", "note": note,
                         "source": "sourcify-feed-2331-shape", "status": verdict}
    # mark the two early leads in seen as well
    for a, stt in (("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96", "early-lead-reported"),
                   ("0x4367b86F889014e6fD57fE812B86A581b913C645", "early-lead-reported")):
        if a in seen_j and isinstance(seen_j[a], dict):
            seen_j[a]["status"] = stt
    json.dump(seen_j, open(BASE + "hot-leg-seen.json", "w"), indent=1)
    print("seen updated, total", len(seen_j))
except Exception as e:
    print("SEEN update FAIL", e)

# --- 6. top-level run note ---
snap["runNote2331_1111"] = (
    "Run 2331 (2026-11-11 23:31 WIB, eksekusi 23:33-00:25 WIB): 0 kandidat baru, 0 strong lead baru, "
    "0 track-B dibuka, 0 track-C lead/kandidat baru, 2 EARLY LEAD BARU (SEVEN 0xFf65..., Binance Life Cards 0x4367... - "
    "dilaporkan sekali run ini). Pre-flight FAIL (Ankr HTTP 401, outage sejak 9 Nov) - scan leg fast-fail, watermark TIDAK "
    "dimajukan (tetap 132512564); 5c dilewati (tanpa output scan). Reread 62 kontrak (blok 133001424) + 23 track_c: velocity 0 LOLOS "
    "(terbesar Twill Fullery +13, STALL +10, SUDOSAINTS +7; semua <20 token). Stampooor tetap strong-lead gate-blocked "
    "(freeMinted 873/1200 = 72,75%%). AgentPals free pool SOLD OUT (freeMinted 300/300; sudah dimiliki user). "
    "Sourcify feed 20 kontrak (verified 16:11-16:41 UTC), shape-check: S1 = SEVEN + BALIFE (keduanya NFT, jadi EARLY track-A, "
    "bukan lead track-C); 3 alamat gagal fetch ABI (0xC7E70B80, 0xebB62dFA, 0x107778f6 - shape UNVERIFIED, retry run berikut). "
    "S1-0895 tetap pending-verification (totalMinted 100, +41/10 mnt, tapi free cap/quote/umur UNVERIFIED). "
    "Boltbook EN GAGAL, ZH OK (43.471 byte, 12 alamat, 0 baru - 1 'baru' 0xc2f677be adalah EOA di postingan Pokechain, bukan kontrak). "
    "Bridge: 0 temuan pelengkap baru (116 kontrak, 7 discarded). Binanceai launched()=false (tetap refund phase). "
    "RigForge: openedAt 0, freeSharesLeft 681, freeBooked(user) 10000 RIG utuh. AGCR tetap age-unverified (98,88%% free). "
    "NAOMI free pool sold out TERKONFIRMASI (777/777; klaim Colony '338 tersisa' salah). Sweep: semua hasil sudah dikenal/excluded "
    "(Agentic Gangster pool habis, Horus Phase-1 free sold out, RIGBYPASS excluded, WNO sudah di-mint user, NOVRA pool habis, "
    "Burn Agent excluded, TINY AGENTS excluded, First-Dollar Grove age-excluded, Agentite age-excluded). "
    "Route 6: Odaily/PANews tidak dicek run ini (legs kehabisan waktu di RigForge; dicatat, bukan 0 item). "
    "Age-exclusion: tidak ada item baru yang memenuhi syarat penghapusan run ini (item berumur terverifikasi >24 jam yang belum "
    "di-exclude: tidak ada; minted-by-user dipertahankan sesuai praktik).")
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT WRITTEN, contracts:", len(C), "track_c:", len(TC))
