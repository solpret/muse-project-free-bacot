import json, shutil, copy, datetime

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SNAP = HF + "onchain-snapshot.json"

shutil.copy(SNAP, SNAP + ".bak-20261108-0401")
snap = json.load(open(SNAP))
contracts = snap.setdefault("contracts", {})

# --- index existing addresses to avoid dupes ---
existing_addrs = set()
for e in contracts.values():
    if isinstance(e, dict) and e.get("address"):
        existing_addrs.add(e["address"].lower())
for sec in ("excluded", "track_c"):
    v = snap.get(sec)
    if isinstance(v, dict):
        for e in v.values():
            if isinstance(e, dict):
                for k in ("address", "sale", "token"):
                    if e.get(k):
                        existing_addrs.add(str(e[k]).lower())

# --- merge re-read (446 kontrak), blok 132271860 ---
rr = json.load(open(HF + "run-2026-11-08-0401-reread.json"))
reread = rr.get("reread", {})
updated = 0
for name, r in reread.items():
    e = contracts.get(name)
    if e is None:
        continue
    old_ts = e.get("totalSupply")
    new_ts = r.get("totalSupply")
    if new_ts is not None:
        e["previousTotalSupply"] = old_ts
        e["totalSupply"] = new_ts
        e["mintedInInterval"] = (new_ts - old_ts) if isinstance(old_ts, int) else None
    if r.get("balanceOf_user") is not None:
        e["balanceOf_user"] = r["balanceOf_user"]
    e["lastReadBlock"] = rr.get("block", 132271860)
    e["lastReadWib"] = "2026-11-08 run 0401"
    updated += 1

# --- velocity ---
vel = json.load(open(HF + "run-2026-11-08-0401-velocity.json"))
for row in vel.get("rows", []):
    e = contracts.get(row["name"])
    if e is None:
        continue
    e["currentRatePerMin"] = row.get("ratePerMin")
    e["previousRatePerMin"] = row.get("prevRatePerMin")
    e["velocityRatio"] = row.get("ratioVsPrev")
    e["velocityLegPasses"] = row.get("velocityPasses")
    e["intervalMinutes"] = row.get("intervalMin")
for p in vel.get("passes", []):
    e = contracts.get(p["name"])
    if e is not None:
        e["velocityNote0401"] = (
            "Run 0401: velocity PASS ARTEFAK (bukan promosi): %s, ratio %.2f, "
            "tapi kontrak ERC20-claim (1.000.000 token/klaim, 18 desimal) jadi "
            "mintedInInterval besar = klaim, bukan NFT; freePct None, umur "
            "UNVERIFIED, xVerified false." % (p["name"], p.get("ratioVsPrev") or 0)
        )
# HIVE / Bubblebruin / Zapcourier run notes
notes0401 = {
    "HIVE Agents": "Run 0401 (blok 132271860): totalSupply 1256 flat vs run 0331 (1256), minted interval 0, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
    "Bubblebruin": "Run 0401 (blok 132271860): totalSupply 2019 (prev 2008), minted interval 11, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
    "Zapcourier": "Run 0401 (blok 132271860): totalSupply 715 flat vs run 0331 (715), minted interval 0, velocity GAGAL; balanceOf(user)=1; free views None (degradasi eth_call, nilai snapshot dipertahankan); minted-by-user, bukan kandidat.",
}
for n, txt in notes0401.items():
    if n in contracts:
        contracts[n]["runNote0401"] = txt

# --- track_c: record the 3 terminal movements ---
tc = snap.get("track_c", {})
for name, txt in {
    "Crack": "Run 0401: 3616->3621, minted-by-user, terminal, tidak berubah status.",
    "ORBITA": "Run 0401: 776->782 (x1e24), minted-by-user, terminal, tidak berubah status.",
    "Ninetailix": "Run 0401: 498->507, age-excluded, terminal, tidak berubah status.",
}.items():
    if name in tc and isinstance(tc[name], dict):
        tc[name]["runNote0401"] = txt

