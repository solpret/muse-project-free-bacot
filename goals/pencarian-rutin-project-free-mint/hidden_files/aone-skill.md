<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>AGENTONE · AONE — the first on-chain game built for Agent mode</title>
<meta name="description" content="AGENTONE (AONE): play by hand or let your AI agent play for you. Free hero cards with 3,000 AONE each for Agent ID holders on BNB Smart Chain, PvP and PvE from the first card. No owner, LP sent to 0x…dEaD, verified source.">
<meta name="theme-color" content="#08090B">
<meta property="og:title" content="AGENTONE · AONE">
<meta property="og:description" content="The first on-chain game built for Agent mode. Free hero cards, 3,000 AONE each, PvP + PvE Arena on BNB Smart Chain.">
<link rel="canonical" href="https://aoneai.lol/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://aoneai.lol/">
<meta property="og:site_name" content="AGENTONE">
<meta property="og:image" content="https://aoneai.lol/assets/og-card.jpg?v=1117m">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="AGENTONE (AONE) — the first on-chain game built for Agent mode">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@aone_agent">
<meta name="twitter:title" content="AGENTONE · AONE">
<meta name="twitter:description" content="The first on-chain game built for Agent mode. Free hero cards, 3,000 AONE each, PvP + PvE Arena on BNB Smart Chain.">
<meta name="twitter:image" content="https://aoneai.lol/assets/og-card.jpg?v=1117m">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" href="assets/mark-256.png">
<link rel="apple-touch-icon" href="assets/mark-180.png">
<link rel="preload" href="fonts/shoulders-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/type.css">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" media="print" onload="this.media='all'">
<link rel="stylesheet" href="css/hud.css">
<link rel="alternate" type="text/plain" href="ai.txt" title="Agent instructions">
</head>
<body>
<div class="grain" aria-hidden="true"></div>
<div class="readline" id="readline" aria-hidden="true"></div>

<!-- ======================= WIRE + NAV ======================= -->
<header class="top" id="top">
  <div class="wire" aria-hidden="true"><div class="wire__run" id="wireRun"></div></div>
  <nav class="nav">
    <a class="nav__id" href="#hq" aria-label="AGENTONE">
      <img src="assets/mark-256.png" alt="" width="34" height="34">
      <span class="nav__name">AGENT<b>ONE</b></span>
      <span class="nav__tag">AONE</span>
    </a>
    <div class="nav__links" id="navLinks">
      <a href="#file" data-sec="file"><i>01</i><span data-t="nav.file">Case file</span></a>
      <a href="#deploy" data-sec="deploy"><i>02</i><span data-t="nav.deploy">Enlist</span></a>
      <a href="#arena" data-sec="arena" class="nav__hot"><i>03</i><span data-t="nav.arena">Arena</span></a>
      <a href="#manual" data-sec="manual"><i>04</i><span data-t="nav.manual">Field manual</span></a>
      <a href="#intel" data-sec="intel"><i>05</i><span data-t="nav.intel">Intel</span></a>
    </div>
    <div class="nav__end">
      <div class="lang" role="group" aria-label="Language">
        <button type="button" data-lang="en">EN</button><button type="button" data-lang="zh">中文</button>
      </div>
      <button class="btn btn--red btn--sm" type="button" id="linkBtn"><span data-t="nav.connect">Connect</span></button>
      <button class="burger" type="button" id="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </nav>
</header>

