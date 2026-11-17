#!/usr/bin/env python3
"""Run 1631 bookkeeping: apply lean re-read + age-sweep to snapshot.
- Backup snapshot.
- Update route-1 values (nulls never overwrite old values). Interval vs run 1601
  read block 131792170 (16:23:36 WIB): 4856 blocks ~= 36.8 min at ~2.2 blk/s.
- Age-exclude 20 items (firstMintWib verified first-mint >48h, fresh reads at
  block 131798333 confirm NOT sold out). NIANNIAN HELD: all supply reads failed
  4x (3 attempts x 4 RPCs) - no evidence to exclude, stays in snapshot.
  False positives kept: Neonnodefox, Pepe420, Pixel Trump, Plutofarm,
  Chiphiveowl, Nbgent, ACOS, Zach Xbt, 4 bridge items (launch UNVERIFIED -
  verifiedAt/first-seen, not first mint). Precedent runs 1431/1501.
- Razor Agent (track C): excluded - free pool exhausted (freeSharesGiven
  3333/3333) + age >48h (genesisStart 2026-10-31 18:54:09 WIB).
- Track-C re-read notes.
Does NOT touch scan state/seen files (subagent A owns those).
"""
import json, shutil, copy
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot-1631.bak.json")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
C = snap["contracts"]
R = json.load(open(f"{BASE}/run-2026-11-05-1631-reread-lean.json"))["reread"]
TC = json.load(open(f"{BASE}/run-2026-11-05-1631-reread-lean.json"))["track_c"]
AGE = json.load(open(f"{BASE}/run-2026-11-05-1631-age-reads.json"))["reads"]
AGE_BLK = json.load(open(f"{BASE}/run-2026-11-05-1631-age-reads.json"))["block"]

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
    e["lastReadBlock"] = 131797026
    e["lastReadWib"] = "2026-11-05 run 1631"
    e["runNote1631"] = note
    if status:
        e["status"] = status

