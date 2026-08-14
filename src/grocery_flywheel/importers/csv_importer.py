from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from typing import Any

from .normalized import import_normalized_history


def import_csv_history(path: Path, *, profile_id: str | None = None) -> dict[str, Any]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("CSV import has no rows")

    first = rows[0]
    payload = {
        "source": "csv_export",
        "as_of": date.today().isoformat(),
        "order": {
            "store": first.get("store") or "CSV retailer",
            "date": first.get("order_date") or first.get("date") or date.today().isoformat(),
        },
        "items": [
            {
                "name": row.get("name") or row.get("item") or "",
                "quantity": row.get("quantity") or 1,
                "size": row.get("size") or row.get("size_raw") or "",
                "spend": row.get("spend") or row.get("total_price") or row.get("price") or 0,
                "category": row.get("category") or "unknown",
                "role": row.get("role") or "",
                "notes": row.get("notes") or "",
                "source_row_id": row.get("id") or row.get("line_id") or "",
            }
            for row in rows
            if row.get("name") or row.get("item")
        ],
    }
    return import_normalized_history(payload, profile_id=profile_id)
