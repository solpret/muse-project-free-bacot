import json, datetime
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
def addr_of(n):
    try: return "0x" + format(int(n), "040x")
    except Exception: return None
snap = json.load(open(HF + "onchain-snapshot.json"))
rr = json.load(open(HF + "run-2026-11-03-1331-reread.json"))
blk = rr.get("block", 131388390)
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
MAP = [("totalSupply()", "totalSupply"), ("freeClaimed()", "freeClaimed"), ("FREE_SUPPLY()", "FREE_SUPPLY"),
       ("totalMinted()", "totalMinted"), ("freeMinted()", "freeMinted"), ("mintOpen()", "mintOpen"),
       ("mintedBy(address)", "userMintedBy"), ("freeUsed(address)", "userFreeUsed"),
       ("balanceOf(address)", "userBalance"), ("quote(address,uint256)", "quoteUser1")]
updated = []
for name, v in rr.items():
    if name == "block" or not isinstance(v, dict): continue
    e = snap["contracts"].get(name)
    if e is None: continue
    for sk, dk in MAP:
        val = v.get(sk)
        if val is None: continue
        if dk == "mintOpen": e[dk] = bool(val)
        else: e[dk] = val
    o = addr_of(v.get("owner()"))
    if o: e["owner"] = o
    free = e.get("freeClaimed") if e.get("freeClaimed") is not None else e.get("freeMinted")
    cap = e.get("FREE_SUPPLY")
    if isinstance(free, int) and isinstance(cap, int) and cap:
        e["freePctVerified"] = round(free / cap * 100, 2)
    e["lastReadBlock"] = blk
    e["lastReadWib"] = now
    updated.append(name)
print("reread-updated:", len(updated))
# Status overrides
rob = snap["contracts"]["Robogent"]
rob["status"] = "strong-lead-gate-blocked-2026-11-03"
rob["gateNote"] = ("Gate website GAGAL run 1331 setelah metode (A)-(N): (H) contractURI tanpa external_link; "
 "(I) tokenURI(1) tanpa external_url; (J) ABI tanpa fungsi situs; (C) metadata Sourcify tanpa URL; (A) pencarian alamat kontrak nihil; "
 "(B) tidak ada post Boltbook bernama Robogent; (D) pola same-family site: nihil; (E) owner grup 6f24 (factory wave tanpa website = GAGAL gate); "
 "(G) pencarian nama proyek nihil (AgentRob = proyek lain di Robinhood Chain, HelloAgents = proyek lain); "
 "(K) GitHub search-index nihil (catatan: code search sejati butuh auth); (L) BscScan via live browser: halaman token cocok, kolom Website/Social KOSONG, "
 "tidak ada tautan situs resmi (sempat terhalang verifikasi Cloudflare, dipulihkan lalu dibaca); (M) site:vercel/pages/deed nihil + pencarian alamat deployer nihil; "
 "(N) tidak ada post Boltbook sehingga tidak ada hop author->X->situs; (F) tidak berlaku (tidak ada handle yang ditemukan untuk dikonfirmasi; X opsional, bukan gate). "
 "3 kaki strong terpenuhi (umur first-mint 2026-11-03 12:20:32 WIB; free 540/2000=27,0%; slot user terbuka quote 0). TIDAK di-preview, TIDAK di-mint.")
for n in ["Vesperfang", "Gourdmare"]:
    if n in snap["contracts"]:
        snap["contracts"][n]["status"] = "promotion-discarded-same-owner-2026-11-03"
        snap["contracts"][n]["discardNote"] = "Owner grup d76d (0xd76d5918fb337667b22fe37ae2055b5542cf8dc9) terkonfirmasi pada re-read run 1331; promosi apapun dibuang aturan same-owner."
for n in ["Medusine", "Mummyrelic", "Ravenhex", "Orbitmarshal", "Mothwraith"]:
    if n in snap["contracts"]:
        snap["contracts"][n]["ownerGroupNote"] = "Owner grup a054 (0xa054275580c6d1c9077543907ac5798f2494ecce) — jangan dipromosikan (preseden Mothwraith: status dibiarkan, promosi ditahan)."
wa = snap["contracts"].get("Whale Agent")
if wa:
    wa["soldOutNote"] = "Free pool SOLD OUT pada re-read run 1331: freeMinted 234/234 (sebelumnya 223/234). Item sudah berstatus promotion-discarded-same-owner, jadi tidak dilaporkan sebagai lead; hanya dicatat + nilai diperbarui."
