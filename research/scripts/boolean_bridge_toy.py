"""Exact Boolean-to-F2 affine-R1CS relation compiler for a two-residue toy.

This is arithmetic/circuit verification only. No cryptographic prover,
commitment, random oracle, or protocol interaction is implemented.
"""
from collections import Counter
from math import isqrt
import json
import random


Q_OLD = 4294967197
BOUND_SQUARED = 65
TARGET_SUM = 7
ELL = 129


class Circuit:
    def __init__(self, input_bits):
        # w[0]=1 is separately pinned; H contains w[1]=0.
        self.one, self.zero = 0, 1
        self.inputs = list(range(2, 2 + input_bits))
        self.wire_count = 2 + input_bits
        self.gates = []
        self.stages = {}

    def gate(self, op, a, b=None):
        out = self.wire_count
        self.wire_count += 1
        self.gates.append((op, a, b, out))
        return out

    def xor(self, a, b):
        return self.gate("XOR", a, b)

    def and_(self, a, b):
        return self.gate("AND", a, b)

    def not_(self, a):
        return self.gate("NOT", a)

    def or_(self, a, b):
        return self.xor(self.xor(a, b), self.and_(a, b))

    def bits(self, value, width):
        assert 0 <= value < 1 << width
        return [self.one if value >> i & 1 else self.zero for i in range(width)]

    def add(self, a, b, carry=None):
        """Full n-bit ripple add: 3n XOR, 2n AND, returns n+1 bits."""
        assert len(a) == len(b)
        carry = self.zero if carry is None else carry
        out = []
        for u, v in zip(a, b):
            t = self.xor(u, v)
            out.append(self.xor(t, carry))
            # The two carry terms cannot simultaneously be one.
            carry = self.xor(self.and_(u, v), self.and_(t, carry))
        return out + [carry]

    def le_constant(self, a, bound):
        """Unsigned <= bound, by the carry of a-(bound+1)."""
        width = len(a)
        assert 0 <= bound < (1 << width) - 1
        complement = ((1 << width) - 1) ^ (bound + 1)
        carry = self.add(a, self.bits(complement, width), self.one)[-1]
        return self.not_(carry)

    def eq_constant(self, a, value):
        differences = [self.xor(u, v) for u, v in zip(a, self.bits(value, len(a)))]
        different = differences[0]
        for bit in differences[1:]:
            different = self.or_(different, bit)
        return self.not_(different)

    def select(self, bit, if_zero, if_one):
        assert len(if_zero) == len(if_one)
        return [self.xor(u, self.and_(bit, self.xor(u, v)))
                for u, v in zip(if_zero, if_one)]

    def centered_magnitude(self, residue):
        """For canonical residues, exact |center_q(residue)| in 32 bits."""
        negative = self.not_(self.le_constant(residue, (Q_OLD - 1) // 2))
        complemented = [self.not_(bit) for bit in residue]
        q_minus_z = self.add(self.bits(Q_OLD, 32), complemented, self.one)[:32]
        return self.select(negative, residue, q_minus_z)

    def multiply(self, a, b):
        """Schoolbook n*n unsigned product; all 2n-bit adders are counted."""
        assert len(a) == len(b)
        n = len(a)
        accumulator = [self.zero] * (2 * n)
        for j, bit in enumerate(b):
            row = [self.zero] * j + [self.and_(u, bit) for u in a]
            row += [self.zero] * (2 * n - len(row))
            accumulator = self.add(accumulator, row)[:2 * n]
        return accumulator

    def stage(self, name, start):
        counts = Counter(op for op, _, _, _ in self.gates[start:])
        self.stages[name] = {**dict(counts), "total": sum(counts.values())}

    def evaluate(self, input_values):
        assert len(input_values) == len(self.inputs)
        assert all(bit in (0, 1) for bit in input_values)
        values = [1, 0] + list(input_values)
        for op, a, b, out in self.gates:
            assert out == len(values)
            if op == "AND":
                values.append(values[a] * values[b])
            elif op == "XOR":
                values.append(values[a] ^ values[b])
            else:
                assert op == "NOT"
                values.append(values[a] ^ 1)
        return values

    def affine_r1cs(self, output):
        """Sparse F2 matrices: one AND row and one H row per affine gate.

        Rows are tuples of nonzero column indices. Repeated indices cancel
        in F2; keeping repetitions in this representation is unambiguous.
        """
        quadratic, linear = [], [(self.zero,)]
        for op, a, b, out in self.gates:
            if op == "AND":
                quadratic.append(((a,), (b,), (out,)))
            elif op == "XOR":
                linear.append((a, b, out))
            else:
                linear.append((a, out, self.one))
        linear.append((output, self.one))
        return quadratic, linear


def compile_relation():
    circuit = Circuit(64)
    x, y = circuit.inputs[:32], circuit.inputs[32:]
    start = len(circuit.gates)
    range_checks = [circuit.le_constant(z, Q_OLD - 1) for z in (x, y)]
    circuit.stage("canonical_ranges", start)

    start = len(circuit.gates)
    full_sum = circuit.add(x, y)
    # Canonical x,y imply 0<=x+y<=2q-2, so these are exactly the two cases.
    modular_check = circuit.or_(circuit.eq_constant(full_sum, TARGET_SUM),
                                circuit.eq_constant(full_sum, Q_OLD + TARGET_SUM))
    circuit.stage("old_modular_equation", start)

    start = len(circuit.gates)
    magnitudes = [circuit.centered_magnitude(z) for z in (x, y)]
    circuit.stage("exact_centered_magnitudes", start)

    start = len(circuit.gates)
    squares = [circuit.multiply(z, z) for z in magnitudes]
    circuit.stage("two_exact_64_bit_squares", start)

    start = len(circuit.gates)
    norm_squared = circuit.add(*squares)
    assert len(norm_squared) == 65
    norm_check = circuit.le_constant(norm_squared, BOUND_SQUARED)
    circuit.stage("65_bit_norm_sum_and_comparison", start)

    start = len(circuit.gates)
    checks = range_checks + [modular_check, norm_check]
    output = checks[0]
    for check in checks[1:]:
        output = circuit.and_(output, check)
    circuit.stage("conjunction", start)
    return circuit, output, norm_squared


def old_relation(x, y):
    if not (0 <= x < Q_OLD and 0 <= y < Q_OLD):
        return False
    center = lambda z: z if z <= (Q_OLD - 1) // 2 else z - Q_OLD
    return ((x + y) % Q_OLD == TARGET_SUM and
            center(x) ** 2 + center(y) ** 2 <= BOUND_SQUARED)


def prime(q):
    if q < 2 or q % 2 == 0:
        return q == 2
    return all(q % divisor for divisor in range(3, isqrt(q) + 1, 2))


def next_prime_5mod8(lower):
    q = lower + ((5 - lower) % 8)
    while not prime(q):
        q += 8
    return q


def main():
    assert prime(Q_OLD) and Q_OLD.bit_length() == 32 and Q_OLD % 8 == 5
    circuit, output, norm_wires = compile_relation()
    quadratic, linear = circuit.affine_r1cs(output)
    gates = Counter(op for op, _, _, _ in circuit.gates)
    n, k, h = circuit.wire_count, len(quadratic), len(linear)
    assert n == 2 + 64 + sum(gates.values())
    assert k == gates["AND"] and h == gates["XOR"] + gates["NOT"] + 2
    M = n + (3 + ELL) * k

    # Use the reviewed core slack s^2=23/5. An exact sufficient start is 9M.
    # The strict lift inequality is q > (23/5 + 2sqrt(23/5))*M.
    q_new = next_prime_5mod8(9 * M)
    margin = 5 * q_new - 23 * M
    assert margin > 0 and margin * margin > 460 * M * M
    assert q_new * q_new >= 287500 * M  # beta_h<=q_new/(250sqrt(23/5)).
    assert 32 < q_new < Q_OLD and prime(q_new)

    cases = [(3, 4), (Q_OLD - 1, 8), (Q_OLD - 2, 9), (0, 7), (2, 6),
             (Q_OLD + 3, 4), (Q_OLD, 7), (2**32 - 1, 0), (0, 0),
             ((Q_OLD - 1) // 2, (Q_OLD + 1) // 2)]
    cases += [(a % Q_OLD, b % Q_OLD) for a in range(-10, 11)
              for b in range(-10, 11)]
    rng = random.Random(20261114)
    cases += [(rng.randrange(2**32), rng.randrange(2**32)) for _ in range(64)]
    accepted = 0
    accepted_distinct = set()
    for x, y in cases:
        inputs = [(x >> i) & 1 for i in range(32)] + [(y >> i) & 1 for i in range(32)]
        assignment = circuit.evaluate(inputs)
        actual = bool(assignment[output])
        assert actual == old_relation(x, y)
        # All gate rows hold, even when the output-one row rejects.
        parity = lambda row: sum(assignment[j] for j in row) % 2
        assert assignment[0] == 1
        assert all(parity(a) * parity(b) == parity(c) for a, b, c in quadratic)
        assert all(parity(row) == 0 for row in linear[:-1])
        assert (parity(linear[-1]) == 0) == actual
        if 0 <= x < Q_OLD and 0 <= y < Q_OLD:
            expected = sum((z if z <= (Q_OLD - 1)//2 else z-Q_OLD)**2 for z in (x,y))
            assert sum(assignment[j] << i for i, j in enumerate(norm_wires)) == expected
        accepted += actual
        if actual:
            accepted_distinct.add((x, y))

    assert accepted_distinct == {(a % Q_OLD, (7-a) % Q_OLD) for a in range(-1, 9)}
    L = 32
    assert len(circuit.gates) == 22*L*L + 71*L + 22
    assert gates["AND"] == 10*L*L + 26*L + 6
    assert gates["XOR"] == 12*L*L + 43*L + 7
    assert gates["NOT"] == 2*L + 9

    # Deliberately modify an AND output: its own sparse R1CS row detects it.
    assignment = circuit.evaluate([0] * 64)
    a, b, c = quadratic[0]
    assignment[c[0]] ^= 1
    assert (sum(assignment[j] for j in a) % 2) * (sum(assignment[j] for j in b) % 2) != sum(assignment[j] for j in c) % 2

    print(json.dumps({
        "scope": "exact relation/circuit reduction only; no crypto protocol",
        "q_old": Q_OLD, "q_old_bits": 32,
        "source_relation": "canonical x,y; x+y=7 mod q_old; centered squares sum <=65",
        "witness_input_bits": 64, "norm_accumulator_bits": 65,
        "gate_counts": dict(gates), "gate_total": len(circuit.gates),
        "stages": circuit.stages,
        "affine_F2_R1CS": {"n_including_one_zero_and_inputs": n, "k_AND_rows": k,
                           "h_linear_rows": h, "one_wire_separately_pinned": True},
        "ell": ELL, "source_aggregation_error": "2^-128", "M": M,
        "parity_frontend_direct_verifier_ledger": {
            "first_commitment_columns": n + 3*k,
            "second_commitment_columns": ELL*k,
            "aggregate_linear_product_terms": ELL*M,
            "aggregate_quadratic_product_terms": ELL*k,
            "source_delta_challenge_entries": ELL*ELL*k,
            "opening_norm_scalar_coefficients_at_d64": 64*M,
            "commitment_product_terms_symbolic": f"{n+3*k}*m0 + {ELL*k}*m1"
        },
        "beta_h_squared": M, "beta_actual_squared": f"{23*M}/5",
        "q_new": q_new, "q_new_bits": q_new.bit_length(), "q_new_mod_8": q_new % 8,
        "strict_lifting_integer_margin": margin*margin - 460*M*M,
        "JL_parameter_integer_margin": q_new*q_new - 287500*M,
        "tested_input_pairs": len(cases), "accepted_pairs_in_test_list": accepted,
        "distinct_accepted_pairs_exhaust_all_solutions": len(accepted_distinct),
        "boundary_valid_pair": [Q_OLD-1, 8],
        "same_modular_equation_but_norm_invalid_pair": [Q_OLD-2, 9],
        "noncanonical_alias_rejected": [Q_OLD+3, 4],
        "warning": "No MSIS rank/security certificate or performance/SNARK claim."
    }, indent=2))


if __name__ == "__main__":
    main()
