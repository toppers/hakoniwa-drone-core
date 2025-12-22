#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from hakoniwa_pdu.apps.drone.hakosim import MultirotorClient, ImageType
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import GameControllerOperation
import pygame
import time
import os
import argparse
from rc_utils.rc_utils import RcConfig, StickMonitor
#from return_to_home import DroneController

from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_CameraCaptureImageRequest import CameraCaptureImageRequest
from hakoniwa_pdu.pdu_msgs.drone_srv_msgs.pdu_pytype_CameraCaptureImageResponse import CameraCaptureImageResponse
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import GameControllerOperation
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_GameControllerOperation import py_to_pdu_GameControllerOperation, pdu_to_py_GameControllerOperation
from hakoniwa_pdu.rpc.auto_wire import make_protocol_clients
from hakoniwa_pdu.rpc.protocol_client import ProtocolClientImmediate
from hakoniwa_pdu.rpc.shm.shm_pdu_service_client_manager import ShmPduServiceClientManager
import hakopy

def is_hakoniwa_running() -> bool:
    import subprocess
    result = subprocess.run(
        ["hako-cmd", "status"],
        capture_output=True,
        text=True
    )

    output = result.stdout.strip()
    print(output)

    if "status=running" in output:
        print("✅ Hakoniwa is running!")
        return True
    else:
        print("❌ Hakoniwa is NOT running.")
        return False

client_pdu_manager: ShmPduServiceClientManager = None
protocol_clients: dict[str, ProtocolClientImmediate] = None

def initialize_pdu_manager(asset_name: str, pdu_config_path: str, pdu_offset_path: str, service_config_path: str, delta_time_usec: int) -> ShmPduServiceClientManager:
    global client_pdu_manager
    global protocol_clients
    if not hakopy.init_for_external():
        print("[ERROR] Failed to register asset")
        return 1

    client_pdu_manager = ShmPduServiceClientManager(asset_name = asset_name, pdu_config_path=pdu_config_path, offset_path= pdu_offset_path)
    client_pdu_manager.initialize_services(service_config_path, delta_time_usec=delta_time_usec)

    while not is_hakoniwa_running():
        print("[Visualizer] Waiting for Hakoniwa to start...")
        time.sleep(1.0)

    #wait for a moment to ensure Hakoniwa is fully running
    #time.sleep(3.0)

    print("[Visualizer] Hakoniwa is now running!")

    protocol_clients = make_protocol_clients(
        pdu_manager=client_pdu_manager,
        services= [
            {
                "service_name": "DroneService/CameraCaptureImage",
                "client_name": "Client01",
                "srv": "CameraCaptureImage",
            }
        ],
        pkg = "hakoniwa_pdu.pdu_msgs.drone_srv_msgs",
        ProtocolClientClass=ProtocolClientImmediate,
    )
    first_client = next(iter(protocol_clients.values()))
    first_client.start_service(None)
    for client in protocol_clients.values():
        client.register()

# デフォルトのJSONファイルパス
DEFAULT_CONFIG_PATH = "rc_config/ps4-control.json"

def saveCameraImage(drone_name: str):
    req = CameraCaptureImageRequest()
    req.drone_name = drone_name
    req.image_type = "png"
    res = protocol_clients["DroneService/CameraCaptureImage"].call(req, poll_interval=0.01, timeout_msec=-1)
    if res is None:
        print("Failed to get response")
        return 1
    print(f"Response: {res}")
    png_images = res.data
    with open("captured_image.png", "wb") as f:
        f.write(bytearray(png_images))
    print("Image saved to captured_image.png")

