import argparse
import threading
from pymavlink import mavutil
from msg.mavlink_message import MavlinkMessage
from msg.message_queue import MessageQueue
from log.log_replay import LogReplay
from comm.udp_receiver import UdpReceiver
from msg.pdu_message_convertor import PduMessageConvertor
from hako_bridge.pdu_writer import HakoBridgePduWriter
from registry.conv import setup_converters
from registry.listen import setup_listen_msgs
import hakopy
import json

global my_context
class BridgeContext:
    def __init__(self, args):
        self.pdu_config = args.pdu_config
        self.delta_time_usec = 20 * 1000
        self.message_queue = MessageQueue(max_size=100)
        self.mavlink_connection = mavutil.mavlink.MAVLink(None)
        self.threads = []
        self.conv_registry = setup_converters(args.comm_config)
        self.list_registry = setup_listen_msgs()
        self.message_queue.set_listened_types(self.list_registry.msgs)
        self.convertor = PduMessageConvertor(args.mavlink_config, args.pdu_config, args.comm_config)

def start_log_replay(context, log_filename):
    log_replay = LogReplay(
        log_filename=log_filename,
        mavlink_connection=context.mavlink_connection,
        message_queue=context.message_queue,
        replay=True,
    )
    log_replay.replay_log()

def start_udp_receiver(context, udp_ip, udp_port):
    udp_receiver = UdpReceiver(
        udp_ip=udp_ip,
        udp_port=udp_port,
        mavlink_connection=context.mavlink_connection,
        message_queue=context.message_queue,
    )
    udp_receiver.start_receiving()

def my_on_initialize(context):
    return 0

def my_on_reset(context):
    return 0

def my_on_manual_timing_control(arg):
    pdu_writer = HakoBridgePduWriter(my_context.pdu_config)
    try:
        while True:
            if not my_context.message_queue.is_empty():
                mavlink_message = my_context.message_queue.dequeue()
                #print(f"queue len: {my_context.message_queue.size()}")
                try:
                    pdu_message = my_context.convertor.create_pdu(mavlink_message)
                    if my_context.conv_registry.get_converter(pdu_message.msg_type):
                        pdu_message = my_context.conv_registry.get_converter(pdu_message.msg_type).convert(pdu_message)
                    pdu_message = my_context.convertor.compile_pdu(pdu_message)
                    #print(f"Sending PDU message: {pdu_message}")
                    pdu_writer.write_pdu_message(pdu_message)
                except ValueError as e:
                    print(f"Conversion error: {e}")
            if not hakopy.usleep(my_context.delta_time_usec):
                break
    except KeyboardInterrupt:
        print("Terminating program...")
        for thread in my_context.threads:
            thread.join()
    return 0

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run MAVLink processing in either log replay or UDP reception mode.")
    parser.add_argument("--mavlink-config", required=True, help="Path to the mavlink-custom.json configuration file.")
    parser.add_argument("--pdu-config", required=True, help="Path to the pdu-custom.json configuration file.")
    parser.add_argument("--comm-config", required=True, help="Path to the comm_config.json configuration file.")
    subparsers = parser.add_subparsers(dest="mode", required=True)
    log_parser = subparsers.add_parser("log", help="Replay a MAVLink log file.")
    log_parser.add_argument("log_file", type=str, help="Path to the MAVLink log file.")
    udp_parser = subparsers.add_parser("udp", help="Receive MAVLink messages over UDP.")
    udp_parser.add_argument("udp_address", type=str, help="IP and port to bind to, in the format <ip>.")
    return parser.parse_args()

def main():
    global my_context
    args = parse_arguments()
    my_context = BridgeContext(args)

    hakopy.conductor_start(my_context.delta_time_usec, 100*1000)
    
    if args.mode == "log":
        log_thread = threading.Thread(
            target=start_log_replay,
            args=(my_context, args.log_file)
        )
        my_context.threads.append(log_thread)
    elif args.mode == "udp":
        with open(args.comm_config, 'r') as f:
            comm_config = json.load(f)
            for vehicle_name, vehicle_info in comm_config["vehicles"].items():
                #udp_ip, udp_port = args.udp_address.split(":")
                udp_ip = args.udp_address
                udp_port = comm_config["vehicles"][vehicle_name]["my_port"]
                udp_thread = threading.Thread(
                    target=start_udp_receiver,
                    args=(my_context, udp_ip, int(udp_port))
                )
                my_context.threads.append(udp_thread)

    for thread in my_context.threads:
        thread.start()

    my_callback = {
        'on_initialize': my_on_initialize,
        'on_simulation_step': None,
        'on_manual_timing_control': my_on_manual_timing_control,
        'on_reset': my_on_reset
    }

    ret = hakopy.asset_register(
        'MavlinkBridge',  # asset_name
        my_context.pdu_config,  # pdu_config
        my_callback,  # callback
        my_context.delta_time_usec,  # delta_time_usec
        hakopy.HAKO_ASSET_MODEL_CONTROLLER  # asset_model
    )

    if not ret:
        print("ERROR: hako_asset_register() failed.")
        return 1

    ret = hakopy.start()
    print(f"INFO: hako_asset_start() returns {ret}")

if __name__ == "__main__":
    main()
