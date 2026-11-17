"""Deep probe of the 2 registry-hit feed contracts (0x8fa0 ERC20 spots-sale,
0xe227 ERC721 mint). READ-ONLY. Probes price/quote/costOf/spots/free views +
string constants WEBSITE/TWITTER. Writes run-2026-11-05-1831-feed-probe.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    raw = bytes.fromhex(out[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64+ln].decode("utf-8", "replace")
        except Exception:
            pass
    return None

UP = USER[2:].lower().rjust(64, "0")
OUT = {}
for addr, noarg in [("0x8fa0714E0B79101Fa9ab694FB10CA5063AF3560A", ["PRICE()", "spotsLeft()", "totalSpotsMinted()", "MAX_SPOTS()", "PER_SPOT()", "poolBalance()", "totalSupply()", "CAP()", "MAX_PER_WALLET()", "progressBps()"]),
                    ("0xe22763bBaa9aA11a88b47E6f604c5DED0510DDE6", ["PRICE()", "spotsLeft()", "totalMinted()", "totalSupply()", "MAX_SUPPLY()", "MAX_PER_WALLET()", "nextTokenId()"])]:
    rec = {}
    for sig in noarg:
        try:
            rec[sig] = dec_uint(rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, "latest"]))
        except Exception as e:
            rec[sig] = "error:" + type(e).__name__
    for sig in ["quote(address,uint256)", "costOf(address,uint256)", "mintedBy(address)", "minted(address)", "balanceOf(address)", "freeClaimed(address)", "freeFor(address)", "agentIds(address)"]:
        try:
            data = sel(sig) + UP + "0000000000000000000000000000000000000000000000000000000000000001" if "uint256" in sig else sel(sig) + UP
            rec[sig] = dec_uint(rpc_call("eth_call", [{"to": addr, "data": data}, "latest"]))
        except Exception as e:
            rec[sig] = "error:" + type(e).__name__
    for sig in ["WEBSITE()", "TWITTER()", "name()", "symbol()"]:
        try:
            rec[sig] = dec_str(rpc_call("eth_call", [{"to": addr, "data": sel(sig)}, "latest"]))
        except Exception as e:
            rec[sig] = "error:" + type(e).__name__
    try:
        rec["AGENT_REGISTRY()"] = rpc_call("eth_call", [{"to": addr, "data": sel("AGENT_REGISTRY()")}, "latest"])
    except Exception as e:
        rec["AGENT_REGISTRY()"] = "error:" + type(e).__name__
    # block time of contract creation approx: first Transfer-from-zero via Ankr getLogs
    OUT[addr] = rec
    print(addr, json.dumps(rec, indent=1), flush=True)

json.dump(OUT, open(HF + "run-2026-11-05-1831-feed-probe.json", "w"), indent=1)
print("WROTE run-2026-11-05-1831-feed-probe.json")
