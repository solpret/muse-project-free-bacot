#!/usr/bin/env python3
"""Asset sell watch — LEG NFT (main wallet, BSC only).

Auto-list rule (user instructions 2026-11-02 ~10:23 WIB):
  - If a project's OWN website market verifiably exists for an unlisted NFT
    (contract-matched, live listings present, floor readable), list it at the
    FRESH FLOOR price, without a second confirmation — ONLY with all safety
    guards: fresh on-chain verification, audit disclosed, clean preview
    000000000, no 351803/351805, no authority surprises.
  - NEVER touch already-listed NFTs.
  - NEVER auto-list a collection the user named for manual execution
    (manual_collections.json — currently DIGG, user hold 2026-11-02).
  - NEVER auto-list soulbound, non-transferable, transfer-locked items, or
    SEVY Genesis (burn-to-redeem rights, not a sale item).
  - Element is NOT a project-own market: Element listings still need a
    per-item confirmation under the standing rule, never auto-listed here.
  - A market whose listing mechanism is not verified in markets.json is
    reported ONCE as "market known, mechanism unverified" — NEVER executed.

markets.json format (keyed by NFT contract, lowercase):
  { "<contract>": {"market": "<addr>", "mechanism": "list1155"|"list721"|...,
                    "verified": true/false, "note": "..."} }
Only entries with verified=true AND a supported mechanism may execute.
Supported mechanisms in this script: list1155 (DIGG-style: list1155(token,
tokenId, amount, price)) and list721 (list721(token, tokenId, price)).
Floor reading is mechanism-specific and lives in markets.json as
"floor_reader": "listings-enum" (enumerate market listings(), filter by NFT
contract + tokenId + active, take min price) — other readers are not
implemented and count as unverified.

Modes: --baseline (read-only: eligibility + registry status, no execution).
Run with: ~/workspace/.abi-venv/bin/python nft_list_watch.py [--baseline]
"""
import sys, json, re, time, urllib.request, subprocess
from eth_abi import encode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
BAW = "/home/hatch/workspace/.baw-cli/bin/baw"
HERE = "/home/hatch/workspace/asset-sell-watch"
LIST_FILE = "/home/hatch/workspace/nft-main-wallet-list.md"

EXCLUDED_NAMES = [  # name fragments: soulbound / non-transferable / locked / redeem-right
    ("HashDroids", "soulbound"),
    ("CharMasks", "non-transferable"),
    ("Crop Pals", "transfer-locked"),
    ("SEVY Genesis", "burn-to-redeem right, not a sale item"),
]

def sel(sig):
    return keccak(text=sig).hex()[:8]

