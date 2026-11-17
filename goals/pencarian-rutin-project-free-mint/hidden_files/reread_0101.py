#!/usr/bin/env python3
"""Route-1 re-read run 0101 (2026-11-06 01:01 WIB). Read-only.
Reads standard views for the active watchlist subset + new Boltbook leads
+ track-C / track-B re-checks. A failed read is None (never zero)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr(a):
    return "000000000000000000000000" + a[2:].lower()

def enc_uint(n):
    return format(n, "064x")

def call(addr, data, timeout=7):
    last = None
    for ep in EPS:
        try:
            return _single(ep, "eth_call", [{"to": addr, "data": data}, "latest"], timeout, retries=0)
        except Exception as e:
            last = e
    return {"_error": f"{type(last).__name__}: {str(last)[:120]}"}

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_bool(out):
    v = dec_uint(out)
    return None if v is None else bool(v)

VIEWS = {
    "totalSupply": ("totalSupply()", "uint"),
    "totalMinted": ("totalMinted()", "uint"),
    "freeClaimed": ("freeClaimed()", "uint"),
    "freeMinted": ("freeMinted()", "uint"),
    "FREE_SUPPLY": ("FREE_SUPPLY()", "uint"),
    "MAX_SUPPLY": ("MAX_SUPPLY()", "uint"),
    "mintOpen": ("mintOpen()", "bool"),
    "price": ("price()", "uint"),
    "owner": ("owner()", "addr"),
    "launched": ("launched()", "bool"),
    "isRefundPhase": ("isRefundPhase()", "bool"),
    "giftsClaimed": ("giftsClaimed()", "uint"),
    "totalMints": ("totalMints()", "uint"),
    "freeLeft": ("freeLeft()", "uint"),
    "opened": ("opened()", "bool"),
    "phase": ("phase()", "uint"),
    "freeOpen": ("freeOpen()", "bool"),
}
ARGS = {
    "quote_user_1": ("quote(address,uint256)", "uint", [USER, 1]),
    "mintedBy_user": ("mintedBy(address)", "uint", [USER]),
    "freeUsed_user": ("freeUsed(address)", "uint", [USER]),
    "freeLeft_user": ("freeLeft(address)", "uint", [USER]),
    "balanceOf_user": ("balanceOf(address)", "uint", [USER]),
    "giftTaken_user": ("giftTaken(address)", "bool", [USER]),
    "tokenClaimed_user": ("tokenClaimed(address)", "bool", [USER]),
    "freeClaimed_user": ("freeClaimed(address)", "uint", [USER]),
    "freeMinted_user": ("freeMinted(address)", "uint", [USER]),
    "costOf_user_1": ("costOf(address,uint256)", "uint", [USER, 1]),
    "costOf_user_2": ("costOf(address,uint256)", "uint", [USER, 2]),
    "mintsLeft_user": ("mintsLeft(address)", "uint", [USER]),
}

CONTRACTS = [
    ("HIVE Agents", "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", ["totalSupply", "balanceOf_user"]),
    ("Moonfall", "0x4232308c31927e493e96FdB05134Fa39C26c24D0", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Binance Agent", "0xE3a382B8e577A58A5540420C11ABa287C62e49f4", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("GHOST", "0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Sonofluidic", "0x1eF7588Dff561b7390D3AF23d06E684D64217419", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Mossminds", "0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Snail Mail", "0xb773e52fE45196c840F8e59c3B4bB944633Ae03a", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]),
    ("Agent Coffee", "0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]),
    ("Driftnauts", "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]),
    ("AGENTIC PERP", "0xf1CE53a4BA97a9BaE4b6CBd15f917D42983a4fBB", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]),
    ("Agent Wallet", "0x1aeEf8218815F7639eA3544D5c57122675A00805", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user"]),
    ("Night Shift", "0x427aed3f7427b48e45f5e648105aa1b77724cf14", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("PRICKLY", "0x4e557ae3824ae3e837aa4a8da2a45a04501beaee", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("unicorn.exe", "0x965286f9662a6dACeFf9bD3C4D58ABaBDD9C87A5", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Blend In", "0x9ca2c07b67cd97109f40378ae90c815feb878b1f", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Buzzkill", "0x4854ce8e3ec3a1acb0dd4eae3f547e5a214c2a0d", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Cuprihive", "0x1e9460475825a3218cd36b8d35a0698d6939aaec", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Skyagent", "0x83decf8076d04d59da771da6bb298132164be55b", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Rookling", "0xe76a5bf585f9378b065d48f1a49d90ecf71ebeba", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "freeLeft_user", "balanceOf_user", "owner"]),
    ("Flyingsquirrelai", "0x9e14822255f2f287f5ef233e4cf8580481dcf75e", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "price", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Dewata", "0x13628D733A26b942213BA1b3C61471925D4a2165", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Agent Frogs", "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("WAGagent", "0x06a6f51D30556f4262e38485C09556fE81e6A984", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Thronemind", "0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Hashseers", "0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Layerloom", "0x1B72ceC52A74537b06F713FCebA0e491f53679aE", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Smeltbots", "0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Tumblebots", "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Forklings", "0xD7B3FD33e0b465B0e374906F60567D317b758FD8", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("Neurolucha", "0x56eBED63452Bb02B975ceE02949DA3C02466725b", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("BNB CACHE Server", "0x1989058Da9eb7F36E69779fCda0EA04578528570", ["totalSupply", "totalMinted", "freeClaimed", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintOpen", "quote_user_1", "mintedBy_user", "freeUsed_user", "balanceOf_user", "owner"]),
    ("BINANCEAI-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", ["launched", "isRefundPhase", "tokenClaimed_user"]),
    ("NJAR-sale", "0x816458b734d17d59058762deaadd9b952bad6985", ["giftsClaimed", "totalSupply", "mintOpen", "giftTaken_user", "quote_user_1"]),
    ("PRDICT-sale", "0x8fF4bd65584882324c44Ee794a23E7791820189b", ["totalMints", "freeLeft", "mintOpen", "quote_user_1", "freeClaimed_user"]),
    ("DROID-sale", "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177", ["totalSupply", "freeClaimed", "mintOpen", "quote_user_1", "freeClaimed_user"]),
    ("OSK-sale", "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37", ["opened", "totalSupply", "freeClaimed", "quote_user_1", "freeClaimed_user"]),
    ("IMARS-sale", "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f", ["opened", "totalSupply", "freeClaimed", "quote_user_1", "freeClaimed_user"]),
    ("NIULAI-sale", "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF", ["launched", "phase", "freeClaimed", "totalSupply", "freeClaimed_user"]),
    ("Whale Alert", "0xA1ecd20893Dbb2BEDc7141434d20125F028E871B", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Fresh Hatch", "0xC3Ba321124e0F621Da8C4A0c1875705c83d6ce8C", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Lion's Share", "0x6AC03204aFE631D673938Eb82D2F121B015eAB3F", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Otter Nonsense", "0xFF6b4bb96C86c0E2e2F942F907F9F6eD1bBbCaDf", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Hot Springs", "0xc7bFeA97f02E9118eD88111A79E43a9CE481B96A", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Down Under", "0x5Bb425ad2069de77ABC8c341d4d322Bcff26c550", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Toucan Play", "0x5ABe8974d554Ea0c797fBC4c6B01EA4446616B2f", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("jelly.exe", "0x807E86F6d1bc8fc5E8f53052DAC5d379D4efc120", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Los Flamingos", "0x4c34027BA34A20b85F0aAb18A9a7fE46c9208571", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Moonhowlers", "0x104381eaF387cE95618bA7B4bfBC101BC98E728B", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Counting Sheep", "0xE726710Dd5258531a1beCb5BFF7592ADc3620593", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Tusk & Trunk", "0x30AeAE09dB59fa202f6d8a518AA0cC1a2838f5D0", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("getpuffr", "0xCEE93a5BFAD6172358F6012A08D83f0D6d7BaD46", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Hippo Social Club", "0x3bbABBDB7451AD28206052F8d29D24e0eAEF7Fd7", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("LLAMA DRAMA", "0x659328E1AAC4f6c006c9Cb2f6E3483af31893981", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("Danger Noodles", "0x8a150fd93b5026d061ADda023B8b8CfdBd7c1202", ['totalSupply', 'price', 'costOf_user_1', 'costOf_user_2', 'mintsLeft_user', 'mintedBy_user', 'balanceOf_user', 'owner']),
    ("WHALE", "0x8a3e3eea10e1fa7d6fa768550f8e572a15eb90d0", ['totalSupply', 'totalMinted', 'freeClaimed', 'freeMinted', 'FREE_SUPPLY', 'MAX_SUPPLY', 'mintOpen', 'quote_user_1', 'mintedBy_user', 'freeUsed_user', 'balanceOf_user', 'owner']),
    ("Agent Grove", "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c", ['totalSupply', 'freeClaimed', 'FREE_SUPPLY', 'freeOpen', 'mintOpen', 'quote_user_1', 'balanceOf_user']),
    ("BINANCEAI-token", "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c", ['balanceOf_user']),
    ("LuckyBox-sale", "0xd08ef372B52C29255fEd7004f59bF41571451894", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("DeY-sale", "0xDB062c12bF0a14227e7Fe896a988950b050B51C1", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("FANBEIMAO-sale", "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Nvagent-sale", "0x7Eb3a26F895d4D1b8FcD38A67E9689cB2693661f", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Nvagent-28Fe-sale", "0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Hongbao-sale", "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Soarm-sale", "0x7ba14e1119d31E876Cc4aa52a0bcB9E43C841799", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Pacture-sale", "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("Ikigai-sale", "0x3611455bE1FC2c6987FE9d016971b7E40B341684", ['totalSupply', 'freeClaimed', 'freeMinted', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("KillZero-sale", "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97", ['launched', 'totalSupply', 'freeClaimed', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("960E-sale", "0x960E7e4126b97679053B8416fA59f13508be88bf", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
    ("CHTCI-sale", "0x050a11c2bfcf881b546983a20550a0e409bf69da", ['totalSupply', 'freeClaimed', 'mintOpen', 'quote_user_1', 'freeClaimed_user', 'balanceOf_user']),
]

def build_data(name):
    if name in VIEWS:
        sig, kind = VIEWS[name]
        return sel(sig), kind
    sig, kind, args = ARGS[name]
    data = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x"):
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    return data, kind

def decode(kind, out):
    if isinstance(out, dict):
        return None
    if kind == "uint":
        return dec_uint(out)
    if kind == "bool":
        return dec_bool(out)
    if kind == "addr":
        if isinstance(out, str) and len(out) >= 66:
            return "0x" + out[26:66]
        return None
    return out

def main():
    try:
        blk = None
        for ep in EPS:
            try:
                blk = int(_single(ep, "eth_blockNumber", [], 7, retries=0), 16)
                break
            except Exception:
                continue
    except Exception:
        blk = None
    print(f"read block: {blk}")
    results = {"block": blk, "contracts": {}}
    for label, addr, views in CONTRACTS:
        entry = {"address": addr}
        for v in views:
            data, kind = build_data(v)
            out = call(addr, data)
            entry[v] = decode(kind, out)
        results["contracts"][label] = entry
        print(f"{label}: " + ", ".join(f"{k}={entry[k]}" for k in views if entry[k] is not None) + (" [some None]" if any(entry[k] is None for k in views) else ""))
    with open("reread-2026-11-06-0101.json", "w") as f:
        json.dump(results, f, indent=1)
    print("wrote reread-2026-11-06-0101.json")

if __name__ == "__main__":
    main()
