#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-08 01:01 WIB (run 0101).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0). No promotions (AgentVOLT velocity passes but free%
unverifiable — all free views revert; Ink Koi velocity passes but user
already claimed #712, slot closed). ONE first-seen EARLY lead: ONES
0xD878B2e224B9F077323d46309EC1dba979857B6E — agent-shaped, first mints
verified on-chain, BUT free pool already exhausted (111/111) by
verification time -> reported once as EARLY + sold-out, added with
status early-lead-2026-11-08-0101-free-pool-exhausted. AGENT ID Card
0x486d0947... (discovery sweep) sold out 3000/3000 -> excluded.
Updates King's Game + Agent Grove + HIVE + binanceai.
Updates last_run + run notes. Watermark NOT advanced (backfill owns it);
scan-state gets note_0101_scan only.
"""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132246544  # reread block

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-08-0101-reread.json"))
vel = json.load(open(HF + "run-2026-11-08-0101-velocity.json"))

vel_by_name = {row["name"]: row for row in vel["rows"]}
updated = 0
none_supply = 0
for name, rd in reread["reread"].items():
    c = snap["contracts"].get(name)
    if c is None:
        continue
    updated += 1
    if rd.get("totalSupply") is not None:
        c["previousTotalSupply"] = c.get("totalSupply")
        c["totalSupply"] = rd["totalSupply"]
    else:
        none_supply += 1
    for f in ("totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen"):
        if rd.get(f) is not None:
            c[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        c["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        c["freeClaimed_user"] = rd["freeClaimed_user"]
    c["lastReadBlock"] = BLOCK
    c["lastReadWib"] = "2026-11-08 run 0101"
    vrow = vel_by_name.get(name)
    if vrow:
        c["mintedInInterval"] = vrow["mintedInInterval"]
        c["intervalMinutes"] = vrow["intervalMin"]
        c["currentRatePerMin"] = vrow["ratePerMin"]
        c["previousRatePerMin"] = vrow["prevRatePerMin"]
        c["velocityRatio"] = vrow["ratioVsPrev"]
        c["velocityLegPasses"] = vrow["velocityPasses"]
        if vrow.get("freePct") is not None:
            c["freePctVerified"] = vrow["freePct"]
    c["runNote0101"] = ("Run 0101 (blok %d): totalSupply %s, minted interval %s, velocity %s."
                        % (BLOCK, c.get("totalSupply"), c.get("mintedInInterval"), c.get("velocityLegPasses")))

# track_c reread (fresh values where readable; None keeps old value)
tc_updated = 0
for name, rd in reread.get("track_c", {}).items():
    t = snap.get("track_c", {}).get(name)
    if t is None:
        continue
    tc_updated += 1
    for f in ("totalSupply", "freeMinted", "freeSharesRemaining"):
        if rd.get(f) is not None:
            t[f] = rd[f]
    if rd.get("balanceOf_user") is not None:
        t["balanceOf_user"] = rd["balanceOf_user"]
    if rd.get("freeClaimed_user") is not None:
        t["freeClaimed_user"] = rd["freeClaimed_user"]
    t["lastReadBlock"] = BLOCK
    t["lastReadWib"] = "2026-11-08 run 0101"

# --- Velocity passers: AgentVOLT (round 1) + Ink Koi — both NOT promotable ---
av = snap["contracts"].get("AgentVOLT (round 1)")
if av is not None:
    av["runNote0101"] = ("Run 0101 (blok 132246544 + single-call re-check run-2026-11-08-0101-passer-free.json, "
                         "blok 132248949): velocity PASSES (+46, 4152->4198 reread / 4199 re-check, rate 2,06/mnt, "
                         "ratio 10,62) TAPI free% TIDAK BISA DIVERIFIKASI: SEMUA free view revert "
                         "(freeMints/freeMinted/freeClaimed/FREE_SUPPLY/FREE_CAP/MAX_SUPPLY/mintOpen/paused/freeLeft/"
                         "freeSupply/totalMinted + semua user free view), launch age UNVERIFIED, website null "
                         "(MINTS) -> BUKAN strong lead, BUKAN kandidat, tetap watchlist-only-unverified, tidak "
                         "dilaporkan ulang. Pola sama seperti run 0631/0901/1801/1901/2231/2301.")
ik = None
for k, v in snap["contracts"].items():
    if isinstance(v, dict) and v.get("address", "").lower() == "0xbd4b4e7189ae9356514664146b0eD683601200a9":
        ik = v
        break
if ik is not None:
    ik["runNote0101"] = ("Run 0101 (blok 132246544): velocity PASSES (+40, rate 1,79/mnt, ratio 1,63, freePct "
                         "35,76%) TAPI user SUDAH memegang #712 (balanceOf(user)=1, freeClaimed(user)=1 per hot-leg "
                         "0104) -> slot gratis user TERTUTUP, BUKAN strong lead, BUKAN kandidat, tidak di-preview/"
                         "mint ulang. Tetap watchlist-only.")

# --- ONES: first-seen EARLY lead, free pool already exhausted ---
snap["contracts"]["ONES"] = {
    "address": "0xD878B2e224B9F077323d46309EC1dba979857B6E",
    "name": "ONES",
    "symbol": "ONES",
    "kind": "ERC721",
    "track": "A",
    "status": "early-lead-2026-11-08-0101-free-pool-exhausted",
    "source": "onchain-scan run 0101 (window 132245622-132246621)",
    "firstSeenBlock": 132246554,
    "firstMintWib": "2026-11-08 01:12:35 WIB",
    "scanMints": 6,
    "scanMinters": 6,
    "totalMinted": 111,
    "nextTokenId": 112,
    "FREE_CAP": 111,
    "MAX_SUPPLY": 1111,
    "MAX_PER_WALLET": 5,
    "PRICE": 2000000000000000,
    "priceNote": "0.002 BNB paid lane; free lane exhausted",
    "mintOpen": 1,
    "mintOpensAt": 1794075112,
    "mintOpensAtWib": "2026-11-08 01:11:52 WIB",
    "freeMinted": 111,
    "freePctVerified": 100.0,
    "freeClaimed_user": 0,
    "mintsBy_user": 0,
    "balanceOf_user": 0,
    "holdsAgentId_user": 1,
    "owner": "0x35967ff462ac6b97463e3ed650e38f827168227e",
    "treasury": "0x35967ff462ac6b97463e3ed650e38f827168227e",
    "agentIdRegistry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "registryBytesHit": True,
    "sourcify": "error:IncompleteRead",
    "xVerified": False,
    "websiteGate": "UNVERIFIED run 0101: contractURI() reverts (no contractURI), tokenURI(1)='1' (no URL), Sourcify metadata unfetchable (IncompleteRead), raw address search 0 hits (browser.search 01:35 WIB)",
    "lastReadBlock": 132248949,
    "lastReadWib": "2026-11-08 run 0101",
    "runNote0101": ("Run 0101: EARLY LEAD first-seen (scan window 132245622-132246621, 6 mints / 6 minters, first "
                    "mint blok 132246554 = 2026-11-08 01:12:35 WIB via fast_rpc block timestamp; mintOpensAt "
                    "01:11:52 WIB). Agent-shaped: registry bytes hit + agentIdRegistry() + free views "
                    "(freeClaimed/freeMinted/FREE_CAP) + NotAgentIdHolder error. Verifikasi segar blok 132248949: "
                    "totalMinted 111, freeMinted 111/111 FREE_CAP = FREE POOL HABIS (100%) dalam ~25 menit; "
                    "MAX_SUPPLY 1111, PRICE 0.002 BNB paid lane masih buka; user holdsAgentId=1, freeClaimed(user)=0, "
                    "mintsBy(user)=0, balanceOf(user)=0 — TAPI pool kosong, tidak ada slot gratis. Website UNVERIFIED "
                    "(H/I/A gagal, lihat websiteGate). BUKAN kandidat, BUKAN strong lead, TIDAK PERNAH di-preview/"
                    "mint (early lead + pool habis). Dilaporkan SEKALI sebagai EARLY + sold-out di run ini."),
}

# --- AGENT ID Card: discovery sweep, sold out -> excluded ---
snap.setdefault("excluded", {})["AGENT ID Card"] = {
    "address": "0x486d0947cAa3d70c19e38f6C789489d39291E9e7",
    "track": "A",
    "status": "excluded-sold-out-2026-11-08",
    "note": ("Discovery sweep run 0101 (Substack 22-project list, 11 days old; totalSupply read 3000): "
             "totalSupply 3000 = MAX_SUPPLY 3000 (SOLD OUT), mintOpen 1; FREE_SUPPLY/freeMinted/freeClaimed "
             "revert (no free views); Sourcify 404 (unverified); registry bytes hit true; balanceOf(user)=0. "
             "No free mint possible; not a lead/candidate. Never previewed/minted. Check "
             "run-2026-11-08-0101-agentidcard-check.json."),
}

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote0101"] = ("Run 0101 (blok 132248502-an, kgame-retry): freeMinted 3, totalMinted 3, balanceOf(user)=0, "
                         "registry_match true — NO CHANGE vs 0031.")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote0101"] = ("Run 0101 (blok 132245115, grove-check): freeOpen 0, freeClaimed(user) false — "
                            "NO CHANGE vs 0031.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote0101"] = ("Run 0101 (single-call retry blok 132248677): totalSupply 1256, balanceOf(user)=1 — "
                           "NO CHANGE vs 0031; minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-08 run 0101"
snap["last_run_wib"] = "2026-11-08T01:01:00+07:00"
snap["timestamp_wib"] = "2026-11-08 run 0101"
snap["runNote0101"] = (
    "Run 0101 (01:01 WIB): reread blok 132246544, 445 kontrak + 69 track_c, 719,3 dtk, 104 supply-None "
    "(degradasi RPC, nilai lama dipertahankan; 0/445 free view terbaca). Velocity: 5 pass — 3 artefak skala "
    "(bridge-0x93bf08d2, VOLT token (bridge), Zhenzhu) + AgentVOLT (round 1) +46 ratio 10,62 TAPI free% "
    "UNVERIFIED (semua free view revert di re-check blok 132248949) + Ink Koi +40 ratio 1,63 freePct 35,76% "
    "TAPI user sudah pegang #712 (slot tertutup) -> 0 promosi. 35 sellout, set identik 0031, 0 sellout baru; "
    "age-exclusion: 0 dihapus (kept 49 grandfathered; unverified-launch 382, sama seperti 0031); HIVE/King's "
    "Game/Grove tanpa perubahan; track_c drift: Crack +5, ORBITA +1,2e25, PLNK +4e24, PHNX +2,5e22, 0 free view "
    "terbaca (0/69), 0 sellout. EARLY LEAD BARU: ONES 0xD878B2e224B9F077323d46309EC1dba979857B6E (first mint "
    "01:12:35 WIB, 6 mints/6 minters) — free pool SUDAH HABIS 111/111 saat verifikasi (~25 mnt), bukan kandidat/"
    "strong lead, dilaporkan sekali sebagai EARLY + sold-out. AGENT ID Card 0x486d0947... (discovery sweep) sold "
    "out 3000/3000 -> excluded. TIDAK ada eksekusi oleh run ini (tidak ada mint/preview/claim)."
)
snap["runNote0101_scan"] = (
    "Run 0101 scan: pre-flight PASS (head 132246486, ankr_getLogs 50 blok OK 967 logs, 9,3 dtk). Window "
    "132245622-132246621 (1000 blok terbaru), 133 ERC721 + 3 ERC1155, 285 ERC-20 mint, 40 Ankr calls, 0 error. "
    "Enrichment PARTIAL: 74/136 ter-enrich, killed di enrich 75/136 oleh timeout 780 dtk (SCAN_EXIT via timeout; "
    "partial JSON terselamatkan, kontrak ter-enrich urut mint_count). HIVE tidak ada di window. Triage: 1 "
    "first-seen — ONES 0xD878B2e2... (6 mints, 6 minters, first mint 01:12:35 WIB), agent-shaped + free path -> "
    "EARLY LEAD (parent: free pool habis 111/111). 62 kontrak window tidak ter-enrich -> backfill. Seen +118 "
    "(nested 12.332). 5c: 41 ERC-20 mint>=10, 37 sudah dicek, 4 baru dicek, 0 sale-shape hit; "
    "track-c-scan-checked.json kini 2.827. WATERMARK TIDAK DIMAJUKAN run ini (milik backfill; "
    "last_scanned_block tetap 132238015); standing gap 132238016-132245621 milik backfill."
)
snap["runNote0101_discovery"] = (
    "Run 0101 discovery (subagent): Boltbook boltbook.fun EN 45.691 B / ZH 46.374 B (HTTP 200), 15 alamat mentah, "
    "10 unik, EN=ZH identik, 0 free-share keyword hit. Klasifikasi: BOLT/NeoGods/AgentBook di snapshot; FREEDROP "
    "excluded same-owner-discarded; BoltRewards footer + BRAINROT ZOO owner/treasury EOA = infrastruktur. 0 "
    "genuinely new dari Boltbook; 4 scan-seen dengan diskusi segar (Agent Goats 582, BRAINROT ZOO 400, Driftnauts "
    "886, REWARD 63) + Gacha Gang 358, Ticker Pets 570, Odyssey (totalSupply() reverts) — semua scan-seen, bukan "
    "lead. AGENT ID Card 0x486d0947... (Substack list) totalSupply 3000 — parent verifikasi: SOLD OUT 3000/3000 "
    "-> excluded. AgentForge sold out 3.333 (Oct 27) -> bukan lead. MINTS index 58 proyek, 0 baru. Sourcify 5a: "
    "20 kontrak (verifiedAt 00:36-01:10 WIB), 0 S1/S2/0 agent-mint-shape (near-miss ONES, registry=False di cek "
    "Sourcify-only). Square/Odaily/PANews/DappBay: hanya item lama, 0 site link baru. Bridge TIDAK berubah "
    "(sha256 b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 promosi)."
)
snap["runNote0101_binanceai"] = (
    "Run 0101 track-B binanceai re-check (blok 132248502): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK 0031; masih pending "
    "(refund phase), bukan kegagalan. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")

# --- Scan state: note only, watermark NOT advanced ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_0101_scan"] = (
    "Run 0101 scan (01:01 WIB): pre-flight PASS (head 132246486, 967 logs/50 blok, 9,3 dtk). Window "
    "132245622-132246621 (1000 blok terbaru), 133 ERC721 + 3 ERC1155, 285 ERC-20 mint, 40 Ankr calls, 0 error. "
    "Enrichment PARTIAL 74/136 (timeout 780 dtk di enrich 75; partial JSON terselamatkan). Triage 1 first-seen "
    "(ONES 0xD878B2e2..., agent-shaped, EARLY lead, free pool habis 111/111). Seen +118 (nested 12.332). 5c: 4 "
    "baru dicek, 0 hit (checked 2.827). WATERMARK TIDAK DIMAJUKAN run ini (milik backfill; last_scanned_block "
    "tetap 132238015); standing gap 132238016-132245621 milik backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("state note_0101_scan written; last_scanned_block still:", st.get("last_scanned_block"))
