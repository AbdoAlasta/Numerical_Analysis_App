"""Non-linear equation solvers: Bisection, False Position, Fixed Point,
Newton-Raphson, Secant.

All functions accept string expressions and use SymPy for safe parsing.
"""
import math
import numpy as np
import sympy as sp


def _parse_function(expr_str: str):
    """Return (sympy_expr, callable) for a function of x."""
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str, locals={"x": x, "e": sp.E, "pi": sp.pi})
    except (sp.SympifyError, TypeError) as exc:
        raise ValueError(f"Cannot parse expression '{expr_str}': {exc}") from exc
    try:
        f = sp.lambdify(x, expr, modules=["numpy", "math"])
        # Test with a finite value
        result = f(1.0)
        float(result)  # ensure scalar
    except Exception as exc:
        raise ValueError(f"Expression evaluation error: {exc}") from exc
    return expr, f


def _approximate_error(x_new: float, x_old: float) -> float:
    if abs(x_new) < 1e-15:
        return 0.0
    return abs((x_new - x_old) / x_new) * 100.0


def _fmt(value: float, dp: int) -> float:
    """Round value to dp decimal places."""
    try:
        return round(float(value), dp)
    except (TypeError, ValueError):
        return value


def solve_bisection(
    f_expr: str,
    xl: float,
    xu: float,
    epsilon: float = 0.0001,
    max_iter: int = 100,
    decimal_places: int = 6,
    stop_by_epsilon: bool = True,
) -> dict:
    _, f = _parse_function(f_expr)
    xl, xu = float(xl), float(xu)

    f_xl = float(f(xl))
    f_xu = float(f(xu))
    if f_xl * f_xu > 0:
        raise ValueError(
            f"No sign change detected between xl={xl} and xu={xu}.\n"
            "f(xl) and f(xu) must have opposite signs."
        )

    iterations = []
    xr_old = None
    converged = False

    for n in range(1, max_iter + 1):
        xr = (xl + xu) / 2.0
        f_xr = float(f(xr))
        f_xl_val = float(f(xl))
        f_xu_val = float(f(xu))

        ea = _approximate_error(xr, xr_old) if xr_old is not None else float("inf")

        iterations.append({
            "n": n,
            "xl": _fmt(xl, decimal_places),
            "xu": _fmt(xu, decimal_places),
            "xr": _fmt(xr, decimal_places),
            "f_xl": _fmt(f_xl_val, decimal_places),
            "f_xu": _fmt(f_xu_val, decimal_places),
            "f_xr": _fmt(f_xr, decimal_places),
            "ea": _fmt(ea, decimal_places) if ea != float("inf") else "---",
        })

        if stop_by_epsilon and xr_old is not None and ea < epsilon:
            converged = True
            break

        if f_xl_val * f_xr < 0:
            xu = xr
        else:
            xl = xr

        xr_old = xr

    if not converged and not stop_by_epsilon:
        converged = True  # stopped by max_iter intentionally

    final_error = iterations[-1]["ea"] if iterations else float("inf")
    if final_error == "---":
        final_error = float("inf")

    return {
        "method": "Bisection",
        "f_expr": f_expr,
        "iterations": iterations,
        "root": _fmt(iterations[-1]["xr"], decimal_places) if iterations else None,
        "final_error": final_error,
        "converged": converged,
        "iterations_count": len(iterations),
    }


def solve_false_position(
    f_expr: str,
    xl: float,
    xu: float,
    epsilon: float = 0.0001,
    max_iter: int = 100,
    decimal_places: int = 6,
    stop_by_epsilon: bool = True,
) -> dict:
    _, f = _parse_function(f_expr)
    xl, xu = float(xl), float(xu)

    f_xl = float(f(xl))
    f_xu = float(f(xu))
    if f_xl * f_xu > 0:
        raise ValueError(
            f"No sign change detected between xl={xl} and xu={xu}.\n"
            "f(xl) and f(xu) must have opposite signs."
        )

    iterations = []
    xr_old = None
    converged = False

    for n in range(1, max_iter + 1):
        f_xl_val = float(f(xl))
        f_xu_val = float(f(xu))
        denom = f_xl_val - f_xu_val
        if abs(denom) < 1e-15:
            raise ZeroDivisionError(
                "f(xl) and f(xu) are equal — False Position cannot continue."
            )
        xr = xu - f_xu_val * (xl - xu) / denom
        f_xr = float(f(xr))

        ea = _approximate_error(xr, xr_old) if xr_old is not None else float("inf")

        iterations.append({
            "n": n,
            "xl": _fmt(xl, decimal_places),
            "xu": _fmt(xu, decimal_places),
            "xr": _fmt(xr, decimal_places),
            "f_xl": _fmt(f_xl_val, decimal_places),
            "f_xu": _fmt(f_xu_val, decimal_places),
            "f_xr": _fmt(f_xr, decimal_places),
            "ea": _fmt(ea, decimal_places) if ea != float("inf") else "---",
        })

        if stop_by_epsilon and xr_old is not None and ea < epsilon:
            converged = True
            break

        if f_xl_val * f_xr < 0:
            xu = xr
        else:
            xl = xr

        xr_old = xr

    if not converged and not stop_by_epsilon:
        converged = True

    final_error = iterations[-1]["ea"] if iterations else float("inf")
    if final_error == "---":
        final_error = float("inf")

    return {
        "method": "False Position",
        "f_expr": f_expr,
        "iterations": iterations,
        "root": _fmt(iterations[-1]["xr"], decimal_places) if iterations else None,
        "final_error": final_error,
        "converged": converged,
        "iterations_count": len(iterations),
    }


