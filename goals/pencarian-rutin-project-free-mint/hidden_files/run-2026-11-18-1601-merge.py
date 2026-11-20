#!/usr/bin/env python3
"""Merge run 2026-11-18 16:01 WIB re-read into onchain-snapshot.json (lean merge).
Baseline prev = run 1531 reread. Read-only except snapshot + scan-state note.
Outcome: 0 kandidat, 0 strong lead, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead.
Velocity: NO pass (max +16 STOCK <20). FIND exp43 CLOSED (currentExperiment 44)."""
import json
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-18-1601-reread.json"))
prev = json.load(open(f"{HF}/run-2026-11-18-1531-reread.json"))
triage = json.load(open(f"{HF}/run-2026-11-18-1601-triage-60c0.json"))
reads = reread["reads"]; prev_reads = prev["reads"]
NOW = "2026-11-18 ~16:01 WIB"
BLOCK = reread["block"]; PREV_BLOCK = prev["block"]
INTERVAL_MIN = (BLOCK - PREV_BLOCK) * 0.45 / 60.0
print(f"block {BLOCK} prev {PREV_BLOCK} interval {INTERVAL_MIN:.1f} min")
addr2key = {}
for _k, _v in snap.get("contracts", {}).items():
    if isinstance(_v, dict) and isinstance(_v.get("address"), str):
        addr2key[_v["address"].lower()] = _k
