# Gate methods (I)-(N) + (F)-browser test results — 2026-11-03
Tap user "Ya, tambahkan metode baru dan uji ke item gate-blocked" + "Metode gate f ganti dengan browser".
Badan cron search/hot-leg/scan sudah dipatch + diverifikasi byte-identical + enabled (~13:00 WIB).

## Top 3 strong-lead-gate-blocked yang diuji
- Animora 0x150699b44B36b542B9F954272bDD0aC3fDD9519b (owner 0xee8d9edfeecfc175a76387a25581c2dc9f5f85f5)
- Deepvane 0xDd682169A6699eA7feF7E6E15C727Cf970C98d97 (owner 0xfd6f24bc75d0f142134099654949ab789332f43a)
- Sentrix 0xb7dce0412BB89dE075413855875D1DB31AC89E8f (owner 0x838fb372a0bf2c42cfad885a69f474f5cfb8cfed)

## Hasil per metode
- (I) tokenURI: ketiga tokenURI = base64 JSON on-chain, keys name/description/image/attributes saja; tidak ada external_url/website/URL. NIHIL.
- (J) ABI site-function grep (Sourcify): ketiga ABI hanya punya contractURI/tokenURI; tidak ada fungsi website/siteURL/domain/external. NIHIL.
- (K) GitHub search-index by exact address: ketiga alamat = nihil (hanya noise tidak terkait).
- (M) site: filters (vercel.app/pages.dev/deed.page/surge.sh + nama/simbol): nihil (noise: Framer template, MintPage, SentX Hedera).
- (M) deployer-address web search (owner address + nama proyek): nihil — Animora → produk dental hewan peliharaan + komik; Deepvane → pompa Honda + token lain; Sentrix → trademark/perusahaan keamanan/care/OpenClaw — tidak ada yang mencetak kontrak BSC proyek.
- (N) registry Agent ID tokenURI + Boltbook author → X bio → site hop: TIDAK DAPAT DIUJI untuk ketiga item ini — entri snapshot tidak mencatat identitas agent (tidak ada field agent/agentId/author/website), jadi tidak ada titik awal hop yang terverifikasi. (N) tetap tersedia untuk item mendatang yang identitas agent/author-nya diketahui.
- (L) BscScan token-info via live browser: SELESAI 2026-11-03 ~12:49 WIB (task 12:44–12:49, sempat terhalang Cloudflare lalu lolos setelah environment diganti; read-only, tanpa login/wallet). Hasil: KETIGA kontrak TIDAK menampilkan tautan website/sosial apa pun — tab Info hanya menampilkan "Click here to update the token information" (proyek belum pernah mendaftarkan info). NIHIL untuk (L). Angka overview saat cek: Animora 224 token/212 holder, Deepvane 225/200, Sentrix 235/232 (totalSupply saat cek, bukan freeClaimed — konsisten dengan drift dari snapshot 12:01).
- Sweep penuh (tokenURI/ABI ke SEMUA item gate-blocked di snapshot): exec proc_9be91eb5b288 selesai 2026-11-03 ~13:0x WIB (14 menit). Inventaris: 32 item strong-lead-gate-blocked. (J) ABI grep: Sourcify TIDAK TERBACA untuk ke-32 item (gagal baca metode via urllib, BUKAN vonis tidak ada fungsi situs). (I) tokenURI putaran 1: 16 terbaca → semua nihil (keys name/description/image/attributes, external_url None, urls []); 16 tidak terbaca (RPC).
- (I) tokenURI putaran ulang (proc_7093b83a48c1, selesai ~13:15 WIB, 20 menit, 5× retry per ID 1/0/2): 3 tambahan terbaca → nihil (Nimaluo, Crtdroid, Glasscore). Total (I): 19/32 nihil, 13 MASIH tidak terbaca (Malabao, Kitsunaru, Nightsable, Krakenbo, Fangcount, Jiayoupanda, AZET, Plutoko, Deco Agent, Opera Agent, Peony Agent, Yunjin Agent, Kelp Agent) — gagal baca RPC/antarmuka untuk ID 0-2, BUKAN bukti ada/tidak ada situs. Catatan: Glasscore tetap dibatalkan user, Plutoko tetap sold-out — status keduanya tidak berubah apapun hasil (I).
- KESIMPULAN AKHIR UJI: tidak ada website ditemukan lewat metode baru untuk item manapun yang teruji; TIDAK ADA perubahan status gate. (J) untuk 29 item di luar 3 utama tetap belum teruji (gagal baca Sourcify putaran sweep); (K)/(M)/(N)/(L) diuji penuh hanya untuk 3 utama.

## Kesimpulan sementara (top 3)
Tidak ada metode baru yang menemukan website untuk Animora/Deepvane/Sentrix. Status gate mereka TIDAK BERUBAH (tetap gate-blocked) sampai (L) dan sweep masuk. Laporan akhir ke user menyusul setelah keduanya masuk.
