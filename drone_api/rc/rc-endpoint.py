#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time
from pathlib import Path

import pygame

from rc_utils.rc_utils import RcConfig, StickMonitor

try:
    from hakoniwa_pdu_endpoint.c_endpoint import Endpoint, PduKey
except ModuleNotFoundError:
    THIS_FILE = Path(__file__).resolve()
    FALLBACK_PYTHON_ROOT = THIS_FILE.parents[3] / "hakoniwa-pdu-endpoint" / "python"
    if FALLBACK_PYTHON_ROOT.exists():
        sys.path.insert(0, str(FALLBACK_PYTHON_ROOT))
    from hakoniwa_pdu_endpoint.c_endpoint import Endpoint, PduKey

from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_conv_GameControllerOperation import (
    py_to_pdu_GameControllerOperation,
)
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_GameControllerOperation import (
    GameControllerOperation,
)


DEFAULT_RC_CONFIG_PATH = "rc_config/ps4-control.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drone RC via hakoniwa-pdu-endpoint")
    parser.add_argument(
        "--endpoint-config",
        default=str(Path(__file__).resolve().parents[2] / "config" / "endpoint" / "drone-game-websocket-client.json"),
        help="Path to endpoint config JSON",
    )
    parser.add_argument(
        "--rc_config",
        default=os.getenv("RC_CONFIG_PATH", DEFAULT_RC_CONFIG_PATH),
        help="Path to RC config JSON",
    )
    parser.add_argument(
        "--name",
        default="Drone",
        help="Robot name in pdudef",
    )
    parser.add_argument(
        "--index",
        default=0,
        type=int,
        help="Joystick index",
    )
    parser.add_argument(
        "--period-sec",
        default=0.02,
        type=float,
        help="Send period in seconds",
    )
    return parser.parse_args()


def create_initial_state() -> GameControllerOperation:
    data = GameControllerOperation()
    data.axis = [0.0] * 6
    data.button = [False] * 15
    return data


def update_axis_state(joystick, data: GameControllerOperation, stick_monitor: StickMonitor, prev_axes) -> None:
    axis_count = min(joystick.get_numaxes(), 6)
    for axis_index in range(axis_count):
        raw_value = joystick.get_axis(axis_index)
        op_index = stick_monitor.rc_config.get_op_index(axis_index)
        if op_index is None:
            continue
        stick_value = stick_monitor.stick_value(axis_index, raw_value)
        if stick_value is None:
            continue
        data.axis[op_index] = stick_value
        previous_value = prev_axes.get(axis_index, 0.0)
        if abs(stick_value) > 0.1 and abs(stick_value - previous_value) > 0.05:
            print(
                f"axis event: stick_index={axis_index} op_index={op_index} "
                f"raw={raw_value:.3f} mapped={stick_value:.3f}"
            , flush=True)
        prev_axes[axis_index] = stick_value


def update_button_state(joystick, data: GameControllerOperation, stick_monitor: StickMonitor, prev_buttons) -> None:
    button_count = min(joystick.get_numbuttons(), 16)
    for button_index in range(button_count):
        is_down = bool(joystick.get_button(button_index))
        previous_down = prev_buttons.get(button_index, False)
        if is_down == previous_down:
            continue
        prev_buttons[button_index] = is_down
        event_op_index = stick_monitor.rc_config.get_event_op_index(button_index)
        if event_op_index is None:
            continue
        event_triggered = stick_monitor.switch_event(button_index, is_down)
        print(
            f"button event: switch_index={button_index} event_op_index={event_op_index} "
            f"down: {is_down} event_triggered={event_triggered}"
        , flush=True)
        data.button[event_op_index] = event_triggered


def open_joystick(index: int):
    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    print(f"Number of joysticks: {joystick_count}")
    try:
        joystick = pygame.joystick.Joystick(index)
        joystick.init()
        print(f"Joystick name: {joystick.get_name()}")
        print(f"Buttons: {joystick.get_numbuttons()}", flush=True)
        return joystick
    except pygame.error:
        print("ERROR: joystick is not connected", flush=True)
        pygame.joystick.quit()
        pygame.quit()
        raise


def cleanup_pygame() -> None:
    pygame.joystick.quit()
    pygame.quit()


def run_loop(endpoint: Endpoint, robot_name: str, joystick, stick_monitor: StickMonitor, period_sec: float) -> None:
    key = PduKey(robot=robot_name, pdu="hako_cmd_game")
    data = create_initial_state()
    next_time = time.perf_counter()
    prev_axes = {}
    prev_buttons = {}

    while True:
        pygame.event.pump()
        update_axis_state(joystick, data, stick_monitor, prev_axes)
        update_button_state(joystick, data, stick_monitor, prev_buttons)

        payload = bytes(py_to_pdu_GameControllerOperation(data))
        endpoint.send_by_name(key, payload)

        next_time += period_sec
        sleep_duration = next_time - time.perf_counter()
        if sleep_duration > 0:
            time.sleep(sleep_duration)
        else:
            next_time = time.perf_counter()


def main() -> int:
    args = parse_args()

    endpoint_config_path = Path(args.endpoint_config)
    rc_config_path = Path(args.rc_config)
    if not endpoint_config_path.exists():
        print(f"ERROR: Endpoint config file not found at '{endpoint_config_path}'")
        return 1
    if not rc_config_path.exists():
        print(f"ERROR: RC config file not found at '{rc_config_path}'")
        return 1

    rc_config = RcConfig(str(rc_config_path))
    if rc_config.config is None:
        return 1
    print(f"RC Config Path: {rc_config_path}")
    print(f"Endpoint Config Path: {endpoint_config_path}")
    print(f"Robot Name: {args.name}")
    print(f"Mode: {rc_config.config['mode']}", flush=True)
    stick_monitor = StickMonitor(rc_config)

    try:
        joystick = open_joystick(args.index)
    except pygame.error:
        return 1

    endpoint = Endpoint("rc_endpoint", "inout")
    try:
        endpoint.open(str(endpoint_config_path))
        endpoint.start()
        time.sleep(1.0)
        run_loop(endpoint, args.name, joystick, stick_monitor, args.period_sec)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            endpoint.stop()
        except Exception:
            pass
        try:
            endpoint.close()
        except Exception:
            pass
        cleanup_pygame()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
