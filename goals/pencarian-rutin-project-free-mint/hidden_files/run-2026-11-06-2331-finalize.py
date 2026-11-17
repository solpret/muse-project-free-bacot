import json, shutil, copy
HF = "."
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
reread = json.load(open(f"{HF}/run-2026-11-06-2331-reread.json"))
vel = json.load(open(f"{HF}/run-2026-11-06-2331-velocity.json"))
bridge = json.load(open(f"{HF}/scan-bridge.json"))
fresh = json.load(open(f"{HF}/run-2026-11-06-2331-verify-fresh3.json"))
REREAD_BLOCK = reread["block"]  # 132043684
contracts = snap["contracts"]
excluded = snap.setdefault("excluded", {})

# --- 1. merge reread (non-None only) ---
merged = 0
for name, rv in reread["reread"].items():
    if name not in contracts or not isinstance(rv, dict):
        continue
    e = contracts[name]
    changed = False
    for k, v in rv.items():
        if k in ("address", "_batch_error", "_batch_v2"):
            continue
        if v is not None:
            e[k] = v; changed = True
    e["lastReadBlock"] = REREAD_BLOCK
    e["lastReadWib"] = "2026-11-06 run 2331"
    merged += 1

# --- 2. fresh independent verification overrides (block 132048801, ~00:27 WIB 2026-11-07) ---
FRESH_BLOCK = fresh["block"]
for name, fr in fresh["reads"].items():
    key = {"Soul Agent":"Soul Agent","Mars Nexus":"Mars Nexus","Orzo-39f6":"Orzo-39f6",
           "Qilingentle-423d":"Qilingentle-423d","Hivejupiter-8DF7":"Hivejupiter-8DF7",
           "MoonCat":"MoonCat"}[name]
    if key not in contracts: continue
    e = contracts[key]
    if fr.get("totalSupply") is not None: e["totalSupply"] = fr["totalSupply"]
    if fr.get("balanceOf_user") is not None:
        e["balanceOf_user"] = fr["balanceOf_user"]; e["userBalance"] = fr["balanceOf_user"]
    e["lastReadBlock"] = FRESH_BLOCK
    e["lastReadWib"] = "2026-11-07 00:27 WIB (verifikasi segar parent, blok 132048801)"
    e["runNote2331_fresh"] = f"Verifikasi segar parent blok {FRESH_BLOCK}: totalSupply {fr.get('totalSupply')}, balanceOf(user) {fr.get('balanceOf_user')}."
print("merged reread contracts:", merged, "| fresh overrides: 6")

# --- 3. velocity merge ---
vmerged = 0
for row in vel.get("rows", []):
    name = row.get("name")
    if name not in contracts: continue
    e = contracts[name]
    for k in ("mintedInInterval","intervalMinutes","currentRatePerMin","previousRatePerMin","velocityLegPasses"):
        if row.get(k) is not None: e[k] = row[k]
    if row.get("velocityNote"): e["velocityNote"] = row["velocityNote"]
    vmerged += 1
for p in vel.get("passes", []):
    name = p["name"]
    if name in contracts:
        contracts[name]["runNote2331_velocity"] = (
            f"Run 2331: velocity LOLOS (+{p['mintedInInterval']}, {p['ratePerMin']}/mnt vs prev "
            f"{p['prevRatePerMin']} = {p['ratioVsPrev']}x) TAPI free% "
            f"{'UNVERIFIED' if p.get('freePct') is None else str(p['freePct'])+'% (nilai 2301, bukan segar)'} + slot/umur "
            f"tidak lengkap -> TIDAK promosi, tetap watchlist-only.")
print("velocity rows merged:", vmerged, "| passes:", [p["name"] for p in vel.get("passes", [])])

# --- 4. track_c merge (non-None totalSupply/free views) ---
tc_merged = 0
for name, rv in reread.get("track_c", {}).items():
    if name not in snap.get("track_c", {}) or not isinstance(rv, dict): continue
    e = snap["track_c"][name]
    for k, v in rv.items():
        if k in ("address", "_batch_error", "_batch_v2"): continue
        if v is not None: e[k] = v
    e["lastReadBlock"] = REREAD_BLOCK
    e["lastReadWib"] = "2026-11-06 run 2331"
    tc_merged += 1
print("track_c merged:", tc_merged)

# --- 5. NEW sellouts (15): prev < max, cur == max ---
NEW_SELLOUT = ["Hexagent","Agentjiayou","Neonmind","Batbot","Astrogent","Duneswarm","Marsagentis",
               "Petalhive","Quantumnode","Kabutomind","Pilotphoenix","Krillfarm","Saturnswarm-238c",
               "Boohiveling-c1da","Cybergentle-3571"]
discarded = {a.lower() for a,v in bridge.get("contracts",{}).items() if v.get("same_owner_discarded")}
reportable, logonly = [], []
for name in NEW_SELLOUT:
    if name not in contracts:
        print("WARN sellout not in contracts:", name); continue
    e = contracts.pop(name)
    prev = next((r["prevSupply"] for r in vel.get("soldOut",[]) if r["name"]==name), e.get("totalSupply"))
    e["status"] = "sold-out-2026-11-06"
    e["selloutNote2331"] = (f"Run 2331: totalSupply {e.get('totalSupply')} = MAX_SUPPLY {e.get('MAX_SUPPLY')} "
        f"(terakhir {prev}) blok {REREAD_BLOCK} -> SOLD OUT, dipindah contracts -> excluded.")
    excluded[name] = e
    (logonly if e.get("address","").lower() in discarded else reportable).append(name)
