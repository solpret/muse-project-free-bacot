import json, shutil
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1531.bak.json")
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
C=snap["contracts"]
REREAD=json.load(open(f"{BASE}/run-2026-11-05-1531-reread.json"))
PROBE=json.load(open(f"{BASE}/run-2026-11-05-1531-early-probe.json"))
# Intervals from block timestamps (eth_getBlockByNumber, WIB):
# reread 131782166=15:08:34 -> 131786455=15:40:44 = 32.17 min
# probe  131782665=15:12:18 -> 131786806=15:43:22 = 31.07 min
# AGF/DRFT verify 131785472=15:33:22 -> reread 131786455=15:40:44 = 7.37 min
def clean(v):
    return v if isinstance(v,int) and not isinstance(v,bool) else None
def upd(name, ts=None, tm=None, fc=None, fm=None, note=None, status=None):
    e=C.get(name)
    if e is None:
        print("MISS", name); return
    if ts is not None:
        e["previousTotalSupply"]=e.get("totalSupply"); e["totalSupply"]=ts
    if tm is not None:
        e["totalMinted"]=tm
    if fc is not None:
        e["freeClaimed"]=fc
    if fm is not None:
        e["freeMinted"]=fm
    if note: e["runNote1531"]=note
    if status: e["status"]=status

