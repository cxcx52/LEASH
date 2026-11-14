# Bounded complete-protocol restarts with accept-gated extraction

Date: 2026-11-14. Status: a conditional classical interactive composition theorem for the repaired ordinary protocol family. The proof uses the reviewed extraction/composition theorems and an explicit ordinary-gate interface. It does not establish Fiat--Shamir, ROM/QROM grinding bounds, simulation extractability, or concrete MSIS security.

The real-gate interface, recursive initial-call-chain argument, adaptive Gen_i experiments, disjoint first-acceptance coupling and expected-cost initializer extension were independently checked by the extraction reviewer against `composition_repair.md`; no blocker was found. The parameter profiles are separately reviewed in `parameter_feasibility_peer_review.md`.

## 1. The restart policy and the required interface

Fix one public statement x and one CRS sampled according to the original setup. Fix an integer Q>=1 before interaction. In each attempt run the **entire** specified ordinary protocol with fresh verifier challenges. Start the next attempt only after rejection of the preceding attempt. Stop immediately on the first acceptance, or reject after Q rejected attempts. The prover may retain state and adapt its messages to all earlier rejected attempts. It may not change the public statement to be proved.

This is a protocol policy, not permission to resample individual unfavorable challenges inside an attempt. In particular, a prover cannot submit only a selected transcript while hiding an unbounded number of trials.

The ordinary protocol may be a single repaired layer or the reviewed composition of ordinary layers, optionally with a repaired source reduction. Let its output witness relation be R_out(x), including the actual relaxed norm and all public-input constraints.

We require a **gate-preserving extractor** E with the following interface:

1. It begins with one faithful ordinary execution of the complete protocol against the original prover state. Denote the actual verifier decision on this execution by G.
2. If G rejects, E returns failure without any extraction fork. It exposes the original post-rejection prover state and transcript.
3. If G accepts, E may perform its specified additional reset/fork computation and return a verified witness or failure. Its final witness output is therefore supported on G=accept. No later successful fork replaces the original ordinary gate transcript.
4. For every admissible initial-state experiment, E succeeds with probability at least epsilon-kappa-nu, where epsilon is its ordinary protocol acceptance probability. The computational quantity nu is the unconditional loss for that complete experiment, including its initial-state generation and every nested extraction call.
5. For every permitted concrete initial state, the expected cost of E is at most C, with parameters and local costs included. This cost bound is uniform; the success or binding bound is not required pointwise in the CRS or state.

The interface does not claim that every accepted ordinary gate yields a witness. Extraction aborts, invalid candidates and collision outputs can all make E fail after G accepted.

## 2. Why the existing ordinary extractors have this interface

For the single-layer E_gate in `composition_repair.md`, properties 1--3 are explicit. Its first ordinary acceptance gate is saved permanently; a rejected gate causes immediate failure. Its runtime bound is C=c*tau with c=1+r/(1-1/N), when tau is a valid bound including local work.

The recursively composed extractor also exposes one **real complete ordinary gate**, although its virtual bare prover's acceptance event is a different, narrower event. This distinction is important.

Unroll the recursive extractor's initial invocation. Before the first coordinate fork at level i, that level follows the original prover prefix and calls the next extractor once for its initial final reply. Recursively, this descends through the original ordinary prefixes until the explicit-witness base case is reached. The base case has made no fork. At that moment one complete original protocol execution has either accepted or rejected.

If it rejected at an earlier prefix or at the base case, the guarded dummy continuation returns failure. Every enclosing first gate then rejects; no coordinate fork starts during the unwind. The original rejection transcript and its saved original prover state are available for the next real attempt.

If an extraction fork is ever started, the initial complete ordinary execution has already accepted. All subsequent inner extraction coins are fresh as required by the composition theorem. If an inner extractor later fails, it can prevent an outer virtual gate from accepting, but cannot change the already recorded real ordinary gate decision.

Consequently the recursive algorithm can be implemented in two phases without changing its law: execute the initial real ordinary path and retain the pending extraction stack; after a real acceptance, resume that stack with fresh extraction coins. Its verified output implies acceptance of that original path. This proves properties 1--3 by induction on the number of layers. The reviewed composition theorem supplies property 4, with kappa equal to the sum of its layer/source statistical errors, and property 5 under its polynomial runtime-product condition.

