#!/usr/bin/env python3
"""Hot-leg run 2026-11-17 02:14 WIB (scheduled 02:14:38).
Legs: (1) Sourcify feed (browser-fetched fresh <1min) + ABI shape-check new
S1/S2 (browser-fetched ABIs); (2) Boltbook EN (browser, fresh) + ZH (STALE
crawler cache dated 2026-11-15, recorded as degraded leg); (3) on-chain
verify new contracts: BSCCat probe (site says source UNVERIFIED, no
Sourcify ABI) + LEGBEE re-read (snapshot: checked-not-agent-shaped
2026-11-16); (4) focus re-read of the 23-entry active set (same as 0209
run) vs 0209 reads for changes, plus PEPE-mint re-read (audit-blocked
track-C lead); bridge read-only. Read-only except hot-leg-seen.json (own
file) + this run JSON. No preview/mint/claim. No snapshot writes.
NEW: BSCCat mint 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A (not seen /
snapshot / reported): site bsccat.com prints exact contract, 18,000
shares incl 800 free, 1 free per Agent ID. Registry mismatch flagged:
site prints registry 0x60B9...022F while Boltbook post claims the mint
contract's registry is 0x31f92aa2f9cc4a17a925b611992622789a4a5fd6 (site
one reverts on binding per post)."""
import json, re, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NOW = "2026-11-17T02:14+07:00"
RUN_TAG = "free-mint-hot-leg 2026-11-17 02:14 WIB"
PREV_RUN = "hot-leg-run-2026-11-17-0209.json"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
EPS = ["https://bsc-dataseed3.bnbchain.org/", "https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
BSCCAT = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"
LEGBEE = "0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149"
t0 = time.time()

def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
seen_n0 = len(seen)

# (1) Sourcify feed -- browser-fetched 02:16-02:17 WIB, crawled <1 min ago
feed_addrs = ["0xC47252a2575f1a97903988598aDF617D6b187777",
 "0xAB776361Ac69307752a2727B2f368f4031bbB0Ef",
 "0xCAeDFEc51A3e8e524bd4B2F33FFDE684a2cF1944",
 "0x8028A6C6fD26d686Ec37c1Dd0BC2c279D1F22bfF",
 "0xb5c8Bac2b2ea5ed60499E1a93bDbD4Df798d5C9F",
 "0x43ED2BD9A00730197645C9feaC19b96314607777",
 "0x460c5C391B2e8a72877B4edA9C4DB0EF85f12E92",
 "0x3D81C161D7B0364a53E172b6697eAb70414bCf5c",
 "0xcBe1ae8F9E001DcB111a27ae67cE7d41Aa001fc1",
 "0x0097ED1369e3B036BF177D6dBC6D56F59e09BBc1",
 "0x5a77b52Cf96822dFa6e430c3D65e4446d5cF3FE2",
 "0xF492e905d13767b6bE591f179bFaBc0D93Fb1496",
 "0xc4A55E456e0d821CA160bBF0a7197C41389E23BC",
 "0x693acb1C10e6EE2f2c70A2dcBA905B81319411ec",
 "0x910db793A1a03F6bBc0AcdbC12B933914F01Dfd0",
 "0xa74Bb34f2cbe6c1Acf7896fEfc86feCDed07D429",
 "0x1cD046c2bF64a1dca6b453447a2f1c7ce3220554",
 "0x1a1A3C9dcad8e51E0beb7F2064B6AF1eD1fbe8DD",
 "0x50EFF3F482548e940362a8f3da032F3c32cD69c2",
 "0x0D5B1487dD4D87Ec49A353D774d38fc465b8e6eA"]
feed_new = [a for a in feed_addrs if a.lower() not in seen_l and a.lower() != REG.lower()
            and a.lower() not in {e.lower() for e in EXCLUDED}]
log("feed total", len(feed_addrs), "new", len(feed_new), feed_new, "top", feed_addrs[0])

# (2) Boltbook EN (browser, fresh <1min) + ZH (STALE crawler cache 2026-11-15)
en_addrs = ["0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5",
            "0x44a6e69a0b41ee345fa67afee68b0cc90a6ca149",
            "0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6"]
bb_new = [a for a in en_addrs if a.lower() not in seen_l
          and a.lower() not in {e.lower() for e in EXCLUDED}]
log("boltbook en addrs", len(en_addrs), "new", len(bb_new), bb_new)
log("boltbook zh STALE: browser.open returned crawler copy dated 2026-11-15 03:05 UTC; "
    "ZH leg degraded this run, EN leg fresh - recorded, retried next run")

# (3) shape-check results (ABIs browser-fetched from Sourcify)
shape_out = [
 {"address": "0xC47252a2575f1a97903988598aDF617D6b187777", "S1": False, "S2": False,
  "has_mint": False, "has_quote": False, "free_views": [], "agent_ref": False,
  "is_token": True, "n_fns": 13, "status": "checked",
  "note": "Plain ERC-20 (team/maxTx/maxHolding/tokenURI, no mint/quote/free/agent). NOT sale shape.",
  "verifiedAt": "2026-11-16T19:11:40Z"},
 {"address": LEGBEE, "S1": False, "S2": False,
  "has_mint": True, "has_quote": True,
  "free_views": ["freeClaimed", "freeFor", "freeLeft", "freeUsed"],
  "agent_ref": False, "is_token": False, "n_fns": 33, "status": "checked",
  "note": "ERC-721 free mint (mint+quote+free views+FREE_SUPPLY 7000) but NO agent "
          "registry/AgentGate reference in ABI -> S1=False. Matches snapshot verdict "
          "checked-not-agent-shaped-2026-11-16 (Legacy Code Bees). NOT a lead.",
  "verifiedAt": "2026-11-12T17:27:35Z"},
 {"address": BSCCAT, "S1": None, "S2": None, "has_mint": None, "has_quote": None,
  "free_views": None, "agent_ref": None, "is_token": None, "status": "shape-check-no-abi",
  "note": "Site bsccat.com states source NOT verified on block explorer; Sourcify ABI "
          "unavailable. Shape judged from on-chain probe below + site (site prints exact "
          "contract, 18,000 shares incl 800 free, 1 free/Agent ID, registry 0x60B9...022F).",
  "verifiedAt": None},
]
hits = [s["address"] for s in shape_out if s.get("S1") or s.get("S2")]

U = [USER]
for r in shape_out:
    log("shape", r["address"][:12], "S1", r.get("S1"), "S2", r.get("S2"), r.get("status"))
log("shape hits:", hits)

ITEMS = {
 "JADE": ("0x1b8894391a3dcfe7e248c321103265ab52e273e0", [
    ("cost_user_1", "cost(address,uint256)", [USER, 1]),
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("freeMinted", "freeMinted()", []), ("totalSupply", "totalSupply()", []),
    ("totalMinted", "totalMinted()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("balanceOf_user", "balanceOf(address)", U)]),
 "Matrix": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("freeMinted", "freeMinted()", []), ("freeRemaining", "freeRemaining()", []),
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", [])]),
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("FREE_CAP", "FREE_CAP()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BNBG": ("0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [
    ("totalMinted", "totalMinted()", [])]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply", "totalSupply()", [])]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("freeUsed_user", "freeUsed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "BoldLeonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941", [
    ("totalSupply", "totalSupply()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", []),
    ("balanceOf_user", "balanceOf(address)", U)]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9", [
    ("freeClaimed", "freeClaimed()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", [])]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", []),
    ("mintOpen", "mintOpen()", [])]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted", "totalMinted()", []), ("mintOpen", "mintOpen()", [])]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [
    ("totalSupply", "totalSupply()", [])]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted", "totalMinted()", [])]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 "Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted", "totalMinted()", []), ("standardRemaining", "standardRemaining()", []),
    ("legendaryRemaining", "legendaryRemaining()", []), ("mintOpen", "mintOpen()", [])]),
 "ONI": ("0x99d01eD93829DBB0EEc11F3a733388c789dA6caD", [
    ("totalMinted", "totalMinted()", []), ("totalSupply", "totalSupply()", [])]),
 "HAPPE": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted", "totalMinted()", []), ("freeMinted", "freeMinted()", [])]),
 "PIXELFROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply", "totalSupply()", []), ("freeMinted", "freeMinted()", []),
    ("freeLeft", "freeLeft()", []), ("mintOpen", "mintOpen()", []),
    ("freeClaimed_user", "freeClaimed(address)", U)]),
 "Flare-bd6f": ("0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599", [
    ("totalSupply", "totalSupply()", [])]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft", "freeSharesLeft()", []), ("openedAt", "openedAt()", []),
    ("freeClaimed", "freeClaimed()", []),
    ("freeBooked_user", "freeBooked(address)", U)]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched", "launched()", []), ("failed", "failed()", []),
    ("isRefundPhase", "isRefundPhase()", []), ("totalShares", "totalShares()", []),
    ("tokenClaimed_user", "tokenClaimed(address)", U)]),
}
PEPE = {"PEPE-mint": ("0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980", [
    ("FREE_SHARES", "FREE_SHARES()", []), ("soldShares", "soldShares()", []),
    ("freeMinted", "freeMinted()", []), ("opened", "opened()", []),
    ("openedTime", "openedTime()", []), ("mintStartTime", "mintStartTime()", []),
    ("mintableNow", "mintableNow()", []), ("costOf_1", "costOf(uint256)", [1]),
    ("bnbQuote_1", "bnbQuote(uint256)", [1]), ("hasMinted_user", "hasMinted(address)", U)])}

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
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)


