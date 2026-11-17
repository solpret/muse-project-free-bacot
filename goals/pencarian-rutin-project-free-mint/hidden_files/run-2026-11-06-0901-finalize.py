#!/usr/bin/env python3
"""Run 2026-11-06 0901 WIB finalize.
1. Snapshot: re-read values + velocity notes (None never overwrites);
   factory contracts keep supplyView=totalMinted (their totalSupply() reads MAX 3333).
2. Crack -> track_c minted-by-user-2026-11-06 (track-C lead direct mint, full evidence).
3. bridge-0x636fdfa9 -> snapshot contracts as bridge finding (NOT a lead, no report).
4. Cipher Mind + Cyber Lynx Agent -> early leads (agent-shaped, first mint verified).
5. OUPE Cards (0xCa88, 2nd contract same name) + intermediateCrack (0x8ED2) +
   Voting Escrow ApeBond -> checked-not-agent-shaped, log only (already in seen).
6. last_run fields + scan-state note.
Backs up snapshot + seen file first. Never touches scan-bridge.json."""
import json, shutil

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0901"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0901")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-0901")

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap.setdefault("contracts", {})
TC = snap.setdefault("track_c", {})
REREAD = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
BLK = REREAD["block"]

def setv(entry, key, val):
    if val is not None:
        entry[key] = val

# ---------- 1. Re-read numeric updates (None never overwrites) ----------
# NOTE: factory contracts' totalSupply() reads MAX (3333); velocity uses totalMinted.
NUMMAP = {
 "HIVE Agents": [("totalSupply", "totalSupply")],
 "KING Agent": [("totalMinted", "totalMinted"), ("remainingFree", "remainingFree")],
 "Mummyhive": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Thronemind": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Hashseers": [("freeMinted", "freeMinted")],
 "Smeltbots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Forklings": [("freeMinted", "freeMinted")],
 "Agent Frogs": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "PassAgentX": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "SEAT-f11e": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "LuckyBox-d08e": [("totalSupply", "totalSupply")],
 "Tumblebots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Mossminds": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Jolly": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted")],
 "AgentGlyph": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Layerloom": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Pacture": [("freeMinted", "freeMinted")],
 "Nebula Ape Agent": [("totalMinted", "totalMinted")],
 "Shadow Yeti Agent": [("totalMinted", "totalMinted")],
 "Silent Hydra Agent": [("totalMinted", "totalMinted")],
 "Cipher Wraith Agent": [("totalMinted", "totalMinted")],
 "Umbra Lynx Agent": [("totalMinted", "totalMinted")],
 "Data Synth": [("totalMinted", "totalMinted")],
 "Zero Genesis": [("totalMinted", "totalMinted")],
}
for name, pairs in NUMMAP.items():
    if name not in C or name not in REREAD["reread"]:
        continue
    src = REREAD["reread"][name]
    for dst, sk in pairs:
        setv(C[name], dst, src.get(sk))
    C[name]["lastReadBlock"] = BLK
    C[name]["lastReadWib"] = "2026-11-06 run 0901"
    if "balanceOf_user" in src:
        setv(C[name], "balanceOf_user", src.get("balanceOf_user"))
    if "mintedBy_user" in src:
        setv(C[name], "mintedBy_user", src.get("mintedBy_user"))

# ---------- Velocity / run notes ----------
C["HIVE Agents"]["runNote0901"] = ("Run 0901 (blok 131927703): totalSupply 1253 flat vs run 0801 (1253) -> velocity GAGAL; "
    "balanceOf(user)=1; minted-by-user, bukan kandidat.")
C["KING Agent"]["runNote0901"] = ("Run 0901 (blok 131927703): totalMinted 649->708 (+59, ~64,4 mnt blok 131919121->131927703 = ~0,92/mnt "
    "vs prev ~0,81/mnt = ~1,13x) -> velocity GAGAL (butuh >=1,5x DAN >=20 token; token terpenuhi, rasio gagal). "
    "Claimed 708/3333=21,24% <25% kaki strong-lead. Slot user terbuka (costOf 0, mintedBy 0, balance 0, agentGateOn 1, mintOpen 1). Tetap EARLY.")
