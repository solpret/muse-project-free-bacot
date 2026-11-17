#!/usr/bin/env python3
"""Finalize FREE BACOT run 2026-11-07 21:31 WIB (run 2131).
Applies leg-1 reread + velocity + age-sweep to onchain-snapshot.json,
adds Paw Gang (EARLY lead, leg-2 verified) + AgentBook (STRONG lead,
gate-blocked, parent-verified), removes Ember Byte (age-excluded 49.5h),
updates King's Game + Agent Grove re-reads, updates last_run + run notes.
Writes snapshot + scan-state note only. Watermark NOT advanced (backfill owns it)."""
import json, os

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
BLOCK = 132217477

snap = json.load(open(HF + "onchain-snapshot.json"))
reread = json.load(open(HF + "run-2026-11-07-2131-reread.json"))
vel = json.load(open(HF + "run-2026-11-07-2131-velocity.json"))
age = json.load(open(HF + "run-2026-11-07-2131-age-sweep.json"))
paw = json.load(open(HF + "run-2026-11-07-2131-pawgang-extra.json"))
abook = json.load(open(HF + "run-2026-11-07-2131-agentbook-verify.json"))

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
    c["lastReadWib"] = "2026-11-07 run 2131"
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
    c["runNote2131"] = ("Run 2131 (blok %d): totalSupply %s, minted interval %s, velocity %s."
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
    t["lastReadWib"] = "2026-11-07 run 2131"

# --- Age exclusion: Ember Byte (verified >48h, not sold out) ---
ember = snap["contracts"].pop("Ember Byte", None)
ember_note = None
if ember is not None:
    ember_note = ("AGE-EXCLUDED run 2131: first mint terverifikasi 2026-11-05 20:01:17 WIB "
                  "(49,5 jam pada run ini, >48 jam); spot sale BERBAYAR 0,001 BNB/spot, "
                  "1/5.000 spot terjual (spotsLeft 4.999) — jelas belum sold out; status "
                  "watchlist-only sejak 2026-11-05, tidak pernah dilaporkan sebagai lead; "
                  "totalSupply 1e27 adalah artefak ERC-20, metrik yang menentukan adalah spots. "
                  "Dihapus dari snapshot contracts run 2131.")
    snap.setdefault("excluded", {})["Ember Byte"] = {
        "address": "0xeC8A897a0De48a6fbfb83646f790581a2280aDB3",
        "name": "Ember Byte", "symbol": "EMBB", "kind": "ERC20",
        "track": "A", "status": "age-excluded-2026-11-07",
        "note": ember_note,
    }

# --- Paw Gang EARLY lead (leg-2 verified; first-seen scan run 2001) ---
snap["contracts"]["Paw Gang"] = {
    "address": "0x587C303982187Ec578dF309d27670327b13202F8",
    "name": "Paw Gang", "symbol": "PAWG", "kind": "ERC721",
    "status": "early-lead-2026-11-07",
    "firstSeenBlock": 132207681,
    "firstMintWib": "2026-11-07 20:00:00 WIB",
    "scanWindow": "132207681-132208680",
    "scanMints": 19, "scanMinters": 19,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "registry_match": True,
    "totalSupply": 313, "totalMinted": 313,
    "FREE_SUPPLY": 3333, "MAX_SUPPLY": 3333,
    "freePctInference": 9.4,
    "freePctNote": ("Inference only: totalMinted 313/3333 (blok 132218094, tumbuh live 286->308->313); "
                    "tidak ada view freeMinted/freeClaimed di kontrak — % BUKAN counter gratis terverifikasi."),
    "freePctVerified": None,
    "mintOpen": 1,
    "freeClaimed_user": None,
    "balanceOf_user": 0,
    "hasMinted_user": 0,
    "website": "https://pawgang.pages.dev",
    "gate": ("website TERVERIFIKASI: pawgang.pages.dev mencetak kontrak NFT persis + registry + "
             "marketplace 0xaD1fF1200091CC9049F666357Cd6e5B38C2B4739; /agent.json sama. "
             "Akun X TIDAK ditemukan — opsional, tidak meng-gate."),
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Launch TERVERIFIKASI ≤48 jam: MINT_START()=1794056400 = 2026-11-07 13:00:00 UTC "
                   "(20:00 WIB hari ini), sama dengan opensAtUtc di agent.json; totalMinted tumbuh live."),
    "note": ("EARLY lead run 2131 (dilaporkan sekali): first-seen scan run 2001 (19 mint/19 minter) TAPI "
             "saat itu triase run 2001 melabeli 'likely PAID-ONLY' karena free view kosong — label itu "
             "DIKOREKSI run 2131: price 0 menurut agent.json, mint PoW mint(uint256 nonce), maks 1/wallet, "
             "gate registry balanceOf>0, mintOpen=1, AGENT_REGISTRY()=registry 0x60B9...022F on-chain. "
             "9,4% < 25% strong-lead dan < 50% kandidat; velocity UNVERIFIED (bacaan pertama). "
             "TIDAK PERNAH di-preview/di-mint sebagai early lead; promosi ke strong lead bila free% >=25%."),
    "lastReadBlock": 132218094,
    "lastReadWib": "2026-11-07 run 2131",
}

