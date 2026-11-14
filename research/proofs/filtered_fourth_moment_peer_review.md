# Independent review of the filtered-challenge fourth-moment bounds

Date: 2026-11-14. Scope: the complete `proofs/filtered_fourth_moment.md` and `scripts/filtered_fourth_moment_checks.py`, including the centered improvement and the retained earlier baselines. The mathematical arguments below were independently derived before the author's complete text was available, then compared with that text section by section.

**Mathematical conclusion:** the stacked complex-structure argument, trace inequalities, uncentered fourth-moment bound and stronger centered-variance bound are valid. The sufficient coefficients 52/3, 12 and 21/2 below are certified by exact arithmetic. They are sufficient envelopes, not claims to solve an exact extremal problem over all attainable filtered distributions.

## 1. The common complex structure survives stacking

Let s_i consist of n degree-<d real coefficient vectors, and let M_i:R^d->R^(nd) stack their negacyclic multiplication matrices. Put t_i=||s_i||^2. Multiplication by X^(d/2) is a real orthogonal skew-symmetric matrix J with J^2=-I. Put J_out=diag(J,...,J) on the output space.

Every negacyclic multiplication block commutes with J, so

    M_i J=J_out M_i.

Taking transposes, using J^T=-J and J_out^T=-J_out, gives J M_i^T=M_i^T J_out. Consequently H_i=M_i^T M_i commutes with J, and M_i M_i^T commutes with J_out. This addresses the potentially delicate point that the witness has many ring coordinates; one cannot replace J_out by the d-by-d J after stacking.

For a symmetric matrix commuting with an orthogonal complex structure, every real eigenspace is preserved by that structure and has even dimension. Its eigenvalues therefore occur with even multiplicity. For a positive semidefinite such matrix H,

    lambda_max(H)<=tr(H)/2,
    tr(H^2)<=tr(H)^2/2.

For two output covariance matrices Sigma_i,Sigma_j of this form,

    tr(Sigma_i Sigma_j)
       <=lambda_max(Sigma_j)tr(Sigma_i)
       <=tr(Sigma_i)tr(Sigma_j)/2.

The first inequality is the usual PSD trace inequality and does not require the two covariance matrices to commute with one another. Their shared complex structure guarantees the needed spectral multiplicity separately.

Each column of M_i is a signed shift of all the witness blocks, hence

    (H_i)_(j,j)=t_i,     tr(H_i)=d*t_i,
    sum_j (H_i)_(j,j)^2=d*t_i^2.

These identities justify retaining the negative fourth-cumulant term exactly.

## 2. Raw fourth moments and two valid conditioning bounds

Let X have iid coordinates uniform in {-2,-1,0,1,2}. The exact moments are E[X_j^2]=2 and E[X_j^4]=34/5. For W_i=||M_i X||^2,

    E[W_i]=2d*t_i,
    E[W_i^2]=4tr(H_i)^2+8tr(H_i^2)
                 -(26/5)sum_j(H_i)_(j,j)^2.

The coefficient -26/5 equals 34/5-3*2^2. The pairwise-spectrum bound proves, with

    h_d=8-26/(5d),       g_d=4-26/(5d),

that

    E[W_i^2]<=h_d*d^2*t_i^2,
    Var(W_i)<=g_d*d^2*t_i^2.

Let F be the operator-norm filter event, p=Pr[F]>a>0, and C=X conditioned on F. Its reviewed covariance is v I_d. For Y_i=M_i C,

    E||Y_i||^2=v*d*t_i,
    Cov(Y_i)=v M_i M_i^T.

Conditioning the nonnegative W_i^2 gives the valid baseline E||Y_i||^4<=h_d*d^2*t_i^2/p.

The stronger conditioning step uses the raw centered square, which is also nonnegative:

    Var(||Y_i||^2)
      = E[(W_i-2d*t_i)^2 | F] -(v-2)^2*d^2*t_i^2
      <= [g_d/p-(v-2)^2]*d^2*t_i^2.                  (CENTERED)

No independence of the filtered coefficients is needed. The subtraction is legitimate because the conditional mean is exactly v*d*t_i. The left side is nonnegative, so for an actual distribution and t_i>0 the bracket cannot be negative.

## 3. Independent challenges and the sum variance

For independent selected C_i, set Z=sum_i M_i C_i and S=sum_i t_i. The witnesses must be fixed before these challenges. Zero means eliminate terms with an unpaired factor, yielding the exact identity

    Var(||Z||^2)
       =sum_i Var(||Y_i||^2)+4sum_(i<j)tr(Sigma_i Sigma_j).

The factors two/four are correct: the terms 2sum_(i<j)E||Y_i||^2 E||Y_j||^2 in the fourth moment cancel the corresponding terms in the square of the mean.

Using the complex trace bound gives, for the uncentered baseline,

    Var(||Z||^2)
      <=d^2[v^2 S^2+(h_d/p-2v^2)sum_i t_i^2]
      <=d^2 S^2 max(h_d/p-v^2,v^2).

Using (CENTERED) instead gives

    Var(||Z||^2)
      <=d^2[v^2 S^2+(g_d/p-(v-2)^2-v^2)sum_i t_i^2]
      <=d^2 S^2 max(g_d/p-(v-2)^2,v^2).              (VAR)

Both last inequalities follow by writing sum_i t_i^2/S^2 in [0,1]; the S=0 case is deterministic. The centered formula is the one used for the 21/2 certificate below.

## 4. Bounding the actual conditional covariance parameter

