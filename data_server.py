import socket
import json

HOST = "127.0.0.1"
PORT = 6000
DATA_FILE = "listings.json"

with open(DATA_FILE, 'r') as file:
    listings = json.load(file)

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
            response = format_response(error="Invalid command")

        conn.sendall(response.encode())

    print(f"Connection with {addr} closed")
    conn.close()

def handle_search(command):
    args = command.split()[1:]
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
    if error is not None:
        return json.dumps({"error": f"ERROR {error}\n"})
    
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

    lines.append("END\n")
    return json.dumps({"response": "\n".join(lines)})

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Data Server is listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            handle_client(conn, addr)
    except KeyboardInterrupt:
        print("Shutting down the Data server...")
    finally:
        server_socket.close()
        
if __name__ == "__main__":
    main()