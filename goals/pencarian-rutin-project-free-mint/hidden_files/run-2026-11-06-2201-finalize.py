#!/usr/bin/env python3
"""Finalize run 2026-11-06 2201 WIB (parent).
Merges leg-1 re-read, velocity rows, scan partial + 5c, Sourcify/Boltbook
findings, targeted reads, bridge (manual), ChimpAgent track-C lead
(gate FAILED via methods A-N incl. BscScan live-browser read).
No preview/mint/claim/approve/sign/transaksi in this run.
"""
import json, shutil, datetime

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-2201"
NOW_WIB = "2026-11-06 run 2201"

for f in ["onchain-snapshot.json", "track-c-scan-checked.json"]:
    shutil.copy(f"{BASE}/{f}", f"{BASE}/{f}.bak-20261106-2201")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
reread = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
vel = json.load(open(f"{BASE}/run-{TS}-velocity.json"))
fivec = json.load(open(f"{BASE}/run-{TS}-5c-checked.json"))
scan = json.load(open(f"{BASE}/run-{TS}-scan.json"))
firstseen = json.load(open(f"{BASE}/run-{TS}-firstseen.json"))

BLOCK = reread.get("block")
merged_nft = 0
merged_tc = 0

# --- leg-1 merge: update numeric/state fields only where the fresh read is not None
NUM_FIELDS = ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
              "FREE_SUPPLY", "MAX_SUPPLY", "maxSupply", "mintOpen", "paused",
              "freeQuota", "remainingFree", "freeCap", "FREE_CAP", "PAID_CAP",
              "paidMinted", "totalPodsMinted", "freePodsClaimed", "freePodsRemaining",
              "phase", "opened", "launched", "saleEnded", "price", "PRICE"]
USER_FIELDS = {"balanceOf_user": "balanceOf_user", "mintedBy_user": "mintedBy_user",
               "freeUsed_user": "freeUsed_user", "quote_user_1": "quote_user_1",
               "costOf_user_1": "costOf_user_1", "canFreeMint_user": "canFreeMint_user",
               "claimedFree_user": "claimedFree_user", "freeClaimed_user": "freeClaimed_user",
               "freeSharesRemaining": "freeSharesRemaining",
               "freeSharesClaimed_user": "freeSharesClaimed_user",
               "hasFreeShare_user": "hasFreeShare_user",
               "sharesMinted": "sharesMinted", "mintsLeft_user": "mintsLeft_user",
               "mintedPerWallet_user": "mintedPerWallet_user",
               "freeClaimedBy_user": "freeClaimedBy_user",
               "freeWindowClosesAt": "freeWindowClosesAt",
               "quoteFor_user_1": "quoteFor_user_1", "agentGateOn": "agentGateOn",
               "spotsLeft": "spotsLeft", "totalMints": "totalMints"}
for name, d in reread.get("reread", {}).items():
    e = snap["contracts"].get(name)
    if e is None:
        continue
    for f in NUM_FIELDS:
        if d.get(f) is not None:
            e[f] = d[f]
    for src, dst in USER_FIELDS.items():
        if d.get(src) is not None:
            e[dst] = d[src]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_nft += 1
for name, d in reread.get("track_c", {}).items():
    e = snap["track_c"].get(name)
    if e is None:
        continue
    for f in NUM_FIELDS + list(USER_FIELDS.keys()):
        if isinstance(d, dict) and d.get(f) is not None:
            e[f] = d[f]
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = NOW_WIB
    merged_tc += 1

