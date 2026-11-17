#!/usr/bin/env python3
"""Run 2026-11-06 0801 WIB finalize.
1. Fix onchain-scan-seen.json: remove 98 wrongly appended top-level keys from triage
   (same top-level-keys bug documented in _meta notes 1901/2231/0301/0501);
   add the 4 TRUE first-seen to nested seen['contracts'] (lowercase keys).
2. Correct triage JSON with a correction note.
3. Update onchain-snapshot.json: re-read values + velocity notes, +2 early leads
   (Data Synth, Zero Genesis), +9 age-excluded, last_run fields.
Backs up snapshot + seen file first. Never touches scan-bridge.json."""
import json, shutil, copy

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0801"

shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0801")
shutil.copy(f"{BASE}/onchain-scan-seen.json", f"{BASE}/onchain-scan-seen.json.bak-20261106-0801")

# ---------- 1. Seen file fix ----------
seen = json.load(open(f"{BASE}/onchain-scan-seen.json"))
removed = [k for k in list(seen.keys()) if k not in ("_meta", "contracts", "known_older_leads")]
for k in removed:
    del seen[k]
TRUE_FS = {
 "0xeFe2adD56Aca269AcF9acd1510AE1C7C81Dd2b0E": 131918216,  # OUPE Cards
 "0x30Ffd5d0b2d3908A38fA31016F148E6b651587A2": 131918385,  # SoulWallet Agent
 "0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642": 131918469,  # Data Synth
 "0x7807202FBE09f4AAC9ac312ed593ba16806F6b34": 131919173,  # Zero Genesis
}
for addr, blk in TRUE_FS.items():
    seen.setdefault("contracts", {})[addr.lower()] = blk
seen["_meta"]["last_scan_wib"] = "2026-11-06 run 0801"
seen["_meta"]["last_scan_window"] = "131918215-131919214"
seen["_meta"]["last_scan_added"] = 4
seen["_meta"]["last_updated_wib"] = "2026-11-06 run 0801"
seen["_meta"]["note_0801"] = (
 "Run 0801: raw first-seen 98 included 94 already in seen['contracts'] "
 "(same top-level-keys bug as runs 1901/2231/0301/0501); corrected true "
 "first-seen = 4 (OUPE Cards, SoulWallet Agent, Data Synth, Zero Genesis). "
 "Removed 98 wrongly appended top-level keys; 4 appended to nested contracts "
 "(lowercase keys). 9 agent-shaped old contracts verified age >48h (already in "
 "seen, NOT first-seen) -> snapshot.excluded, never reported as leads. "
 "Crown Race already in seen (first-seen block 131751883) -> NOT first-seen, log only.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json", "w"), indent=1)
print("SEEN fixed: removed", len(removed), "top-level keys; nested now",
      len(seen["contracts"]), "entries", flush=True)

# ---------- 2. Triage JSON correction ----------
tj = json.load(open(f"{BASE}/run-{TS}-scan-triage.json"))
tj["correction_seen_bug"] = (
 "CORRECTED run 0801 finalize: raw nft_first_seen=98 included 94 already in "
 "seen['contracts'] (triage checked top-level keys only - the documented bug from "
 "runs 1901/2231/0301/0501). TRUE first-seen = 4: OUPE Cards, SoulWallet Agent, "
 "Data Synth, Zero Genesis. The 12 'agent-shaped' entries include 10 already-seen "
 "contracts (9 verified age >48h via Ankr age-bound search + Crown Race already "
 "in seen since block 131751883) and 2 genuinely new (Data Synth, Zero Genesis). "
 "Agent Panda + Ghostbloom were already in snapshot.excluded.")
tj["true_first_seen"] = ["0xeFe2adD56Aca269AcF9acd1510AE1C7C81Dd2b0E",
                         "0x30Ffd5d0b2d3908A38fA31016F148E6b651587A2",
                         "0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642",
                         "0x7807202FBE09f4AAC9ac312ed593ba16806F6b34"]
json.dump(tj, open(f"{BASE}/run-{TS}-scan-triage.json", "w"), indent=1)
print("TRIAGE JSON corrected", flush=True)

# ---------- 3. Snapshot update ----------
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap.setdefault("contracts", {})
EX = snap.setdefault("excluded", {})
REREAD = json.load(open(f"{BASE}/run-{TS}-reread-lean.json"))
BLK = REREAD["block"]

def setv(entry, key, val):
    if val is not None:
        entry[key] = val

