import socket
import uuid
import requests
import os
from App.Backend.Repositories.ClientRepository import ClientRepository


class OverseerHandler:

    OVERSEER_URL = os.getenv("OVERSEER_ADDRESS")

    def __init__(self):
        self.clientRepository = ClientRepository()

    def update_overseer(self):
        # Get all the client data and send it to Overseer
        data = {
            'mac_address': self.get_mac_address(),
            'ip_address': self.get_ip_address(),
            'clients': self.get_clients(),
        }

        try:
            response = requests.post(self.OVERSEER_URL, json=data)
            response.raise_for_status()
            print("Update sent successfully")
        except requests.RequestException as e:
            print(f"Failed to update Overseer: {e}")


    def get_clients(self):
        clients = self.clientRepository.get_all_clients()
        client_list = []

        for client in clients:
            program_data = self.get_programs(client)
            client_json = client.to_dict()
            client_json['programs'] = program_data
            client_list.append(client_json)

        return client_list

    def get_programs(self, client):
        programs = client.get_installed_programs()
        return [program.to_json() for program in programs]


    def get_ip_address(self):
        try:
            # Use Google's public DNS to find the outward-facing IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"Error getting IP address: {e}")
            return '0.0.0.0'


    def get_mac_address(self):
        try:
            mac = uuid.getnode()
            mac_address = ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))
            return mac_address
        except Exception as e:
            print(f"Error getting MAC address: {e}")
            return '00:00:00:00:00:00'
