import itertools
import unittest
from fractions import Fraction as F
from labrador_repair.bounds import (challenge_cube, jl_certificate, lifting_condition,
                                    statistical_budget, validate_ring)
from labrador_repair.ring import centered, encode, evaluate, gcd_mod, negacyclic_multiply
from labrador_repair.r1cs import source_relation, linear_coefficients, encoded_residual


class Repairs(unittest.TestCase):
    def test_numeric_certificate(self):
        result = jl_certificate()
        for name in ("small_norm_upper", "large_coordinate_upper", "spread_upper"):
            self.assertLess(result[name], F(1, 2**164))
        self.assertEqual(result["honest_rejection_upper"], F(8, 33))

    def test_fourth_moment_by_full_enumeration(self):
        for w in ((1,), (1, 1), (1, 2, 3), (2, -1, 0, 3)):
            second = fourth = F(0)
            for row in itertools.product((-1, 0, 1), repeat=len(w)):
                weight = F(1, 4**len(w))
                for x in row:
                    if x == 0:
                        weight *= 2
                value = sum(x*y for x, y in zip(row, w))
                second += weight*value**2
                fourth += weight*value**4
            norm = sum(x*x for x in w)
            self.assertEqual(second, F(norm, 2))
            self.assertEqual(fourth, F(3*norm**2-sum(x**4 for x in w), 4))

    def test_case2_modular_circle_and_boundary(self):
        # All offsets/coefficient values for these moduli, including even endpoints.
        for q in (13, 73, 97, 144, 181, 251):
            for w in range((q+71)//72, q//2+1):
                for offset in range(q):
                    small_mass = sum(weight for x, weight in ((-1,1),(0,2),(1,1))
                                     if abs(centered(offset+x*w, q))*144 < q)
                    self.assertLessEqual(small_mass, 2)
        # The incorrect <= small ball would violate the claimed 1/2 bound.
        bad = sum(weight for x, weight in ((-1,1),(0,2),(1,1))
                  if abs(centered(-1+2*x, 144))*144 <= 144)
        self.assertEqual(bad, 3)

    def test_all_small_naf_encodings(self):
        for d in (2, 4, 8, 16):
            for value in range(2**d+1):
                p = encode(value, d)
                self.assertEqual(evaluate(p) % (2**d+1), value)
                self.assertLessEqual(sum(x*x for x in p), d//2)
                self.assertTrue(all(x in (-1, 0, 1) for x in p))
                self.assertTrue(all(p[i]*p[i+1] == 0 for i in range(d-1)))

    def test_all_small_challenge_differences_are_units(self):
        validate_ring(101, degree=4)
        for delta in itertools.product(range(-4, 5), repeat=4):
            if any(delta):
                self.assertEqual(gcd_mod(delta, (1,0,0,0,1), 101), (1,))
        with self.assertRaises(ValueError):
            validate_ring(13, degree=4)
        self.assertEqual(challenge_cube(64)["cardinality"], 5**64)

    def test_lifting_rejects_known_ambiguity(self):
        self.assertFalse(lifting_condition(F(801, 100), 5, 4, 13))
        self.assertTrue(lifting_condition(F(801, 100), 5, 4, 29))
        f = (2, -1, -7, -5)
        self.assertEqual(evaluate(f) % 17, 0)
        self.assertEqual(evaluate(tuple(centered(x, 13) for x in f)) % 17, 1)
        self.assertEqual(tuple(centered(x, 29) for x in f), f)

    def test_integer_ring_multiplication_preserves_target_arithmetic(self):
        for a in range(17):
            for b in range(17):
                self.assertEqual(evaluate(negacyclic_multiply(encode(a,4), encode(b,4))) % 17,
                                 a*b % 17)

    def test_conditional_budget_not_overstated(self):
        bound = statistical_budget(4294967197)
        self.assertLess(bound, F(1, 2**147))
        self.assertGreater(bound, F(1, 2**148))

    def test_affine_reduction_pins_public_input_and_lifts_honest_residual(self):
        A, B, C, H = ((0,15),), ((0,11),), ((0,14),), ((-4,1),)
        w = (1,4)
        self.assertTrue(source_relation(A,B,C,H,w,17))
        self.assertFalse(source_relation(A,B,C,H,(0,0),17))
        self.assertFalse(source_relation(A,B,C,H,(1,3),17))
        coefficients = linear_coefficients(A,B,C,H,((3,),),(12,),(8,),(2,),((7,),),(5,),0,17)
        witness = tuple(encode(x,4) for x in (9,10,5,1,4,10))
        residual = encoded_residual(coefficients,witness,4,1,2,1,0)
        self.assertLessEqual(sum(x*x for p in witness for x in p), 12)
        self.assertTrue(lifting_condition(12,6,4,101))
        self.assertEqual(evaluate(residual) % 17, 0)
        self.assertEqual(tuple(centered(x,101) for x in residual), residual)

    def test_every_delta_column_tests_its_own_residual(self):
        # Distinct phi_j and delta_j catch the original repeated-i indexing error.
        coefficients = linear_coefficients(((0,1),),((0,1),),((0,1),),(),
                                           ((2,),(5,)),(0,),(0,),(0,),
                                           [(3,),(7,)],(),0,17)
        self.assertEqual(coefficients[0], (3*2+7*5) % 17)
        self.assertEqual(coefficients[-2:], ((-3)%17,(-7)%17))


if __name__ == '__main__':
    unittest.main()
