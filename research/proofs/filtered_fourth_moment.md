# Fourth moments for filtered challenges and fixed ring vectors

Date: 2026-11-14. Scope: rigorous honest-fold rejection bounds for the optional operator-filtered challenge family. This supplies parameter inequalities, not a prover, an end-to-end protocol benchmark, or an MSIS hardness estimate. The bounds below retain the elementary fourth-moment baseline, then exploit the ring's paired real spectrum, and finally use centered conditioning. Standard moment inequalities are not claimed as novel.

The exact checks are in `scripts/filtered_fourth_moment_checks.py`. The independent peer checks use different examples in `scripts/filtered_fourth_moment_peer_checks.py`.

## 1. Model, chronology, and covariance

Let d≥2 be a power of two. Work over the real coefficient representation of R=R[X]/(X^d+1). A ring vector s=(s^(1),...,s^(n)) belongs to R^n, and its squared norm is the sum of squares of all nd real coefficients. Integer coefficients are allowed but are not needed for the moment argument.

Let X have d independent uniform coordinates in {−2,−1,0,1,2}. Let F be the event that its negacyclic multiplication operator has norm strictly less than T, and set p=Pr[F]. Assume a certified bound p>a>0. Let C have the conditional distribution X|F. Independent copies C_1,...,C_r are used with fixed s_1,...,s_r in the same R^n, and

    Y_i=C_i s_i,       z=Σ_i Y_i,
    t_i=||s_i||²,     S=Σ_i t_i≤β².

The complete s_i must be fixed before these independent challenges are drawn. All statements also hold conditionally on a preceding history that fixes the s_i and leaves this challenge law unchanged. They do not cover s_i selected after observing these challenges. Coefficients inside a filtered C_i are generally dependent.

The selected law satisfies

    E[C]=0,        Cov(C)=v I_d,        0≤v≤2/p.       (COV)

Here v=σ², so v²=σ⁴. To recall the covariance proof: negation preserves F and cancels the mean. Signed cyclic shifts preserve F and make diagonal second moments equal. Every off-diagonal moment can, up to sign, be shifted to E[C_0 C_delta]. Write delta=2^e u with u odd and set b=1+d/2^e. The Galois substitution X→X^b is a signed coefficient permutation, preserves the cube, permutes the evaluation roots, fixes coefficient zero, and negates coefficient delta. It preserves F, hence that moment is zero. Finally E_raw||X||²=2d and nonnegative conditioning imply dv≤2d/p.

No coordinate independence is inferred from (COV). It is precisely the full covariance matrix needed below.

## 2. Stacked multiplication and the exact raw fourth moment

For a fixed s in R^n, define M_s:R^d→R^(nd) by M_s x=(s^(1)x,...,s^(n)x). Thus M_s stacks n ordinary negacyclic multiplication matrices vertically. All d columns have squared norm t=||s||². Put H=M_sᵀM_s. Then

    H is positive semidefinite,
    H_jj=t for every j,       tr(H)=dt.

The raw coefficient moments are E[X_j²]=2 and E[X_j⁴]=34/5. Independence and zero means give the exact identity

    E_raw||M_s X||⁴
      =4(tr H)²+8 tr(H²)−(26/5)Σ_j H_jj².            (RAW4)

This follows by expanding (XᵀHX)². Terms with an index occurring once vanish. The pairings contribute the first two terms, while the repeated-index correction is `E[X_j⁴]−3(E[X_j²])²=34/5−12=−26/5`. Thus the correction is negative. This formula holds for rectangular stacked M_s; no square-output-dimension assumption is used.

For independent zero-mean output vectors Y_i, put μ_i=E||Y_i||² and ν_i=E||Y_i||⁴. The other exact identity needed throughout is

    E||Σ_iY_i||⁴
      =Σ_iν_i+2Σ_(i<j)μ_iμ_j+4Σ_(i<j)E<Y_i,Y_j>².  (SUM4)