def chunked(items, n=4):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                log("  chunk ep", ep, "bad shape"); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            log("  chunk ep", ep, "exc", str(e)[:100]); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

# (4) leg-4 focus re-read (same 23-entry set as 0209)
reads, ok, chunk_errors = {}, 0, []
for ci, ch in enumerate(chunked(ITEMS, 4)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        log(f"chunk {ci+1} FAIL {names}")
        chunk_errors.append(names)
        for n in names:
            reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names:
        reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    log(f"chunk {ci+1} OK via {ep} {names}")
pepe_read, pepe_ep = read_chunk(list(PEPE.items()))
pepe_out = pepe_read.get("PEPE-mint") if pepe_read else None
log("pepe re-read via", pepe_ep, pepe_out)
blk = block_number()
log("reread ok", ok, "/", len(ITEMS), "block", blk)

# (3b) BSCCat probe: candidate view selectors (read-only; unknown selector -> None)
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
bsc_read, bsc_ep = read_chunk(list({"BSCCat": (BSCCAT, BSCCAT_VIEWS)}.items()))
bsc_out = bsc_read.get("BSCCat") if bsc_read else None
log("bsccat probe via", bsc_ep, bsc_out)

# (3c) LEGBEE re-read (known ABI) vs snapshot 2026-11-16 00:01 WIB baseline
LEGBEE_VIEWS = [
    ("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("MAX_SUPPLY", "MAX_SUPPLY()", []), ("totalSupply", "totalSupply()", []),
    ("mintOpen", "mintOpen()", []), ("quote_user_1", "quote(address,uint256)", [USER, 1]),
    ("freeLeft_user", "freeLeft(address)", U), ("freeUsed_user", "freeUsed(address)", U),
    ("mintedBy_user", "mintedBy(address)", U),
    ("balanceOf_user", "balanceOf(address)", U),
    ("externalUrl", "externalUrl()", []),
]
leg_read, leg_ep = read_chunk(list({"LEGBEE": (LEGBEE, LEGBEE_VIEWS)}.items()))
leg_out = leg_read.get("LEGBEE") if leg_read else None
log("legbee re-read via", leg_ep, leg_out)

# (3d) getCode + registry-byte search (agent linkage) for BSCCat + LEGBEE
def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=30)
            if isinstance(r, dict) and r.get("result") is not None:
                return r["result"]
        except Exception:
            continue
    return None
REG_BYTES = REG[2:].lower()
code_out = {}
for a in (BSCCAT, LEGBEE):
    code = get_code(a)
    code_out[a] = {"len": len(code) if code else None,
                   "is_contract": bool(code and code != "0x"),
                   "registry_bytes_in_code": bool(code and REG_BYTES in code.lower())}
    log("getCode", a[:12], code_out[a])

# (3e) BSCCat first-mint: Transfer-from-zero logs (bounded, best-effort)
first_mint = {"error": "not-attempted"}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
try:
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
               "params": [{"address": BSCCAT, "fromBlock": "0x7FAF400",
                           "toBlock": "latest",
                           "topics": [TRANSFER,
                                      "0x0000000000000000000000000000000000000000000000000000000000000000"] }]}
    got = None
    for ep in EPS:
        try:
            r = post_rpc(ep, payload, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), list):
                got = r["result"]; break
            log("  getLogs ep", ep, "bad", str(r)[:100])
        except Exception as e:
            log("  getLogs ep", ep, "exc", str(e)[:100]); continue
    if got is None:
        first_mint = {"error": "all-endpoints-failed"}
    else:
        first_mint = {"n_transfer_from_zero": len(got),
                      "first_block": int(got[0]["blockNumber"], 16) if got else None,
                      "last_block": int(got[-1]["blockNumber"], 16) if got else None,
                      "fromBlock_used": 133900000}
        log("first-mint logs", first_mint)
