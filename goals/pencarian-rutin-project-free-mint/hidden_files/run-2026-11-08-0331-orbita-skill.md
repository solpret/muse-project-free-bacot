<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ORBITA — Share Sale on BNB Chain</title>
<meta name="description" content="ORBITA on BNB Chain: a fixed pool of 1,000 shares, 1 share = 1,000,000 ORBITA. Agent ID holders get their first share free, then 0.001 BNB per share; everyone else 0.0015 BNB per share. Unsold shares are never minted.">
<style>
  :root { --bg:#050914; --cy:#57b6ff; --vi:#ffd166; --ink:#eaf3ff; --card:#0b1526; --line:#274268; --mut:#9db4d4; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    background-image:
      radial-gradient(rgba(255,255,255,.85) 1px, transparent 1.6px),
      radial-gradient(rgba(159,216,255,.5) 1px, transparent 1.6px),
      radial-gradient(rgba(255,209,102,.35) 1.5px, transparent 2.2px);
    background-size: 110px 110px, 170px 170px, 260px 260px;
    background-position: 0 0, 40px 60px, 90px 20px;
    color: var(--ink); min-height: 100vh;
    display: flex; align-items: flex-start; justify-content: center; padding: 24px 14px 40px;
  }
  .card {
    background: rgba(11,21,38,.94); border: 2px solid var(--line); border-radius: 24px;
    max-width: 460px; width: 100%; padding: 26px 24px; text-align: center;
    box-shadow: 0 18px 50px rgba(0,0,0,.55);
  }
  .coin { width: 118px; height: 118px; margin: 0 auto; display: block; border-radius: 50%; }
  h1 { font-size: 32px; margin: 12px 0 4px; letter-spacing: .14em; }
  h1 .g { color: var(--cy); }
  .sub { color: var(--mut); font-size: 13.5px; line-height: 1.6; }
  .sub b { color: var(--ink); }
  .stats { display: flex; gap: 8px; margin: 16px 0 4px; }
  .stat { flex: 1; background: rgba(255,255,255,.04); border: 1.5px solid var(--line); border-radius: 14px; padding: 9px 3px; }
  .stat b { display: block; font-size: 14.5px; color: var(--cy); word-break: break-all; }
  .stat b.gold { color: var(--vi); }
  .stat span { font-size: 9.5px; color: var(--mut); text-transform: uppercase; letter-spacing: .04em; }
  .section { border-top: 1.5px solid var(--line); margin-top: 18px; padding-top: 16px; text-align: left; }
  .section h2 { font-size: 16.5px; text-align: center; margin-bottom: 6px; }
  .section p.desc { font-size: 12.5px; color: var(--mut); text-align: center; line-height: 1.55; margin-bottom: 10px; }
  .kv { display: flex; justify-content: space-between; font-size: 13px; padding: 5px 2px; color: var(--mut); }
  .kv b { color: var(--ink); }
  .kv b.gold { color: var(--vi); }
  button {
    width: 100%; padding: 13px; font-size: 16px; font-weight: 800; cursor: pointer;
    background: linear-gradient(90deg, var(--cy), #2f7fd0); color: #04101f;
    border: none; border-radius: 15px;
  }
  button.alt { background: rgba(255,255,255,.07); color: var(--ink); border: 1.5px solid var(--line); }
  button:disabled { opacity: .45; cursor: not-allowed; }
  button:active:not(:disabled) { transform: translateY(1px); }
  .row { display: flex; gap: 8px; }
  .row input { flex: 1; min-width: 0; }
  input {
    width: 100%; padding: 12px; font-size: 16px; border-radius: 12px;
    border: 1.5px solid var(--line); background: rgba(255,255,255,.05); color: var(--ink);
  }
  .est { font-size: 12.5px; color: var(--mut); margin: 8px 2px 10px; line-height: 1.7; }
  .est b { color: var(--cy); }
  .est b.gold { color: var(--vi); }
  #status { margin-top: 14px; font-size: 13.5px; min-height: 20px; line-height: 1.55; word-break: break-word; }
  .links { margin-top: 14px; font-size: 12px; color: var(--mut); line-height: 1.9; }
  a { color: var(--cy); }
  .share { margin-top: 12px; }
</style>
</head>
<body>
<div class="card">
  <img class="coin" src="orbita.svg" alt="ORBITA — planet with an orbit ring">
  <h1><span class="g">ORBITA</span></h1>
  <p class="sub">A fixed-supply token sale on <b>BNB Chain</b>, sold in <b>shares</b>.<br>
  <b>1 share = 1,000,000 ORBITA</b> · only <b>1,000 shares</b> exist — unsold shares are <b>never minted</b>.<br>
  🪪 <b>Agent ID holders:</b> your <b>first share is FREE</b>, then <b>0.001 BNB</b> per share.<br>
  Everyone else: <b>0.0015 BNB</b> per share. Max <b>10 shares</b> per transaction, <b>20</b> per wallet.</p>

  <div class="stats">
    <div class="stat"><b id="sold">…</b><span>Shares sold / 1,000</span></div>
    <div class="stat"><b id="left">…</b><span>Shares left</span></div>
    <div class="stat"><b id="supply">…</b><span>ORBITA minted</span></div>
  </div>

  <div class="section">
    <button id="connectBtn">Connect Wallet</button>
  </div>

  <div class="section" id="walletPanel" style="display:none">
    <h2>🛰️ Your Wallet</h2>
    <div class="kv"><span>Address</span><b id="wAddr">–</b></div>
    <div class="kv"><span>Agent ID holder</span><b id="wAgent">–</b></div>
    <div class="kv"><span>Free share (Agent ID)</span><b id="wFree">–</b></div>
    <div class="kv"><span>Your shares</span><b id="wShares">–</b></div>
    <div class="kv"><span>Your ORBITA balance</span><b class="gold" id="wBal">–</b></div>
  </div>

  <div class="section">
    <h2>🚀 Mint Shares</h2>
    <p class="desc">Enter how many shares you want (1–10 per transaction). The price is read live from the contract — if you hold an Agent ID and your free share is unused, it is applied automatically. You pay exactly the quoted cost; any excess BNB sent is refunded by the contract. Sale proceeds are forwarded directly to the treasury by the contract itself.</p>
    <div class="row"><input id="sharesAmt" type="number" min="1" max="10" step="1" value="1" placeholder="Shares, e.g. 1"></div>
    <p class="est" id="quoteBox">Connect your wallet to see your live quote.</p>
    <button id="mintBtn" disabled>Mint Shares</button>
  </div>

  <div class="share">
    <button class="alt" id="shareBtn">Share on X</button>
  </div>

  <p id="status"></p>

  <p class="links">
    Contract: <span id="contractLink">–</span><br>
    Max supply 1,000,000,000 ORBITA = 1,000 shares × 1,000,000 · No owner, no admin — the contract is the sale<br>
    ✅ Contract is verified — read the source yourself:
    <a href="https://repo.sourcify.dev/56/0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709" target="_blank" rel="noopener">Sourcify</a><br>
    ORBITA is a fixed-supply token sold at a fixed price. Nothing on this page is a promise of profit or future value — please do your own research.
  </p>
</div>

<script src="https://cdn.jsdelivr.net/npm/ethers@6.13.4/dist/ethers.umd.min.js"></script>
<script>
  // === DEPLOYED CONTRACT ===
  const CONTRACT = "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709";
  // =========================
  const RPC = "https://bsc-dataseed1.binance.org";
  const MAX_SHARES = 1000n;
  const TOKENS_PER_SHARE = 1000000n;
  const ABI = [
    "function mint(uint256 shares) payable",
    "function quote(address buyer, uint256 shares) view returns (uint256 freeShares, uint256 costBnb)",
    "function sharesSold() view returns (uint256)",
    "function freeUsed(address) view returns (uint256)",
    "function mintedBy(address) view returns (uint256)",
    "function isAgent(address) view returns (bool)",
    "function balanceOf(address) view returns (uint256)",
    "function totalSupply() view returns (uint256)"
  ];
  const $ = (id) => document.getElementById(id);
  const status = (t) => { $("status").innerHTML = t; };
  const fmtTok = (v) => Number(ethers.formatUnits(v, 18)).toLocaleString("en-US", { maximumFractionDigits: 0 });
  const fmtBnb = (v) => ethers.formatUnits(v, 18);
  const short = (a) => a.slice(0, 6) + "…" + a.slice(-5);
  let account = null, provider = null;
  let lastSold = null, lastMintedBy = null;

  $("contractLink").innerHTML = '<a href="https://bscscan.com/address/' + CONTRACT + '" target="_blank" rel="noopener">' + short(CONTRACT) + "</a>";
  const readProvider = new ethers.JsonRpcProvider(RPC);
  const read = new ethers.Contract(CONTRACT, ABI, readProvider);

  function sharesInput() {
    const n = Math.floor(Number($("sharesAmt").value));
    if (!Number.isFinite(n) || n < 1) return 1;
    return Math.min(n, 10);
  }

  async function refresh() {
    try {
      const [sold, supply] = await Promise.all([read.sharesSold(), read.totalSupply()]);
      lastSold = sold;
      $("sold").textContent = sold.toLocaleString("en-US");
      $("left").textContent = (MAX_SHARES - sold).toLocaleString("en-US");
      $("supply").textContent = fmtTok(supply);
      if (account) {
        const [agent, freeU, mine, bal] = await Promise.all([
          read.isAgent(account), read.freeUsed(account), read.mintedBy(account), read.balanceOf(account)
        ]);
        lastMintedBy = mine;
        $("walletPanel").style.display = "block";
        $("wAddr").textContent = short(account);
        $("wAgent").textContent = agent ? "Yes 🪪" : "No";
        $("wFree").textContent = !agent ? "— (no Agent ID)" : (freeU > 0n ? "Already used" : "Available — 1 free share 🎁");
        $("wShares").textContent = mine.toLocaleString("en-US") + " / 20";
        $("wBal").textContent = fmtTok(bal) + " ORBITA";
        $("mintBtn").disabled = sold >= MAX_SHARES || mine >= 20n;
      }
      updateQuote();
    } catch (e) { /* RPC busy, ignore */ }
  }

  async function updateQuote() {
    if (!account) { $("quoteBox").innerHTML = "Connect your wallet to see your live quote."; return; }
    const n = sharesInput();
    try {
      const [freeShares, cost] = await read.quote(account, BigInt(n));
      const receive = BigInt(n) * TOKENS_PER_SHARE;
      let line = "You receive: <b>" + receive.toLocaleString("en-US") + " ORBITA</b> (" + n + " share" + (n > 1 ? "s" : "") + ")";
      if (freeShares > 0n) line += "<br>Free shares applied: <b class='gold'>" + freeShares.toString() + "</b>";
      line += "<br>Total cost: <b class='gold'>" + fmtBnb(cost) + " BNB</b>" + (cost === 0n ? " — free, just pay gas 🎉" : "");
      $("quoteBox").innerHTML = line;
    } catch (e) { $("quoteBox").textContent = "Could not fetch a quote right now — try again in a moment."; }
  }
  $("sharesAmt").addEventListener("input", updateQuote);

  $("connectBtn").onclick = async () => {
    if (!window.ethereum) { status("No wallet detected. Open this page from a wallet browser (Binance Wallet / MetaMask)."); return; }
    try {
      provider = new ethers.BrowserProvider(window.ethereum);
      const net = await provider.getNetwork();
      if (net.chainId !== 56n) {
        try {
          await window.ethereum.request({ method: "wallet_switchEthereumChain", params: [{ chainId: "0x38" }] });
        } catch (swErr) {
          await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [{ chainId: "0x38", chainName: "BNB Smart Chain", nativeCurrency: { name: "BNB", symbol: "BNB", decimals: 18 }, rpcUrls: ["https://bsc-dataseed1.binance.org"], blockExplorerUrls: ["https://bscscan.com"] }]
          });
        }
        provider = new ethers.BrowserProvider(window.ethereum);
      }
      const signer = await provider.getSigner();
      account = await signer.getAddress();
      $("connectBtn").textContent = "Connected: " + short(account);
      status("Connected: " + short(account));
      refresh();
    } catch (e) { status("Failed to connect wallet: " + (e.shortMessage || e.message)); }
  };

  if (window.ethereum && window.ethereum.on) {
    window.ethereum.on("accountsChanged", () => location.reload());
    window.ethereum.on("chainChanged", () => location.reload());
  }

  $("mintBtn").onclick = async () => {
    if (!provider || !account) return;
    const n = sharesInput();
    if (lastSold !== null && lastSold + BigInt(n) > MAX_SHARES) { status("Not enough shares left — only " + (MAX_SHARES - lastSold).toString() + " remaining."); return; }
    if (lastMintedBy !== null && lastMintedBy + BigInt(n) > 20n) { status("Wallet limit: you can hold at most 20 shares. You already have " + lastMintedBy.toString() + "."); return; }
    $("mintBtn").disabled = true;
    try {
      // Fresh quote right before sending — the page pays exactly the contract's quoted cost.
      const [freeShares, cost] = await read.quote(account, BigInt(n));
      const c = new ethers.Contract(CONTRACT, ABI, await provider.getSigner());
      status("Waiting for your signature in the wallet… (" + n + " share" + (n > 1 ? "s" : "") + ", cost " + fmtBnb(cost) + " BNB" + (freeShares > 0n ? ", incl. " + freeShares.toString() + " free" : "") + ")");
      const tx = await c.mint(BigInt(n), { value: cost });
      status('Transaction sent, waiting for confirmation… <a href="https://bscscan.com/tx/' + tx.hash + '" target="_blank" rel="noopener">view</a>');
      await tx.wait();
      status('✅ Mint successful! ' + (BigInt(n) * TOKENS_PER_SHARE).toLocaleString("en-US") + ' ORBITA are now in your wallet. <a href="https://bscscan.com/tx/' + tx.hash + '" target="_blank" rel="noopener">Transaction proof</a>');
      refresh();
    } catch (e) {
      status("Mint failed: " + (e.shortMessage || e.reason || e.message));
      $("mintBtn").disabled = false;
    }
  };

  $("shareBtn").onclick = () => {
    const text = "ORBITA is live on BNB Chain 🪐 Only 1,000 shares — 1 share = 1,000,000 ORBITA, and unsold shares are never minted. Agent ID holders: your first share is free 🎁";
    window.open("https://twitter.com/intent/tweet?text=" + encodeURIComponent(text), "_blank", "noopener");
  };

  refresh();
  setInterval(refresh, 30000);
</script>
</body>
</html>
