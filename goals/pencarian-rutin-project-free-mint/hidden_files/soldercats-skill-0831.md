<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="robots" content="noindex">
  <title>404 · Not found</title>
  <meta name="theme-color" content="#0b0907">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/styles.css">
  <style>
    .not-found{min-height:calc(100svh - 81px);display:grid;place-items:center;padding:54px 0}
    .not-found-panel{
      position:relative;
      width:min(780px,100%);
      padding:clamp(28px,5vw,58px);
      border:3px solid var(--brown);
      background:
        linear-gradient(135deg,rgba(239,108,50,.1),transparent 48%),
        linear-gradient(180deg,var(--iron-2),var(--coal));
      box-shadow:var(--shadow);
    }
    .not-found-panel:before{
      content:"";
      position:absolute;
      inset:10px;
      border:1px solid var(--line-warm);
      pointer-events:none;
    }
    .not-found-code{
      margin:22px 0 8px;
      color:var(--orange);
      font:clamp(88px,22vw,210px)/.82 var(--display);
      letter-spacing:-.08em;
      text-shadow:7px 7px 0 rgba(0,0,0,.4);
    }
    .not-found-code span{color:var(--paper)}
    .not-found h1{
      margin:0;
      color:var(--pink);
      font:clamp(18px,3.2vw,30px)/1.2 var(--display);
      text-transform:uppercase;
    }
    .not-found .stage-lede{margin-bottom:28px}
    .not-found .pixel-cta{display:inline-flex}
    @media(max-width:640px){
      .not-found{min-height:calc(100svh - 71px);padding:28px 0}
      .not-found-panel{padding:30px 22px 34px}
    }
  </style>
</head>
<body>
  <div class="crt-wash" aria-hidden="true"></div>
  <div class="solder-dust" aria-hidden="true"></div>

  <header class="command-bar">
    <div class="cmd-width command-rig">
      <div class="console-brand">
        <span class="brand-cat" aria-hidden="true"><i></i><b></b></span>
        <span class="brand-type">SOLDER<span>CATS</span></span>
      </div>
    </div>
  </header>

  <main class="not-found">
    <article class="not-found-panel">
      <p class="shell-line"><span class="prompt-token">$</span> rooftop_index.exe --path</p>
      <p class="not-found-code" aria-hidden="true">4<span>0</span>4</p>
      <h1>404 · Not found</h1>
      <p class="stage-lede">This path never made it onto the rooftop repair log. The workshop is still back at the front door.</p>
      <a class="pixel-cta pixel-cta-hot" href="/">Back to SOLDERCATS</a>
    </article>
  </main>
</body>
</html>
