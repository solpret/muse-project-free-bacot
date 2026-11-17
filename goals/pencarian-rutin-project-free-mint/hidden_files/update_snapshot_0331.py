import json
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
# --- seen file ---
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
new_seen={
 "0xd36b54fbd4c9fa99731b52907713c9e1983ad8a4":131883591,
 "0x61b1668af9a34cfde0b4e8565ef3c28aacc3dc2e":131882604,
 "0x4b2469e26451c0813e95d2fbd9683b50e1811035":131882745,
 "0xbc81a0909eb530d7809f9a5b4518999cf20292a3":131883110,
 "0xf4fa74d20a445cbd0a2559890b8eb129befb8eea":131883444,
 "0x638ca21ade5ea01ad15cf6193cbc2b1206b307d1":131883586,
 "0xabd3f4f0c611f6548445f1c5fe5fbc636eee3773":131884092,
 "0x96922bc3f136967b55dab654250f90112c92c0dc":131884137,
}
for k,v in new_seen.items(): seen["contracts"][k]=v
seen["_meta"]["last_scan_wib"]="2026-11-06 run 0331"
seen["_meta"]["last_scan_window"]="131882354-131884353"
seen["_meta"]["last_scan_added"]=8
seen["_meta"]["note_0331"]=("Run 0331: 8 true first-seen appended (MILLION, Nova Pylon, Ethereal Zebra Agent, "
 "Loom Vellum, Void Rat Agent, Pearl Mesa, Zenith Arch, Cyber Scribe). MILLION agent-shaped STRICT "
 "(agentRegistry()=registry Agent ID persis + FREE_SUPPLY 500 + 9 mint/9 minter, totalMinted 14) -> EARLY LEAD run ini. "
 "3 lainnya AGENT_REGISTRY()=registry tapi tanpa free view/konstanta + totalSupply 3333=MAX -> log only (precedent Agent Shift Pals). "
 "4 sisanya hanya registry-bytes hit (diskriminator lemah 81%) tanpa registry read -> log only.")
json.dump(seen, open(f"{BASE}/onchain-scan-seen.json","w"), indent=1)
# --- scan state ---
st=json.load(open(f"{BASE}/onchain-scan-state.json"))
st.update({
 "last_scanned_block":131884353,
 "last_scan_window_from":131882354,
 "last_scan_window_to":131884353,
 "last_scan_wib":"2026-11-06 run 0331",
 "ankr_calls":80, "errors":[],
 "nft_contracts":202, "erc20_mint_contracts":345,
 "skipped_gap":"131878074-131882353 (4280 blok; window dari watermark 131878073 ke head 131884353 = 6280 blok > cap 2000; scan menutup 2000 blok terbaru 131882354-131884353)",
 "note":("Scan run 0331 SUKSES (80 panggilan Ankr, 0 error, ~20 mnt - Ankr lambat hari ini). "
 "8 first-seen sejati. Gap kumulatif sejak run 1831 ~59.000 blok tak ter-scan. Rantai ~0,7 dtk/blok - 30 mnt = ~2500 blok, cap 2000 hanya menutup ~24 mnt."),
 "last_scan_window":"131882354-131884353",
})
json.dump(st, open(f"{BASE}/onchain-scan-state.json","w"), indent=1)
# --- snapshot ---
s=json.load(open(f"{BASE}/onchain-snapshot.json"))
r=json.load(open(f"{BASE}/run-2026-11-06-0331-reread-lean.json"))
rr=r["reread"]; tc=r["track_c"]
def upd(name, **kw):
    e=s["contracts"].setdefault(name,{})
    for k,v in kw.items():
        if v is not None: e[k]=v
    return e
