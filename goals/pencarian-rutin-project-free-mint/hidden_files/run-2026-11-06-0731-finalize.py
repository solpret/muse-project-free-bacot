#!/usr/bin/env python3
"""Run 2026-11-06 0731 WIB FINALIZE: merge backfill triage + early-verify retries,
add the 3 new early leads (FOD Agent, Nebula Ape Agent, Shadow Yeti Agent) to the
snapshot, record re-read deltas, and note scan failure #6 + backfill watermark advance.
Backups written first. Read-only except snapshot/scan-state/hot-leg-seen updates."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0731"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0731")
shutil.copy(f"{BASE}/onchain-scan-state.json", f"{BASE}/onchain-scan-state.json.bak-20261106-0731")

# --- 1. Correct triage JSON with retry verification + resolved names ---
tri = json.load(open(f"{BASE}/run-{TS}-backfill-triage.json"))
ret = json.load(open(f"{BASE}/run-{TS}-early-verify-retry.json"))
ret2 = json.load(open(f"{BASE}/run-{TS}-early-verify-retry2.json"))
NAMES = {"0xA3d24EE16b6b912192724598Da55C7909bBB97e8": ("FOD Agent", "FODG"),
         "0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC": ("Nebula Ape Agent", "NEBA"),
         "0xA193Ea677a39D4F04bB770555fe6954e0e00C02C": ("Shadow Yeti Agent", "SHAY")}
for item in tri["nft_first_seen"]:
    addr = item["address"]
    if addr in NAMES:
        item["name"], item["symbol"] = NAMES[addr]
    key = {"FOD Agent": "FOD Agent", "Nebula Ape Agent": "Unnamed-7972",
           "Shadow Yeti Agent": "Unnamed-A193"}.get(item.get("name"), item.get("name"))
    if key in ret:
        v = ret[key]
        item["first_mint_verified"] = v["first_mint_verified"]
        item["earlier_mints_before_first_block"] = v["earlier_mints_before_first_block"]
        item["first_mint_wib"] = v["first_mint_wib"]
        item["state"] = {k: v[k] for k in
                         ["totalMinted()", "totalSupply()", "spotsLeft()", "MAX_SUPPLY()",
                          "PRICE()", "costOf(address,uint256)", "mintedBy_user", "balanceOf_user",
                          "quote_user_1"] if k in v}
    if item.get("name") == "Nebula Ape Agent":
        item["first_mint_verified"] = ret2["first_mint_verified"]
        item["earlier_mints_before_first_block"] = ret2["earlier_mints_before_first_block"]
        item["first_mint_wib"] = "2026-11-06 05:38:37"
        item["state"] = {"totalMinted()": 1, "totalSupply()": 3333, "spotsLeft()": 3332,
                         "MAX_SUPPLY()": 3333, "PRICE()": 500000000000000,
                         "mintedBy_user": 0, "balanceOf_user": 0, "quote_user_1": None}
json.dump(tri, open(f"{BASE}/run-{TS}-backfill-triage.json", "w"), indent=1)

# --- 2. Snapshot updates ---
s = json.load(open(f"{BASE}/onchain-snapshot.json"))
LEADS = {
 "FOD Agent": {
  "address": "0xA3d24EE16b6b912192724598Da55C7909bBB97e8", "symbol": "FODG",
  "first_block": 131898649, "first_mint_wib": "2026-11-06 05:42:23",
  "scan_mints": 82, "scan_minters": 61, "totalMinted": 500,
  "state_note": ("totalMinted 500 at ~08:10 WIB read (82 mints inside window 131897549-131899548); "
                 "costOf(user,1)=0.005 BNB (paid price); no PRICE()/free view in ABI (33 functions); "
                 "spotsLeft/MAX_SUPPLY unreadable this run; mintedBy(user)=0, balanceOf(user)=0."),
  "launch_note": ("First mint verified on-chain: first Transfer-from-zero at block 131898649, "
                  "2026-11-06 05:42:23 WIB (Ankr getLogs address-filtered 131880000..131898648: 0 earlier "
                  "mints). No project-stated launch time found; Sourcify verifiedAt is verification "
                  "time, NOT launch time. First-seen by this job in run 0731 via backfill chunk "
                  "(main route-4 scan died in shape phase, no JSON)."),
  "baseline_note": ("EARLY lead reported once 2026-11-06 run 0731. Never auto-minted/previewed. "
                    "Agent-shape verified: Sourcify ABI (33 functions) contains agentRegistry + "
                    "agentGateOn + mint + costOf. Free leg UNVERIFIED: no free view in ABI, "
                    "costOf(user,1)=0.005 BNB is the paid price. 61 distinct minters in window "
                    "(organic minting, NOT the single-operator wave). Age verified <=48h (~2.5h at "
                    "report). Promotes to strong lead only on all 3 strong-lead legs; to candidate "
                    "only on ALL criteria + safety."),
 },
 "Nebula Ape Agent": {
  "address": "0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC", "symbol": "NEBA",
  "first_block": 131898146, "first_mint_wib": "2026-11-06 05:38:37",
  "scan_mints": 1, "scan_minters": 1, "totalMinted": 1,
  "state_note": ("totalMinted 1, spotsLeft 3332/3333, MAX_SUPPLY 3333, PRICE 0.0005 BNB; "
                 "quote(user,1) unreadable; mintedBy(user)=0, balanceOf(user)=0."),
  "launch_note": ("First mint verified on-chain: first Transfer-from-zero at block 131898146, "
                  "2026-11-06 05:38:37 WIB (Ankr getLogs address-filtered 131880000..131898145: 0 earlier "
                  "mints; first attempt failed on chunk 131890000-131891999 RemoteDisconnected, retry "
                  "succeeded). No project-stated launch time found. First-seen by this job in run 0731 "
                  "via backfill chunk (main route-4 scan died in shape phase, no JSON)."),
  "baseline_note": ("EARLY lead reported once 2026-11-06 run 0731. Never auto-minted/previewed. "
                    "Agent-shape verified: Sourcify ABI (30 functions, same template as the 0701 trio) "
                    "contains AGENT_REGISTRY (classify() GATE_WORDS misses it - blind spot, corrected "
                    "gate used) + mint + PRICE/quote. Free leg UNVERIFIED: no free view in ABI, "
                    "quote(user,1) unreadable, PRICE 0.0005 BNB. Same operator as the 0701 trio: sole "
                    "minter 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5 (factory wave; same-owner rule may "
                    "discard a later promotion). Age verified <=48h (~2.5h at report). Promotes to strong "
                    "lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
 },
 "Shadow Yeti Agent": {
  "address": "0xA193Ea677a39D4F04bB770555fe6954e0e00C02C", "symbol": "SHAY",
  "first_block": 131899547, "first_mint_wib": "2026-11-06 05:49:07",
  "scan_mints": 1, "scan_minters": 1, "totalMinted": 1,
  "state_note": ("totalMinted 1, spotsLeft 3332/3333, MAX_SUPPLY 3333, PRICE 0.0005 BNB; "
                 "quote(user,1) unreadable; mintedBy(user)=0, balanceOf(user)=0."),
  "launch_note": ("First mint verified on-chain: first Transfer-from-zero at block 131899547, "
                  "2026-11-06 05:49:07 WIB (Ankr getLogs address-filtered 131880000..131899546: 0 earlier "
                  "mints). No project-stated launch time found. First-seen by this job in run 0731 "
                  "via backfill chunk (main route-4 scan died in shape phase, no JSON)."),
  "baseline_note": ("EARLY lead reported once 2026-11-06 run 0731. Never auto-minted/previewed. "
                    "Agent-shape verified: Sourcify ABI (30 functions, same template as the 0701 trio) "
                    "contains AGENT_REGISTRY (classify() GATE_WORDS misses it - blind spot, corrected "
                    "gate used) + mint + PRICE/quote. Free leg UNVERIFIED: no free view in ABI, "
                    "quote(user,1) unreadable, PRICE 0.0005 BNB. Same operator as the 0701 trio: sole "
                    "minter 0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5 (factory wave; same-owner rule may "
                    "discard a later promotion). Age verified <=48h (~2.4h at report). Promotes to strong "
                    "lead only on all 3 strong-lead legs; to candidate only on ALL criteria + safety."),
 },
}
for name, L in LEADS.items():
    s["contracts"][name] = {
        "address": L["address"], "status": "early-lead-reported-2026-11-06",
        "name": name, "symbol": L["symbol"], "kind": "ERC721",
        "totalMinted": L["totalMinted"], "totalSupply": 3333 if name != "FOD Agent" else None,
        "spotsLeft": 3332 if name != "FOD Agent" else None,
        "MAX_SUPPLY": 3333 if name != "FOD Agent" else None,
        "PRICE": 500000000000000 if name != "FOD Agent" else None,
        "costOf_user_1": 5000000000000000 if name == "FOD Agent" else None,
        "freeClaimed": None, "freePctVerified": None, "mintOpen": None,
        "userMintedBy": 0, "userBalance": 0,
        "userSlotNote": L["state_note"],
        "firstSeenBlock": L["first_block"], "firstMintWib": L["first_mint_wib"],
        "scanMints": L["scan_mints"], "scanMinters": L["scan_minters"],
        "scanWindow": "131897549-131899548 (backfill chunk)",
        "lastReadBlock": None,
        "lastReadWib": "2026-11-06 run 0731 (state reads via eth_call/Ankr ~08:10 WIB)",
        "xVerified": False, "velocityVerified": False,
        "launchNote": L["launch_note"], "baselineNote": L["baseline_note"],
        "owner": ("0xe9d9dec36ce804e44fdd5e19f09e2364cbf64ed5" if name != "FOD Agent" else None),
        "source": "backfill-131897549-131899548",
        "supplyView": "totalMinted",
    }

# --- 3. Re-read deltas on existing watchlist items (old values kept where reads failed) ---
def note(name, key, text):
    if name in s["contracts"]:
        s["contracts"][name][key] = text
note("HIVE Agents", "runNote0731",
     "Run 0731: totalSupply 1253 flat vs run 0701 -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
note("KING Agent", "runNote0731",
     "Run 0731: totalMinted 562->627 (+65, ~44 mnt = ~1,48/mnt vs prev 1,47 = ~1,0x) -> velocity GAGAL; "
     "remainingFree 2706 -> claimed 627/3333=18,8% <25% kaki strong-lead; costOf(user,1)=0, mintedBy 0, balance 0. Tetap EARLY.")
note("MILLION", "runNote0731",
     "Run 0731: totalMinted 84->90 (+6, <20) -> velocity GAGAL; FREE_SUPPLY 500, freeMinted unreadable; balance 0. Tetap EARLY.")
note("Silent Hydra Agent", "runNote0731",
     "Run 0731: totalMinted 1 (flat), spotsLeft 3332 - no movement since 0701 baseline; PRICE 0.0005 BNB; mintedBy 0, balance 0. Tetap EARLY.")
note("Cipher Wraith Agent", "runNote0731",
     "Run 0731: totalMinted 1 (flat), spotsLeft 3332 - no movement since 0701 baseline; mintedBy 0, balance 0. Tetap EARLY.")
note("Umbra Lynx Agent", "runNote0731",
     "Run 0731: totalMinted 1 (flat), spotsLeft 3332, MAX_SUPPLY 3333 - no movement since 0701 baseline; mintedBy 0, balance 0. Tetap EARLY.")
note("Thronemind", "runNote0731", "Run 0731: totalSupply/freeMinted 661 flat vs 0701/0734 -> velocity GAGAL; canFreeMint(user)=1, claimedFree 0. Gate-blocked strong lead, no promotion.")
note("Hashseers", "runNote0731", "Run 0731: freeMinted 594 flat (29,70%) -> velocity GAGAL. Gate-blocked strong lead, no promotion.")
note("Smeltbots", "runNote0731", "Run 0731: freeMinted 612 flat (30,60%) -> velocity GAGAL. Gate-blocked strong lead, no promotion.")
note("Forklings", "runNote0731", "Run 0731: totalSupply/freeMinted 922 flat (46,10% <50% kaki kandidat) -> velocity GAGAL. Gate-blocked strong lead, no promotion.")
note("Agent Frogs", "runNote0731", "Run 0731: freeClaimed 434/1111=39,06% flat -> velocity GAGAL. Gate-blocked strong lead, no promotion.")
note("PassAgentX", "runNote0731", "Run 0731: freeMinted 3735 flat; free % UNVERIFIED (no FREE_SUPPLY view). No promotion.")
note("SEAT-f11e", "runNote0731", "Run 0731: totalMinted 3019->3231 (+212, ~44 mnt = ~4,8/mnt vs prev ~9,8 = ~0,49x) -> velocity GAGAL; free % UNVERIFIED. Watchlist-only, no promotion.")

# --- 4. Run notes ---
s["last_run"] = "2026-11-06-0731"
s["last_run_wib"] = "2026-11-06 run 0731"
s["runNote0731"] = ("Run 0731: 3 EARLY leads baru (FOD Agent, Nebula Ape Agent, Shadow Yeti Agent - dari "
    "chunk backfill 131897549-131899548). 0 kandidat, 0 strong lead baru/promosi, 0 track-C lead/kandidat, "
    "0 pending claim baru/dibuka, 0 sellout, 0 age-exclusion, 0 lost free slot. No execution attempted. "
    "Snapshot kontrak 542 -> 545.")
s["runNote0731_scan"] = ("Run 0731: SCAN (route 4) GAGAL ke-6 berturut-turut - kali ini BUKAN stall di awal: "
    "40/40 chunk log selesai (221 ERC721, 5 ERC1155, 463 ERC20-mint, window 131912795-131914794), lalu mati "
    "di fase shape-check Sourcify tanpa menulis JSON (timeout 780 membunuh proses ~08:00 WIB; tidak ada "
    "baris RESULT/wrote). Data jendela scan HILANG - tidak ada triase scan run ini. Cakupan route-4 run ini "
    "hanya chunk backfill 131897549-131899548 (230 NFT, 433 ERC20, 80 panggilan Ankr, 0 error). Watermark "
    "dimajukan backfill sendiri 131897548 -> 131899548. Gap belum ter-cover: 131899549-131915xxx+ "
    "(~16.000 blok, tumbuh ~2.000/run pada block-rate ~0,45 dtk/blok).")
s["runNote0731_binanceai"] = ("Run 0731: binanceai.fun launched=None (gagal baca, sebelumnya 0), failed=1, "
    "isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance=None (gagal baca). Tetap fase "
    "refund/failed, no change vs run 0701. pending_claims tetap kosong; no re-report.")
s["last_run_note"] = ("3 EARLY leads baru (FOD Agent, Nebula Ape Agent, Shadow Yeti Agent); scan route-4 "
    "gagal ke-6 (mati di shape phase, data jendela hilang); backfill majukan watermark ke 131899548.")
json.dump(s, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)

# --- 5. Scan-state notes (watermark already advanced by backfill itself) ---
st = json.load(open(f"{BASE}/onchain-scan-state.json"))
st["note_0731_scan_failed"] = ("Run 0731: SCAN GAGAL ke-6 (timeout 780; 40/40 chunk selesai, mati di fase "
    "shape-check Sourcify tanpa JSON; data jendela 131912795-131914794 HILANG). Watermark TIDAK dimajukan "
    "scan; backfill majukan 131897548 -> 131899548.")
st["note_backfill_131897549_131899548"] = ("Backfill chunk 131897549-131899548: 230 NFT + 433 ERC20-mint "
    "contracts, 5 first-seen, 80 Ankr calls, 0 errors, watermark -> 131899548.")
json.dump(st, open(f"{BASE}/onchain-scan-state.json", "w"), indent=1)

# --- 6. Hot-leg seen: the 1 new Sourcify contract from 5a ---
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen["0x6d5950B0d93672BAc882251Eb44A5b8c8F1688f5"] = {
    "first_seen_wib": "2026-11-06T07:41:00+07:00",
    "note": "S1=False S2=False mint=False quote=False free=[] agent=False token=[name/symbol/decimals/totalSupply] (plain ERC-20 with blacklist/pause)",
    "source": "sourcify-feed", "status": "checked-not-sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("finalize done; snapshot contracts:", len(s["contracts"]), "; hot-leg-seen:", len(seen))