def rpc_batch(calls):
    url = "https://bsc-dataseed.binance.org/"
    batch = [{"jsonrpc": "2.0", "id": i + 1, "method": m, "params": p}
             for i, (m, p) in enumerate(calls)]
    req = urllib.request.Request(url, data=json.dumps(batch).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception:
        return [None] * len(calls)
    out = []
    for r in res:
        if r.get("error") or not r.get("result"):
            out.append(None)
        else:
            out.append(r["result"])
    return out

def call(to, data):
    return rpc_batch([("eth_call", [{"to": to, "data": data}, "latest"])])[0]

def u256(h):
    return int(h, 16) if h else 0

def baw(args):
    r = subprocess.run([BAW] + args, capture_output=True, text=True, timeout=180)
    try:
        return json.loads(r.stdout)
    except Exception:
        return {"success": False, "raw": (r.stdout + r.stderr)[:500]}

def preview_clean(d):
    if not d.get("success"):
        return False, "preview failed: %s" % json.dumps(d)[:300]
    sim = d["data"]["simulationResult"]
    if sim.get("simulationCode") != "000000000":
        return False, "simulationCode %s" % sim.get("simulationCode")
    if sim.get("simulationErrorDetail"):
        return False, "simulationError %s" % sim["simulationErrorDetail"]
    if sim.get("authorityChanges"):
        return False, "authorityChanges present"
    risks = d["data"].get("risks", {})
    if risks.get("riskDetails") or risks.get("riskBehaviors"):
        return False, "risk hits present"
    return True, ""

def receipt(tx):
    for _ in range(12):
        r = rpc_batch([("eth_getTransactionReceipt", [tx])])[0]
        if r:
            return r
        time.sleep(5)
    return None

def parse_list():
    rows = []
    try:
        text = open(LIST_FILE).read()
    except Exception:
        return rows
    for ln in text.split("\n"):
        m = re.match(r"^\| (\d+) \| (.+?) \| (0x[0-9a-fA-F]{40}) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.+?) \|$", ln)
        if m:
            rows.append({"no": int(m.group(1)), "name": m.group(2).strip(),
                         "contract": m.group(3), "rarity": m.group(4).strip(),
                         "status": m.group(8).strip()})
    return rows

def token_id(name):
    m = re.search(r"#(\d+)", name)
    return int(m.group(1)) if m else None

def main():
    baseline = "--baseline" in sys.argv
    try:
        manual = json.load(open(HERE + "/manual_collections.json"))
    except Exception:
        manual = {}
    try:
        markets = json.load(open(HERE + "/markets.json"))
    except Exception:
        markets = {}
    summary = {"mode": "baseline" if baseline else "live", "nfts": [], "actions": []}
    for row in parse_list():
        name = row["name"]
        if row["status"].startswith("TER-LISTING"):
            continue  # never disturb already-listed
        excluded = None
        for frag, reason in EXCLUDED_NAMES:
            if frag in name:
                excluded = reason
                break
        manual_hit = None
        for key, why in manual.items():
            if key.lower() in name.lower():
                manual_hit = why
                break
        item = {"name": name, "contract": row["contract"]}
        if excluded:
            item["status"] = "excluded-" + excluded
            summary["nfts"].append(item)
            continue
        if manual_hit:
            item["status"] = "excluded-manual"
            item["reason"] = manual_hit
            summary["nfts"].append(item)
            continue
        entry = markets.get(row["contract"].lower())
        if not entry or not entry.get("verified"):
            item["status"] = "no-verified-own-market"
            if entry and not entry.get("verified"):
                item["note"] = "market known, mechanism unverified"
            summary["nfts"].append(item)
            continue
        # Verified own market + supported mechanism: live floor + guarded list.
        mech = entry.get("mechanism")
        market = entry.get("market")
        tid = token_id(name)
        if mech not in ("list1155", "list721") or not market or tid is None:
            item["status"] = "market-known-mechanism-unsupported"
            summary["nfts"].append(item)
            continue
        # Floor: enumerate market listings() if reader says so.
        floor = None
        if entry.get("floor_reader") == "listings-enum":
            nxt = call(market, "0x" + sel("nextListingId()"))
            n = u256(nxt) if nxt else 0
            for start in range(1, n, 18):
                ids = list(range(start, min(start + 18, n)))
                batch = [("eth_call", [{"to": market, "data": "0x" + sel("listings(uint256)") +
                                        encode(["uint256"], [i]).hex()}, "latest"]) for i in ids]
                res = rpc_batch(batch)
                for r in res:
                    if not r:
                        continue
                    b = bytes.fromhex(r[2:])
                    w = [int.from_bytes(b[i * 32:(i + 1) * 32], "big") for i in range(7)]
                    token = "0x" + b[32:64][-20:].hex()
                    if token.lower() == row["contract"].lower() and w[2] == tid and bool(w[6]):
                        if floor is None or w[4] < floor:
                            floor = w[4]
        if floor is None or floor <= 0:
            item["status"] = "market-verified-no-live-floor"
            summary["nfts"].append(item)
            continue
        item["floor"] = floor
        item["market"] = market
        if baseline:
            item["status"] = "would-list-at-floor"
            summary["nfts"].append(item)
            continue
        # LIVE: ownership + approval + audit + preview + execute.
        if mech == "list1155":
            bal_h = call(row["contract"], "0x" + sel("balanceOf(address,uint256)") +
                         encode(["address", "uint256"], [W, tid]).hex())
            if not bal_h or u256(bal_h) < 1:
                item["status"] = "not-owned-anymore"
                summary["nfts"].append(item)
                continue
            appr_h = call(row["contract"], "0x" + sel("isApprovedForAll(address,address)") +
                          encode(["address", "address"], [W, market]).hex())
            if not appr_h or not u256(appr_h):
                item["status"] = "approval-needed-manual"
                summary["actions"].append({"name": name, "action":
                    "STOP approval to market not active; approval needs separate confirmation"})
                summary["nfts"].append(item)
                continue
            data = ("0x" + sel("list1155(address,uint256,uint256,uint256)") +
                    encode(["address", "uint256", "uint256", "uint256"],
                           [row["contract"], tid, 1, floor]).hex())
        else:
            own_h = call(row["contract"], "0x" + sel("ownerOf(uint256)") +
                         encode(["uint256"], [tid]).hex())
            if not own_h or ("0x" + own_h[-40:]).lower() != W.lower():
                item["status"] = "not-owned-anymore"
                summary["nfts"].append(item)
                continue
            appr_h = call(row["contract"], "0x" + sel("isApprovedForAll(address,address)") +
                          encode(["address", "address"], [W, market]).hex())
            if not appr_h or not u256(appr_h):
                item["status"] = "approval-needed-manual"
                summary["actions"].append({"name": name, "action":
                    "STOP approval to market not active; approval needs separate confirmation"})
                summary["nfts"].append(item)
                continue
            data = ("0x" + sel("list721(address,uint256,uint256)") +
                    encode(["address", "uint256", "uint256"],
                           [row["contract"], tid, floor]).hex())
        import uuid
        url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit"
        body = json.dumps({"binanceChainId": "56", "contractAddress": market,
                           "requestId": str(uuid.uuid4())}).encode()
        req = urllib.request.Request(url, data=body,
            headers={"Content-Type": "application/json", "source": "agent",
                     "User-Agent": "binance-web3/1.4 (Skill)"})
        try:
            aud = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("data", {})
        except Exception as e:
            aud = {"error": str(e)}
        danger = []
        if aud.get("riskAlert"):
            danger.append("riskAlert")
        for grp in (aud.get("riskItems") or []):
            for det in (grp.get("details") or []):
                if det.get("isHit") and det.get("riskType") == "RISK":
                    danger.append(det.get("title"))
        item["audit"] = {"hasResult": aud.get("hasResult"), "risk_hits": danger}
        if aud.get("error") or danger:
            item["status"] = "blocked-audit"
            summary["actions"].append({"name": name, "action": "STOP audit block"})
            summary["nfts"].append(item)
            continue
        pv = baw(["contract-call", "preview", "--binanceChainId", "56",
                  "--from", W, "--to", market, "--value", "0",
                  "--inputData", data, "--json"])
        ok, why = preview_clean(pv)
        if not ok:
            item["status"] = "blocked-preview"
            summary["actions"].append({"name": name, "action": "STOP listing preview", "why": why})
            summary["nfts"].append(item)
            continue
        ex = baw(["contract-call", "execute",
                  "--requestId", pv["data"]["requestId"], "--json"])
        tx = (ex.get("data") or {}).get("txHash")
        if not tx:
            item["status"] = "blocked-execute"
            summary["actions"].append({"name": name, "action": "STOP listing execute",
                                       "out": json.dumps(ex)[:300]})
            summary["nfts"].append(item)
            continue
        rc = receipt(tx)
        if not rc or int(rc["status"], 16) != 1:
            item["status"] = "blocked-receipt"
            summary["actions"].append({"name": name, "action": "STOP listing receipt", "tx": tx})
            summary["nfts"].append(item)
            continue
        item["status"] = "LISTED"
        item["tx"] = tx
        item["block"] = int(rc["blockNumber"], 16)
        summary["actions"].append({"name": name, "action": "LISTED", "tx": tx,
                                   "block": item["block"], "price": floor,
                                   "market": market})
        summary["nfts"].append(item)
    print(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main()
