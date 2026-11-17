# Deep Screening Tools — Project Free Bacot

Installed 2026-11-01 ~18:57 WIB at user order ("cari alat yang kamu butuhkan di
berbagai sumber terbuka") because routine monitoring kept missing projects.
These tools deepen and sharpen screening; they NEVER replace the standing
gates, the strict scan + clean preview, or per-step permission. A tool result
is evidence, not a verdict.

## 1. GoPlus token_security — contract + distribution in one call

- Helper: `~/workspace/fast_exec/goplus_check.py <bsc-address> [...]`
- API: `https://api.gopluslabs.io/api/v1/token_security/56?contract_addresses=<addr>`
  Free, no key. Tested live 2026-11-01 on SENSEI + BNBS NEW.
- What it returns (use for gates): `is_honeypot`, `is_open_source`, `is_proxy`,
  `is_mintable`, `hidden_owner`, `can_take_back_ownership`, `transfer_pausable`,
  `is_blacklisted`, `selfdestruct`, `cannot_buy`, `cannot_sell_all`,
  `buy_tax` / `sell_tax` (simulation-derived), `holder_count`, top-10 %,
  top-10 % ex-burn, LP-burn %, dex pair + liquidity, creator address.
- Null rules (do not misread):
  - Closed source (`is_open_source=0`) → other risk fields are null BY DESIGN.
    Null is not safe.
  - Proxy (`is_proxy=1`) → honeypot field may be null; upgrade risk applies.
  - Empty tax fields → no simulated trade available; tax is UNVERIFIED, never 0.
- Live examples (2026-11-01): SENSEI — honeypot 0, proxy 0, mintable 1,
  buy 1% / sell 2%, holders 5.463, top-10 49% raw / 28,71% ex-burn,
  LP burn 99,53%. BNBS NEW — honeypot 0, proxy 0, mintable 0, taxes empty
  (unverified), holders 877, pair confirmed as the known NEW/WBNB pair.
- Gate mapping: contract gate (honeypot/proxy/owner powers) + distribution
  gate (top-10 ex-burn, holder count) + sell-path tax cross-check. It does
  NOT replace the Binance audit disclosure or the preview simulation.

## 2. token-safety-scanner (open source, MIT, Bob-QoQ)

- Installed verbatim at `~/workspace/custom-skills/token-safety-scanner/`
  (scanner + adapters + SKILL.md + README + tests; `.git` not copied).
- Code audit before install: only two network destinations — GoPlus
  (`api.gopluslabs.io`) and Binance Web3 public API (`web3.binance.com`);
  no keys, no env access, `requirements.txt` is only `requests`.
- Use: `python main.py --address 0x... --chain bsc --json` for a 0-100 risk
  score + flags (contract audit + holder concentration + smart-money inflow
  via Binance Web3). Treat its score as a second opinion, never as a gate
  override. Its Binance smart-money step is supplementary (same rule as KOL:
  supplementary only, never a buy signal).

## 3. PancakeSwap V2 PairCreated pioneer scan (new-pair discovery)

- Helper: `~/workspace/narrative-pulse/paircreated_scan.py [lookback_blocks]`
  (default 5000 ≈ 4 jam). State: `~/workspace/narrative-pulse/paircreated_state.json`.
- Method: Ankr `getLogs` on the V2 factory
  (`0xca143ce32fe78f1f7019d7d551a6402fc5350c73`) — the factory emits only
  PairCreated, so address filtering IS the pair scan. Decodes token0
  (topic1), token1 (topic2), pair (data word 0). PairCreated selector
  `0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9`.
- CRITICAL QUIRK: the Ankr CLI truncates output at 4000 chars, which breaks
  JSON parsing. This script imports `get_logs` as a module instead — never
  call the CLI for log scans.
- Baseline run 2026-11-01 ~18:58 WIB: 392 new pairs in the 5000-block window
  (most are token-token pairs; filter to WBNB pairs for memecoin relevance).
  Future runs print only pairs newer than the state watermark.
- Use: pioneer/discovery signal for the narrative + free-mint discovery legs
  (a new pair's block time is a verifiable launch-time anchor). A new pair is
  NOT a candidate by itself — it still needs the full Free Bacot gates
  (48h age, ≥50%, rising velocity, X signal, free quota).

## Deliberately NOT adopted

- honeypot.is direct API: endpoint not verified against its official docs in
  this pass, so not wired. GoPlus + preview simulation already cover the
  sellability question; revisit only with a docs-verified endpoint.
- Binance onchain copy-trader skill: a copy-trading scaffold, out of scope
  for free-mint screening (copying others is not screening).
- BscScan API: needs a free API key the user has not provided. Optional
  future addition if the user wants verified-source checks beyond Sourcify.
  Do not ask for it unprompted; Sourcify + GoPlus + on-chain reads suffice.
- Any tool requiring a paid key, a login, or a wallet connection: out of
  scope. All three tools above are free and keyless (Ankr uses the existing
  registered connection).

## Miss causes these tools address (from the 2026-10-29 diagnosis)

- Supply-view gaps → GoPlus holder/dex data + the totalMinted adapter
  (separate change, 2026-11-01).
- Slow/walled discovery sources → PairCreated log scan (on-chain, no wall,
  no polling delay beyond block time) + GoPlus (no key, no wall).
- Weak contract/distribution evidence → GoPlus flags + concentration in one
  call, instead of scattered reads.
- What they do NOT fix: X sign-in walls (twitterapi.io credits remain the
  binding constraint), and the 30-minute routine cadence itself (a cadence
  change still needs its own user confirmation).
