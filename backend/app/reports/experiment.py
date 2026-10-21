from __future__ import annotations

import csv
import html
import io
import json

from app.schemas.experiments import ExperimentResponse


def csv_bytes(data: ExperimentResponse) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["experiment_id", "name", "hypothesis", "kind", "variant", "label",
                     "mean_bb_per_hand", "ci95", "sd_bb_per_hand",
                     "average_max_drawdown", "biggest_win", "observations"])
    for item in data.results:
        writer.writerow([data.id, data.name, data.hypothesis, data.kind, data.variant,
                         item.label, item.mean_bb_per_hand, item.ci95, item.sd_bb_per_hand,
                         item.average_max_drawdown, item.biggest_win, item.observations])
    return output.getvalue().encode("utf-8")


def parquet_bytes(data: ExperimentResponse) -> bytes:
    import pandas as pd

    rows = [{
        "experiment_id": data.id,
        "name": data.name,
        "hypothesis": data.hypothesis,
        "kind": data.kind,
        "variant": data.variant,
        **item.model_dump(),
    } for item in data.results]
    output = io.BytesIO()
    pd.DataFrame(rows).to_parquet(output, index=False)
    return output.getvalue()


def html_report(data: ExperimentResponse) -> str:
    rows = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(value))}</td>" for value in (
            item.label, f"{item.mean_bb_per_hand:.4f}",
            "n/a" if item.ci95 is None else f"{item.ci95:.4f}",
            "n/a" if item.sd_bb_per_hand is None else f"{item.sd_bb_per_hand:.4f}",
            f"{item.average_max_drawdown:.2f}", f"{item.biggest_win:.2f}",
        )) + "</tr>"
        for item in data.results
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(data.name)}</title>
<style>body{{font:16px system-ui;background:#171b19;color:#e8eee9;max-width:1000px;margin:40px auto;padding:0 20px}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #405148;padding:8px;text-align:left}}
th{{background:#254a39}}.muted{{color:#aab7af}}</style></head>
<body><h1>{html.escape(data.name)}</h1>
<p class="muted">{html.escape(data.hypothesis or "No hypothesis supplied.")}</p>
<p>Experiment {data.id} · Type {html.escape(data.kind)} · Variant {html.escape(data.variant)}
 · {data.trials} trials × {data.hands} hands · Seeds: {", ".join(map(str, data.seeds))}</p>
<table><thead><tr><th>Condition</th><th>Mean BB/hand</th><th>95% CI</th>
<th>SD/hand</th><th>Avg max drawdown</th><th>Biggest win</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="muted">Virtual-chip realized observations; confidence intervals describe
trial variability and do not establish causal effects.</p></body></html>"""


def pdf_bytes(data: ExperimentResponse) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

    output = io.BytesIO()
    document = SimpleDocTemplate(output, pagesize=letter, rightMargin=0.5 * inch,
                                 leftMargin=0.5 * inch, topMargin=0.5 * inch,
                                 bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(html.escape(data.name), styles["Title"]),
        Paragraph(html.escape(data.hypothesis or "No hypothesis supplied."), styles["BodyText"]),
        Spacer(1, 12),
        Paragraph(
            f"Experiment {data.id} | Type {html.escape(data.kind)} | "
            f"Variant {html.escape(data.variant)} | {data.trials} trials x {data.hands} hands",
            styles["BodyText"],
        ),
        Spacer(1, 12),
    ]
    rows = [["Condition", "Mean BB/hand", "95% CI", "SD/hand", "Drawdown", "Biggest win"]]
    rows.extend([
        [
            item.label,
            f"{item.mean_bb_per_hand:.4f}",
            "n/a" if item.ci95 is None else f"{item.ci95:.4f}",
            "n/a" if item.sd_bb_per_hand is None else f"{item.sd_bb_per_hand:.4f}",
            f"{item.average_max_drawdown:.2f}",
            f"{item.biggest_win:.2f}",
        ]
        for item in data.results
    ])
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#254a39")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#405148")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 12), Paragraph(
        "Virtual-chip realized observations; confidence intervals describe trial variability "
        "and do not establish causal effects.",
        styles["BodyText"],
    )])
    document.build(story)
    return output.getvalue()