C["KING Agent"]["previousTotalSupply"] = 649
C["KING Agent"]["mintedInInterval"] = 59
C["KING Agent"]["intervalMinutes"] = 64.4
C["KING Agent"]["currentRatePerMin"] = 0.92
C["KING Agent"]["previousRatePerMin"] = 0.81
C["KING Agent"]["velocityLegPasses"] = False
C["MILLION"]["runNote0901"] = ("Run 0901 (blok 131927703): SEMUA view gagal baca (totalSupply/totalMinted/freeClaimed/freeMinted/balanceOf = None) - "
    "degradasi RPC, BUKAN nol; nilai lama dipertahankan, velocity TIDAK dihitung. Tetap EARLY.")
C["FOD Agent"]["runNote0901"] = ("Run 0901 (blok 131927703): SEMUA view gagal baca (None) - degradasi RPC, BUKAN nol; nilai lama dipertahankan, "
    "velocity TIDAK dihitung. Tetap EARLY.")
for n in ["Nebula Ape Agent", "Shadow Yeti Agent", "Silent Hydra Agent", "Cipher Wraith Agent", "Umbra Lynx Agent",
          "Data Synth", "Zero Genesis"]:
    C[n]["runNote0901"] = ("Run 0901 (blok 131927703): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB - "
        "tidak ada pergerakan sejak baseline. Tetap EARLY.")
C["Forklings"]["runNote0901"] = ("Run 0901: freeMinted 927->935 (+8, <20) -> velocity GAGAL; 935/2000=46,75% <50% kaki kandidat; "
    "gate-blocked strong lead; slot user terbuka (balance 0). Tanpa promosi.")
C["Agent Frogs"]["runNote0901"] = ("Run 0901: totalSupply 434->437 (+3), freeClaimed 437/1111=39,32%; gate-blocked strong lead; "
    "slot user terbuka. Tanpa promosi.")
C["PassAgentX"]["runNote0901"] = ("Run 0901: totalSupply 3961->3980 (+19), freeMinted 3744->3766 (+22). Tanpa sellout/promosi.")
C["SEAT-f11e"]["runNote0901"] = ("Run 0901: totalSupply 3362->3532 (+170, ~2,24/mnt vs prev ~4,8 = ~0,47x) -> velocity GAGAL; "
    "free % unverified; watchlist-only.")
C["Thronemind"]["runNote0901"] = "Run 0901: totalSupply 668, freeMinted 668 (+3 vs 0801). Tanpa sellout/promosi."
C["Hashseers"]["runNote0901"] = "Run 0901: freeMinted 602 (+3 vs 0801); totalSupply gagal baca (nilai lama dipertahankan). Tanpa sellout/promosi."
C["Smeltbots"]["runNote0901"] = "Run 0901: totalSupply/freeMinted 619 (+2 vs 0801). Tanpa sellout/promosi."
C["Mossminds"]["runNote0901"] = "Run 0901: totalSupply 927, freeMinted 924 (+12/+15 vs 0801). Tanpa sellout/promosi."
C["Jolly"]["runNote0901"] = "Run 0901: totalMinted/freeMinted 3660 (+10 vs 0801). Tanpa sellout/promosi."
C["AgentGlyph"]["runNote0901"] = "Run 0901: freeClaimed 512/512 - sold out, sudah tercatat; totalSupply 513 (1 paid mint). Tanpa perubahan."
C["Mummyhive"]["runNote0901"] = "Run 0901: totalSupply 600, freeClaimed 582. Tanpa sellout/promosi."
C["Pacture"]["runNote0901"] = "Run 0901: freeMinted 7700; freeClaimed(user)=1. Tanpa perubahan status."
C["Layerloom"]["runNote0901"] = "Run 0901: totalSupply/freeMinted 685. Tanpa sellout/promosi."
C["Tumblebots"]["runNote0901"] = "Run 0901: totalSupply/freeMinted 665. Tanpa sellout/promosi."