# --- targeted reads (printed lines; targeted.json never written: killed at MERGEBORN)
targeted_note = {
    "StarAgent-7d39": "totalSupply 1826 (leg-1 1810, 2131-targeted 1797); sudah excluded-age 2131; tetap minting, belum sold out.",
    "Tampesta-6aA5": "totalSupply gagal baca; paused()=1 (baru terbaca run ini), maxSupply 2222, balanceOf(user)=0; watchlist-only, tanpa promosi.",
    "Jolly": "totalMinted/freeMinted 3720/5000 (leg-1 3718); sudah age-excluded; tidak ada aksi.",
    "MERGEBORN": "targeted terbunuh timeout sebelum MERGEBORN; leg-1 semua view None (degradasi RPC); nilai 2131 dipertahankan; tetap strong-lead-gate-blocked.",
    "BNBFLY Agent Pass": "targeted2 semua view None (degradasi RPC dataseed1); nilai 2131 dipertahankan; slot tetap terblokir MIN_BALANCE.",
    "CLEPSYDRA": "targeted2 semua view None (degradasi RPC); nilai 2131 dipertahankan; gate tetap FAILED.",
}
for k, note in targeted_note.items():
    e = snap["contracts"].get(k) or snap["track_c"].get(k)
    if e is not None:
        e["runNote2201"] = note
snap["contracts"]["Tampesta-6aA5"]["runNote2201"] = targeted_note["Tampesta-6aA5"]

# --- velocity merge
vel_rows = {r[0]: r for r in vel.get("rows", [])}
for name, r in vel_rows.items():
    e = snap["contracts"].get(name)
    if e is None:
        continue
    # row: [name, view, prev_value, now_value, minted, rate_now, rate_prev, ratio, passes]
    e["previousTotalSupply"] = r[2]
    e["mintedInInterval"] = r[4]
    e["currentRatePerMin"] = r[5]
    e["previousRatePerMin"] = r[6]
    e["velocityLegPasses"] = bool(r[8])
    e["velocityNote2201"] = (
        f"Run 2201 (blok {vel.get('block_now')}, interval {vel.get('interval_min'):.2f} mnt "
        f"vs run 2131): {r[2]}->{r[3]} (+{r[4]}, {r[5]}/mnt vs prev {r[6]} = "
        f"{r[7] if r[7] is not None else 'None'}x) -> velocity "
        f"{'LOLOS' if r[8] else 'GAGAL'}."
    )
# PassAgentX: velocity passes but free% unverified -> stays early lead
pa = snap["contracts"]["PassAgentX"]
pa["velocityVerified"] = True
pa["velocityNote2201"] += (" PassAgentX velocity LOLOS run ini, TAPI free% vs free cap tetap "
    "UNVERIFIED (tidak ada FREE_SUPPLY view) -> tetap EARLY lead, TIDAK promosi, "
    "TIDAK dilaporkan (preseden Sprouts-1831 run 2131). Umur terverifikasi 2026-11-05 "
    "06:49:58 WIB, deadline 48 jam 2026-11-07 06:49:58 WIB.")

# --- 5c merge into track-c-scan-checked.json
store = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked = store.get("checked", {}) if isinstance(store, dict) else {}
added5c = 0
for r in fivec.get("checked", []):
    a = r["address"]
    if a.lower() not in {k.lower() for k in checked}:
        checked[a] = {
            "run": TS, "mint_count": r.get("mint_count"),
            "S1": r.get("S1"), "S2": r.get("S2"),
            "note": r.get("error") or r.get("note") or "checked-not-sale-shape",
            "abi_error": bool(r.get("error")),
        }
        added5c += 1
if isinstance(store, dict):
    store["checked"] = checked
json.dump(store, open(f"{BASE}/track-c-scan-checked.json", "w"), indent=1)