To check the missing mixed terms explicitly, expand `||ΣY_i||²=Σ||Y_i||²+2Σ_(i<j)<Y_i,Y_j>`. A term `E[||Y_i||²<Y_i,Y_j>]` vanishes because E[Y_j]=0 and Y_j is independent. Products of distinct inner products also vanish: a disjoint pair has centered independent factors, while two pairs sharing one index vanish after conditioning on the shared vector and averaging the two other centered vectors. No unproved vanishing of an individual third moment is required.

If Σ_i=Cov(Y_i), then independence gives

    E<Y_i,Y_j>²=tr(Σ_iΣ_j).                           (CROSS)

## 3. Independent elementary baseline

Ignoring all ring spectral structure, a positive semidefinite H satisfies tr(H²)≤(tr H)². Dropping the negative term in (RAW4) gives

    E_raw||M_s X||⁴≤12d²t².

After filtering, nonnegative conditioning gives ν_i≤12d²t_i²/p. From (COV), μ_i=vdt_i≤2dt_i/p. The generic covariance inequality `tr(Σ_iΣ_j)≤tr(Σ_i)tr(Σ_j)=μ_iμ_j`, together with (SUM4), yields

    E||z||⁴
      ≤(12d²/p)Σ_it_i²+(24d²/p²)Σ_(i<j)t_it_j
      ≤(12d²/p²)S²,
    E||z||²≤2dS/p.

The final inequality uses p≤1. In particular, Var(||z||²)≤12d²β⁴/a². Cantelli's inequality therefore proves that the sufficient squared norm cap

    Γ² ≥ [(2+sqrt(12(1−f)/f))/a] dβ²                 (BASE)

gives rejection probability at most f, for 0<f<1. This validates the initial candidate bound independently of the refinements below. It is substantially stronger than the corresponding first-moment Markov cap `2dβ²/(af)` for small f.

## 4. The shared complex structure, including multiple blocks

Let J be multiplication by X^(d/2) on R^d. It satisfies

    J²=−I,       Jᵀ=−J,       JᵀJ=I.

On the nd-dimensional output space let J_out be the block diagonal matrix with n copies of J. Commutativity of ring multiplication gives

    M_s J=J_out M_s,
    M_sᵀ J_out=J M_sᵀ.

Therefore both H=M_sᵀM_s and M_sM_sᵀ commute with the appropriate J. The second identity follows by transposing the first and using the skew symmetry of both complex structures; it is not a dimension-changing identification.

Every eigenspace of a real symmetric matrix commuting with J is J-invariant. Such a real eigenspace has even dimension, since J²=−I on it. Thus all eigenvalues, including positive eigenvalues, have even multiplicity. For any such positive semidefinite matrix B,

    λ_max(B)≤tr(B)/2,
    tr(B²)≤(tr B)²/2.                               (PAIR)

This remains valid at d=2 and for zero matrices. Applying (PAIR) to H in (RAW4), and using Σ_jH_jj²=dt², gives

    E_raw||M_s X||⁴≤d² h_d t²,
    h_d=8−26/(5d).                                  (PAIRED4)

The bound is an equality for d=2: H=tI_2 in that case, including for stacked ring vectors. For larger d it is an upper bound, not an assertion that every s attains it.

The filtered output covariance is Σ_i=v M_(s_i)M_(s_i)ᵀ, so it also has the paired spectrum. Since Σ_j is positive semidefinite,

    tr(Σ_iΣ_j)
       ≤λ_max(Σ_i)tr(Σ_j)
       ≤μ_iμ_j/2.                                  (PAIRCROSS)

The Σ_i need not commute with each other. They do share a common output space and complex structure; stacked blocks and within-vector correlations are fully included.

## 5. First strengthened variance and a sufficient cap

Conditioning (PAIRED4) gives ν_i≤d²h_dt_i²/p, while μ_i=vdt_i. Combining (SUM4) and (PAIRCROSS), then subtracting `(Σ_iμ_i)²`, proves

    Var(||z||²)
      ≤d²[v²S²+(h_d/p−2v²)Σ_it_i²]
      ≤d²S² max{h_d/p−v², v²}.                     (V1)

