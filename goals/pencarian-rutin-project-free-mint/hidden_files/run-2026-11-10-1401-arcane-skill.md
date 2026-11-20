<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arcane Stones — Mint the Box. Reveal the Stone.</title>
<meta name="description" content="Arcane Stones: a free mystery-box mint on BNB Chain. Mint a sealed box, reveal the stone inside.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0a0812;
    background-image:
      radial-gradient(900px 500px at 50% -10%, rgba(124, 92, 255, .22), transparent 60%),
      radial-gradient(700px 420px at 85% 110%, rgba(245, 197, 66, .10), transparent 60%);
    color: #ece7f8;
    font-family: 'Inter', system-ui, sans-serif;
    padding: 0 20px 72px;
  }
  a { text-decoration: none; }
  .nav { max-width: 1020px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 22px 0; flex-wrap: wrap; gap: 12px; }
  .nav .logo { font-family: 'Press Start 2P', monospace; font-size: 13px; color: #f5c542; letter-spacing: 1px; }
  .nav .links a { color: #a99cc9; font-size: 14px; font-weight: 600; margin-left: 22px; }
  .nav .links a.active, .nav .links a:hover { color: #f5c542; }
  .wrap { max-width: 1020px; margin: 0 auto; text-align: center; }
  h1 {
    font-family: 'Press Start 2P', monospace;
    font-size: clamp(26px, 5vw, 44px);
    line-height: 1.5;
    margin-top: 44px;
    background: linear-gradient(180deg, #ffe9a3, #f5c542 55%, #c98f1b);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 42px rgba(245, 197, 66, .25);
  }
  .tagline { margin-top: 20px; font-size: 17px; color: #b9aede; line-height: 1.8; }
  .tagline b { color: #fff; }
  .hero { margin: 42px auto 0; max-width: 680px; }
  .hero img { width: 100%; border-radius: 20px; border: 1px solid rgba(255,255,255,.10); box-shadow: 0 24px 70px rgba(0,0,0,.55), 0 0 60px rgba(124,92,255,.18); }
  .caption { margin-top: 14px; font-size: 13px; letter-spacing: .14em; color: #8f83b5; text-transform: uppercase; }
  .mint-panel { margin: 44px auto 0; max-width: 680px; background: rgba(255,255,255,.035); border: 1px solid rgba(245,197,66,.35); border-radius: 20px; padding: 30px 26px; box-shadow: 0 0 60px rgba(245,197,66,.10); }
  .mint-panel h2 { font-family: 'Press Start 2P', monospace; font-size: 15px; color: #fff; letter-spacing: 1px; }
  .mint-panel .mint-sub { margin-top: 12px; font-size: 14px; color: #b9aede; line-height: 1.7; }
  .progress { margin-top: 22px; height: 12px; background: rgba(255,255,255,.08); border-radius: 999px; overflow: hidden; }
  .progress .fill { height: 100%; width: 0%; background: linear-gradient(90deg, #ffe9a3, #f5c542); border-radius: 999px; }
  .progress-label { display: flex; justify-content: space-between; margin-top: 10px; font-size: 13px; font-weight: 700; color: #a99cc9; }
  .progress-label b { color: #f5c542; }
  .mint-facts { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 22px; }
  .mint-facts span { font-size: 12px; font-weight: 700; padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.04); color: #ece7f8; }
  .mint-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 26px; }
  .mint-actions button { font-family: 'Inter', system-ui, sans-serif; font-size: 15px; font-weight: 800; padding: 15px 30px; border-radius: 999px; cursor: pointer; border: none; }
  .mint-actions .primary { background: linear-gradient(180deg, #ffe9a3, #f5c542); color: #0b0714; }
  .mint-actions .ghost { background: rgba(255,255,255,.06); color: #ece7f8; border: 1px solid rgba(255,255,255,.16); }
  .mint-actions button:disabled { opacity: .5; cursor: default; }
  .mint-note { margin-top: 18px; font-size: 12px; color: #8f83b5; line-height: 1.7; }
  .prompt { position: fixed; inset: 0; background: #0a0812; background-image: radial-gradient(900px 500px at 50% -10%, rgba(124, 92, 255, .22), transparent 60%), radial-gradient(700px 420px at 85% 110%, rgba(245, 197, 66, .10), transparent 60%); z-index: 100; display: none; overflow-y: auto; padding: 20px 20px 72px; }
  .prompt.open { display: block; }
  .prompt .inner { max-width: 560px; margin: 0 auto; text-align: center; }
  .prompt .back { display: inline-block; margin-top: 18px; font-size: 14px; font-weight: 700; color: #a99cc9; background: none; border: none; cursor: pointer; padding: 10px 14px; }
  .prompt .back:hover { color: #f5c542; }
  .prompt img { width: 220px; border-radius: 18px; margin-top: 26px; border: 1px solid rgba(255,255,255,.10); }
  .prompt h2 { font-family: 'Press Start 2P', monospace; font-size: 17px; color: #fff; margin-top: 26px; letter-spacing: 1px; }
  .prompt .rows { margin-top: 26px; text-align: left; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); border-radius: 16px; overflow: hidden; }
  .prompt .row { display: flex; justify-content: space-between; gap: 16px; padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,.06); font-size: 14px; }
  .prompt .row:last-child { border-bottom: none; }
  .prompt .row span { color: #a99cc9; }
  .prompt .row b { color: #fff; }
  .prompt .row b.gold { color: #f5c542; }
  .prompt .confirm { margin-top: 26px; width: 100%; font-family: 'Inter', system-ui, sans-serif; font-size: 16px; font-weight: 800; padding: 16px; border-radius: 999px; border: none; background: linear-gradient(180deg, #ffe9a3, #f5c542); color: #0b0714; cursor: pointer; }
  .prompt .confirm:disabled { opacity: .5; cursor: default; }
  .prompt .note { margin-top: 16px; font-size: 12px; color: #8f83b5; line-height: 1.7; }
  .steps { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 52px; text-align: left; }
  .step { flex: 1 1 240px; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); border-radius: 18px; padding: 26px 22px; }
  .step .num { font-family: 'Press Start 2P', monospace; font-size: 15px; color: #f5c542; }
  .step h3 { font-size: 16px; margin: 16px 0 10px; color: #fff; }
  .step p { font-size: 14px; line-height: 1.75; color: #b9aede; }
  .specs { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 52px; }
  .spec { flex: 1 1 180px; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 20px 14px; }
  .spec .label { font-size: 11px; letter-spacing: .16em; color: #8f83b5; text-transform: uppercase; }
  .spec .value { font-size: 20px; font-weight: 800; color: #f5c542; margin-top: 10px; }
  .stones { margin: 52px auto 0; max-width: 680px; }
  .stones-row { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }
  .stones-row img { width: 200px; max-width: 30%; border-radius: 16px; border: 1px solid rgba(255,255,255,.10); box-shadow: 0 24px 70px rgba(0,0,0,.55), 0 0 60px rgba(245,197,66,.12); opacity: 0; animation: stoneIn .8s ease forwards, stoneFloat 3.5s ease-in-out infinite; }
  .stones-row img:nth-child(1) { animation-delay: 0s, .8s; }
  .stones-row img:nth-child(2) { animation-delay: .35s, 1.15s; }
  .stones-row img:nth-child(3) { animation-delay: .7s, 1.5s; }
  @keyframes stoneIn { from { opacity: 0; transform: translateY(24px) scale(.94); } to { opacity: 1; transform: translateY(0) scale(1); } }
  @keyframes stoneFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
  .chips { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 22px; }
  .chip { font-size: 12px; font-weight: 700; padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.04); }
  .chip.common { color: #c9c9c9; }
  .chip.rare { color: #b388ff; border-color: rgba(179,136,255,.4); }
  .chip.epic { color: #d8a7ff; border-color: rgba(216,167,255,.4); }
  .chip.legendary { color: #f5c542; border-color: rgba(245,197,66,.45); }
  .soon { display: inline-block; margin-top: 56px; font-family: 'Press Start 2P', monospace; font-size: 12px; color: #0b0714; background: linear-gradient(180deg, #ffe9a3, #f5c542); padding: 14px 22px; border-radius: 999px; letter-spacing: 1px; }
  .foot { margin-top: 22px; font-size: 13px; color: #6f648f; line-height: 1.9; }
</style>
</head>
<body>
  <div class="nav">
    <a class="logo" href="index.html">ARCANE STONES</a>
    <div class="links">
      <a href="index.html" class="active">Mint</a>
      <a href="market.html">Market</a>
      <a href="mystones.html">My Stones</a>
      <a href="collection.html">Collection</a>
      <a href="faq.html">FAQ</a>
    </div>
  </div>

  <div class="wrap">
    <h1>ARCANE STONES</h1>
    <p class="tagline"><b>Mint the box. Reveal the stone.</b><br>A free mystery-box mint on BNB Chain.</p>

    <div class="hero">
      <img src="box.webp" alt="The sealed Arcane Stones mystery box">
      <p class="caption">Every mint starts sealed — what's inside is revealed after sold out.</p>
    </div>

    <div class="mint-panel">
      <h2>MINT YOUR BOX</h2>
      <p class="mint-sub">One box per Agent ID. Free mint — you only pay gas. The stone inside stays hidden until the reveal.</p>
      <div class="progress"><div class="fill" id="mintFill"></div></div>
      <div class="progress-label"><span><b id="mintCount">0</b> / 4,111 minted</span><span id="mintPct">0%</span></div>
      <div class="mint-facts">
        <span>Price: FREE (gas only)</span>
        <span>Limit: 1 per Agent ID</span>
        <span>Chain: BSC</span>
      </div>
      <div class="mint-actions">
        <button class="ghost" id="connectBtn">Connect Wallet</button>
        <button class="primary" id="mintBtn" disabled>Mint Box</button>
      </div>
      <p class="mint-note" id="mintStatus">Connect your wallet to mint. Free mint — gas only, 1 per Agent ID.</p>
    </div>

    <div class="steps">
      <div class="step">
        <div class="num">01</div>
        <h3>Mint a box</h3>
        <p>Free mint, gas only. One per Agent ID. First come, first served — no phases, no allowlist stages.</p>
      </div>
      <div class="step">
        <div class="num">02</div>
        <h3>Wait for reveal</h3>
        <p>Boxes stay sealed until the mint sells out. Then you open your own box.</p>
      </div>
      <div class="step">
        <div class="num">03</div>
        <h3>Reveal your stone</h3>
        <p>Plain Stone, Geode, Rune Stone, or Meteorite. Rarity stays hidden until the reveal.</p>
      </div>
    </div>

    <div class="specs">
      <div class="spec"><div class="label">Supply</div><div class="value">4,111</div></div>
      <div class="spec"><div class="label">Price</div><div class="value">Free</div></div>
      <div class="spec"><div class="label">Limit</div><div class="value">1 / Agent ID</div></div>
      <div class="spec"><div class="label">Chain</div><div class="value">BSC</div></div>
    </div>

    <div class="stones">
      <div class="stones-row">
        <img src="stone-geode.webp" alt="Geode">
        <img src="stone-rune.webp" alt="Rune Stone">
        <img src="stone-meteorite.webp" alt="Meteorite">
      </div>
      <p class="caption">What will your box hold?</p>
      <div class="chips">
        <span class="chip common">Common · Plain Stone · 60%</span>
        <span class="chip rare">Rare · Geode · 25%</span>
        <span class="chip epic">Epic · Rune Stone · 10%</span>
        <span class="chip legendary">Legendary · Meteorite · 5%</span>
      </div>
    </div>

    <div class="soon" id="soonBanner">MINT IS LIVE</div>
    <p class="foot">Arcane Stones is a free mint. No presale, no team allocation.<br><span id="footContracts">Contracts will be shown here once deployed.</span></p>
  </div>

  <div class="prompt" id="mintPrompt">
    <div class="inner">
      <button class="back" onclick="document.getElementById('mintPrompt').classList.remove('open')">← Back</button>
      <img src="box.webp" alt="Sealed box">
      <h2>MINT 1 SEALED BOX</h2>
      <div class="rows">
        <div class="row"><span>You mint</span><b>1 × Sealed Box</b></div>
        <div class="row"><span>Price</span><b class="gold">FREE</b></div>
        <div class="row"><span>Gas</span><b>~0.00003 BNB</b></div>
        <div class="row"><span>Limit</span><b>1 per Agent ID</b></div>
        <div class="row"><span>Chain</span><b>BSC</b></div>
        <div class="row"><span>Reveal</span><b>After sold out</b></div>
      </div>
      <button class="confirm" id="confirmMintBtn">Confirm Mint</button>
      <p class="note" id="mintPromptStatus">Your wallet will ask you to confirm the mint. Free — gas only.</p>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/ethers@6.13.4/dist/ethers.umd.min.js"></script>
  <script src="config.js"></script>
  <script>
    var wallet = null; // { address, provider, signer }

    function setStatus(msg) {
      document.getElementById('mintStatus').textContent = msg;
    }
    function setPromptStatus(msg) {
      document.getElementById('mintPromptStatus').textContent = msg;
    }

    async function refreshProgress() {
      try {
        if (!isLive()) return;
        var total = await readCall(function (p) { return nftRead(p).totalSupply(); });
        var n = Number(total);
        document.getElementById('mintCount').textContent = n.toLocaleString('en-US');
        document.getElementById('mintPct').textContent = Math.floor(n / 4111 * 100) + '%';
        document.getElementById('mintFill').style.width = (n / 4111 * 100) + '%';
      } catch (e) { /* leave the 0 state; retry on next load */ }
    }

    // Mint is LIVE now — launched early 2026-11-10 ~13:40 WIB at Zaffi's
    // call (the contract was already minting before 07:00 UTC).
    var MINT_OPEN_AT = 0;
    function mintOpen() { return Date.now() >= MINT_OPEN_AT; }
    function fmtLeft(ms) {
      var s = Math.max(0, Math.floor(ms / 1000));
      var h = String(Math.floor(s / 3600)).padStart(2, '0');
      var m = String(Math.floor(s % 3600 / 60)).padStart(2, '0');
      var sec = String(s % 60).padStart(2, '0');
      return h + ':' + m + ':' + sec;
    }
    function tickCountdown() {
      var btn = document.getElementById('mintBtn');
      var banner = document.getElementById('soonBanner');
      if (mintOpen()) {
        btn.disabled = false;
        banner.textContent = 'MINT IS LIVE';
        return;
      }
      btn.disabled = true;
      banner.textContent = 'MINT OPENS 07:00 UTC';
      if (!wallet) setStatus('Mint opens in ' + fmtLeft(MINT_OPEN_AT - Date.now()) + ' (07:00 UTC).');
    }
    tickCountdown();
    setInterval(tickCountdown, 1000);

    async function connect() {
      if (typeof ethers === 'undefined') { setStatus('Wallet library failed to load. Check your connection and refresh.'); return null; }
      try {
        wallet = await connectWallet();
        document.getElementById('connectBtn').textContent = shortAddr(wallet.address);
        setStatus('Connected: ' + shortAddr(wallet.address) + (mintOpen() ? ' — ready to mint.' : ' — mint opens 07:00 UTC.'));
        return wallet;
      } catch (e) {
        setStatus(e.message || 'Could not connect wallet.');
        return null;
      }
    }

    document.getElementById('connectBtn').addEventListener('click', connect);

    document.getElementById('mintBtn').addEventListener('click', function () {
      if (!mintOpen()) { setStatus('Mint opens in ' + fmtLeft(MINT_OPEN_AT - Date.now()) + ' (07:00 UTC).'); return; }
      document.getElementById('mintPrompt').classList.add('open');
      window.scrollTo(0, 0);
    });

    document.getElementById('confirmMintBtn').addEventListener('click', async function () {
      var btn = document.getElementById('confirmMintBtn');
      try {
        if (typeof ethers === 'undefined') { setPromptStatus('Wallet library failed to load. Check your connection and refresh.'); return; }
        if (!isLive()) { setPromptStatus('Contracts are being deployed — please try again in a moment.'); return; }
        if (!mintOpen()) { setPromptStatus('Mint opens 07:00 UTC.'); return; }
        if (!wallet) {
          wallet = await connect();
          if (!wallet) { setPromptStatus('Connect your wallet first.'); return; }
        }
        btn.disabled = true;
        setPromptStatus('Checking your Agent ID...');
        var handle = await readCall(function (p) { return registryRead(p).handleOf(wallet.address); });
        if (!handle) { setPromptStatus('This wallet has no Agent ID. Minting needs an Agent ID.'); btn.disabled = false; return; }
        var agentId = ethers.keccak256(ethers.toUtf8Bytes(handle));
        var already = await readCall(function (p) { return nftRead(p).mintedByAgentId(agentId); });
        if (already) { setPromptStatus('This Agent ID already minted its box.'); btn.disabled = false; return; }
        setPromptStatus('Confirm the mint in your wallet...');
        var nft = nftWrite(wallet.signer);
        var tx = await nft.mint(); // not payable: no value attached
        setPromptStatus('Minting... waiting for confirmation.');
        var receipt = await tx.wait();
        var tokenId = null;
        try {
          for (var i = 0; i < receipt.logs.length; i++) {
            var parsed = nft.interface.parseLog(receipt.logs[i]);
            if (parsed && parsed.name === 'Minted') { tokenId = parsed.args.tokenId.toString(); break; }
          }
        } catch (e) { /* fall through to the index lookup below */ }
        if (tokenId === null) {
          var bal = await nftRead(wallet.provider).balanceOf(wallet.address);
          tokenId = (await nftRead(wallet.provider).tokenOfOwnerByIndex(wallet.address, bal - 1n)).toString();
        }
        setPromptStatus('You minted Sealed Box #' + tokenId + '! See it on My Stones.');
        setStatus('You minted Sealed Box #' + tokenId + '.');
        refreshProgress();
      } catch (e) {
        var msg = (e && e.reason) || (e && e.shortMessage) || (e && e.message) || 'Mint failed.';
        setPromptStatus(msg);
      } finally {
        btn.disabled = false;
      }
    });

    // Footer: show the two contract addresses (plain addresses, no names) once filled.
    if (isLive()) {
      document.getElementById('footContracts').textContent = 'NFT: ' + NFT_ADDRESS + '  ·  Market: ' + MARKET_ADDRESS;
    }
    refreshProgress();
  </script>
</body>
</html>
