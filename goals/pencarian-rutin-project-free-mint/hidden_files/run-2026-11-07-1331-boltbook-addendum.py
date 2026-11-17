#!/usr/bin/env python3
"""Addendum run 1331: record Boltbook-triage dispositions in snapshot excluded.
Reloads snapshot fresh; atomic write. Read-only except this write."""
import json, os
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RUN="2026-11-07 run 1331"
ENTRIES={
 "Kora Agent": {
  "address":"0x67251c3b2830728316f3a0816df57fda5dc959bf",
  "status":"excluded-age-over-48h-2026-11-07",
  "name":"Kora Agent","kind":"ERC721",
  "totalSupply":9900,"totalMinted":9900,"MAX_SUPPLY":10000,
  "freeClaimed":None,"freePctVerified":None,
  "ageExclusionNote":("Boltbook route 2 run 1331 (post recheck 13:36 WIB: 9.900/10.000, 0 mint "
   "~11 mnt, frozen; Sourcify UNVERIFIED; tanpa situs/X/waktu launch). Verifikasi parent: "
   "totalSupply 9900/10000 on-chain (blok 132157978); Ankr ankr_getLogs Transfer-from-zero "
   "untuk kontrak ini: 0 log dalam 48 jam terakhir DAN 0 log dalam jendela 96-48 jam lalu "
   "(kontrol Wuyuhive/Agentdragon/Chipagent pada jendela sama mengembalikan log -> metode "
   "valid). Karena 9.900 token sudah ada tapi tidak ada satu pun mint dalam 96 jam terakhir, "
   "mint terakhir (apalagi mint pertama) terjadi >96 jam lalu -> umur peluncuran TERVERIFIKASI "
   ">48 jam, belum sold out (100 slot tersisa). Free views tidak terbaca (freeClaimed/freeMinted/"
   "FREE_SUPPLY/mintOpen revert/transport-gagal) -> free% UNVERIFIED. Bukan kandidat/strong lead."),
  "lastReadWib":RUN},
 "Nero Agent": {
  "address":"0x26929b87f80b7f126fa56dc26e59a774990641f1",
  "status":"excluded-age-over-48h-2026-11-07",
  "name":"Nero Agent","kind":"ERC721",
  "totalSupply":9900,"totalMinted":9900,"MAX_SUPPLY":10000,
  "freeClaimed":None,"freePctVerified":None,
  "ageExclusionNote":("Boltbook route 2 run 1331 (post recheck 11:44 WIB: 9.900/10.000; Sourcify "
   "belum terkonfirmasi; tanpa situs/X/waktu launch). Verifikasi parent: totalSupply 9900/10000 "
   "on-chain (blok 132157978); Ankr Transfer-from-zero: 0 log dalam 48 jam terakhir DAN 0 log "
   "dalam jendela 96-48 jam lalu (metode tervalidasi kontrol). Mint terakhir >96 jam lalu -> umur "
   "TERVERIFIKASI >48 jam, belum sold out. Free views tidak terbaca -> free% UNVERIFIED. "
   "Bukan kandidat/strong lead."),
  "lastReadWib":RUN},
 "Luma Agent": {
  "address":"0xf198c48534c5853ee3cb3be62a990d3395a73358",
  "status":"excluded-age-over-48h-2026-11-07",
  "name":"Luma Agent","kind":"ERC721",
  "totalSupply":4900,"totalMinted":4900,"MAX_SUPPLY":5000,
  "freeClaimed":None,"freePctVerified":None,
  "ageExclusionNote":("Boltbook route 2 run 1331 (post recheck 01:58 WIB: 4.900/5.000; tanpa "
   "situs/X/waktu launch). Verifikasi parent: totalSupply 4900/5000 on-chain (blok 132157978); "
   "Ankr Transfer-from-zero: 0 log dalam 48 jam terakhir DAN 0 log dalam jendela 96-48 jam lalu "
   "(metode tervalidasi kontrol). Mint terakhir >96 jam lalu -> umur TERVERIFIKASI >48 jam, "
   "belum sold out (100 slot). Free views tidak terbaca -> free% UNVERIFIED. Bukan kandidat/"
   "strong lead."),
  "lastReadWib":RUN},
 "Chipagent": {
  "address":"0xc3d831db5f018ab9977724352ec773ba0ac3ae4a",
  "status":"excluded-sold-out-2026-11-07",
  "name":"Chipagent","kind":"ERC721",
  "totalSupply":999,"MAX_SUPPLY":999,"FREE_SUPPLY":999,"freeClaimed":998,
  "freePctVerified":99.9,
  "ageExclusionNote":("Boltbook route 2 run 1331 (post recheck 09:22 WIB: 892/1.535; Sourcify "
   "VERIFIED). Verifikasi parent: totalSupply 999/999 = MAX_SUPPLY 999 on-chain (blok "
   "132157978); freeClaimed 998/999; mint terakhir ~4,2 jam lalu (Ankr Transfer-from-zero "
   "terbaru blok 132125347). SOLD OUT -> bukan kandidat/lead. Catatan: post menyebut 1.535 "
   "tapi MAX_SUPPLY on-chain 999; 1 free slot tersisa menurut freeClaimed tapi cap total "
   "tercapai, jadi tidak bisa mint lagi."),
  "lastReadWib":RUN},
 "Agentdragon": {
  "address":"0x2df7435f5bce0577bee213e13da68313c74d7d0b",
  "status":"excluded-age-over-48h-2026-11-07",
  "name":"Agentdragon","kind":"ERC721",
  "totalSupply":1930,"MAX_SUPPLY":2000,"FREE_SUPPLY":2000,"freeClaimed":1924,
  "freePctVerified":96.2,
  "ageExclusionNote":("Temuan pelengkap scan (bridge run-16, first-seen 2026-11-03 23:42-23:49 WIB, "
   "bukan lead baru job ini); Boltbook route 2 run 1331 mengonfirmasi (1.822/2.000, frozen). "
   "Verifikasi parent: totalSupply 1930/2000, freeClaimed 1924/2000 (96,2%), mintOpen 1, "
   "balanceOf(user) 0 (blok 132157978); Ankr Transfer-from-zero ada di jendela 96-48 jam lalu "
   "(blok 131773888) + first-seen bridge 2026-11-03 -> umur TERVERIFIKASI >48 jam (~86 jam), "
   "belum sold out. Free% tinggi tapi aturan umur menggugurkan tanpa pandang %. Bukan kandidat/"
   "strong lead; tidak pernah dilaporkan sebagai lead oleh job ini."),
  "lastReadWib":RUN},
 "Wuyuhive": {
  "address":"0x250e800025a9a7861970e253bab6975a57f80567",
  "status":"excluded-age-over-48h-2026-11-07",
  "name":"Wuyuhive","kind":"ERC721",
  "totalSupply":1509,"MAX_SUPPLY":3000,"FREE_SUPPLY":3000,"freeClaimed":1503,
  "freePctVerified":50.1,
  "ageExclusionNote":("Temuan pelengkap scan (bridge run-16, first-seen 2026-11-03 23:42-23:49 WIB, "
   "bukan lead baru job ini); Boltbook route 2 run 1331 mengonfirmasi (1.369/3.000, "
   "freeClaimed 1.363/3.000, FREE_PER_WALLET 2, Sourcify exact_match). Verifikasi parent: "
   "totalSupply 1509/3000, freeClaimed 1503/3000 (50,1%), mintOpen 1, balanceOf(user) 0 (blok "
   "132157978); Ankr Transfer-from-zero ada di jendela 96-48 jam lalu (blok 131773573) + "
   "first-seen bridge 2026-11-03 -> umur TERVERIFIKASI >48 jam (~86 jam), belum sold out. "
   "Free% 50,1% lolos ambang tapi aturan umur menggugurkan tanpa pandang %. Bukan kandidat/"
   "strong lead; tidak pernah dilaporkan sebagai lead oleh job ini."),
  "lastReadWib":RUN},
}
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
for name,e in ENTRIES.items():
    if name in snap.get("contracts",{}):
        print("SKIP (already in contracts):",name); continue
    snap.setdefault("excluded",{})[name]=e
    print("EXCLUDED:",name,e["status"])
with open(f"{BASE}/onchain-snapshot.json.tmp","w") as f:
    json.dump(snap,f,indent=1)
os.replace(f"{BASE}/onchain-snapshot.json.tmp",f"{BASE}/onchain-snapshot.json")
print(f"ADDENDUM DONE contracts={len(snap['contracts'])} excluded={len(snap.get('excluded',{}))}")
