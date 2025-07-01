#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import asyncio
import pygame
import time
import os
import argparse
from rc_utils.rc_utils import RcConfig, StickMonitor
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService

# デフォルトのJSONファイルパス
DEFAULT_CONFIG_PATH = "rc_config/ps4-control.json"

async def joystick_control(manager: PduManager, robot_name: str, joystick, stick_monitor: StickMonitor):
    try:
        if not await manager.declare_pdu_for_write(robot_name, "hako_cmd_game"):
            print(f"[FAIL] Could not declare PDU for READ: {robot_name}/hako_cmd_game")
            raise RuntimeError("Failed to declare PDU for write")

        while True:
            data = manager.pdu_convertor.create_empty_pdu_json(robot_name, "hako_cmd_game")
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis < 6:
                        op_index = stick_monitor.rc_config.get_op_index(event.axis)
                        stick_value = stick_monitor.stick_value(event.axis, event.value)
                        if (abs(stick_value) > 0.1):
                            pass
                            #print(f"stick event: stick_index={event.axis} op_index={op_index} event.value={event.value} stick_value={stick_value}")
                        data['axis'] = list(data['axis'])
                        data['axis'][op_index] = stick_value
                    else:
                        print(f'ERROR: not supported axis index: {event.axis}')
                elif event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                    if event.button < 16:
                        data['button'] = list(data['button'])
                        event_op_index = stick_monitor.rc_config.get_event_op_index(event.button)
                        if event_op_index is not None:
                            event_triggered = stick_monitor.switch_event(event.button, (event.type == pygame.JOYBUTTONDOWN))
                            print(f"button event: switch_index={event.button} event_op_index={event_op_index} down: {(event.type == pygame.JOYBUTTONDOWN)} event_triggered={event_triggered}")
                            data['button'][event_op_index] = event_triggered
                            if event_triggered:
                                if event_op_index == stick_monitor.rc_config.SWITCH_CAMERA_SHOT:
                                    time.sleep(0.5)
                                    print("WARNING: saveCameraImage is not implemented in this version")
                                elif event_op_index == stick_monitor.rc_config.SWITCH_RETURN_HOME:
                                    print("WARNING: DroneController is not implemented in this version")
                    else:
                        print(f'ERROR: not supported button index: {event.button}')
            manager.flush_pdu_raw_data(robot_name, "hako_cmd_game", manager.pdu_convertor.convert_json_to_binary(robot_name, "hako_cmd_game", data))
    except KeyboardInterrupt:
        pygame.joystick.quit()
        pygame.quit()

async def main():
    parser = argparse.ArgumentParser(description="Drone RC")
    parser.add_argument("--config", required=True, help="Path to PDU channel config JSON")
    parser.add_argument("--rc_config", required=True, help="Path to the optional RC config file")
    parser.add_argument("--uri", required=True, help="WebSocket server URI")
    parser.add_argument("--name", type=str, help="Optional name for the configuration")

    args = parser.parse_args()

    print(f"Config Path: {args.config}")

    robot_name = args.name if args.name else "Drone"
    
    config_path = args.config
    rc_config_path = os.getenv("RC_CONFIG_PATH", DEFAULT_CONFIG_PATH)
    if args.rc_config:
        print(f"RC Config Path: {args.rc_config}")
        rc_config_path = args.rc_config
    
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
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f'ジョイスティックの名前: {joystick.get_name()}')
        print(f'ボタン数 : {joystick.get_numbuttons()}')
    except pygame.error:
        print('ジョイスティックが接続されていません')
        pygame.joystick.quit()
        pygame.quit()
        return 1


    # 通信サービス（WebSocket）を生成
    service = WebSocketCommunicationService()

    # PDUマネージャ初期化
    manager = PduManager()
    manager.initialize(config_path=args.config, comm_service=service)

    # 通信開始
    if not await manager.start_service(args.uri):
        print("[ERROR] Failed to start communication service.")
        sys.exit(1)


    try:
        await joystick_control(manager, robot_name, joystick, stick_monitor)
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        pygame.joystick.quit()
        pygame.quit()
        return 1
    return 0

if __name__ == "__main__":
    asyncio.run(main())
