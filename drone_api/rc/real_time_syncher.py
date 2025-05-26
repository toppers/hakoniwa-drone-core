import hakopy
import sys
import time
import os
import hako_pdu
import libs.pdu_info as pdu_info

# Declare the global variable for delta_time_usec
delta_time_usec = 0
config_path = ''

def my_on_initialize(context):

    return 0

def my_on_reset(context):
    print("INFO: RESET EVENT OCCURRED")
    return 0

def my_on_simulation_step(context):
    global delta_time_usec
    time.sleep(delta_time_usec / 1_000_000)  # Convert microseconds to seconds for sleep
    return 0

my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': None,
    'on_reset': my_on_reset
}

def main():
    global delta_time_usec
    global config_path
    
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <config_path> <delta_time_msec>")
        return 1

    asset_name = 'RealTimeSyncher'
    config_path = sys.argv[1]
    delta_time_usec = int(sys.argv[2]) * 1000
    my_callback['on_simulation_step'] = my_on_simulation_step

    ret = hakopy.asset_register(asset_name, config_path, my_callback, delta_time_usec, hakopy.HAKO_ASSET_MODEL_PLANT)
    if ret == False:
        print(f"ERROR: hako_asset_register() returns {ret}.")
        return 1
    
    ret = hakopy.start()
    print(f"INFO: DONE {ret}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
