"""Independent exact checks for stacked negacyclic fourth-moment bounds."""
from fractions import Fraction as F
from itertools import product
import json

from certified_filtered_challenges_checks import certified_op_below, negacyclic_matrix


def transpose(a):
    return list(map(list, zip(*a)))


def mm(a, b):
    bt = transpose(b)
    return [[sum(x*y for x,y in zip(row,col)) for col in bt] for row in a]


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


def scaled(a, k):
    return [[k*x for x in row] for row in a]


def mv(a, v):
    return tuple(sum(x*y for x,y in zip(row,v)) for row in a)


def norm2(v):
    return sum(x*x for x in v)


def stacked(polynomials):
    return [row for polynomial in polynomials for row in negacyclic_matrix(polynomial)]


def block_diagonal(a, count):
    n = len(a)
    out = [[0]*(n*count) for _ in range(n*count)]
    for k in range(count):
        for i in range(n):
            for j in range(n):
                out[k*n+i][k*n+j] = a[i][j]
    return out


def check_instance(d, threshold, blocks):
    cube = tuple(product(range(-2,3), repeat=d))
    selected = tuple(c for c in cube if certified_op_below(c, threshold))
    p = F(len(selected), len(cube))
    v = F(sum(c[0]*c[0] for c in selected), len(selected))
    assert max(F(0), 4-2/p) <= v <= min(F(4),2/p)
    h = F(8)-F(26,5*d)
    g = F(4)-F(26,5*d)
    raw_energy_variance = F(sum((norm2(c)-2*d)**2 for c in cube),len(cube))
    assert raw_energy_variance == F(14*d,5)
    energy_indicator_covariance = F(sum(norm2(c) for c in selected),len(cube))-2*d*p
    assert energy_indicator_covariance == p*d*(v-2)
    assert energy_indicator_covariance**2 <= raw_energy_variance*p*(1-p)
    assert (v-2)**2 <= F(14,5*d)*(1-p)/p
    j = negacyclic_matrix([int(i == d//2) for i in range(d)])
    j_out = block_diagonal(j, len(blocks[0]))
    assert mm(j,j) == [[-int(a==b) for b in range(d)] for a in range(d)]
    moments, covariances, energies, outputs = [], [], [], []
    for source in blocks:
        m = stacked(source)
        energy = sum(norm2(s) for s in source)
        gram = mm(transpose(m),m)
        assert mm(m,j) == mm(j_out,m)
        assert mm(gram,j) == mm(j,gram)
        assert all(gram[i][i] == energy for i in range(d))
        assert trace(gram) == d*energy
        assert 2*trace(mm(gram,gram)) <= trace(gram)**2
        raw_fourth = F(sum(norm2(mv(m,c))**2 for c in cube),len(cube))
        identity = (4*trace(gram)**2 + 8*trace(mm(gram,gram))
                    -F(26,5)*sum(gram[i][i]**2 for i in range(d)))
        assert raw_fourth == identity <= d*d*h*energy*energy
        raw_variance = raw_fourth-(2*d*energy)**2
        assert raw_variance <= g*d*d*energy*energy
        values = tuple(mv(m,c) for c in selected)
        fourth = F(sum(norm2(y)**2 for y in values),len(values))
        assert fourth <= raw_fourth/p <= d*d*h*energy*energy/p
        selected_variance = fourth-(v*d*energy)**2
        selected_centered_second = F(sum((norm2(y)-2*d*energy)**2 for y in values),len(values))
        assert selected_variance == selected_centered_second-(v-2)**2*d*d*energy*energy
        assert selected_centered_second <= raw_variance/p
        assert selected_variance <= (g/p-(v-2)**2)*d*d*energy*energy
        covariance = scaled(mm(m,transpose(m)),v)
        assert mm(covariance,j_out) == mm(j_out,covariance)
        assert 2*trace(mm(covariance,covariance)) <= trace(covariance)**2
        moments.append(fourth)
        covariances.append(covariance)
        energies.append(energy)
        outputs.append(values)
    assert len(outputs) == 2
    assert 2*trace(mm(*covariances)) <= trace(covariances[0])*trace(covariances[1])
    count = len(selected)**2
    second = fourth = F(0)
    for y,z in product(*outputs):
        value = norm2(tuple(a+b for a,b in zip(y,z)))
        second += value
        fourth += value*value
    second /= count
    fourth /= count
    total_energy = sum(energies)
    assert second == d*v*total_energy
    expected_fourth = (sum(moments) + 2*d*d*v*v*energies[0]*energies[1]
                      +4*trace(mm(*covariances)))
    assert fourth == expected_fourth
    variance = fourth-second*second
    detailed = d*d*(v*v*total_energy*total_energy
                   +(h/p-2*v*v)*sum(t*t for t in energies))
    simplified = d*d*total_energy*total_energy*max(h/p-v*v,v*v)
    assert variance <= detailed <= simplified
    centered_detailed = d*d*(v*v*total_energy*total_energy
                            +(g/p-(v-2)**2-v*v)*sum(t*t for t in energies))
    centered_simplified = d*d*total_energy*total_energy*max(g/p-(v-2)**2,v*v)
    assert variance <= centered_detailed <= centered_simplified
    return {"d":d,"threshold":threshold,"selected_count":len(selected),
            "p":str(p),"v":str(v),"joint_cases":count,
            "second_moment":str(second),"fourth_moment":str(fourth),
            "variance":str(variance),"uncentered_variance_upper":str(simplified),
            "centered_variance_upper":str(centered_simplified)}


def main():
    reports = [
        check_instance(2,2,(((1,2),(2,-1)),((1,0),(0,1)))),
        check_instance(4,3,(((1,2,0,-1),(0,1,1,0)),
                            ((2,0,-1,1),(1,-1,0,1))))
    ]
    d,a,f,C = 64,F(9,16),F(1,16),F(52,3)
    h = F(8)-F(26,5*d)
    k = (1-f)/f
    assert C*a/2-1 > 0 and (C*a/2-1)**2 > k
    assert C*C > h/(a*f)
    a34, C34 = F(901,1024), F(12)
    assert C34*a34/2-1 > 0 and (C34*a34/2-1)**2 > k
    assert C34*C34 > h/(a34*f)
    assert h/(a34*f) == F(648704,4505)
    assert 144*4505-648704 == 16
    improved_C = F(21,2)
    g = F(4)-F(26,5*d)
    rho_squared = F(14,5*d)*(1-a34)/a34
    assert g/(a34*f) == F(321024,4505)
    assert (improved_C-2)**2-g/(a34*f) == F(17849,18020) > 0
    assert rho_squared == F(861,144160) < F(5,64)**2
    assert 15 < F(31,8)**2
    assert (2+F(5,64))*(1+F(31,8)) == F(5187,512) < improved_C
    print(json.dumps({"instances":reports,"d64_T31_coefficient_certificate":str(C),
                      "d64_T34_coefficient_certificate":str(C34),
                      "T34_second_branch_exact_squared_margin":"16/4505",
                      "d64_T34_centered_coefficient_certificate":str(improved_C),
                      "centered_first_branch_squared_margin":"17849/18020",
                      "centered_energy_covariance_rho_squared":str(rho_squared),
                      "scope":"exact moment identities and sufficient envelopes only"},indent=2))


if __name__ == "__main__":
    main()
