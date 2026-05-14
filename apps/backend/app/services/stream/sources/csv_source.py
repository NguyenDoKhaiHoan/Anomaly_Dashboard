from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for p in [current, *current.parents]:
        if (p / "data").exists() and (p / "apps").exists():
            return p
    raise RuntimeError("Không tìm thấy PROJECT_ROOT")


class CSVRowSource:
    def __init__(self, csv_path: str | Path, base_dir: str | Path | None = None):
        raw_path = Path(csv_path)

        if base_dir is None:
            self.base_dir = find_project_root(Path(__file__).resolve())
        else:
            self.base_dir = Path(base_dir).resolve()

        if raw_path.is_absolute():
            self.csv_path = raw_path.resolve()
        else:
            self.csv_path = (self.base_dir / raw_path).resolve()

        print(f"[CSV] cwd={Path.cwd()}", flush=True)
        print(f"[CSV] base_dir={self.base_dir}", flush=True)
        print(f"[CSV] raw_path={raw_path}", flush=True)
        print(f"[CSV] resolved={self.csv_path}", flush=True)
        print(f"[CSV] exists={self.csv_path.exists()}", flush=True)

        self._rows: list[dict[str, Any]] = []
        self._index = 0
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Không tìm thấy CSV: {self.csv_path}")

        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            print(f"[CSV] fieldnames={reader.fieldnames}", flush=True)
            self._rows = [dict(row) for row in reader]

        print(f"[CSV] rows={len(self._rows)}", flush=True)

        if not self._rows:
            raise ValueError(f"CSV không có dòng dữ liệu: {self.csv_path}")

    def has_data(self) -> bool:
        return bool(self._rows)

    def next_row(self) -> dict[str, Any]:
        if not self._rows:
            raise RuntimeError(f"CSV source không có dữ liệu: {self.csv_path}")

        row = self._rows[self._index]
        self._index = (self._index + 1) % len(self._rows)
        return row

    def next(self) -> dict[str, Any]:
        return self.next_row()

    def __next__(self) -> dict[str, Any]:
        return self.next_row()

    def reset(self) -> None:
        self._index = 0

    def __len__(self) -> int:
        return len(self._rows)