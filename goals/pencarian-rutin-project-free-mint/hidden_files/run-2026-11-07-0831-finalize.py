import json, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
reread=json.load(open(f"{BASE}/run-2026-11-07-0831-reread.json"))
vel=json.load(open(f"{BASE}/run-2026-11-07-0831-velocity.json"))
BLOCK=reread["block"]  # 132113850
# 1. apply reread to contracts (non-None overwrites; None retains old)
n_upd=0
for k,v in reread["reread"].items():
    if k not in snap["contracts"] or not isinstance(v,dict): continue
    e=snap["contracts"][k]
    for f in ("totalSupply","totalMinted","freeClaimed","freeMinted","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user","freeClaimed_user"):
        if v.get(f) is not None:
            e[f]=v[f]
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-07 run 0831"
    n_upd+=1
# velocity rates for passes
velmap={p["address"].lower():p for p in vel["passes"]}
for k,e in snap["contracts"].items():
    a=(e.get("address") or "").lower()
    if a in velmap:
        p=velmap[a]
        e["ratePerMin"]=p["ratePerMin"]; e["prevRatePerMin"]=p["prevRatePerMin"]
        e["ratioVsPrev"]=p["ratioVsPrev"]; e["mintedInInterval"]=p["mintedInInterval"]
        e["velocityNote"]=f"run 0831: +{p['mintedInInterval']} in {p['intervalMin']:.1f} min, rate {p['ratePerMin']:.4f}/min, ratio {p['ratioVsPrev']:.2f} vs prev"
# 2. track_c reread apply
n_tc=0
for k,v in reread["track_c"].items():
    if k not in snap.get("track_c",{}) or not isinstance(v,dict): continue
    e=snap["track_c"][k]
    for f in ("totalSupply","freeMinted","freeSharesRemaining","balanceOf_user","freeClaimed_user"):
        if v.get(f) is not None:
            e[f]=v[f]
    e["lastReadBlock"]=BLOCK
    e["lastReadWib"]="2026-11-07 run 0831"
    n_tc+=1
# 3. age deletions (proven >48h, not sold out; decided run 0731, confirmed run 0831)
deleted=[]
for k in ("Pulsekeep","Tensortug"):
    if k in snap["contracts"]:
        e=snap["contracts"].pop(k)
        deleted.append({"name":k,"address":e.get("address"),"first_seen_block":e.get("firstSeenBlock"),
                        "last_totalSupply":e.get("totalSupply"),"maxSupply":e.get("MAX_SUPPLY"),
                        "reason":"age-excluded >48h (first_seen < threshold 131731772, head 132115772), not sold out",
                        "deleted_run":"2026-11-07-0831"})
ex=snap.setdefault("excluded",{})
for d in deleted:
    ex[d["name"]]={"address":d["address"],"track":"A","status":"excluded-age-over-48h-2026-11-07",
                   "note":d["reason"]+f"; last totalSupply {d['last_totalSupply']}/{d['maxSupply']}; first_seen {d['first_seen_block']}"}
# 4. Tampesta-6aA5 sold out (reread totalSupply 2222/2222, parent-verified blok 132103698)
t=snap["contracts"].get("Tampesta-6aA5")
if t:
    t["status"]="sold-out-2026-11-07"
    t["totalSupply"]=2222; t["MAX_SUPPLY"]=2222
    t["soldOutNote"]="Sold out 2222/2222 terverifikasi: parent blok 132103698 + reread run 0831 totalSupply 2222 blok 132113850."
# 5. MERGEBORN free lane sold out (fresh freeMinted()=800/800 run 0831 + Boltbook post 07:23)
m=snap["contracts"].get("MERGEBORN")
if m:
    m["status"]="sold-out-free-lane-2026-11-07"
    m["freeMinted"]=800
    m["soldOutNote"]="Free lane HABIS 800/800: freeMinted() segar = 800 run 0831 (Boltbook post 07:23 WIB sama). Paid lane (0.0005 BNB) tetap ada tapi free lane habis -> bukan lead lagi."
