# main_server.py
from server.database import init_db
from server.server import GameServer

# Dòng này kích hoạt các lệnh dispatcher.register() bên trong api_routes.py
import server.api_routes 

if __name__ == "__main__":
    print("========================================")
    print("     Starting ONLINE SERVER       ")
    print("========================================")
    
    init_db()
    
    server = GameServer()
    server.start()

