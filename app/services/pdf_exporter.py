import io
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, Image, HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def _check_available():
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "ReportLab is required for PDF export.\n"
            "Install it with:  pip install reportlab"
        )


def _get_pagesize(size_name: str):
    return letter if size_name.upper() == "LETTER" else A4


def _create_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AppTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4,
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_style,
        "body": body_style,
    }


def _fig_to_image(fig, width_cm: float = 15, height_cm: float = 9):
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return Image(buf, width=width_cm * cm, height=height_cm * cm)


def _build_data_table(rows: list[list], header_color=None):
    if header_color is None:
        header_color = colors.HexColor("#2563EB")

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ])
    tbl = Table(rows, repeatRows=1, style=style)
    return tbl


def _header_story(styles, title: str, method: str, problem_type: str,
                  include_datetime: bool) -> list:
    story = []
    story.append(Paragraph(title, styles["title"]))
    story.append(Paragraph(f"{problem_type}  |  Method: {method}", styles["subtitle"]))
    if include_datetime:
        now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        story.append(Paragraph(f"Generated: {now}", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#2563EB"), spaceAfter=10))
    return story


def export_nonlinear_pdf(
    filepath: str,
    data: dict,
    inputs: dict,
    fig=None,
    settings: dict = None,
) -> None:
    _check_available()
    if settings is None:
        settings = {}

    pagesize = _get_pagesize(settings.get("pdf_paper_size", "A4"))
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=pagesize,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _create_styles()
    story = []

    pdf_title = settings.get("custom_pdf_title", "Numerical Analysis Report")
    story += _header_story(
        styles, pdf_title,
        data.get("method", ""),
        "Non-Linear Equation",
        settings.get("include_datetime_in_pdf", True),
    )

    story.append(Paragraph("Input Parameters", styles["section"]))
    input_rows = [["Parameter", "Value"]]
    input_rows.append(["f(x)", str(inputs.get("f_expr", ""))])
    input_rows.append(["Method", str(data.get("method", ""))])
    for k, v in inputs.items():
        if k == "f_expr":
            continue
        input_rows.append([str(k).replace("_", " ").title(), str(v)])
    story.append(_build_data_table(input_rows, colors.HexColor("#1E40AF")))
    story.append(Spacer(1, 0.4 * cm))

    iterations = data.get("iterations", [])
    if iterations and settings.get("include_table_in_pdf", True):
        story.append(Paragraph("Iteration Table", styles["section"]))
        method = data.get("method", "")
        col_map = {
            "Bisection":       ["n", "xl", "f(xl)", "xu", "f(xu)", "xr", "f(xr)", "ea(%)"],
            "False Position":  ["n", "xl", "f(xl)", "xu", "f(xu)", "xr", "f(xr)", "ea(%)"],
            "Newton-Raphson":  ["n", "xi", "f(xi)", "f'(xi)", "xi+1", "ea(%)"],
            "Secant":          ["n", "xi-1", "xi", "f(xi-1)", "f(xi)", "xi+1", "ea(%)"],
            "Fixed Point":     ["n", "xi", "g(xi)", "ea(%)"],
        }
        col_keys = {
            "Bisection":       ["n", "xl", "f_xl", "xu", "f_xu", "xr", "f_xr", "ea"],
            "False Position":  ["n", "xl", "f_xl", "xu", "f_xu", "xr", "f_xr", "ea"],
            "Newton-Raphson":  ["n", "xi", "f_xi", "df_xi", "xi_next", "ea"],
            "Secant":          ["n", "xi_prev", "xi", "f_xi_prev", "f_xi", "xi_next", "ea"],
            "Fixed Point":     ["n", "xi", "g_xi", "ea"],
        }
        headers = col_map.get(method, list(iterations[0].keys()))
        keys = col_keys.get(method, list(iterations[0].keys()))
        table_data = [headers]
        for row in iterations:
            table_data.append([_fmt(row.get(k, "")) for k in keys])
        story.append(_build_data_table(table_data))
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Results Summary", styles["section"]))
    result_rows = [["Metric", "Value"]]
    result_rows.append(["Root (x)", _fmt(data.get("root", ""))])
    result_rows.append(["Iterations", str(data.get("iterations_count", ""))])
    result_rows.append(["Final Error (%)", _fmt(data.get("final_error", ""))])
    result_rows.append(["Converged", "Yes" if data.get("converged") else "No"])
    story.append(_build_data_table(result_rows, colors.HexColor("#059669")))
    story.append(Spacer(1, 0.4 * cm))

    if fig is not None and settings.get("include_graph_in_pdf", True):
        story.append(Paragraph("Function Graph", styles["section"]))
        try:
            img = _fig_to_image(fig)
            story.append(img)
        except Exception:
            pass

    doc.build(story)


def export_linear_pdf(
    filepath: str,
    data: dict,
    inputs: dict,
    settings: dict = None,
) -> None:
    _check_available()
    if settings is None:
        settings = {}

    pagesize = _get_pagesize(settings.get("pdf_paper_size", "A4"))
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=pagesize,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = _create_styles()
    story = []

    pdf_title = settings.get("custom_pdf_title", "Numerical Analysis Report")
    story += _header_story(
        styles, pdf_title,
        data.get("method", ""),
        "Linear System of Equations",
        settings.get("include_datetime_in_pdf", True),
    )

    story.append(Paragraph("Input Matrix", styles["section"]))
    A = inputs.get("A", [])
    b = inputs.get("b", [])
    n = len(A)
    if A and b:
        headers = [f"x{i+1}" for i in range(n)] + ["=", "b"]
        mat_data = [headers]
        for i in range(n):
            row = [_fmt(A[i][j]) for j in range(n)] + ["", _fmt(b[i])]
            mat_data.append(row)
        story.append(_build_data_table(mat_data, colors.HexColor("#7C3AED")))
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Solution", styles["section"]))
    solution = data.get("solution", [])
    sol_rows = [["Variable", "Value"]]
    for i, val in enumerate(solution):
        sol_rows.append([f"x{i+1}", _fmt(val)])
    story.append(_build_data_table(sol_rows, colors.HexColor("#059669")))
    story.append(Spacer(1, 0.4 * cm))

    steps = data.get("steps", [])
    if steps and settings.get("include_table_in_pdf", True):
        story.append(Paragraph("Step-by-Step Solution", styles["section"]))
        from reportlab.platypus import Preformatted
        from reportlab.lib.styles import ParagraphStyle as PS
        code_style = PS(
            "Code",
            fontName="Courier",
            fontSize=8,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
        )
        steps_text = "\n".join(steps)
        story.append(Paragraph(steps_text.replace("\n", "<br/>"), styles["body"]))

    extra = data.get("extra", {})
    if "L" in extra and "U" in extra:
        story.append(Paragraph("L and U Matrices", styles["section"]))
        L = extra["L"]
        U = extra["U"]
        size = len(L)
        l_headers = ["L"] + [f"col {j+1}" for j in range(size)]
        l_data = [l_headers]
        for i, row in enumerate(L):
            l_data.append([f"row {i+1}"] + [_fmt(v) for v in row])
        story.append(_build_data_table(l_data, colors.HexColor("#6D28D9")))
        story.append(Spacer(1, 0.3 * cm))
        u_headers = ["U"] + [f"col {j+1}" for j in range(size)]
        u_data = [u_headers]
        for i, row in enumerate(U):
            u_data.append([f"row {i+1}"] + [_fmt(v) for v in row])
        story.append(_build_data_table(u_data, colors.HexColor("#6D28D9")))

    if "det_A" in extra:
        story.append(Paragraph("Determinants (Cramer's Rule)", styles["section"]))
        det_rows = [["", "Value"]]
        det_rows.append(["det(A)", _fmt(extra["det_A"])])
        for i, d in enumerate(extra.get("det_Ai", [])):
            det_rows.append([f"det(A{i+1})", _fmt(d)])
        story.append(_build_data_table(det_rows, colors.HexColor("#7C3AED")))

    doc.build(story)


def _fmt(value) -> str:
    try:
        f = float(value)
        if f == int(f) and abs(f) < 1e10:
            return f"{f:.6f}"
        return f"{f:.6e}" if abs(f) > 1e6 or (abs(f) < 1e-4 and f != 0) else f"{f:.6f}"
    except (TypeError, ValueError):
        return str(value)