# Track-C re-read notes (from run-0901-reread-lean.json track_c)
TCR = REREAD["track_c"]
snap["trackC_note0901"] = ("Run 0901 (blok 131927703): OSK totalMinted 2278 flat (opened gagal baca), tetap belum dibuka; "
    "DROID opened 0, freeMinted 603->604 (+1), tetap belum dibuka; IMARS opened 1, freeMinted 300/300 (pool gratis HABIS - diketahui sejak run 0601, BUKAN lead), "
    "totalMinted 624 flat; QAGENT-2 sharesMinted 6702 flat vs 0801 (freeClaimed(user)=1, claimed-by-user); SENBAZURU opened 1, phase 1, hasFreeShare(user)=1 (claimed-by-user); "
    "SAFUAI totalMinted 10000 flat; KillZero launched 0; ShibAgent launched 0, phase 1; Ikigai phase 3; ASOC saleEnded 0, freeClaimed(user)=0. "
    "NIULAI/FABE/DeY/BoxBigem/FANBEIMAO/Hongbao/Nvagent/Soarm: semua view gagal baca run ini (nilai lama dipertahankan). Tanpa perubahan status track-C.")

# ---------- 2. Crack -> track_c minted-by-user ----------
TC["Crack"] = {
 "sale": "0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09",
 "token": "0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09",
 "status": "minted-by-user-2026-11-06",
 "saleShape": "PASS (S1+S2): mint/mintCost/freeMint/freeUsed + PRICE/quote + agentId/hasAgentId/requireAgentId gates (AGENT_REGISTRY=0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F), Sourcify verified, 70 functions",
 "name": "Crack",
 "symbol": "VAULT",
 "kind": "ERC721",
 "totalSupply": 794,
 "totalMinted": 794,
 "MAX_SUPPLY": 5555,
 "publicRemaining": 4711,
 "reserve": 250,
 "reserveMinted": 200,
 "mintMode": 2,
 "mintModeName": "FIRST FREE",
 "price": 1000000000000000,
 "mintOpen": 1,
 "mintCost_user_1": 0,
 "freeUsed_user": 1,
 "hasAgentId_user": 1,
 "userBalance": 1,
 "mintedBy_user": 1,
 "walletInfo_user": [1, 1, 0, 10],
 "ageNote": "VERIFIED <=48h: first mint Transfer-from-zero blok 131921262 = 2026-11-06 08:32:01 WIB (Ankr getLogs address-filtered 131900000..131921703: 29 mints, earliest 131921262; totalSupply 0 di blok 131921261 dan 1 di blok 131921262; 0 ConsecutiveTransfer di range yang sama). Sourcify verifiedAt 2026-11-06T01:33:01Z (08:33 WIB). Umur ~1 jam saat mint.",
 "gateNote": "Website TERVERIFIKASI run ini: vaultcrack.xyz - SITE() + contractURI external_link https://vaultcrack.xyz; /config.js (HTTP 200) mencetak kontrak persis 0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09 + X https://x.com/vault_crack + registry + renderer 0xD37424118a489608a4dae20Edf36F789C21f15b3. X @vault_crack sebagai bukti tambahan.",
 "xNote": "X https://x.com/vault_crack (dari config.js situs proyek, bukti tambahan; bukan gate).",
 "auditNote": "Binance audit run 0901: code 000000, hasResult=false (TANPA HASIL, bukan lolos), isSupported=true, riskLevel -1, riskItems 0 - tanpa hit RISK.",
 "previewNote": "Preview bersih 000000000 (requestId b154fd715edd4dc895d69094776f79e0): mint(1) value 0, simulationErrorDetail null, balanceChanges +1 ERC721 (simulasi tokenId 790), allowanceChanges [], authorityChanges [], risks kosong.",
 "mintTx": "0xf3c1478fc8f66b3dc669a18858fb8e321c65e843f121f3607686854e8de2e41a",
 "mintBlock": 131928533,
 "mintGas": 194544,
 "mintTokenId": 792,
 "mintOrderId": "26110600002022875192",
 "mintNote": ("TRACK-C LEAD DIRECT MINT run 0901 (otorisasi 2026-11-02): sale-shape S1+S2 + free pool 4723 + slot user terbuka "
   "(freeUsed 0, mintCost 0, hasAgentId 1, walletInfo freeAvailable) + umur terverifikasi ~1 jam + gate website lolos + audit tanpa hasil (bukan lolos) + preview bersih. "
   "Token receipt 792 (simulasi menyebut 790 - 2 mint lain mendarat di antara preview dan eksekusi; jumlah simulasi +1 NFT cocok). "
   "Verifikasi pasca: receipt status 1, balanceOf(user) 0->1, ownerOf(792)=wallet, freeUsed 0->1, mintedBy 0->1, totalMinted 782->794 (termasuk mint lain). "
   "Mint berikutnya BERBAYAR (0,001 BNB) - TIDAK diotorisasi."),
 "rarityNote": "Tier not verified (tanpa trait Rarity/Tier). tokenURI traits: Vault=Locker, Loot=Cash, Code=22·96·97, Code pattern=None, Jackpot=No, Alarm=Silent, Origin=Free mint, Era=1. Appended to nft-rarity-inventory.md.",
 "marketplaceNote": ("No live venue verified: situs proyek vaultcrack.xyz hanya mint (tanpa halaman market/trade/floor di home maupun app.js); "
   "pencarian web kontrak + marketplace tanpa hasil yang cocok kontrak. TIDAK di-list; Element hanya fallback manual (tidak dieksekusi)."),
 "lastReadBlock": 131928533,
 "lastReadWib": "2026-11-06 run 0901",
 "firstSeenWib": "2026-11-06 hot-leg 0833 (Sourcify feed); first mint 08:32:01 WIB; lead diverifikasi umur oleh job utama run 0901",
}