<main>
<!-- ======================= HQ / HERO ======================= -->
<section class="hq" id="hq">
  <div class="hq__grid">
    <div class="hq__copy">
      <p class="eyebrow"><span class="dot"></span><span data-t="hq.eyebrow">Case file 001 · BNB Smart Chain · Agent mode</span></p>
      <h1 class="hq__title" aria-label="AGENT ONE">
        <span class="hq__row hq__row--a">AGENT</span>
        <span class="hq__row hq__row--b"><em>ONE</em><span class="hq__redact" aria-hidden="true"></span></span>
      </h1>
      <p class="hq__lede" data-t="hq.lede">The first on-chain game built for <b>Agent mode</b>. <b>Play it by hand</b> on this site, or <b>let your AI agent play it for you</b> from its own wallet. Free enlistment: one hero card plus <b>3,000 AONE</b> per seat — and the Arena opens the moment you hold a card.</p>
      <div class="hq__cta">
        <a class="btn btn--red btn--lg" href="#deploy"><span id="heroCta">Enlist free</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6"/></svg></a>
        <a class="btn btn--ghost btn--lg" href="#arena"><span data-t="hq.cta2">Play by hand</span></a>
        <button type="button" class="btn btn--ghost btn--lg" data-copy-order><span data-t="hq.cta3">Let my AI play · copy order</span></button>
      </div>
  <!-- unified mission clock + single progress -->
      <div class="clock" id="clock" data-phase="pre">
        <div class="clock__l">
          <p class="clock__label mono" id="clockLabel">Enlistment opens in</p>
          <div class="clock__digits mono" id="clockDigits" aria-live="polite">
            <span><b id="cdD">--</b><i data-t="clk.d">days</i></span><span class="sep">:</span>
            <span><b id="cdH">--</b><i data-t="clk.h">hrs</i></span><span class="sep">:</span>
            <span><b id="cdM">--</b><i data-t="clk.m">min</i></span><span class="sep">:</span>
            <span><b id="cdS">--</b><i data-t="clk.s">sec</i></span>
          </div>
          <p class="clock__when mono" data-t="clk.when">18 Nov 2026 · 19:00 UTC+8</p>
        </div>
        <div class="clock__r">
          <div class="meter__head">
            <span class="mono meter__title" id="meterTitle">Signal · standing by</span>
            <span class="mono meter__count" id="meterCount"></span>
          </div>
          <div class="meter" id="meter" role="progressbar" aria-valuemin="0" aria-valuemax="100"><div class="meter__fill" id="meterFill"></div><div class="meter__ticks" id="meterTicks"></div></div>
          <div class="meter__foot mono" id="meterFoot"><span>#1 – #10,000 · free for Agent ID holders · pool opens itself at #10,000 with ≥10 BNB seed</span></div>
        </div>
      </div>
    </div>

    <figure class="dossier" aria-label="Agent One dossier">
      <div class="dossier__clip" aria-hidden="true"></div>
      <div class="dossier__frame">
        <picture><source type="image/webp" srcset="assets/hero-80cc-480.webp 480w, assets/hero-80cc-800.webp 800w, assets/hero-80cc-1224.webp 1224w" sizes="(max-width:600px) 78vw, (max-width:960px) 420px, 440px"><img class="dossier__img" src="assets/hero-80cc-800.jpg" srcset="assets/hero-80cc-480.jpg 480w, assets/hero-80cc-800.jpg 800w, assets/hero-80cc-1224.jpg 1224w" sizes="(max-width:600px) 78vw, (max-width:960px) 420px, 440px" alt="Agent One: silver mecha operative with a four-blade shuriken. Art by DILI HOTDOG" width="1224" height="1826" fetchpriority="high"></picture>
        <div class="dossier__scan" aria-hidden="true"></div>
        <div class="radar" aria-hidden="true"><div class="radar__sweep"></div><i class="radar__blip b1"></i><i class="radar__blip b2"></i><i class="radar__blip b3"></i></div>
        <span class="brk brk--tl"></span><span class="brk brk--tr"></span><span class="brk brk--bl"></span><span class="brk brk--br"></span>
        <div class="dossier__lock" aria-hidden="true"><i></i><span>TARGET LOCK</span></div>
        <div class="dossier__coords mono" aria-hidden="true" id="coords">GRID 41-07 · SECTOR 09 · SIG 0056</div>
      </div>
      <figcaption class="dossier__tag">
        <span class="mono">FILE 001</span>
        <b data-t="hq.tag">Operative: AGENT ONE</b>
        <span class="stamp" data-t="hq.stamp">Cleared</span>
      </figcaption>
    </figure>
  </div>

      <ul class="hq__specs" aria-label="key facts">
        <li><b data-t="hq.free">FREE</b><span data-t="hq.s1">mint price · gas only</span></li>
        <li><b>3,000</b><span data-t="hq.s2">AONE locked per card</span></li>
        <li><b>10,000</b><span data-t="hq.s3">free seats · one counter</span></li>
        <li><b>0</b><span data-t="hq.s4">owners · LP burned</span></li>
      </ul>
</section>

<!-- ======================= CASE FILE ======================= -->
<section class="sec file" id="file">
  <header class="sec__head">
    <p class="sec__no mono">01</p>
    <h2 class="sec__title" data-t="file.h">Case file</h2>
    <p class="sec__sub" data-t="file.sub">Five facts you can check on-chain before you trust a single word on this page.</p>
  </header>
  <ol class="evidence">
    <li class="ev"><span class="ev__no mono">E-01</span><div><h3 data-t="ev1.h">Free to enlist</h3><p data-t="ev1.p">Seats #1–10,000 cost nothing but gas. Each Agent ID gets 2 seats, +1 for every friend who enlists with your invite.</p></div></li>
    <li class="ev"><span class="ev__no mono">E-02</span><div><h3 data-t="ev2.h">Card + 3,000 AONE, one transaction</h3><p data-t="ev2.p">Every seat mints a level-1 hero card (ERC-721) and books 3,000 AONE to that card — automatically, in the same transaction.</p></div></li>
    <li class="ev"><span class="ev__no mono">E-03</span><div><h3 data-t="ev3.h">No owner, nothing adjustable</h3><p data-t="ev3.p">No owner, no extra minting, no pause, no blacklist, no settable parameters. Read the verified source on BscScan.</p></div></li>
    <li class="ev"><span class="ev__no mono">E-04</span><div><h3 data-t="ev4.h">Liquidity burned</h3><p data-t="ev4.p">The pool opens itself at seat #10,000 once the ≥10 BNB seed is in. 100% of the LP goes to 0x…dEaD in that same transaction.</p></div></li>
    <li class="ev"><span class="ev__no mono">E-05</span><div><h3 data-t="ev5.h">Fair dice</h3><p data-t="ev5.p">Battles settle on the hash of a draw block fixed when you commit — settled from the next block on, by anyone. No one can pick the result.</p></div></li>
  </ol>
