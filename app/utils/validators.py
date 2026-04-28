"""Input validation helpers for both non-linear and linear solvers."""
import numpy as np
import sympy as sp


def validate_function(expr_str: str) -> tuple[bool, str]:
    """Validate a mathematical expression string f(x)."""
    if not expr_str or not expr_str.strip():
        return False, "Function f(x) cannot be empty."
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(expr_str.strip(), locals={"x": x, "e": sp.E, "pi": sp.pi})
    except (sp.SympifyError, TypeError) as exc:
        return False, f"Invalid expression: {exc}"
    try:
        f = sp.lambdify(x, expr, modules=["numpy", "math"])
        _ = float(f(1.0))
    except ZeroDivisionError:
        pass  # Division by zero at x=1 is OK; the function may still be valid
    except Exception as exc:
        return False, f"Expression evaluation error at x=1: {exc}"
    return True, ""


def validate_gx(gx_expr: str) -> tuple[bool, str]:
    """Validate the g(x) iteration function for Fixed Point method."""
    if not gx_expr or not gx_expr.strip():
        return False, "g(x) function cannot be empty."
    return validate_function(gx_expr)


def validate_interval(f_expr: str, xl: float, xu: float) -> tuple[bool, str]:
    """Check xl < xu and sign change for bracket methods."""
    if xl >= xu:
        return False, f"xl ({xl}) must be strictly less than xu ({xu})."
    x = sp.Symbol("x")
    try:
        expr = sp.sympify(f_expr.strip(), locals={"x": x, "e": sp.E, "pi": sp.pi})
        f = sp.lambdify(x, expr, modules=["numpy", "math"])
        f_xl = float(f(xl))
        f_xu = float(f(xu))
    except Exception as exc:
        return False, f"Cannot evaluate f at interval boundaries: {exc}"
    if f_xl * f_xu > 0:
        return False, (
            f"No sign change detected between xl={xl} and xu={xu}.\n"
            f"f({xl}) = {f_xl:.6f} and f({xu}) = {f_xu:.6f} have the same sign.\n"
            "Choose an interval where the function changes sign."
        )
    return True, ""


def validate_numeric_field(
    value: str,
    name: str,
    positive: bool = False,
    nonzero: bool = False,
) -> tuple[bool, str]:
    """Validate a string that should be a float."""
    if not value or not value.strip():
        return False, f"{name} cannot be empty."
    try:
        v = float(value.strip())
    except ValueError:
        return False, f"{name} must be a valid number."
    if positive and v < 0:
        return False, f"{name} must be non-negative."
    if nonzero and v == 0:
        return False, f"{name} must not be zero."
    return True, ""


def validate_nonlinear_inputs(
    method: str,
    f_expr: str,
    params: dict,
) -> tuple[bool, str]:
    """Unified validator for non-linear solver inputs."""
    ok, msg = validate_function(f_expr)
    if not ok:
        return False, msg

    if method in ("Bisection", "False Position"):
        for field in ("xl", "xu"):
            ok, msg = validate_numeric_field(str(params.get(field, "")), field)
            if not ok:
                return False, msg
        xl = float(params["xl"])
        xu = float(params["xu"])
        ok, msg = validate_interval(f_expr, xl, xu)
        if not ok:
            return False, msg

    elif method == "Newton-Raphson":
        ok, msg = validate_numeric_field(str(params.get("x0", "")), "Initial guess x0")
        if not ok:
            return False, msg

    elif method == "Secant":
        for field, name in (("x0", "Initial point x0"), ("x1", "Initial point x1")):
            ok, msg = validate_numeric_field(str(params.get(field, "")), name)
            if not ok:
                return False, msg
        if float(params["x0"]) == float(params["x1"]):
            return False, "x0 and x1 must be different values."

    elif method == "Fixed Point":
        ok, msg = validate_numeric_field(str(params.get("x0", "")), "Initial guess x0")
        if not ok:
            return False, msg
        ok, msg = validate_gx(str(params.get("g_expr", "")))
        if not ok:
            return False, msg

    ok, msg = validate_numeric_field(str(params.get("epsilon", "")), "Epsilon", positive=True)
    if not ok:
        return False, msg

    ok, msg = validate_numeric_field(str(params.get("max_iter", "")), "Max iterations", positive=True)
    if not ok:
        return False, msg

    return True, ""


def validate_matrix(
    A_values: list[list[str]],
    b_values: list[str],
) -> tuple[bool, str]:
    """Convert string entries to floats and check for singularity."""
    n = len(A_values)
    A = []
    errors = []
    for i, row in enumerate(A_values):
        float_row = []
        for j, val in enumerate(row):
            if not val or not val.strip():
                errors.append(f"A[{i+1},{j+1}] is empty.")
                float_row.append(0.0)
                continue
            try:
                float_row.append(float(val.strip()))
            except ValueError:
                errors.append(f"A[{i+1},{j+1}] = '{val}' is not a valid number.")
                float_row.append(0.0)
        A.append(float_row)

    b = []
    for i, val in enumerate(b_values):
        if not val or not val.strip():
            errors.append(f"b[{i+1}] is empty.")
            b.append(0.0)
            continue
        try:
            b.append(float(val.strip()))
        except ValueError:
            errors.append(f"b[{i+1}] = '{val}' is not a valid number.")
            b.append(0.0)

    if errors:
        return False, "\n".join(errors)

    try:
        det = float(np.linalg.det(np.array(A, dtype=float)))
        if abs(det) < 1e-12:
            return False, (
                f"The matrix is singular (det ≈ {det:.2e}).\n"
                "The system has no unique solution."
            )
    except Exception as exc:
        return False, f"Matrix validation error: {exc}"

    return True, ""