# --- ChimpAgent -> track_c as gate-blocked lead (reported once via this run)
snap["track_c"]["ChimpAgent"] = {
    "address": "0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689",
    "name": "ChimpAgent",
    "symbol": "Chimp",
    "kind": "ERC20-token+sale-S2",
    "status": "track-c-lead-gate-blocked-2026-11-06",
    "totalSupply": 1000000000000000000000000000,
    "MAX_SUPPLY": 1000000000000000000000000000,
    "MAX_MINTS": 800,
    "totalMints": 53,
    "MINT_AMOUNT": 1000000000000000000000000,
    "FREE_PER_WALLET": 1,
    "MAX_PER_WALLET": 5,
    "PRICE": 500000000000000,
    "MINT_DURATION": 604800,
    "MINT_DEADLINE": 1794582382,
    "mintOpen": 1,
    "tradingOpen": 0,
    "pair": "0x0000000000000000000000000000000000000000",
    "AGENT_ID": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F",
    "FACTORY": "0xca143ce32fe78f1f7019d7d551a6402fc5350c73",
    "dev": "0x57912bd90a5fceb68ec44939349c2facd2441960",
    "freeLeft_user": 1,
    "quote_user_1": 0,
    "mintedBy_user": 0,
    "balanceOf_user": 0,
    "firstMintBlock": 132029852,
    "firstMintWib": "2026-11-06 ~22:06:38 WIB (blok 132029852; supply-mint blok 132029817 = 22:06:22 WIB)",
    "firstSeenBlock": 132029852,
    "verifiedAt": "2026-11-06T15:08:46Z",
    "sourcify": "verified-exact-match-v0.8.24",
    "lastReadBlock": 132033683,
    "lastReadWib": NOW_WIB,
    "xVerified": False,
    "gateNote": ("GATE WEBSITE GAGAL, metode A-N dicoba: (A) cari alamat kontrak nihil; (G) cari "
        "nama ChimpAgent hanya ChimpX AI (Solana, proyek lain); (M) site:vercel.app/pages.dev/deed.page/surge.sh "
        "nihil; (K) GitHub alamat/nama nihil (batasan: pencarian kode sesungguhnya butuh auth); (C) source Sourcify "
        "tidak memuat URL proyek (hanya bzz/ipfs metadata source); (J) ABI tanpa fungsi website/siteURL; (H) "
        "contractURI tidak ada (ERC-20); (I) tokenURI N/A; (B) Boltbook front page en+zh tidak ada; (D) pola "
        "same-family tanpa situs yang mencetak kontrak ini; (E) owner() null, dev tercatat tanpa kaitan situs; "
        "(N) ID agent dev tidak diketahui, hop tidak bisa di-resolve; (L) halaman token BscScan via live browser "
        "(22:40-22:50 WIB): 62 holder, 63 transfer, reputasi UNKNOWN, source terverifikasi Exact Match, tab Info "
        "hanya 'Click here to update the token information' — TIDAK ada tautan Website/X/Telegram/sosial. "
        "X/diskusi UNVERIFIED (opsional, bukan pemblokir). TIDAK di-preview, TIDAK di-mint."),
    "shapeNote": ("S2 lolos penuh: token+sale single-contract, mint(qty) payable, quote, freeLeft(address)/"
        "FREE_PER_WALLET, AGENT_ID()=registry (koreksi atas hot leg 2209 yang mencatat gate_fns=[] karena "
        "classifier-nya melewatkan AGENT_ID() uppercase). Source: fair mint untuk holder Agent ID, 800 mint "
        "@ 1.000.000, 200M cadangan likuiditas, mint pertama gratis/wallet, lalu 0,0005 BNB, maks 5, EOA only; "
        "70% paid mint untuk likuiditas, 30% ke dev; openTrading() pasangkan cadangan + BNB di PCS V2, LP ke "
        "dead address, burn sisa; tanpa owner/tax/blacklist."),
    "baselineNote": ("TRACK-C LEAD dilaporkan sekali run 2201 sebagai lead gate-blocked (bukan kandidat): "
        "bentuk S2 + pool gratis terbuka + slot user terbuka + umur terverifikasi ~30 menit. TIDAK di-preview/di-mint "
        "karena gate website GAGAL. Bila situs proyek terverifikasi muncul kemudian, gate bisa diuji ulang; "
        "bila pool habis / umur lewat 48 jam / terbukti bukan agent-shaped, laporkan sekali + hapus."),
}

