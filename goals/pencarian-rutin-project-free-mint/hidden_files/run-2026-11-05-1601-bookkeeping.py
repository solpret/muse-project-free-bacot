#!/usr/bin/env python3
"""Run 1601 bookkeeping: apply lean re-read + promotion verifications to snapshot.
- Backup snapshot.
- Update route-1 values (nulls never overwrite old values).
- Promote Smeltbots / Thronemind / Hashseers / Agent Frogs to strong-lead-gate-blocked-2026-11-05.
- DYOR-8695 -> sold-out (totalSupply 11111/11111, Boltbook tale.ai post).
- Add WHALE NFT as watchlist-only-2026-11-05 (age verified, free-ness/free % unverified).
- Track-C re-read notes.
Does NOT touch scan state/seen files (subagent A owns those)."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1601.bak.json")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap["contracts"]
R = json.load(open(f"{BASE}/run-2026-11-05-1601-reread-lean.json"))["reread"]
TC = json.load(open(f"{BASE}/run-2026-11-05-1601-reread-lean.json"))["track_c"]
V = json.load(open(f"{BASE}/run-2026-11-05-1601-verify-promotions.json"))
V2 = json.load(open(f"{BASE}/run-2026-11-05-1601-verify2.json"))

def clean(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else None

def upd(name, note, status=None):
    e = C.get(name)
    if e is None:
        print("MISS", name); return
    r = R.get(name, {})
    ts, tm = clean(r.get("totalSupply")), clean(r.get("totalMinted"))
    fc, fm = clean(r.get("freeClaimed")), clean(r.get("freeMinted"))
    if ts is not None:
        e["previousTotalSupply"] = e.get("totalSupply"); e["totalSupply"] = ts
    if tm is not None:
        e["totalMinted"] = tm
    if fc is not None:
        e["freeClaimed"] = fc
    if fm is not None:
        e["freeMinted"] = fm
    e["lastReadBlock"] = 131792170
    e["lastReadWib"] = "2026-11-05 run 1601"
    e["runNote1601"] = note
    if status:
        e["status"] = status

# --- Route 1 re-read notes (blok 131792170, ts 2026-11-05 16:23:36 WIB; interval vs run 1531 blok 131786455 = 42,87 mnt) ---
upd("HIVE Agents", "Run 1601 (blok 131792170): 1242 flat vs 1531 (1242) -> velocity GAGAL; balanceOf(user) gagal baca run ini (nilai lama 1 dipertahankan); minted-by-user, bukan kandidat.")
upd("Tigora-E8c4", "Run 1601: totalMinted 607->609 (+2, <20) -> velocity GAGAL.")
upd("BNBRunnerz-2674", "Run 1601: semua view gagal baca (null) - BUKAN nol; nilai lama (3222) dipertahankan, velocity TIDAK dihitung.")
upd("Shroomies-2AE7", "Run 1601: 975->984 (+9, <20) -> velocity GAGAL; slot views gagal baca run ini; free % tetap UNVERIFIED -> watchlist-only.")
upd("Blobbies-a7fB", "Run 1601: 1426->1435 (+9, <20) -> velocity GAGAL.")
upd("Jolly", "Run 1601: freeMinted 3386->3388 (+2) -> velocity GAGAL; umur ~44 jam (first mint 2026-11-03 23:27:33 WIB) <=48 jam -> tetap gate-blocked, tanpa laporan perubahan.")
upd("HACKED", "Run 1601: semua supply view gagal baca (null) - BUKAN nol; balanceOf(user)=2; nilai lama (3372) dipertahankan.")
upd("SoulAgent", "Run 1601: 679->688 (+9, <20) -> velocity GAGAL.")
upd("PERSONA-A930", "Run 1601: 1121 flat vs 1531 (1121) -> velocity GAGAL.")
upd("RigOrb-539e", "Run 1601: 972->1055 (+83, ~1,94/mnt vs 2,67/mnt run 1531 = 0,73x) -> velocity GAGAL; % pool tetap UNVERIFIED -> watchlist-only.")
upd("Swarmcentaur", "Run 1601: semua view gagal baca (null) - BUKAN nol; nilai lama (777/772) dipertahankan.")
upd("Agentyyds", "Run 1601: 600 flat vs 1531 (600) -> velocity GAGAL.")
upd("Pilotneon", "Run 1601: 500/495 flat vs 1531 -> velocity GAGAL.")
upd("Mummyhive", "Run 1601: 600/582 flat vs 1531 -> velocity GAGAL.")
upd("Saturnode", "Run 1601: 1760->1770 (+10, <20) -> velocity GAGAL; free 1746?/4000 (freeClaimed gagal baca; nilai lama 1737 dipertahankan, 43,4%), umur tetap UNVERIFIED -> tetap EARLY.")
upd("Thronemind", "Run 1601: 496->523 (+27, ~0,63/mnt vs 1,13/mnt run 1531 = 0,56x) -> velocity GAGAL. PROMOSI run ini (lihat promotionNote1601).")
upd("Hashseers", "Run 1601 lean: semua view gagal baca; verify run ini: totalSupply 516, freeMinted 516/2000 = 25,8%. PROMOSI run ini (lihat promotionNote1601).")
upd("Smeltbots", "Run 1601: 495->515 (+20, ~0,47/mnt vs 1,13/mnt run 1531 = 0,41x) -> velocity GAGAL. PROMOSI run ini (lihat promotionNote1601).")
upd("Roguefall", "Run 1601: 197->200 (+3, <20) -> velocity GAGAL; tetap EARLY.")
upd("Agent Goats", "Run 1601: semua view gagal baca (null); nilai lama (114) dipertahankan.")
upd("Agent Owls", "Run 1601: freeClaimed 109->114 (+5) -> velocity GAGAL; tetap EARLY.")
upd("Hirelings-A", "Run 1601: freeMinted 121->122 (+1) -> velocity GAGAL; tetap EARLY.")
upd("Hirelings-B", "Run 1601: 92 flat vs 1531 (92) -> velocity GAGAL; tetap EARLY.")
upd("Forklings", "Run 1601: semua view gagal baca (null); nilai lama (209) dipertahankan; tetap EARLY.")
upd("Auspibots", "Run 1601: semua view gagal baca (null); nilai lama (137) dipertahankan; tetap EARLY.")
upd("Neurolucha", "Run 1601: freeMinted 351->353 (+2) -> velocity GAGAL; canFreeMint=1, claimedFree=0; tetap strong-lead-gate-blocked, tanpa perubahan.")
upd("Agent Frogs", "Run 1601: 294->337 (+43, ~1,0/mnt; rate sebelumnya belum ada -> velocity TIDAK dihitung, baseline baru disimpan); freeClaimed 337/1111 = 30,4%. PROMOSI run ini (lihat promotionNote1601).")
upd("PassAgentX", "Run 1601: totalSupply 2080->3213 (+1133, ~26,4/mnt - lonjakan panas), freeMinted 1976->3033; MAX_SUPPLY 6666, mintStart on-chain 2026-11-05 06:49:58 WIB (umur ~9,7 jam, TERVERIFIKASI <=48 jam), REGISTRY()=registry; TAPI free % UNVERIFIED (tanpa FREE_CAP/FREE_SUPPLY view - % total bukan % free) dan slot belum lengkap (canFreeMint/claimedFree/quote gagal baca; mintedBy(user)=0, mintOpen=1) -> BUKAN promosi strong lead, tetap EARLY; velocity belum bisa dihitung (rate sebelumnya tidak ada).")
upd("Bathybots", "Run 1601: semua view gagal baca (null); nilai lama (59) dipertahankan; tetap EARLY.")
upd("Pulsekeep", "Run 1601: freeMinted 129->495 (+366; totalSupply recheck 495 konsisten) - lonjakan besar; umur tetap UNVERIFIED -> tetap EARLY, bukan promosi; velocity belum bisa dihitung.")
upd("Tensortug", "Run 1601: semua view gagal baca (null); nilai lama (58) dipertahankan; tetap EARLY.")
upd("DYOR-8695", "Run 1601: totalSupply 11111 (recheck 2x konsisten; snapshot lama 730 sudah basi) = SOLD OUT 11.111/11.111 (Boltbook tale.ai, blok 131.789.971); user sudah mint #10092. Bukan kandidat.", status="sold-out-2026-11-05")
upd("PixelLaptop-273f", "Run 1601: semua view gagal baca (null); nilai lama (564) dipertahankan; tetap EARLY.")
upd("AgentLattice-5b9e", "Run 1601: semua view gagal baca (null); nilai lama dipertahankan; tetap EARLY.")
upd("Lucky Charm Atlas II-5812", "Run 1601: semua view gagal baca (null); nilai lama dipertahankan; tetap EARLY.")
upd("MoonCat", "Run 1601: totalMinted 555->661 (+106, ~2,47/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbook-noted.")
upd("PCAT-9b9e", "Run 1601: 2384->2440 (+56, ~1,31/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbook.")
upd("KOAI-6dFE", "Run 1601: 7249->7288 (+39, ~0,91/mnt) -> velocity GAGAL (<20? tidak - +39 >= 20 token tapi ratio vs rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbook.")
upd("LIMITLESS-c7aa", "Run 1601: semua view gagal baca (null); nilai lama (3988) dipertahankan.")
upd("SEAT-f11e", "Run 1601: 626->654 (+28, ~0,65/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbookfun.")
upd("Cogito-COG-A", "Run 1601: semua view gagal baca (null); nilai lama (4675) dipertahankan.")
upd("LIKHIN", "Run 1601: totalMinted 1871->1927 (+56, ~1,31/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbookfun.")
upd("StarAgent-7d39", "Run 1601: semua view gagal baca (null); nilai lama (988) dipertahankan; Boltbook run ini: mintFree() satu-satunya free lane, gate Agent ID revert utk non-agent; tetap early-lead-reported-run2131.")
upd("WAGagent", "Run 1601: totalSupply skala ERC-20 (1e28) - bukan bentuk NFT, diabaikan; totalMints 95 (hot-leg 1614); tetap track-c-lead-gate-blocked-reported-by-hot-leg-1304.")
upd("PACTURE", "Run 1601: totalSupply skala ERC-20 (1,03e29) - bukan bentuk NFT, diabaikan; tetap watchlist-only-pelengkap-scan.")

# --- Promotions: 4 strong leads, gate FAILED (methods A-N), reported once, NOT previewed/minted ---
GATE = ("Gate website GAGAL run 1601 (metode A-N): (A) pencarian alamat mentah - nihil; (B) Boltbook EN+ZH run ini - tidak ada post yang menamai proyek ini; "
        "(C) Sourcify exact_match/match, record tanpa URL; (D) pola same-family - nihil; (E) grup owner tercatat, bukan pengecualian gate; "
        "(F) tidak ada handle X ditemukan - tidak ada yang bisa dikonfirmasi via browser (X opsional, tidak meng-gate); (G) pencarian nama proyek - nihil; "
        "(H) contractURI() revert/null; (I) tokenURI(#1) deskripsi saja tanpa external_url / kosong; (J) ABI tanpa fungsi site/url/domain/website/external/link; "
        "(K) pencarian GitHub - nihil (limitasi: code search sejati butuh auth); (L) BscScan via browser - {L}; "
        "(M) site:vercel.app/pages.dev/deed.page/surge.sh - 0 hasil; pencarian alamat deployer - nihil; "
        "(N) tidak ada profil registry/author-bio hop. X tidak meng-gate; yang menggagalkan adalah tidak adanya website proyek terverifikasi. "
        "Gate gagal = scope block, bukan kegagalan keamanan kontrak. TIDAK di-preview, TIDAK di-mint.")
for name, legs in [
    ("Smeltbots", "PROMOSI run 1601: first mint TERVERIFIKASI 2026-11-05 13:10:38 WIB (blok 131766451, ~3,3 jam, <=48 jam); freeMinted 517/2000 FREE_CAP = 25,85% (>=25%); slot user TERBUKA (canFreeMint=1, claimedFree=0, balanceOf=0); REGISTRY()=registry Agent ID. Velocity GAGAL (0,47/mnt vs 1,13 = 0,41x) - bukan kandidat. Owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba (factory wave batch 06:23 UTC bersama Layerloom/Tumblebots/Cachejack/Hashseers/Thronemind)."),
    ("Thronemind", "PROMOSI run 1601: first mint TERVERIFIKASI 2026-11-05 12:40:04 WIB (blok 131762375, ts 1793857204, ~3,8 jam, <=48 jam); freeMinted 523/2000 FREE_CAP = 26,15% (>=25%); slot user TERBUKA (canFreeMint=1, claimedFree=0, balanceOf=0); REGISTRY()=registry (ABI 57 fungsi, ada REGISTRY). Velocity GAGAL (0,63/mnt vs 1,13 = 0,56x) - bukan kandidat. Owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba (factory wave yang sama)."),
    ("Hashseers", "PROMOSI run 1601: first mint TERVERIFIKASI blok 131762488 (~12:45 WIB, interpolasi dari anchor Thronemind blok 131762375 ts 1793857204 +113 blok; ts langsung gagal dibaca 3 RPC - dicatat sebagai interpolasi, bukan bacaan langsung; umur ~3,7 jam, <=48 jam); freeMinted 516/2000 FREE_CAP = 25,8% (>=25%); slot user TERBUKA (canFreeMint=1, claimedFree=0, balanceOf=0); REGISTRY()=registry (ABI 57 fungsi, ada REGISTRY). Velocity GAGAL (0,51/mnt vs 0,94 = 0,55x) - bukan kandidat. Owner 0x4e9b1d076fda3605ad63f81a94a8693342a08dba (factory wave yang sama)."),
    ("Agent Frogs", "PROMOSI run 1601: first mint TERVERIFIKASI 2026-11-05 05:58:10 WIB (blok 131708808, ts 1793833090, ~10,5 jam, <=48 jam); freeClaimed 338/1111 FREE_SUPPLY = 30,4% (>=25%); slot user TERBUKA (mintedBy(user)=0, balanceOf(user)=0, mintOpen=1; canFreeMint/claimedFree/quote tidak ada di ABI - fungsi tidak tersedia, bukan gagal baca); AGENT_ID()=registry (ABI 38 fungsi, ada AGENT_ID). Velocity belum bisa dihitung (rate sebelumnya tidak ada). Bukan kandidat (X unverified + velocity belum lolos). Owner 0x23f5cdd233925ea83369a495b95f825ed710fbaa (grup berbeda dari factory wave 0x4e9b)."),
]:
    e = C.get(name)
    e["promotionNote1601"] = legs
    e["gateNote1601"] = GATE
    e["status"] = "strong-lead-gate-blocked-2026-11-05"

# --- WHALE NFT: add as watchlist-only (first main-job read this run) ---
C["WHALE"] = {
    "address": "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0",
    "status": "watchlist-only-2026-11-05",
    "name": "WHALE",
    "kind": "ERC721",
    "totalSupply": 3181,
    "firstMintBlock": 131609522,
    "firstMintWib": "2026-11-04 17:33:19 WIB",
    "launchNote": "First mint terverifikasi on-chain via Ankr getLogs: blok 131609522 = 2026-11-04 17:33:19 WIB; umur ~23 jam saat run (<=48 jam).",
    "baselineNote": "Ditambahkan run 1601 sebagai watchlist-only: umur TERVERIFIKASI <=48 jam; free-ness DIPERDEBATKAN (dua author Boltbook berbeda pendapat; tidak ada price getter - mintPrice/PRICE/quote/costOf semua null; sim value-0 lolos tapi bukan bukti gratis); free % UNVERIFIED (tidak ada free view - freeMinted/freeClaimed/FREE_SUPPLY/FREE_CAP/MAX_SUPPLY semua null); AGENT_ID_REGISTRY ada di ABI (86 fungsi, tanpa fungsi site). BUKAN strong lead, BUKAN kandidat. Awas klon 0xf81b...3218 (1.150 mint, nama+symbol sama, alamat parsial).",
    "owner": "0x9e7cc3e1f21accb89e98c78778b0ece3b798ec9d",
    "paused": 0,
    "balanceOf_user": 0,
    "lastReadBlock": 131792170,
    "lastReadWib": "2026-11-05 run 1601",
    "xVerified": False,
    "velocityVerified": False,
    "supplyView": "totalSupply",
}

# --- Track-C re-read notes (blok 131792170) ---
TCN = {
 "OSK": "Run 1601: totalMinted 2277 flat; opened/launched gagal baca (fungsi tidak ada di ABI sale ini); tetap watchlist-only-not-open.",
 "NIULAI": "Run 1601: launched=0, phase=4 (tetap); tetap watchlist-only-not-open.",
 "KillZero-K0-sale": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap watchlist-only-not-open.",
 "DROID": "Run 1601: freeMinted 559->560 (+1); tetap watchlist-only-age-slot-unverified.",
 "IMARS": "Run 1601: opened=1, totalMinted 624 flat, freeMinted 300 flat (hot-leg 1614 sama); tetap watchlist-only-not-open.",
 "ASOC-43cE": "Run 1601: saleEnded=0 (belum buka; buka 20:00 WIB hari ini, startTime 1793883600); tetap watchlist-only-not-open-2026-11-05.",
 "SENBAZURU-b215": "Run 1601: opened=1, hasFreeShare(user)=1 (slot user sudah dipakai); freeClaimed 228->229 (hot-leg 1614); tetap claimed-by-user-hot-leg-2026-11-05.",
 "FABE": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap minted-by-user-2026-11-02.",
 "QAGENT-2": "Run 1601: freeClaimed(user)=1 (slot sudah dipakai); tetap minted-by-user-2026-11-02.",
 "ShibAgent-R2": "Run 1601: phase=1 (tetap); tetap track-c-lead-candidate-session-blocked-2026-11-05.",
 "DeY": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap track-c-lead-gate-blocked-run1731.",
 "BoxBigem-3Ee9": "Run 1601: freeMinted skala ERC-20 (7,76e26) - bukan bentuk sale NFT; tetap watchlist-only-age-unverified-run1731.",
 "FANBEIMAO-824d": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap track-c-lead-gate-blocked-run2101.",
 "Ikigai-Ihigi": "Run 1601: freeMinted 267, phase=1; tetap lead-reported-2026-11-02-gate-blocked-no-mint.",
 "Hongbao-HONGBAO": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap lead-gate-blocked-recorded-2026-11-03.",
 "Nvagent-NVGT-28Fe": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap lead-gate-blocked-recorded-2026-11-03.",
 "Soarm-SOARM": "Run 1601: semua view gagal baca/tidak ada di ABI; tetap lead-gate-blocked-recorded-2026-11-03.",
 "SAFUAI": "Run 1601: totalMinted 10000; tetap checked-not-a-lead-2026-11-03.",
}
tc = snap.get("track_c", {})
for k, note in TCN.items():
    if isinstance(tc.get(k), dict):
        tc[k]["runNote1601"] = note
    else:
        print("TC MISS", k)

snap["runNote1601"] = ("Run 1601 (2026-11-05 ~16:01-16:45 WIB): rute 1 re-read blok 131792170 (interval 42,87 mnt vs run 1531); "
    "4 PROMOSI strong-lead-gate-blocked (Smeltbots, Thronemind, Hashseers, Agent Frogs) - dilaporkan sekali, TIDAK di-preview/mint; "
    "DYOR sold out 11.111/11.111; WHALE ditambahkan watchlist-only (free unverified); RACKRUSH tetap BUKAN lead (bukan agent-shaped + website unverified; free cap 394/400, umur terverifikasi 07:30:36 WIB); "
    "PassAgentX + Pulsekeep lonjakan besar tapi free %/umur unverified - tetap EARLY; track-C tanpa perubahan (ASOC buka 20:00 WIB); "
    "bridge identik run 1531 (113 kontrak, 7 discarded); pending_claims kosong; re-read penuh pertama GAGAL timeout RPC (900 dtk) - diganti versi lean threaded (208 dtk); "
    "route 4/5c + gate (L) menyusul dari subagent A / browser task.")
snap["last_run_wib"] = "2026-11-05 run 1601"
snap["last_run_note"] = snap["runNote1601"]
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("SNAPSHOT UPDATED: contracts", len(snap["contracts"]), "track_c", len(snap.get("track_c", {})))
print("Promoted:", [k for k in ["Smeltbots", "Thronemind", "Hashseers", "Agent Frogs"] if C[k]["status"] == "strong-lead-gate-blocked-2026-11-05"])
