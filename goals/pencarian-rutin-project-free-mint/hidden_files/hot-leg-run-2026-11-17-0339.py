#!/usr/bin/env python3
# TEMPLATE NOTE (2026-11-17 03:39): PREV_REREAD/PREV_RUN below point at THIS run's
# own 0339 files as the last-good baseline (the 0334 files were overwritten by a
# sed slip in this run and deleted; 0334-vs-0339 comparison ran before the
# overwrite and found ZERO value changes). When cloning for the next run, update
# RUN_TAG/NOW/output filenames to the new time, and set PREV_* to 0339 (do NOT
# global-sed 0339->newtime, or PREV will self-reference and change detection
# will silently report no changes).
"""Hot-leg run 2026-11-17 03:39 WIB (scheduled 03:34:38).
Legs: (1) Sourcify feed via direct curl + ABI shape-check of any new
S1/S2 (Sourcify ABI API); (2) Boltbook EN + ZH via direct curl -L;
(3) on-chain verify of any new sale-shape hit (only if one appears);
(4) focus re-read of the 25-entry active set (23 focus + LEGBEE + PEPE)
vs 0334 reads, plus BSCCat probe, chunked direct JSON-RPC batches of 20
to bsc-dataseed3 (fast_rpc race timed out + 429s on 0324 run - NOT used);
bridge read-only. Read-only except hot-leg-seen.json (own file) + run
JSONs. No preview/mint/claim."""
import json, re, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = "2026-11-17T03:39+07:00"
RUN_TAG = "free-mint-hot-leg 2026-11-17 03:39 WIB"
PREV_REREAD = "hot-leg-run-2026-11-17-0339-reread.json"
PREV_RUN = "hot-leg-run-2026-11-17-0339.json"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
EPS = ["https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
BSCCAT = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"
t0 = time.time()

def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

def curl_json(url, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                         capture_output=True, text=True, timeout=timeout + 10)
    return out.stdout, out.returncode

def curl_bytes(url, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                         capture_output=True, timeout=timeout + 10)
    return out.stdout, out.returncode

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
seen_n0 = len(seen)

# (1) Sourcify feed
feed_addrs, feed_meta, feed_err = [], [], None
try:
    raw, rc = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 30)
    data = json.loads(raw)
    items = data if isinstance(data, list) else data.get("results", data)
    for it in items[:20]:
        a = it.get("address") if isinstance(it, dict) else None
        if a:
            feed_addrs.append(a)
            feed_meta.append({"address": a, "verifiedAt": it.get("verifiedAt"),
                              "match": it.get("match")})
    log("feed", len(feed_addrs), "top", feed_addrs[0] if feed_addrs else None,
        feed_meta[0] if feed_meta else None)
except Exception as e:
    feed_err = f"{type(e).__name__}: {str(e)[:120]}"
    log("feed ERROR", feed_err)
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in {e.lower() for e in EXCLUDED}]
log("feed new:", feed_new)

# (2) Boltbook EN + ZH
def boltbook(url):
    try:
        raw, rc = curl_bytes(url, 30)
        text = raw.decode("utf-8", "ignore")
        addrs = []
        for m in re.finditer(r"0x[0-9a-fA-F]{40}", text):
            a = m.group(0)
            if a not in addrs:
                addrs.append(a)
        return {"bytes": len(raw), "http_code": "200" if rc == 0 and raw else "?", "error": None,
                "addresses": addrs}
    except Exception as e:
        return {"bytes": 0, "http_code": None, "error": f"{type(e).__name__}: {str(e)[:100]}",
                "addresses": []}
en = boltbook("https://boltbook.fun/")
zh = boltbook("https://boltbook.fun/?lang=zh")
log("boltbook EN", en["bytes"], "addrs", len(en["addresses"]), en["addresses"])
log("boltbook ZH", zh["bytes"], "addrs", len(zh["addresses"]), zh["addresses"])
bb_all = en["addresses"] + [a for a in zh["addresses"] if a not in en["addresses"]]
bb_new = [a for a in bb_all if a.lower() not in seen_l
          and a.lower() not in {e.lower() for e in EXCLUDED}]
