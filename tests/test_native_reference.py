from dataclasses import replace
from fractions import Fraction
import unittest

from labrador_repair.native_reference import (
    benchmark_report, decode_reference_transport, encode_reference_transport,
    generate_honest_case, transport_metrics, verify_native_case,
)


class NativeReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = generate_honest_case(6,7,16)

    def test_complete_honest_flow_with_real_padding(self):
        checks = verify_native_case(self.case)
        self.assertTrue(all(checks.values()),checks)
        self.assertEqual(len(self.case.transcript.witness_blocks),8)
        self.assertTrue(any(self.case.transcript.witness_blocks[3][0][1:]))
        self.assertTrue(all(x == 0 for block in self.case.transcript.witness_blocks for x in block[1]))
        self.assertEqual(self.case.parameters.norm_slack_squared,Fraction(16,3))

    def test_reference_transport_is_full_witness_and_counted_from_bytes(self):
        metrics = transport_metrics(self.case)
        self.assertEqual(metrics['full_witness_transport_bytes'],8*2*64*4)
        self.assertEqual(metrics['source_commitment_transport_bytes'],2*64*4)
        self.assertEqual(metrics['source_scalar_transport_bytes'],16*4)
        self.assertEqual(metrics['bare_source_prover_transport_bytes'],4096+512+64)
        self.assertGreater(metrics['diagnostic_JSON_bytes'],0)
        self.assertIsNone(metrics['compact_proof_bytes'])

    def test_local_reply_validation_range_parity_and_equation(self):
        tr = self.case.transcript
        for delta in (1,2,self.case.parameters.q):
            changed = replace(tr,scalar_replies=(tr.scalar_replies[0]+delta,)+tr.scalar_replies[1:])
            checks = verify_native_case(replace(self.case,transcript=changed))
            self.assertFalse(all(checks.values()))
        changed = replace(tr,scalar_replies=tr.scalar_replies[:-1])
        self.assertFalse(verify_native_case(replace(self.case,transcript=changed))['structural_shape_and_residues'])
        changed = replace(tr,challenges=tr.challenges[:-1],scalar_replies=tr.scalar_replies[:-1])
        self.assertFalse(verify_native_case(replace(self.case,transcript=changed))['structural_shape_and_residues'])

    def test_reference_wire_roundtrip_and_strict_decoder(self):
        case = self.case
        wire = encode_reference_transport(case)
        def decode(payload,challenges=case.transcript.challenges):
            return decode_reference_transport(case.instance,case.parameters,case.matrix,challenges,payload)
        decoded = decode(wire)
        self.assertEqual(decoded.transcript,case.transcript)
        self.assertTrue(all(verify_native_case(decoded).values()))
        for bad in (wire[:-1],wire+b'\x00',case.parameters.q.to_bytes(4,'little')+wire[4:]):
            with self.assertRaises(ValueError):
                decode(bad)
        with self.assertRaises(ValueError):
            decode(wire,case.transcript.challenges[:-1])
        offset = case.parameters.source_rank*case.parameters.degree*4
        scalar = int.from_bytes(wire[offset:offset+4],'little',signed=True)
        bad = wire[:offset]+(scalar+1).to_bytes(4,'little',signed=True)+wire[offset+4:]
        self.assertFalse(verify_native_case(decode(bad))['integer_reply_range_and_parity'])

    def test_local_coefficient_pin_conjugation_and_padding_validation(self):
        tr = self.case.transcript
        for block_index,ring_index,coefficient in ((3,0,0),(4,0,1),(0,1,0)):
            blocks = [[list(poly) for poly in block] for block in tr.witness_blocks]
            blocks[block_index][ring_index][coefficient] ^= 1
            blocks = tuple(tuple(tuple(poly) for poly in block) for block in blocks)
            checks = verify_native_case(replace(self.case,transcript=replace(tr,witness_blocks=blocks)))
            self.assertFalse(all(checks.values()))
        checks = verify_native_case(replace(self.case,parameters=replace(self.case.parameters,norm_slack_squared=Fraction(1))))
        self.assertTrue(checks['actual_extracted_norm_cap'])

    def test_reproducibility_and_larger_sparse_case(self):
        repeated = generate_honest_case(6,7,16)
        self.assertEqual(repeated.transcript,self.case.transcript)
        self.assertEqual(repeated.matrix,self.case.matrix)
        report = benchmark_report(8,19,16)
        self.assertEqual(report['status'],'passed')
        self.assertEqual(report['source_n_including_constant'],256)
        self.assertEqual(report['target_padding_rings'],0)
        self.assertEqual(report['target_check_status'],'passed')
        self.assertEqual(report['source_oracle_check_status'],'passed')
        self.assertTrue(report['reference_wire_roundtrip'])
        self.assertIsNone(report['cryptographic_security_label'])

    def test_invalid_parameters_are_rejected(self):
        for log_size,seed,rows in ((5,1,16),(11,1,16),(6,-1,16),(6,1,0),(6,1,161),(True,1,16)):
            with self.assertRaises(ValueError):
                generate_honest_case(log_size,seed,rows)
        with self.assertRaises(ValueError):
            verify_native_case(replace(self.case,parameters=replace(self.case.parameters,q=13)))


if __name__ == '__main__':
    unittest.main()
