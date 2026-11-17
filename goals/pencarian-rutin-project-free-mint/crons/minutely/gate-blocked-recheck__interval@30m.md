---
id: gate-blocked-recheck
title: Gate-blocked strong-lead recheck
enabled: true
owner: goal:pencarian-rutin-project-free-mint
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-06T19:01:04
  every: 30m
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
AMENDMENT 2026-11-11 ~09:18 WIB (user tap 'Ya, strong lead saja (25% jadi 70%)'): ambang STRONG LEAD berubah dari ≥25% menjadi >70% kuota gratis yang diklaim — hanya tier strong lead; ambang kandidat track-A (50%), track-C, dan guard tracked-wallet (>25%) TIDAK berubah. Tidak ada perubahan lain pada gate, guard, atau otorisasi eksekusi.

AMENDMENT 2026-11-10 ~19:36 WIB (user: 'Filter free bacot ke waktu deploy kurang dari 24 jam'): ambang umur berubah ≤48 jam → <24 jam; deadline recheck kini 24 jam dari first-mint terverifikasi. Tidak ada perubahan lain.

GATE-BLOCKED STRONG-LEAD RECHECK (dibuat 2026-11-06 atas perintah user "lakukan saja yang menurutmu terbaik" — usulan perbaikan #4). READ-ONLY + lapor saja: TIDAK PERNAH preview/mint/approve/swap/sign/tx. Eksekusi tetap wewenang job pencarian rutin 30-menit / parent di bawah guard yang berlaku.

Konteks: strong lead yang gate websitenya gagal sering mati umur 24 jam sebelum situsnya sempat muncul. Job ini memberi satu kesempatan terakhir: re-check gate singkat ~2 jam sebelum deadline umur.

TIAP RUN (30 menit): baca ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json, cari entri contracts berstatus strong-lead-gate-blocked-* (umur <24 jam, free >70%, slot terbuka). Untuk tiap entri, hitung deadline 24 jam dari first-mint terverifikasi (bila first-mint tidak tercatat, pakai verifiedAt/launched yang tercatat; bila tidak ada patokan waktu sama sekali, lewati).
- Bila deadline TIDAK dalam 2 jam ke depan: DIAM untuk item itu.
- Bila deadline dalam 2 jam ke depan DAN belum pernah di-recheck (cek state file ~/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/gate-recheck-state.json, kunci alamat lower): jalankan SATU re-check gate singkat metode A–N (pencarian alamat mentah; Boltbook; Sourcify source/metadata; pola same-family; contractURI/tokenURI; grep ABI; site: filters; BscScan token-info via live browser read-only HANYA bila metode lain belum menemukan — tanpa login). Catat hasil di state file (alamat -> rechecked_at + website atau null) APAPUN hasilnya, supaya tiap kontrak hanya di-recheck SEKALI.
- Bila website TERVERIFIKASI (situs mencetak kontrak persis): LAPORKAN SEKALI ke chat utama: nama proyek + kontrak + URL website + bukti, dan bahwa item kini lolos gate sehingga run pencarian rutin berikut bisa memprosesnya di bawah guard biasa. Jangan eksekusi di job ini.
- Bila website tetap tidak ditemukan: catat di state file + DIAM (tidak ada laporan gagal kedua).
- Bila tidak ada item dalam jendela 2 jam: DIAM.

Contoh item saat dibuat: Quantumfarm 0xA6Cf213F21C68b87f03Aa7d2a005e78F651eE010 (deadline 2026-11-06 21:00:37 WIB, jendela re-check buka ~19:00); StarAgent (deadline ~2026-11-06 21:26 WIB); Driftnauts 0x6a926234d3767f2eeb3db12c1b4c9e2912c5589b (deadline 2026-11-07 14:48:12 WIB). Observasi run masuk ke log harian ~/memory/YYYY-MM-DD.md. Jangan menulis snapshot/seen/state job lain.