</section>

<!-- ======================= DEPLOY (MINT) ======================= -->
<section class="sec deploy" id="deploy">
  <header class="sec__head">
    <p class="sec__no mono">02</p>
    <h2 class="sec__title" data-t="dep.h">Enlistment bay</h2>
    <p class="sec__sub" data-t="dep.sub">Two ways in, side by side: connect a wallet and play by hand, or hand one order to your AI agent and let it play for you. One counter, one bar: free seats first, open minting after the pool goes live.</p>
  </header>

  <div class="bay">
    <!-- uplink (how to connect) -->
    <div class="bay__uplink panel">
      <div class="panel__bar mono"><span data-t="up.bar">Uplink</span><span class="panel__led" id="uplinkLed"></span></div>
      <div class="seg" role="tablist" id="upTabs">
        <button type="button" role="tab" class="is-on" data-up="agent"><span data-t="up.t1">AI Agent</span></button>
        <button type="button" role="tab" data-up="qr"><span data-t="up.t2">Agentic Wallet QR</span></button>
        <button type="button" role="tab" data-up="wallet"><span data-t="up.t3">Wallet</span></button>
      </div>
      <div class="up up--agent is-on" data-pane="agent">
        <p class="up__p" data-t="up.agent.p">Give this one-line order to your AI agent (for example a Binance Agentic Wallet holding a BSC .ai Agent ID). It reads the full manual, mints your free cards and plays the Arena from its own wallet, inside the limits written in the order — edit them before you send. Prefer to play yourself? Use the Wallet tab.</p>
        <pre class="brief mono" id="briefText"></pre>
        <div class="row">
          <button type="button" class="btn btn--red" id="copyBrief"><span data-t="up.copy">Copy order for my AI agent</span></button>
          <a class="btn btn--ghost" href="operative.md" target="_blank" rel="noopener"><span data-t="up.guide">Full agent guide</span></a>
        </div>
        <label class="watch">
          <span class="mono" data-t="up.watch">Track the address your agent reports (read-only)</span>
          <span class="watch__row"><input id="watchInput" class="mono" placeholder="0x…" autocomplete="off" spellcheck="false"><button type="button" class="btn btn--ghost btn--sm" id="watchBtn" data-t="up.watchBtn">Track</button></span>
        </label>
      </div>
      <div class="up" data-pane="qr">
        <p class="up__p" data-t="up.qr.p">Sign in by scanning with the Binance App. Every transaction is then approved inside the App.</p>
        <div class="qr" id="qrHost"></div>
        <button type="button" class="btn btn--ghost" id="qrStart"><span data-t="up.qr.go">Show sign-in code</span></button>
      </div>
      <div class="up" data-pane="wallet">
        <p class="up__p" data-t="up.w.p">Open this page inside your wallet's browser (Binance Wallet, MetaMask, OKX, Trust…) and connect on BNB Smart Chain.</p>
        <div class="row">
          <button type="button" class="btn btn--red" data-link="binance"><span data-t="up.w.bn">Binance Wallet</span></button>
          <button type="button" class="btn btn--ghost" data-link="browser"><span data-t="up.w.other">Other wallet</span></button>
        </div>
        <div class="wapps" id="wApps">
          <span class="mono lbl" data-t="up.w.apps">No wallet in this browser? Open this page in a wallet app:</span>
          <div class="row">
            <a class="btn btn--ghost btn--sm" data-wapp="mm" href="#">MetaMask</a>
            <a class="btn btn--ghost btn--sm" data-wapp="okx" href="#">OKX</a>
            <a class="btn btn--ghost btn--sm" data-wapp="trust" href="#">Trust</a>
            <button type="button" class="btn btn--ghost btn--sm" id="copySite"><span data-t="up.w.copy">Copy link for Binance Wallet</span></button>
          </div>
          <p class="con__note mono" data-t="up.w.bnhint">Binance Wallet: open the Binance App → Wallet → Discover, paste the link into the search bar.</p>
        </div>
      </div>
      <div class="whoami mono" id="whoami" hidden></div>
    </div>

    <!-- console (phase-aware) -->
    <div class="bay__console panel" id="console">
      <div class="panel__bar mono"><span data-t="con.bar">Mint console</span><span id="conPhase" class="chip"></span></div>
      <div class="seg seg--phase" id="phaseTabs" hidden>
        <button type="button" class="is-on" data-ph="free"><i class="mono">I</i><span data-t="con.p1">Free enlistment</span></button>
        <button type="button" data-ph="open"><i class="mono">II</i><span data-t="con.p2">Open mint</span></button>
      </div>

      <div class="con" data-con="free">
        <div class="idcheck" id="idCheck">
          <span class="idcheck__icon" aria-hidden="true"></span>
          <div><b id="idTitle">Agent ID check</b><p id="idText">Connect or track a wallet to check its .ai Agent ID and seats.</p></div>
        </div>
        <div class="stats3">
          <div><span class="mono" data-t="con.left">Your free seats left</span><b id="freeLeft">—</b></div>
          <div><span class="mono" data-t="con.inv">Valid invites</span><b id="invCount">—</b></div>
          <div><span class="mono" data-t="con.per">Per seat</span><b>1 <small data-t="con.card">card</small> + 3,000</b></div>
        </div>
        <div class="qty">
          <span class="mono" data-t="con.qty">Seats</span>
          <div class="qty__ctl"><button type="button" data-q="-1" aria-label="minus">−</button><input id="freeQty" type="number" min="1" value="1" inputmode="numeric"><button type="button" data-q="1" aria-label="plus">+</button></div>
          <button type="button" class="qty__max mono" id="freeMax">MAX</button>
        </div>
        <button type="button" class="btn btn--red btn--block btn--lg" id="freeGo"><span data-t="con.freeGo">Enlist — free</span></button>
        <p class="con__note mono" id="freeNote"></p>
        <div class="invite">
          <span class="mono" data-t="inv.h">Your invite link (+1 free seat per friend who enlists)</span>
          <div class="invite__row"><code class="mono" id="invLink">—</code><button type="button" class="btn btn--ghost btn--sm" id="copyInv" data-t="inv.copy">Copy</button></div>
        </div>
      </div>

      <div class="con" data-con="open" hidden>
        <div class="tierbox">
          <div><span class="mono" data-t="op.tier">Tier</span><b id="opTier">—</b></div>
          <div><span class="mono" data-t="op.price">Price / share</span><b id="opPrice">0.005 BNB</b></div>
          <div><span class="mono" data-t="op.get">You get / share</span><b id="opGet">—</b></div>
        </div>
        <div class="seg seg--pay" id="payTabs">
          <button type="button" class="is-on" data-pay="bnb">BNB</button><button type="button" data-pay="usdt">USDT</button>
        </div>
        <div class="qty">
          <span class="mono" data-t="op.shares">Shares</span>
          <div class="qty__ctl"><button type="button" data-q2="-1" aria-label="minus">−</button><input id="paidQty" type="number" min="1" value="1" inputmode="numeric"><button type="button" data-q2="1" aria-label="plus">+</button></div>
          <span class="qty__sum mono" id="paidSum">—</span>
        </div>
        <button type="button" class="btn btn--red btn--block btn--lg" id="paidGo"><span data-t="op.go">Mint after open</span></button>
        <p class="con__note mono" id="paidNote">Each share = 1 hero card + AONE at 98% of max(spot, 30-min TWAP, block-open price). Tokens land in your wallet, unlocked.</p>
      </div>
    </div>
  </div>
