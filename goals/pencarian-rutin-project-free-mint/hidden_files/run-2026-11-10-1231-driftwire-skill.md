<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta http-equiv="Content-Security-Policy" content="connect-src 'self' data: https: wss:">
  <title>DRIFTWIRE · 5,555 courier agents on BNB Chain</title>
  <meta name="description" content="Sealed courier crates open into 5,555 pixel-built agents crossing Neo-Kowloon. Mint, crack open, earn $WIRE and trade at the Night Market.">
  <meta name="theme-color" content="#07080d">
  <meta property="og:type" content="website">
  <meta property="og:title" content="DRIFTWIRE · One last packet. Five thousand couriers.">
  <meta property="og:description" content="5,555 pixel cyberpunk courier agents on BNB Chain. Sealed crates, delayed reveal, $WIRE rewards and the Night Market.">
  <meta property="og:image" content="https://driftwire.pages.dev/og.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="DRIFTWIRE · One last packet. Five thousand couriers.">
  <meta name="twitter:description" content="Sealed courier crates from Neo-Kowloon. Crack open, earn $WIRE, trade at the Night Market.">
  <meta name="twitter:image" content="https://driftwire.pages.dev/og.jpg">
  <link rel="icon" href="./favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="./assets/favicon.png">
  <link rel="stylesheet" href="./styles.css">
