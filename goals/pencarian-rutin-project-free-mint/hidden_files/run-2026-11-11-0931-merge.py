#!/usr/bin/env python3
"""Merge run 0931 results into onchain-snapshot.json. Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0931-reread.json"))
probe_nf = json.load(open(BASE + "run-2026-11-11-0931-probe-nf-lowb.json"))
probe_slot = json.load(open(BASE + "run-2026-11-11-0931-probe-slot-7eb9.json"))
probe_ddc2 = json.load(open(BASE + "run-2026-11-11-0931-probe-ddc2.json"))
binanceai = json.load(open(BASE + "run-2026-11-11-0931-binanceai.json"))
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0931-premerge")
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
BLOCK = reread["block"]
TS = "2026-11-11 09:31 WIB"

def vel(name, new_supply, interval=30.0):
    e = C.get(name)
    if not isinstance(e, dict):
        return None
    old = e.get("totalSupply")
    if old is None or new_supply is None:
        return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / interval, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = interval
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = None
    if prev_rate and prev_rate > 0:
        ratio = round(rate / prev_rate, 2)
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    return diff, rate, ratio

# --- 1. reread updates (skip Stampooor + 0x7Eb9: probe-freshest values below) ---
SKIP = {"Stampooor Stamp Packs", "0x7Eb9"}
for name, d in reread["reread"].items():
    if name in SKIP or name not in C:
        continue
    e = C[name]
    if d.get("_batch_fail"):
        e["runNote0931"] = ("Run 0931 (blok %s): baca batch GAGAL (transport) - nilai lama dipertahankan, "
                            "BUKAN nol; velocity TIDAK dihitung run ini; status %s." % (BLOCK, e.get("status")))
        continue
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        old = e.get("totalSupply")
        if old is None:
            e["totalSupply"] = ns
            e["lastReadBlock"] = BLOCK
            e["lastReadWib"] = TS
            e["runNote0931"] = ("Run 0931 (blok %s): totalSupply pertama terbaca %s (sebelumnya None) - "
                                "baseline dicatat, velocity belum lulus; freeMinted=%s; bal_user=%s; status %s."
                                % (BLOCK, ns, d.get("freeMinted"), d.get("balanceOf_user"), e.get("status")))
        else:
            r = vel(name, ns)
            diff, rate, ratio = r if r else (None, None, None)
            e["runNote0931"] = ("Run 0931 (blok %s): totalSupply %s->%s (+%s, %s/mnt vs prev %s = %sx) -> velocity %s; "
                                "bal_user=%s; freeMinted=%s; status %s."
                                % (BLOCK, e.get("previousTotalSupply"), ns, diff, rate,
                                   e.get("previousRatePerMin"), ratio,
                                   "LOLOS" if e.get("velocityLegPasses") else "GAGAL",
                                   d.get("balanceOf_user"), d.get("freeMinted"), e.get("status")))
    if d.get("freeClaimed") is not None:
        e["freeClaimed"] = d["freeClaimed"]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("FREE_SUPPLY") is not None:
        e["FREE_SUPPLY"] = d["FREE_SUPPLY"]
    if d.get("MAX_SUPPLY") is not None:
        e["MAX_SUPPLY"] = d["MAX_SUPPLY"]
    if d.get("balanceOf_user") is not None:
        e["balanceOf_user"] = d["balanceOf_user"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS

# --- 2. NIGHTFORGE: tetap watchlist-only (<70% baru) ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    p = probe_nf.get("NIGHTFORGE", {})
    nf.update({"totalSupply": p.get("totalSupply", 737), "agentFreeUsed": p.get("agentFreeUsed"),
               "paidMinted": p.get("paidMinted"), "mintStart": p.get("mintStart"),
               "mintEnd": p.get("mintEnd"), "freePctVerified": 36.7,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": probe_nf.get("block", BLOCK), "lastReadWib": TS})
    nf["runNote0931"] = ("Run 0931: agentFreeUsed 734/2000 = 36,7%% (totalSupply 737, paidMinted 3), slot terbuka "
        "(agentFreeByWallet 0, balanceOf 0, mintOpen 1). Tetap watchlist-only di bawah ambang strong lead >70%% "
        "(user 11 Nov 09:18 WIB). Deadline umur 14:37 WIB 11 Nov belum lewat. Bukan kandidat (velocity GAGAL +5 token). "
        "TIDAK di-preview/di-mint.")

# --- 3. Stampooor: freshest probe 437 (reread 373 di tengah run) ---
st = C.get("Stampooor Stamp Packs")
slot = probe_slot.get("Stampooor_slot", {})
if isinstance(st, dict):
    fm = slot.get("freeMinted") or 437
    r = vel("Stampooor Stamp Packs", fm)
    diff, rate, ratio = r if r else (None, None, None)
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": fm, "freeMinted": fm, "totalSupply": fm,
               "mintStart": 1794362419, "mintOpen": 1,
               "freeAvailable_user": slot.get("freeAvailable_user"),
               "freeUsed_user": slot.get("freeUsed_user"),
               "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": TS})
    st["runNote0931"] = ("Run 0931: freeMinted 283->373 (re-read blok %s) -> 437 (probe blok %s). "
        "Interval 283->437 = +%s (%.2f/mnt vs prev 9,4333 = %sx) -> velocity GAGAL. Free 437/1200 = 36,42%% "
        "(<70%% strong lead, <50%% kandidat). Slot user TERBUKA (balanceOf 0, freeAvailable(user)=1; "
        "freeUsed(user)=None transport, bukan bukti terpakai). Umur TERVERIFIKASI <24 jam (mintStart 11 Nov ~09:00 WIB). "
        "X + website UNVERIFIED. Tetap EARLY. TIDAK di-preview/di-mint."
        % (BLOCK, probe_slot.get("block", BLOCK), diff, rate, ratio))

# --- 4. Jade Vault 0x7Eb9: freshest probe 320 ---
jv = C.get("0x7Eb9")
q7 = probe_slot.get("0x7Eb9", {})
if isinstance(jv, dict):
    tm = q7.get("totalMinted") or 320
    r = vel("0x7Eb9", tm)
    diff, rate, ratio = r if r else (None, None, None)
    jv.update({"totalMinted": tm, "totalSupply": tm,
               "mintedBy_user": q7.get("mintedBy_user"), "quote_1": q7.get("quote_1"),
               "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": TS})
    jv["runNote0931"] = ("Run 0931: totalMinted 256->288 (re-read) -> 320 (probe blok %s). Interval 256->320 = +%s "
        "(%.2f/mnt, prev rate None = baseline) -> velocity GAGAL. quote(user,1)=0 (GRATIS), mintedBy(user)=0 "
        "(slot terbuka). Free%% tetap UNVERIFIED (template tanpa free counter - %% total supply 320/8888 TIDAK "
        "disubstitusi). Umur + website + X UNVERIFIED. Tetap EARLY. TIDAK di-preview/di-mint."
        % (probe_slot.get("block", BLOCK), diff, rate))

# --- 5. LOWB track_c: masih belum dibuka ---
lb = probe_nf.get("LOWB", {})
if isinstance(TC.get("LOWB"), dict) and lb:
    e = TC["LOWB"]
    e.update({"opened": lb.get("opened"), "totalFreeMinted": lb.get("totalFreeMinted"),
              "totalMinted": lb.get("totalMinted"), "totalPaidMinted": lb.get("totalPaidMinted"),
              "FREE_SHARES": lb.get("FREE_SHARES"), "MAX_SHARES": lb.get("MAX_SHARES"),
              "MINT_DEADLINE": lb.get("MINT_DEADLINE"),
              "lastReadBlock": probe_nf.get("block", BLOCK), "lastReadWib": TS})
    e["runNote0931"] = ("Run 0931: opened MASIH 0 (sale belum dibuka; MINT_DEADLINE 2026-11-14 19:00 WIB). "
        "Free lane maju: totalFreeMinted 783->802/1000, totalMinted 814, totalPaidMinted 12. "
        "Tetap watchlist-only-not-open (lead track-C butuh sale opening).")

# --- 6. track_c updates from reread (non-None only) ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict):
        continue
    e = TC[name]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = TS
    if name == "11-11":
        e["runNote0931"] = "Run 0931: freeMinted 604->608 (minting berjalan pelan); tetap watchlist-only-age-website-unverified."

# --- 7. SHINE: track-C S1, BELUM launching -> watchlist-only-upcoming (baru, dilaporkan sekali sbg upcoming) ---
dd = probe_ddc2.get("DDc2", {})
TC["SHINE"] = {
    "sale": "0xDDc2352d1ceC10b42e05A297232f5328902C6c2C",
    "address": "0xDDc2352d1ceC10b42e05A297232f5328902C6c2C",
    "token": "0xDDc2352d1ceC10b42e05A297232f5328902C6c2C",
    "name": "SHINE", "symbol": "SHINE", "kind": "track-c-sale-S1",
    "status": "watchlist-only-upcoming-2026-11-11",
    "FREE_SHARES": 500, "PAID_SHARES": 14500, "TOTAL_SHARES": 15000,
    "TOKENS_PER_SHARE": 9081713688562350336667,
    "freeClaimed": 0, "freeClaimedBy_user": False, "mintCost_1": 0,
    "remainingShares": 15000, "sharesSold": 0, "soldOut": False,
    "launch": False, "launchBlock": 0, "startTime": 1794394800,
    "startTimeWib": "2026-11-11 18:00 WIB", "deadline": 1794481200,
    "deadlineWib": "2026-11-12 18:00 WIB", "SALE_DURATION": 86400,
    "raised": 0, "owner": "0x7f1865025cbd69059daf61b4f26c54ab1d73d95f",
    "projectWallet": "0x7f1865025cbd69059daf61b4f26c54ab1d73d95f",
    "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "verifiedAt": "2026-11-11T02:02:03Z",
    "website": None, "websiteVerified": False, "xVerified": False,
    "baselineNote": ("UPCOMING track-C run 0931 (temuan feed Sourcify verifiedAt 2026-11-11T02:02:03Z; S1 PASS: "
        "mint + quoteMint/mintCost + freeClaimed + AGENT_ID_REGISTRY; hot-leg 0859 sequential retry + probe-ddc2 run ini "
        "corroborate). FREE_SHARES 500/500 belum terpakai, freeClaimedBy(user)=false, mintCost(1)=0, launch=false, "
        "startTime 2026-11-11 18:00 WIB, deadline 2026-11-12 18:00 WIB. Kontrak + owner BERSIH dari same-owner-discards.json "
        "(61 entri, 12 owner). Website UNVERIFIED (pencarian alamat kontrak + nama proyek: 0 hit; gate dicek ulang saat opening). "
        "BUKAN lead (belum launching, umur UNVERIFIED) - TIDAK di-preview/di-mint."),
    "lastReadBlock": probe_ddc2.get("block", BLOCK), "lastReadWib": TS,
    "runNote0931": ("Run 0931: SHINE BARU sebagai UPCOMING track-C (dilaporkan sekali run ini). Sale S1 terverifikasi, "
        "free pool 500/500, slot user terbuka, TAPI launch=false - buka 18:00 WIB hari ini. Bukan lead, bukan kandidat. "
        "Dicek ulang tiap run; saat opening, gate website + safety dicek sebelum promosi apa pun."),
}

# --- 8. Rulz Share + Mimint Share: tetap upcoming (totalMinted 0) ---
for k in ("Rulz Share", "Mimint Share"):
    e = C.get(k)
    if isinstance(e, dict):
        e["totalMinted"] = probe_slot.get(k, {}).get("totalMinted", 0)
        e["mintStart"] = probe_slot.get(k, {}).get("mintStart", 1794528000)
        e["lastReadBlock"] = probe_slot.get("block", BLOCK)
        e["lastReadWib"] = TS
        e["runNote0931"] = ("Run 0931: totalMinted MASIH 0, mintStart 1794528000 = 13 Nov ~07:00 WIB - "
                            "tetap upcoming, belum launching.")

# --- 9. top-level run notes ---
snap["last_run_wib"] = TS
snap["timestamp_wib"] = TS
snap["last_run_note"] = ("Run 0931: 1 UPCOMING track-C baru: SHINE (sale S1, free pool 500/500, slot user terbuka, "
    "buka 18:00 WIB hari ini - BUKAN lead, tidak di-preview/di-mint). Stampooor 437/1200 = 36,42% (velocity GAGAL, "
    "tetap EARLY); Jade Vault 320/8888, quote 0 (tetap EARLY). NIGHTFORGE 734/2000 = 36,7% (tetap watchlist-only <70%). "
    "LOWB masih belum dibuka (opened 0), free lane 802/1000. Scan FAST-FAIL (pre-flight Ankr timeout >120 dtk). "
    "binanceai launched=0 (refund phase). 0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead baru.")
snap["runNote0931"] = snap["last_run_note"]
snap["runNote0931_scan"] = ("Scan run 0931 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) TIDAK selesai dalam 120 dtk "
    "(timeout wrapper rc=124, log kosong - output ter-buffer; batas aturan <60 dtk). Outage Ankr berlanjut sejak "
    "~13:33 WIB 2026-11-09 (kuota 0% s.d. 1 Des 2026). Watermark TIDAK dimajukan (tetap 132512564; gap ke head "
    "~378.000 blok dan tumbuh; backfill OFF). Track-C 5c dilewati run ini (tidak ada output scan baru).")
snap["runNote0931_binanceai"] = ("Run 0931: launched=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok %s) - "
    "TIDAK BERUBAH (refund phase, sudah dilaporkan sekali). pending_claims kosong." % binanceai.get("block"))
snap["runNote0931_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah), 116 kontrak, "
    "7 same_owner_discarded; 0 kontrak di luar snapshot (semua sudah tercatat). Tidak ada temuan pelengkap baru. "
    "same-owner-discards.json mtime 2026-11-10 20:22 WIB (61 entri, 12 owner) - tidak ada entri baru; owner SHINE "
    "0x7f18...d95f BERSIH dari discards.")
snap["runNote0931_discovery"] = ("Discovery run 0931: Boltbook EN 200 45.820B + ZH 200 45.969B, 12 alamat unik, 0 baru "
    "vs hot-leg-seen (5 di snapshot, 7 sudah dicek hot leg). Sweep EN: 0 proyek baru (Agentic Gangster, Golden Agents, "
    "BNB ORBIT, Agent Operators - semua sudah di snapshot). Sourcify feed 20 kontrak (verified 02:02-02:40Z): retry "
    "shape-check S1=1 (SHINE 0xDDc2), S2=0, EARLY=0; 4 timeout ABI pertama (0x5e36, 0x03Fe, 0xdef5, 0xd262) sudah di "
    "hot-leg-seen (ditriase hot leg, bukan lead). Odaily 200 + PANews 200: 0 keyword hit. SHINE website: pencarian "
    "alamat kontrak + nama proyek 0 hit - UNVERIFIED (gate dicek ulang saat opening 18:00 WIB).")
snap["runNote0931_age_exclusions"] = ("Run 0931: 0 age-exclusion BARU. Deadline berjalan: NIGHTFORGE 14:37 WIB 11 Nov "
    "(mintStart 10 Nov 14:37 WIB; 36,7% - watchlist-only); AgentPals ~06:33 WIB 12 Nov; MOODENG ~02:00 WIB 12 Nov; "
    "UFO ~22:05 WIB 12 Nov. Gelombang early lead umur UNVERIFIED (watchlist-only untuk umur, bukan age-exclusion).")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE DONE. contracts:", len(C), "track_c:", len(TC))
print("SHINE in track_c:", "SHINE" in TC)