The last inequality follows from `0≤Σ_it_i²≤S²`: if its coefficient is nonnegative, bound that sum by S²; otherwise bound it below by zero. This is an upper envelope, not a claim that either endpoint is attainable by every prescribed r and witness family.

Let k=(1−f)/f. For S>0, Cantelli's sufficient threshold is at most

    dS [v+sqrt(k max{h_d/p−v²,v²})].

There are two cases. When the maximum is v², this expression in brackets equals `(1+sqrt(k))v≤2(1+sqrt(k))/p`. Otherwise `h_d/p−v²≥v²≥0`, and Cauchy–Schwarz gives

    v+sqrt(k(h_d/p−v²))≤sqrt((1+k)h_d/p).

There is no square root of a negative value in this case distinction. Using p>a and S≤β² proves the sufficient cap

    Γ² ≥ dβ² max{(2/a)(1+sqrt((1−f)/f)),
                  sqrt(h_d/(af))}.                  (CAP1)

It is a sufficient upper envelope over the dependent unknown quantities p,v. We used only valid inequalities satisfied by their joint values; we did not assume they can vary independently, or claim to have computed their exact feasible supremum. The argument in fact works for all 0<f<1, including the common range f≤1/2.

For d64,a=9/16,f=1/16, the first term of (CAP1) dominates. A rational choice is Γ²=(52/3)dβ²: `( (52/3)a/2−1 )²=(31/8)²=961/64>15`, and the second squared inequality also holds. No floating-point evaluation is required to select this cap.

For the alternative T34 filter, the existing integer tail certificate proves p>901/1024. With a=901/1024 and f=1/16, (CAP1) permits Γ²=12dβ². The exact second-term certificate at d64 is

    h_64/(af)=648704/4505,
    144−648704/4505=16/4505>0.

For the first term, `(12a/2−1)²=(2191/512)²>15`. This is a separate optional profile: changing T31 to T34 changes the challenge operator cap and must be propagated through downstream parameters.

## 6. Centered conditioning and the challenge-energy variance

A further valid bound avoids discarding the raw mean before conditioning. Set

    g_d=h_d−4=4−26/(5d)>0.

The raw variable W=||M_s X||² has mean 2dt and, by (PAIRED4), variance at most d²g_dt². Its conditional mean is vdt. The exact centered identity gives

    Var(W|F)
      =E[(W−2dt)²|F]−((v−2)dt)²
      ≤d²t²[g_d/p−(v−2)²].                          (CENTER)

The right side is necessarily nonnegative for realizable parameters and nonzero t because it upper-bounds a variance. The previous uncentered inequality remains valid as well. Centered and uncentered bounds need not be claimed to have a uniform ordering for every abstract p,v; their difference depends on v. The centered envelope below is sharper for the displayed profile.

Applying (PAIRCROSS) to the variance expansion gives

    Var(||z||²)
      ≤d²[v²S²+(g_d/p−(v−2)²−v²)Σ_it_i²]
      ≤d²S² max{g_d/p−(v−2)²,v²}.                  (V2)

The scalar v is also much more tightly controlled by the raw challenge energy U=||X||². Its raw moments are

    E[U]=2d,
    Var(U)=d(34/5−4)=(14/5)d.

Let I_F be the filter indicator. The exact covariance identity and Cauchy–Schwarz give

    Cov(U,I_F)=pd(v−2),
    p²d²(v−2)²≤((14/5)d)·p(1−p).

Hence

    |v−2|≤sqrt((14/(5d))(1−p)/p)
          ≤rho_a:=sqrt(14(1−a)/(5da)).              (ENERGY)

No assumption about monotonicity of the operator filter in individual coordinates is used here.

