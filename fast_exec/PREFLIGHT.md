# Pre-flight packet pattern — for every multi-step on-chain chain

Problem it solves: the old pattern interleaved verification reads, user
messages, and executions one tool call at a time, so a 3-step chain
(swap → approve → mint) took 8+ minutes even when every step was
healthy — and any stall pushed previews past their ~5 min expiry,
forcing re-previews. The RUNE genesis race (2026-10-30) was lost to
exactly this plus a 20-minute third-party outage, not to a bad preview.

## The pattern (mandatory for time-critical chains)

### Phase 0 — PRE-FLIGHT (one script run, BEFORE any preview)
Verify EVERYTHING and build EVERYTHING in a single run:
- trigger state (sold/phase/minting open, from a raced read)
- session alive (wallet + any API token; re-login FIRST if missing)
- balances cover every step + gas reserve
- allowances / quotas / eligibility for every step
- ALL calldata for every step, built programmatically (never hand-typed)
- print the packet: values, calldata, and what each preview must show

Use `~/workspace/fast_exec/fast_rpc.py` for the reads: `batch()` for
independent reads (1 HTTP request), `race()` for anything that must
not wait on a sick endpoint (8s timeout, first success wins).

### Phase 1 — EXECUTION (preview → execute pairs, back-to-back)
- No verification gaps between steps, no user message between steps
  unless a step blocks (dirty preview, 351803/351805, tap demand).
- Execute each preview within ~2 minutes of creating it (expiry ~5 min).
- Receipt check: poll every 5s (not 10s), max ~6 polls, then move on —
  the next step's preview does not need the previous receipt if the
  step is independent (but a dependent step MUST see its receipt first).
- If any step blocks: stop the chain, report once, leave later steps
  unexecuted. Never execute a later step to "make up" for a blocked one.

### Retry discipline
- Instant failure (error in <60s, no tap in flight) → retry in 10s.
- Tap-timeout failure (~3 min poll exhausted) → retry in 30s.
- API/RPC timeout: 8-10s per attempt when racing, never 25-40s.
- A retry loop that only BUILDS (never executes) may run in the
  background; execution itself stays in the foreground turn, exactly
  once, after the preview check.

## What this pattern NEVER changes
- Every execution still gets its own strict scan + clean preview first.
- Every execution still needs its own explicit permission (or an
  applicable narrow pre-authorization).
- Guards (quotas, caps, no pool-price fallback, 351803 = stop) are
  never waived for speed. Speed comes from transport, parallelism,
  and preparation — never from skipped checks.
- What cannot be sped up, honestly: the user's Binance app tap, chain
  confirmations (~3s/block), preview expiry, and a third-party outage.
  Those are reported, not hidden, and never circumvented.