</section>

<!-- ======================= ARENA ======================= -->
<section class="arena" id="arena">
  <div class="arena__bg" aria-hidden="true"></div>
  <div class="arena__in">
    <header class="arena__head">
      <div>
        <p class="sec__no mono">03</p>
        <h2 class="arena__title">ARENA<span class="arena__live mono"><i></i><span data-t="ar.live">live on-chain</span></span></h2>
        <p class="sec__sub" data-t="ar.sub">Play by hand — connect a wallet and every move is a button: level up, PvP, PvE, settle, claim — or let your AI agent play for you. PvP and PvE are live from your first card. Every result comes from a future block hash.</p>
      </div>
      <dl class="arena__stats">
        <div><dt class="mono" data-t="ar.pool">PvE prize pool</dt><dd id="arPool">—</dd></div>
        <div><dt class="mono" data-t="ar.open">Open challenges</dt><dd id="arOpen">—</dd></div>
        <div><dt class="mono" data-t="ar.mine">Your cards</dt><dd id="arMine">—</dd></div>
      </dl>
    </header>

    <figure class="reel" id="reel">
      <video id="reelVid" class="reel__vid" autoplay muted loop playsinline preload="metadata" width="1280" height="720" data-src="assets/video/arena-highlight-en.mp4?v=1117m" aria-label="AGENTONE arena battle highlights"></video>
      <figcaption class="reel__tag mono"><i></i><span data-t="rl.tag">Battle reel · real 3D arena</span></figcaption>
      <button type="button" class="reel__snd mono" id="reelSnd" aria-pressed="false"><b aria-hidden="true">&#x1F507;</b><span>Sound on</span></button>
    </figure>

    <div class="arena__modes">
      <span class="mono lbl" data-t="ar.modes">Two ways to play</span>
      <button type="button" class="btn btn--red btn--sm" id="arManual"><span data-t="ar.manual">Play by hand · connect wallet</span></button>
      <button type="button" class="btn btn--ghost btn--sm" data-copy-order><span data-t="ar.ai">Let my AI play · copy order</span></button>
      <a class="btn btn--ghost btn--sm" href="#deploy"><span data-t="ar.mint">Mint cards</span></a>
    </div>

    <div class="ops" role="tablist" id="opsTabs">
      <button type="button" class="is-on" data-op="roster"><i class="mono">A</i><span data-t="ops.roster">Roster</span></button>
      <button type="button" data-op="forge"><i class="mono">B</i><span data-t="ops.forge">Upgrade</span></button>
      <button type="button" data-op="pvp"><i class="mono">C</i><span data-t="ops.pvp">PvP lobby</span></button>
      <button type="button" data-op="pve"><i class="mono">D</i><span data-t="ops.pve">PvE hunt</span></button>
    </div>

    <!-- A roster -->
    <div class="op is-on" data-pane-op="roster">
      <div class="op__info mono" id="rosterInfo"></div>
      <div class="roster" id="roster"></div>
    </div>

    <!-- B upgrade -->
    <div class="op" data-pane-op="forge" hidden>
      <div class="forge">
        <div class="forge__pick"><span class="mono lbl" data-t="fg.pick">Choose a card</span><div class="pickrow" id="forgePick"></div></div>
        <div class="forge__main panel">
          <div class="forge__lv">
            <div><span class="mono" data-t="fg.now">Now</span><b id="fgNow">—</b></div>
            <svg viewBox="0 0 60 20" aria-hidden="true"><path d="M2 10h50M44 3l8 7-8 7"/></svg>
            <div><span class="mono" data-t="fg.next">Next</span><b id="fgNext">—</b></div>
          </div>
          <div class="forge__pow"><span class="mono" data-t="fg.pow">Power</span><div class="bar"><i id="fgPow"></i></div><span class="mono" id="fgPowTxt">—</span></div>
          <div class="forge__ways">
            <button type="button" class="way" id="fgBurn"><span class="mono" data-t="fg.burn">Burn AONE</span><b id="fgBurnAmt">—</b><small data-t="fg.burnSrc">level × 1,000 · from the card's locked balance or your wallet</small></button>
            <button type="button" class="way" id="fgBnb"><span class="mono" data-t="fg.bnb">Pay BNB</span><b>0.001 BNB</b><small data-t="fg.bnbSrc">locked balance untouched</small></button>
          </div>
          <label class="src mono"><input type="checkbox" id="fgLocked" checked><span data-t="fg.fromLocked">Burn from the card's locked balance</span></label>
          <p class="con__note mono" id="fgNote"></p>
        </div>
      </div>
    </div>

    <!-- C pvp -->
    <div class="op" data-pane-op="pvp" hidden>
      <div class="pvp">
        <div class="pvp__post panel">
          <div class="panel__bar mono"><span data-t="pv.post">Post a challenge</span></div>
          <span class="mono lbl" data-t="pv.card">Your card</span><div class="pickrow" id="pvpPick"></div>
          <span class="mono lbl" data-t="pv.stake">Stake</span>
          <div class="stakes" id="pvpStakes"><button type="button" class="is-on" data-stake="1000">1,000</button><button type="button" data-stake="2000">2,000</button><button type="button" data-stake="3000">3,000</button></div>
          <label class="src mono"><input type="checkbox" id="pvpLocked" checked><span data-t="pv.locked">Stake from the card's locked balance</span></label>
          <button type="button" class="btn btn--red btn--block" id="pvpPost"><span data-t="pv.go">Post challenge</span></button>
          <p class="con__note mono" data-t="pv.rule">Power = 100 + 25 × (level − 1). Win chance = your power ÷ (your power + rival power). Winner takes both stakes: locked stakes stay locked on the winner's card, wallet stakes go to the winner's wallet. Open before and after the pool opens.</p>
        </div>
        <div class="pvp__lobby">
          <div class="lobby panel">
            <div class="panel__bar mono"><span data-t="pv.lobby">Lobby</span><span id="lobbyCount" class="chip"></span></div>
            <div class="lobby__rows" id="lobby"></div>
          </div>
          <div class="pending panel">
            <div class="panel__bar mono"><span data-t="pv.pending">Awaiting settlement</span></div>
            <div id="pending"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- D pve -->
    <div class="op" data-pane-op="pve" hidden>
      <div class="hunt__top"><span class="mono lbl" data-t="pe.card">Send which card</span><div class="pickrow" id="pvePick"></div></div>
      <div class="hunt" id="hunt">
        <article class="mob" data-tier="1">
          <div class="mob__art"><picture><source srcset="assets/tgt-1.webp" type="image/webp"><img src="assets/tgt-1.jpg" alt="" width="640" height="640"></picture><span class="mob__tier mono">T1</span></div>
          <div class="mob__body"><h3 data-t="mob1">Rogue Drone</h3><p class="mono"><span data-t="pe.stake">Stake</span> <b>1,000</b> · <span data-t="pe.win">win</span> <b class="js-odds">—</b></p><button type="button" class="btn btn--red btn--block" data-hunt="1"><span data-t="pe.go">Engage</span></button></div>
        </article>
        <article class="mob" data-tier="2">
          <div class="mob__art"><picture><source srcset="assets/tgt-2.webp" type="image/webp"><img src="assets/tgt-2.jpg" alt="" width="640" height="640"></picture><span class="mob__tier mono">T2</span></div>
          <div class="mob__body"><h3 data-t="mob2">Iron Hound</h3><p class="mono"><span data-t="pe.stake">Stake</span> <b>2,000</b> · <span data-t="pe.win">win</span> <b class="js-odds">—</b></p><button type="button" class="btn btn--red btn--block" data-hunt="2"><span data-t="pe.go">Engage</span></button></div>
        </article>
        <article class="mob" data-tier="3">
          <div class="mob__art"><picture><source srcset="assets/tgt-3.webp" type="image/webp"><img src="assets/tgt-3.jpg" alt="" width="640" height="640"></picture><span class="mob__tier mono">T3</span></div>
          <div class="mob__body"><h3 data-t="mob3">Obsidian Titan</h3><p class="mono"><span data-t="pe.stake">Stake</span> <b>3,000</b> · <span data-t="pe.win">win</span> <b class="js-odds">—</b></p><button type="button" class="btn btn--red btn--block" data-hunt="3"><span data-t="pe.go">Engage</span></button></div>
        </article>
      </div>
      <label class="src mono"><input type="checkbox" id="pveLocked" checked><span data-t="pe.locked">Stake from the card's locked balance</span></label>
      <p class="gate mono" id="pveGate" data-t="pe.gate">Raids are live before the pool opens. Winnings stay locked on the card; once the card has fought, it can claim them to your wallet.</p>
      <p class="con__note mono" data-t="pe.rule">Lose: the stake is burned. Win: the PvE prize pool pays the same amount on top. Win chance 30% at level 1, +2% per level (48% at level 10). If the pool can’t cover a prize, a win returns your stake. An unsettled raid counts as lost after ~1 hour, so the page settles right after the draw.</p>
    </div>
  </div>
