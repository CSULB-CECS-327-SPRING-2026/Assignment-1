import socket
import time

HOST = "127.0.0.1"
PORT = 7100  # Connect to App Server

def connect_to_server():
    """Connect to the Application Server."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        return sock
    except ConnectionRefusedError:
        print(f"Error: Cannot connect to App Server at {HOST}:{PORT}")
        print("Make sure the App Server is running.")
        return None

def send_command(sock, command):
    """Send a command and receive response."""
    start_time = time.time()
    
    sock.sendall((command + "\n").encode())
    
    response = ""
    while True:
        chunk = sock.recv(4096).decode()
        if not chunk:
            break
        response += chunk
        if response.endswith("END\n") or response.startswith("ERROR"):
            break
    
    elapsed_ms = (time.time() - start_time) * 1000
    return response, elapsed_ms

def display_results(response, elapsed_ms):
    """Display results in a formatted table."""
    lines = response.strip().split('\n')
    
    if not lines:
        print("No response received.")
        return
    
    if lines[0].startswith("ERROR"):
        print(f"\n{lines[0]}")
        return
    
    if not lines[0].startswith("OK RESULT"):
        print(f"Unexpected response: {lines[0]}")
        return
    
    try:
        count = int(lines[0].split()[2])
    except (IndexError, ValueError):
        print("Invalid response format")
        return
    
    print(f"\n{'='*80}")
    print(f" Found {count} listing(s)  |  Response time: {elapsed_ms:.2f}ms")
    print(f"{'='*80}")
    
    if count == 0:
        print("No matching listings found.")
        print(f"{'='*80}\n")
        return
    
    # Print table header
    print(f"{'ID':<6} {'City':<15} {'Address':<30} {'Price':>10} {'Beds':>6}")
    print(f"{'-'*6} {'-'*15} {'-'*30} {'-'*10} {'-'*6}")
    
    # Print listings
    for i in range(1, len(lines)):
        if lines[i] == "END":
            break
        
        # Parse listing
        listing = {}
        for part in lines[i].split(';'):
            if '=' in part:
                key, value = part.split('=', 1)
                listing[key] = value
        
        if listing:
            print(f"{listing.get('id', 'N/A'):<6} "
                  f"{listing.get('city', 'N/A'):<15} "
                  f"{listing.get('address', 'N/A'):<30} "
                  f"${listing.get('price', 'N/A'):>9} "
                  f"{listing.get('bedrooms', 'N/A'):>6}")
    
    print(f"{'='*80}\n")

def print_menu():
    """Print the menu."""
    print("\n" + "="*50)
    print("       HOUSING SEARCH CLIENT")
    print("="*50)
    print("\nCommands:")
    print("  1. SEARCH  - Search by city and max price")
    print("  2. LIST    - List all listings")
    print("  3. QUIT    - Exit")
    print("\nOr type commands directly:")
    print("  SEARCH city=LongBeach max_price=2500")
    print("  LIST")
    print("="*50)

def run_performance_test(sock, iterations=50):
    """Run performance test for caching experiment."""
    print(f"\n{'='*60}")
    print(f" PERFORMANCE TEST: {iterations} iterations")
    print(f" Command: SEARCH city=LongBeach max_price=2500")
    print(f"{'='*60}")
    
    times = []
    command = "SEARCH city=LongBeach max_price=2500"
    
    for i in range(iterations):
        response, elapsed_ms = send_command(sock, command)
        if not response.startswith("ERROR"):
            times.append(elapsed_ms)
        
        if (i + 1) % 10 == 0:
            print(f"  Completed {i + 1}/{iterations}...")
    
    if times:
        print(f"\n{'='*60}")
        print(" RESULTS:")
        print(f"{'='*60}")
        print(f"  Total time:    {sum(times):.2f} ms")
        print(f"  Average time:  {sum(times)/len(times):.2f} ms")
        print(f"  Min time:      {min(times):.2f} ms")
        print(f"  Max time:      {max(times):.2f} ms")
        print(f"  First request: {times[0]:.2f} ms")
        print(f"  Last request:  {times[-1]:.2f} ms")
        print(f"{'='*60}\n")

def main():
    print(f"Connecting to App Server at {HOST}:{PORT}...")
    sock = connect_to_server()
    if not sock:
        return
    print("Connected!\n")
    
    print_menu()
    
    try:
        while True:
            user_input = input("\nEnter command: ").strip()
            
            if not user_input:
                continue
            
            # Menu options
            if user_input == '1' or user_input.upper() == 'SEARCH':
                city = input("Enter city (e.g., LongBeach, LA): ").strip()
                price = input("Enter max price: ").strip()
                if city and price:
                    command = f"SEARCH city={city} max_price={price}"
                else:
                    print("City and price are required.")
                    continue
            elif user_input == '2'or user_input.upper() == 'LIST':
                command = "LIST"
            elif user_input == '3' or user_input.upper() == 'QUIT':
                print("Goodbye!")
                break
            elif user_input.upper().startswith('PERF'):
                # Performance test
                parts = user_input.split()
                iterations = int(parts[1]) if len(parts) > 1 else 50
                run_performance_test(sock, iterations)
                continue
            else:
                print("Unknown command. Use 1, 2, 3, or type a command.")
                continue
            
            response, elapsed_ms = send_command(sock, command)
            display_results(response, elapsed_ms)
            
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    finally:
        try:
            sock.sendall(b"QUIT\n")
        except:
            pass
        sock.close()

if __name__ == "__main__":
    main()