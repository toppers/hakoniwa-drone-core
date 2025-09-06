import os
import sys
import time
import argparse
from typing import Optional, List, Dict
import pandas as pd

import hakopy

from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_pytype_Twist import Twist
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_conv_Twist import py_to_pdu_Twist

from .logdata_model import LogDataModel, find_dynamics_csv
from .replay_model import ReplayModel
from .clock import Clock 

# --------- OutputPolicy (拡張ポイント：ZOH/補間を差替えたい時に) ---------
class OutputPolicy:
    """
    現在は「target_time までに到達している行をすべて flush」のみ。
    将来、ZOH(前値保持)や補間をしたい場合は、publish_* を差し替える。
    """
    def publish_until(self, start_rel_usec: int, end_rel_usec: int, drone_replayer: "DroneReplayer", verbose: bool = False):
        drone_replayer.publish_window(
            start_rel_usec=start_rel_usec,
            end_rel_usec=end_rel_usec,
            verbose=verbose
        )


# --------- Per-drone replayer ---------
class DroneReplayer:
    """
    単一ドローンのリプレイ担当（pandas版）。
    (start, end] のウィンドウ内で最後の1件だけ出力する。
    """
    def __init__(self, drone_name: str, pdu_name: str, model: LogDataModel,
                 pdu_manager: Optional[PduManager],
                 begin_rel_usec: Optional[int], end_rel_usec: Optional[int]):
        self.drone_name = drone_name
        self.pdu_name = pdu_name or "pos"
        self.model = model
        self.pdu_manager = pdu_manager

        rows = model.get_data()
        if not rows:
            raise RuntimeError(f"[{self.drone_name}] No data after validation.")

        # ---- DataFrame化 & 相対時刻列 ----
        df = pd.DataFrame(rows)
        self.base_ts = int(df["timestamp"].iloc[0])
        df["rel_ts"] = df["timestamp"].astype("int64") - self.base_ts

        # ---- 範囲クリップ（再生区間の前処理）----
        self.begin_rel = int(begin_rel_usec or 0)
        self.end_rel = int(end_rel_usec) if end_rel_usec is not None else None
        if self.end_rel is not None:
            df = df[(df["rel_ts"] >= self.begin_rel) & (df["rel_ts"] <= self.end_rel)]
        else:
            df = df[df["rel_ts"] >= self.begin_rel]

        # 空になったら終了
        if df.empty:
            self.df = df.reset_index(drop=True)
            self.cursor = 0
            self.finished = True
            return

        # 位置インデックス（高速に前方消費）
        self.df = df.reset_index(drop=True)
        self.df["pos"] = self.df.index.astype("int64")
        # begin_rel以上の先頭位置にカーソル
        self.cursor = int(self.df["pos"].iloc[0])
        self.finished = False

    # ---- 拡張フック（今はNOP）----
    def on_tick_begin(self, target_time_usec: int):
        pass

    def on_tick_end(self, target_time_usec: int):
        pass

    def _flush_twist_from_row(self, row: pd.Series, verbose: bool = False) -> bool:
        twist = Twist()
        twist.linear.x = float(row["X"]); twist.linear.y = float(row["Y"]); twist.linear.z = float(row["Z"])
        twist.angular.x = float(row["Rx"]); twist.angular.y = float(row["Ry"]); twist.angular.z = float(row["Rz"])
        #print(f"[{self.drone_name}] Publishing at rel_ts={row['rel_ts']}: {twist}")
        raw = py_to_pdu_Twist(twist)
        ok = self.pdu_manager.flush_pdu_raw_data_nowait(self.drone_name, self.pdu_name, raw)
        if not ok and verbose:
            print(f"[{self.drone_name}] WARN: flush failed at rel_ts={row['rel_ts']}")
        return ok

    def publish_window(self, start_rel_usec: int, end_rel_usec: int, verbose: bool = False) -> bool:
        """
        (start_rel_usec, end_rel_usec] の範囲で最後（=最大 rel_ts）の1件だけ出力。
        見つからなければ何もしない。出力したら True。
        """
        if self.finished:
            return False

        # グローバル範囲と交差
        w_start = max(start_rel_usec, self.begin_rel)
        w_end = end_rel_usec if self.end_rel is None else min(end_rel_usec, self.end_rel)
        if w_end <= w_start:
            # 範囲が無効 or もう終端超え
            if self.end_rel is not None and self.cursor >= len(self.df):
                self.finished = True
            return False

        # 現在カーソル以降だけを対象にブールマスク
        df = self.df
        if self.cursor >= len(df):
            self.finished = True
            return False

        view = df.iloc[self.cursor:]
        mask = (view["rel_ts"] > w_start) & (view["rel_ts"] <= w_end)
        if not mask.any():
            # ヒットがない場合、カーソルを w_end を超えない範囲で前進（任意最適化）
            # 次窓での再探索コスト削減：w_end 未満の行はスキップしてよい
            # ただし rel_ts が等間隔でない可能性に配慮し、<= w_end の最大posまで進める
            candidates = view[view["rel_ts"] <= w_end]
            if not candidates.empty:
                self.cursor = int(candidates["pos"].iloc[-1] + 1)
                if self.cursor >= len(df):
                    self.finished = True
            return False

        # 最後の1件（endに最も近い = 最大rel_ts）を選ぶ
        hit = view[mask].iloc[-1]  # mask True 部分の末尾
        self._flush_twist_from_row(hit, verbose=verbose)

        # 消費：その行の次へ
        self.cursor = int(hit["pos"] + 1)
        if self.cursor >= len(df) or (self.end_rel is not None and hit["rel_ts"] >= self.end_rel):
            self.finished = True
            if verbose:
                print(f"[{self.drone_name}] Finished.")
        return True
    
    def reset(self):
        # begin 以上の先頭にカーソル戻す
        if self.df.empty:
            self.cursor = 0
            self.finished = True
            return
        self.cursor = int(self.df["pos"].iloc[0])
        self.finished = False