# --- Rute 1 re-read (blok 131786455, interval 32.17 mnt vs run 1501 blok 131782166) ---
upd("HIVE Agents", ts=1242, note="Run 1531 (blok 131786455): 1242 flat vs 1501 (1242) -> velocity GAGAL; balanceOf(user)=1; minted-by-user, bukan kandidat.")
upd("Tigora", tm=607, note="Run 1531: totalMinted 603->607 (+4, <20) -> velocity GAGAL.")
upd("BNBRunnerz", ts=3222, tm=3222, note="Run 1531: 3207->3222 (+15, <20) -> velocity GAGAL.")
upd("Shroomies", ts=975, note="Run 1531: 957->975 (+18, <20) -> velocity GAGAL; costOf(user,1)=0, mintOpen=1, mintedBy(user)=0 (slot terbuka) tapi free % tetap UNVERIFIED -> watchlist-only.")
upd("Blobbies", ts=1426, note="Run 1531: 1417->1426 (+9, <20) -> velocity GAGAL.")
upd("Robogent", ts=1208, fc=1204, note="Run 1531: 1207->1208 (+1) -> velocity GAGAL; freeClaimed 1204.")
upd("Jolly", tm=3386, note="Run 1531: totalMinted 3382->3386 (+4, ~0,12/mnt vs 0,333 tersimpan = 0,37x) -> velocity GAGAL; umur ~40 jam (first mint 2026-11-03 23:27:33 WIB) <=48 jam -> tetap gate-blocked, tanpa laporan perubahan.")
upd("HACKED", ts=3372, note="Run 1531: 3340->3372 (+32, ~0,99/mnt vs 1,0 tersimpan = 0,99x <1,5x) -> velocity GAGAL; balanceOf(user)=2; minted-by-user.")
upd("SoulAgent", ts=679, tm=679, note="Run 1531: 672->679 (+7, <20) -> velocity GAGAL.")
upd("PERSONA", ts=1121, note="Run 1531: 1120->1121 (+1) -> velocity GAGAL.")
upd("RigOrb", ts=972, note="Run 1531: 886->972 (+86, ~2,67/mnt vs ~4,5/mnt run 1431 = 0,59x) -> velocity GAGAL; % pool tetap UNVERIFIED -> watchlist-only.")
upd("AFROG", ts=333, fc=333, note="Run 1531: 329->333 (+4) -> velocity GAGAL; free 333/1111 = 30,0% (>=25%) TAPI umur peluncuran tetap UNVERIFIED -> tetap watchlist-only, BUKAN promosi strong lead.")
upd("Swarmcentaur", ts=777, fc=772, note="Run 1531: totalSupply 777 = FREE_SUPPLY 777, freeClaimed 772 flat - free pool tersisa 5, BUKAN sold out; early lead, tanpa perubahan status.")
upd("Agentyyds", ts=600, fc=595, note="Run 1531: 600/600, freeClaimed 595 flat - free pool tersisa 5, BUKAN sold out.")
upd("Pilotneon", ts=500, fc=495, note="Run 1531: 500/500, freeClaimed 495 flat - free pool tersisa 5, BUKAN sold out.")
upd("Mummyhive", ts=600, fc=582, note="Run 1531: 600, freeClaimed 582 flat.")
upd("Saturnode", ts=1760, fc=1737, note="Run 1531: 1746->1760 (+14, <20) -> velocity GAGAL; free 1737/4000 = 43,4%, umur UNVERIFIED -> tetap EARLY.")
upd("MeowBark", note="Run 1531: totalSupply skala ERC-20 (491e24, dari 481e24 run 1501), freeClaimed/FREE_SUPPLY revert - bukan bentuk NFT, diabaikan.")
upd("SlimySlug", note="Run 1531: totalSupply 5790 (ERC-20 scale), freeClaimed/FREE_SUPPLY revert - bukan bentuk NFT, diabaikan.")
# Agent Coffee + Driftnauts (early lead baru run 1501; interval verify->reread 7.37 mnt)
upd("Agent Coffee", ts=391, note="Run 1531 (blok 131786455): totalSupply 326->391 (+65, ~8,8/mnt - laju panas) TAPI free % tetap UNVERIFIED (freeMinted/freeClaimed/FREE_CAP/FREE_SUPPLY semua revert); slot user TERBUKA (quote 0, freeLeft 1, freeUsed 0, mintedBy 0, balance 0); umur ~1h20m (first mint 14:51:30 WIB) <=48 jam; website/X UNVERIFIED -> tetap EARLY, BUKAN strong lead, TIDAK di-preview/di-mint.")
upd("Driftnauts", ts=369, fm=369, note="Run 1531: totalSupply 312->369 (+57, ~7,7/mnt); free 369/2640 = 13,98% (<25%); slot user TERBUKA (canFreeMint 1, claimedFree 0, balance 0); umur ~1h25m (first mint 14:48:12 WIB) <=48 jam; website/X UNVERIFIED -> tetap EARLY, BUKAN strong lead, TIDAK di-preview/di-mint.")
# Unbroken (watchlist-only, bacaan segar subagent rute 2, blok 131786713)
upd("Unbroken", ts=4183, note="Run 1531 (bacaan rute 2, blok 131786713): totalSupply 2809 (2026-11-03) -> 4183 (+1374); mintOpen=1, mintedBy(user)=0, balanceOf(user)=0, mintPrice(user,1)=0 (slot TERBUKA). Tetap watchlist-only: free % UNVERIFIED (tidak ada free counter; 4183/10000 = total %, bukan free %), umur launch UNVERIFIED, website UNVERIFIED (contractURI tanpa external_link; DappBay kategori AI tidak memuat Unbroken - ketiadaan membuktikan apa-apa). BUKAN strong lead, BUKAN kandidat.")

