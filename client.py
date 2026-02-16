import socket
import json
import time

HOST = "127.0.0.1" # Default localhost IP address
PORT = 7100 # Port number for the client to connect to the app server

def menu():
    """
    The main menu function of the housing search service. It displays the available commands and prompts the user to select an option. 
    Based on the user's choice, it calls the appropriate function to handle the command.
    """
    print("=====================================")
    print(" " * 7 + "HOUSING SEARCH SERVICE" + " " * 7)
    print("=====================================")
    print("\nAvailable commands:\n")
    print(" " * 5 + "1. SEARCH - Search by city and max price")
    print(" " * 5 + "2. LIST - List all available listings")
    print(" " * 5 + "3. QUIT - Exit\n")

def main():
    """
    Handles the user's command input and interacts with the server accordingly. It processes the user's choice and sends the appropriate command to the server, then displays the response.
    
    Args:
        user_choice: The user's input command, which is expected to be a list of strings.
    """
    menu()
    user_choice = input("Please select an option: ").strip()
    
    while True:
        if user_choice == "1" or user_choice.upper() == "SEARCH":
            city = input("Enter city (Ex: LongBeach, LA, Irvine, SanFrancisco, SanDiego): ").strip()
            price = input("Enter max price: ").strip()
            if city and price:
                command = f"SEARCH city={city} max_price={price}"
            else:
                print("City and price are required.")
                continue
        elif user_choice == "2" or user_choice.upper() == "LIST":
            command = "LIST"
        elif user_choice == "3" or user_choice.upper() == "QUIT":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
            continue
    
main()
