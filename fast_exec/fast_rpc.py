#!/usr/bin/env python3
"""fast_rpc.py — fast BSC JSON-RPC reads for time-critical work.

Techniques (from open sources: JSON-RPC batching, endpoint racing,
connection reuse / keep-alive, concurrent requests):
  1. RACE — the same request is fired at all dataseeds concurrently and
     the first success wins. A dead/slow endpoint costs ~0 extra instead
     of a full sequential timeout (the old pattern paid 25-40s per dead
     endpoint before trying the next one).
  2. BATCH — many independent eth_call / read requests go out as ONE
     JSON-RPC batch array in a single HTTP request (1 round trip, not N).
  3. KEEP-ALIVE — one persistent HTTPS connection per (thread, host),
     reused across calls, so later calls skip TCP+TLS handshakes.
  4. SHORT TIMEOUTS — 8s per endpoint when racing (a healthy BSC call
     answers in <2s); a timeout is treated as "that endpoint is sick",
     not as "the chain is down".

Stdlib only (http.client + threads): nothing to reinstall after a VM
wipe. This module is READ-ONLY — it never signs, approves, or sends a
transaction. Previews/execution still go through baw with their own
clean-preview check; speed here never skips a safety step.

Usage as a script:
  python3 fast_rpc.py balance <address>
  python3 fast_rpc.py block
  python3 fast_rpc.py call <to> <hexdata>
  python3 fast_rpc.py batch-demo     # 3 reads, 1 HTTP request, timed
  python3 fast_rpc.py race-demo      # race vs sequential, incl. dead endpoint
  python3 fast_rpc.py benchmark      # full comparison table

As a module:
  from fast_rpc import race, batch, call_many
  bal = race("eth_getBalance", [wallet, "latest"])
  res = call_many([("0x..usdt", "0x70a08231" + wallet_padded), ...])
"""
import base64
import http.client
import json
import socket
import ssl
import sys
import threading
import time
import urllib.parse

ENDPOINTS = [
    # Primary: official dataseeds (kept first for backward compat).
    "https://bsc-dataseed.binance.org/",
    "https://bsc-dataseed1.bnbchain.org/",
    "https://bsc-dataseed1.defibit.io/",
    # Added 2026-11-01 (infra hardening step 1): independent providers so
    # one family's outage no longer kills all reads. Health state (below)
    # decides who is actually used; a listed-but-dead endpoint costs
    # nothing because the circuit breaker skips it.
    "https://bsc-dataseed2.bnbchain.org/",
    "https://bsc-dataseed3.bnbchain.org/",
    "https://bsc-dataseed4.bnbchain.org/",
    "https://bsc-dataseed-public.bnbchain.org/",
    "https://bsc-rpc.publicnode.com/",
    "https://bsc.nodereal.io/",
    "https://bsc.drpc.org/",
    "https://bnb.api.onfinality.io/public/",
]

# --- Circuit breaker + health state (added 2026-11-01) -------------------
# An endpoint that fails BREAKER_THRESHOLD times in a row is "open"
# (skipped) for BREAKER_COOLDOWN seconds. State persists across processes
# in endpoint_health.json so a breaker tripped by one cron tick still
# protects the next tick; a stale file (>10 min) is ignored. Writes are
# atomic (tmp + rename) and best-effort: a corrupt/missing file must
# never break a read. In-memory state is authoritative inside a process.
import os as _os

HEALTH_FILE = _os.path.expanduser("~/workspace/fast_exec/endpoint_health.json")
BREAKER_THRESHOLD = 3
BREAKER_COOLDOWN = 60
_HEALTH = {}  # url -> {"fails": int, "open_until": float, "latency": float|None, "block": int|None}


def _load_health():
    try:
        if not _os.path.exists(HEALTH_FILE):
            return
        if time.time() - _os.path.getmtime(HEALTH_FILE) > 600:
            return
        data = json.load(open(HEALTH_FILE))
        for url, st in (data or {}).items():
            if isinstance(st, dict):
                _HEALTH[url] = st
    except Exception:
        pass


def _save_health():
    try:
        tmp = HEALTH_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(_HEALTH, f)
        _os.replace(tmp, HEALTH_FILE)
    except Exception:
        pass


