"""Batch processing endpoint.

Accepts a CSV file with ``We`` and ``Oh`` columns (first row = header),
applies the same SL-theory input validation and ``predBeta`` model used by
``/regime`` for each row, and returns a CSV with ``beta`` filled in as the
third column.

No new runtime dependencies - uses Python stdlib ``csv`` only.
"""

import csv
import io
from pathlib import Path

from flask import Blueprint, request, jsonify, Response

from SLtheory_prediction import load_model_payload, predict_beta_from_payload
from theory_ranges import validate_theory_inputs

batch_bp = Blueprint("batch", __name__)
_MODEL_PAYLOAD = load_model_payload(
    Path(__file__).resolve().with_name("SLtheory_model.json")
)
MAX_BATCH_UPLOAD_BYTES = 1024 * 1024


def _format_row_error(line_num, message, we_raw, oh_raw):
    return f"row {line_num}: {message} (We={we_raw!r}, Oh={oh_raw!r})"


@batch_bp.route("/batch", methods=["POST"])
def batch_process():
    """Process a CSV of (We, Oh) pairs and return a CSV with beta filled in."""
    if "file" not in request.files:
        return jsonify({"error": "No file attached. Expected multipart field 'file'."}), 400

    uploaded = request.files["file"]
    filename = uploaded.filename or ""
    if not filename.lower().endswith(".csv"):
        return jsonify({"error": "File must be a .csv"}), 400

    try:
        raw = uploaded.read().decode("utf-8-sig")  # strip BOM if present
    except UnicodeDecodeError:
        return jsonify({"error": "Could not decode file as UTF-8."}), 400

    reader = csv.DictReader(io.StringIO(raw))
    fieldnames = reader.fieldnames

    if not fieldnames or "We" not in fieldnames or "Oh" not in fieldnames:
        return jsonify(
            {"error": "CSV must have 'We' and 'Oh' columns in the first (header) row."}
        ), 400

    # Build output column order: We, Oh, beta, then any remaining columns
    remaining = [col for col in fieldnames if col not in ("We", "Oh", "beta")]
    out_fieldnames = ["We", "Oh", "beta"] + remaining

    out_rows = []
    row_errors = []

    for line_num, row in enumerate(reader, start=2):
        we_raw = row.get("We", "")
        oh_raw = row.get("Oh", "")
        validation_error = None
        try:
            we = float(we_raw)
            oh = float(oh_raw)
            validation_error = validate_theory_inputs(we, oh)
            if validation_error is not None:
                raise ValueError(validation_error)
            pred_beta = predict_beta_from_payload(_MODEL_PAYLOAD, oh=oh, we=we)
            row["beta"] = f"{pred_beta:.6f}"
        except (ValueError, TypeError):
            message = (
                validation_error if validation_error is not None else "Invalid We/Oh inputs"
            )
            row_errors.append(_format_row_error(line_num, message, we_raw, oh_raw))
            row["beta"] = "error"

        out_rows.append(row)

    if not out_rows:
        return jsonify({"error": "CSV contained no data rows."}), 400

    # Build response CSV
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=out_fieldnames, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(out_rows)

    csv_bytes = buf.getvalue().encode("utf-8")

    response = Response(csv_bytes, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=SLtheory_results.csv"
    if row_errors:
        # Surface parse errors as a custom header (non-fatal)
        response.headers["X-Row-Errors"] = "; ".join(row_errors[:10])
    return response
