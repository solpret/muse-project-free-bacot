#!/usr/bin/env python3
"""Merge run 2026-11-08 19:31 WIB into onchain-snapshot.json + seen + scan state.
Route-1 reread updates + velocity; ZGS fresh reads; track-C watchlist updates
(MALTA totalFreeShares, NUSA freeMinted); factory-wave 5 siblings confirmed
same-owner-discarded (promotion blocked, run 1431 precedent); HELIX + Pokechain
early-lead-pending-report entries; scan triage + 5c checked update.
Never touches pending_claims or binanceai. Watermark advanced only because
scan partial=false."""
import json, sys, time, datetime, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN_WIB = "2026-11-08 19:31 WIB"

def load(p):
    with open(p) as f: return json.load(f)
def save(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f: json.dump(obj, f, indent=1)
    os.replace(tmp, p)

snap = load(BASE + "/onchain-snapshot.json")
rr = load(BASE + "/run-2026-11-08-1931-reread.json")
try:
    scan = load(BASE + "/onchain-scan-2026-11-08-1931.json")
except Exception as e:
    scan = {"contracts": [], "erc20_mint_contracts": 0, "partial": True, "errors": [str(e)]}
zgs = load(BASE + "/run-2026-11-08-1931-trackc-zgs-binanceai.json")
seen = load(BASE + "/onchain-scan-seen.json")
contracts = snap.setdefault("contracts", {})
track_c = snap.setdefault("track_c", {})

# ---- Route 1: reread updates + velocity ----
changed, degraded, vel_pass = [], 0, []
PREV_BLOCK = 132389206  # run 1901 read block
INTERVAL_MIN = (rr.get("block", 132395502) - PREV_BLOCK) * 0.45 / 60.0
for name, d in rr.get("reread", {}).items():
    old = contracts.get(name)
    if old is None:
        continue
    nts = d.get("totalSupply")
    if nts is None:
        degraded += 1
        continue
    ots = old.get("totalSupply")
    if ots is None:
        old["totalSupply"] = nts
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        continue
    if nts != ots:
        minted = nts - ots
        old_rate = old.get("currentRatePerMin")
        base = old_rate if old_rate is not None else old.get("previousRatePerMin")
        rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
        ratio = (rate / base) if base else None
        passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
        old["previousTotalSupply"] = ots
        old["totalSupply"] = nts
        old["mintedInInterval"] = minted
        old["intervalMinutes"] = round(INTERVAL_MIN, 1)
        if old_rate is not None:
            old["previousRatePerMin"] = old_rate
        old["currentRatePerMin"] = round(rate, 4)
        old["velocityRatio"] = round(ratio, 2) if ratio is not None else None
        old["velocityLegPasses"] = passes
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("freeMinted") is not None:
            old["freeMinted"] = d["freeMinted"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]
        changed.append((name, ots, nts, minted, passes, old.get("status")))
        if passes:
            vel_pass.append((name, minted, round(ratio, 2)))
    else:
        old["lastReadBlock"] = rr.get("block")
        old["lastReadWib"] = RUN_WIB
        old["mintedInInterval"] = 0
        old["currentRatePerMin"] = 0.0
        old["velocityLegPasses"] = False
        if d.get("freeClaimed") is not None:
            old["freeClaimed"] = d["freeClaimed"]
        if d.get("freeMinted") is not None:
            old["freeMinted"] = d["freeMinted"]
        if d.get("balanceOf_user") is not None:
            old["balanceOf_user"] = d["balanceOf_user"]

# ---- Track C reread updates (freeMinted from route-1 TC views) ----
tc_changed = []
for name, d in rr.get("track_c", {}).items():
    old = track_c.get(name)
    if isinstance(old, dict) and d.get("freeMinted") is not None:
        if old.get("freeMinted") != d["freeMinted"]:
            tc_changed.append((name, old.get("freeMinted"), d["freeMinted"]))
            old["freeMinted"] = d["freeMinted"]
            old["lastReadWib"] = RUN_WIB
            old["lastReadBlock"] = rr.get("block")

# ---- ZGS fresh reads ----
z = zgs.get("zgs", {}).get("Zorrie", {})
if "Zorrie" in contracts and z.get("totalMinted") is not None:
    contracts["Zorrie"]["totalMinted"] = z["totalMinted"]
    contracts["Zorrie"]["freeMintedPerWallet_user"] = z.get("freeMintedPerWallet_user")
    contracts["Zorrie"]["userBalance"] = z.get("balanceOf_user")
    contracts["Zorrie"]["lastReadBlock"] = rr.get("block")
    contracts["Zorrie"]["lastReadWib"] = RUN_WIB
    contracts["Zorrie"]["runNote1931_1108"] = ("Run 1931: totalMinted 6->8/5000 (0,16%), slot user terbuka "
        "(freeMintedPerWallet=0, balanceOf=0). JAUH di bawah 25% -> BUKAN strong lead, tanpa promosi.")
g = zgs.get("zgs", {}).get("Gloop", {})
if "Gloop" in contracts and g.get("totalMinted") is not None:
    contracts["Gloop"]["totalMinted"] = g["totalMinted"]
    contracts["Gloop"]["userBalance"] = g.get("balanceOf_user")
    contracts["Gloop"]["hasMinted_user"] = g.get("hasMinted_user")
    contracts["Gloop"]["lastReadBlock"] = rr.get("block")
    contracts["Gloop"]["lastReadWib"] = RUN_WIB
    contracts["Gloop"]["runNote1931_1108"] = ("Run 1931: totalMinted 38->43/3333, mintOpen 1, MINT_START 1794139200 "
        "(2026-11-08 19:00 WIB, umur terverifikasi <=48 jam). free% TETAP UNVERIFIED (ABI tanpa free view) -> "
        "BUKAN strong lead (butuh >=25% free terverifikasi), tanpa promosi.")
s = zgs.get("zgs", {}).get("Skunk Hollow", {})
if "Skunk Hollow" in contracts and s.get("totalSkunksMinted") is not None:
    contracts["Skunk Hollow"]["totalSkunksMinted"] = s["totalSkunksMinted"]
    contracts["Skunk Hollow"]["freeSkunksRemaining"] = s.get("freeSkunksRemaining")
    contracts["Skunk Hollow"]["freeSkunksClaimed"] = s.get("freeSkunksClaimed")
    contracts["Skunk Hollow"]["freeWindowOpen"] = s.get("freeWindowOpen")
    contracts["Skunk Hollow"]["freeClaimedBy_user"] = s.get("freeClaimedBy_user")
    contracts["Skunk Hollow"]["userBalance"] = s.get("balanceOf_user")
    contracts["Skunk Hollow"]["freePctVerified"] = round(100.0 * s["totalSkunksMinted"] / 2500, 2)
    contracts["Skunk Hollow"]["lastReadBlock"] = rr.get("block")
    contracts["Skunk Hollow"]["lastReadWib"] = RUN_WIB
    contracts["Skunk Hollow"]["runNote1931_1108"] = ("Run 1931: totalSkunksMinted 117->208/2500 (8,3% <25%), "
        "freeWindowOpen 1, slot user terbuka (freeClaimedBy=0). BUKAN strong lead, tanpa promosi.")

# ---- Track-C watchlist fresh updates (from trackc-zgs read) ----
tw = zgs.get("track_c_watchlist", {})
malta = track_c.get("AGENT MALTA")
if isinstance(malta, dict):
    m = tw.get("AGENT MALTA", {})
    if m.get("totalFreeShares") is not None:
        malta["totalFreeShares"] = m["totalFreeShares"]
        malta["totalShares"] = m.get("totalShares")
        malta["freeMinted"] = m["totalFreeShares"]
    malta["totalSupply"] = m.get("totalSupply")
    malta["lastReadBlock"] = rr.get("block")
    malta["lastReadWib"] = RUN_WIB
    malta["runNote1931"] = ("Run 1931: totalFreeShares 426->434, quote(user,1)=(1 free, 0 cost), freeUsed(user)=0, "
        "slot user tetap terbuka. GATE TETAP GAGAL (cek situs = kaki parent, bukan kaki on-chain ini); "
        "TIDAK di-preview/di-mint, TIDAK dilaporkan ulang.")
nusa = track_c.get("NUSA")
if isinstance(nusa, dict):
    n = tw.get("NUSA", {})
    if n.get("freeMinted") is not None:
        nusa["freeMinted"] = n["freeMinted"]
    nusa["lastReadBlock"] = rr.get("block")
    nusa["lastReadWib"] = RUN_WIB
    nusa["runNote1931"] = ("Run 1931: freeMinted 120->142/560 MAX_FREE = 25,4% (melewati 25%); quote(user,1) REVERT "
        "di pembacaan segar ini (sebelumnya freeAvailable=true, freeClaimed(user)=false) -> slot user TIDAK "
        "terverifikasi segar; gate TETAP FAILED (hot-leg 17:04, methods A-H). Tetap lead gate-blocked, "
        "TIDAK di-preview/di-mint, TIDAK dilaporkan ulang sebagai lead baru.")

# ---- Factory-wave 5 siblings: owner re-verified in same-owner-discards (run 1431) ----
SIBS = ["Keyforge", "Pixpad", "Coralume", "Candlewick", "Compasso"]
for name in SIBS:
    e = contracts.get(name)
    if e is None:
        continue
    e["owner"] = "0x53043412c4f2436f68e56bb9638ebebb099fb3c1"
    e["ownerInDiscards"] = True
    e["status"] = "same-owner-discarded-2026-11-08"
    e["discardNote"] = ("Owner 0x5304... = factory wave 8 kontrak template sama (FREE_SUPPLY 7000/MAX_SUPPLY 7777), "
        "discarded run 1431 15:30 WIB (preseden Gourdwick). Run 1931 verifikasi ulang: owner() cocok, "
        "3 kaki strong lead TERPENUHI on-chain (umur terverifikasi <=48 jam, free% 37,8-42,9% >=25%, slot user "
        "terbuka freeLeft=3/quote=0/freeUsed=0) TAPI promosi DIBATALKAN oleh aturan same-owner-discarded: "
        "TIDAK PERNAH dipromosikan/dilaporkan sebagai lead. Hanya run log + status ini.")
    if e.get("freeClaimed") is not None and e.get("FREE_SUPPLY"):
        e["freePctVerified"] = round(100.0 * e["freeClaimed"] / e["FREE_SUPPLY"], 2)
    e["lastReadBlock"] = rr.get("block")
    e["lastReadWib"] = RUN_WIB

# ---- HELIX + Pokechain: early-lead-pending-report ----
triage = load(BASE + "/run-2026-11-08-1931-scan-triage.json")
triage2 = load(BASE + "/run-2026-11-08-1931-scan-triage2.json")
hx = triage.get("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665", {})
hx2 = triage2.get("HELIX", {})
contracts["HELIX"] = {
    "address": "0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665",
    "name": "HELIX", "symbol": "HLX", "kind": "ERC721",
    "status": "early-lead-pending-report",
    "totalMinted": hx.get("totalMinted"), "totalSupply": hx.get("totalSupply"),
    "MAX_SUPPLY": 4444, "mintActive": hx2.get("mintActive"),
    "publicRemaining": hx2.get("publicRemaining"),
    "price": hx2.get("price"), "totalPaidMinted": hx2.get("totalPaidMinted"),
    "firstSeenBlock": 132394604, "firstMintWib": "2026-11-08 19:43:23 WIB",
    "scanMints": 20, "scanMinters": 20,
    "owner": "0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3",
    "ownerInDiscards": "EXCEPTION (file discards: owner ini TIDAK dibuang aturan same-owner; early lead run 04:31 tetap dilaporkan)",
    "agentRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesInCode": True, "sourcify": "exact_match",
    "website": None, "websiteVerified": False,
    "xVerified": False,
    "freePctVerified": None,
    "freePctNote": ("UNVERIFIED: tanpa FREE_SUPPLY/freeClaimed/freeMinted view; freeMint() no-arg payable ada, "
        "freeUsed(user)=0, hasAgentId(user)=1, mintActive=1, price(paid)=0,001 BNB, totalPaidMinted=0. "
        "Pool gratis tidak terukur -> BUKAN strong lead."),
    "userBalance": 0, "freeUsed_user": 0, "hasAgentId_user": 1,
    "requireAgentId": 0,
    "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
    "baselineNote": ("Scan run 1931 first-seen (window 132394599-132395598, 20 mint/20 minter); triase: Sourcify "
        "exact_match, agentRegistry() = registry persis, freeMint() + freeUsed + hasAgentId; first mint blok "
        "132394604 (2026-11-08 19:43:23 WIB, umur terverifikasi <=48 jam). contractURI base64 JSON TANPA "
        "external_link -> website UNVERIFIED (method H). EARLY lead PENDING REPORT (parent laporkan, lalu flip status). "
        "TIDAK di-preview/di-mint."),
}
pk = triage.get("0x4EF929aF00cB93993c3D01834C4DA79200d31e32", {})
pk2 = triage2.get("Pokechain", {})
contracts["Pokechain"] = {
    "address": "0x4EF929aF00cB93993c3D01834C4DA79200d31e32",
    "name": "Pokechain", "symbol": "POKECHAIN", "kind": "ERC721",
    "status": "early-lead-pending-report",
    "totalMinted": pk2.get("totalMinted"), "MAX_SUPPLY": 15555,
    "firstSeenBlock": 132395479, "firstMintWib": "2026-11-08 19:49:56 WIB",
    "scanMints": 12, "scanMinters": 12,
    "owner": "0xf379a6070eb04e3e9d8ea28f11f04bd8ff452b59",
    "ownerInDiscards": False,
    "registryBytesInCode": True, "sourcify": "not_verified (404)",
    "website": "https://pokechain.trade",
    "websiteGate": "UNVERIFIED (klaim di contractURI/tokenURI metadata; situs BELUM diverifikasi mencetak kontrak persis - kaki parent)",
    "xVerified": False,
    "xClaimed": "https://x.com/PokechainTrade (klaim metadata, belum diverifikasi)",
    "freePctVerified": None,
    "freePctNote": ("UNVERIFIED: Sourcify 404 (tanpa ABI); bytecode ADA registry bytes TAPI TIDAK ADA selector "
        "freeMint/mintFree/claimFree (hanya mint(uint256)); tanpa free view. Bentuk gratis TIDAK TERBUKTI - "
        "early lead BORDERLINE (agent-shaped via registry bytes saja, diskriminator lemah 81%)."),
    "userBalance": 0, "mintedBy_user": 0,
    "lastReadBlock": rr.get("block"), "lastReadWib": RUN_WIB,
    "baselineNote": ("Scan run 1931 first-seen (window 132394599-132395598, 12 mint/12 minter); triase: Sourcify 404, "
        "registry bytes ADA di bytecode, mint(uint256) ADA, free-mint selector TIDAK ADA; contractURI/tokenURI "
        "mengklaim 'Minted by AI agents holding a .ai Agent ID', website pokechain.trade, X @PokechainTrade. "
        "First mint blok 132395479 (2026-11-08 19:49:56 WIB, umur terverifikasi <=48 jam). EARLY lead PENDING "
        "REPORT - parent putuskan (borderline: registry-bytes-only). TIDAK di-preview/di-mint."),
}

# ---- Scan triage: newly-seen classification ----
# NOTE: HELIX/Pokechain were just added to contracts above; exclude them from
# snap_addrs here so they still count as new_seen and get recorded in seen.
seen_contracts = seen.setdefault("contracts", {})
snap_addrs = {(v.get("address") or "").lower() for v in contracts.values() if isinstance(v, dict)}
snap_addrs -= {"0x5e0ca9e1ecb5a6205e0b0d7a1fbe16983d2e8665",
               "0x4ef929af00cb93993c3d01834c4da79200d31e32"}
new_seen, agent_shaped_new, historic = [], [], 0
for c in scan.get("contracts", []):
    addr = (c.get("address") or "").lower()
    if not addr:
        continue
    if addr in seen_contracts or addr in snap_addrs:
        historic += 1
        continue
    new_seen.append(c)
    seen_contracts[addr] = {"first_seen_block": c.get("first_block"),
                            "first_seen_run": "2026-11-08-1931",
                            "mint_count_window": c.get("mint_count"),
                            "distinct_minters_window": c.get("distinct_minters")}
    if c.get("registry_bytes_hit"):
        agent_shaped_new.append(c)
save(BASE + "/onchain-scan-seen.json", seen)

# ---- Scan state / watermark ----
state = load(BASE + "/onchain-scan-state.json")
partial = bool(scan.get("partial", True))
state["last_scan_partial"] = partial
state["last_scan_wib"] = "2026-11-08 19:31-20:xx WIB"
state["last_scan_window_from"] = scan.get("from_block")
state["last_scan_window_to"] = scan.get("to_block")
state["last_scan_ankr_calls"] = scan.get("ankr_calls")
state["last_scan_errors"] = len(scan.get("errors", []))
state["last_scan_nft"] = len(scan.get("contracts", []))
state["last_scan_erc20_mint"] = scan.get("erc20_mint_contracts")
state["last_scan_skipped_gap"] = "132389446-132394598 (5153 blok; window > cap 1000, scan hanya 1000 blok terbaru; backfill OFF)"
if not partial:
    state["last_scanned_block"] = scan.get("to_block")
    state["note"] = "Scan run 1931 OK (full); watermark advanced."
else:
    state["last_scan_partial_note"] = ("Scan run 1931 PARTIAL: partial=%s; watermark NOT advanced (tetap %s); "
                                       "run berikut retry window yang sama (cap 1000)." % (scan.get("partial"), state.get("last_scanned_block")))
save(BASE + "/onchain-scan-state.json", state)

# ---- 5c checked update ----
added5c = 0
try:
    five_c = load(BASE + "/run-2026-11-08-1931-5c.json")
    checked = load(BASE + "/track-c-scan-checked.json")
    checked_list = checked.get("checked", []) if isinstance(checked, dict) else checked
    checked_lower = {str(x).lower() for x in checked_list}
    top_keys = {str(k).lower() for k in checked.keys()} if isinstance(checked, dict) else set()
    for a in five_c.keys():
        if a.lower() not in checked_lower and a.lower() not in top_keys:
            checked_list.append(a)
            checked_lower.add(a.lower())
            added5c += 1
    if isinstance(checked, dict):
        checked["checked"] = checked_list
        save(BASE + "/track-c-scan-checked.json", checked)
    else:
        save(BASE + "/track-c-scan-checked.json", checked_list)
except Exception as e:
    five_c = {"error": str(e)}

# ---- Run notes ----
snap["last_run_wib"] = RUN_WIB
snap["last_run"] = "free-mint-search 2026-11-08 1931 WIB"
snap["runNote1931_1108"] = (
    "Run 1931 (19:31 WIB): "
    f"route-1 re-read blok {rr.get('block')}: 539 kontrak + 71 track_c; perubahan supply {len(changed)}, degraded(None) {degraded}; "
    f"velocity LOLOS {len(vel_pass)} ({', '.join('%s +%d %.2fx' % v for v in vel_pass)}). "
    "Velocity passers BUKAN kandidat/promosi: ETHBack = delta supply token ERC20 bridge (bukan velocity NFT); "
    "Keyforge/Pixpad/Coralume/Candlewick/Compasso (+22..+33, 1,54-9,28x) memenuhi 3 kaki strong lead on-chain "
    "(umur terverifikasi 2026-11-08 14:55-14:57 WIB, free% 37,8-42,9% >=25%, slot user terbuka freeLeft=3/quote=0) "
    "TAPI owner 0x5304... ADA di same-owner-discards (factory wave 8 kontrak, discarded run 1431) -> promosi "
    "DIBATALKAN, status diubah same-owner-discarded-2026-11-08, hanya run log. NEKART +118 (9,44x) tapi freeMinted "
    "799/10000 = 8,0% <25% -> bukan strong. THE WALL +20 (6,4x) free% UNVERIFIED -> bukan strong. "
    "Zorrie totalMinted 6->8 (0,16%), Gloop 38->43 (free% tetap UNVERIFIED), Skunk Hollow 117->208 (8,3% <25%) -> "
    "ketiganya TANPA promosi. MALTA totalFreeShares 426->434, quote(user,1)=(1,0), slot terbuka; gate TETAP GAGAL "
    "(cek situs = kaki parent). NUSA freeMinted 120->142/560 = 25,4% (lewati 25%); quote(user,1) REVERT di baca segar "
    "-> slot user tidak terverifikasi segar; gate TETAP FAILED; tetap lead gate-blocked. NIULAI launched=0 phase=4 "
    "(belum buka); KillZero launched=0 (belum buka); DROID freeMinted tetap 732; 960E freeMinted tetap 38 state=0; "
    "Agentidbsc mintOpen=1 quote=0; CHTCI mintOpen=1; BoxBigem freeMinted=totalSupply (S2 partial, tanpa perubahan); "
    "Pacture slot user terpakai (freeClaimed=1); FABE freeSharesRemaining tetap 2821, launched=0. "
    "Binanceai TIDAK BERUBAH (launched 0, failed 1, isRefundPhase 1, totalShares 3110, tokenClaimed user 0, saldo 0) "
    "- sudah dilaporkan sekali sebagai refund phase, TIDAK dilaporkan ulang. Age sweep: 0 flag."
)
snap["runNote1931_1108_scan"] = (
    f"Scan run 1931: window {scan.get('from_block')}-{scan.get('to_block')} (1000 blok, cap), "
    f"{scan.get('ankr_calls')} Ankr calls, {len(scan.get('errors', []))} error, partial={scan.get('partial')}; "
    f"{len(scan.get('contracts', []))} NFT ter-enrich / {scan.get('erc20_mint_contracts')} ERC20-mint; "
    f"first-seen baru {len(new_seen)} (agent-shaped {len(agent_shaped_new)}), historic/known {historic}; "
    f"skipped gap 132389446-132394598 (5153 blok, backfill OFF); "
    f"watermark {'TIDAK dimajukan (partial)' if partial else 'dimajukan ke ' + str(scan.get('to_block'))}; "
    f"HELIX + Pokechain = EARLY lead PENDING REPORT (parent laporkan, lalu flip status); Quiet Lantern bukan agent-shaped. "
    f"5c: {len(five_c) if isinstance(five_c, dict) else 0} ERC20 dicek, track-c-scan-checked +{added5c}, 0 sale-shape hit."
)
save(BASE + "/onchain-snapshot.json", snap)
print("MERGE DONE changed=%d degraded=%d vel_pass=%s tc_changed=%s new_seen=%d agent_shaped=%d historic=%d partial=%s 5c_added=%d" % (
    len(changed), degraded, vel_pass, tc_changed, len(new_seen), len(agent_shaped_new), historic, partial, added5c))
print("CHANGED:", [(n, o, t, m, p, s) for (n, o, t, m, p, s) in changed][:40])
