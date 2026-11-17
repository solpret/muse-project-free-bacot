import sys, json, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
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
    "Spookagent": "0x90f9de2A0Ab81052a0959bd71B46cdcFd57152eB",
    "Chromagent": "0x895087300b81956e3242Be7132d55dB90Af0DEBD",
    "Scarabagent": "0xFC4482e1c66DfDabe4fCCeC0F7A6C480b85C3a47",
    "NIANNIAN": "0x4A2bb7B24C39CA548b050aD0C0aFfea5e6e04aF2",
}
for name, addr in TARGETS.items():
    vals = {}
    for sig, args in [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("totalMinted()", ""), ("freeMinted()", ""), ("mintOpen()", ""), ("mintedBy(address)", pad), ("freeUsed(address)", pad), ("balanceOf(address)", pad), ("owner()", ""), ("quote(address,uint256)", pad + "0"*63 + "1"), ("agentFreeClaimed(address)", pad), ("freeMintedShares()", ""), ("MAX_FREE_CLAIMS()", "")]:
        vals[sig] = call(addr, sig, args)
    print(name, vals, flush=True)
    try:
        raw = subprocess.run(["curl", "-sL", "--max-time", "25", f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"], capture_output=True, text=True).stdout
        d = json.loads(raw); abi = d.get("abi", [])
        fns = sorted({f["name"] for f in abi if f.get("type") == "function"})
        print(name, "ABI fns", len(fns), "AGENT_ID:", "AGENT_ID" in fns, "agentRegistry:", "agentRegistry" in fns, "free:", [f for f in fns if "free" in f.lower() and not f.lower().startswith("freeze")], "mint:", [f for f in fns if "mint" in f.lower()], "contractURI:", "contractURI" in fns, flush=True)
    except Exception as e: print(name, "ABI ERR", type(e).__name__, str(e)[:120], flush=True)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(131200000), "toBlock": hex(131390000), "address": addr, "pageSize": 1000, "decodeLogs": False}, timeout=90)
        logs = body.get("result", {}).get("logs", [])
        zero = "0x" + "00"*32
        mints = [l for l in logs if len(l.get("topics", [])) > 1 and l["topics"][1] == zero] if logs else []
        eb = min((int(l["blockNumber"], 16) for l in mints), default=None)
        print(name, "ankr logs:", len(logs), "mint logs:", len(mints), "earliest mint block:", eb, "latest:", max((int(l["blockNumber"], 16) for l in mints), default=None), flush=True)
        if eb:
            blk = rpc_call("eth_getBlockByNumber", [hex(eb), False])
            ts = int(blk["timestamp"], 16) if isinstance(blk, dict) else None
            print(name, "earliest mint block ts:", ts, flush=True)
    except Exception as e: print(name, "ankr ERR", type(e).__name__, str(e)[:150], flush=True)
print("DONE")
