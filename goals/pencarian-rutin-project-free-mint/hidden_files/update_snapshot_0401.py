import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
# --- seen file ---
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
new_seen={
 "0xf2a6d1a5da92d611cf8ec614548d4d6e83beb6d8":131887159,
 "0xf6972e6263aa411f4e5c4e8d25edbae6ddf68b52":131887628,
 "0x74d09dca3326afae7d078e29f004e2ecf53c740f":131888329,
}
for k,v in new_seen.items(): seen["contracts"][k]=v
seen["_meta"]["last_scan_wib"]="2026-11-06 run 0401"
seen["_meta"]["last_scan_window"]="131886995-131888994"
seen["_meta"]["last_scan_added"]=3
seen["_meta"]["note_0401"]=("Run 0401: 3 true first-seen appended (HATCHIEggy, Titan Wolf Agent, Storm Nomad Agent). "
 "HATCHIEggy: no registry hit, no free views, Sourcify not_verified -> NOT agent-shaped, log only. "
 "Titan Wolf Agent + Storm Nomad Agent: AGENT_REGISTRY()=registry exact BUT no free view/constant + totalSupply 3333=MAX_SUPPLY -> log only "
 "(precedent Ethereal Zebra / Void Rat / Cyber Scribe run 0331). Same minter 0xe9d9dec3... for both 1-mint contracts. NO new early lead this run.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json","w"), indent=1)
# --- scan state ---
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st.update({
 "last_scanned_block":131888994,
 "last_scan_window_from":131886995,
 "last_scan_window_to":131888994,
 "last_scan_wib":"2026-11-06 run 0401",
 "ankr_calls":80, "errors":[],
 "nft_contracts":192, "erc20_mint_contracts":378,
 "skipped_gap":"131884354-131886994 (2641 blok; window dari watermark 131884353 ke head 131888994 = 4641 blok > cap 2000; scan menutup 2000 blok terbaru 131886995-131888994)",
 "note":("Scan run 0401 SUKSES (80 panggilan Ankr, 0 error, ~18 mnt - Ankr lambat; proses 0,5% CPU, I/O-wait). "
 "3 first-seen sejati, 0 early lead baru. Gap kumulatif sejak run 1831 ~61.600 blok tak ter-scan."),
 "last_scan_window":"131886995-131888994",
})
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
# --- snapshot ---
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-06-0401-reread-lean.json"))
def upd(name, **kw):
    e=s["contracts"].setdefault(name,{})
    for k,v in kw.items():
        if v is not None: e[k]=v
    return e
upd("HIVE Agents", totalSupply=1253, balanceOf_user=1)
s["contracts"]["HIVE Agents"]["lastReadWib"]="2026-11-06 run 0401"
s["contracts"]["HIVE Agents"]["lastReadBlock"]=131888994
s["contracts"]["HIVE Agents"]["run0401_velocity"]="FAIL: 1253 flat vs run 0331 (1253) -> velocity 0. Minted-by-user; tetap dipantau."
s["contracts"]["HIVE Agents"]["previousTotalSupply"]=1253
s["contracts"]["HIVE Agents"]["mintedInInterval"]=0
s["contracts"]["HIVE Agents"]["currentRatePerMin"]=0.0
upd("Mummyhive", totalSupply=600, freeClaimed=582, balanceOf_user=0)
upd("Thronemind", totalSupply=650, freeMinted=650, balanceOf_user=0, canFreeMint_user=1, claimedFree_user=0)
upd("Hashseers", totalSupply=590, balanceOf_user=0, canFreeMint_user=1, claimedFree_user=0)
upd("Smeltbots", freeMinted=606, canFreeMint_user=1)
upd("Forklings", freeMinted=912)
upd("Agent Frogs", freeClaimed=410, mintedBy_user=0)
upd("PassAgentX", totalSupply=3889, balanceOf_user=0, mintedBy_user=0)
upd("SEAT-f11e", totalSupply=2576)
upd("LuckyBox-d08e", totalSupply=613, balanceOf_user=0, quote_user_1=0)
upd("SnailMail", totalSupply=302, mintsLeft_user=10, mintedBy_user=0, price=200000000000000)
upd("wheelz", totalSupply=308, balanceOf_user=0, costOf_user_1=0, mintsLeft_user=10, mintOpen=1, mintedBy_user=0)
upd("Layerloom", totalSupply=656, freeMinted=656, balanceOf_user=0)
upd("Tumblebots", freeMinted=650, balanceOf_user=0)
upd("Mossminds", freeMinted=874, canFreeMint_user=1, balanceOf_user=0)
upd("Jolly", totalMinted=3636, balanceOf_user=0)
# MILLION: all views None this run (RPC read failure, NOT zero) - keep old values
s["contracts"].setdefault("MILLION",{})["run0401_note"]=(
 "Run 0401: SEMUA view gagal baca (totalSupply/totalMinted/freeMinted/freeClaimed/agentRegistry/FREE_SUPPLY/balanceOf = None) - "
 "degradasi RPC, BUKAN nol; nilai lama dipertahankan (totalMinted 14 saat triage 0331). Tidak ada promosi: free pool, user slot, website, X "
 "tetap UNVERIFIED; velocity baseline sudah tersimpan run 0331. Tetap early-lead-reported-2026-11-06-run0331, TIDAK pernah di-preview/di-mint.")
