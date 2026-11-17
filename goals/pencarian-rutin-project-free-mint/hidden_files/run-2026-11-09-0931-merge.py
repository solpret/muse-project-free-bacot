#!/usr/bin/env python3
"""Merge run 2026-11-09 0931 WIB (free-mint-search) into onchain-snapshot.json.
Reads run-2026-11-09-0931-reread.json + velocity + special + discovery.
Rules: None = read artefact, NEVER overwrites an old value. Only non-None
numeric fields are updated. Adds LeadLoop watchlist-unverified entry.
Writes backup onchain-snapshot.json.bak-run-2026-11-09-0931 first.
"""
import json, shutil, copy

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{HF}/onchain-snapshot.json", f"{HF}/onchain-snapshot.json.bak-run-2026-11-09-0931")
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-09-0931-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-09-0931-velocity.json"))
special = json.load(open(f"{HF}/run-2026-11-09-0931-special.json"))
disc = json.load(open(f"{HF}/run-2026-11-09-0931-discovery.json"))

READ_BLOCK = 132510544
FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
          "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "balanceOf_user", "freeClaimed_user"]

updated, not_in_snap, skipped_none = 0, [], 0
for name, vals in reread.get("reread", {}).items():
    ent = snap["contracts"].get(name)
    if ent is None:
        not_in_snap.append(name)
        continue
    for f in FIELDS:
        v = vals.get(f)
        if v is not None:
            ent[f] = v
        else:
            skipped_none += 1
    ent["lastReadBlock"] = READ_BLOCK
    ent["lastReadWib"] = "2026-11-09 10:2x WIB"
    updated += 1

# velocity-pass contracts: compact per-contract note
for p in vel.get("velocity_pass", []):
    ent = snap["contracts"].get(p["name"])
    if ent is not None:
        ent["runNote0931_1109"] = (
            f"Run 0931 (blok {READ_BLOCK}): velocity LOLOS (+{p['minted']}, "
            f"rasio {p['ratio']}x) TAPI TIDAK promosi: "
            f"{'token-scale (artefak)' if p['minted'] > 10**15 else 'free% unverified / discard / minted-by-user / tanpa website (lihat velocity.json)'}; "
            "bukan kandidat.")
        ent["previousTotalSupply"] = ent.get("totalSupply")
# HIVE/Bubblebruin/Zapcourier/Cryonyx/Cathodex/Kirinova: short no-change note
for n in ["HIVE Agents", "Bubblebruin", "Zapcourier", "Cryonyx", "Cathodex", "Kirinova"]:
    ent = snap["contracts"].get(n)
    if ent is not None and "runNote0931_1109" not in ent:
        ent["runNote0931_1109"] = (
            f"Run 0931 (blok {READ_BLOCK}): totalSupply {ent.get('totalSupply')} "
            f"(prev {ent.get('previousTotalSupply')}), minted interval 0, velocity GAGAL; "
            f"free={ent.get('freeClaimed')}/{ent.get('FREE_SUPPLY')}; bal_user={ent.get('balanceOf_user', ent.get('userBalance'))}; "
            "status minted-by-user, bukan kandidat.")

# track_c numeric updates from reread track_c (match by key name)
tc_updated = 0
for name, vals in reread.get("track_c", {}).items():
    ent = snap.get("track_c", {}).get(name)
    if ent is None or not isinstance(ent, dict):
        continue
    for f in ["totalSupply", "totalMinted", "freeMinted", "freeSharesRemaining",
              "balanceOf_user", "freeClaimed_user"]:
        v = vals.get(f)
        if v is not None:
            ent[f] = v
    tc_updated += 1

# YAMA from special (authoritative sale reads)
y = snap.get("track_c", {}).get("YAMA")
if isinstance(y, dict):
    y["totalShares"] = special["yama"]["totalShares"]
    y["totalFreeShares"] = special["yama"]["totalFreeShares"]
    y["freeRemaining"] = special["yama"]["MAX_SHARES"] - special["yama"]["totalFreeShares"]
    y["userSlot"] = {"freeUsed": bool(special["yama"]["freeUsed_user"]),
                     "quotaOf": special["yama"]["quotaOf_user"],
                     "quoteFreeShares": special["yama"]["quote_user_1"]["freeShares"],
                     "quoteCostBnb": special["yama"]["quote_user_1"]["costBnb"],
                     "sharesOf": special["yama"]["sharesOf_user"],
                     "slot_open_free": True}
    y["runNote0931_1109"] = ("Run 0931 (blok 132510556): totalShares 413->428 (+15), "
        "free 428/100.000, slot user masih terbuka & gratis (quote 1 share = 0 BNB, quota 10). "
        "Website gate TETAP FAILED (discovery 0931, metode M+N) - tidak di-preview/dieksekusi, tidak dilaporkan ulang.")
    y["lastReadBlock"] = 132510556

# NUSA: free lane still minting (freeMinted 289) - contradicts b/alpha post claim "free lane mati"
nusa = snap.get("track_c", {}).get("NUSA")
if isinstance(nusa, dict):
    nusa["runNote0931_1109"] = ("Run 0931: freeMinted 289 (hot-leg 0944: 287) - free lane MASIH minting on-chain; "
        "klaim post b/alpha 'free lane NUSA mati' TIDAK terkonfirmasi on-chain run ini. Tidak ada perubahan status.")

