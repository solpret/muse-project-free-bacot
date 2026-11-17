#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 23:31 WIB (run 2331).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json.
No age removals (0 candidates). No promotions (NULLRAID velocity passes but
slot already used by user + grandfathered minted-by-user; 2301 passers all fail).
Updates HOG ORBIT / helm.ai supplies (360/358). Records discovery/scan
dispositions in run notes only (nothing new to exclude/add). Updates King's
Game + Agent Grove + HIVE. Updates last_run + run notes. Watermark NOT
advanced (backfill owns it); scan-state gets note_2331_scan only.
Snapshot + run log only. No mint/preview/claim.
NOTE: top-level key `runNote2331` is a STALE Nov-5 note (Jolly age-exclusion,
BNB CACHE) — do NOT overwrite it; this run uses `runNote2331_1107*` keys."""
import json

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132233438

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2331-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2331-velocity.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2331"
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
    c["runNote2331"] = ("Run 2331 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2331"

# --- Velocity passer detail: NULLRAID First Breach — velocity passes, NOT promotable ---
nr = snap["contracts"].get("NULLRAID First Breach")
if nr is not None:
    nr["freeMinted"] = 803
    nr["FREE_CAP"] = 1111
    nr["freePctVerified"] = 72.3
    nr["runNote2331"] = ("Run 2331 (blok 132233438 + single-call re-check run-2026-11-07-2331-passer-free.json, "
                         "blok 132235051): velocity PASSES (+26, 774->800, ratio 1.64, age verified ~8.3h, first "
                         "mint 2026-11-07 15:15:27 WIB) AND freePct VERIFIED 803/1111 = 72.3% >= 50% (freeMints "
                         "803, phaseMinted 803/phaseCap 1111) BUT user's free slot ALREADY USED (freeClaims_user=1, "
                         "balanceOf_user=1, token #503 minted ~18:0x WIB) + status grandfathered minted-by-user -> "
                         "NOT a strong lead, NOT a candidate, no action, no re-report.")

# --- HOG ORBIT / helm.ai: supply drift only; gate still failed, no promotion path ---
hog = snap["contracts"].get("HOG ORBIT")
if hog is not None:
    hog["runNote2331"] = ("Run 2331 (blok 132233438): totalSupply 360 (was 319), velocity not computable (first "
                          "baseline) — gate website FAILED (run 2301), still watchlist-only, no promotion path.")
helm = snap["contracts"].get("helm.ai")
if helm is not None:
    helm["runNote2331"] = ("Run 2331 (blok 132233438): totalSupply 358 (was 337), velocity not computable (first "
                           "baseline) — gate website FAILED (run 2301), still watchlist-only, no promotion path.")

# --- Specials ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["runNote2331"] = ("Run 2331 (blok 132235179): freeMinted 3, totalMinted 3, balanceOf(user)=0, registry_match "
                         "true — NO CHANGE vs 2301.")
grove = snap["contracts"].get("Agent Grove")
if grove is not None:
    grove["runNote2331"] = ("Run 2331 (blok 132235198): freeOpen 0, freeClaimed(user) false — NO CHANGE vs 2301.")
hive = snap["contracts"].get("HIVE Agents")
if hive is not None:
    hive["runNote2331"] = ("Run 2331 (blok 132233438): totalSupply 1256, balanceOf(user)=1 — NO CHANGE vs 2301; "
                           "minted-by-user, bukan kandidat.")

snap["last_run"] = "2026-11-07 run 2331"
snap["last_run_wib"] = "2026-11-07T23:31:00+07:00"
snap["timestamp_wib"] = "2026-11-07 run 2331"
snap["runNote2331_1107"] = (
    "Run 2331 (23:31 WIB): reread blok 132233438, 445 kontrak + 69 track_c, 688 dtk, 104 supply-None (degradasi "
    "RPC, nilai lama dipertahankan; 5 kontrak snapshot tanpa field address tidak bisa di-re-read: Mummyhive, "
    "LuckyBox-d08e, SnailMail, Jolly, AgentGlyph); velocity: 1 passer — NULLRAID First Breach +26 ratio 1,64 "
    "umur ~8,3 jam DAN freePct TERVERIFIKASI 803/1111 = 72,3% (single-call re-check, "
    "run-2026-11-07-2331-passer-free.json) TAPI slot user SUDAH TERPAKAI (freeClaims_user=1, balanceOf_user=1, "
    "token #503) + grandfathered minted-by-user -> TIDAK promotable; 3 passer 2301 gagal run ini (0xbd4B +107 "
    "ratio 0,88; Horus AI +20 ratio 0,80; AgentVOLT +14 ratio 0,18); 35 sellout, set identik 2301, 0 sellout baru; "
    "age-exclusion: 0 dihapus (kept 49 grandfathered; unverified-launch 382, +2 = HOG ORBIT + helm.ai dari 2301); "
    "HOG ORBIT 319->360, helm.ai 337->358, velocity belum terhitung (baseline pertama), gate tetap gagal; "
    "HIVE/King's Game/Grove tanpa perubahan; track_c 8 drift totalSupply saja (Crack 3553->3568, MizzlewickAgent, "
    "ORBITA, PLNK, QuonkersAgent, WibblezapAgent, Draco Coin, PHNX), 0 free view terbaca (0/69), 0 sellout. "
    "CATATAN: top-level key runNote2331 di file ini adalah catatan usang run 2331 tanggal 2026-11-05 (Jolly, "
    "BNB CACHE) — TIDAK ditimpa; catatan run ini memakai kunci runNote2331_1107*."
)
snap["runNote2331_1107_scan"] = (
    "Run 2331 scan: pre-flight PASS (head 132233407, small ankr_getLogs 50 blok OK 216 logs, 4,9 dtk). Scan "
    "SUKSES percobaan pertama, 0 error: window 132232440-132233439 (1000 blok terbaru), 142 NFT (136 ERC721 + 6 "
    "ERC1155, 953 mint), 442 ERC-20 mint, 40 panggilan Ankr, ~17,5 mnt; effective coverage PENUH (max first_block "
    "NFT 132233438, ERC-20 132233432) — TIDAK ada lubang di window ini (beda dengan 2301 yang kehilangan 150 "
    "blok). HIVE tidak ada di window. Triage: 1 first-seen — OinkHash Pigs (OINK) 0x56155fd1818b31256E7f435956D6dff5C732f35f, "
    "21 mint/21 minter, first mint 23:26:44 WIB — NOT agent-shaped (no registry bytes, no free shape, Sourcify "
    "IncompleteRead) -> 0 EARLY lead. Seen file +169 (total nested 11.926). 5c: 11 ERC-20 baru dicek "
    "(mint_count>=10), 0 sale-shape; track-c-scan-checked.json 2.739. WATERMARK TIDAK DIMAJUKAN run ini (tetap "
    "132213365, milik backfill); standing gap 132229264-132232439 (termasuk lubang 150 blok run 2301) tetap milik "
    "backfill."
)
snap["runNote2331_1107_discovery"] = (
    "Run 2331 discovery: Boltbook boltbook.fun EN 46.640 B / ZH 46.854 B (HTTP 200; bare EN URL 302 ke /?lang=en "
    "— redirect bahasa Cloudflare, domain hidup), 13 alamat, EN=ZH identik, 0 free-share keyword hit; vs hot-leg "
    "2329 hanya 2 beda (Agent Cards sudah di snapshot; 0x40cd0aad = false positive, 40 hex pertama dari tx hash). "
    "6 alamat di luar snapshot semuanya dispositioned tanpa bacaan on-chain baru: BRAINROT ZOO 0x3c7d32... "
    "(watchlist-only 2301; post baru: free lane nyata on-chain + sim value-0 lolos, TAPI owner pegang privilege "
    "withdrawal/ubah harga/ubah aturan free — author TIDAK mint; TIDAK ada di snapshot, dicatat saja, tanpa "
    "perubahan tier); FREEDROP 0x92937562... (excluded same-owner-discarded /excluded/FREEDROP-9293; totalSupply "
    "292->300/500, pergerakan hitungan saja, TIDAK PERNAH promotable); ONLYAI token 0xcb505b97... (ERC-20, bukan "
    "mint); 0xcb529c67... (EOA owner AgentBook, bukan kontrak); 0x8269ea16... (footer BoltRewards); 0x40cd0aad... "
    "(tx hash). MINTS index identik 2301 (57 proyek, 0 entri baru). Sourcify 5a: 20 kontrak, 0 S1/S2/0 agent-mint "
    "(1 baru vs 2301: 0x7d8eA4b1..., tanpa shape; near-miss sama 0x56155fd1...). Square/Odaily/PANews: hanya item "
    "lama (Paw Gang, WHALE A sold out / WHALE B di snapshot, Nidavellir age-excluded, Ptah), 0 site link baru. "
    "DappBay tidak diperlukan. Bridge TIDAK berubah (sha256 b3f349f1..., 115 kontrak, 7 same_owner_discarded, 0 "
    "promosi). Track-B binanceai identik run 1701-2301 (launched 0, refund 1) — tidak dilaporkan ulang. Limitasi: "
    "Ankr eth_getLogs tetap butuh API key (age bersandar first-seen + Sourcify verifiedAt)."
)
snap["runNote2331_1107_binanceai"] = (
    "Run 2331 track-B binanceai re-check (blok 132235111): launched()=0, failed()=1, isRefundPhase()=1, "
    "totalShares()=3110, tokenClaimed(user)=0, balance=0, pair reserves 0/0 — IDENTIK run 1701-2301; sudah "
    "dilaporkan sekali, tidak dilaporkan ulang. Tidak ada preview/klaim."
)

json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
print("contracts:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c", {})),
      "| excluded:", len(snap.get("excluded", {})))
print("updated:", updated, "| none_supply:", none_supply, "| tc_updated:", tc_updated)
print("removed (age-excluded): none")

# --- Scan state: note only, watermark NOT advanced ---
st = json.load(open(HF + "onchain-scan-state.json"))
st["note_2331_scan"] = (
    "Run 2331 scan (23:31 WIB): pre-flight PASS (head 132233407, 216 logs/50 blok, 4,9 dtk). Window "
    "132232440-132233439 (1000 blok terbaru), 142 NFT (136 ERC721 + 6 ERC1155, 953 mint), 442 ERC-20 mint, 40 "
    "Ankr calls, ~17,5 mnt, 0 error, effective coverage PENUH (max first_block NFT 132233438). Triage 1 "
    "first-seen (OinkHash Pigs 0x56155fd1..., NOT agent-shaped), 0 EARLY lead. Seen +169 (11.926). 5c: 11 baru "
    "dicek, 0 hit (checked 2.739). WATERMARK TIDAK DIMAJUKAN run ini (tetap 132213365, milik backfill); standing "
    "gap 132229264-132232439 milik backfill."
)
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
print("state note_2331_scan written; last_scanned_block still:", st.get("last_scanned_block"))
