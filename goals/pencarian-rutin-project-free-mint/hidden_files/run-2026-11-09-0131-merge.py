#!/usr/bin/env python3
"""Merge run 2026-11-09 01:31 WIB. Reloads snapshot fresh, applies reread +
triage + scan findings on top. Writes snapshot + seen file. Never touches
the scan-state watermark (owned by backfill, 132436704)."""
import json, shutil
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
WIB = timezone(timedelta(hours=7))
NOW = datetime.now(WIB)
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M WIB")
INTERVAL = 41.23  # block 132439722 ts 01:21:53 -> block 132445220 ts 02:03:07 WIB

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-0131-premerge")
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
rr = json.load(open(f"{BASE}/run-2026-11-09-0131-reread.json"))
C = s["contracts"]; TC = s.get("track_c", {})
NEW_BLOCK = rr.get("block")
updated = 0; degraded = 0; vel_pass = []
for name, e in C.items():
    r = rr["reread"].get(name)
    if r is None:
        continue
    prev_sup = e.get("totalSupply"); new_sup = r.get("totalSupply")
    if new_sup is None:
        degraded += 1
        note = f"Run 0131 (blok {NEW_BLOCK}, 02:03 WIB): totalSupply None (degradasi eth_call, nilai lama dipertahankan); "
    else:
        minted = None; rate = None; ratio = None; vpass = False
        if prev_sup is not None:
            minted = new_sup - prev_sup
            rate = minted / INTERVAL
            prev_rate = float(e.get("currentRatePerMin") or e.get("ratePerMin") or 0) or 0.0
            if prev_rate > 0:
                ratio = rate / prev_rate
            vpass = bool(minted >= 20 and prev_rate > 0 and ratio is not None and ratio >= 1.5)
            if vpass:
                vel_pass.append((name, minted, round(rate, 4), round(prev_rate, 4), round(ratio, 2)))
            e["previousTotalSupply"] = prev_sup; e["mintedInInterval"] = minted
            e["intervalMinutes"] = INTERVAL; e["currentRatePerMin"] = rate
            e["previousRatePerMin"] = prev_rate; e["velocityRatio"] = ratio
            e["velocityLegPasses"] = vpass
        e["totalSupply"] = new_sup
        note = f"Run 0131 (blok {NEW_BLOCK}, 02:03 WIB): totalSupply {prev_sup}->{new_sup} (+{minted if minted is not None else '?'}), velocity {'LOLOS' if vpass else 'GAGAL'}; "
    for k in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if r.get(k) is not None:
            e[k] = r[k]
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = NEW_BLOCK; e["lastReadWib"] = "2026-11-09 02:03 WIB"
    e["runNote0131_1109"] = note + f"free={e.get('freeClaimed')}/{e.get('FREE_SUPPLY')}; bal_user={e.get('balanceOf_user')}; status {e.get('status')}."
    updated += 1

tc_updated = 0
for name, e in TC.items():
    if not isinstance(e, dict):
        continue
    r = rr["track_c"].get(name)
    if r is None:
        continue
    if r.get("freeMinted") is not None:
        e["freeMinted"] = r["freeMinted"]
    if r.get("totalSupply") is not None:
        e["totalSupply"] = r["totalSupply"]
    e["runNote0131_1109"] = f"Run 0131: freeMinted={e.get('freeMinted')}, totalSupply={e.get('totalSupply')} (blok {NEW_BLOCK})."
    tc_updated += 1

# --- helm.ai SOLD OUT: watchlist-only (gate failed), 555/555 ---
removed = []
if "helm.ai" in C:
    e = C.pop("helm.ai")
    s.setdefault("sellouts", []).append({
        "name": "helm.ai", "address": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
        "totalSupply": 555, "MAX_SUPPLY": 555,
        "evidence": "Sold out terverifikasi on-chain run ini (totalSupply 553 -> 555 = MAX_SUPPLY 555, baca langsung blok 132445220). Status sebelumnya watchlist-only-website-gate-failed-2026-11-07 (gate sudah gagal, user balance 0) - dicatat di run log + sellouts, TIDAK dilaporkan ke chat (preseden HokiKoi/Ninetailix: perubahan terminal item non-lead tanpa laporan).",
        "status_before": e.get("status"), "removed_run": "2026-11-09 run 0131",
        "removed_wib": NOW_STR,
        "reason": "Watchlist-only item sold out -> hapus dari snapshot per aturan; bukan lead/kandidat, tanpa laporan chat."})
    removed.append("helm.ai")