# Re-read numeric updates (None never overwrites)
NUMMAP = {
 "HIVE Agents": [("totalSupply", "totalSupply")],
 "KING Agent": [("totalMinted", "totalMinted"), ("remainingFree", "remainingFree")],
 "Mummyhive": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "Thronemind": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Hashseers": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Smeltbots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Forklings": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Agent Frogs": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "PassAgentX": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "SEAT-f11e": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "StarAgent-7d39": [("totalSupply", "totalSupply")],
 "LuckyBox-d08e": [("totalSupply", "totalSupply")],
 "SnailMail": [("totalSupply", "totalSupply")],
 "wheelz": [("totalSupply", "totalSupply")],
 "Tumblebots": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Mossminds": [("totalSupply", "totalSupply"), ("freeMinted", "freeMinted")],
 "Jolly": [("totalMinted", "totalMinted"), ("freeMinted", "freeMinted")],
 "AgentGlyph": [("totalSupply", "totalSupply"), ("freeClaimed", "freeClaimed")],
 "MILLION": [("totalMinted", "totalMinted")],
 "FOD Agent": [("totalMinted", "totalMinted")],
 "Nebula Ape Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Shadow Yeti Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Silent Hydra Agent": [("totalSupply", "totalSupply")],
 "Cipher Wraith Agent": [("totalSupply", "totalSupply"), ("totalMinted", "totalMinted")],
 "Umbra Lynx Agent": [("totalSupply", "totalSupply")],
}
for name, pairs in NUMMAP.items():
    if name not in C or name not in REREAD["reread"]:
        continue
    src = REREAD["reread"][name]
    for dst, sk in pairs:
        setv(C[name], dst, src.get(sk))
    C[name]["lastReadBlock"] = BLK
    C[name]["lastReadWib"] = "2026-11-06 run 0801"
    if "balanceOf_user" in src:
        setv(C[name], "balanceOf_user", src.get("balanceOf_user"))
    if "mintedBy_user" in src:
        setv(C[name], "mintedBy_user", src.get("mintedBy_user"))

# Track-C re-read numeric updates (track_c keyed by sale name in snapshot)
TCMAP = {"OSK": "opened", "DROID": "opened", "IMARS": "opened"}
for name in TCMAP:
    pass  # track_c entries use sale-contract keys; updated via note below only

# Velocity / run notes (key items)
C["HIVE Agents"]["runNote0801"] = ("Run 0801 (blok 131919121): totalSupply 1253 flat vs run 0731 (1253) -> velocity GAGAL; "
    "balanceOf(user) gagal baca run ini (nilai lama 1 dipertahankan); minted-by-user, bukan kandidat.")
C["KING Agent"]["runNote0801"] = ("Run 0801 (blok 131919121): totalMinted 627->649 (+22, ~27 mnt blok 131915480->131919121 = ~0,81/mnt "
    "vs prev ~1,48/mnt = ~0,55x) -> velocity GAGAL (butuh >=1,5x DAN >=20 token; token terpenuhi, rasio gagal). "
    "Claimed 649/3333=19,47% <25% kaki strong-lead. Slot user terbuka (costOf 0, mintedBy 0, balance 0). Tetap EARLY.")
C["KING Agent"]["previousTotalSupply"] = 627
C["KING Agent"]["mintedInInterval"] = 22
C["KING Agent"]["intervalMinutes"] = 27.3
C["KING Agent"]["currentRatePerMin"] = 0.81
C["KING Agent"]["previousRatePerMin"] = 1.48
C["KING Agent"]["velocityLegPasses"] = False
C["MILLION"]["runNote0801"] = ("Run 0801 (blok 131919121): totalMinted 93->94 (+1, <20) -> velocity GAGAL. "
    "FREE_SUPPLY 500. Tetap EARLY.")
C["FOD Agent"]["runNote0801"] = ("Run 0801 (blok 131919121): totalMinted 500 flat vs run 0731 (500) -> velocity GAGAL; "
    "costOf(user,1)=0,005 BNB (berbayar), tanpa free view; mintedBy(user)=0, balanceOf(user)=0. Tetap EARLY.")
for n in ["Nebula Ape Agent", "Shadow Yeti Agent", "Silent Hydra Agent", "Cipher Wraith Agent", "Umbra Lynx Agent"]:
    C[n]["runNote0801"] = ("Run 0801 (blok 131919121): totalMinted tetap 1, spotsLeft 3332, PRICE 0,0005 BNB - "
        "tidak ada pergerakan sejak baseline. Tetap EARLY.")