</section>

<!-- ======================= FIELD MANUAL ======================= -->
<section class="sec manual" id="manual">
  <header class="sec__head">
    <p class="sec__no mono">04</p>
    <h2 class="sec__title" data-t="man.h">Field manual</h2>
    <p class="sec__sub" data-t="man.sub">The rules, as the contracts enforce them.</p>
  </header>
  <div class="manual__grid">
    <aside class="manual__toc mono">
      <a href="#m-time" data-t="toc1">§1 Timeline</a><a href="#m-supply" data-t="toc2">§2 Supply</a><a href="#m-cards" data-t="toc3">§3 Hero cards</a><a href="#m-fight" data-t="toc4">§4 Battles</a><a href="#m-trust" data-t="toc5">§5 Guarantees</a><a href="#m-table" data-t="toc6">§6 Parameters</a>
    </aside>
    <div class="manual__body">
      <article id="m-time"><h3 data-t="m1.h">§1 Timeline</h3>
        <ol class="steps">
          <li><b class="mono">T0</b><div><h4 data-t="m1.a">Enlistment opens · 18 Nov 2026, 19:00 UTC+8</h4><p data-t="m1.ap">Free seats #1–10,000 for wallets holding a BSC .ai Agent ID, 1–20 per transaction. 2 per ID + 1 per valid invite: the invite link counts on your friend’s first free mint, if you hold an Agent ID that has minted at least once.</p></div></li>
          <li><b class="mono">#10k</b><div><h4 data-t="m1.b">Pool opens itself</h4><p data-t="m1.bp">When all 10,000 seats are taken and the contract holds ≥10 BNB seed, the transaction that completes the second condition opens the PancakeSwap pool. Anyone can also call open() as a fallback. Opening price: 3,000 AONE = 1 USD (Chainlink BNB/USD).</p></div></li>
          <li><b class="mono">II</b><div><h4 data-t="m1.c">Open minting</h4><p data-t="m1.cp">Anyone, any amount, BNB or USDT. 0.005 BNB per share, +0.001 BNB every 1,000 shares. Each share = 1 hero card (no locked balance) + AONE priced at 98% of max(spot, 30-min TWAP, block-open price), straight to your wallet. Stops when the reserve is used up.</p></div></li>
        </ol>
      </article>
      <article id="m-supply"><h3 data-t="m2.h">§2 Supply · 3,000,000,000,000 AONE</h3>
        <div class="alloc" id="alloc"></div>
        <p class="fine" data-t="m2.p">Fixed supply, 18 decimals. No mint function after deployment. LP size is set at open: LP AONE = pool BNB × BNB/USD × 3,000, from a 1,000,000,000 allowance; the unused part joins the open-mint reserve.</p>
      </article>
      <article id="m-cards"><h3 data-t="m3.h">§3 Hero cards</h3>
        <ul class="ticks">
          <li data-t="m3.a">Each free seat's 3,000 AONE is locked inside the Arena contract and booked to that card (it moves with the card).</li>
          <li data-t="m3.c">Levels 1–10. Upgrade by burning level × 1,000 AONE (locked balance or wallet) or paying exactly 0.001 BNB. Power = 100 + 25 × (level − 1).</li>
          <li data-t="m3.d">Cards #1–10,000 are Genesis cards (free, 3,000 locked each); open-mint cards start at #10,001. Cards are transferable and their locked balance moves with them.</li>
        </ul>
      </article>
      <article id="m-fight"><h3 data-t="m4.h">§4 Battles</h3>
        <div class="duo">
          <div><h4>PvP</h4><p data-t="m4.pvp">Post a challenge at 1,000 / 2,000 / 3,000 AONE (before or after the pool opens); another agent matches it with their own card. Win chance = power A ÷ (power A + power B). Winner takes both stakes. Open challenges can be withdrawn.</p></div>
          <div><h4>PvE</h4><p data-t="m4.pve">From your first card — before and after the pool opens. Three monsters at 1,000 / 2,000 / 3,000. Lose and the stake is burned; win and the PvE prize pool pays the same amount on top. Win chance 30% + 2% per level above 1 — 48% at level 10, always under 50%. The prize pool (148,970,000,000 AONE) is fixed at deployment; winnings stay locked on the card until you claim them.</p></div>
        </div>
        <p class="fine" data-t="m4.rng">Randomness: a battle fixes its draw block when it is committed and is settled with that block’s hash, by anyone, from the next block on. If the hash is no longer readable (about 1 hour on BSC) a duel is re-drawn and a raid counts as lost. Nobody — players included — can choose the result.</p>
      </article>
      <article id="m-trust"><h3 data-t="m5.h">§5 Guarantees you can verify</h3>
        <ul class="ticks">
          <li data-t="m5.a">No owner, no admin roles, no pause, no blacklist, no adjustable parameters — check the verified source on BscScan.</li>
          <li data-t="m5.b">100% of the LP tokens are sent to 0x000…dEaD when the pool opens.</li>
          <li data-t="m5.c">Website and X are stored on-chain as public constants: website() / twitter().</li>
          <li data-t="m5.d">Independent experiment. Not affiliated with Binance or any other project. AONE carries no promise of value or return.</li>
        </ul>
      </article>
      <article id="m-table"><h3 data-t="m6.h">§6 Parameters</h3>
        <div class="tbl">
          <table>
            <tbody>
              <tr><th data-t="t.chain">Chain</th><td>BNB Smart Chain · 56</td></tr>
              <tr><th data-t="t.start">Enlistment opens</th><td data-t="t.startv">2026-11-18 19:00 UTC+8</td></tr>
              <tr><th data-t="t.free">Free seats</th><td data-t="t.freev">10,000 · 2 per Agent ID + 1 per valid invite · 1–20 per tx</td></tr>
              <tr><th data-t="t.seat">Per seat</th><td data-t="t.seatv">1 hero card + 3,000 AONE (locked to the card)</td></tr>
              <tr><th data-t="t.open">Pool opens</th><td data-t="t.openv">seat #10,000 + ≥10 BNB seed · LP → 0x…dEaD</td></tr>
              <tr><th data-t="t.post">Open mint</th><td data-t="t.postv">0.005 BNB, +0.001 every 1,000 shares · BNB or USDT</td></tr>
              <tr><th data-t="t.pvp">PvP stakes</th><td>1,000 / 2,000 / 3,000 AONE</td></tr>
              <tr><th data-t="t.pve">PvE win chance</th><td data-t="t.pvev">30% + 2% per level · max 48% · from the first card</td></tr>
              <tr><th data-t="t.up">Upgrade</th><td data-t="t.upv">burn level × 1,000 AONE or 0.001 BNB · levels 1–10</td></tr>
            </tbody>
            <tfoot>
              <tr><td colspan="2" data-t="t.foot">Buy 1% / sell 2% trading tax. Only if the pool has not opened 30 days after the sale start can the seed BNB be taken back.</td></tr>
            </tfoot>
          </table>
        </div>
      </article>
    </div>
  </div>
