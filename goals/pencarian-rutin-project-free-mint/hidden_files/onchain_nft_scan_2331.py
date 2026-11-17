#!/usr/bin/env python3
"""On-chain NFT discovery scanner for BSC — READ-ONLY, keyless.

Scans recent blocks for NFT MINT events via Ankr ankr_getLogs (chain-wide:
no contract-address filter, topics filter only) and runs cheap agent-shape
checks per distinct contract. No previews, mints, approvals, signatures,
or transactions of any kind. A failed read is UNVERIFIED, never zero.

Selectors (keccak-verified with pycryptodome, 2026-11-01):
  Transfer       0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
  TransferSingle 0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62
    (NOTE: a draft selector 0xc3d58168c4e7... seen in task notes is WRONG;
     it does not match keccak256("TransferSingle(address,address,address,uint256,uint256)"))
  name()         0x06fdde03   symbol() 0x95d89b41

Classification:
  ERC-721 mint  = topic0 Transfer, topic1 == zero address, 4 topics total
  ERC-20 mint   = topic0 Transfer, topic1 == zero address, 3 topics total
                  (counted separately, excluded from NFT results)
  ERC-1155 mint = topic0 TransferSingle, topic2 (from) == zero address

Usage:
  python3 onchain_nft_scan.py [--blocks 300] [--chunk 50] [--out out.json]
"""
import argparse
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single  # noqa: E402
from ankr import ankr_post  # noqa: E402  (module import: CLI truncates at 4000 chars)

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TS_SINGLE = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO_TOPIC = "0x" + "00" * 32
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
HIVE_AGENTS = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
NAME_SEL = "0x06fdde03"
SYMBOL_SEL = "0x95d89b41"


def rpc_call(method, params, timeout=8):
    """Try dataseeds in order; return first success, else raise last error."""
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:  # noqa: BLE001 - try next endpoint
            last = e
    raise last