C["Forklings"]["runNote0801"] = ("Run 0801: totalSupply 923->924 (+1), freeMinted 924/2000=46,2% <50% kaki kandidat; "
    "velocity GAGAL; gate-blocked strong lead; slot user terbuka. Tanpa promosi.")
C["Agent Frogs"]["runNote0801"] = ("Run 0801: totalSupply 434 flat, freeClaimed 434/1111=39,06%; gate-blocked strong lead; "
    "slot user terbuka. Tanpa promosi.")
C["PassAgentX"]["runNote0801"] = ("Run 0801: totalSupply 3960->3961 (+1), freeMinted 3742->3744 (+2). Tanpa sellout/promosi.")
C["SEAT-f11e"]["runNote0801"] = ("Run 0801: totalSupply 3231->3362 (+131, ~4,8/mnt vs prev ~9,8 = ~0,49x) -> velocity GAGAL; "
    "free % unverified; watchlist-only.")
C["AgentGlyph"]["runNote0801"] = ("Run 0801: freeClaimed 512/512 - sold out, sudah tercatat; totalSupply 513 (1 paid mint). Tanpa perubahan.")

# ---------- Early leads: Data Synth + Zero Genesis ----------
tri = json.load(open(f"{BASE}/run-{TS}-scan-triage.json"))
tri_by_addr = {r["address"].lower(): r for r in tri["nft_first_seen"]}
probe3 = json.load(open(f"{BASE}/run-{TS}-early-probe3.json"))["probe"]
probe4 = json.load(open(f"{BASE}/run-{TS}-early-probe4.json"))["probe"]

