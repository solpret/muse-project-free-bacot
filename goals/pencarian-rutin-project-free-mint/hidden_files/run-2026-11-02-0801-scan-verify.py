"""First-mint + state verification for scan first-seen agent-shaped candidates (run 08:01).
Decisive question per candidate: ANY Transfer-from-zero mint BEFORE the scan window start (131152808)?
0 pre-window logs -> first mint verified in-window -> EARLY lead path.
>0 pre-window logs -> continuation, checked-only, never reported.
Ankr getLogs as MODULE (never CLI). Standard-template state reads included.
"""
import sys, time, json, datetime, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak

B = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00" * 32
WINDOW_START = 131152808
PRE_FROM = 131060000

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    return int(v, 16) if v else None
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def dec_str(v):
    if not v or not v.startswith("0x"): return None
    raw = bytes.fromhex(v[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64: return raw[64:64+ln].decode("utf-8", "replace")
        except Exception: pass
    if len(raw) == 32: return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None
def head():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            ts = int(b["timestamp"], 16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: pass
    return None

def pre_window_mints(C, to_block):
    """All Transfer-from-zero logs for C in [PRE_FROM, to_block]. Returns (logs, truncated, err)."""
    logs = []; tok = None; pages = 0; err = None
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(PRE_FROM), "toBlock": hex(to_block),
                  "pageSize": 1000, "decodeLogs": False, "topics": [TRANSFER, ZERO], "address": C}
        if tok: params["pageToken"] = tok
        try: body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err = str(e)[:200]; break
        res = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend([l for l in res.get("logs", []) if l.get("address", "").lower() == C.lower()])
        tok = res.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
        time.sleep(1)
    truncated = bool(tok)
    return logs, truncated, err

def sourcify_fns(C):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi",
                                     headers={"User-Agent": "free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            abi = json.loads(r.read().decode())["abi"]
        fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
        return fns
    except Exception as e:
        return ["ERROR:" + str(e)[:120]]

CANDS = [
    ("Zombuni", "0xee9156A40f80A812E5269FD0359966759309c230"),
    ("Ganfanko", "0x10f97F4226b763A23C0Af3Af2fdaB0B30343A1b2"),
    ("Lunamoo", "0xFfaDba946937B7b7ffE59AD6b1caC53ccFE862CD"),
    ("Minotiny", "0x43F326420eee3da493bF5cb1D01fE7d23051E37b"),
    ("Uranuby", "0x0c78629512289Edc6A5B2036570F063cF6D00197"),
    ("Drontato", "0x7E3E1cb8a26f5A069385bF1B26021B6029b88056"),
    ("Circuitpug", "0x27446b0Cb76e0BaCa695Fd8a8a71f0a98EE981C1"),
    ("Qilinbo", "0xfFD3B8ec13860068aD9c5D80fCFa09bB9583f375"),
    ("FARM", "0x0862EFB2566346943bf5Ec81b0e3168e2E98D029"),
    ("Glitchowl", "0x4743e25388A12dc969Ab73BaA5284610E368382a"),
    ("Chromeko", "0xaf497A6eC8A2e7D706C2591feFf40A700ad6B62F"),
    ("Flamingoo", "0x539225c4f8141Fd16e512DC50b2376352B9B011B"),
]
h = head(); print("head", h)
out = {"head": h, "window_start": WINDOW_START, "pre_from": PRE_FROM, "candidates": {}}
scan = json.load(open(B + "onchain-scan-2026-11-02-0801.json"))
scanmap = {c["address"].lower(): c for c in scan["contracts"]}
for name, C in CANDS:
    sc = scanmap.get(C.lower(), {})
    logs, trunc, err = pre_window_mints(C, WINDOW_START - 1)
    r = {"address": C, "scan": sc, "pre_window_count": len(logs), "pre_window_truncated": trunc, "pre_window_err": err}
    if logs:
        blks = sorted(int(l["blockNumber"], 16) for l in logs)
        r["pre_window_first_block"] = blks[0]
        r["pre_window_first_wib"] = block_ts(blks[0])
        r["verdict"] = "CONTINUATION (earlier mints exist) -> checked-only, never reported"
    else:
        r["verdict"] = "FIRST MINT IN WINDOW VERIFIED -> EARLY lead path" if not err else "UNVERIFIED (getLogs error) -> checked-only"
    # current state reads (standard template + FARM variant views)
    st = {}
    for fn in ["totalSupply()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
               "freeMinted()", "MAX_FREE()", "freeAvailable(address)", "freeLeft(address)"]:
        arg = enc_addr(USER)[2:] if "address" in fn else ""
        st[fn] = iv(call(C, sel(fn) + arg))
    st["mintedBy_user"] = iv(call(C, sel("mintedBy(address)") + enc_addr(USER)[2:]))
    st["freeUsed_user"] = iv(call(C, sel("freeUsed(address)") + enc_addr(USER)[2:]))
    st["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
    st["quote_user_1"] = words(call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:]))
    st["name"] = dec_str(call(C, sel("name()")))
    st["symbol"] = dec_str(call(C, sel("symbol()")))
    st["agent_id_registry"] = call(C, sel("AGENT_ID()"))
    r["state"] = st
    r["abi_fns"] = sourcify_fns(C)
    out["candidates"][name] = r
    print(name, "| pre-window:", len(logs), "trunc:", trunc, "err:", err, "|", r["verdict"][:60], "| state:", {k: v for k, v in st.items() if v is not None})
    time.sleep(1)
json.dump(out, open(B + "run-2026-11-02-0801-scan-verify.json", "w"), indent=1)
print("saved run-2026-11-02-0801-scan-verify.json")