# ---------- 3. Bridge finding 0x636fdfa9 (NOT a lead, no report) ----------
C["bridge-0x636fdfa9"] = {
 "address": "0x636fdfa9bc3db42c690c09e87b9017d05b36c743",
 "status": "bridge-finding-not-a-lead-2026-11-06",
 "source": "scan-tracked (bridge file, run-70 tracked-wallet scan)",
 "note": ("Temuan pelengkap scan (bridge 2026-11-06 hot-leg 0854: 1 not in snapshot): Unnamed ERC20 (name/symbol kosong on-chain, decimals 18, "
   "totalSupply 913191475743305484379828919270124) mint-pattern PAID (tx value 0,15 BNB), 1 entity only (AFeng, feed-only) - finding, NOT a signal/lead, "
   "NOT auto-mint. Via sale contract 0x1de460f363af910f51726def188f9004276bf4bc + selector 0x4d819a2a (sama seperti temuan ETHBack_Dividen_Tracker run-3); "
   "kontrak kemungkinan dividend tracker, klasifikasi mint di luar Transfer zero-address tidak terverifikasi. Owner 0x10b389eed857fdb84089a64188aab6afbbe2cc2a. "
   "Gate website_no_pointer_found (contractURI() revert di 2 RPC langsung - fungsi tidak ada, bukan gagal baca; Sourcify 404 unverified; tokenURI n/a ERC20). "
   "Ditambahkan ke snapshot watchlist run 0901 sebagai temuan pelengkap scan; TIDAK dilaporkan sebagai lead (tidak memenuhi tier Free Bacot apa pun)."),
 "same_owner_discarded": False,
 "first_seen": "run-70 (2026-11-06 07:05 WIB window, mint 07:12:50 WIB)",
 "website": None,
 "gate": "website_no_pointer_found",
 "lastReadWib": "2026-11-06 run 0901",
}

