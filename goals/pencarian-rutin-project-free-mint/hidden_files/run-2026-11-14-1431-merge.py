#!/usr/bin/env python3
"""Merge run 2026-11-14 14:31 WIB (free-mint-search run 1431) into onchain-snapshot.json.
Read-only on-chain data already collected in run-2026-11-14-1431-reread.json /
verify*.json. Updates snapshot + run notes. No preview/mint."""
import json, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-14-1431-reread.json"))
BLOCK = reread["block"]  # 133504646
INTERVAL_MIN = (BLOCK - 133500940) * 0.45 / 60.0  # ~27.8 min vs run 1401 block
C = snap["contracts"]
SUPPLY_KEY = {  # which read field is the supply for velocity
 "WoozCode": "totalSnippets", "MORFO": "totalMinted", "NOISE": "totalMinted",
 "DragonAgents": "totalSupply", "AngelEye-77D9": "totalSupply", "AngelEye-07bD": "totalSupply",
 "NovaRemnants": "totalRemnants", "RaceAgents": "totalSupply", "AbsurdAgentNFT": "totalMinted",
 "B77D": "totalMinted", "Zero": "totalSupply", "HIVE": "totalSupply",
 "AgentZENITH": "totalSupply", "AgentNOVA": "totalSupply", "SPARKS": "totalSupply",
 "AgentBubble": "totalSupply", "WANGCAI": "totalSupply", "YUANBAO": "totalSupply",
 "NOTV": "totalSupply", "PX24": "totalSupply", "Zephyra": "totalMinted",
 "LumenFindings": "totalSpecimens", "Pengu": "totalMinted", "CPASS": "totalMinted",
 "SPEC": "totalSpecimens", "TrashBandits": "totalMinted", "SKRR": "totalSupply",
 "REOPIR": "totalSupply", "FrieAgent-B751": "totalSupply", "FrieAgent-c64d": "totalSupply",
 "Ledgera": "totalSupply", "MAMI": "totalSupply", "INKI": "totalSupply", "OTV": "totalSupply",
}
def vel_note(name, new_ts, prev_ts, prev_rate):
    if new_ts is None or prev_ts is None:
        return None, None, None
    minted = new_ts - prev_ts
    rate = minted / INTERVAL_MIN if INTERVAL_MIN else 0.0
    ratio = (rate / prev_rate) if prev_rate else None
    passes = bool(ratio is not None and ratio >= 1.5 and minted >= 20)
    note = (f"Run 1431 (blok {BLOCK}, interval ~{INTERVAL_MIN:.1f} mnt vs run 1401): "
            f"{prev_ts}->{new_ts} (+{minted}, {rate:.4f}/mnt vs prev {prev_rate} = "
            f"{ratio if ratio is None else round(ratio,2)}x) -> velocity "
            f"{'LOLOS' if passes else 'GAGAL'}")
    return minted, rate, (ratio, passes, note)
notes = {}
for name, item in reread["reads"].items():
    views = item.get("views")
    if name not in C:
        C[name] = {"address": item["address"]}
    e = C[name]
    if views is None:
        notes[name] = f"Run 1431: SEMUA view gagal baca (nilai lama dipertahankan)."
        continue
    sk = SUPPLY_KEY.get(name)
    prev_ts = e.get("previousTotalSupply")
    if prev_ts is None:
        prev_ts = e.get("totalSupply") if sk == "totalSupply" else e.get("totalMinted")
    new_ts = views.get(sk) if sk else None
    prev_rate = e.get("previousRatePerMin")
    minted, rate, vres = vel_note(name, new_ts, prev_ts, prev_rate)
    # store views (skip None overwrites for supply/free views)
    for k, v in views.items():
        if v is not None:
            e[k] = v
    if new_ts is not None:
        e["previousTotalSupply"] = new_ts
    if rate is not None:
        e["previousRatePerMin"] = round(rate, 4)
        e["currentRatePerMin"] = round(rate, 4)
    if vres:
        ratio, passes, note = vres
        e["velocityRatio"] = ratio
        e["velocityLegPasses"] = passes
        e["runNote1431_1114"] = note
        notes[name] = note
    e["lastReadBlock"] = BLOCK
    e["lastReadWib"] = "2026-11-14 ~14:31 WIB"
    if minted is not None:
        e["mintedInInterval"] = minted
        e["intervalMinutes"] = round(INTERVAL_MIN, 1)