upd("HIVE Agents", totalSupply=1253, balanceOf_user=1)
s["contracts"]["HIVE Agents"]["lastReadWib"]="2026-11-06 run 0331"
s["contracts"]["HIVE Agents"]["lastReadBlock"]=131884353
s["contracts"]["HIVE Agents"]["run0331_velocity"]=("FAIL: 1253 flat vs run 0301 (1253) -> velocity 0. Minted-by-user; tetap dipantau.")
s["contracts"]["HIVE Agents"]["previousTotalSupply"]=1253
s["contracts"]["HIVE Agents"]["mintedInInterval"]=0
s["contracts"]["HIVE Agents"]["currentRatePerMin"]=0.0
upd("Mummyhive", totalSupply=600, freeClaimed=582, balanceOf_user=0)
upd("Thronemind", totalSupply=650, freeMinted=650, balanceOf_user=0, canFreeMint_user=1, claimedFree_user=0)
upd("Hashseers", freeMinted=589, balanceOf_user=0, canFreeMint_user=1, claimedFree_user=0)
upd("Smeltbots", totalSupply=603, freeMinted=603, balanceOf_user=0, canFreeMint_user=1, claimedFree_user=0)
upd("Forklings", totalSupply=908, freeMinted=908, balanceOf_user=0)
upd("Agent Frogs", totalSupply=408, freeClaimed=408, balanceOf_user=0, mintedBy_user=0)
upd("PassAgentX", freeMinted=3648, balanceOf_user=0, mintedBy_user=0)
upd("SEAT-f11e", totalSupply=2555, totalMinted=2555, balanceOf_user=0)
upd("StarAgent-7d39", totalSupply=1102, balanceOf_user=0)
upd("LuckyBox-d08e", totalSupply=611, balanceOf_user=0, mintedBy_user=0, freeUsed_user=0)
upd("SnailMail", totalSupply=301, costOf_user_1=0, mintOpen=1, mintedBy_user=0)
upd("wheelz", totalSupply=307, balanceOf_user=0, costOf_user_1=0, mintsLeft_user=10, mintOpen=1, mintedBy_user=0)
upd("Tumblebots", totalSupply=648, freeMinted=648, balanceOf_user=0)
upd("Mossminds", totalSupply=865, freeMinted=862, canFreeMint_user=1, claimedFree_user=0, balanceOf_user=0)
upd("Jolly", totalMinted=3629, freeMinted=3629, balanceOf_user=0)
upd("AgentGlyph", totalSupply=513, freeClaimed=512)
# velocity notes
s["contracts"]["SEAT-f11e"]["run0331_velocity"]=("FAIL: 2528->2555 (+27, ~0.71/mnt dlm ~38 mnt) vs prev 1.956 = 0.36x -> velocity GAGAL. % gratis + website UNVERIFIED -> tetap watchlist-only.")
s["contracts"]["SEAT-f11e"]["previousTotalSupply"]=2528
s["contracts"]["SEAT-f11e"]["mintedInInterval"]=27
s["contracts"]["SEAT-f11e"]["currentRatePerMin"]=0.71
s["contracts"]["Mossminds"]["run0331_velocity"]=("PASS hitung: 826->865 (+39, ~1.03/mnt dlm ~38 mnt) vs prev 0.3415 = 3.0x DAN >=20 token -> kaki velocity LULUS run ini (interval pasti antar-read tidak tercatat; bahkan interval 60 mnt pun 1.9x). Status TETAP promotion-discarded-same-owner-2026-11-05: TIDAK dipromosikan, TIDAK dilaporkan sebagai lead, TIDAK di-preview/di-mint.")
s["contracts"]["Mossminds"]["previousTotalSupply"]=826
s["contracts"]["Mossminds"]["mintedInInterval"]=39
s["contracts"]["Mossminds"]["currentRatePerMin"]=1.03
s["contracts"]["Mossminds"]["previousRatePerMin"]=0.3415
s["contracts"]["Mossminds"]["velocityLegPasses"]=True
# track_c updates
t=s.setdefault("track_c",{})
if "DROID" in t:
    t["DROID"]["freeMinted"]=581
    t["DROID"]["run0331"]="freeMinted 574->581, opened=0; status watchlist-only-age-slot-unverified tidak berubah."