# Scan watchlist-only additions (pra-window first mints, verified run 1331)
adds = {
 "Spookagent": {"address": "0x90f9de2A0Ab81052a0959bd71B46cdcFd57152eB", "symbol": "SPOOKAGENT",
   "totalSupply": 416, "freeClaimed": 412, "FREE_SUPPLY": 5555, "freePctVerified": 7.42,
   "firstMintBlock": 131383917, "firstMintWib": "2026-11-03T13:20:55+07:00",
   "owner": "0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
   "status": "watchlist-only-not-early-2026-11-03",
   "note": "Scan 1331 first-seen di jendela, TAPI first mint terverifikasi Ankr pra-window (blok 131383917, di gap yang dilewati) -> watchlist-only, bukan early lead (preseden Drakogent). ABI Sourcify terverifikasi: AGENT_ID + free views + mint + contractURI. Slot user terbuka (quote 0)."},
 "Chromagent": {"address": "0x895087300b81956e3242Be7132d55dB90Af0DEBD", "symbol": "CHROMAGENT",
   "totalSupply": 308, "freeClaimed": 304, "FREE_SUPPLY": 4444, "freePctVerified": 6.84,
   "firstMintBlock": 131385868, "firstMintWib": "2026-11-03T13:35:33+07:00",
   "owner": "0x6f244724f61d8c7fc9af40dd37ff7c82bf2b8f5d",
   "status": "watchlist-only-not-early-2026-11-03",
   "note": "Scan 1331 first-seen, TAPI first mint terverifikasi Ankr pra-window (blok 131385868, di gap yang dilewati) -> watchlist-only, bukan early lead. ABI terverifikasi: AGENT_ID + free views + mint + contractURI. Slot user terbuka (quote 0)."},
 "Scarabagent": {"address": "0xFC4482e1c66DfDabe4fCCeC0F7A6C480b85C3a47", "symbol": "SCRBGT",
   "totalSupply": 291, "freeClaimed": 291, "FREE_SUPPLY": 1111, "freePctVerified": 26.19,
   "firstMintBlock": 131383542, "firstMintWib": "2026-11-03T13:18:05+07:00",
   "owner": "0xd76d5918fb337667b22fe37ae2055b5542cf8dc9",
   "status": "promotion-discarded-same-owner-2026-11-03",
   "note": "Scan 1331 first-seen; first mint pra-window (blok 131383542). Free 26,19% + slot terbuka TETAPI owner grup d76d -> promosi DIBUANG aturan same-owner, tidak pernah dilaporkan sebagai lead/di-preview/di-mint."},
 "NIANNIAN": {"address": "0x4A2bb7B24C39CA548b050aD0C0aFfea5e6e04aF2", "symbol": "NIANNIAN-NFT",
   "freeMintedShares": 38, "MAX_FREE_CLAIMS": 2000,
   "firstMintBlock": 131382387, "firstMintWib": "2026-11-03T13:09:25+07:00",
   "status": "watchlist-only-not-early-2026-11-03",
   "note": "Scan 1331 first-seen (ERC721, template klaim-share non-standar: freeMintedShares/agentFreeClaimed/MAX_FREE_CLAIMS; ABI TANPA AGENT_ID/agentRegistry; sebagian besar view standar revert). First mint terverifikasi Ankr pra-window (blok 131382387, di gap yang dilewati) -> watchlist-only, bukan early lead. Slot user UNVERIFIED (agentFreeClaimed revert)."},
}
for name, vals in adds.items():
    e = {"name": name, "kind": "ERC721", "mintOpen": True, "userMintedBy": 0, "userFreeUsed": 0, "userBalance": 0, "quoteUser1": 0,
         "scanWindow": "131386391-131388390", "source": "scan-1331", "lastReadBlock": blk, "lastReadWib": now}
    e.update(vals)
    snap["contracts"][name] = e
print("snapshot contracts now:", len(snap["contracts"]))
snap["timestamp_wib"] = now
snap["note"] = ("Run 1331 final: 3 early lead baru (Threadmoth, Syntaxia, Compilur); Robogent promosi strong-lead-gate-blocked; "
 "Whale Agent free pool sold out 234/234 (item discard, hanya dicatat); scan 1331 sukses 131386391-131388390 (gap 131382259-131386390, 4132 blok, dilewati karena cap 2000); "
 "5c: 20 shape-check, 0 lolos S1/S2; tidak ada auto-mint/auto-claim.")
json.dump(snap, open(HF + "onchain-snapshot.json", "w"), indent=1)
# Scan state + seen
st = json.load(open(HF + "onchain-scan-state.json"))
st["last_scanned_block"] = 131388390
st["last_scan_window_from"] = 131386391
st["last_scan_window_to"] = 131388390
st["last_scan_wib"] = now
st["ankr_calls"] = 80
st["errors"] = []
st["nft_contracts"] = 303
st["erc20_mint_contracts"] = 688
st["skipped_gap"] = "131382259-131386390 (4132 blocks, window capped at 2000; scan covered most recent 2000 blocks 131386391-131388390)"
st["note"] = ("Scan 1331 run: window 131386391-131388390 (2000 blok, cap; watermark sebelumnya 131382258); gap dilewati 131382259-131386390 "
 "(4132 blok) dicatat, bukan dipindai unbounded. 80 panggilan Ankr, 0 error, 303 kontrak NFT/1155, 688 kontrak ERC-20 mint. "
 "First-seen sejati vs scan-seen+snapshot: 25; yang lolos uji agent-shape terverifikasi independen (ABI Sourcify + first-mint Ankr): "
 "Spookagent/Chromagent/Scarabagent/NIANNIAN — keempatnya first mint PRA-window (di gap) sehingga watchlist-only, bukan early lead; "
 "Scarabagent tambahan discard grup d76d. 21 first-seen lainnya bukan agent-shaped (ABI kosong / tanpa free-shape) -> seen-only.")
json.dump(st, open(HF + "onchain-scan-state.json", "w"), indent=1)
scan = json.load(open(HF + "onchain-scan-2026-11-03-1331.json"))
seen = json.load(open(HF + "onchain-scan-seen.json"))
cs = seen.get("contracts", {})
added = 0
for c in scan["contracts"]:
    if c["address"] not in cs and c["address"].lower() not in {k.lower() for k in cs}:
        cs[c["address"]] = c.get("first_block")
        added += 1
seen["contracts"] = cs
json.dump(seen, open(HF + "onchain-scan-seen.json", "w"), indent=1)
print("seen added:", added, "seen total:", len(cs))
print("owner check d76d:", addr_of(1229871558447893504018807355346280440071973735881))
print("owner check 6f24:", addr_of(634506999938203166987997171857479220707097022301))
print("owner check a054:", addr_of(915315212402816936339815748123264820066162896078))