# --- run notes
snap["runNote2201_1106"] = (
    "Run 2201 (22:01-~23:00 WIB): 0 kandidat, 0 auto-mint/claim. 1 temuan baru dilaporkan sekali: "
    "ChimpAgent TRACK-C LEAD gate-gagal (S2 lolos, slot user terbuka, umur ~30 mnt; gate website GAGAL metode A-N, "
    "termasuk BscScan live-browser 22:40-22:50 WIB: 62 holder, tanpa tautan situs/sosial). PassAgentX velocity LOLOS "
    "(+30, 1,84x) tapi free% UNVERIFIED -> tetap early lead, tidak promosi. Scan parsial (chunk 1000 blok "
    "132031735-132032734 OK, enrichment stall 44/157, SCAN_EXIT=124; 0 first-seen baru dari 44 ter-enrich; 113 kontrak "
    "jendela tak ter-enrich = gap). 5c: 43 ERC-20 mint>=10, 6 baru dicek, 0 sale shape (4 gagal fetch ABI Sourcify). "
    "Boltbook 0 baru; sweep route 3/6 nihil; bridge 0 baru. BINANCEAI tak terbaca (degradasi RPC, bukan perubahan state). "
    "Targeted: Tampesta paused()=1 (baru); StarAgent 1826 (sudah excluded); Jolly 3720/5000 (sudah excluded). "
    "Tidak ada age-exclusion baru. Tidak ada preview/mint/claim/approve/sign/transaksi."
)
snap["runNote2201_scan_1106"] = (
    "Scan run 2201: pre-flight OK 3,2 dtk (head 132032697). Jendela 132031735-132032734 (1000 blok, cap 1000), "
    "40 panggilan Ankr, 0 error, partial=true. Enrichment stall di 44/157 (Sourcify URLError + RPC lambat), "
    "SCAN_EXIT=124 (timeout 780 dtk). 0 true first-seen dari 44 kontrak ter-enrich. 113 kontrak NFT jendela tidak "
    "ter-enrich (alamatnya tidak tersimpan di JSON) -> gap cakupan, ditutup bertahap oleh backfill. Watermark TIDAK "
    "dimajukan (milik backfill). Seen file TIDAK ditulis run ini."
)
snap["last_run"] = NOW_WIB
snap["last_run_wib"] = NOW_WIB
snap["timestamp_wib"] = "2026-11-06T23:00:00+07:00"
snap["note"] = snap.get("note", "") + " | Run 2201: ChimpAgent track-C lead gate-blocked (dilaporkan sekali); PassAgentX velocity lolos tapi free% unverified (tetap early); scan parsial 44/157."

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

# --- scan state note (append, do not advance watermark)
state = json.load(open(f"{BASE}/onchain-scan-state.json"))
state["note_2201_scan"] = (
    "Run 2201: pre-flight OK 3,2 dtk (head 132032697). Jendela main-scan 132031735-132032734 (1000 blok, "
    "cap 1000), 40 panggilan Ankr, 0 error, partial=true. Enrichment stall 44/157 (Sourcify URLError + RPC "
    "degradasi), SCAN_EXIT=124 (timeout 780 dtk). 0 true first-seen (44 ter-enrich). 113 kontrak NFT jendela "
    "tidak ter-enrich -> gap cakupan; watermark TIDAK dimajukan (milik backfill); seen file TIDAK ditulis run ini."
)
json.dump(state, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)

# --- bridge file for this run (manual check; main.py section never ran)
bridge = {"total": 115, "discarded": 7, "not_in_snapshot": 0, "not_in_snapshot_list": [],
          "note": "Manual run 2201: 115 kontrak bridge, 7 same_owner_discarded, 0 temuan pelengkap baru "
                  "(3 alamat 'not in snapshot' menurut metode address-set adalah temuan lama yang sudah "
                  "dilaporkan; metode text-grep hot leg: 0). File tidak berubah sejak 2026-11-06 02:48."}
json.dump(bridge, open(f"{BASE}/run-{TS}-bridge.json", "w"), indent=1)

print(f"FINALIZE DONE merged_nft={merged_nft} merged_tc={merged_tc} added5c={added5c} "
      f"firstseen={len(firstseen)} contracts={len(snap['contracts'])} "
      f"track_c={len(snap['track_c'])} excluded={len(snap['excluded'])}")