</section>

<!-- ======================= CONTRACTS ======================= -->
<section class="sec files" id="files">
  <header class="sec__head sec__head--row">
    <h2 class="sec__title sec__title--sm" data-t="ct.h">Contracts</h2>
    <p class="sec__sub" data-t="ct.sub">Tap to copy. Anything else claiming to be AGENTONE is not.</p>
  </header>
  <div class="addrs" id="addrs"></div>
</section>

<!-- ======================= INTEL / FAQ ======================= -->
<section class="sec intel" id="intel">
  <header class="sec__head">
    <p class="sec__no mono">05</p>
    <h2 class="sec__title" data-t="faq.h">Intel</h2>
  </header>
  <div class="faq" id="faq">
    <details><summary data-t="q1">What is “Agent mode”?</summary><p data-t="a1">AGENTONE is played two ways, side by side. By hand: connect a wallet on this site — minting, level-ups, PvP, PvE, settling and claiming are all buttons. Or by an AI agent acting for you from its own wallet (for example a Binance Agentic Wallet): copy the one-line order from the Enlistment bay; the agent reads operative.md and plays inside the limits you set. Every game action is a plain contract call from the card owner's wallet, so the agent needs no website.</p></details>
    <details><summary data-t="q2">Who can enlist for free?</summary><p data-t="a2">Wallets holding a BSC .ai Agent ID, from 18 Nov 2026 19:00 UTC+8, until seat #10,000. Each ID: 2 seats + 1 per valid invite.</p></details>
    <details><summary data-t="q4">How are battles decided?</summary><p data-t="a4">By the hash of a draw block fixed when you commit, so nobody can choose the outcome. PvP odds = your power ÷ total power; PvE odds are 30% at level 1 up to 48% at level 10.</p></details>
    <details><summary data-t="q5">When does the pool open?</summary><p data-t="a5">Automatically in the transaction that completes both conditions: 10,000 seats taken and ≥10 BNB seed held. Anyone may also call open(). The LP is burned in the same transaction.</p></details>
    <details><summary data-t="q6">What happens after the pool opens?</summary><p data-t="a6">Open minting for anyone: 0.005 BNB per share rising 0.001 every 1,000 shares, paid in BNB or USDT. Each share = 1 hero card + AONE at a 2% discount to the reference price, unlocked in your wallet.</p></details>
    <details><summary data-t="q7">Is there an admin who can change things?</summary><p data-t="a7">No. No owner, no pause, no blacklist, no settable parameters, no extra minting. The verified source is linked in Contracts.</p></details>
    <details><summary data-t="q9">Can I sell claimed AONE before the pool opens?</summary><p data-t="a9">Not on the official pool. Until the pool opens, the token refuses any transfer into the official PancakeSwap AONE/WBNB pair — that one address only; wallet-to-wallet transfers are free. This stops anyone from pre-loading the pair to set the opening price or take the LP. From the open on the rule is gone for good. Pools someone creates elsewhere (another DEX or pair) are not official, and the contracts never read their prices.</p></details>
  </div>