# --- Early-probe (blok 131786806, interval 31.07 mnt vs run 1501 blok 131782665) ---
upd("Thronemind", ts=496, fm=496, note="Run 1531 probe: 461->496 (+35); free 496/2000 = 24,8% (<25%) -> tetap EARLY.")
upd("Hashseers", ts=494, fm=494, note="Run 1531 probe: 465->494 (+29); free 494/2000 = 24,7% (<25%) -> tetap EARLY.")
upd("Cachejack", ts=371, fm=371, note="Run 1531 probe: 344->371 (+27); free 371/2000 = 18,55% (<25%) -> tetap EARLY.")
upd("AgentMiner", ts=593, note="Run 1531 probe: 558->593 (+35); free % UNVERIFIED (freeMinted/paidMinted/canFreeMint/claimedFree semua revert; mintedBy(user)=0) -> tetap EARLY.")
upd("Smeltbots", ts=495, fm=495, note="Run 1531 probe: 460->495 (+35); free 495/2000 = 24,75% (<25%) -> tetap EARLY.")
upd("Neurolucha", ts=351, fm=351, note="Run 1531 probe: 347->351 (+4); free 351/800 = 43,9% - sudah strong-lead-gate-blocked-2026-11-05, tanpa perubahan status.")
upd("Roguefall", ts=197, fm=197, note="Run 1531 probe: 196->197 (+1); free 197/2000 = 9,85% -> tetap EARLY.")
upd("Agent Goats", ts=114, fc=114, note="Run 1531 probe: 111->114 (+3); freeClaimed 114/1111 = 10,26% -> tetap EARLY.")
upd("Agent Owls", ts=109, fc=109, note="Run 1531 probe: 107->109 (+2); freeClaimed 109/1111 = 9,81% -> tetap EARLY.")
upd("Hirelings-A", ts=121, fm=121, note="Run 1531 probe: 119->121 (+2); free 121/2000 = 6,05% -> tetap EARLY.")
upd("Hirelings-B", ts=92, fm=92, note="Run 1531 probe: 90->92 (+2); free 92/2000 = 4,6% -> tetap EARLY.")
upd("Forklings", ts=209, fm=209, note="Run 1531 probe: 130->209 (+79, ~2,5/mnt); free 209/2000 = 10,45% (<25%) -> tetap EARLY.")
upd("Auspibots", ts=137, fm=137, note="Run 1531 probe: 134->137 (+3); free 137/2000 = 6,85% -> tetap EARLY.")
# STAR / PACT / MEOW / WAGA (probe set, log-only; STAR di snapshot)
upd("StarAgent", ts=988, note="Run 1531 probe: totalSupply 985->988, claimedFree(user)=0.")
# PACT/MEOW/WAGA tidak ada key kontrak di snapshot (dicatat di run log saja):
# PACT sharesMinted 10520->10499 (-21), paidShares 2820->2797 (-23), freeMinted 7700 flat, freeClaimed(user)=1
#   -> PENURUNAN counter vs run 1501, dicatat sebagai anomali (kemungkinan RPC stale atau mekanisme kontrak); tanpa perubahan tier.
# MEOW totalSupply 481e24->491e24 (skala ERC-20, diabaikan). WAGA totalMints 92->95, quote(user,1)=0, mintOpen=1, freeLeft(user)=1 -> tetap gate-blocked.

# --- PROMOSI: Layerloom + Tumblebots -> strong-lead-gate-blocked ---
GATE1531=("Gate website GAGAL run 1531 (metode A-N, dicek penuh karena naik tier): "
 "(A) pencarian alamat kontrak mentah - nihil (hanya hasil tak terkait); "
 "(B) Boltbook front EN+ZH + post receipt-bearing run ini - tidak ada post yang menamai proyek ini dengan link; "
 "(C) Sourcify exact_match, metadata tanpa URL apa pun; "
 "(D) pola situs same-family - tidak ada situs ditemukan; "
 "(E) owner() 0x4e9b1d076fda3605ad63f81a94a8693342a08dba - grup deployer sama (factory wave 6 batch 06:23 UTC: Cachejack/Layerloom/Tumblebots/Smeltbots/Thronemind/Hashseers), dicatat sebagai grup, BUKAN pengecualian gate; "
 "(F) tidak ada handle X ditemukan di tempat lain - tidak ada yang bisa dikonfirmasi via browser (X opsional, tidak meng-gate); "
 "(G) pencarian nama proyek - nihil (hanya panduan umum/proyek lain); "
 "(H) contractURI() revert (tidak ada di ABI); "
 "(I) tokenURI(#1) base64 JSON deskripsi saja, tanpa external_url/URL; "
 "(J) ABI 46/44 fungsi, tanpa fungsi site/url/domain/website/external/link; "
 "(K) pencarian GitHub by alamat + nama - nihil (limitasi: search-index absence bukan bukti tidak ada repo, code search butuh auth); "
 "(L) BscScan token-info via browser - Tumblebots: halaman termuat, Other Info HANYA Token Contract, tanpa Website/sosial; Layerloom: halaman TERBLOKIR Cloudflare (Ray ID a55a9dfc4cf45907, ~155 dtk + 2 reload gagal) - bacaan terblokir BUKAN bukti ketiadaan, tapi juga bukan bukti website; "
 "(M) site:vercel.app/pages.dev/deed.page/surge.sh - 0 hasil; "
 "(N) tidak ada profil registry/author-bio hop yang ditemukan (tidak ada post Boltbook yang menamai proyek ini run ini). "
 "X UNVERIFIED (tidak ada akun X proyek ditemukan; opsional, tidak meng-gate).")
