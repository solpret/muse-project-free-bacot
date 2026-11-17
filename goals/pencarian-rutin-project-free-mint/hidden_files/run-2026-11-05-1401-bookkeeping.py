"""Run 1401 stage-1 bookkeeping: re-read + early-probe + track-C updates.
Applies ONLY the on-chain re-read results (block 131773397 / probe 131773641).
Scan triage (stage 2) is applied separately after the scan finishes.
"""
import json, shutil, copy
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1401.bak.json")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]
RUN="2026-11-05 run 1401"
BLK=131773397
def upd(name, **kw):
    if name not in C:
        print("MISS", name); return
    C[name].update(kw)
    C[name]["lastReadBlock"]=BLK
    C[name]["lastReadWib"]=RUN

# --- Track A re-read (interval ~30.2 min vs run 1331 block 131769378) ---
upd("HIVE Agents", totalSupply=1242, previousTotalSupply=1241, mintedInInterval=1,
    intervalMinutes=30.2, currentRatePerMin=0.033, previousRatePerMin=0.033,
    velocityLegPasses=False,
    velocityNote1401="Run 1401 (blok 131773397): 1241->1242 (+1, <20) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
upd("Tigora-E8c4", totalMinted=599,
    velocityNote1401="Run 1401: totalMinted 599 flat vs 1331 (599) -> velocity GAGAL.")
upd("BNBRunnerz-2674", totalSupply=3176, previousTotalSupply=3162, mintedInInterval=14,
    intervalMinutes=30.2, currentRatePerMin=0.464, velocityLegPasses=False,
    velocityNote1401="Run 1401: 3162->3176 (+14, <20) -> velocity GAGAL.")
upd("Shroomies-2AE7", totalSupply=906, previousTotalSupply=892, mintedInInterval=14,
    intervalMinutes=30.2, currentRatePerMin=0.464, velocityLegPasses=False,
    velocityNote1401="Run 1401: 892->906 (+14, <20) -> velocity GAGAL; price 0.0002 BNB, costOf(user,1)=0, mintOpen 1, mintedBy(user)=0 (slot terbuka); % gratis tetap UNVERIFIED (tanpa free view).")
upd("Blobbies-a7fB", totalSupply=1414, previousTotalSupply=1409, mintedInInterval=5,
    intervalMinutes=30.2, currentRatePerMin=0.166, velocityLegPasses=False,
    velocityNote1401="Run 1401: 1409->1414 (+5, <20) -> velocity GAGAL.")
upd("Jolly", totalMinted=3351, previousTotalSupply=3344, mintedInInterval=7,
    intervalMinutes=30.2, currentRatePerMin=0.232, velocityLegPasses=False,
    firstMintWib="2026-11-03T23:27:33+07:00",
    velocityNote1401="Run 1401: totalMinted 3344->3351 (+7, <20) -> velocity GAGAL; tetap strong-lead-gate-blocked. First mint TERVERIFIKASI run ini (binary-search Ankr): blok 131464781 = 2026-11-03 23:27:33 WIB -> umur ~38,6 jam <=48 jam, masih dalam jendela.")
upd("HACKED", totalSupply=3282, previousTotalSupply=3230, mintedInInterval=52,
    intervalMinutes=30.2, currentRatePerMin=1.722, previousRatePerMin=1.722, velocityLegPasses=False,
    velocityNote1401="Run 1401: 3230->3282 (+52, ~1,72/mnt). Snapshot TIDAK menyimpan previous rate run 1331 (previousRatePerMin=None; md run 1331 menyebut 1,07/mnt tapi tidak terpersist ke snapshot) -> kaki velocity TIDAK lolos dari state snapshot (vs stored currentRate 1,254 = 1,37x <1,5x). Rate saat ini disimpan untuk run berikut. Minted-by-user (balance 2), bukan kandidat baru.")
upd("SoulAgent", totalSupply=667, previousTotalSupply=663, mintedInInterval=4,
    intervalMinutes=30.2, currentRatePerMin=0.132, velocityLegPasses=False,
    velocityNote1401="Run 1401: 663->667 (+4, <20) -> velocity GAGAL; tetap EARLY.")
upd("PERSONA-A930", totalSupply=1120, previousTotalSupply=1120, mintedInInterval=0,
    intervalMinutes=30.2, currentRatePerMin=0.0, velocityLegPasses=False,
    velocityNote1401="Run 1401: 1120 flat -> velocity GAGAL; tetap EARLY.")
upd("RigOrb-539e", totalSupply=615, previousTotalSupply=591, mintedInInterval=24,
    intervalMinutes=30.2, currentRatePerMin=0.795, previousRatePerMin=0.87, velocityLegPasses=False,
    velocityNote1401="Run 1401: 591->615 (+24; ~0,80/mnt vs stored 0,87 = 0,92x) -> velocity GAGAL; mintOpen 1, priceFor(user,1)=0, mintedCount(user)=0; % pool tetap UNVERIFIED (free views revert) -> tetap EARLY, BUKAN strong lead, TIDAK di-preview/di-mint.")

# --- Robogent AGE-EXCLUSION (verified first mint 2026-11-03 12:20:32 WIB) ---
robo=C.pop("Robogent")
s.setdefault("excluded",{})["Robogent"]={
 "address": robo.get("address"), "symbol": robo.get("symbol"), "track": "A",
 "status": "excluded-age-over-48h-2026-11-05",
 "note": "Age-excluded run 1401: first mint TERVERIFIKASI 2026-11-03T12:20:32+07:00 (binary-search Ankr getLogs: blok pertama Transfer-from-zero 131375872; 0 log pada pre-window 131355631-131375630). Pada re-read run 1401 (blok 131773397, ~14:05 WIB) umur ~49,7 jam >48 jam dan BELUM sold out (totalSupply 1205 flat vs 1331, freeClaimed 1201/2000 = 60,05%). Dihapus dari watchlist aktif per aturan 48 jam; status lama strong-lead-gate-blocked-2026-11-03. Dilaporkan sekali sebagai perubahan (age-exclusion) ke parent run 1401; tidak di-preview/di-mint.",
 "previous_status": "strong-lead-gate-blocked-2026-11-03",
 "firstMintWib": "2026-11-03T12:20:32+07:00",
 "lastReading": "totalSupply 1205, freeClaimed 1201/2000 (re-read run 1401 blok 131773397)",
}
print("Robogent moved to excluded.")

# --- Early leads (probe block 131773641; interval ~30 min vs run 1331 probe) ---
def upd_early(name, supply, free, pct, note):
    if name not in C: print("MISS", name); return
    C[name].update({"totalSupply": supply, "freeClaimed": free, "freePctVerified": pct,
                    "lastReadBlock": 131773641, "lastReadWib": RUN})
    C[name][f"runNote1401"] = note
upd_early("Thronemind", 388, 388, 19.4,
 "Run 1401: 311->388 (+77; ~2,57/mnt vs run 1331 ~3,6/mnt = 0,71x) -> velocity GAGAL; free 388/2000 = 19,4% <25% -> tetap EARLY; slot terbuka (claimedFree(user)=0, canFreeMint=1, balance 0).")
upd_early("Hashseers", 387, 387, 19.35,
 "Run 1401: 298->387 (+89; ~2,97/mnt vs run 1331 ~4,47/mnt = 0,66x) -> velocity GAGAL; free 387/2000 = 19,35% <25% -> tetap EARLY; slot terbuka.")
upd_early("Layerloom", 359, 359, 17.95,
 "Run 1401: 276->359 (+83; ~2,77/mnt vs run 1331 ~4,17/mnt = 0,66x) -> velocity GAGAL; free 359/2000 = 17,95% <25% -> tetap EARLY; slot terbuka.")
upd_early("Cachejack", 221, 221, 11.05,
 "Run 1401: 137->221 (+84; ~2,8/mnt vs run 1331 ~1,77/mnt = ~1,58x, >=20 token) -> kaki VELOCITY LOLOS, TAPI free 221/2000 = 11,05% <25% -> tetap EARLY, BUKAN strong lead, BUKAN kandidat; slot terbuka.")
upd_early("AgentMiner", 397, None, None,
 "Run 1401: totalSupply 259->397 (+138; ~4,6/mnt vs run 1331 ~6,27/mnt = 0,73x) -> velocity GAGAL. Free % tetap UNVERIFIED: freeMinted/claimedFree/canFreeMint revert (nama fn salah — ABI sebenarnya: freeFor/freeLeft/freeUsed, tanpa counter free-cap); totalSupply 397/4444 = 8,9% sebagai batas atas kasar. Umur terverifikasi <=48 jam (first mint 2026-11-05 12:59:40 WIB), slot terbuka, website/X UNVERIFIED (gate run 1301; metode L tertunda). Tetap EARLY.")
upd_early("Smeltbots", 329, 329, 16.45,
 "Run 1401 (re-read pertama pasca-early): 263->329 (+66); free 329/2000 = 16,45% <25% -> tetap EARLY; velocity belum bisa dihitung (tanpa rate sebelumnya); slot terbuka (claimedFree(user)=0, canFreeMint=1).")
upd_early("Tumblebots", 309, 309, 15.45,
 "Run 1401 (re-read pertama pasca-early): 226->309 (+83); free 309/2000 = 15,45% <25% -> tetap EARLY; velocity belum bisa dihitung; slot terbuka.")
prev_early={"Thronemind":311,"Hashseers":298,"Layerloom":276,"Cachejack":137,"AgentMiner":259,"Smeltbots":263,"Tumblebots":226}
for n in ["Thronemind","Hashseers","Layerloom","Cachejack","AgentMiner","Smeltbots","Tumblebots"]:
    if n in C:
        C[n]["previousTotalSupply"]=prev_early[n]

# --- Extras ---
upd("Saturnode", totalSupply=1715, freeClaimed=1692,
    runNote1401="Run 1401: 1676->1715 (+39; free 1692/4000 = 42,3%); umur tetap UNVERIFIED -> tetap EARLY, BUKAN promosi strong lead (butuh umur terverifikasi); slot terbuka (mintedBy 0).")
# AFROG: not in snapshot before; add as watchlist-only (never reported as a lead)
C["AFROG"]={
 "address": "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
 "name": "Agent Frogs", "symbol": "AFROG", "kind": "ERC721",
 "status": "watchlist-only-2026-11-05",
 "totalSupply": 315, "freeClaimed": 315, "FREE_SUPPLY": 1111, "freePctVerified": 28.35,
 "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0,
 "userSlotNote": "Slot open by read: mintedBy(user)=0, balanceOf(user)=0 - NOT preview-verified (watchlist-only items are never previewed).",
 "firstMintBlock": 131708808, "firstMintWib": "2026-11-05T05:58:10+07:00",
 "launchNote": "First mint TERVERIFIKASI run 1401 (binary-search Ankr): blok 131708808 = 2026-11-05 05:58:10 WIB. Itu batas ATAS waktu launch (launch <= first mint), BUKAN bukti launch <=48 jam — umur peluncuran tetap UNVERIFIED (tanpa waktu launch yang dinyatakan proyek). % melewati 25% sejak run 1231 (25,3%) tapi umur UNVERIFIED -> tetap watchlist-only, BUKAN strong lead.",
 "baselineNote": "Tracked as EARLY in run logs since run 0631 (198/1111 = 17,8%) without a snapshot entry; added to snapshot run 1401 as watchlist-only with full history. NEVER reported as a lead (age unverified from the start). Promotes only on verified age <=48h + >=25% + slot open.",
 "lastReadBlock": BLK, "lastReadWib": RUN,
 "runNote1401": "Run 1401: 302->315 (+13; <20) -> velocity GAGAL; free 315/1111 = 28,35% (>=25%) TAPI umur tetap UNVERIFIED -> tetap watchlist-only, BUKAN promosi strong lead. First mint 2026-11-05 05:58:10 WIB (batas atas launch).",
}
for k,sup,free in [("Swarmcentaur",777,772),("Agentyyds",600,595),("Pilotneon",500,495),("Mummyhive",600,582)]:
    if k in C:
        C[k].update({"totalSupply":sup,"freeClaimed":free,"lastReadBlock":BLK,"lastReadWib":RUN,
                     "runNote1401":f"Run 1401: totalSupply {sup}, free {free} (hampir sellout, belum habis); umur UNVERIFIED; owner grup 0x6f24; tidak ada perubahan tier."})
upd("StarAgent", totalSupply=970,
    runNote1401="Run 1401: totalSupply 962->970 (+8); claimedFree(user)=0; tetap EARLY.")

# --- Track C notes ---
TC=s.get("track_c",{})
def tcn(key, note):
    if key in TC:
        TC[key]["runNote1401"]=note
    else:
        print("TC MISS", key)
tcn("OSK","Run 1401: opened 0, totalMinted 2275 flat — tidak berubah (belum dibuka).")
tcn("NIULAI","Run 1401: launched 0, phase 4 — tidak berubah (arti enum phase 4 MASIH belum terverifikasi).")
tcn("KillZero-K0-sale","Run 1401: launched 0 — tidak berubah.")
tcn("DROID","Run 1401: opened 0, freeMinted 557, totalMinted 557 flat — tidak berubah.")
tcn("IMARS","Run 1401: opened 1, freeMinted 300, totalMinted 624 flat — pool gratis 300/300 tetap habis, bukan lead.")
tcn("ASOC-43cE","Run 1401: freeClaimed(user) 0, saleEnded 0 — masih pre-open (jadwal buka 20:00 WIB), TIDAK di-preview/di-mint.")
tcn("SENBAZURU-b215","Run 1401: opened 1, freeClaimed 212->214 (+2 mint pihak lain), hasFreeShare(user)=1 (slot user terpakai, klaim hot-leg 13:39); paidSold tidak dibaca run ini (dipantau hot-leg).")
tcn("FABE","Run 1401: launched 0, freeSharesRemaining 2821, freeSharesClaimed(user)=1 — slot user sudah dipakai, tidak berubah.")
tcn("ShibAgent-R2","Run 1401: freeClaimed 122->123, phase 1, balanceOf(user)=0 — tanpa perubahan tier.")
tcn("QAGENT-2","Run 1401: freeMinted 6666 flat, sharesMinted 6702 — free pool habis, tidak berubah.")
s["runNote1401_reread"]="Run 1401 stage-1 (re-read blok 131773397 / probe 131773641): HIVE +1, Tigora flat, BNBRunnerz +14, Shroomies +14, Blobbies +5, Robogent flat (AGE-EXCLUDED, lihat excluded), Jolly +7, HACKED +52, SoulAgent +4, PERSONA flat, RigOrb +24 — semua velocity GAGAL kecuali Cachejack (velocity lolos, % 11,05% <25% tetap EARLY). Track-C: tidak ada perubahan (OSK/NIULAI/KillZero/DROID/IMARS/ASOC/FABE/BINANCEAI flat; SENBAZURU 212->214; ShibAgentR2 122->123; QAGENT flat). AFROG ditambahkan ke snapshot sebagai watchlist-only (first mint 2026-11-05 05:58:10 WIB, umur UNVERIFIED)."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("stage-1 bookkeeping done; contracts now:", len(s["contracts"]))
