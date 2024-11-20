import asyncio
import hakopy
import threading
import json
import time

class HakoPduCommInfo:
    def __init__(self, name: str, info):
        self.name = name
        self.info = info


async def on_simulation_step_async(context):
    #print("INFO: on_simulation_step_async")
    server_instance = HakoPduServer.get_instance()
    if server_instance is None:
        raise RuntimeError("HakoPduServer has not been initialized")

    for pdu_info in server_instance.pub_pdus:
        #print(f"pdu_data: start read {pdu_info.name} channel: {pdu_info.info['channel_id']} {pdu_info.info['pdu_size']}")
        pdu_data = hakopy.pdu_read(pdu_info.name, pdu_info.info['channel_id'], pdu_info.info['pdu_size'])
        if pdu_data is not None:
            #print(f"pdu_data: start publish: {pdu_info.name}")
            packet = DataPacket(pdu_info.name, pdu_info.info['channel_id'], pdu_data)
            await server_instance.socket.publish_pdu(packet)

    for pdu_info in server_instance.sub_pdus:
        packet = server_instance.get_packet(pdu_info.name, pdu_info.info['channel_id'])
        if packet is not None:
            pdu_data = packet.get_pdu_data()
            ret = hakopy.pdu_write(pdu_info.name, pdu_info.info['channel_id'], pdu_data, pdu_info.info['pdu_size'])
            if ret == False:
                print(f"ERROR: can not write pdu data: robot_name={pdu_info.name} channel_id={pdu_info.info['channel_id']}")

    return 0


class HakoPduServer:
    _instance = None

    @classmethod
    def get_instance(cls, socket=None, asset_name=None, config_path=None, delta_time_usec=None):
        if cls._instance is None:
            if None in (socket, asset_name, config_path, delta_time_usec):
                raise ValueError("HakoPduServer instance not initialized. Missing arguments.")
            cls._instance = HakoPduServer(socket, asset_name, config_path, delta_time_usec)

        return cls._instance

    def __init__(self, socket: HakoPduCommInterface, asset_name: str, config_path: str, delta_time_usec):
        self.socket = socket
        self.config_json = self._load_json(config_path)
        self.delta_time_usec = delta_time_usec
        self.slp_time_sec = float(delta_time_usec) / 1000000.0
        socket.setBuffer(self.put_pdu_data)

        ret = hakopy.init_for_external()
        if ret == False:
            print(f"ERROR: init_for_external() returns {ret}.")
            return False
        self.pdu_buffers = {}
        self.lock = threading.Lock()

        self.pub_pdus = []
        self.sub_pdus = []
        for entry in self.config_json['robots']:
            for writer in entry['shm_pdu_writers']:
                print(f"pdu writer: {entry['name']}")
                info = HakoPduCommInfo(entry['name'], writer)
                self.sub_pdus.append(info)
            for reader in entry['shm_pdu_readers']:
                info = HakoPduCommInfo(entry['name'], reader)
                print(f"pdu reader: {entry['name']}")
                self.pub_pdus.append(info)

    def _load_json(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"ERROR: File not found '{path}'")
        except json.JSONDecodeError:
            print(f"ERROR: Invalid Json fromat '{path}'")
        except PermissionError:
            print(f"ERROR: Permission denied '{path}'")
        except Exception as e:
            print(f"ERROR: {e}")
        return None

    def put_pdu_data(self, packet: DataPacket):
        key = (packet.robot_name, packet.channel_id)
        with self.lock:
            self.pdu_buffers[key] = packet

    def get_packet(self, name: str, channel_id: int) -> DataPacket:
        key = (name, channel_id)
        with self.lock:
            if key in self.pdu_buffers:
                data = self.pdu_buffers[key]
                self.pdu_buffers[key] = None  # データのリセット
                return data
            else:
                return None