s["contracts"]["SEAT-f11e"]["run0401_velocity"]=("FAIL: 2555->2576 (+21, ~0.42/mnt dlm ~50 mnt) vs prev 0.71 = 0.59x -> velocity GAGAL. % gratis + website UNVERIFIED -> tetap watchlist-only.")
s["contracts"]["SEAT-f11e"]["previousTotalSupply"]=2555
s["contracts"]["SEAT-f11e"]["mintedInInterval"]=21
s["contracts"]["SEAT-f11e"]["currentRatePerMin"]=0.42
s["contracts"]["Mossminds"]["run0401_velocity"]=("FAIL: freeMinted 865->874 (+9, ~0.18/mnt) <20 token -> velocity GAGAL. Status TETAP promotion-discarded-same-owner-2026-11-05: TIDAK dipromosikan, TIDAK dilaporkan, TIDAK di-preview/di-mint.")
s["contracts"]["Mossminds"]["previousTotalSupply"]=865
s["contracts"]["Mossminds"]["mintedInInterval"]=9
s["contracts"]["Mossminds"]["currentRatePerMin"]=0.18
s["contracts"]["Mossminds"]["velocityLegPasses"]=False
# track_c value updates (None never overwrites - only set non-None reads)
t=s.setdefault("track_c",{})
if "DROID" in t:
    t["DROID"]["freeMinted"]=584; t["DROID"]["totalMinted"]=584
    t["DROID"]["run0401"]="freeMinted/totalMinted 584, opened=0; status watchlist-only-age-slot-unverified tidak berubah."
if "IMARS" in t:
    t["IMARS"]["freeMinted"]=300; t["IMARS"]["totalMinted"]=624
    t["IMARS"]["run0401"]="opened=1, freeMinted 300/300 FREE_SHARES (pool gratis habis), totalMinted 624 - tetap watchlist-only-not-open."
if "OSK" in t:
    t["OSK"]["totalMinted"]=2278
    t["OSK"]["run0401"]="opened=0, totalMinted 2278 - tetap watchlist-only-not-open."
if "NIULAI" in t:
    t["NIULAI"]["phase"]=4
    t["NIULAI"]["run0401"]="launched=0, phase=4 - tetap watchlist-only-not-open."
if "SENBAZURU-b215" in t:
    t["SENBAZURU-b215"]["hasFreeShare_user"]=1
    t["SENBAZURU-b215"]["run0401"]="opened=1, hasFreeShare(user)=1 (sudah diklaim user); tidak berubah."
if "QAGENT-2" in t:
    t["QAGENT-2"]["freeClaimed_user"]=1
    t["QAGENT-2"]["run0401"]="freeClaimed(user)=1 (sudah diklaim); tidak berubah."
if "SAFUAI" in t:
    t["SAFUAI"]["opened"]=1
    t["SAFUAI"]["run0401"]="opened=1 (recovered read); status checked-not-a-lead tidak berubah."
