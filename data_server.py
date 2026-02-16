import socket
import json

HOST = "127.0.0.1"
PORT = 6000
DATA_FILE = "listings.json"

# Load listings at startup
with open(DATA_FILE, 'r') as file:
    listings = json.load(file)
print(f"Loaded {len(listings)} listings from {DATA_FILE}")

def handle_client(conn, addr):
    while True:
        request = conn.recv(4096)
        if not request:
            break

        command = request.decode().strip()
        print(f"Received command: {command}")

        if command == "RAW_LIST":
            response = format_response(results=listings)
        elif command.startswith("RAW_SEARCH"):
            response = format_response(results=handle_search(command))
        else:
            response = f"ERROR Invalid command\n"

        conn.sendall(response.encode())

    print(f"Connection with {addr} closed")
    conn.close()

def handle_search(command):
    """Parse RAW_SEARCH command and filter listings."""
    args = command.split()[1:]  # Skip "RAW_SEARCH"
    filters = {}

    for arg in args:
        key, value = arg.split('=')
        filters[key] = value

    results = []
    for listing in listings:
        match = True
        if "city" in filters and listing["city"].lower() != filters["city"].lower():
            match = False
        if "max_price" in filters and int(listing["price"]) > int(filters["max_price"]):
            match = False
        if match:
            results.append(listing)

    return results

def format_response(results=None, error=None):
    """Format response according to protocol specification (plain text, not JSON)."""
    if error is not None:
        return f"ERROR {error}\n"
    
    lines = []
    lines.append(f"OK RESULT {len(results)}")

    for e in results:
        line = (
            f"id={e['id']};"
            f"city={e['city']};"
            f"address={e['address']};"
            f"price={e['price']};"
            f"bedrooms={e['bedrooms']}"
        )
        lines.append(line)

    lines.append("END")
    return "\n".join(lines) + "\n"

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Data Server is listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            handle_client(conn, addr)
    except KeyboardInterrupt:
        print("\nShutting down the Data server...")
    finally:
        server_socket.close()
        
if __name__ == "__main__":
    main()
