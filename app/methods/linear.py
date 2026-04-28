"""Linear system solvers: Gauss Elimination, LU Decomposition,
Gauss-Jordan, Cramer's Rule.

All functions accept Python list-of-lists for A and list for b.
They return step-by-step data for GUI display.
"""
import copy
import numpy as np


def _to_float_array(A: list, b: list):
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float)
    return A_arr, b_arr


def _matrix_str(M: np.ndarray, label: str = "", dp: int = 6) -> str:
    lines = []
    if label:
        lines.append(label)
    for row in M:
        formatted = "  ".join(f"{v:>{dp+6}.{dp}f}" for v in row)
        lines.append(f"  [ {formatted} ]")
    return "\n".join(lines)


def _aug_str(Ab: np.ndarray, dp: int = 6) -> str:
    n = Ab.shape[0]
    lines = []
    for i in range(n):
        row_vals = "  ".join(f"{Ab[i, j]:>{dp+5}.{dp}f}" for j in range(n))
        b_val = f"{Ab[i, n]:>{dp+5}.{dp}f}"
        lines.append(f"  [ {row_vals}  |  {b_val} ]")
    return "\n".join(lines)


def _check_singular(A: np.ndarray):
    det = np.linalg.det(A)
    if abs(det) < 1e-12:
        raise ValueError(
            f"The matrix is singular (det ≈ {det:.2e}).\n"
            "The system has no unique solution."
        )


def solve_gauss_elimination(A: list, b: list, decimal_places: int = 6) -> dict:
    A_arr, b_arr = _to_float_array(A, b)
    _check_singular(A_arr)
    n = len(b)
    Ab = np.hstack([A_arr, b_arr.reshape(-1, 1)])
    steps = []
    aug_snapshots = []

    steps.append("=== Gauss Elimination with Partial Pivoting ===\n")
    steps.append("Augmented matrix [A|b]:\n" + _aug_str(Ab, decimal_places))
    aug_snapshots.append(Ab.copy())

    for k in range(n):
        # Partial pivot
        max_row = k + int(np.argmax(np.abs(Ab[k:, k])))
        if max_row != k:
            Ab[[k, max_row]] = Ab[[max_row, k]]
            steps.append(f"\nSwap row {k+1} ↔ row {max_row+1}")
            steps.append(_aug_str(Ab, decimal_places))
            aug_snapshots.append(Ab.copy())

        pivot = Ab[k, k]
        if abs(pivot) < 1e-14:
            raise ValueError(f"Zero pivot encountered at row {k+1}.")

        for i in range(k + 1, n):
            factor = Ab[i, k] / pivot
            Ab[i] = Ab[i] - factor * Ab[k]
            steps.append(f"\nR{i+1} = R{i+1} - ({factor:.{decimal_places}f}) × R{k+1}")
            steps.append(_aug_str(Ab, decimal_places))
            aug_snapshots.append(Ab.copy())

    steps.append("\n=== Back Substitution ===")
    solution = np.zeros(n)
    for i in range(n - 1, -1, -1):
        solution[i] = (Ab[i, n] - np.dot(Ab[i, i+1:n], solution[i+1:n])) / Ab[i, i]
        steps.append(f"x{i+1} = {solution[i]:.{decimal_places}f}")

    return {
        "method": "Gauss Elimination",
        "steps": steps,
        "solution": [round(float(v), decimal_places) for v in solution],
        "extra": {"augmented_matrices": [m.tolist() for m in aug_snapshots]},
        "size": n,
    }