# --- AgentBook STRONG lead, GATE-BLOCKED (parent-verified block 132220450) ---
snap["contracts"]["AgentBook"] = {
    "address": "0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0",
    "name": "AgentBook", "symbol": "ABOOK", "kind": "ERC721",
    "status": "strong-lead-gate-blocked-2026-11-07",
    "firstSeenBlock": 132216769,
    "firstMintWib": "2026-11-07 21:29:09 WIB",
    "scanWindow": "132216460-132217459",
    "scanMints": 75, "scanMinters": 55,
    "agentRegistry": "0x60b9262456de011f7d15a54cdd8c48baaa8b022f",
    "registry_match": True,
    "totalSupply": abook.get("totalSupply"),
    "totalMinted": abook.get("totalSupply"),
    "FREE_QUOTA": abook.get("FREE_QUOTA"),
    "remainingFree": abook.get("remainingFree"),
    "MAX_SUPPLY": abook.get("MAX_SUPPLY"),
    "MAX_PER_WALLET": abook.get("MAX_PER_WALLET"),
    "PAID_PRICE": abook.get("PAID_PRICE"),
    "mintOpen": abook.get("mintOpen"),
    "soldOut": abook.get("soldOut"),
    "agentGateOn": abook.get("agentGateOn"),
    "freePctVerified": 59.5,
    "freePctNote": ("TERVERIFIKASI: FREE_QUOTA 333, remainingFree 135 -> free claimed 198/333 = 59,5%; "
                    "totalSupply 198 (semua mint sejauh ini gratis; berbayar 0,0005 BNB baru sesudah 333)."),
    "costOf_user_1": abook.get("costOf_user_1"),
    "freeUsed_user": abook.get("freeUsed_user"),
    "mintedBy_user": abook.get("mintedBy_user"),
    "balanceOf_user": abook.get("balanceOf_user"),
    "freeClaimed_user": None,
    "contractURI": "data:application/json;base64 (tanpa external_link; deskripsi: first 333 mints free for Binance .ai Agent ID holders, then 0.0005 BNB, max 2/wallet; roles Lurker 60% / Reply Guy 25% / Poster 10% / Moderator 4% / Whale 1%; 5% royalties to owner)",
    "xVerified": False, "velocityVerified": False,
    "launchNote": ("Launch TERVERIFIKASI ≤48 jam: first mint 2026-11-07 21:29:09 WIB (blok 132216769, "
                   "scan window run ini) — ~30 menit sebelum verifikasi parent."),
    "gate": ("website gate GAGAL (dicoba metode A/B/C/D/G/H/I/J/M): raw contract-address search tanpa hit "
             "proyek; Boltbook tanpa post AgentBook; Sourcify exact_match (verifiedAt 2026-11-07T14:29:19Z) "
             "tanpa URL di metadata; agentbook.space (same-name) TIDAK mencetak alamat kontrak "
             "(front page minimal, /llms.txt 404); project-name search tanpa situs proyek; contractURI "
             "base64 tanpa external_link; tokenURI(1) base64 tanpa external_url; ABI 44 fungsi tanpa "
             "fungsi website. X UNVERIFIED (opsional, tidak meng-gate)."),
    "note": ("STRONG LEAD run 2131 (dilaporkan sekali, GATE-BLOCKED): 3 kaki strong lead TERPENUHI — umur "
             "terverifikasi ≤48 jam + free 59,5% TERVERIFIKASI (>=25%) + slot user terbuka (costOf(user,1)=0, "
             "freeUsed=0, mintedBy=0, balanceOf=0). BUKAN kandidat: velocity belum terhitung (bacaan pertama, "
             "tidak ada rate sebelumnya). TIDAK DIEKSEKUSI: website gate GAGAL — TIDAK ADA preview/mint; "
             "promosi ke eksekusi hanya bila website terverifikasi ditemukan + semua guard lolos."),
    "lastReadBlock": abook.get("block"),
    "lastReadWib": "2026-11-07 run 2131",
}

