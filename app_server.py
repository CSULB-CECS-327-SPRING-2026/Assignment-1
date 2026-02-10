import socket
import datetime

HOST = "127.0.0.1"
PORT = 7100
DATA_SERVER_HOST = "127.0.0.1"
DATA_SERVER_PORT = 6000
LOG_FILE = "app_server.log"

class LogInterceptor:
    def __init__(self, log_file):
        self.log_file = log_file
        with open(self.log_file, 'w') as file:
            file.write("App Server Log\n")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as file:
            file.write(f"[{timestamp}] {message}\n")

logger = LogInterceptor(LOG_FILE)

def handle_client(conn, addr):
    while True:
        request = conn.recv(4096)
        if not request:
            break

        command = request.decode().strip()
        print(f"Received command: {command}")
        logger.log(f"Received command: {command}")

        if command == "QUIT":
            conn.close()
            break
        elif command == "LIST" or command.startswith("SEARCH"):
            response = forward_to_data_server(command)
        else:
            response = "ERROR Invalid command\n"

        logger.log(f"Sending response: {response.strip()}")
        conn.sendall(response.encode())

    print(f"Connection with {addr} closed")
    logger.log(f"Connection with {addr} closed")
    conn.close()
    
def forward_to_data_server(command):
    if command == "LIST":
        data_command = "RAW_LIST"
    elif command.startswith("SEARCH"):
        data_command = "RAW_SEARCH " + command[7:]
    
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((DATA_SERVER_HOST, DATA_SERVER_PORT))
    logger.log(f"Forwarding command to Data Server: {data_command}")
    data_socket.sendall(data_command.encode())
    response = data_socket.recv(4096).decode()
    logger.log(f"Received response from Data Server: {response.strip()}")
    data_socket.close()

    return response

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"App Server is listening on {HOST}:{PORT}")
    logger.log(f"App Server is listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            logger.log(f"Connected by {addr}")
            handle_client(conn, addr)
    except KeyboardInterrupt:
        print("Shutting down the App server...")
        logger.log("Shutting down the App server...")
    finally:
        server_socket.close()
        
    
if __name__ == "__main__":
    main()