# --------- Orchestrator (hakopy callbacks) ---------
class HakoAssetReplayer:
    """
    手動タイミング制御で進む箱庭アセット（複数ドローン対応）。
    - spec: ReplayModel.to_spec() の戻り値（drones/pdu_config_dir/timing）
    - グローバル刻み: ユーザ指定の delta_time_usec（等速前進のみ）
    - 出力順: publish(各機体, target) → run_nowait → sleep
    """
    def __init__(self, asset_name: str, spec: dict, delta_time_usec: int,
                 output_policy: Optional[OutputPolicy] = None,
                 verbose: bool = True):
        self.asset_name = asset_name
        self.verbose = verbose

        # spec 展開
        self.pdu_config: str = spec["pdu_def_file"]
        self.drones_spec: List[Dict] = spec["drones"]
        t = spec.get("timing", {})
        self.range_begin_usec = t.get("range_begin_usec")
        self.range_end_usec = t.get("range_end_usec")

        # 時間
        self.clock = Clock(delta_time_usec, self.range_begin_usec, self.range_end_usec)
        if self.verbose:
            print(f"[HakoAssetReplayer] Timing: delta={self.clock.delta} usec, "
                  f"begin={self.range_begin_usec} usec, end={self.range_end_usec} usec")
        # 構成
        self.pdu_manager: Optional[PduManager] = None
        self.drones: List[DroneReplayer] = []
        self.output_policy = output_policy or OutputPolicy()

        self._setup_drones()

        self._callbacks = {
            'on_initialize': self._on_initialize,
            'on_simulation_step': None,
            'on_manual_timing_control': self._on_manual_timing_control,
            'on_reset': self._on_reset,
        }

    def _setup_drones(self):
        begin_rel = self.range_begin_usec
        end_rel = self.range_end_usec

        for dspec in self.drones_spec:
            name = dspec["name"]
            pdu_name = dspec.get("pdu_name", "pos")
            log_path = dspec["log"]
            csv_path = find_dynamics_csv(log_path) if os.path.isdir(log_path) else log_path

            model = LogDataModel(csv_path)
            if self.verbose:
                rep = model.get_report()
                print(f"[{name}] rows={rep.get('rows_final')} duration={rep['timestamp'].get('duration_usec')} usec")

            drone = DroneReplayer(
                drone_name=name,
                pdu_name=pdu_name,
                model=model,
                pdu_manager=None,  # start後に注入
                begin_rel_usec=begin_rel,
                end_rel_usec=end_rel,
            )
            self.drones.append(drone)

    # ---- hakopy callbacks ----
    def _on_initialize(self, context):
        if self.verbose:
            print("[HakoAssetReplayer] INITIALIZE")
        return 0

    def _on_reset(self, context):
        if self.verbose:
            print("[HakoAssetReplayer] RESET")
        for d in self.drones:
            d.reset()
        return 0
    
    def _on_manual_timing_control(self, context):
        # 初回 PDU 起動
        if self.pdu_manager is None:
            self.pdu_manager = PduManager()
            self.pdu_manager.initialize(config_path=self.pdu_config, comm_service=ShmCommunicationService())
            self.pdu_manager.start_service_nowait()
            for d in self.drones:
                d.pdu_manager = self.pdu_manager
            if self.verbose:
                print("[HakoAssetReplayer] START REPLAY (manual timing w/ conductor)")


        print(f"[HakoAssetReplayer] TICK: now={self.clock.now} usec, delta={self.clock.delta} usec end={self.range_end_usec} usec")
        # 終了してたら即 return
        if (self.range_end_usec is not None and self.clock.now >= self.range_end_usec) or all(d.finished for d in self.drones):
            if self.verbose:
                print("[HakoAssetReplayer] Already finished.")
            return 0

        dt = self.clock.delta
        start = self.clock.now
        global_end = self.range_end_usec  # None 可

        # local_end の決定
        # テストで「local_end=global_end」をしたい場合はここで上書きしてOK：
        # local_end = global_end if global_end is not None else start + dt
        # 通常運用なら:
        local_end = start + dt
        if global_end is not None and local_end > global_end:
            local_end = global_end

        # (start, end] スロットで刻む
        t = start
        while t < global_end:

            #print(f"[HakoAssetReplayer]  slot: (>{t} .. {global_end}] usec")

            slot_end = t + dt
            # 各ドローン: (t, slot_end] の最新1件だけ出力
            for d in self.drones:
                self.output_policy.publish_until(start_rel_usec=t, end_rel_usec=slot_end, drone_replayer=d, verbose=self.verbose)

            # 反映
            self.pdu_manager.run_nowait()

            # 箱庭時間を前進
            hakopy.usleep(dt)
            #time.sleep(dt / 1_000_000)
            #print(f"[HakoAssetReplayer]  advanced {dt} usec")
            # 次スロットへ
            t = slot_end
            if t >= global_end:
                print(f"[HakoAssetReplayer]  END slot: (>{t} .. {slot_end}] usec")
                break

        # 内部時計を local_end に進める
        self.clock.seek(local_end)

        # 全終了ログ
        if (global_end is not None and self.clock.now >= global_end) or all(d.finished for d in self.drones):
            if self.verbose:
                print("[HakoAssetReplayer] All drones finished.")
        return 0


    # ---- public API ----
    def register_and_start(self) -> int:
        # 資産登録の内部刻みも conductor と合わせる
        step = max(1, self.clock.delta)
        ret = hakopy.asset_register(
            self.asset_name,
            self.pdu_config,
            {
                'on_initialize': self._on_initialize,
                'on_simulation_step': None,
                'on_manual_timing_control': self._on_manual_timing_control,
                'on_reset': self._on_reset,
            },
            step,
            hakopy.HAKO_ASSET_MODEL_PLANT
        )
        if ret is False:
            print(f"[HakoAssetReplayer] ERROR: asset_register() -> {ret}")
            return 1

        if self.verbose:
            print(f"[HakoAssetReplayer] Registered asset='{self.asset_name}', step={step} usec")

        ret = hakopy.start()
        if self.verbose:
            print(f"[HakoAssetReplayer] DONE start={ret}")
        return 0 if ret else 1


# --------- CLI ---------
def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Hakoniwa Multi-Drone Log Replayer (manual timing, forward-only)")
    p.add_argument("--delta-time-msec", type=int, default=3, help="Global tick in msec (default: 3)")
    p.add_argument("--replay", required=True, help="Path to replay.json")
    p.add_argument("--asset-name", default="AssetReplayer", help="Hakoniwa asset name")
    p.add_argument("--quiet", action="store_true", help="Reduce logs")
    return p


def main() -> int:
    args = build_argparser().parse_args()

    # replay.json → spec へ
    rm = ReplayModel(args.replay)
    spec = rm.to_spec()  # speed 等は現状未使用（将来 slow 実装時に活用）

    delta_time_usec = args.delta_time_msec * 1000

    runner = HakoAssetReplayer(
        asset_name=args.asset_name,
        spec=spec,
        delta_time_usec=delta_time_usec,
        verbose=not args.quiet,
    )

    # conductor も同じ刻みで開始（period, delta ともに usec）
    hakopy.conductor_start(delta_time_usec, 20_000)  # period=20msec
    ret = runner.register_and_start()
    hakopy.conductor_stop()
    return ret


if __name__ == "__main__":
    sys.exit(main())
