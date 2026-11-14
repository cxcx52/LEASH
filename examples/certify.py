"""Display certified mathematical quantities without dumping large integers."""
import json
from fractions import Fraction
from math import log2
from labrador_repair.bounds import jl_certificate, jl_security_profile, repair_profile

def display(value):
    if isinstance(value, Fraction):
        if value < Fraction(1, 2**32):
            return {"log2_display_only": log2(value), "decision_arithmetic": "exact rational"}
        return str(value)
    return value

if __name__ == '__main__':
    print(json.dumps({"jl": {k:display(v) for k,v in jl_certificate().items()},
                      "profile": {k:display(v) for k,v in repair_profile().items()},
                      "jl_security_family": [
                          {k:display(v) for k,v in jl_security_profile(bits).items()}
                          for bits in (128, 256, 512)
                      ]}, indent=2))
