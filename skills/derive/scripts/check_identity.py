"""Verify symbolic identities by randomized high-precision substitution.

`simplify(A - B) == 0` often fails to close for true identities, and its failure is
uninformative — you learn nothing about whether the identity holds. Substituting random
values for every free symbol and evaluating at high precision is decisive in milliseconds,
and a single failing sample is a genuine counterexample you can inspect.

Requires sympy. Import from a derivation notebook or script:

    from check_identity import check_identity, check_matrix_identity

    x, y = sympy.symbols("x y")
    check_identity(sympy.sin(x + y),
                   sympy.sin(x)*sympy.cos(y) + sympy.cos(x)*sympy.sin(y))

Run directly for a self-test:

    python check_identity.py
"""

from __future__ import annotations

import random

import sympy as sp


class IdentityResult:
    def __init__(self, holds, samples, worst, counterexample=None, skipped=0):
        self.holds = holds
        self.samples = samples
        self.worst = worst
        self.counterexample = counterexample
        self.skipped = skipped

    def __bool__(self):
        return self.holds

    def __repr__(self):
        if self.holds:
            return (
                f"<identity holds: {self.samples} samples, "
                f"max |lhs-rhs| = {self.worst:.3e}>"
            )
        return f"<identity FAILS at {self.counterexample}, |lhs-rhs| = {self.worst:.3e}>"


def _sample(symbols, rng, scale, complex_values):
    """Random values away from 0 and 1, where accidental agreement is common."""
    point = {}
    for s in symbols:
        re = rng.uniform(0.2, scale) * rng.choice([-1, 1])
        if complex_values and not s.is_real:
            im = rng.uniform(0.2, scale) * rng.choice([-1, 1])
            point[s] = sp.Float(re, 30) + sp.I * sp.Float(im, 30)
        else:
            point[s] = sp.Float(re, 30)
    return point


def check_identity(
    lhs,
    rhs,
    symbols=None,
    samples: int = 12,
    tol: float = 1e-20,
    scale: float = 3.0,
    complex_values: bool = True,
    precision: int = 40,
    seed: int = 0,
) -> IdentityResult:
    """Test whether lhs == rhs by substituting random values for every free symbol.

    Evaluates at `precision` digits so the tolerance can sit far below anything a real
    discrepancy would produce. A single failure is a counterexample; passing all samples
    is strong evidence, not proof — which is the right trade for catching algebra errors.

    Samples where either side is singular (division by zero, branch point) are skipped
    rather than counted as failures; a run that skips most samples is reported.
    """
    lhs, rhs = sp.sympify(lhs), sp.sympify(rhs)
    symbols = list(symbols) if symbols else sorted(
        lhs.free_symbols | rhs.free_symbols, key=str
    )
    if not symbols:
        diff = complex(sp.N(lhs - rhs, precision))
        return IdentityResult(abs(diff) < tol, 1, abs(diff))

    rng = random.Random(seed)
    worst, skipped = 0.0, 0
    for _ in range(samples):
        point = _sample(symbols, rng, scale, complex_values)
        try:
            diff = complex(sp.N(lhs.subs(point) - rhs.subs(point), precision))
        except (TypeError, ValueError, ZeroDivisionError):
            skipped += 1
            continue
        if not (abs(diff) == abs(diff)):  # NaN
            skipped += 1
            continue
        magnitude = abs(diff)
        if magnitude > tol:
            return IdentityResult(False, samples, magnitude, point, skipped)
        worst = max(worst, magnitude)
    return IdentityResult(True, samples - skipped, worst, skipped=skipped)


def check_matrix_identity(lhs, rhs, samples: int = 8, tol: float = 1e-20, **kwargs):
    """Elementwise version, for operator algebra written as symbolic matrices."""
    lhs, rhs = sp.Matrix(lhs), sp.Matrix(rhs)
    if lhs.shape != rhs.shape:
        return IdentityResult(False, 0, float("inf"), f"shape {lhs.shape} vs {rhs.shape}")
    worst = 0.0
    for i in range(lhs.rows):
        for j in range(lhs.cols):
            result = check_identity(lhs[i, j], rhs[i, j], samples=samples, tol=tol, **kwargs)
            if not result.holds:
                return IdentityResult(
                    False, result.samples, result.worst, (i, j, result.counterexample)
                )
            worst = max(worst, result.worst)
    return IdentityResult(True, samples, worst)


def check_series(expr, reference, var, order: int, point=0, **kwargs) -> IdentityResult:
    """Check that `expr` matches `reference` through the claimed order.

    Use this to confirm the order bookkeeping in a derivation: if you claimed the neglected
    term is O(x^3), the expansions must agree through x^2 and differ at x^3.
    """
    lhs = sp.series(sp.sympify(expr), var, point, order).removeO()
    rhs = sp.series(sp.sympify(reference), var, point, order).removeO()
    return check_identity(sp.expand(lhs - rhs), 0, **kwargs)


if __name__ == "__main__":
    x, y, t = sp.symbols("x y t")

    print("true identity:      ", check_identity(
        sp.sin(x + y), sp.sin(x) * sp.cos(y) + sp.cos(x) * sp.sin(y)))
    print("false identity:     ", check_identity(
        sp.sin(x + y), sp.sin(x) * sp.cos(y) - sp.cos(x) * sp.sin(y)))
    print("subtle sign error:  ", check_identity(
        sp.cos(x - y), sp.cos(x) * sp.cos(y) - sp.sin(x) * sp.sin(y)))
    print("matrix commutator:  ", check_matrix_identity(
        sp.Matrix([[0, x], [x, 0]]) * sp.Matrix([[1, 0], [0, -1]])
        - sp.Matrix([[1, 0], [0, -1]]) * sp.Matrix([[0, x], [x, 0]]),
        sp.Matrix([[0, -2 * x], [2 * x, 0]])))
    print("series to O(t^3):   ", check_series(sp.exp(t), 1 + t + t**2 / 2, t, 3))
    print("series wrong coeff: ", check_series(sp.exp(t), 1 + t + t**2 / 3, t, 3))