def _breaker_open(url, now=None):
    st = _HEALTH.get(url)
    if not st:
        return False
    return (st.get("fails", 0) >= BREAKER_THRESHOLD
            and (now or time.time()) < st.get("open_until", 0))


def _note_result(url, ok, latency=None, block=None):
    """Record one outcome; persist only on a breaker transition so a
    hot read path does not churn the file on every call."""
    st = _HEALTH.setdefault(url, {"fails": 0, "open_until": 0,
                                  "latency": None, "block": None})
    was_open = _breaker_open(url)
    if ok:
        st["fails"] = 0
        st["open_until"] = 0
        if latency is not None:
            st["latency"] = latency
        if block is not None:
            st["block"] = block
    else:
        st["fails"] = st.get("fails", 0) + 1
        if st["fails"] >= BREAKER_THRESHOLD:
            st["open_until"] = time.time() + BREAKER_COOLDOWN
    if was_open != _breaker_open(url):
        _save_health()


def healthy_endpoints(endpoints=None):
    """Endpoints in preference order: closed breakers first, fastest
    known latency first, unknown-latency last. Open breakers are
    excluded unless that would leave nothing."""
    _load_health()
    eps = list(endpoints or ENDPOINTS)
    now = time.time()
    closed = [e for e in eps if not _breaker_open(e, now)]
    pool = closed if closed else eps
    pool.sort(key=lambda e: (_HEALTH.get(e, {}).get("latency")
                             if _HEALTH.get(e, {}).get("latency") is not None
                             else float("inf")))
    return pool


def health_check(endpoints=None, timeout=4):
    """Probe every endpoint with eth_blockNumber (short timeout) and
    return a list of {endpoint, ok, block, lag, latency_ms}. `lag` is
    blocks behind the highest block seen in this probe; an endpoint
    more than 5 blocks behind is reported unhealthy for tip reads.
    This updates the breaker state: ok resets fails, failure counts."""
    _load_health()
    eps = list(endpoints or ENDPOINTS)
    results = {}
    threads = []

    def probe(ep):
        t0 = time.time()
        try:
            r = _single(ep, "eth_blockNumber", [], timeout, retries=0)
            blk = _fmt_wei_hex(r)
            results[ep] = (True, blk, (time.time() - t0) * 1000)
        except Exception:
            results[ep] = (False, None, (time.time() - t0) * 1000)

    for ep in eps:
        threading.Thread(target=probe, args=(ep,), daemon=True).start()
    deadline = time.time() + timeout + 2
    while len(results) < len(eps) and time.time() < deadline:
        time.sleep(0.05)
    best = max([v[1] for v in results.values() if v[0]] or [0])
    out = []
    for ep in eps:
        ok, blk, ms = results.get(ep, (False, None, None))
        if ok and best and best - blk > 5:
            ok = False  # too far behind the tip to trust for fresh reads
        _note_result(ep, ok, latency=ms if ok else None,
                     block=blk if ok else None)
        out.append({"endpoint": ep, "ok": ok, "block": blk,
                    "lag": (best - blk) if (ok and blk is not None) else None,
                    "latency_ms": round(ms, 1) if ms is not None else None})
    _save_health()
    return out

# Per-thread connection cache: {host: HTTPSConnection}. http.client
# connections are not thread-safe, so each racing thread keeps its own.
_tls = threading.local()

# Generous-but-bounded timeouts. Healthy BSC answers in <2s; 8s already
# means "sick endpoint" — do not wait 25-40s for it.
RACE_TIMEOUT = 8
BATCH_TIMEOUT = 15


