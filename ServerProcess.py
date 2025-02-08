import random
import socket
from typing import List, Optional
import re
import threading
import time

from OnSiteServerApplication.Backend.App.Models.MessageHandler import MessageHandler
from OnSiteServerApplication.Backend.App.Repositories.ClientRepository import ClientRepository
from OnSiteServerApplication.Backend.App.Repositories.UserRepository import UserRepository
from OnSiteServerApplication.Backend.App.Server.ClientHandler import ClientHandler


class ServerProcess:
    PORT = 50000

    def __init__(self):
        #just to check
        self.id =  random.randint(1,1000)
        print("serverprocess is created", self.id)
        self.client_controller = None
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)
        self.active_connections = 0
        self.client_handlers: List[ClientHandler] = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lock = threading.Lock()


    def run(self):
        self.server.bind(self.ADDR)
        self.server.listen()
        # Clients haven't connected yet, so I am setting them all to be shutdown
        client_repository = ClientRepository()
        clients = client_repository.get_all_clients()#
        print("running", self.id)
        for client in clients:
            client.set_shutdown(True)
            client.save()

        print(f"server is listening on {self.SERVER}\n")
        threading.Thread(target=self.terminal_process, daemon=True).start()
        threading.Thread(target=self.search_for_clients, daemon=True).start()


    def search_for_clients(self):
        while True:
            conn, addr = self.server.accept()
            print(conn)
            print(addr)
            messageHandler = MessageHandler(conn)
            messageHandler.send_initial_message()
            clientHandler = ClientHandler(messageHandler)
            self.client_handlers.append(clientHandler)
            self.active_connections += 1
            print(f"Users Connected: {self.active_connections}")


    def terminal_process(self):
        try:
            while True:
                time.sleep(0.5)
                message = input("> ")

                if message.lower() == "exit":
                    print("\n[INFO] Exiting client controller.")
                    break

                # Check if the message contains exactly two words
                splitMessage = message.split()

                if splitMessage[0].lower() == "createuser":
                    try:
                        username_password = splitMessage[1].split(":")
                        print(self.generate_user(self, username_password[0], username_password[1]))
                    except:
                        print("Could not create user")

                if len(splitMessage) >= 2 and self.is_valid_uuid(splitMessage[-1]):
                    self.send_to_client(splitMessage, splitMessage[-1])
                else:
                    # Add a slight delay to let the server process
                    time.sleep(1)

                    # Send the message to each client in the list
                    self.broadcast(splitMessage)
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user. Exiting.")


    def enter_command(self, message) -> str:
        try:
            time.sleep(0.5)
            # Check if the message contains exactly two words
            splitMessage = message.split()
            if len(splitMessage) >= 2 and self.is_valid_uuid(splitMessage[-1]):
                self.send_to_client(splitMessage, splitMessage[-1])
            else:
                # Add a slight delay to let the server process
                time.sleep(1)

                # Send the message to each client in the list
                return str(self.broadcast(splitMessage))

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user. Exiting.")


    def broadcast(self, message):
        """
        Broadcast to every connected client
        :param message:
        :return:
        """
        responses = []
        for index, client_handler in enumerate(self.client_handlers):
            try:
                result = self.process_messages(message, client_handler)
                responses.append(result)

            except (socket.error, ConnectionResetError, Exception):
                print(f"\n[CONNECTION ERROR] Client {client_handler.clientModel.uuid} disconnected.")
                client_handler.messageController.connection.close()
                client_handler.set_shutdown()
                self.client_handlers.remove(client_handler)
                self.active_connections -= 1
                return None

        return responses


    def send_to_client(self, message, uuid) -> Optional[str]:
        """
        Send to a Specific Client
        :param uuid:
        :param message:
        :return:
        """
        clientRepository = ClientRepository()
        client = clientRepository.get_client_by_uuid(uuid)[0]

        # Find the ClientHandler object with the same MAC address as the repository object
        client_handler = next(
            (handler for handler in self.client_handlers if handler.clientModel.get_uuid() == client.get_uuid()),
            None
        )
        print(self.active_connections)
        for clientHandler in self.client_handlers:
            print(clientHandler.clientModel.get_uuid())

        if client_handler:
            print(client.get_uuid())
            try:
                result = self.process_messages(message, client_handler)
                return result

            except (socket.error, ConnectionResetError):
                print(f"\n[CONNECTION ERROR] Client {client_handler.messageController.get_message_id()} disconnected.")
                client_handler.messageController.connection.close()
                client_handler.set_shutdown()
                self.client_handlers.remove(client_handler)
                self.active_connections -= 1
                return None


    def process_messages(self, message, client_handler) -> str:
        print("\n[MESSAGE PROCESSING]")
        if message:
            if message[0].lower() == "shutdown":
                return client_handler.shutdown()
            elif message[0].lower() == "upgrades":
                return client_handler.get_available_updates()
            elif message[0].lower() == "software":
                return client_handler.get_client_with_software()

            if len(message) >= 2:
                if message[0].lower() == "install":
                    return client_handler.install_software(message[1])
                elif message[0].lower() == "uninstall":
                    return client_handler.uninstall_software(message[1])
                elif message[0].lower() == "upgrade":
                    return client_handler.upgrade_software(message[1])
        else:
            print("enter a valid message")


    @staticmethod
    def is_valid_uuid(uuid_str):
        # Regular expression for matching UUID format
        uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        return bool(re.match(uuid_pattern, uuid_str))

    @staticmethod
    def generate_user(self, username, password):
        userRepository = UserRepository()
        if userRepository.create_user(username, password):
            return "User Generated Successfully."
        else:
            return "User Generated Failed."

    @staticmethod
    def confirm_user(self, username, password) -> bool:
        userRepository = UserRepository()
        return userRepository.confirm_user(username, password)