# --- item-specific updates ---
# YUANBAO: strong-lead legs verified; gate verdict pending method (L) browser read
y = C["YUANBAO"]
y["first_mint_block"] = 133435803
y["first_mint_wib"] = "2026-11-14 05:58:45 WIB"
y["first_mint_tx"] = "0xedefe5fee1fc56b0439fb5ee5c1b8593a05f0f1fc793ffa1ababfce60a4f3a64"
y["launch_verified"] = True
y["free_pct"] = round(163/188*100, 1)
y["slot_user_open"] = True
y["website"] = None
y["gate"] = "website_failed_pending_L"
y["status"] = "strong-lead-gate-blocked-2026-11-14"
# WANGCAI
w = C["WANGCAI"]
w["free_pct"] = round(129/188*100, 1)
# Ledgera / MAMI / INKI: free% where known
C["Ledgera"]["free_pct"] = round(2419/5000*100, 1)
# ORBIT track_c
tc = snap.setdefault("track_c", {})
if "ORBIT" in tc:
    tc["ORBIT"]["freeClaimed"] = 237
    tc["ORBIT"]["lastReadBlock"] = BLOCK
    tc["ORBIT"]["lastReadWib"] = "2026-11-14 ~14:31 WIB"
    tc["ORBIT"]["runNote1431"] = ("Run 1431: freeClaimed 235->237/888 (26,7%), claimOpen=1, "
        "hasFreeClaimed(user)=0, slot terbuka; umur TETAP UNVERIFIED, website NOT CHECKED -> watchlist-only, tanpa perubahan.")
# binanceai pending claim
pc = snap.setdefault("pending_claims", {}).get("binanceai.fun", {})
pc["lastReadWib"] = "2026-11-14 ~14:31 WIB"
pc["runNote1431"] = ("Run 1431: launched=0, failed=1, isRefundPhase=1, totalShares=3110, "
    "tokenClaimed(user)=0 (blok %d) - tetap pending/refund, sudah dilaporkan sekali (fase refund), DIAM" % BLOCK)