class _ProxiedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPSConnection that tunnels through the sandbox egress proxy
    (CONNECT + TLS wrap). Plain http.client ignores proxy env vars and
    fails in this environment; urllib works only because it honors
    them. This class keeps the persistent-connection benefit while
    routing correctly."""

    def __init__(self, host, proxy_host, proxy_port, proxy_auth,
                 timeout, context):
        super().__init__(host, timeout=timeout, context=context)
        self._proxy = (proxy_host, proxy_port)
        self._proxy_auth = proxy_auth

    def connect(self):
        self.sock = socket.create_connection(self._proxy,
                                             timeout=self.timeout)
        req = (f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
               f"Host: {self.host}:{self.port}\r\n")
        if self._proxy_auth:
            req += f"Proxy-Authorization: {self._proxy_auth}\r\n"
        req += "Proxy-Connection: Keep-Alive\r\n\r\n"
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise IOError("proxy CONNECT closed")
            buf += chunk
        status = buf.split(b"\r\n", 1)[0].decode(errors="replace")
        if " 200 " not in status:
            raise IOError(f"proxy CONNECT failed: {status}")
        self.sock = self._context.wrap_socket(self.sock,
                                              server_hostname=self.host)


def _proxy_conf(host):
    """(proxy_host, proxy_port, auth_header|None) or None for direct.
    Honors https_proxy/HTTPS_PROXY and no_proxy like urllib does."""
    import os
    proxy_url = (os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY")
                 or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY"))
    if not proxy_url:
        return None
    no_proxy = os.environ.get("no_proxy") or os.environ.get("NO_PROXY") or ""
    for pat in [p.strip() for p in no_proxy.split(",") if p.strip()]:
        if pat == "*" or host == pat or host.endswith(pat.lstrip(".")):
            return None
    p = urllib.parse.urlparse(proxy_url)
    auth = None
    if p.username:
        user = urllib.parse.unquote(p.username)
        pw = urllib.parse.unquote(p.password or "")
        auth = "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()
    return (p.hostname, p.port or 3128, auth)


def _conn(url):
    """Persistent HTTPS connection for this thread + host (keep-alive),
    via the egress proxy when one is configured."""
    p = urllib.parse.urlparse(url)
    cache = getattr(_tls, "conns", None)
    if cache is None:
        cache = _tls.conns = {}
    c = cache.get(p.netloc)
    if c is None:
        pc = _proxy_conf(p.hostname)
        if pc:
            c = _ProxiedHTTPSConnection(
                p.hostname, pc[0], pc[1], pc[2],
                timeout=RACE_TIMEOUT, context=ssl.create_default_context())
        else:
            c = http.client.HTTPSConnection(
                p.hostname, timeout=RACE_TIMEOUT,
                context=ssl.create_default_context())
        cache[p.netloc] = c
    return c, (p.path or "/")


def _post(url, payload, timeout, retries=1):
    """One JSON-RPC POST over a reused connection. Returns parsed JSON
    or raises. A stale pooled connection is retried once on a fresh one
    (retries=1); racing callers pass retries=0 because the race itself
    is the redundancy — retrying inside a race doubles its tail."""
    body = payload if isinstance(payload, str) else json.dumps(payload)
    for attempt in range(retries + 1):
        c, path = _conn(url)
        # http.client timeout is fixed at connect time; the socket
        # timeout applies per operation, good enough for our bound.
        try:
            c.request("POST", path, body=body,
                      headers={"Content-Type": "application/json"})
            r = c.getresponse()
            raw = r.read()
            if r.status != 200:
                raise IOError(f"HTTP {r.status}")
            return json.loads(raw)
        except Exception:
            # Drop the (possibly stale) connection and retry once.
            try:
                c.close()
            except Exception:
                pass
            _tls.conns.pop(urllib.parse.urlparse(url).netloc, None)
            if attempt == retries:
                raise


def _single(url, method, params, timeout, retries=1):
    out = _post(url, {"jsonrpc": "2.0", "id": 1, "method": method,
                      "params": params}, timeout, retries=retries)
    if isinstance(out, dict) and out.get("error"):
        raise IOError(f"RPC error: {out['error']}")
    return out["result"]


def race(method, params, endpoints=None, timeout=RACE_TIMEOUT):
    """Fire one request at every endpoint concurrently; return the
    first success. Raises only if ALL endpoints fail. Daemon threads
    + a queue (NOT ThreadPoolExecutor's `with` block, whose shutdown
    waits for the slowest thread — that bug made a race as slow as
    the dead endpoint it was supposed to beat). Overall bound:
    timeout + 2s; losers are abandoned, never waited on."""
    import queue as queue_mod
    # Prefer healthy endpoints (circuit breaker + latency order); if the
    # caller pinned an explicit list, respect it but still drop breakers
    # unless that would leave nothing to try.
    eps = healthy_endpoints(endpoints) if endpoints is None \
        else healthy_endpoints(endpoints)
    q = queue_mod.Queue()
    errs = []
    n = len(eps)

    def worker(ep):
        t0 = time.time()
        try:
            val = _single(ep, method, params, timeout, retries=0)
            _note_result(ep, True, latency=(time.time() - t0) * 1000)
            q.put(("ok", val))
        except Exception as e:
            _note_result(ep, False)
            q.put(("err", f"{ep}: {type(e).__name__}"))

    for ep in eps:
        threading.Thread(target=worker, args=(ep,), daemon=True).start()
    deadline = time.time() + timeout + 2
    seen_err = 0
    while True:
        left = deadline - time.time()
        if left <= 0:
            raise IOError("race timed out: " + "; ".join(errs))
        try:
            kind, val = q.get(timeout=left)
        except queue_mod.Empty:
            raise IOError("race timed out: " + "; ".join(errs))
        if kind == "ok":
            return val
        errs.append(val)
        seen_err += 1
        if seen_err >= n:
            raise IOError("all endpoints failed: " + "; ".join(errs))


def batch(calls, endpoint=None, timeout=BATCH_TIMEOUT):
    """Send many requests as ONE JSON-RPC batch array. `calls` is a list
    of (method, params). Returns results in call order; a failed item
    raises IOError naming its index (fail-fast keeps semantics simple —
    callers that need partial results should split the batch)."""
    # Batch goes to ONE endpoint per attempt (a batch is a single HTTP
    # request), but it now walks the healthy list instead of always
    # hitting ENDPOINTS[0]: if the first healthy endpoint rejects the
    # batch, the next healthy one is tried. An explicitly pinned
    # endpoint is still tried first.
    candidates = ([endpoint] if endpoint else healthy_endpoints())
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
               for i, (m, p) in enumerate(calls)]
    last_err = None
    for ep in candidates:
        try:
            out = _post(ep, payload, timeout)
            if not isinstance(out, list) or len(out) != len(calls):
                raise IOError(f"unexpected batch response: {str(out)[:200]}")
            by_id = {}
            for item in out:
                if isinstance(item, dict) and item.get("error"):
                    raise IOError(f"batch item {item.get('id')} error: "
                                  f"{item['error']}")
                by_id[item["id"]] = item["result"]
            _note_result(ep, True)
            return [by_id[i + 1] for i in range(len(calls))]
        except Exception as e:
            _note_result(ep, False)
            last_err = e
            continue
    raise IOError(f"batch failed on all healthy endpoints: {last_err}")


def call_many(calls, timeout=BATCH_TIMEOUT):
    """Many eth_calls in one batch. `calls` = list of (to, hexdata).
    Falls back to racing each call individually if batching is rejected
    (some nodes cap batch size or disable it)."""
    try:
        return batch([("eth_call", [{"to": to, "data": data}, "latest"])
                      for to, data in calls], timeout=timeout)
    except Exception:
        return [race("eth_call", [{"to": to, "data": data}, "latest"])
                for to, data in calls]


def batch_race(calls, timeout=BATCH_TIMEOUT, max_endpoints=4):
    """Fire the SAME JSON-RPC batch at several endpoints concurrently;
    return the first complete success. Like race() but for a whole batch.

    Why: batch() walks endpoints SEQUENTIALLY — one slow-but-alive
    endpoint can stall a batch ~15s (observed 20.5s for a 5-call BAGENT
    batch on 2026-11-12, vs 2.7-6.6s when the first endpoint was fast).
    In an FCFS race that variance alone can lose the quota. Racing the
    batch makes it as fast as the quickest endpoint, every time.
    Daemon threads + queue, losers abandoned (same pattern as race()).
    Raises only if ALL endpoints fail."""
    import queue as queue_mod
    eps = healthy_endpoints()[:max_endpoints]
    if not eps:
        raise IOError("batch_race: no healthy endpoints")
    q = queue_mod.Queue()
    errs = []
    n = len(eps)

    def worker(ep):
        try:
            val = batch(calls, endpoint=ep, timeout=timeout)
            q.put(("ok", val))
        except Exception as e:
            q.put(("err", f"{ep}: {type(e).__name__}"))

    for ep in eps:
        threading.Thread(target=worker, args=(ep,), daemon=True).start()
    deadline = time.time() + timeout + 2
    seen_err = 0
    while True:
        left = deadline - time.time()
        if left <= 0:
            raise IOError("batch_race timed out: " + "; ".join(errs))
        try:
            kind, val = q.get(timeout=left)
        except queue_mod.Empty:
            raise IOError("batch_race timed out: " + "; ".join(errs))
        if kind == "ok":
            return val
        errs.append(val)
        seen_err += 1
        if seen_err >= n:
            raise IOError("batch_race all endpoints failed: " + "; ".join(errs))


def _fmt_wei_hex(v):
    return int(v, 16) if v else 0


# ---------------------------------------------------------------- CLI --
def _cli(argv):
    if len(argv) >= 3 and argv[1] == "balance":
        t0 = time.time()
        r = race("eth_getBalance", [argv[2], "latest"])
        print(f"balance: {_fmt_wei_hex(r)/1e18} BNB ({time.time()-t0:.2f}s)")
    elif len(argv) >= 2 and argv[1] == "block":
        t0 = time.time()
        r = race("eth_blockNumber", [])
        print(f"block: {_fmt_wei_hex(r)} ({time.time()-t0:.2f}s)")
    elif len(argv) >= 4 and argv[1] == "call":
        t0 = time.time()
        r = race("eth_call", [{"to": argv[2], "data": argv[3]}, "latest"])
        print(f"call: {r} ({time.time()-t0:.2f}s)")
    elif len(argv) >= 2 and argv[1] == "health":
        rows = health_check()
        for r in rows:
            flag = "OK " if r["ok"] else "DOWN"
            lat = (f"{r['latency_ms']}ms"
                   if r['latency_ms'] is not None else "timeout")
            print(f"{flag} {r['endpoint']} block={r['block']} "
                  f"lag={r['lag']} latency={lat}")
        print(f"healthy: {sum(1 for r in rows if r['ok'])}/{len(rows)}")
    elif len(argv) >= 2 and argv[1] == "batch-demo":
        w = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
        usdt = "0x55d398326f99059fF775485246999027B3197955"
        t0 = time.time()
        bal, blk, dec = batch([
            ("eth_getBalance", [w, "latest"]),
            ("eth_blockNumber", []),
            ("eth_call", [{"to": usdt, "data": "0x313ce567"}, "latest"]),
        ])
        dt = time.time() - t0
        print(f"batch (3 reads, 1 HTTP request): {dt:.2f}s")
        print(f"  BNB balance: {_fmt_wei_hex(bal)/1e18}")
        print(f"  block: {_fmt_wei_hex(blk)} | USDT decimals: {_fmt_wei_hex(dec)}")
        t0 = time.time()
        for m, p in [("eth_getBalance", [w, "latest"]), ("eth_blockNumber", []),
                     ("eth_call", [{"to": usdt, "data": "0x313ce567"}, "latest"])]:
            race(m, p)
        print(f"same 3 reads, raced one-by-one: {time.time()-t0:.2f}s")
    elif len(argv) >= 2 and argv[1] == "race-demo":
        dead = "https://10.255.255.1/"  # non-routable: hangs, then times out
        eps = [dead] + ENDPOINTS
        t0 = time.time()
        r = race("eth_blockNumber", [], endpoints=eps, timeout=8)
        print(f"race with 1 dead + 3 live endpoints: {time.time()-t0:.2f}s "
              f"-> block {_fmt_wei_hex(r)}")
        # Sequential old pattern, same 8s timeout, dead endpoint first.
        # (The true old pattern had NO per-endpoint retry — just
        # sequential fallback — so retries=0 here keeps it honest.)
        t0 = time.time()
        got = None
        for ep in eps:
            try:
                got = _single(ep, "eth_blockNumber", [], 8, retries=0)
                break
            except Exception as e:
                print(f"  sequential: {ep} failed ({type(e).__name__})")
        print(f"sequential old pattern: {time.time()-t0:.2f}s "
              f"-> block {_fmt_wei_hex(got) if got else '?'}")
    elif len(argv) >= 2 and argv[1] == "benchmark":
        w = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
        usdt = "0x55d398326f99059fF775485246999027B3197955"
        calls = [("eth_getBalance", [w, "latest"]), ("eth_blockNumber", []),
                 ("eth_call", [{"to": usdt, "data": "0x313ce567"}, "latest"])]
        t0 = time.time()
        for m, p in calls:
            race(m, p)
        t_race = time.time() - t0
        t0 = time.time()
        batch(calls)
        t_batch = time.time() - t0
        print(f"3 reads raced one-by-one : {t_race:.2f}s")
        print(f"3 reads as ONE batch     : {t_batch:.2f}s")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