def solve_lu_decomposition(A: list, b: list, decimal_places: int = 6) -> dict:
    A_arr, b_arr = _to_float_array(A, b)
    _check_singular(A_arr)
    n = len(b)
    steps = []

    L = np.eye(n, dtype=float)
    U = A_arr.copy()

    steps.append("=== LU Decomposition (Doolittle) ===\n")

    for k in range(n):
        if abs(U[k, k]) < 1e-14:
            raise ValueError(f"Zero pivot at position ({k+1},{k+1}). Cannot perform LU decomposition.")
        for i in range(k + 1, n):
            factor = U[i, k] / U[k, k]
            L[i, k] = factor
            U[i] = U[i] - factor * U[k]
            steps.append(f"L[{i+1},{k+1}] = {factor:.{decimal_places}f}  →  "
                         f"R{i+1} = R{i+1} - ({factor:.{decimal_places}f}) × R{k+1}")

    steps.append("\nL matrix:\n" + _matrix_str(L, dp=decimal_places))
    steps.append("\nU matrix:\n" + _matrix_str(U, dp=decimal_places))

    # Forward substitution: Ly = b
    steps.append("\n=== Forward Substitution: Ly = b ===")
    y = np.zeros(n)
    for i in range(n):
        y[i] = (b_arr[i] - np.dot(L[i, :i], y[:i])) / L[i, i]
        steps.append(f"y{i+1} = {y[i]:.{decimal_places}f}")

    # Back substitution: Ux = y
    steps.append("\n=== Back Substitution: Ux = y ===")
    solution = np.zeros(n)
    for i in range(n - 1, -1, -1):
        solution[i] = (y[i] - np.dot(U[i, i+1:], solution[i+1:])) / U[i, i]
        steps.append(f"x{i+1} = {solution[i]:.{decimal_places}f}")

    return {
        "method": "LU Decomposition",
        "steps": steps,
        "solution": [round(float(v), decimal_places) for v in solution],
        "extra": {
            "L": [[round(float(v), decimal_places) for v in row] for row in L],
            "U": [[round(float(v), decimal_places) for v in row] for row in U],
        },
        "size": n,
    }


def solve_gauss_jordan(A: list, b: list, decimal_places: int = 6) -> dict:
    A_arr, b_arr = _to_float_array(A, b)
    _check_singular(A_arr)
    n = len(b)
    Ab = np.hstack([A_arr, b_arr.reshape(-1, 1)])
    steps = []

    steps.append("=== Gauss-Jordan Elimination ===\n")
    steps.append("Augmented matrix [A|b]:\n" + _aug_str(Ab, decimal_places))

    for k in range(n):
        # Partial pivot
        max_row = k + int(np.argmax(np.abs(Ab[k:, k])))
        if max_row != k:
            Ab[[k, max_row]] = Ab[[max_row, k]]
            steps.append(f"\nSwap row {k+1} ↔ row {max_row+1}")

        pivot = Ab[k, k]
        if abs(pivot) < 1e-14:
            raise ValueError(f"Zero pivot at row {k+1}.")

        # Normalize pivot row
        Ab[k] = Ab[k] / pivot
        steps.append(f"\nR{k+1} = R{k+1} / {pivot:.{decimal_places}f}")
        steps.append(_aug_str(Ab, decimal_places))

        for i in range(n):
            if i != k:
                factor = Ab[i, k]
                Ab[i] = Ab[i] - factor * Ab[k]
                steps.append(f"\nR{i+1} = R{i+1} - ({factor:.{decimal_places}f}) × R{k+1}")
                steps.append(_aug_str(Ab, decimal_places))

    solution = Ab[:, n]
    return {
        "method": "Gauss-Jordan",
        "steps": steps,
        "solution": [round(float(v), decimal_places) for v in solution],
        "extra": {},
        "size": n,
    }


def solve_cramers_rule(A: list, b: list, decimal_places: int = 6) -> dict:
    A_arr, b_arr = _to_float_array(A, b)
    n = len(b)
    det_A = float(np.linalg.det(A_arr))

    if abs(det_A) < 1e-12:
        raise ValueError(
            f"det(A) ≈ {det_A:.2e} — the matrix is singular.\n"
            "Cramer's Rule requires a non-singular matrix."
        )

    steps = []
    steps.append("=== Cramer's Rule ===\n")
    steps.append(f"det(A) = {det_A:.{decimal_places}f}")

    solution = []
    det_Ai_list = []

    for i in range(n):
        Ai = A_arr.copy()
        Ai[:, i] = b_arr
        det_Ai = float(np.linalg.det(Ai))
        xi = det_Ai / det_A
        solution.append(xi)
        det_Ai_list.append(det_Ai)
        steps.append(f"det(A{i+1}) = {det_Ai:.{decimal_places}f}")
        steps.append(f"x{i+1} = det(A{i+1}) / det(A) = {det_Ai:.{decimal_places}f} / {det_A:.{decimal_places}f} = {xi:.{decimal_places}f}")

    return {
        "method": "Cramer's Rule",
        "steps": steps,
        "solution": [round(float(v), decimal_places) for v in solution],
        "extra": {
            "det_A": round(det_A, decimal_places),
            "det_Ai": [round(float(d), decimal_places) for d in det_Ai_list],
        },
        "size": n,
    }
