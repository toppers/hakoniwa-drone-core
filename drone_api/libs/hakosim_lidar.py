import struct
import math
from typing import Dict, List, Tuple, Optional
Point = Tuple[float, float, float]
CellKey = Tuple[int, int]

class LidarData:
    def __init__(self, point_cloud, time_stamp, pose, data_frame='VehicleInertialFrame', segmentation=None):
        """
        Initializes a new instance of the LidarData class.

        :param point_cloud: A flat list of floats representing the [x, y, z] coordinates of each point.
        :param time_stamp: Timestamp of the Lidar data capture.
        :param pose: The pose of the Lidar in vehicle inertial frame (in NED, in meters).
        :param data_frame: Frame of the point cloud data. Default is 'VehicleInertialFrame'.
                           It can also be 'SensorLocalFrame' for points in Lidar local frame.
        :param segmentation: Optional; segmentation information for each point's collided object.
        """
        self.point_cloud = point_cloud
        self.time_stamp = time_stamp
        self.pose = pose
        self.data_frame = data_frame
        self.segmentation = segmentation

    def __repr__(self):
        return f"LidarData(time_stamp={self.time_stamp}, data_frame={self.data_frame}, " \
               f"pose={self.pose}, number_of_points={len(self.point_cloud) // 3})"

    @staticmethod
    def parse_point_cloud(point_cloud):
        """
        Parses the flat list of floats into a list of (x, y, z) tuples.

        :param point_cloud: A flat list of floats.
        :return: A list of (x, y, z) tuples representing the coordinates.
        """
        return [(point_cloud[i], point_cloud[i+1], point_cloud[i+2]) for i in range(0, len(point_cloud), 3)]


    @staticmethod
    def extract_xyz_from_point_cloud(point_cloud_bytes, total_data_bytes):
        # 各ポイントは16バイトで、x, y, z, intensityが含まれています。
        num_points = total_data_bytes // 16
        # 出力リストを初期化
        points = []

        for i in range(num_points):
            # 16バイトごとにデータを取り出す
            offset = i * 16
            # '<3f'はリトルエンディアンのfloat32が3つ、x, y, z座標を意味します。
            # 12バイトを読み取り、次の4バイト（intensity）は無視します。
            point = struct.unpack_from('<3f', point_cloud_bytes, offset)
            # 取り出した座標をリストに追加
            points.extend(point)

        return points
    

class LiDARFilter:
    def __init__(self, lidar_data):
        """
        :param lidar_data: あなたの hakosim_lidar.LidarData インスタンス
                           .point_cloud は [x0,y0,z0, x1,y1,z1, ...] のフラット配列を想定
        """
        self.ld = lidar_data

    # --- S0: サニタイズ（未接触/範囲/高さ） ---
    def _iter_sanitized(self,
                        min_r: float,
                        max_r: float,
                        z_band: Optional[Tuple[float, float]],
                        eps: float = 1e-3):
        pc = self.ld.point_cloud
        n = len(pc) // 3
        if z_band is None:
            z0, z1 = -float("inf"), float("inf")
        else:
            z0, z1 = z_band
        for i in range(n):
            x = float(pc[3*i + 0]); y = float(pc[3*i + 1]); z = float(pc[3*i + 2])
            r = math.sqrt(x*x + y*y + z*z)
            # ヒットなしは MaxDistance が入ってくる運用 → ここでは max_r より大きいものを除外して“未接触扱い”
            if (r >= min_r) and (r < max_r - eps) and (z0 <= z <= z1):
                yield (x, y, z), r

    # --- S2: XYグリッドで“最短1点/セル” ---
    @staticmethod
    def _cell_key(p: Point, x_size: float, y_size: float) -> CellKey:
        x, y, _ = p
        return (int(math.floor(x / x_size)),
                int(math.floor(y / y_size)))

    def filter(self,
               *,
               x_size: float = 0.4,
               y_size: float = 0.4,
               min_r: float = 0.3,
               max_r: float = 10.0,
               z_band: Optional[Tuple[float, float]] = (-0.2, 2.5),
               top_k: int = 10,
               with_stats: bool = False) -> List[dict]:
        """
        S0（未接触/範囲/高さフィルタ）→ S2（XYセルの最短点）
        :returns: 近い順Top-Kの候補。with_stats=False なら最短点のみ。
        """
        cells: Dict[CellKey, Dict] = {}
        for p, r in self._iter_sanitized(min_r=min_r, max_r=max_r, z_band=z_band):
            key = self._cell_key(p, x_size, y_size)
            rec = cells.get(key)
            if rec is None or r < rec["r"]:
                # 最短点のみ保持
                cells[key] = {"r": r, "x": p[0], "y": p[1], "z": p[2],
                              "min": [p[0], p[1], p[2]], "max": [p[0], p[1], p[2]], "count": 1}
            else:
                # with_stats のときだけ意味が出るが、更新コストは軽いので常時更新しておく
                rec["count"] += 1
                if p[0] < rec["min"][0]: rec["min"][0] = p[0]
                if p[1] < rec["min"][1]: rec["min"][1] = p[1]
                if p[2] < rec["min"][2]: rec["min"][2] = p[2]
                if p[0] > rec["max"][0]: rec["max"][0] = p[0]
                if p[1] > rec["max"][1]: rec["max"][1] = p[1]
                if p[2] > rec["max"][2]: rec["max"][2] = p[2]

        # 近い順Top-K
        arr = sorted(cells.values(), key=lambda d: d["r"])[:top_k]
        if not with_stats:
            return [{"x": c["x"], "y": c["y"], "z": c["z"], "distance": c["r"]} for c in arr]
        else:
            return [{
                "x": c["x"], "y": c["y"], "z": c["z"], "distance": c["r"],
                "count": c["count"],
                "aabb_min": {"x": c["min"][0], "y": c["min"][1], "z": c["min"][2]},
                "aabb_max": {"x": c["max"][0], "y": c["max"][1], "z": c["max"][2]},
            } for c in arr]