A source wrapper is covered only if it has the same guarded form: its initial source interaction follows the ordinary prover, its core invocation has the interface just proved, and it returns a decoded source witness only after verifying it. A source-wrapper assertion without this interface must be justified separately.

## 3. The adaptive-history experiments

For i=1,...,Q define an initializer Gen_i as follows. It receives the original CRS, generates the same original statement/prover experiment, and simulates the first i-1 **ordinary** attempts with fresh verifier coins. If an earlier attempt accepts, it installs an always-rejecting dummy continuation. Otherwise it supplies the original prover's state after those rejected attempts as the state for attempt i. These experiments include the dummy outcomes; no probability is conditioned on reaching attempt i.

Let A_i be the event that the actual restart protocol first accepts on attempt i. Then the ordinary acceptance probability in experiment Gen_i is

    epsilon_i = Pr[A_i].

The A_i are disjoint, so

    sum_i epsilon_i = epsilon_restart.

All rejected histories may depend on the CRS and on the prover's fixed original tape. They are allowed because Gen_i generates them efficiently in the stated model. This is not permission to supply unexplained CRS-correlated trapdoors or advice. Applying the single-attempt theorem to Gen_i gives

    Pr[E(Gen_i) returns a verified witness]
       >= epsilon_i-kappa_i-nu_i.                         (1)

The nu_i here are for the full Gen_i experiments. They are not conditional failure probabilities given A_i, and no per-CRS binding assertion is used.

If ordinary challenge generation has a uniform expected-polynomial bound, rather than a strict bound, Gen_i has a uniform expected-polynomial bound as well. The same extension to the initial-state model is justified explicitly: prepend Gen_i to each collision experiment and charge its expected cost. A nonnegligibly successful expected-polynomial MSIS solver can be truncated at a polynomial cost selected from its hypothesized nonnegligible success, exactly as in Section 6 of `composition_repair.md`. This establishes the asymptotic negligible-loss conclusion under ordinary PPT hardness. It does not make an arbitrary fixed concrete cutoff free; finite-time bounds must charge the actual prefix cost and chosen truncation losses. Alternatively a strict-time sampler with a specified abort policy may be analyzed as part of the protocol.

## 4. The bounded-restart extractor and its success bound

Define E_restart using one evolving original prover state:

1. Invoke the gate-preserving extractor for the next attempt.
2. If its original ordinary gate rejected, retain that original post-rejection state and continue, up to Q attempts.
3. If its original ordinary gate accepted, finish extraction and **stop regardless of extraction success or failure**. Return only a verified witness; otherwise return failure.

The extractor must not start another attempt after a real gate acceptance merely because extraction failed. That would not implement the specified first-acceptance protocol.

To compare this algorithm with (1), couple all experiments through the same setup, original prover tape, and ordinary verifier coins along the shared rejection path. On the event A_i, use the same fresh additional extraction coins for E_restart and E in experiment Gen_i. Before attempt i every earlier real gate rejected, so no earlier extraction fork altered the original history. Thus the output distribution on this branch is identical in the two experiments. Outside A_i the gate interface prevents E(Gen_i) from returning any witness.

The witness-output events for different i are therefore disjoint in this coupling. Summing (1) yields

    Pr[E_restart returns a verified R_out(x) witness]
       >= epsilon_restart - sum_i kappa_i - sum_i nu_i.  (RESTART)

With one common statistical bound kappa this becomes

    epsilon_restart - Q*kappa - sum_i nu_i.

Negative right-hand sides are interpreted as the trivial lower bound zero. This proof does not independently run Q extractors and incorrectly add overlapping success probabilities; disjointness is supplied by the saved ordinary first-acceptance gates.

For a polynomially bounded Q and a uniformly quantified family of MSIS assumptions/reductions, sum_i nu_i remains negligible. For a concrete theorem retain that sum explicitly and account for every reduction's prefix-generation and nested-extraction runtime. A uniform-index reduction may be used to justify the asymptotic statement for a growing family; individually named negligible functions without uniformity are insufficient.

## 5. Expected running time

Immediately before each reached attempt, its original state and previous rejection history are fixed. The uniform per-state expectation gives a cost at most C_i for this invocation, regardless of how reaching this state biased the CRS or prover state. Therefore

    E[time(E_restart)]
       <= sum_i Pr[reach_i]*C_i
       <= sum_i C_i <= Q*max_i C_i.                      (TIME)

