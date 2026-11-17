# Screening routes — verified 2026-11-04 ~23:00 WIB

Durable notes on which screening routes actually work in this VM, so future
sessions don't re-learn them by failing.

## BSC RPC rotation (use all three, never one alone)
- https://bsc-dataseed1.ninicoin.io — working
- https://bsc-dataseed1.bnbchain.org — working
- https://bsc-dataseed.binance.org — flaky (403 at times, working at others)
- https://bnbchain.api.onfinality.io/public — empty responses, do not use
- https://bsc.publicnode.com — rate-limited (-32005)
- https://rpc.ankr.com/bsc — needs API key (use the Ankr module instead)

## GeckoTerminal (free, no key) — BSC legs that work
- Trending pools: https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools
- New pools: https://api.geckoterminal.com/api/v2/networks/bsc/new_pools
- Note: trending mixes established tokens with movers; it is NOT a new-launch
  feed — new_pools is the fresh-launch leg.

## Dexscreener (free, no key) — caveat
- /token-boosts/top/v1, /token-boosts/latest/v1, /token-profiles/latest/v1
  work, but boosts/profiles are global paid-promotion slots: on 2026-11-04
  they returned 0 BSC entries (Solana/Robinhood dominated). An empty result
  there is NOT "no BSC activity" — use GeckoTerminal for BSC instead.

## four.meme — browser route only
- Direct API guesses (meme-api/v1/token-list, token/list) return the SPA HTML
  shell, not data. Use a live browser task on https://four.meme/en (board is
  public: no login, no wallet connect, no signing needed to read listings).
- Board columns: COIN, MCAP, PROGRESS (bonding curve), AGE, 24 VOL,
  HOLDERS, 5M/1H/4H/24H changes. Per-token price is NOT shown on the board,
  only MCAP. Sorts: Featured (default) and Creation Time (?orderBy=TimeDesc).
- Warning patterns seen 2026-11-04: same-name duplicate contracts (one
  momentum name + several ~$3.2k clones), high-holder zero-volume tokens
  (holder counts can be farmed), and name-family crash clusters (-85% and
  worse in 24h). A name match alone is never identity — verify the contract.

## X access
- twitterapi.io: credits exhausted (402 since 2026-11-02). Top-up was
  declined by the user 2026-11-03; do NOT top up without an explicit new
  approval covering the spend.
- Live browser read of x.com profiles without login works and is the
  fallback (used by the flap.sh safety watch for @flapdotsh).

## Known unfixable gaps (do not re-promise)
- Boltbook DNS fails persistently from this VM (DNS_PROBE_STARTED); it is an
  infrastructure gap, not a code fix. boltbook.fun substitution is
  unverified — never treat it as Boltbook.
- OKX login is impossible in this VM (proven); OKX DEX needs a route check
  (public API or logged-out browser read), not a login retry.
- VM-browser Google login was rejected 2026-10-31 — do NOT retry it.
- Speed: the fastest loops here run in minutes (cron/browser), never
  seconds. Tool fixes cut lag from tens of minutes to minutes, not to
  seconds.

## OKX DEX / Binance DEX route check — 2026-11-04 ~23:05 WIB
- OKX DEX aggregator quote API without a key returns code 50103
  ("OK-ACCESS-KEY can not be empty"). API route needs an OKX API key the
  user has not provided; do NOT invent one. Browser route (logged-out read
  of OKX Web3 pages) is untested, not assumed working.
- Binance classic DEX API (dex.binance.org) returned rate-limit; it is also
  a deprecated Beacon Chain venue, not a BSC degen source — low value even
  if it recovers.
- Binance CEX endpoints from this VM are geo-blocked ("Service unavailable
  from a restricted location", same as the earlier api.binance.com 451).
  No clean Binance route from this VM; do not propose geo circumvention.
- Net: as free legs, OKX DEX and Binance DEX are NOT addable right now.
  OKX needs a user-provided API key (secure flow); Binance needs the user
  to say which Binance surface they meant, and it may still be geo-blocked.