except Exception as ex:
    first_mint = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
    log("first-mint logs error", first_mint)

# change detection vs 0209 run
changes = []
try:
    prev = json.load(open(BASE + PREV_RUN))
    prev_reads = prev.get("leg4_reread", {}).get("reads", {})
    for name, cur in reads.items():
        pv = (prev_reads.get(name) or {}).get("views")
        cv = cur.get("views")
        if pv is None or cv is None:
            if pv != cv:
                changes.append({"item": name, "type": "read-availability-change",
                                "prev": pv, "now": cv})
            continue
        diff = {k: {"prev": pv.get(k), "now": cv.get(k)}
                for k in set(pv) | set(cv) if pv.get(k) != cv.get(k)}
        if diff:
            changes.append({"item": name, "type": "value-change", "diff": diff})
    pv_pepe = prev.get("pepe_reread")
    if pv_pepe != pepe_out:
        pdiff = {k: {"prev": pv_pepe.get(k) if isinstance(pv_pepe, dict) else None,
                     "now": (pepe_out or {}).get(k)}
                 for k in set(list(pv_pepe.keys()) if isinstance(pv_pepe, dict) else [])
                 | set((pepe_out or {}).keys())
                 if (pv_pepe.get(k) if isinstance(pv_pepe, dict) else None) != (pepe_out or {}).get(k)}
        changes.append({"item": "PEPE-mint", "type": "value-change", "diff": pdiff})