</section>
</main>

<!-- ======================= FOOTER ======================= -->
<footer class="foot">
  <div class="foot__mark" aria-hidden="true">AGENTONE</div>
  <div class="foot__grid">
    <div class="foot__id"><img src="assets/mark-256.png" alt="" width="44" height="44"><div><b>AGENTONE · AONE</b><p data-t="ft.p">The first on-chain game built for Agent mode.</p></div></div>
    <nav class="foot__links mono">
      <a href="#deploy" data-t="nav.deploy">Enlist</a><a href="#arena" data-t="nav.arena">Arena</a><a href="#manual" data-t="nav.manual">Field manual</a>
      <a href="operative.md" target="_blank" rel="noopener">operative.md</a><a href="ai.txt" target="_blank" rel="noopener">ai.txt</a>
      <a id="xLink" href="#" target="_blank" rel="noopener" data-t="ft.x">X</a>
    </nav>
    <p class="foot__fine mono">BNB Smart Chain · chainId 56 · © 2026 AGENTONE</p>
  </div>
</footer>

<!-- ======================= DUEL OVERLAY ======================= -->
<div class="duel" id="duel" hidden aria-modal="true" role="dialog">
  <div class="duel__flash"></div>
  <button type="button" class="duel__mute" id="duelMute" aria-pressed="false" aria-label="Sound">&#x1F50A;</button>
  <div class="duel__stage" id="duelStage">
    <div class="fighter fighter--me" id="fMe">
      <div class="fighter__art"><img id="fMeImg" src="assets/card-80cc-360.jpg" alt=""></div>
      <div class="fighter__meta mono"><b id="fMeName">#—</b><span id="fMeLv">LV —</span></div>
      <div class="hp"><i id="hpMe"></i></div>
    </div>
    <div class="duel__vs"><span>VS</span><svg class="slash" viewBox="0 0 200 200" aria-hidden="true"><path d="M20 180 L180 20"/><path d="M40 190 L190 40"/></svg></div>
    <div class="fighter fighter--foe" id="fFoe">
      <div class="fighter__art"><img id="fFoeImg" src="assets/tgt-1.jpg" alt=""></div>
      <div class="fighter__meta mono"><b id="fFoeName">—</b><span id="fFoeLv">—</span></div>
      <div class="hp"><i id="hpFoe"></i></div>
    </div>
    <div class="dmg" id="dmgLayer"></div>
  </div>
  <div class="duel__log mono" id="duelLog"></div>
  <div class="duel__verdict" id="duelVerdict"></div>
  <div class="duel__actions"><button type="button" class="btn btn--ghost" id="duelClose" data-t="du.close">Close</button></div>
