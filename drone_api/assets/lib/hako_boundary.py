# -*- coding: utf-8 -*-
import numpy as np
from scipy.spatial.transform import Rotation as R
import json
class HakoBoundary:
    def __init__(self, boundary_json_file_path:str):
        with open(boundary_json_file_path, 'r') as f:
            boundary_json = f.read()
            self.wall_list = json.loads(boundary_json)

    # 例: ローカル法線軸を指定できるようにする
    def compute_wall_normal_from_view(self, drone_pos, wall_def, local_normal_axis=[0, 0, 1]):
        position = np.array(wall_def["position"])
        rotation = wall_def["rotation"]
        r = R.from_euler('ZYX', rotation, degrees=True)

        normal = r.apply(local_normal_axis)
        v = drone_pos - position

        if np.dot(v, normal) < 0:
            normal = -normal

        return normal

    def intersect_ray_with_plane(self, drone_pos, wall_pos, normal):
        """
        drone_pos: ドローンの世界座標 np.array([x, y, z])
        wall_pos: 壁の中心座標 np.array([x, y, z])
        normal: 壁の法線ベクトル（正規化済み） np.array([nx, ny, nz])
        """
        v = drone_pos - wall_pos
        t = np.dot(v, normal)

        # 交点 = drone_pos - t * normal
        intersection_point = drone_pos - t * normal

        return intersection_point, abs(t)  # tが負なら裏側、正なら正面（今回は気にしない）
    
    def is_point_in_wall_rectangle(self, intersection_point, wall_def):
        wall_pos = np.array(wall_def["position"])
        rot = wall_def["rotation"]
        size = wall_def["size"]  # [width, height] = [x方向, y方向]
        r = R.from_euler('ZYX', rot, degrees=True)

        # ローカル軸（tangent: 横, bitangent: 縦）
        tangent = r.apply([1, 0, 0])       # x方向（幅）
        bitangent = r.apply([0, 1, 0])     # y方向（高さ）

        # 交点から壁中心までのベクトル
        d = intersection_point - wall_pos

        # 各軸への射影（ローカル座標系での相対位置）
        x_proj = np.dot(d, tangent)
        y_proj = np.dot(d, bitangent)

        # 半サイズ（中心からの許容範囲）
        half_w = size[0] / 2
        half_h = size[1] / 2

        # 範囲内かチェック
        return (-half_w <= x_proj <= half_w) and (-half_h <= y_proj <= half_h)
    

    def find_nearest_wall_with_hitbox(self, drone_pos, local_normal_axis=[0, 0, 1]):
        min_dist = float('inf')
        nearest_wall = None
        nearest_normal = None
        hit_point = None

        for wall in self.wall_list:
            wall_pos = np.array(wall["position"])
            normal = self.compute_wall_normal_from_view(drone_pos, wall, local_normal_axis)

            # 平面との交点と距離
            point, dist = self.intersect_ray_with_plane(drone_pos, wall_pos, normal)

            # 交点が壁の矩形内にあるか？
            if self.is_point_in_wall_rectangle(point, wall):
                if dist < min_dist:
                    min_dist = dist
                    nearest_wall = wall
                    nearest_normal = normal
                    hit_point = point

        return nearest_wall, nearest_normal, hit_point, min_dist