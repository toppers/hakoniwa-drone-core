#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math


def next_pow2(x: int) -> int:
    if x <= 1:
        return 1
    return 1 << (x - 1).bit_length()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Calculate recommended core/bridge parameters for fleets."
    )
    p.add_argument("-n", "--drone-count", type=int, required=True, help="Number of drones")
    p.add_argument(
        "--max-drones-per-packet",
        type=int,
        default=0,
        help="Publisher max_drones_per_packet. 0 means single-channel mode (=N).",
    )
    p.add_argument(
        "--service-per-drone",
        type=int,
        default=5,
        help="RPC service count per drone (default: 5)",
    )
    p.add_argument(
        "--logical-channel-per-drone",
        type=int,
        default=19,
        help="Drone logical channels per drone (default: 19)",
    )
    p.add_argument(
        "--publisher-interval-ms",
        type=int,
        default=20,
        help="VisualStatePublisher publish interval ms (default: 20)",
    )
    p.add_argument(
        "--bridge-ticker-ms",
        type=int,
        default=20,
        help="Bridge ticker interval ms (default: 20)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    n = args.drone_count
    if n <= 0:
        raise SystemExit("--drone-count must be > 0")

    max_per_packet = args.max_drones_per_packet if args.max_drones_per_packet > 0 else n
    if max_per_packet <= 0:
        raise SystemExit("--max-drones-per-packet must be > 0")

    service_total = args.service_per_drone * n
    service_channels = service_total * 2  # req/res
    drone_channels = args.logical_channel_per_drone * n
    viewer_channels = 4
    channels_required = drone_channels + service_channels + viewer_channels

    hako_pdu_channel_max = next_pow2(channels_required)
    hako_service_max = next_pow2(service_total)
    hako_recv_event_max = max(1024, next_pow2(hako_service_max * 4))
    hako_service_client_max = max(128, next_pow2(n))
    hako_data_max_asset_num = 16

    visual_state_channels = math.ceil(n / max_per_packet)
    # Empirical sizing rule used in fleets:
    # one DroneVisualState entry is treated as ~64 bytes in transport budget.
    # Keep pdudef pdu_size as power-of-two with margin.
    visual_state_payload_bytes = 64 * max_per_packet
    visual_state_pdu_size_recommended = next_pow2(visual_state_payload_bytes)
    ws_packets_per_sec = 1000.0 / float(args.bridge_ticker_ms)
    ws_throughput_mb_s = (
        visual_state_pdu_size_recommended * visual_state_channels * ws_packets_per_sec
    ) / (1024.0 * 1024.0)

    print("# Fleet parameter recommendation")
    print(f"drone_count={n}")
    print("")
    print("## core-pro")
    print(f"channels_required={channels_required}  # {args.logical_channel_per_drone}*N + 2*{args.service_per_drone}*N + {viewer_channels}")
    print(f"HAKO_PDU_CHANNEL_MAX={hako_pdu_channel_max}")
    print(f"HAKO_SERVICE_MAX={hako_service_max}")
    print(f"HAKO_RECV_EVENT_MAX={hako_recv_event_max}")
    print(f"HAKO_SERVICE_CLIENT_MAX={hako_service_client_max}")
    print(f"HAKO_DATA_MAX_ASSET_NUM={hako_data_max_asset_num}")
    print("")
    print("## visual_state_publisher / bridge")
    print(f"max_drones_per_packet={max_per_packet}")
    print(f"required_visual_state_array_channels={visual_state_channels}")
    print(f"visual_state_payload_bytes_per_packet={visual_state_payload_bytes}")
    print(f"recommended_visual_state_pdu_size={visual_state_pdu_size_recommended}")
    print(f"publish_interval_msec={args.publisher_interval_ms}")
    print(f"bridge_ticker_interval_ms={args.bridge_ticker_ms}")
    print(f"estimated_ws_transfer_rate_mib_s={ws_throughput_mb_s:.2f}")
    print("")
    print("## build/install example")
    print(
        "ASSET_NUM={asset} SERVICE_MAX={svc} RECV_EVENT_MAX={recv} SERVICE_CLIENT_MAX={cli} "
        "bash thirdparty/hakoniwa-core-pro/build.bash".format(
            asset=hako_data_max_asset_num,
            svc=hako_service_max,
            recv=hako_recv_event_max,
            cli=hako_service_client_max,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