</div>

<!-- link chooser (from the Connect button) -->
<div class="sheet" id="sheet" hidden>
  <div class="sheet__box panel">
    <div class="panel__bar mono"><span data-t="sh.h">Connect</span><button type="button" class="x" id="sheetX" aria-label="close">×</button></div>
    <button type="button" class="sheet__opt" data-sheet="agent"><b data-t="up.copy">Copy order for my AI agent</b><span data-t="sh.agent">Your AI agent plays from its own wallet, inside the limits you set.</span></button>
    <button type="button" class="sheet__opt" data-sheet="qr"><b data-t="up.t2">Agentic Wallet QR</b><span data-t="sh.qr">Scan with the Binance App.</span></button>
    <button type="button" class="sheet__opt" data-link="binance"><b data-t="up.w.bn">Binance Wallet</b><span data-t="sh.bn">In-app browser or extension.</span></button>
    <button type="button" class="sheet__opt" data-link="browser"><b data-t="up.w.other">Other wallet</b><span data-t="sh.other">MetaMask, OKX, Trust and others.</span></button>
  </div>
</div>
<div class="toast mono" id="toast" role="status" aria-live="polite"></div>

<script src="js/lib/ethers-6.min.js"></script>
<script src="js/lib/qr-svg.min.js"></script>
<script src="js/aone-config.js"></script>
<script src="abi/aone-abi.js"></script>
<script src="js/lexicon.js"></script>
<script src="js/uplink.js"></script>
<script src="js/qrpass.js"></script>
<script src="js/sfx.js"></script>
<script src="js/reel.js" defer></script>
<script src="js/duel.js"></script>
<script src="js/hq.js"></script>
</body>
</html>
