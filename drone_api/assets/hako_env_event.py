import hakopy
import sys
import time
import os
import asyncio

from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_pytype_Twist import Twist
from hakoniwa_pdu.pdu_msgs.geometry_msgs.pdu_conv_Twist import pdu_to_py_Twist 
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_Disturbance import Disturbance
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_Disturbance import py_to_pdu_Disturbance

from lib.hako_area_accessor_impl import HakoAreaAccessorImpl
from lib.hako_area_pro_accessor_impl import HakoAreaPropAccessorImpl
from lib.hako_aabb_object_space import HakoAABBObjectSpace
from lib.hako_boundary import HakoBoundary

# Declare the global variable for delta_time_usec
delta_time_usec = 0
config_path = ''
area_config_dir=''
def my_on_initialize(context):
    print("INFO: INITIALIZE EVENT OCCURRED")
    return 0

def my_on_reset(context):
    print("INFO: RESET EVENT OCCURRED")
    return 0

def my_sleep():
    global delta_time_usec
    ret = hakopy.usleep(delta_time_usec)
    if ret == False:
        return False
    time.sleep(delta_time_usec / 1_000_000.0)

def on_manual_timing_control(context):
    global delta_time_usec
    print("INFO: START Wind control")
    area_accessor = HakoAreaAccessorImpl(os.path.join(area_config_dir, 'area.json'))
    prop_accessor = HakoAreaPropAccessorImpl(os.path.join(area_config_dir, 'area_property.json'))
    boundary_accessor = HakoBoundary(os.path.join(area_config_dir, 'boundary.json'))
    drone_size = (0.4, 0.4, 0.1)

    # Initialize the PDU manager
    pdu_manager = PduManager()
    pdu_manager.initialize(config_path=config_path, comm_service=ShmCommunicationService())
    pdu_manager.start_service_nowait()

    while True:
        ret = my_sleep()
        if ret == False:
            break

        pdu_manager.run_nowait()

        pose_raw_data = pdu_manager.read_pdu_raw_data('Drone', 'pos')
        if pose_raw_data is None or len(pose_raw_data) == 0:
            #print("ERROR: Failed to read pose data")
            continue
        try:
            pose: Twist = pdu_to_py_Twist(pose_raw_data)
        except Exception as e:
            print("WARNING: hako_env_event is failed to read pose data. writer will be soon available...")
            continue
        #print(f"Drone pose: {pose}")

        drone_position = (pose.linear.x, pose.linear.y, pose.linear.z)
        object_space = HakoAABBObjectSpace(drone_position, drone_size)
        area_id = area_accessor.get_area_id(object_space)

        disturbance: Disturbance = Disturbance()
        disturbance.d_wind.value.x = 0.0
        disturbance.d_wind.value.y = 0.0
        disturbance.d_wind.value.z = 0.0

        if area_id is not None:
            #print area_id
            #print(f"{hakopy.simulation_time()} area_id: {area_id}")
            property_info = prop_accessor.get_property(area_id)
            wind = property_info.get_wind_velocity()
            if wind is not None:
                #print(f"{hakopy.simulation_time()} wind ==> {property_info.get_wind_velocity()}")
                disturbance.d_wind.value.x = wind[0]
                disturbance.d_wind.value.y = wind[1]
                disturbance.d_wind.value.z = wind[2]
            temperature = property_info.get_temperature()
            if temperature is not None:
                #print(f"{hakopy.simulation_time()} temperature ==> {property_info.get_temperature()}")
                disturbance.d_temp.value = temperature
            sea_level_atm = property_info.get_sea_level_atm()
            if sea_level_atm is not None:
                #print(f"{hakopy.simulation_time()} sea_level_atm ==> {property_info.get_sea_level_atm()}")
                disturbance.d_atm.sea_level_atm = sea_level_atm
        else:
            pass
            #print(f"{hakopy.simulation_time()}: No wind")

        wall, normal, point, dist = boundary_accessor.find_nearest_wall_with_hitbox(drone_position, local_normal_axis=[0, 0, 1])
        if wall is not None:
            #print(f"{hakopy.simulation_time()} nearest wall: {wall['name']}, dist: {dist}, normal: {normal}, point: {point}")
            disturbance.d_boundary.boundary_point.x = point[0]
            disturbance.d_boundary.boundary_point.y = point[1]
            disturbance.d_boundary.boundary_point.z = point[2]
            disturbance.d_boundary.boundary_normal.x = normal[0]
            disturbance.d_boundary.boundary_normal.y = normal[1]
            disturbance.d_boundary.boundary_normal.z = normal[2]
        else:
            #print(f"{hakopy.simulation_time()}: No boundary")
            disturbance.d_boundary.boundary_point.x = 0.0
            disturbance.d_boundary.boundary_point.y = 0.0
            disturbance.d_boundary.boundary_point.z = 0.0
            disturbance.d_boundary.boundary_normal.x = 0.0
            disturbance.d_boundary.boundary_normal.y = 0.0
            disturbance.d_boundary.boundary_normal.z = 0.0
        # write pdu data
        disturbance_raw_data = py_to_pdu_Disturbance(disturbance)
        ret = pdu_manager.flush_pdu_raw_data_nowait('Drone', 'disturb', disturbance_raw_data)
        if not ret:
            print("ERROR: Failed to write disturbance data")

    return 0

my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    global delta_time_usec
    global config_path
    global area_config_dir
    global pdu_manager
    
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <config_path> <delta_time_msec> <area_config_dir>")
        return 1

    asset_name = 'HakoEnv'
    config_path = sys.argv[1]
    delta_time_usec = int(sys.argv[2]) * 1000
    area_config_dir = sys.argv[3]

    ret = hakopy.asset_register(asset_name, config_path, my_callback, delta_time_usec, hakopy.HAKO_ASSET_MODEL_PLANT)
    if ret == False:
        print(f"ERROR: hako_asset_register() returns {ret}.")
        return 1
    
    ret = hakopy.start()
    print(f"INFO: DONE {ret}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
