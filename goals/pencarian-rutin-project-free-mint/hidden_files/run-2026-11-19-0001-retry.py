#!/usr/bin/env python3
"""Retry for run 2026-11-19 00:01 WIB. Driver 0001 killed at 420s (EXIT 124):
pre-flight FAILED (egress timeout, not 401); leg-4 chunks 1-20 mostly
TimeoutError, 21-36 mostly OK, results LOST (no incremental write).
This retry: same PLAN, per-chunk incremental persist to reread JSON,
curl timeout 40s, 3 workers, then Boltbook + Sourcify/shape + bridge.
Read-only except snapshot merge by separate script."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
def https_get(host, path, timeout=20, redirects=3):
    conn = ProxyHTTPSConnection(host, 443, timeout=timeout)
    try:
        conn.request("GET", path, headers={"User-Agent": UA, "Accept": "*/*"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
        loc = resp.getheader("Location")
    finally:
        conn.close()
    if status in (301,302,303,307,308) and loc and redirects > 0:
        if loc.startswith("http"):
            from urllib.parse import urlparse
            u = urlparse(loc)
            return https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout, redirects-1)
        return https_get(host, loc, timeout, redirects-1)
    return status, raw
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
now_wib = "2026-11-19 00:01 WIB"
RPC_URL = "https://bsc-dataseed.binance.org/"
out = {"run": "free-mint-search 2026-11-19 00:01 WIB (retry)", "started_wib": now_wib}
out["preflight"] = {"ok": False, "error": "setup: OSError: batch failed on all healthy endpoints: timed out (driver 0001 pre-flight, egress-wide, NOT 401)"}
out["scan_leg"] = "FAST-FAIL (pre-flight failed)"
# ---- RPC helpers ----
def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def curl_json(url, payload, timeout=40):
    # url ignored: all JSON-RPC goes via Quicknode tunnel (dataseed curl dead since 16:29)
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def rpc_batch(calls, timeout=25):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(RPC_URL, payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append(f"err:{it['error']}")
        else:
            res.append(None)
    return res

def rpc_batch_chunked(calls, chunk=5):
    # 1331 fix: sequential curl batches (56 x ~7s) blew the 420s budget on
    # 1301-style egress (run 1331 first attempt: killed at 420s, zero output).
    # Run chunks in parallel (8 workers); per-item error semantics unchanged.
    import concurrent.futures as _cf
    idxs = list(range(0, len(calls), chunk))
    out = [None] * len(idxs)
    errors = []
    def _one(j):
        i = idxs[j]
        try:
            r = rpc_batch(calls[i:i + chunk])
            print(f"chunk {j + 1}/{len(idxs)} calls {i}-{i + len(calls[i:i+chunk]) - 1} OK", flush=True)
            return j, r, None
        except Exception as e:
            print(f"chunk {j + 1}/{len(idxs)} calls {i}-{i + len(calls[i:i+chunk]) - 1} FAIL {type(e).__name__}", flush=True)
            return j, [None] * len(calls[i:i + chunk]), f"calls {i}-{i + len(calls[i:i+chunk]) - 1}: {type(e).__name__}: {str(e)[:150]}"
    with _cf.ThreadPoolExecutor(max_workers=4) as ex:
        for j, r, err in ex.map(_one, range(len(idxs))):
            out[j] = r
            if err:
                errors.append(err)
    res = []
    for r in out:
        res += r
    return res, errors

def curl_get(url, out_path, timeout=25):
    from urllib.parse import urlparse
    u = urlparse(url)
    status, raw = https_get(u.hostname, u.path + ("?" + u.query if u.query else ""), timeout=timeout)
    html = raw.decode("utf-8", errors="replace")
    open(out_path, "w").write(html)
    return html, str(status)

PLAN = [
 ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
  [("totalSupply", "totalSupply()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("PUNNY", "0xaFAE0Bf373ad87E88555afe1605111F66C99062C",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("freeRemaining", "freeRemaining()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintStart", "mintStart()", None), ("mintClosed", "mintClosed()", None),
   ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Vitaliq Scans", "0xad0d78689d047bb9a32f5bf93438373a73da68ec",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("genesisStart", "genesisStart()", None), ("holdsAgentId_user", "holdsAgentId(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Bubblebruin", "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("CAT402", "0xdAba96c14B38725b23502BE6dFE021c08B7a5fB1",
  [("freeCatsClaimed", "freeCatsClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("JADE", "0x1b8894391a3dcfe7e248c321103265ab52e273e0",
  [("cost_user_1", "cost(address,uint256)", "user1"), ("freeClaimed", "freeClaimed()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("DRAGON", "0xfc191b76041498b14dcae3c802af3389c74263e6",
  [("freeMinted", "freeMinted()", None), ("totalMinted", "totalMinted()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted", "freeMinted()", None), ("freeRemaining", "freeRemaining()", None),
   ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None)]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_CAP", "FREE_CAP()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("BNBG", "0x1595013dfc8c6b3f4b172254bf09bdaf1421002b",
  [("totalMinted", "totalMinted()", None)]),
 ("SPARKS", "0xd52fd117c4b47d03e4e16e778871f09faa5a024b",
  [("totalSupply", "totalSupply()", None)]),
 ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("BoldLeonidas", "0x84bcb8c16566e81ce902530c9da1e3de291f9941",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("CPASS", "0x5877d2bb9f226cc3e438f4d656caeb27deafc576",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("REOPIR", "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
  [("freeClaimed", "freeClaimed()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("RAVE", "0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None)]),
 ("MORFO", "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None)]),
 ("PIXELFROGS", "0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("freeLeft", "freeLeft()", None), ("mintOpen", "mintOpen()", None),
   ("freeClaimed_user", "freeClaimed(address)", "user")]),
 ("Flare-bd6f", "0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599",
  [("totalSupply", "totalSupply()", None)]),
 ("PunchCard", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("paidMinted", "paidMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintPriceFor_user_1", "mintPriceFor(address,uint256)", "user1"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("freeQuotaLeft", "freeQuotaLeft()", None),
   ("FREE_TOTAL", "FREE_TOTAL()", None), ("LAUNCH", "LAUNCH()", None),
   ("freeTaken_user", "freeTaken(address)", "user"),
   ("quote_user_1", "quote(address,uint256)", "user1")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("XCOPY", "0x3fbec44c7c845374267b06033940abe45c63edfa",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None)]),
 ("ARKYN", "0x69b0b5756671680766d232eb4b0f39a34be5d852",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("Mine Card", "0xf8a72c4538cd9d570b2c771f01a0d561a90a64eb",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None)]),
 ("ALIEN", "0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb",
  [("totalSupply", "totalSupply()", None)]),
 ("Kitebots", "0x8B8e59c014eb3e229e043AE8F3B0D7E201d21DB0",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None)]),
 ("EIM", "0x1fccfab61461c4b5c4d1b16580d12a7e32012baa",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None)]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None)]),
 ("PXIO Miners", "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab",
  [("totalSupply", "totalSupply()", None)]),
 ("FrieAgent-B751", "0xb7517e3b31107695f2f8837fafc76999b956c871",
  [("totalSupply", "totalSupply()", None)]),
 ("FrieAgent-c64d", "0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5",
  [("totalSupply", "totalSupply()", None)]),
 ("Abyssora", "0x4785e7b396d13fb23b50bd66a6f828797c862770",
  [("totalSupply", "totalSupply()", None)]),
 ("HANAMI", "0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None)]),
 ("Zephyra", "0x00a9791be6317d6e3a6c60f75a706c870d882048",
  [("totalMinted", "totalMinted()", None)]),
 ("AgentNOVA", "0x43462d7f269fde4914b03e1e07067a61b62b9540",
  [("totalSupply", "totalSupply()", None)]),
 ("ONI", "0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("HAPPE", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None)]),
 ("Kryntar", "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",
  [("totalMinted", "totalMinted()", None)]),
 ("Pengu", "0x5AEc03C90656743475810926B2B2bd443D5c26a4",
  [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None)]),
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("THYRK", "0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("mintedCount_user", "mintedCount(address)", "user"),
   ("freeClaimed_user", "freeClaimed(address)", "user"),
   ("freeUsed_user", "freeUsed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ADRAW", "0xdc167f998341aa37d734de94db2108f0983bf2a7",
  [("totalSupply", "totalSupply()", None), ("freeMinted", "freeMinted()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("hasClaimedFree_user", "hasClaimedFree(address)", "user")]),
 ("AgentEcho", "0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2",
  [("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("AGENT_ID", "AGENT_ID()", None),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ARKT", "0xf91b1ebbcb2b038107ed10b4cb163ed51ce39037",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("mintOpen", "mintOpen()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("AGENT_ID", "AGENT_ID()", None), ("agentId", "agentId()", None),
   ("hasClaimed_user", "hasClaimed(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Stromboat", "0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("paidMinted", "paidMinted()", None),
   ("mintOpen", "mintOpen()", None), ("freeMintedBy_user", "freeMintedBy(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Kageveil Genesis", "0xf79860f419be7b604d909e254785400d9edbd9d0",
  [("totalSupply", "totalSupply()", None), ("normalMinted", "normalMinted()", None),
   ("mintOpen", "mintOpen()", None), ("mintClosed", "mintClosed()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Foundry Faces", "0x8653b09bdad22c99915910962167f132e514331f",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None)]),
 ("Compasyn", "0xCd1bb8013E924E26Ed4131A69304f2969c4f8D28",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ARKT-claim-62a7", "0x62a7AC33ca463331858693b8Aa05B16688bA29E0",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("paused", "paused()", None), ("hasClaimed_user", "hasClaimed(address)", "user")]),
 ("APGB V1", "0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Velko Rig", "0x1a1d2418ACCED8228610a1DE2F920A9e18564aBf",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Crown", "0x38f96a09544f557ff4795d59d5e42b34c1a89217",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Longge", "0xeFb7F55EcC230250B7F84DF01dd40B5f1FdD7694",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("freeLeft", "freeLeft()", None), ("FREE_SUPPLY", "FREE_SUPPLY()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("cost_user_1", "cost(address,uint256)", "user1"), ("quote_user_1", "quote(address,uint256)", "user1"),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user")]),
 ("DGF CARD", "0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
  [("totalMinted", "totalMinted()", None), ("balanceOf_user", "balanceOf(address)", "user"),
   ("freeMinted", "freeMinted()", None), ("mintOpen", "mintOpen()", None)]),
 ("THE WALL", "0xa804bBBe09fa2F5832d11D09329cc4230D1d7899",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeLeft", "freeLeft()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 # 2331 additions: AgentPepe + Hivebyte (new snapshot entries run 2301, not yet in PLAN)
 ("AgentPepe", "0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d",
  [("totalMinted", "totalMinted()", None), ("mintOpen", "mintOpen()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("Hivebyte", "0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",
  [("totalSupply", "totalSupply()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 # 2331 additions: hot-leg 2314 noted changes to evaluate this run
 ("E5F8", "0xe5f8f8c424821908752332d527428258EcfC245b",
  [("totalMinted", "totalMinted()", None), ("totalSupply", "totalSupply()", None),
   ("mintOpen", "mintOpen()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("ARKT-8334", "0x8334C7d0e8aF217EEA5251A0A181e628971535e1",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
 # 2331 triage: new Boltbook front-page contract from hot-leg 2314 (shape S1/S2 false per seen notes, not in snapshot)
 ("TRIAGE-df6b", "0xdf6bede5287207e3def3dcbe142e202e2c0d5645",
  [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintOpen", "mintOpen()", None), ("balanceOf_user", "balanceOf(address)", "user")]),
]
BSCCAT_ADDR = "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A"
BSCCAT_VIEWS = [("totalMinted", "totalMinted()", None), ("soldShares", "soldShares()", None),
  ("freeMinted", "freeMinted()", None), ("freeClaimed", "freeClaimed()", None),
  ("freeSharesLeft", "freeSharesLeft()", None), ("FREE_SHARES", "FREE_SHARES()", None),
  ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("totalShares", "totalShares()", None),
  ("totalSupply", "totalSupply()", None), ("mintOpen", "mintOpen()", None),
  ("opened", "opened()", None), ("poolOpen", "poolOpen()", None),
  ("isPoolOpen", "isPoolOpen()", None), ("launched", "launched()", None),
  ("hasMinted_user", "hasMinted(address)", "user"),
  ("freeClaimed_user", "freeClaimed(address)", "user"),
  ("freeUsed_user", "freeUsed(address)", "user"),
  ("freeLeft_user", "freeLeft(address)", "user"),
  ("mintedBy_user", "mintedBy(address)", "user"),
  ("quote_user_1", "quote(address,uint256)", "user1"),
  ("cost_user_1", "cost(address,uint256)", "user1"),
  ("costOf_1", "costOf(uint256)", "one"), ("bnbQuote_1", "bnbQuote(uint256)", "one"),
  ("token", "token()", None), ("TOKEN", "TOKEN()", None),
  ("balanceOf_user", "balanceOf(address)", "user")]
PEPE_MINT = "0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980"
PEPE_VIEWS = [("freeMinted", "freeMinted()", None), ("soldShares", "soldShares()", None),
  ("FREE_SHARES", "FREE_SHARES()", None), ("opened", "opened()", None),
  ("costOf_1", "costOf(uint256)", "one"),
  ("hasMinted_user", "hasMinted(address)", "user")]


# ---- incremental re-read (persist after every chunk) ----
import concurrent.futures as _cf
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg)))
        meta.append((name, addr, label))
for label, sig, arg in BSCCAT_VIEWS:
    calls.append((BSCCAT_ADDR, encode(sig, arg)))
    meta.append(("bsccat", BSCCAT_ADDR, label))
for label, sig, arg in PEPE_VIEWS:
    calls.append((PEPE_MINT, encode(sig, arg)))
    meta.append(("pepe", PEPE_MINT, label))
CHUNK = 5
idxs = list(range(0, len(calls), CHUNK))
res = [None] * len(calls)
chunk_errors = []
def _one(i):
    try:
        r = rpc_batch(calls[i:i+CHUNK], timeout=40)
        print(f"chunk calls {i}-{i+len(calls[i:i+CHUNK])-1} OK", flush=True)
        return i, r, None
    except Exception as e:
        print(f"chunk calls {i}-{i+len(calls[i:i+CHUNK])-1} FAIL {type(e).__name__}", flush=True)
        return i, [None]*len(calls[i:i+CHUNK]), f"calls {i}-{i+len(calls[i:i+CHUNK])-1}: {type(e).__name__}: {str(e)[:150]}"
def _persist():
    reads, bsccat, pepe = {}, {"address": BSCCAT_ADDR, "views": {}}, {}
    for (name, addr, label), val in zip(meta, res):
        if name == "bsccat":
            bsccat["views"][label] = val
        elif name == "pepe":
            pepe[label] = val
        else:
            reads.setdefault(name, {"address": addr, "views": {}})[ "views"][label] = val
    global _cached_block
    if _cached_block is None:
        try:
            blk = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
            _cached_block = int(blk[0]["result"], 16)
        except Exception as e:
            _cached_block = f"error: {str(e)[:120]}"
    block = _cached_block
    json.dump({"reads": reads, "bsccat": bsccat, "pepe": pepe, "errors": chunk_errors,
               "n_calls": len(calls), "elapsed_s": round(time.time()-T0, 1), "block": block},
              open(f"{HF}/run-2026-11-19-0001-reread.json", "w"), indent=1)
    return block
_cached_block = None
block = None
with _cf.ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(_one, i): i for i in idxs}
    done = 0
    for fut in _cf.as_completed(futs):
        i, r, err = fut.result()
        res[i:i+len(r)] = r
        if err: chunk_errors.append(err)
        done += 1
        print(f"progress {done}/{len(idxs)} chunks", flush=True)
        block = _persist()
out["leg4_block"] = block
out["leg4_chunk_errors"] = chunk_errors
out["leg4_n_calls"] = len(calls)
out["leg4_chunks_done"] = done

# ---- Route 2: Boltbook EN + ZH ----
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html, code = curl_get(url, f"{HF}/run-2026-11-19-0001-boltbook-{lang}.html")
        addrs = sorted(set(ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "http_code": code,
            "full_address_contracts": len(addrs), "addresses": addrs,
            "free_kw": html.lower().count("free mint") + html.lower().count("free-mint")}
    except Exception as e:
        out[f"boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
# ---- Route 5a / cross-check: Sourcify recently-verified feed (via tunnel) ----
try:
    status, raw = https_get("sourcify.dev", "/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed = json.loads(raw.decode())
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs = []
    for it in items:
        a = it.get("address") if isinstance(it, dict) else None
        if a: addrs.append(a)
    out["sourcify_feed"] = {"http": status, "total": len(addrs), "addresses": addrs,
        "verifiedAt_top": (items[0].get("verifiedAt") if items and isinstance(items[0], dict) else None)}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
# shape-check feed addresses not yet covered by hot-leg-seen + pending Boltbook triage from 1631
try:
    hl_seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    hl_l = {k.lower() for k in hl_seen}
    snap0 = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_l = {str(v.get("address","")).lower() for v in snap0.get("contracts", {}).values() if isinstance(v, dict)}
    # 0001: the 11 retries from hot-leg 2254 + 0xd0bc were ALL shape-checked at
    # run 2301 (S1=false, S2=false) - no carry-forward retry this run.
    # Only triage: new Boltbook contract 0xdf6b from hot-leg 2314 (Sourcify ABI shape).
    pending_boltbook = []  # 0xdf6b resolved 0001 as no-code, not a contract; no carry-forward retry this run
    targets = [a for a in out.get("sourcify_feed", {}).get("addresses", []) if a.lower() not in hl_l and a.lower() not in snap_l]
    # 0001 fix: carry-forward retries bypass the hl_seen filter - the 2254
    # failures ARE in hot-leg-seen (failed = curl rc=28 transport timeout, NOT a
    # shape verdict), so filtering by hl_l would silently drop every retry.
    # Snapshot filter still applies (already-tracked contracts are not re-checked).
    targets += [a for a in pending_boltbook if a.lower() not in snap_l]
    FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
                  "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
    def shape_check(addr):
        try:
            st2, raw2 = https_get("sourcify.dev", f"/server/v2/contract/56/{addr}?fields=abi", timeout=20)
            meta2 = json.loads(raw2.decode()); abi = meta2.get("abi", [])
            fns = {}
            for e in abi:
                if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
            names = set(fns)
            has_mint = any(n.lower().startswith("mint") for n in names)
            has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
            free_views = sorted(names & FREE_VIEWS)
            agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
            registry_bytes = False
            if not agent_ref:
                # 1901 fix (runlog 1801): hot-leg registry-bytes check — AONE
                # passed S1 via registry address in bytecode while ABI-name
                # agent_ref was False. Same check here via eth_getCode.
                try:
                    code_resp = curl_json(RPC_URL, [{"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}])
                    code = code_resp[0].get("result", "") if isinstance(code_resp, list) else ""
                    if "60b9262456de011f7d15a54cdd8c48baa8b022f" in str(code).lower():
                        agent_ref = True
                        registry_bytes = True
                except Exception:
                    pass
            is_token = bool(names & {"name","symbol","decimals","totalSupply"})
            s1 = has_mint and has_quote and bool(free_views) and agent_ref
            mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
            s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
            return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
                    "free_views": free_views, "agent_ref": agent_ref, "registry_bytes": registry_bytes,
                    "is_token": is_token,
                    "n_fns": len(names), "status": "checked", "verifiedAt": meta2.get("verifiedAt")}
        except Exception as e:
            return {"address": addr, "status": "shape-check-failed", "error": f"{type(e).__name__}: {str(e)[:120]}"}
    sc = [shape_check(a) for a in targets]
    out["shape_check_new"] = sc
    out["shape_check_sale_shape"] = [x for x in sc if x.get("S1") or x.get("S2")]
except Exception as e:
    out["shape_check_new"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}

# ---- Bridge (read-only) ----
try:
    snap = json.load(open(f"{HF}/onchain-snapshot.json"))
    snap_addrs = set()
    for v in snap.get("contracts", {}).values():
        a = v.get("address")
        if a:
            snap_addrs.add(a.lower())
    bridge = json.load(open(f"{HF}/scan-bridge.json"))
    baddrs = list(bridge.get("contracts", {}).keys())
    not_in = [a for a in baddrs if a.lower() not in snap_addrs]
    disc = [a for a, c in bridge.get("contracts", {}).items() if c.get("same_owner_discarded")]
    out["bridge"] = {"total": len(baddrs), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in, "same_owner_discarded": len(disc)}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}


out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(f"{HF}/run-2026-11-19-0001.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("preflight", "scan_leg", "leg4_block", "leg4_chunk_errors", "boltbook_en", "boltbook_zh", "sourcify_feed", "bridge", "elapsed_s")}, indent=1, default=str)[:4000])
