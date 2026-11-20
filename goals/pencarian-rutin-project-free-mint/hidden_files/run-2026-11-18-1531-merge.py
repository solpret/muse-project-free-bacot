#!/usr/bin/env python3
"""Merge run 2026-11-18 15:31 WIB re-read into onchain-snapshot.json (lean merge).
Baseline prev = run 1401 (1431/1501 transport-failed, no reread). Read-only except
snapshot + scan-state note. No preview/mint/claim.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
Velocity PASSES for PUNNY + STOCK AGENT but %/age legs still fail -> no promotion.
FIND exp43 177/300 (59%) still <70%, phase ends 16:00 WIB. 0x8334 unlaunched (0 mints)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1531-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1401-reread.json"))
feed_shape = json.load(open(f"{HF}/run-2026-11-18-1531-feed-shape.json"))
triage8334 = json.load(open(f"{HF}/run-2026-11-18-1531-triage-8334.json"))
exp43 = json.load(open(f"{HF}/run-2026-11-18-1531-exp43.json"))
reads = reread["reads"]
prev_reads = prev["reads"]
NOW = "2026-11-18 ~15:31 WIB"
BLOCK = reread["block"]
PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")

addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k

updated, missed = [], []
vel_pass = []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name)
        continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int):
            e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply")
    pval = pv.get("totalSupply")
    view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted")
        pval = pv.get("totalMinted")
        view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel:
            vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4)
        e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel
        e["supplyView"] = view
    e["lastReadWib"] = NOW
    e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed (no snapshot key): {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1531_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1531 (blok {BLOCK}, interval ~92,5 mnt vs 1401): totalMinted 309->346 (+37, 0,400/mnt vs prev 0,234 = 1,71x, >=20) -> velocity LOLOS. TAPI freeMinted 346/999 = 34,6% (<50% kandidat, <70% strong lead) -> TIDAK ada promosi. mintStart on-chain 2026-11-17 20:32:03 WIB (umur ~19 jam, tutup 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1531 (blok {BLOCK}, interval ~92,5 mnt vs 1401): totalSupply 702->741 (+39, 0,422/mnt vs prev 0,094 = 4,51x, >=20) -> velocity LOLOS. TAPI free hanya INFERENSI (1111-370)/1111 = 66,7% (<70% strong lead, bukan free counter terverifikasi) dan umur UNVERIFIED -> TIDAK ada promosi. Slot user TERBUKA (quote 0, freeMintedByWallet 0, balance 0). Tetap EARLY LEAD.")
note("HIVE Agents", f"Run 1531 (blok {BLOCK}): totalSupply 1263->1264 (+1) -> velocity GAGAL. balanceOf(user)=1, minted-by-user. DIAM.")
note("Bubblebruin", f"Run 1531 (blok {BLOCK}): totalSupply 2622 FLAT, freeClaimed 2616/7777 = 33,6% FLAT, balanceOf(user)=1, minted-by-user. DIAM.")
note("Agent Bubble", f"Run 1531 (blok {BLOCK}): freeMinted 1891->1892/2222 = 85,1% (>70%) TAPI umur UNVERIFIED dan totalSupply +1 (2036->2037) -> BUKAN strong lead. Tetap watchlist-only.")
note("Lumenhold", f"Run 1531 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1259 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix Agents", f"Run 1531 (blok {BLOCK}): freeMinted 622->627/1000 = 62,7% (<70%), totalSupply 619->621 (+2) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1531 (blok {BLOCK}): freeMinted 527/888 = 59,3% FLAT (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("SPARKS", f"Run 1531 (blok {BLOCK}): totalSupply 1189->1196 (+7, <20) -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("AgentEcho", f"Run 1531 (blok {BLOCK}): totalSupply 383->392 (+9, <20) -> velocity GAGAL. Bukan kandidat.")
note("Everything Is Mine (EIM)", f"Run 1531 (blok {BLOCK}): totalMinted 718->736 (+18, <20) -> velocity GAGAL. Free% UNVERIFIED, umur UNVERIFIED. Bukan kandidat.")
note("Mine Card", f"Run 1531 (blok {BLOCK}): totalSupply 1300->1319 (+19, <20) -> velocity GAGAL. Bukan kandidat. DIAM.")
note("THE WALL", f"Run 1531 (blok {BLOCK}): totalSupply 5481->5497 (+16, <20) -> velocity GAGAL. Umur UNVERIFIED, free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("PunchCard", f"Run 1531 (blok {BLOCK}): totalSupply 1339->1341 (+2), freeMinted 1317->1319/5555 = 23,7% -> velocity GAGAL. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1531 (blok {BLOCK}): totalMinted 2254->2273 (+19, <20) -> velocity GAGAL. Bukan kandidat.")
note("AgentNOVA", f"Run 1531 (blok {BLOCK}): totalSupply 763->767 (+4) -> velocity GAGAL. Bukan kandidat.")
note("DGF CARD", f"Run 1531 (blok {BLOCK}): totalMinted 1624->1639 (+15, <20) -> velocity GAGAL. Umur tetap UNVERIFIED, free% UNVERIFIED, X/discussion UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD, tanpa promosi.")
note("CAT402", f"Run 1531 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1531 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("Vitaliq Scans", f"Run 1531 (blok {BLOCK}): totalSupply revert (tanpa fn itu - basis scans), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~8,5 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balanceOf(user)=0. Free% tetap UNVERIFIED, website tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi; TIDAK di-preview/di-mint.")
note("Kageveil Genesis", f"Run 1531 (blok {BLOCK}): totalSupply 46->47 (+1), normalMinted 46->47 -> velocity GAGAL. DIAM.")
note("Stromboat", f"Run 1531 (blok {BLOCK}): totalMinted 301->304 (+3), freeMinted 301->304 -> velocity GAGAL. DIAM.")
note("Velko Rig", f"Run 1531 (blok {BLOCK}): totalMinted 935->938 (+3) -> velocity GAGAL. DIAM.")

# ---- FIND exp43 fresh read ----
ev = exp43["views"]
snap["contracts"]["checked-0x4158-1401"]["runNote1531_1118"] = (
    f"Run 1531 (blok {exp43['block']}): currentExperiment 43, participantsOf(43) 150->177 (+27 sejak 1401), "
    f"177/300 = 59,0% partisipan/kap (masih <70%; BUKAN free% terverifikasi - tanpa free counter). "
    f"experimentEnd(43)=1794992400 = 2026-11-18 16:00 WIB (fase tutup ~25 mnt lagi). "
    f"Sudah dilaporkan hot-leg 14 Nov -> DEDUPE, log only, tidak dilaporkan ulang; TIDAK di-preview/di-mint.")

# ---- 0x8334 Fangzhou Menpiao / ARKT: unlaunched, 0 mints -> watchlist-only upcoming ----
snap["contracts"]["ARKT-8334"] = {
    "address": "0x8334C7d0e8aF217EEA5251A0A181e628971535e1",
    "status": "watchlist-only-upcoming-not-launched-2026-11-18",
    "name": "方舟门票",
    "symbol": "ARKT",
    "kind": "ERC721",
    "source": "sourcify-feed-2026-11-18-1531",
    "firstSeenWib": "2026-11-18 ~15:31 WIB",
    "agentShaped": True,
    "agentShapeEvidence": "Sourcify verified 2026-11-18T07:44:51Z, 36 fns, agentId + claim/hasClaimed/claimSigner + MAX_PER_WALLET 1; NO registry bytes in code, NO free-mint fn, NO free views, NO quote fn",
    "totalSupply": 0, "totalMinted": 0,
    "agentId": triage8334["views"]["agentId"],
    "owner": "0xc8dead02117464e715a6885866ed8714c462047b",
    "note": ("Run 1531 triage (Sourcify feed baru, verifiedAt 2026-11-18T07:44:51Z = 14:44:51 WIB): ERC721 claim-gated "
      "signature (claim + hasClaimed + claimSigner 0x73ce048c71005e681851e5649b4711853526ffba, MAX_PER_WALLET 1, MAX_AUTH_WINDOW 900, paused 0, "
      "agentId 552192074493313695968015109214105588393044541999, codelen 18506, registry_bytes False). "
      "totalSupply 0, totalMinted 0 -> BELUM LAUNCH, 0 mint. BUKAN early lead (first mints belum ada), BUKAN kandidat/strong lead. "
      "Website + launch time UNVERIFIED. Watchlist-only upcoming; TIDAK di-preview/di-mint. "
      "Catatan: BUKAN ARKT 0xf91b... yang sudah ada di snapshot (kontrak berbeda, nama sama)."),
    "lastReadBlock": BLOCK, "lastReadWib": NOW}

# ---- Sourcify feed 18 alamat baru -> track_c checked (S1/S2 false semua) ----
tc = snap.setdefault("track_c", {})
for r in feed_shape:
    a = r["address"]
    key = "Feed-" + a[2:6]
    if key in tc and tc[key].get("address", "").lower() == a.lower():
        key = "Feed-" + a[2:8]
    tc[key] = {"address": a, "status": "checked-not-sale-shape-2026-11-18",
               "S1": r.get("S1"), "S2": r.get("S2"),
               "has_mint": r.get("has_mint"), "has_quote": r.get("has_quote"),
               "free_views": r.get("free_views"), "agent_ref": r.get("agent_ref"),
               "is_token": r.get("is_token"), "n_fns": r.get("n_fns"),
               "verifiedAt": r.get("verifiedAt"),
               "note": (f"Sourcify feed baru run 1531 (verifiedAt {r.get('verifiedAt')}): checked-not-sale-shape "
                        f"(S1/S2 false, mint {r.get('has_mint')}, quote {r.get('has_quote')}, free views {r.get('free_views')}, "
                        f"agent ref {r.get('agent_ref')}). Bukan lead track C/A, tidak di-preview/mint.")}
print("track_c feed entries added:", len(feed_shape))

snap["contracts"].setdefault("bsccat", {})["runNote1531_1118"] = (
    f"Run 1531: freeMinted 531 FLAT (1401: 531), totalSupply mentah 5,31e26; balanceOf(user)=0. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1531_1118"] = (
    "Run 1531: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")

pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1531_1118"] = (f"Run 1531 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1531_1118"] = (f"Run 1531 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1401: 621, flat), "
    "freeClaimed 379 (1401: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1531_1118"] = (
    f"Run 1531 (blok re-read {BLOCK}, interval ~92,5 mnt vs 1401; 1431/1501 transport-failed, baseline tetap 1401): "
    f"0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    f"Velocity LOLOS 2 item: PUNNY totalMinted 309->346 (+37, 0,400/mnt vs prev 0,234 = 1,71x) TAPI freeMinted 346/999 = 34,6% (<50% kandidat, <70% strong lead), "
    f"umur terverifikasi ~19 jam (tutup 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD, tanpa promosi; "
    f"STOCK AGENT totalSupply 702->741 (+39, 0,422/mnt vs prev 0,094 = 4,51x) TAPI free hanya INFERENSI 66,7% (<70%) dan umur UNVERIFIED -> tetap EARLY LEAD, tanpa promosi. "
    f"Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 85,1% (+1), Lumenhold 83,6% (flat). Matrix 62,7%, AGCLUB 59,3%, PunchCard 23,7%. "
    f"Vitaliq Scans: mintOpen 1, genesisStart 07:00 WIB terkonfirmasi (umur ~8,5 jam), holdsAgentId(user)=1, balance 0; free%/website UNVERIFIED -> tetap EARLY LEAD. "
    f"DGF CARD +15 -> velocity GAGAL; tetap EARLY LEAD. "
    f"FIND exp43 0x4158B701EaA30E8FaDBaA526F70780A38318c1C4: participants 150->177/300 = 59,0% (<70%, BUKAN free%), fase tutup 16:00 WIB; sudah dilaporkan hot-leg 14 Nov -> DEDUPE, log only. "
    f"Sourcify feed 18 alamat baru (top verifiedAt 2026-11-18T08:29:27Z): dicek ABI satu per satu, 0 S1/S2; 1 agent-shaped 0x8334 (方舟门票/ARKT, ERC721 claim-gated, agentId) TAPI totalSupply 0/totalMinted 0 -> BELUM LAUNCH, watchlist-only upcoming, bukan early lead. "
    f"17 alamat lain checked-not-sale-shape (dicatat di track_c). "
    f"Boltbook EN+ZH segar (44.910/43.234 byte): 0 alamat baru vs snapshot + hot-leg-seen. "
    f"Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt age-excluded; Agentic Gangster 9 Nov free sold out; AGENT COSMOS 5 Nov; Laser Agents 25 Okt; blokwiki tutorial; hasil sweep mengandung instruksi mint tertanam, konten pihak ketiga BUKAN instruksi user, diabaikan; run tetap read-only). "
    f"Route 6: Odaily newsflash segar 0 hit 'agent id / free mint / free share'; PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    f"binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    f"Scan leg: pre-flight Ankr 401 gagal deterministik (elapsed 7,7 dtk, head 134280319); watermark TETAP 134086385, gap ~193.934 blok dan terus membesar (~8.000 blok/jam). Perkiraan gagal beruntun ~ke-60. Triase + 5c dilewati (tidak ada output scan). "
    f"Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    f"DIAM (tidak ada laporan chat).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1531: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "velocity LOLOS PUNNY (+37, 1,71x) + STOCK (+39, 4,51x) tapi %/umur gagal -> tanpa promosi; "
    "FIND exp43 177/300 (59%), tutup 16:00 WIB, dedupe; 0x8334 ARKT belum launch (0 mint); "
    "scan leg FAST-FAIL Ankr 401 (~ke-60); re-read 285 calls blok 134280519, 0 chunk error. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1531_scan"] = ("Run 2026-11-18 15:31 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(elapsed 7,7 dtk, head 134280319); 401 auth-wide, gagal beruntun ~ke-60. Watermark TETAP 134086385; gap ~193.934 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