To optimize a sufficient Cantelli cap for (V2), split its maximum into two cases. The v² case gives at most `(1+sqrt(k))v≤(1+sqrt(k))(2+rho_a)`. In the other case set u=v−2; Cauchy–Schwarz gives

    v+sqrt(k(g_d/p−(v−2)²))
      =2+u+sqrt(k(g_d/p−u²))
      ≤2+sqrt((1+k)g_d/p).

The argument is valid for either sign of u. Therefore the centered sufficient cap is

    Γ² ≥ dβ² max{2+sqrt(g_d/(af)),
                 (2+rho_a)(1+sqrt((1−f)/f))}.       (CAP2)

This cap again uses an upper envelope, not an exact maximizer of all feasible filtered distributions. One can retain both (CAP1) and (CAP2) and use whichever supplies the smaller certified cap.

## 7. Exact d64,T34 centered certificate

Take d=64, a=901/1024, f=1/16. Then

    g_64=627/160,
    g_64/(af)=321024/4505,
    rho_a²=861/144160.

The rational coefficient G=21/2 passes both conditions in (CAP2). For the first,

    (G−2)²−g_64/(af)
      =289/4−321024/4505
      =17849/18020>0.

For the second, the exact comparisons `rho_a²<1/144` and `15<(31/8)²` imply

    (2+rho_a)(1+sqrt(15))
      <(25/12)(39/8)=325/32<21/2.

Consequently

    Γ²=(21/2)dβ²                                    (D64)

certifies honest fold rejection probability at most 1/16. The alternative threshold Γ²=12dβ² remains a valid independent intermediate certificate. The original elementary coefficient `(2+sqrt(180))/a` is also valid but is larger.

All caps concern the unreduced real/integer sum of challenge products. If an actual protocol takes the centered coefficient representative modulo q, each centered coefficient has no greater absolute value than the corresponding unreduced integer coefficient. The same upper tail bound therefore applies to that centered norm. This observation does not replace any separate modular lifting argument needed for soundness.

## 8. Tail convention and zero witnesses

Cantelli bounds `Pr[V−E V≥t]≤Var(V)/(Var(V)+t²)` for t>0. The displayed thresholds therefore bound a norm rejection event `||z||²>Γ²`, and also the closed event `||z||²≥Γ²` when β>0 and the chosen cap is strictly above the mean. The p>a inequalities and the explicit strict rational margins ensure this in the displayed positive-β profiles. If β=0, all s_i are zero and z=0 deterministically; a verifier accepting norms at most Γ treats that case as an honest acceptance.

Neither a second-moment approximation nor a Gaussian heuristic appears in these proofs. Independence is needed across distinct filtered challenge polynomials, while all dependencies inside one polynomial and across its output blocks are handled by the full matrices.

## 9. Exact verification and limits

Run:

    python scripts/filtered_fourth_moment_checks.py

The script uses only integers and `Fraction`. Its completed checks include:

- Stacked two-block operators in d2 and d4, explicitly checking both intertwining identities, J²=−I, Jᵀ=−J, Gram diagonals, and paired trace inequalities.
- Exact raw fourth moments for multiple signed witness vectors, including equality in (PAIRED4) at d2.
- Exact filtered covariance, second and fourth moments, raw-centered conditional variance, and the indicator-energy covariance bound.
- A d2,T2 three-challenge sum enumerating 729 joint choices, a d2,T3 two-challenge sum enumerating 625 choices, and a d4,T4 two-challenge sum enumerating 201601 choices. These verify (SUM4), cross-covariance traces, (V1), and (V2) with full stacked output vectors.
- 2916 exact scalar parameter checks for (CAP1), including d2, and 55 feasible scalar checks for the displayed centered profile.
- The integer T34 rejection certificate, rational Γ²=12dβ² certificate, and rational Γ²=(21/2)dβ² certificate.

Finite checks validate examples and the implementation; the general statements are proved above. These inequalities supply one part of a parameter manifest. JL rejection, decomposition caps, all outer-opening norms, affine lifting, recursion, restart losses, runtime, and MSIS hardness must still use the actual chosen parameters. No claim is made that the original paper's proof sizes or full security estimates survive these changes automatically.