# Ikigai age-exclusion: move to excluded
ik=t.pop("Ikigai-Ihigi", None)
s.setdefault("excluded",{})["Ikigai-Ihigi"]={
 "sale":"0x3611455bE1FC2c6987FE9d016971b7E40B341684",
 "token":"0x76437a85b768bb5612e8a466e492d89d8ef634b1",
 "track":"C",
 "status":"excluded-age-over-48h-2026-11-06",
 "note":("Run 0331: startTime() dibaca ulang segar = 1793637000 = 2026-11-02 23:30 WIB (cocok snapshot); "
 "umur 76,6 jam > 48 jam -> AGE-EXCLUDED, dihapus dari track_c. Phase dibaca 3 run ini (freeMinted gagal baca, None - bukan nol; "
 "nilai lama 273 dipertahankan di catatan). Gate website-only SUDAH FAILED sejak 2026-11-02 (lead-reported-gate-blocked-no-mint), "
 "tidak pernah di-mint. Dilaporkan sekali sebagai perubahan (age-exclusion) run ini."),
 "freeMinted_last":273, "FREE_CAP":1000,
 "launch_verified":"2026-11-02 23:30 WIB (startTime on-chain)",
 "gate":"FAILED website-only 2026-11-02",
}
# MILLION early lead
s["contracts"]["MILLION"]={
 "address":"0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4",
 "status":"early-lead-reported-2026-11-06-run0331",
 "name":"MILLION","symbol":"MILLION","kind":"ERC721",
 "totalSupply":None,"totalMinted":14,"freeClaimed":None,"freeMinted":None,
 "FREE_SUPPLY":500,"MAX_SUPPLY":5500,
 "freePctVerified":None,
 "mintOpen":None,
 "userMintedBy":0,"userFreeUsed":None,"userBalance":0,
 "userSlotNote":"Slot user UNVERIFIED: canFreeMint/canClaimFree/freeMinted/quote semua null (fungsi tidak ada atau gagal baca RPC) - TIDAK preview-verified (early lead tidak pernah di-preview).",
 "firstSeenBlock":131883591,
 "firstMintWib":"2026-11-06 03:49:26 WIB",
 "scanMints":9,"scanMinters":9,
 "scanWindow":"131882354-131884353",
 "lastReadBlock":131884353,
 "lastReadWib":"2026-11-06 run 0331",
 "xVerified":False,"velocityVerified":False,
 "launchNote":"First mint terverifikasi on-chain: blok 131883591, 2026-11-06 03:49:26 WIB (9 mint/9 minter dalam window scan, totalMinted 14 saat triage). Umur ~35 menit saat triage -> TERVERIFIKASI <=48 jam via first-mint bound. Tidak ada project-stated launch time.",
 "baselineNote":("EARLY lead dilaporkan sekali run 0331. Agent-shape TERBUKTI on-chain: agentRegistry() = 0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F persis (registry Agent ID) + FREE_SUPPLY 500 (konstanta free-supply). "
 "Free pool (% gratis, freeMinted, canFreeMint, quote) UNVERIFIED - semua view null; website + X UNVERIFIED; velocity belum terhitung (baseline pertama). "
 "Tidak pernah auto-mint/preview. Naik ke strong lead hanya bila 3 kaki terpenuhi; ke kandidat hanya bila SEMUA kriteria + safety lolos."),
 "velocityLegPasses":False,
 "supplyView":"totalMinted",
 "previousTotalSupply":14,
 "previousRatePerMin":None,
}
s["runNote0331"]=("Run 0331: EARLY LEAD MILLION (lihat entry) + Ikigai-Ihigi AGE-EXCLUDED (dihapus dari track_c). "
 "Re-read: HIVE 1253 flat (velocity FAIL); SEAT-f11e 2528->2555 (+27, 0.36x, velocity FAIL); Mossminds 826->865 (+39, ~3.0x, velocity PASS hitung - status tetap discarded-same-owner, tidak dipromosikan). "
 "Inkrement kecil lain: Forklings 908, PassAgentX freeMinted 3648, Thronemind 650, Hashseers 589, Smeltbots 603, Agent Frogs 408, Tumblebots 648, Jolly 3629. "
 "Tidak ada sellout baru, tidak ada slot hilang. pending_claims kosong.")
s["runNote0331_scan"]=("Scan run 0331 SUKSES: window 131882354-131884353 (2000 blok, cap; gap 131878074-131882353 = 4280 blok terlewat), 80 panggilan Ankr, 0 error, 202 NFT/1155 + 345 ERC-20. "
 "8 first-seen sejati (MILLION early lead; 7 lain log only). 5c: 16 ERC-20 mint_count>=10 di-shape-check, 0 lolos S1/S2 (checked total 95).")
s["runNote0331_triage"]=("First-seen triage run 0331 (8): MILLION EARLY LEAD (agentRegistry()=registry persis, FREE_SUPPLY 500, totalMinted 14, 9 mint/9 minter, first mint 03:49:26 WIB); "
 "Ethereal Zebra Agent / Void Rat Agent / Cyber Scribe AGENT_REGISTRY()=registry tapi tanpa free view/konstanta + totalSupply 3333=MAX -> log only; "
 "Nova Pylon / Loom Vellum / Pearl Mesa / Zenith Arch hanya registry-bytes hit, tanpa registry read, 1 mint -> log only.")
s["runNote0331_binanceai"]=("Binanceai tetap refund/failed run 0331: launched=0, failed=1, isRefundPhase=1, totalShares=3110, tokenClaimed(user)=0, tokenBalance(user)=0. pending_claims tetap kosong; tidak ada laporan ulang.")
s["last_run_wib"]="2026-11-06 run 0331"
s["last_run_note"]="EARLY LEAD MILLION + Ikigai age-excluded; selain itu silent (tidak ada kandidat/strong lead/track-C baru)."
json.dump(s, open(f"{BASE}/onchain-snapshot.json","w"), indent=1)
print("SNAPSHOT UPDATED; contracts:", len(s["contracts"]), "track_c:", len(s["track_c"]), "excluded:", len(s["excluded"]))
print("Ikigai in track_c:", "Ikigai-Ihigi" in s["track_c"], "| in excluded:", "Ikigai-Ihigi" in s["excluded"])
print("MILLION in contracts:", "MILLION" in s["contracts"])