# LeadLoop: new watchlist-only entry (all legs unverified)
ll = disc.get("leadloop", {})
snap["contracts"]["LeadLoop"] = {
    "address": ll.get("contract", "0xe887584746a1375d732854b3b67460a2a73ae0a9"),
    "status": "watchlist-unverified-2026-11-09",
    "name": "LeadLoop",
    "source": "Boltbook author page 2778.ai (discovery run 0931)",
    "sourceNote": ll.get("source", ""),
    "sourcify": "UNVERIFIED (Sourcify v2 contract endpoint HTTP 404)",
    "totalSupply": (ll.get("reads") or {}).get("totalSupply"),
    "codeBytes": (ll.get("reads") or {}).get("code_bytes"),
    "freePct": "UNVERIFIED",
    "launchAge": "UNVERIFIED",
    "xVerified": False,
    "velocityVerified": False,
    "websiteVerified": False,
    "baselineNote": "Watchlist-only (BUKAN lead): shape, free pool, user slot, launch age semua UNVERIFIED (tanpa ABI). totalSupply 10000 terbaca; cap unknown, mungkin sudah sold out. Perlu deep-dive sebelum promosi apa pun.",
    "lastReadBlock": ll.get("onchain_block"),
    "lastReadWib": "2026-11-09 10:1x WIB",
}

snap["runNote0931_1109"] = (
    "Run 0931: DIAM (0 kandidat, 0 strong lead, 0 early lead, 0 track-C lead baru). "
    f"Re-read lengkap 591/591 kontrak + 77/77 track_c (blok {READ_BLOCK}); velocity lolos 5 "
    "(2 token-scale artefak + Wisps/SHACHO CLUB/AGENT DOSSIER - ketiganya gugur: discard/minted-by-user/free% unverified/tanpa website). "
    "Tidak ada sellout baru, slot/saldo user tidak berubah. Scan partial 800/1000 blok, 1 true first-seen (0x550a5464, bukan agent-shaped). "
    "Discovery nihil; YAMA gate tetap FAILED; bridge tidak berubah; binanceai tetap refund-phase.")
snap["runNote0931_1109_scan"] = (
    "Run 0931 scan: pre-flight OK 5,2 dtk. Window 132507584-132508583, ter-cover 132507584-132508383 (16/20 chunk; "
    "chunk 132508384-132508433 Ankr 'Remote end closed connection' -> break by design; gap 200 blok tidak ter-scan, tidak di-retry). "
    "117 NFT raw + 263 ERC-20 mint. True first-seen 1: 0x550a5464E3C63ae5aed1c59eb47431509b6d7c40 (9 mint/9 minter, first block 132507592) - BUKAN agent-shaped. "
    "5c: 45 kandidat >=10, 3 baru dicek, 0 S1/S2. Watermark TIDAK dimajukan (milik backfill). "
    "KOREKSI DEDUPE: triase 0931 awal melaporkan 15 first-seen, 14 di antaranya ternyata sudah ada di seen['contracts'] (nested, 11.603 entri) - "
    "skrip triase hanya membaca top-level keys. Verifikasi parent: 5 dari 6 'first-seen' run 0901 juga sudah ada di nested seen sebelum run 0901 "
    "(blok first-seen 131105242-132435022) - cacat dedupe yang sama; tidak ada dampak laporan karena kelimanya bukan agent-shaped dan tidak pernah dilaporkan sebagai lead. "
    "Hanya 0xCFB72b0E (Stampooor) yang genuine baru di 0901. Skrip triase 0931 SUDAH diperbaiki (union top-level + nested + known_older_leads, lowercase) - run berikut WAJIB menyalin skrip triase 0931, bukan 0901.")
snap["runNote0931_1109_discovery"] = (
    "Run 0931 discovery: NIHIL. Boltbook ZH segar (~10:00 WIB, 45.232 byte); EN gagal 2x via curl (0 byte, crawl basi dipakai sekunder). "
    "PAWG/HELM sold out; BMT Agents free pool habis; First-Dollar Grove free lane mati; Fleet sold out; Pathwyrm age-excluded. "
    "LeadLoop 0xe8875847 baru vs snapshot tapi semua kaki UNVERIFIED -> watchlist-only (masuk snapshot). "
    "Sourcify 20 entri, 13 baru, semua S1=S2=false. Odaily/PANews 0 hit. Bridge mtime 2026-11-08 18:21 UTC tidak berubah.")
snap["runNote0931_1109_binanceai"] = (
    "Run 0931 (blok 132510556): binanceai.fun TIDAK BERUBAH - launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0, saldo TOKEN user=0. Sudah dilaporkan sekali; tidak dilaporkan ulang.")
snap["runNote0931_1109_age_exclusions"] = (
    "Run 0931: TIDAK ADA age-exclusion baru. Alchemister-0xCafEEDDF sudah di-exclude di merge 0901; konfirmasi segar totalSupply 6295/15000, "
    "mintOpen=1, masih belum sold out sesudah deadline 09:49:19 WIB - konsisten, tanpa tindakan baru. "
    "Alchemister-0x69037Db8 (kontrak lain, early-lead, +5 ke 3282, free% unverified): firstMint TIDAK tercatat - launch age UNVERIFIED, "
    "TIDAK divonis age-excluded run ini; diserahkan ke age-sweep untuk verifikasi first-mint.")
snap["last_run_wib"] = "2026-11-09 10:2x WIB"
snap["last_run_note"] = "Run 0931 DIAM: 0 kandidat/lead baru; re-read lengkap; scan partial; discovery nihil; YAMA gate tetap failed; binanceai tetap refund."

json.dump(snap, open(f"{HF}/onchain-snapshot.json", "w"), indent=1)
print(f"contracts updated: {updated}; not in snapshot: {not_in_snap}; track_c updated: {tc_updated}")
print(f"velocity_pass: {[p['name'] for p in vel.get('velocity_pass', [])]}")
print(f"sellout_new: {vel.get('sellout_new')}; slot_changes: {vel.get('slot_changes')}; balance_changes: {vel.get('balance_changes')}")
print("LeadLoop added; YAMA updated to 428 shares; snapshot written.")