def ankr_logs(from_block, to_block, topics, max_pages=10):
    """Chain-wide ankr_getLogs with topics filter + nextPageToken paging."""
    logs = []
    page_token = None
    pages = 0
    while True:
        params = {"blockchain": "bsc",
                  "fromBlock": hex(from_block), "toBlock": hex(to_block),
                  "pageSize": 1000, "decodeLogs": False, "topics": topics}
        if page_token:
            params["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                time.sleep(30)
                body = ankr_post("ankr_getLogs", params, timeout=30)
            else:
                raise
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break
        time.sleep(2.2)  # stay under 30 req/min
    return logs, pages


def decode_str_or_bytes32(hexdata):
    """Decode an eth_call string/bytes32 return to text, or None."""
    if not isinstance(hexdata, str) or not hexdata.startswith("0x"):
        return None
    raw = bytes.fromhex(hexdata[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None


def sourcify_abi(address):
    """Fetch verified ABI from Sourcify; returns (status, abi_or_None)."""
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return ("verified", data.get("abi"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("not_verified", None)
        return (f"http_{e.code}", None)
    except Exception as e:  # noqa: BLE001
        return (f"error:{type(e).__name__}", None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", type=int, default=300)
    ap.add_argument("--chunk", type=int, default=50)
    ap.add_argument("--out", default="")
    ap.add_argument("--to-block", type=int, default=0)
    args = ap.parse_args()

    latest = args.to_block if args.to_block else int(rpc_call("eth_blockNumber", []), 16)
    to_block = latest
    from_block = max(0, latest - args.blocks + 1)
    print(f"latest block: {latest}; scanning {from_block}..{to_block} "
          f"({args.blocks} blocks, chunks of {args.chunk})", flush=True)

    erc721, erc1155, erc20 = {}, {}, {}
    calls = 0
    errors = []

    def add(store, addr, log):
        e = store.setdefault(addr, {"mint_count": 0, "minters": set(),
                                    "first_block": None, "last_block": None})
        e["mint_count"] += 1
        blk = int(log.get("blockNumber", "0x0"), 16)
        e["first_block"] = blk if e["first_block"] is None else min(e["first_block"], blk)
        e["last_block"] = blk if e["last_block"] is None else max(e["last_block"], blk)
        return e

    chunk_from = from_block
    while chunk_from <= to_block:
        chunk_to = min(chunk_from + args.chunk - 1, to_block)
        # ERC-721/20 mints: topic0 Transfer, topic1 zero address
        # Run 2331: one retry on transient timeout before giving up the chunk.
        try:
            logs, _ = ankr_logs(chunk_from, chunk_to, [TRANSFER, ZERO_TOPIC])
            calls += 1
        except Exception as e:  # noqa: BLE001
            print(f"RETRY Transfer chunk {chunk_from}-{chunk_to} after: {e}", flush=True)
            time.sleep(10)
            try:
                logs, _ = ankr_logs(chunk_from, chunk_to, [TRANSFER, ZERO_TOPIC])
                calls += 1
            except Exception as e2:  # noqa: BLE001
                errors.append(f"Transfer chunk {chunk_from}-{chunk_to}: {e2}")
                print(f"ERROR Transfer chunk {chunk_from}-{chunk_to}: {e2}", flush=True)
                break
        for log in logs:
            topics = log.get("topics", [])
            addr = log.get("address", "")
            if len(topics) == 4:
                e = add(erc721, addr, log)
                e["minters"].add("0x" + topics[2][-40:])
            elif len(topics) == 3:
                e = add(erc20, addr, log)
                e["minters"].add("0x" + topics[2][-40:])
        time.sleep(2.2)
        # ERC-1155 mints: topic0 TransferSingle, topic2 (from) zero.
        # Try positional wildcard first; fall back to selector-only.
        ts_logs = None
        for topic_filter in ([TS_SINGLE, None, ZERO_TOPIC], [TS_SINGLE]):
            try:
                ts_logs, _ = ankr_logs(chunk_from, chunk_to, topic_filter)
                calls += 1
                break
            except Exception as e:  # noqa: BLE001
                if len(topic_filter) > 1 and topic_filter[1] is None:
                    continue
                errors.append(f"TransferSingle chunk {chunk_from}-{chunk_to}: {e}")
                print(f"ERROR TransferSingle chunk {chunk_from}-{chunk_to}: {e}", flush=True)
                ts_logs = []
        for log in (ts_logs or []):
            topics = log.get("topics", [])
            if len(topics) >= 3 and topics[2].lower() == ZERO_TOPIC:
                e = add(erc1155, log.get("address", ""), log)
                e["minters"].add("0x" + topics[3][-40:] if len(topics) >= 4 else "?")
        time.sleep(2.2)
        print(f"chunk {chunk_from}-{chunk_to}: ERC721 contracts so far {len(erc721)}, "
              f"ERC1155 {len(erc1155)}, ERC20-mint {len(erc20)}", flush=True)
        chunk_from = chunk_to + 1

    # Cheap agent-shape checks per distinct NFT contract.
    # Enrichment logs progress per contract (flush) and rewrites the output
    # JSON after EACH contract, so a kill/stall mid-enrichment leaves a
    # usable partial file instead of losing the whole 1000-block window
    # (run 1401: SCAN_EXIT=143 after 3m35s silent enrichment, no JSON).
    contracts = []
    total_nft = len(erc721) + len(erc1155)
    idx = 0

    def build_report(partial):
        hive = [c for c in contracts if c["address"].lower() == HIVE_AGENTS.lower()]
        return {
            "latest_block": latest, "from_block": from_block, "to_block": to_block,
            "ankr_calls": calls, "errors": errors,
            "erc20_mint_contracts": len(erc20),
            "erc20_mint_contracts_list": [
                {"address": addr, "mint_count": e["mint_count"],
                 "distinct_minters": len(e["minters"]),
                 "first_block": e["first_block"], "last_block": e["last_block"]}
                for addr, e in sorted(erc20.items(), key=lambda kv: -kv[1]["mint_count"])
            ],
            "contracts": contracts,
            "hive_agents_found": bool(hive),
            "hive_agents": hive[0] if hive else None,
            "partial": partial,
        }

    def write_report(partial):
        if not args.out:
            return
        tmp = args.out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(build_report(partial), f, indent=1)
        os.replace(tmp, args.out)

    for kind, store in (("ERC721", erc721), ("ERC1155", erc1155)):
        for addr, e in sorted(store.items(), key=lambda kv: -kv[1]["mint_count"]):
            idx += 1
            print(f"enrich {idx}/{total_nft} {kind} {addr}", flush=True)
            code = None
            try:
                code = rpc_call("eth_getCode", [addr, "latest"])
            except Exception as ex:  # noqa: BLE001
                errors.append(f"getCode {addr}: {ex}")
            registry_hit = None
            if isinstance(code, str) and len(code) > 2:
                registry_hit = REGISTRY_BYTES in code[2:].lower()
            status, abi = sourcify_abi(addr)
            free_funcs, mint_funcs = [], []
            if isinstance(abi, list):
                for item in abi:
                    if item.get("type") != "function":
                        continue
                    nm = item.get("name", "")
                    # Curated free-shape test: substring 'free' but NOT
                    # 'freeze...' (e.g. freezeMetadata is a metadata lock,
                    # not a free mint). A name list is used, not a raw
                    # substring dump, to avoid false positives.
                    if "free" in nm.lower() and not nm.lower().startswith("freeze"):
                        free_funcs.append(nm)
                    if "mint" in nm.lower():
                        mint_funcs.append(nm)
            name = symbol = None
            for sel, slot in ((NAME_SEL, "name"), (SYMBOL_SEL, "symbol")):
                try:
                    out = rpc_call("eth_call", [{"to": addr, "data": sel}, "latest"])
                    val = decode_str_or_bytes32(out)
                    if slot == "name":
                        name = val
                    else:
                        symbol = val
                except Exception:  # noqa: BLE001
                    pass
            contracts.append({
                "address": addr, "kind": kind,
                "mint_count": e["mint_count"],
                "distinct_minters": len(e["minters"]),
                "minters_sample": sorted(e["minters"])[:5],
                "first_block": e["first_block"], "last_block": e["last_block"],
                "registry_bytes_hit": registry_hit,
                "sourcify": status,
                "free_shaped": sorted(set(free_funcs))[:10],
                "mint_funcs": sorted(set(mint_funcs))[:10],
                "name": name, "symbol": symbol,
            })
            print(f"enrich {idx}/{total_nft} {addr} done registry={registry_hit} "
                  f"sourcify={status} name={name} symbol={symbol}", flush=True)
            write_report(partial=True)

    hive = [c for c in contracts if c["address"].lower() == HIVE_AGENTS.lower()]
    report = build_report(partial=False)
    if args.out:
        write_report(partial=False)
        print(f"wrote {args.out}", flush=True)
    print(f"\nRESULT: {len(contracts)} NFT contracts, "
          f"{sum(c['mint_count'] for c in contracts)} NFT mints, "
          f"{len(erc20)} ERC-20 mint contracts (excluded)")
    print(f"HIVE Agents found in window: {bool(hive)}")
    if hive:
        print(json.dumps(hive[0], indent=1))
    for c in contracts:
        print(f"  {c['kind']} {c['address']} mints={c['mint_count']} "
              f"minters={c['distinct_minters']} registry={c['registry_bytes_hit']} "
              f"sourcify={c['sourcify']} name={c['name']} symbol={c['symbol']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