# ---------- 4. New early leads: Cipher Mind + Cyber Lynx Agent ----------
tri = json.load(open(f"{BASE}/run-{TS}-scan-triage.json"))
tri_by_addr = {r["address"].lower(): r for r in tri["nft_first_seen"]}
probe = json.load(open(f"{BASE}/run-{TS}-early-probe.json"))
for name, addr, sym, fb, fmt in [
 ("Cipher Mind", "0x3226B724d9F81c4E09E6E07b75532e01e6f5c7B7", "CPM", 131926871, "2026-11-06 09:14:06 WIB"),
 ("Cyber Lynx Agent", "0x5189EAEB67d2A799CD9094AEc4Af6eb76C6E073b", "CYBL", 131927568, "2026-11-06 09:19:19 WIB"),
]:
    st = probe["state"][name]
    C[name] = {
     "address": addr,
     "status": "early-lead-reported-2026-11-06",
     "name": name,
     "symbol": sym,
     "kind": "ERC721",
     "totalSupply": None,
     "totalMinted": 1,
     "freeClaimed": None,
     "FREE_SUPPLY": None,
     "MAX_SUPPLY": 3333,
     "PRICE": 500000000000000,
     "mintOpen": None,
     "userMintedBy": 0,
     "userFreeUsed": None,
     "userBalance": 0,
     "userSlotNote": "Slot UNVERIFIED: mintedBy(user)=0, balanceOf(user)=0, quote(user,1) unreadable - NOT preview-verified (early leads are never previewed).",
     "firstSeenBlock": fb,
     "scanWindow": "131926748-131927747",
     "scanMints": 1,
     "scanMinters": 1,
     "lastReadBlock": BLK,
     "lastReadWib": "2026-11-06 run 0901",
     "xVerified": False,
     "velocityVerified": False,
     "launchNote": (f"First mint VERIFIED on-chain: first Transfer-from-zero at block {fb} = {fmt} "
       f"(Ankr getLogs address-filtered 131919215..{fb-1}: 0 earlier mints; totalMinted=1 confirms the window mint is the only mint). "
       f"No project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. "
       f"First-seen by this job in run 0901 via route-4 scan (true first-seen: absent from seen['contracts'] + snapshot)."),
     "baselineNote": ("EARLY lead reported once 2026-11-06 run 0901. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI "
       "(mint/minted/mintedBy/totalMinted + PRICE/quote + AGENT_REGISTRY gate). Free % UNVERIFIED (no free views); X UNVERIFIED; "
       "velocity baseline pertama (totalMinted 1). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
     "previousTotalSupply": 1,
     "mintedInInterval": 0,
     "intervalMinutes": 0,
     "currentRatePerMin": None,
     "previousRatePerMin": None,
     "velocityLegPasses": False,
     "velocityNote": "Run 0901: baseline pertama (totalMinted 1) - velocity belum terhitung.",
     "supplyView": "totalMinted",
    }

# ---------- 5. Checked-not-agent-shaped (log only; already in seen) ----------
snap["checkedNotAgentShaped0901"] = {
 "OUPE Cards 0xCa8820D36BEC22E462a45B6F658d3f7BB2542a82": ("Second contract same-name OUPE Cards (beda dari 0xeFe2... run 0801): 78 mints/78 minters window ini, "
   "first block 131926748 (window start). Sourcify retry-exhausted (triage + scan); probe 9-selector hanya freeClaimed() hit (freeClaimed 327), "
   "tanpa agentRegistry/AGENT_ID/FREE_SUPPLY/PRICE/quote/mintOpen. Registry-bytes hit saja TIDAK cukup. BUKAN early lead; log only, masuk seen."),
 "intermediateCrack 0x8ED2139bE8Ac9598E513959ED8922FaB1781122f": ("Kontrak pendamping Crack (disebut 'intermediateCrack' di vaultcrack config.js): 14 mints window ini, "
   "totalMinted 382, MAX_SUPPLY 7777, mintOpen 1, mintedBy(user)=0. Sourcify not_verified; probe 9-selector hanya totalMinted/mintOpen/mintedBy hit, "
   "tanpa registry/AgentGate/free view/PRICE/quote. BUKAN agent-shaped, BUKAN lead; log only, masuk seen. Bagian dari alur game Crack, bukan lead mandiri."),
 "Voting Escrow ApeBond 0xDF1dD618f3B564765e3ffc9F229637942ef601B2": ("1 mint window ini; registry_bytes_hit False; Sourcify not_verified. BUKAN agent-shaped; log only, masuk seen."),
 "Crack 0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09": ("First-seen scan run ini (65 mints window) TAPI first mint 131921262 (08:32 WIB) SEBELUM window - first_mint_verified=False untuk window ini. "
   "Sudah ditangani sebagai track-C lead + minted-by-user run ini (lihat track_c.Crack); BUKAN early lead."),
}

snap["last_run_wib"] = "2026-11-06 run 0901"
snap["last_run_note"] = ("Run 0901: TRACK-C LEAD DIRECT MINT Crack #792 (tx 0xf3c1478fc8f66b3dc669a18858fb8e321c65e843f121f3607686854e8de2e41a, blok 131928533, "
    "receipt 1, gas 194544) + 2 EARLY leads baru (Cipher Mind, Cyber Lynx Agent - dilaporkan sekali run ini) + 1 temuan pelengkap scan (bridge 0x636fdfa9, bukan lead). "
    "Scan route 4 SUKSES (pre-flight OK 5,0 dtk, cap 1000 blok, 40 panggilan Ankr, 0 error; window 131926748-131927747; 162 NFT + 309 ERC20-mint; shape-check 762 dtk total, nyaris timeout 780). "
    "KING 708/3333=21,24% velocity GAGAL; HIVE 1253 flat; MILLION/FOD semua view gagal baca (nilai lama dipertahankan); SEAT 3532 velocity GAGAL; "
    "Forklings 935/2000=46,75%; Data Synth/Zero Genesis/trio tetap totalMinted 1. "
    "Boltbook newest post unchanged (2026-11-05T09:20:52Z); sweep tanpa proyek baru; Sourcify 5a 4 baru dicek (0 sale-shape); "
    "5c: 3 ERC-20 baru dicek (0 sale-shape); Odaily/PANews 0 mention; bridge 1 not-in-snapshot (0x636fdfa9, bukan lead); binanceai tetap refund/failed. "
    "OUPE Cards ke-2 + intermediateCrack + Voting Escrow: bukan agent-shaped (log only).")
snap["runNote0901"] = snap["last_run_note"]
snap["runNote0901_scan"] = ("Run 0901: SCAN SUKSES (amendment 2026-11-06 ~07:49: pre-flight ankr_getLogs 50 blok OK 5,0 dtk <60 dtk; "
    "window cap 1000 blok; per-chunk progress log + flush, 20/20 chunk selesai). Window 131926748-131927747, 162 NFT + 309 ERC20-mint contracts, "
    "40 panggilan Ankr, 0 error. Watermark 131919214 -> 131927747. Gap 131919215-131926747 (7.533 blok) belum ter-cover (backfill). "
    "Shape-check phase lambat (total run 762 dtk, nyaris timeout 780) - risiko JSON hilang bila shape mati; perlu penulisan parsial / pemisahan shape-check.")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT updated: contracts", len(C), "track_c", len(TC), "excluded", len(snap.get("excluded", {})), flush=True)

st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0901_finalize"] = ("Run 0901 finalize: triage nested-seen fix dipakai (raw first-seen 6 = true 6, tanpa inflasi top-level-keys); "
    "2 early leads baru (Cipher Mind, Cyber Lynx Agent) + Crack ke track_c (minted) + bridge-0x636fdfa9 ke contracts (bukan lead). "
    "Watermark tetap 131927747 (main scan); backfill gap 131919215-131926747 belum ter-cover.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("STATE noted", flush=True)
print("FINALIZE DONE", flush=True)
