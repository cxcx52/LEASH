"""Independent standard-library reference for the checked-in Rust KATs.

Run from any directory; writes only known_answers.json beside this script.
This is a deterministic arithmetic/encoding test, not a security experiment.
"""
import hashlib
import json
from pathlib import Path

Q, D = 4294967197, 64


def frame(data):
    return len(data).to_bytes(8, "little") + data


class Stream:
    def __init__(self, seed, domain):
        self.input = b"LEASH-XOF-v1\0" + frame(domain) + frame(seed)
        self.offset = 0

    def read(self, count):
        raw = hashlib.shake_256(self.input).digest(self.offset + count)
        result = raw[self.offset:]
        self.offset += count
        return result

    def uniform(self, modulus):
        cutoff = (1 << 64) - (1 << 64) % modulus
        while True:
            value = int.from_bytes(self.read(8), "little")
            if value < cutoff:
                return value % modulus

    def poly(self):
        return [self.uniform(Q) for _ in range(D)]


class Transcript:
    def __init__(self, domain):
        self.state = b"LEASH-TRANSCRIPT-v1\0" + frame(domain)
        self.counter = 0

    def absorb(self, label, message):
        self.state += b"\x01" + frame(label) + frame(message)

    def challenge(self, label):
        counter = self.counter.to_bytes(8, "little")
        self.counter += 1
        seed = hashlib.shake_256(self.state + b"\x02" + frame(label) + counter).digest(64)
        self.state += b"\x03" + frame(label) + counter + frame(seed)
        return Stream(seed, b"LEASH-TRANSCRIPT-CHALLENGE-v1")


def poly(values):
    return [x % Q for x in values] + [0] * (D - len(values))


def mul(left, right):
    out = [0] * D
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[(i + j) % D] += a * b * (1 if i + j < D else -1)
    return [x % Q for x in out]


def matrix_row(seed, domain, row, columns):
    stream = Stream(seed + row.to_bytes(8, "little"), b"LEASH-MATRIX-v1\0" + frame(domain))
    return [stream.poly() for _ in range(columns)]


def digest(polys):
    data = b"".join(x.to_bytes(8, "little") for p in polys for x in p)
    return hashlib.sha3_256(data).hexdigest()


def answers():
    a = poly([(-1) ** i * (i * i + 13) for i in range(D)])
    b = poly([(-1) ** (i // 3) * (7 * i + 2) for i in range(D)])
    stream = Stream(b"known-answer seed", b"core/test")
    uniform_q = [stream.uniform(Q) for _ in range(16)]
    stream = Stream(b"known-answer seed", b"core/test")
    large_modulus = (1 << 63) + 17  # rejection occurs often, unlike q.
    uniform_large = [stream.uniform(large_modulus) for _ in range(16)]
    stream = Stream(b"known-answer seed", b"core/test")
    bits = [bool(x & 1) for x in stream.read(32)]
    stream = Stream(b"known-answer seed", b"core/test")
    ternary = [(x & 1) - ((x >> 1) & 1) for x in stream.read(32)]
    transcript = Transcript(b"test/root")
    transcript.absorb(b"a", b"bc")
    transcript.absorb(b"ab", b"c")
    stream = transcript.challenge(b"coins")
    first = [stream.uniform(Q) for _ in range(8)]
    transcript.absorb(b"reply", b"\0hello")
    stream = transcript.challenge(b"coins")
    second = [stream.uniform(5) for _ in range(8)]
    stream = transcript.challenge(b"coins")
    third = [stream.uniform(Q) for _ in range(8)]
    seed = bytes(range(32))
    matrix = [matrix_row(seed, b"public/setup", row, 3) for row in range(2)]
    opening = [poly([1, -2, 3]), poly([-4, 5]), poly([7])]
    commitment = []
    for row in matrix:
        products = [mul(x, y) for x, y in zip(row, opening)]
        commitment.append([sum(p[i] for p in products) % Q for i in range(D)])
    return {
        "provenance": "Python standard-library hashlib SHAKE256 and arbitrary-precision integer negacyclic arithmetic",
        "dense_product": mul(a, b), "uniform_q": uniform_q,
        "uniform_large": uniform_large, "bits": bits, "ternary": ternary,
        "transcript_first": first, "transcript_second": second, "transcript_third": third,
        "matrix_sha3_256": digest([p for row in matrix for p in row]),
        "commitment_sha3_256": digest(commitment),
    }


if __name__ == "__main__":
    Path(__file__).with_name("known_answers.json").write_text(
        json.dumps(answers(), indent=2) + "\n", encoding="utf-8"
    )
