import socket
import datetime

HOST = "127.0.0.1"
PORT = 7100
DATA_SERVER_HOST = "127.0.0.1"
DATA_SERVER_PORT = 6000
LOG_FILE = "app_server.log"

# ============================================================================
# CACHE - Stores recent query results (required by assignment)
# ============================================================================
cache = {}  # Key: command string, Value: response string

class LogInterceptor:
    """Interceptor pattern - logs all requests and responses."""
    def __init__(self, log_file):
        self.log_file = log_file
        with open(self.log_file, 'w') as file:
            file.write("App Server Log\n")
            file.write("=" * 50 + "\n")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as file:
            file.write(f"[{timestamp}] {message}\n")

logger = LogInterceptor(LOG_FILE)

def parse_listing(line):
    """Parse a listing line into a dictionary."""
    listing = {}
    parts = line.split(';')
    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            if key in ['id', 'price', 'bedrooms']:
                listing[key] = int(value)
            else:
                listing[key] = value
    return listing

def format_listing(listing):
    """Format a listing dictionary back to protocol string."""
    return (f"id={listing['id']};"
            f"city={listing['city']};"
            f"address={listing['address']};"
            f"price={listing['price']};"
            f"bedrooms={listing['bedrooms']}")

def rank_results(response):
    """
    Apply ranking to results.
    Sort by: price ascending, then bedrooms descending.
    """
    lines = response.strip().split('\n')
    
    # Check if valid response
    if not lines[0].startswith("OK RESULT"):
        return response
    
    # Parse listings
    listings = []
    for i in range(1, len(lines)):
        if lines[i] == "END":
            break
        listing = parse_listing(lines[i])
        if listing:
            listings.append(listing)
    
    # Sort: price ascending, bedrooms descending
    listings.sort(key=lambda x: (x.get('price', 0), -x.get('bedrooms', 0)))
    
    # Rebuild response
    result_lines = [f"OK RESULT {len(listings)}"]
    for listing in listings:
        result_lines.append(format_listing(listing))
    result_lines.append("END")
    
    return "\n".join(result_lines) + "\n"

def handle_client(conn, addr):
    while True:
        request = conn.recv(4096)
        if not request:
            break

        command = request.decode().strip()
        print(f"Received command: {command}")
        logger.log(f"REQUEST from {addr}: {command}")

        if command == "QUIT":
            conn.close()
            break
        elif command == "LIST" or command.startswith("SEARCH"):
            # Check cache first
            if command in cache:
                response = cache[command]
                print(f"CACHE HIT for: {command}")
                logger.log(f"CACHE HIT for: {command}")
            else:
                # Cache miss - forward to data server
                print(f"CACHE MISS for: {command}")
                logger.log(f"CACHE MISS for: {command}")
                response = forward_to_data_server(command)
                
                # Apply ranking
                response = rank_results(response)
                
                # Store in cache
                cache[command] = response
                logger.log(f"Cached result for: {command}")
        else:
            response = "ERROR Invalid command\n"

        logger.log(f"RESPONSE to {addr}: {response.strip()[:100]}...")
        conn.sendall(response.encode())

    print(f"Connection with {addr} closed")
    logger.log(f"Connection with {addr} closed")
    conn.close()
    
def forward_to_data_server(command):
    """Forward command to Data Server and get response."""
    # Translate client command to data server command
    if command == "LIST":
        data_command = "RAW_LIST"
    elif command.startswith("SEARCH"):
        data_command = "RAW_SEARCH " + command[7:]  # Remove "SEARCH "
    else:
        return "ERROR Invalid command\n"
    
    try:
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.connect((DATA_SERVER_HOST, DATA_SERVER_PORT))
        logger.log(f"Forwarding to Data Server: {data_command}")
        
        # Send command with newline
        data_socket.sendall((data_command + "\n").encode())
        
        # Receive response (may come in chunks)
        response = ""
        while True:
            chunk = data_socket.recv(4096).decode()
            if not chunk:
                break
            response += chunk
            if response.endswith("END\n") or response.startswith("ERROR"):
                break
        
        logger.log(f"Received from Data Server: {response.strip()[:100]}...")
        data_socket.close()
        return response
        
    except ConnectionRefusedError:
        logger.log("ERROR: Cannot connect to Data Server")
        return "ERROR Cannot connect to Data Server\n"
    except Exception as e:
        logger.log(f"ERROR: {e}")
        return f"ERROR {e}\n"

def main():
    print("=" * 50)
    print("       APPLICATION SERVER")
    print("=" * 50)
    print(f"Cache: ENABLED")
    print(f"Log file: {LOG_FILE}")
    print(f"Data Server: {DATA_SERVER_HOST}:{DATA_SERVER_PORT}")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"App Server is listening on {HOST}:{PORT}")
    logger.log(f"App Server started on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            logger.log(f"Connected by {addr}")
            handle_client(conn, addr)
            
            # Print cache stats
            print(f"Cache size: {len(cache)} entries")
    except KeyboardInterrupt:
        print("\nShutting down the App server...")
        logger.log("Shutting down the App server...")
    finally:
        server_socket.close()
        
if __name__ == "__main__":
    main()