C["Data Synth"] = {
 "address": "0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642",
 "status": "early-lead-reported-2026-11-06",
 "name": "Data Synth",
 "symbol": tri_by_addr["0x7bd19ee3c72b4544787eba0ebd655e1376fe3642"].get("symbol"),
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
 "firstSeenBlock": 131918469,
 "scanWindow": "131918215-131919214",
 "scanMints": 1,
 "scanMinters": 1,
 "lastReadBlock": probe3["Data Synth"]["block"] if "block" in probe3 else 131922983,
 "lastReadWib": "2026-11-06 run 0801",
 "xVerified": False,
 "velocityVerified": False,
 "launchNote": ("First mint VERIFIED on-chain: first Transfer-from-zero at block 131918469 = 2026-11-06 08:11:04 WIB "
   "(Ankr getLogs address-filtered 131899549..131918468: 0 earlier mints; totalMinted=1 confirms the window mint is the only mint). "
   "No project-stated launch time found; Sourcify verifiedAt is verification time, NOT launch time. "
   "First-seen by this job in run 0801 via route-4 scan (true first-seen: absent from seen['contracts'] + snapshot)."),
 "baselineNote": ("EARLY lead reported once 2026-11-06 run 0801. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI "
   "(mint/minted/mintedBy/totalMinted + PRICE/quote + AGENT_REGISTRY gate). Free % UNVERIFIED (no free views); X UNVERIFIED; "
   "velocity baseline pertama (totalMinted 1). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
 "previousTotalSupply": 1,
 "mintedInInterval": 0,
 "intervalMinutes": 0,
 "currentRatePerMin": None,
 "previousRatePerMin": None,
 "velocityLegPasses": False,
 "velocityNote": "Run 0801: baseline pertama (totalMinted 1) - velocity belum terhitung.",
 "supplyView": "totalMinted",
}
C["Zero Genesis"] = {
 "address": "0x7807202FBE09f4AAC9ac312ed593ba16806F6b34",
 "status": "early-lead-reported-2026-11-06",
 "name": "Zero Genesis",
 "symbol": tri_by_addr["0x7807202fbe09f4aac9ac312ed593ba16806f6b34"].get("symbol"),
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
 "firstSeenBlock": 131919173,
 "scanWindow": "131918215-131919214",
 "scanMints": 1,
 "scanMinters": 1,
 "lastReadBlock": probe4["Zero Genesis"]["block"] if "block" in probe4 else 131923864,
 "lastReadWib": "2026-11-06 run 0801",
 "xVerified": False,
 "velocityVerified": False,
 "launchNote": ("First mint VERIFIED on-chain: first Transfer-from-zero at block 131919173 = ~2026-11-06 08:16 WIB "
   "(estimasi dari block timestamp 131918469=08:11:04 WIB; Ankr getLogs address-filtered 131899549..131919172: 0 earlier mints; "
   "totalMinted=1 confirms the window mint is the only mint). No project-stated launch time found; Sourcify verifiedAt is "
   "verification time, NOT launch time. First-seen by this job in run 0801 via route-4 scan (true first-seen: absent from "
   "seen['contracts'] + snapshot; also in Sourcify feed run ini, checked-not-sale-shape)."),
 "baselineNote": ("EARLY lead reported once 2026-11-06 run 0801. Never auto-minted/previewed. Agent-shape verified: Sourcify ABI "
   "(mint/minted/mintedBy/totalMinted + PRICE/quote + AGENT_REGISTRY gate). Free % UNVERIFIED (no free views); X UNVERIFIED; "
   "velocity baseline pertama (totalMinted 1). Promotes to strong lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
 "previousTotalSupply": 1,
 "mintedInInterval": 0,
 "intervalMinutes": 0,
 "currentRatePerMin": None,
 "previousRatePerMin": None,
 "velocityLegPasses": False,
 "velocityNote": "Run 0801: baseline pertama (totalMinted 1) - velocity belum terhitung.",
 "supplyView": "totalMinted",
}

# ---------- 9 age-excluded (already in seen, never reported as leads) ----------
AGE_EX = [
 ("Tacotron", "0x05deBE4445232205AE7E79d02cb5DE5AA0641efF", "TACOTRON", 130497346, "2026-10-29 22:29 WIB",
  "freeClaimed 2272/7000=32,46% (probe run 0801 blok 131921810), totalSupply unreadable, PRICE 0,00005 BNB, mintOpen 1, quote(user,1)=0. Owner 0x53043412c4f2436f68e56bb9638ebebb099fb3c1 (shared dengan Cloudpuff)."),
 ("AgentPad Pass", "0x01c106835091c09D5c69737631Af133530093C89", "AGENTPAD", 130280617, "~2026-10-29 19:00 WIB (estimasi 0,45 dtk/blok dari bound 131534000=2026-11-04 08:06 WIB; timestamp blok gagal dibaca RPC)",
  "totalSupply 3718/10000, MAX_SUPPLY 10000, PRICE 0, tanpa free view. Owner 0x73cf2b2eb72a243602e9dcda9efec6473e5c1741."),
 ("Cloudpuff", "0xe09131bBb48E653C5b2D64099324f14000d67De5", "CLOUDPUFF", 130469362, "~2026-10-30 18:30 WIB (estimasi; timestamp blok gagal dibaca RPC)",
  "freeClaimed 6996/7000=99,94% (probe run 0801 blok 131921810), totalSupply 7292/7777, PRICE 0,00005 BNB, mintOpen 1, quote(user,1)=0. Owner 0x53043412c4f2436f68e56bb9638ebebb099fb3c1 (shared dengan Tacotron)."),
 ("Thalvorix Hero", "0x6D862c8B847323961FCD349ffFbee0133F6B929A", "THALVORIX", 131023264, "2026-11-01 16:15 WIB",
  "totalMinted 2146/6666, tanpa free counter terbaca. Owner unreadable (owner() None, 2x percobaan)."),
 ("Binance Agent Oracle", "0xcBe2DBBFF4264Dc67Bf557c64e29997B82439354", "BAO", 131109864, "~2026-11-02 03:00 WIB (estimasi; timestamp blok gagal dibaca RPC)",
  "totalSupply 8211, totalMinted 9523, MAX_SUPPLY 20000, mintOpen 1, quote(user,1)=0,0002 BNB (berbayar), tanpa free counter. Owner 0xb3455523cc10061d2e9d5ae67dbcfb4db76727ad."),
 ("Agent Creatures", "0xF7245511A890a42F911c776824c665E2da3cedb3", "AGENTCREATURES", 130901722, "2026-11-01 01:03 WIB",
  "totalSupply/totalMinted 1947/5555, mintOpen 1, tanpa free view. Owner 0x77a0c1114f7e2579afbfd14b36dccf2a347bea19."),
 ("CodexCrew", "0xA5921507449eB36eB16BE3ffedBEEe5439C9bDef", "CODEXCREW", 131037193, "2026-11-01 17:59 WIB",
  "totalSupply 191, freeClaimed 178/1207=14,75%, MAX_SUPPLY 1725, PRICE 0,00005 BNB, mintOpen 1, quote(user,1)=0. Owner 0x8a3b31dd69c6ab76b2dda2711b32eaad8646e173."),
 ("Diamondo", "0x58C96735342e5c2e8Ba542E4aAc2a1500Cc769C6", "DIAMONDO", 130619640, "~2026-10-31 12:00 WIB (estimasi; timestamp blok gagal dibaca RPC)",
  "totalSupply 2178, freeClaimed 2177/7000=31,1%, MAX_SUPPLY 7777, PRICE 0,00005 BNB, mintOpen 1, quote(user,1)=0. Owner 0xa054275580c6d1c9077543907ac5798f2494ecce (grup Gourdwick: Mothwraith, Malabao, Kitsunaru, Nightsable, Nimaluo, Medusine, Mummyrelic, Ravenhex, Orbitmarshal, Gondolux) -> promosi apapun juga dibuang aturan same-owner."),
 ("GOAT", "0xE7a548606eECB32a93B227411b6343B0399DC7C0", "GOAT", 131140279, "2026-11-02 06:53 WIB",
  "totalSupply 2717/100000, mintOpen 1, tanpa free view. Owner 0x340317e4c5cc3c990c74ae8a12861ed66432a6ee."),
]
for name, addr, sym, fmb, fmt, note in AGE_EX:
    EX[name] = {
     "address": addr, "symbol": sym, "track": "A",
     "status": "excluded-age-over-48h-2026-11-06",
     "note": (f"Age-excluded run 0801 (tidak pernah dilaporkan sebagai lead; pertama terlihat scan run ini tapi SUDAH ADA di "
       f"seen['contracts']): first mint TERVERIFIKASI blok {fmb} ({fmt}) via Ankr getLogs binary-search [130000000, 131534000] "
       f"(bound 131534000 = 2026-11-04 08:06 WIB); umur >48 jam pada run 0801 dan BELUM sold out. {note} "
       f"Tidak di-preview/di-mint; tidak dilaporkan sebagai lead."),
     "previous_status": "seen-only-never-reported",
     "firstMintWib": fmt,
     "firstMintBlock": fmb,
     "lastReading": f"Run 0801: {note}",
    }

snap["last_run_wib"] = "2026-11-06 run 0801"
snap["last_run_note"] = ("Run 0801: 2 EARLY leads baru (Data Synth, Zero Genesis - dilaporkan sekali run ini) + 9 age-excluded "
    "(Tacotron, AgentPad Pass, Cloudpuff, Thalvorix Hero, Binance Agent Oracle, Agent Creatures, CodexCrew, Diamondo, GOAT - "
    "pertama terlihat scan run ini, first mint terverifikasi >48 jam, TIDAK dilaporkan sebagai lead). "
    "Scan route 4 SUKSES (pre-flight OK 8,8 dtk, cap 1000 blok, 40 panggilan Ankr, 0 error) setelah 6x gagal. "
    "KING 649/3333=19,47% velocity GAGAL; MILLION 94; FOD 500 flat; HIVE 1253 flat. "
    "Boltbook newest post unchanged (2026-11-05T09:20:52Z); sweep tanpa proyek baru; Sourcify 17 baru dicek (0 sale-shape); "
    "5c: 2 ERC-20 baru dicek (0 sale-shape); Odaily/PANews 0 mention; bridge 0 not-in-snapshot; binanceai tetap refund/failed. "
    "Koreksi bug seen-file: raw first-seen 98 -> true 4 (94 sudah ada di seen['contracts']).")
snap["runNote0801"] = snap["last_run_note"]
snap["runNote0801_scan"] = ("Run 0801: SCAN SUKSES (amendment 2026-11-06 ~07:49: pre-flight ankr_getLogs 50 blok OK 8,8 dtk <60 dtk; "
    "window cap 1000 blok; per-chunk progress log + flush). Window 131918215-131919214, 172 NFT + 305 ERC20-mint contracts, "
    "40 panggilan Ankr, 0 error, selesai sebelum timeout 780 (JSON tertulis ~01:29 UTC). Watermark 131899548 -> 131919214. "
    "Gap 131899549-131918142 (~18.594 blok) belum ter-cover (backfill). Bentuk shape-check phase sempat lambat (172 kontrak, "
    "Sourcify retry-exhausted massal) tapi selesai tepat waktu - risiko stall fase shape tetap ada untuk window padat.")

json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT updated: contracts", len(C), "excluded", len(EX), flush=True)

# ---------- 4. Scan-state note about the seen fix ----------
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0801_seenfix"] = ("Run 0801 finalize: triage sempat menghitung 98 first-seen (bug top-level-keys, sudah didokumentasikan "
    "_meta notes 1901/2231/0301/0501); dikoreksi jadi 4 true first-seen; 98 top-level key yang salah dihapus dari seen file; "
    "4 ditambahkan ke nested seen['contracts'] (lowercase). Watermark tetap 131919214.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)
print("STATE noted", flush=True)
print("FINALIZE DONE", flush=True)