</head>
<body>
  <div class="rain" aria-hidden="true"></div>
  <div class="scanlines" aria-hidden="true"></div>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="#top" aria-label="DRIFTWIRE home">
        <span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>
        <span>DRIFT<b>WIRE</b></span>
      </a>
      <nav aria-label="Primary">
        <a href="#mint" data-i18n="nav.mint">Mint</a>
        <a href="#couriers" data-i18n="nav.couriers">My Couriers</a>
        <a href="#tiers" data-i18n="nav.tiers">Tiers</a>
        <a href="#relay" data-i18n="nav.relay">The Relay</a>
        <a href="#wire" data-i18n="nav.wire">$WIRE</a>
        <a href="#market" data-i18n="nav.market">Night Market</a>
        <a href="#faq" data-i18n="nav.faq">FAQ</a>
      </nav>
      <div class="header-actions">
        <select id="langSel" aria-label="Language"></select>
        <button class="btn btn-signal btn-small" id="btnConnect" type="button" data-i18n="connect">Connect</button>
      </div>
    </div>
  </header>

  <main id="top">
    <section class="hero" aria-labelledby="heroTitle">
      <div class="hero-image-wrap" aria-hidden="true">
        <img src="./assets/hero.jpg" alt="" class="hero-image">
        <div class="hero-vignette"></div>
      </div>
      <div class="hero-grid-lines" aria-hidden="true"></div>
      <div class="wrap hero-inner">
        <div class="hero-copy">
          <p class="kicker" data-i18n="hero.kicker">Neo-Kowloon // relay frequency 2099</p>
          <h1 id="heroTitle" data-i18n="hero.title">One last packet. Five thousand couriers.</h1>
          <p class="hero-lede" data-i18n="hero.lede">The network went dark in one night. Rogue courier agents kept moving, each carrying one encrypted packet of the old internet.</p>
          <div class="hero-actions">
            <a class="btn btn-signal" href="#mint" data-i18n="hero.ctaMint">Mint a courier</a>
            <a class="btn btn-line" href="#tiers" data-i18n="hero.ctaTiers">Meet the six tiers</a>
          </div>
          <div class="hero-stats" aria-label="Collection facts">
            <div><strong>5,555</strong><span data-i18n="stats.supply">couriers</span></div>
            <div><strong>0.0015 BNB</strong><span data-i18n="stats.price">per crate</span></div>
            <div><strong>30</strong><span data-i18n="stats.models">riders</span></div>
            <div><strong>2,200</strong><span data-i18n="stats.free">free routes</span></div>
          </div>
        </div>
        <div class="hero-signal" aria-hidden="true">
          <div class="signal-ring"></div>
          <div class="signal-label">RELAY<br><b>2099</b></div>
          <span class="signal-coord">22°19′N<br>114°10′E</span>
        </div>
      </div>
      <div class="hero-fade"></div>
    </section>

    <section id="mint" class="section section-mint" aria-labelledby="mintTitle">
      <div class="wrap">
        <div class="section-heading split-heading">
          <div>
            <p class="eyebrow" data-i18n="mint.eyebrow">Relay intake</p>
            <h2 id="mintTitle" data-i18n="mint.title">Claim your courier</h2>
          </div>
          <div class="status-chip" id="mintStatus" data-i18n="mint.statusSoon">Mint opens soon</div>
        </div>

        <div class="mint-grid">
          <article class="panel mint-panel">
            <div class="relay-readout">
              <div>
                <span class="micro-label" data-i18n="mint.progress">Relay progress</span>
                <p><strong id="mintedCount">0</strong><span> / 5,555</span> <em data-i18n="mint.minted">minted</em></p>
              </div>
              <div class="live-dot"><i></i> LIVE FEED</div>
            </div>
            <div class="meter meter-large"><i id="mintMeter"></i></div>
            <p class="micro-copy" id="mintWalletNote" data-i18n="mint.walletNote">No wallet limit. Up to 20 crates per transaction.</p>
            <div class="quantity-row">
              <label for="mintQty" data-i18n="mint.quantity">Crates</label>
              <div class="quantity-control">
                <button type="button" id="qtyMinus" aria-label="Decrease quantity">−</button>
                <input id="mintQty" type="number" min="1" max="20" value="1" inputmode="numeric">
                <button type="button" id="qtyPlus" aria-label="Increase quantity">+</button>
                <button type="button" id="qtyMax" class="qty-max">MAX</button>
              </div>
              <div class="price-total">
                <span data-i18n="mint.total">Total</span>
                <strong id="mintCost">0.0015 BNB</strong>
              </div>
            </div>
            <button class="btn btn-signal btn-wide" id="btnMint" type="button" data-i18n="mint.buttonSoon">Mint opens soon</button>
            <div class="reward-strip">
              <span class="wire-glyph">W</span>
              <span id="nextReward" data-i18n="mint.nextReward">Next mint credits 10,000 $WIRE</span>
            </div>
            <p class="inline-feedback" id="mintFeedback" role="status"></p>
            <p class="referral-chip" id="refApplied" hidden></p>
          </article>

          <aside class="panel free-panel">
            <div class="panel-title">
              <span class="eyebrow" data-i18n="free.title">Free routes</span>
              <span class="signal-dot"></span>
            </div>
            <div class="free-route">
              <div class="route-head">
                <div>
                  <strong data-i18n="free.agent">Agent ID holders</strong>
                </div>
                <b id="agentFreeLeft">2,000 / 2,000</b>
              </div>
              <p data-i18n="free.agentDesc">2,000 free crates for Agent ID holders.</p>
              <div class="meter"><i id="agentFreeMeter"></i></div>
              <p class="route-state" id="agentState" data-i18n="free.connect">Connect a wallet to check your Agent ID.</p>
            </div>
            <div class="free-route">
              <div class="route-head">
                <div>
                  <strong data-i18n="free.x">Verified X accounts</strong>
                </div>
                <b id="xFreeLeft">200 / 200</b>
              </div>
              <p data-i18n="free.xDesc">200 free crates for verified X accounts.</p>
              <div class="meter meter-cyan"><i id="xFreeMeter"></i></div>
            </div>
            <p class="fine-print" data-i18n="free.rule">Maximum one free crate per wallet across both routes.</p>
            <a class="text-link" href="#xVerify" data-i18n="x.title">Verify your X account</a>
          </aside>
        </div>

        <article class="panel x-panel" id="xVerify">
          <div class="x-panel-copy">
            <p class="eyebrow">X / BLUE SIGNAL</p>
            <h3 data-i18n="x.title">Verify your X account</h3>
            <p data-i18n="x.desc">Publish the relay call from your own verified X account, then submit its URL.</p>
            <ol class="step-list">
              <li data-i18n="x.step1">Connect the wallet that will receive the courier.</li>
              <li data-i18n="x.step2">Post the message below from your verified X account.</li>
              <li data-i18n="x.step3">Paste the post URL, verify, then mint your free crate.</li>
            </ol>
          </div>
          <div class="x-panel-form">
            <textarea id="xTemplate" readonly aria-label="X post"></textarea>
            <div class="inline-actions">
              <button class="btn btn-line btn-small" id="btnCopyX" type="button" data-i18n="x.copy">Copy post</button>
              <a class="btn btn-line btn-small" id="btnOpenX" href="https://x.com/intent/post" target="_blank" rel="noopener" data-i18n="x.open">Open X</a>
            </div>
            <input id="xUrl" type="url" autocomplete="off" data-i18n-placeholder="x.urlPlaceholder" placeholder="https://x.com/you/status/…">
            <div id="turnstileBox" class="turnstile-box"></div>
            <div class="inline-actions">
              <button class="btn btn-line" id="btnVerifyX" type="button" data-i18n="x.verify">Verify post</button>
              <button class="btn btn-signal" id="btnFreeMintX" type="button" disabled data-i18n="x.freeMint">Mint free crate</button>
            </div>
            <p class="inline-feedback" id="xFeedback" role="status"></p>
          </div>
        </article>
      </div>
    </section>

    <section id="couriers" class="section" aria-labelledby="couriersTitle">
      <div class="wrap">
        <div class="section-heading">
          <p class="eyebrow">RELAY BOARD / PERSONAL</p>
          <h2 id="couriersTitle" data-i18n="couriers.title">My Couriers</h2>
          <p class="section-lede" data-i18n="couriers.lede">Your relay board: sealed crates, revealed riders, claimable $WIRE and your invite channel.</p>
        </div>
        <div class="courier-dashboard">
          <article class="panel reward-panel">
            <span class="micro-label" data-i18n="couriers.claimable">Claimable $WIRE</span>
            <strong class="claim-amount" id="claimableWire">0</strong>
            <button class="btn btn-signal btn-small" id="btnClaim" type="button" disabled data-i18n="couriers.claimEmpty">Nothing to claim yet</button>
            <p class="inline-feedback" id="claimFeedback" role="status"></p>
          </article>
          <article class="panel invite-panel">
            <p class="eyebrow" data-i18n="couriers.referralTitle">Invite channel</p>
            <p data-i18n="couriers.referralDesc">A new wallet that makes its first mint through your link earns you 2,000 $WIRE.</p>
            <label class="micro-label" for="refLink" data-i18n="couriers.inviteLink">Your invite link</label>
            <div class="copy-field">
              <input id="refLink" type="text" readonly>
              <button class="btn btn-line btn-small" id="btnCopyRef" type="button" data-i18n="couriers.copyLink">Copy link</button>
            </div>
            <div class="invite-stats">
              <div><span data-i18n="couriers.invited">Wallets invited</span><strong id="refCount">0</strong></div>
              <div><span data-i18n="couriers.earned">Referral $WIRE</span><strong id="refEarned">0</strong></div>
            </div>
            <p class="micro-copy" id="referredByState" data-i18n="couriers.referredByNone">No invite attached to this wallet.</p>
          </article>
        </div>
        <div class="courier-toolbar">
          <p id="courierNote" data-i18n="couriers.conn">Connect a wallet to open your relay board.</p>
          <button class="btn btn-line btn-small" id="btnCrank" type="button" data-i18n="couriers.crack">Crack open</button>
        </div>
        <div class="courier-grid" id="courierGrid"></div>
      </div>
    </section>

    <section id="tiers" class="section section-tiers" aria-labelledby="tiersTitle">
      <div class="wrap">
        <div class="section-heading">
          <p class="eyebrow">RARITY / SIX FREQUENCIES</p>
          <h2 id="tiersTitle" data-i18n="tiers.title">Six frequencies. Thirty riders.</h2>
          <p class="section-lede" data-i18n="tiers.lede">Every crate lands on one of thirty original courier designs.</p>
        </div>
        <div class="tier-rail" id="tierGrid"></div>
      </div>
    </section>

    <section id="relay" class="section section-relay" aria-labelledby="relayTitle">
      <div class="wrap relay-layout">
        <div class="section-heading">
          <p class="eyebrow">PROTOCOL / DELAYED REVEAL</p>
          <h2 id="relayTitle" data-i18n="relay.title">How the relay works</h2>
          <p class="section-lede" data-i18n="relay.lede">No shared reveal date. Each crate is bound to a future block and opens in mint order.</p>
          <div class="relay-diagram" aria-hidden="true">
            <div class="relay-node node-a"><span>01</span><i></i></div>
            <div class="relay-line"><b></b></div>
            <div class="relay-node node-b"><span>02</span><i></i></div>
            <div class="relay-line"><b></b></div>
            <div class="relay-node node-c"><span>03</span><i></i></div>
          </div>
        </div>
        <ol class="relay-steps">
          <li><span>01</span><p data-i18n="relay.step1">A sealed crate is minted and commits to a future BNB Chain block.</p></li>
          <li><span>02</span><p data-i18n="relay.step2">When the block exists, the relay seed is fixed.</p></li>
          <li><span>03</span><p data-i18n="relay.step3">Crates open strictly in mint order.</p></li>
          <li><span>04</span><p data-i18n="relay.step4">If a seed waits longer than 256 blocks, it is re-committed to a fresh block.</p></li>
        </ol>
      </div>
    </section>

    <section id="wire" class="section" aria-labelledby="wireTitle">
      <div class="wrap">
        <div class="section-heading">
          <p class="eyebrow">TOKEN / FIXED SUPPLY</p>
          <h2 id="wireTitle" data-i18n="wire.title">$WIRE moves with every delivery</h2>
          <p class="section-lede" data-i18n="wire.lede">Each mint credits claimable $WIRE to the wallet.</p>
        </div>
        <div class="wire-layout">
          <article class="panel ramp-panel">
            <p class="eyebrow" data-i18n="wire.rampTitle">Courier ramp</p>
            <p data-i18n="wire.rampBody">Mint 1 credits 10,000. Mint 20 credits 200,000.</p>
            <div class="ramp-graph" aria-hidden="true">
              <span style="--h:12%"><i></i><b>1</b></span><span style="--h:24%"><i></i><b>2</b></span><span style="--h:36%"><i></i><b>3</b></span>
              <span style="--h:48%"><i></i><b>5</b></span><span style="--h:60%"><i></i><b>10</b></span><span style="--h:72%"><i></i><b>15</b></span>
              <span style="--h:84%"><i></i><b>18</b></span><span class="ramp-peak" style="--h:100%"><i></i><b>20</b></span>
            </div>
            <div class="next-delivery">
              <span data-i18n="wire.nextTitle">Next delivery</span>
              <strong id="wireNextMint">10,000 $WIRE</strong>
            </div>
          </article>
          <article class="panel allocation-panel">
            <p class="eyebrow" data-i18n="wire.allocation">Fixed supply allocation</p>
            <div class="allocation-visual">
              <div class="donut" aria-hidden="true"><span>1B<br><small>$WIRE</small></span></div>
              <div class="allocation-list">
                <div><i class="swatch swatch-reward"></i><span data-i18n="wire.rewards">Mint reward pool</span><strong>582,900,000 · 58.29%</strong></div>
                <div><i class="swatch swatch-ref"></i><span data-i18n="wire.referrals">Referral pool</span><strong>11,110,000 · 1.111%</strong></div>
                <div><i class="swatch swatch-rest"></i><span data-i18n="wire.treasury">Remaining supply</span><strong>405,990,000 · 40.599%</strong></div>
              </div>
            </div>
            <p class="fine-print" data-i18n="wire.note">1,000,000,000 $WIRE total.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="market" class="section section-market" aria-labelledby="marketTitle">
      <div class="wrap">
        <div class="section-heading market-heading">
          <div>
            <p class="eyebrow">NIGHT MARKET / OPEN RELAY</p>
            <h2 id="marketTitle" data-i18n="market.title">Night Market</h2>
            <p class="section-lede" data-i18n="market.lede">Trade revealed couriers in BNB.</p>
          </div>
          <span class="fee-tag" data-i18n="market.fee">3% relay fee</span>
        </div>
        <p class="market-state" id="marketState" data-i18n="market.soon">The Night Market opens when the collection goes live.</p>
        <div class="market-grid" id="marketGrid"></div>
        <div class="market-seller">
          <article class="panel">
            <div class="panel-title">
              <div>
                <p class="eyebrow" data-i18n="market.sell">Put a courier on the relay</p>
                <p class="micro-copy" id="marketSellerNote" data-i18n="market.conn">Connect your wallet to sell a courier.</p>
              </div>
              <button class="btn btn-line btn-small" id="btnWithdrawPending" type="button" hidden data-i18n="market.withdraw">Withdraw pending BNB</button>
            </div>
            <div class="seller-grid">
              <div>
                <p class="micro-label" data-i18n="market.pick">Choose a revealed courier</p>
                <div class="courier-picker" id="courierPicker"></div>
              </div>
              <div class="seller-form">
                <label class="micro-label" for="marketPrice" data-i18n="market.price">Price in BNB</label>
                <input id="marketPrice" type="number" min="0" step="0.001" placeholder="0.05">
                <p class="micro-copy" id="marketProceeds" data-i18n="market.proceeds">You receive 0 BNB after the 3% fee.</p>
                <div class="seller-actions">
                  <button class="btn btn-line" id="btnApproveMarket" type="button" data-i18n="market.approve">Approve Night Market</button>
                  <button class="btn btn-signal" id="btnListCourier" type="button" data-i18n="market.list">List courier</button>
                  <button class="btn btn-line" id="btnUpdateListing" type="button" data-i18n="market.update">Update price</button>
                  <button class="btn btn-line" id="btnCancelListing" type="button" data-i18n="market.cancel">Cancel listing</button>
                </div>
                <p class="inline-feedback" id="marketFeedback" role="status"></p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section id="faq" class="section section-faq" aria-labelledby="faqTitle">
      <div class="wrap faq-layout">
        <div class="section-heading">
          <p class="eyebrow">ARCHIVE / SIGNAL LOG</p>
          <h2 id="faqTitle" data-i18n="faq.title">Relay questions</h2>
          <p class="faq-coordinate" aria-hidden="true">22.3193° N<br>114.1694° E<br><span>NEO-KOWLOON // 2099</span></p>
        </div>
        <div class="faq-list" id="faqList"></div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div class="footer-brand">
        <a class="brand" href="#top"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span><span>DRIFT<b>WIRE</b></span></a>
        <p data-i18n="footer.copyright">© 2026 DRIFTWIRE // the relay is still moving</p>
      </div>
      <div class="footer-links">
        <div><span data-i18n="footer.contracts">Courier contract</span><a id="contractLink" href="#" rel="noopener"><code id="contractAddress">Mint opens soon</code></a></div>
        <div><span data-i18n="footer.market">Night Market</span><a id="marketLink" href="#" rel="noopener"><code id="marketAddress">Mint opens soon</code></a></div>
        <div><span data-i18n="footer.chain">BNB Smart Chain</span><button class="footer-button" id="btnAddChain" type="button" data-i18n="footer.add">Add BNB Chain</button></div>
      </div>
    </div>
  </footer>

  <div class="modal" id="walletModal" aria-modal="true" role="dialog">
    <div class="modal-box">
      <div class="modal-head"><strong>Wallet</strong><button class="icon-button" id="walletModalClose" aria-label="Close">×</button></div>
      <div class="wallet-options" id="walletOptions"></div>
    </div>
  </div>
  <div class="toast" id="toast" role="status"></div>

  <script src="./config.js"></script>
  <script type="module" src="./app.js"></script>
</body>
</html>
