import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import race
from Crypto.Hash import keccak
from onchain_nft_scan import rpc_call
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad = USER[2:].rjust(64, '0')
def call(addr, sig, args=""):
    try:
        r = rpc_call("eth_call", [{"to": addr, "data": "0x" + sel(sig) + args}, "latest"])
        if isinstance(r, str) and len(r) == 66: return int(r, 16)
        if isinstance(r, str) and len(r) == 130: return "0x" + r[-40:]
        return r
    except Exception as e: return f"ERR:{type(e).__name__}:{str(e)[:80]}"
TARGETS = {
    "Cipheragent": "0xb967642f8a74565a19d399b8be3fe73b618017ce",
    "Beatagent": "0x173d69d1ab7ebd0230950ea97f4fc3f70972665c",
}
for name, addr in TARGETS.items():
    vals = {}
    for sig, args in [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintOpen()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad), ("owner()", ""), ("quote(address,uint256)", pad + "0"*63 + "1"), ("name()", ""), ("symbol()", "")]:
        vals[sig] = call(addr, sig, args)
    print(name, vals, flush=True)
    try:
        raw = subprocess.run(["curl", "-sL", "--max-time", "25", f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"], capture_output=True, text=True).stdout
        d = json.loads(raw); abi = d.get("abi", [])
        fns = sorted({f["name"] for f in abi if f.get("type") == "function"})
        print(name, "ABI fns", len(fns), "AGENT_ID:", "AGENT_ID" in fns, "free:", [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")], "mint:", [f for f in fns if "mint" in f.lower()], "contractURI:", "contractURI" in fns, flush=True)
    except Exception as e: print(name, "ABI ERR", type(e).__name__, str(e)[:120], flush=True)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(131200000), "toBlock": hex(131388500), "address": addr, "pageSize": 1000, "decodeLogs": False}, timeout=60)
        logs = body.get("result", {}).get("logs", [])
        # Transfer from zero = mint: topic1 zero
        zero = "0x" + "00"*32
        mints = [l for l in logs if l.get("topics", [None, None])[1] == zero] if logs else []
        print(name, "ankr logs:", len(logs), "mint logs:", len(mints), "earliest mint block:", min((int(l["blockNumber"], 16) for l in mints), default=None), "latest:", max((int(l["blockNumber"], 16) for l in mints), default=None), flush=True)
    except Exception as e: print(name, "ankr ERR", type(e).__name__, str(e)[:150], flush=True)
print("DONE")