# 6. ONI upcoming watchlist (pre-launch; mint opens 2026-11-07 12:00 WIB)
snap["contracts"]["ONI-74bD"]={
 "address":"0x74bDA11E34EB02121104Ff38471D91Fe1C37F81A",
 "status":"upcoming-watchlist-2026-11-07",
 "name":"ONI","symbol":"ONI","kind":"ERC721",
 "firstSeenBlock":None,
 "mintOpensAtWib":"2026-11-07 12:00 WIB",
 "mintOpensAtEpoch":1794027600,
 "MAX_SUPPLY":4444,"FREE_POOL":1000,"PAID_POOL":3400,
 "totalMinted":0,"freeMinted":0,
 "token":"0xc12E2d8d4476C99Fd5Ae4700C87746A996C991a2",
 "factory":"0xca143ce32fe78f1f7019d7d551a6402fc5350c73",
 "baselineNote":"Feed Sourcify run 0831 (verified 2026-11-07T01:19:31Z): ABI 63 fns incl mintFree/mintPaid/claim/rarityOf/registry; totalMinted 0, freeMinted 0, poolSeeded 0, pair 0 -> BELUM launching (0 mint). Tier-mint (TIER_COMMON/RARE/EPIC/LEGENDARY/MYTHIC). registry() return REVERT saat dicek (fn ada di ABI) -> registry reference unverified. Lacak sesudah 12:00 WIB.",
 "lastReadBlock":BLOCK,"lastReadWib":"2026-11-07 run 0831"}
# 7. Pea Fun Pod fresh values (early lead, no promotion: free 9.0% <25%)
pp=snap["contracts"].get("PeaFunPod-1901")
if pp:
    pp["freePodsRemaining"]=4561
    pp["freePodsClaimed"]=450
    pp["FREE_PODS_TOTAL"]=5000
    pp["totalPodsMinted"]=450
    pp["freeWindowOpen"]=1
    pp["freeWindowClosesAtWib"]="2026-11-07 18:55 WIB"
    pp["gateStartWib"]="2026-11-06 18:55 WIB"
    pp["registryExact"]=True
    pp["freeClaimedBy_user"]=0
    pp["MAX_PODS_PER_WALLET"]=10
    pp["lastReadBlock"]=BLOCK; pp["lastReadWib"]="2026-11-07 run 0831"
    pp["velocityNote"]="run 0831: free 450/5000 = 9.0% <25% -> BUKAN strong lead; gateStart 2026-11-06 18:55 WIB (umur ~14 jam, <=48h); slot user terbuka (freeClaimedBy=0); window tutup 2026-11-07 18:55 WIB."
# 8. run note
snap["runNote0831_1107"]=("Run 0831: 0 kandidat, 0 strong lead baru/promosi, 0 early lead baru, 0 track-C lead/kandidat, "
 "0 pending claim baru/dibuka. Preflight PASS 6,8 dtk (head 132113817). Reread 457 kontrak + 57 track_c, blok 132113850. "
 "Scan SUKSES window 132112966-132113965 (1000 blok, cap), 40 Ankr calls, 0 error, 107 NFT + 290 ERC-20 mint; 0 first-seen sejati. "
 "Velocity 9 pass, semua gagal kaki lain (free% unverified/<25% atau umur unverified). "
 "Age-exclusion: Pulsekeep + Tensortug DIHAPUS (>48j, tidak sold out). "
 "Sold out: Tampesta-6aA5 2222/2222 (ditandai), MERGEBORN free lane 800/800 (ditandai, freeMinted segar). "
 "ONI 0x74bD upcoming (mint buka 2026-11-07 12:00 WIB, FREE_POOL 1000, 0 mint). "
 "Pea Fun Pod: free 450/5000 (9,0%), registry exact, window tutup 18:55 WIB — tetap early lead, bukan strong. "
 "BINANCEAI tetap refund/failed; Grove freeOpen 0. Track C 5c: 2 baru dicek, 0 sale-shape; BLOCK777 gate-blocked tak berubah. "
 "Watermark TIDAK dimajukan run ini (backfill owns it; triase backfill 132112140-132114145 sedang jalan menutup gap 132112140-132112965). "
 "No execution attempted.")
snap["last_run_wib"]="2026-11-07 08:31 WIB"
snap["timestamp_wib"]="2026-11-07 08:31 WIB"
snap["last_run"]="2026-11-07-0831"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print(f"contracts updated: {n_upd}, track_c updated: {n_tc}, deleted: {[d['name'] for d in deleted]}")
print("contracts now:", len(snap["contracts"]), "track_c:", len(snap.get("track_c",{})))
