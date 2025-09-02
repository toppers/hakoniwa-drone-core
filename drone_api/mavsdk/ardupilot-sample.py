import asyncio
from mavsdk import System
from mavsdk.offboard import PositionNedYaw


async def wait_until_ready(drone):
    print("-- Waiting for drone to be ready...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("✓ Drone is ready (GPS & home position OK)")
            break
        await asyncio.sleep(1)

async def wait_until_altitude(drone, target_altitude, tolerance=0.2):
    print(f"-- Waiting to reach {target_altitude}m altitude...")
    while True:
        pos_ned = await drone.telemetry.position_velocity_ned().__anext__()
        current_alt = -pos_ned.position.down_m
        print(f"Current height: {current_alt:.2f}m (target: {target_altitude}m)")
        if abs(current_alt - target_altitude) <= tolerance:
            print(f"✓ Target altitude reached: {current_alt:.2f}m")
            break
        await asyncio.sleep(1)

async def wait_until_position_ned(drone, target_north, target_east, target_down, tolerance=0.5):
    print("-- Waiting to reach target position...")
    while True:
        pos_ned = await drone.telemetry.position_velocity_ned().__anext__()
        current_n = pos_ned.position.north_m
        current_e = pos_ned.position.east_m
        current_d = pos_ned.position.down_m

        horiz_dist = ((current_n - target_north)**2 + (current_e - target_east)**2)**0.5
        vert_diff = abs((-current_d) - (-target_down))

        print(f"Position: N={current_n:.2f}, E={current_e:.2f}, H={-current_d:.2f}")
        print(f"Distance to target: {horiz_dist:.2f}m (horizontal), {vert_diff:.2f}m (altitude)")

        if horiz_dist <= tolerance and vert_diff <= tolerance:
            print("✓ Target position reached")
            break

        await asyncio.sleep(2)


async def move_relative_ned(drone, dx, dy, dz=0.0, yaw=0.0, tolerance=0.5):
    """
    現在位置を基準に、相対移動を行う（NED座標系）
    dx: 北方向への移動量（+前、-後）
    dy: 東方向への移動量（+右、-左）
    dz: 下方向への移動量（+降下、-上昇） → 通常は一定高度なので省略可
    yaw: 目標向き（角度） → 今は0固定でOK
    """

    # 現在位置を取得
    current_pos = await drone.telemetry.position_velocity_ned().__anext__()
    start_north = current_pos.position.north_m
    start_east = current_pos.position.east_m
    start_down = current_pos.position.down_m

    # 目標位置を計算
    target_north = start_north + dx
    target_east = start_east + dy
    target_down = start_down + dz

    print(f"-- Moving relative: ΔN={dx}, ΔE={dy}, ΔD={dz} → N={target_north:.2f}, E={target_east:.2f}, D={target_down:.2f}")

    await drone.offboard.set_position_ned(PositionNedYaw(target_north, target_east, target_down, yaw))

    await wait_until_position_ned(
        drone,
        target_north=target_north,
        target_east=target_east,
        target_down=target_down,
        tolerance=tolerance
    )


async def run():
    print("Drone Offboard Control Sample")
    drone = System()
    await drone.connect(system_address="udp://0.0.0.0:14550")

    print("-- Connecting...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✓ Drone connected")
            break

    await wait_until_ready(drone)

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await wait_until_altitude(drone, target_altitude=2.0)

    print("-- Offboard start")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 0.0))
    await drone.offboard.start()

    # 高度一定、前へ10m進む（相対）
    await move_relative_ned(drone, dx=50.0, dy=0.0, dz=0.0)

    # 右へ5m
    await move_relative_ned(drone, dx=0.0, dy=50.0)

    # 左後ろへ斜め戻る
    await move_relative_ned(drone, dx=-50.0, dy=-50.0)

    print("-- Offboard stop")
    await drone.offboard.stop()

    print("-- Landing")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())