print("sellouts moved:", len(NEW_SELLOUT), "| reportable:", reportable, "| run-log-only (same_owner_discarded):", logonly)

# --- 6. Soul Agent age-exclusion (deadline 2026-11-06 23:53:44 WIB lewat; fresh 1573 < 3000) ---
soul = contracts.pop("Soul Agent", None)
assert soul is not None, "Soul Agent missing from contracts!"
soul["status"] = "age-excluded-2026-11-06"
soul["ageExclusionNote2331"] = ("First mint terverifikasi 2026-11-04 23:53:44 WIB (blok 131660224); "
    "deadline 48 jam 2026-11-06 23:53:44 WIB LEWAT. Verifikasi segar parent blok 132048801 "
    "(~00:27 WIB 2026-11-07): totalSupply 1573 < FREE_TIER_END 3000 / MAX_SUPPLY 5555 -> BELUM sold out. "
    "Slot user terbuka (quote 0, mintedPerWallet 0, balance 0). Dihapus dari watchlist aktif per aturan umur.")
excluded["Soul Agent"] = soul
print("Soul Agent age-excluded.")

# --- 7. snapshot run notes ---
snap["runNote2331_1106"] = (
 "Run 2331 (23:31 WIB 2026-11-06 s.d. ~00:30 WIB 2026-11-07): 0 kandidat, 0 auto-mint/claim, 0 strong-lead baru, "
 "0 early-lead baru. 15 SELLOUT BARU dipindah contracts -> excluded (9 dilaporkan sekali: Agentjiayou, Neonmind, "
 "Batbot, Marsagentis, Pilotphoenix, Quantumnode, Saturnswarm-238c, Boohiveling-c1da, Cybergentle-3571; 6 run-log-only "
 "same_owner_discarded: Hexagent, Astrogent, Duneswarm, Petalhive, Kabutomind, Krillfarm). 1 AGE-EXCLUSION: Soul Agent "
 "(deadline 48 jam 2026-11-06 23:53:44 WIB lewat; fresh totalSupply 1573 < FREE_TIER_END 3000, blok 132048801). "
 "MoonCat 1098/1111 (13 tersisa, belum sold out). Qilingentle + Hivejupiter sama-sama 500 (MAX tak diketahui -> sold-out "
 "unverified, tetap watchlist). Mars Nexus + Orzo-39f6 balanceOf(user) 0 -> 1 (verifikasi segar blok 132048801; "
 "bukan eksekusi run ini — asal mint tidak diketahui, dicatat saja). Velocity lolos 2 tapi TIDAK promosi: SEAT-f11e "
 "+90 (6,26x, free%/slot unverified) + Agent Frogs +22 (3,48x, free% 46,08% nilai 2301). Chipdroidling 683/700 + "
 "Swarmganbei 692/700 nyaris sold out; umur keduanya UNVERIFIED -> tetap watchlist, TIDAK age-exclude. "
 "BINANCEAI: launched/failed None run ini (transport gagal); nilai 2301 dipertahankan (launched 0, failed 1, refund 1). "
 "Grove fase 2: freeOpen 0, tetap belum dibuka. BNB Guardian AI (MINTS index, 0x1d3B27e222EFDEd06736C503D52c4884BF0a9117): "
 "Sourcify not_verified + website null -> gate-blocked, BUKAN lead, tidak masuk snapshot. 3 first-seen scan BUKAN early "
 "lead (Agent Card 0xeE17.., RIPSTACK 0x7237.., Mizukairo 0x43F0..). Sourcify feed 0 S1/S2; retry transport-failed: 5 "
 "terselesaikan not-sale-shape, 4 masih terbuka (0x48b9.., 0x5DB6.., 0xf955.., 0xAE6b..). Route 5c: 0 baru (50/50 sudah dicek; "
 "backfill menambah 56 entri ke track-c-scan-checked.json secara paralel, bukan run ini). Bridge: 115 kontrak, 0 di luar snapshot.")
snap["runNote2331_scan_1106"] = (
 "Scan run 2331: pre-flight v1 gagal (Ankr eth_blockNumber + race dataseed timeout), retry OK 5,0 dtk (675 log). "
 "Attempt 1 gagal chunk pertama (timeout, 0 kontrak). Attempt 2: head 132043740, jendela diminta 132042741-132043740; "
 "chunk berhenti di chunk ke-7 (2x timeout) -> hanya 300 blok ter-cover (132042741-132043040); 700 blok gap milik backfill. "
 "Enrichment timeout 780 dtk (SCAN_EXIT=124): 51/76 ter-enrich, JSON parsial. Watermark TIDAK dimajukan (milik backfill). "
 "Triage first-seen memakai seen['contracts'] (9820 entri): 3 true first-seen, ketiganya BUKAN early lead.")
snap["last_run_wib"] = "2026-11-07 run 2331 (00:30 WIB)"
snap["last_run"] = "2026-11-07 run 2331"
snap["timestamp_wib"] = "2026-11-07T00:30:00+07:00"
json.dump(snap, open(f"{HF}/onchain-snapshot.json","w"), indent=1)
print("contracts now:", len(snap["contracts"]), "| track_c:", len(snap.get("track_c",{})), "| excluded:", len(excluded))
print("REPORTABLE SELLOUTS:", reportable)
print("LOG-ONLY SELLOUTS:", logonly)
