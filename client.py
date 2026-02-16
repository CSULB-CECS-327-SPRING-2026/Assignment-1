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

    user_choice = input("Please select an option: ")

menu()