# --- King's Game + Agent Grove re-reads (no change) ---
kg = snap["contracts"].get("King's Game")
if kg is not None:
    kg["freeMinted"] = 3
    kg["balanceOf_user"] = 0
    kg["lastReadBlock"] = 132217806
    kg["lastReadWib"] = "2026-11-07 run 2131"
    kg["runNote2131"] = ("Run 2131: freeMinted tetap 3 (probe single-call; batch LEAN gagal karena quirk "
                         "whole-batch-revert freeClaimed()), balanceOf(user)=0, view lain revert — TANPA "
                         "perubahan, tanpa promosi.")
gr = snap["contracts"].get("Agent Grove")
if gr is not None:
    gr["lastReadBlock"] = 132217806
    gr["lastReadWib"] = "2026-11-07 run 2131"
    gr["runNote2131"] = ("Run 2131 (blok 132217806): freeOpen 0, freeClaimed(user) false — identik run 2101, "
                         "tetap upcoming watchlist-only.")

snap["last_run"] = "2026-11-07 run 2131"
snap["last_run_wib"] = "2026-11-07 21:31 WIB"
snap["runNote2131"] = (
    "Run 2131 (21:31-~22:05 WIB): 0 kandidat baru, 0 eksekusi, 0 track-C lead/kandidat baru, "
    "0 pending claim baru/terbuka/gagal. 1 EARLY LEAD BARU (dilaporkan sekali): Paw Gang PAWG "
    "0x587C303982187Ec578dF309d27670327b13202F8 (first-seen scan run 2001, label 'likely PAID-ONLY' run 2001 "
    "DIKOREKSI: price 0, mint PoW, mintOpen=1, registry match; launch terverifikasi 20:00 WIB hari ini; "
    "313/3.333 = 9,4% inferensi; website pawgang.pages.dev terverifikasi; slot user terbuka hasMinted=0; "
    "velocity + counter gratis UNVERIFIED; TIDAK di-preview/di-mint). 1 STRONG LEAD BARU (GATE-BLOCKED, "
    "dilaporkan sekali): AgentBook ABOOK 0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0 (first mint 21:29:09 WIB; "
    "free 198/333 = 59,5% TERVERIFIKASI; slot user terbuka costOf=0; REGISTRY() match parent-verified blok "
    "132220450; BUKAN kandidat karena velocity belum terhitung; TIDAK DIEKSEKUSI — website gate GAGAL "
    "metode A/B/C/D/G/H/I/J/M). 1 AGE-EXCLUSION: Ember Byte (first mint 2026-11-05 20:01:17 WIB, 49,5 jam; "
    "spot sale berbayar 1/5.000 terjual) — dihapus dari snapshot. 0 sold-out baru (35 set sama dgn run 2101). "
    "Velocity: 2 pass — WAR3-1aa9 (+205, 8,93x) + Thetavox (+26, 1,54x); keduanya free% UNVERIFIED -> bukan "
    "kandidat/strong (VOLT + Zhenzhu artefak fungible). King's Game freeMinted tetap 3, tanpa perubahan. "
    "Agent Grove freeOpen 0, freeClaimed(user) false — identik run 2101. HIVE Agents totalSupply 1256 flat, "
    "balanceOf(user)=1, minted-by-user. Scan OK (1000 blok 132216460-132217459, 118 NFT, 314 ERC-20, 0 error, "
    "2 true first-seen: AgentBook + Agent Penguin bukan agent-shaped/paid-only; King's Game tidak dilaporkan "
    "ulang). 5c: 6 baru dicek, 0 sale shape. Sourcify feed: 20 dicek, 0 S1/S2. Boltbook EN+ZH segar, 0 lead baru "
    "(Sora Agent 9.900/10.000 paid-only, Frost Agent 4.900/5.000, ETERNAL AGENT minter-only — semua bukan lead). "
    "Bridge: tidak berubah sejak 2026-11-06 02:48, 0 promosi, 7 same_owner_discarded tidak dipromosikan. "
    "Binanceai tetap refund/failed (launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed "
    "user=0) — sudah dilaporkan sekali run 1701, tidak dilaporkan ulang."
)
snap["runNote2131_scan"] = (
    "Scan run 2131 SUKSES. Pre-flight OK 16,0 dtk (head 132217417, 321 logs / 50 blok). Window 132216460-132217459 "
    "(1000 blok, cap), 20/20 chunk + enrich, 40 panggilan Ankr, 0 error, partial=false, ~18 mnt. 118 NFT "
    "(112 ERC721 + 6 ERC1155, 859 mint), 314 ERC-20 mint (6.205 mint). 2 true first-seen (AgentBook EARLY/STRONG "
    "candidate + Agent Penguin bukan lead). Watermark TIDAK dimajukan oleh job ini; backfill memajukannya sendiri "
    "132188665 -> 132191165 selama run ini. Gap terlewati cap 132191166-132216459 (25.294 blok) milik backfill. "
    "Seen file: triage append 97 entri (total nested 11.186). track-c-scan-checked.json: 6 alamat baru "
    "(checked list 2605 -> 2611)."
)
snap["runNote2131_binanceai"] = (
    "Run 2131: BINANCEAI launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, "
    "tokenBalance(user)=0, reserves pair 0/0 — tetap refund/failed, pending_claims kosong, tidak dilaporkan ulang."
)
snap["runNote2131_age_exclusions"] = ember_note or "0 age-exclusion run 2131."

with open(HF + "onchain-snapshot.json.tmp", "w") as f:
    json.dump(snap, f, indent=1)
os.replace(HF + "onchain-snapshot.json.tmp", HF + "onchain-snapshot.json")

st = json.load(open(HF + "onchain-scan-state.json"))
st["note_2131_scan"] = snap["runNote2131_scan"]
with open(HF + "onchain-scan-state.json.tmp", "w") as f:
    json.dump(st, f, indent=1)
os.replace(HF + "onchain-scan-state.json.tmp", HF + "onchain-scan-state.json")

print(f"contracts updated: {updated} (supply-None {none_supply}); track_c updated: {tc_updated}")
print(f"contracts total now: {len(snap['contracts'])}; track_c: {len(snap.get('track_c', {}))}; excluded: {len(snap.get('excluded', {}))}")
print("Ember Byte removed:", ember is not None)
print("Paw Gang + AgentBook added.")
