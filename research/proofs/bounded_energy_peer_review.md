# Independent review: bounded-energy challenge certificate

Date: 2026-11-14. This is a separate development review, not external peer review. The root reviewer read `fixed_energy_challenge_exploration.md`, inspected the checker, reran its exact assertions, and separately checked the compact integer moment identities. Verdict: no blocking mathematical issue in the d64,E104,T30 result. The requested clarification that the general moment lemma uses a power-of-two degree at least two has been incorporated.

## Count, tilting and strict events

The recurrence for coefficients of `(1+2z+2z^4)^d` counts the raw ball exactly. The energy-71 multinomial sum agrees with that independent DP. The original PDF p.6 uses the single type with 23 zeros, 31 unit coefficients and 10 magnitude-two coefficients; the full energy-71 shell is a different, larger raw set. The comparison in the note correctly distinguishes these.

For the product law proportional to t^(c^2), conditioning on a fixed energy is uniform, whereas conditioning on an energy ball is generally not. The note uses the correct ball inequality: each permitted vector has product weight at least t^E/Z^d, so the bad count is at most Z^d t^(-E) times the product-law bad probability. The normalizing ball count is included.

The tilted even-moment argument explicitly checks the fourth moment and then uses the ratio bound below four for later moments. The net factors count d/2 conjugate roots and m angular directions. All three stated squared-cosine lower bounds follow from the given rational square comparisons. The exponential polynomial is a strict lower bound at a positive argument; its reciprocal therefore gives a strict upper bound on the bad count. This justifies the integer rounding `floor(2*N_ball/3)+1`.

The operator bad event is closed, the selected event is strict, and the energy ball includes its energy boundary. Zero remains in the selected set. Uniform selection followed by the deterministic operator predicate gives exactly the desired conditional law. The unit-difference argument is inherited from the already reviewed five-symbol coefficient bound, independently of the changed energy law.

## Dependent raw moments and filtering

The raw ball has independent sign-flip and coordinate-permutation invariance, but its squared coordinates are dependent. The fourth expansion correctly uses m22 rather than v0 squared. The diagonal entries of the stacked Gram matrix all equal the witness energy. The paired-spectrum bound on its trace square supplies

    g=2m22-v0^2+(m4-3m22)/d.

The identity `g=Var(U)/d^2+(1-2/d)m22` proves nonnegativity for actual moments at d>=2. The complex-structure argument itself uses even d; the scoped power-of-two hypothesis supplies this.

After filtering, arbitrary coefficient permutations need not preserve the law. The note instead uses negation, signed shifts and odd Galois maps to establish zero mean and scalar covariance. The conditional variance is centered at the raw mean before conditioning. Its energy-indicator covariance bounds the shift in the selected scalar covariance. These steps require no independence within one challenge.

Independence across distinct selected challenges and fixed witnesses before the draws are explicit. The stacked output covariance matrices have a common complex structure and need not commute with each other. Their trace-product bound remains valid. The two Cantelli branches therefore prove the stated general sufficient cap.

## Exact d64 certificates and scope

Besides rerunning the original checker, the review separately verified that the displayed A,B,C,D0 equal the DP-derived v0,m4,m22. It then checked

    G=(125C+B)D0-64A^2,
    V=(B+63C)D0-64A^2,
    g=G/(64D0^2), rho^2=V/(128D0^2),
    8(9D0-A)^2>3G, 16A<25D0, 2V<D0^2.

Thus Gamma squared equal to 9d beta squared is justified by strict rational margins. The complete Q128 expression includes the challenge, JL, scalar, ring and source statistical terms, and is strictly below 2^-128. The note conditions whole-protocol completeness on a valid recursive norm/packing manifest. No computational hardness, full security level or shorter protocol follows from this certificate alone.

The energy-71 cardinality obstruction concerns the currently proved `(r+2)/N` error expression. It is not a lower bound on actual soundness or an attack. Likewise, failure of the T15 concentration certificate is correctly treated as inconclusive.
