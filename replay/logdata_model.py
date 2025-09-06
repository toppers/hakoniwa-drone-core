import os
import json
import math
import argparse
from typing import List, Dict, Optional

import numpy as np
import pandas as pd

REQUIRED_FIELDS = ["timestamp", "X", "Y", "Z", "Rx", "Ry", "Rz"]


class LogDataModel:
    """
    - 入力: NED座標系の drone_dynamics.csv
    - 出力: ROS座標系に変換済みの辞書列の配列（timestampはusec）
    - バリデーション:
        * 必須列の有無
        * NaN/inf 行の除去
        * 末尾壊れ行の除去（1行）
        * timestamp 単調増加の担保（非増加行の除去）
        * ステップ統計（メディアン等）
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.data_ros: List[Dict] = []

        # 統計
        self.start_ts: Optional[int] = None
        self.end_ts: Optional[int] = None
        self.duration_usec: Optional[int] = None
        self.median_step_usec: Optional[int] = None

        # レポート
        self.validation_report: Dict[str, object] = {}

        self._load_validate_convert()

    # ---------- public API ----------
    def get_data(self) -> List[Dict]:
        return self.data_ros

    def get_delay_median_usec(self) -> Optional[int]:
        return self.median_step_usec

    def get_report(self) -> Dict[str, object]:
        return self.validation_report

    # ---------- pipeline ----------
    def _load_validate_convert(self):
        df = self._read_csv(self.csv_path)
        original_rows = len(df)

        # 末尾壊れ対策: 最後の1行を落とす（0/1行はそのまま）
        if len(df) > 1:
            df = df.iloc[:-1]
        dropped_tail = original_rows - len(df)

        # 必須列チェック
        missing = [c for c in REQUIRED_FIELDS if c not in df.columns]
        if missing:
            raise ValueError(f"CSV missing required fields: {missing}")

        # NaN/inf 除去
        before = len(df)
        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=REQUIRED_FIELDS)
        dropped_nan_inf = before - len(df)

        # timestamp を int64 に
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").astype("Int64")
        before = len(df)
        df = df.dropna(subset=["timestamp"])
        df["timestamp"] = df["timestamp"].astype(np.int64)
        dropped_bad_ts = before - len(df)

        # 単調増加担保（非増加行を除去）
        before = len(df)
        if len(df) >= 2:
            mono_mask = df["timestamp"].diff().fillna(1) > 0
            df = df[mono_mask]
        dropped_non_increasing = before - len(df)

        # ステップ統計（情報用）
        step_stats = {}
        if len(df) >= 3:
            steps = df["timestamp"].diff().iloc[1:]
            med = float(steps.median())
            mean = float(steps.mean())
            std = float(steps.std(ddof=1)) if len(steps) > 1 else 0.0
            step_stats = {
                "count": int(steps.shape[0]),
                "median_usec": int(med) if not math.isnan(med) else None,
                "mean_usec": mean if not math.isnan(mean) else None,
                "std_usec": std if not math.isnan(std) else None,
                "max_usec": int(steps.max()) if steps.size else None,
                "min_usec": int(steps.min()) if steps.size else None,
            }
            self.median_step_usec = int(med) if not math.isnan(med) else None
        elif len(df) == 2:
            step = int(df["timestamp"].iloc[1] - df["timestamp"].iloc[0])
            step_stats = {"count": 1, "median_usec": step, "mean_usec": step, "std_usec": 0,
                          "max_usec": step, "min_usec": step}
            self.median_step_usec = step
        else:
            self.median_step_usec = None

        # NED -> ROS 変換（ベクトル化）
        df_ros = df.copy()
        df_ros["X"] = df_ros["X"].astype(float)
        df_ros["Y"] = (-df_ros["Y"]).astype(float)
        df_ros["Z"] = (-df_ros["Z"]).astype(float)
        df_ros["Rx"] = df_ros["Rx"].astype(float)
        df_ros["Ry"] = (-df_ros["Ry"]).astype(float)
        df_ros["Rz"] = (-df_ros["Rz"]).astype(float)

        # 統計
        if len(df_ros) >= 1:
            self.start_ts = int(df_ros["timestamp"].iloc[0])
            self.end_ts = int(df_ros["timestamp"].iloc[-1])
            self.duration_usec = int(self.end_ts - self.start_ts)

        # メモリへ
        self.data_ros = [
            {
                "timestamp": int(r.timestamp),
                "X": float(r.X), "Y": float(r.Y), "Z": float(r.Z),
                "Rx": float(r.Rx), "Ry": float(r.Ry), "Rz": float(r.Rz),
            }
            for r in df_ros.itertuples(index=False)
        ]

        self.validation_report = {
            "source": os.path.abspath(self.csv_path),
            "rows_original": int(original_rows),
            "dropped_tail_rows": int(dropped_tail),
            "dropped_nan_inf_rows": int(dropped_nan_inf),
            "dropped_bad_timestamp_rows": int(dropped_bad_ts),
            "dropped_non_increasing_rows": int(dropped_non_increasing),
            "rows_final": int(len(self.data_ros)),
            "timestamp": {
                "start_usec": self.start_ts,
                "end_usec": self.end_ts,
                "duration_usec": self.duration_usec,
                "step_stats": step_stats,
            },
        }

    @staticmethod
    def _read_csv(csv_path: str) -> pd.DataFrame:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV not found: {csv_path}")
        return pd.read_csv(
            csv_path,
            usecols=REQUIRED_FIELDS,
            dtype={
                "timestamp": "int64",
                "X": "float64", "Y": "float64", "Z": "float64",
                "Rx": "float64", "Ry": "float64", "Rz": "float64",
            },
            engine="c",
            memory_map=True,
        )


def find_dynamics_csv(log_dir: str) -> str:
    candidate = os.path.join(log_dir, "drone_dynamics.csv")
    if not os.path.exists(candidate):
        raise FileNotFoundError(f"drone_dynamics.csv not found under: {log_dir}")
    return candidate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogDataModel loader & validator")
    parser.add_argument("path", help="Path to drone_dynamics.csv or its parent directory (drone_logX)")
    parser.add_argument("--head", type=int, default=5, help="How many rows to preview (default: 5)")
    args = parser.parse_args()

    target = args.path
    if os.path.isdir(target):
        target = find_dynamics_csv(target)

    model = LogDataModel(target)
    data = model.get_data()
    report = model.get_report()

    print("=== Validation Report ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    print("\n=== Summary ===")
    print(f"rows_final={len(data)}")
    print(f"start_ts={model.start_ts}  end_ts={model.end_ts}  duration_usec={model.duration_usec}")
    print(f"median_step_usec={model.get_delay_median_usec()}")

    print(f"\n=== First {min(args.head, len(data))} rows (ROS coords) ===")
    for row in data[: args.head]:
        print(row)