upd("Layerloom", ts=513, fm=513, status="strong-lead-gate-blocked-2026-11-05",
    note="Run 1531 probe: 477->513 (+36); free 513/2000 = 25,65% (>=25%). PROMOSI ke strong lead run ini: (a) umur TERVERIFIKASI <=48 jam (first mint 2026-11-05 12:42:56 WIB, ~3h), (b) free >=25% terverifikasi, (c) slot user TERBUKA (canFreeMint 1, claimedFree 0, balance 0). TIDAK di-preview/TIDAK di-mint karena gate website GAGAL (lihat gateNote1531). Dilaporkan sekali sebagai STRONG LEAD GATE-BLOCKED.")
upd("Tumblebots", ts=506, fm=506, status="strong-lead-gate-blocked-2026-11-05",
    note="Run 1531 probe: 465->506 (+41); free 506/2000 = 25,3% (>=25%). PROMOSI ke strong lead run ini: (a) umur TERVERIFIKASI <=48 jam (first mint 2026-11-05 13:10:49 WIB, ~3h), (b) free >=25% terverifikasi, (c) slot user TERBUKA (canFreeMint 1, claimedFree 0, balance 0). TIDAK di-preview/TIDAK di-mint karena gate website GAGAL (lihat gateNote1531). Dilaporkan sekali sebagai STRONG LEAD GATE-BLOCKED.")
C["Layerloom"]["gateNote1531"]=GATE1531
C["Tumblebots"]["gateNote1531"]=GATE1531
C["Layerloom"]["promotionNote1531"]="PROMOTED early->strong-lead-gate-blocked run 1531 (25,65%, umur terverifikasi, slot terbuka; gate website GAGAL - dilaporkan sekali, TIDAK di-mint)."
C["Tumblebots"]["promotionNote1531"]="PROMOTED early->strong-lead-gate-blocked run 1531 (25,3%, umur terverifikasi, slot terbuka; gate website GAGAL - dilaporkan sekali, TIDAK di-mint)."
C["Layerloom"]["owner"]="0x4e9b1d076fda3605ad63f81a94a8693342a08dba"
C["Tumblebots"]["owner"]="0x4e9b1d076fda3605ad63f81a94a8693342a08dba"