No computational success guarantee has been conditioned on that history; only the already uniform runtime bound is used conditionally. For a single ordinary layer the ordinary/suffix invocation count is at most Q*(1+r/(1-1/N)), plus the explicitly charged local overhead. For a multi-layer attempt C_i already includes the nested product and local work from the composition theorem; it cannot be replaced by one layer's call factor.

This is the runtime of E_restart, which shares its ordinary rejection path. Each separate MSIS reduction used to bound nu_i may regenerate up to i-1 ordinary attempts in Gen_i, so that additional cost must be included in its advantage estimate. It is polynomial for polynomial Q. The theorem does not assert useful worst-case or exponential-tail extraction time.

## 6. Honest completeness and exact failure bound

Assume every reached honest attempt accepts with conditional probability at least a, uniformly over its fixed public instance, CRS and prior rejection history. Independent fresh complete honest attempts with a uniform single-attempt lower bound suffice; full independence is stronger than necessary.

Let R_i denote rejection of all first i attempts. The conditional bound gives

    Pr[R_i] <= (1-a)Pr[R_(i-1)],

and hence

    Pr[honest final rejection] <= (1-a)^Q,
    Pr[honest acceptance] >= 1-(1-a)^Q.                  (COMP)

The expression (1-a)^Q is exact as a worst-case bound: equality occurs for independent Bernoulli attempts of success probability a. If the underlying per-attempt theorem has a strict lower bound, the corresponding nontrivial failure inequality is strict.

The expected number of honest attempts is bounded by the finite geometric sum

    sum_(j=0)^(Q-1) (1-a)^j
      = (1-(1-a)^Q)/a <= min(Q,1/a)                   (a>0).

Rejected attempts contribute communication and verifier/prover work. The protocol's worst-case communication is at most Q times the complete-attempt upper bound; expected honest communication can be bounded using the displayed expected-attempt count and a uniform per-attempt cost. This does not justify compressing away the rejected interactive histories in a Fiat--Shamir proof.

## 7. Exact arithmetic for the current profiles

The theorem is general in a and Q. The reproduction script `scripts/bounded_restart_checks.py` uses Fraction throughout and writes no proof transcripts. Its finite probability-tree checks validate the first-acceptance/output-mass identities in 729 small cases; the theorem itself is proved above.

For the earlier H=552, fold-failure 1/4 profile,

    a_old=(67/132)^7=6060711605323/698260569735168.

At Q=1024 the failure bound is the exact rational (1-a_old)^1024, approximately 0.0001327771084. This gives roughly 99.9867% honest acceptance, **not** a 128-bit completeness-failure bound.

The reviewed H=640, fold-failure 1/16 profile has per-layer lower bound 479/528, so, under its stated complete parameter certificate,

    a_new=(479/528)^7
      =5785602523725084959/11440301174540992512 > 1/2.

Then Q=16,32,128 give failure strictly below 2^-16, 2^-32, 2^-128, respectively, and expected honest attempts below 1/a_new<2. The exact (1-a_new)^Q bound is stronger; the script retains it for all calculations.

If the complete single-attempt **statistical** budget is less than 2^-140, the restart statistical budget is less than Q*2^-140. Thus:

| Attempt cap Q | Simple new-profile failure bound | Statistical knowledge-error bound |
|---|---:|---:|
| 16 | <2^-16 | <2^-136 |
| 32 | <2^-32 | <2^-135 |
| 128 | <2^-128 | <2^-133 |
| 1024 | <2^-1024 | <2^-130 |

These statistical figures omit sum_i nu_i. In particular, they are not certified concrete 128-bit knowledge-security claims. The current fourth-root computational losses and rank/hardness analysis remain substantive obligations.

## 8. Precise limits

This theorem covers bounded, verifier-visible, complete ordinary restarts under the same public statement and properly generated CRS. It relies on the real ordinary-gate interface and uniform expected runtime proved above. It does not cover local challenge retries, continuing after an accepted gate to select a preferable witness, unbounded grinding, an optimized terminal round without its own extraction proof, or noninteractive retry selection. Those changes alter the experiment and require their own argument.