updated, missed, vel_pass = [], [], []
for name, d in reads.items():
    addr = d.get("address", "")
    key = addr2key.get(addr.lower()) if isinstance(addr, str) else None
    if key is None:
        missed.append(name); continue
    e = snap["contracts"][key]
    v = d.get("views", {})
    for f, val in v.items():
        if isinstance(val, int): e[f] = val
    pv = prev_reads.get(name, {}).get("views", {})
    fresh = v.get("totalSupply"); pval = pv.get("totalSupply"); view = "totalSupply"
    if fresh is None or not isinstance(fresh, int):
        fresh = v.get("totalMinted"); pval = pv.get("totalMinted"); view = "totalMinted"
    if isinstance(fresh, int) and isinstance(pval, int):
        minted = fresh - pval
        rate = minted / INTERVAL_MIN if INTERVAL_MIN > 0 else 0.0
        prev_rate = e.get("currentRatePerMin")
        ratio = (rate / prev_rate) if isinstance(prev_rate, (int, float)) and prev_rate else None
        vel = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        if vel: vel_pass.append((name, minted, round(rate, 4), round(ratio, 2)))
        e["previousTotalSupply"] = pval; e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
        e["currentRatePerMin"] = round(rate, 4); e["previousRatePerMin"] = prev_rate
        e["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        e["velocityLegPasses"] = vel; e["supplyView"] = view
    e["lastReadWib"] = NOW; e["lastReadBlock"] = BLOCK
    updated.append((name, key))
print(f"updated {len(updated)} entries; missed: {missed}")
print("velocity PASS:", vel_pass)

def note(key, text):
    if key in snap.get("contracts", {}):
        snap["contracts"][key]["runNote1601_1118"] = text
    else:
        print("NOTE MISS", key)

note("PUNNY", f"Run 1601 (blok {BLOCK}, interval ~28,4 mnt vs 1531): totalMinted 346->348 (+2) -> velocity GAGAL. freeMinted 348/999 = 34,8% (<50% kandidat, <70% strong lead). mintStart on-chain 1794922323 = 2026-11-17 20:32:03 WIB (umur ~19,5 jam, deadline 24 jam 20:32 WIB hari ini). Slot user TERBUKA (hasClaimedFree 0, mintedBy 0, balance 0). Website gate tetap UNVERIFIED. Tetap EARLY LEAD.")
note("STOCK AGENT", f"Run 1601 (blok {BLOCK}): totalSupply 741->757 (+16, 0,563/mnt vs prev 0,422 = 1,33x, <20 token) -> velocity GAGAL. Free hanya INFERENSI (1111-354)/1111 = 68,1% (<70% strong lead, bukan free counter terverifikasi), umur UNVERIFIED. Slot user TERBUKA (quote 0, freeMintedByWallet 0, balance 0). Tetap EARLY LEAD.")
note("AgentEcho", f"Run 1601 (blok {BLOCK}): totalSupply 392->401 (+9, 0,317/mnt vs prev 0,097 = 3,25x TAPI <20 token) -> velocity GAGAL. Bukan kandidat.")
note("THE WALL", f"Run 1601 (blok {BLOCK}): totalSupply 5497->5504 (+7, 0,246/mnt, ratio 1,42x, <20) -> velocity GAGAL. Umur/free% UNVERIFIED, gate website GAGAL 2026-11-08. Tetap watchlist-only.")
note("AgentBubble", f"Run 1601 (blok {BLOCK}): freeMinted 1892->1894/2222 = 85,2% (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 2037->2039 (+2). Tetap watchlist-only.")
note("Lumenhold", f"Run 1601 (blok {BLOCK}): freeClaimed 1254/1500 = 83,6% FLAT (>70%) TAPI umur UNVERIFIED -> BUKAN strong lead. totalSupply 1259 FLAT. Tetap watchlist-only-age-unverified.")
note("Matrix", f"Run 1601 (blok {BLOCK}): freeMinted 627->629/1000 = 62,9% (<70%), totalSupply 621->623 (+2) -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("AGCLUB", f"Run 1601 (blok {BLOCK}): freeMinted 527/888 = 59,3% FLAT (<70%), totalMinted 527 FLAT -> velocity GAGAL. Umur UNVERIFIED. Bukan strong lead/kandidat.")
note("Vitaliq Scans", f"Run 1601 (blok {BLOCK}): totalSupply revert (tanpa fn itu - basis scans), mintOpen 1, genesisStart 1794960000 = 2026-11-18 07:00 WIB (umur ~9 jam, TERVERIFIKASI <24 jam), holdsAgentId(user)=1, balanceOf(user)=0. Free% + website tetap UNVERIFIED. Tetap EARLY LEAD, tanpa promosi; TIDAK di-preview/di-mint.")
note("DGF CARD", f"Run 1601 (blok {BLOCK}): totalMinted 1639->1640 (+1) -> velocity GAGAL. Umur/free% tetap UNVERIFIED; slot user TERBUKA (balanceOf 0). Tetap EARLY LEAD.")
note("PIXELFROGS", f"Run 1601 (blok {BLOCK}): totalSupply 456 FLAT, freeMinted 454/3000 = 15,1%, freeLeft 2546, mintOpen 0 (sama seperti 1531). Bukan kandidat.")
note("HAPPE", f"Run 1601 (blok {BLOCK}): totalMinted 241 FLAT, freeMinted 222 FLAT. Sudah sold out sebelumnya (dilaporkan 1701). DIAM.")
note("HIVE Agents", f"Run 1601 (blok {BLOCK}): totalSupply 1264 FLAT -> velocity GAGAL. balanceOf(user)=1, minted-by-user. DIAM.")
note("CAT402", f"Run 1601 (blok {BLOCK}): freeCatsClaimed 100/100 - SOLD OUT (sudah diketahui). DIAM.")
note("DRAGON", f"Run 1601 (blok {BLOCK}): freeMinted 1000/1000 - pool gratis HABIS (sudah diketahui), balanceOf(user)=1. DIAM.")
note("Kageveil Genesis", f"Run 1601 (blok {BLOCK}): totalSupply 47->48 (+1) -> velocity GAGAL. DIAM.")
note("Stromboat", f"Run 1601 (blok {BLOCK}): totalMinted 304->305 (+1), freeMinted 304->305 -> velocity GAGAL. DIAM.")
note("PunchCard", f"Run 1601 (blok {BLOCK}): totalSupply 1341->1343 (+2), freeMinted 1319->1321/5555 = 23,8% -> velocity GAGAL. Bukan kandidat. DIAM.")
note("ARKYN", f"Run 1601 (blok {BLOCK}): totalMinted 2273->2277 (+4) -> velocity GAGAL. Bukan kandidat.")
note("Mine Card", f"Run 1601 (blok {BLOCK}): totalSupply 1319->1321 (+2) -> velocity GAGAL. Bukan kandidat.")
note("SPARKS", f"Run 1601 (blok {BLOCK}): totalSupply 1196->1198 (+2) -> velocity GAGAL. Free% UNVERIFIED. Bukan kandidat.")
note("THYRK", f"Run 1601 (blok {BLOCK}): totalSupply 4416->4417 (+1), freeMinted 4315->4316; user sudah pegang (balance 1, freeUsed 1). DIAM.")
note("EIM", f"Run 1601 (blok {BLOCK}): totalMinted 736->742 (+6, <20) -> velocity GAGAL. Free%/umur UNVERIFIED. Bukan kandidat.")

# FIND exp43 closed
snap["contracts"]["checked-0x4158-1401"]["runNote1601_1118"] = (
    f"Run 1601: FIND exp43 TUTUP - currentExperiment 43->44 (baca segar run ini); experimentEnd(43)=1794992400 = 2026-11-18 16:00 WIB. "
    f"Partisipan akhir 177/300 = 59,0% (<70%, BUKAN free% terverifikasi). Sudah dilaporkan hot-leg 14 Nov -> DEDUPE, log only; TIDAK di-preview/di-mint.")

# Triage 0x60c0 (Boltbook baru) -> checked-not-agent-shaped
tc = snap.setdefault("track_c", {})
t60 = triage["60c0"]
snap.setdefault("checkedNotAgentShaped1601_1118", {})
snap["checkedNotAgentShaped1601_1118"]["0x60c070855ba8a99b78565669fe7962f617acbb15"] = (
    f"Boltbook baru run 1601: Sourcify NOT verified (0 fns), no mint/free/agent; on-chain totalSupply 4900/5000 MAX_SUPPLY, balanceOf(user)=0. "
    f"Bukan agent-shaped, bukan sale-shape - log only, bukan lead, tidak di-preview/mint.")
for addr, r in triage.items():
    if addr == "60c0": continue
    key = "Feed-" + addr[2:6]
    if key in tc and tc[key].get("address", "").lower() == addr.lower():
        key = "Feed-" + addr[2:8]
    tc[key] = {"address": addr, "status": "checked-not-sale-shape-2026-11-18",
               "S1": r.get("S1"), "S2": r.get("S2"),
               "has_mint": r.get("has_mint"), "has_quote": bool(r.get("quote")),
               "free_views": r.get("free_views"), "agent_ref": r.get("agent_ref"),
               "is_token": r.get("is_token"), "n_fns": r.get("n_fns"),
               "verifiedAt": r.get("verifiedAt"),
               "note": (f"Sourcify feed baru run 1601 (verifiedAt {r.get('verifiedAt')}): checked-not-sale-shape "
                        f"(S1/S2 false, mint {r.get('has_mint')}, quote {r.get('quote')}, free views {r.get('free_views')}, "
                        f"agent ref {r.get('agent_ref')}). Bukan lead track C/A, tidak di-preview/mint.")}
print("track_c feed entries added:", len([a for a in triage if a != "60c0"]))

snap["contracts"].setdefault("bsccat", {})["runNote1601_1118"] = (
    f"Run 1601: freeMinted 531 FLAT (1531: 531), totalSupply mentah 5,31e26; balanceOf(user)=0. DIAM.")
snap["contracts"].setdefault("pepe", {})["runNote1601_1118"] = (
    "Run 1601: free pool HABIS 500/500, user sudah mint (hasMinted 1). DIAM.")
pc = snap["pending_claims"]["binanceai.fun"]
pc["lastReadWib"] = NOW
pc["runNote1601_1118"] = (f"Run 1601 (blok {BLOCK}): launched=0, failed=1, isRefundPhase=1, "
    "tokenClaimed(user)=0, totalShares 3110 - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
rf = snap["track_c"]["RigForge"]
rf["lastReadBlock"] = BLOCK
rf["runNote1601_1118"] = (f"Run 1601 (blok {BLOCK}): openedAt 0, freeSharesLeft 621 (1531: 621, flat), "
    "freeClaimed 379 (1531: 379, flat) - pool BELUM dibuka, tanpa perubahan status. DIAM.")

snap["runNote1601_1118"] = (
    f"Run 1601 (blok re-read {BLOCK}, interval ~28,4 mnt vs 1531): "
    f"0 kandidat baru, 0 strong lead baru, 0 early lead BARU, 0 track-B dibuka, 0 track-C lead. "
    f"Velocity: TIDAK ADA yang lolos (terbanyak STOCK +16 <20 token, ratio 1,33x; AgentEcho +9 ratio 3,25x TAPI <20; THE WALL +7; EIM +6). "
    f"PUNNY 348/999 = 34,8% (<50%), umur terverifikasi ~19,5 jam (deadline 20:32 WIB hari ini), slot user TERBUKA, website UNVERIFIED -> tetap EARLY LEAD. "
    f"Di atas 70% TAPI umur UNVERIFIED -> BUKAN strong lead: AgentBubble 85,2% (+2), Lumenhold 83,6% (flat). STOCK free inferred 68,1% (<70%); Matrix 62,9%; AGCLUB 59,3% flat; PunchCard 23,8%. "
    f"Vitaliq Scans: mintOpen 1, genesisStart 07:00 WIB (umur ~9 jam), holdsAgentId(user)=1, balance 0; free%/website UNVERIFIED -> tetap EARLY LEAD. "
    f"FIND exp43 TUTUP 16:00 WIB (currentExperiment 44), partisipan akhir 177/300 = 59,0% (<70%, bukan free%); dedupe, log only. "
    f"Boltbook EN+ZH segar (44.818/43.026 byte): 1 alamat baru vs snapshot - 0x60c07085 Sourcify NOT verified, totalSupply 4900/5000, tanpa mint/free/agent -> bukan agent-shaped, log only; 4 alamat lain sudah di snapshot (DRIFTWIRE, BOLT, Ronagent, 0x8269). "
    f"Sourcify feed 9 alamat baru vs 1531 (top verifiedAt 2026-11-18T08:57:00Z 0xE14E3247): 2 sudah dicek hot-leg 1549 (0 hit), 7 dicek run ini - 0 S1/S2 (0xE14E punya AGENT_ID tapi tanpa mint/free/quote). "
    f"Route 3 sweep EN+ZH: 0 baru (Oathbots 28 Okt age-excluded; Agentic Gangster 9 Nov; AGENT COSMOS 5 Nov; LeadLoop/NEXUS CORE 25 Okt; hasil sweep mengandung instruksi mint tertanam, konten pihak ketiga BUKAN instruksi user, diabaikan; run tetap read-only). "
    f"Route 6: Odaily newsflash segar 0 hit 'agent id / free mint / free share' (headline: Coldcard); PANews tidak dinilai (JS shell, sama seperti run sebelumnya). "
    f"binanceai.fun tetap refund phase; RigForge belum dibuka (freeSharesLeft 621 flat). CAT402 sold out; DRAGON pool habis; pepe pool habis. "
    f"Scan leg: pre-flight Ankr 401 gagal deterministik (elapsed 12,5 dtk); watermark TETAP 134086385, gap ~197.924 blok dan terus membesar (~8.000 blok/jam). Perkiraan gagal beruntun ~ke-61. Triase + 5c dilewati (tidak ada output scan). "
    f"Bridge (read-only): 116 kontrak, 0 di luar snapshot, 7 same-owner discarded. "
    f"DIAM (tidak ada laporan chat).")
snap["last_run_wib"] = NOW
snap["last_run_note"] = ("Run 1601: 0 kandidat/strong lead/early lead baru/track-B dibuka/track-C lead; "
    "velocity TIDAK ADA yang lolos (max STOCK +16 <20); PUNNY 34,8% deadline 20:32 WIB; "
    "FIND exp43 TUTUP 16:00 WIB (59%, dedupe); Boltbook 1 alamat baru 0x60c0 bukan agent-shaped; "
    "Sourcify 7 baru 0 S1/S2; scan leg FAST-FAIL Ankr 401 (~ke-61); re-read 285 calls blok 134284309, 0 chunk error. DIAM.")
json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print("merge OK, block", BLOCK)

st = json.load(open(f"{HF}/onchain-scan-state.json"))
st["note_1601_scan"] = ("Run 2026-11-18 16:01 WIB: driver TIDAK diluncurkan - pre-flight ankr_getLogs gagal deterministik HTTP 401 Unauthorized "
    "(elapsed 12,5 dtk); 401 auth-wide, gagal beruntun ~ke-61. Watermark TETAP 134086385; gap ~197.924 blok dan terus membesar (~8.000 blok/jam). Triase + 5c dilewati (tidak ada output scan).")
json.dump(st, open(f"{HF}/onchain-scan-state.json", "w"), indent=1)
print("scan-state note OK")