log("boltbook new:", bb_new)

# (3) shape-check any new contracts (feed + boltbook)
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freessharesclaimed", "freeminted",
              "freesharesleft", "freesharesclaimed"}
def shape_check(addr):
    try:
        raw, rc = curl_json(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 30)
        d = json.loads(raw)
        abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
        if not abi:
            return {"address": addr, "S1": False, "S2": False,
                    "status": "no-abi-from-sourcify"}
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns[e.get("name", "").lower()] = e
        names = set(fns)
        has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "buy", "purchase")
                       for n in names)
        has_quote = bool(names & {"cost", "quote", "costof", "bnbquote", "price", "getcost"})
        has_free_view = bool(names & FREE_VIEWS)
        has_registry_fn = bool(names & {"agentregistry", "registry", "agentgate", "agentid"})
        has_token_meta = bool(names & {"name", "symbol", "decimals", "totalsupply"})
        has_mintfree = "mintfree" in names
        has_free_slots = bool(names & {"free_slots", "free_supply", "free_slots", "freeslots",
                                       "freesupply", "free_amount", "freeamount"})
        s1 = has_mint and has_quote and has_free_view and has_registry_fn
        s2 = has_token_meta and has_mintfree and bool(names & {"freeclaimed", "freeminted"}) \
            and has_free_slots and has_registry_fn
        return {"address": addr, "S1": s1, "S2": s2,
                "status": f"fns={len(fns)} mint={has_mint} quote={has_quote} "
                          f"freeview={has_free_view} regfn={has_registry_fn} "
                          f"mintfree={has_mintfree} freeslots={has_free_slots}",
                "abi_fn_count": len(fns)}
    except Exception as e:
        return {"address": addr, "S1": False, "S2": False,
                "status": f"shape-check-error: {type(e).__name__}: {str(e)[:100]}"}

new_contracts = []
for a in feed_new + bb_new:
    if a.lower() not in {x.lower() for x in new_contracts}:
        new_contracts.append(a)
shape_out = [shape_check(a) for a in new_contracts]
hits = [s["address"] for s in shape_out if s.get("S1") or s.get("S2")]
for s in shape_out:
    log("shape", s["address"][:12], "S1", s.get("S1"), "S2", s.get("S2"), s.get("status"))
log("shape hits:", hits)

# ---- on-chain helpers (chunked direct JSON-RPC, batches of 20) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=45):
    out = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

