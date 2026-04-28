# Numerical Analysis Calculator

A complete, professional Python desktop application for solving numerical analysis problems with precision and efficiency.

## Overview

The Numerical Analysis Calculator is an open-source, Python-based software solution designed to solve numerical analysis problems. It is built for students, educators, engineers, and researchers who need reliable and visual numerical computation tools.

## Features

- **Modern Professional GUI** — Clean light/dark academic theme with CustomTkinter
- **Non-Linear Equation Solvers** — 5 methods with iteration tables and graphs
- **Linear System Solvers** — 4 methods with step-by-step solutions
- **Interactive Graph Visualization** — Embedded Matplotlib plots with root markers
- **PDF Export** — Professional reports with tables and figures via ReportLab
- **Persistent Solution History** — Auto-saved records in JSON format
- **Professional Settings Page** — Customize themes, defaults, and export options
- **About Page** — Project and library information

## Numerical Methods

### Non-Linear Equations
| Method | Description |
|---|---|
| Bisection | Bracket method using midpoint bisection |
| False Position | Bracket method using linear interpolation |
| Fixed Point Iteration | Iterative g(x) convergence |
| Newton-Raphson | Tangent line method using symbolic derivative |
| Secant | Two-point approximation without derivative |

### Linear Systems
| Method | Description |
|---|---|
| Gauss Elimination | Forward elimination with partial pivoting + back substitution |
| LU Decomposition | Doolittle factorization (L and U matrices) |
| Gauss-Jordan | Full RREF reduction |
| Cramer's Rule | Determinant-based solution |

## Installation

1. **Clone or download** this repository.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Requirements

- Python 3.10 or higher
- See `requirements.txt` for library versions

## Project Structure

```
numerical_analysis_calculator/
├── main.py                  # Application entry point
├── requirements.txt
├── README.md
├── app/
│   ├── gui/                 # All GUI pages and components
│   ├── methods/             # Pure numerical computation
│   ├── services/            # PDF export, history, settings
│   └── utils/               # Validators and plotting helpers
└── data/
    ├── history.json         # Persistent calculation history
    └── settings.json        # User preferences
```

## Libraries Used

| Library | Role |
|---|---|
| CustomTkinter | Modern themed GUI widgets |
| NumPy | Matrix operations and array math |
| SymPy | Safe expression parsing and symbolic differentiation |
| SciPy | Scientific utilities |
| Matplotlib | Embedded interactive graphs |
| ReportLab | PDF report generation |
| Pillow | Image processing for PDF figures |

## Future Improvements

- Additional non-linear methods (Müller, Brent)
- Matrix condition number analysis
- Polynomial root finder
- Export to Excel/CSV
- Multi-language support
- Dark/Light theme presets

## License

Open-source for academic and educational purposes.
