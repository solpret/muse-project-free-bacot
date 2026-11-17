#!/usr/bin/env python3
"""Run 2026-11-06 0601 WIB: apply re-read results to onchain-snapshot.json (surgical).
Rule: None = read failure, NEVER overwrites an old value. Backup first."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
shutil.copy(f"{BASE}/onchain-snapshot.json", f"{BASE}/onchain-snapshot.json.bak-20261106-0601")
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
lean = json.load(open(f"{BASE}/run-2026-11-06-0601-reread-lean.json"))

# NFT: map lean keys to snapshot fields
FIELDS = {"totalSupply": "totalSupply", "totalMinted": "totalMinted",
          "freeClaimed": "freeClaimed", "freeMinted": "freeMinted",
          "balanceOf_user": "balanceOf_user", "FREE_SUPPLY": "FREE_SUPPLY"}
for name, d in lean["reread"].items():
    e = snap["contracts"].setdefault(name, {"address": d.get("address")})
    for lk, sk in FIELDS.items():
        if d.get(lk) is not None:
            e[sk] = d[lk]
    e["lastReadBlock"] = lean.get("block")
    e["lastReadWib"] = "2026-11-06 run 0601"

snap["contracts"]["HIVE Agents"]["runNote0601"] = (
    "Run 0601: SEMUA supply view gagal baca (None) - degradasi RPC, BUKAN nol; "
    "nilai lama (1253) dipertahankan, velocity TIDAK dihitung. Minted-by-user; tetap dipantau.")
snap["contracts"]["KING Agent"]["runNote0601"] = (
    "Run 0601: totalMinted/remainingFree gagal baca (nilai lama 423 dipertahankan); "
    "costOf(user,1)=0, balanceOf(user)=0, agentGateOn=1, mintOpen=1 - slot user tetap TERBUKA. "
    "Free % tetap UNVERIFIED (inferensi 423/3333=12,7% <25% strong-lead leg); velocity TIDAK terhitung. "
    "Tetap EARLY, bukan promosi, TIDAK pernah di-preview/di-mint.")
snap["contracts"]["MILLION"]["runNote0601"] = (
    "Run 0601: SEMUA supply view gagal baca (None) - degradasi RPC, BUKAN nol; nilai lama "
    "(totalMinted 74) dipertahankan. Free pool + user slot tetap UNVERIFIED; velocity TIDAK terhitung. "
    "Tetap EARLY, bukan promosi, TIDAK pernah di-preview/di-mint.")
snap["contracts"]["StarAgent-7d39"]["runNote0601"] = "Run 0601: totalSupply 1105->1106 (+1, <20) velocity GAGAL. Tetap early, bukan promosi."
snap["contracts"]["LuckyBox-d08e"]["runNote0601"] = "Run 0601: totalSupply 619->621 (+2). Incremental only."
snap["contracts"]["SnailMail"]["runNote0601"] = "Run 0601: totalSupply 304->305 (+1). Incremental only."
snap["contracts"]["wheelz"]["runNote0601"] = "Run 0601: totalSupply 310->311 (+1). Incremental only."
snap["contracts"]["Layerloom"]["runNote0601"] = "Run 0601: totalSupply 660 flat. Velocity GAGAL."
snap["contracts"]["Tumblebots"]["runNote0601"] = "Run 0601: totalSupply 656 flat. Velocity GAGAL."
snap["contracts"]["Mossminds"]["runNote0601"] = (
    "Run 0601: freeMinted 885->890 (+5). Promotion-discarded-same-owner, never promote.")
snap["contracts"]["Jolly"]["runNote0601"] = "Run 0601: totalMinted/freeMinted 3643->3645 (+2). Incremental only."
snap["contracts"]["AgentGlyph"]["runNote0601"] = (
    "Run 0601: freeClaimed 512/512 FREE_SUPPLY, totalSupply 513 - free pool tetap habis (tidak ada perubahan vs catatan lama).")
snap["contracts"]["Pacture"]["runNote0601"] = (
    "Run 0601: freeMinted 7700 (bacaan pertama yang terbaca; FREE_SUPPLY belum tercatat - tidak bisa dinilai %).")
for n in ["Mummyhive", "Thronemind", "Hashseers", "Smeltbots", "Forklings", "Agent Frogs",
          "PassAgentX", "SEAT-f11e", "WAGagent"]:
    snap["contracts"][n]["runNote0601"] = (
        "Run 0601: semua supply view gagal baca (None) - degradasi RPC, BUKAN nol; "
        "nilai lama dipertahankan, velocity TIDAK dihitung. Tidak ada perubahan status.")

# Track C: record fresh non-null reads (no status change)
tc = snap.setdefault("track_c", {})
def tc_note(key, text):
    e = tc.setdefault(key, {})
    if isinstance(e, dict):
        e[f"note0601"] = text
tc_note("OSK", "Run 0601: opened 0, totalMinted 2259->2278 (+19) - tetap belum dibuka, watchlist-only.")
tc_note("DROID", "Run 0601: opened 0, freeMinted 584->587 (+3) - tetap belum dibuka, watchlist-only.")
tc_note("IMARS", "Run 0601: opened 0->1, freeMinted 300/300 FREE_SHARES (pool gratis HABIS), totalMinted 624 - "
                 "TERBUKA tapi pool gratis habis -> BUKAN lead, tetap watchlist-only.")
tc_note("QAGENT-2", "Run 0601: freeMinted 6666, sharesMinted 6702 - tidak berubah. Minted-by-user.")
tc_note("SAFUAI", "Run 0601: opened 1, totalMinted 10000 - checked-not-a-lead, tidak berubah.")
tc_note("SENBAZURU-b215", "Run 0601: opened 1, launched 0, phase 1 - claimed-by-user, tidak berubah.")
tc_note("ShibAgent-R2", "Run 0601: launched 0, phase 1 - tetap belum launched, candidate-session-blocked.")
tc_note("Ikigai-Ihigi", "Run 0601: freeMinted 273, phase 3 - age-excluded sebelumnya, tidak dilaporkan ulang.")
tc_note("ASOC-43cE", "Run 0601: freeClaimed(user)=0, saleEnded=0 - tidak berubah.")

# Excluded: CodexNFT (new web-sweep hit, fails gas-only + age)
ex = snap.setdefault("excluded", {})
ex["CodexNFT"] = {
    "address": "0xa7046Fc653556b8d50370Ab8dB189b2E447eacDb",
    "site": "http://codexnft.online/",
    "reason": "checked-not-a-candidate-run0601: mint 'free' tapi + creator fee 0.000075 BNB per NFT "
              "(bukan gas-only) + voucher-gated + umur >48h (deploy blok 130527362, ~27 Okt; "
              "last crawl 6 hari lalu). Tidak dilaporkan sebagai kandidat.",
    "status": "excluded-fee-and-age-2026-11-06",
}

snap["runNote0601"] = (
    "Run 0601 SILENT: tidak ada kandidat/strong lead/early lead/track-C baru, tidak ada pembukaan "
    "klaim, tidak ada sellout, tidak ada slot hilang, tidak ada age-exclusion. KING + MILLION tetap EARLY.")
snap["runNote0601_scan"] = (
    "Run 0601 SCAN GAGAL 2x: percobaan 1 fast-fail (eth_blockNumber via fast_rpc timeout di semua "
    "dataseed, SCAN_EXIT=1); percobaan 2 STALL (13 mnt, ~3 dtk CPU, 0 byte log, pola sama run 0431/0531) "
    "- ke-3 kalinya stall berturut-turut. Watermark TIDAK dimajukan (tetap 131895548); seen file TIDAK "
    "berubah; 5c dilewati. Window yang belum ter-scan: 131895549-131901831+ (gap ~4283 blok dilewati cap 2000).")
snap["runNote0601_age"] = (
    "Run 0601 AGE-CHECK (bukan exclusion): batch early-lead 2026-11-04 (Plutofarm, Chiphiveowl, "
    "Swarmdrake, Agentjiayou, Neonmind, Batbot, Seven Sins, Velmora NFT, Marsagentis, Chipdroidling, "
    "Swarmganbei, Nova Wraiths, Dragonmind, Saturndroid, Agentyyds, Pilotphoenix, Glitchdroid, "
    "Chipagent, Botsaturn) launchNote-nya UNVERIFIED dan first-seen block HANYA lower bound - "
    "timestamp blok first-seen (2026-11-04 00:11-04:28 WIB) BUKAN waktu launch terverifikasi, jadi "
    "TIDAK di-age-exclude run ini (aturan: launch UNVERIFIED = watchlist-only, jangan dibuang diam-diam). "
    "Sama untuk LUCKY KOI / Wild Duck / Quilt Agent / PIXEL BOYZ (launch UNVERIFIED). "
    "Verifikasi first-mint sesungguhnya (chunked getLogs) masih tertunda untuk batch ini.")
snap["last_run_wib"] = "2026-11-06 06:01 WIB"
snap["last_run_note"] = "SILENT (tidak ada kandidat/strong lead/early lead/track-C baru; scan gagal/stall ke-3x)"
json.dump(snap, open(f"{BASE}/onchain-snapshot.json", "w"), indent=1)
print("snapshot updated; contracts:", len(snap["contracts"]), "excluded:", len(snap["excluded"]))