snap["runNote1531"]=("Run 1531 (2026-11-05 ~15:31-16:20 WIB): DILAPORKAN SEKALI: 2 promosi strong lead GATE-BLOCKED "
 "(Layerloom 513/2000=25,65% + Tumblebots 506/2000=25,3%; umur terverifikasi <=48 jam, slot user terbuka; gate website GAGAL metode A-N - TIDAK di-preview/di-mint). "
 "Tidak ada kandidat baru, tidak ada early lead baru, tidak ada track-B claim dibuka/diklaim/diblokir, tidak ada track-C lead/kandidat baru. "
 "Scan rute 4 SUKSES (jendela 131784571-131786570, 2000 blok cap, gap 131782181-131784570 dilewati; 80 panggilan Ankr, 0 error; 289 NFT + 612 ERC-20). "
 "First-seen sejati 4, TIDAK ADA early lead baru: HashDoge + Parking Rush Cars diklaim agent-shaped oleh scan (registry-bytes hit) TAPI verifikasi mendalam parent: Sourcify unverified, eth_getCode TIDAK mengandung bytes registry, tanpa fungsi REGISTRY/AGENT_REGISTRY/AGENT_ID, tanpa free shape (semua free view revert) -> BUKAN agent-shaped (preseden run 1431: registry-bytes saja tanpa free shape = checked-not-agent-shaped); dicatat log-only di scan-seen, TIDAK masuk snapshot sebagai lead. "
 "2 bukan agent-shaped (白银, 财来 NFT) log-only. Rute 5c: 73 ERC-20 mint_count>=10 (68 sudah terperiksa + 5 baru), 0 lolos S1/S2. "
 "Emberforge BUKAN temuan baru (koreksi atas rute 2): sudah age-excluded + dihapus run 0431 (first mint 2026-11-02 21:38 WIB); post Boltbook hari ini hanya kelanjutan mint fase 3 (1222/1980), Fase 4 belum dibuka -> TIDAK dilaporkan ulang, TIDAK ditambahkan kembali. "
 "Unbroken 2809->4183, slot terbuka, tetap watchlist-only. ASOC upcoming buka 20:00 WIB hari ini (alamat lengkap 0x43cEef9313CB8c4ca3757bA841C44DF40A223205, saleEnded 0, freeClaimed(user) 0) - sudah dilacak, bukan lead. "
 "AgentPet $PET claim terbuka (claimOpen=1) tapi entitlement user UNVERIFIED (kontrak NFT tidak tercetak di post) -> bukan klaim user. Razor Agent upcoming (kontrak belum deployed). AGENT404 klaim berjalan, entitlement user tidak diketahui. "
 "Age-sweep: 0 exclusion baru (hanya 2 false positive lama Neonnodefox + Pepe420 - timestamp Sourcify, bukan first mint). Bridge identik run 1501 (113 kontrak, 7 same_owner_discarded, tanpa promosi). "
 "0 transaksi. Tidak ada preview/mint/approve/swap.")
snap["runNote1531_scan"]=("Scan run 1531: jendela 131784571-131786570 (2000 blok, cap), head 131786570, watermark lama 131782180; "
 "gap 131782181-131784570 (2390 blok) dilewati karena cap. 80 panggilan Ankr, 0 error, ~14 menit (15:41-15:55 WIB). 289 NFT + 612 ERC-20. "
 "First-seen sejati 4 (2x registry-bytes-only: HashDoge HDOGE 57 mint/30 minter, Parking Rush Cars PRCAR 2 mint; 2 bukan agent-shaped: 白银, 财来 NFT). "
 "Verifikasi mendalam parent membatalkan keduanya sebagai early lead (lihat runNote1531). "
 "Rute 5c: 73 ERC-20 mint_count>=10, 5 baru di-shape-check, 0 lolos S1/S2; total terperiksa kumulatif 1840. "
 "Catatan: head maju ~2,2 blok/detik (BSC sub-detik) - watermark akan tertinggal ~4000 blok per run 30 menit bila cap tetap 2000; gap berulang tiap run.")
snap["last_run"]="2026-11-05 run 1531"
snap["last_run_wib"]="2026-11-05 run 1531"
snap["last_run_note"]=snap["runNote1531"]
json.dump(snap, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("OK snapshot:", len(snap["contracts"]), "contracts;", len(snap.get("excluded",{})), "excluded")
print("Layerloom:", C["Layerloom"]["status"], C["Layerloom"]["totalSupply"], C["Layerloom"]["freeMinted"])
print("Tumblebots:", C["Tumblebots"]["status"], C["Tumblebots"]["totalSupply"], C["Tumblebots"]["freeMinted"])