# --- Golden Agents: EARLY LEAD (first-seen, agent-shaped, first mints verified) ---
C["Golden Agents"] = {
    "address": "0x4233C62919CC03168a361C547117c1553C375bfC",
    "status": "early-lead-2026-11-09",
    "name": "Golden Agents", "symbol": "GAGENTS", "kind": "ERC721",
    "totalSupply": 118, "MAX_SUPPLY": 100000, "mintOpen": None,
    "freeClaimed": None, "FREE_SUPPLY": None,
    "firstSeenBlock": 132445024, "scanWindow": "132444237-132445236",
    "scanMints": 6, "scanMinters": 6,
    "lastReadBlock": NEW_BLOCK, "lastReadWib": "2026-11-09 02:03 WIB",
    "xVerified": False, "velocityVerified": False,
    "launchNote": "First mint terverifikasi on-chain blok 132445024 (~02:00 WIB 2026-11-09); walkback Ankr 12.000 blok ke belakang (s.d. blok 132433024, ~00:30 WIB) menemukan 0 mint lebih awal. Muncul sebagai item baru di feed Sourcify recently-verified (hot-leg 0154). Usia peluncuran TERVERIFIKASI <=48 jam (first mint ~02:00 WIB hari ini).",
    "baselineNote": "EARLY lead dilaporkan sekali run 0131 (2026-11-09). Agent-shaped TERKONFIRMASI: AGENT_ID_REGISTRY() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis (baca langsung); Sourcify verified via endpoint singular ?fields=abi (33 fns; endpoint detail plural 404 - quirk endpoint, bukan unverified); mintActive()=1, publicMinted()=117, totalSupply 58 -> 118 dalam ~10 mnt (minting cepat). Free% UNVERIFIED: ABI TIDAK punya free view / quote / price / cost (free_shaped=[]); jalur gratis TIDAK terverifikasi - BUKAN strong lead, BUKAN kandidat. Website UNVERIFIED (pencarian alamat kontrak + nama proyek: hanya Golden Agents Belanda/PyPI, tidak ada situs proyek). X UNVERIFIED. Slot user terbuka menurut baca (mintedBy(user)=0, balanceOf(user)=0) - BUKAN preview-verified (early lead tidak pernah di-preview/di-mint). Owner 0x931b0b8c6dafaef8719cbbb00815ce939a946a07, TIDAK ada di same-owner-discards.",
    "runNote0131_1109": "Run 0131: ditambahkan sebagai early-lead (dilaporkan sekali).",
}

# --- seen file: append scan contracts not yet seen ---
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
sc = json.load(open(f"{BASE}/run-2026-11-09-0131-scan.json"))
added = 0
for c in sc.get("contracts", []):
    a = (c.get("address") or "").lower()
    if a and a not in seen.get("contracts", {}):
        seen.setdefault("contracts", {})[a] = c.get("first_block") or sc.get("from_block")
        added += 1
seen.setdefault("_meta", {})["note_0131"] = (
    "Run 0131: scan FULL 132444237-132445236 (partial=false, 40 Ankr calls, 0 error, 84 NFT + 244 ERC-20-mint); "
    f"{added} first-seen appended ke seen['contracts'] (Golden Agents EARLY lead; AGENT TERMINAL same-owner discard; "
    "GEODES + BONK AGENT Collector Card bukan agent-shaped). Skipped gap 132436705-132444236 (7532 blok, watermark 132436704 milik backfill, TIDAK dimajukan; backfill DINONAKTIFKAN user 2026-11-08).")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)

