import threading

from flask import Flask

from OnSiteServerApplication.Backend.App.Controllers.ClientController import ClientController
from OnSiteServerApplication.ServerProcess import ServerProcess

global server

if __name__ == '__main__':
    server = ServerProcess()
    print(server.id)
    client_controller = ClientController(server)

    print("run thread")
    threading.Thread(target=client_controller.server.run, daemon=True).start()

    app = Flask(__name__, static_folder='Frontend/static', template_folder='frontend/templates')
    LOGIN_COOKIE_KEY = 'login'
    blueprint = client_controller.getBlueprint()
    app.register_blueprint(blueprint)
    #THIS WILL MAKE HTE APP NOT WORK IF TRUE
    app.run(debug=False)



