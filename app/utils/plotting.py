"""Matplotlib figure creation helpers for non-linear solver visualization."""
import math
import numpy as np
import sympy as sp
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def _parse_f(expr_str: str):
    x = sp.Symbol("x")
    expr = sp.sympify(expr_str, locals={"x": x, "e": sp.E, "pi": sp.pi})
    return sp.lambdify(x, expr, modules=["numpy", "math"])


def _get_plot_range(
    root: float,
    xl: float | None,
    xu: float | None,
) -> tuple[float, float]:
    if xl is not None and xu is not None and xl < xu:
        margin = max((xu - xl) * 0.6, 0.5)
        return xl - margin, xu + margin
    if root is not None:
        return root - 3.0, root + 3.0
    return -5.0, 5.0


def create_nonlinear_figure(
    f_expr: str,
    root: float,
    xl: float | None = None,
    xu: float | None = None,
    method: str = "",
    title: str = "",
) -> plt.Figure:
    """Return a matplotlib Figure showing f(x), zero line, and root marker."""
    try:
        f = _parse_f(f_expr)
    except Exception:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "Cannot plot function", ha="center", va="center",
                transform=ax.transAxes, fontsize=12, color="red")
        return fig

    x_min, x_max = _get_plot_range(root, xl, xu)
    x_vals = np.linspace(x_min, x_max, 600)

    try:
        y_vals = np.array([float(f(xi)) for xi in x_vals], dtype=float)
    except Exception:
        y_vals = np.zeros_like(x_vals)

    # Mask discontinuities: large jumps indicate poles
    dy = np.abs(np.diff(y_vals))
    threshold = max(np.nanpercentile(dy, 95) * 20, 10)
    mask = np.concatenate([[False], dy > threshold])
    y_vals[mask] = np.nan

    # Clip remaining extreme values
    y_vals = np.clip(y_vals, -500, 500)

    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=100)
    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FFFFFF")

    ax.plot(x_vals, y_vals, color="#2563EB", linewidth=2.0, label="f(x)", zorder=2)
    ax.axhline(0, color="#374151", linewidth=0.8, linestyle="--", alpha=0.7, zorder=1)
    ax.axvline(0, color="#374151", linewidth=0.4, linestyle=":", alpha=0.4, zorder=1)

    if xl is not None and xu is not None:
        ax.axvspan(xl, xu, alpha=0.08, color="#2563EB", label="Bracket")

    if root is not None:
        try:
            y_root = float(f(root))
        except Exception:
            y_root = 0.0
        ax.plot(root, 0, "o", color="#DC2626", markersize=9, zorder=5,
                label=f"Root ≈ {root:.6f}", markeredgecolor="white", markeredgewidth=1.5)
        if abs(y_root) > 1e-10:
            ax.plot(root, y_root, "x", color="#F59E0B", markersize=8,
                    markeredgewidth=2, zorder=4)

    ax.set_xlabel("x", fontsize=11, color="#374151")
    ax.set_ylabel("f(x)", fontsize=11, color="#374151")
    plot_title = title or f"{method} — f(x) = {f_expr}"
    ax.set_title(plot_title, fontsize=11, color="#1E293B", pad=10)
    ax.legend(fontsize=9, loc="best", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
    ax.tick_params(colors="#374151", labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#CBD5E1")

    fig.tight_layout()
    return fig


def create_convergence_figure(errors: list, method: str = "") -> plt.Figure:
    """Return a semi-log Figure of approximate error vs iteration."""
    numeric_errors = []
    for e in errors:
        try:
            v = float(e)
            if math.isfinite(v) and v > 0:
                numeric_errors.append(v)
        except (TypeError, ValueError):
            pass

    fig, ax = plt.subplots(figsize=(5.5, 3.5), dpi=100)
    if len(numeric_errors) < 2:
        ax.text(0.5, 0.5, "Not enough data for convergence plot",
                ha="center", va="center", transform=ax.transAxes)
        return fig

    fig.patch.set_facecolor("#FAFAFA")
    ax.set_facecolor("#FFFFFF")
    iterations = list(range(1, len(numeric_errors) + 1))
    ax.semilogy(iterations, numeric_errors, "o-", color="#7C3AED",
                linewidth=2, markersize=5, label="ea (%)")
    ax.set_xlabel("Iteration", fontsize=10)
    ax.set_ylabel("Approximate Error (%)", fontsize=10)
    ax.set_title(f"Convergence — {method}", fontsize=10)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig
