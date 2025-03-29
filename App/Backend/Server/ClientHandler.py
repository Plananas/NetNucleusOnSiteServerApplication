import json
import uuid
import ast
import os

from App.Backend.Models.ClientModel import ClientModel
from App.Backend.Models.MessageHandler import MessageHandler
from App.Backend.Models.ProgramModel import ProgramModel
from App.Backend.Repositories.ClientRepository import ClientRepository
from App.Backend.Repositories.ProgramRepository import ProgramRepository
from App.Backend.Server.ScoopFunctions import ScoopFunctions as Scoop, ScoopFunctions

class ClientHandler:

    SHUTDOWN_COMMAND = "shutdown"
    GET_UPGRADES_COMMAND = "upgrades"
    GET_ALL_SOFTWARE_COMMAND = "software"
    GET_ALL_STATS_COMMAND = "statistics"
    INSTALL_SOFTWARE_COMMAND = "install"
    UNINSTALL_SOFTWARE_COMMAND = "uninstall"
    UPGRADE_SOFTWARE_COMMAND = "upgrade"

    SUCCESSFUL_SHUTDOWN_MESSAGE = "Shutting down"
    SUCCESSFUL_UNINSTALL_MESSAGE = "Successfully uninstalled"
    SUCCESSFUL_INSTALL_MESSAGE = "Successfully installed"
    SUCCESSFUL_UPGRADE_MESSAGE = "Successfully upgraded"

    def __init__(self, message_controller):
        self.messageController: MessageHandler = message_controller
        self.connectedStatus = False
        self.clientModel = self.get_client_with_software()
        self.get_available_updates()

    def shutdown(self):
        self.messageController.write(self.SHUTDOWN_COMMAND)

        #the client is shutting down so I think putting some kind of behaviour to check the status would be good

        response = self.messageController.read()
        if not response:
            print("[ERROR] No response received for shutdown command.")
            return None

        # Check if "Successful" is in the response
        if self.SUCCESSFUL_SHUTDOWN_MESSAGE in response:
            print("Shutdown was successful.")
            self.set_shutdown()

        else:
            print("Shutdown was not successful.")

        return response

    def set_shutdown(self):
        self.clientModel.set_shutdown(True)
        self.clientModel.save()

    def get_available_updates(self):
        """
        :return: Status of the command
        """
        print("getAvailableUpdates")
        programs = self.clientModel.get_installed_programs()
        print("programs:")
        print(programs)
        for program in programs:
            print("find available updates for")
            program.find_available_version()
            print("Getting available version number")
            print(program.available_version)
        return 'saved upgraded versions'


    def get_client_with_software(self) -> ClientModel :
        """
        :return: Array of Software
        """

        self.messageController.write(self.GET_ALL_SOFTWARE_COMMAND)
        installed_software = self.messageController.read()
        self.messageController.write(self.GET_ALL_STATS_COMMAND)
        computer_statistics = self.messageController.read()

        print("RESPONSE ARRAY")
        print(installed_software)
        print(computer_statistics)
        installed_software = ast.literal_eval(installed_software)
        computer_statistics = ast.literal_eval(computer_statistics)
        client = self.save_new_client(installed_software, computer_statistics)

        return client


    def install_software(self, software_name):
        """
        :return: Success Message
        """

        file_path = Scoop.download_installer(software_name)
        response = ""
        if file_path is not None:
            filename = os.path.basename(file_path)

            self.messageController.write(self.INSTALL_SOFTWARE_COMMAND + " " + filename)
            self.messageController.write_file(file_path)

            responseArray = self.messageController.read()
            responseArray = ast.literal_eval(responseArray)  # Assuming it's a string representation of a list
            mac_address = self.clientModel.get_mac_address()
            response = responseArray[mac_address]

        if not response:
            print("[ERROR] No response received for install command.")
            return None

        # Check if "Successful" is in the response
        if self.SUCCESSFUL_INSTALL_MESSAGE in response:
            self.get_client_with_software()
            self.get_available_updates()

        return response

    def uninstall_software(self, software_name):
        """
        :return: Success Message
        """
        self.messageController.write((self.UNINSTALL_SOFTWARE_COMMAND + " " + software_name))

        responseArray = self.messageController.read()
        responseArray = ast.literal_eval(responseArray)  # Assuming it's a string representation of a list
        mac_address = self.clientModel.get_mac_address()

        response = responseArray[mac_address]

        # Check if "Successful" is in the response
        if self.SUCCESSFUL_UNINSTALL_MESSAGE in response:
            self.get_client_with_software()
            self.get_available_updates()

        return responseArray


    def upgrade_software(self, software_name):
        """
        :return: Success Message
        """

        print(f"UPGRADE SOFTWARE {software_name}")

        if software_name == 'all':
            return self.upgrade_all_software()

        programs = self.clientModel.get_installed_programs()
        for program in programs:
            if program.software_name == software_name:
                version = ScoopFunctions.getSoftwareVersionNumber(software_name)
                if version == program.software_version:
                    return "Program is already up to date"

        try:
            return self.install_software(software_name)
        except:
            return "Could not upgrade software"


    def upgrade_all_software(self):
        """
        :return: Success Message
        """

        print("get Installed Software")
        programs = self.clientModel.get_installed_programs()
        print(programs)
        response = []
        for program in programs:
            print(program.current_version)
            version = ScoopFunctions.getSoftwareVersionNumber(program.name)
            if version == program.current_version:
                print(f"{program.name} is already up to date")
                response.append(f"{program.name} is already up to date")
            else:
                response.append(self.install_software(program.software_name))

        return response


    def save_new_client(self, mac_and_software, computer_statistics) -> ClientModel:
        mac_address = next(iter(mac_and_software))
        client_repository = ClientRepository()
        existing_client = client_repository.get_client_by_mac_address(mac_address)
        computer_statistics = computer_statistics[mac_address]

        if existing_client:
            client_uuid = existing_client[0].get_uuid()  # Assuming the existing client has a 'uuid' field
            print('Client exists')
            existing_client[0].set_shutdown(False)
            existing_client[0].save()
        else:
            client_uuid = str(uuid.uuid4())
            print('Client does not exist: Creating Model')
            storage =  str(computer_statistics['storage']['current']) + '/' + str(computer_statistics['storage']['max'])
            self.clientModel: ClientModel = ClientModel(
                uuid=client_uuid,
                mac_address=mac_address,
                nickname='',
                shutdown=False,
                storage=storage,
                firewall_status=json.dumps(computer_statistics['firewall_status']),
                windows_version=computer_statistics['operating_system_information']['windows'],
                windows_version_number=computer_statistics['operating_system_information']['windows_version_number'],
                bitlocker_status=json.dumps(computer_statistics['bitlocker_status']),
                current_user=str(computer_statistics['user']),
            )
            self.clientModel.save()
            existing_client = [self.clientModel]

        # Save the associated program
        self.save_programs(client_uuid, mac_and_software[mac_address])

        return existing_client[0]

    def save_programs(self, client_uuid, installed_software):
        program_repository = ProgramRepository()
        existing_program = program_repository.get_program_by_client_id(client_uuid)
        if existing_program:
            for program in existing_program:
            #The program should already exist if it had a version so we delete it
                program.delete()

        for program in installed_software:
            self.save_program(client_uuid, program)

    def save_program(self, client_uuid, program):
        program_repository = ProgramRepository()
        existing_program = program_repository.get_program_by_client_id_and_name(client_uuid, program["name"])

        if existing_program:
            #The program should already exist if it had a version so we delete it
            existing_program[0].delete()

        programModel = ProgramModel(
            client_uuid=client_uuid,
            name=program["name"],
            current_version=program["current_version"],
            available_version = program.get("available_version") or None
        )

        programModel.save()