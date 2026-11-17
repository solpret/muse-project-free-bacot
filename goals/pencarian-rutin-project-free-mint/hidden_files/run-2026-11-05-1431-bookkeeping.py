"""Run 1431 bookkeeping (single stage): re-read + early-probe + track-C updates,
Agent Panda age-exclusion, batch age-exclusion (49), scan state + seen updates.
"""
import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN="2026-11-05 run 1431"
BLK=131777455
PBLK=131777711
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1431.bak.json")
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=s["contracts"]
def upd(name, **kw):
    if name not in C:
        print("MISS", name); return
    C[name].update(kw)
    C[name]["lastReadBlock"]=BLK
    C[name]["lastReadWib"]=RUN
def val(d, fn):
    v=d.get(fn)
    return v if isinstance(v,int) else None

# --- Track A re-read (interval ~30 min vs run 1401) ---
upd("HIVE Agents", totalSupply=1242, previousTotalSupply=1242, mintedInInterval=0,
    intervalMinutes=30.0, currentRatePerMin=0.0, previousRatePerMin=0.033,
    velocityLegPasses=False,
    velocityNote1431="Run 1431 (blok 131777455): 1242 flat vs 1401 (1242) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
upd("Tigora-E8c4", totalMinted=601,
    velocityNote1431="Run 1431: totalMinted 599->601 (+2, <20) -> velocity GAGAL.")
upd("BNBRunnerz-2674", totalSupply=3191, previousTotalSupply=3176, mintedInInterval=15,
    intervalMinutes=30.0, currentRatePerMin=0.5, velocityLegPasses=False,
    velocityNote1431="Run 1431: 3176->3191 (+15, <20) -> velocity GAGAL.")
upd("Blobbies-a7fB", totalSupply=1416, previousTotalSupply=1414, mintedInInterval=2,
    intervalMinutes=30.0, currentRatePerMin=0.067, velocityLegPasses=False,
    velocityNote1431="Run 1431: 1414->1416 (+2, <20) -> velocity GAGAL.")
upd("Jolly", totalMinted=3361, previousTotalSupply=3351, mintedInInterval=10,
    intervalMinutes=30.0, currentRatePerMin=0.333, velocityLegPasses=False,
    velocityNote1431="Run 1431: totalMinted 3351->3361 (+10, <20) -> velocity GAGAL; umur ~39,2 jam (first mint 2026-11-03 23:27:33 WIB) <=48 jam -> tetap strong-lead-gate-blocked, tanpa laporan perubahan.")
upd("HACKED", totalSupply=3312, previousTotalSupply=3282, mintedInInterval=30,
    intervalMinutes=30.0, currentRatePerMin=1.0, previousRatePerMin=1.722, velocityLegPasses=False,
    velocityNote1431="Run 1431: 3282->3312 (+30, ~1,0/mnt vs 1,722 tersimpan = 0,58x) -> velocity GAGAL; minted-by-user (balance 2), bukan kandidat.")
upd("SoulAgent", totalSupply=670, previousTotalSupply=667, mintedInInterval=3,
    intervalMinutes=30.0, currentRatePerMin=0.1, velocityLegPasses=False,
    velocityNote1431="Run 1431: 667->670 (+3, <20) -> velocity GAGAL; tetap EARLY.")
upd("PERSONA-A930", totalSupply=1120, previousTotalSupply=1120, mintedInInterval=0,
    intervalMinutes=30.0, currentRatePerMin=0.0, velocityLegPasses=False,
    velocityNote1431="Run 1431: 1120 flat -> velocity GAGAL; tetap EARLY.")
# Shroomies / RigOrb: NOT in snapshot (reread-only); velocity notes live in run log only.
upd("AFROG", totalSupply=323, freeClaimed=323, freePctVerified=29.07,
    runNote1431="Run 1431: 315->323 (+8; <20) -> velocity GAGAL; free 323/1111 = 29,07% (>=25%) TAPI umur tetap UNVERIFIED (first mint 2026-11-05 05:58:10 WIB hanya batas atas launch) -> tetap watchlist-only, BUKAN promosi strong lead.")
upd("Saturnode", totalSupply=1729, freeClaimed=1706,
    runNote1431="Run 1431: 1715->1729 (+14; <20) -> velocity GAGAL; free 1706/4000 = 42,65%; umur tetap UNVERIFIED -> tetap EARLY.")
for k,sup,free in [("Swarmcentaur",777,772),("Agentyyds",600,595),("Pilotneon",500,495),("Mummyhive",600,582)]:
    if k in C:
        C[k].update({"totalSupply":sup,"freeClaimed":free,"lastReadBlock":BLK,"lastReadWib":RUN,
                     "runNote1431":f"Run 1431: totalSupply {sup}, freeClaimed {free} flat (5 mint terakhir berbayar untuk 3 yang mencapai cap); free pool tersisa 5 (Swarmcentaur/Agentyyds/Pilotneon) / 18 (Mummyhive) — BUKAN sold out; tanpa perubahan tier."})
upd("StarAgent-7d39", totalSupply=975,
    runNote1431="Run 1431: totalSupply 970->975 (+5); claimedFree(user)=0; tetap EARLY.")

# --- Early leads (probe block 131777711) ---
def upd_early(name, supply, free, pct, prev, rate, note):
    if name not in C: print("MISS", name); return
    C[name].update({"totalSupply": supply, "freeClaimed": free, "freePctVerified": pct,
                    "previousTotalSupply": prev, "mintedInInterval": supply-prev if isinstance(supply,int) and isinstance(prev,int) else None,
                    "intervalMinutes": 30.0, "currentRatePerMin": rate,
                    "lastReadBlock": PBLK, "lastReadWib": RUN})
    C[name]["runNote1431"]=note
upd_early("Thronemind", 431, 431, 21.55, 388, 1.43,
 "Run 1431: 388->431 (+43; ~1,43/mnt vs 2,57 run 1401 = 0,56x) -> velocity GAGAL; free 431/2000 = 21,55% <25% -> tetap EARLY; slot terbuka (claimedFree(user)=0, canFreeMint=1).")
upd_early("Hashseers", 436, 436, 21.8, 387, 1.63,
 "Run 1431: 387->436 (+49; ~1,63/mnt vs 2,97 run 1401 = 0,55x) -> velocity GAGAL; free 436/2000 = 21,8% <25% -> tetap EARLY; slot terbuka.")
upd_early("Layerloom", 414, 414, 20.7, 359, 1.83,
 "Run 1431: 359->414 (+55; ~1,83/mnt vs 2,77 run 1401 = 0,66x) -> velocity GAGAL; free 414/2000 = 20,7% <25% -> tetap EARLY; slot terbuka.")
upd_early("Cachejack", 290, 290, 14.5, 221, 2.3,
 "Run 1431: 221->290 (+69; ~2,3/mnt vs 2,8 run 1401 = 0,82x) -> velocity GAGAL (kaki velocity yang lolos run 1401 kini gagal); free 290/2000 = 14,5% <25% -> tetap EARLY; slot terbuka.")
upd_early("AgentMiner", 499, None, None, 397, 3.4,
 "Run 1431: totalSupply 397->499 (+102; ~3,4/mnt vs 4,6 run 1401 = 0,74x) -> velocity GAGAL. Free % tetap UNVERIFIED (free views revert; ABI: freeFor/freeLeft/freeUsed, tanpa counter free-cap). Tetap EARLY.")
upd_early("Smeltbots", 405, 405, 20.25, 329, 2.53,
 "Run 1431: 329->405 (+76; ~2,53/mnt, re-read ke-2); free 405/2000 = 20,25% <25% -> tetap EARLY; slot terbuka.")
upd_early("Tumblebots", 393, 394, 19.65, 309, 2.8,
 "Run 1431: 309->393 (+84; ~2,8/mnt, re-read ke-2; freeMinted 394 vs totalSupply 393 = selisih 1 antar-panggilan); free 393/2000 = 19,65% <25% -> tetap EARLY; slot terbuka.")
upd_early("Neurolucha", 335, 335, 41.88, 335, 0.0,
 "Run 1431: 335 flat (free 335/800 = 41,88%) — strong lead gate-blocked, tanpa perubahan; TIDAK di-preview/di-mint.")
upd_early("Roguefall", 190, 190, 9.5, 188, 0.067,
 "Run 1431: 188->190 (+2); free 190/2000 = 9,5% -> tetap EARLY; slot terbuka.")
upd_early("Agent Goats", 109, 109, 9.81, 108, 0.033,
 "Run 1431: 108->109 (+1; freeClaimed() no-arg 109/1111 = 9,81%) -> tetap EARLY; slot terbuka (mintedBy(user)=0).")
upd_early("Agent Owls", 105, 105, 9.45, 100, 0.167,
 "Run 1431: totalSupply 100->105 (+5; freeClaimed() no-arg 105/1111 = 9,45%) -> tetap EARLY; slot terbuka (mintedBy(user)=0).")
upd_early("Hirelings-A", 116, 116, 5.8, 115, 0.033,
 "Run 1431: 115->116 (+1); free 116/2000 = 5,8% -> tetap EARLY; slot terbuka.")
upd_early("Hirelings-B", 86, 86, 4.3, 85, 0.033,
 "Run 1431: 85->86 (+1); free 86/2000 = 4,3% -> tetap EARLY; slot terbuka.")
upd_early("Forklings", 126, 126, 6.3, 125, 0.033,
 "Run 1431: 125->126 (+1); free 126/2000 = 6,3% -> tetap EARLY; slot terbuka.")
upd_early("Auspibots", 131, 131, 6.55, 129, 0.067,
 "Run 1431: 129->131 (+2); free 131/2000 = 6,55% -> tetap EARLY; slot terbuka.")
# PACT / MEOW / WAGA re-read (early-probe file)
if "Pacture" in C:
    C["Pacture"].update({"lastReadBlock": PBLK, "lastReadWib": RUN,
        "runNote1431": "Run 1431: sharesMinted 10439->10489, freeMinted 7700 flat, paidShares 2739->2789; freeClaimed(user)=1."})
else:
    print("MISS Pacture (PACT re-read hanya di run log)")

# --- Track C notes ---
TC=s.get("track_c",{})
def tcn(key, note):
    if key in TC: TC[key]["runNote1431"]=note
    else: print("TC MISS", key)
tcn("OSK","Run 1431: opened 0, totalMinted 2275->2277 (+2) — tidak berubah (belum dibuka).")
tcn("NIULAI","Run 1431: launched 0, phase 4 — tidak berubah (arti enum phase 4 MASIH belum terverifikasi).")
tcn("KillZero-K0-sale","Run 1431: launched 0 — tidak berubah.")
tcn("DROID","Run 1431: opened 0, freeMinted 557, totalMinted 557 flat — tidak berubah.")
tcn("IMARS","Run 1431: opened 1, freeMinted 300, totalMinted 624 flat — pool gratis tetap habis, bukan lead.")
tcn("ASOC-43cE","Run 1431: freeClaimed(user) 0, saleEnded 0 — masih pre-open (jadwal buka 20:00 WIB), TIDAK di-preview/di-mint.")
tcn("SENBAZURU-b215","Run 1431: opened 1, freeClaimed 214->222 (+8 mint pihak lain), hasFreeShare(user)=1 (slot user terpakai, klaim hot-leg 13:39); paidSold tidak dibaca run ini (dipantau hot-leg).")
tcn("FABE","Run 1431: launched 0, freeSharesRemaining 2821, freeSharesClaimed(user)=1 — slot user sudah dipakai, tidak berubah.")
tcn("ShibAgent-R2","Run 1431: freeClaimed 123->125, phase 1, balanceOf(user)=0 — tanpa perubahan tier.")
tcn("QAGENT-2","Run 1431: freeMinted 6666 flat, sharesMinted 6702 — free pool habis, tidak berubah.")

# --- Agent Panda AGE-EXCLUSION ---
panda=C.pop("bridge-0x7561c414")
s.setdefault("excluded",{})["Agent Panda"]={
 "address": panda.get("address"), "symbol": "PANDA", "track": "A",
 "status": "excluded-age-over-48h-2026-11-05",
 "note": "Age-excluded run 1431: first mint TERVERIFIKASI 2026-11-03T03:05:04+07:00 (binary-search Ankr getLogs: blok pertama Transfer-from-zero 131301829). Pada run 1431 umur ~60 jam >48 jam dan BELUM sold out (totalMinted 5408/10000, blok 131778225). Website TERBUKTI ADA (agentpandabnb.xyz mencetak kontrak persis + tombol Mint; X @agentpandaonbnb di post Boltbook luoy.ai) dan slot user TERBUKA (freeRemainingFor(user)=2, freeMintedBy(user)=0), TAPI % free TIDAK terverifikasi (tanpa counter free total) dan umur menggugurkan -> dihapus dari watchlist aktif per aturan 48 jam; status lama watchlist-only-scan-bridge-2026-11-03. Dilaporkan sekali sebagai perubahan (age-exclusion) ke parent run 1431; tidak di-preview/di-mint.",
 "previous_status": "watchlist-only-scan-bridge-2026-11-03",
 "firstMintWib": "2026-11-03T03:05:04+07:00",
 "firstMintBlock": 131301829,
 "lastReading": "totalMinted 5408/10000, FREE_PER_WALLET_AGENT 2, freeRemainingFor(user)=2 (run 1431 blok 131778225)",
 "website": "https://agentpandabnb.xyz",
}
print("Agent Panda moved to excluded.")

# --- Batch age-exclusion (49) ---
cands=json.load(open(f"{BASE}/run-2026-11-05-1431-age-candidates.json"))
r1=json.load(open(f"{BASE}/run-2026-11-05-1431-age-reads.json"))
r2=json.load(open(f"{BASE}/run-2026-11-05-1431-age-reads2.json"))
reads={}
for k,v in r1.items():
    if k not in ("block","note"): reads[k]=v
for k,v in r2.items():
    if k not in ("block",): reads[k]=v
def rd(d, fn):
    v=d.get(fn)
    return v if isinstance(v,int) else ("revert" if isinstance(v,dict) else v)
removed=[]
for name, meta in cands.items():
    if name not in C:
        print("AGE MISS (not in contracts):", name); continue
    old=C.pop(name)
    d=reads.get(name, {})
    sup=rd(d,"totalSupply()"); tm=rd(d,"totalMinted()")
    free=rd(d,"freeClaimed()")
    if free is None or free=="revert": free=rd(d,"freeMinted()")
    cap=rd(d,"FREE_SUPPLY()")
    if cap is None or cap=="revert": cap=rd(d,"FREE_CAP()")
    mx=rd(d,"MAX_SUPPLY()")
    supply_txt=str(sup if sup is not None else tm)
    s.setdefault("excluded",{})[name]={
        "address": old.get("address"), "symbol": old.get("symbol"), "track": "A",
        "status": "excluded-age-over-48h-2026-11-05",
        "note": f"Age-excluded run 1431 (batch): first mint TERVERIFIKASI {meta['firstMintWib']} (sumber: {meta['src']}, launchNote snapshot). Umur {meta['age_h']} jam >48 jam pada run 1431 (~15:00 WIB) dan BELUM sold out (bacaan segar run 1431 blok {r2.get('block')}: totalSupply/totalMinted {supply_txt}, free {free}/{cap}, MAX_SUPPLY {mx}). Dihapus dari watchlist aktif per aturan 48 jam; status lama {meta['status']}. Dilaporkan sekali sebagai perubahan (batch age-exclusion) ke parent run 1431; tidak di-preview/di-mint.",
        "previous_status": meta["status"],
        "firstMintWib": meta["firstMintWib"],
        "lastReading": f"totalSupply/totalMinted {supply_txt}, free {free}/{cap}, MAX_SUPPLY {mx} (run 1431)",
    }
    removed.append(name)
print("Batch age-excluded:", len(removed))
print("Removed:", ", ".join(removed))

# --- Scan state + seen updates ---
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st.update({
 "last_scanned_block": 131778153,
 "last_scan_window_from": 131776154,
 "last_scan_window_to": 131778153,
 "last_scan_wib": "2026-11-05 run 1431",
 "ankr_calls": 80,
 "errors": [],
 "nft_contracts": 359,
 "erc20_mint_contracts": 659,
 "skipped_gap": "131773337-131776153 (2817 blok, window dari watermark 131773336 ke head 131777438 = 4102 blok > cap 2000; scan menutup 2000 blok terbaru 131776154-131778153)",
 "note": "Scan run 1431 SELESAI (80 panggilan Ankr, 0 error, ~14 menit); watermark maju ke 131778153. First-seen sejati 2 (keduanya bukan agent-shaped). Gap 131773337-131776153 dilewati karena cap 2000 - kontrak first-seen di gap itu tidak tercakup scan run ini. Laju blok BSC ~0,75 dtk/blok membuat jendela 30 menit ~2400 blok > cap 2000 setiap run.",
})
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
for a, blk, note in [
 ("0xb04276491f1e5791a72d14705c28f75235c75d47", 131776602, "WSA - RigOrb Collection; Sourcify unverified, registry bytes TIDAK ada, tanpa selector free -> checked-not-agent-shaped run 1431"),
 ("0xaa57998f3f7e7cdeba6c60f0ab4726325b0801ef", 131776490, "BNBlock; Sourcify unverified, registry bytes ADA tapi selector bytecode hanya mint(uint256)+FREE_SUPPLY() (tanpa freeMinted/freeClaimed/quote/canFreeMint) -> checked-not-agent-shaped run 1431"),
]:
    seen["contracts"][a]={"first_seen_block": blk, "first_seen_run": "2026-11-05-1431", "note": note}
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json","w"), indent=1)
print("Scan state + seen updated; seen contracts now:", len(seen["contracts"]))

# --- Run notes ---
s["runNote1431"]="Run 1431 (2026-11-05 14:31 WIB): 0 kandidat/strong-lead/early-lead/track-C baru. AGE-EXCLUDED: Agent Panda (first mint 2026-11-03 03:05:04 WIB, umur ~60 jam, totalMinted 5408/10000) + batch 49 item gelombang 2026-11-02/03 (first mint terverifikasi >48 jam, belum sold out, bacaan segar run 1431) -> dipindah ke excluded; item minted-by-user + promotion-discarded dipertahankan (preseden run 1401). Sourcify baru: Mirage Terminal (MIRT) — penjualan spot BERBAYAR (PRICE 0,0003 BNB), tanpa free view, bukan lead. Scan: 359 NFT + 659 ERC-20, 80 panggilan Ankr, 0 error; 2 first-seen, keduanya bukan agent-shaped. 5c: 40 shape-check, 0 lolos S1/S2; 17 sisa jendela dibuang (sampling limit). Shroomies + RigOrb velocity LULUS tapi % pool UNVERIFIED -> tetap watchlist (bukan snapshot). Bridge identik (113 kontrak). Track-B: BINANCEAI tetap refund/failed, tidak ada pending claim."
s["runNote1431_scan"]="Scan run 1431: jendela 131776154-131778153 (2000 blok, cap), head awal 131777438, watermark lama 131773336; gap 131773337-131776153 (2817 blok) dilewati. 80 panggilan Ankr, 0 error, ~14 menit. 359 NFT + 659 ERC-20. First-seen sejati 2 (WSA-RigOrb Collection, BNBlock), keduanya bukan agent-shaped."
s["runNote1431_age_exclusions"]="Run 1431 AGE-EXCLUSIONS (50 item, dilaporkan sekali sebagai perubahan): Agent Panda (first mint 2026-11-03 03:05:04 WIB, totalMinted 5408/10000) + batch 49: Slimelings, Voltabyte, Saturnin, Ghostbloom, Junepup, Vorpry, Kitsunaru, Nightsable, Nimaluo, Agents NormiePunks, Medusine, Mummyrelic, Ravenhex, Orbitmarshal, Orbitty, Neonwolfy, Sphinxel, Onimaru, Rootlinks, PIXEL FROGS, Orchard Agent, Critter Agent, Krakenbo, Glacier Agent, Agent Chronicles, Agentical Glyphs, Lynxeon, Thornscare, Magmaroth, Pumpkito, Saturnyx, Yydspanda, Nexobyte, Lumigeisha, Stitchvolt, Dragonito, Citadel Agent, Falls Agent, Mirage Agent, Deco Agent, Animora, Golemar, Homunqul, Praxion (free pool 750/750 habis), Eidolyn, Deepvane, Neuroveil, Noesyn, Synaptik — semuanya first mint terverifikasi >48 jam (52,7-87,4 jam) dan belum sold out per bacaan segar run 1431 -> DIHAPUS dari kontrak aktif, dipindah ke excluded (status excluded-age-over-48h-2026-11-05). DIPERTAHANKAN: semua item minted-by-user (riwayat tx) dan promotion-discarded-same-owner (penanda discard; preseden Vesperfang run 1401). Pyrevane (first mint 2026-11-02 15:23:25 WIB) belum 48 jam sampai ~15:23 WIB hari ini -> dipertahankan run ini."
s["last_run"]="2026-11-05 run 1431"
s["last_run_wib"]="2026-11-05 run 1431"
s["last_run_note"]=s["runNote1431"]
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("bookkeeping done; contracts now:", len(s["contracts"]), "excluded now:", len(s.get("excluded",{})))