# --- new entries ---
C["Hashcat Depot"] = {
 "address": "0x5aff123300685b6e08aa4396227baf44aabbd4ed",
 "name": "Hashcat Depot", "symbol": "HADE", "kind": "ERC721",
 "status": "watchlist-only-checked-not-lead-2026-11-14",
 "totalSupply": 158, "MAX_SUPPLY": 1125, "mintOpen": 1,
 "mintedBy_user": 0, "balanceOf_user": 0,
 "firstSeenBlock": None, "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~14:31 WIB",
 "website": None, "gate": "website_unverified",
 "launchNote": ("Umur UNVERIFIED: Boltbook pertama menyebut 146/1.125 ~14:2x WIB 14 Nov; "
   "first-mint TIDAK terverifikasi — eth_getLogs jendela 133490000-133493999 gagal semua endpoint "
   "(limit/timeout) kecuali 133491000-133491999 = 0 log; Ankr 401. Sourcify verifiedAt 2026-11-12T19:03:07Z BUKAN launch time."),
 "baselineNote": ("BARU dari Boltbook EN+ZH run 1431 (3 post: 146/1.125, 150/1.125 blok 133503739, 152/1.125 "
   "+20 mnt/~11 mnt). On-chain run ini: totalSupply 158, MAX_SUPPLY 1125, mintOpen 1, mintedBy(user)=0 (slot terbuka); "
   "Sourcify exact_match 34 fns (mint/mintWithAgentTokenId/costOf/mintedBy/mintsLeft/agentIds) TAPI tanpa satu pun free view "
   "(freeClaimed/freeMinted/freeLeft/freeFor semua revert) + registry bytes TIDAK ada di bytecode -> free% UNVERIFIED; "
   "tokenURI(1) = https://hashcatdepot.668823.xyz/meta/1.json (metadata host, tanpa external_url); "
   "situs https://hashcatdepot.668823.xyz/ fetch teks JS shell, TIDAK mencetak kontrak -> website UNVERIFIED. "
   "BUKAN early lead (first mint unverified + free% unverified, preseden Ledgera/MAMI/INKI run 1401). Watchlist-only."),
 "source": "Boltbook EN+ZH run 1431",
}
C["Saturnagent"] = {
 "address": "0xef870a9b4a529373fb2e174b59ca7a66eb018074",
 "name": "Saturnagent", "kind": "ERC721",
 "status": "checked-not-lead-2026-11-14",
 "totalSupply": 1992, "freeClaimed": 1988, "FREE_SUPPLY": 2000, "MAX_SUPPLY": 2000,
 "mintOpen": 1, "mintedBy_user": 0, "balanceOf_user": 0,
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~14:31 WIB",
 "website": None, "gate": "website_unverified",
 "launchNote": ("Umur UNVERIFIED: Sourcify verifiedAt 2026-11-03T10:20:03Z (verifikasi, BUKAN launch time); "
   "first-mint belum dicek (12 free tersisa, nilai lanjut rendah)."),
 "baselineNote": ("Disebut Boltbook run 1431 (post KRYNT 14:25 WIB: 'Saturnagent 9 left'). On-chain run ini: "
   "freeClaimed 1988/2000 = 99,4% (>70%), slot user terbuka (mintedBy 0), mintOpen 1; Sourcify exact_match "
   "(AGENT_ID + free views + quote). BUKAN strong lead: umur UNVERIFIED (verifiedAt 3 Nov, ~11 hari lalu, "
   "sangat mungkin >24 jam) + website belum dicek. Dicatat checked-not-lead, tidak masuk reread rutin."),
 "source": "Boltbook run 1431",
}
C["ECHO-ERC20"] = {
 "address": "0xb3ca4b947872f92307bcb5b69fb3a675abfd8f41",
 "name": "ECHO", "symbol": "ECHO", "kind": "ERC20",
 "status": "checked-not-sale-shape-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~14:31 WIB",
 "baselineNote": ("Boltbook recheck run 1431 (21.250.000 minted). Sourcify exact_match (verifiedAt 2026-11-11T07:03:42Z): "
   "fns BUY_TAX_BPS/SELL_TAX_BPS/configurePair/openTrading/burnLiquidityReserve — token pajak/AMM, TANPA mint/quote/free view/registry "
   "-> BUKAN bentuk sale S1/S2, bukan track C, bukan early lead. Tidak masuk snapshot watchlist aktif."),
 "source": "Boltbook run 1431",
}
C["Feed-0x5489"] = {
 "address": "0x5489becd5DE0f0Ec6a8B49C9a6DC59D03eC3e5F1",
 "kind": "ERC20", "status": "checked-not-agent-shaped-2026-11-14",
 "lastReadBlock": BLOCK, "lastReadWib": "2026-11-14 ~14:31 WIB",
 "baselineNote": ("Sourcify feed run 1431 (verifiedAt 2026-11-14T07:32:08Z, satu-satunya yang baru vs hot-leg-seen). "
   "exact_match 43 fns (buyPackage/claimPairing/airdrop/lpLaunched/usdt) — token TERA paket/airdrop, TANPA mint/quote/free view/registry "
   "-> BUKAN agent-shaped, bukan S1/S2. Tidak dilaporkan, tidak masuk watchlist."),
 "source": "Sourcify feed run 1431",
}
snap["last_run_wib"] = "2026-11-14 ~14:31 WIB"
snap["last_run"] = "run-1431"
json.dump(snap, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("merge done; interval", round(INTERVAL_MIN, 1), "min; block", BLOCK)
for k in ["NOISE","B77D","CPASS","RaceAgents","WANGCAI","YUANBAO","Ledgera","MAMI","INKI","Zephyra","AgentBubble","DragonAgents"]:
    print(k, "->", notes.get(k, "(no velocity note)"))