except Exception as ex:
    changes.append({"item": "_meta", "type": "prev-compare-error", "error": str(ex)[:120]})
log("changes vs 0209:", json.dumps(changes)[:3000])

# threshold check (info only)
def pct(a, b):
    return round(100.0 * a / b, 1) if a is not None and b else None
ag = reads.get("AGCLUB", {}).get("views") or {}
mx = reads.get("Matrix", {}).get("views") or {}
lg = reads.get("Ledgera", {}).get("views") or {}
bo = reads.get("BoldLeonidas", {}).get("views") or {}
threshold = {"AGCLUB_free_pct": pct(ag.get("freeMinted"), ag.get("FREE_CAP")),
             "Matrix_freeMinted": mx.get("freeMinted"),
             "Ledgera_freeClaimed": lg.get("freeClaimed"),
             "BOLD_totalSupply_over_MAX": pct(bo.get("totalSupply"), 1111),
             "BOLD_note": "totalSupply/MAX is NOT a verified free counter (no freeClaimed/freeMinted view); free% stays UNVERIFIED, website unverified, age unverified - no strong-lead promotion possible",
             "LEGBEE_free_pct": pct((leg_out or {}).get("freeClaimed"), (leg_out or {}).get("FREE_SUPPLY")),
             "LEGBEE_note": "Snapshot 2026-11-16 baseline freeClaimed 107/7000 (1.53%); not agent-shaped - no promotion regardless of pace."}
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

# BSCCat lead assessment (track-C)
b = bsc_out or {}
bsccat_assessment = {
  "website_gate": "PASS - bsccat.com (live read 02:17 WIB) prints exact mint contract 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A twice (mint desk + contract section); registry 0x60B9...022F printed",
  "probe_views": {k: b.get(k) for k in ('totalMinted','soldShares','freeMinted','freeClaimed','freeSharesLeft','FREE_SHARES','FREE_SUPPLY','totalShares','totalSupply','mintOpen','opened','poolOpen','isPoolOpen','launched')},
  "user_slot": {k: b.get(k) for k in ('hasMinted_user','freeClaimed_user','freeUsed_user','freeLeft_user','mintedBy_user','quote_user_1','cost_user_1','costOf_1','bnbQuote_1','balanceOf_user')},
  "registry_bytes_in_code": code_out.get(BSCCAT, {}).get("registry_bytes_in_code"),
  "first_mint": first_mint,
  "token_address": b.get("token") or b.get("TOKEN"),
  "site_claims": "18,000 shares incl 800 free; 1 free/Agent ID; 1 share = 1,000,000 $BSC; paid 0.001 BNB/share; pool opens at 7,000 net paid shares or sellout; token non-transferable before pool; 2.5% tax after pool",
  "caveats": "Source UNVERIFIED per site; registry mismatch site 0x60B9...022F vs post 0x31f9...; pool NOT open yet (no market/liquidity until 7,000 paid shares).",
}
log("bsccat assessment", json.dumps(bsccat_assessment)[:2000])

