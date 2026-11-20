---
id: agio-free-mint-watch
title: Pantau free mint AGIO (read-only)
enabled: true
owner: goal:agio-free-mint-watch
mode: task
schedule:
  kind: interval
  timezone: Asia/Jakarta
  at: 2026-11-03T20:32:06
  every: 1h
delivery:
  - chat_id: dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2
metadata:
  tags: [cron:automatic-interval-anchor]
  originating_chat_context_json: '{"chat_id":"dddf9010-ba6e-4f1b-9b2a-01f53f85e4e2","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"8be79870-67e5-4541-845f-63fb93d3f6d3"}'
  presentation_locale: id-ID
---
Pantau free mint AGIO (agio.family) — READ-ONLY, DIAM kecuali launch dibuka atau status free mint berubah. Perintah user 2026-11-03 ~19:29 WIB ("Pantau free mint ini langsung eksekusi selama kontrak aman AGIO").

KONTEKS TERVERIFIKASI 2026-11-03 ~19:35 WIB (jangan pakai angka lama, baca segar tiap run):
- Token AGIO 0xD952350046a229e96E09E1B255d3FE4FA4E458E6 (name Agio, symbol AGIO, decimals 18; catatan skill.md soal metadata JASD sudah basi — metadata saat ini AGIO).
- Mint 0xeF98407D55b3506275732b94c300866a16D6A3BB (Sourcify exact_match). Free mint = freeMint(bytes32 task, uint256 agentTokenId, bytes signature) — BUTUH signature backend AGIO (quotaSigner) yang hanya terbit setelah X tasks terverifikasi backend; TANPA signature, free mint tidak bisa dieksekusi on-chain apa pun.
- User Agent ID tokenId 107187496765866644729837695198686237165740365523485558112864918211974996443404; freeMintDone false untuk kedua task (REPOST_COMMENT 0x2737e8378ddc9f403160ff120e70bd9e1a5d6183096d6c182f29e53a49338388, AVATAR 0x4270bfca07279b2d8717bab7cefb7943a69c398f45151b67b5ad61e75c144e59), quotaOf 10, mintedCount 0.
- Audit 2026-11-03: mint hasResult=false (TIDAK ADA HASIL, bukan lolos); token hasResult=true, riskLevel 2, riskAlert null, 0 hit RISK.

TIAP RUN (baca-saja, tanpa login, tanpa session token AGIO, tanpa X task, tanpa preview/mint/approve/sign):
1. Baca https://agio.family/api/v1/launch/campaign (available, paused, opened, totalMinted, totalPaid) + on-chain paused(), opened(), totalMinted() mint + freeMintDone(userAgentId, kedua task).
2. Simpan state ke ~/workspace/agio-watch/state.json (buat folder bila perlu).
3. DIAM bila tidak ada perubahan material. LAPORKAN SEKALI ke chat utama bila: (a) opened=true DAN paused=false (launch resmi dibuka) — sertakan totalMinted + status freeMintDone segar + pengingat bahwa eksekusi tetap butuh signature backend + keputusan audit mint (hasResult=false) dari user; atau (b) freeMintDone berubah true untuk salah satu task; atau (c) totalMinted mulai bergerak dari 0 (tanda launch hidup meski flag API belum berubah).
4. JANGAN PERNAH dari job ini: preview, mint, eksekusi, approve, sign, connect wallet, login, menangani session token AGIO, mengerjakan X tasks (itu akun X user sendiri), atau mengklaim free mint bisa dieksekusi tanpa signature. Eksekusi apa pun tetap butuh perintah/konfirmasi user terpisah dengan audit segar + preview bersih + cost 0 — monitor ini TIDAK memberi otorisasi eksekusi.

JADWAL: tiap 1 jam. Bila file state tidak bisa dibaca, jangan menimpa dari kosong — catat kegagalan di log run dan lanjut run berikutnya.