# --- top-level run note ---
s["last_run"] = "0131"
s["last_run_wib"] = NOW_STR
s["last_run_note"] = (
    f"Run 0131 (01:31 WIB 9 Nov - {NOW_STR}): re-read blok {NEW_BLOCK} (02:03:07 WIB, interval 41,23 mnt vs blok 132439722 01:21:53 WIB): "
    f"{updated} kontrak + {tc_updated} track_c, 0 batch_fail, {degraded} totalSupply=None degraded (nilai lama dipertahankan, bukan nol). "
    f"Velocity strict: {len(vel_pass)} lolos {vel_pass} - Zhenzhu lolos rumus tapi ARTEFAK (totalSupply skala wei, token bridge, bukan mint NFT); "
    "Dragon Agent +49 (1,19/mnt) tapi velocity GAGAL (rate sebelumnya 0, rasio tidak terhitung) - tetap early lead; Alchemister +31 (0,75/mnt, 0,57x) velocity GAGAL. "
    "Scan leg FULL (pre-flight OK 10,4 dtk, head 132445195; window 132444237-132445236, 1000 blok cap, 40 Ankr calls, 0 error, partial=false; 84 NFT + 244 ERC-20-mint; "
    "skipped gap 132436705-132444236 (7532 blok); watermark 132436704 TIDAK dimajukan (milik backfill, backfill nonaktif). "
    "Sourcify feed: 2 baru sejak hot-leg 0154 (0x4233 Golden Agents, 0x0B32) - detail plural 404 keduanya; Golden Agents terverifikasi via endpoint singular ?fields=abi. 5c: 3 baru dicek (0xE3d8, 0x9FD1, 0x4a1e - semua Sourcify 404), 0 hit S1/S2. "
    "Boltbook EN+ZH ~02:03 WIB: Pokechain SOLD OUT dikonfirmasi (sudah dihapus run 0101); Ringgent 'BARU' nicodart.ai = RE-FIND age-excluded (first mint 2026-11-04, run 1531 08 Nov) - bukan lead; Gryphlume recheck (sudah age-excluded run 0101); WAR3 3.291/7.780 free (42,3%, flat vs reread); GLOOP PoW nonce; Forklings 1.103/8.000 (+27, pace melambat - sudah dikenal, website tidak ditemukan); NUMBI 2.899 'free' tak bisa diklaim; KAGENT backing 0, refund kosong (fase gagal); Brinedroid 1.178/2.222 (sudah di snapshot). "
    "EARLY LEAD BARU: Golden Agents 0x4233C629 (AGENT_ID_REGISTRY persis, first mint blok 132445024 ~02:00 WIB, walkback 0 mint dalam 12.000 blok, totalSupply 58->118 cepat, mintActive=1, MAX 100.000) - free% UNVERIFIED (tanpa free view/quote), website UNVERIFIED, X UNVERIFIED - dilaporkan sekali sebagai EARLY, masuk snapshot, TIDAK di-preview/di-mint. "
    "Bukan lead: AGENT TERMINAL (owner 0x11038f4a terkonfirmasi di same-owner-discards, 11 record) - discard; GEODES (free views ada tapi tanpa registry/agent - bukan agent-shaped); BONK AGENT Collector Card (Sourcify unverified, tanpa free shape/registry - bukan agent-shaped). "
    "helm.ai SOLD OUT 555/555 (terverifikasi on-chain run ini) - dihapus dari snapshot, dicatat di sellouts, tanpa laporan chat (gate sudah gagal, non-lead). "
    "NUSA track_c freeMinted 246->249. Binanceai: tetap refund phase (sudah dilaporkan + dihapus dari tracking). Bridge: 116 kontrak, 0 baru. "
    "Web sweep EN+ZH + route 6 (Odaily/PANews 0 penyebutan Agent ID/free mint): 0 kandidat baru (AGENT MAO paused, AgentForge 27 Okt, HOPKIN, daftar 22 proyek 27 Okt; Agent Grove + Nidavellir sudah di snapshot). "
    "0 kandidat, 0 strong lead baru, 1 early lead baru (Golden Agents), 0 auto-mint.")
s["runNote0131_1109"] = s["last_run_note"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print(f"MERGE DONE updated={updated} degraded={degraded} tc={tc_updated} vel_pass={vel_pass} removed={removed} seen_added={added}")
print("contracts now:", len(s["contracts"]), "track_c now:", len(s["track_c"]))