# update seen (own file only)
added = []
def add_seen(addr, source, status, note):
    global added
    if addr.lower() not in seen_l and addr.lower() not in {x.lower() for x in added}:
        seen[addr] = {"first_seen_wib": NOW, "source": source, "status": status,
                      "note": note[:800]}
        added.append(addr)
add_seen("0xC47252a2575f1a97903988598aDF617D6b187777", "sourcify-feed",
         "checked-not-sale-shape", json.dumps(shape_out[0]))
add_seen(LEGBEE, "boltbook-en", "checked-not-sale-shape",
         "LEGBEE (Legacy Code Bees): S1=False S2=False mint=True quote=True "
         "free=[freeClaimed,freeFor,freeLeft,freeUsed] agent=False; snapshot already "
         "checked-not-agent-shaped-2026-11-16; re-read this run in run JSON.")
add_seen(BSCCAT, "boltbook-en", "track-c-lead-candidate-probe",
         "BSCCat $BSC share sale via Boltbook post + bsccat.com (prints exact contract); "
         "probe results in hot-leg-run-2026-11-17-0214.json; source UNVERIFIED per site.")
add_seen("0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6", "boltbook-en",
         "checked-not-lead-snapshot",
         "Agent Vein VEIN proxy: new Boltbook post 02:16 WIB repeats snapshot evaluation "
         "(proxy unverified, no pair) - already contracts/AgentVein-proxy checked-not-lead "
         "2026-11-16; no change, DIAM.")
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
log("seen", seen_n0, "->", len(seen), "added", added)

out = {"run": RUN_TAG, "started_wib": NOW,
       "sourcify_feed": {"total": len(feed_addrs), "error": None, "new": len(feed_new),
                         "new_contracts": feed_new, "top": feed_addrs[0],
                         "top_verifiedAt": "2026-11-16T19:11:40Z", "all": feed_addrs,
                         "fetch": "browser.open (crawled <1 min ago)"},
       "boltbook_en": {"bytes": None, "http_code": "200", "error": None,
                       "full_address_contracts": len(en_addrs), "addresses": en_addrs,
                       "new": len(bb_new), "new_contracts": bb_new,
                       "fetch": "browser.open (crawled <1 min ago)",
                       "posts_noted": ["BSCCat free mint post (mint via bsccat.com, registry 0x31f9... per post; site prints registry 0x60B9...022F - MISMATCH flagged)",
                                       "Agent Vein VEIN claim post (0x869d... already snapshot checked-not-lead, no change)",
                                       "Motor Agent post (0x86F8... seen 2026-11-09, no change)",
                                       "LEGBEE pace post (0x44a6... snapshot checked-not-agent-shaped, re-read this run)"]},
       "boltbook_zh": {"bytes": None, "http_code": None,
                       "error": "STALE-CACHE: browser.open returned crawler copy dated 2026-11-15 03:05 UTC (2 days old); ZH leg degraded this run, retried next run",
                       "full_address_contracts": None, "addresses": [], "new": 0,
                       "new_contracts": []},
       "shape_check_targets": [s["address"] for s in shape_out],
       "shape_check": shape_out,
       "shape_hits": hits,
       "bsccat_probe": bsc_out,
       "bsccat_getcode": code_out.get(BSCCAT),
       "bsccat_first_mint": first_mint,
       "bsccat_assessment": bsccat_assessment,
       "legbee_reread": leg_out,
       "legbee_getcode": code_out.get(LEGBEE),
       "leg4_reread": {"reads": reads, "endpoint": EPS[0],
                       "n_calls": sum(len(v[1]) for v in ITEMS.values()),
                       "chunk_size": 4, "chunk_errors": chunk_errors,
                       "note": "chunked batches of 4 contracts",
                       "block": blk},
       "leg4_changes_vs_0209": changes,
       "pepe_reread": pepe_out,
       "bridge_scan": bridge_out,
       "seen_added": added, "seen_n": len(seen), "seen_n_prev": seen_n0,
       "threshold_check": threshold,
       "elapsed_s": round(time.time() - t0, 1),
       "executions": "none - no preview, no mint, no claim (this script is read-only)"}
json.dump(out, open(BASE + "hot-leg-run-2026-11-17-0214.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"], "changes", len(changes), "hits", hits)
print("BSCCAT", json.dumps(bsc_out))
print("LEGBEE", json.dumps(leg_out))
print("FIRSTMINT", json.dumps(first_mint))
print("CODE", json.dumps(code_out))