# --- age-exclusions: remove from track_c, tombstone in excluded ---
ex=s.setdefault("excluded",{})
soarm=t.pop("Soarm-SOARM", None)
ex["Soarm-SOARM"]={
 "sale":"0x7ba14e1119d31E876Cc4aa52a0bcB9E43C841799",
 "token":"0x4a02e3824b301a1bf6a8230e56b44b526174ca97",
 "track":"C",
 "status":"excluded-age-over-48h-2026-11-06",
 "note":("Run 0401: first mint terverifikasi 2026-11-03 07:47:23 WIB (first Minted event, Ankr getLogs) -> umur ~69 jam > 48 jam -> AGE-EXCLUDED, "
 "dihapus dari track_c. Fresh read run ini: freeSharesLeft 1848/2000, sharesSold 152, finalized 0 -> BELUM sold out. "
 "Gate website-only SUDAH FAILED sejak 2026-11-03 (lead-reported-gate-blocked), tidak pernah di-mint. Dilaporkan sekali sebagai perubahan run ini."),
 "freeSharesLeft_last":1848, "FREE_SHARES":2000,
 "launch_verified":"2026-11-03 07:47:23 WIB (first Minted event on-chain)",
}
hong=t.pop("Hongbao-HONGBAO", None)
ex["Hongbao-HONGBAO"]={
 "sale":"0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97",
 "token":"0xcdce49721d2fed646d4c1a34a51ec001cd879449",
 "track":"C",
 "status":"excluded-age-over-48h-2026-11-06",
 "note":("Run 0401: first Claimed terverifikasi blok 131180684 = 2026-11-02 11:56:14 WIB -> umur ~89 jam > 48 jam -> AGE-EXCLUDED, "
 "dihapus dari track_c. Fresh read run ini: totalSharesSold 7/10000, mintOpen=1, freeClaimed 7 -> BELUM sold out. "
 "Gate website-only SUDAH FAILED sejak 2026-11-03 (lead-reported-gate-blocked), tidak pernah di-mint. Dilaporkan sekali sebagai perubahan run ini."),
 "totalSharesSold_last":7, "TOTAL_SHARES":10000,
 "launch_verified":"2026-11-02 11:56:14 WIB (first Claimed event on-chain)",
}
nv=t.pop("Nvagent-NVGT", None)
ex["Nvagent-NVGT"]={
 "sale":"0x7Eb3a26F895d4D1b8FcD38A67E9689cB2693661f",
 "token":"0x7Eb3a26F895d4D1b8FcD38A67E9689cB2693661f",
 "track":"C",
 "status":"excluded-age-over-48h-2026-11-06",
 "note":("Run 0401: first user mint terverifikasi 2026-11-03 00:04:21 WIB (first contract->minter Transfer, Ankr getLogs) -> umur ~77 jam > 48 jam -> AGE-EXCLUDED, "
 "dihapus dari track_c. Fresh read run ini: totalMints 59, mintOpen=1 -> BELUM sold out. Proyek Nvagent sudah dilaporkan sekali via deployment 0x4951 "
 "(hot-leg 2026-11-02); deployment ini tidak pernah dilaporkan terpisah. Gate website-only FAILED 2026-11-03, tidak pernah di-mint. Dilaporkan sekali sebagai perubahan run ini."),
 "totalMints_last":59,
 "launch_verified":"2026-11-03 00:04:21 WIB (first user mint on-chain)",
}
nv28=t.pop("Nvagent-NVGT-28Fe", None)
ex["Nvagent-NVGT-28Fe"]={
 "sale":"0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2",
 "token":"0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2",
 "track":"C",
 "status":"excluded-age-over-48h-2026-11-06",
 "note":("Run 0401: first mint terverifikasi blok 131276063 = 2026-11-02 23:51:48 WIB (earliest from-zero, Ankr getLogs) -> umur ~77 jam > 48 jam -> AGE-EXCLUDED, "
 "dihapus dari track_c. Fresh read run ini: totalMints 131, mintOpen=1 -> BELUM sold out. Proyek Nvagent sudah dilaporkan sekali via deployment 0x4951 "
 "(hot-leg 2026-11-02); deployment ini tidak pernah dilaporkan terpisah (same owner group d76d). Gate website-only FAILED 2026-11-03, tidak pernah di-mint. "
 "Dilaporkan sekali sebagai perubahan run ini."),
 "totalMints_last":131,
 "launch_verified":"2026-11-02 23:51:48 WIB (first mint on-chain)",
}
s["last_run_wib"]="2026-11-06 run 0401"
s["last_run"]="Run 0401: SILENT kecuali 4 age-exclusion track-C (Soarm, Hongbao, Nvagent 0x7Eb3 + 0x28Fe). 0 early lead baru, 0 strong lead, 0 kandidat, 0 track-C lead/kandidat, 0 klaim. Scan 2000 blok sukses, 3 first-seen, triage log-only semua."
s["runNote0401"]="Run 0401 (blok 131888994): re-read 21 NFT + 18 track-C; HIVE flat 1253; SEAT 2555->2576 velocity FAIL; Mossminds freeMinted 874 (+9) velocity FAIL + status discarded; MILLION semua view None (RPC fail, bukan nol). Boltbook 0 hits. Sourcify feed 1 baru, 0 sale shape. 5c: 12 ERC-20 dicek, 0 lolos S1/S2. Scan 131886995-131888994 sukses (80 Ankr, 0 error), 3 first-seen, triage log-only. Bridge 0 not in snapshot. Binanceai tetap refund/failed. 4 age-exclusion track-C (Soarm/Hongbao/Nvagent x2) dilaporkan sekali + dihapus dari track_c."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("SNAPSHOT UPDATED; track_c now", len(t), "items; excluded now", len(ex))
print("removed:", bool(soarm), bool(hong), bool(nv), bool(nv28))
