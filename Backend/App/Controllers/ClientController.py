import json
import threading
import secrets

from flask import jsonify, request, redirect, url_for, g
from flask import Blueprint, render_template

from OnSiteServerApplication.Backend.App.Repositories.ClientRepository import ClientRepository
from OnSiteServerApplication.Backend.App.Repositories.ProgramRepository import ProgramRepository


class ClientController:

    main = Blueprint(
        "main",
        __name__,
        static_folder="Frontend/static",
        template_folder="frontend/templates"
    )


    def __init__(self, server):
        # Bind the instance method to the route
        self.main.add_url_rule(
            '/api/clients/shutdown',
            'shutdown_client',
            self.shutdown_client,
            methods=['POST'])
        self.main.add_url_rule(
            '/api/clients/upgrades',
            'scan_for_upgrades',
            self.scan_for_upgrades,
            methods=['POST'])
        self.main.add_url_rule(
            '/api/clients/upgrade',
            'get_upgrade',
            self.get_upgrades,
            methods=['POST'])
        self.main.add_url_rule(
            '/api/clients/install',
            'install_software',
            self.install_software,
            methods=['POST'])
        self.main.add_url_rule(
            '/do_login',
            'do_login',
            self.do_login,
            methods=['POST'])

        self.lock = threading.Lock()
        self.server = server
        print(self.server.id)
        self.session_store = {}

        @self.main.before_request
        def check_login():
            print("check_login")
            if request.endpoint not in ['main.login', 'main.do_login', 'static']:
                login_token = request.cookies.get('login')
                if not login_token or login_token not in self.session_store:
                    return redirect(url_for('main.login'))
                g.user = self.session_store[login_token]


    def getBlueprint(self):
        return self.main


    @staticmethod
    @main.route('/login')
    def login():
        login_failed = request.args.get('login_failed', 'false') == 'true'
        return render_template('login.html', login_failed=login_failed)


    def do_login(self):
        username = request.form.get('username')
        password = request.form.get('password')

        if self.server.confirm_user(self.server, username, password):  # Replace with real logic
            unique_token = secrets.token_hex(16)  # Generate a secure random token
            self.session_store[unique_token] = username  # Save the token associated with the user

            response = redirect(url_for('main.home'))
            response.set_cookie('login', unique_token, max_age=3600, httponly=True, secure=True)  # Secure cookie settings
            return response
        else:
            return redirect(url_for('main.login', login_failed='true'))


    @staticmethod
    @main.route('/')
    def home():
        """Render the home page."""
        client_repository = ClientRepository()
        clients = client_repository.get_all_clients()
        clients_as_dict = [client.to_dict() for client in clients]
        online_client_count = 0

        for client in clients:
            if not client.is_shutdown():
                online_client_count += 1

        return render_template('home.html', clients=clients_as_dict, online_client_count=online_client_count)


    @staticmethod
    @main.route('/api/clients', methods=['GET'])
    def get_clients():
        """Endpoint to return the list of clients."""
        client_repository = ClientRepository()

        # Convert list of ClientModel instances to list of dictionaries
        clients = [client.to_dict() for client in client_repository.get_all_clients()]

        return jsonify(clients), 200


    @staticmethod
    @main.route('/clients', methods=['GET'])
    def get_clients_page():
        """Endpoint to return the list of clients."""
        client_repository = ClientRepository()

        # Convert list of ClientModel instances to list of dictionaries
        clients = [client.to_dict() for client in client_repository.get_all_clients()]

        return render_template('clients.html', clients=clients)


    @staticmethod
    @main.route('/settings', methods=['GET'])
    def get_settings_page():
        return render_template('settings.html')


    @staticmethod
    @main.route('/rules', methods=['GET'])
    def get_rules_page():
        return render_template('rules.html')


    @staticmethod
    @main.route('/default-apps', methods=['GET'])
    def get_default_apps_page():
        return render_template('default-apps.html')


    @staticmethod
    @main.route('/clients/<string:mac_address>', methods=['GET'])
    def get_client_by_mac_page(mac_address):
        """Endpoint to return a single client by name."""
        client_repository = ClientRepository()
        program_repository = ProgramRepository()

        # Attempt to retrieve the client by nickname
        client = client_repository.get_client_by_mac_address(mac_address)[0]

        programs = [program.to_dict() for program in client.get_installed_programs()]
        try:
            client.firewall_status = json.loads(client.firewall_status)
        except Exception:
            client.firewall_status = {}
        try:
            client.bitlocker_status = json.loads(client.bitlocker_status)
        except Exception:
            client.bitlocker_status = {}

        if client is None:
            return jsonify({"error": f"No client found with nickname '{mac_address}'"}), 404

        # Convert the client to a dictionary
        return render_template('client.html', client=client, programs=programs)


    @staticmethod
    @main.route('/api/clients/name/<string:client_name>', methods=['GET'])
    def get_client_by_name(client_name):
        """Endpoint to return a single client by name."""
        client_repository = ClientRepository()

        # Attempt to retrieve the client by nickname
        client = client_repository.get_client_by_nickname(client_name)

        if client is None:
            return jsonify({"error": f"No client found with nickname '{client_name}'"}), 404

        # Convert the client to a dictionary
        return jsonify(client.to_dict()), 200


    def shutdown_client(self):
        data = request.get_json()
        command = 'shutdown'

        if data.get('mac'):
            command += " " + str(data.get('mac'))

        response = self.server.enter_command('shutdown')
        return jsonify({"message": response}), 200


    def scan_for_upgrades(self):
        response = self.server.enter_command('upgrades')

        return jsonify({"message": response}), 200


    def get_upgrades(self):

        response = self.server.enter_command('upgrade all')

        return jsonify({"message": response}), 200


    def install_software(self):
        data = request.get_json()
        command = "install " + str(data.get('software'))

        if data.get('mac'):
            command += " " + str(data.get('mac'))

        response = self.server.enter_command(command)
        return jsonify({"message": response}), 200