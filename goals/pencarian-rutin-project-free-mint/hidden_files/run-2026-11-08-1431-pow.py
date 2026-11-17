"""Paw Gang PoW: find nonce s.t. keccak256(abi.encodePacked(user, nonce)) has >=30 leading zero bits."""
import sys, time, json, os
from multiprocessing import Process, Value, Event
from Crypto.Hash import keccak
USER = bytes.fromhex("eb237F6f9FB4e826739F0954e9768914F28b2c2E")
BITS = 30
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-08-1431-pow.json"
def leading_zero_bits(h: bytes) -> int:
    n = 0
    for b in h:
        if b == 0: n += 8
        else:
            n += 8 - b.bit_length()
            break
    return n
def worker(start, step, found, nonce_out, stop):
    k = keccak.new(digest_bits=256)
    n = start
    tries = 0
    while not stop.is_set():
        # keccak256(address(20 bytes) + nonce(32 bytes BE))
        k2 = keccak.new(digest_bits=256)
        k2.update(USER + n.to_bytes(32, "big"))
        h = k2.digest()
        if leading_zero_bits(h) >= BITS:
            with nonce_out.get_lock():
                if nonce_out.value == -1:
                    nonce_out.value = n
            found.set(); stop.set()
            print(f"FOUND nonce={n} tries={tries}", flush=True)
            return
        n += step
        tries += 1
        if tries % 5000000 == 0:
            print(f"worker start={start} nonce={n} tries={tries}", flush=True)
if __name__ == "__main__":
    t0 = time.time()
    found = Event(); stop = Event()
    nonce_out = Value("q", -1)
    procs = []
    import random
    base = random.randrange(0, 2**40)
    for i in range(4):
        p = Process(target=worker, args=(base + i, 4, found, nonce_out, stop))
        p.start(); procs.append(p)
    for p in procs: p.join()
    el = time.time() - t0
    if nonce_out.value != -1:
        json.dump({"nonce": nonce_out.value, "bits": BITS, "user": "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E", "elapsed_sec": round(el,1), "difficultyBits": 30}, open(OUT, "w"), indent=1)
        print("WROTE", OUT, "nonce", nonce_out.value, "elapsed", round(el,1), flush=True)
    else:
        print("NOT FOUND elapsed", round(el,1), flush=True)