def solve_newton_raphson(
    f_expr: str,
    x0: float,
    epsilon: float = 0.0001,
    max_iter: int = 100,
    decimal_places: int = 6,
    stop_by_epsilon: bool = True,
) -> dict:
    x_sym = sp.Symbol("x")
    try:
        expr = sp.sympify(f_expr, locals={"x": x_sym, "e": sp.E, "pi": sp.pi})
    except (sp.SympifyError, TypeError) as exc:
        raise ValueError(f"Cannot parse expression: {exc}") from exc

    d_expr = sp.diff(expr, x_sym)
    f = sp.lambdify(x_sym, expr, modules=["numpy", "math"])
    df = sp.lambdify(x_sym, d_expr, modules=["numpy", "math"])

    xi = float(x0)
    iterations = []
    converged = False

    for n in range(1, max_iter + 1):
        f_xi = float(f(xi))
        df_xi = float(df(xi))

        if abs(df_xi) < 1e-14:
            raise ZeroDivisionError(
                f"Derivative f'(x) ≈ 0 at x = {xi:.6f}.\n"
                "Newton-Raphson cannot continue. Try a different initial guess."
            )

        xi_next = xi - f_xi / df_xi
        ea = _approximate_error(xi_next, xi)

        iterations.append({
            "n": n,
            "xi": _fmt(xi, decimal_places),
            "f_xi": _fmt(f_xi, decimal_places),
            "df_xi": _fmt(df_xi, decimal_places),
            "xi_next": _fmt(xi_next, decimal_places),
            "ea": _fmt(ea, decimal_places),
        })

        xi = xi_next

        if stop_by_epsilon and ea < epsilon:
            converged = True
            break

    if not converged and not stop_by_epsilon:
        converged = True

    return {
        "method": "Newton-Raphson",
        "f_expr": f_expr,
        "iterations": iterations,
        "root": _fmt(xi, decimal_places),
        "final_error": iterations[-1]["ea"] if iterations else float("inf"),
        "converged": converged,
        "iterations_count": len(iterations),
    }


def solve_secant(
    f_expr: str,
    x0: float,
    x1: float,
    epsilon: float = 0.0001,
    max_iter: int = 100,
    decimal_places: int = 6,
    stop_by_epsilon: bool = True,
) -> dict:
    _, f = _parse_function(f_expr)
    xi_prev = float(x0)
    xi = float(x1)
    iterations = []
    converged = False

    for n in range(1, max_iter + 1):
        f_xi_prev = float(f(xi_prev))
        f_xi = float(f(xi))
        denom = f_xi - f_xi_prev

        if abs(denom) < 1e-15:
            raise ZeroDivisionError(
                f"f(x{n}) ≈ f(x{n-1}) — Secant method denominator is zero.\n"
                "Choose different initial points."
            )

        xi_next = xi - f_xi * (xi - xi_prev) / denom
        ea = _approximate_error(xi_next, xi)

        iterations.append({
            "n": n,
            "xi_prev": _fmt(xi_prev, decimal_places),
            "xi": _fmt(xi, decimal_places),
            "f_xi_prev": _fmt(f_xi_prev, decimal_places),
            "f_xi": _fmt(f_xi, decimal_places),
            "xi_next": _fmt(xi_next, decimal_places),
            "ea": _fmt(ea, decimal_places),
        })

        xi_prev = xi
        xi = xi_next

        if stop_by_epsilon and ea < epsilon:
            converged = True
            break

    if not converged and not stop_by_epsilon:
        converged = True

    return {
        "method": "Secant",
        "f_expr": f_expr,
        "iterations": iterations,
        "root": _fmt(xi, decimal_places),
        "final_error": iterations[-1]["ea"] if iterations else float("inf"),
        "converged": converged,
        "iterations_count": len(iterations),
    }


def solve_fixed_point(
    f_expr: str,
    g_expr: str,
    x0: float,
    epsilon: float = 0.0001,
    max_iter: int = 100,
    decimal_places: int = 6,
    stop_by_epsilon: bool = True,
) -> dict:
    _, g = _parse_function(g_expr)
    xi = float(x0)
    iterations = []
    converged = False

    for n in range(1, max_iter + 1):
        g_xi = float(g(xi))

        if not math.isfinite(g_xi) or abs(g_xi) > 1e10:
            raise RuntimeError(
                f"Fixed Point iteration diverged at n={n} (g(x) = {g_xi}).\n"
                "The iteration function g(x) does not converge. Try a different g(x)."
            )

        ea = _approximate_error(g_xi, xi)

        iterations.append({
            "n": n,
            "xi": _fmt(xi, decimal_places),
            "g_xi": _fmt(g_xi, decimal_places),
            "ea": _fmt(ea, decimal_places),
        })

        xi = g_xi

        if stop_by_epsilon and ea < epsilon:
            converged = True
            break

    if not converged and not stop_by_epsilon:
        converged = True

    return {
        "method": "Fixed Point",
        "f_expr": f_expr,
        "g_expr": g_expr,
        "iterations": iterations,
        "root": _fmt(xi, decimal_places),
        "final_error": iterations[-1]["ea"] if iterations else float("inf"),
        "converged": converged,
        "iterations_count": len(iterations),
    }