def joystick_control(drone_name: str, protocol_clients, joystick, stick_monitor: StickMonitor):
    global client_pdu_manager
    try:
        while True:
            client_pdu_manager.run_nowait()
            data: GameControllerOperation = GameControllerOperation()
            try:
                raw_data = client_pdu_manager.read_pdu_raw_data(robot_name=drone_name, pdu_name="hako_cmd_game")
                data : GameControllerOperation = pdu_to_py_GameControllerOperation(raw_data)
            except Exception as e:
                pass
            data.axis = list(data.axis)
            data.button = list(data.button)
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis < 6:
                        op_index = stick_monitor.rc_config.get_op_index(event.axis)
                        stick_value = stick_monitor.stick_value(event.axis, event.value)
                        if (stick_value is not None):
                            if abs(stick_value) > 0.1:
                                pass
                            #print(f"stick event: stick_index={event.axis} op_index={op_index} event.value={event.value} stick_value={stick_value}")
                            if len(data.axis) <= op_index:
                                print(f'ERROR: axis size is small: {len(data.axis)} <= {op_index}')
                            else:
                                data.axis[op_index] = stick_value
                        else:
                            print(f'ERROR: not supported axis index: {event.axis}')
                elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    if event.button < 16:
                        event_op_index = stick_monitor.rc_config.get_event_op_index(event.button)
                        if event_op_index is not None:
                            event_triggered = stick_monitor.switch_event(event.button, (event.type == pygame.JOYBUTTONDOWN))
                            print(f"button event: switch_index={event.button} event_op_index={event_op_index} down: {(event.type == pygame.JOYBUTTONDOWN)} event_triggered={event_triggered}")
                            data.button[event_op_index] = event_triggered
                            if event_triggered:
                                if event_op_index == stick_monitor.rc_config.SWITCH_CAMERA_SHOT:
                                    time.sleep(0.5)
                                    saveCameraImage(drone_name)
                    else:
                        print(f'ERROR: not supported button index: {event.button}')
            #print("data: button", data['button'])
            raw_data = py_to_pdu_GameControllerOperation(data)
            client_pdu_manager.flush_pdu_raw_data_nowait(robot_name=drone_name, pdu_name="hako_cmd_game", pdu_raw_data=raw_data)
    except KeyboardInterrupt:
        pygame.joystick.quit()
        pygame.quit()

def main():
    parser = argparse.ArgumentParser(description="Drone RC")
    parser.add_argument("config_path", help="Path to the custom.json file")
    parser.add_argument("rc_config_path", nargs="?", help="Path to the optional RC config file")
    parser.add_argument("--name", default="Drone", type=str, help="Optional name for the configuration")
    parser.add_argument("--index", default=0, type=int, help="Joystick index (default: 0)")

    args = parser.parse_args()

    print(f"Config Path: {args.config_path}")
    
    config_path = args.config_path
    rc_config_path = os.getenv("RC_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if args.rc_config_path:
        print(f"RC Config Path: {args.rc_config_path}")
        rc_config_path = args.rc_config_path
    
    if not os.path.exists(config_path):
        print(f"ERROR: Config file not found at '{config_path}'")
        return 1
    if not os.path.exists(rc_config_path):
        print(f"ERROR: Config file not found at '{rc_config_path}'")
        return 1

    # RcConfigとStickMonitorの初期化
    rc_config = RcConfig(rc_config_path)
    print("Controller: ", rc_config_path)
    print("Mode: ", rc_config.config['mode'])
    stick_monitor = StickMonitor(rc_config)

    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    print(f"Number of joysticks: {joystick_count}")
    try:
        joystick = pygame.joystick.Joystick(args.index)
        joystick.init()
        print(f'ジョイスティックの名前: {joystick.get_name()}')
        print(f'ボタン数 : {joystick.get_numbuttons()}')
    except pygame.error:
        print('ジョイスティックが接続されていません')
        pygame.joystick.quit()
        pygame.quit()
        return 1


    initialize_pdu_manager(
        asset_name="RemoteClient",
        pdu_config_path=args.config_path,
        pdu_offset_path='/usr/local/share/hakoniwa/offset',
        service_config_path="../../config/launcher/drone_service_rc.json",
        delta_time_usec=20000,
    )

    joystick_control(args.name, protocol_clients, joystick, stick_monitor)
    return 0

if __name__ == "__main__":
    sys.exit(main())