# --- Route 1 re-read notes (blok 131797026, ~17:00 WIB; interval ~36.8 mnt vs run 1601) ---
upd("HIVE Agents", "Run 1631 (blok 131797026): semua view gagal baca (null) - BUKAN nol; nilai lama (1242) dipertahankan, velocity TIDAK dihitung; minted-by-user, bukan kandidat.")
upd("Tigora-E8c4", "Run 1631: 586->611 (+25, ~0,68/mnt) -> velocity GAGAL (rate sebelumnya tidak ada).")
upd("BNBRunnerz-2674", "Run 1631: 3222->3260 (+38, ~1,03/mnt) -> velocity GAGAL (rate sebelumnya tidak ada).")
upd("Shroomies-2AE7", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (984) dipertahankan.")
upd("Blobbies-a7fB", "Run 1631: 1435->1438 (+3, <20) -> velocity GAGAL.")
upd("Jolly", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama dipertahankan.")
upd("HACKED", "Run 1631: 3372->3438 (+66, ~1,79/mnt) -> velocity GAGAL (rate sebelumnya tidak ada); minted-by-user, slot terpakai, bukan kandidat.")
upd("SoulAgent", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (688) dipertahankan.")
upd("PERSONA-A930", "Run 1631: 1121 flat vs 1601 (1121) -> velocity GAGAL.")
upd("RigOrb-539e", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (1055) dipertahankan.")
upd("Swarmcentaur", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (777) dipertahankan.")
upd("Agentyyds", "Run 1631: 600 flat vs 1601 (600) -> velocity GAGAL.")
upd("Pilotneon", "Run 1631: 500/495 flat vs 1601 -> velocity GAGAL.")
upd("Mummyhive", "Run 1631: 600/582 flat vs 1601 -> velocity GAGAL.")
upd("Saturnode", "Run 1631: 1770->1777 (+7, <20) -> velocity GAGAL.")
upd("Thronemind", "Run 1631: 523->535 (+12, <20) -> velocity GAGAL; freeMinted gagal baca run ini; tetap strong-lead-gate-blocked, tanpa perubahan.")
upd("Hashseers", "Run 1631: 494->524 (+30, ~0,82/mnt), free 524/2000 = 26,2%; tetap strong-lead-gate-blocked, tanpa perubahan.")
upd("Smeltbots", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (515) dipertahankan; tetap strong-lead-gate-blocked.")
upd("Roguefall", "Run 1631: 200->209 (+9, <20) -> velocity GAGAL; tetap EARLY.")
upd("Agent Goats", "Run 1631: 114->116 (+2), free 116/1111 = 10,4% -> velocity GAGAL; tetap EARLY.")
upd("Agent Owls", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (109) dipertahankan; tetap EARLY.")
upd("Hirelings-A", "Run 1631: 121->123 (+2), free 123/2000 = 6,2% -> velocity GAGAL; tetap EARLY.")
upd("Hirelings-B", "Run 1631: 92->93 (+1), free 93/2000 = 4,7% -> velocity GAGAL; tetap EARLY.")
upd("Forklings", "Run 1631: 209->434 (+225 vs baseline 1601 yang basi - interval rate TIDAK dihitung bersih karena baseline 1601 gagal baca; freeClaimed 435/2000 = 21,8% < 25% ambang strong lead) -> tetap EARLY, BUKAN promosi. Slot terbuka (freeMinted naik).")
upd("Auspibots", "Run 1631: 137->139 (+2), free 139/2000 = 7,0% -> velocity GAGAL; tetap EARLY.")
upd("Neurolucha", "Run 1631: 351->355 (+4), free 355/800 = 44,4% -> velocity GAGAL; tetap strong-lead-gate-blocked, tanpa perubahan.")
upd("Agent Frogs", "Run 1631: 337->338 (+1), free 338/1111 = 30,4% -> velocity GAGAL; tetap strong-lead-gate-blocked, tanpa perubahan.")
upd("PassAgentX", "Run 1631: 3213->3289 (+76, ~2,07/mnt), freeMinted 3101; FREE_SUPPLY/FREE_CAP null -> free % tetap UNVERIFIED -> tetap EARLY, BUKAN promosi.")
upd("Bathybots", "Run 1631: 59->214 (+155 vs baseline lama yang basi - interval rate TIDAK dihitung bersih; free 214/2000 = 10,7% < 25%) -> tetap EARLY, BUKAN promosi.")
upd("Pulsekeep", "Run 1631: totalSupply gagal baca; freeMinted 500 (recheck konsisten dgn 495 run 1601); umur tetap UNVERIFIED -> tetap EARLY, bukan promosi.")
upd("Tensortug", "Run 1631: totalSupply gagal baca; freeMinted 178; nilai lama dipertahankan.")
upd("DYOR-8695", "Run 1631: 11111 flat = SOLD OUT 11.111/11.111; user sudah mint #10092.")
upd("PixelLaptop-273f", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (564) dipertahankan.")
upd("AgentLattice-5b9e", "Run 1631: 262->263 (+1), free 257/1295 = 19,8% -> velocity GAGAL; tetap EARLY.")
upd("Lucky Charm Atlas II-5812", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama dipertahankan.")
upd("MoonCat", "Run 1631: 555->663 (+108, ~2,93/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); free % UNVERIFIED (tanpa FREE_SUPPLY) -> tetap watchlist-only-boltbook-noted.")
upd("PCAT-9b9e", "Run 1631: totalSupply gagal baca; freeMinted 2449; nilai lama dipertahankan.")
upd("KOAI-6dFE", "Run 1631: 7288->7292 (+4, <20) -> velocity GAGAL; tetap watchlist-only-boltbook.")
upd("LIMITLESS-c7aa", "Run 1631: 3988->4151 (+163, ~4,43/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tanpa free view -> tetap watchlist-only-boltbookfun.")
upd("SEAT-f11e", "Run 1631: 654->726 (+72, ~1,96/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tetap watchlist-only-boltbookfun.")
upd("Cogito-COG-A", "Run 1631: 4675->4893 (+218, ~5,92/mnt; rate sebelumnya tidak ada -> velocity TIDAK dihitung); tanpa free view -> tetap watchlist-only-boltbookfun.")
upd("LIKHIN", "Run 1631: totalSupply/totalMinted gagal baca run ini (nilai lama 1927 dipertahankan); tetap watchlist-only-boltbookfun.")
upd("StarAgent-7d39", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (988) dipertahankan; tetap early-lead-reported-run2131.")
upd("WAGagent", "Run 1631: semua view gagal baca (null); totalSupply skala ERC-20 diabaikan; tetap track-c-lead-gate-blocked-reported-by-hot-leg-1304.")
upd("PACTURE", "Run 1631: semua view gagal baca (null); totalSupply skala ERC-20 diabaikan; tetap watchlist-only-pelengkap-scan.")
upd("DinoEra", "Run 1631: totalSupply gagal baca (null); freeMinted 4 (tetap, 4/6000 = 0,07%); balanceOf(user)=0; tetap early-lead-reported-run1601, tanpa perubahan.")
upd("WHALE", "Run 1631: semua view gagal baca (null) - BUKAN nol; nilai lama (3181) dipertahankan; tetap watchlist-only-2026-11-05 (free-ness/free % UNVERIFIED).")
# LuckyBox is NOT in the snapshot (hot-leg reported it 16:15 WIB as track-C lead gate-blocked);
# add to track_c so the main job tracks it and never re-reports it.
snap.setdefault("track_c", {})["LuckyBox-LUCK"] = {
 "sale": "0xd08ef372B52C29255fEd7004f59bF41571451894",
 "symbol": "LUCK",
 "track": "C",
 "status": "track-c-lead-gate-blocked-reported-by-hot-leg-2026-11-05",
 "note": "Track-C lead gate-blocked, dilaporkan hot-leg 16:15 WIB run 1601 (BUKAN oleh run ini). Sale-shape S1: mint + quote + free views + REGISTRY()=registry (dikonfirmasi 3/3 on-chain run 1601). contractURI: 'Lucky Box NFT for Binance .ai Agent ID holders. Max supply 5,000. First mint free per wallet, then 0.005 BNB, max 10 per wallet.' First mint blok 131788987 = 15:59:44 WIB. Run 1631 re-read: totalSupply gagal baca (null); mintedBy(user)=0, freeUsed(user)=0 (slot tampak terbuka); quote gagal baca; hot-leg 1644: totalSupply 296, freeLeft(user)=1, quote(user,1)=0, mintOpen=1. Gate website GAGAL (tidak ada website terverifikasi) -> TIDAK di-preview/di-mint. Ditambahkan ke track_c run 1631 agar tidak dilaporkan ulang.",
 "runNote1631": "Run 1631: ditambahkan ke track_c (sebelumnya hanya di hot-leg-reported); totalSupply gagal baca; mintedBy(user)=0, freeUsed(user)=0; tetap gate-blocked, tanpa perubahan.",
}

# --- Track-C re-read notes (blok 131797026) ---
TCN = {
 "OSK": "Run 1631: opened=0 (tetap belum buka); totalMinted gagal baca; tanpa perubahan.",
 "NIULAI": "Run 1631: phase=4, launched=0 (tetap belum launch); tanpa perubahan.",
 "KillZero-K0-sale": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "DROID": "Run 1631: opened=0, totalMinted=561; freeMinted gagal baca; tanpa perubahan tier.",
 "IMARS": "Run 1631: opened=1, freeMinted 300/300 (pool habis), totalMinted gagal baca; tanpa perubahan.",
 "ASOC-43cE": "Run 1631: saleEnded=0, masih BELUM BUKA - buka 20:00 WIB 2026-11-05; tanpa perubahan.",
 "SENBAZURU-b215": "Run 1631: phase=1, launched=0, hasFreeShare(user)=1 (share gratis user sudah diklaim); tanpa perubahan.",
 "FABE": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "QAGENT-2": "Run 1631: sharesMinted 6702, freeClaimed(user)=1 (slot terpakai); tanpa perubahan.",
 "ShibAgent-R2": "Run 1631: phase=1, launched=0; tanpa perubahan.",
 "DeY": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "BoxBigem-3Ee9": "Run 1631: freeMinted skala ERC-20 (diabaikan); tanpa perubahan.",
 "FANBEIMAO-824d": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "Ikigai-Ihigi": "Run 1631: freeMinted 267 (was 215), phase=1; tanpa perubahan tier.",
 "Hongbao-HONGBAO": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "Nvagent-NVGT-28Fe": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "Soarm-SOARM": "Run 1631: semua view gagal baca; nilai lama dipertahankan.",
 "SAFUAI": "Run 1631: opened=1; tanpa perubahan.",
}
for key, note in TCN.items():
    e = snap.get("track_c", {}).get(key)
    if e is None:
        print("TC MISS", key); continue
    r = TC.get(key, {})
    for f in ("opened", "launched", "freeMinted", "totalMinted", "sharesMinted", "saleEnded", "phase"):
        v = clean(r.get(f))
        if v is not None:
            e[f] = v
    if clean(r.get("hasFreeShare_user")) is not None:
        e["hasFreeShare_user"] = clean(r.get("hasFreeShare_user"))
    if clean(r.get("freeClaimed_user")) is not None:
        e["freeClaimed_user"] = clean(r.get("freeClaimed_user"))
    e["runNote1631"] = note

# --- Razor Agent: excluded in track_c (free pool exhausted + age >48h) ---
snap.setdefault("track_c", {})["Razor-RZAG"] = {
 "sale": "0x10E80B0365A3b5e3DD66f55E05A748D0BB031fA1",
 "token": "0xD5c03f871A34a01373d68ee38f6e67AC195cd66B",
 "symbol": "RZAG",
 "track": "C",
 "status": "excluded-free-exhausted-age-over-48h-2026-11-05",
 "site": "https://razoragent.fun",
 "x": "https://x.com/Razor_Agent (disebut situs, belum diverifikasi browser)",
 "note": "Ditemukan route 3 run 1631 (situs razoragent.fun; params.json). Sourcify exact_match (verifiedAt 2026-10-31T00:36:43Z, BUKAN launch). ABI asli 130 fungsi dibaca parent: mint(uint256,address,uint256) + quote + FREE_SHARE_CAP + freeSharesGiven + freeUsed(uint256) + registrar()=registry 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F (agent-shaped OK). TAPI free pool HABIS: freeSharesGiven()=3333 = FREE_SHARE_CAP()=3333 (dikonfirmasi 2x); totalMinted 10422; DAN umur >48h: genesisStart()=1793447649 = 2026-10-31 18:54:09 WIB (~118 jam). Slot user belum terpakai (freeUsed(agentId)=0, quotaOf=10, mintedCount=0) tapi pool habis -> BUKAN lead, BUKAN kandidat. Token belum deploy (eth_getCode 0); pair() 0x61fb6dd9... tercatat tapi token belum ada. Deadline 2026-11-10 18:54:09 WIB. TIDAK dilaporkan sebagai lead; TIDAK di-preview/di-mint.",
}

# --- Age exclusions: 20 items -> excluded ---
from datetime import datetime, timezone, timedelta
AGE_OVERRIDES = {"Chromagent": {"totalSupply": 1116, "freeClaimed": 1112}}
excluded_now = []
for k, c in json.load(open(f"{BASE}/run-2026-11-05-1631-age-candidates.json")).items():
    if k == "NIANNIAN":
        continue  # HELD: reads failed, no evidence
    e = C.get(k)
    if e is None:
        print("AGE MISS", k); continue
    r = AGE.get(k, {})
    ov = AGE_OVERRIDES.get(k, {})
    ts = ov.get("totalSupply", clean(r.get("totalSupply")) if clean(r.get("totalSupply")) is not None else clean(r.get("totalMinted")))
    fc = ov.get("freeClaimed", clean(r.get("freeClaimed")) if clean(r.get("freeClaimed")) is not None else clean(r.get("freeMinted")))
    cap = clean(r.get("FREE_SUPPLY")) or clean(r.get("FREE_CAP")) or e.get("FREE_SUPPLY") or e.get("FREE_CAP")
    mx = clean(r.get("MAX_SUPPLY")) or e.get("MAX_SUPPLY")
    fm = e.get("firstMintWib")
    # age hours
    try:
        fmdt = datetime.strptime(fm.replace(" WIB", "").replace("T", " ")[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone(timedelta(hours=7)))
        age_h = round((datetime(2026, 11, 5, 17, 30, tzinfo=timezone(timedelta(hours=7))) - fmdt).total_seconds() / 3600, 1)
    except Exception:
        age_h = None
    ent = copy.deepcopy(e)
    ent["status"] = "excluded-age-over-48h-2026-11-05"
    ent["ageExclusionNote1631"] = (
        f"Age-excluded run 1631: first mint TERVERIFIKASI {fm} (umur ~{age_h} jam > 48 jam); "
        f"bacaan segar blok {AGE_BLK} (~17:30 WIB): totalSupply={ts}, free={fc}/{cap}, MAX_SUPPLY={mx} -> BELUM sold out; "
        f"balanceOf(user)={clean(r.get('balanceOf_user'))}. Dipindah dari contracts ke excluded. "
        f"Alasan selector lama terlewat: launchNote kosong (run 1431/1501 hanya membaca launchNote, bukan field firstMintWib)."
    )
    snap.setdefault("excluded", {})[k] = ent
    del C[k]
    excluded_now.append(k)

# --- NIANNIAN hold note ---
if "NIANNIAN" in C:
    C["NIANNIAN"]["runNote1631"] = ("Run 1631: SEMUA view supply gagal baca 4x (3 percobaan x 4 RPC) - BUKAN nol; "
        "balanceOf(user)=1 (mungkin sudah dimiliki user - belum disimpulkan). firstMintWib 2026-11-03 13:09:25 WIB (~52 jam) "
        "tapi tanpa bacaan segar supply/free, TIDAK di-age-exclude run ini (fail-closed); tetap di snapshot menunggu bacaan berhasil.")

snap["runNote1631"] = (
    "Run 1631 (blok re-read 131797026, age-reads blok 131798333): 0 kandidat baru, 0 strong lead baru, 0 early lead baru, "
    "0 track-B claim dibuka/diklaim/diblokir, 0 lead/kandidat track-C baru. "
    f"Age-excluded 20 item (batch firstMintWib, terlewat selector launchNote run 1431/1501): {', '.join(excluded_now)}. "
    "NIANNIAN ditahan (bacaan gagal 4x). Razor Agent (RZAG) excluded track-C: free pool habis 3333/3333 + umur ~118 jam. "
    "Forklings 434 (21,8%) + Bathybots 214 (10,7%) tetap early (<25%). Semua strong-lead gate-blocked tanpa perubahan. "
    "Bridge identik run 1531/1601 (113 kontrak, 7 same_owner_discarded). pending_claims kosong."
)
snap["last_run_wib"] = "2026-11-05 run 1631"
snap["last_run"] = "1631"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(snap["contracts"]), "| excluded now:", len(snap.get("excluded", {})))
print("excluded this run:", excluded_now)
