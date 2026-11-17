#!/usr/bin/env python3
"""Snapshot update #3 for run 2026-11-16 12:01 WIB (Glyphs of Xor + run summary).
XOR verdict: AGE-EXCLUDED. Evidence:
- getLogs walk (blxrbdn, 5000-blok chunks, head 133870313): only 3 Transfer-from-zero
  in chunks 0-39 (blok 133670314-133870313, ~25 jam); tertua 133684157 = 15 Nov 13:02 WIB (23,6 jam).
  totalSupply 296 -> 293 mint mendahului jendela -> first mint PASTI >24 jam (lebih tua dari 25 jam).
  Chunk 40-44 (133645314-133670313) tidak ter-cover (blxrbdn timeout/empty, egress flapping) -
  tapi semua blok di sana >24 jam, jadi vonis tidak bergantung padanya.
  Dikoroborasi monitor first-detection 11 Nov 02:38 WIB (Boltbook post _H83Fc6RBFBU).
- free% 296/1555 = 19,0% (<50% dan <70%); velocity ~0 (3 mint/25 jam); website/X unverified.
- Sourcify exact_match, verifiedAt 2026-11-10T19:39:31Z. tokenURI(1)="1" (tanpa URL).
- Komentar binanceweb3x.ai: mint(1) value 0 lolos juga dari dead address tanpa Agent ID -
  jalur gratis mungkin tidak benar-benar ter-gate (tidak dikejar lebih jauh; umur sudah menggugurkan).
Tidak pernah dilaporkan sebelumnya -> DIAM. No preview/mint."""
import json
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
s = json.load(open(BASE + "onchain-snapshot.json"))
s["contracts"]["Glyphs of Xor"] = {
    "address": "0x1577cbaaa3097c16d8aa93639cd00430e14ab90c",
    "name": "Glyphs of Xor", "symbol": "XOR",
    "status": "checked-age-excluded-2026-11-16",
    "totalSupply": 296, "MAX_SUPPLY": 1555, "MAX_PER_WALLET": 10,
    "mintOpen": 1, "price": 200000000000000,
    "costOf_user_1": 0, "mintsLeft_user": 10, "mintedBy_user": 0, "balanceOf_user": 0,
    "freePct": 19.0,
    "firstMintInWindowBlock": 133684157,
    "firstMintInWindowWib": "2026-11-15 13:02 WIB",
    "firstMintAgeHoursInWindow": 23.63,
    "mintsIn25hWindow": 3,
    "source": "Boltbook b/alpha: tetternice.ai /p/_H83Fc6RBFBU (recheck 11:58 WIB, first detected 2026-11-11 02:38 monitor)",
    "lastReadWib": "2026-11-16 ~12:01 WIB",
    "runNote1201": "Run 1201: BARU dari Boltbook. totalSupply 296/1555 = 19,0% free, costOf(user,1)=0, mintsLeft(user)=10, mintOpen=1, Sourcify exact_match. TAPI umur >24 jam: walk getLogs (blxrbdn, chunk 5.000 blok) hanya menemukan 3 mint dalam ~25 jam terakhir (tertua 15 Nov 13:02 WIB, 23,6 jam) sementara 293 dari 296 mint mendahului jendela -> first mint PASTI >24 jam. Chunk 40-44 tidak ter-cover (egress flapping) tapi semuanya >24 jam. Dikoroborasi first-detection monitor 11 Nov 02:38 WIB. -> AGE-EXCLUDED, diam (belum pernah dilaporkan).",
}
s["runNote1201_1116"] = ("Run 1201 (12:01 WIB): re-read 36/36 OK blok 133868584 (87,8 dtk). 0 kandidat baru, 0 strong lead baru, "
 "0 early lead baru, 0 track-B dibuka/diblokir, 0 track-C lead/kandidat baru, 0 eksekusi/preview. "
 "Velocity: hanya SPARKS LOLOS (+27, 0,900/mnt vs prev 0,333 = 2,70x, >=20) tapi free%/umur/website masih UNVERIFIED -> tetap early lead, TIDAK preview/mint; "
 "MORFO +17 (1,06x, <20) GAGAL; Matrix +17 (17,0x TAPI <20) GAGAL; Bold Leonidas +4 GAGAL; sisanya 0/flat. "
 "BARU dicek run ini: PEPE track-C (freeMinted 204/500, hasMinted(user)=1 -> user SUDAH klaim, dicatat minted-by-user, DIAM); "
 "AGENTX (freeMinted 947/1111 = 85,2%, slot user terbuka, TAPI mintOpensAt 12 Nov 23:11 WIB ~85 jam -> AGE-EXCLUDED, diam); "
 "Glyphs of Xor (totalSupply 296/1555 = 19,0%, costOf(user,1)=0, TAPI first mint >24 jam via walk getLogs -> AGE-EXCLUDED, diam). "
 "DRAGON free pool HABIS 888/888 terverifikasi on-chain (status tetap age-excluded-2026-11-14, tidak dilaporkan ulang). "
 "Track-B binanceai.fun TIDAK BERUBAH (launched=0, failed=1, refund). ALIEN + Agent Grove masih BELUM DIBUKA. "
 "Boltbook EN 200 (45.307 byte) / ZH 200 (45.299 byte): 13/12 alamat, 3-4 'baru' (1 kontrak riil = XOR; 3 sisanya tx hash). "
 "Sweep EN+ZH: hanya proyek lama (Agentic Gangster, RIGBYPASS, MOLT AGENT, AGENT MAO, AGENT COSMOS, JINCHAN, Xuanwu). "
 "Odaily newsflash 12:2x WIB: 0 kata 'agent'. Scan leg FAST-FAIL (Ankr 401, 2,84 dtk); watermark TETAP 132512564 (head 133868883, gap 1.356.319). "
 "Sourcify 10 terbaru: 0 S1/S2 (7 retry via curl OK). Bridge 116/116 sudah di snapshot, 0 baru. Verdict akhir: DIAM (tidak ada laporan chat).")
s["last_run_note"] = ("Run 1201: DIAM - 0 kandidat/strong/early/track-B/track-C baru. SPARKS velocity lolos tapi kaki lain unverified. "
 "PEPE: user sudah klaim (minted-by-user). AGENTX + Glyphs of Xor: age-excluded. DRAGON free habis (sudah age-excluded). Ankr 401 berlanjut.")
json.dump(s, open(BASE + "onchain-snapshot.json", "w"), indent=1)
print("contracts now:", len(s["contracts"]), "| track_c now:", len(s.get("track_c", {})))
print("UPDATE3 DONE")
