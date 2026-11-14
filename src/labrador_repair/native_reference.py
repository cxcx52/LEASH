"""Portable honest-flow reference for the bare native binary source reduction.

The final message contains the full witness. This is not the recursive core,
a succinct proof, a security implementation, or a Fiat--Shamir experiment.
Random instances/matrices/challenges use deterministic benchmark-only randomness.
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import random
import time

from .ring import centered, negacyclic_multiply

Q = 4294967197


@dataclass(frozen=True)
class BinaryInstance:
    n: int
    a_rows: tuple
    b_rows: tuple
    c_rows: tuple
    public_pins: tuple
    h_rows: tuple = ()


@dataclass(frozen=True)
class Parameters:
    q: int = Q
    degree: int = 64
    source_rank: int = 2
    chunks_per_block: int = 2
    aggregation_rows: int = 160
    norm_slack_squared: Fraction = Fraction(16, 3)


@dataclass(frozen=True)
class Challenges:
    alpha: tuple
    beta: tuple
    gamma: tuple
    eta: tuple = ()


@dataclass(frozen=True)
class Transcript:
    commitment: tuple
    challenges: tuple
    scalar_replies: tuple
    witness_blocks: tuple


@dataclass(frozen=True)
class NativeCase:
    instance: BinaryInstance
    parameters: Parameters
    matrix: tuple
    transcript: Transcript
    phase_seconds: dict


def _integer(value, lower, name):
    if type(value) is not int or value < lower:
        raise ValueError(name + " is not a valid integer")


def _validate(instance, params):
    _integer(instance.n, 1, "n")
    _integer(params.degree, 2, "degree")
    if params.degree & (params.degree-1) or params.q != Q:
        raise ValueError("this reference requires a power-of-two degree and its fixed prime q")
    _integer(params.source_rank, 1, "source_rank")
    _integer(params.chunks_per_block, 1, "chunks_per_block")
    _integer(params.aggregation_rows, 1, "aggregation_rows")
    if not isinstance(params.norm_slack_squared, Fraction) or params.norm_slack_squared < 1:
        raise ValueError("norm_slack_squared must be a Fraction at least one")
    k = len(instance.a_rows)
    if not k or len(instance.b_rows) != k or len(instance.c_rows) != k:
        raise ValueError("three matrices must have the same positive row count")
    if instance.n % params.degree or k % params.degree:
        raise ValueError("n and k must be divisible by degree")
    for rows in (instance.a_rows, instance.b_rows, instance.c_rows, instance.h_rows):
        for row in rows:
            if len(set(row)) != len(row) or any(type(j) is not int or not 0 <= j < instance.n for j in row):
                raise ValueError("sparse binary rows must contain distinct valid column indices")
    for j, value in instance.public_pins:
        if type(j) is not int or not 0 <= j < instance.n or type(value) is not int or value not in (0, 1):
            raise ValueError("public pins must specify valid bit coordinates")
    total = instance.n+3*k
    cap = params.norm_slack_squared*2*total
    if not cap < params.q or not 6*k < params.q or not total < params.q:
        raise ValueError("the native integer-lifting inequalities do not hold")
    return k, total, cap


def conjugate(poly, q):
    return (poly[0] % q,)+tuple(-x % q for x in reversed(poly[1:]))


def _pack(bits, degree):
    return tuple(tuple(bits[i:i+degree]) for i in range(0, len(bits), degree))


def _mat_bits(rows, witness):
    return tuple(sum(witness[j] for j in row) % 2 for row in rows)


def _delta(instance, challenges):
    out = [0]*instance.n
    for rows, weights in ((instance.a_rows, challenges.alpha), (instance.b_rows, challenges.beta),
                          (instance.c_rows, challenges.gamma), (instance.h_rows, challenges.eta)):
        for indices, weight in zip(rows, weights):
            if weight:
                for j in indices:
                    out[j] ^= 1
    return tuple(out)


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _commit(matrix, opening, q, degree):
    result = []
    for row in matrix:
        accum = [0]*degree
        for left, right in zip(row, opening):
            product = negacyclic_multiply(left, right)
            accum = [(x+y) % q for x, y in zip(accum, product)]
        result.append(tuple(accum))
    return tuple(result)


def _layout(instance, params):
    k = len(instance.a_rows)
    sizes = (k//params.degree,)*3+(instance.n//params.degree,)
    width = (max(sizes)+params.chunks_per_block-1)//params.chunks_per_block
    return sizes, width, width*params.chunks_per_block


def generate_honest_case(log_size=6, seed=1, rows=160):
    """Construct the complete honest bare flow, in its prescribed chronology.

    Toy n=k=2^log_size; the constant wire is included. C is chosen to match the
    generated honest assignment. This generator is not a representative workload
    model, independent-CRS sampler, or cryptographic randomness implementation.
    """
    _integer(log_size, 6, "log_size")
    _integer(seed, 0, "seed")
    _integer(rows, 1, "rows")
    if log_size > 10 or rows > 160:
        raise ValueError("reference experiment limits are log_size<=10 and rows<=160")
    times = {}
    start = time.perf_counter()
    n = 1 << log_size
    rng = random.Random(seed)
    witness = (1,)+tuple(rng.randrange(2) for _ in range(n-1))
    a_rows = tuple(tuple(sorted(rng.sample(range(n), 3))) for _ in range(n))
    b_rows = tuple(tuple(sorted(rng.sample(range(n), 3))) for _ in range(n))
    a, b = _mat_bits(a_rows, witness), _mat_bits(b_rows, witness)
    c = tuple(x*y for x, y in zip(a, b))
    c_rows = tuple((0,) if bit else () for bit in c)
    instance = BinaryInstance(n, a_rows, b_rows, c_rows,
                              tuple((i, witness[i]) for i in range(1, min(4, n))))
    params = Parameters(aggregation_rows=rows)
    _, total, _ = _validate(instance, params)
    originals = tuple(_pack(vector, params.degree) for vector in (a, b, c, witness))
    times['instance_generation'] = time.perf_counter()-start

    start = time.perf_counter()
    # Named deterministic streams separate benchmark components, without making
    # a cryptographic independence claim about Python's PRNG.
    matrix_rng = random.Random(seed ^ 0x4B535243)
    matrix = tuple(tuple(tuple(matrix_rng.randrange(params.q) for _ in range(params.degree))
                         for _ in range(total//params.degree)) for _ in range(params.source_rank))
    times['source_matrix_generation'] = time.perf_counter()-start
    start = time.perf_counter()
    opening = tuple(poly for block in originals for poly in block)
    commitment = _commit(matrix, opening, params.q, params.degree)
    times['source_commitment'] = time.perf_counter()-start

    # Challenges are generated only after the source commitment has been fixed.
    start = time.perf_counter()
    challenge_rng = random.Random(seed ^ 0x4348414C)
    challenges = tuple(Challenges(*(tuple(challenge_rng.randrange(2) for _ in range(n))
                                   for _ in range(3))) for _ in range(rows))
    times['source_challenge_generation'] = time.perf_counter()-start
    start = time.perf_counter()
    replies = tuple(_dot(ch.alpha, a)+_dot(ch.beta, b)+_dot(ch.gamma, c)
                    -_dot(_delta(instance, ch), witness) for ch in challenges)
    times['source_scalar_replies'] = time.perf_counter()-start
    start = time.perf_counter()
    _, _, block_rings = _layout(instance, params)
    zero = (0,)*params.degree
    padded = tuple(block+(zero,)*(block_rings-len(block)) for block in originals)
    conjugates = tuple(tuple(conjugate(poly, params.q) for poly in block) for block in padded)
    transcript = Transcript(commitment, challenges, replies, padded+conjugates)
    times['target_witness_construction'] = time.perf_counter()-start
    return NativeCase(instance, params, matrix, transcript, times)


def verify_native_case(case):
    """Check all bare target equations and decode/verify the source relation.

    Returns a named check map. This local checker may be used on self-generated
    mathematical fixtures; it is not a verifier for upstream or deployed proofs.
    """
    instance, p, tr = case.instance, case.parameters, case.transcript
    k, total, cap = _validate(instance, p)
    sizes, _, block_rings = _layout(instance, p)
    poly_ok = lambda poly: len(poly) == p.degree and all(type(x) is int and 0 <= x < p.q for x in poly)
    structure = (len(tr.witness_blocks) == 8 and
                 all(len(block) == block_rings and all(poly_ok(poly) for poly in block)
                     for block in tr.witness_blocks) and
                 len(case.matrix) == p.source_rank and
                 all(len(row) == total//p.degree and all(poly_ok(poly) for poly in row) for row in case.matrix) and
                 len(tr.commitment) == p.source_rank and all(poly_ok(poly) for poly in tr.commitment) and
                 len(tr.challenges) == len(tr.scalar_replies) == p.aggregation_rows)
    checks = {'structural_shape_and_residues':structure}
    if not structure:
        return checks
    original, conj = tr.witness_blocks[:4], tr.witness_blocks[4:]
    zeros = all(not any(poly) for i, block in enumerate(tr.witness_blocks)
                for poly in block[sizes[i % 4]:])
    checks['aligned_padding_zero'] = zeros
    checks['conjugation_coordinate_equations'] = all(conjugate(x, p.q) == y
        for block, other in zip(original, conj) for x, y in zip(block, other))
    norm_sq = sum(centered(x,p.q)**2 for block in tr.witness_blocks for poly in block for x in poly)
    checks['actual_extracted_norm_cap'] = norm_sq <= cap
    real_opening = tuple(poly for i, block in enumerate(original) for poly in block[:sizes[i]])
    checks['source_commitment_equations'] = _commit(case.matrix,real_opening,p.q,p.degree) == tr.commitment
    jbar = conjugate((1,)*p.degree,p.q)
    bitness = []
    for block, other in zip(original, conj):
        residual = sum(negacyclic_multiply(x,tuple(u-v for u,v in zip(y,jbar)))[0]
                       for x,y in zip(block,other))
        bitness.append(residual % p.q == 0)
    checks['four_Jbar_bitness_equations'] = all(bitness)
    gate = 0
    for a,b,c,aa,bb,cc in zip(original[0],original[1],original[2],conj[0],conj[1],conj[2]):
        left = tuple(x+y-2*z for x,y,z in zip(a,b,c))
        right = tuple(x+y-2*z-j for x,y,z,j in zip(aa,bb,cc,jbar))
        gate += negacyclic_multiply(left,right)[0]
    checks['binary_product_equation'] = gate % p.q == 0
    vectors = tuple(tuple(centered(x,p.q) for poly in block[:sizes[i]] for x in poly)
                    for i,block in enumerate(original))
    a,b,c,w = vectors
    checks['decoded_coefficients_are_bits'] = all(x in (0,1) for vector in vectors for x in vector)
    checks['constant_and_public_coefficient_pins'] = w[0] == 1 and all(w[j] == v for j,v in instance.public_pins)
    challenge_ok = all(len(ch.alpha)==k and len(ch.beta)==k and len(ch.gamma)==k and
        len(ch.eta)==len(instance.h_rows) and all(type(x) is int and x in (0,1)
        for row in (ch.alpha,ch.beta,ch.gamma,ch.eta) for x in row) for ch in tr.challenges)
    checks['binary_challenge_dimensions'] = challenge_ok
    checks['integer_reply_range_and_parity'] = all(type(g) is int and -instance.n <= g <= 3*k
                                                   and g % 2 == 0 for g in tr.scalar_replies)
    if challenge_ok and all(type(g) is int for g in tr.scalar_replies):
        actual = tuple(_dot(ch.alpha,a)+_dot(ch.beta,b)+_dot(ch.gamma,c)
                       -_dot(_delta(instance,ch),w) for ch in tr.challenges)
        checks['scalar_target_equations_mod_q'] = all((x-g) % p.q == 0 for x,g in zip(actual,tr.scalar_replies))
        checks['specified_integer_lift'] = actual == tr.scalar_replies
    else:
        checks['scalar_target_equations_mod_q'] = checks['specified_integer_lift'] = False
    checks['decoded_source_R1CS'] = (checks['decoded_coefficients_are_bits'] and w[0] == 1
        and all(w[j]==v for j,v in instance.public_pins)
        and not any(_mat_bits(instance.h_rows,w))
        and tuple(x*y for x,y in zip(_mat_bits(instance.a_rows,w),_mat_bits(instance.b_rows,w))) == _mat_bits(instance.c_rows,w))
    return checks


def encode_reference_transport(case):
    """Encode the full bare-source prover message for a fixed public context.

    This explicitly sends the whole target witness. Fixed-width reference fields:
    canonical q residues as unsigned little-endian 32-bit words, and source g
    replies as signed 32-bit words. Dimensions/order are supplied by the public
    statement. Verifier challenges and the CRS are not included in this prover
    message. This is not the compact core wire format.
    """
    _validate(case.instance,case.parameters)
    tr = case.transcript
    witness = b''.join(x.to_bytes(4,'little') for block in tr.witness_blocks for poly in block for x in poly)
    commitment = b''.join(x.to_bytes(4,'little') for poly in tr.commitment for x in poly)
    replies = b''.join(g.to_bytes(4,'little',signed=True) for g in tr.scalar_replies)
    return commitment+replies+witness


def decode_reference_transport(instance, parameters, matrix, challenges, payload):
    """Decode against fixed public dimensions/CRS and saved verifier challenges.

    Reject length differences, noncanonical q residues, and a challenge-count
    mismatch. Integer g range/parity and all target equations are subsequently
    checked by verify_native_case; decoding is not proof verification.
    """
    _validate(instance,parameters)
    _,_,block_rings = _layout(instance,parameters)
    p = parameters
    expected_length = 4*(p.source_rank*p.degree+p.aggregation_rows+8*block_rings*p.degree)
    if type(payload) is not bytes or len(payload) != expected_length:
        raise ValueError('reference transport has the wrong exact length')
    if len(challenges) != p.aggregation_rows:
        raise ValueError('public verifier challenge count does not match the manifest')
    offset = 0
    def word(signed=False):
        nonlocal offset
        value = int.from_bytes(payload[offset:offset+4],'little',signed=signed)
        offset += 4
        if not signed and value >= p.q:
            raise ValueError('noncanonical q residue in reference transport')
        return value
    commitment = tuple(tuple(word() for _ in range(p.degree)) for _ in range(p.source_rank))
    replies = tuple(word(True) for _ in range(p.aggregation_rows))
    blocks = tuple(tuple(tuple(word() for _ in range(p.degree)) for _ in range(block_rings)) for _ in range(8))
    assert offset == len(payload)
    return NativeCase(instance,parameters,matrix,Transcript(commitment,tuple(challenges),replies,blocks),{})


def _transport_metrics(case,payload):
    tr,p = case.transcript,case.parameters
    commitment_length = 4*p.source_rank*p.degree
    reply_length = 4*p.aggregation_rows
    witness = payload[commitment_length+reply_length:]
    diagnostic = json.dumps({'commitment':tr.commitment,'challenges':[
        {'alpha':c.alpha,'beta':c.beta,'gamma':c.gamma,'eta':c.eta} for c in tr.challenges],
        'scalar_replies':tr.scalar_replies,'witness_blocks':tr.witness_blocks},
        separators=(',',':')).encode('utf-8')
    return {'full_witness_transport_bytes':len(witness),
            'source_commitment_transport_bytes':commitment_length,
            'source_scalar_transport_bytes':reply_length,
            'bare_source_prover_transport_bytes':len(payload),
            'diagnostic_JSON_bytes':len(diagnostic),
            'full_witness_transport_sha256':hashlib.sha256(witness).hexdigest(),
            'compact_proof_bytes':None,
            'compact_proof_bytes_reason':'No recursive core or compact serializer is implemented here'}


def transport_metrics(case):
    """Count bytes actually constructed by the full-witness reference encoder."""
    return _transport_metrics(case,encode_reference_transport(case))


def benchmark_report(log_size=6, seed=1, rows=160):
    start = time.perf_counter()
    case = generate_honest_case(log_size,seed,rows)
    check_start = time.perf_counter()
    checks = verify_native_case(case)
    verify_seconds = time.perf_counter()-check_start
    encode_start = time.perf_counter()
    wire = encode_reference_transport(case)
    metrics = _transport_metrics(case,wire)
    encode_seconds = time.perf_counter()-encode_start
    decode_start = time.perf_counter()
    decoded = decode_reference_transport(case.instance,case.parameters,case.matrix,case.transcript.challenges,wire)
    decoded_checks = verify_native_case(decoded)
    roundtrip = decoded.transcript == case.transcript and all(decoded_checks.values())
    roundtrip_seconds = time.perf_counter()-decode_start
    k,total,cap = _validate(case.instance,case.parameters)
    sizes,width,block_rings = _layout(case.instance,case.parameters)
    oracle_names = ('decoded_coefficients_are_bits','specified_integer_lift','decoded_source_R1CS')
    target_checks = {name:value for name,value in checks.items() if name not in oracle_names}
    source_oracle = {name:checks.get(name,False) for name in oracle_names}
    report = {
        'status':'passed' if all(checks.values()) and roundtrip else 'failed',
        'scope':'Bare native source reduction with a fully transmitted witness; no succinct core or FS',
        'verification_scope':'Bare target checks plus a decoded-source correctness oracle; not a measured soundness experiment',
        'randomness':'Python random.Random deterministic benchmark-only streams; not cryptographic randomness',
        'seed':seed,'q':case.parameters.q,'d':case.parameters.degree,
        'source_n_including_constant':case.instance.n,'source_k':k,'source_rows':rows,
        'source_rank':case.parameters.source_rank,'source_ring_columns':total//case.parameters.degree,
        'target_r':8*case.parameters.chunks_per_block,'target_n':width,
        'target_witness_ring_length':8*block_rings,
        'target_padding_rings':8*block_rings-2*sum(sizes),
        'beta_honest_squared':2*total,'beta_actual_squared':str(cap),
        'checks':checks,'target_checks':target_checks,
        'target_check_status':'passed' if all(target_checks.values()) else 'failed',
        'source_oracle_checks':source_oracle,
        'source_oracle_check_status':'passed' if all(source_oracle.values()) else 'failed',
        'reference_wire_roundtrip':roundtrip,
        'phase_seconds':dict(case.phase_seconds,verification_with_source_oracle=verify_seconds,
                            reference_encoding=encode_seconds,reference_roundtrip_validation=roundtrip_seconds),
        'local_total_wall_seconds':time.perf_counter()-start,
        'transport':metrics,
        'cryptographic_security_label':None,
    }
    return report
