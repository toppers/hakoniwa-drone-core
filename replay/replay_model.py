import json
import argparse
import re
import os
from typing import Dict, Any, Optional, List


class ReplayModel:
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.config: Dict[str, Any] = {}
        self.start_time_usec: Optional[int] = None
        self.range_begin_usec: Optional[int] = None
        self.range_end_usec: Optional[int] = None
        self._load()

    # ---------- load & parse ----------
    def _load(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        # start_time を usec に変換
        self.start_time_usec = self._time_to_usec(self.config.get("start_time"))

        # range_sec (秒指定) を優先的に評価
        range_sec_cfg = self.config.get("range_sec")
        if range_sec_cfg and self.start_time_usec is not None:
            begin_sec = range_sec_cfg.get("begin")
            end_sec = range_sec_cfg.get("end")
            if begin_sec is not None:
                self.range_begin_usec = self.start_time_usec + int(begin_sec * 1_000_000)
            if end_sec is not None:
                self.range_end_usec = self.start_time_usec + int(end_sec * 1_000_000)
        else:
            # range_sec がなければ、従来の range_timestamp (時刻指定) を評価
            range_cfg = self.config.get("range_timestamp", {})
            self.range_begin_usec = self._time_to_usec(range_cfg.get("begin"))
            self.range_end_usec = self._time_to_usec(range_cfg.get("end"))

    @staticmethod
    def _time_to_usec(timestr: Optional[str]) -> Optional[int]:
        """
        "HH:MM:SS.mmm" / "HH:MM:SS.mmmmmm" を usec に変換
        """
        if timestr is None:
            return None
        m = re.match(r"^(\d+):(\d+):(\d+)\.(\d{1,6})$", timestr)
        if not m:
            raise ValueError(f"Invalid time format: {timestr} (expected HH:MM:SS.mmm[mmm])")
        h, mi, s, sub = m.groups()
        sub_usec = int((sub + "000000")[:6])  # 右パディングで6桁に
        total = (
            int(h) * 3600 * 1_000_000
            + int(mi) * 60 * 1_000_000
            + int(s) * 1_000_000
            + sub_usec
        )
        return total

    def get_config(self) -> Dict[str, Any]:
        return self.config

    # ---------- adapter to runner spec ----------
    def to_spec(self) -> Dict[str, Any]:
        """
        現行の replay.json を元に、HakoAssetReplayer に渡せる spec を構築。
        - drones: [{name, log, pdu_name}]
        - pdu_def_file: pdu_def_file 
        - timing: begin/end/usec, start_usec, speed, slow_factor
        """
        cfg = self.config

        # 1) drones 配列に正規化（log_map の後方互換サポート）
        drones: List[Dict[str, Any]] = []
        log_map = cfg.get("log_map", {})
        if not isinstance(log_map, dict) or not log_map:
            raise ValueError("replay.json: 'log_map' must be a non-empty object")

        for log_dir, spec in log_map.items():
            if isinstance(spec, str):
                # 旧形式: "drone_log0": "Drone"
                drones.append({"name": spec, "log": log_dir, "pdu_name": "pos"})
            elif isinstance(spec, dict):
                # 新形式: "drone_log0": {"drone_name":"Drone","pdu_name":"pos"}
                drone_name = spec.get("drone_name") or spec.get("name")
                if not drone_name:
                    raise ValueError(f"log_map.{log_dir}: 'drone_name' is required in object form")
                pdu_name = spec.get("pdu_name", "pos")
                drones.append({"name": drone_name, "log": log_dir, "pdu_name": pdu_name})
            else:
                raise ValueError(f"log_map.{log_dir}: unsupported mapping type {type(spec)}")

        # 2) pdu_def_file 
        pdu_def_file = cfg.get("pdu_def_file")
        if not pdu_def_file:
            raise ValueError("replay.json: 'pdu_def_file' is required")
        self.pdu_def_file = pdu_def_file

        # 3) speed -> slow_factor へ（内部は“遅くする倍率”）
        speed = float(cfg.get("speed", 1.0))
        if speed <= 0:
            raise ValueError("replay.json: 'speed' must be > 0")
        slow_factor = 1.0 / speed

        return {
            "drones": drones,
            "pdu_def_file": self.pdu_def_file,
            "timing": {
                "start_usec": self.start_time_usec,
                "range_begin_usec": self.range_begin_usec,
                "range_end_usec": self.range_end_usec,
                "speed": speed,
                "slow_factor": slow_factor,
            },
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReplayModel loader & spec generator")
    parser.add_argument("json_file", help="Replay config JSON file (replay.json)")
    args = parser.parse_args()

    model = ReplayModel(args.json_file)

    print("=== Replay Config (raw) ===")
    print(json.dumps(model.get_config(), indent=2, ensure_ascii=False))

    print("\n=== Converted times (usec) ===")
    print(f"start_time_usec: {model.start_time_usec}")
    print(f"range_begin_usec: {model.range_begin_usec}")
    print(f"range_end_usec:   {model.range_end_usec}")

    print("\n=== Runner Spec ===")
    print(json.dumps(model.to_spec(), indent=2, ensure_ascii=False))
