#!/usr/bin/env python3
"""Salvage for hot-leg 2026-11-16 10:19 WIB: leg-3 shape-check failed on
transport (urllib IncompleteRead x2, 404 for a tx hash). Re-check the 3
targets via curl-fetched ABI + on-chain batch reads. Read-only except
updating hot-leg-seen.json entry for 0x7E92 and the run json salvage key.
Never touches main snapshot / scan seen / track-c-checked."""
import json, re, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
T0 = time.time()
out = {}

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def enc_u(n):
    return format(n, "064x")

def batch(calls, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    body = json.dumps(payload).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.loads(r.read().decode())
            by = {it["id"]: it for it in res if isinstance(it, dict)}
            vals = []
            for i in range(len(calls)):
                it = by.get(i + 1, {})
                v = it.get("result")
                vals.append(v)
            return vals, ep
        except Exception as e:
            last = e
    return [None] * len(calls), f"all-endpoints-failed: {last}"

def u256(v):
    if not v or v == "0x":
        return None
    try:
        return int(v, 16)
    except Exception:
        return None

def addr(v):
    if not v or len(v) < 42:
        return None
    return "0x" + v[-40:]

# ABI-derived shape verdicts (from curl-fetched Sourcify ABI)
out["shape_salvage"] = {
    "0xA3Da6C76Be30be4de02cC2533E5968DBA04512de": {
        "S1": False, "S2": False, "has_mint": True, "has_quote": True,
        "free_views": [], "agent_ref": False, "is_token": False, "n_fns": 27,
        "status": "checked", "verifiedAt": "2026-11-16T03:17:49Z", "match": "exact_match",
        "reason": "plain NFT mint (mint/costOf/price, mintsLeft); no free-share view, no registry/AgentGate ref"},
    "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980": {
        "S1": False, "S2": False, "has_mint": True, "has_quote": False,
        "free_views": ["freeClaimed", "freeMinted"], "agent_ref": False,
        "is_token": False, "n_fns": 68,
        "status": "checked", "verifiedAt": "2026-11-15T11:46:30Z", "match": "exact_match",
        "reason": "strict-script S1 fails: quote fns are costOf(uint256)/bnbQuote(uint256)/priceWei (not in script quote set) and registry ref is agentOf(address)/registrar (not in script agent set); BUT contract is a free-share sale shape in substance: claimFree(address), FREE_SHARES/FREE_TOKENS, freeMinted, soldShares, token(), pair()",
        "note": "needs on-chain leg-3 verification below before any tier call"},
    "0xa2cf6719cb51c8986af773bb8e988d04e5eb7f0e": {
        "S1": False, "S2": False, "status": "not-a-contract",
        "reason": "Sourcify 404; this is a tx hash (0xa2cf...f1) quoted in a Boltbook scanner post about token 0xac6d5f6cba4aec0ad3442d79c645bd0330bda198, not a contract address"},
}

# On-chain reads for PEPE mint 0x7E92
calls = [
    (MINT, "0x" + sel("FREE_SHARES()")),
    (MINT, "0x" + sel("FREE_TOKENS()")),
    (MINT, "0x" + sel("TOTAL_SHARES()")),
    (MINT, "0x" + sel("soldShares()")),
    (MINT, "0x" + sel("freeMinted()")),
    (MINT, "0x" + sel("opened()")),
    (MINT, "0x" + sel("openedTime()")),
    (MINT, "0x" + sel("mintStartTime()")),
    (MINT, "0x" + sel("mintableNow()")),
    (MINT, "0x" + sel("token()")),
    (MINT, "0x" + sel("pair()")),
    (MINT, "0x" + sel("PRICE()")),
    (MINT, "0x" + sel("costOf(uint256)") + enc_u(1)),
    (MINT, "0x" + sel("bnbQuote(uint256)") + enc_u(1)),
    (MINT, "0x" + sel("hasMinted(address)") + enc_addr(USER)),
    (MINT, "0x" + sel("walletStatus(address)") + enc_addr(USER)),
    (MINT, "0x" + sel("agentOf(address)") + enc_addr(USER)),
    (MINT, "0x" + sel("overview()")),
]
labels = ["FREE_SHARES", "FREE_TOKENS", "TOTAL_SHARES", "soldShares", "freeMinted",
          "opened", "openedTime", "mintStartTime", "mintableNow", "token", "pair",
          "PRICE", "costOf_1", "bnbQuote_1", "hasMinted_user", "walletStatus_user",
          "agentOf_user", "overview"]
vals, ep = batch(calls)
reads = {}
for lab, v in zip(labels, vals):
    if lab in ("token", "pair"):
        reads[lab] = addr(v)
    elif lab == "walletStatus_user":
        reads[lab] = v  # raw tuple hex, decode below
    elif lab == "overview":
        reads[lab] = v
    elif lab in ("opened", "hasMinted_user"):
        reads[lab] = (u256(v) == 1) if u256(v) is not None else None
    elif lab == "agentOf_user":
        reads[lab] = v
    else:
        reads[lab] = u256(v)
out["pepe_mint_onchain"] = {"endpoint": ep, "reads": reads}
if reads.get("walletStatus_user"):
    h = reads["walletStatus_user"][2:]
    words = [h[i:i + 64] for i in range(0, len(h), 64)]
    out["pepe_mint_onchain"]["walletStatus_decoded"] = [int(w, 16) if w else None for w in words]
if reads.get("agentOf_user"):
    h = reads["agentOf_user"][2:]
    words = [h[i:i + 64] for i in range(0, len(h), 64)]
    out["pepe_mint_onchain"]["agentOf_decoded"] = [int(w, 16) if w else None for w in words]
if reads.get("overview"):
    h = reads["overview"][2:]
    words = [h[i:i + 64] for i in range(0, len(h), 64)]
    out["pepe_mint_onchain"]["overview_decoded"] = [int(w, 16) if w else None for w in words]
# epoch -> WIB for openedTime / mintStartTime
for k in ("openedTime", "mintStartTime"):
    v = reads.get(k)
    if isinstance(v, int) and v > 0:
        out["pepe_mint_onchain"][f"{k}_wib"] = time.strftime(
            "%Y-%m-%d %H:%M:%S WIB", time.gmtime(v + 7 * 3600))

# Token contract reads (name/symbol/decimals/totalSupply) if token known
tok = reads.get("token")
if tok:
    tcalls = [
        (tok, "0x" + sel("name()")),
        (tok, "0x" + sel("symbol()")),
        (tok, "0x" + sel("decimals()")),
        (tok, "0x" + sel("totalSupply()")),
    ]
    tvals, tep = batch(tcalls)
    def dec_str(v):
        if not v or len(v) < 130:
            return None
        try:
            ln = int(v[66:130], 16)
            raw = bytes.fromhex(v[130:130 + ln * 2])
            return raw.decode("utf-8", "replace")
        except Exception:
            return None
    out["pepe_token"] = {"address": tok, "endpoint": tep,
                         "name": dec_str(tvals[0]), "symbol": dec_str(tvals[1]),
                         "decimals": u256(tvals[2]), "totalSupply": u256(tvals[3])}

# Website gate probe: pepebnb.pages.dev — does it print the exact contracts?
site = "https://pepebnb.pages.dev/"
try:
    r = subprocess.run(["curl", "-sS", "-m", "20", "-L", site],
                       capture_output=True, text=True, timeout=30)
    html = r.stdout
    out["website_gate"] = {
        "url": site, "http_ok": r.returncode == 0, "bytes": len(html),
        "prints_mint": MINT.lower() in html.lower(),
        "prints_mint_checksum": MINT in html,
        "prints_token": (tok.lower() in html.lower()) if tok else None,
        "addresses_found": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))[:10],
        "title_snippet": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:300].strip(),
    }
except Exception as e:
    out["website_gate"] = {"url": site, "error": f"{type(e).__name__}: {e}"}

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (salvage is read-only)"

run_path = f"{HF}/hot-leg-run-2026-11-16-1019.json"
run = json.load(open(run_path))
run["shape_check_salvage"] = out["shape_salvage"]
run["pepe_mint_onchain"] = out["pepe_mint_onchain"]
if "pepe_token" in out:
    run["pepe_token"] = out["pepe_token"]
run["website_gate_pepe"] = out["website_gate"]
run["salvage_elapsed_s"] = out["elapsed_s"]
json.dump(run, open(run_path, "w"), indent=1)

# Fix seen entry for 0x7E92 (was mis-recorded as checked-not-sale-shape on a
# failed transport read); keep first_seen/source, correct the status/note.
seen = json.load(open(f"{HF}/hot-leg-seen.json"))
key = next((k for k in seen if k.lower() == MINT.lower()), None)
if key:
    seen[key]["status"] = "sale-shape-substance-pending-onchain"
    seen[key]["note"] = json.dumps(out["shape_salvage"][MINT])[:600]
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
