#!/usr/bin/env python3
"""Run 1731 bookkeeping (parent): apply route-1 re-read + follow-up + gate results
to the snapshot. Non-null values only — null is a failed read, never zero.
Run AFTER subagent A (scan) returns; merges scan first-seen decisions passed in
via run-2026-11-05-1731-scan-decisions.json if present (parent-written)."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1731"
snap_path = f"{BASE}/onchain-snapshot.json"
shutil.copy(snap_path, f"{BASE}/onchain-snapshot-1731.bak.json")
s = json.load(open(snap_path))
C = s["contracts"]
TC = s["track_c"]
EX = s.setdefault("excluded", {})
r = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
fu = json.load(open(f"{BASE}/run-{TS}-followup.json"))
BLK = r["block"]

def setv(d, k, v):
    if isinstance(v, int):
        d[k] = v

# --- generic NFT re-read: update supply/free (non-null only) + run note with delta ---
byaddr = {v["address"].lower(): k for k, v in C.items() if isinstance(v, dict) and v.get("address")}
for name, d in r["reread"].items():
    k = byaddr.get(d["address"].lower())
    if not k:
        continue
    v = C[k]
    old_ts = v.get("totalSupply")
    new_ts = d.get("totalSupply") if isinstance(d.get("totalSupply"), int) else d.get("totalMinted")
    note = None
    if isinstance(new_ts, int) and isinstance(old_ts, int) and new_ts != old_ts:
        note = f"Run 1731 (blok {BLK}): totalSupply {old_ts}->{new_ts} (+{new_ts - old_ts}); "
        setv(v, "totalSupply", new_ts)
    if isinstance(d.get("freeClaimed"), int):
        if v.get("freeClaimed") != d["freeClaimed"]:
            note = (note or "") + f"freeClaimed {v.get('freeClaimed')}->{d['freeClaimed']}; "
        setv(v, "freeClaimed", d["freeClaimed"])
    if isinstance(d.get("freeMinted"), int):
        if v.get("freeMinted") != d["freeMinted"]:
            note = (note or "") + f"freeMinted {v.get('freeMinted')}->{d['freeMinted']}; "
        setv(v, "freeMinted", d["freeMinted"])
    if isinstance(d.get("balanceOf_user"), int) and name in ("HIVE Agents",):
        v["userBalance"] = d["balanceOf_user"]
    if note:
        v["runNote1731"] = note + "tidak ada perubahan tier."
    v["lastReadBlock"] = BLK
    v["lastReadWib"] = "2026-11-05 run 1731"

# --- HIVE Agents velocity (interval ~40 mnt vs run 1631, blok 131797026 ~17:00 WIB) ---
h = C["HIVE Agents"]
h["previousTotalSupply"] = 1242
h["mintedInInterval"] = 10
h["intervalMinutes"] = 40.0
h["currentRatePerMin"] = 0.25
h["previousRatePerMin"] = 0.0
h["velocityLegPasses"] = False
h["velocityNote"] = ("Run 1731 (blok 131801637, ~17:40 WIB): 1242->1252 (+10) dalam ~40 mnt = "
                     "0.25/mnt, rate sebelumnya 0.0; <20 token dalam interval -> velocity leg GAGAL.")
h["runNote1731"] = "Run 1731 (blok 131801637): totalSupply 1242->1252 (+10); balanceOf(user)=1; minted-by-user, bukan kandidat."

# --- Forklings PROMOTION: early -> strong lead (gate-blocked, NO mint) ---
f = C["Forklings"]
f["previousTotalSupply"] = 434
f["mintedInInterval"] = 73
f["intervalMinutes"] = 42.0
f["currentRatePerMin"] = 1.74
f["previousRatePerMin"] = 0.075
f["velocityLegPasses"] = True
f["velocityNote"] = ("Run 1731: 434->507 (+73) dalam ~42 mnt = 1.74/mnt vs rate sebelumnya 0.075/mnt "
                     "= 23.2x DAN >=20 token -> velocity leg LULUS.")
f["totalSupply"] = 507
f["freeMinted"] = 507
f["freePctVerified"] = 25.35
f["freePctNote"] = ("freeMinted 507 / FREE_CAP 2000 = 25.35% (freeMinted adalah counter free; "
                    "freeClaimed()=130 adalah view berbeda yang tidak naik mengikuti mint — dicatat, bukan dipakai).")
f["userBalance"] = 0
f["claimedFree_user"] = 0
f["canFreeMint_user"] = 1
f["status"] = "strong-lead-gate-blocked-2026-11-05"
f["gateNote"] = ("STRONG LEAD run 1731 (dilaporkan sekali, gate-blocked, TIDAK di-mint): 3 kaki lolos — "
    "umur TERVERIFIKASI <=48 jam (first mint 2026-11-05 12:07:30 WIB), free 507/2000 = 25.35% terverifikasi, "
    "slot user terbuka (canFreeMint=1, claimedFree=0, balance 0). Velocity juga LULUS (1.74/mnt, 23.2x, +73). "
    "MANDATORY WEBSITE GATE GAGAL run 1731: metode (A) raw-address search nihil, (B) post Boltbook dibaca penuh tanpa link situs, "
    "(C) Sourcify metadata tanpa URL, (D) pola same-family tanpa bukti, (G) pencarian nama proyek nihil, "
    "(H) contractURI tidak ada di ABI, (I) tokenURI(1) base64 JSON tanpa external_url (run 1401), "
    "(J) grep ABI: tanpa fungsi site/url/domain/external, (M) site:vercel/pages/deed nihil. "
    "X UNVERIFIED (bukan blocker). TIDAK di-preview, TIDAK di-mint.")
f["baselineNote"] = ("PROMOTED ke strong lead run 1731 (dilaporkan sekali sebagai strong lead gate-blocked): "
    "first mint 2026-11-05 12:07:30 WIB (umur ~5.5 jam, terverifikasi), free 507/2000 = 25.35% terverifikasi, "
    "slot user terbuka. X UNVERIFIED; website gate GAGAL (lihat gateNote); velocity LULUS. Bukan kandidat. "
    "Tidak pernah di-preview/di-mint sebagai lead.")
f["runNote1731"] = ("Run 1731: PROMOSI early -> strong lead (freeMinted 507/2000 = 25.35%, umur terverifikasi, "
    "slot terbuka, velocity lulus) — dilaporkan sekali sebagai strong lead GATE-BLOCKED; TIDAK di-mint.")
f["lastReadBlock"] = BLK
f["lastReadWib"] = "2026-11-05 run 1731"

# --- MoonCat: age now VERIFIED; free % + slot stay UNVERIFIED ---
m = C["MoonCat"]
m["totalSupply"] = 686
m["firstMintBlock"] = 131782681
m["firstMintWib"] = "2026-11-05T15:12:25+07:00"
m["launchNote"] = ("First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero, address-filtered): "
                   "blok 131782681 = 2026-11-05 15:12:25 WIB; umur TERVERIFIKASI <=48 jam (~2.5 jam saat run 1731).")
m["ageVerified1731"] = True
m["freePctNote1731"] = ("Free % UNVERIFIED run 1731: freeClaimed/freeMinted/FREE_SUPPLY/FREE_CAP/MAX_SUPPLY semuanya "
    "tidak merespons (revert/tidak ada di kontrak); totalSupply 686, mintOpen 1, mintPrice 0 — tanpa free view, "
    "kaki % TIDAK BOLEH diganti % total supply.")
m["slotNote1731"] = ("Slot user UNVERIFIED run 1731: mintedBy/freeUsed/canFreeMint/claimedFree/quote semuanya tidak "
    "merespons; balanceOf(user)=0 saja.")
m["runNote1731"] = ("Run 1731: totalSupply 555->686 (+131); umur kini TERVERIFIKASI (first mint 15:12:25 WIB); "
    "free % + slot tetap UNVERIFIED (tanpa free view) -> tetap watchlist-only, BUKAN promosi.")
m["lastReadBlock"] = BLK
m["lastReadWib"] = "2026-11-05 run 1731"

# --- SEAT: age now VERIFIED; free % + slot stay UNVERIFIED ---
se = C["SEAT-f11e"]
se["totalSupply"] = 1321
se["MAX_SUPPLY"] = 5000
se["firstMintBlock"] = 131788954
se["firstMintWib"] = "2026-11-05T15:59:29+07:00"
se["launchNote"] = ("First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero, address-filtered): "
                    "blok 131788954 = 2026-11-05 15:59:29 WIB; umur TERVERIFIKASI <=48 jam (~1.7 jam saat run 1731).")
se["ageVerified1731"] = True
se["freePctNote1731"] = ("Free % UNVERIFIED run 1731: freeClaimed/freeMinted/FREE_SUPPLY/FREE_CAP semuanya tidak "
    "merespons; MAX_SUPPLY 5000 diketahui tapi alokasi free tidak diketahui — kaki % TIDAK BOLEH diganti % total supply.")
se["slotNote1731"] = ("Slot user UNVERIFIED run 1731: mintedBy(user)=0 + balanceOf(user)=0 terbaca, tapi "
    "canFreeMint/claimedFree/quote tidak merespons.")
se["runNote1731"] = ("Run 1731: totalSupply 726->1321 (+595); umur kini TERVERIFIKASI (first mint 15:59:29 WIB); "
    "free % + slot tetap UNVERIFIED (tanpa free view) -> tetap watchlist-only, BUKAN promosi.")
se["lastReadBlock"] = BLK
se["lastReadWib"] = "2026-11-05 run 1731"

# --- PassAgentX: free % stays UNVERIFIED ---
px = C["PassAgentX"]
px["totalSupply"] = 3389
px["freeMinted"] = 3185
px["freePctNote1731"] = ("Free % UNVERIFIED run 1731: FREE_SUPPLY/FREE_CAP tidak merespons; freeMinted 3185 dari "
    "MAX_SUPPLY 6666 tidak bisa dijadikan % free tanpa alokasi free. Umur terverifikasi (mintStart 2026-11-05 06:49:58 WIB).")
px["runNote1731"] = ("Run 1731: totalSupply 3289->3389 (+95); freeMinted 3185; free % tetap UNVERIFIED "
    "(tanpa FREE_SUPPLY) -> tetap early lead, BUKAN promosi.")
px["lastReadBlock"] = BLK
px["lastReadWib"] = "2026-11-05 run 1731"

# --- Track-C re-read notes (non-null only; null = failed read) ---
tc_reads = r["track_c"]
def tc_note(key, text):
    if key in TC and isinstance(TC[key], dict):
        TC[key][f"note1731"] = text

tc_note("QAGENT-2", "Run 1731: freeMinted 6666/6666 MAX_FREE — free pool TETAP HABIS (terkonfirmasi on-chain; klaim poster Boltbook 17:29 WIB cocok). Slot user sudah terpakai (freeClaimed_user=1). Tidak ada aksi.")
tc_note("ASOC-43cE", "Run 1731: saleEnded=0, freeClaimed_user=0 — MASIH BELUM BUKA; buka 20:00 WIB 2026-11-05. Tidak ada perubahan.")
tc_note("DROID", "Run 1731: freeMinted 453->562, totalMinted 561->562; opened gagal baca run ini (nilai lama 0 dipertahankan) — tetap belum dibuka.")
tc_note("IMARS", "Run 1731: totalMinted 624 (flat); free pool tetap 0 (300/300). Tidak ada perubahan.")
tc_note("Ikigai-Ihigi", "Run 1731: freeMinted 267 (flat). Tidak ada perubahan.")
tc_note("SAFUAI", "Run 1731: opened=1, totalMinted 10000. Status checked-not-a-lead; tidak ada perubahan.")
tc_note("NIULAI", "Run 1731: phase=4, launched=0. Tidak ada perubahan.")
tc_note("KillZero-K0-sale", "Run 1731: launched=0. Tidak ada perubahan.")
tc_note("SENBAZURU-b215", "Run 1731: hampir semua view gagal baca (null, RPC flaky); nilai lama dipertahankan (freeClaimed 232, paidSold 0/2000, hasFreeShare(user)=1). Deadline 2026-11-14 13:33 UTC.")
tc_note("OSK", "Run 1731: semua view gagal baca (null); nilai lama dipertahankan (opened 0). Tidak ada perubahan terverifikasi.")

# --- Excluded: BNB Bull (subagent B route 2, verified on-chain) ---
EX["BNB Bull"] = {
    "address": "0x0cbc2c5f9c5bdac24d98e71bf173192692050946",
    "status": "excluded-age-over-48h-2026-11-05",
    "name": "BNB Bull",
    "symbol": "BNFULL",
    "site": "moomoo.cloud/bnbull",
    "exclusionNote1731": ("Ditemukan route 2 run 1731 (post Boltbook EN FpEFS4gL9ukk). Website terverifikasi "
        "(skill.md mencetak kontrak persis + registry) DAN sale-shape lolos substansi, TAPI umur 70 jam 37 mnt "
        "saat baca (startTime 2026-11-02 19:00 WIB, blok 131802270) > 48 jam -> AGE-EXCLUDED; free baru 565/3000 "
        "(18,8%). Berakhir malam ini 19:00 WIB; launch mustahil (567/7000, butuh 6000). BUKAN lead, TIDAK dilaporkan "
        "sebagai lead; dicatat di sini agar tidak dilaporkan ulang bila ditemukan lagi."),
    "startTimeWib": "2026-11-02T19:00:00+07:00",
    "freeMinted": 565,
    "freeCap": 3000,
    "lastReadBlock": 131802270,
}
# BAGENT: free window closed — checked, not a lead, no track_c entry (nothing to watch)
EX["BAGENT"] = {
    "address": "0xE3baAd369B4C30E6c6bfB0ffc6658C4a66062D81",
    "status": "excluded-free-window-closed-2026-11-05",
    "name": "BAGENT",
    "exclusionNote1731": ("Ditemukan route 2 run 1731 (post F1 tracker). Registry terverifikasi, freeCount 377/1111, "
        "freeClaimed(user)=false, umur 46 jam 37 mnt (masih <=48 jam s.d. ~18:59 WIB) — TAPI freeWindowActive=false "
        "(window berakhir 2026-11-04 04:59 WIB) dan claimFree signature-gated: jalur gratis TUTUP, hanya berbayar. "
        "BUKAN lead; tidak masuk track_c (tidak ada yang dipantau)."),
}

# --- EARLY LEADS: 10-contract "costOf first-free" wave (parent deep-dive overturns
# subagent A STRICT verdict) ---
# Scan found 13 first-seen; the STRICT free-view test (freeMint/freeClaimed/etc.)
# failed for all 10 wave contracts because this template has NO free* views at all.
# Parent probe (run-2026-11-05-1731-followup.json + direct reads ~18:05 WIB) proves the
# free shape directly on-chain for EACH of the 10: agentIds() == registry
# 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F, price() = 0.0002 BNB, costOf(user,1) = 0
# (first mint FREE per wallet; 2nd+ mint 0.0002 BNB each), mintsLeft(user) = 10,
# mintedBy(user) = 0, mintOpen() = 1. First mints verified on-chain in this run.
# Template: mint(string,uint256) / mint(uint256) / mintWithAgentTokenId(uint256,uint256),
# all payable; owner-controlled (setPrice/setMintOpen/withdraw/treasury) — risk note.
# Same minter wallets recur across all 10 (0x0c931040..., 0x4283692d..., 0x64257b792c...).
# NEVER auto-minted/previewed as early leads. Nexus (1 mint, mintOpen 0), Crimson Vesper
# (1 mint) and Twin3 Agent Identity (registry FALSE, identity not a mint) are NOT leads.
WAVE = [
    ("Dumpster Royalty", "0xA5c88342455829fa6e6311cE444475E1a7Ff64A2", "DUMP", 150, 650, 131799659, "2026-11-05T17:19:32+07:00", 65, 65),
    ("SIDEWAYS", "0x8F1246Dc5556035a4921658d81A0E06427414aFF", "SIDE", 95, 555, 131799749, "2026-11-05T17:18:33+07:00", 23, 23),
    ("Hoard", "0x778C70f091f980fc057a59573CdCF23FBA3AaA72", "HOARD", 106, 640, 131799675, "2026-11-05T17:19:54+07:00", 22, 22),
    ("Slow & Steady", "0xa4b50B23145485e905182Bf763d792E3d91d1e4b", "SLOW", 98, 600, 131799701, "2026-11-05T17:18:46+07:00", 20, 20),
    ("Monke Business", "0xbCc595ba692188a499026cD9dC0E6DF00b19D1ec", "MONKE", 90, 700, 131799649, "2026-11-05T17:19:09+07:00", 15, 15),
    ("Very Good Boys", "0x29Adf4D894CCde764237270444444aEC308dD905", "VGB", 91, 680, 131799649, "2026-11-05T17:19:31+07:00", 14, 14),
    ("Do Not Disturb", "0x95b8fC65C67078dCFe4aA9A2F892B82e43b33a06", "DND", 96, 525, 131799663, "2026-11-05T17:19:36+07:00", 13, 13),
    ("Moth Club", "0x48C3aE8E8129EFa9D20800aC8932D8b51f85C0F0", "MOTH", 67, 666, 131800045, "2026-11-05T17:19:32+07:00", 13, 13),
    ("Snail Mail", "0xb773e52fE45196c840F8e59c3B4bB944633Ae03a", "SNAIL", 99, 500, 131799691, "2026-11-05T17:19:32+07:00", 11, 11),
    ("wheelz", "0x5aCC0Ec4449Edb788f43803cDb1A11f1f6b7E64d", "WHEELZ", 87, 620, 131800104, "2026-11-05T17:19:30+07:00", 10, 10),
]
for name, addr, sym, ts, maxs, first_blk, first_wib, wm, wmin in WAVE:
    C[name] = {
        "address": addr,
        "name": name,
        "symbol": sym,
        "kind": "ERC721",
        "status": "early-lead-reported-2026-11-05",
        "totalSupply": ts,
        "MAX_SUPPLY": maxs,
        "firstSeenBlock": first_blk,
        "firstMintWib": first_wib,
        "scanMints": wm,
        "scanMinters": wmin,
        "scanWindow": "131799645-131801644",
        "lastReadBlock": 131801644,
        "lastReadWib": "2026-11-05 run 1731",
        "xVerified": False,
        "velocityVerified": False,
        "launchNote": (f"First mint terverifikasi on-chain: blok {first_blk} = {first_wib} "
                       "(Ankr getLogs, earliest-mint check run 1731); umur TERVERIFIKASI <=48 jam."),
        "freeShapeNote": ("Template 'costOf first-free' (BARU — detektor free-shape scan tidak mengenalinya): "
            "agentIds() == registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F; price() = 0.0002 BNB; "
            "costOf(user,1) = 0 -> mint PERTAMA GRATIS per wallet, mint ke-2+ 0.0002 BNB; mintsLeft(user) = 10; "
            "mintedBy(user) = 0; mintOpen() = 1. TIDAK ADA fungsi freeMint/freeClaimed/freeLeft — free-ness "
            "dibuktikan via costOf, BUKAN preview (early lead tidak pernah di-preview)."),
        "slotNote": "Slot user TERBUKA per baca on-chain (mintedBy 0, mintsLeft 10, costOf(user,1)=0) — belum preview-verified.",
        "baselineNote": ("EARLY lead dilaporkan sekali run 1731 (gelombang 10 kontrak, minter sama berulang). "
            "Agent-shaped: registry on-chain + mintWithAgentTokenId/agentIds; free pertama terverifikasi via costOf. "
            "Bukan strong lead (free % model 1-per-wallet, tanpa free cap — kaki 25% tidak terpetakan bersih), bukan kandidat "
            "(X unverified, website unverified, velocity belum terhitung). TIDAK di-preview/di-mint sebagai early lead. "
            "Catatan risiko: owner-controlled (setPrice/setMintOpen/withdraw/treasury); minter sama lintas 10 kontrak."),
        "previousTotalSupply": ts,
        "previousRatePerMin": None,
        "velocityLegPasses": False,
        "velocityNote": "Run 1731: baseline pertama disimpan; velocity belum terhitung (butuh rate sebelumnya).",
        "runNote1731": f"Run 1731: EARLY lead baru (first-seen scan); totalSupply {ts}/{maxs} saat probe ~18:05 WIB.",
    }

s["runNote1731_scan"] = ("Scan rute 4 SUKSES: jendela 131799645-131801644 (2000 blok, cap); gap 131797041-131799644 "
    "(2604 blok) dilewati dan dicatat; 80 panggilan Ankr, 0 error; 300 kontrak (237 ERC721 + 8 ERC1155 + sisanya) "
    "dan 504 ERC-20 mint contracts. Watermark maju ke 131801644. First-seen 13 (10 gelombang costOf + Nexus + "
    "Crimson Vesper + Twin3). Parent probe membuktikan 10 gelombang sebagai EARLY lead (template costOf first-free); "
    "Nexus (mintOpen 0), Crimson Vesper, Twin3 (bukan mint) BUKAN lead. Rute 5c: 2 ERC-20 dicek bentuk sale, keduanya "
    "GAGAL (tanpa ABI), tercatat di track-c-scan-checked.json (total 1848); 0 lead track-C. Feed sale-shape: 2 target, "
    "keduanya token polos, bukan sale.")

s["timestamp_wib"] = "2026-11-05 run 1731"
s["last_run_wib"] = "2026-11-05 run 1731"
s["last_run_note"] = ("Run 1731: 1 PROMOSI (Forklings early->strong lead, gate-blocked, TIDAK di-mint, dilaporkan sekali); "
    "10 EARLY LEAD BARU (gelombang template 'costOf first-free': Dumpster Royalty, SIDEWAYS, Hoard, Slow & Steady, "
    "Monke Business, Very Good Boys, Do Not Disturb, Moth Club, Snail Mail, wheelz — dilaporkan sekali, TIDAK di-preview/di-mint); "
    "0 kandidat baru; 0 track-C lead/kandidat baru; 0 track-B claim; "
    "BNB Bull age-excluded; BAGENT free-window-closed; QAGENT free pool tetap habis; ASOC buka 20:00 WIB; "
    "MoonCat + SEAT umur kini terverifikasi (free % + slot tetap unverified, watchlist-only).")
s["runNote1731"] = s["last_run_note"]

# merge scan decisions if parent wrote them (subagent A first-seen handling)
import os
dec_path = f"{BASE}/run-2026-11-05-1731-scan-decisions.json"
if os.path.exists(dec_path):
    dec = json.load(open(dec_path))
    for item in dec.get("add_to_excluded", []):
        EX[item["name"]] = item["entry"]
    s["runNote1731_scan"] = dec.get("note", "")
    print("merged scan decisions:", len(dec.get("add_to_excluded", [])))

json.dump(s, open(snap_path, "w"), indent=1)
print("snapshot updated; contracts:", len(C), "track_c:", len([k for k in TC if isinstance(TC[k], dict)]),
      "excluded:", len(EX), "pending_claims:", s.get("pending_claims"))