The baseline v<=2/p follows by conditioning the nonnegative X_j^2. A sharper bound uses U=||X||^2. Raw independence gives

    E[U]=2d,       Var(U)=(14/5)d.

Since E[U|F]=dv,

    Cov(U,1_F)=p*d*(v-2).

Cauchy--Schwarz, with Var(1_F)=p(1-p), therefore proves

    |v-2|<=sqrt(14(1-p)/(5dp))
          <sqrt(14(1-a)/(5da))=:rho_a.

This is an unconditional covariance calculation followed by conditioning; it does not use a false independence assertion between energy and the filter. It remains valid for any filter with the stated scalar covariance, not only one with an independently analyzable acceptance indicator.

For completeness another weaker admissible interval is max(0,4-2/p)<=v<=min(4,2/p), because X_j^2<=4. The sufficient envelopes below do not need that interval or claim an exact optimization over it.

## 5. Cantelli and the p/v envelopes

Let 0<f<1, k=(1-f)/f and S<=beta^2. Since E||Z||^2=dvS, Cantelli is applicable whenever

    Gamma^2/(d beta^2)
       >=v+sqrt(k*variance_factor).

For the uncentered factor max(h_d/p-v^2,v^2), split into its two branches. In the h_d/p-v^2 branch the radicand is nonnegative, and Cauchy--Schwarz gives

    v+sqrt(k)*sqrt(h_d/p-v^2)<=sqrt((1+k)h_d/p).

The other branch is (1+sqrt(k))*v. Thus a sufficient coefficient is

    C_uncentered=max{(2/a)(1+sqrt(k)),sqrt(h_d/(a f))}.

For (VAR), write w=v-2. The centered branch satisfies

    2+w+sqrt(k)*sqrt(g_d/p-w^2)
       <=2+sqrt((1+k)g_d/p).

The other branch is at most (2+rho_a)(1+sqrt(k)). Hence

    C_centered=max{2+sqrt(g_d/(a f)),
                   (2+rho_a)(1+sqrt(k))}              (CAP)

is sufficient. This proof treats the maximum by cases; it never takes a square root of a negative unused branch. Replacing p by its lower bound a has the safe direction. The actual quantities are strictly smaller when p>a, so a coefficient meeting (CAP) gives fold rejection strictly below f for beta>0. For beta=0, Z=0 deterministically.

These bounds hold conditionally on any prior history that fixes the witness vectors and leaves the challenge samples fresh and independent. They do not apply to witness vectors chosen after observing those challenges.

## 6. Exact certificates at d=64

The independent checker retains each earlier baseline:

- a=9/16, f=1/16: C=52/3 satisfies the uncentered envelope;
- a=901/1024, f=1/16: C=12 satisfies the uncentered envelope.

For the second baseline, h_d/(a f)=648704/4505 and 144*4505-648704=16>0. Also (12a/2-1)^2=(2191/512)^2>15. Thus the 12 coefficient has an exact certificate independent of the centered improvement.

For the centered improvement, take a=901/1024 and f=1/16. Then

    g_d=627/160,
    g_d/(a f)=321024/4505,
    rho_a^2=861/144160.

The clean coefficient C=21/2 satisfies the first branch because

    (21/2-2)^2 - 321024/4505 =17849/18020>0.

For the second branch, rho_a<5/64 and sqrt(15)<31/8, giving

    (2+rho_a)(1+sqrt(15))
        <(133/64)(39/8)=5187/512<21/2.

The author's alternative rho_a<1/12 also suffices. Therefore

    Gamma^2=(21/2)d beta^2

certifiably gives fold rejection below 1/16. Changing the fold cap alone does not change the source norm slack s^2=H/120; all digit caps, actual target B values and collision radii must nevertheless be recalculated from the new Gamma.

## 7. Independent finite checks and remaining scope

`scripts/filtered_fourth_moment_peer_checks.py` uses exact integers/Fraction and its own stacked matrix, moment and covariance calculations. It verifies both domain/output complex structures, the constant Gram diagonal, raw fourth identity, centered variance identity, energy/indicator covariance, tracecross inequality and exact sum moments. It enumerates 81 joint selected-challenge pairs in d=2 and 37249 in d=4 with two ring coordinates per witness. It also verifies every displayed d64 rational certificate. The results are in `notes/parameter-results/filtered_fourth_moment_peer_checks.json`.

The author's completed checker was rerun successfully and its output is in `notes/parameter-results/filtered_fourth_moment_author_rerun.json`. That run included three independent d=2 challenges and a d=4 enumeration of 201601 challenge pairs; it also checked 2916 rational p/v grid points and 55 centered-profile points. Finite checks support the implementation, while the proofs above establish the general bounds.

This result improves honest norm accounting for the specified filtered cube. It does not establish MSIS hardness, a tighter computational binding reduction, improved end-to-end proof size, or applicability to the original fixed-type challenge distribution without its own moment analysis.

## 8. Final-text disposition

The complete author text was reviewed after its final centered section and checker were saved. Sections 1--2 correctly define the rectangular stacked matrices and all mixed moment cancellations. Section 3 is a separate valid baseline. Sections 4--5 retain the output-space complex structure and treat the two variance branches correctly. Sections 6--7 implement the raw-centered conditioning and energy-indicator covariance without silently reintroducing coefficient independence. Section 8 specifies closed/strict tails and the zero witness correctly. The checker and the displayed rational certificates agree.

No mathematical blocker was found. The sufficient coefficient 21/2 may be used in the honest parameter recurrence, provided every downstream digit cap, target extraction budget and MSIS radius is recomputed. This review does not license keeping an old target beta after changing the fold cap, or claiming a security level from the improved cap alone.
