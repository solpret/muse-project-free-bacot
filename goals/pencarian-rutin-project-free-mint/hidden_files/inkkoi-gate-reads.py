import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
ADDR = "0xbd4B4e7189ae9356514664146b0eD683601200A9"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_uint(n): return "0x" + format(n, "064x")
def call(sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": ADDR, "data": data}, "latest"], 8, retries=0)
        except Exception as e:
            last = e
    return f"ERROR: {last}"
def decode_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"DECODE-FAIL {e} raw={raw[:200]}"
out = {}
out["siteUrl_raw"] = call("siteUrl()")
out["siteUrl"] = decode_str(out["siteUrl_raw"]) if isinstance(out["siteUrl_raw"], str) and out["siteUrl_raw"].startswith("0x") else out["siteUrl_raw"]
out["contractURI_raw"] = call("contractURI()")
out["contractURI"] = decode_str(out["contractURI_raw"]) if isinstance(out["contractURI_raw"], str) and out["contractURI_raw"].startswith("0x") else out["contractURI_raw"]
out["tokenURI_1_raw"] = call("tokenURI(uint256)", enc_uint(1))
out["tokenURI_1"] = decode_str(out["tokenURI_1_raw"]) if isinstance(out["tokenURI_1_raw"], str) and out["tokenURI_1_raw"].startswith("0x") else out["tokenURI_1_raw"]
out["tokenURI_700_raw"] = call("tokenURI(uint256)", enc_uint(700))
out["tokenURI_700"] = decode_str(out["tokenURI_700_raw"]) if isinstance(out["tokenURI_700_raw"], str) and out["tokenURI_700_raw"].startswith("0x") else out["tokenURI_700_raw"]
print(json.dumps(out, indent=1)[:4000])
json.dump(out, open("inkkoi-gate-reads.json","w"), indent=1)