def read_all(items, batch_size=20):
    """items: list of (name, addr, [(key, sig, args), ...]). Returns (reads, errors, block)."""
    calls, meta = [], []
    for name, addr, views in items:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    reads, errors = {}, []
    for bi in range(0, len(calls), batch_size):
        batch, bmeta = calls[bi:bi + batch_size], meta[bi:bi + batch_size]
        done = False
        for ep in EPS:
            try:
                res = post_rpc(ep, batch, timeout=45)
                if not isinstance(res, list) or len(res) != len(batch):
                    continue
                for it, (name, key) in zip(res, bmeta):
                    if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                        err = it.get("error") if isinstance(it, dict) else None
                        reads.setdefault(name, {})[key] = (
                            f"err:{err}" if err else None)
                    else:
                        r = it["result"]
                        reads.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
                done = True
                break
            except Exception as e:
                continue
        if not done:
            errors.append({"batch": bi // batch_size, "n": len(batch)})
            for name, key in bmeta:
                reads.setdefault(name, {})[key] = None
    return reads, errors

U = [USER]
ITEMS = [
 ("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0", [
    ("cost_user_1", "cost(address,uint256)", [USER, 1]),
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("AgentBubble", "0x0d72970046c056db90888351b739246f468bff0b", [
    ("freeMinted", "freeMinted()", []), ("totalSupply", "totalSupply()", []),
    ("totalMinted", "totalMinted()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("freeMinted", "freeMinted()", []), ("freeRemaining", "freeRemaining()", []),
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", [])]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("FREE_CAP", "FREE_CAP()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("BNBG", "0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [
    ("totalMinted", "totalMinted()", [])]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply", "totalSupply()", [])]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("freeUsed_user", "freeUsed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("BoldLeonidas", "0x84bcb8c16566e81ce902530c9da1e3de291f9941", [
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 ("CPASS", "0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("REOPIR", "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", [])]),
 ("RAVE", "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 ("MORFO", "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", [])]),
 ("AgentNOVA", "0x43462d7f269fde4914b03e1e07067a61b62b9540", [
    ("totalSupply", "totalSupply()", [])]),
 ("Zephyra", "0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted", "totalMinted()", [])]),
 ("Pengu", "0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 ("Kryntar", "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted", "totalMinted()", []), ("standardRemaining", "standardRemaining()", []),
    ("legendaryRemaining", "legendaryRemaining()", []), ("mintOpen", "mintOpen()", [])]),
 ("ONI", "0x99d01eD93829DBB0EEc11F3a733388c789dA6caD", [
    ("totalMinted", "totalMinted()", []), ("totalSupply", "totalSupply()", [])]),
 ("HAPPE", "0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 ("PIXELFROGS", "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("freeLeft", "freeLeft()", []), ("mintOpen", "mintOpen()", []),
    ("freeClaimed_user", "freeClaimed(address)", U)]),
 ("Flare-bd6f", "0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599", [
    ("totalSupply", "totalSupply()", [])]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft", "freeSharesLeft()", []), ("openedAt", "openedAt()", []),
    ("freeClaimed", "freeClaimed()", []),
    ("freeBooked_user", "freeBooked(address)", U)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", []), ("failed", "failed()", []),
    ("isRefundPhase", "isRefundPhase()", []), ("totalShares", "totalShares()", []),
    ("tokenClaimed_user", "tokenClaimed(address)", U)]),
 ("LEGBEE", "0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149", [
    ("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("MAX_SUPPLY", "MAX_SUPPLY()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 ("PEPE", "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980", [
    ("freeMinted", "freeMinted()", []), ("FREE_SHARES", "FREE_SHARES()", []),
    ("soldShares", "soldShares()", []), ("opened", "opened()", []),
    ("openedTime", "openedTime()", []), ("mintStartTime", "mintStartTime()", []),
    ("costOf_1", "costOf(uint256)", [1]),
    ("hasMinted_user", "hasMinted(address)", U)]),
]
BSCCAT_VIEWS = [
    ("totalMinted", "totalMinted()", []), ("soldShares", "soldShares()", []),
    ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
    ("freeSharesLeft", "freeSharesLeft()", []), ("FREE_SHARES", "FREE_SHARES()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("totalShares", "totalShares()", []),
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("opened", "opened()", []), ("poolOpen", "poolOpen()", []),
    ("isPoolOpen", "isPoolOpen()", []), ("launched", "launched()", []),
    ("hasMinted_user", "hasMinted(address)", U),
    ("freeClaimed_user", "freeClaimed(address)", U),
    ("freeUsed_user", "freeUsed(address)", U),
    ("freeLeft_user", "freeLeft(address)", U),
    ("mintedBy_user", "mintedBy(address)", U),
    ("quote_user_1", "quote(address,uint256)", [USER, 1]),
    ("cost_user_1", "cost(address,uint256)", [USER, 1]),
    ("costOf_1", "costOf(uint256)", [1]),
    ("bnbQuote_1", "bnbQuote(uint256)", [1]),
    ("token", "token()", []), ("TOKEN", "TOKEN()", []),
    ("balanceOf_user", "balanceOf(address)", U),
]
t_rpc = time.time()
reads, errors = read_all(ITEMS)
bsc_reads, bsc_errors = read_all([("BSCCat", BSCCAT, BSCCAT_VIEWS)])
bsc_out = bsc_reads.get("BSCCat")
# block number
blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                          "params": []}, timeout=30)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16); break
    except Exception:
        continue
log(f"reread {len(reads)} items, errors {errors}, bsccat errors {bsc_errors}, "
    f"block {blk}, rpc {time.time()-t_rpc:.1f}s")

# change detection vs 0334 reread
changes = []
try:
    prev = json.load(open(BASE + PREV_REREAD))
    prev_reads = prev.get("reads", {})
    addr_map = {n: a for n, a, _ in ITEMS}
    for name, cur in reads.items():
        pv = (prev_reads.get(name) or {}).get("views")
        cv = cur
        if pv is None or cv is None:
            if pv != cv:
                changes.append({"item": name, "type": "read-availability-change",
                                "prev": pv, "now": cv})
            continue
        diff = {k: {"prev": pv.get(k), "now": cv.get(k)}
                for k in set(pv) | set(cv) if pv.get(k) != cv.get(k)}
        if diff:
            changes.append({"item": name, "type": "value-change", "diff": diff})
except Exception as ex:
    changes.append({"item": "_meta", "type": "prev-compare-error", "error": str(ex)[:120]})
log("changes vs 0334:", json.dumps(changes)[:3000])

# threshold check (info only)
def pct(a, b):
    return round(100.0 * a / b, 1) if a is not None and b else None
ag = reads.get("AGCLUB") or {}
mx = reads.get("Matrix") or {}
lg = reads.get("Ledgera") or {}
pf = reads.get("PIXELFROGS") or {}
le = reads.get("LEGBEE") or {}
threshold = {
  "AGCLUB_free_pct": pct(ag.get("freeMinted"), ag.get("FREE_CAP")),
  "Matrix_free_pct": pct(mx.get("freeMinted"),
                         (mx.get("freeMinted") or 0) + (mx.get("freeRemaining") or 0)),
  "Ledgera_free_pct": pct(lg.get("freeClaimed"), lg.get("FREE_SUPPLY")),
  "PIXELFROGS_free_pct": pct(pf.get("freeMinted"),
                             (pf.get("freeMinted") or 0) + (pf.get("freeLeft") or 0)),
  "LEGBEE_free_pct": pct(le.get("freeClaimed"), le.get("FREE_SUPPLY")),
  "notes": "Strong-lead bar >70% + age <24h + slot open. None above 70% => no promotion. "
            "PIXELFROGS free% uses freeMinted/(freeMinted+freeLeft)."}
log("threshold", threshold)

# bridge (read-only)
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    b_contracts = bridge.get("contracts", bridge) if isinstance(bridge, dict) else bridge
    if isinstance(b_contracts, dict):
        b_list = list(b_contracts.keys())
        b_disc = sum(1 for v in b_contracts.values()
                     if isinstance(v, dict) and v.get("same_owner_discarded"))
    else:
        b_list, b_disc = b_contracts, 0
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        if isinstance(v, dict) and v.get("address"):
            snap_addrs.add(v["address"].lower())
    for v in snap.get("track_c", {}).values():
        if isinstance(v, dict):
            if v.get("sale"):
                snap_addrs.add(str(v["sale"]).lower())
            if v.get("token"):
                snap_addrs.add(str(v["token"]).lower())
    not_in_snap = [a for a in b_list if a.lower() not in snap_addrs]
    bridge_out = {"total": len(b_list), "not_in_snapshot": len(not_in_snap),
                  "not_in_snapshot_list": not_in_snap,
                  "same_owner_discarded": b_disc}
except Exception as ex:
    bridge_out = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
log("bridge", bridge_out)

# BSCCat assessment (track-C lead candidate; website gate passed at 0239 run)
b = bsc_out or {}
bsccat_assessment = {
  "website_gate": "PASS carried from 0239 run (bsccat.com live read 02:17 WIB prints exact mint "
                  "contract 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A twice; registry 0x60B9...022F "
                  "printed) - site NOT re-read this run",
  "probe_views": {k: b.get(k) for k in ('totalMinted', 'soldShares', 'freeMinted', 'freeClaimed',
                  'freeSharesLeft', 'FREE_SHARES', 'FREE_SUPPLY', 'totalShares', 'totalSupply',
                  'mintOpen', 'opened', 'poolOpen', 'isPoolOpen', 'launched')},
  "user_slot": {k: b.get(k) for k in ('hasMinted_user', 'freeClaimed_user', 'freeUsed_user',
                  'freeLeft_user', 'mintedBy_user', 'quote_user_1', 'cost_user_1', 'costOf_1',
                  'bnbQuote_1', 'balanceOf_user')},
  "token_address": b.get("token") or b.get("TOKEN"),
  "site_claims": "18,000 shares incl 800 free; 1 free/Agent ID; 1 share = 1,000,000 $BSC; "
                 "paid 0.001 BNB/share; pool opens at 7,000 net paid shares or sellout; "
                 "token non-transferable before pool; 2.5% tax after pool",
  "caveats": "Source UNVERIFIED per site; registry mismatch site 0x60B9...022F vs post "
             "0x31f9...; pool NOT open yet (no market/liquidity until 7,000 paid shares).",
}
log("bsccat", json.dumps(bsccat_assessment)[:1500])

# update seen (own file only) for genuinely new contracts
added = []
for s in shape_out:
    a = s["address"]
    if a.lower() not in seen_l:
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed/boltbook",
                   "status": ("sale-shape-S1/S2" if (s.get("S1") or s.get("S2"))
                              else "checked-not-sale-shape"),
                   "note": s.get("status", "")[:800]}
        added.append(a)
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
log("seen", seen_n0, "->", len(seen), "added", added)

n_calls = sum(len(v) for _, _, v in ITEMS) + len(BSCCAT_VIEWS)
reread = {"reads": {n: {"address": a, "views": reads.get(n)} for n, a, _ in ITEMS},
          "bsccat": {"address": BSCCAT, "views": bsc_out},
          "errors": errors + bsc_errors, "n_calls": n_calls,
          "elapsed_s": round(time.time() - t_rpc, 1), "block": blk}
json.dump(reread, open(BASE + "hot-leg-run-2026-11-17-0339-reread.json", "w"), indent=1)

out = {"run": RUN_TAG, "started_wib": NOW,
       "sourcify_feed": {"total": len(feed_addrs), "error": feed_err, "new": len(feed_new),
                         "new_contracts": feed_new,
                         "top": feed_addrs[0] if feed_addrs else None,
                         "top_verifiedAt": feed_meta[0].get("verifiedAt") if feed_meta else None,
                         "all": feed_addrs, "fetch": "direct curl"},
       "boltbook_en": {"bytes": en["bytes"], "http_code": en["http_code"], "error": en["error"],
                       "full_address_contracts": len(en["addresses"]),
                       "addresses": en["addresses"], "new": 0, "new_contracts": [],
                       "fetch": "direct curl -L"},
       "boltbook_zh": {"bytes": zh["bytes"], "http_code": zh["http_code"], "error": zh["error"],
                       "full_address_contracts": len(zh["addresses"]),
                       "addresses": zh["addresses"], "new": 0, "new_contracts": [],
                       "fetch": "direct curl -L"},
       "shape_check_targets": [s["address"] for s in shape_out],
       "shape_check": shape_out,
       "shape_hits": hits,
       "bsccat_probe": bsc_out,
       "bsccat_assessment": bsccat_assessment,
       "leg4_reread_file": "hot-leg-run-2026-11-17-0339-reread.json",
       "leg4_changes_vs_0334": changes,
       "leg4_rpc_note": "chunked direct JSON-RPC batches of 20 (no fast_rpc race - it timed "
                         "out + 429 on 0324 run)",
       "bridge_scan": bridge_out,
       "seen_added": added, "seen_n": len(seen), "seen_n_prev": seen_n0,
       "threshold_check": threshold,
       "elapsed_s": round(time.time() - t0, 1),
       "executions": "none - no preview, no mint, no claim (this script is read-only)"}
json.dump(out, open(BASE + "hot-leg-run-2026-11-17-0339.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"], "changes", len(changes), "hits", hits)
print("CHANGES", json.dumps(changes))
print("BSCCAT", json.dumps(bsc_out))
print("THRESHOLD", json.dumps(threshold))
