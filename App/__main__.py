import threading
from dotenv import load_dotenv
from flask import Flask
from App.Backend.Controllers.ClientController import ClientController
from App.ServerProcess import ServerProcess
import App.SetupDB as SetupDB

global server

if __name__ == '__main__':
    load_dotenv()
    SetupDB.setup_database()
    app = Flask(__name__, static_folder='static', template_folder='templates')

    server = ServerProcess()

    print(server.id)
    client_controller = ClientController(server)

    print("run thread")
    threading.Thread(target=client_controller.server.run, daemon=True).start()

    LOGIN_COOKIE_KEY = 'login'
    blueprint = client_controller.getBlueprint()
    app.register_blueprint(blueprint)
    #Debug mode won't let you use the application
    app.run(host='0.0.0.0', port=5000, debug=False)
