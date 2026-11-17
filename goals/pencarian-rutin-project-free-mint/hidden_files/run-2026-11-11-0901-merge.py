#!/usr/bin/env python3
"""Merge run 0901 results into onchain-snapshot.json. Writes snapshot (with .bak)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-11-0901-reread.json"))
probe_nf = json.load(open(BASE + "run-2026-11-11-0901-probe-nf-lowb.json"))
probe_extra = json.load(open(BASE + "run-2026-11-11-0901-probe-extra.json"))
probe_slot = json.load(open(BASE + "run-2026-11-11-0901-probe-slot-7eb9.json"))
probe_stamp = json.load(open(BASE + "run-2026-11-11-0901-probe-stamp-7eb9.json"))
jade_quote = json.load(open(BASE + "run-2026-11-11-0901-jadevault-quote.json"))
# correct-signature quote(user,1)=0 for Jade Vault (probe_slot used wrong quote(uint256) sig)
probe_slot.setdefault("0x7Eb9", {})["quote_1"] = jade_quote.get("quote_user_1")
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0901-premerge")
C = snap.setdefault("contracts", {})
BLOCK = reread["block"]

def vel(name, new_supply):
    e = C.get(name)
    if not isinstance(e, dict):
        return None
    old = e.get("totalSupply")
    if old is None or new_supply is None:
        return None
    diff = new_supply - old
    prev_rate = e.get("currentRatePerMin")
    rate = round(diff / 30.0, 4)
    e["previousTotalSupply"] = old
    e["totalSupply"] = new_supply
    e["mintedInInterval"] = diff
    e["intervalMinutes"] = 30.0
    e["previousRatePerMin"] = prev_rate
    e["currentRatePerMin"] = rate
    ratio = None
    if prev_rate and prev_rate > 0:
        ratio = round(rate / prev_rate, 2)
    e["velocityRatio"] = ratio
    e["velocityLegPasses"] = bool(ratio is not None and ratio >= 1.5 and diff >= 20)
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 09:01 WIB"
    return diff, rate, ratio

# --- 1. reread updates (priority contracts) ---
for name, d in reread["reread"].items():
    if name not in C:
        continue
    e = C[name]
    ns = d.get("totalSupply")
    if ns is None and d.get("totalMinted") is not None:
        ns = d.get("totalMinted")
    if ns is not None:
        r = vel(name, ns)
        diff, rate, ratio = r if r else (None, None, None)
        e["runNote0901"] = (f"Run 0901 (blok {BLOCK}): totalSupply {e.get('previousTotalSupply')}->{ns} "
            f"(+{diff}, {rate}/mnt vs prev {e.get('previousRatePerMin')} = {ratio}x) -> velocity "
            f"{'LOLOS' if e.get('velocityLegPasses') else 'GAGAL'}; bal_user={d.get('balanceOf_user')}; "
            f"freeMinted={d.get('freeMinted')}; status {e.get('status')}.")
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
    e["lastReadWib"] = "2026-11-11 09:01 WIB"

# --- 2. NIGHTFORGE: demoted by new >70% strong-lead rule (adopted 09:18 WIB) ---
nf = C.get("NIGHTFORGE")
if isinstance(nf, dict):
    p = probe_nf.get("NIGHTFORGE", {})
    nf.update({"totalSupply": p.get("totalSupply", 732), "agentFreeUsed": p.get("agentFreeUsed"),
               "paidMinted": p.get("paidMinted"), "mintStart": p.get("mintStart"),
               "mintEnd": p.get("mintEnd"), "freePctVerified": 36.45,
               "status": "watchlist-only-below-70pct-2026-11-11",
               "lastReadBlock": probe_nf.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"})
    nf["runNote0901"] = ("Run 0901: agentFreeUsed 729/2000 = 36,45% (totalSupply 732, paidMinted 3), slot terbuka "
        "(agentFreeByWallet 0, balanceOf 0, mintOpen 1). DEMOSI dari strong-lead-gate-blocked: ambang strong lead "
        "berubah ≥25% -> >70% (user 11 Nov 09:18 WIB) — 36,45% TIDAK lagi strong lead; gate-blocked-recheck TIDAK "
        "lagi berlaku; deadline umur 14:37 WIB 11 Nov moot untuk jalur strong lead. TIDAK di-preview/di-mint. "
        "Bukan kandidat (butuh 50% + velocity; velocity GAGAL +1 token).")

# --- 3. Stampooor Stamp Packs: watchlist-only-upcoming -> EARLY (first mints verified) ---
st = C.get("Stampooor Stamp Packs")
slot = probe_slot.get("Stampooor_slot", {})
if isinstance(st, dict):
    # freshest confirmed freeMinted: probe-stamp (blok 132887891) = 283, beats probe-extra 217
    fm = probe_stamp.get("Stampooor", {}).get("freeMinted") or slot.get("freeMinted") or probe_extra.get("Stampooor Stamp Packs", {}).get("freeMinted")
    st.update({"status": "early-lead-reported-2026-11-11",
               "totalMinted": slot.get("freeMinted") or fm, "freeMinted": fm,
               "totalSupply": slot.get("freeMinted") or fm,
               "mintStart": 1794362419, "mintOpen": 1,
               "freeAvailable_user": slot.get("freeAvailable_user"),
               "freeUsed_user": slot.get("freeUsed_user"),
               "previousTotalSupply": 0, "mintedInInterval": fm, "intervalMinutes": 30.0,
               "currentRatePerMin": round(fm / 30.0, 4) if fm else None, "previousRatePerMin": None,
               "velocityRatio": None, "velocityLegPasses": False,
               "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"})
    st["runNote0901"] = (f"Run 0901 (blok {probe_slot.get('block', BLOCK)}): FIRST MINTS terverifikasi 0->{fm} "
        f"-> PROMOSI watchlist-only-upcoming -> EARLY LEAD (dilaporkan sekali run ini). mintStart 1794362419 = "
        f"11 Nov ~09:00 WIB (umur TERVERIFIKASI <24 jam, ~25 mnt saat probe). Free {fm}/1200 = {round(fm/1200*100,2) if fm else '?'}% "
        f"(<25% lama, <70% baru — BUKAN strong lead). Slot user: balanceOf 0, freeAvailable(user)={slot.get('freeAvailable_user')}, "
        f"freeUsed(user)={slot.get('freeUsed_user')}. Velocity: baseline pertama dicatat, belum lulus. X + website UNVERIFIED. "
        f"TIDAK di-preview/di-mint (tier early).")

# --- 4. 0x7Eb9: agent-shaped via AGENT_ID()=registry resmi; free/paid decided by quote ---
q7 = probe_slot.get("0x7Eb9", {})
if q7.get("quote_1") is not None and q7.get("quote_1") == 0:
    C["0x7Eb9"] = {"address": "0x7Eb92041aa3037e39baA88154F279e3D9F85c593",
        "status": "early-lead-reported-2026-11-11",
        "name": q7.get("name"), "symbol": q7.get("symbol"), "kind": "ERC721",
        "totalMinted": q7.get("totalMinted"), "totalSupply": q7.get("totalMinted"),
        "MAX_SUPPLY": q7.get("MAX_SUPPLY"), "mintedBy_user": q7.get("mintedBy_user"),
        "quote_1": 0, "AGENT_ID": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
        "baselineNote": "EARLY run 0901 (temuan feed Sourcify verifiedAt 2026-11-11T01:40:26Z; retry ABI pasca-timeout): AGENT_ID()=registry resmi 0x60B926...022F (hot-leg 0850 melewatkannya — cek nama-fungsi saja, tanpa baca nilai konstanta). totalMinted 256 terverifikasi on-chain run ini (252 -> 256 antar probe). quote(user,1)=0 (GRATIS). Umur + website + X UNVERIFIED. TIDAK di-preview/di-mint (tier early).",
        "previousTotalSupply": None, "mintedInInterval": None, "intervalMinutes": 30.0,
        "currentRatePerMin": None, "previousRatePerMin": None, "velocityRatio": None,
        "velocityLegPasses": False,
        "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"}
    C["0x7Eb9"]["runNote0901"] = ("Run 0901: EARLY LEAD baru 'Jade Vault' (JADE, dilaporkan sekali). AGENT_ID()=registry resmi; "
        "totalMinted 256/8888; quote(user,1)=0 (gratis); mintedBy(user)=0. Umur/website/X UNVERIFIED. "
        "TIDAK di-preview/di-mint (tier early).")
elif q7.get("quote_1") is not None:
    C["0x7Eb9"] = {"address": "0x7Eb92041aa3037e39baA88154F279e3D9F85c593",
        "status": "checked-not-lead-paid-only-2026-11-11",
        "name": q7.get("name"), "symbol": q7.get("symbol"), "kind": "ERC721",
        "totalMinted": q7.get("totalMinted"), "totalSupply": q7.get("totalMinted"),
        "MAX_SUPPLY": q7.get("MAX_SUPPLY"), "mintedBy_user": q7.get("mintedBy_user"),
        "quote_1": q7.get("quote_1"), "AGENT_ID": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
        "baselineNote": "CHECKED run 0901 (temuan feed Sourcify verifiedAt 2026-11-11T01:40:26Z; retry ABI pasca-timeout): AGENT_ID()=registry resmi, TAPI quote(user,1)>0 (PAID-ONLY) -> BUKAN lead, tidak dilaporkan. totalMinted 252.",
        "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"}
else:
    C["0x7Eb9"] = {"address": "0x7Eb92041aa3037e39baA88154F279e3D9F85c593",
        "status": "checked-not-lead-quote-unverified-2026-11-11",
        "name": q7.get("name"), "symbol": q7.get("symbol"), "kind": "ERC721",
        "totalMinted": q7.get("totalMinted"), "totalSupply": q7.get("totalMinted"),
        "MAX_SUPPLY": q7.get("MAX_SUPPLY"), "mintedBy_user": q7.get("mintedBy_user"),
        "AGENT_ID": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
        "baselineNote": "CHECKED run 0901: AGENT_ID()=registry resmi (agent-shaped), totalMinted 252, TAPI quote gagal dibaca (transport) -> gratis/berbayar UNVERIFIED; TIDAK dilaporkan sebagai lead; dicek ulang run berikut.",
        "lastReadBlock": probe_slot.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"}

# --- 5. Agent Punk Id (Boltbook baru): sold out terverifikasi -> checked, tidak dilaporkan ---
C["Agent Punk Id"] = {"address": "0x53c03c027f1ac5c9bedd08a4ce5d1444bf48ae7d",
    "status": "checked-not-lead-sold-out-2026-11-11",
    "name": "Agent Punk Id", "symbol": "APID", "kind": "ERC721",
    "totalSupply": 10000, "MAX_SUPPLY": 10000, "mintOpen": 1,
    "baselineNote": "CHECKED run 0901 (temuan baru Boltbook front page, post zeleo.ai 2026-11-11T02:06:07Z): totalSupply 10000 = MAX_SUPPLY 10000 -> SOLD OUT penuh (mintOpen 1 adalah jebakan). BUKAN lead, tidak dilaporkan.",
    "lastReadBlock": probe_nf.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"}

# --- 6. LOWB track_c: masih belum dibuka; free lane maju 646->783 ---
TC = snap.setdefault("track_c", {})
lb = probe_nf.get("LOWB", {})
if isinstance(TC.get("LOWB"), dict) and lb:
    e = TC["LOWB"]
    e.update({"opened": lb.get("opened"), "totalFreeMinted": lb.get("totalFreeMinted"),
              "totalMinted": lb.get("totalMinted"), "totalPaidMinted": lb.get("totalPaidMinted"),
              "FREE_SHARES": lb.get("FREE_SHARES"), "MAX_SHARES": lb.get("MAX_SHARES"),
              "lastReadBlock": probe_nf.get("block", BLOCK), "lastReadWib": "2026-11-11 09:01 WIB"})
    e["runNote0901"] = ("Run 0901: opened MASIH 0 (sale belum dibuka; MINT_DEADLINE 2026-11-14 19:00 WIB). "
        "Free lane maju: totalFreeMinted 646->783/1000 (Boltbook 772 di tengah run — konsisten), totalMinted 795, "
        "totalPaidMinted 12. Tetap watchlist-only-not-open (lead track-C butuh sale opening).")

# --- 7. track_c updates from reread (non-None only; batch-fail keeps old values) ---
for name, d in reread["track_c"].items():
    if name not in TC or not isinstance(TC[name], dict):
        continue
    e = TC[name]
    if d.get("freeMinted") is not None:
        e["freeMinted"] = d["freeMinted"]
    if d.get("totalSupply") is not None:
        e["totalSupply"] = d["totalSupply"]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-11 09:01 WIB"
    if name == "VISION":
        e["runNote0901"] = "Run 0901: totalSupply tetap 3,2346e27 (minting berjalan) tapi free views tetap None -> tetap watchlist-only-age-unverified, BUKAN promosi."
    if name == "0x5f76cAb7-5a-hit":
        e["runNote0901"] = "Run 0901: totalSupply 3,2238e27 -> 3,2346e27; free views tetap None -> tanpa perubahan status."

# --- 8. top-level run notes ---
snap["last_run_wib"] = "2026-11-11 09:01 WIB"
snap["timestamp_wib"] = "2026-11-11 09:01 WIB"
snap["last_run_note"] = ("Run 0901: 2 EARLY LEAD baru: Stampooor Stamp Packs (first mints 0->283, mintStart 11 Nov ~09:00 WIB, "
    "free 283/1200 = 23,58%) + Jade Vault (JADE, AGENT_ID()=registry resmi, totalMinted 256/8888, quote(user,1)=0 gratis). "
    "NIGHTFORGE DEMOSI strong-lead -> watchlist-only (36,45% < ambang baru >70%, user 09:18 WIB). "
    "Agent Punk Id (Boltbook baru) SOLD OUT 10000/10000, bukan lead. LOWB masih belum dibuka (opened 0), free lane 783/1000. "
    "Scan FAST-FAIL (Ankr RemoteDisconnected 76 dtk). binanceai launched=0 (refund phase). "
    "0 kandidat / 0 strong-lead mint / 0 track-B / 0 track-C lead baru.")
snap["runNote0901"] = snap["last_run_note"]
snap["runNote0901_scan"] = ("Scan run 0901 FAST-FAIL: pre-flight Ankr ankr_getLogs (50 blok) RemoteDisconnected "
    "('Remote end closed connection without response') dalam 76,0 dtk (head 132885883; BUKAN 401 kali ini — transport putus; "
    "kuota Ankr tetap 0% s.d. 1 Des 2026, outage sejak ~13:33 WIB 2026-11-09). Watermark TIDAK dimajukan (tetap 132512564; "
    "gap ke head ~374.000 blok dan tumbuh; backfill OFF).")
snap["runNote0901_binanceai"] = ("Run 0901: launched=0, tokenClaimed(user)=0, TOKEN balanceOf(user)=0 (blok 132885977) — TIDAK BERUBAH "
    "(refund phase, sudah dilaporkan sekali). pending_claims kosong.")
snap["runNote0901_bridge"] = ("Bridge scan-bridge.json: mtime 2026-11-08 18:21 WIB (STALE, tidak berubah), 116 kontrak, 7 same_owner_discarded. "
    "6 kontrak bridge tidak ada di snapshot — sama seperti run 0831 (temuan scan 3-4 Nov, sudah ditriase BUKAN lead); tidak dipromosikan, "
    "tidak ditambahkan ke snapshot. Tidak ada temuan pelengkap baru. same-owner-discards.json mtime 2026-11-10 20:22 WIB — tidak ada entri baru.")
snap["runNote0901_discovery"] = ("Boltbook EN 45.805 byte + ZH 45.891 byte; 13 alamat EN / 15 ZH, 1 baru vs hot-leg-seen: Agent Punk Id "
    "0x53c03c... (SOLD OUT 10000/10000 — bukan lead). Sweep EN: 0 proyek baru (Oathbots 28 Okt, Agentic Gangster — pool habis, "
    "AGENT MAO paused, BLOB Miner excluded, AgentForge 27 Okt, Pixel Fox 25 Okt). Feed Sourcify 20 terbaru (verified 01:35-02:07Z): "
    "S1=0 S2=0 EARLY=0 pada pass pertama (2 ABI timeout, di-retry: 0x7Eb9 agent-shaped via AGENT_ID, 0x4e11 ERC20 biasa). "
    "Odaily + PANews: 0 keyword Agent ID / free mint / free share / 免费.")
snap["runNote0901_threshold"] = ("ATURAN BARU 11 Nov 09:18 WIB (user tap 'Ya, strong lead saja'): ambang STRONG LEAD berubah ≥25% -> LEBIH DARI 70% "
    "kuota gratis. Hanya tier strong lead (reporting + direct mint). TIDAK berubah: kandidat track-A (50% + velocity), track-C lead, "
    "track-B, guard (b) AUTO-MINT >25% tracked-wallet. Dampak run ini: NIGHTFORGE 36,45% DEMOSI ke watchlist-only; SOLDERCATS/REWINDCLUB "
    "mint 25% pagi ini grandfathered (dieksekusi sebelum perubahan).")

json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("MERGE 0901 DONE")