# --- new watchlist-only entries (Leg 2 discovery, run 0401; NOT leads, NOT reported) ---
new_entries = {
    "THE WALL": {
        "address": "0xa804bBBe09fa2F5832d11D09329cc4230D1d7899",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "totalSupply": 4656, "MAX_SUPPLY": 20000, "freePctNote": "23,3% (post-reported 4.656/20.000, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (post Boltbook pertama ~03:46 WIB 2026-11-08; MINTS index added_at bukan bukti umur; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (Boltbook grandtheftauto6.ai + agata.ai + board): mintFree() no-arg value 0 lolos dari 8+ sim independen, Agent ID gate (revert 0x0d9ab13f untuk non-agent), pace ~0,5/mnt. Website ADA (thewall-agentic.xyz + /skill.md + X @thewall_agentic) tapi TIDAK mencetak alamat kontrak — gate website GAGAL (verifikasi closeout parent: grep alamat di wall-site.html/-skill.md/-launch.json = 0 hit). Sourcify 404. 23,3% < 25% strong-leg. BUKAN early/strong lead, BUKAN kandidat; watchlist-only sampai umur terverifikasi <=48 jam + gate terpenuhi. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "ZSEAT": {
        "address": "0xa5c09809ada4969fbe1d67a9034ed9633c98ab87",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "totalSupply": 237, "MAX_SUPPLY": 2000, "freePctNote": "11,9% (post-reported 237/2.000, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (Boltbook naowrr.ai + board): mint() no-arg value 0 lolos (multi-RPC sim), gate NoAgentId, pace meluruh ~0,7/mnt. TIDAK ADA website/X (metode A + poster search). Sourcify 404. Klaim ZENA BERBAYAR (fee 0,00028 BNB) + pair 0x0 — bukan track-B gratis. BUKAN early/strong lead, BUKAN kandidat; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "WRAITH": {
        "address": "0x4a318eb842c8c95876e895258bc70d0bee767def",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "19,5% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify 404. TIDAK ADA website (MINTS index website None). BUKAN early/strong lead; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "ElonGai": {
        "address": "0x59F93bBBb14cE948Ee16b261a05Ad4A77711ECf1",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "73,0% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify 404. TIDAK ADA website. % tinggi tapi umur UNVERIFIED + tanpa website = BUKAN lead/kandidat; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "Agent Chickens": {
        "address": "0x1F0D3ffeEBdDAf2F49ced65A9a92864332e55Ee5",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "38,4% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify 404. TIDAK ADA website. BUKAN early/strong lead; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "Lucky Agents": {
        "address": "0x0B51Ef6827ab0bc875673d367Dbb78eE1B6Df1Ce",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "29,3% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy; treasury() ada. Sourcify 404. TIDAK ADA website. BUKAN early/strong lead; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "BNAgentFile": {
        "address": "0x6B1719EEFcb271778c40f0CFd71c8651Adbde5d1",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "totalSupply": 5956,
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify exact_match + registry literal — agent-shaped (terkuat di batch ini). TIDAK ADA website. BUKAN early lead (first mint tidak terverifikasi di run ini) dan BUKAN strong lead (umur UNVERIFIED); watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "PilotBoarding": {
        "address": "0xc267E47F1Ba3B6B2BCbA58f16298c92CaCAF7952",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "totalSupply": 24395,
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify match tapi TANPA registry/agent fn — agent-shape tidak ditegakkan. TIDAK ADA website. BUKAN early/strong lead; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "ALIBABA": {
        "address": "0xA2F2ffCA66D324af5ED58e5c98c9D6f544b13303",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "56,8% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy (+receipt). Sourcify 404. TIDAK ADA website. % >50% tapi umur UNVERIFIED + tanpa website = BUKAN lead/kandidat; watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "BHPASS": {
        "address": "0xCd4Af5a9eDE5ef6f5138028AdC9C152a1Acb80ed",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "totalSupply": 8469,
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy (+receipt). Sourcify exact_match, isAgent. TIDAK ADA website. BUKAN early lead (first mint tidak terverifikasi di run ini); watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "PixelSentinels": {
        "address": "0x4e4e43f84E2E80716d03153F3c675e8E715Fa698",
        "status": "watchlist-only-age-unverified-2026-11-08",
        "freePctNote": "36,2% (post-reported, belum verifikasi independen job ini)",
        "launchNote": "Launch time UNVERIFIED (batch vibibiy.ai 4-6 jam; first mint on-chain belum diverifikasi run ini).",
        "baselineNote": "FLAGGED run 0401 (author page vibibiy.ai): free lane sim value 0 oleh vibibiy. Sourcify exact_match, agentId. TIDAK ADA website. BUKAN early lead (first mint tidak terverifikasi di run ini); watchlist-only. Tidak dilaporkan.",
        "xVerified": False, "velocityVerified": False,
    },
    "GLOOP": {
        "address": "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE",
        "status": "upcoming-prelaunch-2026-11-08",
        "launchNote": "PRE-LAUNCH: buka 2026-11-08 12:00 UTC (19:00 WIB), 3.333 free, site gloopagent.xyz (per post Boltbook ghoffar26.ai).",
        "baselineNote": "PRE-LAUNCH run 0401 — upcoming watchlist item saja, BUKAN kandidat, TIDAK PERNAH di-preview/mint sebelum launch + verifikasi on-chain. FLAG: mint = PoW nonce race — perlu keputusan scope parent/user sebelum buka 19:00 WIB. Tidak dilaporkan sebagai kandidat.",
        "xVerified": False, "velocityVerified": False,
    },
}
added = []
skipped = []
for name, entry in new_entries.items():
    if entry["address"].lower() in existing_addrs:
        skipped.append(name)
        continue
    entry["firstSeenRun"] = "2026-11-08 run 0401"
    contracts[name] = entry
    existing_addrs.add(entry["address"].lower())
    added.append(name)

snap["last_run_wib"] = "2026-11-08T04:01:00+07:00"
snap["note_0401_scan"] = ("Run 0401 SUKSES window 132270864-132271863 (1000 blok, cap), 132 ERC721 + 3 ERC1155 + "
    "214 ERC-20 mint, 457 NFT mints, 40 Ankr calls, 0 error, SCAN_EXIT=0, ~16,5 mnt. 0 first-seen sejati. "
    "5c: 28 ERC-20 mint_count>=10, 25 sudah dicek, 3 baru dicek (0xe1822683974d937dF74A01c366D804cf9Ee7d273, "
    "0x604aD895C8eb58f19cFe15c5780665Fe853f3441, 0x6Fb61dEe19845FA87b7B1148B0fF6A4f5537D0e0 — semua Sourcify "
    "not_verified, 0 hit S1/S2). Skipped gap 132268176-132270863 (2.688 blok) untuk backfill; watermark TIDAK "
    "dimajukan (milik backfill). Preflight PASS 3,8 dtk.")
snap["note_0401_reread"] = ("Run 0401 re-read 446/451 kontrak + 70 track_c, blok 132271860, 716 dtk. Free views None di "
    "semua 446 kontrak (degradasi revert, counter snapshot dipertahankan). 105 kontrak tanpa totalSupply/totalMinted "
    "(sama 0301/0331). Velocity: 1 pass ARTEFAK MeowBark (ERC20-claim, bukan NFT), 0 promosi. Sold out 35 set IDENTIK "
    "0331. Age sweep 0 removal (49 kept, 384 launch-unverified). Track-B binanceai TIDAK BERUBAH (launched 0, failed 1, "
    "isRefundPhase 1, totalShares 3110, tokenClaimed(user) 0, reserves 0/0). Grove freeOpen 0. Track_c: Crack 3621, "
    "ORBITA 782, Ninetailix 507 — semua terminal.")
snap["note_0401_discovery"] = ("Run 0401 Boltbook.fun EN 44.682 B / ZH 45.216 B. Masuk: THE WALL, GANG CRYPTO, AlphaPulse, "
    "HAMMER, ZSEAT, Gloop, Agent Goats/HELM/Sable, AgentPad Pass. Keluar: NULLRAID, BYTE, Hash21, Vorn, Cinder, ORBITA, "
    "musegod sweep, HOPKIN/Alchemister. Route 3: 0 baru. Sourcify 5a: 20 kontrak, 0 S1/S2/agent-shape. Route 6: 0 baru. "
    "Bridge TIDAK BERUBAH (sha256 b3f349f1..., 115 kontrak, 7 discarded, 0 promosi). 12 entri watchlist-only baru "
    "(THE WALL, ZSEAT, batch vibibiy 9 kontrak, GLOOP pre-launch) — tidak dilaporkan, bukan lead/kandidat. GANG CRYPTO "
    "paid-only, AlphaPulse presale berbayar — bukan lead.")

json.dump(snap, open(SNAP, "w"), indent=1)
print("updated reread:", updated)
print("added:", added)
print("skipped (already present):", skipped)
print("contracts now:", len(snap["contracts"]))
print("excluded:", len(snap.get("excluded", {})))
